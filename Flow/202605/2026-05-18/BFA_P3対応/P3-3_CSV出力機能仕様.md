# P3-3 CSV出力機能仕様

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-05-18 |
| 対象プロジェクト | BFA（バー）月報ダッシュボード |
| 関連チケット | P3-3 「CSVダウンロード可否の確認」 |
| 元論点 | `/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/対応状況_5Arrowsフィードバック_v1.md` |
| 状態 | 仕様ドラフト（5/16 MTG 回答準備用） |
| 想定実装ブランチ | `feat/csv-export` （未作成・要確認） |

## 0. サマリ

石川氏（5Arrows）より「売上明細・経費明細・月次集計を CSV で落としたい」との要望。現状の Dashboard には **CSV 入力（パース）処理は存在するが、CSV 出力（エクスポート）機能はゼロ**。新規実装が必要。

本仕様書では、外部仕様（ユーザー観点）と内部仕様（実装観点）の双方を定義し、フェーズ分割の実装計画を提示する。

---

# Part 1: ユーザーから見た仕様（外部仕様）

## 1.1 提供する CSV の種別

3 種類を提供する。

| # | 種別 | 用途 | 粒度 | データソース |
|---|------|------|------|------------|
| 1 | 売上明細 CSV | 会計レベルの売上を一次データとして外部分析へ | 1 会計 = 1 行 | `SalesData` + `SalesItem` |
| 2 | 経費明細 CSV | 経費の費目・取引先別の確認・税理士提出 | 1 経費レコード = 1 行 | `PlDailyExpense` + `PlExpenseCategory` + `PlVendor` |
| 3 | 月次集計 CSV | PL サマリ（売上 / FL / その他経費 / 利益）の月別共有 | 1 月 = 1 行（または 1 項目 = 1 行） | `PlDailySales` / `PlDailyExpense` / `PlMonthlyTarget` の月次集計 |

## 1.2 操作 UI（ボタン配置）

ダッシュボード共通ヘッダ右上に **「CSV ダウンロード」ボタン** を新設する。

クリック → モーダル表示 → 以下を選択 → 「ダウンロード」押下でブラウザにファイル保存。

### モーダルの入力項目

| 入力項目 | UI | 必須 | 備考 |
|---------|-----|------|------|
| CSV 種別 | ラジオボタン（売上明細 / 経費明細 / 月次集計） | 必須 | 1 種別ずつダウンロード |
| 期間タイプ | ラジオボタン（単月 / 任意の日付範囲） | 必須 | 月次集計は単月のみ選択可（または年単位） |
| 対象月 | 月選択（YYYY-MM） | 単月時のみ | 既定値：当月 |
| 開始日 / 終了日 | 日付ピッカー | 任意範囲時のみ | 最長 1 年とする |
| 推計値の扱い | チェックボックス「推計値を含める」 | 任意 | 既定 ON（経費明細・月次集計のみ） |

店舗は **ログイン中の店舗 ID で固定**。複数店舗を横断するエクスポートは v1 では提供しない（要確認：BFA は単店舗想定だが将来複数店舗化の可能性あり）。

## 1.3 期間指定の仕様

| CSV 種別 | 単月 | 任意の日付範囲 | 備考 |
|---------|------|--------------|------|
| 売上明細 | 〇 | 〇 | 営業日付ベース（cutoffHour 考慮） |
| 経費明細 | 〇 | 〇 | 計上日（`PlDailyExpense.date`）ベース |
| 月次集計 | 〇 | × | 1 行 = 1 月のため範囲指定は「単月のみ」または「年単位（最大 12 月）」 |

## 1.4 ファイル名命名規則

```
BFA_{種別}_{店舗コード}_{期間}.csv
```

| 種別 | ファイル名例 |
|------|------------|
| 売上明細・単月 | `BFA_売上明細_bfa01_2026-04.csv` |
| 売上明細・範囲 | `BFA_売上明細_bfa01_2026-04-01_2026-04-30.csv` |
| 経費明細・単月 | `BFA_経費明細_bfa01_2026-04.csv` |
| 月次集計 | `BFA_月次集計_bfa01_2026-04.csv` |

- `店舗コード` は `Store.storeCode`（例：`bfa01`）。
- 日本語ファイル名は `Content-Disposition: attachment; filename*=UTF-8''…` で RFC 5987 エンコードする。

