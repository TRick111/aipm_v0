# 月報生成エージェント — インターフェース仕様書

**作成日**: 2026-05-03
**作成者**: AI (mt cockpit-task-69b873c3)
**ステータス**: Draft（田中さん review 待ち）
**関連 BL**: BL-0080 (BFA 月報) / BL-0010 / BL-0034
**位置付け**: 「月報をどのように AI エージェントに作らせるか」を機械が読める形で定義する I/F 契約書

---

## 0. このドキュメントの読み方

このドキュメントは **「月報生成エージェント」というブラックボックス** を扱う側（呼び出し元 = 田中さん or オーケストレータ）と、中の実装者（プロンプト書く人 = AI）の間の契約です。

```
                      ┌───────────────────────┐
[田中さん / cron] ──→ │   月報生成エージェント  │ ──→ Dashboard /api/monthly-reports/upload
                      │  (Stock/月報/00–06)    │
                      └───────────────────────┘
                              ↑           ↓
                          Input         Output
                      (この文書 §2)   (この文書 §3)
```

このため、この文書を満たせば **誰がエージェントを書き換えても呼び出し側は壊れない** ことを保証する目的があります。

---

## 1. 用語と前提

| 用語 | 意味 |
|---|---|
| 運営会社コード | 内部で使う運営会社識別子 (`BFA`, `BBC`, `麻布しき`, `キーポイント`) |
| ストアコード | Dashboard DB 上の店舗識別子 (`bfa-001`, `bginza-001`, …)。運営会社コードと 1:1 対応 |
| 対象月 | `YYYY-MM` 形式（例: `2026-04`）。月初〜月末を自動展開 |
| Phase | プロンプト 00〜06 の 7 段階。各 Phase は独立した markdown プロンプト |
| エージェント | プロンプト 00 をエントリポイントとして 01〜06 を順に実行する AI ランナー |

**前提**:
- エージェントは Claude / Codex / Gemini いずれの LLM 上でも動く（プロンプトは tool-call non-dependent）
- ファイルシステム (`Stock/RestaurantAILab/月報/0_downloads/...` など) への読み書き権限を持つ
- Dashboard API (`/api/monthly-reports/upload`) に POST できるネットワーク権限がある

---

## 2. 入力スキーマ（Input Contract）

呼び出し元が **エージェントを起動するときに渡す引数**。

### 2.1 必須入力

| キー | 型 | 例 | 説明 |
|---|---|---|---|
| `company_code` | string (enum) | `BFA` | 運営会社コード。下記 §2.4 対応表のいずれか |
| `target_month` | string `YYYY-MM` | `2026-04` | 対象月 |
| `pos_data_path` | string (glob) | `Stock/RestaurantAILab/月報/0_downloads/BFA/2026-04/*.csv` | 該当月の POS CSV（会計明細レベル）の絶対 or repo-rooted 相対パス |
| `prev_template_path` | string \| null | `Stock/RestaurantAILab/月報/2_output/BFA/2026-03/*.html` | 前月の月報 HTML（章立て・配色を継承）。**初月は null 可** |

### 2.2 推奨入力（指定すると分析品質が上がる）

| キー | 型 | 例 | 説明 |
|---|---|---|---|
| `weekly_summary_paths` | string[] (glob) | `Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w14/週報スライド構成案.md` | 該当月内の週報構成案（4-5 本）。月報の「週別売上推移」セクションで使う |
| `prev_year_pos_path` | string (glob) \| null | `Stock/.../0_downloads/BFA/2025-04/*.csv` | 前年同月 POS（前年比計算用） |
| `daily_reports_path` | string (glob) \| null | `Stock/.../0_downloads/BFA/2026-04/daily_*.csv` | 日報 CSV（定性情報・接客イベント） |

### 2.3 任意入力（省略可）

| キー | 型 | 例 | 説明 |
|---|---|---|---|
| `events` | object[] | `[{date:"2026-04-27", note:"GW 後半 雨天"}]` | 特記イベント・天候等 |
| `submission_deadline` | string `YYYY-MM-DD` | `2026-05-03` | 提出締切（タイムスタンプ表示用） |
| `dry_run` | boolean | `false` | `true` なら Phase06 のアップロードをスキップしファイル生成のみ |
| `output_dir` | string | `Flow/<today>/RestaurantAILab/月報/<YYYY-MM>/` | 中間/最終成果物の出力先（既定: 上記） |
| `env` | `'dev' \| 'prod'` | `prod` | アップロード先環境（既定: `dev`） |

### 2.4 運営会社コード ↔ ストアコード対応表

