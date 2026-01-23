# -*- coding: utf-8 -*-
"""
THE BIFTEKI 赤坂見附店 - 滞在時間分析
曜日・時間帯別の滞在時間の傾向、分散、月ごとの違いを分析
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 出力ディレクトリ（絶対パスで指定）
OUTPUT_DIR = Path(r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\StayTimeAnalysis")
INPUT_FILE = Path(r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\transformed_pos_data_eatin.csv")

print("=" * 60)
print("THE BIFTEKI 赤坂見附店 - 滞在時間分析")
print("=" * 60)

# =============================================================================
# 1. データ読み込みと前処理
# =============================================================================
print("\n[1] データ読み込み...")
df = pd.read_csv(INPUT_FILE)

# 日時変換（空白や無効な値はNaTに）
df['来店時刻'] = pd.to_datetime(df['H.伝票発行日'], errors='coerce')
df['退店時刻'] = pd.to_datetime(df['H.伝票処理日'], errors='coerce')

# 無効な日時を除外
df = df.dropna(subset=['来店時刻', '退店時刻'])

# 伝票単位でユニークにする（1伝票 = 1来店）
visits = df.groupby('H.伝票番号').agg({
    '来店時刻': 'first',
    '退店時刻': 'first',
    'H.曜日': 'first',
    'H.客数（合計）': 'first',
    'H.小計': 'first'
}).reset_index()

# 滞在時間（分）を計算
visits['滞在時間_分'] = (visits['退店時刻'] - visits['来店時刻']).dt.total_seconds() / 60

# 異常値除去（0分以下、180分以上を除外）
visits_clean = visits[(visits['滞在時間_分'] > 0) & (visits['滞在時間_分'] <= 180)].copy()

# 特徴量追加
visits_clean['来店時間帯'] = visits_clean['来店時刻'].dt.hour
visits_clean['月'] = visits_clean['来店時刻'].dt.month
visits_clean['年月'] = visits_clean['来店時刻'].dt.strftime('%Y-%m')
visits_clean['日付'] = visits_clean['来店時刻'].dt.date

# 曜日を順番に並べるための変換
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
visits_clean['曜日順'] = visits_clean['H.曜日'].map({d: i for i, d in enumerate(weekday_order)})

print(f"  全伝票数: {len(visits):,}")
print(f"  有効伝票数: {len(visits_clean):,}")
print(f"  期間: {visits_clean['来店時刻'].min().date()} ~ {visits_clean['来店時刻'].max().date()}")

# 中間データ保存
visits_clean.to_csv(OUTPUT_DIR / "01_visits_with_stay_time.csv", index=False, encoding='utf-8-sig')
print(f"  保存: 01_visits_with_stay_time.csv")

# =============================================================================
# 2. 基本統計量
# =============================================================================
print("\n[2] 基本統計量...")

basic_stats = visits_clean['滞在時間_分'].describe()
print(f"\n  滞在時間の基本統計:")
print(f"    平均: {basic_stats['mean']:.1f}分")
print(f"    標準偏差: {basic_stats['std']:.1f}分")
print(f"    最小: {basic_stats['min']:.1f}分")
print(f"    25%: {basic_stats['25%']:.1f}分")
print(f"    中央値: {basic_stats['50%']:.1f}分")
print(f"    75%: {basic_stats['75%']:.1f}分")
print(f"    最大: {basic_stats['max']:.1f}分")

# =============================================================================
# 3. 曜日別の統計（平均、分散、標準偏差）
# =============================================================================
print("\n[3] 曜日別統計...")

weekday_stats = visits_clean.groupby('H.曜日')['滞在時間_分'].agg([
    'count', 'mean', 'std', 'var', 'min', 'max',
    lambda x: x.quantile(0.25),
    lambda x: x.quantile(0.50),
    lambda x: x.quantile(0.75)
]).reset_index()
weekday_stats.columns = ['曜日', '件数', '平均', '標準偏差', '分散', '最小', '最大', '25%', '中央値', '75%']
weekday_stats['曜日順'] = weekday_stats['曜日'].map({d: i for i, d in enumerate(weekday_order)})
weekday_stats = weekday_stats.sort_values('曜日順').drop('曜日順', axis=1)
weekday_stats['変動係数'] = weekday_stats['標準偏差'] / weekday_stats['平均'] * 100

weekday_stats.to_csv(OUTPUT_DIR / "02_weekday_stats.csv", index=False, encoding='utf-8-sig')
print(f"  保存: 02_weekday_stats.csv")
print(weekday_stats.to_string(index=False))

# =============================================================================
# 4. 時間帯別の統計
# =============================================================================
print("\n[4] 時間帯別統計...")

hour_stats = visits_clean.groupby('来店時間帯')['滞在時間_分'].agg([
    'count', 'mean', 'std', 'var'
]).reset_index()
hour_stats.columns = ['時間帯', '件数', '平均', '標準偏差', '分散']
hour_stats['変動係数'] = hour_stats['標準偏差'] / hour_stats['平均'] * 100

hour_stats.to_csv(OUTPUT_DIR / "03_hour_stats.csv", index=False, encoding='utf-8-sig')
print(f"  保存: 03_hour_stats.csv")
print(hour_stats.to_string(index=False))

# =============================================================================
# 5. 曜日×時間帯のクロス集計（平均・分散）
# =============================================================================
print("\n[5] 曜日×時間帯クロス集計...")

# 平均
pivot_mean = visits_clean.pivot_table(
    index='H.曜日', columns='来店時間帯', values='滞在時間_分', aggfunc='mean'
)
pivot_mean = pivot_mean.reindex(weekday_order)

# 分散
pivot_var = visits_clean.pivot_table(
    index='H.曜日', columns='来店時間帯', values='滞在時間_分', aggfunc='var'
)
pivot_var = pivot_var.reindex(weekday_order)

# 標準偏差
pivot_std = visits_clean.pivot_table(
    index='H.曜日', columns='来店時間帯', values='滞在時間_分', aggfunc='std'
)
pivot_std = pivot_std.reindex(weekday_order)

# 件数
pivot_count = visits_clean.pivot_table(
    index='H.曜日', columns='来店時間帯', values='滞在時間_分', aggfunc='count'
)
pivot_count = pivot_count.reindex(weekday_order)

pivot_mean.to_csv(OUTPUT_DIR / "04_weekday_hour_mean.csv", encoding='utf-8-sig')
pivot_var.to_csv(OUTPUT_DIR / "05_weekday_hour_variance.csv", encoding='utf-8-sig')
pivot_std.to_csv(OUTPUT_DIR / "06_weekday_hour_std.csv", encoding='utf-8-sig')
pivot_count.to_csv(OUTPUT_DIR / "07_weekday_hour_count.csv", encoding='utf-8-sig')
print(f"  保存: 04_weekday_hour_mean.csv")
print(f"  保存: 05_weekday_hour_variance.csv")
print(f"  保存: 06_weekday_hour_std.csv")
print(f"  保存: 07_weekday_hour_count.csv")

# =============================================================================
# 6. 同じ曜日の中での月別比較
# =============================================================================
print("\n[6] 曜日×月別統計（同じ曜日の月ごとの違い）...")

weekday_month_stats = visits_clean.groupby(['H.曜日', '月'])['滞在時間_分'].agg([
    'count', 'mean', 'std', 'var'
]).reset_index()
weekday_month_stats.columns = ['曜日', '月', '件数', '平均', '標準偏差', '分散']
weekday_month_stats['曜日順'] = weekday_month_stats['曜日'].map({d: i for i, d in enumerate(weekday_order)})
weekday_month_stats = weekday_month_stats.sort_values(['曜日順', '月']).drop('曜日順', axis=1)

weekday_month_stats.to_csv(OUTPUT_DIR / "08_weekday_month_stats.csv", index=False, encoding='utf-8-sig')
print(f"  保存: 08_weekday_month_stats.csv")

# 曜日ごとの月間変動を計算
print("\n  曜日ごとの月間変動（平均の標準偏差）:")
for wd in weekday_order:
    wd_data = weekday_month_stats[weekday_month_stats['曜日'] == wd]
    if len(wd_data) > 1:
        mean_of_means = wd_data['平均'].mean()
        std_of_means = wd_data['平均'].std()
        cv = std_of_means / mean_of_means * 100 if mean_of_means > 0 else 0
        print(f"    {wd}: 月間平均の変動 ±{std_of_means:.1f}分 (CV={cv:.1f}%)")

# =============================================================================
# 7. 可視化
# =============================================================================
print("\n[7] 可視化...")

# 7-1. 曜日別箱ひげ図（分散の違いを視覚化）
fig, ax = plt.subplots(figsize=(10, 6))
visits_clean_sorted = visits_clean.sort_values('曜日順')
bp = ax.boxplot([visits_clean_sorted[visits_clean_sorted['H.曜日'] == wd]['滞在時間_分'].values 
                  for wd in weekday_order],
                 labels=weekday_order, patch_artist=True)
colors = plt.cm.tab10(np.linspace(0, 1, 7))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_xlabel('曜日')
ax.set_ylabel('滞在時間（分）')
ax.set_title('曜日別 滞在時間の分布（箱ひげ図）')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "10_boxplot_weekday.png", dpi=150)
plt.close()
print(f"  保存: 10_boxplot_weekday.png")

# 7-2. 時間帯別箱ひげ図
fig, ax = plt.subplots(figsize=(12, 6))
hours = sorted(visits_clean['来店時間帯'].unique())
bp = ax.boxplot([visits_clean[visits_clean['来店時間帯'] == h]['滞在時間_分'].values 
                  for h in hours],
                 labels=[f"{h}時" for h in hours], patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor('steelblue')
    patch.set_alpha(0.7)
ax.set_xlabel('来店時間帯')
ax.set_ylabel('滞在時間（分）')
ax.set_title('時間帯別 滞在時間の分布（箱ひげ図）')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "11_boxplot_hour.png", dpi=150)
plt.close()
print(f"  保存: 11_boxplot_hour.png")

# 7-3. ヒートマップ（曜日×時間帯の平均滞在時間）
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(pivot_mean, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
            cbar_kws={'label': '平均滞在時間（分）'})
ax.set_xlabel('来店時間帯')
ax.set_ylabel('曜日')
ax.set_title('曜日×時間帯 平均滞在時間（分）')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "12_heatmap_mean.png", dpi=150)
plt.close()
print(f"  保存: 12_heatmap_mean.png")

# 7-4. ヒートマップ（曜日×時間帯の分散）
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(pivot_var, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax,
            cbar_kws={'label': '分散'})
ax.set_xlabel('来店時間帯')
ax.set_ylabel('曜日')
ax.set_title('曜日×時間帯 滞在時間の分散')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "13_heatmap_variance.png", dpi=150)
plt.close()
print(f"  保存: 13_heatmap_variance.png")

# 7-5. ヒートマップ（曜日×時間帯の標準偏差）
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(pivot_std, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
            cbar_kws={'label': '標準偏差（分）'})
ax.set_xlabel('来店時間帯')
ax.set_ylabel('曜日')
ax.set_title('曜日×時間帯 滞在時間の標準偏差（分）')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "14_heatmap_std.png", dpi=150)
plt.close()
print(f"  保存: 14_heatmap_std.png")

# 7-6. 曜日別・月別の平均滞在時間（同じ曜日の月ごと変動）
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, wd in enumerate(weekday_order):
    ax = axes[i]
    wd_data = weekday_month_stats[weekday_month_stats['曜日'] == wd]
    ax.bar(wd_data['月'], wd_data['平均'], yerr=wd_data['標準偏差'], 
           capsize=3, color=colors[i], alpha=0.7)
    ax.set_xlabel('月')
    ax.set_ylabel('平均滞在時間（分）')
    ax.set_title(f'{wd}曜日')
    ax.set_xticks(wd_data['月'])
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 50)

# 最後のパネルは非表示
axes[7].axis('off')
plt.suptitle('曜日別・月ごとの平均滞在時間（エラーバー=標準偏差）', fontsize=14)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "15_weekday_by_month.png", dpi=150)
plt.close()
print(f"  保存: 15_weekday_by_month.png")

# 7-7. 滞在時間のヒストグラム
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(visits_clean['滞在時間_分'], bins=50, edgecolor='black', alpha=0.7)
ax.axvline(visits_clean['滞在時間_分'].mean(), color='red', linestyle='--', 
           label=f'平均: {visits_clean["滞在時間_分"].mean():.1f}分')
ax.axvline(visits_clean['滞在時間_分'].median(), color='orange', linestyle='--',
           label=f'中央値: {visits_clean["滞在時間_分"].median():.1f}分')
ax.set_xlabel('滞在時間（分）')
ax.set_ylabel('頻度')
ax.set_title('滞在時間の分布')
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "16_histogram.png", dpi=150)
plt.close()
print(f"  保存: 16_histogram.png")

# 7-8. 曜日別の分散比較棒グラフ
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 分散
ax1 = axes[0]
weekday_stats_sorted = weekday_stats.copy()
weekday_stats_sorted['曜日順'] = weekday_stats_sorted['曜日'].map({d: i for i, d in enumerate(weekday_order)})
weekday_stats_sorted = weekday_stats_sorted.sort_values('曜日順')
ax1.bar(weekday_stats_sorted['曜日'], weekday_stats_sorted['分散'], 
        color=[colors[i] for i in range(7)], alpha=0.7)
ax1.set_xlabel('曜日')
ax1.set_ylabel('分散')
ax1.set_title('曜日別 滞在時間の分散')
ax1.grid(axis='y', alpha=0.3)

# 変動係数
ax2 = axes[1]
ax2.bar(weekday_stats_sorted['曜日'], weekday_stats_sorted['変動係数'], 
        color=[colors[i] for i in range(7)], alpha=0.7)
ax2.set_xlabel('曜日')
ax2.set_ylabel('変動係数（%）')
ax2.set_title('曜日別 滞在時間の変動係数（CV）')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "17_weekday_variance_cv.png", dpi=150)
plt.close()
print(f"  保存: 17_weekday_variance_cv.png")

# 7-9. 時間帯別の分散比較
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax1 = axes[0]
ax1.bar([f"{h}時" for h in hour_stats['時間帯']], hour_stats['分散'], 
        color='steelblue', alpha=0.7)
ax1.set_xlabel('時間帯')
ax1.set_ylabel('分散')
ax1.set_title('時間帯別 滞在時間の分散')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', alpha=0.3)

ax2 = axes[1]
ax2.bar([f"{h}時" for h in hour_stats['時間帯']], hour_stats['変動係数'], 
        color='steelblue', alpha=0.7)
ax2.set_xlabel('時間帯')
ax2.set_ylabel('変動係数（%）')
ax2.set_title('時間帯別 滞在時間の変動係数（CV）')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "18_hour_variance_cv.png", dpi=150)
plt.close()
print(f"  保存: 18_hour_variance_cv.png")

# =============================================================================
# 8. 統計的分析（分散の比較）
# =============================================================================
print("\n[8] 分散の比較分析...")

# 曜日間の分散比を計算
max_var = weekday_stats['分散'].max()
min_var = weekday_stats['分散'].min()
var_ratio = max_var / min_var
print(f"\n  曜日間の分散比:")
print(f"    最大分散: {max_var:.1f} ({weekday_stats.loc[weekday_stats['分散'].idxmax(), '曜日']})")
print(f"    最小分散: {min_var:.1f} ({weekday_stats.loc[weekday_stats['分散'].idxmin(), '曜日']})")
print(f"    分散比（最大/最小）: {var_ratio:.2f}")

# 時間帯間の分散比を計算
max_var_h = hour_stats['分散'].max()
min_var_h = hour_stats[hour_stats['件数'] >= 100]['分散'].min()  # 十分なサンプル数のある時間帯
var_ratio_h = max_var_h / min_var_h
print(f"\n  時間帯間の分散比:")
print(f"    最大分散: {max_var_h:.1f}")
print(f"    最小分散（n>=100）: {min_var_h:.1f}")
print(f"    分散比: {var_ratio_h:.2f}")

# 統計検定の結果プレースホルダー（scipy不要）
h_stat, p_val = 0, 0  # プレースホルダー
levene_stat, levene_p = 0, 0  # プレースホルダー

# =============================================================================
# 9. サマリーレポート作成
# =============================================================================
print("\n[9] サマリーレポート作成...")

report = f"""# THE BIFTEKI 赤坂見附店 - 滞在時間分析レポート

