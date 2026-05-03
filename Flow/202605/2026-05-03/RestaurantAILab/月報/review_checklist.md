# BL-0080 — 実装完了レポート + レビュー項目チェックリスト

**作成日**: 2026-05-03
**作成者**: AI (mt cockpit-task)
**ステータス**: Implementation done — 田中さん review 待ち
**関連 BL**: BL-0080 (BFA 月報 4月分) / BL-0010 / BL-0034
**前段プラン**: `dashboard_extension_plan.md` (同フォルダ、5/3 朝に承認済み)

---

## TL;DR

- ダッシュボードアプリの **「週報・月報確認」エリア** を実装完了
- 月報を週報と並列モデルで追加（DB / API / UI / 統合エンドポイント / アップロードスクリプト）
- 週報の URL とコンポーネントは温存（`/weekly-reports` のまま、内部は週報＋月報のマージリストに変身）
- `Stock/RestaurantAILab/月報/` の Phase06（Dashboard アップロード）プロンプトを補完
- **未実施**: マイグレーションの DB 適用、本番デプロイ、4月分 BFA 月報 HTML の生成（テンプレ受領待ち）

実装は **dev ブランチで未コミット** の状態。コミット・PR・デプロイは田中さん review 後に実施します。

---

## 1. 実装したもの一覧

### 1.1 ファイル変更まとめ（Dashboard リポジトリ）

| 種別 | パス | 役割 |
|---|---|---|
| modified | `prisma/schema.prisma` | `MonthlyReport` モデル追加 + `Store.monthlyReports` リレーション |
| new | `prisma/migrations/20260503130000_add_monthly_reports/migration.sql` | `monthly_reports` テーブル CREATE + インデックス + FK |
| new | `types/monthly-report.ts` | `MonthlyReportSummary` / `MonthlyReportDetail` / `MonthlyReportsByYear` |
| new | `types/store-report.ts` | 統合 `StoreReportListItem` (kind: 'weekly'\|'monthly') |
| new | `lib/db/repositories/monthlyReportRepository.ts` | list / get / create / delete（週報リポの対称コピー） |
| modified | `lib/storage/blob.ts` | `uploadMonthlyReportToBlob` / `deleteMonthlyReportFromBlob` を追加 |
| new | `app/api/monthly-reports/route.ts` | GET 一覧 |
| new | `app/api/monthly-reports/[id]/route.ts` | GET 詳細 / DELETE (admin) |
| new | `app/api/monthly-reports/[id]/html/route.ts` | Blob HTML プロキシ |
| new | `app/api/monthly-reports/upload/route.ts` | POST upload (admin, multipart) |
| new | `app/api/store-reports/route.ts` | 週報＋月報マージ・年別グループ・endDate 降順 |
| modified | `app/store/[storeId]/page.tsx` | カード文言: "週報確認" → "週報・月報確認" |
| modified | `app/store/[storeId]/weekly-reports/page.tsx` | `/api/store-reports` を fetch して merged 表示に差し替え |
| new | `app/store/[storeId]/monthly-reports/[monthId]/page.tsx` | 月報ビューア（週報ビューアの対称コピー） |
| new | `scripts/upload-monthly-report.mjs` | コマンドラインアップローダ（`upload-weekly-report.mjs` の対称形） |

### 1.2 ファイル変更まとめ（aipm_v0 リポジトリ）

| 種別 | パス | 役割 |
|---|---|---|
| new | `Stock/RestaurantAILab/月報/06_Dashboardアップロード_プロンプト.md` | Phase06 プロンプト（既存 00–05 を補完） |
| new | `Flow/202605/2026-05-03/RestaurantAILab/月報/review_checklist.md` | 本ドキュメント |

`Stock/RestaurantAILab/月報/` には既に 00〜05 のプロンプトが存在していたため、新規作成は 06 のみ。00〜05 は既存内容を活用する想定（4月分生成時に内容を再確認 → 必要なら修正）。

---

## 2. 田中さんがレビューすべき項目（チェックリスト）

> 各項目を上から順に確認していただけると助かります。
> ❓ がついている項目は、私から田中さんへの質問（pending_questions に書き戻し済）。

