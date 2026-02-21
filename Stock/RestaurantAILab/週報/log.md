# log（週報）

## 2026-02-22 (データパイプライン v2: Node.js化)
- create: `Dashboard/scripts/export-rawdata.mjs` — Dashboard APIからrawdata.csvをエクスポートするNode.jsスクリプト（既存bulk-upload-*.mjsと同じlib/env.mjs利用、--env dev|prod対応）
- edit: `Dashboard/.claude/skills/dashboard-data-pipeline/skill.md` — v2.0.0へ更新。Node.jsエクスポートスクリプトに対応、アップロードは既存bulk-upload-*.mjsを使用
- edit: `skills/週報データ準備スキル.mdc` — Step 2をNode.js既存スクリプト、Step 3をexport-rawdata.mjsに変更
- edit: `ProjectIndex.yaml` — export-rawdata.mjs追加
- edit: `log.md` — 本エントリ

## 2026-01-28
- create: `Stock/RestaurantAILab/週報/ProjectIndex.yaml`
- create: `Stock/RestaurantAILab/週報/log.md`
- create: `Stock/RestaurantAILab/週報/Scripts/bfa_category_product_ranking_html.py`
- create: `Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w04/README.md`
- edit: `Stock/RestaurantAILab/週報/00_週報作成_統合プロンプト.md`
- edit: `Stock/RestaurantAILab/週報/01_週報作成プロンプトテンプレート.md`
- edit: `Stock/RestaurantAILab/週報/02_曜日深堀分析_プロンプト.md`
- edit: `Stock/RestaurantAILab/週報/03_スライド構成案作成_プロンプト.md`
- edit: `Stock/RestaurantAILab/週報/ProjectIndex.yaml`

## 2026-02-16 (データパイプライン自動化)
- create: `Scripts/dashboard_data_pipeline.py` — Dashboard APIを使ったPOS CSVアップロード＆rawdata.csvエクスポートのCLIスクリプト（upload/export/syncサブコマンド、全4店舗対応）
- create: `skills/週報データ準備スキル.mdc` — POS DL→Dashboard upload→rawdata.csv exportの全工程オーケストレーションスキル
- create: `Dashboard/.claude/skills/dashboard-data-pipeline/skill.md` — Pythonスクリプトを使ったパイプラインのClaudeスキル定義
- edit: `ProjectIndex.yaml` — dashboard_data_pipeline.py、週報データ準備スキル追加
- edit: `log.md` — 本エントリ

## 2026-02-16 (W07週報)
- create: 全4店舗のW07週報（Phase 1〜5）を一括生成
  - BFA: `2_output/BFA/2_output_2026w07/` — 31枚HTMLスライド + 中間ファイル一式
  - BBC: `2_output/BBC/2_output_2026w07/` — 31枚HTMLスライド + 中間ファイル一式
  - 麻布しき: `2_output/麻布しき/2_output_2026w07/` — 32枚HTMLスライド + 中間ファイル一式
  - キーポイント: `2_output/キーポイント/2_output_2026w07/` — 28枚HTMLスライド（日報なし）+ 中間ファイル一式
- create: 全4店舗の監査レポート・監査チェックリスト（`監査レポート_*.md` / `監査チェックリスト_*.md`）
  - BFA: A（優良）、BBC: A（優良・E4要確認1件）、麻布しき: B（良好・A2/A3不合格）、キーポイント: A（優良）
- edit: `2_output/BFA/2_output_2026w07/*.html` — スライド7の曜日別要因分解グラフを修正（色2色化・点線枠・ゼブラストライプ追加）
- edit: `2_output/キーポイント/2_output_2026w07/週報作成基礎資料.md` — 「その他」カテゴリ金額 ¥17,876→¥18,876 修正
- create: `skills/週報監査スキル.mdc` — 監査手法の標準化スキル（7カテゴリ25項目・判定基準・レポートテンプレート）
- create: `2_output/BFA/2_output_2026w07/20260209_20260215BARFIveArrows売り上げランキング.html` — BFAカテゴリ別商品売上ランキングHTML
- create: `2_output/BFA/2_output_2026w07/20260209_20260215BARFIveArrows売り上げランキング_slide.html` — 同スライド版
- edit: `ProjectIndex.yaml` — skills/、分析観点.md、入力4店舗ディレクトリ追加
- edit: `README.md` — 4店舗対応・監査システム・skillsディレクトリの記載追加
- edit: `log.md` — 本エントリ

## 2026-02-11
- create: `Stock/RestaurantAILab/週報/05_HTMLスライド作成_プロンプト.md` — フェーズ5 D3.js+HTMLスライド生成プロンプト（月報版を週報用に変換）
- edit: `Stock/RestaurantAILab/週報/00_週報作成_統合プロンプト.md` — フェーズ5追加、フロー図更新、プロンプト一覧・成果物ツリー・更新履歴追記
- edit: `Stock/RestaurantAILab/週報/ProjectIndex.yaml` — 04, 05プロンプトをfiles追加
- edit: `Stock/RestaurantAILab/週報/log.md` — 本エントリ

## 2026-02-09
- create: `Stock/RestaurantAILab/週報/1_input/pos_store_accounts.yaml`
- edit: `Stock/RestaurantAILab/週報/ProjectIndex.yaml`