## 1.5 文字コード・区切り・改行

| 項目 | 値 | 理由 |
|------|----|------|
| 文字コード | UTF-8（**BOM 付き**） | Excel for Windows での文字化け防止 |
| 区切り文字 | カンマ（`,`） | 標準 CSV |
| 改行コード | CRLF（`\r\n`） | Excel 互換 |
| 引用符 | ダブルクォート（`"`） | 値内にカンマ・改行・引用符を含む場合に必須 |
| エスケープ | ダブルクォートを `""` に置換 | RFC 4180 準拠 |

## 1.6 ヘッダー行

**1 行目は日本語ヘッダ**（石川氏含む非エンジニア利用想定のため）。英語ヘッダ版は v1 では提供しない（要確認）。

## 1.7 権限・セキュリティ

| 項目 | 仕様 |
|------|------|
| 認証 | 既存の `StoreSession`（cookie 認証）必須 |
| 店舗フィルタ | セッションの `storeId` を **強制適用**（クエリの `storeId` は session と一致しなければ 403） |
| グループ管理者 | `StoreGroupSession` 経由なら所属店舗のみ選択可（要確認：BFA は単店舗運用） |
| 監査ログ | `CsvImportLog` 相当の `CsvExportLog`（新設、要検討）に記録するか後述（内部仕様参照） |

## 1.8 数値・日付の書式

| 項目 | 書式 | 例 |
|------|------|----|
| 金額 | **税込・整数（円）** | `12,500` ではなく `12500`（**カンマ区切りなし**、Excel 側で書式設定可能なように） |
| 日付 | `YYYY-MM-DD` | `2026-04-15` |
| 日時 | `YYYY-MM-DD HH:mm:ss` | `2026-04-15 18:30:00` |
| 営業日付 | `YYYY-MM-DD`（cutoffHour 適用済み） | 売上明細のみ |
| 真偽値 | `1` / `0` | `hasReservation` 等 |
| NULL | 空文字 | `""` |

## 1.9 推計値／確定値の扱い

経費明細では `expenseType` カラムにて種別を明示する。

| `expenseType` | 表示 | 意味 |
|--------------|------|------|
| `RECURRING` | 月次固定 | 月次計上の固定費（家賃等） |
| `VARIABLE` | 変動費 | 日次計上の変動費 |
| `ESTIMATED` | 推計値 | 推計値（要確認：現スキーマで本値が定義されているか） |

月次集計 CSV では「確定済み」「推計含む」を別列で出さず、**モーダルのチェックボックスで切り替え**、ファイル名末尾に `_推計込` を付与する。

## 1.10 各 CSV のカラム定義

### 1.10.1 売上明細 CSV

`SalesData` 1 行 = CSV 1 行（明細レベル＝`SalesItem` は別 CSV／v1 では会計サマリのみ）。

| # | 列名（日本語） | 型 | サンプル値 | 備考 |
|---|--------------|-----|----------|------|
| 1 | 営業日付 | string | `2026-04-15` | cutoffHour 適用後の businessDate |
| 2 | 入店日時 | datetime | `2026-04-15 18:30:00` | `entryAt`（JST） |
| 3 | 退店日時 | datetime | `2026-04-15 21:45:00` | `exitAt`（JST） |
| 4 | 曜日 | string | `水` | `dayOfWeek` |
| 5 | 会計ID | string | `A20260415001` | `accountId` |
| 6 | 売上金額（税込） | integer | `12500` | `totalAmount` |
| 7 | 客数 | integer | `4` | `customerCount` |
| 8 | 品数 | integer | `12` | `itemCount` |
| 9 | 客単価 | integer | `3125` | 計算値（売上 / 客数）、客数 0 のとき空文字 |
| 10 | 予約有無 | integer | `1` | `hasReservation`（1/0） |
| 11 | コース利用 | integer | `0` | `isCourse`（1/0） |
| 12 | CSV取込形式 | string | `airregi` | `csvFormat` |
| 13 | 登録日時 | datetime | `2026-04-16 02:10:00` | `createdAt` |

**メモ欄について**：要望には「メモ欄付き」とあるが、`SalesData` モデルにメモ列は存在しない。**要確認**（`SalesItem` の備考か、PL 日次の備考と取り違えの可能性）。v1 ではメモ列なしで実装し、必要なら v1.1 で追加カラム検討。