| `company_code` | 店名 | `store_code` (Dashboard) | Blob パス前置 |
|---|---|---|---|
| `BFA` | BAR FIVE Arrows | `bfa-001` | `bfa-001/monthly-reports/` |
| `BBC` | 別天地　銀座 | `bginza-001` | `bginza-001/monthly-reports/` |
| `麻布しき` | 麻布しき 旗の台店 | `shiki-001` | `shiki-001/monthly-reports/` |
| `キーポイント` | かめや駅前店 | `kameya-001` | `kameya-001/monthly-reports/` |

エージェントはこの対応表を **エージェント内部で持つ**（`Stock/RestaurantAILab/月報/06_Dashboardアップロード_プロンプト.md` 参照）。

### 2.5 入力 JSON 例（最小構成）

```json
{
  "company_code": "BFA",
  "target_month": "2026-04",
  "pos_data_path": "Stock/RestaurantAILab/月報/0_downloads/BFA/2026-04/*.csv",
  "prev_template_path": "Stock/RestaurantAILab/月報/2_output/BFA/2026-03/20260301_20260331_BAR_FIVE_Arrows_月次報告資料.html"
}
```

### 2.6 入力 JSON 例（フル構成）

```json
{
  "company_code": "BFA",
  "target_month": "2026-04",
  "pos_data_path": "Stock/RestaurantAILab/月報/0_downloads/BFA/2026-04/*.csv",
  "prev_template_path": "Stock/RestaurantAILab/月報/2_output/BFA/2026-03/20260301_20260331_BAR_FIVE_Arrows_月次報告資料.html",
  "weekly_summary_paths": [
    "Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w14/週報スライド構成案.md",
    "Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w15/週報スライド構成案.md",
    "Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w16/週報スライド構成案.md",
    "Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w17/週報スライド構成案.md"
  ],
  "prev_year_pos_path": "Stock/RestaurantAILab/月報/0_downloads/BFA/2025-04/*.csv",
  "daily_reports_path": "Stock/RestaurantAILab/月報/0_downloads/BFA/2026-04/daily_*.csv",
  "events": [
    { "date": "2026-04-27", "note": "GW 後半 4/27-29 は雨天で予約キャンセル 4 組" }
  ],
  "submission_deadline": "2026-05-03",
  "dry_run": false,
  "env": "prod"
}
```

---

## 3. 出力スキーマ（Output Contract）

エージェントは **下記すべてを生成** し、最後に呼び出し元に成功レスポンスを返す。

### 3.1 ファイル成果物

| パス | 必須 | 形式 | 備考 |
|---|:---:|---|---|
| `<output_dir>/{startDate}_{endDate}_{店名}_月次報告資料.html` | ✅ | 単一 HTML | D3.js v7 (CDN), 内蔵 CSS, 1280×720 スライド形式 |
| `<output_dir>/月報スライド構成案.md` | ✅ | Markdown | スライド単位の章立てと数値根拠 |
| `<output_dir>/月次曜日深堀分析.md` | 推奨 | Markdown | 4-5 週分の曜日傾向 |
| `<output_dir>/_run_meta.json` | ✅ | JSON | エージェント実行メタ（§3.4） |

ファイル名規則:
- `{店名}` は半角スペース → アンダースコア (`BAR_FIVE_Arrows`)
- `{startDate}` / `{endDate}` は `YYYYMMDD`（ハイフンなし）

### 3.2 HTML の最低要件

| 要件 | 値 |
|---|---|
| 文字エンコーディング | UTF-8 (`<meta charset="UTF-8">`) |
| 外部依存 | **D3.js v7 CDN のみ**（`https://d3js.org/d3.v7.min.js`） |
| CSS | 全て `<style>` インライン（外部 CSS 禁止） |
| スライド寸法 | `1280px × 720px`（`.slide` クラスで統一） |
| ファイルサイズ | 上限 5MB（実用上 30〜80KB を想定） |
| 印刷対応 | `@media print` でスライド単位 page-break |
| 必須セクション | (1) 表紙 (2) エグゼクティブサマリー (3) 数値分析 (4) カテゴリ別分析 (5) 来月アクション、最低 5 スライド |

### 3.3 Dashboard アップロード成果物

`dry_run: false` のとき、エージェントは Phase06 で `/api/monthly-reports/upload` に POST する。レスポンスは下記形式で `_run_meta.json` に記録:

```json
{
  "success": true,
  "data": {
    "id": "<uuid>",
    "year": 2026,
    "month": 4,
    "startDate": "2026-04-01",
    "endDate": "2026-04-30",
    "title": "BAR FIVE Arrows 月次営業報告 — 2026-04",
    "fileSize": 13061,
    "createdAt": "2026-05-03T13:31:27.962Z",
    "blobUrl": "https://....public.blob.vercel-storage.com/bfa-001/monthly-reports/2026-M04.html"
  }
}
```

