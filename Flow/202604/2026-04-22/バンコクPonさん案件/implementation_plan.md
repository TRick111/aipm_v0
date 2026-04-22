# BL-0037 Implementation Plan — PONさんChatGPT履歴整理

最終更新: 2026-04-22

## 0. 前提
- Discovery: `discovery_notes.md` 参照
- 作業ディレクトリ（Flow）: `Flow/202604/2026-04-22/バンコクPonさん案件/`
- 成果物本体の出力先: `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/` (パイプラインのDEPLOY_DIR)
- ナレッジソース（PONさん向け追加成果物）の出力先: 同じく `ChatGPT移行/for_PON/` を予定（命名は確認事項）

## 1. 実行計画ざっくり（3フェーズ）

### Phase 1: Step4 完走（Stock基盤の確定）
現状 submit 済みのバッチを process → deploy し、AIOSナレッジベース構造を完成させる。

### Phase 2: PONさん向けナレッジソース生成
Stock配下の構造を素材に、PONさんが「ChatGPT等で過去の文脈を再利用できる」形式のファイル群を作る。

### Phase 3: 案内ドキュメント作成・送付
PONさん向けREADMEを書き、合意した方法で送付（実送付は田中さん本人の可能性あり）。

---

## 2. Phase 1 — Step4 完走（所要 15〜20分）

### 2.1 作業手順

```bash
# 作業ディレクトリ
cd ~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT分析

# ステータス再確認（バッチがまだ取得可能か）
python pipeline.py step4 --process   # ← ここでバッチ結果取得 + README生成
# 成功すると pipeline/step4_output/output/ 配下にREADME群が出る

python pipeline.py step4 --deploy    # ← Stock配下に配置
# Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/ ができる
```

### 2.2 成果物

- `Stock/…/ChatGPT移行/README.md`（トップ）
- `Stock/…/ChatGPT移行/ProjectIndex.yaml`
- `Stock/…/ChatGPT移行/log.md`
- `Stock/…/ChatGPT移行/{カテゴリ}/README.md` × 4
- `Stock/…/ChatGPT移行/{カテゴリ}/{サブカテゴリ}/README.md` × 21
- 各サブカテゴリに `conversations_summary.md` / `conversations_index.json` / `artifacts/` もコピーされる

### 2.3 リスクと対策

- **バッチ結果が取得不可**: 再 `--prepare → --submit` で再生成（コスト約$2、所要1〜数時間）。事前にユーザーに確認済み「取得可能」だが、process実行時にエラー出たら即ユーザーへ報告
- **process失敗**: 詳細ログを discovery_notes.md に追記して報告

### 2.4 Stock更新（AIOSルール6.1より必須）

deploy後、以下4ファイルを同時更新:
- `Stock/MasterIndex.yaml`（バンコクPonさん案件配下に ChatGPT移行 プロジェクト追加 — 既に親プログラムに載っている場合は files 追記のみ）
- `Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/ProjectIndex.yaml`（step4が自動生成）
- `Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/README.md`（step4が自動生成）
- `Stock/バンコクPonさん案件/log.md`（ChatGPT移行プロジェクト配置を1行追記）

---

## 3. Phase 2 — ナレッジソース生成（所要 60〜120分、ハイブリッド方式）

### 3.1 設計方針

**目的**: PONさんがChatGPT等に「過去の文脈をコピペ/アップロードするだけで、過去の相談・決定を踏まえて対話できる」状態。

**推奨方式: ハイブリッド (C)**
- ペルソナ・業務全体像・テーマ別ナレッジ → LLM合成（既存conversations_summary.mdを再編集・統合）
- 決定事項ログ・未実行アイデア → LLM抽出（各サマリの「重要な決定事項」から構造化）
- 人物表・成果物インデックス → 機械的マージ（スクリプトでJSON/YAMLから生成）

**出力先案**: `Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/for_PON/`
- PONさん専用の長期記憶ファイル群
- 「ChatGPTに貼り付ける」「ChatGPT Projects に登録する」前提の粒度
- 各ファイル先頭にコンテキスト説明のメタヘッダを付ける（AIが一読で役割を理解できる）

### 3.2 生成するファイル群（7種）

| # | ファイル | 生成方法 | 所要 |
|---|---|---|---|
| ① | `01_PON_persona.md` | LLM（全サブカテゴリ人物表＋README統合） | 10分 |
| ② | `02_business_overview.md` | LLM（4カテゴリREADMEから俯瞰図を合成） | 10分 |
| ③ | `03_themes/{7テーマ}.md` | LLM（サマリを「給与/プロモ/商品開発/人事/競合/海外展開/経営管理」7軸に再編） | 30〜60分 |
| ④ | `04_decisions_log.md` | LLM抽出（各サマリの「重要な決定事項」を時系列にマージ） | 15分 |
| ⑤ | `05_open_ideas.md` | LLM抽出（未決/検討中/アイデア止まりの項目を抽出） | 15分 |
| ⑥ | `06_people_directory.md` | 機械生成（conversations_index.json / 人物表を集約） | 10分 |
| ⑦ | `07_artifacts_index.md` | 機械生成（439件の成果物をカテゴリ別に目次化） | 10分 |

### 3.3 生成スクリプトの置き場所

