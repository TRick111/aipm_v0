# THE BIFTEKI 赤坂見附店 売上分析レポート

## 概要

POSデータを用いた売上分析。ピークタイムの処理能力、滞在時間、売上に影響する要因などを可視化・分析した。

---

## データ処理フロー

### 1. データ準備

| ファイル | 説明 | スクリプト |
|---|---|---|
| `input/*.csv` | POSから分割出力された元データ（9ファイル） | - |
| `merged_pos_data.csv` | 統合されたPOSデータ | `merge_pos_csv.py` |
| `transformed_pos_data.csv` | 商品コード/商品名分割、ベース価格追加 | `transform_pos_data.py` |
| `transformed_pos_data_eatin.csv` | Eat Inデータのみ抽出 | `split_by_category.py` |
| `transformed_pos_data_takeout.csv` | Take Outデータのみ抽出 | `split_by_category.py` |
| `StayTimeAnalysis/visits_with_duration.csv` | 伝票単位の滞在時間データ | `StayTimeAnalysis/analyze_turnover.py` |
| `StayTimeAnalysis/occupancy_10min.csv` | 10分刻みの店内人数データ | `StayTimeAnalysis/analyze_turnover.py` |

---

## 分析結果一覧

### 📊 滞在時間分析

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `StayTimeAnalysis/duration_histogram.png` | 滞在時間のヒストグラム（120分以下）と曜日別箱ひげ図。平均滞在時間は約25〜30分。 | `StayTimeAnalysis/plot_duration_histogram.py` |
| `StayTimeAnalysis/duration_by_hour_weekday.png` | 入店時刻別の平均滞在時間（曜日別折れ線）。ディナー帯の滞在時間がランチより長い。 | `StayTimeAnalysis/plot_duration_by_hour.py` |

### 📊 ピークタイム処理能力分析

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `PeakAnalysis/occupancy_timeseries_weekday.png` | 曜日別の店内人数推移（10分刻み）。ランチピークは12時台、ディナーピークは19-20時台。 | `PeakAnalysis/plot_peak_analysis.py` |
| `PeakAnalysis/hourly_visits_occupancy_split.png` | 平日/土日別の時間帯別来店組数（棒）と店内人数（折れ線）の複合グラフ。ランチのほうが店内人数が多い理由＝来店数が多いため（リトルの法則）。 | `PeakAnalysis/plot_peak_analysis_weekday_weekend.py` |

### 📊 ピーク来店数 vs 売上分析（PeakAnalysisフォルダ）

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `PeakAnalysis/peak_visits_vs_sales.png` | ピーク時来店組数と1日売上の散布図（平日/土日別）。正の相関あり。平日は2群に分かれる傾向。 | `PeakAnalysis/analyze_peak_vs_sales.py` |
| `PeakAnalysis/split_cause_analysis.png` | 平日の2群分離の原因分析。ディナー組数で色分けし、ディナー来店が売上を決定づけることを可視化。 | `PeakAnalysis/analyze_split_cause.py` |

### 📊 売上要因探索（PeakAnalysisフォルダ）

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `PeakAnalysis/sales_factor_exploration.png` | 売上との相関が高い要因TOP6の散布図（平日のみ）。ディナー組数が最も相関が高い（r=0.926）。 | `PeakAnalysis/explore_sales_factors.py` |
| `PeakAnalysis/sales_factor_exploration_平日.png` | 平日データのみで売上との相関TOP6を散布図化。 | `PeakAnalysis/explore_sales_factors_split.py` |
| `PeakAnalysis/sales_factor_exploration_土日.png` | 土日データのみで売上との相関TOP6を散布図化。土日は総来店客数が最も相関が高い（r=0.961）。 | `PeakAnalysis/explore_sales_factors_split.py` |
| `PeakAnalysis/sales_2d_separation.png` | 2軸での売上上位/下位の分布（平日）。ランチ×ディナー、総来店×組単価など。 | `PeakAnalysis/explore_sales_factors.py` |
| `PeakAnalysis/sales_2d_separation_平日.png` | 平日の2軸分布図。売上上位日はディナー組数が多い傾向が明確。 | `PeakAnalysis/explore_sales_factors_split.py` |
| `PeakAnalysis/sales_2d_separation_土日.png` | 土日の2軸分布図。平日ほど明確な分離は見られない。 | `PeakAnalysis/explore_sales_factors_split.py` |

### 📊 客単価分析（PeakAnalysisフォルダ）

| 画像 | 分析内容 | スクリプト |
|---|---|---|
| `PeakAnalysis/spend_by_time_15min.png` | 入店時間帯別の客単価推移（15分刻み、平日/土日折れ線）。ランチは低単価、ディナーは高単価。 | `PeakAnalysis/plot_spend_by_time.py` |
| `PeakAnalysis/spend_customers_by_time_split.png` | 入店時間帯別の客数（棒）と客単価（折れ線）を平日/土日で並べた複合グラフ。客数と客単価の負の関係を可視化。 | `PeakAnalysis/plot_spend_customers_by_time.py` |

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

## フォルダ構成

```
Flow/202601/2026-01-21/
├── README_sales_analysis.md    # 本ファイル
├── input/                      # 元データ（POSエクスポート）
├── merge_pos_csv.py            # データ統合
├── merged_pos_data.csv         # 統合データ
├── transform_pos_data.py       # データ変換
├── transformed_pos_data.csv    # 変換済みデータ
├── split_by_category.py        # EatIn/TakeOut分割
├── transformed_pos_data_eatin.csv
├── transformed_pos_data_takeout.csv
├── StayTimeAnalysis/           # 滞在時間分析
│   ├── analyze_turnover.py     # 滞在時間・店内人数計算
│   ├── visits_with_duration.csv # 伝票単位滞在時間
│   ├── occupancy_10min.csv     # 10分刻み店内人数
│   ├── plot_duration_histogram.py
│   ├── duration_histogram.png
│   ├── plot_duration_by_hour.py
│   └── duration_by_hour_weekday.png
├── PeakAnalysis/               # ピークタイム分析
│   ├── plot_peak_analysis.py
│   ├── occupancy_timeseries_weekday.png
│   ├── plot_peak_analysis_weekday_weekend.py
│   ├── hourly_visits_occupancy_split.png
│   ├── analyze_peak_reason.py
│   ├── analyze_peak_vs_sales.py
│   ├── peak_visits_vs_sales.png
│   ├── analyze_split_cause.py
│   ├── split_cause_analysis.png
│   ├── explore_sales_factors.py
│   ├── sales_factor_exploration.png
│   ├── sales_2d_separation.png
│   ├── explore_sales_factors_split.py
│   ├── sales_factor_exploration_平日.png
│   ├── sales_factor_exploration_土日.png
│   ├── sales_2d_separation_平日.png
│   ├── sales_2d_separation_土日.png
│   ├── plot_spend_by_time.py
│   ├── spend_by_time_15min.png
│   ├── plot_spend_customers_by_time.py
│   └── spend_customers_by_time_split.png
└── SalesFactorAnalysis/        # 売上要因分析
    └── sales_factor_analysis.py
```

---

## 作成日

2026-01-21
