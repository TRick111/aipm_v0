# gcal_busy_blocker（WIP）

Google公式の **Google Calendar API + OAuth** を使って、指定カレンダーに `BUSY` 予定を入れる最小ツールです。

## これでできること
- カレンダー一覧の表示（`work` の `calendarId` を特定）
- `work` カレンダーに `BUSY` 予定を1件追加（busyブロック）
- `work` カレンダーに `BUSY` の**定期予定**を追加（繰り返し）

## セットアップ（初回だけ）

### 1) Google Cloud Console 側
- Google Cloudでプロジェクト作成
- **Google Calendar API** を有効化
- OAuthクライアントID作成（推奨: **デスクトップアプリ**）
- `credentials.json` をダウンロードして、このフォルダに配置

### 2) ローカル（Cursorのターミナル）

```bash
cd "/Users/rikutanaka/aipm_v0/Flow/202602/2026-02-07/日程管理/gcal_busy_blocker"
npm install
npm run auth -- --force
```

## 使い方

### カレンダー一覧を出して `work` を探す

```bash
npm run list
```

### `work` に `BUSY` を追加（1件）

```bash
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 13:00" --end="2026-02-10 14:30"
```

### `work` に `BUSY` を追加（定期 / 繰り返し）

- **RRULEで指定**できます（Googleカレンダー標準）。
- よく使うのは「毎週」「平日」「回数」「終了日」です。

#### いちばん簡単（週次 / 隔週）

- `--repeat=weekly` または `--repeat=biweekly` を使うと、RRULEを自動生成します。
- 曜日は未指定の場合、**`start` の曜日**が自動で使われます（例: startが火曜なら `BYDAY=TU`）。

```bash
# 週次（startの曜日で繰り返し）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 09:00" --end="2026-02-10 10:00" --repeat=weekly --until="2026-03-31"

# 隔週（startの曜日で繰り返し）
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 09:00" --end="2026-02-10 10:00" --repeat=biweekly --count=10
```

曜日を固定したい場合は `--byday=MO` / `--byday=MO,TU` を指定できます。

#### 例1: 平日（月〜金）毎週（終了日あり）

```bash
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 09:00" --end="2026-02-10 10:00" --rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR" --until="2026-03-31"
```

#### 例2: 毎週（10回だけ）

```bash
npm run block -- --calendar=work --title=BUSY --timezone=Asia/Tokyo --start="2026-02-10 18:00" --end="2026-02-10 19:00" --rrule="FREQ=WEEKLY;BYDAY=MO" --count=10
```

#### 引数
- `--repeat`: `weekly` or `biweekly`（ショートカット）
- `--byday`: `MO` / `MO,TU`（repeat使用時の曜日上書き）
- `--rrule`: `RRULE:` を除いた中身でもOK（例: `FREQ=WEEKLY;BYDAY=MO`）
- `--until`: `YYYY-MM-DD`（このツールでは **その日の23:59:59(UTC)** までの繰り返しとして扱う簡易実装）
- `--count`: 回数（`--until` と同時指定は不可扱い：RRULE側に書いた場合を優先）

## セキュリティ注意
- `credentials.json` / `token.json` は機密情報です（`.gitignore` 済み）
- 権限（scope）は **`calendar.readonly`（一覧取得） + `calendar.events`（予定作成）** のみにしています