## 分析概要
- **分析期間**: {visits_clean['来店時刻'].min().date()} ~ {visits_clean['来店時刻'].max().date()}
- **有効伝票数**: {len(visits_clean):,}件

## 1. 基本統計量

| 指標 | 値 |
|------|-----|
| 平均滞在時間 | {basic_stats['mean']:.1f}分 |
| 標準偏差 | {basic_stats['std']:.1f}分 |
| 中央値 | {basic_stats['50%']:.1f}分 |
| 最小 | {basic_stats['min']:.1f}分 |
| 最大 | {basic_stats['max']:.1f}分 |
| 25パーセンタイル | {basic_stats['25%']:.1f}分 |
| 75パーセンタイル | {basic_stats['75%']:.1f}分 |

## 2. 曜日別統計

| 曜日 | 件数 | 平均(分) | 標準偏差 | 分散 | 変動係数(%) |
|------|------|----------|----------|------|-------------|
"""

for _, row in weekday_stats.iterrows():
    report += f"| {row['曜日']} | {row['件数']:.0f} | {row['平均']:.1f} | {row['標準偏差']:.1f} | {row['分散']:.0f} | {row['変動係数']:.1f} |\n"

report += f"""
### 曜日間の分散比較
- **分散比（最大/最小）**: {var_ratio:.2f}
- **最大分散**: {max_var:.1f}（{weekday_stats.loc[weekday_stats['分散'].idxmax(), '曜日']}曜日）
- **最小分散**: {min_var:.1f}（{weekday_stats.loc[weekday_stats['分散'].idxmin(), '曜日']}曜日）

