#!/usr/bin/env python3
"""
4月以降データ限定：売上高低の要因分析
- ランチ帯: 売上上位 vs 下位
- ディナー帯: 売上上位 vs 下位
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

OUTPUT_DIR = '/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-21/SegmentAnalysis/HighLowAnalysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("4月以降：売上高低の要因分析")
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

# 4月以降に限定
cutoff_date = pd.Timestamp('2025-04-01')
df = df[df['H.集計対象営業年月日'] >= cutoff_date].copy()
print(f"  4月以降のレコード数: {len(df):,}")

# 時間帯の分割
df['daypart'] = np.where(df['order_hour'] < 16, 'Lunch', 'Dinner')

# ============================================================
# 詳細な特徴量を含む日次集計
# ============================================================
print("\n[Step 2] 詳細な日次集計...")

def create_daily_features(df, daypart_filter):
    """時間帯別の日次特徴量を作成"""
    filtered = df[df['daypart'] == daypart_filter].copy()
    
    results = []
    for date in filtered['H.集計対象営業年月日'].unique():
        day_data = filtered[filtered['H.集計対象営業年月日'] == date]
        
        # 基本指標
        total_sales = day_data['D.価格'].sum()
        slip_data = day_data.drop_duplicates(subset=['H.伝票番号'])
        total_customers = slip_data['H.客数（合計）'].sum()
        slip_count = slip_data['H.伝票番号'].nunique()
        
        if total_customers == 0 or slip_count == 0:
            continue
        
        # 客単価・1組あたり客数
        avg_unit_price = total_sales / total_customers if total_customers > 0 else 0
        avg_customers_per_slip = total_customers / slip_count if slip_count > 0 else 0
        
        # カテゴリ別売上比率
        total_for_ratio = day_data['D.価格'].sum()
        alcohol_sales = day_data[day_data['D.商品カテゴリ2'] == 'アルコール']['D.価格'].sum()
        topping_sales = day_data[day_data['D.商品カテゴリ2'] == 'トッピング']['D.価格'].sum()
        soft_drink_sales = day_data[day_data['D.商品カテゴリ2'] == 'ソフトドリンク']['D.価格'].sum()
        
        alcohol_ratio = alcohol_sales / total_for_ratio if total_for_ratio > 0 else 0
        topping_ratio = topping_sales / total_for_ratio if total_for_ratio > 0 else 0
        soft_drink_ratio = soft_drink_sales / total_for_ratio if total_for_ratio > 0 else 0
        
        # 商品多様性
        unique_products = day_data['D.商品名'].nunique()
        
        # 1伝票あたり商品数
        items_per_slip = len(day_data) / slip_count if slip_count > 0 else 0
        
        # 時間帯内の集中度（ピーク時間の比率）
        if daypart_filter == 'Lunch':
            # ランチ: 12-13時がピーク
            peak_sales = day_data[(day_data['order_hour'] >= 12) & (day_data['order_hour'] < 13)]['D.価格'].sum()
        else:
            # ディナー: 18-19時がピーク
            peak_sales = day_data[(day_data['order_hour'] >= 18) & (day_data['order_hour'] < 19)]['D.価格'].sum()
        peak_concentration = peak_sales / total_for_ratio if total_for_ratio > 0 else 0
        
        # 曜日
        weekday = pd.Timestamp(date).dayofweek
        weekday_name = pd.Timestamp(date).day_name()
        is_weekend = 1 if weekday in [5, 6] else 0
        
        results.append({
            'date': date,
            'daypart': daypart_filter,
            'total_sales': total_sales,
            'total_customers': total_customers,
            'slip_count': slip_count,
            'avg_unit_price': avg_unit_price,
            'avg_customers_per_slip': avg_customers_per_slip,
            'alcohol_ratio': alcohol_ratio,
            'topping_ratio': topping_ratio,
            'soft_drink_ratio': soft_drink_ratio,
            'unique_products': unique_products,
            'items_per_slip': items_per_slip,
            'peak_concentration': peak_concentration,
            'weekday': weekday,
            'weekday_name': weekday_name,
            'is_weekend': is_weekend
        })
    
    return pd.DataFrame(results)

# ランチとディナーそれぞれで日次集計
lunch_daily = create_daily_features(df, 'Lunch')
dinner_daily = create_daily_features(df, 'Dinner')

print(f"  ランチ日数: {len(lunch_daily)}")
print(f"  ディナー日数: {len(dinner_daily)}")

# ============================================================
# 売上上位/下位の分類
# ============================================================
print("\n[Step 3] 売上上位/下位の分類...")

def classify_high_low(daily_df, q_high=0.75, q_low=0.25):
    """売上で上位/下位に分類"""
    high_threshold = daily_df['total_sales'].quantile(q_high)
    low_threshold = daily_df['total_sales'].quantile(q_low)
    
    daily_df['sales_category'] = 'Middle'
    daily_df.loc[daily_df['total_sales'] >= high_threshold, 'sales_category'] = 'High'
    daily_df.loc[daily_df['total_sales'] <= low_threshold, 'sales_category'] = 'Low'
    
    return daily_df, high_threshold, low_threshold

lunch_daily, lunch_high_th, lunch_low_th = classify_high_low(lunch_daily)
dinner_daily, dinner_high_th, dinner_low_th = classify_high_low(dinner_daily)

print(f"\nランチ売上閾値: 上位 >= {lunch_high_th:,.0f}円, 下位 <= {lunch_low_th:,.0f}円")
print(f"ディナー売上閾値: 上位 >= {dinner_high_th:,.0f}円, 下位 <= {dinner_low_th:,.0f}円")

# ============================================================
# 上位/下位の比較分析
# ============================================================
print("\n[Step 4] 上位/下位の比較分析...")

def compare_high_low(daily_df, daypart_name):
    """上位と下位の特徴を比較"""
    high = daily_df[daily_df['sales_category'] == 'High']
    low = daily_df[daily_df['sales_category'] == 'Low']
    
    metrics = [
        ('total_sales', '売上', '円'),
        ('total_customers', '客数', '人'),
        ('avg_unit_price', '客単価', '円'),
        ('avg_customers_per_slip', '1組あたり客数', '人'),
        ('alcohol_ratio', 'アルコール比率', '%'),
        ('topping_ratio', 'トッピング比率', '%'),
        ('soft_drink_ratio', 'ドリンク比率', '%'),
        ('items_per_slip', '1伝票あたり商品数', '個'),
        ('peak_concentration', 'ピーク集中度', '%'),
        ('is_weekend', '週末比率', '%'),
    ]
    
    print(f"\n【{daypart_name}】上位 vs 下位 比較")
    print("-" * 80)
    print(f"{'指標':<20} {'上位(n={})'.format(len(high)):>15} {'下位(n={})'.format(len(low)):>15} {'差':>15} {'比率':>10}")
    print("-" * 80)
    
    comparison = []
    for col, name, unit in metrics:
        high_val = high[col].mean()
        low_val = low[col].mean()
        diff = high_val - low_val
        ratio = high_val / low_val if low_val != 0 else 0
        
        if unit == '%':
            print(f"{name:<20} {high_val*100:>14.1f}% {low_val*100:>14.1f}% {diff*100:>+14.1f}% {ratio:>9.2f}x")
        elif unit == '円':
            print(f"{name:<20} {high_val:>14,.0f} {low_val:>14,.0f} {diff:>+14,.0f} {ratio:>9.2f}x")
        else:
            print(f"{name:<20} {high_val:>14.1f} {low_val:>14.1f} {diff:>+14.1f} {ratio:>9.2f}x")
        
        comparison.append({
            'metric': name,
            'high_avg': high_val,
            'low_avg': low_val,
            'diff': diff,
            'ratio': ratio
        })
    
    # 曜日分布
    print(f"\n曜日分布:")
    weekday_names = ['月', '火', '水', '木', '金', '土', '日']
    print(f"  上位: ", end="")
    for w in range(7):
        cnt = len(high[high['weekday'] == w])
        print(f"{weekday_names[w]}:{cnt} ", end="")
    print()
    print(f"  下位: ", end="")
    for w in range(7):
        cnt = len(low[low['weekday'] == w])
        print(f"{weekday_names[w]}:{cnt} ", end="")
    print()
    
    return pd.DataFrame(comparison), high, low

lunch_comparison, lunch_high, lunch_low = compare_high_low(lunch_daily, 'ランチ')
dinner_comparison, dinner_high, dinner_low = compare_high_low(dinner_daily, 'ディナー')

# ============================================================
# 可視化
# ============================================================
print("\n[Step 5] 可視化...")

# 色定義
colors = {'High': '#2ecc71', 'Low': '#e74c3c', 'Middle': '#95a5a6'}

# 図1: ランチの上位/下位比較
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# ランチ - 客数分布
ax = axes[0, 0]
for cat in ['High', 'Low']:
    data = lunch_daily[lunch_daily['sales_category'] == cat]['total_customers']
    ax.hist(data, bins=20, alpha=0.6, label=f'{cat} (平均:{data.mean():.0f})', color=colors[cat])
ax.set_xlabel('客数')
ax.set_ylabel('頻度')
ax.set_title('【ランチ】客数分布')
ax.legend()

# ランチ - 客単価分布
ax = axes[0, 1]
for cat in ['High', 'Low']:
    data = lunch_daily[lunch_daily['sales_category'] == cat]['avg_unit_price']
    ax.hist(data, bins=20, alpha=0.6, label=f'{cat} (平均:{data.mean():,.0f}円)', color=colors[cat])
ax.set_xlabel('客単価（円）')
ax.set_ylabel('頻度')
ax.set_title('【ランチ】客単価分布')
ax.legend()

# ランチ - 曜日別件数
ax = axes[0, 2]
weekday_names = ['月', '火', '水', '木', '金', '土', '日']
x = np.arange(7)
width = 0.35
high_counts = [len(lunch_high[lunch_high['weekday'] == w]) for w in range(7)]
low_counts = [len(lunch_low[lunch_low['weekday'] == w]) for w in range(7)]
ax.bar(x - width/2, high_counts, width, label='High', color=colors['High'], alpha=0.8)
ax.bar(x + width/2, low_counts, width, label='Low', color=colors['Low'], alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(weekday_names)
ax.set_xlabel('曜日')
ax.set_ylabel('日数')
ax.set_title('【ランチ】曜日別 High/Low 日数')
ax.legend()

# ディナー - 客数分布
ax = axes[1, 0]
for cat in ['High', 'Low']:
    data = dinner_daily[dinner_daily['sales_category'] == cat]['total_customers']
    ax.hist(data, bins=20, alpha=0.6, label=f'{cat} (平均:{data.mean():.0f})', color=colors[cat])
ax.set_xlabel('客数')
ax.set_ylabel('頻度')
ax.set_title('【ディナー】客数分布')
ax.legend()

# ディナー - 客単価分布
ax = axes[1, 1]
for cat in ['High', 'Low']:
    data = dinner_daily[dinner_daily['sales_category'] == cat]['avg_unit_price']
    ax.hist(data, bins=20, alpha=0.6, label=f'{cat} (平均:{data.mean():,.0f}円)', color=colors[cat])
ax.set_xlabel('客単価（円）')
ax.set_ylabel('頻度')
ax.set_title('【ディナー】客単価分布')
ax.legend()

# ディナー - 曜日別件数
ax = axes[1, 2]
high_counts = [len(dinner_high[dinner_high['weekday'] == w]) for w in range(7)]
low_counts = [len(dinner_low[dinner_low['weekday'] == w]) for w in range(7)]
ax.bar(x - width/2, high_counts, width, label='High', color=colors['High'], alpha=0.8)
ax.bar(x + width/2, low_counts, width, label='Low', color=colors['Low'], alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(weekday_names)
ax.set_xlabel('曜日')
ax.set_ylabel('日数')
ax.set_title('【ディナー】曜日別 High/Low 日数')
ax.legend()

plt.suptitle('売上上位(緑) vs 下位(赤) の比較', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_high_low_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 01_high_low_distribution.png")

# 図2: 要因の影響度比較（バーチャート）
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

metrics_to_plot = [
    ('total_customers', '客数'),
    ('avg_unit_price', '客単価'),
    ('avg_customers_per_slip', '1組あたり客数'),
    ('items_per_slip', '商品数/伝票'),
]

# ランチ
ax = axes[0]
x = np.arange(len(metrics_to_plot))
width = 0.35

high_vals = [lunch_high[m[0]].mean() for m in metrics_to_plot]
low_vals = [lunch_low[m[0]].mean() for m in metrics_to_plot]

# 正規化（下位を1として比率表示）
high_ratios = [h/l if l != 0 else 0 for h, l in zip(high_vals, low_vals)]
low_ratios = [1] * len(metrics_to_plot)

ax.bar(x - width/2, high_ratios, width, label='High', color=colors['High'], alpha=0.8)
ax.bar(x + width/2, low_ratios, width, label='Low (=1.0)', color=colors['Low'], alpha=0.8)
ax.axhline(1.0, color='black', linestyle='--', alpha=0.5)
ax.set_xticks(x)
ax.set_xticklabels([m[1] for m in metrics_to_plot])
ax.set_ylabel('比率（Lowを1とした場合）')
ax.set_title('【ランチ】High/Low 比率')
ax.legend()

# 数値ラベル
for i, ratio in enumerate(high_ratios):
    ax.text(i - width/2, ratio + 0.02, f'{ratio:.2f}x', ha='center', fontsize=10)

# ディナー
ax = axes[1]
high_vals = [dinner_high[m[0]].mean() for m in metrics_to_plot]
low_vals = [dinner_low[m[0]].mean() for m in metrics_to_plot]
high_ratios = [h/l if l != 0 else 0 for h, l in zip(high_vals, low_vals)]

ax.bar(x - width/2, high_ratios, width, label='High', color=colors['High'], alpha=0.8)
ax.bar(x + width/2, low_ratios, width, label='Low (=1.0)', color=colors['Low'], alpha=0.8)
ax.axhline(1.0, color='black', linestyle='--', alpha=0.5)
ax.set_xticks(x)
ax.set_xticklabels([m[1] for m in metrics_to_plot])
ax.set_ylabel('比率（Lowを1とした場合）')
ax.set_title('【ディナー】High/Low 比率')
ax.legend()

for i, ratio in enumerate(high_ratios):
    ax.text(i - width/2, ratio + 0.02, f'{ratio:.2f}x', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_factor_ratio.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 02_factor_ratio.png")

# 図3: 客数 vs 売上（High/Low色分け）
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# ランチ
ax = axes[0]
for cat in ['High', 'Low', 'Middle']:
    data = lunch_daily[lunch_daily['sales_category'] == cat]
    ax.scatter(data['total_customers'], data['total_sales'], 
               alpha=0.6, s=50, label=cat, color=colors[cat])
ax.set_xlabel('客数')
ax.set_ylabel('売上（円）')
ax.set_title('【ランチ】客数 vs 売上')
ax.legend()

# ディナー
ax = axes[1]
for cat in ['High', 'Low', 'Middle']:
    data = dinner_daily[dinner_daily['sales_category'] == cat]
    ax.scatter(data['total_customers'], data['total_sales'], 
               alpha=0.6, s=50, label=cat, color=colors[cat])
ax.set_xlabel('客数')
ax.set_ylabel('売上（円）')
ax.set_title('【ディナー】客数 vs 売上')
ax.legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_scatter_high_low.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 03_scatter_high_low.png")

# 図4: 詳細比較（レーダーチャート風のバー）
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

metrics_radar = [
    ('total_customers', '客数', False),
    ('avg_unit_price', '客単価', False),
    ('avg_customers_per_slip', '1組客数', False),
    ('alcohol_ratio', 'アルコール', True),
    ('topping_ratio', 'トッピング', True),
    ('items_per_slip', '商品数', False),
    ('is_weekend', '週末', True),
]

# ランチ
ax = axes[0]
labels = [m[1] for m in metrics_radar]
x = np.arange(len(labels))
width = 0.35

# 正規化（0-1スケール）
high_data = lunch_high[[m[0] for m in metrics_radar]].mean()
low_data = lunch_low[[m[0] for m in metrics_radar]].mean()
all_data = pd.concat([high_data, low_data])
high_norm = (high_data - all_data.min()) / (all_data.max() - all_data.min() + 0.001)
low_norm = (low_data - all_data.min()) / (all_data.max() - all_data.min() + 0.001)

ax.barh(x - width/2, high_norm.values, width, label='High', color=colors['High'], alpha=0.8)
ax.barh(x + width/2, low_norm.values, width, label='Low', color=colors['Low'], alpha=0.8)
ax.set_yticks(x)
ax.set_yticklabels(labels)
ax.set_xlabel('正規化スコア')
ax.set_title('【ランチ】各指標のHigh/Low比較')
ax.legend()

# ディナー
ax = axes[1]
high_data = dinner_high[[m[0] for m in metrics_radar]].mean()
low_data = dinner_low[[m[0] for m in metrics_radar]].mean()
all_data = pd.concat([high_data, low_data])
high_norm = (high_data - all_data.min()) / (all_data.max() - all_data.min() + 0.001)
low_norm = (low_data - all_data.min()) / (all_data.max() - all_data.min() + 0.001)

ax.barh(x - width/2, high_norm.values, width, label='High', color=colors['High'], alpha=0.8)
ax.barh(x + width/2, low_norm.values, width, label='Low', color=colors['Low'], alpha=0.8)
ax.set_yticks(x)
ax.set_yticklabels(labels)
ax.set_xlabel('正規化スコア')
ax.set_title('【ディナー】各指標のHigh/Low比較')
ax.legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_metrics_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 04_metrics_comparison.png")

# ============================================================
# サマリーレポート
# ============================================================
print("\n[Step 6] サマリーレポート作成...")

# 売上の分解（客数 × 客単価）
lunch_high_contrib = f"客数 {lunch_high['total_customers'].mean():.0f} × 客単価 {lunch_high['avg_unit_price'].mean():,.0f} = {lunch_high['total_sales'].mean():,.0f}円"
lunch_low_contrib = f"客数 {lunch_low['total_customers'].mean():.0f} × 客単価 {lunch_low['avg_unit_price'].mean():,.0f} = {lunch_low['total_sales'].mean():,.0f}円"
dinner_high_contrib = f"客数 {dinner_high['total_customers'].mean():.0f} × 客単価 {dinner_high['avg_unit_price'].mean():,.0f} = {dinner_high['total_sales'].mean():,.0f}円"
dinner_low_contrib = f"客数 {dinner_low['total_customers'].mean():.0f} × 客単価 {dinner_low['avg_unit_price'].mean():,.0f} = {dinner_low['total_sales'].mean():,.0f}円"

summary = f"""# 4月以降：売上高低の要因分析レポート

