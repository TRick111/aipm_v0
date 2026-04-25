# 並行タスク ダッシュボード — 2026-04-22

最終更新: 2026-04-25 BL-0060 Claude Code Mac側 完了（Win手順書化済、Win実施は手元作業として残）

## サマリ

| 状態 | 件数 |
|---|---|
| 🟢 実行中 | 1 |
| ⏸ ユーザー対応待ち | 2 |
| 🆕 新規（要件詰め待ち） | 1 |
| ✅ 完了 | 7 |
| 合計 | 11 |

## タスク一覧

| Task ID    | BL ID   | タスク                | フェーズ    | アクション必要？                                             | INBOXセクション |
| ---------- | ------- | ------------------ | ------- | ---------------------------------------------------- | --------------- |
| `828b1bfe` | BL-0017 | マイナンバー再交付          | ✅ 完了    | — オンライン申請完了                                          | [✅ 完了](INBOX.md#-本日完了参考) |
| `34286f55` | BL-0028 | 睡眠デバイス比較           | ⏸ デバイス保留 | ❓ Vivoactive 6 vs Venu 4（明日以降）                          | [🟡 確認・判断](INBOX.md#-確認判断時間ある時) |
| `206a5614` | BL-0060 | Claude Code アップデート | ✅ Mac完了 | — Windows実施は手順書あり・本人作業 | [BL-0060](INBOX.md#bl-0060-claude-code-アップデート) |
| `86ab7e6d` | BL-0061 | AI-Core PL 計画      | ✅ 完了    | — 計画v2.1確定                                            | [✅ 完了](INBOX.md#-本日完了参考) |
| `3b95ee3a` | BL-0061 | AI-Core PL **実装フェーズ** | ✅ 完了 | — 本番デプロイ + E2E動作確認まで完了 | [BL-0061](INBOX.md#bl-0061-ai-core-pl) |
| `8aadf9da` | BL-0037 | PONチャット履歴ナレッジ化 | ✅ 完了 | — 残り田中さん側でPONさん招待のみ | [BL-0037](INBOX.md#bl-0037) |
| `f96e4e36` | BL-0062 | 低速タキオン **要件詰め** | ✅ 完了（v1.1確定） | — 実装フェーズへ引継ぎ済 | [🔵 BL-0062](INBOX.md) |
| `a1a66ab9` | BL-0062 | 低速タキオン **実装フェーズ** | ✅ 完了 | — 8 commits / Phase1 DoD 9項目達成 / Backlog=done | [✅ BL-0062](INBOX.md) |
| `1ebd755a` | BL-0053 | AIOS+G-Brain統合 **要件詰め** | ⏸ ユーザー対応待ち | ❓ Q1〜Q5（スコープA/B/C / G-Brain所在 / 大地さん稼働 / 後方互換 / マルチリポ昇格） | [🟡 BL-0053](INBOX.md) |
| `42069a3c` | BL-0061 | AI-Core LP **モバイルフィルター折りたたみ修正** | ⏸ ユーザー目視確認待ち | ❓ モバイル本番動作確認お願いします | [BL-0061](INBOX.md#bl-0061-ai-core-pl) |
| — | BL-0065 | リライフメディカル予約システム デモ作成 | 🆕 新規・要件詰め待ち | ❓ エージェント起動判断 + 要件詳細化 | [🆕 BL-0065](INBOX.md#bl-0065-リライフメディカル予約システム-デモ作成--新規) |

### フェーズ凡例
- 🆕 新規（着手前）/ 🟢 実行中 / ⏸ ユーザー対応待ち / 🔵 計画完了（次フェーズ起動待ち） / ✅ 完了 / ❌ ブロック・中断

---

## 重要な計画変更ログ

| 時刻 | タスク | 変更内容 | 理由 |
|---|---|---|---|
| 12:00頃 | BL-0028 睡眠デバイス | Oura Ring 4 → Garmin Vivoactive 6 | Q2でサブスク却下、Q6でコスト最優先と判明 |
| 12:30頃 | BL-0061 AI-Core PL | Neon Postgres + Prisma → Notion DB | Q-Bでユーザー希望「DBはNotionに」 |
| 12:45頃 | BL-0017 マイナンバー | 「更新」→「失効後の再交付」 | Q4で両方期限切れと判明、カードが既に無効状態 |
| 12:45頃 | BL-0017 マイナンバー | 優先度 P2 → P1 | カード失効が確定申告(BL-0014)に直撃するため |
| 14:25 | BL-0061 AI-Core PL | 計画 v2.0 → v2.1 | Slack通知削除、Notion `Status=未対応` 運用に統一 |
| 14:35 | BL-0028 睡眠デバイス | 判断材料追加 | **Garmin→Apple Healthに体温は流れない** = Venu 4の体温センサーはAIOS連携で活かせない |
| 14:50 | BL-0017 マイナンバー | ✅ 完了 | オンライン申請完了（net.kojinbango-card.go.jp）。新カード到着待ち |
| 14:50 | BL-0061 AI-Core PL | ✅ 計画完了 → 実装フェーズ起動 | 新タスク `3b95ee3a` を `~/RestaurantAILab/` で起動 |
| 14:55 | クラスB | 3タスク並行起動 | BL-0037（PONチャット履歴・最優先）/ BL-0062（低速タキオン）/ BL-0053（AIOS+G-Brain）を要件詰めフェーズで起動。BL-0037はゴール明確化済（インデックスだけでなくPONさん向け長期記憶ナレッジ群を生成、PONさんに送付するところまで） |
| 15:15 | BL-0037 | 計画完了 → Q1〜Q4 確認待ち | INBOX🔴セクション追加。投入先AIツール / 送付方法 / 秘匿性 / 本日スコープ |
| 15:25 | BL-0062 | 計画完了 → Q1〜Q7 確認待ち | INBOX🟡セクション追加。遅延許容 / 入力ソース / 出力先 / トリガー / 実装場所 / レビュー / メタ情報粒度 |
| 15:35 | BL-0053 | スコープ提案完了 → Q1〜Q5 確認待ち | scope_proposal.md 作成。**G-Brain本体がローカル不在**（大地さん側のみ）= Q2 がブロッカー。AI推奨スコープは案B（2-3日） |
| 15:45 | BL-0062 | Q1〜Q7 回答受領 → 4追加質問で2巡目 | **新規要件「タスク実行機能」追加**（Q3発）。Q1(5分以内)/Q5(既存Tachyon内)/Q7(スキーマ)確定。残りは Q2-rev(Notion連携時期) / Q6-rev(レビュー3案) / Q8(実行フロー) / Q9(アップロード) |
| 16:05 | BL-0062 | 🔵 計画 v1.0 確定（要件詰め完了） | 全Q回答反映: レビュー=案B(UI事前) / 実行=SDK直接 / 保存=Tachyon+Notion / 失敗=手動再実行 / アップロード=テキストのみ(新規会議扱い)。Phase1工数 14〜17h。Notion DB作成後に実装タスク起動 |
| 16:15 | INBOX運用 | プロジェクト別構造へ変更 | 田中さん方針: 緊急/確認/待機の優先度グループ化を廃止、BL ID順のプロジェクト別セクションに統一。状態は見出し横の状態タグで表示。`12_parallel_task_orchestration.mdc` と `INBOX.template.md` も更新 |
| 16:45 | BL-0037 | ✅ 全Phase完了 | GitHub repo `pon-chatgpt-knowledge` (private) に push 完了。531ファイル/4 Programs/11 LLM合成。残りは田中さんがPONさんGHアカウント確認後に Collaborator 招待のみ |
| 16:50 | BL-0061 | ✅ 実装フェーズ完了 | ユーザー指示で `3b95ee3a` を complete。本番URL https://ai-core-pl.vercel.app/ で稼働中 |
| 17:00 | BL-0062 | 計画 v1.0 → v1.1（実行エンジン変更） | 田中さん指示「タスク実行のみClaude Code CLIで」→ 生成はSDK直接維持、実行を `@anthropic-ai/claude-agent-sdk` + bypassPermissions + allowedTools に変更。MCP/bash/gws/gh 利用可。工数 14〜17h → 17〜20h。Q10(allowedTools)/Q11(承認モード) を追加投入 |
| 17:15 | BL-0062 | 🔵 計画 v1.1 確定 | Q10=B（中: fs+web+Bash+Notion MCP+Drive MCP）/ Q11=A（bypassPermissions 全自動）で確定。全ブロッカー解消、「実装着手 BL-0062」指示待ち |
| 17:20 | BL-0062 | 実装フェーズ起動 | 別エージェント `a1a66ab9` を background で起動。作業場所 `~/tachyon-workspace/tachyon/`、Phase1工数 17〜20h見積、完了通知待ち。実装中の追加確認はINBOXに自動追記される |
| 17:50 | BL-0062 | ✅ 実装フェーズ完了（見積大幅短縮） | Phase1 全項目達成、**8 commits** (`7e1f284`〜`c548019`)。見積17〜20h → 約**2〜3h**で完了（既存 `lib/meetings.ts` / `proposal-agent.ts` パターン流用、Notion REST直叩き、Agent SDK PreToolUse hook 想定通り動作が主因）。DoD 9項目達成、実会議3件でE2E確認。Stock反映+Backlog=done+MasterIndex更新済み |
| 21:25 | BL-0061 | AI-Core LP モバイルUI修正 起動 | モバイル表示でフィルターメニューがビューポートを埋め尽くす問題。`42069a3c` を `~/RestaurantAILab/ai-core-pl/` で起動。mdブレイクポイント未満でデフォルト折りたたみ、タップで展開。完了後 Vercel auto-deploy |
| 21:30 | BL-0061 | モバイルUI修正 ✅ 本番デプロイ完了 | commit `e73bf41`、Vercel auto-deploy Ready (15s)。本番モバイル動作確認済（default 折りたたみ・タップ展開・適用中バッジ・desktop 変化なし）。田中さん側で本番目視確認待ち |
| 04-25 | BL-0060 | ✅ Mac側完了・Win手順書化 | npm `2.1.117` → Native Installer `2.1.119` に切替。`~/.local/bin/claude` 配置、自動更新ON。Windows 用手順書（`claude_code_update_windows.md`）作成済 — Windows 実施は本人手元作業として残 |

---

## 関連ファイル
- ABCD分類済み本日タスク: [`../0422_daily_tasks.md`](../0422_daily_tasks.md)
- アクション一覧 + 質問・回答欄: [`INBOX.md`](INBOX.md)
- 運用ルール: `.cursor/rules/aios/ops/12_parallel_task_orchestration.mdc`
