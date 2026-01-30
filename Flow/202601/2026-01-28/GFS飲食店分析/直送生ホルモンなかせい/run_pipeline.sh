#!/usr/bin/env bash
set -euo pipefail

STORE_ROOT="$(cd "$(dirname "$0")" && pwd)"
SHARED="/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/GFS飲食店分析/shared_scripts/scripts"

echo "STORE_ROOT=$STORE_ROOT"

# 1) 滞在時間/occupancy（ピーク分析の前提データ）
python3 "$SHARED/02_duration/analyze_turnover.py" --store-root "$STORE_ROOT"

echo "done."

