---
schema_version: 1
project: ワールドネイバーズ_カフェポイントシェア
category: 0.Other
status: paused
owner_turn: user
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0075
next_action: "PoC 第1ステップ: 自分の決済を自分の PC 上で行い、携帯端末からトリガーする最小構成を試作。決済 Web アプリの画面遷移・認証方式の調査から着手"
blocker: null
related_bls: [BL-0075]
---

# ワールドネイバーズ_カフェポイントシェア

## 🎯 次のアクション
BL-0075 PoC 第1ステップ: 自分の決済を自分の PC 上で実行し、携帯端末からトリガーする個人内構成を試作する。まず決済 Web アプリの画面遷移・認証方式の調査から着手。

## 🚧 現在のブロッカー
なし (P3、構想段階)

## 📋 概要
シェアハウス「ワールドネイバーズ」では全住民に毎月15,000円分のカフェポイントが付与され月末失効する。余らせる人と使い切る人がいるため住民間で融通できる仕組みを作りたい。素朴案として提供側の決済アプリ ID/パスワードを保存し PC 上で RPA 的に決済処理を起動、受取側は別 UI からトリガー、店員には完了画面のスクリーンショットを送る方式を検討中。アイディアメモ段階の趣味プロジェクト。

## 🔄 進行中
- [ ] BL-0075 ワールドネイバーズ カフェポイントシェアアプリ: 第1ステップ PoC (自分PC→携帯で決済トリガー) (todo / P3)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-24 README + ProjectIndex 整備、構想メモ確定

## 🧠 決定事項 (Why ログ)
- 第1ステップは「他人決済」ではなく「自分内 PoC」に限定: 規約・セキュリティ論点 (シェアハウス規約 / ID パスワード保管 / 偽造耐性) を切り分けるため
- RPA 候補は Playwright が有力 (READMEより)

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/0.Other/ワールドネイバーズ_カフェポイントシェア/README.md`
- ProjectIndex: `Stock/0.Other/ワールドネイバーズ_カフェポイントシェア/ProjectIndex.yaml`
- log: `Stock/0.Other/ワールドネイバーズ_カフェポイントシェア/log.md`
