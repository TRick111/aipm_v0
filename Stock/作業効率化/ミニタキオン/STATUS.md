---
project: ミニタキオン
category: 作業効率化
status: in_progress
owner_turn: user
updated_at: 2026-04-25T18:45:00+09:00
updated_by: master-agent
current_bl: BL-TBD-001
status: in_progress
owner_turn: ai
next_action: "Cockpit task 7d51e727 で Phase 1 実装中。エージェントの進捗を監視、質問が来たら応答"
blocker: "iPhoneがTailscale (rikus-mac-mini-3.tailad7d87.ts.net) にログインしているか未確認 — Phase 1 動作確認時に必要"
related_bls: [BL-TBD-001]
active_cockpit_tasks:
  - id: 7d51e727
    bl_id: BL-TBD-001
    started_at: 2026-04-25T18:44:27+09:00
tech_stack:
  framework: "Next.js 15+ (App Router)"
  runtime: "Bun"
  ui: "Tailwind CSS + shadcn/ui"
  port: 3000
---

# ミニタキオン

## 🎯 次のアクション
Phase 1 着手: Bun + Hono webapp スケルトン + `/today` 画面 (Stock STATUS.md スキャン → ホーム表示)

## 🚧 現在のブロッカー
iPhoneがTailscale (`rikus-mac-mini-3.tailad7d87.ts.net`) にログインしているか未確認 — Phase 1 動作確認時に必要

## 📋 概要

AIPMの成果物レビュー＋次指示をスマホ一画面で完結させるツール。
[Tachyon Workspace](~/tachyon-workspace) のミニ版。**作業効率化プログラム**所属。

スコープ拡張済 (2026-04-25): INBOX.md / daily_tasks.md を廃止し、その責務を全てミニタキオンが引き受ける構成。AIPM の散文ベース 3ファイル同期を、構造化データ (YAML) + UI ベースのインタラクションに置き換える。

## 🔄 進行中

- [ ] **BL-TBD-001 Phase 1: View-only MVP** — Cockpit task 7d51e727 で実装中 (担当: claude エージェント, 開始: 18:44)
  - Next.js (App Router) スケルトン → 4画面 view-only → launchd 登録 → iPhone 動作確認

## ✅ 完了済
- [x] 2026-04-25 設計確定 (Approach A 採用、INBOX 廃止スコープで改訂)
- [x] 2026-04-25 設計書作成: `Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- [x] 2026-04-25 Stock/作業効率化/ミニタキオン/ 初期化
- [x] 2026-04-25 技術スタック確定: Next.js 15+ (App Router) + Bun + Tailwind + shadcn/ui

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
