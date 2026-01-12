import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
import json
import sys

# 標準出力のエンコーディングを設定
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings('ignore')

# 日本語フォントの設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Hiragino Sans', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

# 中間メモを保存
memo_content = []

def save_memo(title, content):
    """分析中のメモを保存"""
    memo_content.append(f"\n## {title}\n{content}\n")
    print(f"\n[メモ] {title}")
    print(content)

# ==========================================
# データ読み込み
# ==========================================
print("=" * 80)
print("飲食店データ分析スクリプト - 週報作成基礎資料（2025-W42）")
print("=" * 80)
save_memo("データ読み込み", "売上データと口コミデータを読み込んでいます...")

sales_df = pd.read_csv(r'Stock\RestaurantAILab\週報\1_input\rawdata.csv')
reviews_df = pd.read_csv(r'Stock\RestaurantAILab\週報\1_input\reviews.csv', encoding='utf-8-sig')

# 日付型への変換
sales_df['entry_at'] = pd.to_datetime(sales_df['entry_at'])
sales_df['exit_at'] = pd.to_datetime(sales_df['exit_at'])
if 'ordered_at' in sales_df.columns:
    sales_df['ordered_at'] = pd.to_datetime(sales_df['ordered_at'], errors='coerce')

# 日付、週、月の情報を追加
sales_df['date'] = sales_df['entry_at'].dt.date
sales_df['year'] = sales_df['entry_at'].dt.year
sales_df['month'] = sales_df['entry_at'].dt.month
sales_df['week'] = sales_df['entry_at'].dt.isocalendar().week
sales_df['year_week'] = sales_df['entry_at'].dt.strftime('%Y-W%U')
sales_df['hour'] = sales_df['entry_at'].dt.hour
sales_df['weekday'] = sales_df['day_of_week']

# 口コミデータの日付処理
reviews_df['投稿日'] = pd.to_datetime(reviews_df['投稿日'], format='%y/%m/%d', errors='coerce')

# ★★★ 対象週を指定 ★★★
target_week = '2025-W42'
target_date_end = pd.to_datetime('2025-10-24').date()
target_date_start = target_date_end - timedelta(days=6)

# 対象週のデータをフィルタリング
sales_df_filtered = sales_df[(sales_df['date'] >= target_date_start) &
                               (sales_df['date'] <= target_date_end)]

memo_text = f"""
- 売上データ期間: {sales_df['date'].min()} ～ {sales_df['date'].max()}
- 売上データ件数: {len(sales_df):,} レコード
- 口コミデータ件数: {len(reviews_df):,} 件
- **対象週: {target_week} ({target_date_start} ～ {target_date_end})**
- 対象週のレコード数: {len(sales_df_filtered):,} レコード
- 店舗: {sales_df['store_name'].iloc[0]}
"""
save_memo("データ概要", memo_text)

# 出力ディレクトリの作成
output_dir = r'Stock\RestaurantAILab\週報\2_output_week42'
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 1. 売上分析
# ==========================================
save_memo("売上分析", """
【目的】対象週の売上傾向を把握し、前週・前月・前年と比較して業績の変化を理解する
【仮説】
- 曜日や時間帯によって売上パターンがあり、ピークタイムを特定できる
- 客単価と客数の変動が売上に大きく影響している
- 前週・前月・前年比較により、季節要因や成長トレンドを把握できる
""")

# 会計単位でのデータ集計（重複除去）
account_df = sales_df.groupby(['account_id', 'date', 'year_week', 'weekday', 'hour']).agg({
    'account_total': 'first',
    'customer_count': 'first'
}).reset_index()

save_memo("データ処理", f"会計単位で集計: {len(account_df):,} 件の会計データ")

# 週次売上集計
weekly_sales = account_df.groupby('year_week').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={
    'account_total': '売上',
    'customer_count': '客数',
    'account_id': '組数'
})
weekly_sales['客単価'] = weekly_sales['売上'] / weekly_sales['客数']
weekly_sales = weekly_sales.sort_index()

# 対象週のデータ取得
latest_week = target_week
latest_week_data = weekly_sales.loc[latest_week] if latest_week in weekly_sales.index else None

if latest_week_data is None:
    print(f"\n警告: {target_week} のデータが見つかりません")
    print("利用可能な週:", weekly_sales.index.tolist())
    sys.exit(1)

