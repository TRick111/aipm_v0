#!/usr/bin/env python3
"""
Gemini-TTS用のTTSスクリプト（prompt/text分離版）
Google Cloud Text-to-Speech Gemini-TTSを使用してCSVから音声を生成

使用例:
python tts-from-csv-gemini.py お役立ち情報台本_rewritten2.csv --target_no 11 --start_col 3 --end_col 9
"""

import argparse
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
from google.cloud import texttospeech

# 環境変数を読み込み
load_dotenv()

# ===== 設定 =====
# Gemini-TTSモデル設定
MODEL_NAME = "gemini-2.5-pro-preview-tts"  # or "gemini-2.5-flash-preview-tts"
DEFAULT_VOICE = "Sulafat"  # 女性の声
LANGUAGE_CODE = "en-US"

# 音声設定
AUDIO_ENCODING = texttospeech.AudioEncoding.LINEAR16  # WAV形式
WAV_CHANNELS = 1
WAV_RATE = 24000
WAV_SAMPLE_WIDTH = 2

# 処理設定
PART_COLS = ["フック（0-5秒）", "共感（5-12秒）", "前提知識（12-21秒）", "メイン解説（21-30秒）", "解説まとめ（30-32秒）", "実践（32-44秒）", "CTA（42-45秒）"]
SPEED_MULTIPLIER = 1.0  # プロンプトで速度調整するため後処理は無効
ADD_SILENCE_PADDING = True
SILENCE_DURATION = 0.5

# パート別スタイルプロンプト（1.15倍速指定込み）
PART_STYLE_PROMPTS = {
    "フック（0-5秒）": "Say the following in an energetic and catchy way to grab attention. Speak at 1.15x normal speed.",
    "共感（5-12秒）": "Say the following in a warm and understanding way, showing empathy. Speak at 1.15x normal speed.",
    "前提知識（12-21秒）": "Say the following in a clear and informative way, as if explaining basics. Speak at 1.15x normal speed.",
    "メイン解説（21-30秒）": "Say the following in a professional and detailed way, as the main explanation. Speak at 1.15x normal speed.",
    "解説まとめ（30-32秒）": "Say the following in a conclusive and summarizing way. Speak at 1.15x normal speed.",
    "実践（32-44秒）": "Say the following in an encouraging and practical way, motivating action. Speak at 1.15x normal speed.",
    "CTA（42-45秒）": "Say the following in a friendly and inviting way, encouraging engagement. Speak at 1.15x normal speed."
}

# pydub利用可能性チェック
try:
    from pydub import AudioSegment
    HAS_PYDUB = True
    print("[INFO] pydub is available for high-quality speed adjustment")
except ImportError:
    HAS_PYDUB = False
    print("[INFO] pydub not available, using simple speed adjustment")

# ===== ヘルパー関数 =====

def split_text_by_sentences(text: str) -> List[str]:
    """句点、感嘆符、疑問符で区切って一文ずつに分割する"""
    if not text.strip():
        return []
    
    # 句点、感嘆符、疑問符で分割（日本語・英語両方対応）
    sentences = re.split(r'([。！？!?])', text)
    result = []
    
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i].strip()
            if sentence:
                # 句点等を付加
                if i + 1 < len(sentences) and sentences[i + 1] in '。！？!?':
                    sentence += sentences[i + 1]
                result.append(sentence)
    
    # 空文字列を除去
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
    """PCMデータをWAVファイルとして保存（速度調整・無音パディング含む）"""
    import wave
    
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


def build_gemini_prompt_and_text(part_name: str, text: str) -> tuple[str, str]:
    """
    Gemini-TTS用のpromptとtextを構築
    Returns: (prompt, text)
    """
    # パート別のスタイルプロンプトを取得
    prompt = PART_STYLE_PROMPTS.get(part_name, "Say the following in a natural way")
    
    # テキストはそのまま使用
    clean_text = text.strip()
    
    return prompt, clean_text


