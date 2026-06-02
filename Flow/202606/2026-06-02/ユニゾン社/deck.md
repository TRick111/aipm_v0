---
marp: true
theme: anthropic-cream
title: Claude Code で PowerPoint を作る 3 方法
author: ユニゾン社向け検証
paginate: true
---

# Claude Code で PowerPoint を作る 3 方法

- ローカル PC のデータを参照しながら Claude Code 上でスライドを生成する
- 候補: python-pptx / pptxGenJs / Marp
- 共通入力 Markdown を 1 本 (この deck.md) → 3 方法で同一内容を pptx 化
- 比較軸: 入力形式 / 出力品質 / テンプレ流用性 / ブランドカラー指定 / 編集性

---

# 方法A: python-pptx

- 入力: Python コード + 空テンプレ.pptx (Anthropic Cream 等)
- 処理: pptx の中身 (Open XML) を Python オブジェクトとして読み書き
- 出力: 編集可能 .pptx (PowerPoint で再編集 OK)
- 向く: コーポレートテンプレ流用、データ駆動の量産、表/グラフ多用
- 向かない: ドラフトを即時に投影したいとき、レイアウト微調整の試行錯誤

---

# 方法B: pptxGenJs

- 入力: JavaScript / Node コード (オブジェクト記述)
- 処理: JS オブジェクトを pptxGenJs ライブラリが pptx にシリアライズ
- 出力: 編集可能 .pptx (PowerPoint で再編集 OK)
- 向く: Web アプリからの動的生成、JS エコシステム前提のチーム
- 向かない: 既存 PowerPoint テンプレを忠実に流用したいとき (テンプレ読込弱め)

---

# 方法C: Marp

- 入力: Markdown 1 本 (フロントマター + `---` 区切り)
- 処理: Markdown を Marp CLI が解析 → HTML/CSS → 各形式に変換
- 出力: PDF / HTML / .pptx (既定は画像化、`--pptx-editable` で編集可)
- 向く: 速さ重視、Git 管理、Markdown ドラフトをそのまま投影
- 向かない: PowerPoint で細かく後編集する用途、複雑なレイアウト

---

# 比較表

| 観点 | python-pptx | pptxGenJs | Marp |
| --- | --- | --- | --- |
| 入力形式 | Python + テンプレ | JS オブジェクト | Markdown |
| 出力 | 編集可 .pptx | 編集可 .pptx | 画像化/編集可 .pptx, PDF, HTML |
| テンプレ流用 | ◎ (既存pptx読込) | △ (マスター定義) | △ (CSS) |
| ブランドカラー | ◎ (テンプレ + コード) | ◎ (コード) | ◎ (CSS) |
| PowerPointでの後編集 | ◎ | ◎ | △ (画像化時は不可) |
| 学習コスト | 中 | 中 | 低 |
| ローカル参照 | ◎ | ◎ | ◎ |
| 日本語 | ◎ | ○ | ◎ (CSS で Noto Sans JP) |
| 推奨ユースケース | 会社テンプレ忠実再現 | Webアプリ連携 | 速いドラフト/技術資料 |