### 3.4 `_run_meta.json` スキーマ

```json
{
  "schema_version": 1,
  "agent": "monthly-report-agent",
  "started_at": "2026-05-03T13:00:00.000Z",
  "completed_at": "2026-05-03T13:24:32.123Z",
  "duration_ms": 1472123,
  "input": { /* §2 で渡された JSON */ },
  "phases": [
    { "phase": "01", "started_at": "...", "completed_at": "...", "status": "ok",
      "notes": "POS 集計完了 (3,214 行 → 26 営業日)" },
    { "phase": "02", "status": "ok", "notes": "曜日別分析 完了" },
    { "phase": "03", "status": "ok", "notes": "5 スライド構成案 確定" },
    { "phase": "04", "status": "skipped", "notes": "日報スライド未指定" },
    { "phase": "05", "status": "ok", "notes": "HTML 生成 13,061 byte" },
    { "phase": "06", "status": "ok", "notes": "Dashboard upload 成功", "upload_response": { /* §3.3 */ } }
  ],
  "deliverable": {
    "html_path": "Flow/202605/2026-05-03/RestaurantAILab/月報/2026-04/...html",
    "outline_path": "...月報スライド構成案.md",
    "blob_url": "https://....html"
  },
  "errors": []
}
```

---

## 4. 実行手順（Phase ごとの責務）

呼び出し元から見ると Phase は隠蔽されているが、実装者向けに記述する。

| Phase | 入力 | 出力 | プロンプト | エラー時 |
|:---:|---|---|---|---|
| 0 | §2 の入力全部 | 全 Phase orchestration | `Stock/RestaurantAILab/月報/00_月報作成_統合プロンプト.md` | input validation 失敗で fail-fast |
| 1 | POS / 日報 CSV | 集計表 + 基礎資料 .md | `01_月報作成プロンプトテンプレート.md` | CSV パース失敗時 row 単位 skip + warn |
| 2 | Phase1 出力 | 曜日深堀 .md | `02_週別深堀分析_プロンプト.md` | 営業日 < 7 日なら skip |
| 3 | Phase1+2 + 前月テンプレ | スライド構成案 .md | `03_スライド構成案作成_プロンプト.md` | 前月テンプレ欠損時はデフォルト章立て |
| 4 | （任意）日報構成案 | 日報スライド .md | `04_日報スライド作成_プロンプト.md` | `daily_reports_path` 未指定時 skip |
| 5 | Phase3 構成案 | 単一 HTML | `05_HTMLスライド作成_プロンプト.md` | D3 syntax error 時 fail（Lint 必須） |
| 6 | HTML | API POST 結果 | `06_Dashboardアップロード_プロンプト.md` | `dry_run` 時 skip / API 5xx は 3 回 retry |

各 Phase の **境界条件・エラー条件・retry ポリシー** はプロンプト本体に書く（このドキュメントは契約のみ）。

---

## 5. エラー条件と返却

### 5.1 入力 validation エラー（Phase0 で fail-fast）

| code | message | 例 |
|---|---|---|
| `INPUT-001` | `company_code` が対応表にない | `"BFA2"` を渡された |
| `INPUT-002` | `target_month` が `YYYY-MM` 形式でない | `"2026/04"` |
| `INPUT-003` | `pos_data_path` の glob が 0 件にマッチ | パス typo |
| `INPUT-004` | `pos_data_path` の CSV が必須カラムを欠く | `account_total` 列がない |

### 5.2 実行時エラー

| code | 発生 Phase | 対処 |
|---|---|---|
| `RUN-101` | Phase1 — POS 集計後の月間売上が 0 円 | データ範囲を疑う → 呼び出し元に return |
| `RUN-102` | Phase5 — D3 描画スクリプトの構文エラー | `node --check` で事前検証、fail なら return |
| `RUN-201` | Phase6 — `/api/monthly-reports/upload` が 4xx | response body をそのまま `errors[]` に積んで return |
| `RUN-202` | Phase6 — API が 5xx | 3 回まで指数バックオフ retry、最終失敗で return |

### 5.3 失敗時のレスポンス例

```json
{
  "success": false,
  "error": { "code": "INPUT-003", "message": "pos_data_path にマッチするファイルがありません: Stock/.../BFA/2026-04/*.csv" },
  "phases_completed": [],
  "deliverable": null
}
```

---

## 6. 呼び出し方の例

### 6.1 田中さんが手動で起動（typical）

