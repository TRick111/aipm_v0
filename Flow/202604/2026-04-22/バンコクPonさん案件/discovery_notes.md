# BL-0037 Discovery Notes — PONさんChatGPT履歴整理

最終更新: 2026-04-22

## 1. タスクの最終ゴール（再確認）

PONさんが**今後ChatGPT等で会話する際に「過去の会話履歴の内容を反映したチャット」ができる状態**を作る。
そのために AIOS に取り込める長期記憶ファイル群一式を生成し、PONさん本人に送付する。

完了条件は4つ（ユーザー指示より）:

1. Step4 deploy 完了 — Stock配下 `ChatGPT移行/` に README.md / ProjectIndex.yaml / カテゴリ別ディレクトリを配置
2. PONさん向けナレッジソース一覧を生成（テーマ別知見、未実行アイデア、頻出トピック、など）
3. PONさん向け案内ドキュメント — 「これを使えば過去会話を踏まえたチャットができます」
4. 送付方法を田中さんと合意

## 2. 既知情報の確認結果

### 2.1 パイプラインの現状（2026-04-22 15時時点）

| Step | フェーズ | 状態 | ソース |
|---|---|---|---|
| Step1 抽出 | done | 225件の個別JSON生成済み | `pipeline/step1_extracted/` |
| Step2 判別 | done | 成果物あり120 / なし105 | `pipeline/step2_classified/` |
| Step3 マージ | done | 21サブカテゴリ生成済み | `pipeline/step3_merged/` (下記 §2.2) |
| Step4 合成 | **submit済・process未** | batch_id `msgbatch_01Cr5eMWNpfpMH6PBSWYbmZA` が `ended / 25 succeeded` で待機中 | `pipeline/step4_output/batch_log.json` |

- Step4のバッチはサブカテゴリREADME 21件(Sonnet) + カテゴリREADME 4件(Opus) = 25件
- バッチ送信日時: 2026-04-11 17:45（ユーザー事前確認で結果は取得可能とのこと）
- Step4 process 実行すれば `OUTPUT_DIR = pipeline/step4_output/output/` 配下に全READMEが並ぶ
- Step4 deploy 実行で `DEPLOY_DIR = Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/` へコピー（現状未作成）

### 2.2 Step3 マージ結果サマリ（`merge_manifest.json`）

- 4カテゴリ × 21サブカテゴリ
- 会話件数（成果物なしでサマリ化されたもの）合計: **115件**
- 成果物ファイル合計: **439件**

