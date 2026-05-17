# TZ/日付境界バグ 全体修正 — テスト計画 v1

- **作成日**: 2026-05-18
- **対象**: 監査レポート `TZ日付バグ全体監査_v1.md` で挙がった 26 件 (Critical 5 / High 8 / Medium 6 / Low 4 / 確認のみ 3)
- **ブランチ**: `feat/business-day-cutoff` 継続
- **方針**: テスト先行 (Red → Green) で各バグを潰す。**全テストは TZ=UTC / TZ=Asia/Tokyo / TZ=America/Los_Angeles の3パターンで緑になること**を必須条件とする。

---

## 0. テスト全体戦略

| レイヤ | テスト形態 | ツール | TZマトリックス |
|---|---|---|---|
| 純粋関数 (utils, calculator) | unit | vitest | ★必須 |
| Prisma リポジトリ | unit + 軽い integration | vitest + モック | UTC / JST のみ (mock なので LA は冗長) |
| API ルート | unit (vi.mock) | vitest | UTC / JST |
| クライアントロジック (純粋関数部) | unit | vitest | 3 TZ |
| クライアントコンポーネント描画 | smoke | dev ブラウザ目視 | JST (= 本番) |
| データ整合 (本番コピー) | manual | dev DB + AirMate | JST |

### TZマトリックス実行ルール

```bash
# 各修正ごとに3パターン緑にする
for tz in UTC Asia/Tokyo America/Los_Angeles; do
  TZ=$tz pnpm vitest run <該当テスト> || exit 1
done
```

CI には別PRで matrix を追加。本PRでは手動で3パターン回す。

---

## 1. Critical (5件)

### 1.1 attendance — 勤怠時刻計算の TZ 非依存化

**バグ**: `record.startTime.getHours()` が runtime TZ で読まれる。

**テスト計画**:

1. **新ユニットテスト** `__tests__/api/trends/attendance-hours.test.ts`:
   - `startTime=2026-05-01T13:00Z` (JST 22:00), `endTime=2026-05-01T17:00Z` (JST 翌02:00) → **4h**
   - `startTime=2026-04-30T15:00Z` (JST 5/1 00:00), `endTime=2026-05-01T05:00Z` (JST 5/1 14:00) → **14h**
   - `endTime - startTime` (timestamp 差分) で計算
   - 3 TZ で同じ結果になるか
   - 既存の `workHours` プロパティが設定済みの場合は優先される (回帰テスト)

2. **期待**:
   - 1.1 修正前: `TZ=UTC` で深夜跨ぎシフトが 0 時間計上される (ケースによる)
   - 1.1 修正後: timestamp 差分で常に正

---

### 1.2 & 2.6 — 日報の "今日" を営業日付化

**バグ**: `new Date().toISOString().split('T')[0]` (UTC暦日) を保存・表示。

**テスト計画**:

1. **新ユニットテスト** `__tests__/utils/businessDate.test.ts` に追加:
   - `todayBusinessDate(5, new Date('2026-05-01T15:30:00Z'))` (= JST 5/2 00:30) → `'2026-05-01'`
   - `todayBusinessDate(5, new Date('2026-04-30T19:59:59Z'))` (= JST 5/1 04:59:59) → `'2026-04-30'`
   - `todayBusinessDate(0, ...)` (暦日基準) と異なることを確認

2. **API ユニットテスト** `__tests__/api/today/route.test.ts` (新規エンドポイント):
   - storeId + cutoffHour=5 → `{ today: '2026-04-30' }` (JST 5/1 0:30 のとき)
   - storeId + cutoffHour=0 → `{ today: '2026-05-01' }`

3. **クライアント側**:
   - ページ表示のスナップショットテストは省略 (ブラウザでの目視確認に委ねる)
   - dev サーバで JST 0:00-5:00 のクロックを差し替えて手動確認 (オプション)

---

### 1.3 calculateWeeks — 週月曜日算出の TZ 非依存化

**バグ**: local-TZ Date の `getDay()/setDate()` で月曜算出。

**テスト計画**:

1. **新ユニットテスト** `__tests__/analytics/calculateWeeks.test.ts`:
   - 入力: `dailyData = [{date: '2026-04-01', ...}, {date: '2026-04-30', ...}, ...]` (4月の各日)
   - 期待: 第1週 start='2026-03-30' (月), end='2026-04-05' (日)
   - 3 TZ で同じ結果
   - 月またぎ・年またぎケース

2. **回帰テスト**:
   - 入力: `[{date: '2025-12-29'}, {date: '2026-01-01'}, ...]`
   - 期待: 第1週 start='2025-12-29' (月)

---

### 1.4 dashboard frontend weeks — 同上 (フロント版)

