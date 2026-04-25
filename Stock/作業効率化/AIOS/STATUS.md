---
schema_version: 1
project: AIOS
category: 作業効率化
status: awaiting_user
owner_turn: user
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0053
next_action: "BL-0053 G-Brain の内容を田中さん自身が読んで理解する (本人がボトルネック)。理解完了後に Q1-Q5 への回答が可能になり AIOS+G-Brain 統合方針が決定できる。BL-0066 (飯武さん導入) の前提整備"
blocker: "BL-0053 G-Brain 構想の理解が田中さん側で進行中。本人がボトルネック (READMEより)"
related_bls: [BL-0053, BL-0067]
---

# AIOS

## 🎯 次のアクション
BL-0053 田中さん自身が G-Brain (大地さん共有ライブラリ) の内容を読んで理解する。本人がボトルネック。理解完了後、Q1-Q5 への回答 → AIOS+G-Brain 統合方針が決定できる。本タスクは BL-0066 (飯武さん AI コア導入支援) の前提整備でもある。並行して BL-0067 INBOX 設計の再検討 (Cockpit 統合 + 対応優先度の可視化) を検討。

## 🚧 現在のブロッカー
BL-0053 G-Brain の責務と AIOS の責務の切り分けが田中さん側で整理中。「本人がボトルネック」と README に明記。

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

## 🧠 決定事項 (Why ログ)
- 旧 BL-0053 を AIOS アップデート全体に置き換え: G-Brain 統合と AIOS ルール見直しは不可分のためまとめて1 BL に集約
- BL-0066 (飯武さん) の前提整備として位置付け: 飯武さんに提供するルールベースをここで確定する必要がある
- BL-0067 INBOX 起票背景 (2026-04-22): エージェントが自分の回答待ちで止まっているのに意識から外れて進まないケースが発生 (プロジェクト跨ぎの切替コストが要因)

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/作業効率化/AIOS/README.md`
- log: `Stock/作業効率化/AIOS/log.md`
- ProjectIndex: `Stock/作業効率化/AIOS/ProjectIndex.yaml`
- 調査ノート: `Stock/作業効率化/AIOS/discovery_notes.md`
- スコープ提案: `Stock/作業効率化/AIOS/scope_proposal.md`
- AIOS ルール本体: `.cursor/rules/aios/`
