# 週報作成システム - 分析フロー詳細ドキュメント

**作成日**: 2025年12月28日
**対象店舗**: Five Arrows
**目的**: 売上データと口コミデータから週報作成基礎資料を自動生成するシステムの完全な運用ガイド

---

## 目次

1. [システム概要](#1-システム概要)
2. [分析フローの全体像](#2-分析フローの全体像)
3. [ディレクトリ構成](#3-ディレクトリ構成)
4. [前提条件とセットアップ](#4-前提条件とセットアップ)
5. [分析の実行方法](#5-分析の実行方法)
6. [出力ファイルの詳細](#6-出力ファイルの詳細)
7. [分析観点とロジック](#7-分析観点とロジック)
8. [トラブルシューティング](#8-トラブルシューティング)
9. [更新履歴](#9-更新履歴)

---

## 1. システム概要

### 1.1 システムの目的

このシステムは、飲食店の週次データを包括的に分析し、経営判断に役立つ週報基礎資料を自動生成します。

**主な特徴**:
- Pythonによるデータ分析と可視化
- Claude（AI）による自然言語インサイト生成
- Google Docs互換のWord形式での出力
- 複数週の比較分析（前週比、前月比、前年比）
- カテゴリおよび商品レベルでの構成比推移分析

### 1.2 分析の2層構造

このシステムは2つの処理層で構成されています:

#### 第1層: Python分析層
- **役割**: 数値データの集計、統計処理、グラフ生成
- **ツール**: pandas, matplotlib, seaborn
- **出力**: JSON, CSV, PNG（グラフ）

#### 第2層: AI自然言語分析層
- **役割**: データの解釈、インサイト抽出、推奨アクション策定
- **ツール**: Claude（LLM）
- **出力**: Markdown → Word（.docx）

---

## 2. 分析フローの全体像

```
┌─────────────────────────────────────────────────────────────┐
│ 【入力データ】                                               │
│  ├─ 1_input/rawdata.csv  (売上トランザクションデータ)        │
│  └─ 1_input/reviews.csv  (口コミデータ)                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 【第1層: Python分析】 analysis_script.py                     │
│                                                              │
│  1. データ読み込みとクレンジング                              │
│  2. 週次集計（year_week列の生成）                            │
│  3. 対象週の特定と比較週の設定                                │
│     - 対象週                                                 │
│     - 前週（1週前）                                          │
│     - 前月同週（4週前）                                      │
│     - 前年同週（52週前）                                     │
│  4. 多角的分析の実行                                         │
│     ├─ 週次推移分析（売上、客数、客単価、組数）              │
│     ├─ 曜日別分析（営業日パターン）                          │
│     ├─ 時間帯別分析（ピークタイム特定）                      │
│     ├─ カテゴリ別分析（商品構成比と推移）                    │
│     └─ 商品別分析（個別メニューランキングと推移）            │
│  5. データ可視化（7種類のグラフ生成）                        │
│  6. 構造化データ出力（JSON, CSV）                            │
│     └─ NEW! 構成比時系列データの出力                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 【中間出力】                                                 │
│  ├─ 2_output/analysis_results.json       (全分析結果)       │
│  ├─ 2_output/weekly_sales.csv            (週次集計)         │
│  ├─ 2_output/category_latest.csv         (カテゴリ最新週)   │
│  ├─ 2_output/product_latest.csv          (商品最新週)       │
│  ├─ 2_output/category_composition_trend.csv (カテゴリ構成比推移) NEW! │
│  ├─ 2_output/product_composition_trend.csv  (商品構成比推移) NEW! │
│  └─ 2_output/*.png                       (7種類のグラフ)    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 【第2層: Claude AI分析】                                     │
│                                                              │
│  1. JSONデータの読み込みと理解                               │
│  2. 分析観点に基づくインサイト抽出                           │
│     （参照: 分析観点.md）                                    │
│  3. セクション別分析の実施                                   │
│     ├─ 売上分析（週次推移、曜日別、時間帯別）                │
│     ├─ 商品分析（カテゴリ別、商品別）                        │
│     │   └─ 構成比推移CSVを使った時系列分析 NEW!             │
│     └─ 口コミ分析（投稿数、内容評価）                        │
│  4. 総合考察とアクションプラン策定                           │
│  5. Markdown形式でレポート生成                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 【Markdown出力】                                             │
│  └─ 2_output/週報作成基礎資料.md                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 【形式変換】 generate_docx.py                                │
│  - pypandocを使用してMarkdown → Word変換                     │
│  - 目次の自動生成                                            │
│  - 画像の埋め込み                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 【最終出力】                                                 │
│  └─ 2_output/週報作成基礎資料.docx                          │
│     (Google Docsにアップロード可能)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. ディレクトリ構成

```
Stock/RestaurantAILab/週報/
│
├── README.md                          # 本ドキュメント
├── 分析観点.md                         # AI分析時の判断基準ドキュメント
│
├── 1_input/                           # 入力データディレクトリ
│   ├── rawdata.csv                    # 売上トランザクションデータ
│   └── reviews.csv                    # 口コミデータ
│
├── 2_output/                          # 最新週（Week 43）の出力
│   ├── analysis_results.json          # 全分析結果（構造化データ）
│   ├── weekly_sales.csv               # 週次集計データ
│   ├── category_latest.csv            # カテゴリ別最新週データ
│   ├── product_latest.csv             # 商品別最新週データ
│   ├── category_composition_trend.csv # カテゴリ構成比推移 NEW!
│   ├── product_composition_trend.csv  # 商品構成比推移 NEW!
│   ├── weekly_sales_trend.png         # 週次推移グラフ
│   ├── weekday_sales.png              # 曜日別売上グラフ
│   ├── hourly_sales.png               # 時間帯別売上グラフ
│   ├── category_composition.png       # カテゴリ構成比（円グラフ）
│   ├── category_trend.png             # カテゴリ推移（積み上げ棒グラフ）
│   ├── product_ranking.png            # 商品売上TOP20
│   ├── product_trend.png              # 商品売上構成比推移
│   ├── 週報作成基礎資料.md             # Markdownレポート
│   └── 週報作成基礎資料.docx           # Wordレポート（最終成果物）
│
├── 2_output_week42/                   # Week 42の出力（同様の構成）
│   ├── analysis_results_W42.json
│   ├── ...
│   └── 週報作成基礎資料_W42.docx
│
├── analysis_script.py                 # メイン分析スクリプト（Week 43用）
├── analysis_script_week42.py          # Week 42用分析スクリプト
├── generate_docx.py                   # Word変換スクリプト（Week 43用）
├── generate_docx_week42.py            # Word変換スクリプト（Week 42用）
└── fix_markdown_bullets.py            # Markdown箇条書き修正スクリプト
```

---

## 4. 前提条件とセットアップ

### 4.1 必要な環境

- **Python**: 3.8以上
- **OS**: Windows, macOS, Linux（本システムはWindows環境で開発）
- **エディタ**: 任意（VSCode推奨）

### 4.2 Pythonパッケージのインストール

```bash
# 基本パッケージ（事前コンパイル版を使用）
pip install --only-binary=:all: pandas numpy matplotlib seaborn

# Word変換ツール
pip install pypandoc

# Pandocのインストール（pypandoc用）
# Windows: https://pandoc.org/installing.html からインストーラーをダウンロード
# macOS: brew install pandoc
# Linux: sudo apt-get install pandoc
```

### 4.3 UTF-8エンコーディング設定（Windows）

Windowsで日本語を正しく表示するため、スクリプトの冒頭に以下を追加:

```python
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
```

---

## 5. 分析の実行方法

### 5.1 最新週（Week 43: 2025年10月25日〜31日）の分析

#### ステップ1: Python分析の実行

```bash
# プロジェクトルートから実行
cd c:\Users\auk1i\aipm_v0
python "Stock/RestaurantAILab/週報/analysis_script.py"
```

**実行内容**:
- rawdata.csvとreviews.csvを読み込み
- 2025年10月25日〜31日のデータを対象週として分析
- 2_output/ディレクトリに分析結果を出力

**出力確認**:
```bash
# JSON出力の確認
cat "Stock/RestaurantAILab/週報/2_output/analysis_results.json"

# グラフファイルの確認
ls "Stock/RestaurantAILab/週報/2_output/*.png"

# 構成比推移CSVの確認（NEW!）
head "Stock/RestaurantAILab/週報/2_output/category_composition_trend.csv"
head "Stock/RestaurantAILab/週報/2_output/product_composition_trend.csv"
```

#### ステップ2: Claudeによる自然言語分析

1. `2_output/analysis_results.json` を開く
2. Claudeに以下のプロンプトで依頼:

```
以下のJSONデータは飲食店の週次分析結果です。
分析観点.md に記載された基準に従って、週報作成基礎資料をMarkdown形式で作成してください。

また、以下のCSVファイルも参照して、構成比の推移を分析してください:
- category_composition_trend.csv: カテゴリ別構成比の時系列データ
- product_composition_trend.csv: 商品別構成比の時系列データ

[analysis_results.jsonの内容を貼り付け]
```

3. Claudeが生成したMarkdownを `2_output/週報作成基礎資料.md` として保存

#### ステップ3: Word形式への変換

```bash
python "Stock/RestaurantAILab/週報/generate_docx.py"
```

**出力**: `2_output/週報作成基礎資料.docx`

---

## 5.x 追加ツール: BFA カテゴリ別「商品売り上げランキング」HTML出力

rawdata.csv を使って、指定期間の **カテゴリ別の商品売り上げランキング**を **ダッシュボード風HTML** で出力します（PDF印刷向けのCSSも同梱）。

- **スクリプト**: `Scripts/bfa_category_product_ranking_html.py`
- **入力**: `1_input/BFA/rawdata.csv`
- **出力**: HTML（命名規則推奨: `yyyymmdd_yyyymmdd＜店舗名＞売り上げランキング.html`）

実行例（macOS / システムpython3）:

```bash
/Library/Developer/CommandLineTools/usr/bin/python3 \
  "Stock/RestaurantAILab/週報/Scripts/bfa_category_product_ranking_html.py" \
  --sales-data "Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv" \
  --start-date 2026-01-19 \
  --end-date   2026-01-25 \
  --output-dir  "Flow/202601/2026-01-27" \
  --store-name  "BARFIveArrows"
```

- `--output-dir` 指定時は、ファイル名が自動で `yyyymmdd_yyyymmdd＜店舗名＞売り上げランキング.html` になります
- 既存運用どおり `--output-html` を明示指定することも可能です（任意のファイル名で出力）

### 5.2 別の週の分析（例: Week 42）

#### 方法1: 既存スクリプトを使用

```bash
python "Stock/RestaurantAILab/週報/analysis_script_week42.py"
python "Stock/RestaurantAILab/週報/generate_docx_week42.py"
```

#### 方法2: 新しい週用にスクリプトをカスタマイズ

1. `analysis_script.py` をコピー
2. 対象日付を変更:

```python
# 分析対象週の最終日を指定
target_end_date = pd.Timestamp('2025-11-07')  # 例: Week 44
```

3. 出力ディレクトリを変更:

```python
output_dir = Path('2_output_week44')
output_dir.mkdir(exist_ok=True)
```

---

## 6. 出力ファイルの詳細

### 6.1 JSON出力（analysis_results.json）

構造化された分析結果の全データ。Claudeが読み込んで解釈します。

**主要セクション**:

```json
{
  "metadata": {
    "target_week": "2025-W43",
    "date_range": {...},
    "store_name": "Five Arrows"
  },
  "sales_analysis": {
    "weekly_trend": [...],
    "weekday_summary": {...},
    "hourly_summary": {...}
  },
  "product_analysis": {
    "category_summary": {...},
    "product_summary": {...}
  },
  "review_analysis": {...},
  "comparison": {
    "vs_previous_week": {...},
    "vs_previous_month": {...},
    "vs_previous_year": {...}
  }
}
```

### 6.2 CSV出力

#### weekly_sales.csv
週次集計データ（全週分）

| 列名 | 説明 |
|------|------|
| year_week | 年-週番号（例: 2025-W43） |
| total_sales | 週次売上合計 |
| customer_count | 週次客数 |
| avg_ticket | 客単価 |
| group_count | 組数 |

#### category_latest.csv
対象週のカテゴリ別データ

| 列名 | 説明 |
|------|------|
| category | カテゴリ名 |
| subtotal | カテゴリ別売上 |
| quantity | 販売数量 |
| 構成比 | 構成比（%） |

#### product_latest.csv
対象週の商品別データ（TOP20）

| 列名 | 説明 |
|------|------|
| menu_name | 商品名 |
| subtotal | 商品別売上 |
| quantity | 販売数量 |
| 構成比 | 構成比（%） |

#### category_composition_trend.csv（NEW!）
カテゴリ別構成比の時系列データ

| 列名 | 説明 |
|------|------|
| week | 年-週番号 |
| category1 | カテゴリ名 |
| subtotal | カテゴリ別売上 |
| quantity | 販売数量 |
| 構成比 | その週における構成比（%） |

**用途**: カテゴリごとの構成比が週ごとにどう変化しているかを時系列分析

#### product_composition_trend.csv（NEW!）
商品別構成比の時系列データ（最新週のTOP20商品）

| 列名 | 説明 |
|------|------|
| week | 年-週番号 |
| menu_name | 商品名 |
| subtotal | 商品別売上 |
| quantity | 販売数量 |
| 構成比 | その週における構成比（%） |

**用途**: 人気商品の構成比推移を追跡し、トレンドや季節性を分析

### 6.3 グラフ出力（PNG）

| ファイル名 | 内容 | サイズ |
|-----------|------|--------|
| weekly_sales_trend.png | 週次推移（売上・客数・客単価・組数） | 12×8 |
| weekday_sales.png | 曜日別売上と客数 | 12×6 |
| hourly_sales.png | 時間帯別売上 | 12×6 |
| category_composition.png | カテゴリ構成比（円グラフ） | 10×8 |
| category_trend.png | カテゴリ推移（積み上げ棒） | 14×8 |
| product_ranking.png | 商品売上TOP20（横棒） | 12×10 |
| product_trend.png | 商品構成比推移（積み上げ棒） | 14×8 |

### 6.4 Markdown/Word出力

#### 週報作成基礎資料.md
構造化されたレポート。以下のセクションで構成:

1. **エグゼクティブサマリー**
2. **売上分析**
   - 週次推移分析
   - 曜日別分析
   - 時間帯別分析
3. **商品分析**
   - カテゴリ別分析（構成比推移を含む）
   - 商品別分析（構成比推移を含む）
4. **口コミ分析**
5. **総合考察とアクションプラン**

#### 週報作成基礎資料.docx
Google Docsにアップロード可能なWord形式。
- 自動生成目次（3階層）
- 画像の埋め込み
- 箇条書きフォーマット適用済み

---

## 7. 分析観点とロジック

詳細は [`分析観点.md`](分析観点.md) を参照してください。

### 7.1 比較分析の基準

| 比較軸 | 対象期間 | 目的 |
|--------|---------|------|
| 前週比 | 1週前 | 短期的な変化の検出 |
| 前月比 | 4週前 | 月次サイクルの把握、季節性除去 |
| 前年比 | 52週前 | 年次成長率、外部環境影響 |

### 7.2 インサイト抽出の閾値

#### ポジティブな傾向
- 売上が前週比・前月比・前年比のいずれかでプラス成長
- 客単価が継続的に上昇（+10%以上）
- 前月比で回復傾向

#### 懸念事項
- 売上が複数期間で減少傾向
- 客数が大幅減少（-20%以上）
- 前週比で急激な変化（±30%以上）

#### 変化の表現基準
- 大きな変化: ±20%以上 → 「大幅に」
- 中程度: ±10-20% → 「やや」「若干」
- 小さい: ±10%未満 → 「微増」「微減」「横ばい」

### 7.3 カテゴリ・商品分析の観点

#### カテゴリ別
- 構成比トップ3を「強み」として認識
- 構成比が前週比で±5pt以上変化した場合に注目
- **構成比推移CSVを使った長期トレンド分析（NEW!）**
  - 過去8週間の構成比変化を追跡
  - 継続的な上昇・下降トレンドの検出
  - 季節性パターンの特定

#### 商品別
- TOP10商品を重点分析
- 構成比が±2pt以上変化した商品に注目
- 売上集中度（上位3商品の合計構成比）を評価
- 死に筋商品（構成比1%未満かつ減少傾向）を特定
- **商品構成比推移CSVを使った詳細分析（NEW!）**
  - 人気商品の構成比推移パターン
  - 新商品の成長速度
  - 定番商品の安定性評価

### 7.4 構成比時系列データの活用方法（NEW!）

#### 分析の目的
構成比の「推移」を見ることで、単なる売上金額の変動ではなく、商品ミックスの変化やトレンドをより正確に把握できます。

#### カテゴリ構成比推移の分析例

**データ例**（category_composition_trend.csv）:
```csv
week,category1,subtotal,quantity,構成比
2025-W35,テキーラ,95000,30,15.2
2025-W36,テキーラ,102000,32,16.1
2025-W37,テキーラ,110000,35,17.3
2025-W38,テキーラ,98000,28,16.8
```

**分析観点**:
1. **トレンドの検出**: テキーラの構成比が4週間で15.2% → 17.3%と上昇傾向
2. **変動の評価**: W38で若干下落したが、依然として高水準を維持
3. **インサイト**: テキーラカテゴリへの需要が継続的に増加。プロモーション強化や関連商品開発の機会

**分析に使えるポイント**:
- 過去4〜8週間の構成比平均を算出
- 標準偏差を計算し、安定性を評価
- 前月同週との比較で季節性を判断

#### 商品構成比推移の分析例

**データ例**（product_composition_trend.csv）:
```csv
week,menu_name,subtotal,quantity,構成比
2025-W39,ドンフリオ1942,75000,25,13.2
2025-W40,ドンフリオ1942,78000,26,13.5
2025-W41,ドンフリオ1942,82000,28,13.7
2025-W42,ドンフリオ1942,81200,29,14.3
2025-W43,ドンフリオ1942,85000,30,14.9
```

**分析観点**:
1. **成長の持続性**: 5週間連続で構成比が上昇（13.2% → 14.9%）
2. **販売数量の増加**: 数量も25個 → 30個と安定的に増加
3. **インサイト**: この商品は明確な成長トレンドにあり、看板商品として確立されつつある

**週報での記載例**:
```markdown
### 商品別構成比推移分析

**ドンフリオ1942の継続的成長**
- 過去5週間で構成比が13.2%から14.9%へ+1.7pt上昇
- 週平均+0.4ptのペースで成長を継続
- 販売数量も安定的に増加（25個 → 30個）
- **インサイト**: 看板商品として確立。バリエーション展開や関連商品の訴求が有効
```

#### 時系列分析のベストプラクティス

1. **最低4週間のデータを参照**
   - 1〜2週間だけでは偶然の変動か本当のトレンドか判断できない
   - 4〜8週間のデータで信頼性の高い分析が可能

2. **絶対値と相対値の両方を見る**
   - 構成比（相対値）: 商品ミックスの変化を把握
   - 売上金額（絶対値）: 実際のビジネスインパクトを評価

3. **季節性を考慮する**
   - 前年同週のデータがあれば必ず参照
   - 特定の季節にのみ人気の商品は、年次比較が重要

4. **複数商品の連動を見る**
   - A商品の構成比が下がり、B商品が上がっている → 顧客嗜好の変化
   - 全体的に特定カテゴリが上昇 → カテゴリ全体のトレンド

---

## 8. トラブルシューティング

### 8.1 よくある問題と解決方法

#### 問題1: pandasインストールエラー（Visual Studio関連）

**エラー**: `error: Microsoft Visual C++ 14.0 or greater is required`

**解決策**:
```bash
pip install --only-binary=:all: pandas numpy matplotlib seaborn
```

#### 問題2: 日本語が文字化けする（Windows）

**症状**: コンソール出力が文字化け

**解決策**: スクリプトの冒頭に追加
```python
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
```

#### 問題3: Word変換後、箇条書きが正しく表示されない

**症状**: インサイトの箇条書きが改行のない本文になる

**解決策**:
1. 絵文字見出しの後に空行を追加
2. 絵文字を太字の内側に配置

```markdown
# 修正前
✅ **ポジティブな傾向**
- 客単価が上昇

# 修正後
**✅ ポジティブな傾向**

- 客単価が上昇
```

修正スクリプト: `fix_markdown_bullets.py`

#### 問題4: pypandoc実行時にPandocが見つからない

**エラー**: `Pandoc not found`

**解決策**: Pandocを個別にインストール
```bash
# Windows: https://pandoc.org/installing.html
# macOS:
brew install pandoc
# Linux:
sudo apt-get install pandoc
```

#### 問題5: スクリプト実行時のパスエラー

**エラー**: `FileNotFoundError: [Errno 2] No such file or directory`

**解決策**: プロジェクトルートから実行
```bash
# 現在のディレクトリを確認
pwd
# c:\Users\auk1i\aipm_v0 であることを確認

# スクリプトを実行
python "Stock/RestaurantAILab/週報/analysis_script.py"
```

### 8.2 データエラーのデバッグ

#### 週番号が正しく生成されない

**確認事項**:
```python
# スクリプト内で週番号の生成を確認
sales_df['year_week'] = sales_df['sales_date'].dt.strftime('%Y-W%U')
print(sales_df['year_week'].unique())
```

#### 対象週のデータが空になる

**原因**: 指定した日付範囲にデータが存在しない

**確認方法**:
```python
print(f"データ期間: {sales_df['sales_date'].min()} ～ {sales_df['sales_date'].max()}")
print(f"対象週: {target_week}")
```

---

## 9. 更新履歴

### v1.4 (2025-12-28)
- **READMEの拡充**
  - セクション7.4「構成比時系列データの活用方法」を追加
  - 具体的な分析例とベストプラクティスを記載
  - 週報での記載例を提示
- **Week 42スクリプトの更新**
  - 商品別分析機能を追加
  - 構成比時系列データ出力機能を追加
  - Week 43スクリプトと同じ機能セットに統一

### v1.3 (2025-12-28)
- **構成比推移分析機能の追加**
  - `category_composition_trend.csv`: カテゴリ別構成比の時系列データ
  - `product_composition_trend.csv`: 商品別構成比の時系列データ（TOP20）
- **自然言語分析の強化**
  - 構成比の長期トレンド分析が可能に
  - 季節性パターンの検出
  - 商品人気の継続性評価
- README.mdの全面改訂（本ドキュメント）

### v1.2 (2025-12-27)
- 商品別分析機能の追加
- product_ranking.png, product_trend.png, product_latest.csvの生成
- 分析観点.mdの更新（商品別分析観点の追加）

### v1.1 (2025-12-27)
- Week 42の分析対応
- Word形式での出力対応
- 箇条書きフォーマットの修正

### v1.0 (2025-12-27)
- 初版システムの完成
- 基本的な売上分析機能
- カテゴリ別分析
- 口コミ分析

---

## 付録: 主要スクリプトの役割

### analysis_script.py
- **役割**: Python分析のメインスクリプト
- **入力**: rawdata.csv, reviews.csv
- **出力**: JSON, CSV（9種類）, PNG（7種類）
- **処理**:
  1. データクレンジング
  2. 週次集計
  3. 比較分析（前週、前月、前年）
  4. 構成比時系列データ生成（NEW!）
  5. 可視化
  6. 構造化データ出力

### 分析観点.md
- **役割**: AI分析時の判断基準ドキュメント
- **内容**:
  - インサイト抽出の閾値
  - 表現のトーン
  - アクションプラン策定基準
  - 分析の再現性確保

### generate_docx.py
- **役割**: Markdown→Word変換
- **使用ツール**: pypandoc
- **オプション**:
  - 目次自動生成（3階層）
  - 画像埋め込み
  - スタンドアロンドキュメント

### fix_markdown_bullets.py
- **役割**: Markdownの箇条書きフォーマット修正
- **修正内容**:
  - 絵文字見出し後の空行追加
  - 絵文字の太字内配置

---

## 使用例: 完全なワークフロー

```bash
# 1. プロジェクトルートに移動
cd c:\Users\auk1i\aipm_v0

# 2. Python分析を実行
python "Stock/RestaurantAILab/週報/analysis_script.py"

# 3. 出力ファイルの確認
ls "Stock/RestaurantAILab/週報/2_output/"

# 4. Claude AIによる分析（対話的）
# - analysis_results.jsonを開く
# - category_composition_trend.csvを確認
# - product_composition_trend.csvを確認
# - Claudeに分析を依頼
# - 生成されたMarkdownを保存

# 5. Word形式に変換
python "Stock/RestaurantAILab/週報/generate_docx.py"

# 6. 最終成果物を確認
start "Stock/RestaurantAILab/週報/2_output/週報作成基礎資料.docx"
```

---

**このREADMEは、週報作成システムの完全な運用ガイドです。新しい機能追加や改善があれば、随時更新してください。**

**質問・フィードバック**: このシステムに関する質問や改善提案があれば、プロジェクトメンバーにご連絡ください。


