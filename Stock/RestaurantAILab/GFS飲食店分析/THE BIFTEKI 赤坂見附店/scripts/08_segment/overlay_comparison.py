#!/usr/bin/env python3
"""
4セグメントを重ねて比較するグラフ
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import rcParams
from pathlib import Path

# 日本語フォント設定
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', 'sans-serif']
rcParams['axes.unicode_minus'] = False

import os
PROJECT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_DIR / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# データ読み込み
daily = pd.read_csv(PROJECT_DIR / "data" / "output" / "daily_by_segment.csv")

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

print("4セグメント重ね比較グラフを作成中...")

# ============================================================
# 図1: 全指標を1枚に（2x2）
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. 売上分布（重ね）
ax = axes[0, 0]
for seg in segments:
    data = daily[daily['segment'] == seg]['total_sales'].dropna()
    ax.hist(data, bins=30, alpha=0.5, label=segment_labels[seg], color=segment_colors[seg], edgecolor='white')
ax.set_xlabel('売上（円）', fontsize=12)
ax.set_ylabel('頻度', fontsize=12)
ax.set_title('売上分布の比較', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')

# 2. 客数分布（重ね）
ax = axes[0, 1]
for seg in segments:
    data = daily[daily['segment'] == seg]['total_customers'].dropna()
    ax.hist(data, bins=30, alpha=0.5, label=segment_labels[seg], color=segment_colors[seg], edgecolor='white')
ax.set_xlabel('客数', fontsize=12)
ax.set_ylabel('頻度', fontsize=12)
ax.set_title('客数分布の比較', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')

# 3. 客単価分布（重ね）
ax = axes[1, 0]
for seg in segments:
    data = daily[daily['segment'] == seg]['avg_spend_per_customer'].dropna()
    ax.hist(data, bins=30, alpha=0.5, label=segment_labels[seg], color=segment_colors[seg], edgecolor='white')
ax.set_xlabel('客単価（円）', fontsize=12)
ax.set_ylabel('頻度', fontsize=12)
ax.set_title('客単価分布の比較', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')

# 4. 客数 vs 売上（重ね）
ax = axes[1, 1]
for seg in segments:
    data = daily[daily['segment'] == seg].dropna(subset=['total_customers', 'total_sales'])
    ax.scatter(data['total_customers'], data['total_sales'], 
               alpha=0.5, s=25, label=segment_labels[seg], color=segment_colors[seg])
    # 回帰直線
    if len(data) > 1:
        z = np.polyfit(data['total_customers'], data['total_sales'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(data['total_customers'].min(), data['total_customers'].max(), 100)
        ax.plot(x_line, p(x_line), '--', color=segment_colors[seg], linewidth=2, alpha=0.8)
ax.set_xlabel('客数', fontsize=12)
ax.set_ylabel('売上（円）', fontsize=12)
ax.set_title('客数 vs 売上', fontsize=14, fontweight='bold')
ax.legend(loc='upper left')

plt.suptitle('4セグメント比較（重ね表示）', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "09_overlay_all.png", dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 09_overlay_all.png")

# ============================================================
# 図2: 売上分布のみ（大きく）
# ============================================================
fig, ax = plt.subplots(figsize=(14, 8))

for seg in segments:
    data = daily[daily['segment'] == seg]['total_sales'].dropna()
    ax.hist(data, bins=40, alpha=0.5, label=f"{segment_labels[seg]} (平均: {data.mean():,.0f}円)", 
            color=segment_colors[seg], edgecolor='white')
    # 平均線
    ax.axvline(data.mean(), color=segment_colors[seg], linestyle='--', linewidth=2, alpha=0.8)

ax.set_xlabel('売上（円）', fontsize=14)
ax.set_ylabel('頻度', fontsize=14)
ax.set_title('4セグメント 売上分布の比較', fontsize=16, fontweight='bold')
ax.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "10_overlay_sales.png", dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 10_overlay_sales.png")

# ============================================================
# 図3: 客数分布のみ（大きく）
# ============================================================
fig, ax = plt.subplots(figsize=(14, 8))

for seg in segments:
    data = daily[daily['segment'] == seg]['total_customers'].dropna()
    ax.hist(data, bins=40, alpha=0.5, label=f"{segment_labels[seg]} (平均: {data.mean():.0f}人)", 
            color=segment_colors[seg], edgecolor='white')
    ax.axvline(data.mean(), color=segment_colors[seg], linestyle='--', linewidth=2, alpha=0.8)

ax.set_xlabel('客数', fontsize=14)
ax.set_ylabel('頻度', fontsize=14)
ax.set_title('4セグメント 客数分布の比較', fontsize=16, fontweight='bold')
ax.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "11_overlay_customers.png", dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 11_overlay_customers.png")

# ============================================================
# 図4: 客単価分布のみ（大きく）
# ============================================================
fig, ax = plt.subplots(figsize=(14, 8))

for seg in segments:
    data = daily[daily['segment'] == seg]['avg_spend_per_customer'].dropna()
    ax.hist(data, bins=40, alpha=0.5, label=f"{segment_labels[seg]} (平均: {data.mean():,.0f}円)", 
            color=segment_colors[seg], edgecolor='white')
    ax.axvline(data.mean(), color=segment_colors[seg], linestyle='--', linewidth=2, alpha=0.8)

ax.set_xlabel('客単価（円）', fontsize=14)
ax.set_ylabel('頻度', fontsize=14)
ax.set_title('4セグメント 客単価分布の比較', fontsize=16, fontweight='bold')
ax.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "12_overlay_unit_price.png", dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 12_overlay_unit_price.png")

# ============================================================
# 図5: 客数 vs 売上（大きく）
# ============================================================
fig, ax = plt.subplots(figsize=(14, 10))

for seg in segments:
    data = daily[daily['segment'] == seg].dropna(subset=['total_customers', 'total_sales'])
    if len(data) > 1:
        corr = data['total_customers'].corr(data['total_sales'])
        slope = np.polyfit(data['total_customers'], data['total_sales'], 1)[0]
        ax.scatter(data['total_customers'], data['total_sales'], 
                   alpha=0.5, s=30, label=f"{segment_labels[seg]} (傾き: {slope:,.0f}円/人)", 
                   color=segment_colors[seg])
        # 回帰直線
        z = np.polyfit(data['total_customers'], data['total_sales'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(data['total_customers'].min(), data['total_customers'].max(), 100)
        ax.plot(x_line, p(x_line), '--', color=segment_colors[seg], linewidth=2.5, alpha=0.9)

ax.set_xlabel('客数', fontsize=14)
ax.set_ylabel('売上（円）', fontsize=14)
ax.set_title('4セグメント 客数 vs 売上', fontsize=16, fontweight='bold')
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "13_overlay_scatter.png", dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 13_overlay_scatter.png")

# ============================================================
# 図6: 箱ひげ図での比較（横並び）
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# データ準備
segment_order = ['Before_Lunch', 'Before_Dinner', 'After_Lunch', 'After_Dinner']
labels = [segment_labels[s] for s in segment_order]

# 売上
ax = axes[0]
data_list = [daily[daily['segment'] == seg]['total_sales'].dropna() for seg in segment_order]
bp = ax.boxplot(data_list, labels=labels, patch_artist=True)
for patch, seg in zip(bp['boxes'], segment_order):
    patch.set_facecolor(segment_colors[seg])
    patch.set_alpha(0.7)
ax.set_ylabel('売上（円）', fontsize=12)
ax.set_title('売上', fontsize=14, fontweight='bold')
ax.tick_params(axis='x', rotation=30)

# 客数
ax = axes[1]
data_list = [daily[daily['segment'] == seg]['total_customers'].dropna() for seg in segment_order]
bp = ax.boxplot(data_list, labels=labels, patch_artist=True)
for patch, seg in zip(bp['boxes'], segment_order):
    patch.set_facecolor(segment_colors[seg])
    patch.set_alpha(0.7)
ax.set_ylabel('客数', fontsize=12)
ax.set_title('客数', fontsize=14, fontweight='bold')
ax.tick_params(axis='x', rotation=30)

# 客単価
ax = axes[2]
data_list = [daily[daily['segment'] == seg]['avg_spend_per_customer'].dropna() for seg in segment_order]
bp = ax.boxplot(data_list, labels=labels, patch_artist=True)
for patch, seg in zip(bp['boxes'], segment_order):
    patch.set_facecolor(segment_colors[seg])
    patch.set_alpha(0.7)
ax.set_ylabel('客単価（円）', fontsize=12)
ax.set_title('客単価', fontsize=14, fontweight='bold')
ax.tick_params(axis='x', rotation=30)

plt.suptitle('4セグメント比較（箱ひげ図）', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "14_boxplot_comparison.png", dpi=150, bbox_inches='tight')
plt.close()
print("  保存: 14_boxplot_comparison.png")

print("\n完了！")
