---
name: CSV エクスポート不可な媒体管理画面の Playwright スクレイピング手順
description: 食べログ等「CSV ボタンがない」管理画面から、Playwright で HTML を取得 → bs4 で CSV に整形する標準手順。今後 CSV 出力不可の媒体を増設する際のテンプレ。
type: project
last_updated: 2026-06-26
---

# Playwright スクレイピング手順 ── CSV 不可ページ用

マーケダッシュボード Phase 1.1 自動取得の **CSV エクスポートできないページ向け** 共通手順。
食べログ店舗管理画面の 5 ページで実証済み（`tabelog/` 配下）。

## 設計の3層分離

```
┌─────────────────────────────────────────────────────────┐
│ 1. 認証層 (一回だけ手動)                                │
│    login_and_save_state.py                              │
│    -> ヘッド付き Chromium で手動ログイン                │
│    -> state/storageState.json に Cookie 保存            │
├─────────────────────────────────────────────────────────┤
│ 2. フェッチ層 (定期実行)                                │
│    fetch_all.py                                         │
│    -> storageState.json をロード                        │
│    -> 5 ページの URL を順次 GET                         │
│    -> raw_html/*.html に保存                            │
├─────────────────────────────────────────────────────────┤
│ 3. パース層 (HTML → CSV、媒体非依存)                    │
│    parsers/parse_<name>.py                              │
│    -> BeautifulSoup で表/カードを抽出                   │
│    -> output/<name>.csv に出力 (UTF-8 BOMなし)          │
└─────────────────────────────────────────────────────────┘
```

**なぜ 3 層分離か**: ① 認証はセッション失効時のみ再実行する遅頻度 ② フェッチは月次実行で十分 ③ パースは HTML サンプルがあれば認証なしでも開発・テスト可能。

## 媒体ごとの実装状況

### 食べログ 5 ページ（`tabelog/`）

各 CSV 出力例は `tabelog/output/`。

| URL | パーサ | 出力CSV列 | 行数（実機サンプル） |
|---|---|---|---|
| `/owner_rst/access_report_total?display_type=monthly` | `parse_access_report_total.py` | **年月/PC/スマホ/アプリ/総合**（月次表示固定） | 13（13ヶ月分） |
| `/owner_rst/access_report_page` ※ドロップダウンで月選択 | `parse_access_report_page.py` | period_start/period_end/page_type/pv/share_percent/note | 12（**1ヶ月分のページ別**、ドロップダウン選択で月絞り込み） |
| `/owner_rst/access_report_total_conversion` | `parse_access_report_total_conversion.py` | 年月/通話成立数/ネット予約組数/地図印刷PV/全体PV | 13（13ヶ月分） |
| `/owner_rst/rstupreview_entry/?srt=visit&sby=desc&PG=1&smp=2&lc=0` | `parse_rstupreview_entry.py` | 来店日/総合評価/投稿者/本文先頭 | 20（1ページ仕様） |
| `/owner_rst/access_ranking` | `parse_access_ranking.py` | エリア/順位/店舗名/店舗エリア/ジャンル/アクセス数/前月比/is_own_shop | 101（TOP100＋自店舗1） |

### 実機HTMLで判明した非自明な仕様

- **access_report_page**: ページ別の「13ヶ月分まとめ」しか取れない構造。月次トレンドが欲しければ月パラメータを変えて複数回 fetch → 集約する追加実装が必要。
- **access_report_total_conversion**: テーブル内に `tr.device-more` というナビ行が混在するため `th[scope="row"]` の有無でデータ行を判定。
- **rstupreview_entry**: 「投稿日」は UI 上存在せず、**来店月**（YYYY/MM訪問）のみ。`YYYY-MM-01` に正規化済み。評価は `c-rating-v2--val35` のような class からフォールバック抽出。
- **access_ranking**: 自店舗が TOP100 圏外の場合、ランキング表末尾に `<tr id="my-ranking" class="outside">` の 1 行が追加される構造。順位ジャンプあり。ダッシュボードでは `is_own_shop=true` 行を別扱い推奨。
- **access_report_total**: 最終行に「合計」行があり、日付パターン非該当でスキップ。**`?display_type=monthly` 必須**（月次表示で 13ヶ月分の月別データを取得）。パーサは日次/月次の両モードを自動判別。
- **access_report_page の月絞り込み**: ページ右上「表示期間」開始月のドロップダウンを操作（Playwright MCP の `browser_select_option`）すると、自動的に `?start_month=YYYYMM&end_month=YYYYMM`（同月）に遷移する。

### ホットペッパー（HPG）クチコミ 1 ページ（`hotpepper/`）

| URL | パーサ | 出力CSV列 | 行数（実機サンプル） |
|---|---|---|---|
| `/CLP/ccm010/showReportListAllForAuth` | `parse_reviews.py` | 投稿日/総合評価/投稿者/利用シーン/最終審査日/口コミID/本文先頭 | 20（1ページ仕様） |

