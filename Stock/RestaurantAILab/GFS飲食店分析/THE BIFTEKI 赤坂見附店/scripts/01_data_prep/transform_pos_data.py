#!/usr/bin/env python3
"""
POSデータ整形スクリプト
- 商品列を商品コードと商品名に分割
- 各商品のベース価格（サブメニューなしの価格）を追加
"""

import csv

INPUT_FILE = "merged_pos_data.csv"
OUTPUT_FILE = "transformed_pos_data.csv"

def detect_encoding(filepath):
    """エンコーディングを自動検出"""
    encodings = ["utf-8", "utf-8-sig", "cp932", "shift_jis"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                f.read(1000)  # 最初の1000文字を読んで確認
            return enc
        except UnicodeDecodeError:
            continue
    return "utf-8"  # デフォルト

def main():
    # 1. エンコーディングを検出してデータを読み込み
    encoding = detect_encoding(INPUT_FILE)
    print(f"読み込み中: {INPUT_FILE} (エンコーディング: {encoding})")
    with open(INPUT_FILE, "r", encoding=encoding) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"  データ行数: {len(rows)}")
    
    # 2. 商品コードを分割してベース価格を収集
    print("ベース価格を収集中...")
    base_prices = {}  # 商品コード -> ベース価格
    
    for row in rows:
        product = row.get("D.商品", "")
        submenu = row.get("D.サブメニュー", "")
        price = row.get("D.価格", "")
        
        # 商品コードを抽出
        if ":" in product:
            product_code = product.split(":")[0]
        else:
            product_code = product
        
        # サブメニューが空の場合、ベース価格として記録
        if submenu == "" and price:
            try:
                price_int = int(price)
                # 既存のベース価格がない、または新しい価格が小さい場合に更新
                if product_code not in base_prices or price_int < base_prices[product_code]:
                    base_prices[product_code] = price_int
            except ValueError:
                pass
    
    print(f"  ベース価格を持つ商品数: {len(base_prices)}")
    
    # 3. データを変換
    print("データを変換中...")
    transformed_rows = []
    
    for row in rows:
        product = row.get("D.商品", "")
        
        # 商品コードと商品名を分割
        if ":" in product:
            parts = product.split(":", 1)
            product_code = parts[0]
            product_name = parts[1] if len(parts) > 1 else ""
        else:
            product_code = product
            product_name = ""
        
        # 新しい行を作成
        new_row = dict(row)
        new_row["D.商品コード"] = product_code
        new_row["D.商品名"] = product_name
        new_row["D.ベース価格"] = base_prices.get(product_code, "")
        
        transformed_rows.append(new_row)
    
    # 4. 新しいカラム順を定義
    original_columns = list(rows[0].keys())
    # D.商品の位置を見つける
    product_idx = original_columns.index("D.商品")
    
    # 新しいカラム順: D.商品の後にD.商品コード、D.商品名を挿入、D.価格の後にD.ベース価格を挿入
    new_columns = []
    for col in original_columns:
        new_columns.append(col)
        if col == "D.商品":
            new_columns.append("D.商品コード")
            new_columns.append("D.商品名")
        elif col == "D.価格":
            new_columns.append("D.ベース価格")
    
    # 5. 出力（UTF-8で出力）
    print(f"出力中: {OUTPUT_FILE} (UTF-8)")
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_columns, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(transformed_rows)
    
    print(f"\n完了!")
    print(f"  出力ファイル: {OUTPUT_FILE}")
    print(f"  カラム追加: D.商品コード, D.商品名, D.ベース価格")
    
    # サンプル出力
    print("\n--- サンプル（最初の5行）---")
    for i, row in enumerate(transformed_rows[:5]):
        print(f"\n行 {i+1}:")
        print(f"  商品: {row['D.商品']}")
        print(f"  商品コード: {row['D.商品コード']}")
        print(f"  商品名: {row['D.商品名']}")
        print(f"  サブメニュー: {row['D.サブメニュー']}")
        print(f"  価格: {row['D.価格']}")
        print(f"  ベース価格: {row['D.ベース価格']}")

if __name__ == "__main__":
    main()
