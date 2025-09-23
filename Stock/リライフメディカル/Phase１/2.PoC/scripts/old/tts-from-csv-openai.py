#!/usr/bin/env python3
"""
OpenAI TTS APIを使用したCSVからの音声生成スクリプト
速度指定機能でピッチ変化なしの高速音声を生成
"""

import argparse
import io
import os
import pandas as pd
import re
import time
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("[ERROR] openai package is required. Install with: pip install openai")
    exit(1)

# 設定
PART_COLS = ["フック（0-5秒）", "共感（5-12秒）", "前提知識（12-21秒）", "メイン解説（21-30秒）", "解説まとめ（30-32秒）", "実践（32-44秒）", "CTA（42-45秒）"]
SPEED_MULTIPLIER = 1.5  # デフォルト速度（1.5倍速）

# OpenAI TTS設定
OPENAI_MODEL = "tts-1"  # または "tts-1-hd" (高品質版)
OPENAI_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
OPENAI_FORMAT = "wav"   # mp3, opus, aac, flac, wav, pcm

def load_openai_client():
    """OpenAI クライアントを初期化"""
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables")
        print("[INFO] Please set OPENAI_API_KEY in your .env file or environment")
        return None
    
    try:
        client = openai.OpenAI(api_key=api_key)
        print(f"[INFO] OpenAI client initialized successfully")
        return client
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}")
        return None

def generate_tts_openai(client: openai.OpenAI, text: str, speed: float = 1.0, voice: str = "alloy") -> Optional[bytes]:
    """
    OpenAI TTS APIで音声生成
    """
    try:
        response = client.audio.speech.create(
            model=OPENAI_MODEL,
            voice=voice,
            input=text,
            speed=speed,
            response_format=OPENAI_FORMAT
        )
        
        return response.content
        
    except Exception as e:
        print(f"[ERROR] OpenAI TTS generation failed: {e}")
        return None

def split_text_by_sentences(text: str) -> List[str]:
    """文章を句点で分割"""
    if not text.strip():
        return []
    
    # 日本語の句点・疑問符・感嘆符で分割
    sentences = re.split(r'[。！？!?]', text)
    
    # 空文字列を除去し、句点を復元
    result = []
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            # 最後の文以外は句点を追加
            if i < len(sentences) - 1:
                # 元のテキストから対応する句点を見つけて追加
                original_end = text.find(sentence) + len(sentence)
                if original_end < len(text):
                    punctuation = text[original_end]
                    if punctuation in '。！？!?':
                        sentence += punctuation
            result.append(sentence)
    
    return result if result else [text]

def add_silence_to_audio(audio_data: bytes, silence_duration: float = 1.0) -> bytes:
    """音声データの前後に無音を追加"""
    try:
        from pydub import AudioSegment
        
        # 音声データを読み込み
        audio = AudioSegment.from_wav(io.BytesIO(audio_data))
        
        # 無音セグメントを作成（指定秒数）
        silence = AudioSegment.silent(duration=int(silence_duration * 1000))  # ミリ秒に変換
        
        # 前後に無音を追加
        final_audio = silence + audio + silence
        
        # バイト形式で返す
        output_buffer = io.BytesIO()
        final_audio.export(output_buffer, format="wav")
        return output_buffer.getvalue()
        
    except ImportError:
        print("[WARN] pydub not available, skipping silence padding")
        return audio_data
    except Exception as e:
        print(f"[WARN] Failed to add silence: {e}, using original audio")
        return audio_data

