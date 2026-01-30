"""
Y2Y（Year over Year）分析スクリプト
飲食店の売上データを月ごとに集計し、客数・客単価・組数の推移をグラフ化
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUIバックエンドを使わない
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import argparse
import os
from pathlib import Path
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']

# --------------------------------------------
# CLI（互換維持 + スライド素材分割用フラグ）
# --------------------------------------------
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--store-root", default=None)
parser.add_argument("--input", default=None)
parser.add_argument("--out-dir", default=None)
parser.add_argument("--split-assets", action="store_true", help="複合グラフをスライド素材用に分割して出力する（デフォルトOFF）")
parser.add_argument("--assets-dir", default=None, help="分割素材の出力先（未指定なら <out_dir>/_slide_assets/）")
args, _ = parser.parse_known_args()

if args.store_root or args.input or args.out_dir:
    store_root = Path(args.store_root or ".").resolve()
    input_path = Path(args.input) if args.input else (store_root / "data" / "output" / "transformed_pos_data_eatin.csv")
    out_dir = Path(args.out_dir) if args.out_dir else (store_root / "charts" / "y2y")
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(out_dir)
else:
    # 互換維持（従来の相対パス前提）
    input_path = Path("../transformed_pos_data_eatin.csv")
    out_dir = Path(".").resolve()

assets_dir = Path(args.assets_dir).resolve() if args.assets_dir else (out_dir / "_slide_assets")
if args.split_assets:
    assets_dir.mkdir(parents=True, exist_ok=True)

def _split_4rows(img_path: Path, names: list[str]):
    img = Image.open(img_path)
    w, h = img.size
    row_h = h // 4
    boxes = [
        (0, 0, w, row_h),
        (0, row_h, w, row_h * 2),
        (0, row_h * 2, w, row_h * 3),
        (0, row_h * 3, w, h),
    ]
    for box, name in zip(boxes, names):
        img.crop(box).save(assets_dir / name)

# データ読み込み
df = pd.read_csv(input_path)

# 日付をdatetime型に変換
df['H.集計対象営業年月日'] = pd.to_datetime(df['H.集計対象営業年月日'])

# 年月を抽出
df['年月'] = df['H.集計対象営業年月日'].dt.to_period('M')
df['年'] = df['H.集計対象営業年月日'].dt.year
df['月'] = df['H.集計対象営業年月日'].dt.month

# 伝票単位でユニークにする（1伝票1行に集約）
# 各伝票の情報は最初の行から取得
df_tickets = df.drop_duplicates(subset=['H.伝票番号'])[['H.伝票番号', 'H.集計対象営業年月日', 'H.客数（合計）', 'H.小計', '年月', '年', '月']].copy()

# 日別に集計（営業日数カウント用）
daily_stats = df_tickets.groupby('H.集計対象営業年月日').agg({
    'H.小計': 'sum'
}).reset_index()
daily_stats.columns = ['日付', '売上']

# 売上が0より大きい日を営業日とする
daily_stats['営業日'] = daily_stats['売上'] > 0
daily_stats['年月'] = pd.to_datetime(daily_stats['日付']).dt.to_period('M')

# 月ごとの営業日数を計算
operating_days = daily_stats[daily_stats['営業日']].groupby('年月').size().reset_index(name='営業日数')

# 月ごとに集計
monthly_stats = df_tickets.groupby('年月').agg({
    'H.客数（合計）': 'sum',      # 総客数
    'H.小計': 'sum',              # 総売上
    'H.伝票番号': 'nunique'       # 組数（ユニークな伝票数）
}).reset_index()

monthly_stats.columns = ['年月', '客数', '売上', '組数']

# 営業日数をマージ
monthly_stats = monthly_stats.merge(operating_days, on='年月', how='left')

# 営業日あたりの指標を計算
monthly_stats['売上/営業日'] = monthly_stats['売上'] / monthly_stats['営業日数']
monthly_stats['客数/営業日'] = monthly_stats['客数'] / monthly_stats['営業日数']
monthly_stats['組数/営業日'] = monthly_stats['組数'] / monthly_stats['営業日数']

monthly_stats['客単価'] = monthly_stats['売上'] / monthly_stats['客数']
monthly_stats['組単価'] = monthly_stats['売上'] / monthly_stats['組数']

# 年月を日付型に変換（グラフ表示用）
monthly_stats['日付'] = monthly_stats['年月'].dt.to_timestamp()

print("=== 月別集計データ ===")
print(monthly_stats.to_string())
print()

# CSVに保存
monthly_stats.to_csv('monthly_stats.csv', index=False, encoding='utf-8-sig')
print("月別集計データを monthly_stats.csv に保存しました")

# グラフ作成
fig, axes = plt.subplots(4, 1, figsize=(14, 16))

# カラーパレット
colors = {'main': '#2E86AB', 'accent': '#A23B72', 'highlight': '#F18F01', 'sales': '#28A745'}

# 1. 売上の推移
ax0 = axes[0]
bars0 = ax0.bar(monthly_stats['日付'], monthly_stats['売上'] / 10000, color=colors['sales'], alpha=0.8, width=25)
ax0.set_ylabel('売上（万円）', fontsize=12)
ax0.set_title('月別 売上推移', fontsize=14, fontweight='bold', pad=10)
ax0.tick_params(axis='x', rotation=45)
ax0.grid(axis='y', linestyle='--', alpha=0.7)

# 年の境界線を追加
for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax0.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax0.text(year_start, ax0.get_ylim()[1]*0.95, f'{year}年', fontsize=10, color='red', ha='center')

# 2. 客数の推移
ax1 = axes[1]
bars1 = ax1.bar(monthly_stats['日付'], monthly_stats['客数'], color=colors['main'], alpha=0.8, width=25)
ax1.set_ylabel('客数（人）', fontsize=12)
ax1.set_title('月別 客数推移', fontsize=14, fontweight='bold', pad=10)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 年の境界線を追加
for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax1.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax1.text(year_start, ax1.get_ylim()[1]*0.95, f'{year}年', fontsize=10, color='red', ha='center')

# 3. 客単価の推移
ax2 = axes[2]
ax2.plot(monthly_stats['日付'], monthly_stats['客単価'], marker='o', markersize=6, 
         color=colors['accent'], linewidth=2, label='客単価')
ax2.fill_between(monthly_stats['日付'], monthly_stats['客単価'], alpha=0.2, color=colors['accent'])
ax2.set_ylabel('客単価（円）', fontsize=12)
ax2.set_title('月別 客単価推移', fontsize=14, fontweight='bold', pad=10)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 年の境界線を追加
for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax2.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax2.text(year_start, ax2.get_ylim()[1]*0.98, f'{year}年', fontsize=10, color='red', ha='center')

# 4. 組数の推移
ax3 = axes[3]
bars3 = ax3.bar(monthly_stats['日付'], monthly_stats['組数'], color=colors['highlight'], alpha=0.8, width=25)
ax3.set_ylabel('組数', fontsize=12)
ax3.set_title('月別 組数推移', fontsize=14, fontweight='bold', pad=10)
ax3.tick_params(axis='x', rotation=45)
ax3.grid(axis='y', linestyle='--', alpha=0.7)

# 年の境界線を追加
for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax3.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax3.text(year_start, ax3.get_ylim()[1]*0.95, f'{year}年', fontsize=10, color='red', ha='center')

plt.tight_layout()
plt.savefig('monthly_trends.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("グラフを monthly_trends.png に保存しました")

# === 営業日あたりの指標グラフ（標準化版） ===
fig_norm, axes_norm = plt.subplots(4, 1, figsize=(14, 16))

# 1. 売上/営業日の推移
ax0 = axes_norm[0]
bars0 = ax0.bar(monthly_stats['日付'], monthly_stats['売上/営業日'] / 10000, color=colors['sales'], alpha=0.8, width=25)
ax0.set_ylabel('売上/営業日（万円）', fontsize=12)
ax0.set_title('月別 売上推移（営業日あたり）', fontsize=14, fontweight='bold', pad=10)
ax0.tick_params(axis='x', rotation=45)
ax0.grid(axis='y', linestyle='--', alpha=0.7)

for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax0.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax0.text(year_start, ax0.get_ylim()[1]*0.95, f'{year}年', fontsize=10, color='red', ha='center')

# 2. 客数/営業日の推移
ax1 = axes_norm[1]
bars1 = ax1.bar(monthly_stats['日付'], monthly_stats['客数/営業日'], color=colors['main'], alpha=0.8, width=25)
ax1.set_ylabel('客数/営業日（人）', fontsize=12)
ax1.set_title('月別 客数推移（営業日あたり）', fontsize=14, fontweight='bold', pad=10)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax1.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax1.text(year_start, ax1.get_ylim()[1]*0.95, f'{year}年', fontsize=10, color='red', ha='center')

# 3. 客単価の推移（これは元のまま）
ax2 = axes_norm[2]
ax2.plot(monthly_stats['日付'], monthly_stats['客単価'], marker='o', markersize=6, 
         color=colors['accent'], linewidth=2, label='客単価')
ax2.fill_between(monthly_stats['日付'], monthly_stats['客単価'], alpha=0.2, color=colors['accent'])
ax2.set_ylabel('客単価（円）', fontsize=12)
ax2.set_title('月別 客単価推移', fontsize=14, fontweight='bold', pad=10)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax2.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax2.text(year_start, ax2.get_ylim()[1]*0.98, f'{year}年', fontsize=10, color='red', ha='center')

# 4. 組数/営業日の推移
ax3 = axes_norm[3]
bars3 = ax3.bar(monthly_stats['日付'], monthly_stats['組数/営業日'], color=colors['highlight'], alpha=0.8, width=25)
ax3.set_ylabel('組数/営業日', fontsize=12)
ax3.set_title('月別 組数推移（営業日あたり）', fontsize=14, fontweight='bold', pad=10)
ax3.tick_params(axis='x', rotation=45)
ax3.grid(axis='y', linestyle='--', alpha=0.7)

for year in [2025, 2026]:
    year_start = pd.Timestamp(f'{year}-01-01')
    if year_start >= monthly_stats['日付'].min() and year_start <= monthly_stats['日付'].max():
        ax3.axvline(x=year_start, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax3.text(year_start, ax3.get_ylim()[1]*0.95, f'{year}年', fontsize=10, color='red', ha='center')

plt.tight_layout()
plt.savefig('monthly_trends_normalized.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("営業日標準化グラフを monthly_trends_normalized.png に保存しました")

if args.split_assets:
    _split_4rows(
        Path("monthly_trends_normalized.png"),
        [
            "monthly_trends_normalized__sales_per_day.png",
            "monthly_trends_normalized__customers_per_day.png",
            "monthly_trends_normalized__unit_price.png",
            "monthly_trends_normalized__groups_per_day.png",
        ],
    )

# === 年比較の詳細分析 ===
print("\n=== 年別サマリー ===")
df_tickets['年'] = df_tickets['H.集計対象営業年月日'].dt.year

yearly_stats = df_tickets.groupby('年').agg({
    'H.客数（合計）': 'sum',
    'H.小計': 'sum',
    'H.伝票番号': 'nunique'
}).reset_index()
yearly_stats.columns = ['年', '客数', '売上', '組数']
yearly_stats['客単価'] = yearly_stats['売上'] / yearly_stats['客数']
yearly_stats['組単価'] = yearly_stats['売上'] / yearly_stats['組数']
yearly_stats['客数/組'] = yearly_stats['客数'] / yearly_stats['組数']

print(yearly_stats.to_string())

# 同月比較用のデータ作成
monthly_stats['年'] = monthly_stats['年月'].dt.year
monthly_stats['月のみ'] = monthly_stats['年月'].dt.month

# 2024年と2025年の同月比較
comparison = monthly_stats.pivot_table(index='月のみ', columns='年', values=['客数', '客単価', '組数'])
print("\n=== 月別年比較 ===")
print(comparison.to_string())

# 年比較グラフ（同じ月を並べて比較）
fig2, axes2 = plt.subplots(4, 1, figsize=(14, 16))

years = sorted(monthly_stats['年'].unique())
months = range(1, 13)
month_labels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

# 年ごとの色
year_colors = {2024: '#2E86AB', 2025: '#A23B72', 2026: '#F18F01'}
x = np.arange(12)
width = 0.25

# 1. 売上の年比較
ax0 = axes2[0]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['売上']
    values = [year_data.get(m, 0) / 10000 for m in months]  # 万円単位
    ax0.bar(x + i*width, values, width, label=f'{year}年', color=year_colors.get(year, 'gray'), alpha=0.8)
ax0.set_xlabel('月')
ax0.set_ylabel('売上（万円）')
ax0.set_title('売上 年比較（同月比較）', fontsize=14, fontweight='bold')
ax0.set_xticks(x + width)
ax0.set_xticklabels(month_labels)
ax0.legend()
ax0.grid(axis='y', linestyle='--', alpha=0.7)

# 2. 客数の年比較
ax1 = axes2[1]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['客数']
    values = [year_data.get(m, 0) for m in months]
    ax1.bar(x + i*width, values, width, label=f'{year}年', color=year_colors.get(year, 'gray'), alpha=0.8)
ax1.set_xlabel('月')
ax1.set_ylabel('客数（人）')
ax1.set_title('客数 年比較（同月比較）', fontsize=14, fontweight='bold')
ax1.set_xticks(x + width)
ax1.set_xticklabels(month_labels)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 3. 客単価の年比較
ax2 = axes2[2]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['客単価']
    values = [year_data.get(m, np.nan) for m in months]
    ax2.plot(x, values, marker='o', markersize=8, label=f'{year}年', color=year_colors.get(year, 'gray'), linewidth=2)
ax2.set_xlabel('月')
ax2.set_ylabel('客単価（円）')
ax2.set_title('客単価 年比較（同月比較）', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(month_labels)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 4. 組数の年比較
ax3 = axes2[3]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['組数']
    values = [year_data.get(m, 0) for m in months]
    ax3.bar(x + i*width, values, width, label=f'{year}年', color=year_colors.get(year, 'gray'), alpha=0.8)
ax3.set_xlabel('月')
ax3.set_ylabel('組数')
ax3.set_title('組数 年比較（同月比較）', fontsize=14, fontweight='bold')
ax3.set_xticks(x + width)
ax3.set_xticklabels(month_labels)
ax3.legend()
ax3.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('y2y_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("\n年比較グラフを y2y_comparison.png に保存しました")

# === 営業日標準化版の年比較グラフ ===
fig3, axes3 = plt.subplots(4, 1, figsize=(14, 16))

# 1. 売上/営業日の年比較
ax0 = axes3[0]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['売上/営業日']
    values = [year_data.get(m, 0) / 10000 for m in months]  # 万円単位
    ax0.bar(x + i*width, values, width, label=f'{year}年', color=year_colors.get(year, 'gray'), alpha=0.8)
ax0.set_xlabel('月')
ax0.set_ylabel('売上/営業日（万円）')
ax0.set_title('売上/営業日 年比較（同月比較）', fontsize=14, fontweight='bold')
ax0.set_xticks(x + width)
ax0.set_xticklabels(month_labels)
ax0.legend()
ax0.grid(axis='y', linestyle='--', alpha=0.7)

# 2. 客数/営業日の年比較
ax1 = axes3[1]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['客数/営業日']
    values = [year_data.get(m, 0) for m in months]
    ax1.bar(x + i*width, values, width, label=f'{year}年', color=year_colors.get(year, 'gray'), alpha=0.8)
ax1.set_xlabel('月')
ax1.set_ylabel('客数/営業日（人）')
ax1.set_title('客数/営業日 年比較（同月比較）', fontsize=14, fontweight='bold')
ax1.set_xticks(x + width)
ax1.set_xticklabels(month_labels)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 3. 客単価の年比較（元のまま）
ax2 = axes3[2]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['客単価']
    values = [year_data.get(m, np.nan) for m in months]
    ax2.plot(x, values, marker='o', markersize=8, label=f'{year}年', color=year_colors.get(year, 'gray'), linewidth=2)
ax2.set_xlabel('月')
ax2.set_ylabel('客単価（円）')
ax2.set_title('客単価 年比較（同月比較）', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(month_labels)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 4. 組数/営業日の年比較
ax3 = axes3[3]
for i, year in enumerate(years):
    year_data = monthly_stats[monthly_stats['年'] == year].set_index('月のみ')['組数/営業日']
    values = [year_data.get(m, 0) for m in months]
    ax3.bar(x + i*width, values, width, label=f'{year}年', color=year_colors.get(year, 'gray'), alpha=0.8)
ax3.set_xlabel('月')
ax3.set_ylabel('組数/営業日')
ax3.set_title('組数/営業日 年比較（同月比較）', fontsize=14, fontweight='bold')
ax3.set_xticks(x + width)
ax3.set_xticklabels(month_labels)
ax3.legend()
ax3.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('y2y_comparison_normalized.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("営業日標準化の年比較グラフを y2y_comparison_normalized.png に保存しました")

if args.split_assets:
    _split_4rows(
        Path("y2y_comparison_normalized.png"),
        [
            "y2y_comparison_normalized__sales_per_day.png",
            "y2y_comparison_normalized__customers_per_day.png",
            "y2y_comparison_normalized__unit_price.png",
            "y2y_comparison_normalized__groups_per_day.png",
        ],
    )

# 営業日数情報を表示
print("\n=== 月別営業日数 ===")
print(monthly_stats[['年月', '営業日数', '売上/営業日', '客数/営業日', '組数/営業日']].to_string())

# === ミッドポイント法による売上変化の要因分解 ===
print("\n=== 売上変化の要因分解（ミッドポイント法） ===")

# 前月との比較用データを準備
monthly_stats_sorted = monthly_stats.sort_values('日付').reset_index(drop=True)

# 要因分解を計算（月合計ベース）
decomposition = []
for i in range(1, len(monthly_stats_sorted)):
    current = monthly_stats_sorted.iloc[i]
    previous = monthly_stats_sorted.iloc[i-1]
    
    # 前月のデータ
    P0 = previous['客数']  # 前月客数
    A0 = previous['客単価']  # 前月客単価
    S0 = previous['売上']  # 前月売上
    
    # 当月のデータ
    P1 = current['客数']  # 当月客数
    A1 = current['客単価']  # 当月客単価
    S1 = current['売上']  # 当月売上
    
    # 売上差
    delta_S = S1 - S0
    
    # ミッドポイント法による要因分解
    # 客数要因寄与 = (P1 - P0) × (A1 + A0) / 2
    contrib_P = (P1 - P0) * (A1 + A0) / 2
    
    # 客単価要因寄与 = (A1 - A0) × (P1 + P0) / 2
    contrib_A = (A1 - A0) * (P1 + P0) / 2
    
    decomposition.append({
        '年月': current['年月'],
        '日付': current['日付'],
        '売上差': delta_S,
        '客数要因寄与': contrib_P,
        '客単価要因寄与': contrib_A,
        '検算': contrib_P + contrib_A,  # 売上差と一致するはず
        '前月売上': S0,
        '当月売上': S1,
        '前月客数': P0,
        '当月客数': P1,
        '前月客単価': A0,
        '当月客単価': A1
    })

decomp_df = pd.DataFrame(decomposition)

# === 営業日あたりで標準化した要因分解 ===
print("\n=== 売上変化の要因分解（営業日あたり・ミッドポイント法） ===")

decomposition_normalized = []
for i in range(1, len(monthly_stats_sorted)):
    current = monthly_stats_sorted.iloc[i]
    previous = monthly_stats_sorted.iloc[i-1]
    
    # 営業日数がNaNの場合はスキップ
    if pd.isna(current['営業日数']) or pd.isna(previous['営業日数']):
        continue
    if current['営業日数'] == 0 or previous['営業日数'] == 0:
        continue
    
    # 前月のデータ（営業日あたり）
    P0 = previous['客数/営業日']  # 前月客数/営業日
    A0 = previous['客単価']  # 前月客単価（これは既に1人あたり）
    S0 = previous['売上/営業日']  # 前月売上/営業日
    
    # 当月のデータ（営業日あたり）
    P1 = current['客数/営業日']  # 当月客数/営業日
    A1 = current['客単価']  # 当月客単価
    S1 = current['売上/営業日']  # 当月売上/営業日
    
    # 売上差（営業日あたり）
    delta_S = S1 - S0
    
    # ミッドポイント法による要因分解
    contrib_P = (P1 - P0) * (A1 + A0) / 2
    contrib_A = (A1 - A0) * (P1 + P0) / 2
    
    decomposition_normalized.append({
        '年月': current['年月'],
        '日付': current['日付'],
        '売上差/営業日': delta_S,
        '客数要因寄与': contrib_P,
        '客単価要因寄与': contrib_A,
        '検算': contrib_P + contrib_A,
        '前月売上/営業日': S0,
        '当月売上/営業日': S1,
        '前月客数/営業日': P0,
        '当月客数/営業日': P1,
        '前月客単価': A0,
        '当月客単価': A1,
        '前月営業日数': previous['営業日数'],
        '当月営業日数': current['営業日数']
    })

decomp_norm_df = pd.DataFrame(decomposition_normalized)

if len(decomp_norm_df) > 0:
    print(decomp_norm_df[['年月', '売上差/営業日', '客数要因寄与', '客単価要因寄与', '検算']].to_string())
    
    # 営業日標準化版CSVを保存
    decomp_norm_df.to_csv('sales_decomposition_normalized.csv', index=False, encoding='utf-8-sig')
    print("\n営業日標準化の要因分解データを sales_decomposition_normalized.csv に保存しました")
    
    # === 営業日標準化版の要因分解グラフ ===
    fig_norm_decomp, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(decomp_norm_df))
    width = 0.35
    
    # 棒グラフ（万円単位）
    bars1 = ax.bar(x - width/2, decomp_norm_df['客数要因寄与'] / 10000, width, 
                   label='客数要因寄与', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, decomp_norm_df['客単価要因寄与'] / 10000, width, 
                   label='客単価要因寄与', color='#A23B72', alpha=0.8)
    
    # 売上差を線で表示
    ax.plot(x, decomp_norm_df['売上差/営業日'] / 10000, marker='D', markersize=8, 
            color='#28A745', linewidth=2, label='売上差/営業日（合計）')
    
    # ゼロライン
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # 年の境界線
    for idx, row in enumerate(decomp_norm_df.itertuples()):
        if row.日付.month == 1:
            ax.axvline(x=idx - 0.5, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
            ax.text(idx, ax.get_ylim()[1]*0.95, f"{row.日付.year}年", 
                    fontsize=10, color='red', ha='center')
    
    ax.set_xlabel('月', fontsize=12)
    ax.set_ylabel('寄与額/営業日（万円）', fontsize=12)
    ax.set_title('売上変化の要因分解（前月比・営業日あたり・ミッドポイント法）', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([str(d.year) + '/' + str(d.month) for d in decomp_norm_df['日付']], rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('sales_decomposition_normalized.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("営業日標準化の要因分解グラフを sales_decomposition_normalized.png に保存しました")

# NaNを含む行を除外（2025年3月のデータなど）
decomp_df = decomp_df.dropna()

print(decomp_df[['年月', '売上差', '客数要因寄与', '客単価要因寄与', '検算']].to_string())

# 要因分解CSVを保存
decomp_df.to_csv('sales_decomposition.csv', index=False, encoding='utf-8-sig')
print("\n要因分解データを sales_decomposition.csv に保存しました")

# === 要因分解グラフ ===
fig4, ax = plt.subplots(figsize=(16, 8))

x = np.arange(len(decomp_df))
width = 0.35

# 棒グラフ
bars1 = ax.bar(x - width/2, decomp_df['客数要因寄与'] / 10000, width, 
               label='客数要因寄与', color='#2E86AB', alpha=0.8)
bars2 = ax.bar(x + width/2, decomp_df['客単価要因寄与'] / 10000, width, 
               label='客単価要因寄与', color='#A23B72', alpha=0.8)

# 売上差を線で表示
ax.plot(x, decomp_df['売上差'] / 10000, marker='D', markersize=8, 
        color='#28A745', linewidth=2, label='売上差（合計）')

# ゼロライン
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# 年の境界線
for i, row in decomp_df.iterrows():
    if row['日付'].month == 1:
        idx = decomp_df.index.get_loc(i)
        ax.axvline(x=idx - 0.5, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
        ax.text(idx, ax.get_ylim()[1]*0.95, f"{row['日付'].year}年", 
                fontsize=10, color='red', ha='center')

ax.set_xlabel('月', fontsize=12)
ax.set_ylabel('寄与額（万円）', fontsize=12)
ax.set_title('売上変化の要因分解（前月比・ミッドポイント法）', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([str(d.year) + '/' + str(d.month) for d in decomp_df['日付']], rotation=45, ha='right')
ax.legend(loc='upper left')
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('sales_decomposition.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("要因分解グラフを sales_decomposition.png に保存しました")

# === 年比較用の要因分解（同月前年比） ===
print("\n=== 売上変化の要因分解（前年同月比） ===")

# 年と月を抽出
decomp_yoy = []
for i, row in monthly_stats_sorted.iterrows():
    current_year = row['日付'].year
    current_month = row['日付'].month
    
    # 前年同月を探す
    prev_year_data = monthly_stats_sorted[
        (monthly_stats_sorted['日付'].dt.year == current_year - 1) & 
        (monthly_stats_sorted['日付'].dt.month == current_month)
    ]
    
    if len(prev_year_data) > 0:
        previous = prev_year_data.iloc[0]
        
        P0, A0, S0 = previous['客数'], previous['客単価'], previous['売上']
        P1, A1, S1 = row['客数'], row['客単価'], row['売上']
        
        delta_S = S1 - S0
        contrib_P = (P1 - P0) * (A1 + A0) / 2
        contrib_A = (A1 - A0) * (P1 + P0) / 2
        
        decomp_yoy.append({
            '年月': row['年月'],
            '日付': row['日付'],
            '月': current_month,
            '年': current_year,
            '売上差': delta_S,
            '客数要因寄与': contrib_P,
            '客単価要因寄与': contrib_A,
        })

decomp_yoy_df = pd.DataFrame(decomp_yoy)
decomp_yoy_df = decomp_yoy_df.dropna()

if len(decomp_yoy_df) > 0:
    print(decomp_yoy_df[['年月', '売上差', '客数要因寄与', '客単価要因寄与']].to_string())
    
    # 前年同月比のグラフ
    fig5, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(decomp_yoy_df))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, decomp_yoy_df['客数要因寄与'] / 10000, width, 
                   label='客数要因寄与', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, decomp_yoy_df['客単価要因寄与'] / 10000, width, 
                   label='客単価要因寄与', color='#A23B72', alpha=0.8)
    
    ax.plot(x, decomp_yoy_df['売上差'] / 10000, marker='D', markersize=8, 
            color='#28A745', linewidth=2, label='売上差（合計）')
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    ax.set_xlabel('月', fontsize=12)
    ax.set_ylabel('寄与額（万円）', fontsize=12)
    ax.set_title('売上変化の要因分解（前年同月比・ミッドポイント法）', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(row['年'])}/{int(row['月'])}月" for _, row in decomp_yoy_df.iterrows()], 
                       rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('sales_decomposition_yoy.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("\n前年同月比の要因分解グラフを sales_decomposition_yoy.png に保存しました")

# === 前年同月比の要因分解（営業日あたり） ===
print("\n=== 売上変化の要因分解（前年同月比・営業日あたり） ===")

decomp_yoy_norm = []
for i, row in monthly_stats_sorted.iterrows():
    current_year = row['日付'].year
    current_month = row['日付'].month
    
    # 営業日数がNaNの場合はスキップ
    if pd.isna(row['営業日数']) or row['営業日数'] == 0:
        continue
    
    # 前年同月を探す
    prev_year_data = monthly_stats_sorted[
        (monthly_stats_sorted['日付'].dt.year == current_year - 1) & 
        (monthly_stats_sorted['日付'].dt.month == current_month)
    ]
    
    if len(prev_year_data) > 0:
        previous = prev_year_data.iloc[0]
        
        # 前年の営業日数がNaNの場合はスキップ
        if pd.isna(previous['営業日数']) or previous['営業日数'] == 0:
            continue
        
        # 営業日あたりの指標で計算
        P0 = previous['客数/営業日']
        A0 = previous['客単価']
        S0 = previous['売上/営業日']
        
        P1 = row['客数/営業日']
        A1 = row['客単価']
        S1 = row['売上/営業日']
        
        delta_S = S1 - S0
        contrib_P = (P1 - P0) * (A1 + A0) / 2
        contrib_A = (A1 - A0) * (P1 + P0) / 2
        
        decomp_yoy_norm.append({
            '年月': row['年月'],
            '日付': row['日付'],
            '月': current_month,
            '年': current_year,
            '売上差/営業日': delta_S,
            '客数要因寄与': contrib_P,
            '客単価要因寄与': contrib_A,
            '当月営業日数': row['営業日数'],
            '前年営業日数': previous['営業日数']
        })

decomp_yoy_norm_df = pd.DataFrame(decomp_yoy_norm)

if len(decomp_yoy_norm_df) > 0:
    print(decomp_yoy_norm_df[['年月', '売上差/営業日', '客数要因寄与', '客単価要因寄与']].to_string())
    
    # 前年同月比（営業日あたり）のグラフ
    fig6, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(decomp_yoy_norm_df))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, decomp_yoy_norm_df['客数要因寄与'] / 10000, width, 
                   label='客数要因寄与', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, decomp_yoy_norm_df['客単価要因寄与'] / 10000, width, 
                   label='客単価要因寄与', color='#A23B72', alpha=0.8)
    
    ax.plot(x, decomp_yoy_norm_df['売上差/営業日'] / 10000, marker='D', markersize=8, 
            color='#28A745', linewidth=2, label='売上差/営業日（合計）')
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    ax.set_xlabel('月', fontsize=12)
    ax.set_ylabel('寄与額/営業日（万円）', fontsize=12)
    ax.set_title('売上変化の要因分解（前年同月比・営業日あたり・ミッドポイント法）', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(row['年'])}/{int(row['月'])}月" for _, row in decomp_yoy_norm_df.iterrows()], 
                       rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('sales_decomposition_yoy_normalized.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("\n前年同月比（営業日あたり）の要因分解グラフを sales_decomposition_yoy_normalized.png に保存しました")

print("\n処理完了！")
