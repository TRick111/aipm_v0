# BL-0080 — 計画ドラフト: ダッシュボードアプリ「週報＋月報」表示拡張 + 月報作成プロンプトのインプット定義

**作成日**: 2026-05-03
**作成者**: AI (mt cockpit-task-f2830076)
**ステータス**: Draft（田中さん review 待ち）
**関連 BL**: BL-0080 (BFA 月報 4月分) / BL-0010 (依存 BL) / BL-0034 (ダッシュボードあり方)

---

## 0. 背景と狙い

### 田中さん指示 (2026-05-03 朝)

> ダッシュボードアプリの週報のエリアを、週報および月報を表示するように仕様を変えたい。
> 今、週報の一覧が並んでいるところに、同じように並列で月報も並べたい。
> ただし、色やタグなどを変えて、月報だとわかるようにする。
> 並ぶのは時系列順。月報自体は週報と同じような HTML 形式で作成する。

### 設計上の狙い

- 既存の週報運用 (Phase1 POSデータ → Phase2 週報作成 → Phase3 Dashboard アップロード) と同じ流れに **月報** を**最小差分で**載せる
- ストア管理者が **「週報確認」画面 1 枚で時系列に把握**できる UI に統合する
- 月報生成プロンプトは週報の `00_週報作成_統合プロンプト.md` 〜 `06_Dashboardアップロード_プロンプト.md` 構造を **そのまま流用**し、集計粒度だけを「週」→「月」に切り替える

---

## 1. 現状把握 (As-Is)

### 1.1 ダッシュボードアプリの構成 (RestaurantAILab/Dashboard)

| レイヤ | 場所 | 役割 |
|---|---|---|
| ストアホーム | `app/store/[storeId]/page.tsx` | アプリカード 3 種 (売上 / PL / **週報確認**) を表示。色= `amber` (アンバー) で統一 |
| 週報リスト | `app/store/[storeId]/weekly-reports/page.tsx` | 年でグルーピング → 各週カード（`W##` バッジ + 開始-終了日 + ファイルサイズ） |
| 週報ビューア | `app/store/[storeId]/weekly-reports/[weekId]/page.tsx` | 単一 HTML を iframe で表示 |
| API GET | `app/api/weekly-reports/route.ts` (`?storeId=`) | `listWeeklyReports(storeCode)` で年別グループ化 JSON |
| API GET HTML | `app/api/weekly-reports/[id]/html/route.ts` | Blob から HTML をプロキシ配信 (Content-Disposition inline 強制) |
| API POST | `app/api/weekly-reports/upload/route.ts` (admin) | multipart/form-data: `file, storeCode, year, week, startDate, endDate, title` |
| Repo | `lib/db/repositories/weeklyReportRepository.ts` | Prisma 経由で WeeklyReport CRUD |
| Storage | `lib/storage/blob.ts` | Vercel Blob に `storeCode/year/week/...html` で保存 |
| Prisma model | `prisma/schema.prisma` | `WeeklyReport(id, storeId, year, week, startDate, endDate, title, blobUrl, fileSize, createdAt, updatedAt)` |

### 1.2 週報プロンプト構造 (RestaurantAILab/週報/)

`00_週報作成_統合プロンプト.md` を入口に、01〜06 を順次実行:

| Phase | プロンプト | 入力 | 出力 |
|---|---|---|---|
| 0 | 統合 (00) | 運営会社コード / 対象週 (ISO) / 終了日 | 全 Phase オーケストレーション |
| 1 | 基礎資料 (01) | 上記＋ POS DL データ | 集計表 + Markdown 基礎資料 |
| 2 | 曜日深堀分析 (02) | Phase1 出力 | 曜日別所見 Markdown |
| 3 | 構成案 (03) | Phase1+2 | スライド構成案 Markdown |
| 4 | 日報スライド (04) | 構成案 | 日報スライド差し込み |
| 5 | HTML スライド (05) | 構成案 | 単一 HTML (D3.js v7 + 内蔵 CSS) |
| 6 | Dashboard アップロード (06) | HTML | `/api/weekly-reports/upload` POST |

POS DL は Playwright 経由 (排他ロック)、HTML 出力は単一ファイル (D3.js CDN のみ外部参照)。

---

## 2. 変更計画 (To-Be)

### 2.1 全体方針

**最小破壊で月報を追加**。週報 (Weekly) の構造を **抽象化せず、月報 (Monthly) を並走モデル** として平行追加する。1 ページに **時系列マージ** したリストを描画する。

理由:
- 既存週報の運用 (POS / Playwright / 自動アップロード) を壊さない
- DB スキーマも `weekly_reports` を改名せず `monthly_reports` を新設するだけで済む
- UI もリスト merge だけなのでバグ表面が狭い

