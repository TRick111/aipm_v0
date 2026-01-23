#!/usr/bin/env python3
"""
滞在時間のヒストグラムを生成
"""

import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 日本語フォント設定
plt.rcParams['font.family'] = ['Hiragino Sans', 'Arial Unicode MS', 'sans-serif']

INPUT_FILE = "visits_with_duration.csv"
OUTPUT_FILE = "duration_histogram.png"

def main():
    # データ読み込み
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        durations = [int(row["滞在時間_分"]) for row in reader]
    
    print(f"総組数: {len(durations)}")
    print(f"平均: {sum(durations)/len(durations):.1f}分")
    print(f"最小: {min(durations)}分, 最大: {max(durations)}分")
    
    # 外れ値を除外（120分以上は除外してヒストグラム表示）
    filtered = [d for d in durations if d <= 120]
    outliers = len(durations) - len(filtered)
    print(f"120分以下: {len(filtered)}組 ({100*len(filtered)/len(durations):.1f}%)")
    print(f"120分超（外れ値）: {outliers}組")
    
    # ヒストグラム作成
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 左: 全体（120分以下）
    ax1 = axes[0]
    ax1.hist(filtered, bins=range(0, 125, 5), edgecolor='white', alpha=0.8, color='#2196F3')
    ax1.set_xlabel('滞在時間（分）', fontsize=12)
    ax1.set_ylabel('組数', fontsize=12)
    ax1.set_title(f'滞在時間分布（120分以下, n={len(filtered):,}）', fontsize=14)
    ax1.axvline(x=sum(filtered)/len(filtered), color='red', linestyle='--', label=f'平均 {sum(filtered)/len(filtered):.1f}分')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # 右: 曜日別の箱ひげ図
    ax2 = axes[1]
    
    # 曜日別にデータを再読み込み
    weekday_data = {wd: [] for wd in ["月", "火", "水", "木", "金", "土", "日"]}
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = int(row["滞在時間_分"])
            wd = row["曜日"]
            if d <= 120 and wd in weekday_data:
                weekday_data[wd].append(d)
    
    weekday_order = ["月", "火", "水", "木", "金", "土", "日"]
    data_for_box = [weekday_data[wd] for wd in weekday_order]
    
    bp = ax2.boxplot(data_for_box, labels=weekday_order, patch_artist=True)
    colors = ['#BBDEFB', '#BBDEFB', '#BBDEFB', '#BBDEFB', '#BBDEFB', '#FFCDD2', '#FFCDD2']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax2.set_xlabel('曜日', fontsize=12)
    ax2.set_ylabel('滞在時間（分）', fontsize=12)
    ax2.set_title('曜日別滞在時間分布', fontsize=14)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
    print(f"\n保存: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
