import os
import time
import re
import wave
from pathlib import Path
from typing import List, Dict, Union, Optional

import pandas as pd
from tqdm import tqdm

from google import genai
from google.genai import types

# 追加: .envから環境変数を読み込む
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except Exception:
    HAS_PYDUB = False

import argparse


# ====== 設定エリア ======
INPUT_CSV = "scripts.csv"  # デフォルト値。コマンドラインで上書き可
OUTPUT_DIR = "tts_outputs"
ID_COL = None
TITLE_COL = "title"
PART_COLS = ["フック（0-5秒）", "共感（5-12秒）", "前提知識（12-21秒）", "メイン解説（21-30秒）", "解説まとめ（30-32秒）", "実践（32-44秒）", "CTA（42-45秒）"]
SPEED_MULTIPLIER = 1.0  # プロンプトで速度指定するため、後処理では1.0（無効化）

# --- モデル/音声 ---
MODEL_NAME = "gemini-2.5-pro-preview-tts"  # "gemini-2.5-pro-preview-tts" も可
DEFAULT_VOICE = "Sulafat"

# --- 生成パラメータ（★追加） ---
# 公式APIの GenerateContentConfig で指定（AI Studio UI と同趣旨）:
# temperature: 0.0〜2.0（Vertex/AI Studioの一般指針）/ デフォルトは 1.0 付近
TEMPERATURE = 0.8 
TOP_P = 0.9           # 任意：確率質量サンプリング
TOP_K = 40            # 任意：上位K語彙サンプリング
MAX_OUTPUT_TOKENS = None  # 音声生成では通常未指定のままでOK

# PART_STYLE_HINTS削除：速度調整は後処理で行うため、プロンプトはシンプルに

USE_MULTI_SPEAKER_IF_AVAILABLE = True

WAV_RATE = 24000
WAV_CHANNELS = 1
WAV_SAMPLE_WIDTH = 2

# --- 無音パディング設定 ---
ADD_SILENCE_PADDING = True    # 前後に無音を追加するかどうか
SILENCE_DURATION = 0.5        # 無音の長さ（秒）
# ========================


def safe_slug(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\-.]+", "_", s)
    return s[:80] if s else "item"


def split_text_by_sentences(text: str) -> List[str]:
    """句点で区切って一文ずつに分割する"""
    if not text.strip():
        return []
    
    # 句点で分割（。！？で分割）
    sentences = re.split(r'([。！？])', text)
    
    # 句点と文を再結合
    result = []
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i].strip()
            if sentence:  # 空文字列でない場合
                # 次の要素が句点記号の場合は結合
                if i + 1 < len(sentences) and sentences[i + 1] in '。！？':
                    sentence += sentences[i + 1]
                result.append(sentence)
    
    # 空の要素を除去
    result = [s for s in result if s.strip()]
    
    return result if result else [text]


def adjust_playback_speed(pcm_bytes: bytes, speed_multiplier: float = 1.0,
                         channels=WAV_CHANNELS, rate=WAV_RATE, sample_width=WAV_SAMPLE_WIDTH) -> bytes:
    """PCM音声データの再生速度を調整"""
    if abs(speed_multiplier - 1.0) < 1e-6:
        return pcm_bytes  # 速度変更なし
    
    try:
        if HAS_PYDUB:
            # pydubを使用した高品質な速度調整
            import io
            from pydub import AudioSegment
            
            # PCMデータをAudioSegmentに変換
            audio_io = io.BytesIO(pcm_bytes)
            audio_segment = AudioSegment.from_raw(
                audio_io, 
                sample_width=sample_width, 
                frame_rate=rate, 
                channels=channels
            )
            
            # 速度調整（ピッチを保持）
            if speed_multiplier > 1.0:
                # 速くする場合：フレームレートを上げてからリサンプリング
                fast_audio = audio_segment._spawn(audio_segment.raw_data, overrides={
                    "frame_rate": int(audio_segment.frame_rate * speed_multiplier)
                })
                adjusted_audio = fast_audio.set_frame_rate(rate)
            else:
                # 遅くする場合：フレームレートを下げてからリサンプリング
                slow_audio = audio_segment._spawn(audio_segment.raw_data, overrides={
                    "frame_rate": int(audio_segment.frame_rate * speed_multiplier)
                })
                adjusted_audio = slow_audio.set_frame_rate(rate)
            
            return adjusted_audio.raw_data
        else:
            # pydubがない場合：シンプルなサンプリング調整
            print("[WARN] pydub not available, using simple speed adjustment")
            return simple_speed_adjustment(pcm_bytes, speed_multiplier, channels, rate, sample_width)
            
    except Exception as e:
        print(f"[WARN] Speed adjustment failed: {e}, using original audio")
        return pcm_bytes


