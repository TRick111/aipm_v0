import os
import time
import re
import wave
from pathlib import Path
from typing import List, Dict

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
PART_COLS = ["hook", "body1", "body2", "outro"]  # デフォルト
SPEED_MULTIPLIER = 1.18  # 話速倍率（デフォルト1.18x）。CLIで上書き可能

# --- モデル/音声 ---
MODEL_NAME = "gemini-2.5-pro-preview-tts"  # "gemini-2.5-pro-preview-tts" も可
DEFAULT_VOICE = "Sulafat"

# --- 生成パラメータ（★追加） ---
# 公式APIの GenerateContentConfig で指定（AI Studio UI と同趣旨）:
# temperature: 0.0〜2.0（Vertex/AI Studioの一般指針）/ デフォルトは 1.0 付近
TEMPERATURE = 1.2  # ← ここを1.2で固定
TOP_P = 0.9           # 任意：確率質量サンプリング
TOP_K = 40            # 任意：上位K語彙サンプリング
MAX_OUTPUT_TOKENS = None  # 音声生成では通常未指定のままでOK

PART_STYLE_HINTS = {
    "hook":  "Energetic, catchy social-video hook in Japanese.",
    "body1": "Clear, friendly, and informative tone.",
    "body2": "Keep the pace natural; emphasize key nouns.",
    "outro": "Warm and upbeat call-to-action in Japanese."
}

USE_MULTI_SPEAKER_IF_AVAILABLE = True

WAV_RATE = 24000
WAV_CHANNELS = 1
WAV_SAMPLE_WIDTH = 2
# ========================


def safe_slug(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\-.]+", "_", s)
    return s[:80] if s else "item"


def write_wav_pcm16(filename: Path, pcm_bytes: bytes,
                    channels=WAV_CHANNELS, rate=WAV_RATE, sample_width=WAV_SAMPLE_WIDTH):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)


def build_single_speaker_prompt(part_name: str, text: str) -> str:
    hint = PART_STYLE_HINTS.get(part_name, "")
    speed_directive = ""
    if SPEED_MULTIPLIER and abs(SPEED_MULTIPLIER - 1.0) > 1e-6:
        # 日本語と英語の併記で明示（モデルの解釈安定化）
        speed_directive = f"(速度は通常の{SPEED_MULTIPLIER:.2f}倍で話してください / Please speak at approximately {SPEED_MULTIPLIER:.2f}x normal speed)\n\n"
    base = f"{hint}\n\n{speed_directive}{text}" if hint else f"{speed_directive}{text}"
    return base


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


def _extract_audio_bytes(resp) -> bytes | None:
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


def generate_tts_single_speaker(client: genai.Client, text: str, voice_name: str) -> bytes | None:
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=text,
        config=_build_gen_config_for_single(voice_name),
    )
    return _extract_audio_bytes(resp)


def generate_tts_multi_speaker(client: genai.Client,
                               script_with_speaker_lines: str,
                               speaker_to_voice: Dict[str, str]) -> bytes | None:
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
                write_wav_pcm16(wav_path, pcm)
                print(f"[INFO] Saved: {wav_path}")
                part_wavs.append(wav_path)

        else:
            for part_index, p in enumerate(PART_COLS, start=1):
                text = "" if pd.isna(row[p]) else str(row[p])
                if not text.strip():
                    continue
                prompt = build_single_speaker_prompt(p, text)
                print(f"[INFO] Generating TTS for part '{p}' in {base_name}...")
                # Filename: NNN_Title_YY_PartName.wav
                # Clean part name: remove parentheses content like （xx-yy秒） or (xx-yy)
                clean_part = re.sub(r"[（(][^）)]*[）)]", "", str(p)).strip()
                wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}.wav"
                wav_path = item_dir / wav_filename
                # Resume support: skip if already exists
                if wav_path.exists():
                    print(f"[INFO] Exists, skip: {wav_path}")
                    continue

                pcm = generate_tts_single_speaker(client, prompt, DEFAULT_VOICE)
                if not pcm:
                    print(f"[WARN] No audio returned for part '{p}' in {base_name}. Skipping.")
                    continue
                write_wav_pcm16(wav_path, pcm)
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
    args = parser.parse_args()
    main(start_row=args.start_row, end_row=args.end_row, input_csv=args.input_csv, start_col=args.start_col, end_col=args.end_col, speed_multiplier=args.speed_multiplier)
