#!/usr/bin/env python3
"""
売上と相関する様々な要因を探索
複数の軸で散布図を作成
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
VISITS_FILE = "../visits_with_duration.csv"
OCCUPANCY_FILE = "../occupancy_10min.csv"

def main():
    print("売上と相関する要因を探索中...")
    
    weekdays_list = ["月", "火", "水", "木", "金"]
    
    # 1. 日次データを収集
    daily_data = defaultdict(lambda: {
        "sales": 0, "tickets": set(), "weekday": "", "is_weekday": False,
        "lunch_groups": 0, "dinner_groups": 0,
        "total_groups": 0, "total_customers": 0,
        "total_duration": 0, "duration_count": 0,
        "peak_occupancy": 0
    })
    
    # 売上データ収集
    print("売上データを収集中...")
    with open(EATIN_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["H.集計対象営業年月日"]
            ticket_no = row["H.伝票番号"]
            weekday = row["H.曜日"]
            
            daily_data[date]["weekday"] = weekday
            daily_data[date]["is_weekday"] = weekday in weekdays_list
            
            if ticket_no not in daily_data[date]["tickets"]:
                try:
                    sales = int(row["H.小計"])
                    daily_data[date]["sales"] += sales
                    daily_data[date]["tickets"].add(ticket_no)
                except:
                    pass
    
    # 来店・滞在時間データ収集
    print("来店・滞在時間データを収集中...")
    with open(VISITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["営業日"]
            customers = int(row["客数"])
            duration = int(row["滞在時間_分"])
            entry_time = row["入店時刻"]
            
            if duration > 120:  # 外れ値除外
                continue
            
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                hour = dt.hour
                
                daily_data[date]["total_groups"] += 1
                daily_data[date]["total_customers"] += customers
                daily_data[date]["total_duration"] += duration
                daily_data[date]["duration_count"] += 1
                
                if 11 <= hour <= 13:
                    daily_data[date]["lunch_groups"] += 1
                elif 18 <= hour <= 21:
                    daily_data[date]["dinner_groups"] += 1
            except:
                pass
    
    # ピーク時店内人数データ収集
    print("ピーク時店内人数データを収集中...")
    with open(OCCUPANCY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["営業日"]
            count = int(row["店内人数"])
            
            if count > daily_data[date]["peak_occupancy"]:
                daily_data[date]["peak_occupancy"] = count
    
    # 2. 指標を計算
    records = []
    for date, info in daily_data.items():
        if info["sales"] == 0 or info["total_groups"] == 0:
            continue
        
        avg_duration = info["total_duration"] / info["duration_count"] if info["duration_count"] > 0 else 0
        avg_spend_per_group = info["sales"] / info["total_groups"]
        avg_spend_per_customer = info["sales"] / info["total_customers"] if info["total_customers"] > 0 else 0
        
        records.append({
            "date": date,
            "weekday": info["weekday"],
            "is_weekday": info["is_weekday"],
            "sales": info["sales"] / 10000,  # 万円
            "total_groups": info["total_groups"],
            "total_customers": info["total_customers"],
            "lunch_groups": info["lunch_groups"],
            "dinner_groups": info["dinner_groups"],
            "avg_duration": avg_duration,
            "peak_occupancy": info["peak_occupancy"],
            "avg_spend_per_group": avg_spend_per_group,
            "avg_spend_per_customer": avg_spend_per_customer,
            "dinner_ratio": info["dinner_groups"] / info["total_groups"] if info["total_groups"] > 0 else 0
        })
    
    # 平日のみ抽出
    weekday_records = [r for r in records if r["is_weekday"]]
    
    # 3. 各要因と売上の相関を計算
    print("\n" + "=" * 70)
    print("売上との相関係数（平日のみ）")
    print("=" * 70)
    
    sales = [r["sales"] for r in weekday_records]
    
    factors = [
        ("総来店組数", [r["total_groups"] for r in weekday_records]),
        ("総来店客数", [r["total_customers"] for r in weekday_records]),
        ("ランチ組数", [r["lunch_groups"] for r in weekday_records]),
        ("ディナー組数", [r["dinner_groups"] for r in weekday_records]),
        ("ディナー比率", [r["dinner_ratio"] for r in weekday_records]),
        ("平均滞在時間", [r["avg_duration"] for r in weekday_records]),
        ("ピーク店内人数", [r["peak_occupancy"] for r in weekday_records]),
        ("組単価", [r["avg_spend_per_group"] for r in weekday_records]),
        ("客単価", [r["avg_spend_per_customer"] for r in weekday_records]),
    ]
    
    correlations = []
    print(f"\n{'要因':<15} {'相関係数':>10}")
    print("-" * 30)
    for name, values in factors:
        corr = np.corrcoef(sales, values)[0, 1]
        correlations.append((name, corr, values))
        print(f"{name:<15} {corr:>10.3f}")
    
    # 相関の高い順にソート
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # 4. 上位6つの要因で散布図を作成
    print("\n散布図を作成中...")
    
    top_factors = correlations[:6]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, (name, corr, values) in enumerate(top_factors):
        ax = axes[idx]
        
        # 散布図
        ax.scatter(values, sales, alpha=0.4, s=30, c='#2196F3')
        
        # 回帰直線
        z = np.polyfit(values, sales, 1)
        x_line = np.linspace(min(values), max(values), 100)
        ax.plot(x_line, z[0]*x_line + z[1], 'r--', linewidth=2)
        
        ax.set_xlabel(name, fontsize=11)
        ax.set_ylabel('1日売上（万円）', fontsize=11)
        ax.set_title(f'{name} vs 売上\n相関: {corr:.3f}', fontsize=12)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('売上と相関する要因（平日、相関の高い順）', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("sales_factor_exploration.png", dpi=150, bbox_inches='tight')
    print("保存: sales_factor_exploration.png")
    
    # 5. 2軸で色分けした散布図（最も分離がきれいになる組み合わせを探す）
    print("\n2軸組み合わせで分離度を探索中...")
    
    # 売上の中央値で上位/下位を分類
    median_sales = np.median(sales)
    high_sales = [r for r in weekday_records if r["sales"] > median_sales]
    low_sales = [r for r in weekday_records if r["sales"] <= median_sales]
    
    fig2, axes2 = plt.subplots(2, 2, figsize=(14, 14))
    
    # 組み合わせ1: ディナー組数 vs ランチ組数（売上で色分け）
    ax = axes2[0, 0]
    ax.scatter([r["lunch_groups"] for r in low_sales], 
               [r["dinner_groups"] for r in low_sales],
               alpha=0.5, s=40, c='#2196F3', label=f'売上下位（≤{median_sales:.0f}万円）')
    ax.scatter([r["lunch_groups"] for r in high_sales], 
               [r["dinner_groups"] for r in high_sales],
               alpha=0.5, s=40, c='#E53935', label=f'売上上位（>{median_sales:.0f}万円）')
    ax.set_xlabel('ランチ組数', fontsize=11)
    ax.set_ylabel('ディナー組数', fontsize=11)
    ax.set_title('ランチ組数 vs ディナー組数', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 組み合わせ2: 総来店組数 vs 組単価
    ax = axes2[0, 1]
    ax.scatter([r["total_groups"] for r in low_sales], 
               [r["avg_spend_per_group"] for r in low_sales],
               alpha=0.5, s=40, c='#2196F3', label=f'売上下位')
    ax.scatter([r["total_groups"] for r in high_sales], 
               [r["avg_spend_per_group"] for r in high_sales],
               alpha=0.5, s=40, c='#E53935', label=f'売上上位')
    ax.set_xlabel('総来店組数', fontsize=11)
    ax.set_ylabel('組単価（円）', fontsize=11)
    ax.set_title('総来店組数 vs 組単価', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 組み合わせ3: ピーク店内人数 vs ディナー組数
    ax = axes2[1, 0]
    ax.scatter([r["peak_occupancy"] for r in low_sales], 
               [r["dinner_groups"] for r in low_sales],
               alpha=0.5, s=40, c='#2196F3', label=f'売上下位')
    ax.scatter([r["peak_occupancy"] for r in high_sales], 
               [r["dinner_groups"] for r in high_sales],
               alpha=0.5, s=40, c='#E53935', label=f'売上上位')
    ax.set_xlabel('ピーク店内人数', fontsize=11)
    ax.set_ylabel('ディナー組数', fontsize=11)
    ax.set_title('ピーク店内人数 vs ディナー組数', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 組み合わせ4: 平均滞在時間 vs 総来店組数
    ax = axes2[1, 1]
    ax.scatter([r["avg_duration"] for r in low_sales], 
               [r["total_groups"] for r in low_sales],
               alpha=0.5, s=40, c='#2196F3', label=f'売上下位')
    ax.scatter([r["avg_duration"] for r in high_sales], 
               [r["total_groups"] for r in high_sales],
               alpha=0.5, s=40, c='#E53935', label=f'売上上位')
    ax.set_xlabel('平均滞在時間（分）', fontsize=11)
    ax.set_ylabel('総来店組数', fontsize=11)
    ax.set_title('平均滞在時間 vs 総来店組数', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('売上上位/下位の2軸分布（平日）', fontsize=14)
    plt.tight_layout()
    plt.savefig("sales_2d_separation.png", dpi=150, bbox_inches='tight')
    print("保存: sales_2d_separation.png")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
