---
schema_version: 1
project: <Project名>
category: <Program名>
status: in_progress           # in_progress | awaiting_user | blocked | completed | paused
owner_turn: ai                # ai | user | external
updated_at: YYYY-MM-DDTHH:MM:SS+09:00
updated_by: <agent identifier>
current_bl: BL-XXXX           # 現在 active な BL ID。なければ null
next_action: "<次の具体的な一手 (1-2 行)>"
blocker: null                 # 阻害要因あれば文字列で
related_bls: [BL-XXXX, BL-YYYY]
---

# <Project名>

## 🎯 次のアクション
<README + active BL から判断した具体的な次の一手>

## 🚧 現在のブロッカー
なし (or 具体的な阻害要因)

## 📋 概要
<プロジェクトの目的、現状、関係者などを 1 段落>

## 🔄 進行中
- [ ] BL-XXXX <タイトル> (state / priority)

## ✅ 完了済 (ハイライト)
- [x] YYYY-MM-DD <内容>

## 🧠 決定事項 (Why ログ)
- YYYY-MM-DD: <重要な決定とその理由>

## 📜 履歴
- YYYY-MM-DD <変更内容>

## 🔗 関連リンク
- README: `Stock/<Program>/<Project>/README.md`
- ProjectIndex: `Stock/<Program>/<Project>/ProjectIndex.yaml`
- 中央 Backlog: `Stock/定型作業/バックログ/Backlog.md`

---

> このテンプレートは **ミニタキオン v2 schema** に準拠。
> 編集は **`mt` CLI 経由のみ** (`mt projects list` / `mt bl get` 等)。
> YAML を直接書き換えない (zod 検証で reject される)。
> 詳細: `aios/ops/13_mini_tachyon_protocol.mdc`。
