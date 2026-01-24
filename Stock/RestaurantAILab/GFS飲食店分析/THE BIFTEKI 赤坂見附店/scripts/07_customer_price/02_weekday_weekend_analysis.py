# -*- coding: utf-8 -*-
"""
THE BIFTEKI 赤坂見附店 - 平日/土日別 客単価分析
曜日・時間帯ごとの客単価分布を平日と土日で分けて可視化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ===== データ読み込み =====
print("=" * 60)
print("平日/土日別 客単価分析")
print("=" * 60)

output_dir = r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\CustomerPriceAnalysis"
orders = pd.read_csv(f"{output_dir}/02_orders_with_price_per_customer.csv")

# 日時型に変換
orders['伝票発行日'] = pd.to_datetime(orders['伝票発行日'])
orders['営業日'] = pd.to_datetime(orders['営業日'])

# 時間帯カテゴリを再作成
def categorize_hour(h):
    if 11 <= h < 14:
        return 'ランチ(11-14時)'
    elif 14 <= h < 17:
        return 'アイドル(14-17時)'
    elif 17 <= h < 20:
        return 'ディナー前半(17-20時)'
    else:
        return 'ディナー後半(20時以降)'

orders['時'] = orders['伝票発行日'].dt.hour
orders['時間帯カテゴリ'] = orders['時'].apply(categorize_hour)

# 曜日の順序設定
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
orders['曜日'] = pd.Categorical(orders['曜日'], categories=weekday_order, ordered=True)

time_order = ['ランチ(11-14時)', 'アイドル(14-17時)', 'ディナー前半(17-20時)', 'ディナー後半(20時以降)']
orders['時間帯カテゴリ'] = pd.Categorical(orders['時間帯カテゴリ'], categories=time_order, ordered=True)

# 平日/土日の分類
weekday_map = {'月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6}
orders['曜日数値'] = orders['曜日'].map(weekday_map)
orders['日種別'] = orders['曜日数値'].apply(lambda x: '土日' if x >= 5 else '平日')

# 平日と土日のデータを分離
weekday_data = orders[orders['日種別'] == '平日']
weekend_data = orders[orders['日種別'] == '土日']

print(f"\n平日データ: {len(weekday_data):,}件")
print(f"土日データ: {len(weekend_data):,}件")

# ===== Figure 1: 曜日別客単価分布（平日 vs 土日） =====
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 平日（月～金）
ax = axes[0]
weekday_only = ['月', '火', '水', '木', '金']
weekday_df = orders[orders['曜日'].isin(weekday_only)]
weekday_df.boxplot(column='客単価', by='曜日', ax=ax)
ax.set_xlabel('曜日')
ax.set_ylabel('客単価（円）')
ax.set_title(f'【平日】曜日別の客単価分布 (N={len(weekday_df):,})')
plt.suptitle('')

# 土日
ax = axes[1]
weekend_only = ['土', '日']
weekend_df = orders[orders['曜日'].isin(weekend_only)]
weekend_df.boxplot(column='客単価', by='曜日', ax=ax)
ax.set_xlabel('曜日')
ax.set_ylabel('客単価（円）')
ax.set_title(f'【土日】曜日別の客単価分布 (N={len(weekend_df):,})')
plt.suptitle('')

plt.tight_layout()
plt.savefig(f"{output_dir}/13_boxplot_weekday_by_daytype.png", dpi=150, bbox_inches='tight')
plt.close()
print("\n保存: 13_boxplot_weekday_by_daytype.png")

# ===== Figure 2: 時間帯別客単価分布（平日 vs 土日） =====
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 平日
ax = axes[0]
weekday_data.boxplot(column='客単価', by='時間帯カテゴリ', ax=ax)
ax.set_xlabel('時間帯')
ax.set_ylabel('客単価（円）')
ax.set_title(f'【平日】時間帯別の客単価分布 (N={len(weekday_data):,})')
ax.tick_params(axis='x', rotation=15)
plt.suptitle('')

# 土日
ax = axes[1]
weekend_data.boxplot(column='客単価', by='時間帯カテゴリ', ax=ax)
ax.set_xlabel('時間帯')
ax.set_ylabel('客単価（円）')
ax.set_title(f'【土日】時間帯別の客単価分布 (N={len(weekend_data):,})')
ax.tick_params(axis='x', rotation=15)
plt.suptitle('')

plt.tight_layout()
plt.savefig(f"{output_dir}/14_boxplot_hour_by_daytype.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 14_boxplot_hour_by_daytype.png")

# ===== Figure 3: 平日/土日の比較（同一グラフ上でバイオリンプロット） =====
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 時間帯別（平日 vs 土日 重ね合わせ）
ax = axes[0]
# seaborn用にデータ準備
plot_data = orders[['時間帯カテゴリ', '客単価', '日種別']].dropna()
sns.boxplot(x='時間帯カテゴリ', y='客単価', hue='日種別', data=plot_data, ax=ax, palette=['skyblue', 'salmon'])
ax.set_xlabel('時間帯')
ax.set_ylabel('客単価（円）')
ax.set_title('時間帯別 客単価分布（平日 vs 土日）')
ax.tick_params(axis='x', rotation=15)
ax.legend(title='')

# 曜日別（全曜日）
ax = axes[1]
plot_data2 = orders[['曜日', '客単価', '日種別']].dropna()
sns.boxplot(x='曜日', y='客単価', data=plot_data2, ax=ax, 
            palette=['skyblue']*5 + ['salmon']*2)
ax.set_xlabel('曜日')
ax.set_ylabel('客単価（円）')
ax.set_title('曜日別 客単価分布（青=平日、赤=土日）')
ax.axvline(4.5, color='gray', linestyle='--', alpha=0.5)  # 平日と土日の境界線

plt.tight_layout()
plt.savefig(f"{output_dir}/15_boxplot_comparison_daytype.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 15_boxplot_comparison_daytype.png")

# ===== 統計サマリー =====
print("\n" + "=" * 60)
print("【平日 vs 土日 統計サマリー】")
print("=" * 60)

# 時間帯別の平均客単価
print("\n【時間帯別 平均客単価】")
time_stats = orders.groupby(['時間帯カテゴリ', '日種別'])['客単価'].agg(['mean', 'median', 'count']).round(0)
time_stats.columns = ['平均', '中央値', '件数']
print(time_stats)

# 曜日別の平均客単価
print("\n【曜日別 平均客単価】")
weekday_stats = orders.groupby('曜日')['客単価'].agg(['mean', 'median', 'count']).round(0)
weekday_stats.columns = ['平均', '中央値', '件数']
print(weekday_stats)

# CSV保存
time_pivot = orders.pivot_table(values='客単価', index='時間帯カテゴリ', columns='日種別', 
                                 aggfunc=['mean', 'median', 'count'])
time_pivot.to_csv(f"{output_dir}/16_time_daytype_stats.csv", encoding='utf-8-sig')

weekday_stats.to_csv(f"{output_dir}/17_weekday_stats.csv", encoding='utf-8-sig')

print("\n" + "=" * 60)
print("【分析完了】")
print("=" * 60)
print("\n生成ファイル:")
print("  - 13_boxplot_weekday_by_daytype.png (曜日別：平日/土日分離)")
print("  - 14_boxplot_hour_by_daytype.png (時間帯別：平日/土日分離)")
print("  - 15_boxplot_comparison_daytype.png (平日vs土日 比較)")
print("  - 16_time_daytype_stats.csv (時間帯×日種別 統計)")
print("  - 17_weekday_stats.csv (曜日別 統計)")
