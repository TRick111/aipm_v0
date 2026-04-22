# AI-Core（タスク管理用）

## 背景
- AIOS / AI Core を授業・伴走・導入支援の形で複数クライアントへ展開するための共通母艦プログラム
- 個別案件（Pon・UNISON・西村）から再利用可能な提供資産（教材・テンプレート・契約書・運用基盤）を一般化して保守する

## 目的
- AI活用支援で使う共通教材・テンプレート・運用基盤を一元管理する
- 提案、契約、導入、運用定着までを一貫して支えられる共通パッケージを維持する
- 個別案件は本ディレクトリを起点にクライアント向け最適化版を派生させる

## 成果物の所在
**このディレクトリはタスク管理専用。成果物の本体は以下を参照:**
- `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/`
  - `共通提供基盤/` … 現行運用中の共通教材・テンプレート・契約書
  - `次期戦略案/2026-04-04_商品設計プラン/` … 次期サービス設計案

## アクティブなプロジェクト

### 1. PL（Price List = 提供サービス選択ツール）
- 50事例 × 11カテゴリの提供メニューを Web 上でクライアントに選択・登録してもらう
- 起点: `~/Downloads/AI秘書事業_事例集_v1.html`（町田第一さん作成）
- DB: Notion（事例一覧 / クライアント依頼）
- デプロイ: Vercel（既存ダッシュボードと同 team / `restaurant-ai-lab`）
- **公開URL（UI プレビュー・2026-04-22 初回デプロイ）**: https://ai-core-pl.vercel.app/
- **リポジトリ**: https://github.com/RestaurantAILab/ai-core-pl
- **ローカル**: `~/RestaurantAILab/ai-core-pl/`
- 関連バックログ: BL-0061
- 計画: `Flow/202604/2026-04-22/AI-Core/implementation_plan.md` v2.1
- 実装ログ: `Flow/202604/2026-04-22/AI-Core/implementation_log.md`
- Phase 1 残タスク: Notion DB 2つ作成 + token 受領 → seed + Vercel env + 本番再デプロイ（INBOX Q-notion-db 回答待ち）

## 関係者

| 名前 | 所属・役職 | 役割 |
|---|---|---|
| 町田第一 | Restaurant AI Lab | AI-Core 提供資料作成（HTML 等） |
| 町田大地 | Restaurant AI Lab AI担当 | AI企画・提案・運用 |
| 田中利空 | Restaurant AI Lab 開発担当 | 開発・実装 |

## 現在の状況・ネクストアクション
- 2026-04-22 AM: PL 立ち上げ準備（HTML 受領 → 探索完了 → 実装計画 v2.0 → v2.1 Slack 削除）
- 2026-04-22 PM: Phase 1 完全完了 ✅
  - UI / API / Notion 接続 / 本番デプロイ / E2E 動作確認 すべて完了
  - 公開URL（クライアント共有可）: https://ai-core-pl.vercel.app/
  - 50 事例を Notion ServiceCases に seed 済、ClientRequests への送信が `Status=未対応` で確実に入ることを検証
- ネクストアクション: 関係者に URL 共有 → 実クライアント運用開始。Phase 2 候補（PDF出力・認証・集計・通知復活・HTML v2 差分）は別バックログ起票で対応。
