#!/usr/bin/env bash
set -euo pipefail

STORE_ROOT="$(cd "$(dirname "$0")" && pwd)"
SHARED="/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/GFS飲食店分析/shared_scripts/scripts"

export MPLCONFIGDIR="$STORE_ROOT/.mplconfig"
export MPLBACKEND="Agg"
mkdir -p "$MPLCONFIGDIR"

echo "STORE_ROOT=$STORE_ROOT"

# 0) 前提: data/intermediate/transformed_pos_data_eatin.csv があること

# 0.5) 月次KPI（合計/ランチ/ディナー）と推移グラフ（3月除外）
python3 "$SHARED/01_kpis/generate_monthly_kpis.py" --store-root "$STORE_ROOT"

# 1) 回転率（滞在時間/occupancy）
# 外れ値（入力異常）で店内人数が過大にならないよう、滞在時間は上限でクリップ（5時間）
python3 "$SHARED/02_duration/analyze_turnover.py" --store-root "$STORE_ROOT" --max-duration-minutes 300

# 2) 客数分析（※なかせいは過去データ制約により、Y2Y比較は参考程度/一部スキップあり）
python3 "$SHARED/06_customer_count/01_analyze_customer_count.py" --store-root "$STORE_ROOT"
python3 "$SHARED/06_customer_count/02_create_graphs.py" --store-root "$STORE_ROOT"

# 3) 客単価分析（BIFTEKIと同等の切り口）
python3 "$SHARED/07_customer_price/customer_price_analysis.py" --store-root "$STORE_ROOT"

# 4) 中間レポート用グラフ（graph01..13）
python3 "$SHARED/09_interim_report/generate_graphs.py" --store-root "$STORE_ROOT"

# 5) セグメント分析（中間レポートで参照される図）
python3 "$SHARED/08_segment/segment_analysis.py" --store-root "$STORE_ROOT"
python3 "$SHARED/08_segment/high_low_analysis.py" --store-root "$STORE_ROOT"
python3 "$SHARED/08_segment/overlay_comparison.py" --store-root "$STORE_ROOT" --period-filter after

echo "done."

