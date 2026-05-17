#!/usr/bin/env python3
"""Parse spreadsheet PL JSON into structured dict and save."""
import json, re, sys

SRC = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/pl_sheet_raw.json"
OUT = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/sheet_pl_parsed.json"

with open(SRC) as f:
    raw = json.load(f)

values = raw["values"]
headers = values[0]

# Map column -> period
period_cols = {}  # period_name -> col_index_for_value
for i, h in enumerate(headers):
    if not h:
        continue
    period_cols[h] = i

def to_num(s):
    if s is None or s == "":
        return None
    s = str(s).strip().replace(",", "").replace("¥", "")
    try:
        return float(s)
    except ValueError:
        return None

def normalize_ym(period_name: str):
    m = re.match(r"^(\d{4})年(\d{1,2})月$", period_name)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    return period_name  # aggregate periods kept as-is

# Build structured data
result = {
    "periods": [],          # list of normalized period names
    "sales": {},            # category -> {period: amount}
    "expenses": {},         # category -> {period: amount}
    "totals": {             # period -> {sales, expense, profit}
    },
}

# Sales rows: 1-7 (categories), 8 (total)
sales_rows = list(range(1, 8))
for r in sales_rows:
    cat = values[r][1]
    if not cat:
        continue
    result["sales"][cat] = {}
    for period_name, col in period_cols.items():
        ym = normalize_ym(period_name)
        amount = to_num(values[r][col]) if col < len(values[r]) else None
        if amount is not None:
            result["sales"][cat][ym] = amount

# Expense rows: 9-19
for r in range(9, 20):
    cat = values[r][1] if len(values[r]) > 1 else None
    if not cat or cat == "合計":
        continue
    result["expenses"][cat] = {}
    for period_name, col in period_cols.items():
        ym = normalize_ym(period_name)
        amount = to_num(values[r][col]) if col < len(values[r]) else None
        if amount is not None:
            result["expenses"][cat][ym] = amount

# Totals from row 8 (sales total), 20 (expense total), 21 (profit)
for period_name, col in period_cols.items():
    ym = normalize_ym(period_name)
    s = to_num(values[8][col]) if col < len(values[8]) else None
    e = to_num(values[20][col]) if col < len(values[20]) else None
    p = to_num(values[21][col]) if col < len(values[21]) else None
    result["totals"][ym] = {"sales": s, "expense": e, "profit": p}
    result["periods"].append(ym)

with open(OUT, "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("periods:", result["periods"])
print("sales categories:", list(result["sales"].keys()))
print("expense categories:", list(result["expenses"].keys()))
print(f"wrote {OUT}")
