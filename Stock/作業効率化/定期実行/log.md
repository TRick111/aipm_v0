# 定期実行 — log

| 日付 | 操作 | ファイル | 備考 |
|---|---|---|---|
| 2026-04-27 | 作成 | README.md, ProjectIndex.yaml, log.md | プロジェクト初期化 |
| 2026-04-27 | 作成/更新 | Cron定期実行_準備手順.md, ProjectIndex.yaml | Cron準備手順を追加 |
| 2026-04-27 | 作成/更新 | scripts/gmail_daily_reply_report.py, scripts/run_gmail_daily_reply_report.sh, ジョブ一覧/README.md, ジョブ一覧/日次_Gmail返信要否レポート.md, ProjectIndex.yaml | 日次Gmail返信要否レポートジョブを追加 |
| 2026-04-27 | 更新 | scripts/gmail_daily_reply_report.py | gwsのJSON形式に合わせて件名/差出人/本文の取得処理を修正 |
| 2026-04-27 | 作成/更新 | README.md, テンプレート/ジョブ定義テンプレート.md, 別AIエージェント依頼プロンプト_定期実行プロジェクト再現.md, ProjectIndex.yaml | 定期実行の運用ルールと再現用プロンプトを追加 |
| 2026-04-27 | 確定反映 | Flow/202604/2026-04-27/定期実行/* | Flow内の定期実行成果物をStockへ反映 |
| 2026-06-15 | 更新 | README.md, ProjectIndex.yaml | 実行基盤の選択肢（Cron / Cockpit autorun / launchd）と launchd 常駐サービスのルールを追記 |
| 2026-06-15 | 作成 | ジョブ一覧/Markserv常駐_3ポート.md | Markserv 3ポート（8810/8811/8812）の launchd 常駐サービスをジョブ定義として追加 |
| 2026-06-15 | 反映 | ~/Library/LaunchAgents/jp.markserv.{aipm-flow,markdowns-1,dashboard-docs,aipm-flow.refresh}.plist, ~/aipm_v0/Stock/作業効率化/シェルスクリプト/refresh-markserv-flow.sh | Cockpit autorun (06e82964) を disable し、Markserv を launchd へ移行。8810 は Flow 今月+先月の symlink を動的切り替え。滞留していた waiting_confirmation タスク10件を remove |