### 1.10.2 経費明細 CSV

`PlDailyExpense` 1 行 = CSV 1 行。

| # | 列名（日本語） | 型 | サンプル値 | 備考 |
|---|--------------|-----|----------|------|
| 1 | 計上日 | string | `2026-04-15` | `date` |
| 2 | 費目カテゴリ | string | `食材` | `PlExpenseCategory.name`（JOIN） |
| 3 | 費目グループ | string | `原材料費` | `PlExpenseCategoryGroup.name`（JOIN, NULL 可） |
| 4 | FL対象 | integer | `1` | `PlExpenseCategory.isFLCost`（1/0） |
| 5 | 取引先 | string | `〇〇酒販` | `PlVendor.name`（JOIN, NULL 可） |
| 6 | 金額（税込） | integer | `45200` | `amount` |
| 7 | 種別 | string | `VARIABLE` | `expenseType` （`RECURRING` / `VARIABLE` 等） |
| 8 | メモ | string | `週次仕入れ` | `memo`（最大 500 文字） |
| 9 | 登録日時 | datetime | `2026-04-15 20:00:00` | `createdAt` |
| 10 | 更新日時 | datetime | `2026-04-15 20:00:00` | `updatedAt` |

### 1.10.3 月次集計 CSV

PL サマリの構造化エクスポート。

| # | 列名（日本語） | 型 | サンプル値 | 備考 |
|---|--------------|-----|----------|------|
| 1 | 対象月 | string | `2026-04` | `yearMonth` |
| 2 | 店舗コード | string | `bfa01` | `Store.storeCode` |
| 3 | 店舗名 | string | `BFA` | `Store.storeName` |
| 4 | 売上目標 | integer | `5000000` | `PlMonthlyTarget.salesTarget` |
| 5 | 売上実績（税込） | integer | `4820000` | `PlDailySales.amount` SUM |
| 6 | 売上達成率 | string | `96.4%` | 実績 / 目標、目標 0 のとき空文字 |
| 7 | 食材費 | integer | `1280000` | `PlExpenseCategory.isFLCost=true` かつ F 区分の合計（要確認：F/L の判別ロジック） |
| 8 | 人件費 | integer | `1100000` | L 区分の合計 |
| 9 | FL合計 | integer | `2380000` | 食材費 + 人件費 |
| 10 | FL率 | string | `49.4%` | FL合計 / 売上実績 |
| 11 | その他経費 | integer | `850000` | FL 対象外経費の合計 |
| 12 | 経費合計 | integer | `3230000` | FL合計 + その他経費 |
| 13 | 営業利益 | integer | `1590000` | 売上実績 - 経費合計 |
| 14 | 利益率 | string | `33.0%` | 営業利益 / 売上実績 |
| 15 | 推計値含む | integer | `1` | 1 = 推計含む / 0 = 確定値のみ |

---

# Part 2: 内部仕様（実装仕様）

## 2.1 アーキテクチャ概要

```
[ブラウザ]
  └ CSVダウンロードボタン → モーダル
        ↓ GET (Cookie auth)
[/api/export/sales]      ← 売上明細
[/api/export/expenses]   ← 経費明細
[/api/export/monthly]    ← 月次集計
        ↓
[/lib/csv/exporters/*.ts] ← サーバー側組み立て
        ↓
[Repository 層（既存）]
  ├ plDailyRepository
  ├ salesRepository（新規 or 既存リファクタ）
  └ plMonthlySummaryService（新規 or dashboard API ロジック流用）
        ↓
[Neon PostgreSQL]
```

## 2.2 API ルート設計

### 2.2.1 売上明細

```
GET /api/export/sales
  ?storeId=<uuid>
  &mode=month | range
  &month=YYYY-MM             （mode=month 時）
  &startDate=YYYY-MM-DD      （mode=range 時）
  &endDate=YYYY-MM-DD        （mode=range 時）
```

### 2.2.2 経費明細

```
GET /api/export/expenses
  ?storeId=<uuid>
  &mode=month | range
  &month=YYYY-MM
  &startDate=YYYY-MM-DD
  &endDate=YYYY-MM-DD
  &includeEstimated=true | false   （既定 true）
```

### 2.2.3 月次集計

