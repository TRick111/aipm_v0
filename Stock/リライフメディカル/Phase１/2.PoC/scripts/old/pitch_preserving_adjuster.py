#!/usr/bin/env python3
"""
ピッチ保持速度調整スクリプト（改良版）
より安定したアルゴリズムを使用
"""

import argparse
import numpy as np
from pathlib import Path
from typing import List, Optional

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("[ERROR] pydub is required")
    exit(1)

def pitch_shift_semitones(audio_segment, semitones):
    """
    ピッチシフト（半音単位）
    """
    # 半音 = 2^(1/12) の比率
    ratio = 2 ** (semitones / 12.0)
    
    # フレームレートを変更してピッチシフト
    shifted = audio_segment._spawn(audio_segment.raw_data, overrides={
        "frame_rate": int(audio_segment.frame_rate * ratio)
    })
    
    # 元のフレームレートに戻す
    return shifted.set_frame_rate(audio_segment.frame_rate)

def speed_change_with_pitch_correction(audio_segment, speed_multiplier):
    """
    速度変更 + ピッチ補正
    """
    # 1. 速度変更（ピッチも変わる）
    speed_changed = audio_segment._spawn(audio_segment.raw_data, overrides={
        "frame_rate": int(audio_segment.frame_rate * speed_multiplier)
    }).set_frame_rate(audio_segment.frame_rate)
    
    # 2. ピッチを元に戻す補正
    # speed_multiplier倍高くなったピッチを元に戻す
    semitones_to_correct = -12 * np.log2(speed_multiplier)
    
    # 3. ピッチシフトで補正
    corrected = pitch_shift_semitones(speed_changed, semitones_to_correct)
    
    return corrected

def overlap_add_stretch(audio_segment, stretch_factor):
    """
    オーバーラップ・アド法による時間伸縮
    """
    # 音声データを取得
    samples = np.array(audio_segment.get_array_of_samples())
    
    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2))
        # ステレオの場合は左チャンネルのみ処理（簡略化）
        samples = samples[:, 0]
    
    # パラメータ
    frame_size = 1024
    hop_size = frame_size // 4
    
    # 出力サイズ計算
    input_length = len(samples)
    output_length = int(input_length / stretch_factor)
    
    # 出力バッファ
    output = np.zeros(output_length)
    
    # オーバーラップ・アド処理
    input_pos = 0
    output_pos = 0
    
    while output_pos + frame_size < output_length and input_pos + frame_size < input_length:
        # フレーム抽出
        frame = samples[input_pos:input_pos + frame_size]
        
        # ウィンドウ適用
        windowed_frame = frame * np.hanning(frame_size)
        
        # オーバーラップして加算
        if output_pos + frame_size <= output_length:
            output[output_pos:output_pos + frame_size] += windowed_frame
        
        # 位置更新
        input_pos += int(hop_size * stretch_factor)
        output_pos += hop_size
    
    # AudioSegmentに戻す
    output_int = np.clip(output * 32767, -32768, 32767).astype(np.int16)
    
    return AudioSegment(
        output_int.tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width,
        channels=1  # モノラルに変換
    )

def adjust_speed_pitch_preserving(input_path: Path, output_path: Path, speed_multiplier: float, method: str = "correction") -> bool:
    """
    ピッチ保持速度調整
    """
    try:
        # 音声ファイルを読み込み
        audio = AudioSegment.from_wav(str(input_path))
        
        print(f"[DEBUG] Original: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels}ch")
        
        if abs(speed_multiplier - 1.0) < 0.001:
            adjusted_audio = audio
        else:
            if method == "correction":
                # 方法1: 速度変更 + ピッチ補正
                adjusted_audio = speed_change_with_pitch_correction(audio, speed_multiplier)
                print(f"[DEBUG] Using pitch correction method")
                
            elif method == "overlap_add":
                # 方法2: オーバーラップ・アド法
                adjusted_audio = overlap_add_stretch(audio, speed_multiplier)
                print(f"[DEBUG] Using overlap-add method")
                
            else:
                # フォールバック: シンプル版
                adjusted_audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed_multiplier)
                }).set_frame_rate(audio.frame_rate)
                print(f"[DEBUG] Using simple method (pitch will change)")
        
        print(f"[DEBUG] Adjusted: {len(adjusted_audio)}ms, speed={speed_multiplier:.2f}x")
        
        # 出力ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # WAVファイルとして保存
        adjusted_audio.export(str(output_path), format="wav")
        
        print(f"[SUCCESS] {input_path.name} -> {output_path.name} ({speed_multiplier:.2f}x, {method})")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to adjust {input_path.name}: {e}")
        return False

def find_wav_files(directory: Path) -> List[Path]:
    """WAVファイル検索"""
    wav_files = []
    if directory.is_file() and directory.suffix.lower() == '.wav':
        wav_files.append(directory)
    elif directory.is_dir():
        wav_files.extend(directory.rglob('*.wav'))
    return sorted(wav_files)

def main():
    parser = argparse.ArgumentParser(
        description="ピッチ保持音声速度調整",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ピッチ補正方式
  python pitch_preserving_adjuster.py input.wav --speed 1.2 --method correction
  
  # オーバーラップ・アド方式
  python pitch_preserving_adjuster.py input.wav --speed 1.2 --method overlap_add
        """
    )
    
    parser.add_argument("input_path", help="入力ファイルまたはディレクトリ")
    parser.add_argument("--speed", "-s", type=float, default=1.2, help="速度倍率")
    parser.add_argument("--method", choices=["correction", "overlap_add", "simple"], 
                       default="correction", help="処理方式")
    parser.add_argument("--suffix", default="_pitch_preserved", help="出力ファイルサフィックス")
    parser.add_argument("--output", "-o", help="出力ディレクトリ")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"[ERROR] Input path does not exist: {input_path}")
        return 1
    
    # 出力ディレクトリ決定
    if args.output:
        output_dir = Path(args.output)
    else:
        if input_path.is_file():
            output_dir = input_path.parent / f"{input_path.stem}_pitch_preserved"
        else:
            output_dir = input_path.parent / f"{input_path.name}_pitch_preserved"
    
    # WAVファイル検索
    wav_files = find_wav_files(input_path)
    
    if not wav_files:
        print(f"[ERROR] No WAV files found")
        return 1
    
    print(f"[INFO] Found {len(wav_files)} files")
    print(f"[INFO] Speed: {args.speed:.2f}x, Method: {args.method}")
    print(f"[INFO] Output: {output_dir}")
    
    # 処理実行
    success_count = 0
    
    for wav_file in wav_files:
        relative_path = wav_file.relative_to(input_path if input_path.is_dir() else input_path.parent)
        output_file = output_dir / relative_path.parent / f"{relative_path.stem}{args.suffix}.wav"
        
        success = adjust_speed_pitch_preserving(wav_file, output_file, args.speed, args.method)
        if success:
            success_count += 1
    
    print(f"\n[INFO] Complete: {success_count}/{len(wav_files)} files")
    return 0

if __name__ == "__main__":
    exit(main())
