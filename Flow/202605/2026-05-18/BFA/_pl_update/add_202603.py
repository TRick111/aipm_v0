#!/usr/bin/env python3
"""2026-03 のPLを sheet_pl_parsed.json に追加する。
- expenses: ユーザー確定値（家賃補完済、初期費用除外）
- sales: v2/comparison.json のシート売上（参考。KPI売上はPOSから）
- pipeline 互換フィールド (expenses_by_month / expense_totals / sales_by_month) も更新
"""
import json
from pathlib import Path

BASE = Path("/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA")
TARGET_FILE = BASE / "sheet_pl_parsed.json"
COMP_FILE = BASE / "v2/comparison.json"

YM = "2026-03"

# 確定値（家賃補完済、初期費用除外）
EXPENSES_202603 = {
    "食材": 320995.0,
    "ドリンク": 386324.0,
    "広告費": 411520.0,
    "家賃": 1112859.0,
    "人件費": 322784.0,
    "ローン返済": 179982.0,
    "水道光熱費": 77844.0,
    "管理費": 245473.0,
    "備品": 95467.0,
    "税金": 0.0,
}
EXPENSE_TOTAL_202603 = sum(EXPENSES_202603.values())
assert int(EXPENSE_TOTAL_202603) == 3153248, f"total mismatch: {EXPENSE_TOTAL_202603}"

with open(TARGET_FILE) as f:
    data = json.load(f)

with open(COMP_FILE) as f:
    comp = json.load(f)

sales_202603 = comp["sheet"]["actual"]["sales"].get(YM, {})
sales_clean = {k: float(v) for k, v in sales_202603.items()}
sales_total = sum(sales_clean.values())

# periods
if YM not in data["periods"]:
    data["periods"].append(YM)

# sales (category -> ym)
for cat, amt in sales_clean.items():
    data["sales"].setdefault(cat, {})[YM] = float(amt)

# expenses (category -> ym)
for cat, amt in EXPENSES_202603.items():
    data["expenses"].setdefault(cat, {})[YM] = float(amt)

# totals
data["totals"][YM] = {
    "sales": sales_total,
    "expense": EXPENSE_TOTAL_202603,
    "profit": sales_total - EXPENSE_TOTAL_202603,
}

# pipeline 互換: expenses_by_month / expense_totals / sales_by_month
data.setdefault("expenses_by_month", {})[YM] = dict(EXPENSES_202603)
data.setdefault("expense_totals", {})[YM] = EXPENSE_TOTAL_202603
data.setdefault("sales_by_month", {})[YM] = sales_total

# source_per_month
data.setdefault("source_per_month", {})[YM] = "【BFA】運営管理 / 新PL管理シート（家賃補完・初期費用除外）"

# notes
data.setdefault("notes_per_month", {})[YM] = {
    "rent_supplemented": True,
    "rent_value": 1112859.0,
    "rent_reason": "シート転記漏れ。1-2月と同額の固定費として補完。",
    "initial_cost_excluded": True,
    "initial_cost_value": 950000.0,
    "initial_cost_reason": "撮影/試作費等の一過性費用。PLから除外。",
}

with open(TARGET_FILE, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ wrote {TARGET_FILE}")
print(f"  2026-03 expense total: ¥{EXPENSE_TOTAL_202603:,.0f}")
print(f"  2026-03 sheet sales total: ¥{sales_total:,.0f}")
print(f"  periods count: {len(data['periods'])}")
