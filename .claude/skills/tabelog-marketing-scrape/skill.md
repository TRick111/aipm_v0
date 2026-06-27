---
name: "食べログ店舗管理画面マーケKPIスクレイプ"
description: "食べログ店舗管理画面の5ページ（CSV出力不可）をPlaywright MCPで取得し、Pythonパーサで月次マーケKPIのCSVを生成する。マーケダッシュボード Phase 1.1 の取り込みパイプライン。"
version: "1.0.0"
author: "Restaurant AI Lab"
created: "2026-06-28"
updated: "2026-06-28"
dependencies:
  - playwright-mcp
  - python3
  - beautifulsoup4
  - lxml
parameters:
  - name: yearMonth
    type: string
    required: true
    description: 取得対象年月（YYYY-MM形式）。access_report_page の URL パラメータ生成に使用
    example: "2026-06"
  - name: storeContext
    type: string
    required: false
    description: 店舗識別ヒント。出力ファイル名や注釈に使用（複数店舗運用時）
    example: "ネネチキン東岡崎店"
constants:
  scraperRoot: "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/tabelog"
  sampleDataRoot: "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/sample_data/tabelog"
  loginUrl: "https://owner.tabelog.com/owner_account/login/"
  authCheckUrl: "https://owner.tabelog.com/owner_rst/access_report_total"
  endpoints:
    access_report_total: "https://owner.tabelog.com/owner_rst/access_report_total"
    access_report_page: "https://owner.tabelog.com/owner_rst/access_report_page?start_month={YYYYMM}&end_month={YYYYMM}"
    access_report_total_conversion: "https://owner.tabelog.com/owner_rst/access_report_total_conversion"
    rstupreview_entry: "https://owner.tabelog.com/owner_rst/rstupreview_entry/?srt=visit&sby=desc&PG=1&smp=2&lc=0"
    access_ranking: "https://owner.tabelog.com/owner_rst/access_ranking"
  outputPattern: "{scraperRoot}/output/{yearMonth}/{name}.csv"
  rawHtmlPattern: "{scraperRoot}/raw_html/{yearMonth}/{name}.html"
---

# 食べログ店舗管理画面マーケKPIスクレイプ

## 概要

このSkillは、食べログ店舗管理画面の **CSV エクスポートできない 5 ページ** を Playwright MCP で開き、レンダリング後の HTML をディスクに保存し、既存の Python パーサで CSV に整形する。マーケダッシュボード Phase 1.1（Playwright 自動取得）の取り込み基盤。

**取得対象ページ**:

| エンドポイント | 取得内容 | 月次粒度 | 出力CSV列 |
|---|---|---|---|
| `access_report_total` | 日別アクセス（直近1ヶ月、PC/スマホ/アプリ/総合） | △（直近1ヶ月固定） | 日付/曜日/PC/スマホ/アプリ/総合 |
| `access_report_page` | ページ別 PV・構成比 | ◯ URL パラメータで月指定 | period_start/period_end/page_type/pv/share_percent/note |
| `access_report_total_conversion` | 月別 CV（通話・ネット予約・地図印刷・全体PV） | ◯ 13ヶ月集計 | 年月/通話成立数/ネット予約組数/地図印刷PV/全体PV |
| `rstupreview_entry` | クチコミ一覧（1ページ20件、来店日降順） | ◯ 来店月ベース | 来店日/総合評価/投稿者/本文先頭 |
| `access_ranking` | エリア内アクセスランキング（TOP100＋自店舗） | ◯ 当月スナップショット | エリア/順位/店舗名/店舗エリア/ジャンル/アクセス数/前月比/is_own_shop |

詳細仕様は `/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/docs/データ取得・UI設計書_v1.md` §3.1 参照。

---

## 必要なパラメータ

| パラメータ | 必須 | 説明 | 例 |
|---|---|---|---|
| `yearMonth` | ✅ | 取得対象年月（YYYY-MM） | `2026-06` |
| `storeContext` | — | 店舗識別ヒント（複数店舗運用時の注釈用） | `ネネチキン東岡崎店` |

