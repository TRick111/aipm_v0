# -*- coding: utf-8 -*-
"""
THE BIFTEKI 赤坂見附店 - 客単価分析
客単価の高い組と低い組の傾向を分析する
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ===== データ読み込み =====
print("=" * 60)
print("THE BIFTEKI 赤坂見附店 - 客単価分析")
print("=" * 60)

input_path = r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\transformed_pos_data_eatin.csv"
df = pd.read_csv(input_path)

print(f"\n【元データ】")
print(f"  総行数: {len(df):,}")
print(f"  カラム: {list(df.columns)}")

# ===== 伝票単位で集約 =====
# 伝票ヘッダー情報（各伝票で固定の値）
header_cols = ['H.伝票番号', 'H.集計対象営業年月日', 'H.曜日', 'H.伝票発行日', 
               'H.伝票処理日', 'H.客数（合計）', 'H.小計', 'H.総商品数']

# 伝票単位でユニークに
orders = df.groupby('H.伝票番号').first()[header_cols[1:]].reset_index()
orders.columns = ['伝票番号', '営業日', '曜日', '伝票発行日', '伝票処理日', '客数', '小計', '総商品数']

# 客数が0の行を除外（客単価計算不可）
orders = orders[orders['客数'] > 0]

# 客単価を計算（小計 ÷ 客数）
orders['客単価'] = orders['小計'] / orders['客数']

# 時刻情報を抽出（エラーを無視）
orders['伝票発行日'] = pd.to_datetime(orders['伝票発行日'], errors='coerce')
orders['伝票処理日'] = pd.to_datetime(orders['伝票処理日'], errors='coerce')
orders['営業日'] = pd.to_datetime(orders['営業日'], errors='coerce')

# 日時データが不正な行を除外
orders = orders.dropna(subset=['伝票発行日', '伝票処理日', '営業日'])

# 客単価が異常値（無限大、NaN）の行を除外
orders = orders[np.isfinite(orders['客単価'])]

orders['時'] = orders['伝票発行日'].dt.hour
orders['分'] = orders['伝票発行日'].dt.minute
orders['時間帯'] = orders['時'] + orders['分'] / 60  # 時間を小数で表現

# 滞在時間（分）
orders['滞在時間'] = (orders['伝票処理日'] - orders['伝票発行日']).dt.total_seconds() / 60

# 曜日を数値に変換（月=0, 火=1, ..., 日=6）
weekday_map = {'月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6}
orders['曜日数値'] = orders['曜日'].map(weekday_map)

# 平日/週末フラグ
orders['週末'] = orders['曜日数値'].apply(lambda x: 1 if x >= 5 else 0)

# 時間帯カテゴリ
def categorize_hour(h):
    if 11 <= h < 14:
        return 'ランチ(11-14時)'
    elif 14 <= h < 17:
        return 'アイドル(14-17時)'
    elif 17 <= h < 20:
        return 'ディナー前半(17-20時)'
    else:
        return 'ディナー後半(20時以降)'

orders['時間帯カテゴリ'] = orders['時'].apply(categorize_hour)

print(f"\n【集約後データ】")
print(f"  伝票数（会計数）: {len(orders):,}")
print(f"  期間: {orders['営業日'].min().strftime('%Y-%m-%d')} ～ {orders['営業日'].max().strftime('%Y-%m-%d')}")

# ===== 基本統計 =====
print(f"\n【客単価の基本統計】")
print(orders['客単価'].describe())

# 中間データ保存
output_dir = r"c:\Users\auk1i\aipm_v0\Flow\202601\2026-01-21\CustomerPriceAnalysis"
orders.to_csv(f"{output_dir}/02_orders_with_price_per_customer.csv", index=False, encoding='utf-8-sig')
print(f"\n中間データを保存: 02_orders_with_price_per_customer.csv")

# ===== 商品カテゴリ情報を追加 =====
# 各伝票でアルコールを注文したかどうか
alcohol_orders = df[df['D.商品カテゴリ2'] == 'アルコール'].groupby('H.伝票番号').size().reset_index(name='アルコール品数')
drink_orders = df[df['D.商品カテゴリ2'] == 'ソフトドリンク'].groupby('H.伝票番号').size().reset_index(name='ソフトドリンク品数')
topping_orders = df[df['D.商品カテゴリ2'] == 'トッピング'].groupby('H.伝票番号').size().reset_index(name='トッピング品数')

orders = orders.merge(alcohol_orders, left_on='伝票番号', right_on='H.伝票番号', how='left')
orders = orders.merge(drink_orders, left_on='伝票番号', right_on='H.伝票番号', how='left')
orders = orders.merge(topping_orders, left_on='伝票番号', right_on='H.伝票番号', how='left')

# 不要カラム削除とNaN埋め
orders = orders.drop(columns=['H.伝票番号_x', 'H.伝票番号_y', 'H.伝票番号'], errors='ignore')
orders['アルコール品数'] = orders['アルコール品数'].fillna(0).astype(int)
orders['ソフトドリンク品数'] = orders['ソフトドリンク品数'].fillna(0).astype(int)
orders['トッピング品数'] = orders['トッピング品数'].fillna(0).fillna(0).astype(int)

# アルコールありフラグ
orders['アルコールあり'] = (orders['アルコール品数'] > 0).astype(int)

# ===== 相関分析 =====
print("\n" + "=" * 60)
print("【相関分析】")
print("=" * 60)

# 相関を計算する数値カラム
corr_cols = ['客単価', '客数', '総商品数', '時間帯', '曜日数値', '週末', '滞在時間', 
             'アルコール品数', 'ソフトドリンク品数', 'トッピング品数', 'アルコールあり']

# 欠損値を除外
orders_clean = orders[corr_cols].dropna()

# 相関行列
corr_matrix = orders_clean.corr()

print("\n【客単価との相関係数】")
print(corr_matrix['客単価'].sort_values(ascending=False))

# ===== 可視化 =====
print("\n" + "=" * 60)
print("【グラフ出力開始】")
print("=" * 60)

# Figure 1: 相関行列ヒートマップ
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax)
ax.set_title('客単価と各要素の相関行列', fontsize=14)
plt.tight_layout()
plt.savefig(f"{output_dir}/03_correlation_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 03_correlation_heatmap.png")

# Figure 2: 散布図マトリックス（主要要素）
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 2-1: 客単価 vs 時間帯
ax = axes[0, 0]
ax.scatter(orders['時間帯'], orders['客単価'], alpha=0.3, s=10)
ax.set_xlabel('時間帯（時）')
ax.set_ylabel('客単価（円）')
ax.set_title('時間帯と客単価')
z = np.polyfit(orders['時間帯'].dropna(), orders.loc[orders['時間帯'].notna(), '客単価'], 1)
p = np.poly1d(z)
x_line = np.linspace(orders['時間帯'].min(), orders['時間帯'].max(), 100)
ax.plot(x_line, p(x_line), "r--", alpha=0.8, label=f'回帰線')
ax.legend()

# 2-2: 客単価 vs 客数
ax = axes[0, 1]
ax.scatter(orders['客数'], orders['客単価'], alpha=0.3, s=10)
ax.set_xlabel('客数（人）')
ax.set_ylabel('客単価（円）')
ax.set_title('客数と客単価')

# 2-3: 客単価 vs 総商品数
ax = axes[0, 2]
ax.scatter(orders['総商品数'], orders['客単価'], alpha=0.3, s=10)
ax.set_xlabel('総商品数')
ax.set_ylabel('客単価（円）')
ax.set_title('総商品数と客単価')

# 2-4: 客単価 vs 滞在時間
ax = axes[1, 0]
valid = orders['滞在時間'].between(0, 120)  # 外れ値除外
ax.scatter(orders.loc[valid, '滞在時間'], orders.loc[valid, '客単価'], alpha=0.3, s=10)
ax.set_xlabel('滞在時間（分）')
ax.set_ylabel('客単価（円）')
ax.set_title('滞在時間と客単価')

# 2-5: 客単価 vs アルコール品数
ax = axes[1, 1]
ax.scatter(orders['アルコール品数'], orders['客単価'], alpha=0.3, s=10)
ax.set_xlabel('アルコール品数')
ax.set_ylabel('客単価（円）')
ax.set_title('アルコール品数と客単価')

# 2-6: 客単価 vs トッピング品数
ax = axes[1, 2]
ax.scatter(orders['トッピング品数'], orders['客単価'], alpha=0.3, s=10)
ax.set_xlabel('トッピング品数')
ax.set_ylabel('客単価（円）')
ax.set_title('トッピング品数と客単価')

plt.suptitle('客単価と各要素の散布図', fontsize=14)
plt.tight_layout()
plt.savefig(f"{output_dir}/04_scatter_plots.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 04_scatter_plots.png")

# Figure 3: 曜日別・時間帯別の客単価分布
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 3-1: 曜日別
ax = axes[0]
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
orders['曜日'] = pd.Categorical(orders['曜日'], categories=weekday_order, ordered=True)
orders.boxplot(column='客単価', by='曜日', ax=ax)
ax.set_xlabel('曜日')
ax.set_ylabel('客単価（円）')
ax.set_title('曜日別の客単価分布')
plt.suptitle('')

# 3-2: 時間帯カテゴリ別
ax = axes[1]
time_order = ['ランチ(11-14時)', 'アイドル(14-17時)', 'ディナー前半(17-20時)', 'ディナー後半(20時以降)']
orders['時間帯カテゴリ'] = pd.Categorical(orders['時間帯カテゴリ'], categories=time_order, ordered=True)
orders.boxplot(column='客単価', by='時間帯カテゴリ', ax=ax)
ax.set_xlabel('時間帯')
ax.set_ylabel('客単価（円）')
ax.set_title('時間帯別の客単価分布')
plt.suptitle('')

plt.tight_layout()
plt.savefig(f"{output_dir}/05_boxplot_weekday_hour.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 05_boxplot_weekday_hour.png")

# Figure 4: アルコールあり/なしの比較
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 4-1: アルコールあり/なし
ax = axes[0]
orders.boxplot(column='客単価', by='アルコールあり', ax=ax)
ax.set_xlabel('アルコールあり (0=なし, 1=あり)')
ax.set_ylabel('客単価（円）')
ax.set_title('アルコール有無と客単価')
plt.suptitle('')

# 4-2: 週末/平日
ax = axes[1]
orders.boxplot(column='客単価', by='週末', ax=ax)
ax.set_xlabel('週末 (0=平日, 1=週末)')
ax.set_ylabel('客単価（円）')
ax.set_title('平日/週末と客単価')
plt.suptitle('')

plt.tight_layout()
plt.savefig(f"{output_dir}/06_boxplot_alcohol_weekend.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 06_boxplot_alcohol_weekend.png")

# Figure 5: 客単価の分布とヒストグラム
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 5-1: 客単価のヒストグラム
ax = axes[0]
ax.hist(orders['客単価'], bins=50, edgecolor='black', alpha=0.7)
ax.axvline(orders['客単価'].median(), color='red', linestyle='--', label=f'中央値: {orders["客単価"].median():,.0f}円')
ax.axvline(orders['客単価'].mean(), color='blue', linestyle='--', label=f'平均値: {orders["客単価"].mean():,.0f}円')
ax.set_xlabel('客単価（円）')
ax.set_ylabel('頻度')
ax.set_title('客単価の分布')
ax.legend()

# 5-2: 客単価の累積分布
ax = axes[1]
sorted_price = np.sort(orders['客単価'])
cum_prob = np.arange(1, len(sorted_price) + 1) / len(sorted_price)
ax.plot(sorted_price, cum_prob)
ax.axhline(0.25, color='gray', linestyle=':', alpha=0.7)
ax.axhline(0.75, color='gray', linestyle=':', alpha=0.7)
q1 = orders['客単価'].quantile(0.25)
q3 = orders['客単価'].quantile(0.75)
ax.axvline(q1, color='orange', linestyle='--', label=f'Q1(25%): {q1:,.0f}円')
ax.axvline(q3, color='green', linestyle='--', label=f'Q3(75%): {q3:,.0f}円')
ax.set_xlabel('客単価（円）')
ax.set_ylabel('累積確率')
ax.set_title('客単価の累積分布')
ax.legend()

plt.tight_layout()
plt.savefig(f"{output_dir}/07_price_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 07_price_distribution.png")

# ===== 高単価・低単価グループの特徴分析 =====
print("\n" + "=" * 60)
print("【高単価/低単価グループの比較】")
print("=" * 60)

# 四分位で分類
q1 = orders['客単価'].quantile(0.25)
q3 = orders['客単価'].quantile(0.75)

low_group = orders[orders['客単価'] <= q1].copy()
high_group = orders[orders['客単価'] >= q3].copy()

print(f"\n低単価グループ(下位25%): 客単価 <= {q1:,.0f}円, N={len(low_group)}")
print(f"高単価グループ(上位25%): 客単価 >= {q3:,.0f}円, N={len(high_group)}")

# 比較表の作成
comparison_cols = ['客数', '総商品数', '時間帯', '滞在時間', 'アルコール品数', 'トッピング品数']

comparison_df = pd.DataFrame({
    '指標': comparison_cols,
    '低単価(平均)': [low_group[c].mean() for c in comparison_cols],
    '高単価(平均)': [high_group[c].mean() for c in comparison_cols],
    '全体(平均)': [orders[c].mean() for c in comparison_cols]
})
comparison_df['差分(高-低)'] = comparison_df['高単価(平均)'] - comparison_df['低単価(平均)']

print("\n【数値指標の比較】")
print(comparison_df.to_string(index=False))

# カテゴリ変数の比較
print("\n【曜日分布の比較】")
low_weekday = low_group['曜日'].value_counts(normalize=True).sort_index() * 100
high_weekday = high_group['曜日'].value_counts(normalize=True).sort_index() * 100
weekday_comp = pd.DataFrame({
    '曜日': weekday_order,
    '低単価(%)': [low_weekday.get(d, 0) for d in weekday_order],
    '高単価(%)': [high_weekday.get(d, 0) for d in weekday_order]
})
weekday_comp['差分'] = weekday_comp['高単価(%)'] - weekday_comp['低単価(%)']
print(weekday_comp.to_string(index=False))

print("\n【時間帯分布の比較】")
low_time = low_group['時間帯カテゴリ'].value_counts(normalize=True) * 100
high_time = high_group['時間帯カテゴリ'].value_counts(normalize=True) * 100
time_comp = pd.DataFrame({
    '時間帯': time_order,
    '低単価(%)': [low_time.get(t, 0) for t in time_order],
    '高単価(%)': [high_time.get(t, 0) for t in time_order]
})
time_comp['差分'] = time_comp['高単価(%)'] - time_comp['低単価(%)']
print(time_comp.to_string(index=False))

print("\n【アルコール注文率の比較】")
low_alcohol_rate = low_group['アルコールあり'].mean() * 100
high_alcohol_rate = high_group['アルコールあり'].mean() * 100
print(f"  低単価グループ: {low_alcohol_rate:.1f}%")
print(f"  高単価グループ: {high_alcohol_rate:.1f}%")

# Figure 6: 高単価/低単価グループの比較
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 6-1: 時間帯分布
ax = axes[0, 0]
x = np.arange(len(time_order))
width = 0.35
ax.bar(x - width/2, [low_time.get(t, 0) for t in time_order], width, label='低単価', color='skyblue')
ax.bar(x + width/2, [high_time.get(t, 0) for t in time_order], width, label='高単価', color='salmon')
ax.set_xticks(x)
ax.set_xticklabels(time_order, rotation=15)
ax.set_ylabel('割合(%)')
ax.set_title('時間帯分布（低単価 vs 高単価）')
ax.legend()

# 6-2: 曜日分布
ax = axes[0, 1]
x = np.arange(len(weekday_order))
ax.bar(x - width/2, [low_weekday.get(d, 0) for d in weekday_order], width, label='低単価', color='skyblue')
ax.bar(x + width/2, [high_weekday.get(d, 0) for d in weekday_order], width, label='高単価', color='salmon')
ax.set_xticks(x)
ax.set_xticklabels(weekday_order)
ax.set_ylabel('割合(%)')
ax.set_title('曜日分布（低単価 vs 高単価）')
ax.legend()

# 6-3: 客数分布
ax = axes[1, 0]
low_group['客数'].hist(ax=ax, bins=range(1, 12), alpha=0.6, label='低単価', density=True)
high_group['客数'].hist(ax=ax, bins=range(1, 12), alpha=0.6, label='高単価', density=True)
ax.set_xlabel('客数')
ax.set_ylabel('密度')
ax.set_title('客数分布（低単価 vs 高単価）')
ax.legend()

# 6-4: アルコール/トッピング比較
ax = axes[1, 1]
categories = ['アルコール注文率', 'トッピング注文率']
low_rates = [low_group['アルコールあり'].mean() * 100, (low_group['トッピング品数'] > 0).mean() * 100]
high_rates = [high_group['アルコールあり'].mean() * 100, (high_group['トッピング品数'] > 0).mean() * 100]
x = np.arange(len(categories))
ax.bar(x - width/2, low_rates, width, label='低単価', color='skyblue')
ax.bar(x + width/2, high_rates, width, label='高単価', color='salmon')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_ylabel('割合(%)')
ax.set_title('追加注文率（低単価 vs 高単価）')
ax.legend()

plt.suptitle('高単価/低単価グループの特徴比較', fontsize=14)
plt.tight_layout()
plt.savefig(f"{output_dir}/08_high_low_comparison.png", dpi=150, bbox_inches='tight')
plt.close()
print("\n保存: 08_high_low_comparison.png")

# Figure 7: 時間帯×曜日のヒートマップ
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 7-1: 客単価の平均
pivot_mean = orders.pivot_table(values='客単価', index='時間帯カテゴリ', columns='曜日', aggfunc='mean')
pivot_mean = pivot_mean.reindex(index=time_order, columns=weekday_order)
ax = axes[0]
sns.heatmap(pivot_mean, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
ax.set_title('時間帯×曜日別 客単価（平均）')
ax.set_xlabel('曜日')
ax.set_ylabel('時間帯')

# 7-2: 会計数
pivot_count = orders.pivot_table(values='客単価', index='時間帯カテゴリ', columns='曜日', aggfunc='count')
pivot_count = pivot_count.reindex(index=time_order, columns=weekday_order)
ax = axes[1]
sns.heatmap(pivot_count, annot=True, fmt='.0f', cmap='Blues', ax=ax)
ax.set_title('時間帯×曜日別 会計数')
ax.set_xlabel('曜日')
ax.set_ylabel('時間帯')

plt.tight_layout()
plt.savefig(f"{output_dir}/09_heatmap_weekday_hour.png", dpi=150, bbox_inches='tight')
plt.close()
print("保存: 09_heatmap_weekday_hour.png")

# ===== 分析結果の保存 =====
# 高単価/低単価グループのサマリー保存
comparison_df.to_csv(f"{output_dir}/10_comparison_summary.csv", index=False, encoding='utf-8-sig')
weekday_comp.to_csv(f"{output_dir}/11_weekday_comparison.csv", index=False, encoding='utf-8-sig')
time_comp.to_csv(f"{output_dir}/12_time_comparison.csv", index=False, encoding='utf-8-sig')

print("\n" + "=" * 60)
print("【分析完了】")
print("=" * 60)
print(f"\n出力先: {output_dir}")
print("\n生成ファイル一覧:")
print("  - 02_orders_with_price_per_customer.csv (伝票単位集約データ)")
print("  - 03_correlation_heatmap.png (相関行列)")
print("  - 04_scatter_plots.png (散布図)")
print("  - 05_boxplot_weekday_hour.png (曜日・時間帯別ボックスプロット)")
print("  - 06_boxplot_alcohol_weekend.png (アルコール・平日週末別)")
print("  - 07_price_distribution.png (客単価分布)")
print("  - 08_high_low_comparison.png (高単価/低単価比較)")
print("  - 09_heatmap_weekday_hour.png (時間帯×曜日ヒートマップ)")
print("  - 10_comparison_summary.csv (数値比較)")
print("  - 11_weekday_comparison.csv (曜日比較)")
print("  - 12_time_comparison.csv (時間帯比較)")
