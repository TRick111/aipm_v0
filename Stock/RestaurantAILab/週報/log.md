# log（週報）

## 2026-05-19 （月報共通ルール v2.3 を週報側に展開・マスター判断 K-1〜K-8 反映）
- create: `Stock/RestaurantAILab/週報/共通ルール.md` v1.1 — 一般ルール（業務日基準・3点セット・主張バー・分類条件帯・絵文字運用・ランキング・KPI比較値2系統 等）
- create: `Stock/RestaurantAILab/共通/BFA固有ルール.md` v1.1 — BFA-1〜BFA-8 抽出キー / ボトル扱い / 客単価2系統 / AirRegi CSV仕様 / エアメイト差異 / インバウンド運用 / 命名規則
- create: `Flow/202605/2026-05-18/週報ルール展開/_weekly_rules/classification.md` — 月報→週報 ルール分類（確定版）
- create: `Flow/.../_weekly_rules/script_changes.md` — スクリプト修正提案9件
- create: `Flow/.../_weekly_rules/questions_to_user.md` — マスター判断（回答済み）
- create: `Flow/.../_weekly_rules/script_implementation_plan.md` — #2/#3/#4 高優先の別タスク計画
- edit: `Stock/RestaurantAILab/月報/共通ルール.md` v2.4 — §3/§4/§5/§17/§19/§20 を BFA固有ルール参照に置換
- edit: `00_週報作成_統合プロンプト.md` — §0「共通ルール」セクション追加
- edit: `01_週報作成プロンプトテンプレート.md` — 参照節と完了チェック更新
- edit: `02_曜日深堀分析_プロンプト.md` — 参照節追加
- edit: `03_スライド構成案作成_プロンプト.md` — 各スライド必須構成、KPI 2系統表（K-6）反映
- edit: `04_スライド作成_プロンプト.md` — 参照節追加
- edit: `05_HTMLスライド作成_プロンプト.md` — §0「全スライド共通構成」追加、カラー K-1 確定、セルフチェック拡充
- edit: `STATUS.md` — 履歴追記、共通ルール／BFA固有ルールへのリンク追加
- backup: 上記すべてのファイルに `.bak_20260518_apply_monthly_rules` を保存
- next: スクリプト修正（合計>0 / BFAボトル除外 / TOP15＋★）は別タスクで実施 — `_weekly_rules/script_implementation_plan.md` 参照

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