```
GET /api/export/monthly
  ?storeId=<uuid>
  &year=YYYY                 （年単位）
  &month=YYYY-MM             （単月）
  &includeEstimated=true | false
```

### 2.2.4 共通レスポンス

| 状況 | ステータス | ヘッダ / ボディ |
|------|----------|---------------|
| 正常 | 200 | `Content-Type: text/csv; charset=utf-8`, `Content-Disposition: attachment; filename*=UTF-8''<encoded>` |
| 期間不正 | 400 | `{ success: false, error: { code: 'ERR-EXPORT-001', message: '期間指定が不正です' } }` |
| 認証なし | 401 | 既存ミドルウェアに合わせる |
| 店舗権限なし | 403 | `{ success: false, error: { code: 'ERR-EXPORT-003', message: '対象店舗へのアクセス権限がありません' } }` |
| データなし | 200 + 空 CSV（ヘッダのみ） | （**404 にはしない**：Excel で開けた方が UX 良） |
| サーバーエラー | 500 | `{ success: false, error: { code: 'ERR-EXPORT-999', message: 'エクスポートに失敗しました' } }` |

## 2.3 エラーコード（新設）

`config/constants.ts` に追加：

| コード | 意味 |
|--------|------|
| `ERR-EXPORT-001` | 期間指定が不正（開始 > 終了、範囲が 1 年超、未指定など） |
| `ERR-EXPORT-002` | 対象 CSV 種別が不正 |
| `ERR-EXPORT-003` | 店舗 ID 未指定 / 権限なし |
| `ERR-EXPORT-004` | 月次集計データの再計算失敗（dashboard サービス例外） |
| `ERR-EXPORT-999` | 想定外のサーバーエラー |

## 2.4 ストリーミング vs バッファ

| 観点 | バッファ（一括） | ストリーミング |
|------|--------------|---------------|
| 実装難度 | 低 | 中（Web Streams API or Node Readable） |
| メモリ | 行数 × 〜200byte（BFA は月 300〜500 行 → 〜100KB） | 一定 |
| Vercel タイムアウト | 300s | 300s（同じ） |
| 推奨 | **バッファで十分** | 将来 1 万行超なら検討 |

**v1 はバッファ実装**を採用。Next.js App Router の Route Handler で `Response` を直接返す：

```ts
return new Response('﻿' + csvString, {
  headers: {
    'Content-Type': 'text/csv; charset=utf-8',
    'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(fileName)}`,
  },
});
```

## 2.5 CSV 組み立てライブラリ

| 候補 | 採用判断 |
|------|---------|
| `csv-stringify`（`csv` パッケージ） | **採用候補 1**：型安全、エスケープ堅牢、依存軽量 |
| 自前実装（テンプレ文字列） | **採用候補 2**：3 種類だけなら自前で十分。`lib/csv/exporters/buildCsv.ts` に共通ヘルパー |
| `papaparse` | 入力（パース）用途であり出力には冗長 |

**推奨**：自前の `buildCsv(rows: Record<string, string|number|null>[], headers: { key: string; label: string }[]): string` を `lib/csv/exporters/buildCsv.ts` として新設。BOM 付与・CRLF・エスケープを集約。

## 2.6 BOM 付与

文字列の先頭に `﻿` を 1 文字付ける。Response 生成時に 1 か所だけで付与（exporter 関数の責務にしない）。

## 2.7 データ取得（リポジトリ再利用）

| CSV 種別 | 再利用元 | 新規追加 |
|---------|---------|---------|
| 売上明細 | （要確認）`SalesData` クエリは既存 dashboard API のロジックを参照 | `lib/db/repositories/salesRepository.ts` に `getSalesByDateRange(storeId, start, end)` を切り出し |
| 経費明細 | `lib/db/repositories/plDailyRepository.ts` の `getDailyExpenses` 系 | 必要に応じて vendor / category JOIN を追加 |
| 月次集計 | `/app/api/pl/dashboard/route.ts` の集計ロジック | `lib/services/plMonthlySummaryService.ts` として関数化 |

**重要**：月次集計は `/api/pl/dashboard` の表示用ロジックと**同じ計算式**を使うこと。乖離が出ると石川氏に「ダッシュボードと CSV で数字が違う」と指摘される。サービス層に切り出して両方から呼ぶ構造にする。

## 2.8 期間バリデーション

```ts
// lib/csv/exporters/validateRange.ts
- mode が month の場合: month = /^\d{4}-\d{2}$/ かつ実在月
- mode が range の場合: startDate <= endDate かつ (endDate - startDate) <= 366日
- いずれも未来 1 か月超を指定したら 400（要件次第、要確認）
```

## 2.9 営業日付の扱い（売上明細）

`StoreSettings.businessDayCutoffHour` を `lib/utils/businessDate.ts` の既存関数で適用し、`営業日付` 列に出す。`SalesData.entryAt` の JST 変換は既存実装と揃える。**直近 5/15 のコミット群（営業日カットオフ対応）と整合させること**（要確認：`businessDate.ts` の API シグネチャ）。

## 2.10 大量データ対策

| 項目 | 対策 |
|------|------|
| 行数上限 | 1 ファイル 10 万行（=年間に余裕、超えたら 400） |
| クエリ最適化 | 期間で WHERE、必要列のみ SELECT、`take` で上限ガード |
| Vercel Functions タイムアウト | 300s。BFA 規模では 1 秒未満想定 |
| ネットワーク | gzip は Vercel が自動付与 |

## 2.11 セキュリティ

| 観点 | 対策 |
|------|------|
| 認証 | 既存 `StoreSession` cookie を必須化（middleware で弾く） |
| 店舗 ID 改ざん | URL の `storeId` とセッションの `storeId` を必ず突合、不一致は 403 |
| ログ | `CsvExportLog`（新設）に `storeId / fileType / yearMonth / startDate / endDate / rowCount / requestedAt / requestedBy` を保存（**要確認**：監査要件があるか石川氏に質問） |
| PII | BFA の経費メモに個人名が混入する可能性あり。**要確認**：石川氏とのデータ授受で個人情報配慮が必要か |

## 2.12 既存「CSV 入力」処理との関係

既存：
```
lib/csv/
  ├ airregiParser.ts
  ├ mapper.ts
  ├ parser.ts
  ├ transformer.ts
  └ validator.ts
