---
schema_version: 1
project: 週報
category: RestaurantAILab
status: in_progress
owner_turn: ai
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0038
next_action: "口コミデータの取得基盤を構築。BL-0038 (食べログ) と BL-0039 (Google Places API) を並行で実装し、完了後 BL-0040 で週報の手法に組み込む"
blocker: null
related_bls: [BL-0038, BL-0039, BL-0040]
---

# 週報

## 🎯 次のアクション
口コミ取得基盤の構築。BL-0038 (食べログから口コミ取得) と BL-0039 (Google Places API から口コミ取得) を並行で実装し、完了後 BL-0040 で取得した口コミを週報の手法分析に組み込む。

## 🚧 現在のブロッカー
なし

## 📋 概要
飲食店 (BFA / BBC 別天地 銀座 / 麻布しき 旗の台店 / キーポイント かめや駅前店) の週次データから週報を自動生成するシステム。Python (pandas / matplotlib / seaborn) + Claude (LLM) の2層構成で、JSON/CSV/PNG → Markdown → Word (.docx) 出力。前週比 / 前月比 / 前年比の比較とカテゴリ・商品レベルの構成比推移分析を含む。

2025-12-28 作成、2026-02-16 最終更新。BL-0008 (店員日報データの自動連携) は 2026-04-12 完了済。

関係者: Restaurant AI Lab 開発・AI チーム。

## 🔄 進行中
- [ ] BL-0038 食べログから口コミを取得できるようにする (todo / P2)
- [ ] BL-0039 Google API から口コミを取得できるようにする (todo / P2)
- [ ] BL-0040 口コミの内容を週報の手法に含める (todo / P2, BL-0038 / BL-0039 完了後)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-12 BL-0008 店員日報データの自動連携実装
- [x] 週報自動生成システム稼働 (BFA / BBC / 麻布しき / キーポイント 4店舗対応)
- [x] 構成比時系列データ (category_composition_trend.csv / product_composition_trend.csv) 出力対応
- [x] 曜日深堀分析の README 別出し (`README_曜日深堀分析.md`)

## 🧠 決定事項 (Why ログ)
- 2層構造採用 (Python 分析 + AI 自然言語分析): 数値処理は Python に任せ、AI はインサイト抽出と推奨アクション策定に集中
- 出力形式は Google Docs 互換の Word (.docx): クライアントが直接編集できるようにする
- 口コミ取得は食べログと Google を並行で取りに行く: 単一ソース依存を避けカバレッジを高める

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/RestaurantAILab/週報/README.md`
- 曜日深堀分析: `Stock/RestaurantAILab/週報/README_曜日深堀分析.md`
- log: `Stock/RestaurantAILab/週報/log.md`
- ProjectIndex: `Stock/RestaurantAILab/週報/ProjectIndex.yaml`
