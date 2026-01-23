"""
THE BIFTEKI赤坂見附店 客単価上昇要因分析
リニューアル前後（2025年5-7月 vs 10-12月）の比較分析
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

# データ読み込み
print("=" * 80)
print("THE BIFTEKI赤坂見附店 客単価上昇要因分析")
print("=" * 80)

df = pd.read_csv('transformed_pos_data_eatin.csv')
df['日付'] = pd.to_datetime(df['H.集計対象営業年月日'])
df['年月'] = df['日付'].dt.to_period('M')

# 期間定義
period_a_start = pd.to_datetime('2025-05-01')
period_a_end = pd.to_datetime('2025-07-31')
period_b_start = pd.to_datetime('2025-10-01')
period_b_end = pd.to_datetime('2025-12-31')

df_period_a = df[(df['日付'] >= period_a_start) & (df['日付'] <= period_a_end)].copy()
df_period_b = df[(df['日付'] >= period_b_start) & (df['日付'] <= period_b_end)].copy()

print(f"\n期間A（リニューアル直後）: 2025年5月～7月")
print(f"  レコード数: {len(df_period_a):,}")
print(f"  伝票数: {df_period_a['H.伝票番号'].nunique():,}")

print(f"\n期間B（直近3か月）: 2025年10月～12月")
print(f"  レコード数: {len(df_period_b):,}")
print(f"  伝票数: {df_period_b['H.伝票番号'].nunique():,}")

# ================================================================================
# 1. 基礎指標の算出
# ================================================================================
print("\n" + "=" * 80)
print("1. 基礎指標比較")
print("=" * 80)

def calc_metrics(df_period):
    """期間の基礎指標を計算"""
    # 伝票レベルの集計
    receipt_df = df_period.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first',
        'D.価格': 'sum',
        'D.商品': 'count'
    }).reset_index()

    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']
    receipt_df['一人当たり品数'] = receipt_df['D.商品'] / receipt_df['H.客数（合計）']
    receipt_df['平均商品単価'] = receipt_df['D.価格'] / receipt_df['D.商品']

    return {
        '伝票数': len(receipt_df),
        '客単価_平均': receipt_df['客単価'].mean(),
        '客単価_中央値': receipt_df['客単価'].median(),
        '一人当たり品数': receipt_df['一人当たり品数'].mean(),
        '平均商品単価': receipt_df['平均商品単価'].mean(),
        '総売上': receipt_df['H.小計'].sum(),
        '総客数': receipt_df['H.客数（合計）'].sum()
    }

metrics_a = calc_metrics(df_period_a)
metrics_b = calc_metrics(df_period_b)

comparison_df = pd.DataFrame({
    '期間A (5-7月)': metrics_a,
    '期間B (10-12月)': metrics_b
})
comparison_df['変化率'] = ((comparison_df['期間B (10-12月)'] / comparison_df['期間A (5-7月)']) - 1) * 100
comparison_df['差分'] = comparison_df['期間B (10-12月)'] - comparison_df['期間A (5-7月)']

print("\n【基礎指標比較】")
print(comparison_df.round(2).to_string())

# 客単価の要因分解
avg_price_change = metrics_b['平均商品単価'] - metrics_a['平均商品単価']
items_per_person_change = metrics_b['一人当たり品数'] - metrics_a['一人当たり品数']

print("\n【客単価変化の要因分解】")
print(f"客単価変化: {metrics_b['客単価_平均'] - metrics_a['客単価_平均']:.0f}円")
print(f"  └ 平均商品単価の変化寄与: {avg_price_change * metrics_a['一人当たり品数']:.0f}円")
print(f"  └ 一人当たり品数の変化寄与: {items_per_person_change * metrics_a['平均商品単価']:.0f}円")

# ================================================================================
# 2. 月次推移の可視化
# ================================================================================
print("\n" + "=" * 80)
print("2. 月次推移分析")
print("=" * 80)

# 月次集計
monthly_df = df.groupby('年月').apply(lambda x: pd.Series({
    '伝票数': x['H.伝票番号'].nunique(),
    '総売上': x.groupby('H.伝票番号')['H.小計'].first().sum(),
    '総客数': x.groupby('H.伝票番号')['H.客数（合計）'].first().sum(),
    '総品数': len(x)
})).reset_index()

monthly_df['客単価'] = monthly_df['総売上'] / monthly_df['総客数']
monthly_df['一人当たり品数'] = monthly_df['総品数'] / monthly_df['総客数']
monthly_df['平均商品単価'] = monthly_df['総売上'] / monthly_df['総品数']
monthly_df['年月_str'] = monthly_df['年月'].astype(str)

# 2025年以降のみ表示
monthly_df_2025 = monthly_df[monthly_df['年月'] >= '2025-01'].copy()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('月次推移（2025年以降）', fontsize=16, fontweight='bold')

# 客単価推移
ax1 = axes[0, 0]
ax1.plot(monthly_df_2025['年月_str'], monthly_df_2025['客単価'], marker='o', linewidth=2, markersize=8)
ax1.axvspan('2025-05', '2025-07', alpha=0.2, color='blue', label='期間A (5-7月)')
ax1.axvspan('2025-10', '2025-12', alpha=0.2, color='red', label='期間B (10-12月)')
ax1.axvline(x='2025-03', color='green', linestyle='--', linewidth=2, label='リニューアル')
ax1.set_title('客単価推移', fontsize=12, fontweight='bold')
ax1.set_ylabel('客単価（円）', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.legend()
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# 平均商品単価推移
ax2 = axes[0, 1]
ax2.plot(monthly_df_2025['年月_str'], monthly_df_2025['平均商品単価'], marker='s', linewidth=2, markersize=8, color='orange')
ax2.axvspan('2025-05', '2025-07', alpha=0.2, color='blue')
ax2.axvspan('2025-10', '2025-12', alpha=0.2, color='red')
ax2.axvline(x='2025-03', color='green', linestyle='--', linewidth=2)
ax2.set_title('平均商品単価推移', fontsize=12, fontweight='bold')
ax2.set_ylabel('平均商品単価（円）', fontsize=11)
ax2.grid(True, alpha=0.3)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# 一人当たり品数推移
ax3 = axes[1, 0]
ax3.plot(monthly_df_2025['年月_str'], monthly_df_2025['一人当たり品数'], marker='^', linewidth=2, markersize=8, color='green')
ax3.axvspan('2025-05', '2025-07', alpha=0.2, color='blue')
ax3.axvspan('2025-10', '2025-12', alpha=0.2, color='red')
ax3.axvline(x='2025-03', color='green', linestyle='--', linewidth=2)
ax3.set_title('一人当たり品数推移', fontsize=12, fontweight='bold')
ax3.set_ylabel('品数', fontsize=11)
ax3.grid(True, alpha=0.3)
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

# 伝票数推移
ax4 = axes[1, 1]
ax4.bar(monthly_df_2025['年月_str'], monthly_df_2025['伝票数'], color='steelblue', alpha=0.7)
ax4.axvline(x='2025-03', color='green', linestyle='--', linewidth=2, label='リニューアル')
ax4.set_title('月次伝票数', fontsize=12, fontweight='bold')
ax4.set_ylabel('伝票数', fontsize=11)
ax4.grid(True, alpha=0.3, axis='y')
ax4.legend()
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
print("\n[OK] 月次推移グラフを保存しました: monthly_trends.png")

# ================================================================================
# 3. メニュー構成の変化分析
# ================================================================================
print("\n" + "=" * 80)
print("3. メニュー構成の変化分析")
print("=" * 80)

def analyze_menu_ranking(df_period, period_name):
    """メニュー別の販売数・販売金額をランキング"""
    menu_df = df_period.groupby('D.商品名').agg({
        'D.価格': ['sum', 'mean', 'count']
    }).reset_index()
    menu_df.columns = ['商品名', '販売金額', '平均単価', '販売数']
    menu_df['販売金額構成比'] = menu_df['販売金額'] / menu_df['販売金額'].sum() * 100
    menu_df = menu_df.sort_values('販売金額', ascending=False).reset_index(drop=True)
    return menu_df

menu_ranking_a = analyze_menu_ranking(df_period_a, '期間A')
menu_ranking_b = analyze_menu_ranking(df_period_b, '期間B')

print("\n【期間A（5-7月）TOP20メニュー】")
print(menu_ranking_a.head(20)[['商品名', '販売数', '販売金額', '平均単価', '販売金額構成比']].round(1).to_string(index=False))

print("\n【期間B（10-12月）TOP20メニュー】")
print(menu_ranking_b.head(20)[['商品名', '販売数', '販売金額', '平均単価', '販売金額構成比']].round(1).to_string(index=False))

# メニュー別変化率の算出
menu_comparison = menu_ranking_a[['商品名', '販売数', '販売金額']].merge(
    menu_ranking_b[['商品名', '販売数', '販売金額']],
    on='商品名',
    how='outer',
    suffixes=('_A', '_B')
).fillna(0)

menu_comparison['販売数_変化率'] = ((menu_comparison['販売数_B'] / menu_comparison['販売数_A'].replace(0, np.nan)) - 1) * 100
menu_comparison['販売金額_変化率'] = ((menu_comparison['販売金額_B'] / menu_comparison['販売金額_A'].replace(0, np.nan)) - 1) * 100
menu_comparison = menu_comparison.sort_values('販売金額_変化率', ascending=False)

print("\n【販売金額が大きく増加したメニューTOP10】")
top_increase = menu_comparison[(menu_comparison['販売金額_A'] > 0) & (menu_comparison['販売金額_B'] > 0)].head(10)
print(top_increase[['商品名', '販売金額_A', '販売金額_B', '販売金額_変化率']].round(1).to_string(index=False))

print("\n【販売金額が大きく減少したメニューTOP10】")
top_decrease = menu_comparison[(menu_comparison['販売金額_A'] > 0) & (menu_comparison['販売金額_B'] > 0)].tail(10)
print(top_decrease[['商品名', '販売金額_A', '販売金額_B', '販売金額_変化率']].round(1).to_string(index=False))

# 高単価メニューの販売比率
def calc_high_price_ratio(df_period):
    """1500円以上のメニューの販売比率"""
    total_items = len(df_period)
    high_price_items = len(df_period[df_period['D.価格'] >= 1500])
    return high_price_items / total_items * 100

high_price_ratio_a = calc_high_price_ratio(df_period_a)
high_price_ratio_b = calc_high_price_ratio(df_period_b)

print(f"\n【高単価メニュー（1500円以上）の販売比率】")
print(f"期間A: {high_price_ratio_a:.1f}%")
print(f"期間B: {high_price_ratio_b:.1f}%")
print(f"変化: {high_price_ratio_b - high_price_ratio_a:+.1f}ポイント")

# ================================================================================
# 4. カテゴリ別売上構成の変化
# ================================================================================
print("\n" + "=" * 80)
print("4. カテゴリ別売上構成の変化")
print("=" * 80)

def analyze_category(df_period, period_name):
    """カテゴリ別の売上構成"""
    category_df = df_period.groupby('D.商品カテゴリ2').agg({
        'D.価格': ['sum', 'count']
    }).reset_index()
    category_df.columns = ['カテゴリ', '販売金額', '販売数']
    category_df['販売金額構成比'] = category_df['販売金額'] / category_df['販売金額'].sum() * 100
    category_df = category_df.sort_values('販売金額', ascending=False)
    return category_df

category_a = analyze_category(df_period_a, '期間A')
category_b = analyze_category(df_period_b, '期間B')

print("\n【カテゴリ別売上構成】")
category_comparison = category_a[['カテゴリ', '販売金額構成比']].merge(
    category_b[['カテゴリ', '販売金額構成比']],
    on='カテゴリ',
    suffixes=('_A', '_B')
)
category_comparison['構成比変化'] = category_comparison['販売金額構成比_B'] - category_comparison['販売金額構成比_A']
category_comparison = category_comparison.sort_values('構成比変化', ascending=False)
print(category_comparison.round(2).to_string(index=False))

# アルコール・トッピング付加率
def calc_attachment_rate(df_period, category):
    """特定カテゴリの伝票あたりの付加率"""
    total_receipts = df_period['H.伝票番号'].nunique()
    receipts_with_category = df_period[df_period['D.商品カテゴリ2'] == category]['H.伝票番号'].nunique()
    return receipts_with_category / total_receipts * 100

print("\n【伝票あたりの付加率】")
for category in ['アルコール', 'トッピング', 'ソフトドリンク']:
    rate_a = calc_attachment_rate(df_period_a, category)
    rate_b = calc_attachment_rate(df_period_b, category)
    print(f"{category}:")
    print(f"  期間A: {rate_a:.1f}%")
    print(f"  期間B: {rate_b:.1f}%")
    print(f"  変化: {rate_b - rate_a:+.1f}ポイント")

# カテゴリ構成比の可視化
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('カテゴリ別売上構成比の比較', fontsize=14, fontweight='bold')

category_a_sorted = category_a.sort_values('販売金額構成比', ascending=True)
category_b_sorted = category_b.sort_values('販売金額構成比', ascending=True)

axes[0].barh(category_a_sorted['カテゴリ'], category_a_sorted['販売金額構成比'], color='steelblue')
axes[0].set_title('期間A（5-7月）', fontsize=12)
axes[0].set_xlabel('構成比（%）', fontsize=11)
axes[0].grid(True, alpha=0.3, axis='x')

axes[1].barh(category_b_sorted['カテゴリ'], category_b_sorted['販売金額構成比'], color='coral')
axes[1].set_title('期間B（10-12月）', fontsize=12)
axes[1].set_xlabel('構成比（%）', fontsize=11)
axes[1].grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('category_composition.png', dpi=300, bbox_inches='tight')
print("\n[OK] カテゴリ構成比グラフを保存しました: category_composition.png")

# ================================================================================
# 5. 注文パターンの変化
# ================================================================================
print("\n" + "=" * 80)
print("5. 注文パターンの変化")
print("=" * 80)

# 定食セット比率
def calc_teishoku_rate(df_period):
    """定食セットの注文比率"""
    total = len(df_period)
    teishoku = len(df_period[df_period['D.サブメニュー'].str.contains('定食セット', na=False)])
    return teishoku / total * 100

teishoku_rate_a = calc_teishoku_rate(df_period_a)
teishoku_rate_b = calc_teishoku_rate(df_period_b)

print(f"\n【定食セット注文比率】")
print(f"期間A: {teishoku_rate_a:.1f}%")
print(f"期間B: {teishoku_rate_b:.1f}%")
print(f"変化: {teishoku_rate_b - teishoku_rate_a:+.1f}ポイント")

# 大盛選択率
def calc_omori_rate(df_period):
    """大盛の選択率（定食セット注文の中で）"""
    teishoku_df = df_period[df_period['D.サブメニュー'].str.contains('定食セット', na=False)]
    if len(teishoku_df) == 0:
        return 0
    omori = len(teishoku_df[teishoku_df['D.サブメニュー'].str.contains('大盛', na=False)])
    return omori / len(teishoku_df) * 100

omori_rate_a = calc_omori_rate(df_period_a)
omori_rate_b = calc_omori_rate(df_period_b)

print(f"\n【大盛選択率（定食セット注文の中で）】")
print(f"期間A: {omori_rate_a:.1f}%")
print(f"期間B: {omori_rate_b:.1f}%")
print(f"変化: {omori_rate_b - omori_rate_a:+.1f}ポイント")

# 一伝票あたりの商品数分布
def calc_items_distribution(df_period):
    """伝票あたりの商品数分布"""
    receipt_items = df_period.groupby('H.伝票番号')['D.商品'].count()
    return receipt_items.value_counts(normalize=True).sort_index() * 100

items_dist_a = calc_items_distribution(df_period_a)
items_dist_b = calc_items_distribution(df_period_b)

print(f"\n【一伝票あたりの商品数分布（TOP10）】")
dist_comparison = pd.DataFrame({
    '期間A（%）': items_dist_a.head(10),
    '期間B（%）': items_dist_b.head(10)
}).fillna(0)
print(dist_comparison.round(1).to_string())

# ================================================================================
# 6. 価格帯別メニュー販売構成
# ================================================================================
print("\n" + "=" * 80)
print("6. 価格帯別メニュー販売構成")
print("=" * 80)

def analyze_price_segment(df_period):
    """価格帯別の販売構成"""
    df_period['価格帯'] = pd.cut(df_period['D.価格'],
                                  bins=[0, 1000, 1500, 2000, 10000],
                                  labels=['～1000円', '1000-1500円', '1500-2000円', '2000円～'])

    segment_df = df_period.groupby('価格帯').agg({
        'D.価格': ['count', 'sum']
    }).reset_index()
    segment_df.columns = ['価格帯', '販売数', '販売金額']
    segment_df['販売数構成比'] = segment_df['販売数'] / segment_df['販売数'].sum() * 100
    segment_df['販売金額構成比'] = segment_df['販売金額'] / segment_df['販売金額'].sum() * 100
    return segment_df

segment_a = analyze_price_segment(df_period_a.copy())
segment_b = analyze_price_segment(df_period_b.copy())

print("\n【価格帯別販売構成】")
print("\n期間A（5-7月）:")
print(segment_a.round(1).to_string(index=False))
print("\n期間B（10-12月）:")
print(segment_b.round(1).to_string(index=False))

# 価格帯別構成比の可視化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('価格帯別販売構成の比較', fontsize=14, fontweight='bold')

# 販売数構成比
axes[0, 0].bar(segment_a['価格帯'].astype(str), segment_a['販売数構成比'], color='steelblue', alpha=0.7)
axes[0, 0].set_title('期間A（5-7月） - 販売数構成比', fontsize=11)
axes[0, 0].set_ylabel('構成比（%）', fontsize=10)
axes[0, 0].grid(True, alpha=0.3, axis='y')
plt.setp(axes[0, 0].xaxis.get_majorticklabels(), rotation=15)

axes[0, 1].bar(segment_b['価格帯'].astype(str), segment_b['販売数構成比'], color='coral', alpha=0.7)
axes[0, 1].set_title('期間B（10-12月） - 販売数構成比', fontsize=11)
axes[0, 1].set_ylabel('構成比（%）', fontsize=10)
axes[0, 1].grid(True, alpha=0.3, axis='y')
plt.setp(axes[0, 1].xaxis.get_majorticklabels(), rotation=15)

# 販売金額構成比
axes[1, 0].bar(segment_a['価格帯'].astype(str), segment_a['販売金額構成比'], color='steelblue', alpha=0.7)
axes[1, 0].set_title('期間A（5-7月） - 販売金額構成比', fontsize=11)
axes[1, 0].set_ylabel('構成比（%）', fontsize=10)
axes[1, 0].grid(True, alpha=0.3, axis='y')
plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=15)

axes[1, 1].bar(segment_b['価格帯'].astype(str), segment_b['販売金額構成比'], color='coral', alpha=0.7)
axes[1, 1].set_title('期間B（10-12月） - 販売金額構成比', fontsize=11)
axes[1, 1].set_ylabel('構成比（%）', fontsize=10)
axes[1, 1].grid(True, alpha=0.3, axis='y')
plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=15)

plt.tight_layout()
plt.savefig('price_segment_composition.png', dpi=300, bbox_inches='tight')
print("\n[OK] 価格帯別構成グラフを保存しました: price_segment_composition.png")

# ================================================================================
# 7. 総合サマリー
# ================================================================================
print("\n" + "=" * 80)
print("7. 総合サマリー：客単価上昇の要因")
print("=" * 80)

customer_price_change = metrics_b['客単価_平均'] - metrics_a['客単価_平均']
customer_price_change_rate = (metrics_b['客単価_平均'] / metrics_a['客単価_平均'] - 1) * 100

print(f"""
【客単価変化】
  期間A（5-7月）: {metrics_a['客単価_平均']:.0f}円
  期間B（10-12月）: {metrics_b['客単価_平均']:.0f}円
  変化: {customer_price_change:+.0f}円（{customer_price_change_rate:+.1f}%）