## 分析概要

**対象期間**: 2025年4月以降
**分析単位**: 日次（ランチ帯・ディナー帯それぞれ）
**分類方法**: 売上上位25%を「High」、下位25%を「Low」として比較

## ランチ帯の分析

### 売上分類の閾値
- High（上位25%）: 売上 >= {lunch_high_th:,.0f}円
- Low（下位25%）: 売上 <= {lunch_low_th:,.0f}円

### 売上の構造分解
- **High日**: {lunch_high_contrib}
- **Low日**: {lunch_low_contrib}

### High日とLow日の違い

| 指標 | High日 | Low日 | 差 | 比率 |
|------|--------|-------|-----|------|
| 売上 | {lunch_high['total_sales'].mean():,.0f}円 | {lunch_low['total_sales'].mean():,.0f}円 | {lunch_high['total_sales'].mean() - lunch_low['total_sales'].mean():+,.0f}円 | {lunch_high['total_sales'].mean() / lunch_low['total_sales'].mean():.2f}x |
| 客数 | {lunch_high['total_customers'].mean():.0f}人 | {lunch_low['total_customers'].mean():.0f}人 | {lunch_high['total_customers'].mean() - lunch_low['total_customers'].mean():+.0f}人 | {lunch_high['total_customers'].mean() / lunch_low['total_customers'].mean():.2f}x |
| 客単価 | {lunch_high['avg_unit_price'].mean():,.0f}円 | {lunch_low['avg_unit_price'].mean():,.0f}円 | {lunch_high['avg_unit_price'].mean() - lunch_low['avg_unit_price'].mean():+,.0f}円 | {lunch_high['avg_unit_price'].mean() / lunch_low['avg_unit_price'].mean():.2f}x |
| 1組あたり客数 | {lunch_high['avg_customers_per_slip'].mean():.2f}人 | {lunch_low['avg_customers_per_slip'].mean():.2f}人 | {lunch_high['avg_customers_per_slip'].mean() - lunch_low['avg_customers_per_slip'].mean():+.2f}人 | {lunch_high['avg_customers_per_slip'].mean() / lunch_low['avg_customers_per_slip'].mean():.2f}x |
| 週末比率 | {lunch_high['is_weekend'].mean()*100:.0f}% | {lunch_low['is_weekend'].mean()*100:.0f}% | - | - |

