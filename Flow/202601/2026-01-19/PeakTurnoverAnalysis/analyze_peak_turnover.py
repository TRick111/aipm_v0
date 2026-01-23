# -*- coding: utf-8 -*-
"""
THE BIFTEKI 赤坂見附店 - ピーク時間帯の回転数分析
ピーク時間: 11:30〜13:30の2時間
回転数 = 1時間あたりの入店者数（人数ベース）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time
# 日本語フォント設定
import matplotlib
matplotlib.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
import warnings
warnings.filterwarnings('ignore')

# 出力フォルダ
OUTPUT_DIR = './'

# データ読み込み
print("データを読み込み中...")
df = pd.read_csv('../transformed_pos_data_eatin.csv', encoding='utf-8')

# 列名の確認
print(f"列名: {df.columns.tolist()}")

# 日時列のパース
df['伝票発行日時'] = pd.to_datetime(df['H.伝票発行日'])
df['営業日'] = pd.to_datetime(df['H.集計対象営業年月日'])

# 伝票ごとにユニークな来店を抽出（同一伝票番号の最初の行を使用）
visits = df.groupby('H.伝票番号').agg({
    '伝票発行日時': 'first',
    '営業日': 'first',
    'H.曜日': 'first',
    'H.客数（合計）': 'first'
}).reset_index()

visits.rename(columns={'H.客数（合計）': '客数'}, inplace=True)
print(f"総来店数（伝票数）: {len(visits)}")

# 来店時刻を抽出
visits['来店時刻'] = visits['伝票発行日時'].dt.time
visits['来店時間'] = visits['伝票発行日時'].dt.hour + visits['伝票発行日時'].dt.minute / 60

# ピーク時間帯の定義（11:30〜13:30）
PEAK_START = time(11, 30)
PEAK_END = time(13, 30)

def is_peak_time(t):
    """11:30〜13:30の間かどうか判定"""
    return PEAK_START <= t < PEAK_END

visits['ピーク時間帯'] = visits['来店時刻'].apply(is_peak_time)

# ピーク時間帯の来店のみ抽出
peak_visits = visits[visits['ピーク時間帯']].copy()
print(f"ピーク時間帯（11:30-13:30）の来店数: {len(peak_visits)}")

# 日別ピーク処理人数を集計
daily_peak = peak_visits.groupby('営業日').agg({
    '客数': 'sum',
    'H.伝票番号': 'count'
}).reset_index()
daily_peak.columns = ['営業日', 'ピーク処理人数', 'ピーク組数']

# 回転数（1時間あたりの人数）= ピーク処理人数 / 2時間
daily_peak['回転数_時間あたり'] = daily_peak['ピーク処理人数'] / 2

# 曜日情報を追加
daily_peak['曜日'] = daily_peak['営業日'].dt.dayofweek
daily_peak['曜日名'] = daily_peak['営業日'].dt.day_name()
daily_peak['月'] = daily_peak['営業日'].dt.month
daily_peak['年月'] = daily_peak['営業日'].dt.to_period('M')
daily_peak['週番号'] = daily_peak['営業日'].dt.isocalendar().week

# 日本語曜日マッピング
weekday_jp = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
daily_peak['曜日_jp'] = daily_peak['曜日'].map(weekday_jp)

# 平日/週末フラグ
daily_peak['週末'] = daily_peak['曜日'].isin([5, 6])

print(f"\n日別集計データ数: {len(daily_peak)}")
print(f"期間: {daily_peak['営業日'].min()} 〜 {daily_peak['営業日'].max()}")

# 基本統計量を出力
print("\n===== ピーク処理人数の基本統計 =====")
print(daily_peak['ピーク処理人数'].describe())

# CSVに保存
daily_peak.to_csv(f'{OUTPUT_DIR}daily_peak_summary.csv', index=False, encoding='utf-8-sig')
print(f"\n日別集計データを保存: daily_peak_summary.csv")

# ============================================================
# グラフ作成
# ============================================================

fig_size = (14, 8)

# ----- 1. 時系列プロット -----
fig, ax = plt.subplots(figsize=fig_size)
ax.plot(daily_peak['営業日'], daily_peak['ピーク処理人数'], marker='o', markersize=4, alpha=0.7, label='日別')
# 7日移動平均
daily_peak['移動平均7日'] = daily_peak['ピーク処理人数'].rolling(window=7, min_periods=1).mean()
ax.plot(daily_peak['営業日'], daily_peak['移動平均7日'], color='red', linewidth=2, label='7日移動平均')
ax.set_xlabel('日付')
ax.set_ylabel('ピーク処理人数（人）')
ax.set_title('THE BIFTEKI 赤坂見附店 - ピーク時間帯（11:30-13:30）処理人数の推移')
ax.legend()
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}01_timeseries_peak.png', dpi=150)
plt.close()
print("保存: 01_timeseries_peak.png")

# ----- 2. 曜日別ボックスプロット -----
fig, ax = plt.subplots(figsize=(12, 6))
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
data_by_weekday = [daily_peak[daily_peak['曜日_jp'] == w]['ピーク処理人数'].values for w in weekday_order]
bp = ax.boxplot(data_by_weekday, labels=weekday_order, patch_artist=True)
colors = ['#3498db'] * 5 + ['#e74c3c'] * 2  # 平日は青、週末は赤
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.set_xlabel('曜日')
ax.set_ylabel('ピーク処理人数（人）')
ax.set_title('曜日別ピーク処理人数の分布')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}02_boxplot_weekday.png', dpi=150)
plt.close()
print("保存: 02_boxplot_weekday.png")

# ----- 3. 曜日別平均（バーチャート） -----
fig, ax = plt.subplots(figsize=(12, 6))
weekday_means = daily_peak.groupby('曜日_jp')['ピーク処理人数'].mean().reindex(weekday_order)
weekday_std = daily_peak.groupby('曜日_jp')['ピーク処理人数'].std().reindex(weekday_order)
bars = ax.bar(weekday_order, weekday_means, yerr=weekday_std, capsize=5, color=colors, alpha=0.7)
ax.set_xlabel('曜日')
ax.set_ylabel('ピーク処理人数（人）')
ax.set_title('曜日別ピーク処理人数の平均（エラーバー: 標準偏差）')
ax.grid(True, alpha=0.3, axis='y')
# 値ラベル
for bar, mean in zip(bars, weekday_means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{mean:.1f}', 
            ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}03_bar_weekday_mean.png', dpi=150)
plt.close()
print("保存: 03_bar_weekday_mean.png")

# ----- 4. 月別トレンド -----
monthly_stats = daily_peak.groupby('年月').agg({
    'ピーク処理人数': ['mean', 'std', 'count']
}).reset_index()
monthly_stats.columns = ['年月', '平均', '標準偏差', '営業日数']
monthly_stats['年月_str'] = monthly_stats['年月'].astype(str)

fig, ax = plt.subplots(figsize=fig_size)
ax.bar(range(len(monthly_stats)), monthly_stats['平均'], 
       yerr=monthly_stats['標準偏差'], capsize=3, color='#2ecc71', alpha=0.7)
ax.set_xticks(range(len(monthly_stats)))
ax.set_xticklabels(monthly_stats['年月_str'], rotation=45, ha='right')
ax.set_xlabel('年月')
ax.set_ylabel('ピーク処理人数（人）')
ax.set_title('月別ピーク処理人数の平均（エラーバー: 標準偏差）')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}04_bar_monthly_trend.png', dpi=150)
plt.close()
print("保存: 04_bar_monthly_trend.png")

# 月別統計をCSV保存
monthly_stats.to_csv(f'{OUTPUT_DIR}monthly_peak_stats.csv', index=False, encoding='utf-8-sig')
print("保存: monthly_peak_stats.csv")

# ----- 5. 平日 vs 週末 比較 -----
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 5a. ボックスプロット
weekday_data = daily_peak[~daily_peak['週末']]['ピーク処理人数']
weekend_data = daily_peak[daily_peak['週末']]['ピーク処理人数']

bp = axes[0].boxplot([weekday_data, weekend_data], labels=['平日', '週末'], patch_artist=True)
bp['boxes'][0].set_facecolor('#3498db')
bp['boxes'][1].set_facecolor('#e74c3c')
for box in bp['boxes']:
    box.set_alpha(0.6)
axes[0].set_ylabel('ピーク処理人数（人）')
axes[0].set_title('平日 vs 週末：ピーク処理人数の分布')
axes[0].grid(True, alpha=0.3, axis='y')

# 5b. 統計サマリ
summary_data = {
    '区分': ['平日', '週末'],
    '平均': [weekday_data.mean(), weekend_data.mean()],
    '中央値': [weekday_data.median(), weekend_data.median()],
    '標準偏差': [weekday_data.std(), weekend_data.std()],
    '最小': [weekday_data.min(), weekend_data.min()],
    '最大': [weekday_data.max(), weekend_data.max()],
    'サンプル数': [len(weekday_data), len(weekend_data)]
}
summary_df = pd.DataFrame(summary_data)

axes[1].axis('off')
table = axes[1].table(cellText=summary_df.round(1).values,
                      colLabels=summary_df.columns,
                      cellLoc='center',
                      loc='center')
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.5)
axes[1].set_title('平日 vs 週末：統計サマリ')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}05_weekday_weekend_comparison.png', dpi=150)
plt.close()
print("保存: 05_weekday_weekend_comparison.png")

# ----- 6. 週番号別トレンド（季節性を見る） -----
daily_peak['週番号_int'] = daily_peak['週番号'].astype(int)
weekly_stats = daily_peak.groupby('週番号_int').agg({
    'ピーク処理人数': ['mean', 'std', 'count']
}).reset_index()
weekly_stats.columns = ['週番号', '平均', '標準偏差', 'サンプル数']
weekly_stats['標準偏差'] = weekly_stats['標準偏差'].fillna(0)

fig, ax = plt.subplots(figsize=fig_size)
x_vals = weekly_stats['週番号'].values.astype(float)
y_vals = weekly_stats['平均'].values.astype(float)
y_std = weekly_stats['標準偏差'].values.astype(float)
ax.plot(x_vals, y_vals, marker='o', markersize=6, color='#9b59b6')
ax.fill_between(x_vals, y_vals - y_std, y_vals + y_std, alpha=0.2, color='#9b59b6')
ax.set_xlabel('週番号（年間）')
ax.set_ylabel('ピーク処理人数（人）')
ax.set_title('週番号別ピーク処理人数の平均（帯: ±1標準偏差）')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}06_weekly_trend.png', dpi=150)
plt.close()
print("保存: 06_weekly_trend.png")

# ----- 7. ヒストグラム -----
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(daily_peak['ピーク処理人数'], bins=30, edgecolor='black', alpha=0.7, color='#1abc9c')
ax.axvline(daily_peak['ピーク処理人数'].mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {daily_peak["ピーク処理人数"].mean():.1f}')
ax.axvline(daily_peak['ピーク処理人数'].median(), color='orange', linestyle='--', linewidth=2, label=f'中央値: {daily_peak["ピーク処理人数"].median():.1f}')
ax.set_xlabel('ピーク処理人数（人）')
ax.set_ylabel('頻度（日数）')
ax.set_title('ピーク処理人数の分布')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}07_histogram.png', dpi=150)
plt.close()
print("保存: 07_histogram.png")

# ----- 8. 月×曜日 ヒートマップ -----
pivot_table = daily_peak.pivot_table(values='ピーク処理人数', 
                                      index='月', 
                                      columns='曜日_jp', 
                                      aggfunc='mean')
pivot_table = pivot_table.reindex(columns=weekday_order)

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(pivot_table.values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(weekday_order)))
ax.set_xticklabels(weekday_order)
ax.set_yticks(range(len(pivot_table.index)))
ax.set_yticklabels([f'{m}月' for m in pivot_table.index])
ax.set_xlabel('曜日')
ax.set_ylabel('月')
ax.set_title('月×曜日別 ピーク処理人数ヒートマップ（平均）')

# 値を表示
for i in range(len(pivot_table.index)):
    for j in range(len(weekday_order)):
        val = pivot_table.values[i, j]
        if not np.isnan(val):
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=9,
                   color='white' if val > pivot_table.values[~np.isnan(pivot_table.values)].mean() else 'black')

plt.colorbar(im, label='ピーク処理人数（人）')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}08_heatmap_month_weekday.png', dpi=150)
plt.close()
print("保存: 08_heatmap_month_weekday.png")

# ----- 9. 年月×曜日 ヒートマップ（詳細版） -----
daily_peak['年月_str'] = daily_peak['年月'].astype(str)
pivot_detailed = daily_peak.pivot_table(values='ピーク処理人数', 
                                         index='年月_str', 
                                         columns='曜日_jp', 
                                         aggfunc='mean')
pivot_detailed = pivot_detailed.reindex(columns=weekday_order)

fig, ax = plt.subplots(figsize=(14, max(8, len(pivot_detailed) * 0.5)))
im = ax.imshow(pivot_detailed.values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(weekday_order)))
ax.set_xticklabels(weekday_order)
ax.set_yticks(range(len(pivot_detailed.index)))
ax.set_yticklabels(pivot_detailed.index)
ax.set_xlabel('曜日')
ax.set_ylabel('年月')
ax.set_title('年月×曜日別 ピーク処理人数ヒートマップ（平均）')

for i in range(len(pivot_detailed.index)):
    for j in range(len(weekday_order)):
        val = pivot_detailed.values[i, j]
        if not np.isnan(val):
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=8,
                   color='white' if val > np.nanmean(pivot_detailed.values) else 'black')

plt.colorbar(im, label='ピーク処理人数（人）')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}09_heatmap_yearmonth_weekday.png', dpi=150)
plt.close()
print("保存: 09_heatmap_yearmonth_weekday.png")

# ----- 10. 回転数（時間あたり）の推移 -----
fig, ax = plt.subplots(figsize=fig_size)
ax.plot(daily_peak['営業日'], daily_peak['回転数_時間あたり'], marker='o', markersize=4, alpha=0.7, label='日別')
daily_peak['回転数_移動平均7日'] = daily_peak['回転数_時間あたり'].rolling(window=7, min_periods=1).mean()
ax.plot(daily_peak['営業日'], daily_peak['回転数_移動平均7日'], color='red', linewidth=2, label='7日移動平均')
ax.set_xlabel('日付')
ax.set_ylabel('回転数（人/時間）')
ax.set_title('ピーク時間帯の回転数（1時間あたりの入店者数）の推移')
ax.legend()
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}10_timeseries_turnover.png', dpi=150)
plt.close()
print("保存: 10_timeseries_turnover.png")

# ----- 11. 日付の特徴分析（月初/月末/給料日周辺など） -----
daily_peak['日'] = daily_peak['営業日'].dt.day
daily_peak['月末フラグ'] = daily_peak['日'] >= 25
daily_peak['月初フラグ'] = daily_peak['日'] <= 5
daily_peak['給料日周辺'] = daily_peak['日'].isin([24, 25, 26, 27, 28])  # 25日給料日仮定

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 月初 vs その他
month_start = daily_peak[daily_peak['月初フラグ']]['ピーク処理人数']
month_other = daily_peak[~daily_peak['月初フラグ']]['ピーク処理人数']
bp1 = axes[0].boxplot([month_start, month_other], labels=['月初(1-5日)', 'その他'], patch_artist=True)
bp1['boxes'][0].set_facecolor('#3498db')
bp1['boxes'][1].set_facecolor('#95a5a6')
axes[0].set_ylabel('ピーク処理人数（人）')
axes[0].set_title(f'月初 vs その他\n(平均: {month_start.mean():.1f} vs {month_other.mean():.1f})')
axes[0].grid(True, alpha=0.3, axis='y')

# 月末 vs その他
month_end = daily_peak[daily_peak['月末フラグ']]['ピーク処理人数']
month_other2 = daily_peak[~daily_peak['月末フラグ']]['ピーク処理人数']
bp2 = axes[1].boxplot([month_end, month_other2], labels=['月末(25日〜)', 'その他'], patch_artist=True)
bp2['boxes'][0].set_facecolor('#e74c3c')
bp2['boxes'][1].set_facecolor('#95a5a6')
axes[1].set_ylabel('ピーク処理人数（人）')
axes[1].set_title(f'月末 vs その他\n(平均: {month_end.mean():.1f} vs {month_other2.mean():.1f})')
axes[1].grid(True, alpha=0.3, axis='y')

# 給料日周辺 vs その他
payday = daily_peak[daily_peak['給料日周辺']]['ピーク処理人数']
payday_other = daily_peak[~daily_peak['給料日周辺']]['ピーク処理人数']
bp3 = axes[2].boxplot([payday, payday_other], labels=['給料日周辺(24-28日)', 'その他'], patch_artist=True)
bp3['boxes'][0].set_facecolor('#f39c12')
bp3['boxes'][1].set_facecolor('#95a5a6')
axes[2].set_ylabel('ピーク処理人数（人）')
axes[2].set_title(f'給料日周辺 vs その他\n(平均: {payday.mean():.1f} vs {payday_other.mean():.1f})')
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}11_date_features.png', dpi=150)
plt.close()
print("保存: 11_date_features.png")

# ----- 12. 日付×ピーク処理人数のパターン -----
daily_avg_by_day = daily_peak.groupby('日')['ピーク処理人数'].mean()

fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(daily_avg_by_day.index, daily_avg_by_day.values, color='#16a085', alpha=0.7)
ax.axhline(daily_peak['ピーク処理人数'].mean(), color='red', linestyle='--', label='全体平均')
ax.set_xlabel('日付（日）')
ax.set_ylabel('ピーク処理人数（人）')
ax.set_title('日付（1〜31日）別ピーク処理人数の平均')
ax.set_xticks(range(1, 32))
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}12_day_of_month_pattern.png', dpi=150)
plt.close()
print("保存: 12_day_of_month_pattern.png")

# ----- 13. 組あたりの平均人数（グループサイズ）の推移 -----
daily_peak['平均グループサイズ'] = daily_peak['ピーク処理人数'] / daily_peak['ピーク組数']

fig, ax = plt.subplots(figsize=fig_size)
ax.plot(daily_peak['営業日'], daily_peak['平均グループサイズ'], marker='o', markersize=4, alpha=0.7, label='日別')
daily_peak['グループサイズ_移動平均7日'] = daily_peak['平均グループサイズ'].rolling(window=7, min_periods=1).mean()
ax.plot(daily_peak['営業日'], daily_peak['グループサイズ_移動平均7日'], color='red', linewidth=2, label='7日移動平均')
ax.set_xlabel('日付')
ax.set_ylabel('平均グループサイズ（人/組）')
ax.set_title('ピーク時間帯の平均グループサイズの推移')
ax.legend()
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}13_group_size_trend.png', dpi=150)
plt.close()
print("保存: 13_group_size_trend.png")

# ----- 14. 曜日別グループサイズ -----
fig, ax = plt.subplots(figsize=(12, 6))
group_size_by_weekday = daily_peak.groupby('曜日_jp')['平均グループサイズ'].mean().reindex(weekday_order)
bars = ax.bar(weekday_order, group_size_by_weekday, color=colors, alpha=0.7)
ax.set_xlabel('曜日')
ax.set_ylabel('平均グループサイズ（人/組）')
ax.set_title('曜日別平均グループサイズ')
ax.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, group_size_by_weekday):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{val:.2f}', 
            ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}14_group_size_weekday.png', dpi=150)
plt.close()
print("保存: 14_group_size_weekday.png")

# ----- 15. 前週比較（週ごとの変動） -----
daily_peak['年_週'] = daily_peak['営業日'].dt.strftime('%Y-W%W')
weekly_total = daily_peak.groupby('年_週').agg({
    'ピーク処理人数': 'sum',
    '営業日': 'count'
}).reset_index()
weekly_total.columns = ['年_週', '週間処理人数', '営業日数']
weekly_total['前週比'] = weekly_total['週間処理人数'].pct_change() * 100

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 週間処理人数
axes[0].bar(range(len(weekly_total)), weekly_total['週間処理人数'], color='#3498db', alpha=0.7)
axes[0].set_xticks(range(0, len(weekly_total), max(1, len(weekly_total)//20)))
axes[0].set_xticklabels([weekly_total['年_週'].iloc[i] for i in range(0, len(weekly_total), max(1, len(weekly_total)//20))], rotation=45, ha='right')
axes[0].set_ylabel('週間ピーク処理人数（人）')
axes[0].set_title('週別ピーク処理人数')
axes[0].grid(True, alpha=0.3, axis='y')

# 前週比
colors_wow = ['#2ecc71' if x >= 0 else '#e74c3c' for x in weekly_total['前週比'].fillna(0)]
axes[1].bar(range(len(weekly_total)), weekly_total['前週比'].fillna(0), color=colors_wow, alpha=0.7)
axes[1].axhline(0, color='black', linewidth=0.5)
axes[1].set_xticks(range(0, len(weekly_total), max(1, len(weekly_total)//20)))
axes[1].set_xticklabels([weekly_total['年_週'].iloc[i] for i in range(0, len(weekly_total), max(1, len(weekly_total)//20))], rotation=45, ha='right')
axes[1].set_ylabel('前週比（%）')
axes[1].set_title('週別ピーク処理人数の前週比')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}15_weekly_comparison.png', dpi=150)
plt.close()
print("保存: 15_weekly_comparison.png")

# ============================================================
# サマリレポート作成
# ============================================================
print("\n" + "="*60)
print("分析サマリ")
print("="*60)

summary_text = f"""
# THE BIFTEKI 赤坂見附店 - ピーク時間帯処理人数分析レポート

