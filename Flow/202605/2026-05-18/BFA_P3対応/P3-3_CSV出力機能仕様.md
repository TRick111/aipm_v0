# P3-3 CSV出力機能仕様

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-05-18 |
| 更新日 | 2026-05-18（**売上CSVを出力対象に追加**） |
| 対象プロジェクト | BFA（バー）月報ダッシュボード |
| 関連チケット | P3-3 「CSVダウンロード可否の確認」 |
| 元論点 | `/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/対応状況_5Arrowsフィードバック_v1.md` |
| 状態 | 仕様確定（5/16 MTG 回答ベース） |
| 実装ブランチ | `dev` |

## 0. サマリ

石川氏（5Arrows）より「PL ダッシュボードのデータを CSV で落としたい」との要望。

**PL ダッシュボードでは経費だけでなく売上も入力されている**ため、本機能では **PL ダッシュボードで入力された売上（`PlDailySales`）も含めて CSV 出力する**。POS 連携した会計レベルの売上ではなく、**PL ダッシュボードのカテゴリ別日次売上**を出力対象とする（会計明細レベルのエクスポートは P3-3 のスコープ外）。

本仕様書では、外部仕様（ユーザー観点）と内部仕様（実装観点）を定義し、Phase 分割の実装計画を提示する。

---

# Part 1: ユーザーから見た仕様（外部仕様）

## 1.1 提供する CSV の種別

3 種類を提供する。**いずれも PL ダッシュボードで入力された日次データを起点とする**。

| # | 種別 | 用途 | 粒度 | データソース |
|---|------|------|------|------------|
| 1 | **売上明細 CSV** | PL ダッシュボードに入力した売上を日付・カテゴリ別に確認・外部分析 | 1 レコード = 1 行（日付 × カテゴリ） | `PlDailySales` + `PlSalesCategory` |
| 2 | **経費明細 CSV** | 経費の費目・取引先別の確認・税理士提出 | 1 経費レコード = 1 行 | `PlDailyExpense` + `PlExpenseCategory` + `PlVendor` + `PlExpenseCategoryGroup` |
| 3 | **月次集計 CSV** | PL サマリ（売上合計 / FL / その他経費 / 利益）の月別共有 | 1 月 = 1 行 | `PlDailySales` / `PlDailyExpense` / `PlMonthlyTarget` の月次集計 |

## 1.2 操作 UI（ボタン配置）

PL ダッシュボード（`/store/[storeId]/pl/dashboard`）ヘッダ右上に **「CSV出力」ボタン** を新設する。

クリック → モーダル表示 → 以下を選択 → 「ダウンロード」押下でブラウザにファイル保存。

### モーダルの入力項目

| 入力項目 | UI | 必須 | 備考 |
|---------|-----|------|------|
| CSV 種別 | ラジオボタン（売上明細 / 経費明細 / 月次集計） | 必須 | 1 種別ずつダウンロード |
| 対象月 | 月選択（YYYY-MM） | 必須 | 既定値：当月（営業日付ベース） |

店舗は **ログイン中の店舗 ID で固定**。複数店舗を横断するエクスポートは v1 では提供しない。

任意の日付範囲（range モード）は v1.1 以降で検討。v1 は **月単位のみ**でシンプルに実装し、まず使ってもらう。

## 1.3 期間指定の仕様

| CSV 種別 | 単月 | 任意の日付範囲 | 備考 |
|---------|------|--------------|------|
| 売上明細 | 〇 | （v1.1） | `PlDailySales.date`（営業日付として保存）ベース |
| 経費明細 | 〇 | （v1.1） | `PlDailyExpense.date` ベース |
| 月次集計 | 〇 | × | 1 行 = 1 月のため範囲指定なし |

## 1.4 ファイル名命名規則

```
BFA_{種別}_{店舗コード}_{YYYY-MM}.csv
```

| 種別 | ファイル名例 |
|------|------------|
| 売上明細 | `BFA_売上明細_bfa01_2026-04.csv` |
| 経費明細 | `BFA_経費明細_bfa01_2026-04.csv` |
| 月次集計 | `BFA_月次集計_bfa01_2026-04.csv` |