### 2.1 設計・スコープの整合性

- [ ] **計画ドラフト (`dashboard_extension_plan.md`) 通りの実装か** — DB / API / UI / プロンプト構造が朝の計画と一致していること
- [ ] **PR 分割案** — 計画では PR1+2+4+7 が最小ローンチだったが、実装では **PR3 (`/api/store-reports` 統合エンドポイント)** も同時に投入した（UI が 1 fetch で済む、後述の 2.4 で体感できる）。これで OK か
- [ ] **既存週報運用への影響なし** — `/api/weekly-reports/*` / `weekly_reports` テーブル / 既存 admin スクリプトは完全に温存。週報リスト URL も `/store/[id]/weekly-reports` のまま

### 2.2 DB スキーマ・マイグレーション

- [ ] **`MonthlyReport` モデル** — 週報と同じフィールド構成（`year` / `month` だけ差分）。`@@unique([storeId, year, month])` で同月の上書き運用を担保
- [ ] **マイグレーション SQL** — `prisma/migrations/20260503130000_add_monthly_reports/migration.sql`
  - `IF NOT EXISTS` でべき等
  - FK は `pg_constraint` チェックで二重投入回避（既存パターンと同じ）
- [ ] **Blob パス命名** — `{storeCode}/monthly-reports/{year}-M{MM}.html` （週報の `W{WW}` と対称、衝突なし）
- ❓ **マイグレーションの DB 適用タイミング** — このまま `prisma migrate deploy` してよいか、それともレビュー後にまとめて流すか

### 2.3 API 仕様

- [ ] **認可ルール** — 週報と完全同じ:
  - GET 系: `getSession()` 必須、`role === 'store'` は自店のみ、`admin` は全店
  - DELETE / upload: `admin` 限定
- [ ] **`/api/monthly-reports/upload` バリデーション** — `month` は 1–12 のみ受け付け、それ以外は 400
- [ ] **`/api/monthly-reports/[id]/html`** — `Content-Disposition: inline` 強制 + `Cache-Control: public, max-age=3600` (週報と同じ)
- [ ] **`/api/store-reports`** — 週報＋月報を並列 fetch → `endDate desc` でマージ → 年別グルーピング。同じ `endDate` が並んだ場合は **monthly を先（上）** にソート（月報 = 月次まとめなので上の方がレビューしやすい想定）

### 2.4 UI / 視覚設計

- [ ] **ストアホームのカード** — 「週報確認」→「週報・月報確認」、description も「週次・月次の…」に更新
- [ ] **リスト 1 ページ** — 1 fetch (`/api/store-reports`) で年別 → 時系列降順
- [ ] **凡例バー** — リスト上部に小さく「□ 週報 / □ 月報」を表示（色分けの意味を明示）
- [ ] **配色（重要、変更可）**:
  - 週報: `border-l-amber-400` + `text-amber-700 bg-amber-50` （**従来踏襲**）
  - 月報: `border-l-indigo-500` + `text-indigo-700 bg-indigo-100 ring-1 ring-indigo-300` + `font-semibold`
- [ ] **タグ文字** — 週報 `W##` / 月報 `M##` （零詰め 2 桁）
- [ ] **ビューアルート** — 週報: `/weekly-reports/[weekId]` （既存）/ 月報: `/monthly-reports/[monthId]` （新設、対称コピー）
- ❓ **配色案の確認** — indigo で本当に OK か。代替案（emerald / violet など）に差し替える場合、修正は `weekly-reports/page.tsx` 内の `ReportRow` 関数と `monthly-reports/[monthId]/page.tsx` のヘッダ部 2 箇所のみ
- ❓ **同 endDate 時の並び順** — 同じ endDate（例: 2026-04-30 が月報 M04 と週報 W17 の終端と一致するパターン）で **monthly を上** にしたが、逆（weekly 上）の方が直感的か？

### 2.5 アップロードスクリプト

