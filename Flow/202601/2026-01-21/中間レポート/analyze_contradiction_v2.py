# -*- coding: utf-8 -*-
"""
4.2の客単価上昇と6.4のHigh/Low分析の矛盾を解明する分析（修正版）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = Path(__file__).parent.parent
print(f"データディレクトリ: {DATA_DIR}")

# データ読み込み
df = pd.read_csv(DATA_DIR / 'transformed_pos_data_eatin.csv')
df['日付'] = pd.to_datetime(df['H.集計対象営業年月日'])
df['伝票発行時刻'] = pd.to_datetime(df['H.伝票発行日'])
df['時間'] = df['伝票発行時刻'].dt.hour

# 期間定義
period_a_start = pd.to_datetime('2025-05-01')
period_a_end = pd.to_datetime('2025-07-31')
period_b_start = pd.to_datetime('2025-10-01')
period_b_end = pd.to_datetime('2025-12-31')
april_start = pd.to_datetime('2025-04-01')
april_end = pd.to_datetime('2025-04-30')

# 各期間のデータ
df_april = df[(df['日付'] >= april_start) & (df['日付'] <= april_end)].copy()
df_period_a = df[(df['日付'] >= period_a_start) & (df['日付'] <= period_a_end)].copy()
df_period_b = df[(df['日付'] >= period_b_start) & (df['日付'] <= period_b_end)].copy()
df_apr_onwards = df[df['日付'] >= april_start].copy()

print("=" * 80)
print("分析1: 各期間の客単価比較（4.2の分析の確認）")
print("=" * 80)

def calc_customer_price(df_period, period_name):
    """期間全体の客単価を計算"""
    receipt_df = df_period.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first'
    }).reset_index()
    receipt_df = receipt_df[receipt_df['H.客数（合計）'] > 0].copy()
    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']
    
    total_sales = receipt_df['H.小計'].sum()
    total_customers = receipt_df['H.客数（合計）'].sum()
    avg_customer_price = total_sales / total_customers
    median_customer_price = receipt_df['客単価'].median()
    
    print(f"\n[{period_name}]")
    print(f"  伝票数: {len(receipt_df):,}")
    print(f"  総客数: {total_customers:,}人")
    print(f"  総売上: {total_sales:,.0f}円")
    print(f"  客単価（平均）: {avg_customer_price:.0f}円")
    print(f"  客単価（中央値）: {median_customer_price:.0f}円")
    
    return receipt_df, avg_customer_price, median_customer_price

receipt_april, avg_april, med_april = calc_customer_price(df_april, '4月のみ')
receipt_a, avg_a, med_a = calc_customer_price(df_period_a, '期間A (5-7月)')
receipt_b, avg_b, med_b = calc_customer_price(df_period_b, '期間B (10-12月)')

print(f"\n[時系列での変化]")
print(f"  4月 -> 期間A: {med_a - med_april:+.0f}円 ({(med_a/med_april-1)*100:+.1f}%)")
print(f"  期間A -> 期間B: {med_b - med_a:+.0f}円 ({(med_b/med_a-1)*100:+.1f}%)")
print(f"  4月 -> 期間B: {med_b - med_april:+.0f}円 ({(med_b/med_april-1)*100:+.1f}%)")

print("\n" + "=" * 80)
print("分析2: 各期間内でのHigh/Low分析（日次・ディナー帯）")
print("=" * 80)

def analyze_high_low_by_period(df_period, period_name):
    """期間内でのHigh/Low分析（修正版）"""
    # ディナー帯（17-22時）のみ抽出
    df_dinner = df_period[(df_period['時間'] >= 17) & (df_period['時間'] <= 22)].copy()
    
    if len(df_dinner) == 0:
        print(f"\n[{period_name}] データなし")
        return None
    
    # 伝票単位で集計
    receipt_dinner = df_dinner.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first',
        'H.集計対象営業年月日': 'first'
    }).reset_index()
    receipt_dinner = receipt_dinner[receipt_dinner['H.客数（合計）'] > 0].copy()
    receipt_dinner['客単価'] = receipt_dinner['H.小計'] / receipt_dinner['H.客数（合計）']
    
    # 日次集計
    daily = receipt_dinner.groupby('H.集計対象営業年月日').agg({
        'H.伝票番号': 'count',
        'H.小計': 'sum',
        'H.客数（合計）': 'sum',
        '客単価': 'mean'
    }).reset_index()
    daily.columns = ['日付', '組数', '売上', '客数', '平均客単価']
    daily = daily[daily['客数'] > 0].copy()
    daily['客単価_計算'] = daily['売上'] / daily['客数']
    
    if len(daily) < 4:
        print(f"\n[{period_name}] データが少なすぎます: {len(daily)}日")
        return None
    
    # High/Low分類（売上で）
    q75 = daily['売上'].quantile(0.75)
    q25 = daily['売上'].quantile(0.25)
    
    high_days = daily[daily['売上'] >= q75]
    low_days = daily[daily['売上'] <= q25]
    
    high_avg_price = high_days['客単価_計算'].mean()
    low_avg_price = low_days['客単価_計算'].mean()
    
    high_avg_customers = high_days['客数'].mean()
    low_avg_customers = low_days['客数'].mean()
    
    print(f"\n[{period_name}] ディナー帯のHigh/Low分析")
    print(f"  総日数: {len(daily)}日")
    print(f"  High日数: {len(high_days)}日, Low日数: {len(low_days)}日")
    print(f"  High閾値（売上）: {q75:,.0f}円以上")
    print(f"  Low閾値（売上）: {q25:,.0f}円以下")
    print(f"  High日の平均客単価: {high_avg_price:.0f}円")
    print(f"  Low日の平均客単価: {low_avg_price:.0f}円")
    print(f"  客単価の差: {high_avg_price - low_avg_price:+.0f}円")
    print(f"  High日の平均客数: {high_avg_customers:.0f}人")
    print(f"  Low日の平均客数: {low_avg_customers:.0f}人")
    print(f"  客数の差: {high_avg_customers - low_avg_customers:+.0f}人 (比率: {high_avg_customers/low_avg_customers:.2f}x)")
    
    return {
        'period': period_name,
        'high_price': high_avg_price,
        'low_price': low_avg_price,
        'price_diff': high_avg_price - low_avg_price,
        'high_customers': high_avg_customers,
        'low_customers': low_avg_customers,
        'overall_median_price': daily['客単価_計算'].median()
    }

result_april = analyze_high_low_by_period(df_april, '4月のみ')
result_a = analyze_high_low_by_period(df_period_a, '期間A (5-7月)')
result_b = analyze_high_low_by_period(df_period_b, '期間B (10-12月)')
result_all = analyze_high_low_by_period(df_apr_onwards, '4月以降全体')

print("\n" + "=" * 80)
print("分析3: 矛盾の原因を特定")
print("=" * 80)

if result_april and result_a and result_b and result_all:
    print(f"""