# 前週・前月・前年のデータ取得
week_list = sorted(weekly_sales.index.tolist())
latest_week_idx = week_list.index(latest_week) if latest_week in week_list else -1

prev_week = week_list[latest_week_idx - 1] if latest_week_idx > 0 else None
prev_week_data = weekly_sales.loc[prev_week] if prev_week else None

prev_month_week = week_list[latest_week_idx - 4] if latest_week_idx >= 4 else None
prev_month_data = weekly_sales.loc[prev_month_week] if prev_month_week else None

# 前年同週の計算
try:
    latest_year = int(latest_week.split('-W')[0])
    latest_week_num = int(latest_week.split('-W')[1])
    prev_year_week = f"{latest_year - 1}-W{latest_week_num:02d}"
    prev_year_data = weekly_sales.loc[prev_year_week] if prev_year_week in weekly_sales.index else None
except:
    prev_year_data = None

# 比較結果のメモ
comparison_memo = f"""
### 対象週 ({latest_week})
- 売上: ¥{latest_week_data['売上']:,.0f}
- 客数: {latest_week_data['客数']:.0f}人
- 組数: {latest_week_data['組数']:.0f}組
- 客単価: ¥{latest_week_data['客単価']:,.0f}
"""

if prev_week_data is not None:
    sales_change = ((latest_week_data['売上'] - prev_week_data['売上']) / prev_week_data['売上'] * 100)
    customer_change = ((latest_week_data['客数'] - prev_week_data['客数']) / prev_week_data['客数'] * 100)
    unit_price_change = ((latest_week_data['客単価'] - prev_week_data['客単価']) / prev_week_data['客単価'] * 100)

    comparison_memo += f"""
### 前週比 ({prev_week})
- 売上: {sales_change:+.1f}% (¥{prev_week_data['売上']:,.0f} → ¥{latest_week_data['売上']:,.0f})
- 客数: {customer_change:+.1f}% ({prev_week_data['客数']:.0f}人 → {latest_week_data['客数']:.0f}人)
- 客単価: {unit_price_change:+.1f}% (¥{prev_week_data['客単価']:,.0f} → ¥{latest_week_data['客単価']:,.0f})
"""

if prev_month_data is not None:
    sales_change_m = ((latest_week_data['売上'] - prev_month_data['売上']) / prev_month_data['売上'] * 100)
    customer_change_m = ((latest_week_data['客数'] - prev_month_data['客数']) / prev_month_data['客数'] * 100)

    comparison_memo += f"""
### 前月比 ({prev_month_week})
- 売上: {sales_change_m:+.1f}%
- 客数: {customer_change_m:+.1f}%
"""

if prev_year_data is not None:
    sales_change_y = ((latest_week_data['売上'] - prev_year_data['売上']) / prev_year_data['売上'] * 100)
    customer_change_y = ((latest_week_data['客数'] - prev_year_data['客数']) / prev_year_data['客数'] * 100)

    comparison_memo += f"""
### 前年同週比 ({prev_year_week})
- 売上: {sales_change_y:+.1f}%
- 客数: {customer_change_y:+.1f}%
"""

save_memo("週次売上比較", comparison_memo)

# グラフ作成：週次売上推移
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

weekly_sales['売上'].plot(ax=axes[0, 0], marker='o', linewidth=2, markersize=6)
axes[0, 0].set_title('週次売上推移', fontsize=14, fontweight='bold')
axes[0, 0].set_ylabel('売上 (円)', fontsize=12)
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].axvline(x=week_list.index(latest_week), color='red', linestyle='--', alpha=0.5, label='対象週')

weekly_sales['客数'].plot(ax=axes[0, 1], marker='o', linewidth=2, markersize=6, color='green')
axes[0, 1].set_title('週次客数推移', fontsize=14, fontweight='bold')
axes[0, 1].set_ylabel('客数 (人)', fontsize=12)
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].axvline(x=week_list.index(latest_week), color='red', linestyle='--', alpha=0.5, label='対象週')

weekly_sales['客単価'].plot(ax=axes[1, 0], marker='o', linewidth=2, markersize=6, color='orange')
axes[1, 0].set_title('週次客単価推移', fontsize=14, fontweight='bold')
axes[1, 0].set_ylabel('客単価 (円)', fontsize=12)
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].axvline(x=week_list.index(latest_week), color='red', linestyle='--', alpha=0.5, label='対象週')

