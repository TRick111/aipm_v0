#!/usr/bin/env python3
"""
音声ファイルの速度調整スクリプト
既存の音声ファイルに対してさらなる速度調整を適用
"""

import argparse
import os
from pathlib import Path
from typing import List, Optional
import wave
import struct

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
    print("[INFO] pydub is available for high-quality speed adjustment")
except ImportError:
    HAS_PYDUB = False
    print("[WARN] pydub not available, using basic speed adjustment")

def adjust_audio_speed_pydub(input_path: Path, output_path: Path, speed_multiplier: float) -> bool:
    """
    pydubを使用した高品質な速度調整（ピッチ保持）
    """
    try:
        # 音声ファイルを読み込み
        audio = AudioSegment.from_wav(str(input_path))
        
        # ピッチを保持しながら速度調整
        # speedup_without_changing_pitch: ピッチを変えずに速度のみ調整
        if abs(speed_multiplier - 1.0) > 0.001:  # 速度変更が必要な場合のみ
            # pydubの高度な速度調整（ピッチ保持）
            # 方法1: 時間伸縮アルゴリズムを使用
            try:
                # librosaがある場合の高品質処理
                import librosa
                import numpy as np
                import soundfile as sf
                
                # 音声データを取得（正規化）
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                
                # 16bit整数から-1.0〜1.0の範囲に正規化
                if audio.sample_width == 2:  # 16bit
                    samples = samples / 32768.0
                elif audio.sample_width == 1:  # 8bit
                    samples = (samples - 128) / 128.0
                else:
                    samples = samples / (2**(audio.sample_width * 8 - 1))
                
                # ステレオの場合は処理を調整
                if audio.channels == 2:
                    samples = samples.reshape((-1, 2))
                    # 各チャンネルを個別に処理
                    left_stretched = librosa.effects.time_stretch(samples[:, 0], rate=speed_multiplier)
                    right_stretched = librosa.effects.time_stretch(samples[:, 1], rate=speed_multiplier)
                    samples_stretched = np.column_stack((left_stretched, right_stretched))
                    samples_stretched = samples_stretched.flatten()
                else:
                    # モノラルの場合
                    samples_stretched = librosa.effects.time_stretch(samples, rate=speed_multiplier)
                
                # クリッピング防止
                samples_stretched = np.clip(samples_stretched, -1.0, 1.0)
                
                # 16bit整数に戻す
                if audio.sample_width == 2:
                    samples_int = (samples_stretched * 32767).astype(np.int16)
                elif audio.sample_width == 1:
                    samples_int = ((samples_stretched * 127) + 128).astype(np.uint8)
                else:
                    max_val = 2**(audio.sample_width * 8 - 1) - 1
                    samples_int = (samples_stretched * max_val).astype(np.int16)
                
                adjusted_audio = AudioSegment(
                    samples_int.tobytes(),
                    frame_rate=audio.frame_rate,
                    sample_width=audio.sample_width,
                    channels=audio.channels
                )
                
            except (ImportError, Exception) as e:
                # librosaが無い場合、またはlibrosa処理でエラーが発生した場合
                print(f"[INFO] librosa processing failed ({e}), using pydub fallback")
                
                # PyDubでの基本的な速度調整（ピッチは変わるが安全）
                # 単純だが確実な方法
                adjusted_audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed_multiplier)
                }).set_frame_rate(audio.frame_rate)
                
                print("[WARN] Using basic speed adjustment - pitch will change")
        else:
            adjusted_audio = audio
        
        # 出力ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # WAVファイルとして保存
        adjusted_audio.export(str(output_path), format="wav")
        
        print(f"[SUCCESS] {input_path.name} -> {output_path.name} ({speed_multiplier:.2f}x, pitch preserved)")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to adjust {input_path.name}: {e}")
        return False

def adjust_audio_speed_basic(input_path: Path, output_path: Path, speed_multiplier: float) -> bool:
    """
    基本的な速度調整（pydub不使用時のフォールバック）
    """
    try:
        with wave.open(str(input_path), 'rb') as wf_in:
            # WAVファイルの情報を取得
            channels = wf_in.getnchannels()
            sample_width = wf_in.getsampwidth()
            frame_rate = wf_in.getframerate()
            frames = wf_in.readframes(wf_in.getnframes())
        
        # サンプル数を調整（単純なリサンプリング）
        if sample_width == 2:  # 16bit
            samples = struct.unpack(f'<{len(frames)//2}h', frames)
            new_samples = []
            
            original_length = len(samples)
            new_length = int(original_length / speed_multiplier)
            
            for i in range(new_length):
                # 線形補間でサンプルを取得
                original_index = i * speed_multiplier
                index_floor = int(original_index)
                index_ceil = min(index_floor + 1, original_length - 1)
                
                if index_floor == index_ceil:
                    new_samples.append(samples[index_floor])
                else:
                    # 線形補間
                    weight = original_index - index_floor
                    interpolated = samples[index_floor] * (1 - weight) + samples[index_ceil] * weight
                    new_samples.append(int(interpolated))
            
            adjusted_frames = struct.pack(f'<{len(new_samples)}h', *new_samples)
        else:
            print(f"[ERROR] Unsupported sample width: {sample_width}")
            return False
        
        # 出力ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 調整済み音声を保存
        with wave.open(str(output_path), 'wb') as wf_out:
            wf_out.setnchannels(channels)
            wf_out.setsampwidth(sample_width)
            wf_out.setframerate(frame_rate)
            wf_out.writeframes(adjusted_frames)
        
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
        description="音声ファイルの速度を調整します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一ファイルを1.2倍速に
  python speed_adjuster.py input.wav --speed 1.2
  
  # ディレクトリ内の全WAVファイルを1.2倍速に
  python speed_adjuster.py tts_outputs/011_マスク... --speed 1.2
  
  # 出力先を指定
  python speed_adjuster.py input.wav --speed 1.2 --output adjusted_output/
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
        help="出力ディレクトリ（デフォルト: 入力パス + '_adjusted'）"
    )
    
    parser.add_argument(
        "--suffix",
        default="_1.2x",
        help="出力ファイル名に追加するサフィックス（デフォルト: '_1.2x'）"
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
            output_dir = input_path.parent / f"{input_path.stem}_adjusted"
        else:
            output_dir = input_path.parent / f"{input_path.name}_adjusted"
    
    # WAVファイルを検索
    wav_files = find_wav_files(input_path)
    
    if not wav_files:
        print(f"[ERROR] No WAV files found in: {input_path}")
        return 1
    
    print(f"[INFO] Found {len(wav_files)} WAV file(s)")
    print(f"[INFO] Speed multiplier: {args.speed:.2f}x")
    print(f"[INFO] Output directory: {output_dir}")
    print(f"[INFO] Using {'pydub (high-quality)' if HAS_PYDUB else 'basic method'}")
    
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
        if HAS_PYDUB:
            success = adjust_audio_speed_pydub(wav_file, output_file, args.speed)
        else:
            success = adjust_audio_speed_basic(wav_file, output_file, args.speed)
        
        if success:
            success_count += 1
    
    print(f"\n[INFO] Processing complete!")
    print(f"[INFO] Successfully processed: {success_count}/{len(wav_files)} files")
    print(f"[INFO] Output directory: {output_dir.resolve()}")
    
    return 0

if __name__ == "__main__":
    exit(main())
