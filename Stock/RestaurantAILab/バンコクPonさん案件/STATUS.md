---
schema_version: 1
project: バンコクPonさん案件
category: RestaurantAILab
status: in_progress
owner_turn: ai
updated_at: 2026-04-26T01:00:00+09:00
updated_by: master-agent
current_bl: BL-0073
next_action: "2026-04-27 第6回セッション (PONさん) 資料準備 (BL-0073) と売上データAIアクセス説得資料 (BL-0074) を作成。並行して JBeauty デジタルサイネージ要件一覧 (BL-0070) を整理して送付"
blocker: null
related_bls: [BL-0037, BL-0041, BL-0042, BL-0043, BL-0044, BL-0045, BL-0068, BL-0070, BL-0071, BL-0072, BL-0073, BL-0074]
---

# バンコクPonさん案件

## 🎯 次のアクション
2026-04-27 (月) 第6回セッション本番に向けて:
1. **BL-0073** セッション資料・内容 (繰り返しタスク設定 / iCloud カレンダー連携 / 会話履歴インポート)
2. **BL-0074** 売上データ AI アクセスの設計・説得資料 (IT 担当者向け、データ流出懸念対応)

その後 JBeauty (BL-0070 要件一覧送付) と バーチャル美容アドバイザー POC (BL-0041〜BL-0045) を並列で進める。請求方法は BL-0068 PayPal → WISE 切替検討中。

## 🚧 現在のブロッカー
なし (BL-0066 飯武さん向けは別プロジェクトに分離済)

## 📋 概要
バンコクで複数拠点の美容院を経営する PON さんに対し、生成 AI 活用の戦略立案・導入・運用・開発を横断して支援する案件。Instagram 運用を含む集客・採用・業務効率化まで幅広く対象。本ディレクトリはタスク管理専用、成果物本体は `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/` 配下。

主要トラック:
- **PONさん AI 活用サポート**: 週1回セッション (現在 第6回 2026-04-27 予定)
- **J-Beauty Innovation Hub**: 日本政府の J-Beauty 施策への提言・提案
- **バーチャル美容アドバイザー POC**: 音声 + 実写アバター (BL-0041〜BL-0045)

関係者: 近藤Pon (Rio's Innovation 社長) / 田中利空 (開発) / 町田大地 (AI 担当)。

## 🔄 進行中
- [ ] BL-0073 第6回セッション資料・内容準備 (todo / P1, due 2026-04-27)
- [ ] BL-0074 売上データAIアクセスの設計・説得資料 (todo / P1, due 2026-04-27)
- [ ] BL-0037 チャット履歴の整理 (doing / P2, 2026-04-21 再開)
- [ ] BL-0041 バーチャル美容アドバイザー POC (todo / P1, 親タスク)
- [ ] BL-0042 タイ語テキストの確認 (todo / P1, BL-0041 サブタスク)
- [ ] BL-0043 タイ語テキストのスピーチ対応確認 (todo / P1, BL-0041 サブタスク)
- [ ] BL-0044 商品知識データの作成と連携検証 (todo / P1, BL-0041 サブタスク)
- [ ] BL-0045 実写アバターの動作確認 (todo / P1, BL-0041 サブタスク)
- [ ] BL-0068 PayPal → WISE 切替検討 (todo / P1)
- [ ] BL-0070 JBeauty: デジタルサイネージ要件一覧の作成と PONさんへ送付 (todo / P1)
- [ ] BL-0071 JBeauty: デジタルサイネージをリアルな人間の動きで実装 (検証) (todo / P2)
- [ ] BL-0072 JBeauty: デジタルサイネージが実プロダクトから提案する仕組みの検証 (todo / P2)

## ✅ 完了済 (ハイライト)
- [x] 2026-04-22 BL-0037 Phase 1〜3 着手 (ChatGPT 履歴を AIPM Program 形式にリパッケージ、GitHub private repo に push)
- [x] 2026-04-12 BL-0019 チケット管理システムの構築
- [x] 2026-04-12 BL-0035 第5回セッション資料作成
- [x] 2026-04-12 BL-0036 店舗内観イメージ生成方法の確立 (Gemini ベース)
- [x] 2026-03-24 BL-0018 第4回セッション資料 / BL-0020 2月分稼働時間計算 / BL-0021 2月分請求書発行

## 🧠 決定事項 (Why ログ)
- 請求方法を PayPal → WISE に切替検討 (BL-0068): タイで PayPal が使えないため
- ChatGPT 履歴は AIPM Program 形式にリパッケージし独立 GitHub private repo で管理 (BL-0037): PONさん招待しやすく履歴の構造化と版管理を両立
- BL-0041 を親タスクとし BL-0042〜BL-0045 をサブタスクに分解: タイ語 / TTS / 商品知識 / アバターの検証を並列で進めるため

## 📜 履歴
- 2026-04-26 master が STATUS.md を bootstrap (README + Backlog.md より生成)

## 🔗 関連リンク
- README: `Stock/RestaurantAILab/バンコクPonさん案件/README.md`
- log: `Stock/RestaurantAILab/バンコクPonさん案件/log.md`
- ProjectIndex: `Stock/RestaurantAILab/バンコクPonさん案件/ProjectIndex.yaml`
- BL-0037 Phase 1-3 計画: `Stock/RestaurantAILab/バンコクPonさん案件/implementation_plan_2026-04-22.md`
- 成果物本体 (AIOS提供): `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/`
- 成果物本体 (J-Beauty): `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/J-Beauty_Innovation_Hub/`