weekly_sales['組数'].plot(ax=axes[1, 1], marker='o', linewidth=2, markersize=6, color='purple')
axes[1, 1].set_title('週次組数推移', fontsize=14, fontweight='bold')
axes[1, 1].set_ylabel('組数', fontsize=12)
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].axvline(x=week_list.index(latest_week), color='red', linestyle='--', alpha=0.5, label='対象週')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'weekly_sales_trend.png'), dpi=150, bbox_inches='tight')
plt.close()

save_memo("グラフ保存", "週次売上推移グラフを保存しました")

# 曜日別売上分析
weekday_sales = account_df.groupby('weekday').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
})
weekday_sales['客単価'] = weekday_sales['account_total'] / weekday_sales['customer_count']

# 曜日順にソート
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
weekday_sales_ordered = weekday_sales.reindex([w for w in weekday_order if w in weekday_sales.index])

weekday_memo = "### 曜日別売上\n"
for day in weekday_sales_ordered.index:
    data = weekday_sales_ordered.loc[day]
    weekday_memo += f"- {day}曜日: 売上 ¥{data['account_total']:,.0f}, 客数 {data['customer_count']:.0f}人, 客単価 ¥{data['客単価']:,.0f}\n"

save_memo("曜日別分析", weekday_memo)

# グラフ作成：曜日別売上
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

weekday_sales_ordered['account_total'].plot(kind='bar', ax=axes[0], color='skyblue', edgecolor='black')
axes[0].set_title('曜日別売上', fontsize=14, fontweight='bold')
axes[0].set_ylabel('売上 (円)', fontsize=12)
axes[0].set_xlabel('曜日', fontsize=12)
axes[0].tick_params(axis='x', rotation=0)
axes[0].grid(axis='y', alpha=0.3)

weekday_sales_ordered['客単価'].plot(kind='bar', ax=axes[1], color='orange', edgecolor='black')
axes[1].set_title('曜日別客単価', fontsize=14, fontweight='bold')
axes[1].set_ylabel('客単価 (円)', fontsize=12)
axes[1].set_xlabel('曜日', fontsize=12)
axes[1].tick_params(axis='x', rotation=0)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'weekday_sales.png'), dpi=150, bbox_inches='tight')
plt.close()

# 時間別売上分析
hourly_sales = account_df.groupby('hour').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
})
hourly_sales['客単価'] = hourly_sales['account_total'] / hourly_sales['customer_count']

peak_hour = hourly_sales['account_total'].idxmax()
hourly_memo = f"""
### 時間別売上
- ピーク時間帯: {peak_hour}時台 (売上 ¥{hourly_sales.loc[peak_hour, 'account_total']:,.0f})
- 営業時間帯: {hourly_sales.index.min()}時 ～ {hourly_sales.index.max()}時
"""
save_memo("時間別分析", hourly_memo)

# グラフ作成：時間別売上
fig, ax = plt.subplots(figsize=(14, 5))
hourly_sales['account_total'].plot(kind='bar', ax=ax, color='lightcoral', edgecolor='black')
ax.set_title('時間別売上', fontsize=14, fontweight='bold')
ax.set_ylabel('売上 (円)', fontsize=12)
ax.set_xlabel('時間帯', fontsize=12)
ax.tick_params(axis='x', rotation=0)
ax.grid(axis='y', alpha=0.3)
ax.axvline(x=list(hourly_sales.index).index(peak_hour), color='red', linestyle='--', alpha=0.7, linewidth=2, label=f'ピーク: {peak_hour}時')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'hourly_sales.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==========================================
# 2. 商品分析
# ==========================================
save_memo("商品分析", """
【目的】どのカテゴリの商品が売れているか、構成比の変化を把握し、商品戦略に活かす
【仮説】
- 特定のカテゴリに人気が集中している
- 時期によって売れるカテゴリが変わる（季節性）
- 構成比の変化から顧客の嗜好変化を読み取れる
- 不人気カテゴリの改善余地がある
""")

# カテゴリ別売上（週次）
category_weekly = sales_df.groupby(['year_week', 'category1']).agg({
    'subtotal': 'sum',
    'quantity': 'sum'
}).reset_index()

