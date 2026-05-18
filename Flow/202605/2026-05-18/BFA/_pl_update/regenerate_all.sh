#!/bin/bash
# Regenerate analysis.json + HTML for 2026-01, 02, 03, 04
# - 組数+1 修正版 monthly_report_pipeline.py を使用
# - PL は sheet_pl_parsed.json (2026-01/02 が新PL管理（移管前）から追加済み)
set -e

BFA=/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA
PIPE=/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/月報/Scripts/monthly_report_pipeline.py
PL_SHEET="$BFA/sheet_pl_parsed.json"

run_month () {
    local YM=$1            # 2026-01
    local YMM=$2           # 202601
    local SALES_CSV=$3
    local OUT="$BFA/月報_$YMM"
    local DAILY="$OUT/DailyReport_$YMM.csv"
    local COMP="$OUT/compare_rawdata.csv"
    echo "=== $YM ==="
    python3 "$PIPE" \
        --target-month "$YM" \
        --store-code BFA \
        --sales-csv "$SALES_CSV" \
        --output-dir "$OUT" \
        --compare-rawdata "$COMP" \
        --daily-report-csv "$DAILY" \
        --pl-source sheet \
        --pl-sheet-parsed "$PL_SHEET"

    # Build HTML（per-month builder スクリプト＝動的月対応）
    local BUILD="$OUT/build_html_$YMM.py"
    if [ ! -f "$BUILD" ]; then
        BUILD=/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/月報/Scripts/build_monthly_html.py
    fi
    python3 "$BUILD" \
        --analysis-json "$OUT/analysis.json" \
        --output "$OUT/${YMM}_BFA_月次報告資料.html" \
        --store-name "BAR FIVE Arrows"
}

run_month 2026-01 202601 "$BFA/月報_202601/sales_202601.csv"
run_month 2026-02 202602 "$BFA/月報_202602/sales_202602.csv"
run_month 2026-03 202603 "$BFA/月報_202603/sales_202603.csv"
run_month 2026-04 202604 "/Users/rikutanaka/RestaurantAILab/Dashboard/.local/bulkupload/bfa-001/会計明細_20260401-20260430_LATEST.csv"
