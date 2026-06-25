---
schema_version: 1
project: マーケダッシュボード
category: RestaurantAILab
status: in_progress
owner_turn: user
updated_at: 2026-06-25T21:30:00+09:00
updated_by: master-agent
current_bl: BL-0098
schedule: "B案（段階リリース）採用 2026-06-25"
next_action: "BL-0098（Prismaスキーマ+seed）着手。Featureブランチ feature/marke-dash-BL-0098-prisma-schema で開発。並行でPO判断項目（Retty/ぐるなびサンプル、食べログ050契約、HPマンスリー受領体制、規約レビュー担当）を竹矢さんに確認"
blocker: "BL-0100/0105 は依然PO判断待ち（サンプル提供と規約レビュー担当）。BL-0098〜0099/0102/0103/0104 は着手可"
related_bls: [BL-0098, BL-0099, BL-0100, BL-0101, BL-0102, BL-0103, BL-0104, BL-0105, BL-0106]
---

# マーケダッシュボード

## 🎯 次のアクション

**スケジュール B 案（段階リリース）採用済**（2026-06-25 開発側判断）。BL-0098 から実装着手する。

1. **BL-0098 着手**: Prisma スキーマ追加 + マイグレーション + 媒体マスタ seed
   - ブランチ: `feature/marke-dash-BL-0098-prisma-schema`
2. **PO 判断項目を並行で確認**（竹矢さん）:
   - Retty／ぐるなびのサンプル CSV／管理画面スクショ提供（6/25 期限）→ BL-0100 解除条件
   - 食べログ 050 番号 + PR／集客サービス契約の状況確認 → 食べログ KPI 取得可否確定
   - ホットペッパーのマンスリークライアントレポート受領体制
   - 媒体規約レビュー（M-14d）の実施担当確定 → BL-0105 解除条件
   - 媒体ログイン情報の管理ルール（S-03）受入可否

## 🚧 現在のブロッカー

- **BL-0100**（Retty／ぐるなびパーサ）: サンプル提供待ち
- **BL-0105**（Playwright 自動取得）: 規約レビュー担当の確定待ち
- 上記以外（BL-0098／0099／0102／0103／0104）は着手可能

## 📋 概要

外注コンサル（CMO／CFOプラン）運用を可能にするため、既存ダッシュボードに **7 媒体（食べログ／食べログノート／ホットペッパー／一休／オズモール／Retty／ぐるなび）の月次マーケKPIを集約するビュー** と **外注コンサル向けロール** を追加するプロジェクト。

竹矢さん（PO・Chef's Room 社長）からの追加要望:
- Retty／ぐるなび等の媒体追加が必須
- 食べログ「月間ページレポート／来店指標」、食べログノート「席稼働数／項目別」、ホットペッパー「レストランボード集計分析」も対象に
- CSV ダウンロード自動化（Playwright）を Phase 1 に含める

→ 当初の 6/24 完了→7月初旬リリースから、**B 案（段階リリース）** で 7月初旬に Phase 1.0、7月下旬以降に Phase 1.1（自動取得）を段階追加する提案。

関係者: 竹矢（PO） / 吉田（代表） / 町田（AI） / 田中（開発）。

## 🔄 進行中（Phase 1 バックログ）

- [ ] BL-0098 Prisma スキーマ追加 + マイグレーション + 媒体マスタ seed (todo / P1)
- [ ] BL-0099 既定 5 媒体のCSVパーサ実装 (todo / P1)
- [ ] BL-0100 Retty／ぐるなびサンプル確認 + パーサ実装 (blocked / P1)
- [ ] BL-0101 媒体別アップロード画面 + 横断KPIビュー + 媒体別タブ (todo / P1)
- [ ] BL-0102 外注コンサル権限（S-01/S-02）+ 媒体ログイン情報集中管理（S-03）(todo / P1)
- [ ] BL-0103 店舗別契約媒体フィーチャーフラグ + 運用フロー定義書 (todo / P1)
- [ ] BL-0104 スライド出力（O-01）(todo / P1)
- [ ] BL-0105 CSV 自動取得（M-14, Playwright, 段階導入）(todo / P2)
- [ ] BL-0106 Phase 1 受入検証 + リリース (todo / P1)

## ✅ 完了済 (ハイライト)

- [x] 2026-06-12 v3 要件一覧確定（媒体×KPI マトリックス、Web リサーチで裏取り）
- [x] 2026-06-15 Phase 1 スコープ承認資料（HTML）作成、Google Drive アップロード、GitHub Pages 公開
- [x] 2026-06-19 要件定義書 v1 確定（竹矢さんフィードバック反映）

## 🧠 決定事項 (Why ログ)

- **媒体マスタを拡張可能設計に**: Retty／ぐるなび追加に加え、将来 Yahoo!ロコ等の追加も視野。M-13 で管理者UIから媒体追加可能に
- **CSV自動取得を Phase 1 に繰上**: 当初 Phase 2 想定だったが、PO 要望で繰上。ただし全媒体一斉ではなく **媒体ごとに段階導入** する前提（B 案）
- **コンサル用ロールは StoreGroup を拡張**: 新規 `consultant` ロール独立は避け、既存 StoreGroup に `groupType` フィールドを追加して対応（実装コスト最小化）
- **媒体ログイン情報は社内集中管理**: コンサル UI には一切表示しない（S-03、暗号化テーブル + 1Password）

## 📜 履歴

- 2026-06-25 master が Stock に確定反映（README/ProjectIndex/STATUS/log + docs + backlog BL-0098〜BL-0106）

## 🔗 関連リンク

- README: `Stock/RestaurantAILab/マーケダッシュボード/README.md`
- 要件定義書: `Stock/RestaurantAILab/マーケダッシュボード/docs/要件定義書_v1.md`
- Phase 1 承認資料 (GitHub Pages): https://trick111.github.io/phase1-scope-review/
- 実装方針メモ (Dashboard リポジトリ): `RestaurantAILab/Dashboard/docs/03_dev-notes/0519_マーケダッシュボード実装方針.md`
