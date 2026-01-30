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
import argparse
from PIL import Image

# 日本語フォント設定（macOS優先でフォールバック）
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

PROJECT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_DIR / "reports"
DATA_DIR = PROJECT_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"出力ディレクトリ: {OUTPUT_DIR}")
print(f"データディレクトリ: {DATA_DIR}")

# ---------------------------------
# 素材（分割）出力
# ---------------------------------
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--split-assets", action="store_true", help="複合グラフをスライド素材用に分割して出力する（デフォルトOFF）")
parser.add_argument("--assets-dir", default=None, help="分割素材の出力先（未指定なら reports/_slide_assets/）")
args, _ = parser.parse_known_args()

ASSETS_DIR = Path(args.assets_dir).resolve() if args.assets_dir else (OUTPUT_DIR / "_slide_assets")
if args.split_assets:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def _safe_save_crop(img: Image.Image, crop_box, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cropped = img.crop(crop_box)
    cropped.save(out_path)

def _split_2cols(img_path: Path, left_name: str, right_name: str):
    img = Image.open(img_path)
    w, h = img.size
    mid = w // 2
    _safe_save_crop(img, (0, 0, mid, h), ASSETS_DIR / left_name)
    _safe_save_crop(img, (mid, 0, w, h), ASSETS_DIR / right_name)

def _split_2x2(img_path: Path, names: list[str]):
    img = Image.open(img_path)
    w, h = img.size
    mid_x = w // 2
    mid_y = h // 2
    boxes = [
        (0, 0, mid_x, mid_y),        # top-left
        (mid_x, 0, w, mid_y),        # top-right
        (0, mid_y, mid_x, h),        # bottom-left
        (mid_x, mid_y, w, h),        # bottom-right
    ]
    for name, box in zip(names, boxes):
        _safe_save_crop(img, box, ASSETS_DIR / name)

# =========================================
# 図1 & 図2: 月別営業日当たり客数（6月含む）
# =========================================
print("\n=== 図1 & 図2: 月別営業日当たり客数の比較 ===")

monthly_summary = pd.read_csv(DATA_DIR / '02_monthly_summary.csv')

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
# 図3: パーセンタイル別客単価の変化（旧：不均一な分位）
#   - レポートでは20%刻み（5エリア）を採用するため、旧図は生成しない
# =========================================
print("\n=== 図3: パーセンタイル別客単価の変化（旧）: skip ===")

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

# NOTE: 旧図の生成ロジックは削除（必要ならgit履歴から復元）

# =========================================
# 図3-2: 客単価分布の変化（20%刻み・5エリア・4.3追加用）
#   - 0-20 / 20-40 / 40-60 / 60-80 / 80-100 の5区間
# =========================================
print("\n=== 図3-2: 客単価分布の変化（20%刻み・5エリア） ===")

bin_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
bin_labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']

def add_quintile_bins(receipt_df: pd.DataFrame) -> pd.DataFrame:
    out = receipt_df.copy()
    # qcutで各期間内を20%ずつの5区間に分割（同率が多い場合はduplicates='drop'で安全側）
    out['エリア'] = pd.qcut(out['客単価'], q=bin_edges, labels=bin_labels, duplicates='drop')
    return out

ra = add_quintile_bins(receipt_a)
rb = add_quintile_bins(receipt_b)

def summarize_bins(r: pd.DataFrame) -> pd.DataFrame:
    s = r.groupby('エリア', observed=True).agg(
        平均客単価=('客単価', 'mean'),
        下限=('客単価', 'min'),
        上限=('客単価', 'max'),
        件数=('客単価', 'count'),
    ).reindex(bin_labels)
    return s

sa = summarize_bins(ra)
sb = summarize_bins(rb)

# 変化（平均客単価ベース）
mean_a = sa['平均客単価'].values
mean_b = sb['平均客単価'].values
changes = mean_b - mean_a
change_rates = (mean_b / mean_a - 1) * 100

# グラフ作成（5エリア）
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('客単価分布の変化（20%刻み・5エリア）（期間A: 5-7月 → 期間B: 10-12月）', fontsize=14, fontweight='bold')

# 左: エリア別の平均客単価（各期間内で20%ずつの区間）
ax1 = axes[0]
x = np.arange(len(bin_labels))
width = 0.35
ax1.bar(x - width/2, mean_a, width, label='期間A (5-7月)', color='steelblue', alpha=0.7)
ax1.bar(x + width/2, mean_b, width, label='期間B (10-12月)', color='coral', alpha=0.7)
ax1.set_xticks(x)
ax1.set_xticklabels(bin_labels)
ax1.set_ylabel('平均客単価（円）', fontsize=11)
ax1.set_title('エリア別の平均客単価（20%刻み）', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 右: 平均客単価の変化量と変化率
ax2 = axes[1]
colors = ['#27AE60' if c > 0 else '#E74C3C' for c in changes]
bars = ax2.bar(x, changes, color=colors, alpha=0.7)
ax2.set_xticks(x)
ax2.set_xticklabels(bin_labels)
ax2.set_ylabel('平均客単価の変化（円）', fontsize=11)
ax2.set_title('エリア別の平均客単価変化（20%刻み）', fontsize=12, fontweight='bold')
ax2.axhline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y')

for i, bar in enumerate(bars):
    height = bar.get_height()
    sign_yen = '+' if height >= 0 else ''
    sign_pct = '+' if change_rates[i] >= 0 else ''
    ax2.annotate(f'{sign_yen}{height:.0f}円\n({sign_pct}{change_rates[i]:.1f}%)',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3 if height >= 0 else -28),
                 textcoords="offset points",
                 ha='center',
                 va='bottom' if height >= 0 else 'top',
                 fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph03_percentile_change_20pct.png', dpi=150, bbox_inches='tight')
plt.close()
print("graph03_percentile_change_20pct.png を作成しました")

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

if args.split_assets:
    # 左: カテゴリ別売上増減額 / 右: 販売数増加TOP
    _split_2cols(
        OUTPUT_DIR / "graph05_menu_contribution.png",
        "graph05_menu_contribution__category_contribution.png",
        "graph05_menu_contribution__top_volume.png",
    )

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

if args.split_assets:
    # 2x2を分割（スライドでは主に左上を使用）
    _split_2x2(
        OUTPUT_DIR / "graph08_sales_2d_separation.png",
        [
            "graph08_sales_2d_separation__lunch_vs_dinner.png",
            "graph08_sales_2d_separation__total_groups_vs_dinner.png",
            "graph08_sales_2d_separation__total_customers_vs_dinner.png",
            "graph08_sales_2d_separation__lunch_vs_total_customers.png",
        ],
    )

# =========================================
# 図9-12: CustomerCountAnalysis用グラフ（6月含む）
# =========================================
print("\n=== 図9-12: CustomerCountAnalysis用グラフ（6月含む）===")

# 時間帯別・曜日別データ読み込み
time_month = pd.read_csv(DATA_DIR / '04_time_month_comparison.csv')
weekday_month = pd.read_csv(DATA_DIR / '03_weekday_month_comparison.csv')

# 有効な月（3月のみ除外、6月は含める）
valid_months_all = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# 図9: 時間帯別ヒートマップ（6月含む）
time_order = ['ランチ(11-15時)', 'アイドル(15-17時)', 'ディナー(17-22時)']
time_pivot = time_month[time_month['月'].isin(valid_months_all)].pivot_table(
    index='時間帯', columns='月', values='差分_日当たり客数'
).reindex(time_order)

fig, ax = plt.subplots(figsize=(14, 5))
im = ax.imshow(time_pivot.values, cmap='RdYlGn', aspect='auto', vmin=-100, vmax=100)

ax.set_xticks(np.arange(len(valid_months_all)))
ax.set_yticks(np.arange(len(time_order)))
ax.set_xticklabels([f'{m}月' for m in valid_months_all])
ax.set_yticklabels(time_order)

for i in range(len(time_order)):
    for j in range(len(valid_months_all)):
        val = time_pivot.iloc[i, j] if j < len(time_pivot.columns) else np.nan
        if pd.notna(val):
            text_color = 'white' if abs(val) > 50 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', color=text_color, fontsize=10)

ax.set_title(f'時間帯別・営業日当たり客数の前年比増減（2025年 - 2024年）', fontsize=14)
fig.colorbar(im, ax=ax, label='増減（人/日）')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph09_time_heatmap.png', dpi=150)
plt.close()
print("graph09_time_heatmap.png を作成しました")

# 図10: 時間帯別の寄与度分析（積み上げ棒グラフ、6月含む）
time_contrib = time_month[time_month['月'].isin(valid_months_all) & 
                          time_month['時間帯'].isin(time_order)].copy()
time_contrib_pivot = time_contrib.pivot_table(
    index='月', columns='時間帯', values='差分_日当たり客数'
)[time_order]

fig, ax = plt.subplots(figsize=(14, 6))

bottom_pos = np.zeros(len(valid_months_all))
bottom_neg = np.zeros(len(valid_months_all))
colors_time = {'ランチ(11-15時)': '#3498DB', 'アイドル(15-17時)': '#9B59B6', 'ディナー(17-22時)': '#E67E22'}

for time_slot in time_order:
    values = []
    for m in valid_months_all:
        if m in time_contrib_pivot.index:
            values.append(time_contrib_pivot.loc[m, time_slot] if time_slot in time_contrib_pivot.columns else 0)
        else:
            values.append(0)
    values = np.array(values)
    pos_values = np.where(values > 0, values, 0)
    neg_values = np.where(values < 0, values, 0)
    
    ax.bar(valid_months_all, pos_values, bottom=bottom_pos, label=time_slot, color=colors_time[time_slot])
    ax.bar(valid_months_all, neg_values, bottom=bottom_neg, color=colors_time[time_slot])
    
    bottom_pos += pos_values
    bottom_neg += neg_values

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'時間帯別の客数増減寄与（2025年 - 2024年）', fontsize=14)
ax.set_xticks(valid_months_all)
ax.set_xticklabels([f'{m}月' for m in valid_months_all])
ax.legend(loc='upper right')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph10_time_contribution.png', dpi=150)
plt.close()
print("graph10_time_contribution.png を作成しました")

# 図11: 曜日別ヒートマップ（6月含む）
weekday_order = ['月', '火', '水', '木', '金', '土', '日']
weekday_pivot = weekday_month[weekday_month['月'].isin(valid_months_all)].pivot_table(
    index='曜日', columns='月', values='差分_日当たり客数'
).reindex(weekday_order)

fig, ax = plt.subplots(figsize=(14, 6))
im = ax.imshow(weekday_pivot.values, cmap='RdYlGn', aspect='auto', vmin=-100, vmax=200)

ax.set_xticks(np.arange(len(valid_months_all)))
ax.set_yticks(np.arange(len(weekday_order)))
ax.set_xticklabels([f'{m}月' for m in valid_months_all])
ax.set_yticklabels(weekday_order)

for i in range(len(weekday_order)):
    for j in range(len(valid_months_all)):
        val = weekday_pivot.iloc[i, j] if j < len(weekday_pivot.columns) else np.nan
        if pd.notna(val):
            text_color = 'white' if abs(val) > 80 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', color=text_color, fontsize=9)

ax.set_title(f'曜日別・営業日当たり客数の前年比増減（2025年 - 2024年）', fontsize=14)
fig.colorbar(im, ax=ax, label='増減（人/日）')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'graph11_weekday_heatmap.png', dpi=150)
plt.close()
print("graph11_weekday_heatmap.png を作成しました")

