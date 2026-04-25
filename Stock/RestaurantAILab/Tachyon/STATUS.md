---
schema_version: 1
project: Tachyon
category: RestaurantAILab
status: in_progress
owner_turn: ai
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0024
next_action: "BL-0024 町田大地さんへの Tachyon 展開を進める (実運用テスト含む)。BL-0048 タスク生成精度向上は BL-0047 完了後に並行着手"
blocker: null
related_bls: [BL-0024, BL-0025, BL-0048, BL-0049]
---

# Tachyon

## 🎯 次のアクション
BL-0024 町田大地さんへ Tachyon を展開し、実運用テストでフィードバックを得る。並行して BL-0048 タスク生成精度の向上に着手 (BL-0047 音声読み取り精度向上は 2026-04-22 で一旦完了済)。

## 🚧 現在のブロッカー
なし (Phase 1 は安定稼働中)

## 📋 概要
Restaurant AI Lab の会議をリアルタイム文字起こしし、Claude Code エージェントがタスクを提案・実行する会議ドリブン開発支援システム。元々「Albert」として LINE Bot 案を検討していたが、会議ドリブン開発支援に方向転換。Phase 1 (BL-0062) 2026-04-22 完了済 — Claude Sonnet 4.6 SDK 直接生成 + `@anthropic-ai/claude-agent-sdk` (`bypassPermissions` + allowedTools=中) で実行 + Notion DB `Tachyon ToDos` 自動同期。実装は独立リポ `~/tachyon-workspace/tachyon/` (AIPM 外)。

技術スタック: Next.js 16 (App Router) + TypeScript + Tailwind / STT: OpenAI gpt-4o-mini-transcribe / エージェント: Claude Code CLI + Agent SDK / ストレージ: ファイルベース。

関係者: 田中利空 (開発) / 吉田 (代表・統括) / 町田大地 (AI 企画)。

## 🔄 進行中
- [ ] BL-0024 Tachyon: 町田への展開 (todo / P2)
- [ ] BL-0025 Tachyon: 吉田への展開 (todo / P2)
- [ ] BL-0048 Tachyon: タスク生成精度の向上 (todo / P2, BL-0047 完了後)
- [ ] BL-0049 Tachyon: タスク管理システムとの接続 (todo / P3)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-22 BL-0062 低速タキオン Phase 1 完了 (Claude Sonnet 4.6 SDK 直接生成 + Agent SDK 実行 + 破壊的コマンドブロック + Notion DB 同期 + .md/.txt アップロード対応、E2E 3 会議以上で動作確認)
- [x] 2026-04-22 BL-0047 音声読み取り精度の向上 (一旦) 完了
- [x] Phase 1 詳細ログ: `Flow/202604/2026-04-22/Tachyon/implementation_log.md`
- [x] 7 commits (7e1f284〜c548019) を独立リポに push

## 🧠 決定事項 (Why ログ)
- 実装場所は AIPM リポ外の `~/tachyon-workspace/tachyon/` 独立リポ: AIPM Stock は仕様・タスク管理に集中、コードは独立管理
- 実行は Agent SDK + `bypassPermissions` + allowedTools=中 (Read/Write/Edit/Glob/Grep/WebFetch/WebSearch/Bash) + 破壊的コマンド15パターン pre-tool-use ブロック + cwd 隔離: 安全性と実用性のバランス
- 展開は町田 → 吉田の順 (BL-0024 → BL-0025): 実運用フィードバックの母数を段階的に拡大
- Phase 2 候補 (Notion AI Meeting Notes 直接取込 / confidence 自動承認 / MCP 拡張) は別 BL 起票予定

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/RestaurantAILab/Tachyon/README.md`
- log: `Stock/RestaurantAILab/Tachyon/log.md`
- ProjectIndex: `Stock/RestaurantAILab/Tachyon/ProjectIndex.yaml`
- 実装場所: `~/tachyon-workspace/tachyon/`
- 仕様書: `~/tachyon-workspace/SPEC.md`
- Phase 1 実装ログ: `Flow/202604/2026-04-22/Tachyon/implementation_log.md`