- `店舗コード` は `Store.storeCode`（例：`bfa01`）。
- 日本語ファイル名は `Content-Disposition: attachment; filename*=UTF-8''…` で **RFC 5987** エンコードする。ASCII fallback の `filename=` も併記。

## 1.5 文字コード・区切り・改行

| 項目 | 値 | 理由 |
|------|----|------|
| 文字コード | UTF-8（**BOM 付き**） | Excel for Windows での文字化け防止 |
| 区切り文字 | カンマ（`,`） | 標準 CSV |
| 改行コード | CRLF（`\r\n`） | Excel 互換 |
| 引用符 | ダブルクォート（`"`） | 値内にカンマ・改行・引用符を含む場合に必須 |
| エスケープ | ダブルクォートを `""` に置換 | RFC 4180 準拠 |

## 1.6 ヘッダー行

**1 行目は日本語ヘッダ**（石川氏含む非エンジニア利用想定のため）。英語ヘッダ版は v1 では提供しない。

## 1.7 権限・セキュリティ

| 項目 | 仕様 |
|------|------|
| 認証 | 既存の `StoreSession`（cookie 認証）必須 |
| 店舗フィルタ | セッションの `storeId` を **強制適用**（クエリの `storeId` がセッションと一致しなければ 403） |
| グループ管理者 | `StoreGroupSession` 経由なら所属店舗のみ選択可（v1 では `role === 'store'` のみ実装） |
| 監査ログ | v1 では実装しない（要件次第で v1.1） |

## 1.8 数値・日付の書式

| 項目 | 書式 | 例 |
|------|------|----|
| 金額 | **税込・整数（円）** | `12500`（カンマ区切りなし、Excel 側で書式設定可能なように） |
| 日付 | `YYYY-MM-DD` | `2026-04-15` |
| 日時 | `YYYY-MM-DD HH:mm:ss` | `2026-04-15 18:30:00` |
| 真偽値 | `1` / `0` | `FL対象` 等 |
| NULL | 空文字 | `""` |

## 1.9 各 CSV のカラム定義

### 1.9.1 売上明細 CSV（**新規追加**）

`PlDailySales` 1 行 = CSV 1 行。**PL ダッシュボードで入力された日次売上**を出力する。

| # | 列名（日本語） | 型 | サンプル値 | 備考 |
|---|--------------|-----|----------|------|
| 1 | 計上日 | string | `2026-04-15` | `date`（営業日付として保存済み） |
| 2 | 売上カテゴリ | string | `フード` | `PlSalesCategory.name`（JOIN） |
| 3 | 金額（税込） | integer | `48200` | `amount` |
| 4 | 登録日時 | datetime | `2026-04-15 22:00:00` | `createdAt` |
| 5 | 更新日時 | datetime | `2026-04-15 22:30:00` | `updatedAt` |

> 備考：会計明細レベル（POS 連携）の売上は別 CSV（v1.1 以降のスコープ）。本 CSV は **PL ダッシュボードに入力したカテゴリ別日次売上** を対象とする。

### 1.9.2 経費明細 CSV

`PlDailyExpense` 1 行 = CSV 1 行。

| # | 列名（日本語） | 型 | サンプル値 | 備考 |
|---|--------------|-----|----------|------|
| 1 | 計上日 | string | `2026-04-15` | `date` |
| 2 | 費目カテゴリ | string | `食材` | `PlExpenseCategory.name`（JOIN） |
| 3 | 費目グループ | string | `原材料費` | `PlExpenseCategoryGroup.name`（JOIN, NULL 可） |
| 4 | FL対象 | integer | `1` | `PlExpenseCategory.isFLCost`（1/0） |
| 5 | 取引先 | string | `〇〇酒販` | `PlVendor.name`（JOIN, NULL 可） |
| 6 | 金額（税込） | integer | `45200` | `amount` |
| 7 | 種別 | string | `VARIABLE` | `expenseType` （`RECURRING` / `VARIABLE`） |
| 8 | メモ | string | `週次仕入れ` | `memo`（最大 500 文字） |
| 9 | 登録日時 | datetime | `2026-04-15 20:00:00` | `createdAt` |
| 10 | 更新日時 | datetime | `2026-04-15 20:00:00` | `updatedAt` |

