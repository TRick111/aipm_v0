# ChefsRoomマーケティング支援

## 背景
- Chef's Room社長 竹矢さんのInstagramアカウントの運用補助が必要
- 定期的にコンテンツを発信することでブランディング・集客につなげたい

## 目的
- 竹矢さんのInstagramアカウント向けに、リール動画等の台本を作成・納品する

## ゴール（完了条件）
- 定期的に台本テーマリストを受け取り、台本化して納品するフローが回っている

## 関係者

| 名前 | 所属・役職 | 役割 |
|---|---|---|
| 竹矢 | Chef's Room 社長 | クライアント・テーマ提供 |
| 吉田 | Restaurant AI Lab 代表 | 全体統括 |
| 町田大地 | Restaurant AI Lab AI担当 | 台本作成 |
| 田中利空 | Restaurant AI Lab 開発担当 | 開発・自動化 |

## 現在の状況・ネクストアクション
- 現状: 継続運用中（定期的に台本テーマを受け取り納品）
- ネクストアクション:
  - [ ] 次回テーマリスト受領後、台本作成

---

## 台本生成の手順

### 概要
テーマリスト（CSV）を入力として、Gemini APIを使って17シーン構成のリール台本を自動生成する。

### 1. 入力CSVの準備

入力CSVには以下の列が必要:

| 列名 | 説明 | 必須 |
|---|---|---|
| No | 連番 | 任意 |
| タイトル | テーマ名（台本のタイトルになる） | 必須 |
| フック | 冒頭の引きになる文言 | 推奨 |
| 解決策 | 提示する解決策 | 推奨 |
| エンド | 締めの文言 | 推奨 |

**入力例:**
```csv
No,タイトル,フック,解決策,エンド,処理済み
1,限界利益と粗利の違い,まさか限界利益と粗利の違い分からん飲食店オーナーいませんよね？,定義・目的が明確に異なる...,飲食店経営は「売上を作る業態」ではなく...,
```

### 2. スクリプトの実行

#### 必要なもの
- Python 3.10+
- Gemini API Key（`GOOGLE_API_KEY` 環境変数）
- 依存パッケージ: `langchain-google-genai`, `python-dotenv`, `langchain-core`

#### 実行方法

**方法A: 一時作業ディレクトリで実行（推奨）**

日本語パスの問題を回避するため、以下の手順で実行:

```powershell
# 1. 作業ディレクトリを作成
mkdir c:\temp\scripts_work

# 2. 必要ファイルをコピー
Copy-Item "Stock\RestaurantAILab\ChefsRoomマーケティング支援\2.execute\1.scripts\generate_scripts_with_gemini.py" "c:\temp\scripts_work\"
Copy-Item "Stock\RestaurantAILab\ChefsRoomマーケティング支援\2.execute\1.scripts\examples.yaml" "c:\temp\scripts_work\"
Copy-Item "Stock\RestaurantAILab\ChefsRoomマーケティング支援\2.execute\prompt_improved.md" "c:\temp\scripts_work\"
Copy-Item "<入力CSVのパス>" "c:\temp\scripts_work\input.csv"

# 3. スクリプト内のパス設定を一時ディレクトリ用に修正（CSV_IN, CSV_OUT, PROMPT_MD等）

# 4. 環境変数を設定して実行
$env:GOOGLE_API_KEY = "<YOUR_API_KEY>"
$env:CSV_IN = "c:\temp\scripts_work\input.csv"
$env:CSV_OUT = "c:\temp\scripts_work\output_scripts.csv"
python c:\temp\scripts_work\generate_scripts_with_gemini.py
```

**方法B: 環境変数で入出力パスを指定**

```powershell
$env:GOOGLE_API_KEY = "<YOUR_API_KEY>"
$env:CSV_IN = "<入力CSVのフルパス>"
$env:CSV_OUT = "<出力CSVのフルパス>"
python "Stock\RestaurantAILab\ChefsRoomマーケティング支援\2.execute\1.scripts\generate_scripts_with_gemini.py"
```

### 3. 出力

17シーン構成の台本がCSVで出力される:

| 列 | 説明 |
|---|---|
| No | 連番 |
| テーマ | 入力のタイトル |
| シーン1〜シーン17 | 各シーンのセリフ |
| 参考例ID | 生成時に参照した例のタイトル（セミコロン区切り） |

### 4. 注意事項

- `langchain-google-genai` の新しいバージョンでは `llm.invoke()` を使用する（旧: `llm()` は非推奨）
- 1件あたり約20-30秒かかる（12件で約5分）
- 生成結果は `examples.yaml` の参考例に基づいて関西弁のトーンで出力される

---

## フォルダ構成

```
2.execute/
├── 1.scripts/
│   ├── generate_scripts_with_gemini.py  # 台本生成スクリプト
│   └── examples.yaml                     # 参考例（トーン学習用）
├── 2.input/
│   ├── YYYY-MM-DD/                       # 日付別フォルダ
│   │   └── input.csv
│   └── inputXX.csv                       # または連番管理
├── 3.output/
│   ├── YYYY-MM-DD/                       # 日付別フォルダ
│   │   └── output_scripts.csv
│   └── generated_scripts_YYYY_MM_DD.csv  # または日付付きファイル名
├── prompt_improved.md                    # Geminiへの指示プロンプト
└── work_log.md                           # 作業ログ
```

---

## 今後のプラン（中期）

| 時期 | 項目 | 備考 |
|---|---|---|
| 継続 | 定期台本作成・納品 | |

## 重要リンク（外部）

| 名称 | URL | 備考 |
|---|---|---|
| （後で追加） | | |
