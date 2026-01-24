# -*- coding: utf-8 -*-
"""
THE BIFTEKI 赤坂見附店 - 客数分析スクリプト
2024年と2025年の各月で、営業日当たりの客数を時間帯・曜日別に比較
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import japanize_matplotlib
from pathlib import Path

# 出力先
OUTPUT_DIR = Path(__file__).parent
DATA_PATH = Path(__file__).parent.parent / "transformed_pos_data_eatin.csv"

print("=== データ読み込み ===")
df = pd.read_csv(DATA_PATH, encoding='utf-8')
print(f"総レコード数: {len(df):,}")
print(f"カラム: {df.columns.tolist()}")

# 日付と時間の処理
df['営業日'] = pd.to_datetime(df['H.集計対象営業年月日'], format='%Y/%m/%d')
df['伝票発行日時'] = pd.to_datetime(df['H.伝票発行日'], format='%Y/%m/%d %H:%M:%S')
df['時間'] = df['伝票発行日時'].dt.hour

# 年・月の抽出
df['年'] = df['営業日'].dt.year
df['月'] = df['営業日'].dt.month
df['年月'] = df['営業日'].dt.to_period('M')
df['曜日'] = df['H.曜日']

# データの期間確認
print(f"\nデータ期間: {df['営業日'].min()} ~ {df['営業日'].max()}")
print(f"年の分布:\n{df['年'].value_counts().sort_index()}")

# 伝票単位でユニークにする（1伝票=1組の来店）
visit_df = df.drop_duplicates(subset=['H.伝票番号']).copy()
visit_df['客数'] = visit_df['H.客数（合計）'].astype(int)

print(f"\nユニーク伝票数: {len(visit_df):,}")
print(f"年別伝票数:\n{visit_df['年'].value_counts().sort_index()}")

# 時間帯区分を作成（ランチ/ディナー分けと細かい時間帯）
def get_time_period(hour):
    if 11 <= hour < 15:
        return 'ランチ(11-15時)'
    elif 15 <= hour < 17:
        return 'アイドル(15-17時)'
    elif 17 <= hour < 22:
        return 'ディナー(17-22時)'
    else:
        return 'その他'

def get_hour_group(hour):
    if hour < 11:
        return '11時前'
    elif hour < 12:
        return '11時台'
    elif hour < 13:
        return '12時台'
    elif hour < 14:
        return '13時台'
    elif hour < 15:
        return '14時台'
    elif hour < 16:
        return '15時台'
    elif hour < 17:
        return '16時台'
    elif hour < 18:
        return '17時台'
    elif hour < 19:
        return '18時台'
    elif hour < 20:
        return '19時台'
    elif hour < 21:
        return '20時台'
    elif hour < 22:
        return '21時台'
    else:
        return '22時以降'

visit_df['時間帯'] = visit_df['時間'].apply(get_time_period)
visit_df['時間グループ'] = visit_df['時間'].apply(get_hour_group)

# 曜日を日本語順にソートするためのマッピング
weekday_order = {'月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6}
visit_df['曜日順'] = visit_df['曜日'].map(weekday_order)

print("\n=== 年月別の営業日数と総客数 ===")

# 年月ごとの営業日数を計算（データに存在するユニークな日付数）
operating_days = visit_df.groupby(['年', '月'])['営業日'].nunique().reset_index()
operating_days.columns = ['年', '月', '営業日数']

# 年月ごとの総客数
monthly_customers = visit_df.groupby(['年', '月'])['客数'].sum().reset_index()
monthly_customers.columns = ['年', '月', '総客数']

# 結合
monthly_summary = operating_days.merge(monthly_customers, on=['年', '月'])
monthly_summary['営業日当たり客数'] = monthly_summary['総客数'] / monthly_summary['営業日数']

print(monthly_summary.to_string())
monthly_summary.to_csv(OUTPUT_DIR / '02_monthly_summary.csv', index=False, encoding='utf-8-sig')

# 2024年と2025年のデータを比較（共通する月のみ）
years_in_data = monthly_summary['年'].unique()
print(f"\nデータに含まれる年: {sorted(years_in_data)}")

# 年が2024, 2025のみ取り出す（または最新2年）
if 2024 in years_in_data and 2025 in years_in_data:
    compare_years = [2024, 2025]
else:
    compare_years = sorted(years_in_data)[-2:]
    print(f"2024/2025がないため、{compare_years}を比較します")

year1, year2 = compare_years[0], compare_years[1]
print(f"\n比較対象年: {year1}年 vs {year2}年")

# 各年のデータを絞る
df_y1 = visit_df[visit_df['年'] == year1].copy()
df_y2 = visit_df[visit_df['年'] == year2].copy()

print(f"{year1}年 伝票数: {len(df_y1):,}, 客数合計: {df_y1['客数'].sum():,}")
print(f"{year2}年 伝票数: {len(df_y2):,}, 客数合計: {df_y2['客数'].sum():,}")

# ===========================
# 月×曜日別の分析
# ===========================
print("\n=== 月×曜日別の分析 ===")

def calc_per_day_stats(df, year_label):
    """月×曜日ごとに営業日数と営業日当たり客数を計算"""
    # 月×曜日×日付ごとの客数合計
    daily_stats = df.groupby(['月', '曜日', '営業日']).agg({
        '客数': 'sum'
    }).reset_index()
    
    # 月×曜日ごとの営業日数と平均客数
    result = daily_stats.groupby(['月', '曜日']).agg({
        '営業日': 'count',  # 営業日数
        '客数': 'mean'      # 営業日当たり客数
    }).reset_index()
    result.columns = ['月', '曜日', f'{year_label}_営業日数', f'{year_label}_日当たり客数']
    return result

stats_y1 = calc_per_day_stats(df_y1, f'{year1}')
stats_y2 = calc_per_day_stats(df_y2, f'{year2}')

# マージ
weekday_month_stats = stats_y1.merge(stats_y2, on=['月', '曜日'], how='outer')
weekday_month_stats['差分_日当たり客数'] = weekday_month_stats[f'{year2}_日当たり客数'] - weekday_month_stats[f'{year1}_日当たり客数']
weekday_month_stats['曜日順'] = weekday_month_stats['曜日'].map(weekday_order)
weekday_month_stats = weekday_month_stats.sort_values(['月', '曜日順'])

print(weekday_month_stats.to_string())
weekday_month_stats.to_csv(OUTPUT_DIR / '03_weekday_month_comparison.csv', index=False, encoding='utf-8-sig')

# ===========================
# 月×時間帯別の分析
# ===========================
print("\n=== 月×時間帯別の分析 ===")

def calc_per_day_time_stats(df, year_label):
    """月×時間帯ごとに営業日当たり客数を計算"""
    # 月×時間帯×日付ごとの客数合計
    daily_stats = df.groupby(['月', '時間帯', '営業日']).agg({
        '客数': 'sum'
    }).reset_index()
    
    # 月×時間帯ごとの営業日数と平均客数
    result = daily_stats.groupby(['月', '時間帯']).agg({
        '営業日': 'count',
        '客数': 'mean'
    }).reset_index()
    result.columns = ['月', '時間帯', f'{year_label}_営業日数', f'{year_label}_日当たり客数']
    return result

time_stats_y1 = calc_per_day_time_stats(df_y1, f'{year1}')
time_stats_y2 = calc_per_day_time_stats(df_y2, f'{year2}')

time_month_stats = time_stats_y1.merge(time_stats_y2, on=['月', '時間帯'], how='outer')
time_month_stats['差分_日当たり客数'] = time_month_stats[f'{year2}_日当たり客数'] - time_month_stats[f'{year1}_日当たり客数']

# 時間帯の順序付け
time_order = {'ランチ(11-15時)': 0, 'アイドル(15-17時)': 1, 'ディナー(17-22時)': 2, 'その他': 3}
time_month_stats['時間帯順'] = time_month_stats['時間帯'].map(time_order)
time_month_stats = time_month_stats.sort_values(['月', '時間帯順'])

print(time_month_stats.to_string())
time_month_stats.to_csv(OUTPUT_DIR / '04_time_month_comparison.csv', index=False, encoding='utf-8-sig')

# ===========================
# 要因分析：各月で差に最も寄与している要因
# ===========================
print("\n=== 要因分析（各月で増加の最大要因を特定） ===")

# 月別サマリ：どの要因が一番大きいか
results = []

for month in range(1, 13):
    # 両年にデータがある月のみ
    y1_month = monthly_summary[(monthly_summary['年'] == year1) & (monthly_summary['月'] == month)]
    y2_month = monthly_summary[(monthly_summary['年'] == year2) & (monthly_summary['月'] == month)]
    
    if len(y1_month) == 0 or len(y2_month) == 0:
        continue
    
    total_diff = y2_month['営業日当たり客数'].values[0] - y1_month['営業日当たり客数'].values[0]
    
    # 曜日別の差分
    weekday_data = weekday_month_stats[weekday_month_stats['月'] == month].copy()
    if len(weekday_data) > 0:
        max_weekday_row = weekday_data.loc[weekday_data['差分_日当たり客数'].idxmax()]
        max_weekday = max_weekday_row['曜日']
        max_weekday_diff = max_weekday_row['差分_日当たり客数']
    else:
        max_weekday, max_weekday_diff = '-', 0
    
    # 時間帯別の差分
    time_data = time_month_stats[time_month_stats['月'] == month].copy()
    if len(time_data) > 0:
        max_time_row = time_data.loc[time_data['差分_日当たり客数'].idxmax()]
        max_time = max_time_row['時間帯']
        max_time_diff = max_time_row['差分_日当たり客数']
    else:
        max_time, max_time_diff = '-', 0
    
    results.append({
        '月': month,
        f'{year1}年_営業日当たり客数': y1_month['営業日当たり客数'].values[0],
        f'{year2}年_営業日当たり客数': y2_month['営業日当たり客数'].values[0],
        '総差分': total_diff,
        '最大増加曜日': max_weekday,
        '曜日別最大差分': max_weekday_diff,
        '最大増加時間帯': max_time,
        '時間帯別最大差分': max_time_diff
    })

factor_summary = pd.DataFrame(results)
print(factor_summary.to_string())
factor_summary.to_csv(OUTPUT_DIR / '05_factor_summary.csv', index=False, encoding='utf-8-sig')

# ===========================
# 詳細な時間帯別分析（1時間単位）
# ===========================
print("\n=== 1時間単位の時間帯別分析 ===")

def calc_per_day_hour_stats(df, year_label):
    """月×時間グループごとに営業日当たり客数を計算"""
    daily_stats = df.groupby(['月', '時間グループ', '営業日']).agg({
        '客数': 'sum'
    }).reset_index()
    
    result = daily_stats.groupby(['月', '時間グループ']).agg({
        '営業日': 'count',
        '客数': 'mean'
    }).reset_index()
    result.columns = ['月', '時間グループ', f'{year_label}_営業日数', f'{year_label}_日当たり客数']
    return result

hour_stats_y1 = calc_per_day_hour_stats(df_y1, f'{year1}')
hour_stats_y2 = calc_per_day_hour_stats(df_y2, f'{year2}')

hour_month_stats = hour_stats_y1.merge(hour_stats_y2, on=['月', '時間グループ'], how='outer')
hour_month_stats['差分_日当たり客数'] = hour_month_stats[f'{year2}_日当たり客数'] - hour_month_stats[f'{year1}_日当たり客数']

# 時間順にソート
hour_order = ['11時前', '11時台', '12時台', '13時台', '14時台', '15時台', '16時台', 
              '17時台', '18時台', '19時台', '20時台', '21時台', '22時以降']
hour_month_stats['時間順'] = hour_month_stats['時間グループ'].apply(lambda x: hour_order.index(x) if x in hour_order else 99)
hour_month_stats = hour_month_stats.sort_values(['月', '時間順'])

print(hour_month_stats.to_string())
hour_month_stats.to_csv(OUTPUT_DIR / '06_hour_month_comparison.csv', index=False, encoding='utf-8-sig')

print("\n=== 分析完了 ===")
print(f"出力先: {OUTPUT_DIR}")