| カテゴリ | サブカテゴリ数 | 会話 | 成果物 |
|---|---:|---:|---:|
| 美容室 | 8 (全般 / Rapi-rabi / YAMS / Cuu's / BELL / Rio / ベトナム支店 / その他) | 75 | 230 |
| 美容専門店 | 4 (ネイル / アイラッシュ / MONDO / その他) | 18 | 62 |
| 自社ブランド | 4 (KINUJO / ヌリプラ / DOT / 商品_店販) | 19 | 65 |
| J-Beauty | 5 (アカデミー / 政策_予算 / イベント / 総合_戦略 / コスメ) | 8 | 82 |

- 各サブカテゴリ内には `conversations_summary.md` / `conversations_index.json` / `artifacts/` が揃っている
- サマリ内容は「概要 / 主要トピック / 時系列 / 重要な決定事項 / 登場人物」で構成されており、人間向けの読み物として既に完成度が高い（美容室全般を目視確認）

### 2.3 関連ファイル

- パイプライン本体: `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT分析/`
  - `pipeline.py` / `config.py` / `batch_api.py` / `step4_synthesize.py` 他
- DEPLOY先: `~/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/` (未作成)
- 分類仕様書: `ChatGPT分析/確定_分類手順と分類案.md`

## 3. ゴールに対する現状とギャップ

### 3.1 Step4 deploy（ゴール完了条件 a）

- **ギャップ**: process と deploy の2コマンドを回すだけで到達可能
- **リスク**: バッチ結果の取得可能期間（Anthropic標準29日）をすでに11日経過。まだ取得可能と確認済みだが、優先的に process を走らせる

### 3.2 PONさん向け「ナレッジソース」(ゴール完了条件 b)

**ここが本タスクの主眼で、Step4 deploy だけでは満たされない。**

Step4で生成されるのは「AIOSディレクトリ構造＋カテゴリ/サブカテゴリREADME」。PONさんが **ChatGPT/Claude等にコンテキストとして投入して過去会話を反映した対話を実現する**ためには、別フォーマットの「長期記憶ファイル群」が必要。

想定される成果物カテゴリ（AI提案）:

| # | ファイル種別 | 目的 | ソース |
|---|---|---|---|
| ① | `PON_persona.md` | AIに毎回冒頭で渡す「PONさんは誰・何をやってる人か」コンテキスト（事業領域/店舗一覧/関係者/価値観） | Stock/README.md + 全サブカテゴリの人物表を統合 |
| ② | `business_context.md` | 経営全体像（美容室群/自社ブランド/J-Beauty）の俯瞰。ChatGPT新規会話の最初に貼る用途 | 各カテゴリREADME + manifestを合成 |
| ③ | `themes/{theme}.md` | テーマ別ナレッジ（給与制度・プロモ・商品開発・人事・競合・海外展開 ほか） | 21サブカテゴリの conversations_summary.md をテーマ軸で再編 |
| ④ | `decisions_log.md` | 過去に決定した事項の時系列ログ（給与制度/コミッション率/人件費率など） | 各サマリの「重要な決定事項」セクションをマージ |
| ⑤ | `open_ideas.md` | 話に出たが未実行のアイデア・保留案 | conversations_summary.md + artifacts を再走査 |
| ⑥ | `people_directory.md` | スタッフ・取引先・相談相手の一覧 | conversations_index.json + conversations_summary.md の人物表 |
| ⑦ | `artifacts_index.md` | 439件の成果物のカテゴリ別目次（PONさんが必要時に取り出せるよう） | Step3 artifacts全ファイル名 + メタデータ |

**生成方法の選択肢**:
- (A) Batch APIで追加合成する（LLMに再走査させて品質の高い長期記憶を作る）
- (B) 既存ファイルの再編集・機械的マージだけで作る（速い・安い・低リスク）
- (C) A+B ハイブリッド（ペルソナ系①②③はLLM合成、インデックス系⑥⑦は機械的、決定事項④・アイデア⑤はLLM抽出）

AI推奨は **(C) ハイブリッド**。理由は後述 implementation_plan.md §3。

### 3.3 PONさん向け案内ドキュメント（ゴール完了条件 c）

未作成。必要記述:
- ファイル群の一覧と各ファイルの用途
- 具体的な使い方（ChatGPT Projects / Custom GPT / NotebookLM / Claude Projects のいずれに投入するか）
- よくあるシナリオのテンプレ（例: 「給与制度の続きを相談したい時はこのファイルを貼る」）

### 3.4 送付方法（ゴール完了条件 d）

未確定。候補:
- (1) Google Drive 共有フォルダ
- (2) Zip 添付（メール/LINE/Slack）
- (3) GitHub private repo に push して招待
- (4) Notion ページ化

## 4. 確認が必要な不明点（→ INBOX.md へ）

1. **PONさんが使う想定のAIツール**は？ ChatGPT Plus(Projects) / Custom GPT / NotebookLM / Claude Projects / 複数併用 — これによりファイル粒度と命名規則が変わる
2. **送付方法**の希望はあるか？（例: Google Drive に一式置いて共有URLを送る、が簡単）
3. **秘匿性のレベル** — スタッフ実名・具体的な給与額が多数含まれる。そのまま送付 / 伏字化 / PONさん本人だから全面OK のどれか
4. **本日の作業スコープ** — 今日中に①Step4 deploy + ②ナレッジソース生成まで完了させるか、それとも段階分割（今日はStep4 deploy + 設計レビューまで）にするか

## 5. 想定所要時間

- Step4 process + deploy 実行: 10〜20分（バッチ取得・ファイルコピー）
- ナレッジソース生成: プランB（機械的）なら 30〜60分 / プランC（LLM合成込み）なら Batch API 1サイクル + 人間確認で 1〜3時間（Batch待ち含む）
- 案内ドキュメント作成: 30分
- Stock反映（MasterIndex/README/log更新）: 15分

合計: 最短 90分 / ハイブリッドLLMで 3〜4時間（Batch待ち時間含む）