### 1.9.3 月次集計 CSV

PL サマリの構造化エクスポート。

| # | 列名（日本語） | 型 | サンプル値 | 備考 |
|---|--------------|-----|----------|------|
| 1 | 対象月 | string | `2026-04` | `yearMonth` |
| 2 | 店舗コード | string | `bfa01` | `Store.storeCode` |
| 3 | 売上目標 | integer | `5000000` | `PlMonthlyTarget.salesTarget` |
| 4 | 売上実績（税込） | integer | `4820000` | `PlDailySales.amount` SUM |
| 5 | 売上達成率（%） | string | `96.4` | 実績 / 目標 × 100、目標 0 のとき空文字 |
| 6 | FL対象経費 | integer | `2380000` | `PlExpenseCategory.isFLCost=true` 経費の合計 |
| 7 | その他経費 | integer | `850000` | FL 対象外経費の合計 |
| 8 | 経費合計 | integer | `3230000` | FL対象経費 + その他経費 |
| 9 | FL率（%） | string | `49.4` | FL対象経費 / 売上実績 × 100 |
| 10 | 営業利益 | integer | `1590000` | 売上実績 - 経費合計 |
| 11 | 利益率（%） | string | `33.0` | 営業利益 / 売上実績 × 100 |

---

# Part 2: 内部仕様（実装仕様）

## 2.1 アーキテクチャ概要

```
[ブラウザ]
  └ CSVダウンロードボタン → モーダル（種別＋月）
        ↓ GET (Cookie auth)
[/api/pl/export/sales]      ← 売上明細
[/api/pl/export/expenses]   ← 経費明細
[/api/pl/export/monthly]    ← 月次集計
        ↓
[lib/csv/buildCsv.ts]       ← BOM/CRLF/エスケープを集約
        ↓
[Repository 層（既存再利用）]
  ├ plDailyRepository.getDailySalesRange / getDailyExpensesRange
  ├ plDashboardRepository.getDashboardRawData（月次集計用）
  └ plMonthlyRepository.getMonthlyTarget
        ↓
[Neon PostgreSQL]
```

## 2.2 API ルート設計

### 2.2.1 売上明細

```
GET /api/pl/export/sales?storeId=<storeCode>&month=YYYY-MM
```

### 2.2.2 経費明細

```
GET /api/pl/export/expenses?storeId=<storeCode>&month=YYYY-MM
```

### 2.2.3 月次集計

```
GET /api/pl/export/monthly?storeId=<storeCode>&month=YYYY-MM
```

### 2.2.4 共通レスポンス

| 状況 | ステータス | ヘッダ / ボディ |
|------|----------|---------------|
| 正常 | 200 | `Content-Type: text/csv; charset=utf-8`, `Content-Disposition: attachment; filename*=UTF-8''<encoded>` + BOM 付き CSV 本文 |
| 期間不正 | 400 | `{ success: false, error: { code: 'ERR-EXPORT-001', message: '期間指定が不正です' } }` |
| storeId 未指定 | 400 | `{ success: false, error: { code: 'ERR-EXPORT-002', message: '店舗IDが指定されていません' } }` |
| 認証なし | 401 | `{ success: false, error: { code: 'ERR-AUTH-001', message: '認証が必要です' } }` |
| 店舗権限なし | 403 | `{ success: false, error: { code: 'ERR-AUTH-007', message: 'アクセス権限がありません' } }` |
| データ取得失敗 | 500 | `{ success: false, error: { code: 'ERR-EXPORT-003', message: 'CSV生成に失敗しました' } }` |

データ 0 件のときは 200 + ヘッダのみの CSV を返す（Excel で開けた方が UX が良いため、404 にはしない）。

## 2.3 エラーコード（新設）

`config/constants.ts` に追加：

| コード | 意味 |
|--------|------|
| `ERR-EXPORT-001` | 期間指定が不正（month の形式不正・未指定） |
| `ERR-EXPORT-002` | 店舗 ID 未指定 |
| `ERR-EXPORT-003` | データ取得・CSV 生成失敗 |