def simple_speed_adjustment(pcm_bytes: bytes, speed_multiplier: float,
                           channels: int, rate: int, sample_width: int) -> bytes:
    """シンプルな速度調整（pydubなしの場合）"""
    if speed_multiplier == 1.0:
        return pcm_bytes
    
    # サンプル数を計算
    bytes_per_sample = channels * sample_width
    total_samples = len(pcm_bytes) // bytes_per_sample
    
    # 新しいサンプル数を計算
    new_sample_count = int(total_samples / speed_multiplier)
    
    # リサンプリング（線形補間）
    result = bytearray()
    for i in range(new_sample_count):
        # 元のサンプルインデックスを計算
        original_index = int(i * speed_multiplier)
        if original_index < total_samples:
            start_byte = original_index * bytes_per_sample
            end_byte = start_byte + bytes_per_sample
            result.extend(pcm_bytes[start_byte:end_byte])
    
    return bytes(result)


def add_silence_padding(pcm_bytes: bytes, silence_duration: float = 0.5,
                       channels=WAV_CHANNELS, rate=WAV_RATE, sample_width=WAV_SAMPLE_WIDTH) -> bytes:
    """PCMバイトデータの前後に無音を追加"""
    # 無音のサンプル数を計算
    silence_samples = int(silence_duration * rate)
    silence_bytes_per_sample = channels * sample_width
    silence_byte_count = silence_samples * silence_bytes_per_sample
    
    # 無音データ（0で埋める）
    silence_data = b'\x00' * silence_byte_count
    
    # 前後に無音を追加
    return silence_data + pcm_bytes + silence_data


def write_wav_pcm16(filename: Path, pcm_bytes: bytes,
                    channels=WAV_CHANNELS, rate=WAV_RATE, sample_width=WAV_SAMPLE_WIDTH,
                    add_silence: bool = True, silence_duration: float = 0.5,
                    speed_multiplier: float = 1.0):
    filename.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 速度調整を適用
    if abs(speed_multiplier - 1.0) > 1e-6:
        print(f"[INFO] Adjusting playback speed to {speed_multiplier:.2f}x")
        pcm_bytes = adjust_playback_speed(pcm_bytes, speed_multiplier, channels, rate, sample_width)
    
    # 2. 無音パディングを追加
    if add_silence:
        pcm_bytes = add_silence_padding(pcm_bytes, silence_duration, channels, rate, sample_width)
    
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)


def build_single_speaker_prompt(part_name: str, text: str) -> str:
    """
    StyleInstructionとTextの形式でプロンプトを構築
    """
    style_instruction = """Important!!  かなり早口で話す。通常の1.4倍程度の速さで。

全体イメージ
	•	雰囲気：親しみやすくフレンドリー、でも清潔感や上品さを失わない。
	•	キャラクター：SNSで日常の美容習慣を気軽にシェアしてくれる「ちょっと年上で信頼できるお姉さん」。
	•	ゴール：聞き手が「自分もやってみようかな」と前向きな気持ちになれる。

⸻

トーン詳細
	•	声色：明るくやさしい声。高すぎず、少しだけ上に寄せて軽やかさを出す。
	•	抑揚：文頭を少し明るく立ち上げ、キーワードや数字を軽く強調。最後は落ち着いて締める。疑問文では語尾の音を上げる。断定する場合は文の終わりで語尾を下げる。
	•	間の取り方：
	•	キーフレーズの前後は200ms程度。

⸻

例えるなら…
	•	友達のインスタストーリーで「最近これ試したんだけど、よかったよ〜」とシェアしている感じ。
	•	営業感ゼロで、あくまで「自分が実際にやっていること」を優しく教えてくれる。"""
    
    return f"""StyleInstruction:
'''
{style_instruction}
'''
Text: {text.strip()}"""


