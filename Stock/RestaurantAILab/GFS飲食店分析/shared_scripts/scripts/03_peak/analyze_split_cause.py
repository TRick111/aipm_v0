#!/usr/bin/env python3
"""
平日の散布図で上下に分かれる原因を分析
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

def main():
    print("平日の上下分離の原因を分析中...")
    
    weekdays_list = ["月", "火", "水", "木", "金"]
    
    # 1. 日次データを収集
    # 売上、ピーク来店数、ディナー来店数、客単価など
    daily_data = defaultdict(lambda: {
        "sales": 0, "tickets": set(), "weekday": "",
        "lunch_groups": 0, "dinner_groups": 0,
        "lunch_customers": 0, "dinner_customers": 0,
        "total_groups": 0, "total_customers": 0,
        "month": ""
    })
    
    # 売上データ収集
    print("売上データを収集中...")
    with open(EATIN_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["H.集計対象営業年月日"]
            ticket_no = row["H.伝票番号"]
            weekday = row["H.曜日"]
            
            if weekday not in weekdays_list:
                continue
            
            if ticket_no not in daily_data[date]["tickets"]:
                try:
                    sales = int(row["H.小計"])
                    daily_data[date]["sales"] += sales
                    daily_data[date]["tickets"].add(ticket_no)
                    daily_data[date]["weekday"] = weekday
                    # 月を取得
                    dt = datetime.strptime(date, "%Y/%m/%d")
                    daily_data[date]["month"] = dt.strftime("%Y-%m")
                except:
                    pass
    
    # 来店データ収集（時間帯別）
    print("来店データを収集中...")
    with open(VISITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["営業日"]
            weekday = row["曜日"]
            customers = int(row["客数"])
            entry_time = row["入店時刻"]
            
            if weekday not in weekdays_list:
                continue
            
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                hour = dt.hour
                
                daily_data[date]["total_groups"] += 1
                daily_data[date]["total_customers"] += customers
                
                if 11 <= hour <= 13:  # ランチ
                    daily_data[date]["lunch_groups"] += 1
                    daily_data[date]["lunch_customers"] += customers
                elif 18 <= hour <= 21:  # ディナー
                    daily_data[date]["dinner_groups"] += 1
                    daily_data[date]["dinner_customers"] += customers
            except:
                pass
    
    # 2. ピーク来店数でグループ化して、回帰直線からの残差を計算
    print("残差分析中...")
    
    # ピーク来店数（12時台）を再計算
    peak_visits = defaultdict(int)
    with open(VISITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["営業日"]
            entry_time = row["入店時刻"]
            weekday = row["曜日"]
            
            if weekday not in weekdays_list:
                continue
            
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                if dt.hour == 12:
                    peak_visits[date] += 1
            except:
                pass
    
    # データ統合
    records = []
    for date, info in daily_data.items():
        if date not in peak_visits or info["sales"] == 0:
            continue
        
        peak = peak_visits[date]
        sales = info["sales"] / 10000  # 万円
        
        if info["total_groups"] > 0:
            avg_spend = info["sales"] / info["total_groups"]  # 組あたり売上
        else:
            avg_spend = 0
        
        records.append({
            "date": date,
            "weekday": info["weekday"],
            "month": info["month"],
            "sales": sales,
            "peak": peak,
            "lunch_groups": info["lunch_groups"],
            "dinner_groups": info["dinner_groups"],
            "total_groups": info["total_groups"],
            "avg_spend": avg_spend,
            "dinner_ratio": info["dinner_groups"] / info["total_groups"] if info["total_groups"] > 0 else 0
        })
    
    # 回帰直線を計算
    x = [r["peak"] for r in records]
    y = [r["sales"] for r in records]
    z = np.polyfit(x, y, 1)
    
    # 残差を計算（予測値との差）
    for r in records:
        predicted = z[0] * r["peak"] + z[1]
        r["residual"] = r["sales"] - predicted
    
    # 残差で上位/下位に分類
    median_residual = np.median([r["residual"] for r in records])
    
    upper_group = [r for r in records if r["residual"] > median_residual]
    lower_group = [r for r in records if r["residual"] <= median_residual]
    
    print(f"  上位グループ: {len(upper_group)}日")
    print(f"  下位グループ: {len(lower_group)}日")
    
    # 3. 上位/下位グループの特徴を比較
    print("\n" + "=" * 70)
    print("上位グループ vs 下位グループ 比較")
    print("=" * 70)
    
    def group_stats(group, name):
        print(f"\n【{name}】(n={len(group)})")
        print(f"  平均売上: {np.mean([r['sales'] for r in group]):.1f}万円")
        print(f"  平均ピーク来店: {np.mean([r['peak'] for r in group]):.1f}組")
        print(f"  平均ディナー組数: {np.mean([r['dinner_groups'] for r in group]):.1f}組")
        print(f"  平均ディナー比率: {np.mean([r['dinner_ratio'] for r in group])*100:.1f}%")
        print(f"  平均組単価: {np.mean([r['avg_spend'] for r in group]):.0f}円")
        print(f"  平均総来店組数: {np.mean([r['total_groups'] for r in group]):.1f}組")
    
    group_stats(upper_group, "上位グループ（回帰線より上）")
    group_stats(lower_group, "下位グループ（回帰線より下）")
    
    # 4. 曜日別の分布
    print("\n" + "=" * 70)
    print("曜日別の分布")
    print("=" * 70)
    
    print(f"\n{'曜日':>4} {'上位':>8} {'下位':>8} {'上位率':>8}")
    for wd in weekdays_list:
        upper_count = len([r for r in upper_group if r["weekday"] == wd])
        lower_count = len([r for r in lower_group if r["weekday"] == wd])
        total = upper_count + lower_count
        ratio = upper_count / total * 100 if total > 0 else 0
        print(f"{wd:>4} {upper_count:>8} {lower_count:>8} {ratio:>7.1f}%")
    
    # 5. 可視化：ディナー組数で色分け
    print("\n散布図を作成中（ディナー組数で色分け）...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # 左: ディナー組数で色分け
    ax1 = axes[0]
    x_vals = [r["peak"] for r in records]
    y_vals = [r["sales"] for r in records]
    dinner_vals = [r["dinner_groups"] for r in records]
    
    scatter = ax1.scatter(x_vals, y_vals, c=dinner_vals, cmap='RdYlBu_r', 
                          alpha=0.6, s=40, vmin=0, vmax=max(dinner_vals))
    plt.colorbar(scatter, ax=ax1, label='ディナー組数')
    
    # 回帰直線
    x_line = np.linspace(min(x_vals), max(x_vals), 100)
    ax1.plot(x_line, z[0]*x_line + z[1], 'k--', linewidth=2)
    
    ax1.set_xlabel('12時台の来店組数', fontsize=12)
    ax1.set_ylabel('1日売上（万円）', fontsize=12)
    ax1.set_title('ディナー組数で色分け（赤=多い、青=少ない）', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    # 右: 曜日で色分け
    ax2 = axes[1]
    colors = {"月": "#1976D2", "火": "#2196F3", "水": "#4CAF50", "木": "#FF9800", "金": "#E53935"}
    
    for wd in weekdays_list:
        wd_records = [r for r in records if r["weekday"] == wd]
        x_wd = [r["peak"] for r in wd_records]
        y_wd = [r["sales"] for r in wd_records]
        ax2.scatter(x_wd, y_wd, c=colors[wd], alpha=0.5, s=40, label=wd)
    
    ax2.plot(x_line, z[0]*x_line + z[1], 'k--', linewidth=2)
    ax2.set_xlabel('12時台の来店組数', fontsize=12)
    ax2.set_ylabel('1日売上（万円）', fontsize=12)
    ax2.set_title('曜日で色分け', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("split_cause_analysis.png", dpi=150, bbox_inches='tight')
    print("保存: split_cause_analysis.png")
    
    # 6. 相関分析
    print("\n" + "=" * 70)
    print("残差との相関（上下分離の原因特定）")
    print("=" * 70)
    
    residuals = [r["residual"] for r in records]
    
    factors = [
        ("ディナー組数", [r["dinner_groups"] for r in records]),
        ("ディナー比率", [r["dinner_ratio"] for r in records]),
        ("組単価", [r["avg_spend"] for r in records]),
        ("総来店組数", [r["total_groups"] for r in records]),
    ]
    
    print(f"\n{'要因':<15} {'相関係数':>10}")
    print("-" * 30)
    for name, values in factors:
        corr = np.corrcoef(residuals, values)[0, 1]
        print(f"{name:<15} {corr:>10.3f}")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