## 3. 時間帯別統計

| 時間帯 | 件数 | 平均(分) | 標準偏差 | 分散 | 変動係数(%) |
|--------|------|----------|----------|------|-------------|
"""

for _, row in hour_stats.iterrows():
    report += f"| {row['時間帯']:.0f}時 | {row['件数']:.0f} | {row['平均']:.1f} | {row['標準偏差']:.1f} | {row['分散']:.0f} | {row['変動係数']:.1f} |\n"

report += """
## 4. 同じ曜日の月別変動

各曜日における月ごとの平均滞在時間の変動を分析しました。

"""

for wd in weekday_order:
    wd_data = weekday_month_stats[weekday_month_stats['曜日'] == wd]
    if len(wd_data) > 1:
        mean_of_means = wd_data['平均'].mean()
        std_of_means = wd_data['平均'].std()
        min_mean = wd_data['平均'].min()
        max_mean = wd_data['平均'].max()
        report += f"### {wd}曜日\n"
        report += f"- 月間平均の変動範囲: {min_mean:.1f}分 ~ {max_mean:.1f}分（差: {max_mean - min_mean:.1f}分）\n"
        report += f"- 月間平均の標準偏差: {std_of_means:.1f}分\n\n"

report += """
## 5. 主要な発見

### 分散について
"""

# 分散が最も大きい曜日・時間帯を特定
max_var_weekday = weekday_stats.loc[weekday_stats['分散'].idxmax()]
min_var_weekday = weekday_stats.loc[weekday_stats['分散'].idxmin()]
max_var_hour = hour_stats.loc[hour_stats['分散'].idxmax()]
min_var_hour = hour_stats.loc[hour_stats['分散'].idxmin()]

report += f"""
- **分散が最も大きい曜日**: {max_var_weekday['曜日']}曜日（分散={max_var_weekday['分散']:.0f}、変動係数={max_var_weekday['変動係数']:.1f}%）
- **分散が最も小さい曜日**: {min_var_weekday['曜日']}曜日（分散={min_var_weekday['分散']:.0f}、変動係数={min_var_weekday['変動係数']:.1f}%）
- **分散が最も大きい時間帯**: {max_var_hour['時間帯']:.0f}時（分散={max_var_hour['分散']:.0f}、変動係数={max_var_hour['変動係数']:.1f}%）
- **分散が最も小さい時間帯**: {min_var_hour['時間帯']:.0f}時（分散={min_var_hour['分散']:.0f}、変動係数={min_var_hour['変動係数']:.1f}%）

