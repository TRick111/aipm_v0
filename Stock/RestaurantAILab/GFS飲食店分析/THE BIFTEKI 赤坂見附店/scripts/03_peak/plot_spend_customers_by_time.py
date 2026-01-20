#!/usr/bin/env python3
"""
入店時間帯別の客数と客単価（15分刻み）
平日と土日で別グラフ、客数と客単価を同じグラフ内で表示
"""

import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict
from datetime import datetime
import numpy as np

plt.rcParams['font.family'] = ['Hiragino Sans', 'Arial Unicode MS', 'sans-serif']

EATIN_FILE = "../transformed_pos_data_eatin.csv"

def get_15min_slot(hour, minute):
    """15分刻みのスロットを取得"""
    slot_minute = (minute // 15) * 15
    return f"{hour:02d}:{slot_minute:02d}"

def main():
    print("入店時間帯別の客数と客単価を計算中...")
    
    weekdays_list = ["月", "火", "水", "木", "金"]
    weekends_list = ["土", "日"]
    
    # 伝票単位でデータを収集
    # 平日/土日 -> 15分スロット -> [(売上, 客数), ...]
    data = {
        "平日": defaultdict(lambda: {"total_sales": 0, "total_customers": 0, "count": 0}),
        "土日": defaultdict(lambda: {"total_sales": 0, "total_customers": 0, "count": 0})
    }
    
    # 伝票ごとにユニーク化するためのセット
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
                data[day_type][slot]["total_sales"] += sales
                data[day_type][slot]["total_customers"] += customers
                data[day_type][slot]["count"] += 1
            except:
                continue
    
    # 15分スロットのリスト（10:00〜22:45）
    time_slots = []
    for h in range(10, 23):
        for m in [0, 15, 30, 45]:
            time_slots.append(f"{h:02d}:{m:02d}")
    
    # 各スロットの平均客単価と客数を計算
    stats = {"平日": {"spend": [], "customers": []}, 
             "土日": {"spend": [], "customers": []}}
    
    for day_type in ["平日", "土日"]:
        for slot in time_slots:
            slot_data = data[day_type][slot]
            if slot_data["total_customers"] > 0:
                avg_spend = slot_data["total_sales"] / slot_data["total_customers"]
                stats[day_type]["spend"].append(avg_spend)
                stats[day_type]["customers"].append(slot_data["total_customers"])
            else:
                stats[day_type]["spend"].append(None)
                stats[day_type]["customers"].append(0)
    
    # グラフ作成（平日と土日で分けて）
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    x_indices = list(range(len(time_slots)))
    
    # X軸ラベル（1時間ごとに表示）
    tick_indices = [i for i, slot in enumerate(time_slots) if slot.endswith(":00")]
    tick_labels = [time_slots[i] for i in tick_indices]
    
    colors = {"平日": "#2196F3", "土日": "#E53935"}
    
    for idx, day_type in enumerate(["平日", "土日"]):
        ax1 = axes[idx]
        
        # 棒グラフ: 客数（左軸）
        customers = stats[day_type]["customers"]
        bars = ax1.bar(x_indices, customers, color=colors[day_type], alpha=0.6, label='客数')
        
        ax1.set_xlabel('入店時刻', fontsize=12)
        ax1.set_ylabel('客数', fontsize=12, color=colors[day_type])
        ax1.tick_params(axis='y', labelcolor=colors[day_type])
        ax1.set_xticks(tick_indices)
        ax1.set_xticklabels(tick_labels, rotation=45)
        ax1.set_xlim(-0.5, len(time_slots)-0.5)
        ax1.grid(axis='y', alpha=0.3)
        
        # 折れ線: 客単価（右軸）
        ax2 = ax1.twinx()
        spend = stats[day_type]["spend"]
        
        # Noneを除いてプロット
        valid_x = [x for x, s in zip(x_indices, spend) if s is not None]
        valid_y = [s for s in spend if s is not None]
        
        line = ax2.plot(valid_x, valid_y, color='#FF9800', linewidth=2.5, 
                       marker='o', markersize=4, label='客単価')
        ax2.set_ylabel('客単価（円）', fontsize=12, color='#FF9800')
        ax2.tick_params(axis='y', labelcolor='#FF9800')
        
        # Y軸の範囲を揃える
        ax2.set_ylim(800, 1800)
        
        # 凡例を統合
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax1.set_title(f'{day_type}：入店時間帯別の客数と客単価（15分刻み）', fontsize=14)
    
    plt.tight_layout()
    plt.savefig("spend_customers_by_time_split.png", dpi=150, bbox_inches='tight')
    print("\n保存: spend_customers_by_time_split.png")
    
    # サマリー
    print("\n" + "=" * 60)
    print("時間帯別サマリー")
    print("=" * 60)
    
    for day_type in ["平日", "土日"]:
        print(f"\n【{day_type}】")
        total_customers = sum(stats[day_type]["customers"])
        
        # ピーク時間帯
        max_customers_idx = stats[day_type]["customers"].index(max(stats[day_type]["customers"]))
        max_customers_time = time_slots[max_customers_idx]
        max_customers = stats[day_type]["customers"][max_customers_idx]
        
        # 客単価が最高・最低の時間帯
        valid_spend = [(i, s) for i, s in enumerate(stats[day_type]["spend"]) if s is not None]
        if valid_spend:
            max_spend_idx = max(valid_spend, key=lambda x: x[1])[0]
            min_spend_idx = min(valid_spend, key=lambda x: x[1])[0]
            
            print(f"  総客数: {total_customers:,}人")
            print(f"  客数ピーク: {max_customers_time} ({max_customers:,}人)")
            print(f"  客単価最高: {time_slots[max_spend_idx]} ({stats[day_type]['spend'][max_spend_idx]:.0f}円)")
            print(f"  客単価最低: {time_slots[min_spend_idx]} ({stats[day_type]['spend'][min_spend_idx]:.0f}円)")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
