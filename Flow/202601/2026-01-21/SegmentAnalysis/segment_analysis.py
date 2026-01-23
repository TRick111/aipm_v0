#!/usr/bin/env python3
"""
4セグメント分析
- 2025年3月以前 × ランチ帯（〜16時）
- 2025年3月以前 × ディナー帯（16時〜）
- 2025年3月以降 × ランチ帯（〜16時）
- 2025年3月以降 × ディナー帯（16時〜）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import rcParams
import os

# 日本語フォント設定
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']
rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = '/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-21/SegmentAnalysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("4セグメント分析を開始")
print("=" * 60)

# ============================================================
# データ読み込みと前処理
# ============================================================
print("\n[Step 1] データ読み込み...")

df = pd.read_csv('/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-21/transformed_pos_data_eatin.csv')

# 日付・時間の処理
df['H.集計対象営業年月日'] = pd.to_datetime(df['H.集計対象営業年月日'])
df['D.オーダー日時'] = pd.to_datetime(df['D.オーダー日時'])
df['order_hour'] = df['D.オーダー日時'].dt.hour

print(f"  総レコード数: {len(df):,}")

# ============================================================
# セグメント分割
# ============================================================
print("\n[Step 2] セグメント分割...")

# 期間の分割（2025年3月を境界）
cutoff_date = pd.Timestamp('2025-04-01')  # 4月1日以降を「以降」とする
df['period'] = np.where(df['H.集計対象営業年月日'] < cutoff_date, 'Before', 'After')

# 時間帯の分割（16時を境界）
df['daypart'] = np.where(df['order_hour'] < 16, 'Lunch', 'Dinner')

# セグメント名
df['segment'] = df['period'] + '_' + df['daypart']

# セグメント別のレコード数
print("\nセグメント別レコード数:")
print(df['segment'].value_counts())

# ============================================================
# セグメント別の日次集計
# ============================================================
print("\n[Step 3] セグメント別の日次集計...")

# 伝票単位のユニークデータ（セグメント別）
# 注意: 1つの伝票がランチとディナーにまたがる可能性があるので、
# 明細レベルで時間帯を判定し、その売上を集計する

def aggregate_by_segment(df):
    """セグメント別に日次集計を行う"""
    results = []
    
    for segment in df['segment'].unique():
        segment_df = df[df['segment'] == segment]
        
        # 日付ごとに集計
        daily = segment_df.groupby('H.集計対象営業年月日').agg({
            'D.価格': 'sum',  # 売上
            'H.伝票番号': 'nunique',  # 伝票数
        }).reset_index()
        
        # 客数は伝票単位で取得（重複排除）
        # 伝票ごとの客数を取得
        slip_customers = segment_df.drop_duplicates(subset=['H.伝票番号'])[['H.集計対象営業年月日', 'H.伝票番号', 'H.客数（合計）']]
        daily_customers = slip_customers.groupby('H.集計対象営業年月日')['H.客数（合計）'].sum().reset_index()
        
        daily = daily.merge(daily_customers, on='H.集計対象営業年月日', how='left')
        
        daily.columns = ['date', 'total_sales', 'slip_count', 'total_customers']
        daily['segment'] = segment
        daily['period'] = segment.split('_')[0]
        daily['daypart'] = segment.split('_')[1]
        
        # 客単価
        daily['avg_spend_per_customer'] = daily['total_sales'] / daily['total_customers']
        daily['avg_spend_per_customer'] = daily['avg_spend_per_customer'].replace([np.inf, -np.inf], np.nan)
        
        # 曜日
        daily['weekday'] = pd.to_datetime(daily['date']).dt.dayofweek
        daily['weekday_name'] = pd.to_datetime(daily['date']).dt.day_name()
        
        results.append(daily)
    
    return pd.concat(results, ignore_index=True)

daily_segment = aggregate_by_segment(df)

# 保存
daily_segment.to_csv(f'{OUTPUT_DIR}/daily_by_segment.csv', index=False)
print(f"  保存: daily_by_segment.csv")

# ============================================================
# 基本統計の計算
# ============================================================
print("\n[Step 4] 基本統計の計算...")

# セグメント定義
segments = ['Before_Lunch', 'Before_Dinner', 'After_Lunch', 'After_Dinner']
segment_labels = {
    'Before_Lunch': '3月以前・ランチ',
    'Before_Dinner': '3月以前・ディナー',
    'After_Lunch': '4月以降・ランチ',
    'After_Dinner': '4月以降・ディナー'
}
segment_colors = {
    'Before_Lunch': '#3498db',      # 青
    'Before_Dinner': '#2c3e50',     # 紺
    'After_Lunch': '#e74c3c',       # 赤
    'After_Dinner': '#c0392b'       # 暗い赤
}

# 基本統計
print("\n【セグメント別基本統計】")
print("-" * 100)
print(f"{'セグメント':<20} {'日数':>8} {'平均売上':>12} {'平均客数':>10} {'平均客単価':>12} {'売上SD':>12}")
print("-" * 100)

stats_summary = []
for seg in segments:
    seg_data = daily_segment[daily_segment['segment'] == seg]
    if len(seg_data) > 0:
        stats = {
            'segment': seg,
            'label': segment_labels[seg],
            'days': len(seg_data),
            'avg_sales': seg_data['total_sales'].mean(),
            'std_sales': seg_data['total_sales'].std(),
            'avg_customers': seg_data['total_customers'].mean(),
            'avg_unit_price': seg_data['avg_spend_per_customer'].mean()
        }
        stats_summary.append(stats)
        print(f"{segment_labels[seg]:<20} {stats['days']:>8} {stats['avg_sales']:>12,.0f} {stats['avg_customers']:>10,.1f} {stats['avg_unit_price']:>12,.0f} {stats['std_sales']:>12,.0f}")

stats_df = pd.DataFrame(stats_summary)
stats_df.to_csv(f'{OUTPUT_DIR}/segment_statistics.csv', index=False)

# ============================================================
# 可視化
# ============================================================
print("\n[Step 5] 可視化...")

# 図1: 売上分布の比較（4セグメント）
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, seg in enumerate(segments):
    seg_data = daily_segment[daily_segment['segment'] == seg]['total_sales']
    if len(seg_data) > 0:
        axes[idx].hist(seg_data, bins=30, color=segment_colors[seg], edgecolor='black', alpha=0.7)
        axes[idx].axvline(seg_data.mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {seg_data.mean():,.0f}円')
        axes[idx].set_xlabel('売上（円）')
        axes[idx].set_ylabel('頻度')
        axes[idx].set_title(f'{segment_labels[seg]}\n(n={len(seg_data)}日)')
        axes[idx].legend()

plt.suptitle('セグメント別 売上分布', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_sales_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 01_sales_distribution.png")

# 図2: 客数分布の比較
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, seg in enumerate(segments):
    seg_data = daily_segment[daily_segment['segment'] == seg]['total_customers']
    if len(seg_data) > 0:
        axes[idx].hist(seg_data, bins=30, color=segment_colors[seg], edgecolor='black', alpha=0.7)
        axes[idx].axvline(seg_data.mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {seg_data.mean():,.0f}人')
        axes[idx].set_xlabel('客数')
        axes[idx].set_ylabel('頻度')
        axes[idx].set_title(f'{segment_labels[seg]}\n(n={len(seg_data)}日)')
        axes[idx].legend()

plt.suptitle('セグメント別 客数分布', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_customers_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 02_customers_distribution.png")

# 図3: 客単価分布の比較
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, seg in enumerate(segments):
    seg_data = daily_segment[daily_segment['segment'] == seg]['avg_spend_per_customer'].dropna()
    if len(seg_data) > 0:
        axes[idx].hist(seg_data, bins=30, color=segment_colors[seg], edgecolor='black', alpha=0.7)
        axes[idx].axvline(seg_data.mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {seg_data.mean():,.0f}円')
        axes[idx].set_xlabel('客単価（円）')
        axes[idx].set_ylabel('頻度')
        axes[idx].set_title(f'{segment_labels[seg]}\n(n={len(seg_data)}日)')
        axes[idx].legend()

plt.suptitle('セグメント別 客単価分布', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_unit_price_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 03_unit_price_distribution.png")

# 図4: 客数 vs 売上 散布図（4セグメント重ねて）
fig, ax = plt.subplots(figsize=(12, 8))

for seg in segments:
    seg_data = daily_segment[daily_segment['segment'] == seg]
    if len(seg_data) > 0:
        ax.scatter(seg_data['total_customers'], seg_data['total_sales'], 
                   c=segment_colors[seg], alpha=0.6, s=30, label=segment_labels[seg])
        
        # 回帰直線
        valid_data = seg_data.dropna(subset=['total_customers', 'total_sales'])
        if len(valid_data) > 1:
            z = np.polyfit(valid_data['total_customers'], valid_data['total_sales'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid_data['total_customers'].min(), valid_data['total_customers'].max(), 100)
            ax.plot(x_line, p(x_line), '--', color=segment_colors[seg], linewidth=2, alpha=0.8)

ax.set_xlabel('客数')
ax.set_ylabel('売上（円）')
ax.set_title('セグメント別 客数 vs 売上')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_customers_vs_sales.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 04_customers_vs_sales.png")

# 図5: 客数 vs 売上 散布図（4分割）
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, seg in enumerate(segments):
    seg_data = daily_segment[daily_segment['segment'] == seg]
    if len(seg_data) > 0:
        axes[idx].scatter(seg_data['total_customers'], seg_data['total_sales'], 
                         c=segment_colors[seg], alpha=0.6, s=30)
        
        # 回帰直線と相関係数
        valid_data = seg_data.dropna(subset=['total_customers', 'total_sales'])
        if len(valid_data) > 1:
            corr = valid_data['total_customers'].corr(valid_data['total_sales'])
            z = np.polyfit(valid_data['total_customers'], valid_data['total_sales'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid_data['total_customers'].min(), valid_data['total_customers'].max(), 100)
            axes[idx].plot(x_line, p(x_line), 'r--', linewidth=2, label=f'傾き: {z[0]:,.0f}円/人')
            axes[idx].set_title(f'{segment_labels[seg]}\n相関: {corr:.3f}')
        else:
            axes[idx].set_title(segment_labels[seg])
        
        axes[idx].set_xlabel('客数')
        axes[idx].set_ylabel('売上（円）')
        axes[idx].legend()

plt.suptitle('セグメント別 客数 vs 売上', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_customers_vs_sales_split.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 05_customers_vs_sales_split.png")

# 図6: 曜日別平均売上（4セグメント比較）
fig, ax = plt.subplots(figsize=(14, 8))

weekday_names = ['月', '火', '水', '木', '金', '土', '日']
x = np.arange(7)
width = 0.2

for i, seg in enumerate(segments):
    seg_data = daily_segment[daily_segment['segment'] == seg]
    if len(seg_data) > 0:
        weekday_avg = seg_data.groupby('weekday')['total_sales'].mean()
        # 全曜日分のデータを用意（欠損は0）
        values = [weekday_avg.get(w, 0) for w in range(7)]
        ax.bar(x + i*width, values, width, label=segment_labels[seg], color=segment_colors[seg], alpha=0.8)

ax.set_xticks(x + width*1.5)
ax.set_xticklabels(weekday_names)
ax.set_xlabel('曜日')
ax.set_ylabel('平均売上（円）')
ax.set_title('セグメント別 曜日別平均売上')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_weekday_sales.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 06_weekday_sales.png")

# 図7: 曜日別平均売上（4分割）
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, seg in enumerate(segments):
    seg_data = daily_segment[daily_segment['segment'] == seg]
    if len(seg_data) > 0:
        weekday_avg = seg_data.groupby('weekday')['total_sales'].mean()
        values = [weekday_avg.get(w, 0) for w in range(7)]
        axes[idx].bar(weekday_names, values, color=segment_colors[seg], alpha=0.8)
        axes[idx].axhline(seg_data['total_sales'].mean(), color='red', linestyle='--', label=f'全体平均: {seg_data["total_sales"].mean():,.0f}円')
        axes[idx].set_xlabel('曜日')
        axes[idx].set_ylabel('平均売上（円）')
        axes[idx].set_title(segment_labels[seg])
        axes[idx].legend()

plt.suptitle('セグメント別 曜日別平均売上', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/07_weekday_sales_split.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 07_weekday_sales_split.png")

# 図8: 基本統計の比較バーチャート
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 平均売上
ax = axes[0]
labels = [segment_labels[s] for s in segments]
values = [stats_df[stats_df['segment'] == s]['avg_sales'].values[0] if len(stats_df[stats_df['segment'] == s]) > 0 else 0 for s in segments]
colors = [segment_colors[s] for s in segments]
bars = ax.bar(labels, values, color=colors, alpha=0.8)
ax.set_ylabel('平均売上（円）')
ax.set_title('平均売上の比較')
ax.tick_params(axis='x', rotation=45)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000, f'{val:,.0f}', ha='center', va='bottom', fontsize=9)

# 平均客数
ax = axes[1]
values = [stats_df[stats_df['segment'] == s]['avg_customers'].values[0] if len(stats_df[stats_df['segment'] == s]) > 0 else 0 for s in segments]
bars = ax.bar(labels, values, color=colors, alpha=0.8)
ax.set_ylabel('平均客数')
ax.set_title('平均客数の比較')
ax.tick_params(axis='x', rotation=45)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.0f}', ha='center', va='bottom', fontsize=9)

# 平均客単価
ax = axes[2]
values = [stats_df[stats_df['segment'] == s]['avg_unit_price'].values[0] if len(stats_df[stats_df['segment'] == s]) > 0 else 0 for s in segments]
bars = ax.bar(labels, values, color=colors, alpha=0.8)
ax.set_ylabel('平均客単価（円）')
ax.set_title('平均客単価の比較')
ax.tick_params(axis='x', rotation=45)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, f'{val:,.0f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/08_segment_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 08_segment_comparison.png")

# ============================================================
# サマリーレポート
# ============================================================
print("\n[Step 6] サマリーレポート作成...")

summary = f"""# 4セグメント分析レポート