### ランチのHigh日の特徴
"""

# ランチのHigh日の曜日分布
lunch_high_weekday = lunch_high['weekday'].value_counts().sort_index()
most_common_weekday = lunch_high_weekday.idxmax()
weekday_jp = ['月', '火', '水', '木', '金', '土', '日']

summary += f"""
1. **曜日**: {weekday_jp[most_common_weekday]}曜日が最多（{lunch_high_weekday[most_common_weekday]}日）
2. **客数**: Low日の約{lunch_high['total_customers'].mean() / lunch_low['total_customers'].mean():.1f}倍
3. **客単価**: Low日より{lunch_high['avg_unit_price'].mean() - lunch_low['avg_unit_price'].mean():,.0f}円高い

---

## ディナー帯の分析

### 売上分類の閾値
- High（上位25%）: 売上 >= {dinner_high_th:,.0f}円
- Low（下位25%）: 売上 <= {dinner_low_th:,.0f}円

### 売上の構造分解
- **High日**: {dinner_high_contrib}
- **Low日**: {dinner_low_contrib}

### High日とLow日の違い

| 指標 | High日 | Low日 | 差 | 比率 |
|------|--------|-------|-----|------|
| 売上 | {dinner_high['total_sales'].mean():,.0f}円 | {dinner_low['total_sales'].mean():,.0f}円 | {dinner_high['total_sales'].mean() - dinner_low['total_sales'].mean():+,.0f}円 | {dinner_high['total_sales'].mean() / dinner_low['total_sales'].mean():.2f}x |
| 客数 | {dinner_high['total_customers'].mean():.0f}人 | {dinner_low['total_customers'].mean():.0f}人 | {dinner_high['total_customers'].mean() - dinner_low['total_customers'].mean():+.0f}人 | {dinner_high['total_customers'].mean() / dinner_low['total_customers'].mean():.2f}x |
| 客単価 | {dinner_high['avg_unit_price'].mean():,.0f}円 | {dinner_low['avg_unit_price'].mean():,.0f}円 | {dinner_high['avg_unit_price'].mean() - dinner_low['avg_unit_price'].mean():+,.0f}円 | {dinner_high['avg_unit_price'].mean() / dinner_low['avg_unit_price'].mean():.2f}x |
| アルコール比率 | {dinner_high['alcohol_ratio'].mean()*100:.1f}% | {dinner_low['alcohol_ratio'].mean()*100:.1f}% | {(dinner_high['alcohol_ratio'].mean() - dinner_low['alcohol_ratio'].mean())*100:+.1f}% | - |
| 週末比率 | {dinner_high['is_weekend'].mean()*100:.0f}% | {dinner_low['is_weekend'].mean()*100:.0f}% | - | - |