- [ ] **`scripts/upload-monthly-report.mjs`** — `upload-weekly-report.mjs` の対称形
  - 引数: `--file --store --month --title --env`
  - `--month` は `YYYY-MM`、month は 1–12 バリデーション
  - 月初日 / 月末日は UTC で自動計算（`new Date(Date.UTC(y, m-1, 1))` / `Date.UTC(y, m, 0)`）
  - 既存 `lib/env.mjs` を流用（admin ログイン → multipart POST）
- [ ] **既存の admin ログインフロー** — `storeCode: 'admin'` + `ADMIN_PASSWORD` で動作（週報スクリプトと同じ）

### 2.6 プロンプト（aipm_v0/Stock/RestaurantAILab/月報/）

- [ ] **00〜05 は既存** — 朝の計画時点で発見できなかった既存ファイル。中身は私はまだ精査していない。**4月分の月報生成時に内容再確認 → 必要なら修正** という運用にしている
- [ ] **06_Dashboardアップロード_プロンプト.md（新規）** — 週報の Phase06 を月報に翻訳。`upload-monthly-report.mjs` を呼ぶ手順、ストアコード対応表、エラー対応、チェックリストを完備
- ❓ **00〜05 の内容レビュー** — 既存の 00〜05 が今回の API（`/api/monthly-reports/upload` POST）と整合しているかは未確認。**4月分生成と同時にチェックする想定** で良いか、それとも先に整合性監査だけ別タスクで切り出すか

### 2.7 BL-0080 本体（4月分の月報そのもの）

- ❓ **テンプレ HTML の提供** — 計画では「田中さんから前月（2026-03 分）月報 HTML テンプレを受領 → Phase1〜5 を実行 → 単一 HTML 生成」だった。本日中の生成希望か、別日に回すか
- [ ] **テンプレ受領後の段取り** — `Flow/202605/2026-05-03/RestaurantAILab/月報/2026-04/` に入力配置 → 00〜05 プロンプトを実行 → 06 で `bfa-001` にアップロード

---

## 3. 検証メモ（私が確認したこと / していないこと）

### 3.1 ✅ 確認済み

- `npx prisma generate` 成功（`MonthlyReport` 型が Prisma Client に反映）
- `npx tsc --noEmit` で **新規追加ファイルすべて型エラーなし**
  （pre-existing なテスト関連エラーは複数あるが、すべて私の変更と無関係）
- ファイル配置・命名規則が週報と完全対称になっていること

### 3.2 ⚠️ 未確認 / 未実施

- **`prisma migrate deploy` で実 DB に適用** — 田中さん判断待ち（dev / prod とも未適用）
- **実際の HTML アップロード** — テンプレ HTML 未受領のため動作テスト不可（API ルート単体は logic 上問題なし）
- **`useAuth` フックの再ログイン挙動** — 既存週報ページから流用（同フック）なので回帰なしと判断、E2E は未実施
- **iframe スケーリング** — 月報ビューアは週報ビューアの完全コピーなので同等動作の想定。実 HTML が来たら再確認

---

## 4. 次アクション

| 期限 | アクション | 担当 |
|---|---|---|
| 5/3 中 | 本チェックリスト review → OK / 要修正のフィードバック | 田中さん |
| 5/3 中 | review OK 後、コミット → PR (`feat(reports): add monthly report parallel to weekly`) → dev デプロイ | AI |
| 5/3 中 | 前月（2026-03）月報 HTML テンプレ提供 | 田中さん |
| 5/3 中 | テンプレ受領後、4 月分 BFA 月報を 00〜05 で生成 → 06 で `bfa-001` にアップロード | AI |
| 5/4 以降 | 本番マイグレーション → 本番デプロイ → 田中さんがブラウザで `M04` バッジを確認 | AI + 田中さん |

---

## 5. mini-tachyon 上の対応

- 本ドキュメントを deliverable `d-bl0080-20260503-implementation` として登録
- `mt deliverable update-state d-bl0080-20260503-implementation --state unreviewed` 実行
- 配色・並び順・既存 00〜05 プロンプトのレビュー方針について **3 件 BL に質問を追加** （pending_questions）
- 実装完了は **commitment** として BL-0080 に記録

田中さんへ: チェックリスト確認後「**タスククローズしてください**」と書いていただければ、cockpit task を complete します。