def _build_gen_config_for_single(voice_name: str) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        temperature=TEMPERATURE,     # ★追加
        top_p=TOP_P,                 # ★任意
        top_k=TOP_K,                 # ★任意
        max_output_tokens=MAX_OUTPUT_TOKENS,  # ★任意
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            )
        ),
    )


def _build_gen_config_for_multi(speaker_to_voice: Dict[str, str]) -> types.GenerateContentConfig:
    speaker_cfgs = []
    for speaker, voice_name in speaker_to_voice.items():
        speaker_cfgs.append(
            types.SpeakerVoiceConfig(
                speaker=speaker,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            )
        )
    return types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        temperature=TEMPERATURE,     # ★追加
        top_p=TOP_P,                 # ★任意
        top_k=TOP_K,                 # ★任意
        max_output_tokens=MAX_OUTPUT_TOKENS,  # ★任意
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_cfgs
            )
        ),
    )


def _extract_audio_bytes(resp) -> Optional[bytes]:
    try:
        for cand in getattr(resp, "candidates", []) or []:
            content = getattr(cand, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    return inline.data
    except Exception:
        return None
    return None


def add_furigana_with_gemini(client: genai.Client, text: str) -> str:
    """
    Geminiを使って小学生が読めない難しい漢字にふりがなを追加する
    """
    try:
        furigana_prompt = f"""以下のテキストに含まれる小学生が読めない可能性のある難しい漢字や熟語にふりがなを追加してください。

ルール:
- 小学生レベルで読めない漢字・熟語にのみふりがなを追加
- ふりがなの形式: 漢字（ひらがな）
- 例: 不織布 → 不織布（ふしょくふ）
- 一般的な漢字（例：知る、同じ、等）にはふりがなを追加しない
- テキストの内容や意味は一切変更しない
- ふりがな以外の文字は元のまま保持

テキスト: {text}

ふりがなを追加したテキスト:"""
        
        # テキスト生成モデルを使用（音声生成ではないため）
        resp = client.models.generate_content(
            model="gemini-2.0-flash-exp",  # テキスト生成用モデル
            contents=furigana_prompt
        )
        
        # レスポンスからテキストを抽出
        if hasattr(resp, 'candidates') and resp.candidates:
            candidate = resp.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    furigana_text = candidate.content.parts[0].text.strip()
                    print(f"[INFO] Furigana added: {text} → {furigana_text}")
                    return furigana_text
        
        print(f"[WARN] Failed to add furigana, using original text: {text}")
        return text
        
    except Exception as e:
        print(f"[ERROR] Furigana processing failed: {e}, using original text")
        return text


def generate_tts_single_speaker(client: genai.Client, text: str, voice_name: str) -> Optional[bytes]:
    """
    シンプルなTTS生成（速度調整は後処理で行う）
    """
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=text,
        config=_build_gen_config_for_single(voice_name),
    )
    return _extract_audio_bytes(resp)


def generate_tts_multi_speaker(client: genai.Client,
                               script_with_speaker_lines: str,
                               speaker_to_voice: Dict[str, str]) -> Optional[bytes]:
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=script_with_speaker_lines,
        config=_build_gen_config_for_multi(speaker_to_voice),
    )
    return _extract_audio_bytes(resp)


