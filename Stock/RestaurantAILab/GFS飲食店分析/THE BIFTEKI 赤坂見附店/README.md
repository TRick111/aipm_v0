# THE BIFTEKI 赤坂見附店 売上分析

## 概要

POSデータを用いた売上分析。ピークタイムの処理能力、滞在時間、売上に影響する要因などを可視化・分析した。

---

## フォルダ構成

```
THE BIFTEKI 赤坂見附店/
├── README.md              # 本ファイル
├── data/
│   ├── input/             # 元データ（POSエクスポートCSV 9ファイル）
│   ├── intermediate/      # 中間加工データ
│   └── output/            # 分析結果データ
├── scripts/
│   ├── 01_data_prep/      # データ準備スクリプト
│   ├── 02_duration/       # 滞在時間分析
│   ├── 03_peak/           # ピーク分析
│   ├── 04_sales_factor/   # 売上要因分析
│   └── 05_y2y/            # 前年比分析
├── charts/
│   ├── duration/          # 滞在時間グラフ
│   ├── peak/              # ピーク分析グラフ
│   ├── sales_factor/      # 売上要因グラフ
│   └── y2y/               # 前年比グラフ
└── reports/               # レポート類
```

---

## データ処理フロー

### 1. データ準備 (`scripts/01_data_prep/`)

| ファイル | 説明 | スクリプト |
|---|---|---|
| `data/input/*.csv` | POSから分割出力された元データ（9ファイル） | - |
| `data/intermediate/merged_pos_data.csv` | 統合されたPOSデータ | `merge_pos_csv.py` |
| `data/intermediate/transformed_pos_data.csv` | 商品コード/商品名分割、ベース価格追加 | `transform_pos_data.py` |
| `data/intermediate/transformed_pos_data_eatin.csv` | Eat Inデータのみ抽出 | `split_by_category.py` |
| `data/intermediate/transformed_pos_data_takeout.csv` | Take Outデータのみ抽出 | `split_by_category.py` |
| `data/intermediate/visits_with_duration.csv` | 伝票単位の滞在時間データ | `analyze_turnover.py` |
| `data/intermediate/occupancy_10min.csv` | 10分刻みの店内人数データ | `analyze_turnover.py` |

---

## 分析結果一覧

### 📊 滞在時間分析 (`charts/duration/`)

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `duration_histogram.png` | 滞在時間のヒストグラム（120分以下）と曜日別箱ひげ図。平均滞在時間は約25〜30分。 | `02_duration/plot_duration_histogram.py` |
| `duration_by_hour_weekday.png` | 入店時刻別の平均滞在時間（曜日別折れ線）。ディナー帯の滞在時間がランチより長い。 | `02_duration/plot_duration_by_hour.py` |

### 📊 ピークタイム処理能力分析 (`charts/peak/`)

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `occupancy_timeseries_weekday.png` | 曜日別の店内人数推移（10分刻み）。ランチピークは12時台、ディナーピークは19-20時台。 | `03_peak/plot_peak_analysis.py` |
| `hourly_visits_occupancy_split.png` | 平日/土日別の時間帯別来店組数（棒）と店内人数（折れ線）の複合グラフ。 | `03_peak/plot_peak_analysis_weekday_weekend.py` |
| `peak_visits_vs_sales.png` | ピーク時来店組数と1日売上の散布図（平日/土日別）。正の相関あり。 | `03_peak/analyze_peak_vs_sales.py` |
| `split_cause_analysis.png` | 平日の2群分離の原因分析。ディナー組数で色分け。 | `03_peak/analyze_split_cause.py` |
| `sales_factor_exploration.png` | 売上との相関が高い要因TOP6の散布図（平日のみ）。 | `03_peak/explore_sales_factors.py` |
| `sales_factor_exploration_平日.png` | 平日データのみで売上との相関TOP6を散布図化。 | `03_peak/explore_sales_factors_split.py` |
| `sales_factor_exploration_土日.png` | 土日データのみで売上との相関TOP6を散布図化。 | `03_peak/explore_sales_factors_split.py` |
| `sales_2d_separation.png` | 2軸での売上上位/下位の分布（平日）。 | `03_peak/explore_sales_factors.py` |
| `sales_2d_separation_平日.png` | 平日の2軸分布図。 | `03_peak/explore_sales_factors_split.py` |
| `sales_2d_separation_土日.png` | 土日の2軸分布図。 | `03_peak/explore_sales_factors_split.py` |
| `spend_customers_by_time_split.png` | 入店時間帯別の客数（棒）と客単価（折れ線）。 | `03_peak/plot_spend_customers_by_time.py` |

