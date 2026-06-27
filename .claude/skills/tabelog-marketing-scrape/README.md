# 食べログ店舗管理画面マーケKPIスクレイプ Skill

このSkillは、食べログ店舗管理画面の**CSV出力ボタンが存在しない 5 ページ**から月次マーケKPIを自動取得する手順を Claude Code/Agent に提供する。

## いつ使うか

- マーケダッシュボードの月次データ更新（月初）
- 単月の食べログ KPI（PV / CV / クチコミ / 順位 / ページ別PV）を取りたい
- Phase 1.1 自動取得運用のテスト・デバッグ

## 取得対象

| 項目 | 取得元 | 月次粒度 |
|---|---|---|
| 日別アクセス（PC/スマホ/アプリ/総合） | `/owner_rst/access_report_total` | △ |
| ページ別 PV・構成比 | `/owner_rst/access_report_page?start_month=YYYYMM&end_month=YYYYMM` | ◯ |
| 月別 CV（通話・ネット予約・地図印刷・PV） | `/owner_rst/access_report_total_conversion` | ◯ |
| クチコミ一覧（最新20件） | `/owner_rst/rstupreview_entry/?srt=visit&sby=desc&PG=1&...` | ◯ |
| エリア内アクセスランキング | `/owner_rst/access_ranking` | ◯ |

## 呼び出し方

サブエージェントに `skill.md` を読ませて手順実行。

主要パラメータ:
- `yearMonth`: `YYYY-MM`（例: `2026-06`）

## 詳細

`skill.md` を参照。フロントマターに URL パターン・出力先・依存ツールが定義されている。