## 分析概要
- **分析期間**: {daily_peak['営業日'].min().strftime('%Y-%m-%d')} 〜 {daily_peak['営業日'].max().strftime('%Y-%m-%d')}
- **ピーク時間帯**: 11:30〜13:30（2時間）
- **総営業日数**: {len(daily_peak)}日
- **総ピーク来店組数**: {daily_peak['ピーク組数'].sum():,}組
- **総ピーク処理人数**: {daily_peak['ピーク処理人数'].sum():,}人

## 基本統計（ピーク処理人数/日）
- **平均**: {daily_peak['ピーク処理人数'].mean():.1f}人
- **中央値**: {daily_peak['ピーク処理人数'].median():.1f}人
- **標準偏差**: {daily_peak['ピーク処理人数'].std():.1f}人
- **最小**: {daily_peak['ピーク処理人数'].min():.0f}人
- **最大**: {daily_peak['ピーク処理人数'].max():.0f}人

## 回転数（1時間あたりの入店者数）
- **平均**: {daily_peak['回転数_時間あたり'].mean():.1f}人/時間
- **中央値**: {daily_peak['回転数_時間あたり'].median():.1f}人/時間

## 曜日別傾向
| 曜日 | 平均 | 標準偏差 | サンプル数 |
|------|------|----------|------------|
"""

for w in weekday_order:
    w_data = daily_peak[daily_peak['曜日_jp'] == w]['ピーク処理人数']
    summary_text += f"| {w} | {w_data.mean():.1f} | {w_data.std():.1f} | {len(w_data)} |\n"

summary_text += f"""
## 平日 vs 週末
- **平日平均**: {weekday_data.mean():.1f}人（{len(weekday_data)}日）
- **週末平均**: {weekend_data.mean():.1f}人（{len(weekend_data)}日）
- **差**: {weekend_data.mean() - weekday_data.mean():+.1f}人（週末が{'多い' if weekend_data.mean() > weekday_data.mean() else '少ない'}）