---

## 認証情報の取得元

食べログ店舗管理画面の ID / PW は **Playwright MCP ブラウザの保存ログイン情報**で自動入力される。Skill 起動時にログインフォームが既に埋まっている場合がほとんど。

**手順**:
1. `mcp__playwright__browser_navigate` で `authCheckUrl` に遷移
2. 遷移先がログイン画面 (`/owner_account/login/`) の場合、`mcp__playwright__browser_snapshot` でフォーム状態を確認
3. フォームが事前入力済 → 「ログインする」ボタンを `mcp__playwright__browser_click` でクリック
4. 事前入力されていない → ユーザーに対話的ログインを依頼

> セッションが生きていれば 2 は不要。直接 5 ページのフェッチに進む。

---

## ステップバイステップ手順

### Step 1: 認証確認 & ログイン

```
mcp__playwright__browser_navigate(url="https://owner.tabelog.com/owner_rst/access_report_total")
```

- 結果のURLが `/owner_rst/access_report_total` なら認証OK → Step 2 へ
- `/owner_account/login/` にリダイレクトされたら:
  - `mcp__playwright__browser_snapshot()` でフォーム確認
  - フォームが埋まっていれば「ログインする」ボタンをクリック
  - 埋まっていなければユーザーに依頼

### Step 2: 5 ページの HTML 取得

各エンドポイントを順次 navigate → evaluate で HTML を保存。

```
# 出力先ディレクトリ準備
mkdir -p {scraperRoot}/raw_html/{yearMonth}
mkdir -p {scraperRoot}/output/{yearMonth}
```

**URL パターン**（`{yearMonth}` = `2026-06` の場合 `{YYYYMM}` = `202606`）:

| name | URL（テンプレート展開後）|
|---|---|
| `access_report_total` | `https://owner.tabelog.com/owner_rst/access_report_total` |
| `access_report_page` | `https://owner.tabelog.com/owner_rst/access_report_page?start_month=202606&end_month=202606` |
| `access_report_total_conversion` | `https://owner.tabelog.com/owner_rst/access_report_total_conversion` |
| `rstupreview_entry` | `https://owner.tabelog.com/owner_rst/rstupreview_entry/?srt=visit&sby=desc&PG=1&smp=2&lc=0` |
| `access_ranking` | `https://owner.tabelog.com/owner_rst/access_ranking` |

各 URL について:

```
mcp__playwright__browser_navigate(url=<URL>)
mcp__playwright__browser_evaluate(
  function="() => document.documentElement.outerHTML",
  filename="{scraperRoot}/raw_html/{yearMonth}/{name}.html"
)
```

### Step 3: HTML アンラップ

`browser_evaluate` の結果は JSON 文字列ラップされて保存されるため、生 HTML に戻す:

```bash
cd {scraperRoot}/raw_html/{yearMonth}
for f in *.html; do
  python3 -c "import json; data=open('$f').read(); out=json.loads(data) if data.startswith('\"') else data; open('$f','w').write(out)"
done
```

### Step 4: パース実行

既存の 5 本のパーサを `parsers/parse_<name>.py` から実行:

```bash
cd {scraperRoot}
for p in parsers/parse_*.py; do
  name=$(basename "$p" .py | sed 's/^parse_//')
  python3 "$p" "raw_html/{yearMonth}/${name}.html" "output/{yearMonth}/${name}.csv"
done
```

各パーサは UTF-8 (BOM なし) で CSV を出力し、stdout に行数・列名サマリを表示する。

### Step 5: sample_data へコピー

検証用の参考データとして:

```bash
mkdir -p {sampleDataRoot}/{yearMonth}
cp {scraperRoot}/output/{yearMonth}/*.csv {sampleDataRoot}/{yearMonth}/
```

### Step 6: 結果サマリ報告

ユーザーに次を報告:
- 5 ファイル全て出力されたか
- 各 CSV の行数
- 自店舗の順位（access_ranking から）
- 当月の通話成立数 / ネット予約組数 / 全体PV（access_report_total_conversion から）

