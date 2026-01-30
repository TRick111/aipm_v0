#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
なかせいPOS（取引データ） → THE BIFTEKI互換の中間CSVを生成する変換スクリプト。

出力は BIFTEKI の `transformed_pos_data_eatin.csv` と同一ヘッダー（列名）に揃える。
※持ち帰り無しの前提で D.商品カテゴリ1 は全件 'EAT IN' 固定。
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


BIFTEKI_COLUMNS = [
    "H.伝票番号",
    "H.集計対象営業年月日",
    "H.曜日",
    "H.伝票発行日",
    "H.伝票処理日",
    "H.客数（合計）",
    "H.小計",
    "H.総商品数",
    "D.商品カテゴリ1",
    "D.商品カテゴリ2",
    "D.商品",
    "D.商品コード",
    "D.商品名",
    "D.サブメニュー",
    "D.価格",
    "D.ベース価格",
    "D.オーダーメモ",
    "D.オーダー日時",
]


JP_WEEKDAY = ["月", "火", "水", "木", "金", "土", "日"]


def parse_dt_any(s: str) -> Optional[datetime]:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def fmt_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def fmt_date(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y/%m/%d")


def to_int(s: str, default: int = 0) -> int:
    s = (s or "").strip()
    if s == "":
        return default
    try:
        # "0.00" 等が来る場合があるので float 経由
        return int(float(s))
    except ValueError:
        return default


@dataclass
class TxAgg:
    ticket_no: str
    business_date: str
    weekday: str
    entry_dt: Optional[datetime]
    exit_dt: Optional[datetime]
    customers: int
    subtotal: int
    total_qty: int


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(
            Path(__file__).resolve().parents[2]
            / "work"
            / "merged_transactions_20241201_20260128.csv"
        ),
        help="merged取引CSV（UTF-8）",
    )
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parents[2]
            / "work"
            / "transformed_pos_data_eatin.csv"
        ),
        help="BIFTEKI互換の中間CSV（UTF-8）",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1st pass: transaction-level aggregation
    tx: Dict[str, TxAgg] = {}

    with in_path.open("r", encoding="utf-8", newline="") as rf:
        r = csv.DictReader(rf)
        for row in r:
            # filter: 通常取引のみ、取消は除外
            if row.get("取引区分 （1：通常、2：入金、3：出金、4:：預かり金、 5：預かり金返金、6：ポイント加算、7：ポイント減算、8：ポイント失効、11：チップ、13：マイル加算、14：マイル減算、 16：領収証発行）") != "1":
                continue
            if row.get("取消区分 (0:通常、1：取消)") != "0":
                continue

            tx_id = (row.get("取引ID") or "").strip()
            if not tx_id:
                continue

            ticket_no = f"No:{tx_id}"
            # 営業日: 締め日時 が最優先。無ければ取引日時の日付。
            #
            # 重要: このPOSでは「精算日時」が締め/集計処理の実行日時として入っているケースがある（後日になる）。
            # 滞在時間・店内人数の推定に使う退店時刻は「取引日時（=精算/会計タイミング）」を優先する。
            close_dt = parse_dt_any(row.get("取引日時") or "") or parse_dt_any(row.get("精算日時") or "")
            business_date_raw = (row.get("締め日時") or "").strip()
            business_date_dt = parse_dt_any(business_date_raw) or close_dt
            business_date = fmt_date(business_date_dt)
            weekday = JP_WEEKDAY[business_date_dt.weekday()] if business_date_dt else ""

            entry_dt = parse_dt_any(row.get("入店日時") or "")
            exit_dt = close_dt

            customers = to_int(row.get("客数") or "0", default=0)
            subtotal = to_int(row.get("合計") or row.get("小計") or "0", default=0)

            qty = to_int(row.get("数量") or "0", default=0)

            if tx_id not in tx:
                tx[tx_id] = TxAgg(
                    ticket_no=ticket_no,
                    business_date=business_date,
                    weekday=weekday,
                    entry_dt=entry_dt,
                    exit_dt=exit_dt,
                    customers=customers,
                    subtotal=subtotal,
                    total_qty=qty,
                )
            else:
                # 合算（数量）
                tx[tx_id].total_qty += qty

                # customers/subtotal が行によりブレる場合に備えて、最大値を採用
                tx[tx_id].customers = max(tx[tx_id].customers, customers)
                tx[tx_id].subtotal = max(tx[tx_id].subtotal, subtotal)

                # 入退店時刻は最小/最大で補正
                if entry_dt and (not tx[tx_id].entry_dt or entry_dt < tx[tx_id].entry_dt):
                    tx[tx_id].entry_dt = entry_dt
                if exit_dt and (not tx[tx_id].exit_dt or exit_dt > tx[tx_id].exit_dt):
                    tx[tx_id].exit_dt = exit_dt

    # 2nd pass: write item rows with BIFTEKI schema
    written = 0
    skipped_no_item = 0

    with in_path.open("r", encoding="utf-8", newline="") as rf, out_path.open(
        "w", encoding="utf-8", newline=""
    ) as wf:
        r = csv.DictReader(rf)
        w = csv.DictWriter(wf, fieldnames=BIFTEKI_COLUMNS, quoting=csv.QUOTE_ALL)
        w.writeheader()

        for row in r:
            if row.get("取引区分 （1：通常、2：入金、3：出金、4:：預かり金、 5：預かり金返金、6：ポイント加算、7：ポイント減算、8：ポイント失効、11：チップ、13：マイル加算、14：マイル減算、 16：領収証発行）") != "1":
                continue
            if row.get("取消区分 (0:通常、1：取消)") != "0":
                continue

            tx_id = (row.get("取引ID") or "").strip()
            if not tx_id or tx_id not in tx:
                continue

            item_name = (row.get("商品名") or "").strip()
            if not item_name:
                skipped_no_item += 1
                continue

            agg = tx[tx_id]

            # product code fallback: 商品コード → 商品ID → 空
            product_code = (row.get("商品コード") or "").strip() or (row.get("商品ID") or "").strip()

            d_item = f"{product_code}:{item_name}" if product_code else item_name

            qty = to_int(row.get("数量") or "0", default=0)
            line_total = to_int(
                row.get("販売価格計（値引済）（税込）") or row.get("値引き後計") or "0",
                default=0,
            )
            if line_total == 0 and qty > 0:
                unit_price = to_int(row.get("販売単価") or row.get("商品単価") or "0", default=0)
                line_total = unit_price * qty

            order_dt = parse_dt_any(row.get("取引日時") or "") or agg.exit_dt or agg.entry_dt

            out_row = {
                "H.伝票番号": agg.ticket_no,
                "H.集計対象営業年月日": agg.business_date,
                "H.曜日": agg.weekday,
                "H.伝票発行日": fmt_dt(agg.entry_dt),
                "H.伝票処理日": fmt_dt(agg.exit_dt),
                "H.客数（合計）": str(agg.customers),
                "H.小計": str(agg.subtotal),
                "H.総商品数": str(agg.total_qty),
                "D.商品カテゴリ1": "EAT IN",
                "D.商品カテゴリ2": (row.get("部門名") or "").strip(),
                "D.商品": d_item,
                "D.商品コード": product_code,
                "D.商品名": item_name,
                "D.サブメニュー": "",
                "D.価格": str(line_total),
                "D.ベース価格": "",
                "D.オーダーメモ": "",
                "D.オーダー日時": fmt_dt(order_dt),
            }
            w.writerow(out_row)
            written += 1

    print("input :", in_path)
    print("output:", out_path)
    print("tx_count:", len(tx))
    print("rows_written:", written)
    print("rows_skipped_no_item:", skipped_no_item)


if __name__ == "__main__":
    main()

