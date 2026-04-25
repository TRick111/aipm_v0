---
schema_version: 1
project: 健康管理
category: ゴール管理
status: awaiting_user
owner_turn: user
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0028
next_action: "BL-0028 睡眠計測デバイス (Oura Ring 4 / Garmin Vivoactive 6 / Garmin Venu 4) の最終決定を田中さん側で実施。決定後 BL-0029 (記録運用開始) と BL-0030 (AIOS 自動連携構築) を 2026-04-30 までに着手"
blocker: "BL-0028 デバイス選定の最終判断待ち (Backlog 内『Oura Ring 4 確定』と daily_tasks の『Vivoactive 6 推奨・Venu 4 検討』が未整合)"
related_bls: [BL-0028, BL-0029, BL-0030]
---

# 健康管理

## 🎯 次のアクション
BL-0028 睡眠計測デバイスの最終決定を田中さん側で実施 (2026-04-23 以降の判断待ち)。Oura Ring 4 / Garmin Vivoactive 6 / Garmin Venu 4 の3案で比較レポートあり。デバイス確定後、BL-0029 (睡眠の質の記録運用開始) と BL-0030 (AIOS 自動連携構築) を 2026-04-30 までに着手。

## 🚧 現在のブロッカー
BL-0028 デバイス選定の最終判断待ち。Backlog 内の「Oura Ring 4 確定」と daily_tasks 内の「Vivoactive 6 推奨・Venu 4 検討」が未整合のため、田中さんによる確定判断が必要。

## 📋 概要
体重・体脂肪率を健康的な水準に戻し、運動・食事・睡眠を継続的に管理するためのプロジェクト。日次で体重・運動・食事メモを記録し、デバイス導入後は睡眠スコア / 睡眠時間 / 深い睡眠の割合を自動計測する構成。2026-04 末を目標に、デバイスから AIOS へ睡眠データが自動連携される状態を作る。

ベースライン (2026-03-22): 体重 68.7kg / 体脂肪率 15.9% / 目標体脂肪率 14% (BL-0027 ✅完了)。

## 🔄 進行中
- [ ] BL-0028 睡眠計測デバイスの購入 (Oura Ring / Garmin 等) (doing / P1, due 2026-03-29 — 期限超過、田中さん最終判断待ち)
- [ ] BL-0029 睡眠の質の記録運用を開始 (todo / P1, due 2026-04-30, BL-0028 完了後)
- [ ] BL-0030 睡眠データの AIOS 自動連携の構築 (todo / P1, due 2026-04-30, BL-0028 完了後)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-05 BL-0027 健康管理: 目標値の設定 (体脂肪率 14%、ベースライン 15.9%)
- [x] 2026-03-22 BL-0012 ベースライン計測と記録開始 (体重 68.7kg / 体脂肪率 15.9%)

## 🧠 決定事項 (Why ログ)
- 2026-04-22 デバイス候補は Oura Ring 4 / Garmin Vivoactive 6 / Garmin Venu 4 の3択。比較レポート: `sleep_device_final_comparison_2026-04-22.md`
- AIOS 自動連携の準備ドキュメント: `bl0030_integration_prep_2026-04-22.md` 作成済
- 2026-04-22 「結論を一晩寝かせて 2026-04-23 以降に決定」: 即断による後悔回避のため
- Phase 1 (〜3月末) ベースライン計測 + デバイス購入 → Phase 2 (4月) 記録開始 + 自動連携 → Phase 3 (5月〜) データ統合活用

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/ゴール管理/健康管理/README.md`
- log: `Stock/ゴール管理/健康管理/log.md`
- ProjectIndex: `Stock/ゴール管理/健康管理/ProjectIndex.yaml`
- デバイス比較: `Stock/ゴール管理/健康管理/sleep_device_final_comparison_2026-04-22.md`
- AIOS 連携準備: `Stock/ゴール管理/健康管理/bl0030_integration_prep_2026-04-22.md`
- 詳細手順: `Flow/202604/2026-04-22/健康管理/sleep_device_comparison.md`