# 対象週のカテゴリ別売上
latest_week_category = category_weekly[category_weekly['year_week'] == latest_week].copy()
latest_week_category = latest_week_category.sort_values('subtotal', ascending=False)
total_sales = latest_week_category['subtotal'].sum()
latest_week_category['構成比'] = latest_week_category['subtotal'] / total_sales * 100

# 前週のカテゴリ別売上
if prev_week:
    prev_week_category = category_weekly[category_weekly['year_week'] == prev_week].copy()
    prev_week_total = prev_week_category['subtotal'].sum()
    prev_week_category['構成比'] = prev_week_category['subtotal'] / prev_week_total * 100 if prev_week_total > 0 else 0
    prev_week_category = prev_week_category.set_index('category1')
else:
    prev_week_category = pd.DataFrame()

# 前月のカテゴリ別売上
if prev_month_week:
    prev_month_category = category_weekly[category_weekly['year_week'] == prev_month_week].copy()
    prev_month_total = prev_month_category['subtotal'].sum()
    prev_month_category['構成比'] = prev_month_category['subtotal'] / prev_month_total * 100 if prev_month_total > 0 else 0
    prev_month_category = prev_month_category.set_index('category1')
else:
    prev_month_category = pd.DataFrame()

# カテゴリランキングのメモ
category_memo = f"### 対象週 ({latest_week}) カテゴリ別ランキング\n"
for idx, row in latest_week_category.head(10).iterrows():
    category = row['category1']
    sales = row['subtotal']
    ratio = row['構成比']
    qty = row['quantity']

    # 前週比
    prev_change = ""
    if not prev_week_category.empty and category in prev_week_category.index:
        prev_ratio = prev_week_category.loc[category, '構成比']
        change = ratio - prev_ratio
        prev_change = f" (前週比: {change:+.1f}pt)"

    category_memo += f"{idx+1}. {category}: ¥{sales:,.0f} ({ratio:.1f}%, {qty:.0f}個){prev_change}\n"

save_memo("カテゴリランキング", category_memo)

# グラフ作成：カテゴリ別売上構成比
fig, ax = plt.subplots(figsize=(12, 8))
colors = sns.color_palette('Set3', len(latest_week_category))
wedges, texts, autotexts = ax.pie(
    latest_week_category['subtotal'],
    labels=latest_week_category['category1'],
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    textprops={'fontsize': 10}
)
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
ax.set_title(f'カテゴリ別売上構成比 ({latest_week})', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'category_composition.png'), dpi=150, bbox_inches='tight')
plt.close()

# カテゴリ別推移グラフ
category_pivot = category_weekly.pivot(index='year_week', columns='category1', values='subtotal').fillna(0)
top_categories = latest_week_category.head(8)['category1'].tolist()

fig, ax = plt.subplots(figsize=(15, 7))
for cat in top_categories:
    if cat in category_pivot.columns:
        category_pivot[cat].plot(ax=ax, marker='o', label=cat, linewidth=2)
ax.set_title('カテゴリ別売上推移（上位8カテゴリ）', fontsize=14, fontweight='bold')
ax.set_ylabel('売上 (円)', fontsize=12)
ax.set_xlabel('週', fontsize=12)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'category_trend.png'), dpi=150, bbox_inches='tight')
plt.close()

# カテゴリ別構成比の時系列データを作成（自然言語分析用）
save_memo("カテゴリ構成比時系列データ作成", "各週のカテゴリ別構成比を計算しています...")
category_composition_trend = []
for week in category_weekly['year_week'].unique():
    week_data = category_weekly[category_weekly['year_week'] == week].copy()
    week_total = week_data['subtotal'].sum()
    week_data['構成比'] = (week_data['subtotal'] / week_total * 100) if week_total > 0 else 0
    week_data['week'] = week
    category_composition_trend.append(week_data[['week', 'category1', 'subtotal', 'quantity', '構成比']])

category_composition_df = pd.concat(category_composition_trend, ignore_index=True)
category_composition_df = category_composition_df.sort_values(['week', '構成比'], ascending=[True, False])

# ==========================================
# 2.3. 商品別分析（NEW）
# ==========================================
save_memo("商品別分析", """
【目的】個別商品レベルでの売れ筋・死に筋を特定し、メニュー改訂の判断材料とする
【仮説】
- 特定の商品に売上が集中している
- 構成比の変化から商品人気の変動を読み取れる
- 売れ筋商品と死に筋商品が明確に分かれる
""")