```

新設：
```
lib/csv/
  ├ exporters/
  │   ├ buildCsv.ts          ← 共通ヘルパー（BOM/CRLF/エスケープ）
  │   ├ exportSales.ts       ← 売上明細
  │   ├ exportExpenses.ts    ← 経費明細
  │   ├ exportMonthly.ts     ← 月次集計
  │   ├ validateRange.ts     ← 期間バリデーション
  │   └ formatters.ts        ← 数値・日付・真偽値の整形
  └ （既存 parser 系はそのまま）
```

## 2.13 UI 実装

| ファイル（想定） | 内容 |
|----------------|------|
| `components/export/CsvExportButton.tsx` | ヘッダ右上のボタン |
| `components/export/CsvExportModal.tsx` | モーダル本体（種別 / 期間 / 推計） |
| `lib/hooks/useCsvExport.ts` | `fetch` → Blob → `URL.createObjectURL` → `<a download>` クリック |
| ダッシュボード共通レイアウト | ボタンを配置（要確認：BFA 用のレイアウトファイル位置） |

ダウンロードは `<a download>` クリックではなく **`fetch` で Blob 取得 → `URL.createObjectURL`** で行う（エラー時にトーストを出すため）。

## 2.14 テスト観点

| カテゴリ | テスト項目 |
|---------|---------|
| ユニット | `buildCsv` のエスケープ（カンマ・改行・引用符を含む文字列） |
| ユニット | `validateRange` の境界値（同日 / 1 年丁度 / 1 年 + 1 日） |
| ユニット | 営業日付計算（cutoffHour=5 で深夜 4:59 が前日扱い） |
| 統合 | 経費明細 API：vendor が NULL の行が空文字で出る |
| 統合 | 月次集計：ダッシュボード表示値と CSV 値が完全一致 |
| E2E | ボタン → モーダル → ダウンロード → Excel 文字化けなし（macOS Numbers / Windows Excel 両方） |
| 手動 | BOM の有無を `hexdump` で確認 |

## 2.15 工数見積もり

| 項目 | 工数 |
|------|------|
| API ルート × 3 | 0.5 人日 |
| 共通 exporter / formatter | 0.3 人日 |
| UI（ボタン + モーダル + hook） | 0.4 人日 |
| 月次集計の計算ロジック切り出し（既存 dashboard API 流用） | 0.5 人日 |
| エラーコード追加・バリデーション | 0.1 人日 |
| テスト（ユニット + 手動 Excel 確認） | 0.3 人日 |
| ドキュメント更新（`docs/開発ルール.md` 反映） | 0.1 人日 |
| **合計** | **約 2.2 人日（バッファ込み 3 人日）** |

3 種類同時実装の場合の総工数。Phase 分割するなら下記参照。

---

# Part 3: 5/16 MTG での回答案

## 3.1 1 段落サマリ（石川氏向け）

> 売上明細・経費明細・月次集計の 3 種類とも、CSV ダウンロード機能としてご提供可能です。現状の Dashboard では CSV 出力機能は未実装のため新規開発になりますが、データはすべて DB に揃っているため、3 種類同時実装でも **約 3 人日（バッファ込み）** で完了見込みです。文字コードは UTF-8 BOM 付き、Excel でそのまま開ける形式で出力します。経費の取引先名や費目グループも JOIN して列に含めます。月次集計はダッシュボード画面と完全に同じ数字が出るよう、計算ロジックを共通化します。

## 3.2 実装フェーズ提案

| Phase | 内容 | 期間 | 価値 |
|-------|------|------|------|
| **Phase 1** | 経費明細 CSV（先行） | 0.8 人日 | 石川氏が一番求めていそうな費目別の確認・税理士提出にすぐ使える |
| **Phase 2** | 売上明細 CSV | 0.7 人日 | 会計レベル分析・他ツールとの突合 |
| **Phase 3** | 月次集計 CSV | 1.0 人日 | PL サマリの月次共有、計算ロジック切り出しが必要なため最後 |
| **横断** | UI モーダル・共通 exporter・エラーコード | 0.5 人日 | Phase 1 と同時着手 |

**推奨**：Phase 1 + 横断 を 5/22 までに先行リリース、Phase 2-3 を 5/30 までに追加リリース。

## 3.3 5/16 MTG で確認したい論点

| # | 論点 | 理由 |
|---|------|------|
| 1 | 売上明細の「メモ欄」とは具体的に何のデータか | `SalesData` 自体にメモ列なし。`SalesItem` の備考か、別データ（予約システム）かを確認 |
| 2 | 月次集計の F/L 内訳の粒度 | 「食材費・人件費」の 2 区分で十分か、もっと細かい費目別が欲しいか |
| 3 | 監査ログの要否 | 誰がいつ落としたかの履歴を残すか |
| 4 | 経費メモの個人情報 | スタッフ名など個人情報が混入していないか確認 |
| 5 | ヘッダー言語（日本語 / 英語） | システム連携先で英語ヘッダ希望があるか |
| 6 | 推計値の出力定義 | `expenseType=ESTIMATED` というスキーマ値の運用が確定済みか |
| 7 | 任意日付範囲の利用シーン | 「単月だけで十分」なら範囲モードは不要、工数 -0.3 人日 |

---

## 付録 A: 参照ファイル

| ファイル | 用途 |
|--------|------|
| `/Users/rikutanaka/RestaurantAILab/Dashboard/prisma/schema.prisma` | データモデル |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/app/api/pl/daily-expenses/route.ts` | 経費 API 既存実装 |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/app/api/pl/dashboard/route.ts` | 月次集計の計算ロジック |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/app/store/[storeId]/pl/daily/page.tsx` | 経費 UI |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/lib/db/repositories/plDailyRepository.ts` | 経費リポジトリ |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/lib/csv/` | 既存 CSV 入力処理（参考） |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/config/constants.ts` | エラーコード追加先 |
| `/Users/rikutanaka/RestaurantAILab/Dashboard/lib/utils/businessDate.ts` | 営業日付計算 |

## 付録 B: 用語

| 用語 | 定義 |
|------|------|
| 営業日付 | `entryAt` を `cutoffHour` で前日にシフトした日付。`businessDate.ts` 参照 |
| FL | 食材費 (Food) + 人件費 (Labor)。`PlExpenseCategory.isFLCost` で判別 |
| 推計値 | `expenseType=ESTIMATED` の経費（要確認：定義の確定状況） |
| BOM | UTF-8 の Byte Order Mark (`﻿`)。Excel for Windows 文字化け回避 |
