#!/usr/bin/env python3
"""
時期による変化を調査
- アルコール提供開始時期
- 2025年3月前後の変化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import rcParams

# 日本語フォント設定
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']
rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = '/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-21/SalesFactorAnalysis'

# 日次集計データを読み込み
daily = pd.read_csv(f'{OUTPUT_DIR}/daily_summary_with_cluster.csv')
daily['date'] = pd.to_datetime(daily['date'])

print("=" * 60)
print("時期による変化を調査")
print("=" * 60)

# アルコールあり/なしのフラグ
daily['has_alcohol'] = daily['alcohol_ratio'] > 0

# ============================================================
# 調査1: アルコール提供の時系列
# ============================================================
print("\n【調査1: アルコール提供の時系列】")

# 月別のアルコールあり日の比率
daily['year_month'] = daily['date'].dt.to_period('M')
monthly_alcohol = daily.groupby('year_month').agg({
    'has_alcohol': ['sum', 'count', 'mean'],
    'alcohol_ratio': 'mean',
    'total_sales': 'mean'
}).reset_index()
monthly_alcohol.columns = ['year_month', 'alcohol_days', 'total_days', 'alcohol_day_ratio', 'avg_alcohol_ratio', 'avg_sales']

print("\n月別アルコール提供状況:")
print(monthly_alcohol.to_string())

# アルコール提供開始日を特定
first_alcohol_date = daily[daily['has_alcohol']]['date'].min()
print(f"\n最初にアルコールが出た日: {first_alcohol_date}")

# アルコールなし日の最後
last_no_alcohol = daily[~daily['has_alcohol']]['date'].max()
print(f"最後にアルコールが出なかった日: {last_no_alcohol}")

# ============================================================
# 調査2: 2025年3月前後の変化
# ============================================================
print("\n" + "=" * 60)
print("【調査2: 2025年3月前後の変化】")
print("=" * 60)

# 2025年3月を境に分割
cutoff_date = pd.Timestamp('2025-03-01')
daily['period'] = np.where(daily['date'] < cutoff_date, '2025年3月以前', '2025年3月以降')

# 期間別の統計
print("\n期間別統計:")
period_stats = daily.groupby('period').agg({
    'total_sales': ['mean', 'std', 'count'],
    'total_customers': 'mean',
    'avg_spend_per_customer': 'mean',
    'alcohol_ratio': 'mean',
    'has_alcohol': 'mean',
    'lunch_ratio': 'mean',
    'dinner_ratio': 'mean'
}).round(2)
print(period_stats)

# ============================================================
# 可視化
# ============================================================

# 図1: アルコール提供の時系列推移
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# アルコール比率の時系列
axes[0].plot(daily['date'], daily['alcohol_ratio'], alpha=0.5, linewidth=0.5)
axes[0].axvline(cutoff_date, color='red', linestyle='--', linewidth=2, label='2025年3月')
axes[0].axvline(first_alcohol_date, color='green', linestyle='--', linewidth=2, label=f'最初のアルコール日: {first_alcohol_date.strftime("%Y-%m-%d")}')
axes[0].set_xlabel('日付')
axes[0].set_ylabel('アルコール比率')
axes[0].set_title('アルコール比率の時系列推移')
axes[0].legend()

# アルコールあり/なしの散布図（時系列）
colors = ['red' if ha else 'blue' for ha in daily['has_alcohol']]
axes[1].scatter(daily['date'], daily['total_sales'], c=colors, alpha=0.5, s=10)
axes[1].axvline(cutoff_date, color='black', linestyle='--', linewidth=2, label='2025年3月')
axes[1].set_xlabel('日付')
axes[1].set_ylabel('売上（円）')
axes[1].set_title('売上の時系列（赤=アルコールあり、青=なし）')
axes[1].legend()

# 月別アルコール提供日比率
monthly_alcohol['year_month_str'] = monthly_alcohol['year_month'].astype(str)
axes[2].bar(range(len(monthly_alcohol)), monthly_alcohol['alcohol_day_ratio'], color='steelblue')
axes[2].set_xticks(range(len(monthly_alcohol)))
axes[2].set_xticklabels(monthly_alcohol['year_month_str'], rotation=45, ha='right')
axes[2].axhline(0.5, color='red', linestyle='--', alpha=0.5)
axes[2].set_xlabel('年月')
axes[2].set_ylabel('アルコール提供日の比率')
axes[2].set_title('月別アルコール提供日の比率')

# 2025年3月の位置に縦線
march_2025_idx = list(monthly_alcohol['year_month_str']).index('2025-03') if '2025-03' in list(monthly_alcohol['year_month_str']) else None
if march_2025_idx:
    axes[2].axvline(march_2025_idx, color='red', linestyle='--', linewidth=2, label='2025年3月')
    axes[2].legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/12_alcohol_timeline.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n保存: 12_alcohol_timeline.png")

# 図2: 2025年3月前後の比較
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 売上分布
for i, period in enumerate(['2025年3月以前', '2025年3月以降']):
    data = daily[daily['period'] == period]['total_sales']
    axes[0, 0].hist(data, bins=30, alpha=0.5, label=period)
axes[0, 0].set_xlabel('売上（円）')
axes[0, 0].set_ylabel('頻度')
axes[0, 0].set_title('売上分布の比較')
axes[0, 0].legend()

# 客数分布
for i, period in enumerate(['2025年3月以前', '2025年3月以降']):
    data = daily[daily['period'] == period]['total_customers']
    axes[0, 1].hist(data, bins=30, alpha=0.5, label=period)
axes[0, 1].set_xlabel('客数')
axes[0, 1].set_ylabel('頻度')
axes[0, 1].set_title('客数分布の比較')
axes[0, 1].legend()

# 客単価分布
for i, period in enumerate(['2025年3月以前', '2025年3月以降']):
    data = daily[daily['period'] == period]['avg_spend_per_customer']
    axes[0, 2].hist(data, bins=30, alpha=0.5, label=period)
axes[0, 2].set_xlabel('客単価（円）')
axes[0, 2].set_ylabel('頻度')
axes[0, 2].set_title('客単価分布の比較')
axes[0, 2].legend()

# 客数 vs 売上（期間別）
colors = {'2025年3月以前': 'blue', '2025年3月以降': 'red'}
for period in ['2025年3月以前', '2025年3月以降']:
    data = daily[daily['period'] == period]
    axes[1, 0].scatter(data['total_customers'], data['total_sales'], 
                       c=colors[period], alpha=0.5, s=20, label=period)
axes[1, 0].set_xlabel('客数')
axes[1, 0].set_ylabel('売上（円）')
axes[1, 0].set_title('客数 vs 売上（期間別）')
axes[1, 0].legend()

# アルコール比率の分布（期間別）
for i, period in enumerate(['2025年3月以前', '2025年3月以降']):
    data = daily[daily['period'] == period]['alcohol_ratio']
    axes[1, 1].hist(data, bins=30, alpha=0.5, label=period)
axes[1, 1].set_xlabel('アルコール比率')
axes[1, 1].set_ylabel('頻度')
axes[1, 1].set_title('アルコール比率分布の比較')
axes[1, 1].legend()

# 曜日別売上（期間別）
weekday_sales = daily.groupby(['period', 'weekday']).agg({'total_sales': 'mean'}).reset_index()
weekday_names = ['月', '火', '水', '木', '金', '土', '日']
width = 0.35
x = np.arange(7)
for i, period in enumerate(['2025年3月以前', '2025年3月以降']):
    data = weekday_sales[weekday_sales['period'] == period].sort_values('weekday')['total_sales']
    axes[1, 2].bar(x + i*width, data, width, label=period, color=colors[period], alpha=0.7)
axes[1, 2].set_xticks(x + width/2)
axes[1, 2].set_xticklabels(weekday_names)
axes[1, 2].set_xlabel('曜日')
axes[1, 2].set_ylabel('平均売上（円）')
axes[1, 2].set_title('曜日別平均売上（期間別）')
axes[1, 2].legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/13_before_after_march2025.png', dpi=150, bbox_inches='tight')
plt.close()
print("保存: 13_before_after_march2025.png")

# ============================================================
# 詳細分析
# ============================================================
print("\n" + "=" * 60)
print("【詳細分析】")
print("=" * 60)

# 2025年3月前後での主要指標の変化
print("\n■ 2025年3月前後の主要指標比較")
before = daily[daily['period'] == '2025年3月以前']
after = daily[daily['period'] == '2025年3月以降']

metrics = [
    ('平均売上', 'total_sales'),
    ('平均客数', 'total_customers'),
    ('平均客単価', 'avg_spend_per_customer'),
    ('アルコール提供日比率', 'has_alcohol'),
    ('平均アルコール比率', 'alcohol_ratio'),
    ('ランチ比率', 'lunch_ratio'),
    ('ディナー比率', 'dinner_ratio'),
]

print(f"\n{'指標':<20} {'3月以前':>15} {'3月以降':>15} {'変化':>15} {'変化率':>10}")
print("-" * 75)
for name, col in metrics:
    val_before = before[col].mean()
    val_after = after[col].mean()
    change = val_after - val_before
    pct_change = (change / val_before * 100) if val_before != 0 else 0
    
    if col in ['total_sales', 'avg_spend_per_customer']:
        print(f"{name:<20} {val_before:>15,.0f} {val_after:>15,.0f} {change:>+15,.0f} {pct_change:>+9.1f}%")
    elif col in ['has_alcohol', 'alcohol_ratio', 'lunch_ratio', 'dinner_ratio']:
        print(f"{name:<20} {val_before*100:>14.1f}% {val_after*100:>14.1f}% {change*100:>+14.1f}% {pct_change:>+9.1f}%")
    else:
        print(f"{name:<20} {val_before:>15.1f} {val_after:>15.1f} {change:>+15.1f} {pct_change:>+9.1f}%")

# アルコール提供パターンの変化
print("\n■ アルコール提供パターンの時期別分析")
print("\n月別のアルコール提供日数と比率:")
print(monthly_alcohol[['year_month', 'alcohol_days', 'total_days', 'alcohol_day_ratio']].to_string())

# 2025年3月以降でアルコールなしの日を確認
print("\n■ 2025年3月以降のアルコールなし日:")
after_no_alcohol = after[~after['has_alcohol']]
print(f"  日数: {len(after_no_alcohol)}日")
if len(after_no_alcohol) > 0:
    print(f"  日付例: {after_no_alcohol['date'].head(10).tolist()}")
    print(f"  曜日分布:")
    print(after_no_alcohol['weekday'].value_counts().sort_index())

# 結論
print("\n" + "=" * 60)
print("【結論】")
print("=" * 60)

# アルコール提供開始時期の判定
monthly_alcohol['alcohol_day_ratio_num'] = monthly_alcohol['alcohol_day_ratio']
transition_month = monthly_alcohol[monthly_alcohol['alcohol_day_ratio_num'] > 0.3]['year_month'].min()
print(f"\n1. アルコール提供が本格化した時期: {transition_month}")

# 2025年3月前後の変化
sales_change = (after['total_sales'].mean() - before['total_sales'].mean()) / before['total_sales'].mean() * 100
print(f"\n2. 2025年3月前後の変化:")
print(f"   - 平均売上: {sales_change:+.1f}%")
print(f"   - アルコール提供日比率: {before['has_alcohol'].mean()*100:.1f}% → {after['has_alcohol'].mean()*100:.1f}%")
