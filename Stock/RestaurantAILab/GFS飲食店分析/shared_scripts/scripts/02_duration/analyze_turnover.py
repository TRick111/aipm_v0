#!/usr/bin/env python3
"""
回転率分析用データ生成スクリプト
- 伝票単位で滞在時間を計算
- 10分刻みの店内人数を算出
"""

import argparse
import csv
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

ENCODING = "utf-8"

def parse_datetime(s):
    """日時文字列をパース"""
    try:
        return datetime.strptime(s, "%Y/%m/%d %H:%M:%S")
    except:
        return None

def get_10min_slot(dt):
    """10分刻みのスロットを取得（例: 11:27 -> 11:20）"""
    return dt.replace(minute=(dt.minute // 10) * 10, second=0, microsecond=0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store-root", default=".", help="店舗ルート（data/charts/reportsを含む）")
    parser.add_argument(
        "--input",
        default=None,
        help="BIFTEKI互換の中間CSV（未指定なら <store-root>/data/intermediate/transformed_pos_data_eatin.csv）",
    )
    parser.add_argument(
        "--out-visits",
        default=None,
        help="滞在時間付きvisit CSV出力（未指定なら <store-root>/data/intermediate/visits_with_duration.csv）",
    )
    parser.add_argument(
        "--out-occupancy",
        default=None,
        help="10分刻みoccupancy CSV出力（未指定なら <store-root>/data/intermediate/occupancy_10min.csv）",
    )
    parser.add_argument(
        "--max-duration-minutes",
        type=int,
        default=None,
        help="滞在時間の上限（分）。指定した場合、退店時刻を entry+上限 にクリップして回転率/occupancyの外れ値を抑える。",
    )
    args = parser.parse_args()

    store_root = Path(args.store_root)
    input_path = Path(args.input) if args.input else store_root / "data/intermediate/transformed_pos_data_eatin.csv"
    out_visits = Path(args.out_visits) if args.out_visits else store_root / "data/intermediate/visits_with_duration.csv"
    out_occupancy = (
        Path(args.out_occupancy) if args.out_occupancy else store_root / "data/intermediate/occupancy_10min.csv"
    )
    out_visits.parent.mkdir(parents=True, exist_ok=True)
    out_occupancy.parent.mkdir(parents=True, exist_ok=True)

    print(f"読み込み中: {input_path}")
    with open(input_path, "r", encoding=ENCODING) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"  総行数: {len(rows)}")
    
    # 1. 伝票単位でユニーク化
    print("\n伝票単位でユニーク化中...")
    visits = {}  # 伝票番号 -> {入店, 退店, 客数, 曜日, 営業日}
    
    for row in rows:
        ticket_no = row["H.伝票番号"]
        if ticket_no not in visits:
            entry_time = parse_datetime(row["H.伝票発行日"])
            exit_time = parse_datetime(row["H.伝票処理日"])
            
            if entry_time and exit_time:
                duration_sec = (exit_time - entry_time).total_seconds()
                duration_min_raw = int(duration_sec / 60)

                # 外れ値対策: 滞在時間を上限でクリップ（翌日精算などで極端に長くなるケースを抑える）
                exit_time_used = exit_time
                duration_min = duration_min_raw
                if args.max_duration_minutes is not None and duration_min_raw > args.max_duration_minutes:
                    duration_min = args.max_duration_minutes
                    exit_time_used = entry_time + timedelta(minutes=args.max_duration_minutes)
                
                visits[ticket_no] = {
                    "伝票番号": ticket_no,
                    "営業日": row["H.集計対象営業年月日"],
                    "曜日": row["H.曜日"],
                    "入店時刻": row["H.伝票発行日"],
                    "退店時刻": row["H.伝票処理日"],
                    "客数": int(row["H.客数（合計）"]),
                    "滞在時間_分_raw": duration_min_raw,
                    "滞在時間_分": duration_min,
                    "entry_dt": entry_time,
                    "exit_dt": exit_time_used
                }
    
    print(f"  伝票数（組数）: {len(visits)}")
    
    # 滞在時間の統計
    durations = [v["滞在時間_分"] for v in visits.values()]
    avg_duration = sum(durations) / len(durations)
    print(f"  平均滞在時間: {avg_duration:.1f}分")
    print(f"  最短: {min(durations)}分, 最長: {max(durations)}分")
    
    # 2. 滞在時間付きデータを出力
    print(f"\n出力中: {out_visits}")
    fieldnames = ["伝票番号", "営業日", "曜日", "入店時刻", "退店時刻", "客数", "滞在時間_分_raw", "滞在時間_分"]
    with open(out_visits, "w", encoding=ENCODING, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for v in visits.values():
            writer.writerow(v)
    
    # 3. 10分刻みの店内人数を計算
    print("\n10分刻みの店内人数を計算中...")
    
    # 各営業日の時間範囲を特定
    days = defaultdict(list)  # 営業日 -> [visits]
    for v in visits.values():
        days[v["営業日"]].append(v)
    
    # 10分刻みの店内人数を格納
    occupancy_data = []  # [{営業日, 曜日, 時刻, 店内人数}, ...]
    
    for day, day_visits in sorted(days.items()):
        if not day_visits:
            continue
        
        # この日の曜日を取得
        weekday = day_visits[0]["曜日"]
        
        # この日の最小・最大時刻を特定
        min_time = min(v["entry_dt"] for v in day_visits)
        max_time = max(v["exit_dt"] for v in day_visits)
        
        # 開始・終了を10分刻みに調整
        start_slot = get_10min_slot(min_time)
        end_slot = get_10min_slot(max_time) + timedelta(minutes=10)
        
        # 各10分スロットで店内人数をカウント
        current_slot = start_slot
        while current_slot <= end_slot:
            # この時刻に店内にいる人数をカウント
            # 条件: 入店時刻 <= current_slot < 退店時刻
            count = 0
            for v in day_visits:
                if v["entry_dt"] <= current_slot < v["exit_dt"]:
                    count += v["客数"]
            
            occupancy_data.append({
                "営業日": day,
                "曜日": weekday,
                "時刻": current_slot.strftime("%H:%M"),
                # 営業日ラベルと整合するよう、日付は「営業日」を採用する（current_slotは翌日に跨ると日付がズレる）
                "時刻_datetime": f"{day} {current_slot.strftime('%H:%M')}",
                "店内人数": count
            })
            
            current_slot += timedelta(minutes=10)
    
    # 4. 店内人数データを出力
    print(f"出力中: {out_occupancy}")
    fieldnames = ["営業日", "曜日", "時刻", "時刻_datetime", "店内人数"]
    with open(out_occupancy, "w", encoding=ENCODING, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(occupancy_data)
    
    print(f"  営業日数: {len(days)}")
    print(f"  10分スロット数: {len(occupancy_data)}")
    
    # 5. 曜日別サマリーも出力
    print("\n曜日別サマリー:")
    weekday_stats = defaultdict(lambda: {"count": 0, "total_duration": 0, "total_customers": 0})
    for v in visits.values():
        wd = v["曜日"]
        weekday_stats[wd]["count"] += 1
        weekday_stats[wd]["total_duration"] += v["滞在時間_分"]
        weekday_stats[wd]["total_customers"] += v["客数"]
    
    weekday_order = ["月", "火", "水", "木", "金", "土", "日"]
    for wd in weekday_order:
        if wd in weekday_stats:
            stats = weekday_stats[wd]
            avg_dur = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
            print(f"  {wd}: 組数={stats['count']}, 客数={stats['total_customers']}, 平均滞在={avg_dur:.1f}分")
    
    print("\n完了!")
    print(f"  {out_visits}: 伝票単位の滞在時間データ")
    print(f"  {out_occupancy}: 10分刻み店内人数（曜日・時刻でグループ化分析用）")

if __name__ == "__main__":
    main()