# 図12: 平日vs土日比較（6月含む）
weekday_month_copy = weekday_month.copy()
weekday_month_copy['曜日タイプ'] = weekday_month_copy['曜日'].apply(lambda x: '土日' if x in ['土', '日'] else '平日')
daytype_contrib = weekday_month_copy[weekday_month_copy['月'].isin(valid_months_all)].groupby(['月', '曜日タイプ'])['差分_日当たり客数'].mean().reset_index()
daytype_pivot = daytype_contrib.pivot_table(index='月', columns='曜日タイプ', values='差分_日当たり客数')

fig, ax = plt.subplots(figsize=(14, 6))

x = np.arange(len(valid_months_all))
width = 0.35

weekday_values = [daytype_pivot.loc[m, '平日'] if m in daytype_pivot.index else 0 for m in valid_months_all]
weekend_values = [daytype_pivot.loc[m, '土日'] if m in daytype_pivot.index else 0 for m in valid_months_all]

bars1 = ax.bar(x - width/2, weekday_values, width, label='平日', color='#2980B9')
bars2 = ax.bar(x + width/2, weekend_values, width, label='土日', color='#C0392B')

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('営業日当たり客数の増減（人）', fontsize=12)
ax.set_title(f'平日vs土日の客数増減寄与（2025年 - 2024年）', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels([f'{m}月' for m in valid_months_all])
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
plt.savefig(OUTPUT_DIR / 'graph12_weekday_vs_weekend.png', dpi=150)
plt.close()
print("graph12_weekday_vs_weekend.png を作成しました")

# =========================================
# 図13: 曜日別・入店時刻別の平均滞在時間（フォント修正）
# =========================================
print("\n=== 図13: 曜日別・入店時刻別の平均滞在時間 ===")

VISITS_FILE_STAY = DATA_DIR / "visits_with_duration.csv"

# データ読み込み
stay_data = defaultdict(lambda: defaultdict(list))

with open(VISITS_FILE_STAY, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        duration = int(row["滞在時間_分"])
        weekday = row["曜日"]
        entry_time = row["入店時刻"]
        
        if duration > 120:
            continue
        
        try:
            dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
            hour = dt.hour
            stay_data[weekday][hour].append(duration)
        except:
            continue

weekday_order_stay = ["月", "火", "水", "木", "金", "土", "日"]
hours_stay = list(range(10, 23))

avg_stay_data = {}
for wd in weekday_order_stay:
    avg_stay_data[wd] = []
    for h in hours_stay:
        durations = stay_data[wd][h]
        if durations:
            avg_stay_data[wd].append(sum(durations) / len(durations))
        else:
            avg_stay_data[wd].append(None)

fig, ax = plt.subplots(figsize=(14, 7))

colors_stay = {
    "月": "#1976D2",
    "火": "#2196F3", 
    "水": "#42A5F5",
    "木": "#64B5F6",
    "金": "#90CAF9",
    "土": "#E53935",
    "日": "#FF7043"
}

markers_stay = {
    "月": "o", "火": "s", "水": "^", "木": "D", 
    "金": "v", "土": "o", "日": "s"
}

for wd in weekday_order_stay:
    y_values = avg_stay_data[wd]
    valid_x = [h for h, v in zip(hours_stay, y_values) if v is not None]
    valid_y = [v for v in y_values if v is not None]
    
    linewidth = 2.5 if wd in ["土", "日"] else 1.5
    ax.plot(valid_x, valid_y, marker=markers_stay[wd], label=wd, 
            color=colors_stay[wd], linewidth=linewidth, markersize=6)

ax.set_xlabel('入店時刻', fontsize=12)
ax.set_ylabel('平均滞在時間（分）', fontsize=12)
ax.set_title('曜日別・入店時刻別の平均滞在時間', fontsize=14)
ax.set_xticks(hours_stay)
ax.set_xticklabels([f"{h}:00" for h in hours_stay], rotation=45)
ax.legend(loc='upper right', title='曜日')
ax.grid(True, alpha=0.3)
ax.set_ylim(15, 45)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph13_duration_by_hour_weekday.png", dpi=150, bbox_inches='tight')
plt.close()
print("graph13_duration_by_hour_weekday.png を作成しました")

print("\n=== 全グラフ作成完了 ===")