### 2.2 DB / Prisma 拡張

**新規モデル**: `MonthlyReport` を `weekly_reports` と並列で追加。

```prisma
model MonthlyReport {
  id        String   @id @default(uuid()) @db.Uuid
  storeId   String   @map("store_id") @db.Uuid
  year      Int
  month     Int      // 1-12
  startDate DateTime @map("start_date") @db.Date    // 月初日
  endDate   DateTime @map("end_date")   @db.Date    // 月末日
  title     String   @db.VarChar(200)
  blobUrl   String   @map("blob_url")  @db.VarChar(500)
  fileSize  Int?     @map("file_size")
  createdAt DateTime @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt DateTime @updatedAt        @map("updated_at") @db.Timestamptz(6)
  store     Store    @relation(fields: [storeId], references: [id], onDelete: Cascade)

  @@unique([storeId, year, month])
  @@index([storeId, year])
  @@map("monthly_reports")
}
```

`Store` モデルに `monthlyReports MonthlyReport[]` を追加。マイグレーション名: `add_monthly_reports`。

### 2.3 ストレージ (Vercel Blob)

パスを `storeCode/year/M{MM}/...html` で分離（既存週報は `storeCode/year/W{WW}/...html` 想定）。`lib/storage/blob.ts` に `uploadMonthlyReportToBlob`, `deleteMonthlyReportFromBlob` を週報の対称関数として追加。

### 2.4 API ルート (新設)

| ルート | メソッド | 役割 |
|---|---|---|
| `/api/monthly-reports?storeId=` | GET | 年×月でグループ化リスト返却 |
| `/api/monthly-reports/[id]/html` | GET | Blob HTML プロキシ (Content-Disposition inline) |
| `/api/monthly-reports/upload` | POST (admin) | multipart upload (`file, storeCode, year, month, startDate, endDate, title`) |
| `/api/monthly-reports/[id]` | GET / DELETE | メタ取得・削除 |

実装は `app/api/weekly-reports/*` の対称コピー。Repository: `lib/db/repositories/monthlyReportRepository.ts` を `weeklyReportRepository.ts` をベースに作成。

#### 統合エンドポイント (オプション、推奨)

UI が 1 度の fetch で時系列マージを取れるよう、以下を追加すると最も綺麗:

- `GET /api/store-reports?storeId=` → `[ { kind: 'weekly'|'monthly', id, year, period, startDate, endDate, title, fileSize } ]` を `endDate desc` で返す

UI 側 fetch 1 回・並び替えロジック不要に。週報 / 月報の API は単独でも残す (admin upload UI 用)。

### 2.5 UI (`app/store/[storeId]/weekly-reports/page.tsx` のリプレース)

**A. ルート名**: 既存の `/store/[storeId]/weekly-reports` は維持（URL は変えない / ブックマーク互換）。タイトルだけ「週報・月報」に変更。

ストアホーム (`app/store/[storeId]/page.tsx`) のカード `'weekly-reports'` の表示文言を「**週報・月報確認**」に、description を「週次・月次の営業報告資料の閲覧」に更新。

**B. リスト構造**: 年セクション内で **時系列降順 (endDate desc)** にマージ表示。

```
2026年
├── M04  2026-04-01 〜 2026-04-30   (月報・濃いタグ色)
├── W17  2026-04-21 〜 2026-04-27
├── W16  2026-04-14 〜 2026-04-20
├── W15  2026-04-07 〜 2026-04-13
├── W14  2026-03-31 〜 2026-04-06
├── M03  2026-03-01 〜 2026-03-31   (月報)
├── W13  ...
```

**C. 視覚差別化**:

| 種別 | バッジ文字 | 配色 | アイコン (任意) |
|---|---|---|---|
| 週報 | `W##` (零詰め) | `text-amber-700 bg-amber-50` (既存維持) | calendar |
| 月報 | `M##` (零詰め) | `text-indigo-700 bg-indigo-100 ring-1 ring-indigo-300` | book |

差別化のポイント:
- カード背景は同じ白だが **左ボーダー 4px** を月報は `border-l-indigo-500`、週報は `border-l-amber-400`
- 月報カードは `font-semibold` で項目名を強調
- Hover 色も対応 (`hover:border-indigo-400` / `hover:border-amber-400`)

**D. 必要な型** (`types/weekly-report.ts` を `types/store-report.ts` に拡張、または並列で `types/monthly-report.ts` 追加):

```ts
export type StoreReportKind = 'weekly' | 'monthly';
export interface StoreReportListItem {
  kind: StoreReportKind;
  id: string;
  year: number;
  period: number;       // weekly: ISO週番号, monthly: 1-12
  startDate: string;    // 'YYYY-MM-DD'
  endDate: string;      // 'YYYY-MM-DD'
  title: string;
  fileSize: number | null;
}
export interface StoreReportsByYear {
  year: number;
  reports: StoreReportListItem[];
}
```

