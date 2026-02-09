# BUSYスケジュール登録依頼（2026-02-10）

## 依頼内容の整理

### 単発予定
1. **2026-02-10（火）17:00-17:30** - 単発
2. **2026-02-11（水）17:00-18:00** - 単発（1時間）
3. **2026-02-12（木）16:00-17:00** - 単発
4. **2026-02-16（月）15:00-15:30** - 単発

### 毎週予定
1. **平日（月〜金）9:30-10:00** - 毎週
2. **火曜日 17:30-18:00** - 毎週
3. **水曜日 12:00-13:00** - 毎週
4. **水曜日 21:00-22:30** - 毎週
5. **木曜日 15:00-15:30** - 毎週
6. **金曜日 11:00-11:30** - 毎週
7. **金曜日 11:30-12:00** - 毎週

### 隔週予定
1. **火曜日 14:00-14:30** - 隔週（直近は10日スタート）
2. **水曜日 14:00-14:30** - 隔週（18日スタート）
3. **水曜日 15:00-15:30** - 隔週（18日スタート）
4. **水曜日 15:30-16:00** - 隔週（18日スタート）
5. **木曜日 14:00-14:30** - 隔週（20日スタート）

## 実行コマンド

### 単発予定
```bash
# 1. 2026-02-10（火）17:00-17:30
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 17:00" --end="2026-02-10 17:30"

# 2. 2026-02-11（水）17:00-18:00
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-11 17:00" --end="2026-02-11 18:00"

# 3. 2026-02-12（木）16:00-17:00
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-12 16:00" --end="2026-02-12 17:00"

# 4. 2026-02-16（日）15:00-15:30
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-16 15:00" --end="2026-02-16 15:30"
```

### 毎週予定
```bash
# 1. 平日（月〜金）9:30-10:00
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 09:30" --end="2026-02-10 10:00" --rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"

# 2. 火曜日 17:30-18:00
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 17:30" --end="2026-02-10 18:00" --repeat=weekly

# 3. 水曜日 12:00-13:00
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-11 12:00" --end="2026-02-11 13:00" --repeat=weekly

# 4. 水曜日 21:00-22:30
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-11 21:00" --end="2026-02-11 22:30" --repeat=weekly

# 5. 木曜日 15:00-15:30
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-12 15:00" --end="2026-02-12 15:30" --repeat=weekly

# 6. 金曜日 11:00-11:30
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-13 11:00" --end="2026-02-13 11:30" --repeat=weekly

# 7. 金曜日 11:30-12:00
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-13 11:30" --end="2026-02-13 12:00" --repeat=weekly
```

### 隔週予定
```bash
# 1. 火曜日 14:00-14:30（10日スタート）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 14:00" --end="2026-02-10 14:30" --repeat=biweekly

# 2. 水曜日 14:00-14:30（18日スタート）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-18 14:00" --end="2026-02-18 14:30" --repeat=biweekly

# 3. 水曜日 15:00-15:30（18日スタート）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-18 15:00" --end="2026-02-18 15:30" --repeat=biweekly

# 4. 水曜日 15:30-16:00（18日スタート）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-18 15:30" --end="2026-02-18 16:00" --repeat=biweekly

# 5. 木曜日 14:00-14:30（20日スタート）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-20 14:00" --end="2026-02-20 14:30" --repeat=biweekly
```