## 6. 生成ファイル一覧

### データファイル
- `01_visits_with_stay_time.csv` - 滞在時間を計算した伝票データ
- `02_weekday_stats.csv` - 曜日別統計
- `03_hour_stats.csv` - 時間帯別統計
- `04_weekday_hour_mean.csv` - 曜日×時間帯の平均滞在時間
- `05_weekday_hour_variance.csv` - 曜日×時間帯の分散
- `06_weekday_hour_std.csv` - 曜日×時間帯の標準偏差
- `07_weekday_hour_count.csv` - 曜日×時間帯の件数
- `08_weekday_month_stats.csv` - 曜日×月別統計

### グラフファイル
- `10_boxplot_weekday.png` - 曜日別箱ひげ図
- `11_boxplot_hour.png` - 時間帯別箱ひげ図
- `12_heatmap_mean.png` - 曜日×時間帯 平均滞在時間ヒートマップ
- `13_heatmap_variance.png` - 曜日×時間帯 分散ヒートマップ
- `14_heatmap_std.png` - 曜日×時間帯 標準偏差ヒートマップ
- `15_weekday_by_month.png` - 曜日別・月ごとの平均滞在時間
- `16_histogram.png` - 滞在時間のヒストグラム
- `17_weekday_variance_cv.png` - 曜日別の分散・変動係数
- `18_hour_variance_cv.png` - 時間帯別の分散・変動係数
"""

with open(OUTPUT_DIR / "analysis_report.md", 'w', encoding='utf-8') as f:
    f.write(report)
print(f"  保存: analysis_report.md")

print("\n" + "=" * 60)
print("分析完了！")
print("=" * 60)
