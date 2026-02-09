# 日程管理：BUSYブロック依頼フォーマット

このプロジェクトでは **Googleカレンダー（`work`）に `BUSY` 固定**で予定を入れます。

## 依頼テンプレ（コピペ用）

```yaml
calendar: work
title: BUSY
timezone: Asia/Tokyo
blocks:
  - start: "2026-02-10 13:00"
    end:   "2026-02-10 14:30"
  - start: "2026-02-11 09:00"
    end:   "2026-02-11 12:00"
```

## 定期予定（繰り返し）も可能

Googleカレンダー標準の **RRULE** で繰り返し指定できます。

```yaml
calendar: work
title: BUSY
timezone: Asia/Tokyo
blocks:
  - start: "2026-02-10 09:00"
    end:   "2026-02-10 10:00"
    rrule: "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
    until: "2026-03-31"
```

## 週次 / 隔週（これだけでOK）

RRULEを覚えなくても、`repeat` だけで指定できます。

```yaml
calendar: work
title: BUSY
timezone: Asia/Tokyo
blocks:
  - start: "2026-02-10 09:00"
    end:   "2026-02-10 10:00"
    repeat: weekly     # weekly | biweekly
    until: "2026-03-31"
```

## ルール
- `calendar`: 表示名（今回は `work` 固定）
- `title`: `BUSY` 固定
- `timezone`: 既定は `Asia/Tokyo`（変える場合だけ指定）
- `start/end`: `"YYYY-MM-DD HH:MM"`（24時間表記）
- `repeat`: `weekly` / `biweekly`（週次/隔週ショートカット）
- `rrule`: RRULE（例: `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR`）
- `until`: `YYYY-MM-DD`（その日まで繰り返し）

