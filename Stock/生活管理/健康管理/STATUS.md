---
schema_version: 1
project: 健康管理
category: 生活管理
status: in_progress
owner_turn: user
updated_at: 2026-04-22T17:55:00+09:00
updated_by: master-agent
current_bl: BL-0028
next_action: "BL-0028 睡眠デバイスの最終決定 (Vivoactive 6 か Venu 4)"
blocker: null
related_bls: [BL-0028, BL-0030]
---

# 健康管理

## 🎯 次のアクション
BL-0028 睡眠デバイスの最終決定 (Vivoactive 6 か Venu 4)。AI 推奨は (a) Vivoactive 6 だが、田中さんは Venu 4 が欲しいと表明。一晩寝かせて判断中。

## 🚧 現在のブロッカー
なし

## 📋 概要

田中さんの睡眠の質、運動量、心拍など健康指標を継続トラッキングする基盤を整える。
GarminスマートウォッチをiPhone Health経由でAIOSに連携、Webhook で Vercel に飛ばし、Apple Health のデータを活用する。

## 🔄 進行中
- [ ] BL-0028 睡眠デバイス比較 (回答待ち)
- [ ] BL-0030 Health Auto Export 連携準備 (AI 作業中)

## ✅ 完了済
- [x] 2026-04-15 健康管理プロジェクト立ち上げ
- [x] 2026-04-20 候補機種3社調査 (Garmin/Apple/Oura)

## 🧠 決定事項
- 2026-04-20: Apple Watch ではなく Garmin を選定 (バッテリー24h装着の優先)
- 2026-04-22: Oura Ring はサブスク制で却下
- 2026-04-22: Webhook 先は Vercel、DB 候補は GitHub commit (TODO)

## 📜 履歴
- 2026-04-22 17:55 BL-0028 ブロッカー解消 (体温データは AIOS に流れないことが判明)、Vivoactive 6 推奨に確定
- 2026-04-20 BL-0028 候補2機種に絞り込み

## 🔗 関連リンク
- AIOS パイプライン設計: `Flow/202604/2026-04-22/健康管理/bl0030_integration_prep.md`