# 商品別売上（週次）
product_weekly = sales_df.groupby(['year_week', 'menu_name']).agg({
    'subtotal': 'sum',
    'quantity': 'sum'
}).reset_index()

# 最新週の商品別売上
latest_week_product = product_weekly[product_weekly['year_week'] == latest_week].copy()
latest_week_product = latest_week_product.sort_values('subtotal', ascending=False)
total_sales_product = latest_week_product['subtotal'].sum()
latest_week_product['構成比'] = latest_week_product['subtotal'] / total_sales_product * 100

# 前週の商品別売上
if prev_week:
    prev_week_product = product_weekly[product_weekly['year_week'] == prev_week].copy()
    prev_week_product_total = prev_week_product['subtotal'].sum()
    prev_week_product['構成比'] = prev_week_product['subtotal'] / prev_week_product_total * 100 if prev_week_product_total > 0 else 0
    prev_week_product = prev_week_product.set_index('menu_name')
else:
    prev_week_product = pd.DataFrame()

# 前月の商品別売上
if prev_month_week:
    prev_month_product = product_weekly[product_weekly['year_week'] == prev_month_week].copy()
    prev_month_product_total = prev_month_product['subtotal'].sum()
    prev_month_product['構成比'] = prev_month_product['subtotal'] / prev_month_product_total * 100 if prev_month_product_total > 0 else 0
    prev_month_product = prev_month_product.set_index('menu_name')
else:
    prev_month_product = pd.DataFrame()

# 商品別ランキングのメモ
product_memo = f"### 対象週 ({latest_week}) 商品別ランキング TOP20\n"
for idx, row in latest_week_product.head(20).iterrows():
    product = row['menu_name']
    sales = row['subtotal']
    ratio = row['構成比']
    qty = row['quantity']

    # 前週比
    prev_change = ""
    if not prev_week_product.empty and product in prev_week_product.index:
        prev_ratio = prev_week_product.loc[product, '構成比']
        change = ratio - prev_ratio
        prev_change = f" (前週比: {change:+.2f}pt)"

    product_memo += f"{idx+1}. {product}: ¥{sales:,.0f} ({ratio:.2f}%, {qty:.0f}個){prev_change}\n"

save_memo("商品別ランキング", product_memo)

# グラフ作成：商品別売上TOP20（横棒グラフ）
fig, ax = plt.subplots(figsize=(12, 10))
top20_products = latest_week_product.head(20).copy()
top20_products = top20_products.iloc[::-1]  # 逆順にして上位が上に来るように

colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top20_products)))
bars = ax.barh(range(len(top20_products)), top20_products['subtotal'], color=colors, edgecolor='black')

ax.set_yticks(range(len(top20_products)))
ax.set_yticklabels(top20_products['menu_name'], fontsize=9)
ax.set_xlabel('売上 (円)', fontsize=12)
ax.set_title(f'商品別売上ランキング TOP20 ({latest_week})', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# 各バーに構成比を表示
for i, (bar, ratio) in enumerate(zip(bars, top20_products['構成比'])):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2, f' {ratio:.1f}%',
            ha='left', va='center', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'product_ranking.png'), dpi=150, bbox_inches='tight')
plt.close()

# 商品別構成比推移グラフ（上位10商品）
product_pivot = product_weekly.pivot(index='year_week', columns='menu_name', values='subtotal').fillna(0)
top_products = latest_week_product.head(10)['menu_name'].tolist()

fig, ax = plt.subplots(figsize=(15, 7))
for product in top_products:
    if product in product_pivot.columns:
        product_pivot[product].plot(ax=ax, marker='o', label=product, linewidth=2)
ax.set_title('商品別売上推移（上位10商品）', fontsize=14, fontweight='bold')
ax.set_ylabel('売上 (円)', fontsize=12)
ax.set_xlabel('週', fontsize=12)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'product_trend.png'), dpi=150, bbox_inches='tight')
plt.close()

# 商品別構成比の時系列データを作成（自然言語分析用）
save_memo("商品構成比時系列データ作成", "各週の商品別構成比を計算しています（TOP20商品のみ）...")
top20_product_names = latest_week_product.head(20)['menu_name'].tolist()
product_composition_trend = []
for week in product_weekly['year_week'].unique():
    week_data = product_weekly[product_weekly['year_week'] == week].copy()
    week_total = week_data['subtotal'].sum()
    week_data['構成比'] = (week_data['subtotal'] / week_total * 100) if week_total > 0 else 0
    # TOP20商品のみに絞る
    week_data_top = week_data[week_data['menu_name'].isin(top20_product_names)]
    week_data_top = week_data_top.copy()
    week_data_top['week'] = week
    product_composition_trend.append(week_data_top[['week', 'menu_name', 'subtotal', 'quantity', '構成比']])

