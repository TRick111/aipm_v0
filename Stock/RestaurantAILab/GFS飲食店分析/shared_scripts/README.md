# GFS飲食店分析 - shared scripts

## 目的
複数店舗で共通利用できる分析スクリプト群（元: `THE BIFTEKI 赤坂見附店/scripts/`）。

各スクリプトは **店舗ディレクトリ（store-root）** を引数で受け取り、店舗ごとの
`data/` `charts/` `reports/` に出力する形に寄せていく。

## 想定する店舗ディレクトリ構造（例）
```
<store-root>/
  data/
    intermediate/
      transformed_pos_data_eatin.csv
    output/
  charts/
    duration/
    peak/
    sales_factor/
    y2y/
  reports/
```

## 実行方針（推奨）
- 店舗ごとに Flow で作業し、`<store-root>/data/intermediate/transformed_pos_data_eatin.csv` を用意
- `python3` で shared scripts を呼び出す（店舗ごとに `--store-root` を渡す）
- 生成物を確認後、Stockへ確定反映

## スライド素材（画像分割）の作り方
「1枚の画像に複数グラフが入っている」図を、スライド用に **1グラフ=1画像**で使いたい場合は
`--split-assets` を付けて実行する。

- **デフォルト**: 分割はしない（従来互換）
- **出力先**: `--assets-dir` で指定（未指定の場合は `<out_dir>/_slide_assets/` などに出力）

### 例（THE BIFTEKI 赤坂見附店）
（スライド作業フォルダの `assets/` にまとめて出力したいケース）

```bash
# 2-3 / 2-2 など（4段の複合図）を4分割
python3 "Stock/RestaurantAILab/GFS飲食店分析/shared_scripts/scripts/05_y2y/y2y_analysis.py" \
  --store-root "Stock/RestaurantAILab/GFS飲食店分析/THE BIFTEKI 赤坂見附店" \
  --out-dir    "Stock/RestaurantAILab/GFS飲食店分析/THE BIFTEKI 赤坂見附店/charts/y2y" \
  --split-assets \
  --assets-dir "Flow/YYYYMM/YYYY-MM-DD/GFS飲食店分析/<slide-work>/assets"

# 4.5（左右2グラフ）/ 6-1（2x2）などを分割
python3 "Stock/RestaurantAILab/GFS飲食店分析/shared_scripts/scripts/09_interim_report/generate_graphs.py" \
  --store-root "Stock/RestaurantAILab/GFS飲食店分析/THE BIFTEKI 赤坂見附店" \
  --out-dir    "Stock/RestaurantAILab/GFS飲食店分析/THE BIFTEKI 赤坂見附店/reports" \
  --split-assets \
  --assets-dir "Flow/YYYYMM/YYYY-MM-DD/GFS飲食店分析/<slide-work>/assets"

# 6-4（2行x3列）を列ごとに切り出し
python3 "Stock/RestaurantAILab/GFS飲食店分析/shared_scripts/scripts/08_segment/high_low_analysis.py" \
  --store-root "Stock/RestaurantAILab/GFS飲食店分析/THE BIFTEKI 赤坂見附店" \
  --out-dir    "Stock/RestaurantAILab/GFS飲食店分析/THE BIFTEKI 赤坂見附店/reports/HighLowAnalysis" \
  --split-assets \
  --assets-dir "Flow/YYYYMM/YYYY-MM-DD/GFS飲食店分析/<slide-work>/assets"
```

## 中間レポート（章別）: グラフ → 生成スクリプト対応表
`THE_BIFTEKI_赤坂見附店_売上分析中間レポート.md` に登場する **各グラフ**について、
「どのスクリプトで生成されたか」を整理。

- **出力パス**: `store-root/` からの相対パス（= レポートで参照している実ファイル想定）
- **生成スクリプト**: この `shared_scripts/` 配下の相対パス

| 章 | 図（レポート内の表記） | 出力パス（store-root相対） | 生成スクリプト（shared_scripts相対） |
|---|---|---|---|
| 2. 売上の全体推移 | 月別推移（営業日あたり） | `charts/y2y/monthly_trends_normalized.png` | `scripts/05_y2y/y2y_analysis.py` |
| 2. 売上の全体推移 | 年比較（営業日あたり） | `charts/y2y/y2y_comparison_normalized.png` | `scripts/05_y2y/y2y_analysis.py` |
| 3. 客数の部 | 月別比較グラフ | `reports/graph01_monthly_comparison.png` | `scripts/09_interim_report/generate_graphs.py` |
| 3. 客数の部 | 前年比増減グラフ | `reports/graph02_yoy_change.png` | `scripts/09_interim_report/generate_graphs.py` |
| 3. 客数の部 | 時間帯別寄与度 | `reports/graph10_time_contribution.png` | `scripts/09_interim_report/generate_graphs.py` |
| 3. 客数の部 | 時間帯別ヒートマップ | `reports/graph09_time_heatmap.png` | `scripts/09_interim_report/generate_graphs.py` |
| 3. 客数の部 | 曜日別ヒートマップ | `reports/graph11_weekday_heatmap.png` | `scripts/09_interim_report/generate_graphs.py` |
| 3. 客数の部 | 平日vs土日比較 | `reports/graph12_weekday_vs_weekend.png` | `scripts/09_interim_report/generate_graphs.py` |
| 4. 客単価の部 | 要因分解 | `reports/01_decomposition_analysis.png` | `scripts/07_customer_price/comprehensive_analysis.py` |
| 4. 客単価の部 | パーセンタイル別変化 | `reports/graph03_percentile_change_20pct.png` | `scripts/09_interim_report/generate_graphs.py` |
| 4. 客単価の部 | 曜日・時間帯分析 | `reports/graph04_weekday_hour_analysis.png` | `scripts/09_interim_report/generate_graphs.py` |
| 4. 客単価の部 | メニュー貢献度 | `reports/graph05_menu_contribution.png` | `scripts/09_interim_report/generate_graphs.py` |
| 5. 回転率の部 | 曜日別・時間帯別滞在時間 | `reports/graph13_duration_by_hour_weekday.png` | `scripts/09_interim_report/generate_graphs.py` |
| 5. 回転率の部 | 時間帯別来店組数と店内人数 | `reports/graph06_hourly_visits_occupancy.png` | `scripts/09_interim_report/generate_graphs.py` |
| 6. その他インサイトなど | 売上上位/下位の2軸分布 | `reports/graph08_sales_2d_separation.png` | `scripts/09_interim_report/generate_graphs.py` |
| 6. その他インサイトなど | 時間帯別の客数と客単価 | `reports/graph07_spend_customers_by_time.png` | `scripts/09_interim_report/generate_graphs.py` |
| 6. その他インサイトなど | 4セグメント比較 | `reports/09_overlay_all.png` | `scripts/08_segment/overlay_comparison.py` |
| 6. その他インサイトなど | High/Low比較 | `reports/HighLowAnalysis/01_high_low_distribution.png` | `scripts/08_segment/high_low_analysis.py` |
| 6. その他インサイトなど | 要因比率 | `reports/HighLowAnalysis/02_factor_ratio.png` | `scripts/08_segment/high_low_analysis.py` |

