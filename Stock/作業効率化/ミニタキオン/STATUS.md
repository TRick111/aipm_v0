---
schema_version: 1
project: ミニタキオン
category: 作業効率化
status: in_progress
owner_turn: user
updated_at: 2026-05-05T07:30:00+09:00
updated_by: master-agent
current_bl: BL-0001
next_action: "Phase 5 (MCP + skill 化) 完了。USAGE.md / INTEGRATIONS.md 公開済。Critical 8 + Moderate 10 + Minor 6 の整合性 hotfix を 2026-05-05 にまとめて実施 (旧パス ~/.agi-tools/mini-tachyon/ と launchd label jp.agi-tools.mini-tachyon の残骸撤去 / launchd/install.sh 修復 / STATUS 更新 等)。次は Phase 6 (Telegram 通知) または BL-TBD-006/007 (Phase 3c/3d)"
blocker: null
related_bls: [BL-0001, BL-TBD-006, BL-TBD-007]
tech_stack:
  framework: "Next.js 16+ (App Router)"
  runtime: "Bun"
  ui: "Tailwind CSS + shadcn/ui"
  port: 3000
  mcp: "@modelcontextprotocol/sdk@1.29 (stdio)"
---

# ミニタキオン

## 🎯 次のアクション
**Phase 5 + 整合性 hotfix 完了** (2026-05-05)。利用者向け [USAGE.md](USAGE.md) と監査+起動手順 [INTEGRATIONS.md](INTEGRATIONS.md) が Stock 配下に公開済。MCP server (`bin/mt-mcp`、18 tool) と Claude Code skill (`/mini-tachyon`) も稼働中。残: BL-TBD-006 (Phase 3c cron + 承認後自動更新) / BL-TBD-007 (Phase 3d UI polish) / Phase 6 (Telegram 通知、後回し)。

## 🚧 現在のブロッカー
なし (port 3000 launchd 常駐 `jp.mini-tachyon`、tests 199/199 pass、live MCP→API e2e 確認済)

## 📋 概要

AIPMの成果物レビュー＋次指示をスマホ一画面で完結させるツール。
[Tachyon Workspace](~/tachyon-workspace) のミニ版。**作業効率化プログラム**所属。

スコープ拡張済 (2026-04-25): INBOX.md / daily_tasks.md を廃止し、その責務を全てミニタキオンが引き受ける構成。AIPM の散文ベース 3ファイル同期を、構造化データ (YAML) + UI ベースのインタラクションに置き換える。

## 🔄 進行中

なし (Phase 5 完了で BL-0001 配下のロードマップは一段落、田中さんレビュー待ち)。

## 📋 残タスク (今後着手)

- [ ] **BL-TBD-006 Phase 3c: cron + 承認後自動更新** — Phase 4 のおかげで `mt morning finalize` ベースで簡素実装可能、優先度判断
- [ ] **BL-TBD-007 Phase 3d: 「📅 今日の運用」UI 拡張 + 「📚 過去の運用」リンク** — UI polish
- [ ] **Phase 6: Telegram 通知** — 後回し (本人運用で困っていない)

