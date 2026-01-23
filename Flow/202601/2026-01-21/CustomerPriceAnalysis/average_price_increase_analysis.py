"""
客単価平均値上昇の要因分析
平均値が中央値より大きく上昇している理由を深掘り
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("客単価平均値上昇の要因分析")
print("=" * 80)

# データ読み込み
df = pd.read_csv('transformed_pos_data_eatin.csv')
df['日付'] = pd.to_datetime(df['H.集計対象営業年月日'])

# 期間定義
period_a_start = pd.to_datetime('2025-05-01')
period_a_end = pd.to_datetime('2025-07-31')
period_b_start = pd.to_datetime('2025-10-01')
period_b_end = pd.to_datetime('2025-12-31')

df_period_a = df[(df['日付'] >= period_a_start) & (df['日付'] <= period_a_end)].copy()
df_period_b = df[(df['日付'] >= period_b_start) & (df['日付'] <= period_b_end)].copy()

# 伝票レベルのデータ作成
def create_receipt_data(df_period):
    """伝票レベルのデータを作成"""
    receipt_df = df_period.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first',
        'D.価格': 'sum',
        'D.商品': 'count'
    }).reset_index()

    # 客数が0の伝票を除外
    receipt_df = receipt_df[receipt_df['H.客数（合計）'] > 0].copy()

    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']
    receipt_df['一人当たり品数'] = receipt_df['D.商品'] / receipt_df['H.客数（合計）']

    # 異常値を除外（客単価が10000円以上は除外）
    receipt_df = receipt_df[receipt_df['客単価'] < 10000].copy()

    return receipt_df

receipt_a = create_receipt_data(df_period_a)
receipt_b = create_receipt_data(df_period_b)

print(f"\n期間A（5-7月）: {len(receipt_a):,}伝票")
print(f"期間B（10-12月）: {len(receipt_b):,}伝票")

# ================================================================================
# 1. 基本統計量の比較
# ================================================================================
print("\n" + "=" * 80)
print("1. 客単価の基本統計量比較")
print("=" * 80)

stats_comparison = pd.DataFrame({
    '期間A (5-7月)': receipt_a['客単価'].describe(),
    '期間B (10-12月)': receipt_b['客単価'].describe()
})
stats_comparison['差分'] = stats_comparison['期間B (10-12月)'] - stats_comparison['期間A (5-7月)']
stats_comparison['変化率(%)'] = (stats_comparison['期間B (10-12月)'] / stats_comparison['期間A (5-7月)'] - 1) * 100

print("\n【客単価の分布統計】")
print(stats_comparison.round(2).to_string())

# 平均値と中央値の乖離
print(f"\n【平均値と中央値の乖離】")
print(f"期間A:")
print(f"  平均値: {receipt_a['客単価'].mean():.0f}円")
print(f"  中央値: {receipt_a['客単価'].median():.0f}円")
print(f"  乖離: {receipt_a['客単価'].mean() - receipt_a['客単価'].median():.0f}円")

print(f"\n期間B:")
print(f"  平均値: {receipt_b['客単価'].mean():.0f}円")
print(f"  中央値: {receipt_b['客単価'].median():.0f}円")
print(f"  乖離: {receipt_b['客単価'].mean() - receipt_b['客単価'].median():.0f}円")

# ================================================================================
# 2. 客単価分布の変化（ヒストグラム）
# ================================================================================
print("\n" + "=" * 80)
print("2. 客単価分布の変化")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('客単価分布の変化分析', fontsize=16, fontweight='bold')

# ヒストグラム（全体）
ax1 = axes[0, 0]
ax1.hist(receipt_a['客単価'], bins=50, alpha=0.5, label='期間A (5-7月)', color='blue', edgecolor='black')
ax1.hist(receipt_b['客単価'], bins=50, alpha=0.5, label='期間B (10-12月)', color='red', edgecolor='black')
ax1.axvline(receipt_a['客単価'].mean(), color='blue', linestyle='--', linewidth=2, label=f'期間A平均: {receipt_a["客単価"].mean():.0f}円')
ax1.axvline(receipt_b['客単価'].mean(), color='red', linestyle='--', linewidth=2, label=f'期間B平均: {receipt_b["客単価"].mean():.0f}円')
ax1.axvline(receipt_a['客単価'].median(), color='blue', linestyle=':', linewidth=2, label=f'期間A中央値: {receipt_a["客単価"].median():.0f}円')
ax1.axvline(receipt_b['客単価'].median(), color='red', linestyle=':', linewidth=2, label=f'期間B中央値: {receipt_b["客単価"].median():.0f}円')
ax1.set_xlabel('客単価（円）', fontsize=11)
ax1.set_ylabel('伝票数', fontsize=11)
ax1.set_title('客単価分布（全体）', fontsize=12, fontweight='bold')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# ボックスプロット
ax2 = axes[0, 1]
box_data = [receipt_a['客単価'], receipt_b['客単価']]
bp = ax2.boxplot(box_data, labels=['期間A (5-7月)', '期間B (10-12月)'], patch_artist=True)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('lightcoral')
ax2.set_ylabel('客単価（円）', fontsize=11)
ax2.set_title('客単価の箱ひげ図', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 累積分布
ax3 = axes[1, 0]
ax3.hist(receipt_a['客単価'], bins=50, alpha=0.5, label='期間A (5-7月)', color='blue',
         cumulative=True, density=True, histtype='step', linewidth=2)
ax3.hist(receipt_b['客単価'], bins=50, alpha=0.5, label='期間B (10-12月)', color='red',
         cumulative=True, density=True, histtype='step', linewidth=2)
ax3.set_xlabel('客単価（円）', fontsize=11)
ax3.set_ylabel('累積確率', fontsize=11)
ax3.set_title('客単価の累積分布', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 高単価ゾーンの拡大表示
ax4 = axes[1, 1]
ax4.hist(receipt_a['客単価'], bins=np.arange(0, 6000, 200), alpha=0.5, label='期間A (5-7月)', color='blue')
ax4.hist(receipt_b['客単価'], bins=np.arange(0, 6000, 200), alpha=0.5, label='期間B (10-12月)', color='red')
ax4.set_xlabel('客単価（円）', fontsize=11)
ax4.set_ylabel('伝票数', fontsize=11)
ax4.set_title('客単価分布（詳細）', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_xlim(0, 6000)

plt.tight_layout()
plt.savefig('customer_price_distribution.png', dpi=300, bbox_inches='tight')
print("\n[OK] 客単価分布グラフを保存: customer_price_distribution.png")

# ================================================================================
# 3. 価格帯別の伝票数・構成比の変化
# ================================================================================
print("\n" + "=" * 80)
print("3. 価格帯別の伝票数分析")
print("=" * 80)

# 価格帯を細かく設定
price_bins = [0, 1000, 1500, 2000, 2500, 3000, 4000, 10000]
price_labels = ['～1000円', '1000-1500円', '1500-2000円', '2000-2500円', '2500-3000円', '3000-4000円', '4000円～']

receipt_a['価格帯'] = pd.cut(receipt_a['客単価'], bins=price_bins, labels=price_labels)
receipt_b['価格帯'] = pd.cut(receipt_b['客単価'], bins=price_bins, labels=price_labels)

price_segment_a = receipt_a['価格帯'].value_counts().sort_index()
price_segment_b = receipt_b['価格帯'].value_counts().sort_index()

price_segment_comparison = pd.DataFrame({
    '期間A_伝票数': price_segment_a,
    '期間B_伝票数': price_segment_b,
    '期間A_構成比(%)': (price_segment_a / len(receipt_a) * 100),
    '期間B_構成比(%)': (price_segment_b / len(receipt_b) * 100)
})
price_segment_comparison['構成比変化(pt)'] = price_segment_comparison['期間B_構成比(%)'] - price_segment_comparison['期間A_構成比(%)']
price_segment_comparison['伝票数変化率(%)'] = ((price_segment_comparison['期間B_伝票数'] / price_segment_comparison['期間A_伝票数']) - 1) * 100

print("\n【価格帯別の伝票数・構成比】")
print(price_segment_comparison.round(2).to_string())

# 高額伝票の分析
print("\n【高額伝票の増加】")
thresholds = [2000, 2500, 3000, 4000, 5000]
for threshold in thresholds:
    count_a = len(receipt_a[receipt_a['客単価'] >= threshold])
    count_b = len(receipt_b[receipt_b['客単価'] >= threshold])
    ratio_a = count_a / len(receipt_a) * 100
    ratio_b = count_b / len(receipt_b) * 100
    print(f"{threshold}円以上の伝票:")
    print(f"  期間A: {count_a:,}件 ({ratio_a:.1f}%)")
    print(f"  期間B: {count_b:,}件 ({ratio_b:.1f}%)")
    print(f"  変化: {count_b - count_a:+,}件 ({ratio_b - ratio_a:+.1f}pt)")

# ================================================================================
# 4. 伝票あたりの品数と客数の関係
# ================================================================================
print("\n" + "=" * 80)
print("4. 伝票あたりの品数・客数の分析")
print("=" * 80)

# 客数別の分析
guest_analysis_a = receipt_a.groupby('H.客数（合計）').agg({
    '客単価': ['mean', 'median', 'count'],
    'D.商品': 'mean'
}).round(2)
guest_analysis_a.columns = ['平均客単価', '中央値客単価', '伝票数', '平均品数']

guest_analysis_b = receipt_b.groupby('H.客数（合計）').agg({
    '客単価': ['mean', 'median', 'count'],
    'D.商品': 'mean'
}).round(2)
guest_analysis_b.columns = ['平均客単価', '中央値客単価', '伝票数', '平均品数']

print("\n【期間A: 客数別の平均客単価】")
print(guest_analysis_a.head(10).to_string())

print("\n【期間B: 客数別の平均客単価】")
print(guest_analysis_b.head(10).to_string())

# 一人当たり品数の分析
print("\n【一人当たり品数の統計】")
items_stats = pd.DataFrame({
    '期間A': receipt_a['一人当たり品数'].describe(),
    '期間B': receipt_b['一人当たり品数'].describe()
})
items_stats['変化'] = items_stats['期間B'] - items_stats['期間A']
print(items_stats.round(2).to_string())

# ================================================================================
# 5. 高単価伝票の特徴分析
# ================================================================================
print("\n" + "=" * 80)
print("5. 高単価伝票の特徴分析")
print("=" * 80)

# 2500円以上の高単価伝票を抽出
high_price_threshold = 2500
high_receipts_a = receipt_a[receipt_a['客単価'] >= high_price_threshold]['H.伝票番号'].tolist()
high_receipts_b = receipt_b[receipt_b['客単価'] >= high_price_threshold]['H.伝票番号'].tolist()

print(f"\n【{high_price_threshold}円以上の高単価伝票】")
print(f"期間A: {len(high_receipts_a)}件 ({len(high_receipts_a)/len(receipt_a)*100:.1f}%)")
print(f"期間B: {len(high_receipts_b)}件 ({len(high_receipts_b)/len(receipt_b)*100:.1f}%)")

# 高単価伝票で注文されているメニュー
high_menu_a = df_period_a[df_period_a['H.伝票番号'].isin(high_receipts_a)].groupby('D.商品名').agg({
    'D.価格': ['sum', 'count', 'mean']
}).reset_index()
high_menu_a.columns = ['商品名', '販売金額', '販売数', '平均単価']
high_menu_a = high_menu_a.sort_values('販売金額', ascending=False)

high_menu_b = df_period_b[df_period_b['H.伝票番号'].isin(high_receipts_b)].groupby('D.商品名').agg({
    'D.価格': ['sum', 'count', 'mean']
}).reset_index()
high_menu_b.columns = ['商品名', '販売金額', '販売数', '平均単価']
high_menu_b = high_menu_b.sort_values('販売金額', ascending=False)

print(f"\n【期間A: 高単価伝票のTOP10メニュー】")
print(high_menu_a.head(10).round(0).to_string(index=False))

print(f"\n【期間B: 高単価伝票のTOP10メニュー】")
print(high_menu_b.head(10).round(0).to_string(index=False))

# 高単価伝票でのカテゴリ構成
high_category_a = df_period_a[df_period_a['H.伝票番号'].isin(high_receipts_a)].groupby('D.商品カテゴリ2').agg({
    'D.価格': 'sum'
}).reset_index()
high_category_a['構成比'] = high_category_a['D.価格'] / high_category_a['D.価格'].sum() * 100
high_category_a = high_category_a.sort_values('構成比', ascending=False)

high_category_b = df_period_b[df_period_b['H.伝票番号'].isin(high_receipts_b)].groupby('D.商品カテゴリ2').agg({
    'D.価格': 'sum'
}).reset_index()
high_category_b['構成比'] = high_category_b['D.価格'] / high_category_b['D.価格'].sum() * 100
high_category_b = high_category_b.sort_values('構成比', ascending=False)

print(f"\n【高単価伝票のカテゴリ構成】")
category_comp = high_category_a[['D.商品カテゴリ2', '構成比']].merge(
    high_category_b[['D.商品カテゴリ2', '構成比']],
    on='D.商品カテゴリ2',
    how='outer',
    suffixes=('_A', '_B')
).fillna(0)
category_comp['変化'] = category_comp['構成比_B'] - category_comp['構成比_A']
category_comp = category_comp.sort_values('変化', ascending=False)
print(category_comp.round(2).to_string(index=False))

# ================================================================================
# 6. グラフ作成：価格帯別構成比の変化
# ================================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('価格帯別伝票構成比の変化', fontsize=14, fontweight='bold')

x = np.arange(len(price_labels))
width = 0.35

ax1 = axes[0]
ax1.bar(x - width/2, price_segment_comparison['期間A_構成比(%)'], width, label='期間A (5-7月)', color='steelblue', alpha=0.7)
ax1.bar(x + width/2, price_segment_comparison['期間B_構成比(%)'], width, label='期間B (10-12月)', color='coral', alpha=0.7)
ax1.set_xlabel('価格帯', fontsize=11)
ax1.set_ylabel('構成比（%）', fontsize=11)
ax1.set_title('価格帯別構成比', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(price_labels, rotation=45, ha='right')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

ax2 = axes[1]
colors = ['red' if x > 0 else 'blue' for x in price_segment_comparison['構成比変化(pt)']]
ax2.barh(price_labels, price_segment_comparison['構成比変化(pt)'], color=colors, alpha=0.7)
ax2.set_xlabel('構成比変化（ポイント）', fontsize=11)
ax2.set_title('価格帯別構成比の変化', fontsize=12)
ax2.axvline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('price_segment_change.png', dpi=300, bbox_inches='tight')
print("\n[OK] 価格帯別変化グラフを保存: price_segment_change.png")

# ================================================================================
# 7. まとめ
# ================================================================================
print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
print("\n生成されたファイル:")
print("  1. customer_price_distribution.png - 客単価分布分析")
print("  2. price_segment_change.png - 価格帯別変化")
