#!/usr/bin/env python3
"""W21 (2026-05-18 ～ 2026-05-24) 客層分析①②③ 抽出スクリプト

- BFA-1 (インバウンド): AirRegi CSV のメモ欄に "海外" 部分一致
- BFA-2 (CLP社員)   : rawdata.csv のメニュー名に "CLP" 部分一致
- BFA-3 (イベント)  : rawdata.csv の category1 が "イベント" 完全一致

業務日基準 (朝6時境界): entry_at が 0:00-5:59 の場合は前日扱い
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta, date
from pathlib import Path

RAWDATA = Path("/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv")
AIRREGI_MAY = Path("/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads/20260501-20260531-BAR FIVE Arrows.csv")

W21_START = date(2026, 5, 18)
W21_END = date(2026, 5, 24)


def business_date(dt: datetime) -> date:
    if dt.hour < 6:
        return (dt - timedelta(days=1)).date()
    return dt.date()


def utc_to_jst_business_date(s: str) -> date | None:
    """rawdata.csv の entry_at (UTC, 文字列) を JST に変換し営業日を返す"""
    try:
        dt_utc = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    dt_jst = dt_utc + timedelta(hours=9)
    return business_date(dt_jst)


# ---------- rawdata.csv 集計 ----------
account_totals: dict[str, int] = {}     # account_id -> account_total
account_customers: dict[str, int] = {}  # account_id -> customer_count
account_bdate: dict[str, date] = {}     # account_id -> business_date
account_menu_clp: set[str] = set()      # BFA-2: メニュー名に "CLP" を含む account_id
account_category_event: set[str] = set()  # BFA-3: category "イベント"

with RAWDATA.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bd = utc_to_jst_business_date(row["entry_at"])
        if bd is None:
            continue
        if not (W21_START <= bd <= W21_END):
            continue
        acc = row["account_id"]
        try:
            total = int(row["account_total"])
        except (ValueError, TypeError):
            total = 0
        try:
            cust = int(row["customer_count"])
        except (ValueError, TypeError):
            cust = 0
        account_totals[acc] = total
        account_customers[acc] = cust
        account_bdate[acc] = bd

        menu = row.get("menu_name", "") or ""
        cat = row.get("category1", "") or ""
        if "CLP" in menu:
            account_menu_clp.add(acc)
        if cat.strip() == "イベント":
            account_category_event.add(acc)


# ---------- AirRegi CSV (BFA-1 memo "海外") ----------
import io
import re

def header_account_ids_with_overseas_memo(path: Path) -> tuple[set[str], dict[str, int], dict[str, int], dict[str, date]]:
    """エアレジCSV (Shift-JIS) を読み、メモ欄に"海外"を含む取引No (account_id) と
    すべてのヘッダー行の合計・人数・業務日も取得する。"""
    overseas = set()
    air_totals: dict[str, int] = {}
    air_customers: dict[str, int] = {}
    air_bdate: dict[str, date] = {}

    with path.open("rb") as fb:
        raw = fb.read().decode("shift_jis")

    # csv.reader でパース
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    header = rows[0]
    idx = {name: i for i, name in enumerate(header)}

    for row in rows[1:]:
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        txn = row[idx["取引No"]].strip()
        # ヘッダー行は会計日 (会計日カラム) が非空
        kaikei_hi = row[idx["会計日"]].strip()
        if not kaikei_hi:
            continue  # 明細行

        # 会計日時を組み立て、業務日を決定
        kaikei_jikan = row[idx["会計時間"]].strip()
        try:
            dt = datetime.strptime(f"{kaikei_hi} {kaikei_jikan}", "%Y/%m/%d %H:%M:%S")
        except ValueError:
            continue
        bd = business_date(dt)
        if not (W21_START <= bd <= W21_END):
            continue

        try:
            total = int(row[idx["合計"]].replace(",", "") or "0")
        except ValueError:
            total = 0
        try:
            cust = int(row[idx["人数"]].replace(",", "") or "0")
        except ValueError:
            cust = 0

        air_totals[txn] = total
        air_customers[txn] = cust
        air_bdate[txn] = bd

        memo = row[idx["メモ"]].strip()
        if "海外" in memo:
            overseas.add(txn)

    return overseas, air_totals, air_customers, air_bdate


overseas, air_totals, air_customers, air_bdate = header_account_ids_with_overseas_memo(AIRREGI_MAY)


# ---------- 集計関数 ----------
def aggregate(matched_ids: set[str], totals: dict[str, int], customers: dict[str, int]) -> dict:
    sales_match = sum(totals.get(a, 0) for a in matched_ids if a in totals)
    cust_match = sum(customers.get(a, 0) for a in matched_ids if a in customers)
    org_match = sum(1 for a in matched_ids if a in totals)
    sales_total = sum(totals.values())
    cust_total = sum(customers.values())
    org_total = len(totals)
    return {
        "sales_match": sales_match,
        "sales_total": sales_total,
        "sales_ratio": (sales_match / sales_total * 100) if sales_total else 0.0,
        "cust_match": cust_match,
        "cust_total": cust_total,
        "cust_ratio": (cust_match / cust_total * 100) if cust_total else 0.0,
        "org_match": org_match,
        "org_total": org_total,
        "org_ratio": (org_match / org_total * 100) if org_total else 0.0,
    }


# 3 切口とも分母は rawdata.csv (prod DB 正本)。
# BFA-1 のヒット account_id は AirRegi の memo 由来だが、
# rawdata.csv に同じ取引No が含まれる場合のみカウント (両者に存在する 0001 系以外の取引)
# rawdata に存在しない (= AirRegi にのみある) 取引はスキップ
bfa1_ids_in_raw = {a for a in overseas if a in account_totals}
bfa1 = aggregate(bfa1_ids_in_raw, account_totals, account_customers)
bfa2 = aggregate(account_menu_clp, account_totals, account_customers)
bfa3 = aggregate(account_category_event, account_totals, account_customers)


# ---------- レポート出力 ----------
report = {
    "week": "2026-W21",
    "period_business_days": [W21_START.isoformat(), W21_END.isoformat()],
    "rawdata_org_total": len(account_totals),
    "rawdata_sales_total": sum(account_totals.values()),
    "rawdata_cust_total": sum(account_customers.values()),
    "airregi_org_total": len(air_totals),
    "airregi_sales_total": sum(air_totals.values()),
    "airregi_cust_total": sum(air_customers.values()),
    "BFA-1_inbound": {
        "source": "airregi_memo_海外",
        "matched_accounts": sorted(overseas),
        **bfa1,
    },
    "BFA-2_clp_employee": {
        "source": "rawdata_menu_CLP",
        "matched_accounts_count": len(account_menu_clp),
        **bfa2,
    },
    "BFA-3_event": {
        "source": "rawdata_category_イベント",
        "matched_accounts_count": len(account_category_event),
        **bfa3,
    },
}

out = Path(__file__).parent / "customer_segment_results.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