### 📊 売上要因分析 (`charts/sales_factor/`)

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `01_eda_basic.png` | 基本EDA | `04_sales_factor/sales_factor_analysis.py` |
| `02_correlation_heatmap.png` | 相関ヒートマップ | `04_sales_factor/sales_factor_analysis.py` |
| `03_high_low_comparison.png` | 高/低売上日の比較 | `04_sales_factor/sales_factor_analysis.py` |
| `04_cluster_optimization.png` | クラスタ最適化 | `04_sales_factor/sales_factor_analysis.py` |
| `05_cluster_pca.png` | PCAによるクラスタ可視化 | `04_sales_factor/sales_factor_analysis.py` |
| `06_cluster_radar.png` | クラスタ別レーダーチャート | `04_sales_factor/sales_factor_analysis.py` |
| `07_feature_importance.png` | 特徴量重要度 | `04_sales_factor/sales_factor_analysis.py` |
| `08_top_features_scatter.png` | 重要特徴量の散布図 | `04_sales_factor/sales_factor_analysis.py` |

### 📊 前年比分析 (`charts/y2y/`)

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `monthly_trends.png` | 月別トレンド | `05_y2y/y2y_analysis.py` |
| `monthly_trends_normalized.png` | 月別トレンド（正規化） | `05_y2y/y2y_analysis.py` |
| `sales_decomposition.png` | 売上要因分解 | `05_y2y/y2y_analysis.py` |
| `sales_decomposition_normalized.png` | 売上要因分解（正規化） | `05_y2y/y2y_analysis.py` |
| `sales_decomposition_yoy.png` | YoY売上要因分解 | `05_y2y/y2y_analysis.py` |
| `sales_decomposition_yoy_normalized.png` | YoY売上要因分解（正規化） | `05_y2y/y2y_analysis.py` |
| `y2y_comparison.png` | 前年比較 | `05_y2y/y2y_analysis.py` |
| `y2y_comparison_normalized.png` | 前年比較（正規化） | `05_y2y/y2y_analysis.py` |

---

## 主な分析結果サマリー

### 売上との相関係数（平日 vs 土日）

| 要因 | 平日 | 土日 |
|---|:---:|:---:|
| ディナー組数 | **0.926** | 0.891 |
| 総来店客数 | 0.911 | **0.961** |
| 総来店組数 | 0.865 | 0.953 |
| ランチ組数 | 0.654 | 0.861 |
| 客単価 | 0.677 | 0.822 |
| 組単価 | 0.619 | 0.774 |
| ピーク店内人数 | 0.388 | 0.765 |
| 平均滞在時間 | -0.079 | -0.026 |

### 主要インサイト

1. **平日の売上を決めるのはディナー来店数**
   - ランチは来店数が多いが低単価（薄利多売）
   - ディナー組数との相関が0.926と非常に強い

2. **土日は終日の来店数が売上を決める**
   - ランチ・ディナー両方の来店数が効く
   - 総来店客数との相関が0.961

3. **滞在時間は売上と相関しない**
   - 平日・土日とも相関係数は約0（-0.08〜-0.03）
   - 回転率向上より来店数増加が重要

4. **ランチピーク時の店内人数がディナーより多い理由**
   - ランチは滞在時間が短いが、来店数が圧倒的に多い
   - リトルの法則：店内人数 ≒ 来店率 × 滞在時間

5. **客数と客単価は負の関係**
   - 客数が多い時間帯（ランチ）ほど客単価が低い
   - 平日ランチ：約1,300円、ディナー：約1,550円

---

## レポート (`reports/`)

| ファイル | 内容 |
|---|---|
| `sales_factor_analysis_summary.md` | 売上要因分析の詳細サマリー |
| `y2y_analysis_report.md` | 前年比分析レポート（Markdown） |
| `y2y_analysis_report.html` | 前年比分析レポート（HTML） |
| `THE BIFTEKI 赤坂見附店 売上分析レポート — aipm_v0.pdf` | 最終PDFレポート |
| `slidedraft/2026-01-28/スライド構成_ドラフト.md` | スライド作成用の構成ドラフト（画像埋め込み済み） |

---

## スクリプト → 出力ファイル対応表

各スクリプトが生成するデータファイル・画像の一覧。

### `scripts/01_data_prep/` データ準備