- 追加する合成スクリプトは **Flow** に置いて作業する（AIOSルール2.1）
- 場所: `Flow/202604/2026-04-22/バンコクPonさん案件/scripts/`
  - `build_for_pon.py` — Batch API 呼び出し + 機械マージを一括実行
  - `for_pon_prompts.py` — 各ファイル用のシステムプロンプト定義
- 確定・再利用したくなったら後日 `Stock/…/ChatGPT分析/` へ移送

### 3.4 LLM合成はBatch APIを使う

- ファイル数 = ③の7テーマ + ①②④⑤の4ファイル = 計11リクエスト
- Sonnet中心、俯瞰系①②のみOpusで品質担保を検討
- 3フェーズ（prepare/submit/process）で進め、submit後はバッチ待機
- コスト見積: 約$1〜2（Batch割引込み）

### 3.5 秘匿性の扱い（※確認事項に依存）

- デフォルト: PONさん本人への返却なのでマスキングなし（=原文のまま）
- ユーザー指示があれば: スタッフ名を伏字化するポストプロセス層を入れる

---

## 4. Phase 3 — 案内ドキュメント作成と送付（所要 30〜45分）

### 4.1 `for_PON/README.md` の内容

- このディレクトリの目的（「過去ChatGPT会話を踏まえた対話を実現するためのコンテキストパック」）
- ファイル一覧と各ファイルの役割
- 3つの使い方シナリオ（ChatGPT Projects / NotebookLM / 都度コピペ）
  - 例: **ChatGPT Projects の場合**: このフォルダ一式を zip でアップロード → 新規スレッドで質問すればOK
  - 例: **NotebookLMの場合**: 01〜07のmdを全ソースとしてアップ → 「テーマXについて過去の議論を踏まえて提案して」と聞く
  - 例: **Claude Projects の場合**: 同様の手順
- 更新方法のメモ（今後ChatGPTを使い続けるなら、一定期間ごとに再エクスポート→同じパイプラインで更新できる）

### 4.2 送付（確認事項に依存）

候補別の作業量:
- (1) Google Drive 共有: フォルダアップロード → 共有設定 → URL発行（5分。gws CLI でやってもよい）
- (2) Zip添付: `tar czf for_PON_20260422.tgz for_PON/` → 田中さん経由で送信（5分）
- (3) GitHub private: 新規repo作成 → push → PONさん招待（15分）
- (4) Notion: gws CLI or手動で各mdをNotion化（30分〜）

AI推奨は **(1) Google Drive**。理由: ファイル多数（75+ファイル）、今後の更新配布もURL再共有で済む、zipより閲覧が楽、田中さん経由の手間が少ない。

## 5. タスク分解（並行タスク運用ルール準拠）

### 5.1 クラス分類
- **クラスA（実装）**: Phase 1（Step4完走）、Phase 2（ナレッジソース生成）、Phase 3（案内ドキュメント）
- **クラスB（確認）**: 不明点4件（INBOX起票済み）

### 5.2 サブタスク一覧

| ID | サブタスク | フェーズ | 状態 | 依存 |
|---|---|---|---|---|
| S1 | Step4 --process 実行 | Phase 1 | 未着手 | (なし) |
| S2 | Step4 --deploy 実行 | Phase 1 | 未着手 | S1 |
| S3 | MasterIndex/log更新 | Phase 1 | 未着手 | S2 |
| S4 | for_pon_prompts.py + build_for_pon.py 作成 | Phase 2 | 未着手 | S2 |
| S5 | Batch API prepare → submit | Phase 2 | 未着手 | S4 |
| S6 | Batch 結果 process（7テーマ+4俯瞰） | Phase 2 | 未着手 | S5 |
| S7 | 人物表・artifacts目次の機械生成 | Phase 2 | 未着手 | S2 |
| S8 | for_PON/README.md 案内ドキュメント作成 | Phase 3 | 未着手 | S6, S7 |
| S9 | 送付方法確定 + 実施 | Phase 3 | 未着手 | S8 + 不明点Q2 |

S1〜S3 は不明点なしで即着手可能。S4以降は **不明点Q1（投入先ツール）とQ3（秘匿性）** の回答があれば品質を最適化できる。

## 6. 実装ゲート（ユーザー承認ポイント）

- **ゲート1**: 本計画書の承認 → Phase 1 着手
- **ゲート2**: Phase 1 完了報告 + 不明点4件回答 → Phase 2 着手
- **ゲート3**: ナレッジソース生成物の目視確認 → Phase 3（送付）着手

## 7. 想定アウトプットサマリ

最終的にPONさんに届くもの:

```
for_PON/
├── README.md                      # 案内（使い方）
├── 01_PON_persona.md              # AIに最初に渡すペルソナ定義
├── 02_business_overview.md        # 事業全体像俯瞰
├── 03_themes/
│   ├── 給与制度とスタッフマネジメント.md
│   ├── プロモーション・マーケティング.md
│   ├── 商品開発・ブランド戦略.md
│   ├── 人事評価・採用.md
│   ├── 競合分析と市場対応.md
│   ├── 海外展開とJ-Beauty.md
│   └── 経営指標・財務管理.md
├── 04_decisions_log.md            # 時系列決定ログ
├── 05_open_ideas.md               # 未実行アイデア集
├── 06_people_directory.md         # 登場人物一覧
└── 07_artifacts_index.md          # 成果物439件の目次
```

計 **13ファイル**。各ファイル2,000〜8,000字想定。zip合計 <1MB。
