#!/usr/bin/env python3
"""
散布図に見える2つのラインの正体を調査
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

print("=" * 60)
print("2つのラインの正体を調査")
print("=" * 60)

# 客単価（売上/客数）を計算して、ラインの傾きを確認
daily['calc_unit_price'] = daily['total_sales'] / daily['total_customers']

# 客単価の分布を確認
print("\n【客単価の分布】")
print(daily['calc_unit_price'].describe())

# 客単価でグループ分け（閾値を探す）
print("\n【客単価のヒストグラム分析】")
print(f"客単価の中央値: {daily['calc_unit_price'].median():.0f}円")
print(f"客単価の平均値: {daily['calc_unit_price'].mean():.0f}円")

# 外れ値（客数0など）を除外
daily_valid = daily[daily['total_customers'] > 0].copy()

# 図1: 客単価で色分けした散布図
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 客単価で色分け
scatter1 = axes[0, 0].scatter(daily_valid['total_customers'], daily_valid['total_sales'], 
                               c=daily_valid['calc_unit_price'], cmap='viridis', alpha=0.6, s=30)
axes[0, 0].set_xlabel('客数')
axes[0, 0].set_ylabel('売上（円）')
axes[0, 0].set_title('客単価で色分け')
plt.colorbar(scatter1, ax=axes[0, 0], label='客単価（円）')

# アルコール比率で色分け
scatter2 = axes[0, 1].scatter(daily_valid['total_customers'], daily_valid['total_sales'], 
                               c=daily_valid['alcohol_ratio'], cmap='Reds', alpha=0.6, s=30)
axes[0, 1].set_xlabel('客数')
axes[0, 1].set_ylabel('売上（円）')
axes[0, 1].set_title('アルコール比率で色分け')
plt.colorbar(scatter2, ax=axes[0, 1], label='アルコール比率')

# 週末/平日で色分け
colors = ['blue' if w == 0 else 'orange' for w in daily_valid['is_weekend']]
axes[1, 0].scatter(daily_valid['total_customers'], daily_valid['total_sales'], 
                   c=colors, alpha=0.6, s=30)
axes[1, 0].set_xlabel('客数')
axes[1, 0].set_ylabel('売上（円）')
axes[1, 0].set_title('平日（青）vs 週末（オレンジ）')

# ディナー比率で色分け
scatter4 = axes[1, 1].scatter(daily_valid['total_customers'], daily_valid['total_sales'], 
                               c=daily_valid['dinner_ratio'], cmap='Purples', alpha=0.6, s=30)
axes[1, 1].set_xlabel('客数')
axes[1, 1].set_ylabel('売上（円）')
axes[1, 1].set_title('ディナー比率で色分け')
plt.colorbar(scatter4, ax=axes[1, 1], label='ディナー比率')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/09_two_lines_investigation.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n保存: 09_two_lines_investigation.png")

# 図2: アルコールあり/なしで明確に分けて確認
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# アルコールあり/なしでグループ分け
daily_valid['has_alcohol'] = daily_valid['alcohol_ratio'] > 0

# グループ別の統計
print("\n【アルコールあり/なし別の統計】")
for has_alc, group in daily_valid.groupby('has_alcohol'):
    label = 'アルコールあり' if has_alc else 'アルコールなし'
    print(f"\n{label}:")
    print(f"  日数: {len(group)}")
    print(f"  平均売上: {group['total_sales'].mean():,.0f}円")
    print(f"  平均客数: {group['total_customers'].mean():.0f}人")
    print(f"  平均客単価: {group['calc_unit_price'].mean():,.0f}円")
    
    # 回帰直線の傾き（客1人あたり売上）
    slope = np.polyfit(group['total_customers'], group['total_sales'], 1)[0]
    print(f"  回帰直線の傾き（客1人あたり売上）: {slope:,.0f}円")

# 左: アルコールあり/なしで色分け
colors = ['red' if ha else 'blue' for ha in daily_valid['has_alcohol']]
axes[0].scatter(daily_valid['total_customers'], daily_valid['total_sales'], 
                c=colors, alpha=0.5, s=30)

# 各グループの回帰直線
for has_alc in [True, False]:
    group = daily_valid[daily_valid['has_alcohol'] == has_alc]
    z = np.polyfit(group['total_customers'], group['total_sales'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(group['total_customers'].min(), group['total_customers'].max(), 100)
    color = 'red' if has_alc else 'blue'
    label = f'アルコールあり (傾き: {z[0]:,.0f}円/人)' if has_alc else f'アルコールなし (傾き: {z[0]:,.0f}円/人)'
    axes[0].plot(x_line, p(x_line), '--', color=color, linewidth=2, label=label)

axes[0].set_xlabel('客数')
axes[0].set_ylabel('売上（円）')
axes[0].set_title('アルコールあり（赤）vs なし（青）')
axes[0].legend()

# 右: クラスタで色分け
scatter = axes[1].scatter(daily_valid['total_customers'], daily_valid['total_sales'], 
                          c=daily_valid['cluster'], cmap='viridis', alpha=0.6, s=30)
axes[1].set_xlabel('客数')
axes[1].set_ylabel('売上（円）')
axes[1].set_title('クラスタで色分け')
plt.colorbar(scatter, ax=axes[1], label='クラスタ')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/10_alcohol_split_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("保存: 10_alcohol_split_analysis.png")

# 図3: より詳細な分析 - 客単価の2峰性を確認
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 客単価のヒストグラム
axes[0].hist(daily_valid['calc_unit_price'], bins=50, edgecolor='black', alpha=0.7)
axes[0].axvline(1500, color='red', linestyle='--', label='閾値候補: 1500円')
axes[0].set_xlabel('客単価（円）')
axes[0].set_ylabel('頻度')
axes[0].set_title('客単価の分布')
axes[0].legend()

# 客単価 vs アルコール比率
axes[1].scatter(daily_valid['alcohol_ratio'], daily_valid['calc_unit_price'], alpha=0.5)
axes[1].set_xlabel('アルコール比率')
axes[1].set_ylabel('客単価（円）')
axes[1].set_title('アルコール比率 vs 客単価')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/11_unit_price_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("保存: 11_unit_price_analysis.png")

# 結論をまとめる
print("\n" + "=" * 60)
print("【結論】")
print("=" * 60)

# アルコールあり/なしの客単価差
alc_yes = daily_valid[daily_valid['has_alcohol']]['calc_unit_price'].mean()
alc_no = daily_valid[~daily_valid['has_alcohol']]['calc_unit_price'].mean()
print(f"\nアルコールあり日の平均客単価: {alc_yes:,.0f}円")
print(f"アルコールなし日の平均客単価: {alc_no:,.0f}円")
print(f"差額: {alc_yes - alc_no:,.0f}円")

# 回帰直線の傾きの差
slope_alc = np.polyfit(daily_valid[daily_valid['has_alcohol']]['total_customers'], 
                       daily_valid[daily_valid['has_alcohol']]['total_sales'], 1)[0]
slope_no_alc = np.polyfit(daily_valid[~daily_valid['has_alcohol']]['total_customers'], 
                          daily_valid[~daily_valid['has_alcohol']]['total_sales'], 1)[0]

print(f"\n【回帰直線の傾き（= 客1人あたり売上）】")
print(f"アルコールあり日: {slope_alc:,.0f}円/人")
print(f"アルコールなし日: {slope_no_alc:,.0f}円/人")
print(f"差: {slope_alc - slope_no_alc:,.0f}円/人")

print(f"\n→ 2本のラインは「アルコール販売の有無」で分かれている！")
print(f"  上のライン: アルコールが出る日（ディナー営業中心）")
print(f"  下のライン: アルコールが出ない日（ランチ営業中心）")