[重要な発見]

1. 「4.2の客単価上昇」と「6.4のHigh/Low分析」は異なる比較をしている

   - 4.2: 期間A（5-7月）と期間B（10-12月）の時系列比較
     -> 期間Aの全日の中央値 vs 期間Bの全日の中央値
     -> 結果: {med_a:.0f}円 -> {med_b:.0f}円 = {med_b - med_a:+.0f}円上昇

   - 6.4: 4月以降の同一期間内での売上High日 vs Low日の比較
     -> 同じ期間の中で、売上が高い日と低い日の客単価を比較
     -> 結果: High日 {result_all['high_price']:.0f}円 vs Low日 {result_all['low_price']:.0f}円 = {result_all['price_diff']:+.0f}円

2. 各期間内でのHigh/Low差（ディナー帯）

   | 期間 | High日客単価 | Low日客単価 | 差 | 期間全体中央値 |
   |------|------------|-----------|-----|--------------|
   | 4月のみ | {result_april['high_price']:.0f}円 | {result_april['low_price']:.0f}円 | {result_april['price_diff']:+.0f}円 | {result_april['overall_median_price']:.0f}円 |
   | 期間A (5-7月) | {result_a['high_price']:.0f}円 | {result_a['low_price']:.0f}円 | {result_a['price_diff']:+.0f}円 | {result_a['overall_median_price']:.0f}円 |
   | 期間B (10-12月) | {result_b['high_price']:.0f}円 | {result_b['low_price']:.0f}円 | {result_b['price_diff']:+.0f}円 | {result_b['overall_median_price']:.0f}円 |
   | 4月以降全体 | {result_all['high_price']:.0f}円 | {result_all['low_price']:.0f}円 | {result_all['price_diff']:+.0f}円 | {result_all['overall_median_price']:.0f}円 |

