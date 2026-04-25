---
schema_version: 1
project: AI-Core_飯武さん導入
category: RestaurantAILab
status: in_progress
owner_turn: ai
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0066
next_action: "2026-04-29 までに第1回 (4/30) 提供資料を作成。中間マイルストーン: 2026-04-24 議事録を飯武さんに渡す"
blocker: null
related_bls: [BL-0066]
---

# AI-Core_飯武さん導入

## 🎯 次のアクション
BL-0066: 第1回 (2026-04-30) セッションの提供内容と資料を 2026-04-29 までに作成する。中間マイルストーン: 2026-04-24 議事録を飯武さんに渡す。前提タスクとして BL-0053 (AIOS+G-Brain 統合) と BL-0054 (共用リポ設計) の進捗を取り込む。

## 🚧 現在のブロッカー
議事録未到着 (READMEより、提供内容詳細抽出には議事録が必要)。前提タスク BL-0053 / BL-0054 の決定事項を取り込む必要あり。

## 📋 概要
「AIコア」を Restaurant AI Lab として複数クライアントに導入支援する取り組みの一環で、飯武さん (クライアント) に対し AI コアの構築・導入・運用定着までを伴走支援するプロジェクト。第1回導入支援セッションを 2026-04-30 に実施予定。後続クライアント (PONさん向け、UNISON 向け等) にも展開可能なテンプレートを整備する。

関係者: 飯武さん (クライアント) / 田中利空 (導入支援) / 町田大地 (G-Brain 担当)。

## 🔄 進行中
- [ ] BL-0066 飯武さんAIコア導入支援 第1回 (4/30) 提供内容・資料準備 (doing / P1, due 2026-04-29)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-22 プロジェクト初期化 (README / log / ProjectIndex 作成)
- [x] 2026-04-22 BL-0061 AIコア PL 作成 Phase 1 完了 (営業フロント https://ai-core-pl.vercel.app/ )

## 🧠 決定事項 (Why ログ)
- AIコア共通基盤 (`AI-Core/`) と顧客別導入支援 (`AI-Core_<顧客>/`) を **兄弟 Project** に分離: 共通教材と顧客カスタマイズを物理分離して再利用性を確保
- 第1回スコープ: AIOS の何をどこまで提供するかは BL-0053 / BL-0054 の決定待ち。先行で議事録読み込みと枠組設計を進める

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/RestaurantAILab/AI-Core_飯武さん導入/README.md`
- log: `Stock/RestaurantAILab/AI-Core_飯武さん導入/log.md`
- ProjectIndex: `Stock/RestaurantAILab/AI-Core_飯武さん導入/ProjectIndex.yaml`
- 兄弟プロジェクト: `Stock/RestaurantAILab/AI-Core/`
- 共通教材本体: `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/共通提供基盤/`
- AIコア PL (営業フロント): https://ai-core-pl.vercel.app/
