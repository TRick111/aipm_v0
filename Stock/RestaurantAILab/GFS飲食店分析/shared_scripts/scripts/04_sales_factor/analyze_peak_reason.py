#!/usr/bin/env python3
"""
ランチ vs ディナーの店内人数差の理由を分析
"""

import csv
from collections import defaultdict
from datetime import datetime

VISITS_FILE = "visits_with_duration.csv"

def main():
    # 平日のみ分析
    weekdays = ["月", "火", "水", "木", "金"]
    
    # 時間帯別データ
    lunch_hours = [11, 12, 13]
    dinner_hours = [18, 19, 20, 21]
    
    hourly_data = defaultdict(lambda: {"groups": 0, "customers": 0, "total_duration": 0, "days": set()})
    
    with open(VISITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            weekday = row["曜日"]
            if weekday not in weekdays:
                continue
            
            duration = int(row["滞在時間_分"])
            if duration > 120:  # 外れ値除外
                continue
            
            customers = int(row["客数"])
            date = row["営業日"]
            entry_time = row["入店時刻"]
            
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                hour = dt.hour
                hourly_data[hour]["groups"] += 1
                hourly_data[hour]["customers"] += customers
                hourly_data[hour]["total_duration"] += duration
                hourly_data[hour]["days"].add(date)
            except:
                continue
    
    print("=" * 60)
    print("平日の時間帯別分析（ランチ vs ディナー）")
    print("=" * 60)
    
    print("\n【時間帯別詳細】")
    print(f"{'時刻':>6} {'組数/日':>10} {'客数/日':>10} {'平均滞在':>10} {'組数×滞在':>12}")
    print("-" * 50)
    
    lunch_total = {"groups": 0, "customers": 0, "duration_sum": 0, "days": set()}
    dinner_total = {"groups": 0, "customers": 0, "duration_sum": 0, "days": set()}
    
    for h in range(10, 23):
        data = hourly_data[h]
        num_days = len(data["days"]) if data["days"] else 1
        groups_per_day = data["groups"] / num_days
        customers_per_day = data["customers"] / num_days
        avg_duration = data["total_duration"] / data["groups"] if data["groups"] > 0 else 0
        
        # 組数×滞在時間 = 「人・分」（店内にいる時間の総量）
        load = groups_per_day * avg_duration
        
        marker = ""
        if h in lunch_hours:
            marker = "◆ランチ"
            lunch_total["groups"] += data["groups"]
            lunch_total["customers"] += data["customers"]
            lunch_total["duration_sum"] += data["total_duration"]
            lunch_total["days"].update(data["days"])
        elif h in dinner_hours:
            marker = "◆ディナー"
            dinner_total["groups"] += data["groups"]
            dinner_total["customers"] += data["customers"]
            dinner_total["duration_sum"] += data["total_duration"]
            dinner_total["days"].update(data["days"])
        
        print(f"{h:>4}:00 {groups_per_day:>10.1f} {customers_per_day:>10.1f} {avg_duration:>8.1f}分 {load:>10.0f}  {marker}")
    
    print("\n" + "=" * 60)
    print("【ランチ帯 vs ディナー帯 比較】")
    print("=" * 60)
    
    # ランチ帯合計
    lunch_days = len(lunch_total["days"]) if lunch_total["days"] else 1
    lunch_groups_day = lunch_total["groups"] / lunch_days
    lunch_customers_day = lunch_total["customers"] / lunch_days
    lunch_avg_duration = lunch_total["duration_sum"] / lunch_total["groups"] if lunch_total["groups"] > 0 else 0
    
    # ディナー帯合計
    dinner_days = len(dinner_total["days"]) if dinner_total["days"] else 1
    dinner_groups_day = dinner_total["groups"] / dinner_days
    dinner_customers_day = dinner_total["customers"] / dinner_days
    dinner_avg_duration = dinner_total["duration_sum"] / dinner_total["groups"] if dinner_total["groups"] > 0 else 0
    
    print(f"\n{'指標':<20} {'ランチ(11-13時)':>15} {'ディナー(18-21時)':>15} {'比率':>10}")
    print("-" * 65)
    print(f"{'時間帯の長さ':<20} {'3時間':>15} {'4時間':>15} {'─':>10}")
    print(f"{'来店組数/日':<20} {lunch_groups_day:>15.1f} {dinner_groups_day:>15.1f} {lunch_groups_day/dinner_groups_day:>9.1f}x")
    print(f"{'来店客数/日':<20} {lunch_customers_day:>15.1f} {dinner_customers_day:>15.1f} {lunch_customers_day/dinner_customers_day:>9.1f}x")
    print(f"{'平均滞在時間':<20} {lunch_avg_duration:>13.1f}分 {dinner_avg_duration:>13.1f}分 {lunch_avg_duration/dinner_avg_duration:>9.2f}x")
    
    # 1時間あたりの来店数
    lunch_groups_per_hour = lunch_groups_day / 3
    dinner_groups_per_hour = dinner_groups_day / 4
    
    print(f"\n{'1時間あたり来店組数':<20} {lunch_groups_per_hour:>15.1f} {dinner_groups_per_hour:>15.1f} {lunch_groups_per_hour/dinner_groups_per_hour:>9.1f}x")
    
    print("\n" + "=" * 60)
    print("【結論】")
    print("=" * 60)
    print(f"""
店内人数 = 来店フロー × 平均滞在時間

・ランチ: {lunch_groups_per_hour:.1f}組/時 × {lunch_avg_duration:.0f}分 = {lunch_groups_per_hour * lunch_avg_duration:.0f} 組分/時
・ディナー: {dinner_groups_per_hour:.1f}組/時 × {dinner_avg_duration:.0f}分 = {dinner_groups_per_hour * dinner_avg_duration:.0f} 組分/時

→ ランチは「1時間あたりの来店数」がディナーの{lunch_groups_per_hour/dinner_groups_per_hour:.1f}倍
→ 滞在時間の差（{dinner_avg_duration/lunch_avg_duration:.2f}倍）を大きく上回る
→ 結果、ランチの店内人数がディナーより多くなる
""")

if __name__ == "__main__":
    main()