【主な要因】
  1. 平均商品単価の上昇: {metrics_b['平均商品単価'] - metrics_a['平均商品単価']:+.0f}円（{(metrics_b['平均商品単価']/metrics_a['平均商品単価']-1)*100:+.1f}%）
     → 寄与度: {avg_price_change * metrics_a['一人当たり品数']:.0f}円

  2. 一人当たり品数の変化: {metrics_b['一人当たり品数'] - metrics_a['一人当たり品数']:+.2f}品（{(metrics_b['一人当たり品数']/metrics_a['一人当たり品数']-1)*100:+.1f}%）
     → 寄与度: {items_per_person_change * metrics_a['平均商品単価']:.0f}円

  3. カテゴリ構成の変化:
     - アルコール付加率: {calc_attachment_rate(df_period_b, 'アルコール') - calc_attachment_rate(df_period_a, 'アルコール'):+.1f}ポイント
     - トッピング付加率: {calc_attachment_rate(df_period_b, 'トッピング') - calc_attachment_rate(df_period_a, 'トッピング'):+.1f}ポイント

  4. 高単価メニュー比率: {high_price_ratio_b - high_price_ratio_a:+.1f}ポイント

  5. 大盛選択率: {omori_rate_b - omori_rate_a:+.1f}ポイント
""")

print("\n" + "=" * 80)
print("分析完了！")
print("=" * 80)
print("\n生成されたファイル:")
print("  1. monthly_trends.png - 月次推移グラフ")
print("  2. category_composition.png - カテゴリ別構成比")
print("  3. price_segment_composition.png - 価格帯別構成")
