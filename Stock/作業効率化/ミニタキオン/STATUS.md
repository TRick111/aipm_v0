---
schema_version: 1
project: ミニタキオン
category: 作業効率化
status: in_progress
owner_turn: ai
updated_at: 2026-04-25T20:25:00+09:00
updated_by: master-agent
current_bl: BL-TBD-003
next_action: "iPhone Safari で http://rikus-mac-mini-3.tailad7d87.ts.net:3000/ を開いて Phase 1 view-only MVP の動作確認 + Phase 2 着手判断"
blocker: null
related_bls: [BL-TBD-001]
active_cockpit_tasks:
  - id: 7d51e727
    bl_id: BL-TBD-001
    started_at: 2026-04-25T18:44:27+09:00
    completed_at: 2026-04-25T19:57:00+09:00
    status: phase1_complete_awaiting_user_verification
tech_stack:
  framework: "Next.js 15+ (App Router)"
  runtime: "Bun"
  ui: "Tailwind CSS + shadcn/ui"
  port: 3000
---

# ミニタキオン

## 🎯 次のアクション
BL-TBD-003 進行中: ウェブデザイナーエージェントが UI 全面リデザイン中 (Cockpit task 7d51e727 に follow-up 送信済)。完了通知を待つ。

## 🚧 現在のブロッカー
なし (Phase 1 prod build + curl 動作確認済、prod サーバ稼働中)

## 📋 概要

AIPMの成果物レビュー＋次指示をスマホ一画面で完結させるツール。
[Tachyon Workspace](~/tachyon-workspace) のミニ版。**作業効率化プログラム**所属。

スコープ拡張済 (2026-04-25): INBOX.md / daily_tasks.md を廃止し、その責務を全てミニタキオンが引き受ける構成。AIPM の散文ベース 3ファイル同期を、構造化データ (YAML) + UI ベースのインタラクションに置き換える。

## 🔄 進行中

- [ ] **BL-TBD-002 Phase 2: 書き込み機能** — 未着手 (Phase 1 確認後)
- [ ] iPhone Safari からの実機動作確認 — ユーザー対応

## ⏸ ユーザー判断待ち

エージェントから3件の確認事項 (Phase 1 完了報告内):
1. ~~STATUS.md frontmatter の重複キー~~ → ✅ master 修正済 (2026-04-25 20:05)
2. ~~既存 YAML に schema_version: 1 が無い~~ → ✅ master 修正済 (STATUS.md 2026-04-25 20:05、BL-TBD-001.yaml 同時)
3. 「私の番」グルーピングの実データ動作確認 → Phase 2 で実 mutation が走り始めてからでOK

## ✅ 完了済
- [x] 2026-04-25 設計確定 (Approach A 採用、INBOX 廃止スコープで改訂)
- [x] 2026-04-25 設計書作成: `Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- [x] 2026-04-25 Stock/作業効率化/ミニタキオン/ 初期化
- [x] 2026-04-25 技術スタック確定: Next.js 15+ (App Router) + Bun + Tailwind + shadcn/ui
- [x] 2026-04-25 /plan-eng-review 完了、設計書に Eng Review Decisions セクション追加 (5 issues 解決 + 1 critical gap mitigated、Lake Score 5/5)
- [x] **2026-04-25 19:57 BL-TBD-001 Phase 1 (View-only MVP) 実装完了** — 4画面 + lib/watcher (chokidar+5min fallback) + lib/index-store (BL駆動 load + singleton) + instrumentation hook + launchd plist + install.sh、prod build OK、Tailscale curl 200 OK

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

## 🧪 テーブル表示テスト (一時)

| ファイル | 役割 | 行数目安 |
|---|---|---:|
| `app/page.tsx` | ホーム | ~100 |
| `app/projects/[slug]/page.tsx` | プロジェクト詳細 | ~150 |
| `app/bl/[id]/page.tsx` | BL 詳細 | ~250 |
| `lib/index-store.ts` | in-memory index | ~80 |
| `lib/watcher.ts` | chokidar | ~70 |

> 上記テーブルはマークダウンレンダリング検証用。Phase 2 に入る前に削除します。

## 🔗 関連リンク

- 設計書: `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- 当日作業フォルダ: `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/`
- 実装ディレクトリ (予定): `~/.agi-tools/mini-tachyon/`
- 親プロジェクト: [Tachyon Workspace](~/tachyon-workspace)
- Cockpit CLI: `/Users/rikutanaka/.agi-tools/data/cockpit/master/bin/cockpit`
- Tailscale ホスト: `rikus-mac-mini-3.tailad7d87.ts.net`
