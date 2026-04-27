# Cron定期実行の準備手順（Cursor CLI + AI前提）

## 1. 実行環境を固定する
- 実行ユーザーを決める（例: `rikutanaka`）
- プロジェクトルートを固定する（例: `/Users/rikutanaka/aipm_v0`）
- Python/Nodeなどランタイムのパスを確認する
  - 例: `which python3`, `which node`

## 2. ジョブの最小構成を作る
- `scripts/` にジョブ本体を作成（例: `scripts/daily_report.py`）
- 失敗時に非0終了コードを返すようにする（`sys.exit(1)` 等）
- ローカルで手動実行して成功を確認する

## 3. ログ保存先を作る
- 例: `logs/cron/`
- ジョブごとに出力ファイルを分ける
  - 例: `logs/cron/daily_report.log`
- 標準出力/標準エラーを両方記録する

## 4. 環境変数・秘密情報を分離する
- APIキーやトークンは `.env` などで管理し、リポジトリへコミットしない
- Cron実行時に必要な環境変数を明示する（Cronはシェル環境が最小）
- 必要ならラッパースクリプト（`run_daily_report.sh`）で `cd` と環境読み込みを行う

## 5. crontabを設定する
- 編集: `crontab -e`
- 確認: `crontab -l`
- 例（毎日 07:00 実行）:

```cron
0 7 * * * cd /Users/rikutanaka/aipm_v0 && /usr/bin/python3 scripts/daily_report.py >> logs/cron/daily_report.log 2>&1
```

## 6. 監視と通知を入れる
- 最低限、失敗時に検知できるようにログを確認する
- 可能なら通知連携（LINE / メール / Slack）を追加する
- 1回目は短い間隔で動作検証し、問題なければ本来スケジュールへ戻す

## 7. 運用ルール（推奨）
- ジョブごとに以下をREADMEへ明記する
  - 実行タイミング
  - 入出力ファイル
  - 失敗時の復旧手順
- 変更時は `log.md` に記録する
- 月1回、不要ジョブの棚卸しを行う

## Cursor CLI + AIで進めるコツ
- AIには「実行コマンド」「期待する出力」「失敗時条件」をセットで渡す
- まず手動実行を成功させてからCron化する（先にCron化しない）
- 1ジョブ1責務で小さく作り、連鎖処理は別ジョブに分割する
