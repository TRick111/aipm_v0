# Albert

## 背景
- Restaurant AI Lab メンバー3名（吉田・町田・田中）は、日常的にLINEで業務連絡を行っている
- ミーティング日程の調整やAIへの問い合わせを、LINEグループ内で完結させたいニーズがある
- 外部ツールを行き来せず、チャットの延長線上で業務支援を受けられるAIエージェントが求められている

## 目的
- Restaurant AI Lab 内部で使えるAIエージェント「Albert」を構築する
- LINEグループに常駐し、LLMチャットと日程調整機能を提供する
- Next.js + Vercel で構築し、LINE Messaging API / Claude API / Google Calendar API を連携する

## ゴール（完了条件）
- LINEグループで `@Albert` にメンションすると、Claude APIで応答が返る
- `@Albert 日程調整` で、3名のGoogleカレンダーから共通の空き時間が提案される
- Vercel にデプロイされ、安定稼働している

## 関係者

| 名前 | 所属・役職 | 役割 |
|---|---|---|
| 吉田 | Restaurant AI Lab 代表 | 全体統括・利用者 |
| 町田大地 | Restaurant AI Lab AI担当 | AI企画・プロンプト設計・利用者 |
| 田中利空 | Restaurant AI Lab 開発担当 | 開発・実装・利用者 |

## 現在の状況・ネクストアクション
- 現状: 計画・仕様書 v1 を策定完了（2026-02-17）
- ネクストアクション:
  - [ ] 外部サービス準備（LINE Bot作成、GCPサービスアカウント、Anthropic APIキー）
  - [ ] Next.jsプロジェクト作成・Vercelデプロイ
  - [ ] LINE Webhook 疎通確認
  - [ ] LLMチャット機能実装
  - [ ] Google Calendar連携・日程調整機能実装

## 今後のプラン（中期）

| 時期 | 項目 | 備考 |
|---|---|---|
| Phase 1 | MVP: LLMチャット + 日程調整 | LINE Bot + Claude API + Google Calendar |
| Phase 2 | 会話履歴永続化・日程確定→カレンダー登録 | Vercel KV 導入 |
| Phase 3 | タスク管理・リマインド・週報連携 | 業務支援機能の拡充 |

## 重要リンク（外部）

| 名称 | URL | 備考 |
|---|---|---|
| LINE Developers Console | https://developers.line.biz/ | Bot管理 |
| GCP Console | https://console.cloud.google.com/ | Calendar API・サービスアカウント |
| Anthropic Console | https://console.anthropic.com/ | APIキー管理 |
| Vercel Dashboard | https://vercel.com/dashboard | デプロイ管理 |
