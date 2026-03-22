# Tachyon

## 背景
- Restaurant AI Labのチームは日常的にLINEやミーティングで業務を進めているが、会議中に出たアイデアやタスクが流れてしまいがち
- 会議の音声をリアルタイムで文字起こしし、AIエージェントがタスクを提案・実行する仕組みがあれば、会議の生産性が大幅に向上する
- 元々「Albert」として検討していたLINE Bot案から方向転換し、会議ドリブン開発支援に舵を切った

## 目的
- 会議中の音声をリアルタイム文字起こしし、Claude Codeエージェントがタスクを提案・実行する会議ドリブン開発支援システムを構築する

## ゴール（完了条件）
- スマホから会議を録音し、リアルタイムでtranscriptが表示される
- エージェントがtranscriptを分析し、タスクを提案する
- ユーザーが承認したタスクをエージェントが自動実行し、結果を表示する

## 技術スタック
- Next.js 16 (App Router) + TypeScript + Tailwind CSS
- STT: OpenAI API (gpt-4o-mini-transcribe)
- エージェント: Claude Code CLI / Agent SDK
- ストレージ: ファイルベース

## 開発場所
- `~/Tachyon-Workspace/` で開発（このリポジトリ外）
- 仕様書: `~/Tachyon-Workspace/SPEC.md`

## 関係者

| 名前 | 役職 | 役割 |
|---|---|---|
| 田中利空 | Restaurant AI Lab 開発担当 | 開発・実装 |
| 吉田 | Restaurant AI Lab 代表 | 全体統括 |
| 町田大地 | Restaurant AI Lab AI担当 | AI企画 |

## 現在の状況・ネクストアクション
- 現状: 基本機能（録音→STT→transcript表示→エージェント提案→承認→実行）は動作する状態
- ネクストアクション:
  - [ ] 実運用テスト（実際の会議で使ってフィードバックを得る）
  - [ ] エージェントの安定性改善（sleep後のwaiting_confirmation問題等）