---

## 出力仕様

| ファイル | 場所 | 行数 | 列 |
|---|---|---|---|
| `access_report_total.csv` | `output/{yearMonth}/` + `sample_data/tabelog/{yearMonth}/` | 約31（直近1ヶ月分） | 日付/曜日/PC/スマホ/アプリ/総合 |
| `access_report_page.csv` | 同上 | 約12（ページ種別数） | period_start/period_end/page_type/pv/share_percent/note |
| `access_report_total_conversion.csv` | 同上 | 13（13ヶ月分） | 年月/通話成立数/ネット予約組数/地図印刷PV/全体PV |
| `rstupreview_entry.csv` | 同上 | 20（1ページ仕様） | 来店日/総合評価/投稿者/本文先頭 |
| `access_ranking.csv` | 同上 | 約101（TOP100+自店舗） | エリア/順位/店舗名/店舗エリア/ジャンル/アクセス数/前月比/is_own_shop |

すべて UTF-8 (BOM なし)、カンマ区切り、1行目ヘッダ。

---

## 既知の制約

| 制約 | 内容 | 影響 |
|---|---|---|
| `access_report_total` の月境界 | デフォルトで「直近30日」しか取れない（URL パラメータ不可） | 月初に取得しないと前月分が欠損。当月途中の値は混在 |
| `access_report_total_conversion` の月境界 | 月初確定型。当月分は通常含まれない | 6月確定値が欲しい場合は 7月初に再取得 |
| `access_report_page` 月指定 | `?start_month=YYYYMM&end_month=YYYYMM` で月別取得可（同月指定でその月だけ） | 12ヶ月推移が必要な場合は月別ループで12回 fetch |
| `rstupreview_entry` ページング | デフォルト 1 ページ目（20件）のみ。過去分が必要なら `PG=2,3,...` でループ | 月次クチコミ件数算出には「来店月が対象月」のものを件数カウント |
| `access_ranking` の自店舗位置 | 自店舗が TOP100 圏外の場合、ランキング表末尾に `<tr id="my-ranking" class="outside">` 1 行が追加される | パーサは `is_own_shop=true` で識別。順位ジャンプがあるのでダッシュボードで別扱い |
| DOM 変化 | 食べログ管理画面の HTML 構造が変わるとパース失敗 | 月初に取得失敗を検知 → 手動でパーサ修正 |

---

## エラーハンドリング

| 症状 | 対処 |
|---|---|
| Step 1 でログイン画面のフォームが空 | ユーザーに対話ログイン依頼 |
| Step 1 でログインボタン押下後もログイン画面に留まる | 認証情報が古い／2要素認証が要求された可能性。ユーザーに確認 |
| Step 2 でナビゲート後に `/owner_account/login/` にリダイレクト | セッション失効 → Step 1 をやり直し |
| Step 4 でパーサが exit 1 | HTML 構造が変わった可能性。`raw_html/{yearMonth}/<name>.html` を直接確認、パーサ修正 |
| `access_report_total_conversion` の出力に対象月が含まれない | 月初確定型のため当月途中は含まれない仕様。翌月初に再取得 |

---

## 関連ドキュメント

- データ取得・UI設計書: `/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/docs/データ取得・UI設計書_v1.md`
- パーサ実装: `{scraperRoot}/parsers/`
- 既存スクレイプ運用手順書: `/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/README.md`
- HPGクチコミ取得（兄弟Skill）: 別途 `hotpepper-reviews-scrape` として整備予定（`hotpepper/parsers/parse_reviews.py` を流用）

---

## 実行履歴

| 日付 | yearMonth | 店舗 | 結果 |
|---|---|---|---|
| 2026-06-26 | 2026-05 | ネネチキン東岡崎店 | 5ファイル成功（初回） |
| 2026-06-28 | 2026-06 | ネネチキン東岡崎店 | 5ファイル成功（v1リリース時の検証） |
