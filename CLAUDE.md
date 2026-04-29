# CLAUDE.md - プロジェクトルール

## 必須: セッション開始時にルールファイルを読み込む

このリポジトリで作業する際は、**必ず最初に以下のファイルを読み込み**、その内容をルールとして遵守すること。

### コアルール（常時適用）
- `.cursor/rules/aios/00_aios_core.mdc` — AIOS運用の基本原則

### 運用ルール（必要に応じて参照）
| ユーザー意図 | 参照ファイル |
|---|---|
| プログラム初期化 | `.cursor/rules/aios/ops/01_program_init.mdc` |
| プロジェクト初期化 | `.cursor/rules/aios/ops/02_project_init.mdc` |
| 今日のタスク作成 / 朝の整理 | `.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| 作業（投稿案/集計/資料作成等） | `.cursor/rules/aios/ops/04_project_work.mdc` |
| 確定反映 / Stockに保存 | `.cursor/rules/aios/ops/05_finalize_to_stock.mdc` |
| 会議反映 / 議事録アップ | `.cursor/rules/aios/ops/06_meeting_close.mdc` |
| バックログ管理 | `.cursor/rules/aios/ops/07_backlog_management.mdc` |
| 進捗報告 / タスク完了 | `.cursor/rules/aios/ops/08_progress_report.mdc` |
| 今日の振り返り / 終業 | `.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| 週次振り返り | `.cursor/rules/aios/ops/10_weekly_review.mdc` |
| 月次振り返り | `.cursor/rules/aios/ops/11_monthly_review.mdc` |
| 並行タスク運用 / 状態管理 | `.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |

### ルーティング
ユーザー意図から適切な運用ルールを選ぶ詳細は `.cursor/rules/aios/10_aios_ops_router.mdc` を参照。

---

**重要**: 上記ファイルを読まずに作業を始めないこと。