def main(start_row=None, end_row=None, input_csv=None, start_col=None, end_col=None, speed_multiplier=None):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY in .env or environment variable.")
    print("[INFO] GOOGLE_API_KEY loaded.")

    client = genai.Client(api_key=api_key)

    # 話速倍率の設定
    global SPEED_MULTIPLIER
    if speed_multiplier is not None:
        SPEED_MULTIPLIER = float(speed_multiplier)

    csv_path = input_csv if input_csv else INPUT_CSV
    print(f"[INFO] Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    out_root = Path(OUTPUT_DIR)
    out_root.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output directory: {out_root.resolve()}")

    # 列範囲指定があればPART_COLSを自動設定
    global PART_COLS
    if start_col is not None and end_col is not None:
        col_names = list(df.columns)
        PART_COLS = col_names[start_col-1:end_col]
        print(f"[INFO] PART_COLS set to: {PART_COLS}")
    else:
        print(f"[INFO] PART_COLS (default): {PART_COLS}")

    missing = [c for c in PART_COLS if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing columns in CSV: {missing}")
        raise ValueError(f"Missing columns in CSV: {missing}")

    # 行範囲のスライス
    data = df.reset_index(drop=True)
    total = len(data)
    s = (start_row - 1) if start_row else 0
    e = end_row if end_row else total
    data = data.iloc[s:e]
    print(f"[INFO] Processing rows: {s+1} to {e} (1-based, header excluded)")

    processed_count = 0
    total_rows = len(data)
    for idx, row in tqdm(data.iterrows(), total=total_rows, desc="Generating TTS"):
        # --- Determine numbering and title columns ---
        no_col = "No." if "No." in df.columns else None
        theme_col = "テーマ" if "テーマ" in df.columns else (TITLE_COL if TITLE_COL in df.columns else None)

        # Video number (3 digits)
        try:
            video_num = int(row[no_col]) if no_col and pd.notna(row[no_col]) else (idx + 1)
        except Exception:
            video_num = idx + 1
        video_num_str = f"{video_num:03d}"

        # Title (use theme/title if available)
        raw_title = str(row[theme_col]) if theme_col and pd.notna(row[theme_col]) else (str(row[TITLE_COL]) if TITLE_COL in df.columns and pd.notna(row[TITLE_COL]) else f"row_{idx+1}")
        title_slug = safe_slug(raw_title).strip("_")
        # Shorten to first 3 characters with ellipsis if longer
        short_core = title_slug[:3]
        title_short = f"{short_core}..." if len(title_slug) > 3 else short_core

        # Base directory name: 001_<short-title>
        base_name = f"{video_num_str}_{title_short}"

        item_dir = out_root / base_name
        item_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Processing: {base_name} (output: {item_dir})")

        part_wavs: List[Path] = []

        # --- マルチスピーカー判定 ---
        has_any_speaker = False
        speaker_map: Dict[str, str] = {}
        if USE_MULTI_SPEAKER_IF_AVAILABLE:
            for p in PART_COLS:
                spk_col = f"speaker_{p}"
                if spk_col in df.columns and pd.notna(row[spk_col]):
                    has_any_speaker = True
                    speaker = str(row[spk_col]).strip()
                    if speaker:
                        speaker_map.setdefault(speaker, DEFAULT_VOICE)

        if has_any_speaker:
            lines = []
            for p in PART_COLS:
                text = "" if pd.isna(row[p]) else str(row[p])
                if not text.strip():
                    continue
                spk_col = f"speaker_{p}"
                speaker = str(row[spk_col]).strip() if spk_col in df.columns and pd.notna(row[spk_col]) else "Narrator"
                text_with_hint = build_single_speaker_prompt(p, text)
                lines.append(f"{speaker}: {text_with_hint}")
                speaker_map.setdefault(speaker, DEFAULT_VOICE)

            script = "\n".join(lines)
            if not script.strip():
                print(f"[WARN] No script for {base_name}, skipping.")
                continue

            print(f"[INFO] Generating multi-speaker TTS for {base_name}...")
            pcm = generate_tts_multi_speaker(client, script, speaker_map)
            if not pcm:
                print(f"[WARN] No audio returned for {base_name} (multi). Skipping.")
            else:
                wav_path = item_dir / f"{base_name}.wav"
                write_wav_pcm16(wav_path, pcm, add_silence=ADD_SILENCE_PADDING, silence_duration=SILENCE_DURATION)
                print(f"[INFO] Saved: {wav_path}")
                part_wavs.append(wav_path)

        else:
            for part_index, p in enumerate(PART_COLS, start=1):
                text = "" if pd.isna(row[p]) else str(row[p])
                if not text.strip():
                    continue
                
                # 一文ずつ分割
                sentences = split_text_by_sentences(text)
                print(f"[INFO] Part '{p}' split into {len(sentences)} sentences")
                
                # Clean part name: remove parentheses content like （xx-yy秒） or (xx-yy)
                clean_part = re.sub(r"[（(][^）)]*[）)]", "", str(p)).strip()
                
                for sentence_index, sentence_text in enumerate(sentences, start=1):
                    # ふりがな追加処理
                    furigana_text = add_furigana_with_gemini(client, sentence_text)
                    
                    # シンプルなプロンプト構築（速度調整は後処理で行う）
                    prompt = build_single_speaker_prompt(p, furigana_text)
                    
                    # 複数文の場合は番号を追加
                    suffix = os.getenv("TTS_FILENAME_SUFFIX", "").strip()
                    suffix_part = f"_{suffix}" if suffix else ""
                    if len(sentences) > 1:
                        wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}_{sentence_index:02d}{suffix_part}.wav"
                        print(f"[INFO] Generating TTS for part '{p}' sentence {sentence_index}/{len(sentences)} in {base_name}...")
                    else:
                        wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}{suffix_part}.wav"
                        print(f"[INFO] Generating TTS for part '{p}' in {base_name}...")
                    
                    print(f"[DEBUG] Prompt: {prompt}")
                    
                    wav_path = item_dir / wav_filename
                    
                    # Resume support: skip if already exists
                    if wav_path.exists():
                        print(f"[INFO] Exists, skip: {wav_path}")
                        continue

                    # 通常速度でTTS生成
                    pcm = generate_tts_single_speaker(client, prompt, DEFAULT_VOICE)
                    if not pcm:
                        print(f"[WARN] No audio returned for sentence {sentence_index} of part '{p}' in {base_name}. Skipping.")
                        continue
                    
                    # 速度調整を含む後処理でWAVファイル作成
                    write_wav_pcm16(wav_path, pcm, 
                                   add_silence=ADD_SILENCE_PADDING, 
                                   silence_duration=SILENCE_DURATION,
                                   speed_multiplier=SPEED_MULTIPLIER)
                    print(f"[INFO] Saved: {wav_path}")
                    part_wavs.append(wav_path)
            # Concatenation disabled per requirement
        processed_count += 1
        if processed_count < total_rows:
            print("[INFO] Sleeping 30s between rows to throttle RPM...")
            time.sleep(30)
    print(f"[INFO] Done. Outputs under: {out_root.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=str, default=None, help="入力CSVファイルパス")
    parser.add_argument("--start-row", type=int, default=None, help="処理開始行番号（1始まり、ヘッダ除く）")
    parser.add_argument("--end-row", type=int, default=None, help="処理終了行番号（1始まり、含む）")
    parser.add_argument("--start-col", type=int, default=None, help="処理開始列番号（1始まり、ヘッダ含む）")
    parser.add_argument("--end-col", type=int, default=None, help="処理終了列番号（1始まり、含む、ヘッダ含む）")
    parser.add_argument("--speed-multiplier", type=float, default=None, help="話速倍率（例: 1.25）")
    parser.add_argument("--suffix", type=str, default="", help="出力ファイル名の末尾に付与する文字列（例: temp0_7）")
    parser.add_argument("--temperature", type=float, default=None, help="Gemini生成のtemperatureを上書き（0.0-2.0）")
    args = parser.parse_args()

    # グローバル設定の上書き
    if args.temperature is not None:
        # 安全域にクランプ
        t = max(0.0, min(2.0, float(args.temperature)))
        globals()["TEMPERATURE"] = t
        print(f"[INFO] TEMPERATURE overridden to {t}")

    # 末尾サフィックスを環境変数で渡して生成側の命名に反映（簡便対応）
    if args.suffix:
        os.environ["TTS_FILENAME_SUFFIX"] = args.suffix

    main(start_row=args.start_row, end_row=args.end_row, input_csv=args.input_csv, start_col=args.start_col, end_col=args.end_col, speed_multiplier=args.speed_multiplier)
