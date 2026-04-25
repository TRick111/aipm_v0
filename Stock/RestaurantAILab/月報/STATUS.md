---
schema_version: 1
project: 月報
category: RestaurantAILab
status: blocked
owner_turn: ai
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0010
next_action: "ダッシュボード改の PL 機能 (BL-0004〜BL-0006) は 2026-04-12 完了済。データの安定運用を確認次第 BL-0010 月報作成を BFA・別天地から再開"
blocker: "ダッシュボード改 PL 機能のデータ安定運用待ち (BFA/別天地への月報フィード前提)"
related_bls: [BL-0010]
---

# 月報

## 🎯 次のアクション
BL-0010 ダッシュボード改の PL 機能完了後 (2026-04-12 ✅) のデータ安定運用を確認したら、BFA・別天地から月報作成を再開する。月報パイプライン (プロンプト6本 + スクリプト2本) は完成済。

## 🚧 現在のブロッカー
ダッシュボード改の PL 機能データの安定運用待ち。2026年2月に BFA・別天地に月報を1回出した後停止中。BL-0004〜BL-0006 (PL 関連) は 2026-04-12 完了済のため、運用ステーブル化次第ブロッカー解除。

## 📋 概要
クライアント飲食店に対して月次の売上・運営レポートを提供する仕組み。週報のデータを月単位で再集計し、トレンド分析・前年比較・週別深掘りを行う。月報作成パイプラインは完成 (フェーズ1: 基礎資料 → フェーズ5: HTML スライド + D3.js + PDF 改ページ)。

関係者: 竹矢 (Chef's Room 社長) / 吉田 (代表) / 町田大地 (AI 企画) / 田中利空 (開発)。

## 🔄 進行中
- [ ] BL-0010 月報: ダッシュボード改 PL 対応後に月報作成再開 (todo / P2, due 2026-04-15)

## ✅ 完了済 (ハイライト)
- [x] 月報パイプライン完成 (プロンプト6本 + スクリプト2本: monthly_analysis_script.py / deep_dive_weekly_analysis.py)
- [x] BFA 2026年1月分のアウトプット例完了
- [x] フェーズ1〜5 (基礎資料 → 週別深掘り → スライド構成 → 日報スライド → HTML スライド) 全部実装済

## 🧠 決定事項 (Why ログ)
- ダッシュボード改 PL 完了待ち戦略: PL データが月報の中核入力。先に出すと再生成コストが嵩む
- 再開順序は BFA → 別天地 → 麻布しき・キーポイント: 既に月報を1回出した実績がある店舗を優先

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/RestaurantAILab/月報/README.md`
- log: `Stock/RestaurantAILab/月報/log.md`
- ProjectIndex: `Stock/RestaurantAILab/月報/ProjectIndex.yaml`
- 統合プロンプト入口: `Stock/RestaurantAILab/月報/00_月報作成_統合プロンプト.md`
