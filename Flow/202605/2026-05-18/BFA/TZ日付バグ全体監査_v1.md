# TZ/日付境界バグ 全体監査レポート v1

**監査対象**: `/Users/rikutanaka/RestaurantAILab/Dashboard`
**監査日**: 2026-05-18
**前提**:
- アプリ層は最終的に `TZ=Asia/Tokyo` で動作。DB は UTC 保存。
- `StoreSettings.businessDayCutoffHour` (デフォルト 5) により JST 5:00 が営業日境界。
- `@db.Date` 列 = 営業日付。`@db.Timestamptz` = UTC タイムスタンプ。
- 既に対応済の領域 (businessDate.ts 新設、plDashboardRepository.getMonthRange 修正、
  trends/monthly の visitDate を toBusinessDate 化、data/[month] の visitDate 化、等) は除外。

---

## 0. サマリ

**Critical: 5 件 / High: 8 件 / Medium: 6 件 / Low: 4 件 / 確認のみ: 3 件**

| # | ファイル:行 | パターン | 重要度 | 影響 | 修正方針 |
|---|---|---|---|---|---|
| 1 | app/api/trends/monthly/route.ts:233-236 | B | **Critical** | 勤怠 startTime/endTime を `getHours()/getMinutes()` で読む → TZ=UTC では JST -9h で計算され人件費が誤集計 | `getUTCHours()/getUTCMinutes()` + JST オフセット適用、もしくは `workHours` 列を必須化 |
| 2 | app/daily-report/[storeId]/page.tsx:33 | C | **Critical** | 日報保存日 `today = new Date().toISOString().split('T')[0]` が UTC 暦日 → JST 0:00–8:59 に提出すると **前日付** で DB 保存される | `toBusinessDate(new Date(), cutoffHour)` または最低でも JST 暦日に変換 |
| 3 | lib/analytics/calculator.ts:365-403 (calculateWeeks) | B | **Critical** | `new Date(date)` 後 `getDay()/getDate()/setDate()` を local TZ 系で操作 → 週の Monday 算出/週末算出が TZ で 1 日ズレ。`toISOString().split('T')[0]` も併用しているため UTC 暦日と local 暦日が混在し、月初・月末の週ラベルが誤る | UTC 系 (`getUTCDay/getUTCDate/setUTCDate`) に統一、もしくは 'YYYY-MM-DD' 文字列ベース実装 |
| 4 | app/store/[storeId]/dashboard/[month]/page.tsx:240-265 | B | **Critical** | 同上の "Monday 算出 → weekEnd" を local-TZ Date で実行。`toISOString()` で UTC 暦日に変換した結果を `start/end` として使うため、TZ=Asia/Tokyo + JST 月初の月曜が UTC 前日 (15:00 UTC) としてラベル化される | UTC 系 API に統一、または businessDate.ts の `addBusinessDays` を使った文字列計算 |
| 5 | lib/db/repositories/dailyStoreSummaryRepository.ts:103-109 (getSummariesByMonth) | D + A | **Critical** | `new Date(Date.UTC(year, month, 0))` = 月末日 UTC midnight。Prisma `lte: endDate` で `@db.Date` 列を絞ると、月末日 (00:00:00) ピッタリに保存された行のみ含まれる → 同日 (UTC midnight) を Prisma が日比較する際は OK だが、本来は半開区間 `lt: nextMonthStart` のほうが安全。**より深刻なのは** `salesRepository` 等で `@db.Date` を `@db.Timestamptz` 等とコピーした時にズレが顕在化する点 | `calendarMonthRangeUTC` ヘルパで `{ gte: monthStart, lt: nextMonthStart }` に統一 |
| 6 | lib/db/repositories/dailyReportRepository.ts:138-150 (getRecentReports) | D | **High** | `where: { date: { lte: dateObj } }` で `beforeDate + 'T00:00:00Z'` を使用 → "指定日以前" として `beforeDate` 当日を含む意図だが、`@db.Date` の比較で `dateObj` = UTC midnight ぴったりに保存された行のみ含まれる。当日分の取得意図と整合するが、半開区間で書くべき | `{ lt: tomorrowUTC }` に変更 (`tomorrowUTC = dateObj + 1day`) |
| 7 | lib/db/repositories/dailyStoreSummaryRepository.ts:79-85 (getLatestSummary) | D | **High** | 同上 (`lte: dateObj`) — "指定日以前の最新" を取得する関数だが、当日含意が曖昧 | 半開区間 `lt: tomorrowUTC` で再記述 |
| 8 | lib/db/repositories/plDailyRepository.ts:49 / 130 | D | **High** | `getDailySalesRange` / `getDailyExpensesRange` が `{ gte: new Date(startDate), lte: new Date(endDate) }` で両端 inclusive。`@db.Date` 比較なので機能上は両端 inclusive で OK だが、`new Date('2026-04-30')` (ISO short, UTC) を使うため endDate 翌日 0:00 にズレるエッジが残る (タイムゾーン誤実装が紛れ込んだ場合に壊れる) | `{ gte: parseBusinessDateToUTC(startDate), lt: addBusinessDays(endDate, 1) -> UTC }` の半開区間に統一 |
| 9 | lib/line/sales-context.ts:171 (getRecentDailySummaries) | D | **High** | `{ date: { gte: startDate, lte: endDate } }`。startDate, endDate ともに UTC midnight Date で生成されているので `@db.Date` 比較は OK だが、`endDate = parseBusinessDateToUTC(date)` のため当日含む。一方 `new Date(... - days*86400000)` の `gte` は意図通り | 半開区間に書き換える方が将来の混入を防げる |
| 10 | app/store/[storeId]/pl/dashboard/page.tsx:89, 179, 139-141 | C + B | **High** | "今日" を `new Date().toISOString().split('T')[0]` (UTC暦日) で算出 → JST 00:00–08:59 に画面を開くと前日付の `/api/daily-report/reports?date=...` に投げる。`new Date().getMonth()+1 / getDate() / getDay()` も local TZ で、TZ=UTC 環境では別日になる | `toBusinessDate(new Date(), cutoffHour)` で文字列化し、表示も同文字列をパースして使う |
| 11 | app/daily-report/[storeId]/page.tsx:154 | C | **High** | 画面表示 `<p>{today}</p>` に bug #2 と同じ値を表示 → JST 0:00-8:59 に開くと前日表示 | bug #2 と同時修正 |
| 12 | app/store/[storeId]/pl/dashboard/page.tsx:15, /pl/monthly/page.tsx:17 | B | **High** | `getCurrentYearMonth()` = `now.getFullYear() + ... getMonth()+1` → local TZ。TZ=UTC では JST 早朝月初の "今月" が前月扱いに | `now.getUTCFullYear() / getUTCMonth() + 1` or businessDate ベース。さらに営業日 cutoff も考慮するなら `todayBusinessDate(cutoff).slice(0,7)` |
| 13 | lib/utils/date.ts:50-63 (parseDateTime) | B | **High** | `date.setHours(time.hour, ...)` を `new Date(datePart)` (UTC midnight Date) に対して呼ぶ → local TZ の hour として書き込まれ、JST 環境では UTC 9 時間オフセットが追加 | `new Date(`${datePart}T${timePart}+09:00`)` (JST 解釈) もしくは UTC として明示パース |
| 14 | lib/utils/date.ts:85-88 (getDayOfWeekJa) / :93-110 (getWeekStart/getWeekEnd) | B | **High** | `date.getDay() / getDate() / setDate() / setHours()` を local TZ で実行。週次レポートのファイル名や境界計算で使用されると週末の境界が TZ で 1 日ズレる可能性 | UTC 系 API に統一。または businessDate.ts の文字列実装に置き換え |
| 15 | lib/utils/date.ts:118-133 (getMonthEnd) | D | **Medium** | `new Date(Date.UTC(year, month, 0))` 自体は安全だが、命名上 "月末日" の UTC midnight を返すので、これを `lte` で渡すと `@db.Timestamptz` 集計で 0:00 以降が抜け落ちる | 命名を `getMonthEndExclusive`/`getNextMonthStart` に変えて半開区間で使う |
| 16 | lib/csv/airregiParser.ts:24-28 (getDayOfWeek) | F | **Medium** | `new Date('YYYY-MM-DD')` (UTC midnight) に対し `.getDay()` を呼ぶ。TZ=Asia/Tokyo (本番) は JST 9:00 当日 → `getDay()` 正しい。TZ=America/* (西側) では前日扱い | `.getUTCDay()` に変更 |
| 17 | lib/csv/airregiParser.ts (parser path is legacy fallback, dayOfWeek 結果は最終的に sales_data.dayOfWeek へ書き込まれる) | F | **Medium** | パターン F の取込時固定。後段で `toBusinessDate` 経由で再計算される箇所 (data/[month]) もあるが、書き込み時点で dayOfWeek が暦日ベースになるため、深夜会計の曜日表示は依然ズレる | dayOfWeek は表示時に営業日付から再計算するか、保存しない (ビュー化) |
| 18 | components/pl/HolidayCalendar.tsx:22-24, 117-123 | B + I | **Medium** | `const today = new Date()` の `getFullYear()/getMonth()/getDate()` で "今日" を計算。TZ=Asia/Tokyo (運用 TZ) は OK だが、TZ=UTC の CI / Vercel デフォルト環境で JST 0:00-8:59 に SSR された場合、初期 viewYear/viewMonth が前日になる可能性 | `getUTCFullYear/getUTCMonth + 1 + JST オフセット` を計算、または `todayBusinessDate(cutoff)` を文字列で扱う |
| 19 | components/daily-report/DailyStoreSummaryCard.tsx:18-20 | B + I | **Medium** | `new Date(dateStr + 'T00:00:00')` (T サフィックス + 時刻、Z なし → local TZ midnight) を生成し `.getDay()` を呼ぶ。日曜判定 `dayNames[0]` を表示する曜日ラベル。TZ=Asia/Tokyo は OK、TZ=America/* で 1 日ずれた曜日が表示 | `new Date(dateStr + 'T00:00:00Z').getUTCDay()` または businessDate.ts の `dayOfWeekUTC` を使う |
| 20 | app/store/[storeId]/pl/daily-reports/page.tsx:25-28 (formatDateShort) | B + I | **Medium** | 同上 (`new Date(dateStr + 'T00:00:00').getDay()`) | 同上 |
| 21 | app/store/[storeId]/pl/daily/page.tsx:11-16, 40 | C + I | **Medium** | `formatDate(new Date())` を local-TZ Date に対して呼ぶ。TZ=Asia/Tokyo 運用なら JST 暦日 = ほぼ営業日と一致するが、cutoff=5 の場合 JST 0:00-4:59 で 1 日ズレ (営業日 vs 暦日) | `todayBusinessDate(cutoffHour)` に置換。フロントから API 経由で取るのが理想 |
| 22 | app/store/[storeId]/pl/daily-reports/page.tsx:11-16, 37 | C + I | **Medium** | 同上 (`formatDate(new Date())`) | 同上 |
| 23 | lib/db/repositories/weeklyReportRepository.ts:123-124, 17-19 (formatDate / new Date(params.startDate)) | H | **Low** | `new Date('YYYY-MM-DD')` (UTC midnight) で保存 → `formatDate` で `toISOString().split('T')[0]` → UTC 暦日として読み出し。書き込みと読み出しが対称なので機能上は問題ないが、`startDate/endDate` 列が `@db.Date` か `@db.Timestamptz` かで結果が変わるリスク | スキーマ確認の上、`@db.Date` ならば現状の方法で問題なし。`@db.Timestamptz` なら明示 JST→UTC 変換 |
| 24 | lib/db/repositories/monthlyReportRepository.ts:123-124, 17-19 | H | **Low** | 同上 | 同上 |
| 25 | lib/utils/date.ts:11-23 (parseVisitDate) | A | **Low** | YYYY/M/D 形式を UTC midnight として返す。CSV 取込で利用するなら "営業日" として保存する用途。意図通り | 用途のコメント明記のみ |
| 26 | app/api/months/route.ts:33, 69 (uploadedAt: new Date().toISOString()) | I | **Low** | `uploadedAt` を毎リクエストの now で上書きしているが、月リスト UI の表示用なので無害 | 不要なフィールドであれば削除 |
| 27 | scripts/verify-bfa-verify.ts, scripts/check-bfa-boundary.ts | J (旧バグ再現用) | 確認のみ | 旧バグの再現実験スクリプト。意図的に `new Date(year, month-1, day)` を使用 | コメント済。対応不要 |
| 28 | lib/demo/demoDataGenerator.ts | J (デモ) | 確認のみ | デモデータ生成器内で `new Date(year, month-1, day)` を使用。本番に書き込まないので影響範囲が限定 | 既存 override で許容 |
| 29 | __tests__/pl/calculator.test.ts, __tests__/utils/businessDate.test.ts | J | 確認のみ | テスト用の Date 構築 | 対応不要 |

---

## 1. Critical

### 1.1 app/api/trends/monthly/route.ts:233-236 — 勤怠時刻を local TZ で読んでいる
- **パターン**: B (ローカルTZ依存の Date 読み出し)
- **コード抜粋** (l.231-249):
  ```ts
  } else if (record.startTime && record.endTime) {
    // Calculate from start and end times if workHours is not set
    const startHours = record.startTime.getHours();
    const startMinutes = record.startTime.getMinutes();
    const endHours = record.endTime.getHours();
    const endMinutes = record.endTime.getMinutes();

    const startTotalMinutes = startHours * 60 + startMinutes;
    const endTotalMinutes = endHours * 60 + endMinutes;
    const hoursWorked = (endTotalMinutes - startTotalMinutes) / 60;
  ```
- **何が起こる**:
  - `record.startTime` / `record.endTime` は Prisma 由来の Date オブジェクト (UTC のタイムスタンプ)。
  - `getHours()` は **ランタイムの TZ** で解釈される。
  - Vercel デフォルト = `TZ=UTC` の場合: JST 9:00 出勤 → 内部的に UTC 0:00 → `getHours() = 0`。JST 17:00 退勤 → UTC 8:00 → `getHours() = 8`。一見正しく見えるが、JST 19:00 退勤 → UTC 10:00 → 8時間扱い (正)。問題は **0時を跨ぐ深夜営業**: JST 22:00 出勤 → UTC 13:00, JST 翌5:00 退勤 → UTC 翌20:00. `getHours()` = 13 と 20 → 7時間 (正)。一方 JST 出勤 22:00 → 退勤 JST 翌2:00 (UTC 22:00 → 翌17:00) で日付跨ぎでも startTotal=22*60, endTotal=17*60 → 負 → 0扱い → **人件費 0 計上**。
  - `TZ=Asia/Tokyo` 環境では同じ Date でも `getHours()` が JST 値を返すので、深夜跨ぎでも `start > end` 問題は残るが、シフトの大半 (昼〜夜) は正しく出る。**production と CI で結果が変わる** 点が最も厄介。
- **数値ズレ例**:
  - JST 22:00–翌02:00 シフト (4h) → `TZ=UTC` で startHours=13, endHours=17 → 4h (正、たまたま)
  - JST 22:00–翌05:00 シフト (7h) → `TZ=UTC` で startHours=13, endHours=20 → 7h (正)
  - JST 23:30–翌00:30 シフト (1h) → `TZ=UTC` で startHours=14, endHours=15 → 1h (正)
  - 上記 3 ケースは UTC 表現でも end > start のため動く。**実害は JST 表現での "0時跨ぎ"** : startTime = `2026-05-01T13:00:00Z` (=JST 22:00) と endTime = `2026-05-01T17:00:00Z` (=JST 翌2:00) — Postgres が同じ日 (5/1) で保存していれば計算可能だが、`new Date('2026-05-02T17:00:00Z').getHours()` を JST で読むと 2 になり startTotal=22*60, endTotal=2*60 → -1200 → `hoursWorked = 0` → 人件費の "0" 計上。
- **修正方針**:
  ```ts
  // 推奨1: workHours を必須化し、startTime/endTime 計算を捨てる
  // 推奨2: 差分で計算 (TZ非依存)
  const hoursWorked = (record.endTime.getTime() - record.startTime.getTime()) / 3600_000;
  ```
- **テスト**:
  - 0:00 跨ぎシフトのテスト: start = 2026-05-01T13:00Z (JST 22:00), end = 2026-05-01T17:00Z (JST 翌02:00) → 4h
  - `TZ=UTC` / `TZ=Asia/Tokyo` 両方で同じ結果になることを確認

### 1.2 app/daily-report/[storeId]/page.tsx:33 — 日報の "今日" が UTC 暦日
- **パターン**: C
- **コード抜粋**:
  ```ts
  const today = new Date().toISOString().split('T')[0];
  ...
  body: JSON.stringify({
    storeId,
    memberId: selectedMemberId,
    date: today,
    answers,
    ...
  }),
  ```
- **何が起こる**:
  - スタッフが JST 0:00 〜 8:59 に日報を提出すると、`new Date().toISOString()` は UTC 表現で **前日の 15:00–23:59** を返す。
  - 結果 `today` = 前日 (UTC 暦日)。`/api/daily-report/submit` に前日付で保存される。
  - 例: スタッフが JST 5/1 02:00 に日報を提出 → `today = '2026-04-30'` → DailyReport.date が 4/30 として保存 → 翌日マネージャーが 5/1 の日報を見ても表示されない。
- **修正方針**:
  ```ts
  import { todayBusinessDate, DEFAULT_BUSINESS_DAY_CUTOFF_HOUR } from '@/lib/utils/businessDate';
  // 店舗の cutoff はサーバーから取得して props で渡す
  const today = todayBusinessDate(cutoffHour ?? DEFAULT_BUSINESS_DAY_CUTOFF_HOUR);
  ```
  もしくは最低限 JST 暦日:
  ```ts
  const today = formatUTCtoJST(new Date(), 'date');
  ```
- **テスト**:
  - `new Date('2026-05-01T15:30:00Z')` (= JST 5/2 00:30) で `today` が `'2026-05-01'` (cutoff=5) になることを確認

### 1.3 lib/analytics/calculator.ts:365-403 (calculateWeeks) — 週境界の local-TZ 算出
- **パターン**: B + C
- **コード抜粋** (l.365-401):
  ```ts
  function calculateWeeks(dailyData: DailyData[]): WeekInfo[] {
    if (dailyData.length === 0) return [];

    const sortedDays = _.sortBy(dailyData, 'date');
    const firstDate = new Date(sortedDays[0].date);  // 'YYYY-MM-DD' → UTC midnight Date

    // Find the Monday of the first week
    const firstMonday = new Date(firstDate);
    const dayOfWeek = firstDate.getDay();              // ← local TZ
    const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    firstMonday.setDate(firstDate.getDate() + daysToMonday); // ← local TZ

    const weeks: WeekInfo[] = [];
    let weekStart = new Date(firstMonday);

    for (let i = 0; i < 6; i++) {
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);

      const startStr = weekStart.toISOString().split('T')[0]; // ← UTC 暦日
      const endStr = weekEnd.toISOString().split('T')[0];     // ← UTC 暦日
      ...
      weekStart.setDate(weekStart.getDate() + 7);
      ...
  ```
- **何が起こる**:
  - `firstDate = new Date('2026-04-01')` (UTC midnight)
  - `TZ=Asia/Tokyo`: `firstDate.getDay()` を呼ぶと JST 09:00 として解釈 → 4/1(水) → getDay()=3 → daysToMonday=-2 → setDate(1-2)=-1 → JST 3/30(月) → toISOString() → UTC 3/29T15:00:00 → split → `'2026-03-29'`. 期待は 3/30。**1 日ズレ**。
  - `TZ=UTC`: `firstDate.getDay()` = 3 (水) (UTC 0:00 解釈で水) → daysToMonday=-2 → setDate(1-2)=-1 → UTC 3/30(月) → toISOString → `'2026-03-30'`. 正。
- **数値ズレ例**:
  - JST 4/1 が水曜 → 第1週は 3/30(月)〜4/5(日)。
  - `TZ=Asia/Tokyo` で稼働: ラベル `2026-03-29 〜 2026-04-04` (誤、1日早い)
  - `TZ=UTC` で稼働: ラベル `2026-03-30 〜 2026-04-05` (正)
  - dashboard ページで週セレクタの境界が壊れる。
- **修正方針**:
  ```ts
  // 文字列ベースで週月曜日を算出 (TZ非依存)
  import { dayOfWeekUTC, addBusinessDays } from '@/lib/utils/businessDate';
  function mondayOf(dateStr: string): string {
    const dow = dayOfWeekUTC(dateStr); // 0=Sun..6=Sat
    const offset = dow === 0 ? -6 : 1 - dow;
    return addBusinessDays(dateStr, offset);
  }
  ```
- **テスト**:
  - 各 TZ で `calculateWeeks([{date: '2026-04-01'...}])` → 第1週 start='2026-03-30'

### 1.4 app/store/[storeId]/dashboard/[month]/page.tsx:240-265 — フロントで週境界を local-TZ 算出
- **パターン**: B + C
- **コード抜粋** (l.245-265):
  ```ts
  // Find the Monday of the week containing the start date
  let currentWeekStart = new Date(startDate);
  const dayOfWeek = currentWeekStart.getDay();
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  currentWeekStart.setDate(currentWeekStart.getDate() + diff);

  let weekIndex = 0;
  while (currentWeekStart <= endDate && weekIndex < 6) {
    const weekEnd = new Date(currentWeekStart);
    weekEnd.setDate(weekEnd.getDate() + 6);

    weeksList.push({
      id: `week-${weekIndex}`,
      label: `第${weekIndex + 1}週`,
      start: currentWeekStart.toISOString().split('T')[0],
      end: weekEnd.toISOString().split('T')[0]
    });

    currentWeekStart.setDate(currentWeekStart.getDate() + 7);
    weekIndex++;
  }
  ```
- **何が起こる**: 1.3 と同じパターン。フロントエンドはユーザの browser TZ (= JST がほとんどだが Mac で UTC や EDT のユーザもいる) で計算されるため、**閲覧者によって表示が変わる**。
- **数値ズレ例**: 1.3 と同じ。
- **修正方針**: 1.3 と同じ。`addBusinessDays` 互換ヘルパをフロントでも使う。
- **テスト**: brower TZ 偽装テスト (vitest で `process.env.TZ`)

### 1.5 lib/db/repositories/dailyStoreSummaryRepository.ts:97-112 (getSummariesByMonth) — `lte: endDate` 半開区間化漏れ
- **パターン**: D
- **コード抜粋**:
  ```ts
  const [year, month] = yearMonth.split('-').map(Number);
  const startDate = new Date(Date.UTC(year, month - 1, 1));
  const endDate = new Date(Date.UTC(year, month, 0));    // 月末日 UTC 00:00

  const summaries = await prisma.dailyStoreSummary.findMany({
    where: {
      storeId,
      date: { gte: startDate, lte: endDate },
    },
    ...
  });
  ```
- **何が起こる**:
  - `dailyStoreSummary.date` のスキーマ確認が必要だが、`saveSummary` で `new Date(date + 'T00:00:00Z')` を upsert している → 各レコードは UTC midnight 固定 → `lte: endDate` (= 月末日 UTC 00:00) でちょうど含まれる。**機能上は今のところ動いている**。
  - ただし、`saveSummary` で誰かが `new Date(date)` (TZ依存) に変えると即座に壊れる。
  - また UI 側で「6月分」を見る時に "5/31 23:00 JST = 5/31 14:00 UTC" のレコードが境界に来た場合、UTC midnight 想定が壊れていれば取りこぼし。
- **数値ズレ例**:
  - 仮に dailyStoreSummary.date を `new Date('2026-05-31')` (JST 解釈) で保存していたとすると、JST 環境では `2026-05-30T15:00:00Z` として保存される → `gte: 2026-05-01T00:00:00Z, lte: 2026-05-31T00:00:00Z` のクエリでは 5/30 のもの扱いになり 6 月レンジから外れる。
- **修正方針**:
  ```ts
  import { calendarMonthRangeUTC } from '@/lib/utils/businessDate';
  const { gte, lt } = calendarMonthRangeUTC(yearMonth);
  await prisma.dailyStoreSummary.findMany({ where: { storeId, date: { gte, lt } } });
  ```
- **テスト**: 月末・月初境界でのレコード取得テスト

---

## 2. High

### 2.1 lib/db/repositories/dailyReportRepository.ts:138-150 (getRecentReports) — `lte: dateObj` の半開区間化
- **パターン**: D
- **抜粋**:
  ```ts
  const dateObj = new Date(beforeDate + 'T00:00:00Z');
  const reports = await prisma.dailyReport.findMany({
    where: { storeId, date: { lte: dateObj } },
    ...
  });
  ```
- **影響**: `dailyReport.date` は @db.Date と思われるが、ここで `lte` を使うと "当日を含む" 意図。スキーマ変更耐性が低い。
- **修正**: `{ lt: new Date(addBusinessDays(beforeDate, 1) + 'T00:00:00Z') }` で当日含む半開区間に。

### 2.2 lib/db/repositories/dailyStoreSummaryRepository.ts:72-85 (getLatestSummary) — `lte: dateObj`
- **パターン**: D
- **影響**: 2.1 と同じパターン。"指定日以前の最新" を取りたいが、`lte: dateObj` が UTC midnight ぴったり比較になり、保存方式が変わると壊れる。
- **修正**: 半開区間 + コメントで明記。

### 2.3 lib/db/repositories/plDailyRepository.ts:40-61 / 121-148 — `gte/lte` レンジ
- **パターン**: D
- **抜粋**:
  ```ts
  where: { storeId, date: { gte: new Date(startDate), lte: new Date(endDate) } }
  ```
- **影響**: `@db.Date` 列なので動作は OK だが、`new Date('2026-04-30')` は UTC midnight。今後 `pl_daily_sales.date` を `@db.Timestamptz` に変更したり、データを TZ ありで保存すると endDate 当日 23:59 のレコードが取れなくなる。
- **修正**: `parseBusinessDateToUTC + 1day` の半開区間に統一。

### 2.4 lib/line/sales-context.ts:171 (getRecentDailySummaries) — `gte+lte`
- **パターン**: D
- **影響**: 2.1/2.2 と同様。
- **修正**: 半開区間化。

### 2.5 app/store/[storeId]/pl/dashboard/page.tsx:89, 179, 139-141 — "今日" の UTC 暦日問題
- **パターン**: C + B
- **抜粋**:
  ```ts
  const today = new Date().toISOString().split('T')[0]; // line 89
  ...
  date={new Date().toISOString().split('T')[0]} // line 179
  ...
  {new Date().getMonth() + 1}月{new Date().getDate()}日 // line 139
  {['日','月','火','水','木','金','土'][new Date().getDay()]}曜日 // line 141
  ```
- **影響**:
  - 89, 179: JST 0:00-8:59 に画面を開くと前日付で `/api/daily-report/reports` を呼ぶ → 当日の日報が「未提出」と表示される。
  - 139-141: SSR (`TZ=UTC` 環境) でレンダリングされた値が初期 HTML に焼かれる。クライアントでは local TZ で再評価されるため hydration ズレが発生する可能性 (`suppressHydrationWarning` の有無を確認すべき)。
- **修正**: 営業日付ベースで統一。

### 2.6 app/daily-report/[storeId]/page.tsx:154 — "今日" 表示が UTC 暦日
- **パターン**: C
- **影響**: 1.2 と同じ `today` を `<p>{today}</p>` に表示する。スタッフが「今日の日付がおかしい」と気づくきっかけにはなるが、誤データのまま提出される可能性。
- **修正**: 1.2 と同時に修正。

### 2.7 app/store/[storeId]/pl/dashboard/page.tsx:13-16 / pl/monthly/page.tsx:15-17 — `getCurrentYearMonth()`
- **パターン**: B
- **抜粋**:
  ```ts
  function getCurrentYearMonth(): string {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  }
  ```
- **影響**:
  - `TZ=Asia/Tokyo`: JST 暦日基準 → ほぼ意図通り。ただし JST 0:00-4:59 で cutoff=5 の場合、営業月とズレる (5/1 1:00 → 営業日 4/30, 営業月 4 月だが UI は 5 月)。
  - `TZ=UTC` (Vercel default): JST 早朝の月初・月末で 1 ヶ月ズレ。
- **修正**:
  ```ts
  function getCurrentYearMonth(cutoffHour: number): string {
    return todayBusinessDate(cutoffHour).slice(0, 7);
  }
  ```

### 2.8 lib/utils/date.ts:50-63 (parseDateTime) — `setHours()` で local-TZ 上書き
- **パターン**: A + B
- **抜粋**:
  ```ts
  export function parseDateTime(dateTimeStr: string): Date {
    const [datePart, timePart] = dateTimeStr.split(' ');
    if (datePart && timePart) {
      const date = new Date(datePart);       // UTC midnight
      const time = parseTime(timePart);
      date.setHours(time.hour, time.minute, time.second); // ← local TZ で時刻書き込み
      return date;
    }
    return new Date(dateTimeStr);
  }
  ```
- **影響**: 入力 `'2026-05-01 19:00:00'` (JST 想定) → UTC 2026-04-30T15:00 (UTC midnight) → JST 環境で setHours(19,0,0) → JST 2026-04-30 19:00 = UTC 2026-04-30T10:00 (約9時間ズレ). 用途 (現状コードで使われていないなら影響小だが、使われると即バグ)。
- **修正**: `parseJSTtoUTC` を使うか、`new Date(`${datePart}T${timePart}+09:00`)`。

### 2.9 lib/utils/date.ts:85-110 (getDayOfWeekJa / getWeekStart / getWeekEnd) — 全て local TZ
- **パターン**: B + F
- **抜粋**:
  ```ts
  export function getDayOfWeekJa(date: Date): string {
    const days = ['日', '月', '火', '水', '木', '金', '土'];
    return days[date.getDay()];
  }
  export function getWeekStart(date: Date): Date {
    const day = date.getDay();
    const diff = day === 0 ? -6 : 1 - day;
    const weekStart = new Date(date);
    weekStart.setDate(date.getDate() + diff);
    weekStart.setHours(0, 0, 0, 0);
    return weekStart;
  }
  ```
- **影響**: 週次レポート生成やファイル名生成で利用されると週末境界が TZ で 1 日ズレる。検索で使用箇所を確認すべきだが、公開 API として残っているのでリスク。
- **修正**: UTC 系 API に置換 (`getUTCDay/getUTCDate/setUTCDate/setUTCHours`) もしくは businessDate.ts の `dayOfWeekUTC` / `addBusinessDays` を使った文字列ベース実装に統一。

---

## 3. Medium

### 3.1 lib/utils/date.ts:118-133 (getMonthEnd) — 命名の罠
- **パターン**: D
- **抜粋**:
  ```ts
  export function getMonthEnd(yearMonth: string): Date {
    const [year, month] = yearMonth.split('-').map(Number);
    return new Date(Date.UTC(year, month, 0));
  }
  ```
- **影響**: 月末日 UTC midnight を返すが、`.lte: getMonthEnd(...)` で渡されると `@db.Timestamptz` 列ではその日の 0:00 以降の行を取りこぼす。命名で誤認するリスク。
- **修正**: 関数名を `getMonthEndExclusiveUTC` または `getNextMonthStartUTC` に。

### 3.2 lib/csv/airregiParser.ts:24-29 — `getDay()` で曜日算出
- **パターン**: F
- **抜粋**:
  ```ts
  function getDayOfWeek(dateString: string): string {
    const date = new Date(dateString.replace(/\//g, '-')); // UTC midnight
    const days = ['日', '月', '火', '水', '木', '金', '土'];
    return days[date.getDay()];
  }
  ```
- **影響**: TZ=Asia/Tokyo 本番では問題ないが、CI/開発環境で TZ が異なると曜日がズレる → DB に保存される `sales_data.dayOfWeek` が誤る。data/[month] では `toBusinessDate` から再計算されるが、`sales_data.dayOfWeek` 自身を直接読む箇所では誤値。
- **修正**: `.getUTCDay()` に置換 (transformer.ts:295-316 と同じパターンで)。

### 3.3 lib/csv/transformer.ts:295-316 getDayOfWeek (airregi data path 内)
- **パターン**: F
- **状況**: l.313 `new Date(Date.UTC(year, month, day))` + `.getUTCDay()` で安全実装済み。`Date.UTC(year, month-1, day)` の引数を `month` (0-indexed) に渡しているかは一致しており OK。
- **影響**: なし。**確認のみ**だが、`mapper.ts:80` の `calculateDayOfWeek` も同様の実装で OK。

### 3.4 components/pl/HolidayCalendar.tsx:22-24, 117-123 — 今日マーカーの TZ 依存
- **パターン**: B + I
- **抜粋**:
  ```ts
  const today = new Date();
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth() + 1);
  ...
  const isToday =
    cell.day === today.getDate() &&
    viewMonth === today.getMonth() + 1 &&
    viewYear === today.getFullYear();
  ```
- **影響**: 初期表示の年月とtoday マーカーが local TZ 基準。SSR (TZ=UTC) と CSR (browser TZ) で hydration mismatch の可能性。
- **修正**: 一度サーバから "今日の営業日付" を取得し props で渡す。または `formatUTCtoJST(new Date(),'date')` で JST 暦日を取得。

### 3.5 components/daily-report/DailyStoreSummaryCard.tsx:18-20 — 曜日ラベル
- **パターン**: B + I
- **抜粋**:
  ```ts
  function formatDateLabel(dateStr: string): string {
    const [, m, d] = dateStr.split('-');
    const dateObj = new Date(dateStr + 'T00:00:00');  // local-TZ midnight
    const dayNames = ['日', '月', '火', '水', '木', '金', '土'];
    const dayName = dayNames[dateObj.getDay()];
    return `${parseInt(m)}/${parseInt(d)}（${dayName}）`;
  }
  ```
- **影響**: `new Date('2026-05-01T00:00:00')` (Zなし) は local-TZ midnight → `getDay()` の結果は date 文字列の曜日になるが、ユーザ browser が TZ=America/* だと前日扱い → 曜日が 1 つズレ。
- **修正**: `new Date(dateStr + 'T00:00:00Z').getUTCDay()` または `dayOfWeekUTC(dateStr)`。

### 3.6 app/store/[storeId]/pl/daily-reports/page.tsx:23-29 — 同上
- **パターン**: B + I
- **抜粋**: 3.5 と同じパターン。
- **修正**: 3.5 と同じ。

### 3.7 app/store/[storeId]/pl/daily/page.tsx:11-16, 40 / pl/daily-reports/page.tsx:11-16, 37 — formatDate(new Date())
- **パターン**: B + C + I
- **抜粋**:
  ```ts
  function formatDate(date: Date): string {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
  const [date, setDate] = useState(formatDate(new Date()));
  ```
- **影響**: ユーザ browser TZ で "今日" を解釈。JST ユーザは JST 暦日が初期値になり、cutoff=5 の場合 JST 0:00-4:59 で営業日と 1 日ズレ → 当日 PL 入力フォームに前日の営業日値が表示される。
- **修正**: `todayBusinessDate(cutoffHour)` 経由。

---

## 4. Low / 確認のみ

### 4.1 lib/db/repositories/weeklyReportRepository.ts:17-19, 123-124
- **パターン**: H
- **抜粋**:
  ```ts
  function formatDate(d: Date): string {
    return d.toISOString().split('T')[0]; // UTC 暦日
  }
  ...
  startDate: new Date(params.startDate),  // UTC midnight (ISO short)
  endDate: new Date(params.endDate),
  ```
- **影響**: 書込/読出の両方が UTC midnight で対称になるので機能上の問題なし。スキーマが `@db.Date` ならば動く。`@db.Timestamptz` だと書込時刻と読出時刻でズレるリスクあるが、schema 確認 (prisma/schema.prisma) で WeeklyReport.startDate の型を要チェック。
- **修正**: 不要。スキーマ Comment 推奨。

### 4.2 lib/db/repositories/monthlyReportRepository.ts:17-19, 123-124
- 4.1 と同じ。

### 4.3 lib/utils/date.ts:11-23 (parseVisitDate)
- **パターン**: A
- **状況**: 旧バグ修正済の安全実装。JSDoc に既に「常に UTC midnight として解釈」と明記済。
- **影響**: なし。

### 4.4 app/api/months/route.ts:33, 69 (uploadedAt: new Date().toISOString())
- **パターン**: I
- **状況**: month リストの飾り情報。ISO 文字列なので TZ 安全。表示用のため影響なし。
- **影響**: なし。

---

## 5. パターン別頻度分析

| パターン | 件数 | コメント |
|---|---|---|
| A: ローカルTZ依存の Date 構築 | 2 | parseVisitDate (修正済), parseDateTime |
| B: ローカルTZ依存の Date 読み出し | 13 | 最多パターン。getDay/getMonth/getFullYear/getHours が散在 |
| C: 集計キーのズレ (UTC暦日 vs 営業日) | 6 | `today.toISOString().split('T')[0]` 多発 |
| D: 月境界 `gte/lte` (両端含む) | 7 | repositories 全般。半開区間に統一すべき |
| E: 月またぎ年またぎ算術 | 0 | 全てユーティリティ経由で吸収済 |
| F: 曜日 TZ | 3 | airregiParser, transformer, mapper (うち 2 つは getUTCDay 実装済) |
| G: 日報・週報レンジ | 2 | dailyReportRepository, dailyStoreSummaryRepository |
| H: ファイル名・URL に日付埋込 | 2 | weekly/monthly report repositories |
| I: フロントエンド固有 | 8 | 今日マーカー、初期表示、曜日ラベル |
| J: スクリプト系 | 0 (実害) | デモ/検証スクリプトのみ。本番書き込みは Date.UTC で対応済 |
| K: CSV取込パス | 1 | airregiParser.ts (getDay) |

---

## 6. 推奨される横断対策

1. **`sales_data.dayOfWeek` カラム廃止 → ビュー化または都度算出**:
   現状は CSV 取込時に固定。`@db.Date` の営業日付からビューで計算するか、表示時に `dayOfWeekUTC(businessDate)` を呼ぶようにすれば、取込パスの TZ バグが集計に伝播しない。

2. **"今日" を取得するヘルパを 1 つに集約**:
   フロント・バックの全箇所で `new Date()` から直接 `getDay/getMonth/...` を呼ぶのを禁じ、`todayBusinessDate(cutoffHour)` 経由を強制。フロントから直接呼べないので、`/api/today?storeId=xxx` のような薄い API を追加し、ページ初期化時に取得するパターンを定着させる。

3. **`@db.Date` カラム全レンジクエリを半開区間に統一**:
   `{ gte: x, lt: y }` に統一。`businessDate.ts` の `calendarMonthRangeUTC` / `businessDateRangeUTC` / `addBusinessDays` を活用。`{ gte, lte }` を見つけ次第置換。

4. **`@db.Date` 読み出しは必ず `.toISOString().split('T')[0]` 経由**:
   現状もほぼこれだが、`@db.Timestamptz` に変えた瞬間に破綻するので、Repository 層に `toBusinessDateString(r.date, cutoffHour)` のような明示ヘルパを噛ませる。

5. **勤怠の `workHours` を必須化**:
   `getHours()/getMinutes()` で計算する fallback path (1.1) を削除。Timestamptz の差分のみで時間計算する。

6. **lib/utils/date.ts の旧 API を deprecated 化**:
   `getDayOfWeekJa`, `getWeekStart`, `getWeekEnd`, `parseDateTime` を `@deprecated` マーク + businessDate.ts への誘導コメント。

7. **CI で TZ=UTC, TZ=Asia/Tokyo, TZ=America/Los_Angeles の 3 つで vitest を走らせる**:
   `vitest --tz=UTC` 系の指定がなくても `process.env.TZ` で切り替え可能。matrix で実行することで local-TZ 依存コードが検出される。

---

## 7. ESLint ルールの追加候補

既存の `no-restricted-syntax` で `new Date(y, m, d)` を弾いている。追加で弾くべきパターン:

```jsonc
{
  "rules": {
    "no-restricted-syntax": [
      "error",
      {
        "selector": "CallExpression[callee.object.callee.name='Date'][callee.property.name=/^(getFullYear|getMonth|getDate|getDay|getHours|getMinutes|getSeconds)$/]",
        "message": "Use getUTC* variants. local TZ getters are forbidden in app code."
      },
      {
        "selector": "MemberExpression[object.callee.name='Date'][property.name=/^(getFullYear|getMonth|getDate|getDay|getHours|getMinutes)$/]",
        "message": "Use getUTC* on Date objects."
      },
      {
        "selector": "CallExpression[callee.property.name='setDate']",
        "message": "Use setUTCDate or addBusinessDays from lib/utils/businessDate."
      },
      {
        "selector": "CallExpression[callee.property.name='setHours']",
        "message": "Use setUTCHours or businessDate utilities. setHours is TZ-dependent."
      },
      {
        "selector": "NewExpression[callee.name='Date'] > BinaryExpression[operator='+'][right.value=/.*[T ]\\d/]",
        "message": "new Date with 'YYYY-MM-DDThh:mm:ss' (no Z) is local-TZ. Use parseJSTtoUTC or append +09:00."
      }
    ],
    "no-restricted-properties": [
      "error",
      { "object": "Date", "property": "parse", "message": "Date.parse interprets strings ambiguously by TZ. Use parseJSTtoUTC or new Date('YYYY-MM-DDTHH:MM:SS+09:00')." }
    ]
  }
}
```

加えて、`getDay()` / `getDate()` / `getHours()` / `getMonth()` / `getFullYear()` を識別する custom rule を作成し、override を持つ ESLint config (`__tests__/`, `lib/demo/`, `scripts/`) のみ許可するのが理想。

---

## 8. 補足: 取込時の visitDate と営業日付の不整合

`app/api/upload/route.ts:453-460` で月分割は CSV の `visitDate` (JST 暦日) を使っている:
```ts
const dataByMonth = _.groupBy(standardData, (row) => {
  const date = row.visitDate;
  return normalizedDate ? normalizedDate.substring(0, 7) : '';
});
```

この結果、JST 5/1 02:30 の会計は CSV 上 `visitDate='2026/05/01'` → 5 月のバッチに含まれ、ImportLog.yearMonth=`2026-05` で記録される。一方 `sales_data.entryAt` は UTC で保存され、後段で `toBusinessDate(entryAt, cutoff=5)` を通すと 営業日付 = `2026-04-30` (営業月 4 月)。**取込ログ上の月** と **集計上の営業月** が乖離する。

**重要度: Medium**。`import_logs.yearMonth` は管理画面の表示用なので機能影響は小さいが、運用者が「5 月分を上げた」と思って 4 月の数字が変わるという混乱を引き起こす。

修正案: 取込時にも `toBusinessDate(parseJSTtoUTC(row.exitDateTime), cutoffHour)` を経由してから groupBy する。ただし cutoff は店舗ごとなので、upload route の冒頭で store.cutoffHour を取得して渡す必要あり。

---

## 9. まとめ

- **最優先 (Critical 5件)**:
  1. 勤怠 `getHours()` (深夜勤務人件費が消える)
  2. 日報 `today = UTC暦日` (JST 早朝提出が前日に保存)
  3. analytics `calculateWeeks` の週月曜算出 (TZ で 1 日ズレ)
  4. dashboard ページ同上 (フロント側)
  5. dailyStoreSummary 月レンジの `lte` 半開区間化

- **High 8件** は、`gte+lte`半開区間化、"今日" 算出ヘルパ統一、`parseDateTime`/`getWeekStart` の utils 修正。

- **横断対策** として `dayOfWeek` カラム廃止/ビュー化と、CI で 3 TZ 併走テストが効く。

- **ESLint ルール強化** で再発を防止。

総計約 30 箇所のうち、本番運用 (TZ=Asia/Tokyo) では大半が "たまたま動く" 状態。だが Vercel デフォルトの TZ=UTC で動くケース (CI / ローカル開発 / もし `TZ` を unset したまま deploy した場合) で多数のバグが顕在化する。営業時刻が深夜帯のバー店舗 (cutoff=5) では JST 暦日と営業日付のズレが本番でも常時発生しており、現在の運用でも 1.2 (日報前日保存) と 3.7 (PL 入力フォーム初期値) は実害を出している可能性が高い。