**バグ**: 1.3 と同パターンが `app/store/[storeId]/dashboard/[month]/page.tsx` にコピペで存在。

**テスト計画**:

1. **計算ロジックを `lib/utils/dashboardWeeks.ts` に抽出してテスト**:
   - フロントから呼べる純粋関数として切り出し
   - `__tests__/utils/dashboardWeeks.test.ts` で 3 TZ テスト
   - ページ側からは抽出した関数を呼ぶだけにする (描画ロジックは残す)

---

### 1.5 & 2.2 dailyStoreSummary — 月レンジ / 最新サマリの半開区間化

**バグ**: `{ gte, lte: monthEnd }` で月末日のみ含む。半開区間ではない。

**テスト計画**:

1. **新ユニットテスト** `__tests__/repositories/dailyStoreSummary.test.ts` (Prisma モック):
   - `getSummariesByMonth('2026-04')` → `prisma.findMany` が `{ gte: '2026-04-01T00:00:00Z', lt: '2026-05-01T00:00:00Z' }` で呼ばれることを assert
   - `getLatestSummary('2026-04-30')` → `{ lt: '2026-05-01T00:00:00Z' }` (= 当日含む半開区間)

2. **回帰テスト**:
   - 月末日のレコードが含まれること (`'2026-04-30'`)
   - 翌月初日のレコードが含まれないこと (`'2026-05-01'`)

---

## 2. High (8件)

### 2.1 dailyReportRepository.getRecentReports
### 2.3 plDailyRepository (Range系2関数)
### 2.4 line/sales-context.getRecentDailySummaries

**バグ**: 全部 `gte + lte` (両端 inclusive) で半開区間ではない。

**テスト計画**:

1. **共通**: 各リポジトリ関数を Prisma モックで呼び、`findMany` の where 引数が `{ gte, lt }` の半開区間になっていることを assert
2. **回帰**: 月末・週末境界のレコード取得が正しいこと

### 2.5 pl/dashboard "today" / 2.7 getCurrentYearMonth

**バグ**: `new Date().toISOString().split('T')[0]` (UTC暦日) と `new Date().getMonth()+1` (local TZ)。

**テスト計画**:

1. `getCurrentYearMonth()` を `todayBusinessDate(cutoff).slice(0,7)` に置き換えた版をユーティリティ化 → unit test 3 TZ
2. ページ自体は描画なので smoke test (dev ブラウザ目視)

### 2.8 parseDateTime / 2.9 getDayOfWeekJa / getWeekStart / getWeekEnd

**バグ**: `setHours()` / `getDay()` で local TZ。

**テスト計画**:

1. **`parseDateTime`** を `parseJSTtoUTC` のラッパに変える (元々 JST 文字列前提だった可能性が高い) → unit test
2. **`getDayOfWeekJa`** に Date 引数を渡したとき、UTC 解釈で曜日を返すか:
   - `getDayOfWeekJa(new Date('2026-05-01T00:00:00Z'))` → `'金'` (UTC で 5/1 は金曜)
3. **`getWeekStart` / `getWeekEnd`** は使用箇所を grep し、誰も使っていなければ削除。使われていれば UTC 系 API に置き換え + unit test。

---

## 3. Medium (6件)

### 3.2 airregiParser.getDayOfWeek

**テスト計画**:

1. unit test: `new Date('2026-05-03').getUTCDay()` → 0 (日曜) になることを確認
2. `getUTCDay()` に置換するだけ

### 3.4 HolidayCalendar today マーカー

**テスト計画**:

1. ロジック部 (今日判定) を純粋関数化 → unit test
2. React コンポーネント自体は smoke test

### 3.5/3.6 曜日ラベル (DailyStoreSummaryCard, pl/daily-reports)

**テスト計画**:

1. `formatDateLabel('2026-05-01')` → `'5/1（金）'`
2. `dayOfWeekUTC` を使う実装に置き換え → unit test

### 3.7 pl/daily, pl/daily-reports formatDate(new Date())

**テスト計画**:

1. クライアント側で `todayBusinessDate(cutoff)` を呼べるよう、`/api/today` 経由でサーバから受け取る
2. もしくは `formatUTCtoJST(new Date(),'date')` で JST 暦日に最低限合わせる
3. 初期値テストは smoke test に委譲

---

## 4. Low / 確認のみ (4 + 3件)

### 4.1/4.2 weekly/monthly Report Repository

- **対応**: スキーマコメント追加のみ。テスト追加なし。

### 4.3 parseVisitDate / 4.4 uploadedAt

- **対応**: 不要。確認のみ。

### 確認のみ (3件)

