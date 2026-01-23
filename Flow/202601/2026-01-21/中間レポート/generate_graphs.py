# -*- coding: utf-8 -*-
"""
中間レポート用グラフ生成スクリプト
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import csv
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定（Windows）
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = Path(__file__).parent
DATA_DIR = OUTPUT_DIR.parent
print(f"出力ディレクトリ: {OUTPUT_DIR}")
print(f"データディレクトリ: {DATA_DIR}")

# =========================================
# 図1 & 図2: 月別営業日当たり客数（6月含む）
# =========================================
print("\n=== 図1 & 図2: 月別営業日当たり客数の比較 ===")

monthly_summary = pd.read_csv(DATA_DIR / 'CustomerCountAnalysis' / '02_monthly_summary.csv')

year1, year2 = 2024, 2025

# 有効な月を取得（3月のみ除外、6月は含める）
y1_months = set(monthly_summary[monthly_summary['年'] == year1]['月'].values)
y2_months = set(monthly_summary[(monthly_summary['年'] == year2) & (monthly_summary['月'] != 3)]['月'].values)
valid_months = sorted(list(y1_months & y2_months))
print(f"有効な比較対象月: {valid_months}")

# 図1: 月別営業日当たり客数の比較
fig, ax = plt.subplots(figsize=(12, 6))

y1_data = monthly_summary[(monthly_summary['年'] == year1) & (monthly_summary['月'].isin(valid_months))].sort_values('月')
y2_data = monthly_summary[(monthly_summary['年'] == year2) & (monthly_summary['月'].isin(valid_months))].sort_values('月')

x = np.arange(len(valid_months))
width = 0.35

bars1 = ax.bar(x - width/2, y1_data['営業日当たり客数'], width, label=f'{year1}年', color='#5DADE2')
bars2 = ax.bar(x + width/2, y2_data['営業日当たり客数'], width, label=f'{year2}年', color='#F5B041')

ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数（人）', fontsize=12)
ax.set_title(f'THE BIFTEKI 赤坂見附店 - 月別営業日当たり客数の比較（{year1}年 vs {year2}年）', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.legend()
ax.grid(axis='y', alpha=0.3)

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
plt.savefig(OUTPUT_DIR / 'graph01_monthly_comparison.png', dpi=150)
plt.close()
print("graph01_monthly_comparison.png を作成しました")

# 図2: 月別の前年比増減
fig, ax = plt.subplots(figsize=(12, 6))

merged = y1_data.merge(y2_data, on='月', suffixes=('_2024', '_2025'))
merged['差分'] = merged['営業日当たり客数_2025'] - merged['営業日当たり客数_2024']
merged['増減率'] = (merged['差分'] / merged['営業日当たり客数_2024'] * 100).round(1)

colors = ['#27AE60' if d > 0 else '#E74C3C' for d in merged['差分']]
bars = ax.bar(valid_months, merged['差分'], color=colors)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'THE BIFTEKI 赤坂見附店 - 営業日当たり客数の前年比増減（{year2}年 - {year1}年）', fontsize=14)
ax.set_xticks(valid_months)
ax.set_xticklabels([f'{m}月' for m in valid_months])
ax.grid(axis='y', alpha=0.3)

for i, bar in enumerate(bars):
    height = bar.get_height()
    rate = merged['増減率'].iloc[i]
    sign = '+' if height > 0 else ''
    ax.annotate(f'{sign}{height:.0f}\n({sign}{rate}%)',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3 if height > 0 else -25), textcoords="offset points",
                ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph02_yoy_change.png', dpi=150)
plt.close()
print("graph02_yoy_change.png を作成しました")

# =========================================
# 図3: パーセンタイル別客単価の変化（4.3用）
# =========================================
print("\n=== 図3: パーセンタイル別客単価の変化 ===")

df = pd.read_csv(DATA_DIR / 'transformed_pos_data_eatin.csv')
df['日付'] = pd.to_datetime(df['H.集計対象営業年月日'])

# 期間定義
period_a_start = pd.to_datetime('2025-05-01')
period_a_end = pd.to_datetime('2025-07-31')
period_b_start = pd.to_datetime('2025-10-01')
period_b_end = pd.to_datetime('2025-12-31')

df_period_a = df[(df['日付'] >= period_a_start) & (df['日付'] <= period_a_end)].copy()
df_period_b = df[(df['日付'] >= period_b_start) & (df['日付'] <= period_b_end)].copy()

# 伝票単位の客単価を計算
def get_customer_price(df_period):
    receipt_df = df_period.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first'
    }).reset_index()
    receipt_df = receipt_df[receipt_df['H.客数（合計）'] > 0].copy()
    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']
    return receipt_df

receipt_a = get_customer_price(df_period_a)
receipt_b = get_customer_price(df_period_b)

# パーセンタイル計算
percentiles = [10, 25, 50, 75, 90, 95]
percentile_labels = ['10%', '25%', '50%\n(中央値)', '75%', '90%', '95%']
percentile_values_a = [receipt_a['客単価'].quantile(p/100) for p in percentiles]
percentile_values_b = [receipt_b['客単価'].quantile(p/100) for p in percentiles]
changes = [b - a for a, b in zip(percentile_values_a, percentile_values_b)]
change_rates = [(b/a - 1) * 100 for a, b in zip(percentile_values_a, percentile_values_b)]

# グラフ作成
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('客単価分布の変化（期間A: 5-7月 → 期間B: 10-12月）', fontsize=14, fontweight='bold')

# 左: パーセンタイル別客単価の比較
ax1 = axes[0]
x = np.arange(len(percentiles))
width = 0.35
bars1 = ax1.bar(x - width/2, percentile_values_a, width, label='期間A (5-7月)', color='steelblue', alpha=0.7)
bars2 = ax1.bar(x + width/2, percentile_values_b, width, label='期間B (10-12月)', color='coral', alpha=0.7)
ax1.set_xticks(x)
ax1.set_xticklabels(percentile_labels)
ax1.set_ylabel('客単価（円）', fontsize=11)
ax1.set_title('パーセンタイル別客単価の比較', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 右: 変化量と変化率
ax2 = axes[1]
colors = ['#27AE60' if c > 0 else '#E74C3C' for c in changes]
bars = ax2.bar(x, changes, color=colors, alpha=0.7)
ax2.set_xticks(x)
ax2.set_xticklabels(percentile_labels)
ax2.set_ylabel('客単価の変化（円）', fontsize=11)
ax2.set_title('パーセンタイル別の客単価変化', fontsize=12, fontweight='bold')
ax2.axhline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y')

# 変化率を注釈で表示
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax2.annotate(f'+{changes[i]:.0f}円\n(+{change_rates[i]:.1f}%)',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph03_percentile_change.png', dpi=150, bbox_inches='tight')
plt.close()
print("graph03_percentile_change.png を作成しました")

# =========================================
# 図4: 曜日・時間帯別客単価（X軸10-22時）
# =========================================
print("\n=== 図4: 曜日・時間帯別客単価 ===")

# 伝票単位で時間情報を取得
def analyze_by_hour_fixed(df_period):
    df_period = df_period.copy()
    df_period['伝票発行時刻'] = pd.to_datetime(df_period['H.伝票発行日'])
    df_period['時間'] = df_period['伝票発行時刻'].dt.hour
    
    receipt_df = df_period.groupby(['H.伝票番号', '時間']).agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first'
    }).reset_index()
    receipt_df = receipt_df[receipt_df['H.客数（合計）'] > 0].copy()
    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']
    
    hour_summary = receipt_df.groupby('時間').agg({
        '客単価': ['mean', 'count']
    }).reset_index()
    hour_summary.columns = ['時間', '平均客単価', '伝票数']
    
    return hour_summary

hour_a = analyze_by_hour_fixed(df_period_a)
hour_b = analyze_by_hour_fixed(df_period_b)

hour_comp = hour_a.merge(hour_b, on='時間', suffixes=('_A', '_B'))
hour_comp['客単価変化'] = hour_comp['平均客単価_B'] - hour_comp['平均客単価_A']
hour_comp = hour_comp[(hour_comp['伝票数_A'] >= 10) & (hour_comp['時間'] >= 10) & (hour_comp['時間'] <= 22)]

# 曜日別分析
def analyze_by_weekday_fixed(df_period):
    receipt_df = df_period.groupby(['H.伝票番号', 'H.曜日']).agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first'
    }).reset_index()
    receipt_df = receipt_df[receipt_df['H.客数（合計）'] > 0].copy()
    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']
    
    weekday_summary = receipt_df.groupby('H.曜日').agg({
        '客単価': ['mean', 'count']
    }).reset_index()
    weekday_summary.columns = ['曜日', '平均客単価', '伝票数']
    
    weekday_order = ['月', '火', '水', '木', '金', '土', '日']
    weekday_summary['曜日'] = pd.Categorical(weekday_summary['曜日'], categories=weekday_order, ordered=True)
    weekday_summary = weekday_summary.sort_values('曜日')
    
    return weekday_summary

weekday_a = analyze_by_weekday_fixed(df_period_a)
weekday_b = analyze_by_weekday_fixed(df_period_b)

weekday_comp = weekday_a[['曜日', '平均客単価', '伝票数']].merge(
    weekday_b[['曜日', '平均客単価', '伝票数']],
    on='曜日',
    suffixes=('_A', '_B')
)
weekday_comp['客単価変化'] = weekday_comp['平均客単価_B'] - weekday_comp['平均客単価_A']

# グラフ作成
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('曜日別・時間帯別分析', fontsize=14, fontweight='bold')

# 曜日別客単価
ax1 = axes[0, 0]
x = np.arange(len(weekday_comp))
width = 0.35
ax1.bar(x - width/2, weekday_comp['平均客単価_A'], width, label='期間A (5-7月)', color='steelblue', alpha=0.7)
ax1.bar(x + width/2, weekday_comp['平均客単価_B'], width, label='期間B (10-12月)', color='coral', alpha=0.7)
ax1.set_xticks(x)
ax1.set_xticklabels(weekday_comp['曜日'])
ax1.set_ylabel('平均客単価（円）', fontsize=11)
ax1.set_title('曜日別平均客単価', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 曜日別客単価変化
ax2 = axes[0, 1]
colors2 = ['red' if x > 0 else 'blue' for x in weekday_comp['客単価変化']]
ax2.bar(weekday_comp['曜日'], weekday_comp['客単価変化'], color=colors2, alpha=0.7)
ax2.set_ylabel('客単価変化（円）', fontsize=11)
ax2.set_title('曜日別客単価変化', fontsize=12, fontweight='bold')
ax2.axhline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y')

# 時間帯別客単価（X軸10-22時のみ）
ax3 = axes[1, 0]
ax3.plot(hour_comp['時間'], hour_comp['平均客単価_A'], 'o-', linewidth=2, markersize=6, label='期間A (5-7月)', color='steelblue')
ax3.plot(hour_comp['時間'], hour_comp['平均客単価_B'], 's-', linewidth=2, markersize=6, label='期間B (10-12月)', color='coral')
ax3.set_xlabel('時間', fontsize=11)
ax3.set_ylabel('平均客単価（円）', fontsize=11)
ax3.set_title('時間帯別平均客単価', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xticks(range(10, 23, 2))
ax3.set_xlim(9.5, 22.5)

# 時間帯別伝票数（X軸10-22時のみ）
ax4 = axes[1, 1]
ax4.bar(hour_comp['時間'] - 0.2, hour_comp['伝票数_A'], width=0.4, alpha=0.5, label='期間A (5-7月)', color='steelblue')
ax4.bar(hour_comp['時間'] + 0.2, hour_comp['伝票数_B'], width=0.4, alpha=0.5, label='期間B (10-12月)', color='coral')
ax4.set_xlabel('時間', fontsize=11)
ax4.set_ylabel('伝票数', fontsize=11)
ax4.set_title('時間帯別伝票数', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_xticks(range(10, 23, 2))
ax4.set_xlim(9.5, 22.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph04_weekday_hour_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("graph04_weekday_hour_analysis.png を作成しました")

# =========================================
# 図5: メニュー貢献度（カテゴリ別 + TOP10）
# =========================================
print("\n=== 図5: メニュー貢献度 ===")

# メニュー別売上分析
def analyze_menu_sales(df_period):
    menu_df = df_period.groupby('D.商品名').agg({
        'D.価格': ['sum', 'count', 'mean']
    }).reset_index()
    menu_df.columns = ['商品名', '販売金額', '販売数', '平均単価']
    menu_df = menu_df.sort_values('販売金額', ascending=False).reset_index(drop=True)
    return menu_df

menu_a = analyze_menu_sales(df_period_a)
menu_b = analyze_menu_sales(df_period_b)

# 比較
menu_comparison = menu_a[['商品名', '販売金額', '販売数']].merge(
    menu_b[['商品名', '販売金額', '販売数']],
    on='商品名',
    how='outer',
    suffixes=('_A', '_B')
).fillna(0)

menu_comparison['販売金額_差分'] = menu_comparison['販売金額_B'] - menu_comparison['販売金額_A']
menu_comparison['販売数_差分'] = menu_comparison['販売数_B'] - menu_comparison['販売数_A']
menu_comparison = menu_comparison.sort_values('販売金額_差分', ascending=False)

# カテゴリ別貢献度
def analyze_category_contribution(df_period_a, df_period_b):
    cat_a = df_period_a.groupby('D.商品カテゴリ2')['D.価格'].sum()
    cat_b = df_period_b.groupby('D.商品カテゴリ2')['D.価格'].sum()
    
    cat_comp = pd.DataFrame({
        '販売金額_A': cat_a,
        '販売金額_B': cat_b
    }).fillna(0)
    
    cat_comp['差分'] = cat_comp['販売金額_B'] - cat_comp['販売金額_A']
    cat_comp = cat_comp.sort_values('差分', ascending=False)
    
    return cat_comp

cat_contribution = analyze_category_contribution(df_period_a, df_period_b)

# グラフ作成
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('メニュー別売上貢献度分析（期間A: 5-7月 → 期間B: 10-12月）', fontsize=14, fontweight='bold')

# 左: カテゴリ別貢献度
ax1 = axes[0]
cat_sorted = cat_contribution.sort_values('差分')
colors1 = ['#27AE60' if x > 0 else '#E74C3C' for x in cat_sorted['差分']]
bars1 = ax1.barh(cat_sorted.index, cat_sorted['差分'] / 10000, color=colors1, alpha=0.7)  # 万円単位
ax1.set_xlabel('売上増減額（万円）', fontsize=11)
ax1.set_title('カテゴリ別売上増減額', fontsize=12, fontweight='bold')
ax1.axvline(0, color='black', linewidth=0.8)
ax1.grid(True, alpha=0.3, axis='x')

# 右: 販売数増加TOP10
ax2 = axes[1]
top_volume = menu_comparison.sort_values('販売数_差分', ascending=False).head(10)
colors2 = ['#27AE60' if x > 0 else '#E74C3C' for x in top_volume['販売数_差分']]
bars2 = ax2.barh(range(len(top_volume)), top_volume['販売数_差分'], color=colors2, alpha=0.7)
ax2.set_yticks(range(len(top_volume)))
ax2.set_yticklabels(top_volume['商品名'], fontsize=9)
ax2.set_xlabel('販売数増加', fontsize=11)
ax2.set_title('販売数が最も増加したメニューTOP10', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph05_menu_contribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("graph05_menu_contribution.png を作成しました")

# =========================================
# 図6: 時間帯別来店組数と店内人数（フォント修正）
# =========================================
print("\n=== 図6: 時間帯別来店組数と店内人数 ===")

VISITS_FILE = DATA_DIR / "visits_with_duration.csv"
OCCUPANCY_FILE = DATA_DIR / "occupancy_10min.csv"

weekdays = ["月", "火", "水", "木", "金"]
weekends = ["土", "日"]

hourly_visits = {
    "平日": defaultdict(lambda: {"groups": 0, "customers": 0, "days": set()}),
    "土日": defaultdict(lambda: {"groups": 0, "customers": 0, "days": set()})
}

with open(VISITS_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        entry_time = row["入店時刻"]
        customers = int(row["客数"])
        date = row["営業日"]
        weekday = row["曜日"]
        
        day_type = "平日" if weekday in weekdays else "土日"
        
        try:
            dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
            hour = dt.hour
            hourly_visits[day_type][hour]["groups"] += 1
            hourly_visits[day_type][hour]["customers"] += customers
            hourly_visits[day_type][hour]["days"].add(date)
        except:
            continue

hourly_occupancy = {
    "平日": defaultdict(list),
    "土日": defaultdict(list)
}

with open(OCCUPANCY_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        time_slot = row["時刻"]
        count = int(row["店内人数"])
        weekday = row["曜日"]
        hour = int(time_slot.split(":")[0])
        
        day_type = "平日" if weekday in weekdays else "土日"
        hourly_occupancy[day_type][hour].append(count)

hours = list(range(10, 23))

data_hourly = {}
for day_type in ["平日", "土日"]:
    data_hourly[day_type] = {
        "groups": [],
        "customers": [],
        "occupancy": []
    }
    for h in hours:
        visit_data = hourly_visits[day_type][h]
        num_days = len(visit_data["days"]) if visit_data["days"] else 1
        data_hourly[day_type]["groups"].append(visit_data["groups"] / num_days)
        data_hourly[day_type]["customers"].append(visit_data["customers"] / num_days)
        
        occ_values = hourly_occupancy[day_type][h]
        data_hourly[day_type]["occupancy"].append(sum(occ_values) / len(occ_values) if occ_values else 0)

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

colors_day = {"平日": "#2196F3", "土日": "#E53935"}

for idx, day_type in enumerate(["平日", "土日"]):
    ax1 = axes[idx]
    x = range(len(hours))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], data_hourly[day_type]["groups"], width, 
            label='来店組数/日', color=colors_day[day_type], alpha=0.7)
    ax1.bar([i + width/2 for i in x], data_hourly[day_type]["customers"], width,
            label='来店客数/日', color='#4CAF50', alpha=0.7)
    
    ax1.set_xlabel('時刻', fontsize=12)
    ax1.set_ylabel('1日あたりの来店数', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{h}:00" for h in hours], rotation=45)
    ax1.set_ylim(0, 45)
    ax1.grid(axis='y', alpha=0.3)
    
    ax2 = ax1.twinx()
    ax2.plot(x, data_hourly[day_type]["occupancy"], color='#FF5722', linewidth=2.5, 
            marker='o', markersize=6, label='平均店内人数')
    ax2.set_ylabel('平均店内人数', fontsize=12, color='#FF5722')
    ax2.tick_params(axis='y', labelcolor='#FF5722')
    ax2.set_ylim(0, 25)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    ax1.set_title(f'{day_type}の来店数と店内人数（1日平均）', fontsize=14)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph06_hourly_visits_occupancy.png", dpi=150, bbox_inches='tight')
plt.close()
print("graph06_hourly_visits_occupancy.png を作成しました")

# =========================================
# 図7: 時間帯別客数と客単価（フォント修正）
# =========================================
print("\n=== 図7: 時間帯別客数と客単価 ===")

EATIN_FILE = DATA_DIR / "transformed_pos_data_eatin.csv"

weekdays_list = ["月", "火", "水", "木", "金"]
weekends_list = ["土", "日"]

def get_15min_slot(hour, minute):
    slot_minute = (minute // 15) * 15
    return f"{hour:02d}:{slot_minute:02d}"

data_spend = {
    "平日": defaultdict(lambda: {"total_sales": 0, "total_customers": 0, "count": 0}),
    "土日": defaultdict(lambda: {"total_sales": 0, "total_customers": 0, "count": 0})
}

processed_tickets = set()

with open(EATIN_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticket_no = row["H.伝票番号"]
        
        if ticket_no in processed_tickets:
            continue
        processed_tickets.add(ticket_no)
        
        weekday = row["H.曜日"]
        entry_time = row["H.伝票発行日"]
        
        try:
            sales = int(row["H.小計"])
            customers = int(row["H.客数（合計）"])
            
            if customers == 0:
                continue
            
            dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
            slot = get_15min_slot(dt.hour, dt.minute)
            
            day_type = "平日" if weekday in weekdays_list else "土日"
            data_spend[day_type][slot]["total_sales"] += sales
            data_spend[day_type][slot]["total_customers"] += customers
            data_spend[day_type][slot]["count"] += 1
        except:
            continue

# 15分スロット（10:00〜22:45）
time_slots = []
for h in range(10, 23):
    for m in [0, 15, 30, 45]:
        time_slots.append(f"{h:02d}:{m:02d}")

stats = {"平日": {"spend": [], "customers": []}, 
         "土日": {"spend": [], "customers": []}}

for day_type in ["平日", "土日"]:
    for slot in time_slots:
        slot_data = data_spend[day_type][slot]
        if slot_data["total_customers"] > 0:
            avg_spend = slot_data["total_sales"] / slot_data["total_customers"]
            stats[day_type]["spend"].append(avg_spend)
            stats[day_type]["customers"].append(slot_data["total_customers"])
        else:
            stats[day_type]["spend"].append(None)
            stats[day_type]["customers"].append(0)

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

x_indices = list(range(len(time_slots)))
tick_indices = [i for i, slot in enumerate(time_slots) if slot.endswith(":00")]
tick_labels = [time_slots[i] for i in tick_indices]

colors_spend = {"平日": "#2196F3", "土日": "#E53935"}

for idx, day_type in enumerate(["平日", "土日"]):
    ax1 = axes[idx]
    
    customers = stats[day_type]["customers"]
    bars = ax1.bar(x_indices, customers, color=colors_spend[day_type], alpha=0.6, label='客数')
    
    ax1.set_xlabel('入店時刻', fontsize=12)
    ax1.set_ylabel('客数', fontsize=12, color=colors_spend[day_type])
    ax1.tick_params(axis='y', labelcolor=colors_spend[day_type])
    ax1.set_xticks(tick_indices)
    ax1.set_xticklabels(tick_labels, rotation=45)
    ax1.set_xlim(-0.5, len(time_slots)-0.5)
    ax1.grid(axis='y', alpha=0.3)
    
    ax2 = ax1.twinx()
    spend = stats[day_type]["spend"]
    
    valid_x = [x for x, s in zip(x_indices, spend) if s is not None]
    valid_y = [s for s in spend if s is not None]
    
    line = ax2.plot(valid_x, valid_y, color='#FF9800', linewidth=2.5, 
                   marker='o', markersize=4, label='客単価')
    ax2.set_ylabel('客単価（円）', fontsize=12, color='#FF9800')
    ax2.tick_params(axis='y', labelcolor='#FF9800')
    ax2.set_ylim(800, 1800)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax1.set_title(f'{day_type}：入店時間帯別の客数と客単価（15分刻み）', fontsize=14)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph07_spend_customers_by_time.png", dpi=150, bbox_inches='tight')
plt.close()
print("graph07_spend_customers_by_time.png を作成しました")

# =========================================
# 図8: 売上上位/下位の2軸分布（フォント修正）
# =========================================
print("\n=== 図8: 売上上位/下位の2軸分布 ===")

VISITS_FILE = DATA_DIR / "visits_with_duration.csv"
OCCUPANCY_FILE = DATA_DIR / "occupancy_10min.csv"

weekdays_list = ["月", "火", "水", "木", "金"]

daily_data = defaultdict(lambda: {
    "sales": 0, "tickets": set(), "weekday": "", "is_weekday": False,
    "lunch_groups": 0, "dinner_groups": 0,
    "total_groups": 0, "total_customers": 0,
    "total_duration": 0, "duration_count": 0,
    "peak_occupancy": 0
})

with open(EATIN_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row["H.集計対象営業年月日"]
        ticket_no = row["H.伝票番号"]
        weekday = row["H.曜日"]
        
        daily_data[date]["weekday"] = weekday
        daily_data[date]["is_weekday"] = weekday in weekdays_list
        
        if ticket_no not in daily_data[date]["tickets"]:
            try:
                sales = int(row["H.小計"])
                daily_data[date]["sales"] += sales
                daily_data[date]["tickets"].add(ticket_no)
            except:
                pass

with open(VISITS_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row["営業日"]
        customers = int(row["客数"])
        duration = int(row["滞在時間_分"])
        entry_time = row["入店時刻"]
        
        if duration > 120:
            continue
        
        try:
            dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
            hour = dt.hour
            
            daily_data[date]["total_groups"] += 1
            daily_data[date]["total_customers"] += customers
            daily_data[date]["total_duration"] += duration
            daily_data[date]["duration_count"] += 1
            
            if 11 <= hour <= 13:
                daily_data[date]["lunch_groups"] += 1
            elif 18 <= hour <= 21:
                daily_data[date]["dinner_groups"] += 1
        except:
            pass

records = []
for date, info in daily_data.items():
    if info["sales"] == 0 or info["total_groups"] == 0:
        continue
    
    records.append({
        "date": date,
        "weekday": info["weekday"],
        "is_weekday": info["is_weekday"],
        "sales": info["sales"] / 10000,
        "total_groups": info["total_groups"],
        "total_customers": info["total_customers"],
        "lunch_groups": info["lunch_groups"],
        "dinner_groups": info["dinner_groups"],
    })

weekday_records = [r for r in records if r["is_weekday"]]

sales = [r["sales"] for r in weekday_records]
median_sales = np.median(sales)
high_sales = [r for r in weekday_records if r["sales"] > median_sales]
low_sales = [r for r in weekday_records if r["sales"] <= median_sales]

fig2, axes2 = plt.subplots(2, 2, figsize=(14, 14))

# ランチ vs ディナー
ax = axes2[0, 0]
ax.scatter([r["lunch_groups"] for r in low_sales], 
           [r["dinner_groups"] for r in low_sales],
           alpha=0.5, s=40, c='#2196F3', label=f'売上下位（≤{median_sales:.0f}万円）')
ax.scatter([r["lunch_groups"] for r in high_sales], 
           [r["dinner_groups"] for r in high_sales],
           alpha=0.5, s=40, c='#E53935', label=f'売上上位（>{median_sales:.0f}万円）')
ax.set_xlabel('ランチ組数', fontsize=11)
ax.set_ylabel('ディナー組数', fontsize=11)
ax.set_title('ランチ組数 vs ディナー組数', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

# 総来店組数 vs ディナー組数
ax = axes2[0, 1]
ax.scatter([r["total_groups"] for r in low_sales], 
           [r["dinner_groups"] for r in low_sales],
           alpha=0.5, s=40, c='#2196F3', label=f'売上下位')
ax.scatter([r["total_groups"] for r in high_sales], 
           [r["dinner_groups"] for r in high_sales],
           alpha=0.5, s=40, c='#E53935', label=f'売上上位')
ax.set_xlabel('総来店組数', fontsize=11)
ax.set_ylabel('ディナー組数', fontsize=11)
ax.set_title('総来店組数 vs ディナー組数', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

# 総来店客数 vs ディナー組数
ax = axes2[1, 0]
ax.scatter([r["total_customers"] for r in low_sales], 
           [r["dinner_groups"] for r in low_sales],
           alpha=0.5, s=40, c='#2196F3', label=f'売上下位')
ax.scatter([r["total_customers"] for r in high_sales], 
           [r["dinner_groups"] for r in high_sales],
           alpha=0.5, s=40, c='#E53935', label=f'売上上位')
ax.set_xlabel('総来店客数', fontsize=11)
ax.set_ylabel('ディナー組数', fontsize=11)
ax.set_title('総来店客数 vs ディナー組数', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

# ランチ vs 総来店客数
ax = axes2[1, 1]
ax.scatter([r["lunch_groups"] for r in low_sales], 
           [r["total_customers"] for r in low_sales],
           alpha=0.5, s=40, c='#2196F3', label=f'売上下位')
ax.scatter([r["lunch_groups"] for r in high_sales], 
           [r["total_customers"] for r in high_sales],
           alpha=0.5, s=40, c='#E53935', label=f'売上上位')
ax.set_xlabel('ランチ組数', fontsize=11)
ax.set_ylabel('総来店客数', fontsize=11)
ax.set_title('ランチ組数 vs 総来店客数', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

plt.suptitle('売上上位/下位の2軸分布（平日）', fontsize=14)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph08_sales_2d_separation.png", dpi=150, bbox_inches='tight')
plt.close()
print("graph08_sales_2d_separation.png を作成しました")

print("\n=== 全グラフ作成完了 ===")
