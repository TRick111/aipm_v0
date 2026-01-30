"""
THE BIFTEKI赤坂見附店 客単価上昇要因の包括的分析

目的:
- なぜ客単価が上昇したのか？
- どの部分が上昇したのか？
- 商品点数が増えたのか、商品単価が上がったのか？
- 高額顧客が増えたのか、全体が横にシフトしたのか？
- 特定の曜日や時間帯の客単価が上がっているのか？
- どのメニューが売上上昇に貢献したのか？
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定（macOS優先でフォールバック）
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("THE BIFTEKI赤坂見附店 客単価上昇要因の包括的分析")
print("=" * 80)

# データ読み込み
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_DIR / "data" / "output" / "transformed_pos_data_eatin.csv"
OUTPUT_DIR = PROJECT_DIR / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)
df['日付'] = pd.to_datetime(df['H.集計対象営業年月日'])
df['年月'] = df['日付'].dt.to_period('M')
df['曜日'] = df['H.曜日']

# 時間帯の抽出
df['伝票発行時刻'] = pd.to_datetime(df['H.伝票発行日'])
df['時間'] = df['伝票発行時刻'].dt.hour

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
# 1. 客単価の要因分解分析: 点数 × 単価
# ================================================================================
print("\n" + "=" * 80)
print("第1章: 客単価の要因分解分析")
print("客単価 = 一人当たり品数 × 平均商品単価")
print("=" * 80)

def calc_decomposition(df_period, period_name):
    """客単価の要因分解を計算"""
    receipt_df = df_period.groupby('H.伝票番号').agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first',
        'D.価格': ['sum', 'count', 'mean']
    }).reset_index()

    receipt_df.columns = ['伝票番号', '小計', '客数', '総額', '商品数', '平均商品単価_伝票']
    receipt_df = receipt_df[receipt_df['客数'] > 0].copy()

    receipt_df['客単価'] = receipt_df['小計'] / receipt_df['客数']
    receipt_df['一人当たり品数'] = receipt_df['商品数'] / receipt_df['客数']

    # 全体の平均を計算
    total_sales = receipt_df['小計'].sum()
    total_customers = receipt_df['客数'].sum()
    total_items = receipt_df['商品数'].sum()

    avg_customer_price = total_sales / total_customers
    avg_items_per_person = total_items / total_customers
    avg_item_price = total_sales / total_items

    print(f"\n【{period_name}】")
    print(f"  客単価: {avg_customer_price:.0f}円")
    print(f"  一人当たり品数: {avg_items_per_person:.2f}品")
    print(f"  平均商品単価: {avg_item_price:.0f}円")
    print(f"  検算: {avg_items_per_person:.2f} × {avg_item_price:.0f} = {avg_items_per_person * avg_item_price:.0f}円")

    return {
        '客単価': avg_customer_price,
        '一人当たり品数': avg_items_per_person,
        '平均商品単価': avg_item_price,
        '伝票データ': receipt_df
    }

result_a = calc_decomposition(df_period_a, '期間A (5-7月)')
result_b = calc_decomposition(df_period_b, '期間B (10-12月)')

# 変化の分析
customer_price_change = result_b['客単価'] - result_a['客単価']
items_change = result_b['一人当たり品数'] - result_a['一人当たり品数']
price_change = result_b['平均商品単価'] - result_a['平均商品単価']

print(f"\n【変化】")
print(f"  客単価の変化: {customer_price_change:+.0f}円 ({customer_price_change/result_a['客単価']*100:+.1f}%)")
print(f"  一人当たり品数の変化: {items_change:+.3f}品 ({items_change/result_a['一人当たり品数']*100:+.1f}%)")
print(f"  平均商品単価の変化: {price_change:+.0f}円 ({price_change/result_a['平均商品単価']*100:+.1f}%)")

# 要因分解（寄与度分析）
# 客単価変化 ≈ (品数変化 × 期間Aの単価) + (単価変化 × 期間Bの品数)
contribution_items = items_change * result_a['平均商品単価']
contribution_price = price_change * result_b['一人当たり品数']

print(f"\n【要因分解: 客単価変化 {customer_price_change:+.0f}円の内訳】")
print(f"  (1) 一人当たり品数の変化による寄与: {contribution_items:+.0f}円")
print(f"  (2) 平均商品単価の変化による寄与: {contribution_price:+.0f}円")
print(f"  合計（近似値）: {contribution_items + contribution_price:+.0f}円")

print(f"\n【結論】")
if abs(contribution_price) > abs(contribution_items):
    print(f"  → 客単価上昇の主要因は「平均商品単価の上昇」({contribution_price:+.0f}円)")
    print(f"     一人当たり品数の寄与は小さい({contribution_items:+.0f}円)")
else:
    print(f"  → 客単価上昇の主要因は「一人当たり品数の増加」({contribution_items:+.0f}円)")

# グラフ作成
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('客単価の要因分解分析', fontsize=14, fontweight='bold')

# 各指標の比較
metrics = ['客単価', '一人当たり品数', '平均商品単価']
values_a = [result_a['客単価'], result_a['一人当たり品数'], result_a['平均商品単価']]
values_b = [result_b['客単価'], result_b['一人当たり品数'], result_b['平均商品単価']]
changes = [customer_price_change, items_change, price_change]
change_rates = [customer_price_change/result_a['客単価']*100,
                items_change/result_a['一人当たり品数']*100,
                price_change/result_a['平均商品単価']*100]

for i, (ax, metric) in enumerate(zip(axes, metrics)):
    x = [0, 1]
    y = [values_a[i], values_b[i]]

    ax.bar(x, y, color=['steelblue', 'coral'], alpha=0.7, width=0.6)
    ax.plot(x, y, 'ko-', linewidth=2, markersize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(['期間A\n(5-7月)', '期間B\n(10-12月)'])
    ax.set_title(f'{metric}', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # 変化量を表示
    mid_x = 0.5
    mid_y = (y[0] + y[1]) / 2
    ax.annotate(f'{changes[i]:+.2f}\n({change_rates[i]:+.1f}%)',
                xy=(mid_x, mid_y), fontsize=11, ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '01_decomposition_analysis.png', dpi=300, bbox_inches='tight')
print("\n[OK] 要因分解グラフを保存: 01_decomposition_analysis.png")

# ================================================================================
# 2. 分布分析: 全体シフト vs 高額層増加
# ================================================================================
print("\n" + "=" * 80)
print("第2章: 分布分析 - 全体シフト vs 高額層増加")
print("=" * 80)

receipt_a = result_a['伝票データ']
receipt_b = result_b['伝票データ']

print(f"\n【分布の基本統計】")
print(f"期間A:")
print(f"  平均: {receipt_a['客単価'].mean():.0f}円")
print(f"  中央値: {receipt_a['客単価'].median():.0f}円")
print(f"  標準偏差: {receipt_a['客単価'].std():.0f}円")
print(f"  25%タイル: {receipt_a['客単価'].quantile(0.25):.0f}円")
print(f"  75%タイル: {receipt_a['客単価'].quantile(0.75):.0f}円")

print(f"\n期間B:")
print(f"  平均: {receipt_b['客単価'].mean():.0f}円")
print(f"  中央値: {receipt_b['客単価'].median():.0f}円")
print(f"  標準偏差: {receipt_b['客単価'].std():.0f}円")
print(f"  25%タイル: {receipt_b['客単価'].quantile(0.25):.0f}円")
print(f"  75%タイル: {receipt_b['客単価'].quantile(0.75):.0f}円")

# パーセンタイル別の変化
percentiles = [10, 25, 50, 75, 90, 95]
print(f"\n【パーセンタイル別の客単価】")
print(f"{'パーセンタイル':<12} {'期間A':<10} {'期間B':<10} {'変化':<10} {'変化率'}")
for p in percentiles:
    val_a = receipt_a['客単価'].quantile(p/100)
    val_b = receipt_b['客単価'].quantile(p/100)
    change = val_b - val_a
    change_rate = change / val_a * 100
    print(f"{p}%ile{'':<7} {val_a:>8.0f}円  {val_b:>8.0f}円  {change:>8.0f}円  {change_rate:>6.1f}%")

print(f"\n【結論】")
print(f"  → 25%タイルの変化: {receipt_b['客単価'].quantile(0.25) - receipt_a['客単価'].quantile(0.25):+.0f}円 ({(receipt_b['客単価'].quantile(0.25)/receipt_a['客単価'].quantile(0.25)-1)*100:+.1f}%)")
print(f"  → 50%タイル（中央値）の変化: {receipt_b['客単価'].median() - receipt_a['客単価'].median():+.0f}円 ({(receipt_b['客単価'].median()/receipt_a['客単価'].median()-1)*100:+.1f}%)")
print(f"  → 75%タイルの変化: {receipt_b['客単価'].quantile(0.75) - receipt_a['客単価'].quantile(0.75):+.0f}円 ({(receipt_b['客単価'].quantile(0.75)/receipt_a['客単価'].quantile(0.75)-1)*100:+.1f}%)")
print(f"  → 95%タイルの変化: {receipt_b['客単価'].quantile(0.95) - receipt_a['客単価'].quantile(0.95):+.0f}円 ({(receipt_b['客単価'].quantile(0.95)/receipt_a['客単価'].quantile(0.95)-1)*100:+.1f}%)")

if (receipt_b['客単価'].quantile(0.95) - receipt_a['客単価'].quantile(0.95)) > (receipt_b['客単価'].median() - receipt_a['客単価'].median()) * 2:
    print(f"\n  → 高額層（上位5%）の上昇が中央値の上昇より大きい")
    print(f"     = 「高額顧客の増加」と「全体シフト」の両方が起きている")
else:
    print(f"\n  → 全体的に均等に上昇している = 「分布全体の横シフト」")

# 分布の可視化
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('客単価分布の詳細分析', fontsize=16, fontweight='bold')

# ヒストグラム（重ね合わせ）
ax1 = axes[0, 0]
bins = np.arange(0, 6000, 100)
ax1.hist(receipt_a['客単価'], bins=bins, alpha=0.5, label='期間A (5-7月)', color='steelblue', edgecolor='black')
ax1.hist(receipt_b['客単価'], bins=bins, alpha=0.5, label='期間B (10-12月)', color='coral', edgecolor='black')
ax1.axvline(receipt_a['客単価'].mean(), color='blue', linestyle='--', linewidth=2, label=f'期間A平均: {receipt_a["客単価"].mean():.0f}円')
ax1.axvline(receipt_b['客単価'].mean(), color='red', linestyle='--', linewidth=2, label=f'期間B平均: {receipt_b["客単価"].mean():.0f}円')
ax1.axvline(receipt_a['客単価'].median(), color='blue', linestyle=':', linewidth=2, label=f'期間A中央値: {receipt_a["客単価"].median():.0f}円')
ax1.axvline(receipt_b['客単価'].median(), color='red', linestyle=':', linewidth=2, label=f'期間B中央値: {receipt_b["客単価"].median():.0f}円')
ax1.set_xlabel('客単価（円）', fontsize=11)
ax1.set_ylabel('伝票数', fontsize=11)
ax1.set_title('客単価分布（ヒストグラム）', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 5000)

# 累積分布
ax2 = axes[0, 1]
sorted_a = np.sort(receipt_a['客単価'])
sorted_b = np.sort(receipt_b['客単価'])
cumulative_a = np.arange(1, len(sorted_a)+1) / len(sorted_a) * 100
cumulative_b = np.arange(1, len(sorted_b)+1) / len(sorted_b) * 100
ax2.plot(sorted_a, cumulative_a, linewidth=2, label='期間A (5-7月)', color='steelblue')
ax2.plot(sorted_b, cumulative_b, linewidth=2, label='期間B (10-12月)', color='coral')
ax2.set_xlabel('客単価（円）', fontsize=11)
ax2.set_ylabel('累積割合（%）', fontsize=11)
ax2.set_title('客単価の累積分布', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 5000)

# パーセンタイル比較
ax3 = axes[1, 0]
percentile_labels = ['10%', '25%', '50%\n(中央値)', '75%', '90%', '95%']
percentile_values_a = [receipt_a['客単価'].quantile(p/100) for p in percentiles]
percentile_values_b = [receipt_b['客単価'].quantile(p/100) for p in percentiles]
x = np.arange(len(percentiles))
width = 0.35
ax3.bar(x - width/2, percentile_values_a, width, label='期間A (5-7月)', color='steelblue', alpha=0.7)
ax3.bar(x + width/2, percentile_values_b, width, label='期間B (10-12月)', color='coral', alpha=0.7)
ax3.set_xticks(x)
ax3.set_xticklabels(percentile_labels)
ax3.set_ylabel('客単価（円）', fontsize=11)
ax3.set_title('パーセンタイル別客単価', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 箱ひげ図
ax4 = axes[1, 1]
box_data = [receipt_a['客単価'], receipt_b['客単価']]
bp = ax4.boxplot(box_data, labels=['期間A\n(5-7月)', '期間B\n(10-12月)'], patch_artist=True,
                 showmeans=True, meanline=True)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('lightcoral')
ax4.set_ylabel('客単価（円）', fontsize=11)
ax4.set_title('客単価の箱ひげ図', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '02_distribution_analysis.png', dpi=300, bbox_inches='tight')
print("\n[OK] 分布分析グラフを保存: 02_distribution_analysis.png")

# ================================================================================
# 3. 曜日別・時間帯別分析
# ================================================================================
print("\n" + "=" * 80)
print("第3章: 曜日別・時間帯別分析")
print("=" * 80)

# 曜日別分析
def analyze_by_weekday(df_period, period_name):
    """曜日別の客単価を分析"""
    receipt_df = df_period.groupby(['H.伝票番号', '曜日']).agg({
        'H.小計': 'first',
        'H.客数（合計）': 'first'
    }).reset_index()
    receipt_df = receipt_df[receipt_df['H.客数（合計）'] > 0].copy()
    receipt_df['客単価'] = receipt_df['H.小計'] / receipt_df['H.客数（合計）']

    weekday_summary = receipt_df.groupby('曜日').agg({
        '客単価': ['mean', 'median', 'count']
    }).reset_index()
    weekday_summary.columns = ['曜日', '平均客単価', '中央値客単価', '伝票数']

    # 曜日の順序を設定
    weekday_order = ['月', '火', '水', '木', '金', '土', '日']
    weekday_summary['曜日'] = pd.Categorical(weekday_summary['曜日'], categories=weekday_order, ordered=True)
    weekday_summary = weekday_summary.sort_values('曜日')

    return weekday_summary

weekday_a = analyze_by_weekday(df_period_a, '期間A')
weekday_b = analyze_by_weekday(df_period_b, '期間B')

print(f"\n【曜日別客単価】")
weekday_comp = weekday_a[['曜日', '平均客単価', '伝票数']].merge(
    weekday_b[['曜日', '平均客単価', '伝票数']],
    on='曜日',
    suffixes=('_A', '_B')
)
weekday_comp['客単価変化'] = weekday_comp['平均客単価_B'] - weekday_comp['平均客単価_A']
weekday_comp['客単価変化率'] = (weekday_comp['平均客単価_B'] / weekday_comp['平均客単価_A'] - 1) * 100

print(weekday_comp.round(1).to_string(index=False))

max_increase_day = weekday_comp.loc[weekday_comp['客単価変化'].idxmax(), '曜日']
max_increase = weekday_comp['客単価変化'].max()

print(f"\n【結論】")
print(f"  → 最も客単価が上昇した曜日: {max_increase_day}曜日 ({max_increase:+.0f}円)")
print(f"  → 全曜日で上昇している場合、全般的な価格上昇。特定曜日のみの場合、その曜日の客層変化")

# 時間帯別分析
def analyze_by_hour(df_period, period_name):
    """時間帯別の客単価を分析"""
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

hour_a = analyze_by_hour(df_period_a, '期間A')
hour_b = analyze_by_hour(df_period_b, '期間B')

print(f"\n【時間帯別客単価（主要時間帯のみ）】")
hour_comp = hour_a.merge(hour_b, on='時間', suffixes=('_A', '_B'))
hour_comp['客単価変化'] = hour_comp['平均客単価_B'] - hour_comp['平均客単価_A']
hour_comp = hour_comp[hour_comp['伝票数_A'] >= 10]  # 伝票数が少ない時間帯は除外

print(hour_comp.round(1).to_string(index=False))

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
colors = ['red' if x > 0 else 'blue' for x in weekday_comp['客単価変化']]
ax2.bar(weekday_comp['曜日'], weekday_comp['客単価変化'], color=colors, alpha=0.7)
ax2.set_ylabel('客単価変化（円）', fontsize=11)
ax2.set_title('曜日別客単価変化', fontsize=12, fontweight='bold')
ax2.axhline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y')

# 時間帯別客単価
ax3 = axes[1, 0]
ax3.plot(hour_comp['時間'], hour_comp['平均客単価_A'], 'o-', linewidth=2, markersize=6, label='期間A (5-7月)', color='steelblue')
ax3.plot(hour_comp['時間'], hour_comp['平均客単価_B'], 's-', linewidth=2, markersize=6, label='期間B (10-12月)', color='coral')
ax3.set_xlabel('時間', fontsize=11)
ax3.set_ylabel('平均客単価（円）', fontsize=11)
ax3.set_title('時間帯別平均客単価', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xticks(range(0, 24, 2))

# 時間帯別伝票数
ax4 = axes[1, 1]
ax4.bar(hour_comp['時間'], hour_comp['伝票数_A'], alpha=0.5, label='期間A (5-7月)', color='steelblue')
ax4.bar(hour_comp['時間'], hour_comp['伝票数_B'], alpha=0.5, label='期間B (10-12月)', color='coral')
ax4.set_xlabel('時間', fontsize=11)
ax4.set_ylabel('伝票数', fontsize=11)
ax4.set_title('時間帯別伝票数', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '03_weekday_hour_analysis.png', dpi=300, bbox_inches='tight')
print("\n[OK] 曜日・時間帯分析グラフを保存: 03_weekday_hour_analysis.png")

print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
print("\n生成されたファイル:")
print("  1. 01_decomposition_analysis.png - 客単価の要因分解")
print("  2. 02_distribution_analysis.png - 分布分析")
print("  3. 03_weekday_hour_analysis.png - 曜日・時間帯分析")
print("\n次のスクリプトでメニュー貢献度分析を実施します...")
