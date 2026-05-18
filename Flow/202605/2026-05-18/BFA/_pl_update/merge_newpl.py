#!/usr/bin/env python3
"""新PL管理（移管前）から 2026-01/02 を抽出し、既存 sheet_pl_parsed.json に追加。
さらに pipeline 互換の expenses_by_month / expense_totals / sales_by_month も同居させる。
"""
import json, os, shutil, sys
from pathlib import Path

BASE = Path("/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA")
SRC_EXISTING = BASE / "sheet_pl_parsed.json"
SRC_NEW = BASE / "v2/comparison.json"
OUT = BASE / "sheet_pl_parsed.json"
OUT_NEWPL_ONLY = BASE / "_pl_update/sheet_newpl_parsed.json"

# 1) 既存（legacy: categories→months）
with open(SRC_EXISTING) as f:
    legacy = json.load(f)

# 2) 新PL管理（移管前） v2/comparison.json から 2026-01 / 02 を取り出す
with open(SRC_NEW) as f:
    newpl_all = json.load(f)
newpl_actual = newpl_all["sheet"]["actual"]
newpl_expenses = newpl_actual["expenses"]
newpl_sales = newpl_actual["sales"]

TARGETS = ["2026-01", "2026-02"]

# 3) 新PL管理だけのファイル（pipeline 互換形式）
newpl_only = {
    "source": "【BFA】本部サポート / 新PL管理（移管前）シート",
    "spreadsheet_id": "1yALYHSMncsSURPfWEN0SXQJeVUdMm6yxUXhhkal-q3o",
    "sheet_name": "新PL管理（移管前）",
    "fetched_at": "2026-05-18",
    "expenses_by_month": {},
    "expense_totals": {},
    "sales_by_month": {},
    "sales_breakdown": {},
}

for ym in TARGETS:
    exp = newpl_expenses.get(ym, {})
    # 念のため数値化＋ゼロ削除（税金=0 は残す）
    exp_clean = {k: float(v) for k, v in exp.items()}
    newpl_only["expenses_by_month"][ym] = exp_clean
    newpl_only["expense_totals"][ym] = sum(exp_clean.values())

    sales = newpl_sales.get(ym, {})
    newpl_only["sales_breakdown"][ym] = {k: float(v) for k, v in sales.items()}
    newpl_only["sales_by_month"][ym] = sum(float(v) for v in sales.values())

os.makedirs(OUT_NEWPL_ONLY.parent, exist_ok=True)
with open(OUT_NEWPL_ONLY, "w") as f:
    json.dump(newpl_only, f, ensure_ascii=False, indent=2)
print(f"✓ wrote {OUT_NEWPL_ONLY}")

# 4) 既存 legacy 形式に 2026-01/02 を追加 ＋ pipeline 互換フィールドも同居させる
#    既存スキーマ: {periods, sales: {cat: {ym: amt}}, expenses: {cat: {ym: amt}}, totals: {ym: {sales, expense, profit}}}
for ym in TARGETS:
    if ym not in legacy["periods"]:
        legacy["periods"].append(ym)

    # sales（カテゴリ別）
    sales_bd = newpl_only["sales_breakdown"][ym]
    for cat, amt in sales_bd.items():
        legacy["sales"].setdefault(cat, {})[ym] = float(amt)

    # expenses（カテゴリ別）
    exp = newpl_only["expenses_by_month"][ym]
    for cat, amt in exp.items():
        legacy["expenses"].setdefault(cat, {})[ym] = float(amt)

    # totals
    legacy["totals"][ym] = {
        "sales": newpl_only["sales_by_month"][ym],
        "expense": newpl_only["expense_totals"][ym],
        "profit": newpl_only["sales_by_month"][ym] - newpl_only["expense_totals"][ym],
    }

# 5) pipeline 互換フィールドを同ファイルに追加（過去のlegacy月分も含めて再構築）
expenses_by_month = {}
expense_totals = {}
sales_by_month = {}

# legacy.expenses は {category: {ym: amt}} なので、{ym: {category: amt}} に転置
for cat, by_ym in legacy["expenses"].items():
    for ym, amt in by_ym.items():
        if amt is None:
            continue
        # YM フォーマット("YYYY-MM")だけ残す
        if not (isinstance(ym, str) and len(ym) == 7 and ym[4] == "-"):
            continue
        expenses_by_month.setdefault(ym, {})[cat] = float(amt)
        expense_totals[ym] = expense_totals.get(ym, 0.0) + float(amt)

for cat, by_ym in legacy["sales"].items():
    for ym, amt in by_ym.items():
        if amt is None:
            continue
        if not (isinstance(ym, str) and len(ym) == 7 and ym[4] == "-"):
            continue
        sales_by_month[ym] = sales_by_month.get(ym, 0.0) + float(amt)

legacy["expenses_by_month"] = expenses_by_month
legacy["expense_totals"] = expense_totals
legacy["sales_by_month"] = sales_by_month
legacy["source_per_month"] = {
    "2026-01": "【BFA】本部サポート / 新PL管理（移管前）シート",
    "2026-02": "【BFA】本部サポート / 新PL管理（移管前）シート",
}

with open(OUT, "w") as f:
    json.dump(legacy, f, ensure_ascii=False, indent=2)
print(f"✓ updated {OUT}")
print(f"  months in expenses_by_month: {len(expenses_by_month)}")
print(f"  2026-01 expense total: ¥{expense_totals.get('2026-01', 0):,.0f}")
print(f"  2026-02 expense total: ¥{expense_totals.get('2026-02', 0):,.0f}")
print(f"  2026-01 sales total:   ¥{sales_by_month.get('2026-01', 0):,.0f}")
print(f"  2026-02 sales total:   ¥{sales_by_month.get('2026-02', 0):,.0f}")