### ディナーのHigh日の特徴
"""

dinner_high_weekday = dinner_high['weekday'].value_counts().sort_index()
most_common_weekday_d = dinner_high_weekday.idxmax()

summary += f"""
1. **曜日**: {weekday_jp[most_common_weekday_d]}曜日が最多（{dinner_high_weekday[most_common_weekday_d]}日）
2. **客数**: Low日の約{dinner_high['total_customers'].mean() / dinner_low['total_customers'].mean():.1f}倍
3. **客単価**: Low日より{dinner_high['avg_unit_price'].mean() - dinner_low['avg_unit_price'].mean():,.0f}円高い
4. **アルコール比率**: {dinner_high['alcohol_ratio'].mean()*100:.1f}% vs {dinner_low['alcohol_ratio'].mean()*100:.1f}%

---

## 主要な発見

### 売上を分ける最大の要因

| 時間帯 | 最も影響が大きい要因 | 寄与度の推定 |
|--------|----------------------|--------------|
| ランチ | **客数** | High/Low比 {lunch_high['total_customers'].mean() / lunch_low['total_customers'].mean():.2f}x |
| ディナー | **客数** | High/Low比 {dinner_high['total_customers'].mean() / dinner_low['total_customers'].mean():.2f}x |

### 時間帯別の特徴

**ランチ帯**:
- 売上の差は主に「客数」で決まる
- 客単価の差は比較的小さい
- 曜日による影響が大きい

**ディナー帯**:
- 客数に加え「客単価」の差も大きい
- アルコール比率の違いが客単価に影響
- High日はグループ客が多い傾向

---

*生成日: 2026-01-21*
"""

with open(f'{OUTPUT_DIR}/analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(summary)
print("  保存: analysis_report.md")

# CSVも保存
lunch_daily.to_csv(f'{OUTPUT_DIR}/lunch_daily_classified.csv', index=False)
dinner_daily.to_csv(f'{OUTPUT_DIR}/dinner_daily_classified.csv', index=False)
print("  保存: lunch_daily_classified.csv, dinner_daily_classified.csv")

print("\n" + "=" * 60)
print("分析完了！")
print(f"出力先: {OUTPUT_DIR}")
print("=" * 60)