HPG 特有の留意点:
- **HPG は食べログとは別ドメイン**（`cms.hotpepper.jp`）→ 独立した `storageState.json` 管理。`hotpepper/login_and_save_state.py` で別途認証保存。
- **「来店日」UI なし** → `投稿日` と `利用シーン`（ランチ/ディナー）で代替。マーケダッシュボードの月次集計は「投稿日ベース」で運用（食べログは「来店月ベース」と非対称な点に注意）。
- HTML 構造: `<table class="style01 ...">` を 1 件単位で 20 回繰り返し。`<span id="contributionDateN">` (N=0..19) を抽出キー、本文は `<input id="reportTextN">` の value から取得。
- 評価詳細（料理／接客／雰囲気）は一覧画面にはなく、総合★のみ。

## 標準運用フロー

### 1. 初回セットアップ（1 回だけ）

```bash
# Python 依存
pip3 install --break-system-packages playwright beautifulsoup4 lxml
python3 -m playwright install chromium

# 認証セッション保存
cd Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/tabelog
python3 login_and_save_state.py
# -> Chromium が開く -> 手動でログイン -> Enter
# -> state/storageState.json が生成される
```

### 2. 定期実行（月次・週次）

```bash
cd Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/tabelog
./run_all.sh
# -> fetch_all.py で 5 ページの HTML を raw_html/ に保存
# -> 5 本のパーサを順次実行して output/*.csv を生成
```

### 3. セッション失効時

`fetch_all.py` が `[ERROR] セッション失効` を吐いたら、`login_and_save_state.py` を再実行して `storageState.json` を更新。

### 4. 個別ページのみ取得

```bash
python3 fetch_all.py access_report_total      # 1 ページだけ fetch
python3 parsers/parse_access_report_total.py  # そのページだけ parse
```

## 新しい CSV 不可ページを追加する手順（テンプレ）

1. **HTML 1 サンプル取得**: ブラウザでログイン状態にし、`mcp__playwright__browser_navigate` + `browser_evaluate(() => document.documentElement.outerHTML)` で raw_html を取得。または `fetch_all.py` の `PAGES` 辞書に URL を追加して fetch。
2. **HTML を bs4 で覗く**: テーブル class / id、繰り返し要素の構造、データ行と非データ行（ナビ・合計）の判別子を確認。
3. **`parsers/parse_<name>.py` 新規作成**: 既存 5 本をテンプレに、CLI `(input.html, output.csv)`、UTF-8 BOMなし、エラー時 stderr+exit1、stdout サマリ、の規約を踏襲。
4. **`fetch_all.py` の `PAGES` 辞書に URL を追加**。
5. **`run_all.sh` は変更不要**（`parsers/parse_*.py` を glob で拾うため）。

## セキュリティ・運用注意

- `state/storageState.json` は **ログイン Cookie を含む機密ファイル**。`.gitignore` で除外済み。Git にコミットしないこと。
- `raw_html/*.html` も店舗特定情報を含むため `.gitignore` で除外済み。実機サンプルは GitHub の RestaurantAILab/Dashboard 側に持たず、ローカル運用のみ想定。
- アカウントロック対策: fetch_all.py は 5 URL 順次なので連打ではないが、月初の集中アクセスは控えめに（数十秒間隔程度の余裕を取る形に将来拡張可）。
- HTML 構造はサイト更新で変わる。**月初の取得失敗 → パース失敗で気付ける** ようにモニタリングを別途仕込むこと（Phase 1.1 の課題）。

## ディレクトリレイアウト

```
tabelog/
├── .gitignore              # state/, raw_html/*.html, output/*.csv を除外
├── login_and_save_state.py # 一回だけ手動ログイン -> storageState 保存
├── fetch_all.py            # storageState ロード -> 5 URL の HTML 取得
├── run_all.sh              # fetch_all + 全パーサ実行
├── state/
│   └── storageState.json   # gitignore 対象（機密）
├── raw_html/               # gitignore 対象（店舗特定情報あり）
│   └── <name>.html         # fetch_all.py が生成
├── parsers/
│   └── parse_<name>.py     # HTML → CSV
└── output/                 # gitignore 対象
    └── <name>.csv          # 最終成果物
```

## Phase 1.1 への移行メモ

- 今は `Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/tabelog/` の PoC 位置。
- 実装が安定したら `RestaurantAILab/Dashboard` リポジトリの取り込みパイプラインに移植する。
- 移植時の改修候補:
  - storageState を環境変数で複数アカウント切替（多店舗対応）
  - `fetch_all.py` を Cron / GitHub Actions スケジュール化
  - パース失敗時に Slack/メール通知
  - HTML サンプルをスナップショットテストに使う（DOM 変化検知）
