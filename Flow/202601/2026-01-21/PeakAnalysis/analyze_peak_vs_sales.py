#!/usr/bin/env python3
"""
ピーク時来店数 vs 1日売上の散布図
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

EATIN_FILE = "../transformed_pos_data_eatin.csv"
VISITS_FILE = "../visits_with_duration.csv"

def main():
    print("ピーク時来店数 vs 1日売上の分析を開始...")
    
    weekdays_list = ["月", "火", "水", "木", "金"]
    weekends_list = ["土", "日"]
    
    # 1. 日次売上を計算（伝票単位でユニーク化して小計を合計）
    print("日次売上を計算中...")
    daily_sales = defaultdict(lambda: {"sales": 0, "tickets": set(), "weekday": ""})
    
    with open(EATIN_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["H.集計対象営業年月日"]
            ticket_no = row["H.伝票番号"]
            weekday = row["H.曜日"]
            
            # 伝票単位で売上を取得（重複防止）
            if ticket_no not in daily_sales[date]["tickets"]:
                try:
                    sales = int(row["H.小計"])
                    daily_sales[date]["sales"] += sales
                    daily_sales[date]["tickets"].add(ticket_no)
                    daily_sales[date]["weekday"] = weekday
                except:
                    pass
    
    print(f"  営業日数: {len(daily_sales)}")
    
    # 2. ピーク時間帯（12時台）の来店組数を計算
    print("ピーク時来店組数を計算中...")
    peak_visits = defaultdict(int)  # date -> 12時台の来店組数
    
    with open(VISITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["営業日"]
            entry_time = row["入店時刻"]
            
            try:
                dt = datetime.strptime(entry_time, "%Y/%m/%d %H:%M:%S")
                if dt.hour == 12:  # 12時台のみ
                    peak_visits[date] += 1
            except:
                pass
    
    # 3. データを統合
    data = {"平日": {"x": [], "y": [], "dates": []}, 
            "土日": {"x": [], "y": [], "dates": []}}
    
    for date, info in daily_sales.items():
        if date not in peak_visits:
            continue
        
        sales = info["sales"]
        peak = peak_visits[date]
        weekday = info["weekday"]
        
        day_type = "平日" if weekday in weekdays_list else "土日"
        data[day_type]["x"].append(peak)
        data[day_type]["y"].append(sales / 10000)  # 万円単位
        data[day_type]["dates"].append(date)
    
    print(f"  平日: {len(data['平日']['x'])}日")
    print(f"  土日: {len(data['土日']['x'])}日")
    
    # 4. 散布図作成
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    colors = {"平日": "#2196F3", "土日": "#E53935"}
    
    for idx, day_type in enumerate(["平日", "土日"]):
        ax = axes[idx]
        x = data[day_type]["x"]
        y = data[day_type]["y"]
        
        ax.scatter(x, y, alpha=0.5, color=colors[day_type], s=30)
        
        # 回帰直線
        if len(x) > 1:
            import numpy as np
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(x), max(x), 100)
            ax.plot(x_line, p(x_line), color='black', linestyle='--', linewidth=2, 
                   label=f'回帰直線 (傾き: {z[0]:.2f}万円/組)')
            
            # 相関係数
            corr = np.corrcoef(x, y)[0, 1]
            ax.text(0.05, 0.95, f'相関係数: {corr:.3f}', transform=ax.transAxes, 
                   fontsize=12, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('12時台の来店組数', fontsize=12)
        ax.set_ylabel('1日売上（万円）', fontsize=12)
        ax.set_title(f'{day_type}: ピーク時来店数 vs 1日売上', fontsize=14)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("peak_visits_vs_sales.png", dpi=150, bbox_inches='tight')
    print("\n保存: peak_visits_vs_sales.png")
    
    # 5. サマリー統計
    print("\n" + "=" * 60)
    print("サマリー統計")
    print("=" * 60)
    
    import numpy as np
    
    for day_type in ["平日", "土日"]:
        x = data[day_type]["x"]
        y = data[day_type]["y"]
        
        if len(x) > 1:
            corr = np.corrcoef(x, y)[0, 1]
            z = np.polyfit(x, y, 1)
            
            print(f"\n【{day_type}】")
            print(f"  データ数: {len(x)}日")
            print(f"  ピーク来店組数: 平均 {np.mean(x):.1f}組, 最小 {min(x)}組, 最大 {max(x)}組")
            print(f"  1日売上: 平均 {np.mean(y):.1f}万円, 最小 {min(y):.1f}万円, 最大 {max(y):.1f}万円")
            print(f"  相関係数: {corr:.3f}")
            print(f"  回帰直線: 売上 = {z[0]:.2f} × ピーク来店数 + {z[1]:.1f} (万円)")
            print(f"  → ピーク時に1組増えると、1日売上が約{z[0]*10000:.0f}円増加")
    
    # 6. 上位/下位比較
    print("\n" + "=" * 60)
    print("ピーク来店数 上位10日 vs 下位10日 比較")
    print("=" * 60)
    
    for day_type in ["平日", "土日"]:
        x = data[day_type]["x"]
        y = data[day_type]["y"]
        dates = data[day_type]["dates"]
        
        if len(x) < 20:
            continue
        
        # ソート
        sorted_data = sorted(zip(x, y, dates), key=lambda t: t[0], reverse=True)
        
        top10 = sorted_data[:10]
        bottom10 = sorted_data[-10:]
        
        top10_avg_peak = np.mean([t[0] for t in top10])
        top10_avg_sales = np.mean([t[1] for t in top10])
        bottom10_avg_peak = np.mean([t[0] for t in bottom10])
        bottom10_avg_sales = np.mean([t[1] for t in bottom10])
        
        print(f"\n【{day_type}】")
        print(f"  上位10日: ピーク平均 {top10_avg_peak:.1f}組 → 売上平均 {top10_avg_sales:.1f}万円")
        print(f"  下位10日: ピーク平均 {bottom10_avg_peak:.1f}組 → 売上平均 {bottom10_avg_sales:.1f}万円")
        print(f"  差: ピーク +{top10_avg_peak - bottom10_avg_peak:.1f}組 → 売上 +{top10_avg_sales - bottom10_avg_sales:.1f}万円")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
