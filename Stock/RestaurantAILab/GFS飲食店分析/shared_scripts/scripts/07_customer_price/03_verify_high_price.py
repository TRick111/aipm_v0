# -*- coding: utf-8 -*-
"""
客単価が高いケースの検証
本当に一人当たり単価か確認する
"""

import pandas as pd

output_dir = r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\CustomerPriceAnalysis"
orders = pd.read_csv(f"{output_dir}/02_orders_with_price_per_customer.csv")

print("=" * 80)
print("客単価の計算検証")
print("=" * 80)

print("\n【計算式の確認】")
print("客単価 = 小計（会計額）÷ 客数")
print("→ これは「一人当たりの単価」です")

print("\n" + "=" * 80)
print("【客単価 上位20件の詳細】")
print("=" * 80)

top20 = orders.nlargest(20, '客単価')[['伝票番号', '営業日', '曜日', '客数', '小計', '客単価', '総商品数']]
top20['小計÷客数(検算)'] = top20['小計'] / top20['客数']

print(top20.to_string(index=False))

print("\n" + "=" * 80)
print("【客単価 5,000円以上のケース分析】")
print("=" * 80)

high_price = orders[orders['客単価'] >= 5000]
print(f"\n客単価5,000円以上: {len(high_price)}件 ({len(high_price)/len(orders)*100:.2f}%)")

print("\n【客数別の内訳】")
print(high_price['客数'].value_counts().sort_index())

print("\n【曜日別の内訳】")
print(high_price['曜日'].value_counts())

print("\n" + "=" * 80)
print("【客単価 10,000円以上のケース詳細】")
print("=" * 80)

very_high = orders[orders['客単価'] >= 10000]
print(f"\n客単価10,000円以上: {len(very_high)}件")

if len(very_high) > 0:
    print("\n詳細:")
    print(very_high[['伝票番号', '営業日', '曜日', '客数', '小計', '客単価', '総商品数']].to_string(index=False))

# 元データからも確認
print("\n" + "=" * 80)
print("【元データから高単価伝票の商品明細を確認】")
print("=" * 80)

input_path = r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\transformed_pos_data_eatin.csv"
df = pd.read_csv(input_path)

# 最高客単価の伝票を確認
if len(very_high) > 0:
    top_slip = very_high.nlargest(3, '客単価')['伝票番号'].tolist()
    
    for slip in top_slip:
        print(f"\n--- 伝票番号: {slip} ---")
        slip_data = df[df['H.伝票番号'] == slip]
        print(f"客数: {slip_data['H.客数（合計）'].iloc[0]}")
        print(f"小計: {slip_data['H.小計'].iloc[0]:,}円")
        print(f"客単価: {slip_data['H.小計'].iloc[0] / slip_data['H.客数（合計）'].iloc[0]:,.0f}円")
        print(f"\n商品明細:")
        print(slip_data[['D.商品名', 'D.価格']].to_string(index=False))
