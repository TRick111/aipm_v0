---
schema_version: 1
project: AI-Core
category: RestaurantAILab
status: in_progress
owner_turn: user
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0054
next_action: "BL-0054 共用リポジトリ構成・アクセス権・運用ルールを設計確定し、兄弟プロジェクト AI-Core_共用リポジトリ として独立させる。BL-0066 (飯武さん導入) の前提整備"
blocker: null
related_bls: [BL-0054]
---

# AI-Core

## 🎯 次のアクション
BL-0054 RestaurantAILab 共用リポジトリの構成・アクセス権・運用ルールを設計確定する。本タスクは BL-0066 (飯武さん AI コア導入支援) と BL-0053 (AIOS+G-Brain 統合) の前提整備。完了後、兄弟 Project `AI-Core_共用リポジトリ` として独立予定。

## 🚧 現在のブロッカー
なし (BL-0053 の G-Brain 整理は田中さん側ボトルネックだが、BL-0054 は単独着手可能)

## 📋 概要
AIOS / AI Core を授業・伴走・導入支援の形で複数クライアントへ展開するための共通母艦プログラム。個別案件 (Pon・UNISON・西村・飯武) から再利用可能な提供資産 (教材・テンプレート・契約書・運用基盤) を一般化して保守する。顧客別の導入支援は **兄弟 Project** (`AI-Core_<顧客名>`) として独立、本プロジェクトは共通基盤＋PL を担う。成果物本体は `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/` 配下。

関係者: 町田第一 (AI-Core 提供資料作成・HTML 等) / 町田大地 (AI 担当) / 田中利空 (開発担当)。

## 🔄 進行中
- [ ] BL-0054 RestaurantAILab 共用リポジトリ・ファイル共有設計 (doing / P1, due 2026-04-21)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-22 BL-0061 AIコア PL 作成 Phase 1 完了 (公開URL: https://ai-core-pl.vercel.app/, GitHub: RestaurantAILab/ai-core-pl, Notion ServiceCases 50件 seed + ClientRequests, E2E 動作確認済)
- [x] 2026-04-22 PL 立ち上げ準備: HTML 受領 → 探索完了 → 実装計画 v2.0 → v2.1 (Slack 削除)
- [x] 2026-04-21 BL-0054 共用リポジトリ設計に着手

## 🧠 決定事項 (Why ログ)
- 顧客別導入支援は **兄弟 Project** として独立: 共通基盤 (本プロジェクト) と顧客カスタマイズを切り分け、教材・テンプレートの再利用性を高める
- 本ディレクトリはタスク管理専用、成果物本体は `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/` に集約: AIPM Stock とコンテンツ Stock を物理分離
- Phase 2 候補 (PDF 出力 / 認証 / 集計 / 通知復活 / HTML v2) は別 BL 起票で対応: スコープ管理を BL 単位に絞る

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/RestaurantAILab/AI-Core/README.md`
- log: `Stock/RestaurantAILab/AI-Core/log.md`
- ProjectIndex: `Stock/RestaurantAILab/AI-Core/ProjectIndex.yaml`
- 実装ログ (Phase 1): `Stock/RestaurantAILab/AI-Core/implementation_log_2026-04-22.md`
- PL 公開URL: https://ai-core-pl.vercel.app/
- GitHub: https://github.com/RestaurantAILab/ai-core-pl
- 成果物本体: `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/`