product_composition_df = pd.concat(product_composition_trend, ignore_index=True)
product_composition_df = product_composition_df.sort_values(['week', '構成比'], ascending=[True, False])

# ==========================================
# 3. 口コミ分析
# ==========================================
save_memo("口コミ分析", """
【目的】顧客の声を収集し、満足度や改善点を把握する
【仮説】
- 口コミから顧客の満足度や不満点が明確になる
- 高評価・低評価の理由から改善すべき点が見つかる
- 口コミの内容から顧客の期待値を理解できる
""")

# 対象週の口コミ抽出
latest_date_dt = pd.to_datetime(target_date_end)
week_start_dt = pd.to_datetime(target_date_start)

latest_week_reviews = reviews_df[
    (reviews_df['投稿日'] >= week_start_dt) &
    (reviews_df['投稿日'] <= latest_date_dt)
].copy()

reviews_memo = f"""
### 対象週の口コミ ({target_date_start} ～ {target_date_end})
- 新規投稿数: {len(latest_week_reviews)}件
"""

if len(latest_week_reviews) > 0:
    avg_score = latest_week_reviews['総合点数'].mean()
    reviews_memo += f"- 平均評価: {avg_score:.2f}点\n\n"

    for idx, row in latest_week_reviews.iterrows():
        reviews_memo += f"""
#### {row['投稿者']} ({row['投稿日'].date()})
- 評価: {row['総合点数']}点
- タイトル: {row['口コミタイトル']}
- 内容: {row['口コミ内容'][:200]}{'...' if len(str(row['口コミ内容'])) > 200 else ''}
- 使用金額: {row['使った金額_夜']}
---
"""
else:
    reviews_memo += "- 対象週に新規投稿はありませんでした\n"

save_memo("対象週の口コミ", reviews_memo)

# 口コミ評価の推移（月次）
reviews_df['year_month'] = reviews_df['投稿日'].dt.strftime('%Y-%m')
monthly_reviews = reviews_df.groupby('year_month').agg({
    '総合点数': 'mean',
    '投稿者': 'count'
}).rename(columns={'投稿者': '投稿数'})

if len(monthly_reviews) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    monthly_reviews['総合点数'].plot(ax=axes[0], marker='o', linewidth=2, markersize=6, color='green')
    axes[0].set_title('月次平均評価推移', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('平均評価 (点)', fontsize=12)
    axes[0].set_ylim(0, 5)
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)

    monthly_reviews['投稿数'].plot(kind='bar', ax=axes[1], color='skyblue', edgecolor='black')
    axes[1].set_title('月次口コミ投稿数', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('投稿数 (件)', fontsize=12)
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'reviews_trend.png'), dpi=150, bbox_inches='tight')
    plt.close()

# ==========================================
# 結果の保存
# ==========================================
save_memo("データ保存", "分析結果をJSON、CSVファイルに保存しています...")

