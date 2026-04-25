---
schema_version: 1
project: ミニタキオン
category: 作業効率化
status: in_progress
owner_turn: ai
updated_at: 2026-04-25T23:20:00+09:00
updated_by: master-agent
current_bl: BL-TBD-004
next_action: "Phase 3a (☀️ 朝の整理) 着手 — 新 Cockpit task で実装"
blocker: null
related_bls: [BL-TBD-001, BL-TBD-002, BL-TBD-003, BL-TBD-004]
tech_stack:
  framework: "Next.js 15+ (App Router)"
  runtime: "Bun"
  ui: "Tailwind CSS + shadcn/ui"
  port: 3000
---

# ミニタキオン

## 🎯 次のアクション
**Phase 2 完了 + Phase 3 設計改訂版レビュー待ち**:
- BL-TBD-004 (Daily Loop Phase 3) の改訂版 daily_loop_design.md を iPhone で再レビュー
- 田中さん OK なら Phase 3a (☀️ 朝の整理) 着手のため新タスク起動

## 🚧 現在のブロッカー
なし (Phase 1 prod build + curl 動作確認済、prod サーバ稼働中)

## 📋 概要

AIPMの成果物レビュー＋次指示をスマホ一画面で完結させるツール。
[Tachyon Workspace](~/tachyon-workspace) のミニ版。**作業効率化プログラム**所属。

スコープ拡張済 (2026-04-25): INBOX.md / daily_tasks.md を廃止し、その責務を全てミニタキオンが引き受ける構成。AIPM の散文ベース 3ファイル同期を、構造化データ (YAML) + UI ベースのインタラクションに置き換える。

## 🔄 進行中

- [ ] **BL-TBD-004 Phase 3a: ☀️ 朝の整理ボタン** — Cockpit task 83948eeb で実装中 (claude agent, 2026-04-25 23:17 開始)
  - ホーム画面の ☀️ ボタン
  - 「📅 今日の運用」セクション
  - Server Action `startDailyLoop()`
  - 固定プロンプト (AI 回答ルール + schema 厳守ルール 組み込み)
  - vitest テスト追加
- [ ] (今後) Phase 3b 🌙 / 3c cron+自動更新 / 3d 過去の運用リンク

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
- [x] **2026-04-25 23:00 Phase 2 dogfooding 成功** — 田中さんが ミニタキオン上で daily_loop_design.md に needs_revision を実行、create-fallback で Cockpit task 717658ce が自動 spawn、設計書を v2 (D1-D9 決定事項テーブル付き) に改訂、deliverable を unreviewed に戻して再レビュー待ち
- [x] **2026-04-25 23:15 Daily Loop 設計 v2 田中さん承認** (BL-TBD-004 done) — Phase 3 課題発見「AI 回答が UI に反映されない」を Phase 3a プロンプトに組み込みルール化
- [x] **2026-04-25 23:20 Phase 2 残骸クリーンアップ完了** — example BLs/STATUS.md (健康管理/麻布しき配下/バー5アローズ) 削除、test deliverable 削除、Cockpit task 88973dd5/717658ce/0535418e complete、test markdown table 削除。残存: ミニタキオン 4 BL のみ、index = projects:1 / bls:4 / deliverables:1
- [x] **2026-04-25 23:17 BL-TBD-002 Phase 2 完了マーク** — Cockpit task 88973dd5 で完了済の事実を yaml に反映 (state: completed)

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

- 設計書: `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- 当日作業フォルダ: `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/`
- 実装ディレクトリ (予定): `~/.agi-tools/mini-tachyon/`
- 親プロジェクト: [Tachyon Workspace](~/tachyon-workspace)
- Cockpit CLI: `/Users/rikutanaka/.agi-tools/data/cockpit/master/bin/cockpit`
- Tailscale ホスト: `rikus-mac-mini-3.tailad7d87.ts.net`