**E. ビューアルート**:

- 週報: `/store/[storeId]/weekly-reports/[weekId]` → 既存維持
- 月報: `/store/[storeId]/monthly-reports/[monthId]` → 新規 (週報ビューアの対称コピー)

リスト内でカードクリック時、`kind` に応じてルートを切替。

**F. 管理画面**:

`/admin` 配下に「月報アップロード」フォームを追加 (週報フォームの対称コピー、`year/month` 入力)。

### 2.6 月報生成プロンプト (週報からの delta)

`Stock/RestaurantAILab/月報/` 配下に **00〜06 構造を週報からコピーして月報用に書き換え**:

```
Stock/RestaurantAILab/月報/
├── 00_月報作成_統合プロンプト.md
├── 01_月報作成プロンプトテンプレート.md
├── 02_月次曜日深堀分析_プロンプト.md  (4-5週分の曜日傾向)
├── 03_月次スライド構成案作成_プロンプト.md
├── 04_月次日報スライド作成_プロンプト.md  (任意)
├── 05_HTMLスライド作成_プロンプト.md  (週報と同形式・タイトルだけ "月次" に)
└── 06_Dashboardアップロード_プロンプト.md  (POST → /api/monthly-reports/upload)
```

**月報固有の差分**:

- 集計粒度: 週 → **月 (4-5 週分)** に拡張
- 月次 PL 観点 (売上 / コスト / 客単 / 来客 / 営業日 / 月間トップ商品 / 前月比 / 前年同月比) を必須セクション化
- 月の振り返り (好調日・不調日・天候・イベント・来月予測) を構成案に追加
- HTML 出力: 同じ `D3.js v7 + 内蔵 CSS` パターン。タイトルだけ `{店舗名} 月次営業報告 — {YYYY-MM}`

### 2.7 月報作成プロンプトの「想定インプット」

田中さんが今日の最初の確認事項として求めているのが下記。**月報生成 AI に渡すインプット (最小セット)** を定義:

| 項目 | 必須 | 説明 | 例 |
|---|:-:|---|---|
| `運営会社コード` | ✅ | 店舗識別子 | `BFA` (BAR FIVE Arrows) |
| `対象月` | ✅ | `YYYY-MM` 形式 | `2026-04` |
| `月初日 / 月末日` | ✅ | ISO 日付 | `2026-04-01` / `2026-04-30` |
| `店舗名 (表示用)` | ✅ | 表示タイトル用 | `BAR FIVE Arrows` |
| `POS データ` | ✅ | 該当月の全売上 CSV (会計明細レベル) | `0_downloads/BFA/2026-04/*.csv` |
| `前月テンプレ HTML` | 推奨 | 前月の月報 HTML (構成 / 配色 / 章立てを継承) | `2_output/BFA/2026-03/*.html` |
| `週報集計サマリ` | 推奨 | 該当月内の週報 (4-5本) のメタと主要 KPI | `2_output/BFA/2026-W14〜W17/週報スライド構成案.md` |
| `前年同月データ` | 推奨 | 比較用 | `0_downloads/BFA/2025-04/*.csv` |
| `特記イベント / 天候` | 任意 | コメント用 | "GW 後半 4/27-29 は雨天" |
| `提出締切` | 任意 | 表示・タイムスタンプ用 | `2026-05-03` |

**マスタープロンプト テンプレ** (週報 `00` の対称形):

```text
月報を作成してください（メタプロンプト）。

## インプット情報
- 運営会社: {運営会社コード}
- 対象月: {YYYY-MM}
- 月初日 / 月末日: {YYYY-MM-DD} / {YYYY-MM-DD}
- 前月テンプレ: {file path}
- 週報集計サマリ: {file path glob}

## 実行手順
1. ./01_月報作成プロンプトテンプレート.md に従って基礎資料を作成
2. ./02_月次曜日深堀分析_プロンプト.md に従って分析
3. ./03_月次スライド構成案作成_プロンプト.md に従って構成案
4. ./05_HTMLスライド作成_プロンプト.md に従って HTML 生成
5. ./06_Dashboardアップロード_プロンプト.md に従って /api/monthly-reports/upload へ POST

## 最終成果物
- ./2_output/{運営会社}/{YYYY-MM}/月報スライド構成案.md
- ./2_output/{運営会社}/{YYYY-MM}/{startDate}_{endDate}_{店名}_月次報告資料.html
- Dashboard 上で月報が閲覧可能であること
```

---

## 3. 実装 PR 分割案 (推奨)