## ✅ 完了済
- [x] 2026-04-25 設計確定 (Approach A 採用、INBOX 廃止スコープで改訂)
- [x] 2026-04-25 設計書作成: `Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- [x] 2026-04-25 Stock/作業効率化/ミニタキオン/ 初期化
- [x] 2026-04-25 技術スタック確定: Next.js 15+ (App Router) + Bun + Tailwind + shadcn/ui
- [x] 2026-04-25 /plan-eng-review 完了、設計書に Eng Review Decisions セクション追加 (5 issues 解決 + 1 critical gap mitigated、Lake Score 5/5)
- [x] **2026-04-25 19:57 BL-TBD-001 Phase 1 (View-only MVP) 実装完了** — 4画面 + lib/watcher (chokidar+5min fallback) + lib/index-store (BL駆動 load + singleton) + instrumentation hook + launchd plist + install.sh、prod build OK、Tailscale curl 200 OK
- [x] **2026-04-25 22:00 BL-TBD-003 UI デザイン改善 完了** — v1〜v4 の4回フィードバックループ。プロジェクト別折りたたみ / @tailwindcss/typography / レビュー待ち pill / AI 成果物→フィードバック hero / markserv リンク / UI 密度向上、Cockpit task 7d51e727 complete
- [x] **2026-04-25 22:00 schema v2 移行完了** — BL.yaml の thread → cockpit_task_ids + pending_questions + decisions に分離 (例データ8BL マイグレ済、設計書も v2 化)
- [x] **2026-04-25 22:30 BL-TBD-002 Phase 2 完了** — 書き込み機能 + クリーンアップ + マイクボタン削除、vitest 37/37 pass、launchd 本番化、Cockpit task 88973dd5
- [x] **2026-04-26 BL-TBD-004 Phase 3a (☀️ 朝の整理)** — UI ボタン + Server Action + 固定プロンプト v2 (305→175行に圧縮済)
- [x] **2026-04-26 BL-TBD-008 Phase 3a v3 修正** — create-fallback コンテキスト同梱、generating state、グルーピング修正
- [x] **2026-04-26 BL-TBD-005 Phase 3b (🌙 夜の振り返り)** — endDailyLoop / daily-wrapup.md / lib/merge.ts
- [x] **2026-04-26 BL-TBD-009 中央 Backlog.md 読み込み** — 43 active BL を統合、20 project 全表示
- [x] **2026-04-26 BL-TBD-010 「今日の選択」フィルタ** — ホームを focus、/backlog 別ページ
- [x] **2026-04-26 BL-TBD-011 Phase 4a (API + mt CLI)** — 16 endpoints、zod validate、structured error、docs 完備
- [x] **2026-04-26 BL-TBD-012 Phase 4b (prompt skill 化)** — daily-start.md 305→175行、mt CLI ベース、167 tests pass
- [x] **2026-04-26 23:30 Cleanup** — 8 leftover Cockpit tasks complete、6 BL (TBD-005/008/009/010/011/012) を mt CLI 経由で completed に更新

## 🧠 決定事項 (Why ログ)

- **2026-04-25 Approach A (Mac-hosted webapp + Tailscale) 採用、B/C 却下**
  - Notion同期は async エッジケース (削除・衝突・順序) が ocean 化、コメント→指示遅延あり
  - Telegram は markdown インライン指摘 UX が成立しない
  - Cockpit CLI が PATH 上にあり、subprocess で連携可能
- **2026-04-25 INBOX.md / daily_tasks.md 廃止、ミニタキオンに統合**
  - AIPM の3ファイル同期は人間とエージェント双方の認知負荷が高い
  - 散文ベースで構造化データとして扱いづらい
  - ミニタキオン が UI と構造化データ (YAML) で代替する
- **2026-04-25 BL ファイルは Stock 直接編集 (Flow 中間レイヤなし)**
  - BL会話は本質的に時系列累積、Flow経由だとマージ複雑化
  - ミニタキオン がファイルロックで競合回避
- **2026-04-25 STATUS.md は Flow→Stock パターン (手動マージ + 03:00 cron セーフティネット)**
- **2026-04-25 deliverables.yaml は当日 Flow のみ (Stock に上がらない)**
  - 成果物メタは「その日の出来事」、横断 query は in-memory index で処理

## 📜 履歴 (最新→古, append-only)

- 2026-05-05 16:30 整合性 hotfix: 監査 (INTEGRATIONS.md) で見つかった Critical 8 + Moderate 10 + Minor 6 を全件修正 — 旧パス `~/.agi-tools/mini-tachyon/` を `~/mini-tachyon/` に統一、launchd label `jp.agi-tools.mini-tachyon` を `jp.mini-tachyon` に統一、`launchd/install.sh` を bootstrap/bootout/kickstart 流儀に書き直し canonical な plist (`launchd/jp.mini-tachyon.plist`) を repo に同梱、STATUS.md を Phase 5 完了状態に同期、`add_comment` の `by` を `enum [user,ai]` に絞る、`bin/mt` HELP に `--due`/`--created-by` 追記、`docs/MCP.md` を 4 client 別 table に整理、`mcp-config.sample.json` を Cursor / Claude Code / Claude Desktop 形式に分割 等
- 2026-05-05 16:00 サブエージェント 2 本で `Stock/作業効率化/ミニタキオン/USAGE.md` (303 行) + `INTEGRATIONS.md` (348 行) を作成。前者は田中さん向け運用リファレンス、後者は設計監査 + MCP/skill 起動手順 (4 client)
- 2026-05-05 13:50 Phase 5 完了 (a/b/c 全部実装、本 BL とは別タスクで実施): MCP server (`bin/mt-mcp`、18 tool、stdio transport) + Claude Code skill (`~/.claude/skills/mini-tachyon/SKILL.md`、ユースケース別手順 A〜F) + 組み込み prompt を MCP-first / CLI fallback の 2 経路並記に書き換え。tests 199/199 pass、live MCP→API e2e 動作確認済
- 2026-05-05 13:00 BL-0015 で「成果物が表示されない」bug 発覚 → 根治 (`mt deliverable register` 新設で deliverables.yaml + BL.deliverable_refs を atomic 更新、index-store に bl_id 逆引き backstop 追加、組み込み prompt と rule 13 を register 1 発に書き換え)
- 2026-04-26 19:25 Phase 4 着手: BL-TBD-011 (API + CLI) を Cockpit task f285aa69 起動。BL-TBD-012 (prompt 移行) は依存待ちで pending。4/26 dogfood で drift 多発の根本対応 — エージェントを skill-calling に転換
- 2026-04-26 18:30 田中さんアーキ提案: 「ユースケースをスキル化、API 公開、エージェント連携」を Phase 4 として正式着手。実現可能性評価で 5-6 日見積り、ROI 大、推奨判断
- 2026-04-26 14:35 BL-TBD-010 ホーム「今日の選択」フィルタ + /backlog 完了 (81100e18、vitest 112 pass)
- 2026-04-26 13:25 並列2タスク起動: BL-TBD-009 (b0c9e231 中央Backlog.md読込) + BL-TBD-005 (976dc72a Phase 3b 夜の振り返り)。ファイルテリトリー明示でコンフリクト回避
- 2026-04-26 13:00 田中さんと意思決定: 朝のタスク案からループ閉じる動線が無い問題の整理 → 穴A (UI拡張) + 穴B (Phase 3c) を発見、案D (UI拡張 + Phase 3b 並列) を採用
- 2026-04-26 11:30 BL-TBD-008 v3 修正完了報告 (a4adcf48): Fix1/Fix2/Fix3 全て実装、tests 68 pass、launchd 再起動。田中さん再 dogfood 待ち
- 2026-04-26 11:05 BL-TBD-008 (Phase 3a v3 運用フィードバック修正) 起動 — Cockpit task a4adcf48。Fix1: create-fallback コンテキスト同梱 (P0)、Fix2: generating state 追加 (P1)、Fix3: needs_revision を AIの番グルーピング (P1)
- 2026-04-26 09:15 田中さん 4/26 朝の Phase 3a v2 dogfooding 完了 → BL-TBD-004 を completed 承認、BL-TBD-005 を pending → planned に。3 つの運用フィードバックを抽出
- 2026-04-26 01:00 STATUS.md bootstrap タスク 9402a54f 完了 — Backlog.md の active 19 プロジェクトに対して v2 形式 STATUS.md を README ベースで一括作成、index: projects 1 → 20
- 2026-04-26 00:15 BL-TBD-004 を Phase 3a 専用に圧縮 (タイトル変更、awaiting_user)、BL-TBD-005/006/007 新規作成 (3b/3c/3d 分割)。4/26 朝の実機テスト待ち
- 2026-04-25 23:30 Phase 3a v1 → v2 修正完了: lib/prompts/daily-start.md 305行に書き直し (中央 Backlog.md 採用、4/24 planning 形式、案件別グルーピング、クラスABC、AI回答ルール+schema厳守ルール維持)。vitest 47/47 pass。
- 2026-04-25 23:30 田中さん v1 朝の整理プロンプトを iPhone でテスト → ミニタキオンしか出てこない / ステータス階層が好みでない / 4/24 形式に合わせたい とフィードバック
- 2026-04-25 23:20 Phase 2 残骸クリーンアップ + Phase 3a 起動: example BL/STATUS/deliverables 全削除、Cockpit task 88973dd5/717658ce/0535418e complete、BL-TBD-002 を completed に、test markdown table 削除、Cockpit task 83948eeb (Phase 3a ☀️ 朝の整理) 起動
- 2026-04-25 23:15 BL-TBD-004 Daily Loop v2 設計を田中さん承認 (state: planned)。Phase 3 課題発見「AI 回答が UI に反映されない」を Phase 3a 固定プロンプトの「AI 回答ルール」と「schema 厳守ルール」として組み込みルール化
- 2026-04-25 23:00 田中さん ミニタキオンUI 上で daily_loop_design.md に needs_revision + コメント送信 → create-fallback で Cockpit task 717658ce 自動spawn → 設計書を v2 に改訂 (D1-D9 決定事項テーブル) → deliverable unreviewed に戻し再レビュー待ち。Phase 2 dogfooding 成功
- 2026-04-25 22:30 Phase 2 完了報告 (88973dd5)、マイクボタン削除も完了、vitest 37/37 pass。Daily Loop 設計書 v1 を BL-TBD-004 のレビュー物として登録 (田中さん要望)
- 2026-04-25 22:05 Phase 1 締め (Cockpit task 7d51e727 complete、BL-TBD-001 / BL-TBD-003 ✅完了) → Phase 2 起動 (Cockpit task 88973dd5、BL-TBD-002 = 書き込み機能 + クリーンアップ + done+コメント送信 UX)
- 2026-04-25 22:00 田中さん v4 確認: UI OK、コメント送信は Phase 2 で OK、「全会話を見る」削除推奨、「done + コメントで AI に送る」UX 提案 → Phase 2 仕様に統合
- 2026-04-25 21:55 BL-TBD-003 v4 完了報告 (修正7点全て対応): 「レビュー待ち」rename / マーカー撤去 → pill 明示 / BL 詳細「AI からの成果物 → AI へのフィードバック」hero / @tailwindcss/typography / markserv リンク (port 8810) / UI 密度向上
- 2026-04-25 21:50 BL-TBD-003 v4 修正指示送信 (7点): 「私の番」→「レビュー待ち」rename / オレンジ線の意味明示化 / BL詳細リデザイン (AI成果物 → AIフィードバック を hero、詳細は折りたたみ) / UI密度向上 / @tailwindcss/typography 導入 / markserv リンク (port 8810 検出済)
- 2026-04-25 21:10 BL.yaml schema v1 → v2 移行 (master が例データ8BL を手動 migrate)、設計書の BL スキーマセクション更新、Cockpit task に v2 zod 対応 + UI 変更指示送信
- 2026-04-25 20:50 BL-TBD-003 v2 修正指示送信: トップページのプロジェクト別折りたたみ化、STATUS.md の markdown レンダリング、色削減 (状態色のみ)、glassmorphism 廃止
- 2026-04-25 20:40 BL-TBD-003 v1 完了 (デザインシステム / 4画面 / AI フィードバック visual + localStorage)
- 2026-04-25 20:25 BL-TBD-003 (UI デザイン改善) を Cockpit task 7d51e727 に follow-up 送信、例データ4プロジェクト・8BL を Stock に展開 (健康管理/麻布しき/バー5アローズ + ミニタキオン BL-TBD-002, BL-TBD-003)
- 2026-04-25 20:05 master が STATUS.md frontmatter 重複キー修正、schema_version: 1 を STATUS.md と BL-TBD-001.yaml に追記 (Eng Review 2A 完全反映)
- 2026-04-25 19:57 BL-TBD-001 Phase 1 (View-only MVP) 実装完了報告 — 4画面 + watcher + index-store + launchd plist + prod build OK + Tailscale 200 OK、3つの判断事項を ESCalation
- 2026-04-25 19:35 /plan-eng-review 完了 (5 issues + 1 critical gap、Lake Score 5/5)、設計書に Eng Review Decisions セクション追加、Cockpit task 7d51e727 に更新指示送信
- 2026-04-25 18:44 BL-TBD-001 (Phase 1) を Cockpit task 7d51e727 として起動 (claude agent, dir: ~/.agi-tools/mini-tachyon)
- 2026-04-25 18:35 BL-TBD-001 yaml 作成、~/.agi-tools/mini-tachyon ディレクトリ作成 + Cockpit workspace 登録
- 2026-04-25 18:30 技術スタックを Next.js (App Router) に変更、設計書のディレクトリ構成・Phase 1/2 を更新
- 2026-04-25 18:00 Stock/作業効率化/ミニタキオン/ 作成、STATUS.md 初期化
- 2026-04-25 14:30〜18:00 /office-hours セッションで設計改訂版確定 (INBOX 廃止スコープ)
- 2026-04-25 10:42 /office-hours で初版設計確定 (V1: review hub のみ)

## 🔗 関連リンク

- 利用者向けドキュメント: [USAGE.md](USAGE.md) (10 章 / 田中さん向け運用リファレンス)
- 設計監査 + MCP/skill 起動手順: [INTEGRATIONS.md](INTEGRATIONS.md)
- 設計書 (オリジナル): `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- 当日作業フォルダ: `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/`
- 実装ディレクトリ: `~/mini-tachyon/`
- 親プロジェクト: [Tachyon Workspace](~/tachyon-workspace)
- Cockpit CLI: `/Users/rikutanaka/.agi-tools/data/cockpit/master/bin/cockpit` (`COCKPIT_BIN` env で上書き可)
- Tailscale ホスト: `rikus-mac-mini-3.tailad7d87.ts.net`