## 2.4 CSV 組み立てライブラリ

新規 `lib/csv/buildCsv.ts`（純粋関数、依存なし）。

```ts
export interface CsvColumn<T> {
  header: string;             // 日本語ヘッダ
  value: (row: T) => string | number | null;
}

export function buildCsv<T>(rows: T[], columns: CsvColumn<T>[]): string {
  // BOM + ヘッダ行 + データ行（CRLF）
  // カンマ・改行・"" を含む値は "" でクオート
}
```

BOM 付与・CRLF・エスケープを集約。**`any` 禁止**。

## 2.5 Response 生成

Next.js App Router の Route Handler で `Response` を直接返す：

```ts
const filename = `BFA_売上明細_${storeCode}_${month}.csv`;
return new Response(csvString, {
  headers: {
    'Content-Type': 'text/csv; charset=utf-8',
    'Content-Disposition':
      `attachment; filename="BFA_sales_${month}.csv"; ` +
      `filename*=UTF-8''${encodeURIComponent(filename)}`,
  },
});
```

## 2.6 データ取得（リポジトリ再利用）

| CSV 種別 | 使用関数 |
|---------|---------|
| 売上明細 | `plDailyRepository.getDailySalesRange(storeCode, startDate, endDate)` |
| 経費明細 | `plDailyRepository.getDailyExpensesRange(storeCode, startDate, endDate)` |
| 月次集計 | `plDashboardRepository.getDashboardRawData(storeCode, yearMonth)` + `plMonthlyRepository.getMonthlyTarget(storeCode, yearMonth)` |

経費明細は `categoryName` / `vendorName` / `memo` / `expenseType` を含む既存型を活用。費目グループ名（`groupName`）は別途取得が必要：

- 既存の `getDailyExpensesRange` は `groupName` を返していない → **追加クエリで `PlExpenseCategory` を JOIN して `groupName` を解決**、または出力時に補完する。本実装ではエクスポート API 内で `prisma.plExpenseCategory.findMany` を 1 回呼んで `categoryId → { groupName, isFLCost }` のマップを作る方針を採用（リポジトリの既存 API を壊さない）。

## 2.7 期間バリデーション

`month=YYYY-MM` を必須化。`/^\d{4}-(0[1-9]|1[0-2])$/` でフォーマット検証。

期間の月初〜月末を `startDate = YYYY-MM-01`、`endDate = YYYY-MM-末日` として `getDailySalesRange` に渡す。営業日付として保存されているため、cutoffHour の追加処理は不要（リポジトリが [gte, lt) 半開区間で範囲を取る）。

## 2.8 月次集計の計算式

`/api/pl/dashboard` および `/api/pl/trends` と**同じ計算式**を使う：

- 売上実績 = `Σ PlDailySales.amount`（対象月）
- FL対象経費 = `Σ PlDailyExpense.amount where category.isFLCost = true`
- その他経費 = `Σ PlDailyExpense.amount where category.isFLCost = false`
- 経費合計 = FL対象経費 + その他経費
- 営業利益 = 売上実績 − 経費合計
- FL率 = FL対象経費 / 売上実績 × 100
- 利益率 = 営業利益 / 売上実績 × 100

「ダッシュボードと CSV で数字が違う」と指摘されないよう、`getDashboardRawData` の戻り値をそのまま集計に使う。

## 2.9 UI 実装

| ファイル | 内容 |
|---------|------|
| `components/pl/CsvExportButton.tsx` | ヘッダ右上のボタン + モーダル本体 |
| `app/store/[storeId]/pl/dashboard/page.tsx` | 上記ボタンを配置 |

ダウンロードは `window.location.href = '/api/pl/export/...'` で簡潔に。エラー時はサーバが 4xx/5xx JSON を返すため、ブラウザの挙動に委ねる（v1 ではトースト出さず簡略化）。

モーダルは shadcn/ui ではなく、プロジェクト既存パターン（Tailwind ベタ書き）に合わせて自前の `fixed inset-0` Overlay で実装する。

## 2.10 既存「CSV 入力」処理との関係