```bash
# repo root から
mt cockpit spawn \
  --agent-type claude \
  --instruction "$(cat <<EOF
あなたは「月報生成エージェント」です。
Stock/RestaurantAILab/月報/00_月報作成_統合プロンプト.md を読んで、
以下の入力で月報を作成してください:

{
  "company_code": "BFA",
  "target_month": "2026-04",
  "pos_data_path": "Stock/RestaurantAILab/月報/0_downloads/BFA/2026-04/*.csv",
  "prev_template_path": "Stock/RestaurantAILab/月報/2_output/BFA/2026-03/*.html",
  "env": "prod"
}

完了したら _run_meta.json をユーザに報告してください。
EOF
)" \
  --bl BL-0080 \
  --directory /Users/rikutanaka/aipm_v0
```

### 6.2 cron で月初に自動実行（将来）

```bash
# 毎月 3 日 09:00 に前月分を生成
0 9 3 * * cd /path/to/aipm_v0 && \
  PREV_MONTH=$(date -v-1m +%Y-%m) && \
  mt cockpit spawn --agent-type claude \
    --instruction "..." --bl BL-AUTO-MONTHLY
```

### 6.3 `dry_run` で出力だけ確認したい場合

入力 JSON で `"dry_run": true` を渡す → Phase05 までは実行され HTML は出力されるが Phase06 のアップロードはスキップされる。手動で内容確認 → `node scripts/upload-monthly-report.mjs ...` で別途アップロード。

---

## 7. 検証チェックリスト（呼び出し元向け）

エージェントの実行が完了した後、呼び出し元が確認するべき項目:

- [ ] `_run_meta.json` の `phases[]` が **6 件すべて** ある（Phase04 は `skipped` でも可）
- [ ] `errors[]` が空配列
- [ ] `deliverable.html_path` のファイルが実在
- [ ] HTML を直接ブラウザで開いて 5 スライド分が表示される
- [ ] `deliverable.blob_url` がアクセス可能（または `dry_run` ならスキップ）
- [ ] Dashboard `/store/{store_code}/weekly-reports` を開くと **`M{MM}` インディゴバッジ** で月報が見える
- [ ] Dashboard `/store/{store_code}/monthly-reports/{id}` で iframe スケーリング込みで全スライドが見える

---

## 8. 既知の制約 / 今後の拡張

| 制約 | 影響 | 対応予定 |
|---|---|---|
| 同月の上書き運用 | 同じ `(store, year, month)` に再 upload すると以前の Blob は async 削除 | 仕様（履歴管理は将来別 BL） |
| 前年同月データの欠損 | 前年比計算が `N/A` になる | プロンプトで明示的に「データなし」表記 |
| 週報集計サマリの欠損 | 「週別売上推移」セクションは POS から再集計 | フォールバック実装済み |
| 月またぎ週の扱い | 4/27-5/3 のような週は当該週の数値を「該当月分のみ」按分 | Phase01 で日次集計 → 月で再合計、Phase05 で「W18(部分)」表記 |
| `output_dir` のデフォルト | `Flow/<today>/RestaurantAILab/月報/<YYYY-MM>/` 固定 | カスタム対応は v2 で |

---

## 9. 関連リソース

| 種別 | パス |
|---|---|
| プロンプト本体 | `Stock/RestaurantAILab/月報/00_月報作成_統合プロンプト.md` 〜 `06_Dashboardアップロード_プロンプト.md` |
| API 仕様 | `RestaurantAILab/Dashboard/app/api/monthly-reports/*.ts` |
| アップロードスクリプト | `RestaurantAILab/Dashboard/scripts/upload-monthly-report.mjs` |
| Prisma モデル | `RestaurantAILab/Dashboard/prisma/schema.prisma` (`MonthlyReport`) |
| 計画ドラフト | `Flow/202605/2026-05-03/RestaurantAILab/月報/dashboard_extension_plan.md` |
| 実装レビューチェックリスト | `Flow/202605/2026-05-03/RestaurantAILab/月報/review_checklist.md` |
| ダミー HTML (動作確認用) | `Flow/202605/2026-05-03/RestaurantAILab/月報/2026-04/20260401_20260430_BAR_FIVE_Arrows_月次報告資料_DUMMY.html` |

---

## 10. 田中さんへの確認事項

- [ ] 入力スキーマ §2 で **必須/推奨/任意** の区分けは適切か（特に `weekly_summary_paths` を必須にしたいか）
- [ ] 出力スキーマ §3.1 で `_run_meta.json` を必須にしているが、不要なら削除可
- [ ] エラーコード命名規則（`INPUT-NNN` / `RUN-NNN`）はこれで OK か
- [ ] 将来の cron 自動化（§6.2）は実施したいか、当面は手動運用（§6.1）で十分か
- [ ] 入力に **「前月レポートのレビュー指摘」フィードバックループ** を追加したいか（例: 「前月は鰻の話を入れすぎ」のような）