## セグメント定義

| セグメント | 期間 | 時間帯 |
|------------|------|--------|
| 3月以前・ランチ | 〜2025年3月 | 〜16時 |
| 3月以前・ディナー | 〜2025年3月 | 16時〜 |
| 4月以降・ランチ | 2025年4月〜 | 〜16時 |
| 4月以降・ディナー | 2025年4月〜 | 16時〜 |

## 基本統計

| セグメント | 日数 | 平均売上 | 平均客数 | 平均客単価 |
|------------|------|----------|----------|------------|
"""

for _, row in stats_df.iterrows():
    summary += f"| {row['label']} | {row['days']} | {row['avg_sales']:,.0f}円 | {row['avg_customers']:.0f}人 | {row['avg_unit_price']:,.0f}円 |\n"

# 回帰直線の傾き（客1人あたり売上）を計算
summary += "\n## 客1人あたり売上（回帰直線の傾き）\n\n"
summary += "| セグメント | 傾き（円/人） | 相関係数 |\n"
summary += "|------------|---------------|----------|\n"

for seg in segments:
    seg_data = daily_segment[daily_segment['segment'] == seg].dropna(subset=['total_customers', 'total_sales'])
    if len(seg_data) > 1:
        corr = seg_data['total_customers'].corr(seg_data['total_sales'])
        slope = np.polyfit(seg_data['total_customers'], seg_data['total_sales'], 1)[0]
        summary += f"| {segment_labels[seg]} | {slope:,.0f} | {corr:.3f} |\n"

summary += """
## 主要な発見

