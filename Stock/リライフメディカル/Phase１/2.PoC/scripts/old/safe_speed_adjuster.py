#!/usr/bin/env python3
"""
安全な音声速度調整スクリプト（ホワイトノイズ対策版）
pydubのみを使用した確実な処理
"""

import argparse
import os
from pathlib import Path
from typing import List, Optional

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
    print("[INFO] pydub is available")
except ImportError:
    HAS_PYDUB = False
    print("[ERROR] pydub is required for this script")
    exit(1)

def adjust_audio_speed_safe(input_path: Path, output_path: Path, speed_multiplier: float) -> bool:
    """
    安全な速度調整（pydubのみ使用、ピッチは変わるが確実）
    """
    try:
        # 音声ファイルを読み込み
        audio = AudioSegment.from_wav(str(input_path))
        
        print(f"[DEBUG] Original: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels}ch, {audio.sample_width*8}bit")
        
        # 速度調整（シンプルで確実な方法）
        if abs(speed_multiplier - 1.0) > 0.001:
            # フレームレートを調整して速度変更
            adjusted_audio = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed_multiplier)
            })
            # 元のフレームレートに戻す（これで速度が変わる）
            adjusted_audio = adjusted_audio.set_frame_rate(audio.frame_rate)
            
            print(f"[DEBUG] Adjusted: {len(adjusted_audio)}ms, speed={speed_multiplier:.2f}x")
        else:
            adjusted_audio = audio
        
        # 出力ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # WAVファイルとして保存
        adjusted_audio.export(str(output_path), format="wav")
        
        print(f"[SUCCESS] {input_path.name} -> {output_path.name} ({speed_multiplier:.2f}x)")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to adjust {input_path.name}: {e}")
        return False

def find_wav_files(directory: Path) -> List[Path]:
    """
    指定ディレクトリ内のWAVファイルを再帰的に検索
    """
    wav_files = []
    if directory.is_file() and directory.suffix.lower() == '.wav':
        wav_files.append(directory)
    elif directory.is_dir():
        wav_files.extend(directory.rglob('*.wav'))
    return sorted(wav_files)

def main():
    parser = argparse.ArgumentParser(
        description="音声ファイルの速度を安全に調整します（ピッチは変わります）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一ファイルを1.2倍速に
  python safe_speed_adjuster.py input.wav --speed 1.2
  
  # ディレクトリ内の全WAVファイルを1.2倍速に
  python safe_speed_adjuster.py tts_outputs/011_マスク... --speed 1.2
        """
    )
    
    parser.add_argument(
        "input_path",
        help="入力ファイルまたはディレクトリのパス"
    )
    
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=1.2,
        help="速度倍率（デフォルト: 1.2）"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="出力ディレクトリ（デフォルト: 入力パス + '_safe_adjusted'）"
    )
    
    parser.add_argument(
        "--suffix",
        default="_1.2x_safe",
        help="出力ファイル名に追加するサフィックス（デフォルト: '_1.2x_safe'）"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="既存ファイルを上書きする"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    if not input_path.exists():
        print(f"[ERROR] Input path does not exist: {input_path}")
        return 1
    
    # 出力ディレクトリを決定
    if args.output:
        output_dir = Path(args.output)
    else:
        if input_path.is_file():
            output_dir = input_path.parent / f"{input_path.stem}_safe_adjusted"
        else:
            output_dir = input_path.parent / f"{input_path.name}_safe_adjusted"
    
    # WAVファイルを検索
    wav_files = find_wav_files(input_path)
    
    if not wav_files:
        print(f"[ERROR] No WAV files found in: {input_path}")
        return 1
    
    print(f"[INFO] Found {len(wav_files)} WAV file(s)")
    print(f"[INFO] Speed multiplier: {args.speed:.2f}x")
    print(f"[INFO] Output directory: {output_dir}")
    print(f"[INFO] Using safe pydub-only processing (pitch will change)")
    
    # 処理実行
    success_count = 0
    
    for wav_file in wav_files:
        # 出力ファイル名を生成
        relative_path = wav_file.relative_to(input_path if input_path.is_dir() else input_path.parent)
        output_file = output_dir / relative_path.parent / f"{relative_path.stem}{args.suffix}.wav"
        
        # 既存ファイルのチェック
        if output_file.exists() and not args.overwrite:
            print(f"[SKIP] Already exists: {output_file.name}")
            continue
        
        # 速度調整実行
        success = adjust_audio_speed_safe(wav_file, output_file, args.speed)
        
        if success:
            success_count += 1
    
    print(f"\n[INFO] Processing complete!")
    print(f"[INFO] Successfully processed: {success_count}/{len(wav_files)} files")
    print(f"[INFO] Output directory: {output_dir.resolve()}")
    
    return 0

if __name__ == "__main__":
    exit(main())