| # | PR タイトル | 範囲 |
|:-:|---|---|
| 1 | feat(db): MonthlyReport モデル追加 | Prisma schema + migration + repository + 単体テスト |
| 2 | feat(api): /api/monthly-reports CRUD | GET list / GET html / POST upload / DELETE。型は `types/monthly-report.ts` |
| 3 | feat(api): /api/store-reports 統合エンドポイント | 週報＋月報マージ・時系列降順 |
| 4 | feat(ui): store/[storeId]/weekly-reports → 統合表示 | リスト UI を `kind` に応じて分岐。月報カードは indigo タグ + 左ボーダー |
| 5 | feat(ui): /store/[storeId]/monthly-reports/[monthId] ビューア | 週報の対称コピー |
| 6 | feat(admin): 月報アップロードフォーム | `/admin` 内に月報用フォーム追加 |
| 7 | feat(prompt): Stock/RestaurantAILab/月報/ 00〜06 プロンプト整備 | 週報 prompts のコピー + 月次差分書き換え |

**最小ローンチ (今日〜数日)**: PR1 + PR2 + PR4 + PR7 で「BFA 4月分の月報を月報用フォーマットで生成 → 既存 admin 経由で一旦 weekly_reports と別系統で表示」までは可能。PR5/6 はその次の週で OK。

---

## 4. 今日の月報提出の進め方 (BL-0080 本日対応)

田中さん「テンプレは後ほど提供」とのことなので、本日の段取り:

1. **AI 側 (今すぐ)**: 本ドキュメントを review してもらう (構成 / 色分け / インプット定義に関する田中さんの方向性確認)
2. **田中さん側**: 前月 (2026-03 分) の月報 HTML テンプレを提供 (元になるファイル or イメージ)
3. **AI 側 (テンプレ受領後)**: 上記「マスタープロンプト テンプレ」のインプットを埋め、`Flow/202605/2026-05-03/RestaurantAILab/月報/2026-04/` 配下に Phase1〜5 を実行 → 単一 HTML 生成
4. **田中さん側**: 内容 review → 既存 admin の weekly-reports upload (一旦) で BFA 2026-04 として登録 (新エンドポイント未実装のため)
5. **後追い**: 次の数日で PR1〜4 を着地、admin に月報専用フォームを提供。アップロード済 HTML を移行

---

## 5. 田中さんへの確認事項

- [ ] **配色**: 月報= indigo (`indigo-500`+`indigo-100`)、週報= amber (既存) で OK か？ 別案: 月報= 深緑 (`emerald-700`)、月報= 紫 (`violet-500`) など
- [ ] **タグ文字**: `M04` (零詰め月) で OK? `2026-04` (フル) を選ぶ?
- [ ] **時系列マージ**: 同じ年セクション内 endDate desc で問題ないか？ (月報を年セクションの「先頭」に固定する案も可)
- [ ] **URL ルート**: `/weekly-reports` 名は維持で OK? (内部的に「週報・月報リスト」という意味になる)。クリーンに `/reports` へ rename も可
- [ ] **PR 分割**: PR1+2+4+7 を最小ローンチとして良いか? それとも段階リリース vs 一括 PR の好みは?
- [ ] **本日提出**: 今日中の提出は (a) 既存 weekly-reports に月報 HTML を週報扱いで暫定 upload、または (b) 月報の HTML を Drive 等で先に共有 → Dashboard 反映は後追い、どちらが良い?

---

## 6. 関連ファイル

| パス | 役割 |
|---|---|
| `Dashboard/app/store/[storeId]/weekly-reports/page.tsx` | UI 改修対象 |
| `Dashboard/app/api/weekly-reports/route.ts` | 参考 (月報 API のひな型) |
| `Dashboard/prisma/schema.prisma` | `MonthlyReport` モデル追加先 |
| `Dashboard/lib/storage/blob.ts` | `uploadMonthlyReportToBlob` 追加先 |
| `Stock/RestaurantAILab/週報/00_週報作成_統合プロンプト.md` | 月報 00 の元 |
| `Stock/RestaurantAILab/週報/05_HTMLスライド作成_プロンプト.md` | 月報 05 の元 |
| `Stock/RestaurantAILab/月報/` (新設) | 月報プロンプト一式 |

---

## 7. 次アクション (calendar)

| 期限 | アクション | 担当 |
|---|---|---|
| 5/3 中 | 本ドキュメントの方針合意 | 田中さん review |
| 5/3 中 | 前月テンプレ HTML を AI に渡す | 田中さん |
| 5/3 中 | 月報 4月分 HTML 生成 → 提出 | AI → 田中さん |
| 5/4-5/5 | PR1+2 着地 (DB + API) | AI |
| 5/5-5/7 | PR4 (UI 統合) + PR7 (プロンプト一式) | AI |
| 5/7-5/10 | PR5 (ビューア) + PR6 (admin form) | AI |
