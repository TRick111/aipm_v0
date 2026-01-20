#!/usr/bin/env python3
"""
POSデータをEAT IN / TAKE OUTで分割
"""

import csv

INPUT_FILE = "transformed_pos_data.csv"
OUTPUT_EATIN = "transformed_pos_data_eatin.csv"
OUTPUT_TAKEOUT = "transformed_pos_data_takeout.csv"
ENCODING = "utf-8"

def main():
    print(f"読み込み中: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding=ENCODING) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    print(f"  総データ行数: {len(rows)}")
    
    # 分割
    eatin_rows = []
    takeout_rows = []
    other_rows = []
    
    for row in rows:
        category1 = row.get("D.商品カテゴリ1", "")
        if category1 == "EAT IN":
            eatin_rows.append(row)
        elif category1 == "TAKE OUT":
            takeout_rows.append(row)
        else:
            other_rows.append(row)
    
    print(f"\n分割結果:")
    print(f"  EAT IN: {len(eatin_rows)}行")
    print(f"  TAKE OUT: {len(takeout_rows)}行")
    print(f"  その他: {len(other_rows)}行（シェアデリ、定食など）")
    
    # EAT IN出力
    print(f"\n出力中: {OUTPUT_EATIN}")
    with open(OUTPUT_EATIN, "w", encoding=ENCODING, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(eatin_rows)
    
    # TAKE OUT出力
    print(f"出力中: {OUTPUT_TAKEOUT}")
    with open(OUTPUT_TAKEOUT, "w", encoding=ENCODING, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(takeout_rows)
    
    print("\n完了!")

if __name__ == "__main__":
    main()