| スクリプト | 出力ファイル |
|---|---|
| `merge_pos_csv.py` | `data/intermediate/merged_pos_data.csv` |
| `transform_pos_data.py` | `data/intermediate/transformed_pos_data.csv` |
| `split_by_category.py` | `data/intermediate/transformed_pos_data_eatin.csv`<br>`data/intermediate/transformed_pos_data_takeout.csv` |

### `scripts/02_duration/` 滞在時間分析

| スクリプト | 出力ファイル |
|---|---|
| `analyze_turnover.py` | `data/intermediate/visits_with_duration.csv`<br>`data/intermediate/occupancy_10min.csv` |
| `plot_duration_histogram.py` | `charts/duration/duration_histogram.png` |
| `plot_duration_by_hour.py` | `charts/duration/duration_by_hour_weekday.png` |

### `scripts/03_peak/` ピーク分析

| スクリプト | 出力ファイル |
|---|---|
| `plot_peak_analysis.py` | `charts/peak/occupancy_timeseries_weekday.png` |
| `plot_peak_analysis_weekday_weekend.py` | `charts/peak/hourly_visits_occupancy_split.png` |
| `analyze_peak_vs_sales.py` | `charts/peak/peak_visits_vs_sales.png` |
| `analyze_split_cause.py` | `charts/peak/split_cause_analysis.png` |
| `explore_sales_factors.py` | `charts/peak/sales_factor_exploration.png`<br>`charts/peak/sales_2d_separation.png` |
| `explore_sales_factors_split.py` | `charts/peak/sales_factor_exploration_平日.png`<br>`charts/peak/sales_factor_exploration_土日.png`<br>`charts/peak/sales_2d_separation_平日.png`<br>`charts/peak/sales_2d_separation_土日.png` |
| `plot_spend_by_time.py` | （グラフ出力） |
| `plot_spend_customers_by_time.py` | `charts/peak/spend_customers_by_time_split.png` |

### `scripts/04_sales_factor/` 売上要因分析

| スクリプト | 出力ファイル |
|---|---|
| `sales_factor_analysis.py` | `charts/sales_factor/01_eda_basic.png`<br>`charts/sales_factor/02_correlation_heatmap.png`<br>`charts/sales_factor/03_high_low_comparison.png`<br>`charts/sales_factor/04_cluster_optimization.png`<br>`charts/sales_factor/05_cluster_pca.png`<br>`charts/sales_factor/06_cluster_radar.png`<br>`charts/sales_factor/07_feature_importance.png`<br>`charts/sales_factor/08_top_features_scatter.png`<br>`data/output/daily_summary.csv`<br>`data/output/daily_summary_with_cluster.csv`<br>`reports/sales_factor_analysis_summary.md` |
| `analyze_peak_reason.py` | （分析用補助スクリプト） |

### `scripts/05_y2y/` 前年比分析

| スクリプト | 出力ファイル |
|---|---|
| `y2y_analysis.py` | `charts/y2y/monthly_trends.png`<br>`charts/y2y/monthly_trends_normalized.png`<br>`charts/y2y/sales_decomposition.png`<br>`charts/y2y/sales_decomposition_normalized.png`<br>`charts/y2y/sales_decomposition_yoy.png`<br>`charts/y2y/sales_decomposition_yoy_normalized.png`<br>`charts/y2y/y2y_comparison.png`<br>`charts/y2y/y2y_comparison_normalized.png`<br>`data/output/monthly_stats.csv`<br>`data/output/sales_decomposition.csv`<br>`data/output/sales_decomposition_normalized.csv`<br>`reports/y2y_analysis_report.md` |
| `convert_to_html.py` | `reports/y2y_analysis_report.html` |
| `convert_to_pdf.py` | （PDF変換用） |

#### スライド素材（画像分割）
スライド用途で「複数グラフが1枚になっている画像」を分割して使いたい場合は、以下のフラグを利用する。

- **`--split-assets`**: 分割を有効化（デフォルトOFF）
- **`--assets-dir`**: 分割素材の出力先（例: `Flow/.../THEBIFTEKI赤坂見附スライド/assets/`）

対象スクリプト（現状）:
- `scripts/05_y2y/y2y_analysis.py`（4段の複合図 → 4分割）
- `scripts/09_interim_report/generate_graphs.py`（左右2分割、2x2分割）
- `scripts/08_segment/high_low_analysis.py`（2行x3列 → 列ごとに切り出し）

---

## 作成日

2026-01-21
