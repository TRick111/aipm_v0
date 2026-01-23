# -*- coding: utf-8 -*-
"""
滞在時間データの品質評価・外れ値分析
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# 日本語フォント設定
plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = Path(r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\StayTimeAnalysis")

# データ読み込み
df = pd.read_csv(OUTPUT_DIR / "01_visits_with_stay_time.csv")

print('=' * 60)
print('滞在時間データの品質評価')
print('=' * 60)

stay = df['滞在時間_分']

print(f'\n■ 基本情報')
print(f'  総件数: {len(stay):,}')
print(f'  最小値: {stay.min():.2f}分')
print(f'  最大値: {stay.max():.2f}分')

print(f'\n■ 極端に短い滞在時間')
for t in [1, 2, 3, 5, 10]:
    cnt = (stay <= t).sum()
    pct = cnt / len(stay) * 100
    print(f'  {t}分以下: {cnt:,}件 ({pct:.2f}%)')

print(f'\n■ 極端に長い滞在時間')
for t in [60, 90, 120, 150, 180]:
    cnt = (stay >= t).sum()
    pct = cnt / len(stay) * 100
    print(f'  {t}分以上: {cnt:,}件 ({pct:.2f}%)')

print(f'\n■ 外れ値検出（IQR法）')
Q1 = stay.quantile(0.25)
Q3 = stay.quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
print(f'  Q1: {Q1:.1f}分, Q3: {Q3:.1f}分, IQR: {IQR:.1f}分')
print(f'  下限: {lower:.1f}分, 上限: {upper:.1f}分')
outliers_low = (stay < lower).sum()
outliers_high = (stay > upper).sum()
print(f'  下側外れ値: {outliers_low:,}件 ({outliers_low/len(stay)*100:.2f}%)')
print(f'  上側外れ値: {outliers_high:,}件 ({outliers_high/len(stay)*100:.2f}%)')

print(f'\n■ 極端なケースのサンプル')
print(f'\n  【5分以下の例（最初の10件）】')
short = df[stay <= 5][['来店時刻', '退店時刻', '滞在時間_分', 'H.客数（合計）', 'H.小計']].head(10)
for _, row in short.iterrows():
    print(f"    {row['来店時刻']} → {row['退店時刻']} | {row['滞在時間_分']:.1f}分 | {row['H.客数（合計）']}人 | ¥{row['H.小計']:,.0f}")

print(f'\n  【120分以上の例（最初の10件）】')
long_stay = df[stay >= 120][['来店時刻', '退店時刻', '滞在時間_分', 'H.客数（合計）', 'H.小計']].head(10)
for _, row in long_stay.iterrows():
    print(f"    {row['来店時刻']} → {row['退店時刻']} | {row['滞在時間_分']:.1f}分 | {row['H.客数（合計）']}人 | ¥{row['H.小計']:,.0f}")

print(f'\n■ 分布の歪み')
print(f'  平均: {stay.mean():.2f}分')
print(f'  中央値: {stay.median():.2f}分')
print(f'  歪度: {stay.skew():.2f} (正=右に裾が長い)')
print(f'  尖度: {stay.kurtosis():.2f} (正=外れ値が多い)')

print(f'\n■ パーセンタイル分布')
for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    val = stay.quantile(p/100)
    print(f'  {p}%: {val:.1f}分')

# 短い滞在の詳細分析
print(f'\n■ 短い滞在時間の特徴分析')
short_df = df[stay <= 5]
normal_df = df[(stay > 5) & (stay <= 60)]
print(f'  5分以下の平均客数: {short_df["H.客数（合計）"].mean():.1f}人')
print(f'  通常(5-60分)の平均客数: {normal_df["H.客数（合計）"].mean():.1f}人')
print(f'  5分以下の平均単価: ¥{short_df["H.小計"].mean():,.0f}')
print(f'  通常(5-60分)の平均単価: ¥{normal_df["H.小計"].mean():,.0f}')

# 長い滞在の詳細分析
print(f'\n■ 長い滞在時間の特徴分析')
long_df = df[stay >= 60]
print(f'  60分以上の平均客数: {long_df["H.客数（合計）"].mean():.1f}人')
print(f'  60分以上の平均単価: ¥{long_df["H.小計"].mean():,.0f}')

# 可視化: 外れ値を強調したヒストグラム
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 全体分布（外れ値含む）
ax1 = axes[0, 0]
ax1.hist(stay, bins=100, edgecolor='black', alpha=0.7)
ax1.axvline(lower, color='red', linestyle='--', label=f'下限({lower:.0f}分)')
ax1.axvline(upper, color='red', linestyle='--', label=f'上限({upper:.0f}分)')
ax1.set_xlabel('滞在時間（分）')
ax1.set_ylabel('頻度')
ax1.set_title('全体分布（外れ値の閾値表示）')
ax1.legend()
ax1.grid(alpha=0.3)

# 2. 短い滞在時間の詳細（0-15分）
ax2 = axes[0, 1]
short_data = stay[stay <= 15]
ax2.hist(short_data, bins=30, edgecolor='black', alpha=0.7, color='orange')
ax2.set_xlabel('滞在時間（分）')
ax2.set_ylabel('頻度')
ax2.set_title(f'短い滞在時間の分布（15分以下: {len(short_data):,}件）')
ax2.grid(alpha=0.3)

# 3. 長い滞在時間の詳細（60分以上）
ax3 = axes[1, 0]
long_data = stay[stay >= 60]
ax3.hist(long_data, bins=30, edgecolor='black', alpha=0.7, color='red')
ax3.set_xlabel('滞在時間（分）')
ax3.set_ylabel('頻度')
ax3.set_title(f'長い滞在時間の分布（60分以上: {len(long_data):,}件）')
ax3.grid(alpha=0.3)

# 4. 主要範囲（10-60分）
ax4 = axes[1, 1]
main_data = stay[(stay >= 10) & (stay <= 60)]
ax4.hist(main_data, bins=50, edgecolor='black', alpha=0.7, color='green')
ax4.set_xlabel('滞在時間（分）')
ax4.set_ylabel('頻度')
ax4.set_title(f'主要範囲の分布（10-60分: {len(main_data):,}件 = {len(main_data)/len(stay)*100:.1f}%）')
ax4.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "20_data_quality_histograms.png", dpi=150)
plt.close()
print(f'\n保存: 20_data_quality_histograms.png')

# 外れ値候補のリスト出力
print(f'\n■ 外れ値候補をCSVに出力')
outliers = df[(stay < lower) | (stay > upper)].copy()
outliers = outliers.sort_values('滞在時間_分')
outliers.to_csv(OUTPUT_DIR / "21_outliers.csv", index=False, encoding='utf-8-sig')
print(f'  保存: 21_outliers.csv ({len(outliers):,}件)')

# データ品質サマリー
print(f'\n' + '=' * 60)
print('データ品質の総合評価')
print('=' * 60)
valid_range = (stay >= 5) & (stay <= 60)
print(f'\n  妥当な範囲（5-60分）に入る件数: {valid_range.sum():,}件 ({valid_range.sum()/len(stay)*100:.1f}%)')
print(f'  外れ値候補（IQR法）: {len(outliers):,}件 ({len(outliers)/len(stay)*100:.1f}%)')

if outliers_low > 0 or outliers_high > 0:
    print(f'\n  【注意】外れ値が {len(outliers):,}件 あります')
    print(f'    - 短すぎる（<{lower:.0f}分）: {outliers_low:,}件')
    print(f'    - 長すぎる（>{upper:.0f}分）: {outliers_high:,}件')
    print(f'\n  外れ値を除外した場合の統計:')
    clean = stay[(stay >= lower) & (stay <= upper)]
    print(f'    平均: {clean.mean():.1f}分')
    print(f'    標準偏差: {clean.std():.1f}分')
    print(f'    中央値: {clean.median():.1f}分')
