#!/bin/bash
# BFA 4ヶ月分の月報を prod DB に直接アップロード
set -euo pipefail

cd /Users/rikutanaka/RestaurantAILab/Dashboard

FINAL=/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/_prod_verification/final

node scripts/upload-monthly-report-prod-direct.mjs \
  --file "$FINAL/202601_BFA_月次報告資料.html" \
  --store bfa-001 \
  --month 2026-01 \
  --title "BAR FIVE Arrows 月次営業報告 — 2026-01"

node scripts/upload-monthly-report-prod-direct.mjs \
  --file "$FINAL/202602_BFA_月次報告資料.html" \
  --store bfa-001 \
  --month 2026-02 \
  --title "BAR FIVE Arrows 月次営業報告 — 2026-02"

node scripts/upload-monthly-report-prod-direct.mjs \
  --file "$FINAL/202603_BFA_月次報告資料.html" \
  --store bfa-001 \
  --month 2026-03 \
  --title "BAR FIVE Arrows 月次営業報告 — 2026-03"

node scripts/upload-monthly-report-prod-direct.mjs \
  --file "$FINAL/202604_BFA_月次報告資料_v2draft.html" \
  --store bfa-001 \
  --month 2026-04 \
  --title "BAR FIVE Arrows 月次営業報告 — 2026-04"