- 旧バグ再現スクリプト・デモ生成・既存テスト
- **対応**: コメント追記のみ。

---

## 5. 横断対策

### 5.1 `/api/today` エンドポイント新設

**テスト計画**:
- `__tests__/api/today/route.test.ts`:
  - GET /api/today?storeId=bfa-001 → `{ today: 'YYYY-MM-DD', cutoffHour: 5 }`
  - storeId 不正 → 400
  - 認証なし → 401

### 5.2 ESLint ルール強化

**追加候補** (`.eslintrc.json` の `no-restricted-syntax`):

```jsonc
{
  "selector": "CallExpression[callee.property.name=/^(getDay|getDate|getMonth|getFullYear|getHours|getMinutes|getSeconds)$/]",
  "message": "Date.getXxx() は local TZ 依存。getUTCXxx() か lib/utils/businessDate.ts のヘルパを使うこと"
},
{
  "selector": "CallExpression[callee.property.name=/^(setDate|setMonth|setFullYear|setHours)$/]",
  "message": "Date.setXxx() は local TZ 依存。setUTCXxx() か addBusinessDays() を使うこと"
},
{
  "selector": "MemberExpression[object.name='Date'][property.name='parse']",
  "message": "Date.parse はTZ曖昧。parseJSTtoUTC か '...+09:00' を明示すること"
}
```

**override で許容** (これまで通り `scripts/`, `__tests__/`, `lib/demo/`, `lib/utils/businessDate.ts`, `lib/utils/date.ts`, `lib/csv/mapper.ts`, `lib/csv/transformer.ts`)。

**さらに追加**: 既存のコード (ジェネレータ・CSVパーサなど) で `getUTCXxx` を使うべき箇所はinline 修正。

### 5.3 CI matrix (本PRでは未実装、別PRで導入)

`.github/workflows/test.yml` 想定:
```yaml
strategy:
  matrix:
    tz: [UTC, Asia/Tokyo, America/Los_Angeles]
steps:
  - run: TZ=${{matrix.tz}} pnpm test
```

---

## 6. 実行順序

| Phase | 内容 | 検証 |
|---|---|---|
| 0 | テスト計画レビュー (本書) | — |
| **1** | **`lib/utils/date.ts` の修正** (parseDateTime, getDayOfWeekJa, getWeekStart/End, getMonthEnd rename) + 既存テスト緑維持 | 3 TZ vitest |
| **2** | **Critical 1.1** 勤怠 timestamp 差分 + 新テスト | 3 TZ vitest |
| **3** | **Critical 1.5/2.2** dailyStoreSummary 半開区間 + 新テスト | 3 TZ vitest |
| **4** | **Critical 1.3** analytics calculateWeeks 文字列ベース化 + 新テスト | 3 TZ vitest |
| **5** | **Critical 1.4** dashboard ページ週ロジック抽出 + 新テスト | 3 TZ vitest |
| **6** | **Critical 1.2/2.6** daily-report today + `/api/today` 追加 + 新テスト | 3 TZ vitest + dev ブラウザ |
| **7** | **High 2.1/2.3/2.4** 各 repository の gte+lte → gte+lt | 3 TZ vitest |
| **8** | **High 2.5/2.7** pl/dashboard, pl/monthly の getCurrentYearMonth | 3 TZ vitest + dev ブラウザ |
| **9** | **Medium 3.2/3.4/3.5/3.6/3.7** 各 UI/曜日修正 | 3 TZ vitest |
| **10** | **横断**: ESLint ルール強化 (壊れた箇所が無いか lint で全件チェック) | lint 緑 |
| **11** | **回帰**: 一次調査時の `5/1 ¥48,870 / 11人` が dev で再現するか確認 | dev ブラウザ |
| **12** | **コミット**: Critical / High / Medium / 横断 の4コミット | git log |

---

## 7. 受入基準 (Done definition)

- [ ] `__tests__/` 配下に **本 PR 由来の新規テスト約 25 件**追加
- [ ] `TZ=UTC pnpm test` / `TZ=Asia/Tokyo pnpm test` / `TZ=America/Los_Angeles pnpm test` の **3つすべてで全テスト緑**
- [ ] `pnpm lint` 緑 (ESLint 新ルール含む)
- [ ] `pnpm exec tsc --noEmit` で `lib/`/`app/`/`components/` から TS エラーが消えている
- [ ] dev ブラウザで http://127.0.0.1:3000/store/bfa-verify/dashboard/2026-05?sheet=home の 5/1 = ¥48,870 / 11人 が表示されている
- [ ] 本書に挙がった 26 件中 Low / 確認のみ 7 件を除く **19 件すべてに対応コミットまたは修正記録**がある