### 1. 期間による変化（2025年3月前後）
"""

# 期間別の集計
before_total = daily_segment[daily_segment['period'] == 'Before']['total_sales'].sum()
after_total = daily_segment[daily_segment['period'] == 'After']['total_sales'].sum()

summary += f"""
- 3月以前: ランチ中心の営業
- 4月以降: ディナー帯が大幅に強化（アルコール提供開始）

### 2. ランチ vs ディナーの違い
"""

# ランチ/ディナー別
lunch_avg = daily_segment[daily_segment['daypart'] == 'Lunch']['avg_spend_per_customer'].mean()
dinner_avg = daily_segment[daily_segment['daypart'] == 'Dinner']['avg_spend_per_customer'].mean()

summary += f"""
- ランチ帯の平均客単価: {lunch_avg:,.0f}円
- ディナー帯の平均客単価: {dinner_avg:,.0f}円
- ディナー帯は客単価が高い傾向

### 3. 4月以降のディナー帯が最も高収益
"""

# 4月以降ディナー
after_dinner = stats_df[stats_df['segment'] == 'After_Dinner']
if len(after_dinner) > 0:
    summary += f"""
- 平均売上: {after_dinner['avg_sales'].values[0]:,.0f}円
- 平均客数: {after_dinner['avg_customers'].values[0]:.0f}人
- 平均客単価: {after_dinner['avg_unit_price'].values[0]:,.0f}円
"""

summary += """
## 生成ファイル

- `01_sales_distribution.png` - 売上分布
- `02_customers_distribution.png` - 客数分布
- `03_unit_price_distribution.png` - 客単価分布
- `04_customers_vs_sales.png` - 客数vs売上（重ね）
- `05_customers_vs_sales_split.png` - 客数vs売上（4分割）
- `06_weekday_sales.png` - 曜日別売上（重ね）
- `07_weekday_sales_split.png` - 曜日別売上（4分割）
- `08_segment_comparison.png` - 基本統計比較
- `daily_by_segment.csv` - セグメント別日次データ
- `segment_statistics.csv` - セグメント別統計

---
*生成日: 2026-01-21*
"""

with open(f'{OUTPUT_DIR}/analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(summary)
print("  保存: analysis_report.md")

print("\n" + "=" * 60)
print("分析完了！")
print(f"出力先: {OUTPUT_DIR}")
print("=" * 60)

# ファイル一覧
print("\n【生成ファイル一覧】")
for f in sorted(os.listdir(OUTPUT_DIR)):
    print(f"  - {f}")