## 月別傾向
| 年月 | 平均 | 標準偏差 | 営業日数 |
|------|------|----------|----------|
"""

for _, row in monthly_stats.iterrows():
    summary_text += f"| {row['年月_str']} | {row['平均']:.1f} | {row['標準偏差']:.1f} | {int(row['営業日数'])} |\n"

summary_text += f"""
## 日付特徴分析
- **月初（1-5日）平均**: {month_start.mean():.1f}人
- **月末（25日〜）平均**: {month_end.mean():.1f}人
- **給料日周辺（24-28日）平均**: {payday.mean():.1f}人
- **全体平均**: {daily_peak['ピーク処理人数'].mean():.1f}人

## グループサイズ（組あたり人数）
- **全体平均**: {daily_peak['平均グループサイズ'].mean():.2f}人/組
- **平日平均**: {daily_peak[~daily_peak['週末']]['平均グループサイズ'].mean():.2f}人/組
- **週末平均**: {daily_peak[daily_peak['週末']]['平均グループサイズ'].mean():.2f}人/組

## 出力ファイル
### CSV
- `daily_peak_summary.csv`: 日別ピーク処理人数データ
- `monthly_peak_stats.csv`: 月別統計

### グラフ
1. `01_timeseries_peak.png`: ピーク処理人数の時系列推移
2. `02_boxplot_weekday.png`: 曜日別ボックスプロット
3. `03_bar_weekday_mean.png`: 曜日別平均（バーチャート）
4. `04_bar_monthly_trend.png`: 月別トレンド
5. `05_weekday_weekend_comparison.png`: 平日 vs 週末比較
6. `06_weekly_trend.png`: 週番号別トレンド（季節性）
7. `07_histogram.png`: ピーク処理人数のヒストグラム
8. `08_heatmap_month_weekday.png`: 月×曜日ヒートマップ
9. `09_heatmap_yearmonth_weekday.png`: 年月×曜日ヒートマップ
10. `10_timeseries_turnover.png`: 回転数の時系列推移
11. `11_date_features.png`: 日付特徴分析（月初/月末/給料日）
12. `12_day_of_month_pattern.png`: 日付（1〜31日）別パターン
13. `13_group_size_trend.png`: グループサイズの時系列推移
14. `14_group_size_weekday.png`: 曜日別グループサイズ
15. `15_weekly_comparison.png`: 週別比較と前週比
"""

with open(f'{OUTPUT_DIR}analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(summary_text)

print(summary_text)
print("\n分析完了！")
print(f"出力フォルダ: {OUTPUT_DIR}")