既存：`lib/csv/airregiParser.ts` などは **入力（パース）用途**。本機能は **出力（生成）**用途であり、独立した `lib/csv/buildCsv.ts` として新設する。既存実装には触れない。

---

# Part 3: 5/16 MTG 回答案（Phase 計画）

## 3.1 1 段落サマリ（石川氏向け）

> PL ダッシュボードの **売上明細・経費明細・月次集計** の 3 種類とも、CSV ダウンロード機能としてご提供します。経費だけでなく、PL ダッシュボードに入力された売上もカテゴリ別に CSV 出力します。文字コードは UTF-8 BOM 付き、Excel でそのまま開ける形式で出力します。月次集計はダッシュボード画面と完全に同じ数字が出るよう、計算ロジックを共通化しています。

## 3.2 実装フェーズ提案（**更新**）

旧 Phase 計画は「経費 → 売上 → 月次集計」の順だったが、**売上と経費は同じリポジトリ／同じ CSV 組み立て構造で実装できる**ため、Phase 1 で同時実装するのが効率的。

| Phase | 内容 | 工数 | 価値 |
|-------|------|------|------|
| **Phase 1** | 売上明細 CSV + 経費明細 CSV（同時）／ UI モーダル／共通 `buildCsv` ／エラーコード | 1.2 人日 | PL ダッシュボード入力データの一次出力をまず提供。石川氏の主要ニーズ（外部分析・税理士提出）をカバー。 |
| **Phase 2** | 月次集計 CSV（dashboard 計算ロジック共通化） | 0.7 人日 | PL サマリの月次共有。Phase 1 と同時実装も可能だが、計算式の整合性確認に時間を取りたいため後続。 |
| **v1.1（将来）** | 任意の日付範囲 / 監査ログ / 推計値フラグ | — | MTG での要望次第 |

**推奨**：Phase 1 と Phase 2 を同時着手し、Phase 2 完了次第まとめてリリース（合計 2 人日見込み）。

## 3.3 5/16 MTG で確認したい論点

| # | 論点 | 理由 |
|---|------|------|
| 1 | 売上 CSV の粒度は「PL 入力ベース（日付 × カテゴリ）」で良いか | 会計明細レベルが必要なら別 CSV を v1.1 で検討 |
| 2 | 月次集計の F/L 内訳の粒度 | `isFLCost` の 2 区分で十分か、もっと細かい費目別が欲しいか |
| 3 | 監査ログの要否 | 誰がいつ落としたかの履歴を残すか |
| 4 | 経費メモの個人情報 | スタッフ名など個人情報が混入していないか確認 |
| 5 | 任意日付範囲の利用シーン | v1 は単月のみ。範囲指定が必要なら v1.1 で対応 |

---

## 付録 A: 参照ファイル

| ファイル | 用途 |
|--------|------|
| `prisma/schema.prisma` | データモデル（`PlDailySales` / `PlDailyExpense` / `PlExpenseCategory` / `PlSalesCategory` / `PlVendor`） |
| `lib/db/repositories/plDailyRepository.ts` | 日次売上・経費の範囲取得（既存再利用） |
| `lib/db/repositories/plDashboardRepository.ts` | 月次集計（既存再利用） |
| `lib/db/repositories/plMonthlyRepository.ts` | 月次目標（既存再利用） |
| `app/api/pl/export/[type]/route.ts` | **新規** エクスポート API（type = sales / expenses / monthly） |
| `lib/csv/buildCsv.ts` | **新規** CSV 組み立てヘルパー |
| `components/pl/CsvExportButton.tsx` | **新規** UI ボタン + モーダル |
| `app/store/[storeId]/pl/dashboard/page.tsx` | ボタン配置先 |
| `config/constants.ts` | エラーコード追加 |

## 付録 B: 用語

| 用語 | 定義 |
|------|------|
| 営業日付 | `PlDailySales.date` / `PlDailyExpense.date` は cutoffHour 適用済みの営業日付として保存されている |
| FL | 食材費 (Food) + 人件費 (Labor)。`PlExpenseCategory.isFLCost` で判別 |
| BOM | UTF-8 の Byte Order Mark (`﻿`)。Excel for Windows 文字化け回避 |