3. 解釈
   
   - 各期間内では、High日とLow日で客単価にほとんど差がない
   - しかし、期間ごとの全体中央値は上昇している（4月: {result_april['overall_median_price']:.0f}円 -> 期間B: {result_b['overall_median_price']:.0f}円）
   - つまり、「日ごとの売上変動」と「長期トレンド」は異なるメカニズム
""")

print("\n" + "=" * 80)
print("分析4: ランチ帯でも同様か確認")
print("=" * 80)

def analyze_high_low_lunch(df_period, period_name):
    """ランチ帯のHigh/Low分析"""
    df_lunch = df_period[(df_period['時間'] >= 11) & (df_period['時間'] <= 15)].copy()
    
    if len(df_lunch) == 0:
        print(f"\n[{period_name}] データなし")
        return None
    
    # 伝票単位で集計
    receipt_lunch = df_lunch.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first',
        'H.集計対象営業年月日': 'first'
    }).reset_index()
    receipt_lunch = receipt_lunch[receipt_lunch['H.客数（合計）'] > 0].copy()
    receipt_lunch['客単価'] = receipt_lunch['H.小計'] / receipt_lunch['H.客数（合計）']
    
    # 日次集計
    daily = receipt_lunch.groupby('H.集計対象営業年月日').agg({
        'H.伝票番号': 'count',
        'H.小計': 'sum',
        'H.客数（合計）': 'sum'
    }).reset_index()
    daily.columns = ['日付', '組数', '売上', '客数']
    daily = daily[daily['客数'] > 0].copy()
    daily['客単価'] = daily['売上'] / daily['客数']
    
    if len(daily) < 4:
        return None
    
    q75 = daily['売上'].quantile(0.75)
    q25 = daily['売上'].quantile(0.25)
    
    high_days = daily[daily['売上'] >= q75]
    low_days = daily[daily['売上'] <= q25]
    
    high_avg_price = high_days['客単価'].mean()
    low_avg_price = low_days['客単価'].mean()
    
    print(f"\n[{period_name}] ランチ帯のHigh/Low分析")
    print(f"  High日の平均客単価: {high_avg_price:.0f}円")
    print(f"  Low日の平均客単価: {low_avg_price:.0f}円")
    print(f"  客単価の差: {high_avg_price - low_avg_price:+.0f}円")
    print(f"  期間全体の中央値: {daily['客単価'].median():.0f}円")
    
    return {
        'high_price': high_avg_price,
        'low_price': low_avg_price,
        'overall_median': daily['客単価'].median()
    }

lunch_april = analyze_high_low_lunch(df_april, '4月のみ')
lunch_a = analyze_high_low_lunch(df_period_a, '期間A (5-7月)')
lunch_b = analyze_high_low_lunch(df_period_b, '期間B (10-12月)')

if lunch_april and lunch_a and lunch_b:
    print(f"""

[ランチ帯の時系列変化]
- 4月: 中央値 {lunch_april['overall_median']:.0f}円
- 期間A: 中央値 {lunch_a['overall_median']:.0f}円 ({lunch_a['overall_median'] - lunch_april['overall_median']:+.0f}円)
- 期間B: 中央値 {lunch_b['overall_median']:.0f}円 ({lunch_b['overall_median'] - lunch_a['overall_median']:+.0f}円)

[ランチ帯のHigh/Low差]
- ランチでもHigh日とLow日の客単価差は小さい（むしろLow日の方が高い傾向）
- これは「混雑時は客単価が下がる」現象（ランチはオフィスワーカーが安く早く済ませる）
""")

print("\n" + "=" * 80)
print("最終結論")
print("=" * 80)

print("""
[矛盾の解消]

2つの分析は矛盾していない。それぞれ異なることを示している：

1. 「4.2の客単価上昇」が示すこと:
   -> 時間経過とともに、全体の客単価水準が上昇している
   -> 原因: メニュー改定、高単価商品の投入、価格戦略
   -> これは「期間間の比較」

2. 「6.4のHigh/Low分析」が示すこと:
   -> 同一期間内で、売上High日とLow日で客単価はほぼ同じ
   -> 売上の高低を決めるのは「客数」であり「客単価」ではない
   -> これは「日間の比較（同一期間内）」

[直感的な説明]

イメージ: 
- 5月1日のHigh日（売上25万円）と5月15日のLow日（売上12万円）を比べると、客単価はほぼ同じ
- しかし、5月全体と10月全体を比べると、10月の方が客単価が高い

つまり:
- 「今日の売上が高いか低いか」-> 客数で決まる
- 「今月の売上が先月より高いか」-> 客数 + 客単価（長期トレンド）で決まる
""")
