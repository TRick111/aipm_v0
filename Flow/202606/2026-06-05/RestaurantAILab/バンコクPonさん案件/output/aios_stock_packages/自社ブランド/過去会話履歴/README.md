# 過去会話履歴

## このProjectについて

PONさん（近藤Pon / Rios Innovation Co., Ltd.）が過去に **ChatGPT** で行ってきた会話のうち、自社ブランド に関連する分を **1会話 = 1サマリー** の粒度で整理した個別ナレッジ集です。

各サマリーには以下が含まれます：
- frontmatter（conversation_id / date / subcategory / artifact_files など）
- ひとことサマリー
- 論点と結論（主語述語が明確な完全文）
- 決定事項・アクション
- 言及された人物・店舗・商品
- 関連 artifacts へのリンク（同階層 `artifacts/`）
- 重要な引用（原文）

## このフォルダの中身

| 項目 | 件数 |
|---|---:|
| 個別会話サマリー (.md) | 20 |
| 関連 artifacts (`artifacts/`) | 65 |

### サブカテゴリ内訳

- **KINUJO**: 10件
- **ヌリプラ**: 7件
- **DOT**: 3件

## 使い方（Cursor + AIOS）

### 1. 最初に読むべきファイル

新しい AI セッションを始めるときは、まず以下を会話の冒頭で参照させてください：

- `_overview/01_PON_persona.md` — PONさん全体のビジネスコンテキスト
- このProjectの `README.md`（本ファイル）

これで AI は PONさんが 自社ブランド で過去に検討してきた論点を踏まえた回答ができます。

### 2. テーマで探す

- 横断テーマ → `_overview/themes/{テーマ}.md`（給与・プロモ・商品・人事・競合・海外・経営指標）
- 過去の決定事項 → `_overview/03_decisions_log.md`
- 未実行アイデア → `_overview/04_open_ideas.md`
- 個別会話索引 → `_overview/06_conversations_index.md`（20件、日付昇順）

### 3. 個別の論点を深掘り

- `{date}_{slug}_{convId8}.md` のファイル名から該当会話を開く
- frontmatter の `artifact_files` から関連成果物に飛ぶ
- 本文中のリンクから `artifacts/...` を直接開く

### 4. 人物・店舗で検索

- `grep -r "RISA" .` 等で名前を横断検索
- 該当する個別サマリー → frontmatter の subcategory・日付で時系列把握

## 参照のヒント

- サマリーの**論点と結論**は完全な文章で書かれているので、grep の対象になりやすいです
- artifact ファイル名は元会話で AI が生成した実体（提案書・スクリプト・メール文案・分析レポート）

## 関連

- 横断ナレッジ: `_overview/`
- 変更履歴: `log.md`
- 全体カタログ: `Stock/MasterIndex.yaml`