def generate_tts_gemini(client: texttospeech.TextToSpeechClient, 
                       prompt: str, text: str, voice_name: str) -> Optional[bytes]:
    """
    Gemini-TTSを使用してTTS生成（prompt/text分離版）
    """
    try:
        # SynthesisInputでpromptとtextを分離
        synthesis_input = texttospeech.SynthesisInput(
            text=text,
            prompt=prompt
        )
        
        # 音声選択
        voice = texttospeech.VoiceSelectionParams(
            language_code=LANGUAGE_CODE,
            name=voice_name,
            model_name=MODEL_NAME
        )
        
        # 音声設定
        audio_config = texttospeech.AudioConfig(
            audio_encoding=AUDIO_ENCODING
        )
        
        # TTS実行
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content
        
    except Exception as e:
        print(f"[ERROR] Gemini-TTS generation failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="CSV to TTS using Gemini-TTS (prompt/text separated)")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("--target_no", type=int, help="Target row number (e.g., 11)")
    parser.add_argument("--start_col", type=int, default=3, help="Start column index (0-based)")
    parser.add_argument("--end_col", type=int, default=9, help="End column index (0-based, exclusive)")
    parser.add_argument("--output_dir", default="tts_outputs", help="Output directory")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice name")
    parser.add_argument("--model", default=MODEL_NAME, help="Gemini-TTS model name")
    parser.add_argument("--speed", type=float, default=SPEED_MULTIPLIER, help="Speed multiplier")
    
    args = parser.parse_args()
    
    # Google API Key認証確認
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] GOOGLE_API_KEY not found. Please set GOOGLE_API_KEY in .env or environment variable.")
        return
    print("[INFO] GOOGLE_API_KEY loaded.")
    
    # CSVファイル読み込み
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"[ERROR] CSV file not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    print(f"[INFO] Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
    print(f"[INFO] Columns: {list(df.columns)}")
    
    # 対象行の特定
    if args.target_no:
        target_rows = df[df.iloc[:, 0] == args.target_no]  # No.列で検索
        if target_rows.empty:
            print(f"[ERROR] No.{args.target_no} not found in CSV")
            return
        df = target_rows
        print(f"[INFO] Processing No.{args.target_no}")
    
    # 出力ディレクトリ作成
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Text-to-Speechクライアント初期化（APIキー使用）
    try:
        from google.cloud import texttospeech
        from google.oauth2 import service_account
        import tempfile
        import json
        
        # APIキーを使用した認証（サービスアカウントキーの代替）
        # 注意: Google Cloud Text-to-Speech APIは通常サービスアカウントを使用
        # APIキーでの直接認証は制限される場合があります
        
        # 環境変数でAPIキーを設定
        os.environ['GOOGLE_API_KEY'] = api_key
        
        # クライアントを初期化
        client = texttospeech.TextToSpeechClient()
        
        print("[INFO] Google Cloud Text-to-Speech client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize TTS client: {e}")
        print("[INFO] Google Cloud Text-to-Speech requires service account credentials.")
        print("[INFO] Consider using the GenAI API version (tts-from-csv.py) instead.")
        return
    
    # 使用する列を決定
    if args.end_col > len(df.columns):
        args.end_col = len(df.columns)
    
    part_columns = df.columns[args.start_col:args.end_col]
    print(f"[INFO] Using columns: {list(part_columns)}")
    
    # 各行を処理
    processed_count = 0
    total_rows = len(df)
    
    for idx, row in df.iterrows():
        video_num = row.iloc[0] if not pd.isna(row.iloc[0]) else f"row_{idx}"
        title = row.iloc[1] if len(row) > 1 and not pd.isna(row.iloc[1]) else "untitled"
        
        # ファイル名用の短縮タイトル
        title_short = re.sub(r"[^\w\s]", "", str(title))[:20]
        video_num_str = f"{int(video_num):03d}" if isinstance(video_num, (int, float)) else str(video_num)
        base_name = f"{video_num_str}_{title_short}"
        
        # アイテムディレクトリ作成
        item_dir = output_dir / base_name
        item_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[INFO] Processing {base_name} ({processed_count + 1}/{total_rows})")
        
        # 各パートを処理
        for part_index, column_name in enumerate(part_columns, start=1):
            text = "" if pd.isna(row[column_name]) else str(row[column_name])
            if not text.strip():
                continue
            
            # 文単位で分割
            sentences = split_text_by_sentences(text)
            print(f"[INFO] Part '{column_name}' split into {len(sentences)} sentences")
            
            # パート名をクリーンアップ
            clean_part = re.sub(r"[（(][^）)]*[）)]", "", str(column_name)).strip()
            
            for sentence_index, sentence_text in enumerate(sentences, start=1):
                # プロンプトとテキストを構築
                prompt, clean_text = build_gemini_prompt_and_text(column_name, sentence_text)
                
                # ファイル名決定
                if len(sentences) > 1:
                    wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}_{sentence_index:02d}.wav"
                    print(f"[INFO] Generating TTS for part '{column_name}' sentence {sentence_index}/{len(sentences)} in {base_name}...")
                else:
                    wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}.wav"
                    print(f"[INFO] Generating TTS for part '{column_name}' in {base_name}...")
                
                print(f"[DEBUG] Prompt: {prompt}")
                print(f"[DEBUG] Text: {clean_text}")
                
                wav_path = item_dir / wav_filename
                
                # 既存ファイルをスキップ
                if wav_path.exists():
                    print(f"[INFO] Exists, skip: {wav_path}")
                    continue
                
                # Gemini-TTSで音声生成
                audio_content = generate_tts_gemini(client, prompt, clean_text, args.voice)
                if not audio_content:
                    print(f"[WARN] No audio returned for sentence {sentence_index} of part '{column_name}' in {base_name}. Skipping.")
                    continue
                
                # 速度調整・無音パディングを含む保存
                write_wav_pcm16(wav_path, audio_content,
                               add_silence=ADD_SILENCE_PADDING,
                               silence_duration=SILENCE_DURATION,
                               speed_multiplier=args.speed)
                print(f"[INFO] Saved: {wav_path}")
        
        processed_count += 1
        if processed_count < total_rows:
            print("[INFO] Sleeping 30s between rows to throttle RPM...")
            time.sleep(30)
    
    print(f"\n[INFO] Processing complete! Generated audio files in {output_dir}")


if __name__ == "__main__":
    main()
