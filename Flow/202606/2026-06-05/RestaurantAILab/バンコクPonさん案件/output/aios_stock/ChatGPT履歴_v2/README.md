# ChatGPT履歴_v2

## このProgramについて

PONさん（近藤Pon / Rios Innovation Co., Ltd.）の過去のChatGPT会話履歴を、**1会話=1サマリー**の粒度で AIOS ナレッジに統合したナレッジベースです。

旧版 (`ChatGPT履歴` / 2026-04-22 生成) はサブカテゴリ単位の総体サマリーでしたが、本v2では：

- 個別会話単位のサマリー **226件**（論点・結論・決定事項・関連artifacts・重要引用）
- 関連 artifacts **439件** を同階層に同梱

これにより、特定の決定がどの会話で生まれたかを会話レベルで辿れます。

## ディレクトリ構造

```
ChatGPT履歴_v2/
├── README.md                     ← このファイル
├── MasterIndex_snippet.yaml      ← PONさんの Stock/MasterIndex.yaml に追記する分
├── _overview/                    ← Program横断ナレッジ（最初に読む）
│   ├── 00_README.md
│   ├── 01_PON_persona.md         ← AIに最初に渡すペルソナ
│   ├── 02_business_overview.md   ← 事業全体像
│   ├── 03_decisions_log.md       ← 決定事項の時系列ログ
│   ├── 04_open_ideas.md          ← 未実行アイデア集
│   ├── 05_people_directory.md    ← 登場人物・関係者
│   ├── 06_artifacts_index.md     ← (旧)成果物目次
│   ├── 06_conversations_index.md ← (新) 226件の個別会話索引
│   └── themes/                   ← テーマ別ナレッジ7本
├── 美容室/                       ← Project
├── 美容専門店/                   ← Project
├── 自社ブランド/                 ← Project
└── J-Beauty/                     ← Project
```

各 Project 直下に：
- `README.md` / `ProjectIndex.yaml` / `log.md`（AIOS規約）
- 個別会話サマリー (`{date}_{slug}_{convId8}.md`)
- `artifacts/` ディレクトリ

## 統計

| Project | 個別サマリー | artifacts |
|---|---:|---:|
| 美容室 | 141 | 230 |
| 美容専門店 | 40 | 62 |
| 自社ブランド | 20 | 65 |
| J-Beauty | 25 | 82 |
| **合計** | **226** | **439** |

## PONさん側でのセットアップ（3ステップ）

### Step 1. Stockに配置

```bash
# PONさんのAIOSリポジトリのルートで
cp -r ChatGPT履歴_v2 ~/path/to/your-aios/Stock/
```

### Step 2. MasterIndex.yaml に追記

`MasterIndex_snippet.yaml` の内容を、自分の `Stock/MasterIndex.yaml` の Programs セクションに追記してください。

### Step 3. 使ってみる

Cursorで新しいチャットを開き、以下のように冒頭で参照する：

> 「Stock/ChatGPT履歴_v2/_overview/01_PON_persona.md を読んで、私が誰か理解してください。
> その上で、ラピラピのワタルさん向け給与体系の核心を、過去の整理を踏まえて教えてください。」

AI が `美容室/2026-03-19_美容室再建の給与設計_*.md` を参照し、artifacts まで辿れます。

## 旧版との関係

| 観点 | 旧版 (`ChatGPT履歴`) | 新版 (`ChatGPT履歴_v2`) |
|---|---|---|
| Project数 | 21（subcategory単位） | 4（category単位） |
| 会話サマリー粒度 | サブカテゴリ単位の総体 | **1会話=1サマリー** |
| サマリー件数 | 21 | **226** |
| artifacts | 同梱 | 同梱（フラット配置） |
| 並存 | — | 旧と独立、両方Stockに置ける |

両方Stockに置いた場合、PONさんは状況に応じて使い分けできます：
- 大まかなテーマで掴みたい → 旧版
- 「あの決定はどの会話で？」→ 新版

## 秘密情報について

スタッフ氏名・給与額・取引先など機微情報を含みます。**privateリポジトリで運用してください**。

## 生成元

- PONさんのChatGPT会話履歴 export (2026-03-23 取得 / 654会話)
- うち4カテゴリに該当する225会話を1会話=1サマリーで整形（2026-06-05 生成）
- 田中利空 + Claude Code（Master + Sub-agent並列）

## ライセンス

Rios Innovation Co., Ltd. 内部ナレッジベース。無断で外部共有しないでください。
