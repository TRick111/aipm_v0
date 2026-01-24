#!/usr/bin/env python3
"""
時間帯別「来店組数」+「店内人数」複合グラフ
平日と土日で分けて表示
"""

import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict
from datetime import datetime

# 日本語フォント設定
plt.rcParams['font.family'] = ['Hiragino Sans', 'Arial Unicode MS', 'sans-serif']

VISITS_FILE = "../StayTimeAnalysis/visits_with_duration.csv"
OCCUPANCY_FILE = "../StayTimeAnalysis/occupancy_10min.csv"

def main():
    print("平日/土日別の時間帯別グラフを作成中...")
    
    weekdays = ["月", "火", "水", "木", "金"]
    weekends = ["土", "日"]
    
    # 来店データ読み込み
    # 平日/土日 -> 時間帯(HH) -> 来店組数、客数、日数
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
    
    # 店内人数データ読み込み
    # 平日/土日 -> 時間帯(HH) -> [店内人数リスト]
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
    
    # データ集計
    hours = list(range(10, 23))
    
    data = {}
    for day_type in ["平日", "土日"]:
        data[day_type] = {
            "groups": [],
            "customers": [],
            "occupancy": []
        }
        for h in hours:
            visit_data = hourly_visits[day_type][h]
            num_days = len(visit_data["days"]) if visit_data["days"] else 1
            data[day_type]["groups"].append(visit_data["groups"] / num_days)
            data[day_type]["customers"].append(visit_data["customers"] / num_days)
            
            occ_values = hourly_occupancy[day_type][h]
            data[day_type]["occupancy"].append(sum(occ_values) / len(occ_values) if occ_values else 0)
    
    # グラフ作成（2つ横並び）
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    colors = {"平日": "#2196F3", "土日": "#E53935"}
    
    for idx, day_type in enumerate(["平日", "土日"]):
        ax1 = axes[idx]
        x = range(len(hours))
        width = 0.35
        
        # 棒グラフ: 来店組数・客数（左軸）
        ax1.bar([i - width/2 for i in x], data[day_type]["groups"], width, 
                label='来店組数/日', color=colors[day_type], alpha=0.7)
        ax1.bar([i + width/2 for i in x], data[day_type]["customers"], width,
                label='来店客数/日', color='#4CAF50', alpha=0.7)
        
        ax1.set_xlabel('時刻', fontsize=12)
        ax1.set_ylabel('1日あたりの来店数', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels([f"{h}:00" for h in hours], rotation=45)
        ax1.set_ylim(0, 45)
        ax1.grid(axis='y', alpha=0.3)
        
        # 折れ線: 平均店内人数（右軸）
        ax2 = ax1.twinx()
        ax2.plot(x, data[day_type]["occupancy"], color='#FF5722', linewidth=2.5, 
                marker='o', markersize=6, label='平均店内人数')
        ax2.set_ylabel('平均店内人数', fontsize=12, color='#FF5722')
        ax2.tick_params(axis='y', labelcolor='#FF5722')
        ax2.set_ylim(0, 25)
        
        # 凡例を統合
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        ax1.set_title(f'{day_type}の来店数と店内人数（1日平均）', fontsize=14)
    
    plt.tight_layout()
    plt.savefig("hourly_visits_occupancy_split.png", dpi=150, bbox_inches='tight')
    print("保存: hourly_visits_occupancy_split.png")
    
    # サマリー出力
    print("\n時間帯別サマリー（1日平均）:")
    print(f"{'':>6} {'─────平日─────':>30} {'─────土日─────':>30}")
    print(f"{'時刻':>6} {'組数':>8} {'客数':>8} {'店内':>8} {'組数':>8} {'客数':>8} {'店内':>8}")
    
    for i, h in enumerate(hours):
        print(f"{h:>4}:00", end="")
        for day_type in ["平日", "土日"]:
            print(f" {data[day_type]['groups'][i]:>7.1f} {data[day_type]['customers'][i]:>7.1f} {data[day_type]['occupancy'][i]:>7.1f}", end="")
        print()
    
    # ピーク比較
    print("\nピーク比較:")
    for day_type in ["平日", "土日"]:
        peak_hour = hours[data[day_type]["groups"].index(max(data[day_type]["groups"]))]
        peak_groups = max(data[day_type]["groups"])
        peak_occ = max(data[day_type]["occupancy"])
        print(f"  {day_type}: 来店ピーク {peak_hour}:00 ({peak_groups:.1f}組/日), 最大店内人数 {peak_occ:.1f}人")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
