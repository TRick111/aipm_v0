# 生成AI × データ分析フロー（Python → 示唆 → グラフ → スライド）概要

**作成日**: 2026-01-30  
**目的**: 「初めてこの話を聞いた人」でも、**どういう順番で何を作れば、精度高く“示唆→説明資料”まで辿り着けるか**が分かるようにする。  
（※分析手法の細部はここでは触れない）

---

## 1. まず結論（重要）
- **示唆生成の入力は、グラフ画像より“構造化データ（集計表）”が基本的に強い**
  - 画像だと、LLMが「軸・単位・母数・集計条件」を誤読/復元ミスしやすい
- **Pythonは“事実（数値）を確定する”役、LLMは“解釈と説明”に寄せると精度が出る**
  - 「計算」はPythonで固定  
  - 「主張・言い回し・スライド構成」はLLMで支援

---

## 2. 推奨パイプライン（01〜05）
ここでは **01〜05** のステップに分けて、各ステップの **Input / Process / Output** を整理します。

### 01. Ingest & Normalize（取り込み・正規化）
**Input**
- 生データ（例: POSのCSV複数ファイル）
- ルール（例: EAT INのみ、期間A/B、外れ値除外など）

**Process（例）**
- 複数CSVの統合（メタ行スキップ、ヘッダ差異吸収、列順統一）
- 型変換（日付・数値・カテゴリ）
- 重複排除（伝票単位など）
- EAT IN抽出（カテゴリ1/2の逆転なども正規化）

**Output（例）**
- `data/normalized/tickets.csv`（伝票=1行）
- `data/normalized/transactions_line.csv`（明細=1行）
- `data/metadata/data_dictionary.json`（列の意味・単位・定義）
- `data/metadata/quality_report.json`（件数/期間/欠損など）

---

### 02. Build Facts（示唆の材料になる“集計表”を作る）
**Input**
- `data/normalized/*`
- 期間A/Bや時間帯定義などのルール

**Process（例）**
- 月次/日次/曜日/時間帯/カテゴリ別など、説明に使う観点で集計
- 前年同月比（YoY）、A/B比較、差分・増減率を作る

**Output（例）**
- `data/facts/facts_monthly.csv`（売上/客数/組数/客単価 + 営業日あたり）
- `data/facts/facts_yoy_monthly.csv`（前年差/前年比%）
- `data/facts/facts_time_contrib.csv`（時間帯別の増減寄与）
- `data/facts/facts_price_percentile.csv`（価格帯/分位別の変化）
- `data/facts/facts_menu_contrib.csv`（カテゴリ/メニュー別の増減）

---

### 03. Evidence Pack & Chart Catalog（根拠パック＋作れるグラフ定義を確定）
**ねらい**: 04（LLM）が「推測」ではなく「参照」で話せる状態にする。

**Input**
- `data/facts/*`

**Process（例）**
- “主張の根拠になる数値”をまとめる（増減・寄与・主要指標など）
- **生成可能なグラフ（全候補）をID付きで定義する**
  - LLMが「どのグラフを使うか」を **IDで選べる**ようにする

**Output（例）**
- `analysis/insights_facts.json`
  - 主要数値、参照すべき表、注意点（母数/例外）を格納
- `analysis/chart_catalog.json`
  - 例: `y2y_sales_per_day` / `yoy_customers_delta` / `decomposition` など  
  - それぞれに「入力facts」「描画仕様」「出力パス」を紐付ける

---

### 04. Insight Generation（LLM：主張・根拠・使うグラフIDを決める）
**Input**
- `analysis/insights_facts.json`
- `analysis/chart_catalog.json`
- `analysis/constraints.md`（因果断定禁止などのガードレール）

**Process（例）**
- 1スライド=1主張、に合わせて
  - 主張（何を言うか）
  - 根拠（どの数値を引用するか）
  - 使うグラフ（chart_id）  
  を決める
- 出力はまず **JSON** で固定（ブレ防止）

**Output（例）**
- `analysis/insights.json`
  - `slides[] = { claim, evidence_refs, chart_ids, caveats }`
- `analysis/insights.md`（任意：人が読む文章版）

---

### 05. Chart & Slide Materialization（Python：必要なグラフだけ生成→資料化）
**Input**
- `analysis/insights.json`（使う `chart_ids` のリスト）
- `analysis/chart_catalog.json`
- `data/facts/*`

**Process（例）**
- `chart_ids` だけを描画して `assets/` に出す（＝無駄なグラフを作らない）
- スライド用に分割・切り出し（4分割/2分割など）
- スライド構成Markdown（またはMarp）を出力

**Output（例）**
- `slides/assets/*.png`（使う分だけ）
- `slides/スライド構成_ドラフト.md`

---

## 3. THE BIFTEKI（川崎店）の例（このリポジトリでの実例）
今回の作業では、上記の考え方を “Python中心のパイプライン” として回しています。

### 例：パイプラインの入口
- `Flow/202601/2026-01-28/GFS飲食店分析/THEBIFTEKI川崎店/scripts/run_pipeline.py`
  - 生CSV → 正規化/集計 → グラフ出力 → 中間レポート（Markdown）までを一括実行

### 例：人に説明する成果物（グラフ・レポート）
- 中間レポート（Markdown）
  - `Flow/202601/2026-01-28/GFS飲食店分析/THEBIFTEKI川崎店/reports/THE_BIFTEKI_川崎店_売上分析中間レポート.md`
- 図表（PNG）
  - `Flow/202601/2026-01-28/GFS飲食店分析/THEBIFTEKI川崎店/reports/*.png`
  - `Flow/202601/2026-01-28/GFS飲食店分析/THEBIFTEKI川崎店/charts/y2y/*.png`

### 例：スライド化（1枚=1主張+1グラフ）
- スライド構成ドラフト
  - `Flow/202601/2026-01-28/GFS飲食店分析/THEBIFTEKI川崎スライド/スライド構成_ドラフト.md`
- スライド素材（assets）
  - `Flow/202601/2026-01-28/GFS飲食店分析/THEBIFTEKI川崎スライド/assets/`

---

## 4. 運用のコツ（最低限）
- **LLMに渡すのは「集計表（facts）+ 定義 + 注意点」**
- **LLMは “作れるグラフID” を選ぶだけ**（勝手に新しいグラフを発明させない）
- **スライドは「1枚=1主張」**に固定すると、示唆がブレにくい

