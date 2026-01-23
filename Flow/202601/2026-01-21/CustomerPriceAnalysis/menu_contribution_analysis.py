"""
THE BIFTEKI赤坂見附店 メニュー別貢献度分析

目的:
- どのメニューが売上上昇に貢献したのか？
- 新商品の影響は？
- 既存商品の中で伸びたもの・減ったものは？
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("第4章: メニュー別貢献度分析")
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

# ================================================================================
# 1. メニュー別売上分析
# ================================================================================
print("\n【メニュー別売上分析】")

def analyze_menu_sales(df_period):
    """メニュー別の売上を分析"""
    menu_df = df_period.groupby('D.商品名').agg({
        'D.価格': ['sum', 'count', 'mean']
    }).reset_index()
    menu_df.columns = ['商品名', '販売金額', '販売数', '平均単価']
    menu_df['販売金額構成比'] = menu_df['販売金額'] / menu_df['販売金額'].sum() * 100
    menu_df = menu_df.sort_values('販売金額', ascending=False).reset_index(drop=True)
    return menu_df

menu_a = analyze_menu_sales(df_period_a)
menu_b = analyze_menu_sales(df_period_b)

print(f"\n期間A（5-7月）の総売上: {menu_a['販売金額'].sum():,.0f}円")
print(f"期間B（10-12月）の総売上: {menu_b['販売金額'].sum():,.0f}円")
print(f"売上増加額: {menu_b['販売金額'].sum() - menu_a['販売金額'].sum():,.0f}円 ({(menu_b['販売金額'].sum() / menu_a['販売金額'].sum() - 1) * 100:+.1f}%)")

# ================================================================================
# 2. メニュー別の貢献度分析
# ================================================================================
print("\n【メニュー別貢献度分析】")

# 両期間のデータをマージ
menu_comparison = menu_a[['商品名', '販売金額', '販売数', '平均単価']].merge(
    menu_b[['商品名', '販売金額', '販売数', '平均単価']],
    on='商品名',
    how='outer',
    suffixes=('_A', '_B')
).fillna(0)

menu_comparison['販売金額_差分'] = menu_comparison['販売金額_B'] - menu_comparison['販売金額_A']
menu_comparison['販売数_差分'] = menu_comparison['販売数_B'] - menu_comparison['販売数_A']

# 売上増加への貢献度
total_increase = menu_b['販売金額'].sum() - menu_a['販売金額'].sum()
menu_comparison['貢献度'] = menu_comparison['販売金額_差分'] / total_increase * 100

# 貢献度でソート
menu_comparison = menu_comparison.sort_values('販売金額_差分', ascending=False)

print(f"\n【売上増加に最も貢献したメニューTOP20】")
top_contributors = menu_comparison.head(20)
print(top_contributors[['商品名', '販売金額_A', '販売金額_B', '販売金額_差分', '貢献度']].round(1).to_string(index=False))

print(f"\n【売上減少したメニューTOP10】")
bottom_contributors = menu_comparison[menu_comparison['販売金額_差分'] < 0].head(10)
print(bottom_contributors[['商品名', '販売金額_A', '販売金額_B', '販売金額_差分']].round(1).to_string(index=False))

# 貢献度の累積分析
print(f"\n【TOP10メニューの累積貢献度】")
top10_contribution = top_contributors.head(10)['貢献度'].sum()
print(f"TOP10メニューで売上増加の {top10_contribution:.1f}% を説明")

top20_contribution = top_contributors.head(20)['貢献度'].sum()
print(f"TOP20メニューで売上増加の {top20_contribution:.1f}% を説明")

# ================================================================================
# 3. 新商品 vs 既存商品
# ================================================================================
print("\n【新商品 vs 既存商品】")

# 新商品の判定（期間Aで販売がなく、期間Bで販売があるもの）
new_items = menu_comparison[menu_comparison['販売金額_A'] == 0]
existing_items = menu_comparison[menu_comparison['販売金額_A'] > 0]

print(f"\n新商品数: {len(new_items)}品")
print(f"新商品の売上合計（期間B）: {new_items['販売金額_B'].sum():,.0f}円")
print(f"新商品の売上構成比（期間B）: {new_items['販売金額_B'].sum() / menu_b['販売金額'].sum() * 100:.1f}%")

if len(new_items) > 0:
    print(f"\n【主要な新商品TOP10】")
    new_items_top = new_items.sort_values('販売金額_B', ascending=False).head(10)
    print(new_items_top[['商品名', '販売金額_B', '販売数_B', '平均単価_B']].round(1).to_string(index=False))

print(f"\n既存商品の売上変化: {existing_items['販売金額_差分'].sum():,.0f}円")
print(f"既存商品の売上変化率: {(existing_items['販売金額_B'].sum() / existing_items['販売金額_A'].sum() - 1) * 100:+.1f}%")

# ================================================================================
# 4. カテゴリ別の貢献度
# ================================================================================
print("\n【カテゴリ別貢献度】")

def analyze_category_contribution(df_period_a, df_period_b):
    """カテゴリ別の貢献度を分析"""
    cat_a = df_period_a.groupby('D.商品カテゴリ2')['D.価格'].sum()
    cat_b = df_period_b.groupby('D.商品カテゴリ2')['D.価格'].sum()

    cat_comp = pd.DataFrame({
        '販売金額_A': cat_a,
        '販売金額_B': cat_b
    }).fillna(0)

    cat_comp['差分'] = cat_comp['販売金額_B'] - cat_comp['販売金額_A']
    cat_comp['貢献度'] = cat_comp['差分'] / total_increase * 100
    cat_comp = cat_comp.sort_values('差分', ascending=False)

    return cat_comp

cat_contribution = analyze_category_contribution(df_period_a, df_period_b)
print(cat_contribution.round(1).to_string())

# ================================================================================
# 5. 価格帯別の貢献度
# ================================================================================
print("\n【価格帯別貢献度】")

def analyze_price_segment_contribution(df_period_a, df_period_b):
    """価格帯別の貢献度を分析"""
    df_period_a_copy = df_period_a.copy()
    df_period_b_copy = df_period_b.copy()

    # 価格帯を設定
    bins = [0, 500, 1000, 1500, 2000, 2500, 10000]
    labels = ['～500円', '500-1000円', '1000-1500円', '1500-2000円', '2000-2500円', '2500円～']

    df_period_a_copy['価格帯'] = pd.cut(df_period_a_copy['D.価格'], bins=bins, labels=labels)
    df_period_b_copy['価格帯'] = pd.cut(df_period_b_copy['D.価格'], bins=bins, labels=labels)

    price_a = df_period_a_copy.groupby('価格帯')['D.価格'].sum()
    price_b = df_period_b_copy.groupby('価格帯')['D.価格'].sum()

    price_comp = pd.DataFrame({
        '販売金額_A': price_a,
        '販売金額_B': price_b
    }).fillna(0)

    price_comp['差分'] = price_comp['販売金額_B'] - price_comp['販売金額_A']
    price_comp['貢献度'] = price_comp['差分'] / total_increase * 100

    return price_comp

price_contribution = analyze_price_segment_contribution(df_period_a, df_period_b)
print(price_contribution.round(1).to_string())

# ================================================================================
# 6. グラフ作成
# ================================================================================

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# TOP20メニューの貢献度
ax1 = fig.add_subplot(gs[0, :])
top20 = menu_comparison.head(20)
colors = ['green' if x > 0 else 'red' for x in top20['販売金額_差分']]
ax1.barh(range(len(top20)), top20['販売金額_差分'], color=colors, alpha=0.7)
ax1.set_yticks(range(len(top20)))
ax1.set_yticklabels(top20['商品名'], fontsize=9)
ax1.set_xlabel('売上増減額（円）', fontsize=11)
ax1.set_title('メニュー別売上貢献度 TOP20', fontsize=13, fontweight='bold')
ax1.axvline(0, color='black', linewidth=0.8)
ax1.grid(True, alpha=0.3, axis='x')
ax1.invert_yaxis()

# カテゴリ別貢献度
ax2 = fig.add_subplot(gs[1, 0])
cat_sorted = cat_contribution.sort_values('差分')
colors2 = ['green' if x > 0 else 'red' for x in cat_sorted['差分']]
ax2.barh(cat_sorted.index, cat_sorted['差分'], color=colors2, alpha=0.7)
ax2.set_xlabel('売上増減額（円）', fontsize=11)
ax2.set_title('カテゴリ別貢献度', fontsize=12, fontweight='bold')
ax2.axvline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='x')

# 価格帯別貢献度
ax3 = fig.add_subplot(gs[1, 1])
colors3 = ['green' if x > 0 else 'red' for x in price_contribution['差分']]
ax3.bar(range(len(price_contribution)), price_contribution['差分'], color=colors3, alpha=0.7)
ax3.set_xticks(range(len(price_contribution)))
ax3.set_xticklabels(price_contribution.index, rotation=45, ha='right')
ax3.set_ylabel('売上増減額（円）', fontsize=11)
ax3.set_title('価格帯別貢献度', fontsize=12, fontweight='bold')
ax3.axhline(0, color='black', linewidth=0.8)
ax3.grid(True, alpha=0.3, axis='y')

# 販売数変化TOP10
ax4 = fig.add_subplot(gs[2, 0])
top_volume_change = menu_comparison.sort_values('販売数_差分', ascending=False).head(10)
ax4.barh(range(len(top_volume_change)), top_volume_change['販売数_差分'], color='steelblue', alpha=0.7)
ax4.set_yticks(range(len(top_volume_change)))
ax4.set_yticklabels(top_volume_change['商品名'], fontsize=9)
ax4.set_xlabel('販売数増加', fontsize=11)
ax4.set_title('販売数が最も増加したメニューTOP10', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')
ax4.invert_yaxis()

# 貢献度円グラフ（増加分のみ）
ax5 = fig.add_subplot(gs[2, 1])
# マイナス貢献度は除外して、プラス貢献度のみで円グラフを作成
contribution_summary = pd.DataFrame({
    'カテゴリ': ['TOP10', 'TOP11-20', 'その他増加'],
    '貢献額': [
        top_contributors.head(10)['販売金額_差分'].sum(),
        top_contributors.iloc[10:20]['販売金額_差分'].sum(),
        menu_comparison[(menu_comparison['販売金額_差分'] > 0) & (~menu_comparison.index.isin(top_contributors.head(20).index))]['販売金額_差分'].sum()
    ]
})
colors_pie = ['#2ecc71', '#3498db', '#95a5a6']
ax5.pie(contribution_summary['貢献額'], labels=contribution_summary['カテゴリ'],
        autopct='%1.1f%%', colors=colors_pie, startangle=90)
ax5.set_title('売上増加への貢献度内訳\n(増加分のみ)', fontsize=12, fontweight='bold')

plt.savefig('04_menu_contribution.png', dpi=300, bbox_inches='tight')
print("\n[OK] メニュー貢献度グラフを保存: 04_menu_contribution.png")

# ================================================================================
# 7. まとめ
# ================================================================================
print("\n" + "=" * 80)
print("まとめ: どのメニューが売上上昇に貢献したか")
print("=" * 80)

print(f"\n【主要な発見】")
print(f"1. TOP3貢献メニュー:")
for i, row in top_contributors.head(3).iterrows():
    print(f"   {row['商品名']}: {row['販売金額_差分']:,.0f}円増 (貢献度{row['貢献度']:.1f}%)")

print(f"\n2. カテゴリ別では「{cat_contribution['差分'].idxmax()}」が最大の貢献")
print(f"   → {cat_contribution.loc[cat_contribution['差分'].idxmax(), '差分']:,.0f}円増")

print(f"\n3. 価格帯別では「{price_contribution['差分'].idxmax()}」が最大の貢献")
print(f"   → {price_contribution.loc[price_contribution['差分'].idxmax(), '差分']:,.0f}円増")

if len(new_items) > 0 and new_items['販売金額_B'].sum() / total_increase > 0.1:
    print(f"\n4. 新商品が売上増加の{new_items['販売金額_B'].sum() / total_increase * 100:.1f}%を占める")
    print(f"   → 新商品戦略が成功")

print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
