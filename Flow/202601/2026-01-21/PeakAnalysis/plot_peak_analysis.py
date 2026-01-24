#!/usr/bin/env python3
"""
ピークタイム分析グラフ
1. 時間帯別「来店組数」+「店内人数」の複合グラフ
3. 曜日別・店内人数の時系列推移（10分刻み）
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
    # ========================================
    # グラフ3: 曜日別・店内人数の時系列推移
    # ========================================
    print("グラフ3: 曜日別・店内人数の時系列推移を作成中...")
    
    # 10分刻みデータ読み込み
    # 曜日 -> 時刻(HH:MM) -> [店内人数リスト]
    occupancy_data = defaultdict(lambda: defaultdict(list))
    
    with open(OCCUPANCY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            weekday = row["曜日"]
            time_slot = row["時刻"]
            count = int(row["店内人数"])
            occupancy_data[weekday][time_slot].append(count)
    
    # 平均を計算
    weekday_order = ["月", "火", "水", "木", "金", "土", "日"]
    
    # 時刻スロット（10:00〜22:50まで10分刻み）
    time_slots = []
    for h in range(10, 23):
        for m in [0, 10, 20, 30, 40, 50]:
            time_slots.append(f"{h:02d}:{m:02d}")
    
    avg_occupancy = {}
    for wd in weekday_order:
        avg_occupancy[wd] = []
        for ts in time_slots:
            values = occupancy_data[wd][ts]
            if values:
                avg_occupancy[wd].append(sum(values) / len(values))
            else:
                avg_occupancy[wd].append(0)
    
    # グラフ3作成
    fig3, ax3 = plt.subplots(figsize=(16, 7))
    
    colors = {
        "月": "#1976D2", "火": "#2196F3", "水": "#42A5F5",
        "木": "#64B5F6", "金": "#90CAF9", "土": "#E53935", "日": "#FF7043"
    }
    
    x_indices = list(range(len(time_slots)))
    
    for wd in weekday_order:
        linewidth = 2.5 if wd in ["土", "日"] else 1.5
        ax3.plot(x_indices, avg_occupancy[wd], label=wd, 
                color=colors[wd], linewidth=linewidth, alpha=0.8)
    
    # X軸ラベル（30分ごとに表示）
    tick_indices = [i for i, ts in enumerate(time_slots) if ts.endswith(":00") or ts.endswith(":30")]
    tick_labels = [time_slots[i] for i in tick_indices]
    ax3.set_xticks(tick_indices)
    ax3.set_xticklabels(tick_labels, rotation=45)
    
    ax3.set_xlabel('時刻', fontsize=12)
    ax3.set_ylabel('平均店内人数', fontsize=12)
    ax3.set_title('曜日別・店内人数の時系列推移（10分刻み平均）', fontsize=14)
    ax3.legend(loc='upper right', title='曜日')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, len(time_slots)-1)
    
    plt.tight_layout()
    plt.savefig("occupancy_timeseries_weekday.png", dpi=150, bbox_inches='tight')
    print("  保存: occupancy_timeseries_weekday.png")
    plt.close()
    
    # ========================================
    # グラフ1: 時間帯別「来店組数」+「店内人数」複合グラフ
    # ========================================
    print("\nグラフ1: 時間帯別「来店組数」+「店内人数」複合グラフを作成中...")
    
    # 来店データ読み込み
    # 時間帯(HH) -> 来店組数、客数
    hourly_visits = defaultdict(lambda: {"groups": 0, "customers": 0, "days": set()})
    
    with open(VISITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry_time = row["入店時刻"]
            customers = int(row["客数"])
            date = row["営業日"]
            
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                hour = dt.hour
                hourly_visits[hour]["groups"] += 1
                hourly_visits[hour]["customers"] += customers
                hourly_visits[hour]["days"].add(date)
            except:
                continue
    
    # 店内人数の時間帯平均
    # 時間帯(HH) -> 平均店内人数
    hourly_occupancy = defaultdict(list)
    
    with open(OCCUPANCY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_slot = row["時刻"]
            count = int(row["店内人数"])
            hour = int(time_slot.split(":")[0])
            hourly_occupancy[hour].append(count)
    
    # データ集計
    hours = list(range(10, 23))
    
    # 1日あたり平均来店組数
    avg_groups_per_day = []
    avg_customers_per_day = []
    avg_occupancy_per_hour = []
    
    for h in hours:
        data = hourly_visits[h]
        num_days = len(data["days"]) if data["days"] else 1
        avg_groups_per_day.append(data["groups"] / num_days)
        avg_customers_per_day.append(data["customers"] / num_days)
        
        occ_values = hourly_occupancy[h]
        avg_occupancy_per_hour.append(sum(occ_values) / len(occ_values) if occ_values else 0)
    
    # グラフ1作成（2軸）
    fig1, ax1 = plt.subplots(figsize=(14, 7))
    
    x = range(len(hours))
    width = 0.35
    
    # 棒グラフ: 来店組数（左軸）
    bars = ax1.bar([i - width/2 for i in x], avg_groups_per_day, width, 
                   label='来店組数/日', color='#2196F3', alpha=0.7)
    ax1.bar([i + width/2 for i in x], avg_customers_per_day, width,
            label='来店客数/日', color='#4CAF50', alpha=0.7)
    
    ax1.set_xlabel('時刻', fontsize=12)
    ax1.set_ylabel('1日あたりの来店数', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{h}:00" for h in hours], rotation=45)
    ax1.legend(loc='upper left')
    ax1.grid(axis='y', alpha=0.3)
    
    # 折れ線: 平均店内人数（右軸）
    ax2 = ax1.twinx()
    line = ax2.plot(x, avg_occupancy_per_hour, color='#E53935', linewidth=2.5, 
                    marker='o', markersize=6, label='平均店内人数')
    ax2.set_ylabel('平均店内人数', fontsize=12, color='#E53935')
    ax2.tick_params(axis='y', labelcolor='#E53935')
    
    # 凡例を統合
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax1.set_title('時間帯別の来店数と店内人数（1日平均）', fontsize=14)
    
    plt.tight_layout()
    plt.savefig("hourly_visits_occupancy.png", dpi=150, bbox_inches='tight')
    print("  保存: hourly_visits_occupancy.png")
    plt.close()
    
    # サマリー出力
    print("\n時間帯別サマリー（1日平均）:")
    print(f"{'時刻':>6} {'来店組数':>10} {'来店客数':>10} {'店内人数':>10}")
    for i, h in enumerate(hours):
        print(f"{h:>4}:00 {avg_groups_per_day[i]:>10.1f} {avg_customers_per_day[i]:>10.1f} {avg_occupancy_per_hour[i]:>10.1f}")
    
    # ピーク特定
    peak_hour_groups = hours[avg_groups_per_day.index(max(avg_groups_per_day))]
    peak_hour_occupancy = hours[avg_occupancy_per_hour.index(max(avg_occupancy_per_hour))]
    
    print(f"\nピーク時間帯:")
    print(f"  来店組数ピーク: {peak_hour_groups}:00 ({max(avg_groups_per_day):.1f}組/日)")
    print(f"  店内人数ピーク: {peak_hour_occupancy}:00 ({max(avg_occupancy_per_hour):.1f}人)")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
