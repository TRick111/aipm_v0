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

## 開発場所・リポジトリ
- 実装場所: `~/tachyon-workspace/tachyon/`（独立リポジトリ、AIPM リポの外）
- GitHub リポジトリ: 田中さん管理の GitHub リポに push 済（**URL 要追記**）
- 仕様書: `~/tachyon-workspace/SPEC.md`

## 実装フェーズ
- **Phase 1 完了（2026-04-22）** — BL-0062 低速タキオン Phase1
- 主要機能:
  - 生成: Claude Sonnet 4.6 SDK 直接呼び出し
  - 実行: `@anthropic-ai/claude-agent-sdk` を `bypassPermissions` + allowedTools=中（Read/Write/Edit/Glob/Grep/WebFetch/WebSearch/Bash）で起動
  - Notion DB `Tachyon ToDos` への自動同期
  - テキスト（.md/.txt）アップロードからの会議取込対応
- Phase 1 詳細ログ: `Flow/202604/2026-04-22/Tachyon/implementation_log.md`
- Phase 2 候補（別 BL 起票予定）: Notion AI Meeting Notes 直接取込 / confidence ベース自動承認 / MCP 拡張（Figma・Canva・Playwright・Vercel 等）

## 関係者

| 名前 | 役職 | 役割 |
|---|---|---|
| 田中利空 | Restaurant AI Lab 開発担当 | 開発・実装 |
| 吉田 | Restaurant AI Lab 代表 | 全体統括 |
| 町田大地 | Restaurant AI Lab AI担当 | AI企画 |

## 現在の状況・ネクストアクション
- 現状: 基本機能（録音→STT→transcript表示→エージェント提案→承認→実行）は動作する状態
- 2026-04-22: **BL-0062 低速タキオン Phase1 完了**
  - 会議close時に全文トランスクリプトを Claude Sonnet 4.6 で解析し、構造化ToDoを生成（5分以内）
  - UIで承認/編集/スキップ/実行が可能、承認時に Notion DB `Tachyon ToDos` に自動投入
  - 実行は `@anthropic-ai/claude-agent-sdk` を `bypassPermissions` + allowedTools=中（Read/Write/Edit/Glob/Grep/WebFetch/WebSearch/Bash）で起動
  - 破壊的コマンド（rm -rf / / sudo / git push --force / DROP TABLE 等15パターン）を pre-tool-use hook で自動拒否
  - 作業ディレクトリ `~/tachyon-workspace/projects/slow-exec-{todoId}/` に隔離、cwd外書込も拒否
  - タイムアウト15分、実行ログ `data/meetings/{id}/slow-exec/{todoId}/exec.log` に記録
  - テキスト（.md/.txt）アップロードから新規会議として取込→生成まで対応（Phase2で Notion AI Meeting Notes 直接取込予定）
- ネクストアクション:
  - [ ] 実運用テスト（実際の会議で使ってフィードバックを得る）
  - [ ] エージェントの安定性改善（sleep後のwaiting_confirmation問題等）
  - [ ] BL-0062 Phase2: Notion AI Meeting Notes 直接取込 / confidenceベース自動承認（Q6-rev=C） / Figma・Canva等MCP拡張