def save_audio_file(audio_data: bytes, file_path: Path, add_silence: bool = True, silence_duration: float = 1.0) -> bool:
    """音声データをファイルに保存（無音パディング付き）"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 無音パディングを追加
        if add_silence:
            audio_data = add_silence_to_audio(audio_data, silence_duration)
        
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save audio file {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="OpenAI TTS APIを使用してCSVから音声を生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python tts-from-csv-openai.py input.csv --target_no 11 --speed 1.38
  python tts-from-csv-openai.py input.csv --start_row 1 --end_row 5 --voice nova
        """
    )
    
    parser.add_argument("csv_file", help="入力CSVファイル")
    parser.add_argument("--target_no", type=int, help="特定の番号のみ処理")
    parser.add_argument("--start_row", type=int, help="開始行（1ベース）")
    parser.add_argument("--end_row", type=int, help="終了行（1ベース）")
    parser.add_argument("--start_col", type=int, default=3, help="開始列（0ベース）")
    parser.add_argument("--end_col", type=int, default=9, help="終了列（0ベース）")
    parser.add_argument("--speed", type=float, default=SPEED_MULTIPLIER, 
                       help=f"音声速度（デフォルト: {SPEED_MULTIPLIER}）")
    parser.add_argument("--voice", default=OPENAI_VOICE, 
                       choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer", "ballad", "marin", "sage", "ash", "coral"],
                       help="音声の種類")
    parser.add_argument("--model", default=OPENAI_MODEL, 
                       choices=["tts-1", "tts-1-hd", "gpt-4l-mini-tts", "gpt-4o-mini-tts"],
                       help="使用モデル")
    parser.add_argument("--output", default="tts_outputs_openai", help="出力ディレクトリ")
    parser.add_argument("--suffix", default="", help="ファイル名末尾に追加する文字列")
    
    args = parser.parse_args()
    
    # OpenAI クライアント初期化
    client = load_openai_client()
    if not client:
        return 1
    
    # CSV読み込み
    try:
        df = pd.read_csv(args.csv_file)
        print(f"[INFO] Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        print(f"[INFO] Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return 1
    
    # 処理対象の決定
    if args.target_no:
        # 特定番号のみ
        target_rows = df[df.iloc[:, 0] == args.target_no]
        if target_rows.empty:
            print(f"[ERROR] No.{args.target_no} not found in CSV")
            return 1
        print(f"[INFO] Processing No.{args.target_no}")
    else:
        # 行範囲指定
        start_idx = (args.start_row - 1) if args.start_row else 0
        end_idx = args.end_row if args.end_row else len(df)
        target_rows = df.iloc[start_idx:end_idx]
        print(f"[INFO] Processing rows {start_idx + 1} to {end_idx}")
    
    # パート列の決定
    part_columns = PART_COLS[args.start_col:args.end_col]
    print(f"[INFO] Using columns: {part_columns}")
    
    # 出力ディレクトリ
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[INFO] Output directory: {output_dir}")
    print(f"[INFO] Speed: {args.speed:.2f}x, Voice: {args.voice}, Model: {args.model}")
    
    # 各行を処理
    processed_count = 0
    total_rows = len(target_rows)
    
    for idx, row in target_rows.iterrows():
        video_num = row.iloc[0] if not pd.isna(row.iloc[0]) else f"row_{idx}"
        title = row.iloc[1] if len(row) > 1 and not pd.isna(row.iloc[1]) else "untitled"
        
        # ファイル名用の短縮タイトル（最初の4文字のみ）
        title_clean = re.sub(r"[^\w\s]", "", str(title))
        title_short = title_clean[:4] if len(title_clean) >= 4 else title_clean
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
            
            # 文分割
            sentences = split_text_by_sentences(text)
            print(f"[INFO] Part '{column_name}' split into {len(sentences)} sentences")
            
            # パート名をクリーンアップ
            clean_part = re.sub(r"[（(][^）)]*[）)]", "", str(column_name)).strip()
            
            for sentence_index, sentence_text in enumerate(sentences, start=1):
                # ファイル名決定（suffix対応）
                suffix_part = f"_{args.suffix}" if args.suffix else ""
                if len(sentences) > 1:
                    wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}_{sentence_index:02d}{suffix_part}.wav"
                    print(f"[INFO] Generating TTS for part '{column_name}' sentence {sentence_index}/{len(sentences)} in {base_name}...")
                else:
                    wav_filename = f"{video_num_str}_{title_short}_{part_index:02d}_{clean_part}{suffix_part}.wav"
                    print(f"[INFO] Generating TTS for part '{column_name}' in {base_name}...")
                
                print(f"[DEBUG] Text: {sentence_text}")
                print(f"[DEBUG] Speed: {args.speed:.2f}x")
                
                wav_path = item_dir / wav_filename
                
                # 既存ファイルスキップ
                if wav_path.exists():
                    print(f"[INFO] Exists, skip: {wav_path}")
                    continue
                
                # TTS生成
                audio_data = generate_tts_openai(client, sentence_text, args.speed, args.voice)
                if not audio_data:
                    print(f"[WARN] No audio returned for sentence {sentence_index} of part '{column_name}' in {base_name}. Skipping.")
                    continue
                
                # ファイル保存（1秒の無音パディング付き）
                if save_audio_file(audio_data, wav_path, add_silence=True, silence_duration=1.0):
                    print(f"[INFO] Saved: {wav_path} (with 1s silence padding)")
                else:
                    print(f"[ERROR] Failed to save: {wav_path}")
        
        processed_count += 1
        
        # レート制限対策（OpenAI TTS APIの制限に応じて調整）
        if processed_count < total_rows:
            print("[INFO] Sleeping 2s between rows...")
            time.sleep(2)
    
    print(f"\n[INFO] Processing complete! Generated audio files in {output_dir}")
    return 0

if __name__ == "__main__":
    exit(main())