# 分析結果をJSON形式で保存
analysis_results = {
    'meta': {
        'analysis_date': str(datetime.now()),
        'data_period_start': str(sales_df['date'].min()),
        'data_period_end': str(sales_df['date'].max()),
        'target_week': latest_week,
        'target_date_start': str(target_date_start),
        'target_date_end': str(target_date_end),
        'store_name': sales_df['store_name'].iloc[0]
    },
    'sales_analysis': {
        'target_week': {
            '売上': float(latest_week_data['売上']) if latest_week_data is not None else None,
            '客数': int(latest_week_data['客数']) if latest_week_data is not None else None,
            '組数': int(latest_week_data['組数']) if latest_week_data is not None else None,
            '客単価': float(latest_week_data['客単価']) if latest_week_data is not None else None
        },
        'comparisons': {
            'previous_week': {
                'week': prev_week,
                'data': {
                    '売上': float(prev_week_data['売上']) if prev_week_data is not None else None,
                    '客数': int(prev_week_data['客数']) if prev_week_data is not None else None,
                    '客単価': float(prev_week_data['客単価']) if prev_week_data is not None else None
                }
            } if prev_week_data is not None else None,
            'previous_month': {
                'week': prev_month_week,
                'data': {
                    '売上': float(prev_month_data['売上']) if prev_month_data is not None else None,
                    '客数': int(prev_month_data['客数']) if prev_month_data is not None else None,
                    '客単価': float(prev_month_data['客単価']) if prev_month_data is not None else None
                }
            } if prev_month_data is not None else None,
            'previous_year': {
                'week': prev_year_week,
                'data': {
                    '売上': float(prev_year_data['売上']) if prev_year_data is not None else None,
                    '客数': int(prev_year_data['客数']) if prev_year_data is not None else None,
                    '客単価': float(prev_year_data['客単価']) if prev_year_data is not None else None
                }
            } if prev_year_data is not None else None
        }
    },
    'category_analysis': {
        'target_week': latest_week_category.to_dict('records'),
        'previous_week': prev_week_category.to_dict() if not prev_week_category.empty else None,
        'previous_month': prev_month_category.to_dict() if not prev_month_category.empty else None
    },
    'product_analysis': {
        'target_week': latest_week_product.to_dict('records'),
        'previous_week': prev_week_product.to_dict() if not prev_week_product.empty else None,
        'previous_month': prev_month_product.to_dict() if not prev_month_product.empty else None
    },
    'reviews_analysis': {
        'target_week_count': len(latest_week_reviews),
        'target_week_reviews': latest_week_reviews.to_dict('records')
    }
}

with open(os.path.join(output_dir, 'analysis_results.json'), 'w', encoding='utf-8') as f:
    json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)

# CSV形式でも保存
weekly_sales.to_csv(os.path.join(output_dir, 'weekly_sales.csv'), encoding='utf-8-sig')
weekday_sales.to_csv(os.path.join(output_dir, 'weekday_sales.csv'), encoding='utf-8-sig')
hourly_sales.to_csv(os.path.join(output_dir, 'hourly_sales.csv'), encoding='utf-8-sig')
latest_week_category.to_csv(os.path.join(output_dir, 'category_latest.csv'), encoding='utf-8-sig', index=False)
latest_week_product.to_csv(os.path.join(output_dir, 'product_latest.csv'), encoding='utf-8-sig', index=False)

# 構成比時系列データの保存（自然言語分析用）NEW!
category_composition_df.to_csv(os.path.join(output_dir, 'category_composition_trend.csv'), encoding='utf-8-sig', index=False)
product_composition_df.to_csv(os.path.join(output_dir, 'product_composition_trend.csv'), encoding='utf-8-sig', index=False)

if not latest_week_reviews.empty:
    latest_week_reviews.to_csv(os.path.join(output_dir, 'reviews_latest_week.csv'), encoding='utf-8-sig', index=False)

# 中間メモの保存
memo_file = os.path.join(output_dir, 'analysis_memo.txt')
with open(memo_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("分析中間メモ (2025-W42)\n")
    f.write("=" * 80 + "\n")
    for memo in memo_content:
        f.write(memo)

save_memo("完了", f"""
分析完了！結果は {output_dir} に保存されました。

生成されたファイル:
【グラフ】
- weekly_sales_trend.png: 週次売上推移グラフ
- weekday_sales.png: 曜日別売上グラフ
- hourly_sales.png: 時間別売上グラフ
- category_composition.png: カテゴリ別構成比グラフ
- category_trend.png: カテゴリ別推移グラフ
- product_ranking.png: 商品別売上ランキングTOP20（NEW）
- product_trend.png: 商品別売上推移（上位10商品）（NEW）
- reviews_trend.png: 口コミ評価推移グラフ

【データ】
- analysis_results.json: 分析結果（JSON、商品別データ含む）
- weekly_sales.csv: 週次売上データ
- weekday_sales.csv: 曜日別売上データ
- hourly_sales.csv: 時間別売上データ
- category_latest.csv: 対象週カテゴリ別売上
- product_latest.csv: 対象週商品別売上（NEW）
- category_composition_trend.csv: カテゴリ別構成比時系列データ（NEW）
- product_composition_trend.csv: 商品別構成比時系列データ（TOP20）（NEW）
- reviews_latest_week.csv: 対象週の口コミ
- analysis_memo.txt: 分析中間メモ
""")

print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
