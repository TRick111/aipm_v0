# -*- coding: utf-8 -*-
"""
THE BIFTEKI 赤坂見附店 - グラフ作成スクリプト
2024年と2025年の各月で、営業日当たりの客数を時間帯・曜日別に比較
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
import argparse
from pathlib import Path

# 日本語フォント設定（macOS/Windows差分を吸収）
def _set_japanese_font():
    candidates = [
        "Hiragino Sans",          # macOS
        "AppleGothic",            # macOS
        "Apple SD Gothic Neo",    # macOS
        "Yu Gothic",              # Windows
        "Meiryo",                 # Windows
        "Arial Unicode MS",       # macOS/Office
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False

_set_japanese_font()

# 設定（互換維持: 引数なしなら従来通り）
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--store-root", default=None)
args, _ = parser.parse_known_args()

if args.store_root:
    OUTPUT_DIR = Path(args.store_root).resolve() / "CustomerCountAnalysis"
else:
    OUTPUT_DIR = Path(__file__).parent
print(f"出力ディレクトリ: {OUTPUT_DIR}")
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.dpi'] = 120

# データ読み込み
monthly_summary = pd.read_csv(OUTPUT_DIR / '02_monthly_summary.csv')
weekday_month = pd.read_csv(OUTPUT_DIR / '03_weekday_month_comparison.csv')
time_month = pd.read_csv(OUTPUT_DIR / '04_time_month_comparison.csv')
try:
    factor_summary = pd.read_csv(OUTPUT_DIR / '05_factor_summary.csv')
except Exception:
    # 空ファイル/未作成でも落ちないようにする
    factor_summary = pd.DataFrame()
hour_month = pd.read_csv(OUTPUT_DIR / '06_hour_month_comparison.csv')

# 年は入力データから動的に決める（なかせい等で2024が無いケースに対応）
years = sorted([int(y) for y in monthly_summary['年'].dropna().unique().tolist()])
if len(years) >= 2:
    year1, year2 = years[0], years[1]
elif len(years) == 1:
    year1, year2 = years[0], years[0]
else:
    year1, year2 = 2024, 2025

# 共通の月（3月は2025年データが不完全なので除外）
common_months = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# さらに営業日数が10日未満のデータは除外
y1_months = set(monthly_summary[(monthly_summary['年'] == year1) & (monthly_summary['営業日数'] >= 10)]['月'].values)
y2_months = set(monthly_summary[(monthly_summary['年'] == year2) & (monthly_summary['営業日数'] >= 10)]['月'].values)
valid_months = sorted(list(y1_months & y2_months))
print(f"有効な比較対象月: {valid_months}")

# =========================================
# 図1: 月別営業日当たり客数の比較
# =========================================
fig, ax = plt.subplots(figsize=(12, 6))

y1_data = monthly_summary[(monthly_summary['年'] == year1) & (monthly_summary['月'].isin(valid_months))]
y2_data = monthly_summary[(monthly_summary['年'] == year2) & (monthly_summary['月'].isin(valid_months))]

x = np.arange(len(valid_months))
width = 0.35

bars1 = ax.bar(x - width/2, y1_data.sort_values('月')['営業日当たり客数'], width, label=f'{year1}年', color='#5DADE2')
bars2 = ax.bar(x + width/2, y2_data.sort_values('月')['営業日当たり客数'], width, label=f'{year2}年', color='#F5B041')

ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数（人）', fontsize=12)
ax.set_title(f'THE BIFTEKI 赤坂見附店 - 月別営業日当たり客数の比較（{year1}年 vs {year2}年）', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.legend()
ax.grid(axis='y', alpha=0.3)

# 値を表示
for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=8)
for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph01_monthly_comparison.png')
plt.close()
print("graph01_monthly_comparison.png を作成しました")

# =========================================
# 図2: 月別の前年比増減
# =========================================
fig, ax = plt.subplots(figsize=(12, 6))

merged = y1_data.sort_values('月').merge(
    y2_data.sort_values('月'),
    on='月',
    suffixes=(f'_{year1}', f'_{year2}')
)
merged['差分'] = merged[f'営業日当たり客数_{year2}'] - merged[f'営業日当たり客数_{year1}']
merged['増減率'] = (merged['差分'] / merged[f'営業日当たり客数_{year1}'] * 100).round(1)

colors = ['#27AE60' if d > 0 else '#E74C3C' for d in merged['差分']]
bars = ax.bar(valid_months, merged['差分'], color=colors)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'THE BIFTEKI 赤坂見附店 - 営業日当たり客数の前年比増減（{year2}年 - {year1}年）', fontsize=14)
ax.set_xticks(valid_months)
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.grid(axis='y', alpha=0.3)

# 値と増減率を表示
for i, bar in enumerate(bars):
    height = bar.get_height()
    rate = merged['増減率'].iloc[i]
    sign = '+' if height > 0 else ''
    ax.annotate(f'{sign}{height:.0f}\n({sign}{rate}%)',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3 if height > 0 else -25), textcoords="offset points",
                ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph02_yoy_change.png')
plt.close()
print("graph02_yoy_change.png を作成しました")

# =========================================
# 図3: 時間帯別の前年比増減（月別ヒートマップ）
# =========================================
time_order = ['ランチ(11-15時)', 'アイドル(15-17時)', 'ディナー(17-22時)']
time_pivot = time_month[time_month['月'].isin(valid_months)].pivot_table(
    index='時間帯', columns='月', values='差分_日当たり客数'
).reindex(time_order)

fig, ax = plt.subplots(figsize=(12, 5))
im = ax.imshow(time_pivot.values, cmap='RdYlGn', aspect='auto', vmin=-100, vmax=100)

ax.set_xticks(np.arange(len(valid_months)))
ax.set_yticks(np.arange(len(time_order)))
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.set_yticklabels(time_order)

# 値をセル内に表示
for i in range(len(time_order)):
    for j in range(len(valid_months)):
        val = time_pivot.iloc[i, j]
        if pd.notna(val):
            text_color = 'white' if abs(val) > 50 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', color=text_color, fontsize=10)

ax.set_title(f'時間帯別・営業日当たり客数の前年比増減（{year2}年 - {year1}年）', fontsize=14)
fig.colorbar(im, ax=ax, label='増減（人/日）')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph03_time_heatmap.png')
plt.close()
print("graph03_time_heatmap.png を作成しました")

# =========================================
# 図4: 曜日別の前年比増減（月別ヒートマップ）
# =========================================
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
weekday_pivot = weekday_month[weekday_month['月'].isin(valid_months)].pivot_table(
    index='曜日', columns='月', values='差分_日当たり客数'
).reindex(weekday_order)

fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(weekday_pivot.values, cmap='RdYlGn', aspect='auto', vmin=-100, vmax=200)

ax.set_xticks(np.arange(len(valid_months)))
ax.set_yticks(np.arange(len(weekday_order)))
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.set_yticklabels(weekday_order)

for i in range(len(weekday_order)):
    for j in range(len(valid_months)):
        val = weekday_pivot.iloc[i, j]
        if pd.notna(val):
            text_color = 'white' if abs(val) > 80 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', color=text_color, fontsize=9)

ax.set_title(f'曜日別・営業日当たり客数の前年比増減（{year2}年 - {year1}年）', fontsize=14)
fig.colorbar(im, ax=ax, label='増減（人/日）')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph04_weekday_heatmap.png')
plt.close()
print("graph04_weekday_heatmap.png を作成しました")

# =========================================
# 図5: 時間帯別の寄与度分析（積み上げ棒グラフ）
# =========================================
time_contrib = time_month[time_month['月'].isin(valid_months) & 
                          time_month['時間帯'].isin(time_order)].copy()
time_contrib_pivot = time_contrib.pivot_table(
    index='月', columns='時間帯', values='差分_日当たり客数'
)
# 期待する時間帯列が無い場合でも落ちないように補完
for c in time_order:
    if c not in time_contrib_pivot.columns:
        time_contrib_pivot[c] = 0.0
time_contrib_pivot = time_contrib_pivot[time_order]

fig, ax = plt.subplots(figsize=(12, 6))

bottom_pos = np.zeros(len(valid_months))
bottom_neg = np.zeros(len(valid_months))
colors = {'ランチ(11-15時)': '#3498DB', 'アイドル(15-17時)': '#9B59B6', 'ディナー(17-22時)': '#E67E22'}

for time_slot in time_order:
    values = time_contrib_pivot[time_slot].values
    pos_values = np.where(values > 0, values, 0)
    neg_values = np.where(values < 0, values, 0)
    
    ax.bar(valid_months, pos_values, bottom=bottom_pos, label=time_slot, color=colors[time_slot])
    ax.bar(valid_months, neg_values, bottom=bottom_neg, color=colors[time_slot])
    
    bottom_pos += pos_values
    bottom_neg += neg_values

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'時間帯別の客数増減寄与（{year2}年 - {year1}年）', fontsize=14)
ax.set_xticks(valid_months)
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.legend(loc='upper right')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph05_time_contribution.png')
plt.close()
print("graph05_time_contribution.png を作成しました")

# =========================================
# 図6: 曜日別の寄与度分析（平日vs土日）
# =========================================
weekday_month['曜日タイプ'] = weekday_month['曜日'].apply(lambda x: '土日' if x in ['土', '日'] else '平日')
daytype_contrib = weekday_month[weekday_month['月'].isin(valid_months)].groupby(['月', '曜日タイプ'])['差分_日当たり客数'].mean().reset_index()
daytype_pivot = daytype_contrib.pivot_table(index='月', columns='曜日タイプ', values='差分_日当たり客数')
# 欠けている列があっても落ちないように補完
for c in ['平日', '土日']:
    if c not in daytype_pivot.columns:
        daytype_pivot[c] = 0.0

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(valid_months))
width = 0.35

bars1 = ax.bar(x - width/2, daytype_pivot.loc[valid_months, '平日'], width, label='平日', color='#2980B9')
bars2 = ax.bar(x + width/2, daytype_pivot.loc[valid_months, '土日'], width, label='土日', color='#C0392B')

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'平日vs土日の客数増減寄与（{year2}年 - {year1}年）', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.legend()
ax.grid(axis='y', alpha=0.3)

for bar in bars1:
    height = bar.get_height()
    if height != 0:
        sign = '+' if height > 0 else ''
        ax.annotate(f'{sign}{height:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height > 0 else -12), textcoords="offset points",
                    ha='center', va='bottom' if height > 0 else 'top', fontsize=8)
for bar in bars2:
    height = bar.get_height()
    if height != 0:
        sign = '+' if height > 0 else ''
        ax.annotate(f'{sign}{height:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height > 0 else -12), textcoords="offset points",
                    ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph06_weekday_vs_weekend.png')
plt.close()
print("graph06_weekday_vs_weekend.png を作成しました")

# =========================================
# 図7: 1時間単位の時間帯別比較（代表月）
# =========================================
if len(valid_months) == 0:
    print("有効な比較対象月が無いため、graph07_hourly_detail.png はスキップします")
else:
    hour_order = ['11時台', '12時台', '13時台', '14時台', '15時台', '16時台',
                  '17時台', '18時台', '19時台', '20時台', '21時台']

    # 4月と10月を代表月として詳細表示
    rep_months = [4, 10]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for idx, month in enumerate(rep_months):
        ax = axes[idx]
        month_data = hour_month[(hour_month['月'] == month) & (hour_month['時間グループ'].isin(hour_order))].copy()
        month_data['hour_idx'] = month_data['時間グループ'].apply(lambda x: hour_order.index(x) if x in hour_order else 99)
        month_data = month_data.sort_values('hour_idx')

        x = np.arange(len(hour_order))
        width = 0.35

        # 必要列が無い場合は0埋め（念のため）
        if f'{year1}_日当たり客数' not in month_data.columns:
            month_data[f'{year1}_日当たり客数'] = 0
        if f'{year2}_日当たり客数' not in month_data.columns:
            month_data[f'{year2}_日当たり客数'] = 0

        y1_vals = month_data[f'{year1}_日当たり客数'].fillna(0).values
        y2_vals = month_data[f'{year2}_日当たり客数'].fillna(0).values

        # 長さ不一致がある場合は hour_order 側に合わせて0埋め
        if len(y1_vals) != len(hour_order):
            y1_vals = np.pad(y1_vals, (0, max(0, len(hour_order) - len(y1_vals))), constant_values=0)[:len(hour_order)]
        if len(y2_vals) != len(hour_order):
            y2_vals = np.pad(y2_vals, (0, max(0, len(hour_order) - len(y2_vals))), constant_values=0)[:len(hour_order)]

        ax.bar(x - width/2, y1_vals, width, label=f'{year1}年', color='#5DADE2')
        ax.bar(x + width/2, y2_vals, width, label=f'{year2}年', color='#F5B041')

        ax.set_xlabel('時間帯', fontsize=10)
        ax.set_ylabel('営業日当たり客数（人）', fontsize=10)
        ax.set_title(f'{month}月 - 時間帯別の客数比較', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(hour_order, rotation=45, ha='right', fontsize=9)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph07_hourly_detail.png')
    plt.close()
    print("graph07_hourly_detail.png を作成しました")

# =========================================
# 図8: 要因分析サマリー
# =========================================
factor_valid = factor_summary[factor_summary['月'].isin(valid_months)].copy()

fig, ax = plt.subplots(figsize=(14, 6))

x = np.arange(len(factor_valid))
width = 0.25

bars1 = ax.bar(x - width, factor_valid['総差分'], width, label='総差分', color='#34495E')
bars2 = ax.bar(x, factor_valid['曜日別最大差分'], width, label='曜日別最大差分', color='#3498DB')
bars3 = ax.bar(x + width, factor_valid['時間帯別最大差分'], width, label='時間帯別最大差分', color='#E67E22')

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'月別・要因別の客数増減分析（{year2}年 - {year1}年）', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels([f'{m}月' for m in factor_valid['月']])
ax.legend()
ax.grid(axis='y', alpha=0.3)

# 最大要因のラベルを追加
for i, (idx, row) in enumerate(factor_valid.iterrows()):
    if row['総差分'] > 0:
        label = f"曜:{row['最大増加曜日']}\n時:{row['最大増加時間帯'][:5]}"
        ax.annotate(label, xy=(i, row['総差分']), xytext=(0, 5), 
                    textcoords="offset points", ha='center', va='bottom', fontsize=7)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph08_factor_summary.png')
plt.close()
print("graph08_factor_summary.png を作成しました")

print("\n=== 全グラフ作成完了 ===")
