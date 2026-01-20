#!/usr/bin/env python3
"""
POSデータCSVマージスクリプト
複数のCSVファイル（Shift-JIS）を1つにマージする
"""

import os
import glob

INPUT_DIR = "input"
OUTPUT_FILE = "merged_pos_data.csv"
ENCODING = "cp932"
HEADER_LINES = 11  # 1-10行目はメタ情報、11行目がCSVヘッダー

def merge_csv_files():
    # 入力ファイルを取得（ソートして順番を保証）
    csv_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.csv")))
    
    if not csv_files:
        print("CSVファイルが見つかりません")
        return
    
    print(f"マージ対象: {len(csv_files)} ファイル")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")
    
    merged_lines = []
    csv_header = None
    total_data_rows = 0
    
    for i, csv_file in enumerate(csv_files):
        with open(csv_file, "r", encoding=ENCODING) as f:
            lines = f.readlines()
        
        if i == 0:
            # 最初のファイル: メタ情報 + ヘッダー + データ
            merged_lines.extend(lines[:HEADER_LINES])  # メタ情報 + CSVヘッダー
            csv_header = lines[HEADER_LINES - 1].strip()  # 11行目
            data_lines = lines[HEADER_LINES:]  # 12行目以降
        else:
            # 2番目以降: データ行のみ
            # ヘッダーが一致するか確認
            file_header = lines[HEADER_LINES - 1].strip()
            if file_header != csv_header:
                print(f"警告: {os.path.basename(csv_file)} のヘッダーが異なります")
            data_lines = lines[HEADER_LINES:]  # 12行目以降
        
        merged_lines.extend(data_lines)
        total_data_rows += len(data_lines)
        print(f"  {os.path.basename(csv_file)}: {len(data_lines)} 行")
    
    # 出力
    with open(OUTPUT_FILE, "w", encoding=ENCODING) as f:
        f.writelines(merged_lines)
    
    print(f"\n完了: {OUTPUT_FILE}")
    print(f"  メタ情報 + ヘッダー: {HEADER_LINES} 行")
    print(f"  データ行: {total_data_rows} 行")
    print(f"  合計: {HEADER_LINES + total_data_rows} 行")

if __name__ == "__main__":
    merge_csv_files()
