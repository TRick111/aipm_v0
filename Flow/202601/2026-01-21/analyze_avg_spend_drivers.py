#!/usr/bin/env python3
"""
Analyze avg spend drivers with CSV-only Python.

Outputs (in AvgSpendAnalysis/):
  - monthly_avg_spend.csv
  - category_monthly_metrics.csv
  - category_yoy_decomposition_2025_vs_2024.csv
  - product_yoy_delta_2025_vs_2024.csv
  - avg_spend_python_analysis.md
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "transformed_pos_data_eatin.csv"
OUT_DIR = BASE_DIR / "AvgSpendAnalysis"
OUT_DIR.mkdir(exist_ok=True)


def safe_float(value: str) -> float:
    if value is None:
        return 0.0
    value = value.replace(",", "").strip()
    try:
        return float(value)
    except ValueError:
        return 0.0


def parse_month_key(date_str: str) -> str | None:
    # date format: YYYY/MM/DD
    parts = (date_str or "").split("/")
    if len(parts) < 2:
        return None
    year = parts[0].strip()
    month = parts[1].strip()
    if not (year.isdigit() and month.isdigit()):
        return None
    return f"{int(year):04d}-{int(month):02d}"


def parse_month_num(month_key: str) -> int:
    return int(month_key.split("-")[1])


def parse_quantity(sub_menu: str) -> int:
    # Example: "定食セット(並盛)x1"
    if not sub_menu:
        return 1
    match = re.search(r"x(\\d+)", sub_menu)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return 1
    return 1


month_customers = defaultdict(float)
month_sales = defaultdict(float)
month_cat_sales = defaultdict(lambda: defaultdict(float))
month_cat_items = defaultdict(lambda: defaultdict(int))
month_prod_sales = defaultdict(lambda: defaultdict(float))
month_prod_items = defaultdict(lambda: defaultdict(int))

slip_seen = set()

with DATA_PATH.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        date_str = (row.get("H.集計対象営業年月日") or "").strip()
        month_key = parse_month_key(date_str)
        if not month_key:
            continue

        slip = (row.get("H.伝票番号") or "").strip()
        slip_key = (date_str, slip)
        if slip and slip_key not in slip_seen:
            slip_seen.add(slip_key)
            customers = safe_float(row.get("H.客数（合計）") or "0")
            subtotal = safe_float(row.get("H.小計") or "0")
            month_customers[month_key] += customers
            month_sales[month_key] += subtotal

        price = safe_float(row.get("D.価格") or "0")
        category = (row.get("D.商品カテゴリ2") or "不明").strip() or "不明"
        product = (row.get("D.商品名") or "不明").strip() or "不明"
        quantity = parse_quantity(row.get("D.サブメニュー") or "")

        month_cat_sales[month_key][category] += price
        month_cat_items[month_key][category] += quantity
        month_prod_sales[month_key][product] += price
        month_prod_items[month_key][product] += quantity


def per_customer(value: float, month_key: str) -> float:
    customers = month_customers.get(month_key, 0.0)
    return value / customers if customers else 0.0


monthly_avg_spend = {}
for month_key, sales in month_sales.items():
    monthly_avg_spend[month_key] = per_customer(sales, month_key)


# Monthly category metrics
category_rows = []
for month_key in sorted(month_cat_sales):
    customers = month_customers.get(month_key, 0.0)
    for category, sales in month_cat_sales[month_key].items():
        items = month_cat_items[month_key].get(category, 0)
        sales_per_cust = sales / customers if customers else 0.0
        items_per_cust = items / customers if customers else 0.0
        avg_price = sales / items if items else 0.0
        category_rows.append({
            "month": month_key,
            "category": category,
            "customers": round(customers, 2),
            "sales_total": round(sales, 2),
            "items_total": items,
            "sales_per_customer": round(sales_per_cust, 2),
            "items_per_customer": round(items_per_cust, 4),
            "avg_price_per_item": round(avg_price, 2),
        })


# Monthly product metrics (for YoY deltas only)
product_rows = []
for month_key in sorted(month_prod_sales):
    customers = month_customers.get(month_key, 0.0)
    for product, sales in month_prod_sales[month_key].items():
        items = month_prod_items[month_key].get(product, 0)
        sales_per_cust = sales / customers if customers else 0.0
        avg_price = sales / items if items else 0.0
        product_rows.append({
            "month": month_key,
            "product": product,
            "sales_per_customer": sales_per_cust,
            "items_total": items,
            "avg_price_per_item": avg_price,
        })


# YoY decomposition (2025 vs 2024) by category
category_by_month = defaultdict(dict)
for row in category_rows:
    category_by_month[row["month"]][row["category"]] = row

months_2024 = sorted([m for m in monthly_avg_spend if m.startswith("2024-")])
months_2025 = sorted([m for m in monthly_avg_spend if m.startswith("2025-")])
months_intersect = sorted({parse_month_num(m) for m in months_2024} & {parse_month_num(m) for m in months_2025})

category_yoy_rows = []
for month_num in months_intersect:
    m2024 = f"2024-{month_num:02d}"
    m2025 = f"2025-{month_num:02d}"
    cats = set(category_by_month[m2024]) | set(category_by_month[m2025])
    for cat in cats:
        r0 = category_by_month[m2024].get(cat, {})
        r1 = category_by_month[m2025].get(cat, {})
        s0 = r0.get("sales_per_customer", 0.0)
        s1 = r1.get("sales_per_customer", 0.0)
        i0 = r0.get("items_per_customer", 0.0)
        i1 = r1.get("items_per_customer", 0.0)
        p0 = r0.get("avg_price_per_item", 0.0)
        p1 = r1.get("avg_price_per_item", 0.0)
        delta = s1 - s0
        vol_effect = (i1 - i0) * (p1 + p0) / 2
        price_effect = (p1 - p0) * (i1 + i0) / 2
        category_yoy_rows.append({
            "month_num": month_num,
            "category": cat,
            "delta_sales_per_customer": round(delta, 2),
            "volume_effect": round(vol_effect, 2),
            "price_effect": round(price_effect, 2),
            "sales_per_customer_2024": round(s0, 2),
            "sales_per_customer_2025": round(s1, 2),
        })


# YoY delta by product (per customer)
product_by_month = defaultdict(dict)
for row in product_rows:
    product_by_month[row["month"]][row["product"]] = row

product_yoy_rows = []
for month_num in months_intersect:
    m2024 = f"2024-{month_num:02d}"
    m2025 = f"2025-{month_num:02d}"
    prods = set(product_by_month[m2024]) | set(product_by_month[m2025])
    for prod in prods:
        r0 = product_by_month[m2024].get(prod, {})
        r1 = product_by_month[m2025].get(prod, {})
        s0 = r0.get("sales_per_customer", 0.0)
        s1 = r1.get("sales_per_customer", 0.0)
        product_yoy_rows.append({
            "month_num": month_num,
            "product": prod,
            "delta_sales_per_customer": round(s1 - s0, 2),
            "sales_per_customer_2024": round(s0, 2),
            "sales_per_customer_2025": round(s1, 2),
        })


# Write CSV outputs
def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


write_csv(
    OUT_DIR / "monthly_avg_spend.csv",
    ["month", "customers", "sales_total", "avg_spend_per_customer"],
    [
        {
            "month": m,
            "customers": round(month_customers.get(m, 0.0), 2),
            "sales_total": round(month_sales.get(m, 0.0), 2),
            "avg_spend_per_customer": round(monthly_avg_spend.get(m, 0.0), 2),
        }
        for m in sorted(monthly_avg_spend)
    ],
)

write_csv(
    OUT_DIR / "category_monthly_metrics.csv",
    [
        "month",
        "category",
        "customers",
        "sales_total",
        "items_total",
        "sales_per_customer",
        "items_per_customer",
        "avg_price_per_item",
    ],
    category_rows,
)

write_csv(
    OUT_DIR / "category_yoy_decomposition_2025_vs_2024.csv",
    [
        "month_num",
        "category",
        "delta_sales_per_customer",
        "volume_effect",
        "price_effect",
        "sales_per_customer_2024",
        "sales_per_customer_2025",
    ],
    category_yoy_rows,
)

write_csv(
    OUT_DIR / "product_yoy_delta_2025_vs_2024.csv",
    [
        "month_num",
        "product",
        "delta_sales_per_customer",
        "sales_per_customer_2024",
        "sales_per_customer_2025",
    ],
    product_yoy_rows,
)


# Build summary markdown
def top_n(items: list[tuple[float, str]], n: int) -> list[tuple[float, str]]:
    items_sorted = sorted(items, reverse=True)
    return items_sorted[:n]


md_lines = []
md_lines.append("# 客単価増加要因（Python分析）")
md_lines.append("")
md_lines.append("## 1. 分析概要")
md_lines.append("- 対象: EAT IN POSデータ")
md_lines.append("- 手法: 月別客単価をカテゴリ/商品ごとの**円/客**に分解")
md_lines.append("- YoY比較: 2025年 - 2024年（同月）")
md_lines.append("- 価格 vs 数量: 1人あたりの**アイテム数**と**平均単価**で分解（ミッドポイント法）")
md_lines.append("")
md_lines.append("## 2. 月別客単価（平均）")
md_lines.append("")
md_lines.append("| 月 | 客単価(円/客) |")
md_lines.append("|---|---:|")
for month_key in sorted(monthly_avg_spend):
    md_lines.append(f"| {month_key} | {monthly_avg_spend[month_key]:.1f} |")

md_lines.append("")
md_lines.append("## 3. 前年同月比（2025 vs 2024）の主要因")
md_lines.append("")
md_lines.append("| 月 | 客単価差分 | 主因カテゴリ(+) | 主因カテゴリ(-) | 主因メニュー(+) |")
md_lines.append("|---|---:|---|---|---|")

for month_num in months_intersect:
    m2024 = f"2024-{month_num:02d}"
    m2025 = f"2025-{month_num:02d}"
    diff = monthly_avg_spend.get(m2025, 0.0) - monthly_avg_spend.get(m2024, 0.0)

    cat_diffs = []
    for row in category_yoy_rows:
        if row["month_num"] == month_num:
            cat_diffs.append((row["delta_sales_per_customer"], row["category"]))

    prod_diffs = []
    for row in product_yoy_rows:
        if row["month_num"] == month_num:
            prod_diffs.append((row["delta_sales_per_customer"], row["product"]))

    top_cat_pos = ", ".join([f"{name}({value:.0f})" for value, name in top_n(cat_diffs, 2)])
    top_cat_neg = ", ".join([f"{name}({value:.0f})" for value, name in sorted(cat_diffs)[:2]])
    top_prod_pos = ", ".join([f"{name}({value:.0f})" for value, name in top_n(prod_diffs, 3)])
    md_lines.append(f"| {month_num:02d} | {diff:.1f} | {top_cat_pos} | {top_cat_neg} | {top_prod_pos} |")

md_lines.append("")
md_lines.append("## 4. 価格効果 vs 数量効果（カテゴリ別）")
md_lines.append("")
md_lines.append("- 月別の前年差分を「数量（1人あたり購入数）」と「価格（平均単価）」に分解。")
md_lines.append("- 詳細: `category_yoy_decomposition_2025_vs_2024.csv`")
md_lines.append("")
md_lines.append("## 5. 2025年4月以降の緩やかな上昇の要因")
md_lines.append("")
md_lines.append("### 4-6月平均 vs 10-12月平均（円/客の差）")

# Compute Apr-Jun vs Oct-Dec deltas for categories and products
def avg_over_months(rows: list[dict], months: set[int], key: str) -> dict:
    acc = defaultdict(list)
    for row in rows:
        month = row["month"]
        if not month.startswith("2025-"):
            continue
        if parse_month_num(month) in months:
            acc[row[key]].append(row["sales_per_customer"])
    return {k: (sum(v) / len(v) if v else 0.0) for k, v in acc.items()}


early_months = {4, 5, 6}
late_months = {10, 11, 12}

cat_early = avg_over_months(category_rows, early_months, "category")
cat_late = avg_over_months(category_rows, late_months, "category")
prod_early = avg_over_months(product_rows, early_months, "product")
prod_late = avg_over_months(product_rows, late_months, "product")

cat_deltas = [(cat_late.get(c, 0.0) - cat_early.get(c, 0.0), c) for c in set(cat_early) | set(cat_late)]
prod_deltas = [(prod_late.get(p, 0.0) - prod_early.get(p, 0.0), p) for p in set(prod_early) | set(prod_late)]

md_lines.append("")
md_lines.append("**カテゴリ（上位）**")
for value, name in top_n(cat_deltas, 8):
    md_lines.append(f"- {name}: {value:.1f}")

md_lines.append("")
md_lines.append("**メニュー（上位）**")
for value, name in top_n(prod_deltas, 10):
    md_lines.append(f"- {name}: {value:.1f}")

md_lines.append("")
md_lines.append("## 6. 注意点")
md_lines.append("- 1行 = 1アイテムとして数量を推定（サブメニューの `xN` を数量として採用）")
md_lines.append("- 2025-03 は休業/売上0のため前年比の解釈から除外推奨")


report_path = OUT_DIR / "avg_spend_python_analysis.md"
report_path.write_text("\n".join(md_lines), encoding="utf-8")

print("Analysis complete.")
print(f"- Output dir: {OUT_DIR}")
print(f"- Report: {report_path}")
