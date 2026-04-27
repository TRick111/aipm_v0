# ジョブ定義: 日次_Gmail返信要否レポート

## ジョブID
- `job_daily_gmail_reply_classification`

## 目的
- 前日に受信したGmailを対象に「返信必要 / 返信不要」を自動分類し、件数レポートを当日の作業フォルダへ保存する。

## 実行タイミング
- 毎日 07:00（JST）を想定

## 実行コマンド
```bash
cd /Users/rikutanaka/aipm_v0 && bash "Stock/作業効率化/定期実行/scripts/run_gmail_daily_reply_report.sh"
```

## Cron設定例
```cron
0 7 * * * cd /Users/rikutanaka/aipm_v0 && bash "Stock/作業効率化/定期実行/scripts/run_gmail_daily_reply_report.sh" >> "Stock/作業効率化/定期実行/logs/cron_daily_gmail_reply_report.log" 2>&1
```

## 入力（Input）
- Gmail APIアクセス権（`gws` CLIの認証済み状態）
- 対象期間: 前日 00:00-当日 00:00 の受信メール
- 取得データ:
  - メッセージID
  - 件名
  - 差出人
  - 受信日時
  - スニペット

## 処理（Operation）
1. 前日受信分のメール一覧を取得する
2. 各メールのヘッダー/本文スニペットを読み込む
3. ルールベースで「返信必要 / 返信不要」を判定する
4. 件数集計と明細をMarkdownレポート化する
5. 当日のFlow作業フォルダに保存する

## 出力（Output）
- 保存先: `Flow/YYYYMM/YYYY-MM-DD/定期実行/`
- 出力ファイル: `日次_Gmail返信要否レポート_YYYY-MM-DD.md`
- 出力内容:
  - 総メール数
  - 返信必要件数
  - 返信不要件数
  - 返信必要メールの明細
  - 返信不要メールの一覧

## 失敗時の対応
- `gws auth status` で認証状態を確認
- スクリプト単体実行でエラー再現:
  - `python3 Flow/202604/2026-04-27/定期実行/scripts/gmail_daily_reply_report.py`
- Cron実行ログを確認し、PATHや実行権限を修正

## 補足
- 本ジョブの判定は一次分類（簡易）であり、最終判断は手動確認を前提とする。
