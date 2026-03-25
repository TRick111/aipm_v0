"""萌さんの水曜日夜の返信時間分析"""

import re
from datetime import datetime, timedelta
from collections import defaultdict

LINE_EXPORT = "/Users/rikutanaka/aipm_v0/Stock/0.Other/萌さん/LINEトーク/2026-03-23_LINE_export.txt"

with open(LINE_EXPORT, "r", encoding="utf-8") as f:
    lines = f.readlines()

messages = []
current_date = None
current_dow = None

date_pattern = re.compile(r"^(\d{4}\.\d{2}\.\d{2})\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)")
msg_pattern = re.compile(r"^(\d{2}:\d{2})\s+(わたなべもえ|田中利空\s+Riku)\s+(.*)")

for line in lines:
    line = line.strip()
    dm = date_pattern.match(line)
    if dm:
        current_date = datetime.strptime(dm.group(1), "%Y.%m.%d")
        current_dow = dm.group(2)
        continue

    mm = msg_pattern.match(line)
    if mm and current_date:
        time_str = mm.group(1)
        sender = "萌" if "わたなべもえ" in mm.group(2) else "利空"
        content = mm.group(3)
        h, m = map(int, time_str.split(":"))
        msg_dt = current_date.replace(hour=h, minute=m)
        messages.append({
            "datetime": msg_dt,
            "date": current_date.date(),
            "dow": current_dow,
            "time": time_str,
            "sender": sender,
            "content": content,
        })

print("=" * 70)
print("萌さんの水曜日のメッセージ（全時間帯）")
print("=" * 70)

wed_messages = [m for m in messages if m["dow"] == "Wednesday"]
wed_dates = sorted(set(m["date"] for m in wed_messages))

for d in wed_dates:
    day_msgs = [m for m in wed_messages if m["date"] == d]
    print(f"\n--- {d} (水) ---")
    for msg in day_msgs:
        marker = "★" if msg["sender"] == "萌" else "  "
        print(f"  {marker} {msg['time']} [{msg['sender']}] {msg['content'][:60]}")

print("\n")
print("=" * 70)
print("萌さんの水曜日「夜」(18:00以降) の返信時間")
print("=" * 70)

for d in wed_dates:
    day_msgs = [m for m in wed_messages if m["date"] == d]
    moe_evening = [m for m in day_msgs if m["sender"] == "萌" and int(m["time"].split(":")[0]) >= 18]
    if moe_evening:
        print(f"\n--- {d} (水) ---")
        for msg in moe_evening:
            print(f"  ★ {msg['time']} {msg['content'][:60]}")
    else:
        print(f"\n--- {d} (水) --- 夜の返信なし")


print("\n")
print("=" * 70)
print("水曜日の会話フロー分析（利空→萌の返信ラグ）")
print("=" * 70)

for d in wed_dates:
    day_msgs = sorted([m for m in wed_messages if m["date"] == d], key=lambda x: x["datetime"])
    print(f"\n--- {d} (水) ---")

    last_riku_time = None
    for msg in day_msgs:
        if msg["sender"] == "利空":
            last_riku_time = msg["datetime"]
        elif msg["sender"] == "萌" and last_riku_time:
            lag = msg["datetime"] - last_riku_time
            lag_mins = int(lag.total_seconds() / 60)
            h = int(msg["time"].split(":")[0])
            evening_tag = " [夜]" if h >= 18 else ""
            print(f"  利空 {last_riku_time.strftime('%H:%M')} → 萌 {msg['time']} (返信ラグ: {lag_mins}分){evening_tag}")
            last_riku_time = None


print("\n")
print("=" * 70)
print("萌さんの水曜夜の返信時刻サマリー")
print("=" * 70)

evening_reply_times = []
for d in wed_dates:
    day_msgs = [m for m in wed_messages if m["date"] == d]
    moe_evening = [m for m in day_msgs if m["sender"] == "萌" and int(m["time"].split(":")[0]) >= 18]
    if moe_evening:
        first_reply = moe_evening[0]
        last_reply = moe_evening[-1]
        evening_reply_times.append({
            "date": d,
            "first": first_reply["time"],
            "last": last_reply["time"],
            "count": len(moe_evening),
        })

print(f"\n{'日付':<15} {'最初の返信':<12} {'最後の返信':<12} {'返信数'}")
print("-" * 55)
for r in evening_reply_times:
    print(f"{str(r['date']):<15} {r['first']:<12} {r['last']:<12} {r['count']}")

if evening_reply_times:
    first_times = [int(r["first"].split(":")[0]) * 60 + int(r["first"].split(":")[1]) for r in evening_reply_times]
    avg_first = sum(first_times) / len(first_times)
    avg_h = int(avg_first // 60)
    avg_m = int(avg_first % 60)
    print(f"\n平均「最初の夜返信」時刻: {avg_h:02d}:{avg_m:02d}")

    print(f"\n勤務スケジュール参考: 水曜は午後〜19:00終")
    print(f"→ 19:00以降にLINEを返す余裕が出るパターンが多いか確認:")

    for r in evening_reply_times:
        h = int(r["first"].split(":")[0])
        if h < 19:
            print(f"  {r['date']}: {r['first']} ← 仕事終了前に返信")
        elif h < 20:
            print(f"  {r['date']}: {r['first']} ← 仕事終了直後 (19時台)")
        elif h < 21:
            print(f"  {r['date']}: {r['first']} ← 仕事終了後1時間以内 (20時台)")
        elif h < 22:
            print(f"  {r['date']}: {r['first']} ← 仕事終了後2時間以内 (21時台)")
        else:
            print(f"  {r['date']}: {r['first']} ← 仕事終了後かなり経ってから (22時以降)")


print("\n")
print("=" * 70)
print("水曜日以外も含めた夜(18時以降)の萌さん初回返信時刻（曜日別比較）")
print("=" * 70)

dow_names = {"Monday": "月", "Tuesday": "火", "Wednesday": "水",
             "Thursday": "木", "Friday": "金", "Saturday": "土", "Sunday": "日"}
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

dow_evening_first = defaultdict(list)

all_dates = sorted(set(m["date"] for m in messages))
for d in all_dates:
    day_msgs = [m for m in messages if m["date"] == d]
    if not day_msgs:
        continue
    dow = day_msgs[0]["dow"]
    moe_evening = [m for m in day_msgs if m["sender"] == "萌" and int(m["time"].split(":")[0]) >= 18]
    if moe_evening:
        first_time = moe_evening[0]["time"]
        mins = int(first_time.split(":")[0]) * 60 + int(first_time.split(":")[1])
        dow_evening_first[dow].append({"date": d, "time": first_time, "mins": mins})

for dow in dow_order:
    entries = dow_evening_first.get(dow, [])
    jp = dow_names[dow]
    if entries:
        avg = sum(e["mins"] for e in entries) / len(entries)
        avg_h, avg_m = int(avg // 60), int(avg % 60)
        print(f"\n{jp}曜日 (データ数: {len(entries)}, 平均初回返信: {avg_h:02d}:{avg_m:02d})")
        for e in entries:
            print(f"  {e['date']}: {e['time']}")
    else:
        print(f"\n{jp}曜日: 夜の返信データなし")
