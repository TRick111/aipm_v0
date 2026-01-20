#!/usr/bin/env python3
"""
曜日別・入店時刻別の平均滞在時間を折れ線グラフで表示
"""

import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict
from datetime import datetime

# 日本語フォント設定
plt.rcParams['font.family'] = ['Hiragino Sans', 'Arial Unicode MS', 'sans-serif']

INPUT_FILE = "visits_with_duration.csv"
OUTPUT_FILE = "duration_by_hour_weekday.png"

def main():
    # データ読み込み
    # 曜日 -> 時刻(HH:00) -> [滞在時間リスト]
    data = defaultdict(lambda: defaultdict(list))
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            duration = int(row["滞在時間_分"])
            weekday = row["曜日"]
            entry_time = row["入店時刻"]
            
            # 外れ値除外（120分以下）
            if duration > 120:
                continue
            
            # 入店時刻から時（HH）を抽出
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                hour = dt.hour
                data[weekday][hour].append(duration)
            except:
                continue
    
    # 平均を計算
    weekday_order = ["月", "火", "水", "木", "金", "土", "日"]
    hours = list(range(10, 23))  # 10時〜22時
    
    avg_data = {}
    for wd in weekday_order:
        avg_data[wd] = []
        for h in hours:
            durations = data[wd][h]
            if durations:
                avg_data[wd].append(sum(durations) / len(durations))
            else:
                avg_data[wd].append(None)
    
    # グラフ作成
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 色設定（平日は青系、土日は赤系）
    colors = {
        "月": "#1976D2",
        "火": "#2196F3", 
        "水": "#42A5F5",
        "木": "#64B5F6",
        "金": "#90CAF9",
        "土": "#E53935",
        "日": "#FF7043"
    }
    
    markers = {
        "月": "o", "火": "s", "水": "^", "木": "D", 
        "金": "v", "土": "o", "日": "s"
    }
    
    for wd in weekday_order:
        y_values = avg_data[wd]
        # Noneを含む場合は線を分割せずプロット
        valid_x = [h for h, v in zip(hours, y_values) if v is not None]
        valid_y = [v for v in y_values if v is not None]
        
        linewidth = 2.5 if wd in ["土", "日"] else 1.5
        ax.plot(valid_x, valid_y, marker=markers[wd], label=wd, 
                color=colors[wd], linewidth=linewidth, markersize=6)
    
    ax.set_xlabel('入店時刻', fontsize=12)
    ax.set_ylabel('平均滞在時間（分）', fontsize=12)
    ax.set_title('曜日別・入店時刻別の平均滞在時間', fontsize=14)
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h}:00" for h in hours], rotation=45)
    ax.legend(loc='upper right', title='曜日')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(15, 45)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
    print(f"保存: {OUTPUT_FILE}")
    
    # 統計サマリー
    print("\n時間帯別サマリー:")
    print(f"{'時刻':>6}", end="")
    for wd in weekday_order:
        print(f"{wd:>6}", end="")
    print()
    
    for i, h in enumerate(hours):
        print(f"{h:>4}:00", end="")
        for wd in weekday_order:
            v = avg_data[wd][i]
            if v:
                print(f"{v:>6.1f}", end="")
            else:
                print(f"{'--':>6}", end="")
        print()

if __name__ == "__main__":
    main()
