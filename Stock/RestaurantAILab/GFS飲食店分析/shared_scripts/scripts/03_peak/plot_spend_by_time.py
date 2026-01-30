#!/usr/bin/env python3
"""
入店時間帯別の客単価の推移（15分刻み）
平日と土日で分けて表示
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
    print("入店時間帯別の客単価を計算中...")
    
    weekdays_list = ["月", "火", "水", "木", "金"]
    weekends_list = ["土", "日"]
    
    # 伝票単位でデータを収集
    # 平日/土日 -> 15分スロット -> [(売上, 客数), ...]
    data = {
        "平日": defaultdict(list),
        "土日": defaultdict(list)
    }
    
    # 伝票ごとにユニーク化するためのセット
    processed_tickets = set()
    
    with open(EATIN_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticket_no = row["H.伝票番号"]
            
            # 既に処理済みの伝票はスキップ
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
                
                spend_per_customer = sales / customers
                
                # 入店時刻から15分スロットを取得
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                slot = get_15min_slot(dt.hour, dt.minute)
                
                day_type = "平日" if weekday in weekdays_list else "土日"
                data[day_type][slot].append(spend_per_customer)
            except:
                continue
    
    print(f"  平日の伝票数: {sum(len(v) for v in data['平日'].values())}")
    print(f"  土日の伝票数: {sum(len(v) for v in data['土日'].values())}")
    
    # 15分スロットのリスト（10:00〜22:45）
    time_slots = []
    for h in range(10, 23):
        for m in [0, 15, 30, 45]:
            time_slots.append(f"{h:02d}:{m:02d}")
    
    # 各スロットの平均客単価を計算
    avg_spend = {"平日": [], "土日": []}
    count = {"平日": [], "土日": []}
    
    for day_type in ["平日", "土日"]:
        for slot in time_slots:
            values = data[day_type][slot]
            if values:
                avg_spend[day_type].append(np.mean(values))
                count[day_type].append(len(values))
            else:
                avg_spend[day_type].append(None)
                count[day_type].append(0)
    
    # グラフ作成
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    colors = {"平日": "#2196F3", "土日": "#E53935"}
    
    x_indices = list(range(len(time_slots)))
    
    # 上段: 客単価推移
    ax1 = axes[0]
    for day_type in ["平日", "土日"]:
        y_values = avg_spend[day_type]
        # Noneを除いてプロット
        valid_x = [x for x, y in zip(x_indices, y_values) if y is not None]
        valid_y = [y for y in y_values if y is not None]
        
        ax1.plot(valid_x, valid_y, marker='o', markersize=4, 
                label=day_type, color=colors[day_type], linewidth=2, alpha=0.8)
    
    # X軸ラベル（1時間ごとに表示）
    tick_indices = [i for i, slot in enumerate(time_slots) if slot.endswith(":00")]
    tick_labels = [time_slots[i] for i in tick_indices]
    ax1.set_xticks(tick_indices)
    ax1.set_xticklabels(tick_labels, rotation=45)
    
    ax1.set_xlabel('入店時刻', fontsize=12)
    ax1.set_ylabel('平均客単価（円）', fontsize=12)
    ax1.set_title('入店時間帯別の客単価（15分刻み）', fontsize=14)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, len(time_slots)-1)
    
    # 下段: サンプルサイズ（棒グラフ）
    ax2 = axes[1]
    width = 0.4
    ax2.bar([x - width/2 for x in x_indices], count["平日"], width, 
            label='平日', color=colors["平日"], alpha=0.7)
    ax2.bar([x + width/2 for x in x_indices], count["土日"], width, 
            label='土日', color=colors["土日"], alpha=0.7)
    
    ax2.set_xticks(tick_indices)
    ax2.set_xticklabels(tick_labels, rotation=45)
    ax2.set_xlabel('入店時刻', fontsize=12)
    ax2.set_ylabel('伝票数（サンプルサイズ）', fontsize=12)
    ax2.set_title('時間帯別の伝票数', fontsize=14)
    ax2.legend(loc='upper right')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_xlim(0, len(time_slots)-1)
    
    plt.tight_layout()
    plt.savefig("spend_by_time_15min.png", dpi=150, bbox_inches='tight')
    print("\n保存: spend_by_time_15min.png")
    
    # サマリー出力
    print("\n" + "=" * 60)
    print("時間帯別客単価サマリー（1時間単位で集約）")
    print("=" * 60)
    
    print(f"\n{'時刻':>6} {'平日単価':>10} {'平日件数':>8} {'土日単価':>10} {'土日件数':>8}")
    print("-" * 50)
    
    for h in range(10, 23):
        # 1時間分の15分スロットを集約
        weekday_values = []
        weekend_values = []
        for m in [0, 15, 30, 45]:
            slot = f"{h:02d}:{m:02d}"
            weekday_values.extend(data["平日"][slot])
            weekend_values.extend(data["土日"][slot])
        
        wd_avg = np.mean(weekday_values) if weekday_values else 0
        we_avg = np.mean(weekend_values) if weekend_values else 0
        
        print(f"{h:>4}:00 {wd_avg:>10.0f} {len(weekday_values):>8} {we_avg:>10.0f} {len(weekend_values):>8}")
    
    # ピーク時間帯の特徴
    print("\n" + "=" * 60)
    print("ピーク時間帯の客単価比較")
    print("=" * 60)
    
    # ランチ（11-13時）とディナー（18-21時）
    for day_type in ["平日", "土日"]:
        lunch_values = []
        dinner_values = []
        for h in range(11, 14):
            for m in [0, 15, 30, 45]:
                slot = f"{h:02d}:{m:02d}"
                lunch_values.extend(data[day_type][slot])
        for h in range(18, 22):
            for m in [0, 15, 30, 45]:
                slot = f"{h:02d}:{m:02d}"
                dinner_values.extend(data[day_type][slot])
        
        lunch_avg = np.mean(lunch_values) if lunch_values else 0
        dinner_avg = np.mean(dinner_values) if dinner_values else 0
        diff = dinner_avg - lunch_avg
        
        print(f"\n【{day_type}】")
        print(f"  ランチ（11-13時）: {lunch_avg:.0f}円 (n={len(lunch_values)})")
        print(f"  ディナー（18-21時）: {dinner_avg:.0f}円 (n={len(dinner_values)})")
        print(f"  差: +{diff:.0f}円 ({diff/lunch_avg*100:.1f}%)")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
