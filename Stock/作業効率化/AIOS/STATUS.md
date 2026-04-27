---
schema_version: 1
project: AIOS
category: 作業効率化
status: awaiting_user
owner_turn: user
updated_at: 2026-04-27T10:10:00+09:00
updated_by: bl-0053-spawn-20260427
current_bl: BL-0053
next_action: "BL-0053 田中さんが INBOX の Q1（G-Brain = `garrytan/gbrain` で合っているか）に回答。確定後 Q2（統合案 (E) ハイブリッド採用）/ Q3（4/30 飯武さん第 1 回は AIOS のみで OK か）を確定 → Phase 1（軽い案 C 部分、半日）即着手可。成果物: `Flow/202604/2026-04-27/作業効率化/AIOS/g_brain_investigation_v1.md` + `g_brain_aios_integration_options_v1.md`"
blocker: "BL-0053 田中さん→大地さんの 1 行確認（gbrain = garrytan/gbrain か）。確定すれば Phase 1 着手可。Phase 2/3 は 5 月以降"
related_bls: [BL-0053, BL-0066, BL-0067]
---

# AIOS

## 🎯 次のアクション
BL-0053 田中さんが INBOX (`Flow/202604/2026-04-27/_orchestration/INBOX.md`) の **BL-0053 セクション Q1〜Q3** に回答する。Q1 = G-Brain は `garrytan/gbrain` で合っているか（1 行確認） / Q2 = 統合方針 案 (E) ハイブリッドで進めるか / Q3 = 飯武さん 4/30 第 1 回は AIOS のみで OK か。回答後、Phase 1（軽い案 C 部分: RESOLVER.md / Compiled Truth + Timeline / MECE README、半日）に即着手可能。並行して BL-0067 INBOX 設計の再検討 (Cockpit 統合 + 対応優先度の可視化) を検討。

## 🚧 現在のブロッカー
BL-0053 田中さん→大地さんの 1 行確認待ち（"gbrain って `github.com/garrytan/gbrain` のこと？"）。確定すれば 4/30 飯武さん第 1 回までに Phase 1 を完了できる。

## 📋 概要
AIOS (AI Operating System) は AIPM を起点とした業務運用ルールおよびエージェント挙動を規定するルール群。現在 `.cursor/rules/` 配下に複数ファイルが散在し、追加のたびに整合性を取る手間が発生。田中さんが構想中の G-Brain (個人の知識・意思決定を蓄積する中核レイヤー) との統合を見据え、AIOS ルール全体の棚卸しと再設計が必要。BL-0066 (飯武さん AI コア導入支援、2026-04-30) の前提整備としても位置付け。

関係者: 田中利空 (オーナー / G-Brain 構想立案) / 町田大地 (G-Brain 提供元)。

## 🔄 進行中
- [ ] BL-0053 AIOS アップデート (G-Brain 統合 + ルール全体の見直し) (todo / P1, 田中さん本人ボトルネック)
- [ ] BL-0067 INBOX 設計の再検討 (Cockpit 統合 + 対応優先度の可視化) (todo / P2, 2026-04-22 振り返りで起票)

## ✅ 完了済 (ハイライト)
- [x] 調査ノート `discovery_notes.md` 作成
- [x] スコープ提案 `scope_proposal.md` 作成
- [x] 旧 BL-0053 (AI コア共有ライブラリ統合) を AIOS アップデート全体に置き換え
- [x] 2026-04-26 G-Brain Phase 0 仮説整理ドラフト (`Flow/.../2026-04-26/AIOS/g_brain_research.md`、大地さん私的リポ前提で探索 → 未発見)
- [x] **2026-04-27 G-Brain 目的調査 v1 + AIOS 統合案 v1 作成**: G-Brain = `garrytan/gbrain` (OSS / MIT / 11.5k★ / Garry Tan 作 / 2026-04-05 公開) で確定濃厚。AIOS との設計思想が近接（markdown-first / MECE / resolver / two-layer pages）。統合案 5 つを比較し推奨は **(E) ハイブリッド** (MCP 並走 + 思想取り込み)

## 🧠 決定事項 (Why ログ)
- 旧 BL-0053 を AIOS アップデート全体に置き換え: G-Brain 統合と AIOS ルール見直しは不可分のためまとめて1 BL に集約
- BL-0066 (飯武さん) の前提整備として位置付け: 飯武さんに提供するルールベースをここで確定する必要がある
- BL-0067 INBOX 起票背景 (2026-04-22): エージェントが自分の回答待ちで止まっているのに意識から外れて進まないケースが発生 (プロジェクト跨ぎの切替コストが要因)
- **2026-04-27 G-Brain の正体推定変更**: 4/26 までは「大地さん本人作の私的リポ」前提だったが、田中さん新前提（GitHub にある / 長期記憶）+ 再探索で **公開 OSS `garrytan/gbrain` でほぼ確定**。AIPM ローカル / RestaurantAILab org に無かったのは公開 OSS だから（採用を勧めているのが大地さん）
- **2026-04-27 統合方針として案 (E) ハイブリッド推奨**: 案 (A) 全乗り換えは 4/30 飯武さん導入に間に合わない / 単独の (B)(C)(D) は片手落ち / **(E) は段階導入で AIOS 既存資産を保護しつつ gbrain の検索 / enrichment / MCP の力を取り込める**

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)
- 2026-04-26 G-Brain Phase 0 仮説整理ドラフト作成 (Backlog Notes / 4/22 discovery を統合、リポ未特定で停止)
- **2026-04-27 G-Brain 目的調査 v1 + AIOS 統合案 v1 作成、INBOX に Q1〜Q3 起票 (田中さん回答待ち)**

## 🔗 関連リンク
- README: `Stock/作業効率化/AIOS/README.md`
- log: `Stock/作業効率化/AIOS/log.md`
- ProjectIndex: `Stock/作業効率化/AIOS/ProjectIndex.yaml`
- 調査ノート: `Stock/作業効率化/AIOS/discovery_notes.md`
- スコープ提案: `Stock/作業効率化/AIOS/scope_proposal.md`
- AIOS ルール本体: `.cursor/rules/aios/`
- **2026-04-27 G-Brain 目的調査 v1**: `Flow/202604/2026-04-27/作業効率化/AIOS/g_brain_investigation_v1.md`
- **2026-04-27 AIOS×G-Brain 統合案 v1**: `Flow/202604/2026-04-27/作業効率化/AIOS/g_brain_aios_integration_options_v1.md`
- 4/26 G-Brain Phase 0 ドラフト: `Flow/202604/2026-04-26/AIOS/g_brain_research.md`
- 外部 (OSS): https://github.com/garrytan/gbrain
