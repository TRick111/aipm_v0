#!/usr/bin/env python3
"""
Dashboard Data Pipeline
=======================
Dashboard APIを使って POS CSVアップロード & rawdata.csv エクスポートを行うCLIスクリプト。

Usage:
  python dashboard_data_pipeline.py upload  --store BFA --file "0_downloads/20260209-20260215-BAR FIVE Arrows.csv"
  python dashboard_data_pipeline.py export  --store BFA --start-date 2026-02-09 --end-date 2026-02-15
  python dashboard_data_pipeline.py sync    --start-date 2026-02-09 --end-date 2026-02-15 --downloads-dir 0_downloads
  python dashboard_data_pipeline.py incremental-export --store BFA --end-date 2026-02-22
  python dashboard_data_pipeline.py incremental-export --end-date 2026-02-22   # 全店舗
"""

import argparse
import csv
import io
import json
import os
import re
import sys
from calendar import monthrange
from datetime import datetime, timedelta

import requests

# ──────────────────────────────────────────────
# 店舗設定
# ──────────────────────────────────────────────

STORES = {
    "BFA": {
        "store_code": "test-003",
        "store_name": "BAR FIVE Arrows",
        "pos_type": "airregi",
        "file_pattern": "BAR FIVE Arrows",
    },
    "BBC": {
        "store_code": "bginza-001",
        "store_name": "別天地　銀座",
        "pos_type": "dinii",
        "file_pattern": "別天地 銀座",
    },
    "麻布しき": {
        "store_code": "shiki-001",
        "store_name": "麻布しき",
        "pos_type": "usenregi",
        "file_pattern": "麻布しき",
    },
    "キーポイント": {
        "store_code": "kp-001",
        "store_name": "かめや駅前店",
        "pos_type": "airregi",
        "file_pattern": "かめや駅前店",
    },
}

# USENレジ カラムマッピング
USEN_MAPPING = {
    "accountId": "H.伝票番号",
    "exitDateTime": "H.伝票処理日",
    "dayOfWeek": "H.曜日",
    "totalAmount": "H.小計",
    "customerCount": "H.客数（合計）",
    "itemCount": "H.総商品数",
    "category1": "D.商品カテゴリ1",
    "category2": "D.商品カテゴリ2",
    "menuName": "D.商品",
    "price": "D.価格",
    "quantity": "D.数量",
    "orderedAt": "D.オーダー日時",
}

DEFAULT_BASE_URL = "http://127.0.0.1:3000"
ADMIN_STORE_CODE = "admin"
ADMIN_PASSWORD = "admin2024"

# rawdata.csv が存在しない場合のデフォルト開始日（開業以来の全データ取得用）
DEFAULT_START_DATE = "2024-01-01"

RAWDATA_COLUMNS = [
    "store_code", "store_name", "account_id", "entry_at", "exit_at",
    "day_of_week", "account_total", "customer_count", "item_count",
    "has_reservation", "is_course", "menu_name", "price", "quantity",
    "subtotal", "category1", "ordered_at", "cost_rate",
]


# ──────────────────────────────────────────────
# API Client
# ──────────────────────────────────────────────

class DashboardClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def login(self):
        resp = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"storeCode": ADMIN_STORE_CODE, "password": ADMIN_PASSWORD},
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError(f"Login failed: {data.get('error', {}).get('message', 'unknown')}")
        print(f"  Logged in as admin")

    # ── Upload ──

    def _check_response(self, resp):
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise RuntimeError(f"HTTP {resp.status_code}: {body}")
        return resp.json()

    def upload_airregi(self, store_code: str, csv_path: str):
        with open(csv_path, "rb") as f:
            files = {"file": (os.path.basename(csv_path), f, "text/csv")}
            form = {"storeId": store_code, "isAirRegi": "true"}
            resp = self.session.post(f"{self.base_url}/api/upload", files=files, data=form)
        return self._check_response(resp)

    def upload_dinii(self, store_code: str, orders_path: str, transactions_path: str):
        with open(orders_path, "rb") as fo, open(transactions_path, "rb") as ft:
            files = {
                "file": (os.path.basename(orders_path), fo, "text/csv"),
                "transactionsFile": (os.path.basename(transactions_path), ft, "text/csv"),
            }
            form = {"storeId": store_code, "isDinii": "true"}
            resp = self.session.post(f"{self.base_url}/api/upload", files=files, data=form)
        return self._check_response(resp)

    def upload_usenregi(self, store_code: str, csv_path: str):
        skip_rows = detect_usen_skip_rows(csv_path)
        mapping = dict(USEN_MAPPING)
        # H.小計 or H.伝票金額 の動的検出
        actual_header = get_usen_header_columns(csv_path, skip_rows)
        if "H.伝票金額" in actual_header and "H.小計" not in actual_header:
            mapping["totalAmount"] = "H.伝票金額"
        with open(csv_path, "rb") as f:
            files = {"file": (os.path.basename(csv_path), f, "text/csv")}
            form = {
                "storeId": store_code,
                "isUsenRegi": "true",
                "skipRows": str(skip_rows),
                "mapping": json.dumps(mapping),
            }
            resp = self.session.post(f"{self.base_url}/api/upload", files=files, data=form)
        return self._check_response(resp)

    # ── Export ──

    def export_data(self, store_code: str, month: str, start_date: str, end_date: str):
        params = {"storeId": store_code, "startDate": start_date, "endDate": end_date}
        resp = self.session.get(f"{self.base_url}/api/data/{month}", params=params)
        return self._check_response(resp)


# ──────────────────────────────────────────────
# USEN helpers
# ──────────────────────────────────────────────

def _read_file_text(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8", "shift_jis", "cp932"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode("utf-8", errors="replace")


def detect_usen_skip_rows(csv_path: str) -> int:
    """ヘッダー行までの非空行数を返す（API側の Papa.parse skipEmptyLines:true に合わせる）"""
    text = _read_file_text(csv_path)
    non_empty_index = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if "H.伝票番号" in stripped or "H.年表番号" in stripped:
            return non_empty_index
        non_empty_index += 1
    raise ValueError(f"USENレジ ヘッダー行が見つかりません: {csv_path}")


def get_usen_header_columns(csv_path: str, skip_rows: int) -> list[str]:
    text = _read_file_text(csv_path)
    lines = text.split("\n")
    if skip_rows >= len(lines):
        return []
    header_line = lines[skip_rows]
    reader = csv.reader(io.StringIO(header_line))
    return [col.strip() for col in next(reader, [])]


# ──────────────────────────────────────────────
# Export → rawdata.csv 変換
# ──────────────────────────────────────────────

def sales_data_to_rawdata(sales_data: list[dict], store_code: str, store_name: str) -> list[dict]:
    rows = []
    for item in sales_data:
        subtotal = round(float(item.get("price", 0)) * int(item.get("quantity", 0)))
        rows.append({
            "store_code": store_code,
            "store_name": store_name,
            "account_id": item.get("accountId", ""),
            "entry_at": item.get("visitDateTime", ""),
            "exit_at": item.get("exitDateTime", ""),
            "day_of_week": item.get("dayOfWeek", ""),
            "account_total": item.get("totalAmount", ""),
            "customer_count": item.get("customerCount", ""),
            "item_count": item.get("itemCount", ""),
            "has_reservation": "t" if item.get("hasReservation") else "f",
            "is_course": "t" if item.get("isCourse") else "f",
            "menu_name": item.get("menuName", ""),
            "price": item.get("price", ""),
            "quantity": item.get("quantity", ""),
            "subtotal": subtotal,
            "category1": item.get("category1", ""),
            "ordered_at": item.get("orderedAt", ""),
            "cost_rate": "",
        })
    return rows


def write_rawdata_csv(rows: list[dict], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAWDATA_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows)} rows → {output_path}")


# ──────────────────────────────────────────────
# sync 用: ダウンロードファイル自動検出
# ──────────────────────────────────────────────

def find_download_files(downloads_dir: str, store_key: str, start_date: str, end_date: str) -> dict:
    """ダウンロードディレクトリから対象店舗のファイルを検索する"""
    cfg = STORES[store_key]
    pattern = cfg["file_pattern"]
    date_prefix = f"{start_date.replace('-', '')}-{end_date.replace('-', '')}"

    if cfg["pos_type"] == "dinii":
        orders = None
        transactions = None
        for fname in os.listdir(downloads_dir):
            if pattern in fname and date_prefix in fname:
                if fname.endswith("-orders.csv"):
                    orders = os.path.join(downloads_dir, fname)
                elif fname.endswith("-transactions.csv"):
                    transactions = os.path.join(downloads_dir, fname)
        if orders and transactions:
            return {"orders": orders, "transactions": transactions}
        return {}

    # airregi / usenregi: 単一ファイル
    for fname in os.listdir(downloads_dir):
        if pattern in fname and date_prefix in fname and fname.endswith(".csv"):
            return {"file": os.path.join(downloads_dir, fname)}

    # date_prefix が一致しない場合、同月のファイルを探す（例: 20260201-20260228）
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    month_prefix = start_dt.strftime("%Y%m")
    for fname in os.listdir(downloads_dir):
        if pattern in fname and fname.endswith(".csv"):
            # ファイル名の日付範囲が同月を含むか
            m = re.search(r"(\d{8})-(\d{8})", fname)
            if m and m.group(1).startswith(month_prefix):
                return {"file": os.path.join(downloads_dir, fname)}

    return {}


# ──────────────────────────────────────────────
# サブコマンド: upload
# ──────────────────────────────────────────────

def cmd_upload(args):
    cfg = STORES[args.store]
    client = DashboardClient(args.base_url)
    client.login()

    pos_type = cfg["pos_type"]
    print(f"  Uploading {args.store} ({cfg['store_code']}) as {pos_type}...")

    if pos_type == "airregi":
        result = client.upload_airregi(cfg["store_code"], args.file)
    elif pos_type == "dinii":
        if not args.transactions_file:
            sys.exit("Error: Dinii requires --transactions-file")
        result = client.upload_dinii(cfg["store_code"], args.file, args.transactions_file)
    elif pos_type == "usenregi":
        result = client.upload_usenregi(cfg["store_code"], args.file)
    else:
        sys.exit(f"Error: Unknown POS type: {pos_type}")

    if result.get("success"):
        months = result.get("data", {}).get("months", [])
        for m in months:
            s = m.get("stats", {})
            print(f"  {m['month']}: inserted={s.get('inserted',0)}, skipped={s.get('skipped',0)}, errors={s.get('errors',0)}")
        print("  Upload OK")
    else:
        err = result.get("error", {})
        sys.exit(f"Upload failed: {err.get('message', json.dumps(err))}")


# ──────────────────────────────────────────────
# サブコマンド: export
# ──────────────────────────────────────────────

def cmd_export(args):
    cfg = STORES[args.store]
    client = DashboardClient(args.base_url)
    client.login()

    month = args.start_date[:7]  # YYYY-MM
    print(f"  Exporting {args.store} ({cfg['store_code']}) {args.start_date} ~ {args.end_date}...")

    result = client.export_data(cfg["store_code"], month, args.start_date, args.end_date)
    if not result.get("success"):
        err = result.get("error", {})
        sys.exit(f"Export failed: {err.get('message', json.dumps(err))}")

    sales_data = result["data"]["salesData"]
    rows = sales_data_to_rawdata(sales_data, cfg["store_code"], cfg["store_name"])

    output_dir = args.output_dir or f"1_input/{args.store}"
    output_path = os.path.join(output_dir, "rawdata.csv")
    write_rawdata_csv(rows, output_path)
    print(f"  Export OK: {len(rows)} records")


# ──────────────────────────────────────────────
# サブコマンド: sync (upload + export 全店舗)
# ──────────────────────────────────────────────

def cmd_sync(args):
    client = DashboardClient(args.base_url)
    client.login()

    stores_to_process = list(STORES.keys()) if not args.store else [args.store]
    downloads_dir = args.downloads_dir or "0_downloads"

    for store_key in stores_to_process:
        cfg = STORES[store_key]
        print(f"\n{'='*50}")
        print(f"  [{store_key}] {cfg['store_name']} ({cfg['store_code']})")
        print(f"{'='*50}")

        # ── Upload ──
        files = find_download_files(downloads_dir, store_key, args.start_date, args.end_date)
        if not files:
            print(f"  SKIP: ダウンロードファイルが見つかりません ({downloads_dir})")
            continue

        pos_type = cfg["pos_type"]
        try:
            if pos_type == "airregi":
                print(f"  Upload: {files['file']}")
                result = client.upload_airregi(cfg["store_code"], files["file"])
            elif pos_type == "dinii":
                print(f"  Upload: {files['orders']} + {files['transactions']}")
                result = client.upload_dinii(cfg["store_code"], files["orders"], files["transactions"])
            elif pos_type == "usenregi":
                print(f"  Upload: {files['file']}")
                result = client.upload_usenregi(cfg["store_code"], files["file"])
            else:
                print(f"  SKIP: Unknown POS type {pos_type}")
                continue
        except Exception as e:
            print(f"  Upload ERROR: {e}")
            continue

        if result.get("success"):
            for m in result.get("data", {}).get("months", []):
                s = m.get("stats", {})
                print(f"    {m['month']}: inserted={s.get('inserted',0)}, skipped={s.get('skipped',0)}, errors={s.get('errors',0)}")
        else:
            err = result.get("error", {})
            print(f"  Upload FAILED: {err.get('message', '')}")
            continue

        # ── Export ──
        month = args.start_date[:7]
        try:
            export_result = client.export_data(cfg["store_code"], month, args.start_date, args.end_date)
        except Exception as e:
            print(f"  Export ERROR: {e}")
            continue

        if not export_result.get("success"):
            err = export_result.get("error", {})
            print(f"  Export FAILED: {err.get('message', '')}")
            continue

        sales_data = export_result["data"]["salesData"]
        rows = sales_data_to_rawdata(sales_data, cfg["store_code"], cfg["store_name"])

        output_dir = f"1_input/{store_key}"
        output_path = os.path.join(output_dir, "rawdata.csv")
        write_rawdata_csv(rows, output_path)

    print(f"\n{'='*50}")
    print("  Sync complete")
    print(f"{'='*50}")


# ──────────────────────────────────────────────
# incremental-export 用ヘルパー
# ──────────────────────────────────────────────

def get_latest_date_in_rawdata(csv_path: str) -> str | None:
    """既存 rawdata.csv の entry_at カラムから最新日付(YYYY-MM-DD)を返す。ファイルがなければ None。"""
    if not os.path.exists(csv_path):
        return None
    max_date = None
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry_at = row.get("entry_at", "")
            if len(entry_at) >= 10:
                date_str = entry_at[:10]  # YYYY-MM-DD
                if max_date is None or date_str > max_date:
                    max_date = date_str
    return max_date


def generate_month_range(start_date: str, end_date: str) -> list[str]:
    """start_date〜end_date に含まれる全月を YYYY-MM のリストで返す。"""
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(day=1)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(day=1)
    months = []
    current = start
    while current <= end:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def fetch_all_months(client: DashboardClient, store_code: str, start_date: str, end_date: str) -> list[dict]:
    """start_date〜end_date の全月を順番に API 呼び出しし、salesData を結合して返す。"""
    months = generate_month_range(start_date, end_date)
    all_sales = []
    for month in months:
        year, mon = map(int, month.split("-"))
        _, last_day = monthrange(year, mon)
        month_first = f"{month}-01"
        month_last = f"{month}-{last_day:02d}"
        fetch_start = max(start_date, month_first)
        fetch_end = min(end_date, month_last)
        try:
            result = client.export_data(store_code, month, fetch_start, fetch_end)
            if result.get("success"):
                sales = result.get("data", {}).get("salesData", [])
                if sales:
                    print(f"    {month}: {len(sales)} records")
                    all_sales.extend(sales)
            # success=false は月データなしとして静かにスキップ
        except RuntimeError as e:
            # HTTP 404 はデータなしなのでスキップ（ログ不要）
            if "404" not in str(e):
                print(f"    {month}: Error - {e}")
        except Exception as e:
            print(f"    {month}: Error - {e}")
    return all_sales


def append_rawdata_csv(rows: list[dict], output_path: str):
    """既存 rawdata.csv にヘッダーなしで追記する。"""
    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAWDATA_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
    print(f"  Appended {len(rows)} rows → {output_path}")


# ──────────────────────────────────────────────
# サブコマンド: incremental-export
# ──────────────────────────────────────────────

def cmd_incremental_export(args):
    """既存 rawdata.csv の続きからデータを取得してマージする。ファイルがなければ全期間を取得。"""
    stores_to_process = list(STORES.keys()) if not args.store else [args.store]
    client = DashboardClient(args.base_url)
    client.login()

    for store_key in stores_to_process:
        cfg = STORES[store_key]
        output_dir = args.output_dir or f"1_input/{store_key}"
        output_path = os.path.join(output_dir, "rawdata.csv")

        print(f"\n{'='*50}")
        print(f"  [{store_key}] {cfg['store_name']} ({cfg['store_code']})")
        print(f"{'='*50}")

        # Step 1: 既存データの最終日付を確認
        latest_date = get_latest_date_in_rawdata(output_path)

        if latest_date:
            next_date = (datetime.strptime(latest_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"  Existing data up to: {latest_date}")
            print(f"  Fetching from: {next_date}")
        else:
            next_date = args.start_date or DEFAULT_START_DATE
            print(f"  No existing data. Fetching from: {next_date}")

        if next_date > args.end_date:
            print(f"  Already up to date (latest: {latest_date}, target: {args.end_date})")
            continue

        # Step 2: 月ごとにAPIからデータ取得
        print(f"  Period: {next_date} ~ {args.end_date}")
        all_sales = fetch_all_months(client, cfg["store_code"], next_date, args.end_date)

        if not all_sales:
            print(f"  No new data found")
            continue

        rows = sales_data_to_rawdata(all_sales, cfg["store_code"], cfg["store_name"])

        # Step 3: 既存ファイルに追記 or 新規作成
        if latest_date and os.path.exists(output_path):
            append_rawdata_csv(rows, output_path)
        else:
            write_rawdata_csv(rows, output_path)

        print(f"  Total new records: {len(rows)}")

    print(f"\n{'='*50}")
    print("  Incremental export complete")
    print(f"{'='*50}")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Dashboard Data Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    base_url_kwargs = {"default": DEFAULT_BASE_URL,
                       "help": f"Dashboard base URL (default: {DEFAULT_BASE_URL})"}

    # upload
    p_upload = subparsers.add_parser("upload", help="Upload POS CSV to Dashboard")
    p_upload.add_argument("--base-url", **base_url_kwargs)
    p_upload.add_argument("--store", required=True, choices=STORES.keys(), help="Store key")
    p_upload.add_argument("--file", required=True, help="CSV file path")
    p_upload.add_argument("--transactions-file", help="Transactions CSV (Dinii only)")

    # export
    p_export = subparsers.add_parser("export", help="Export rawdata.csv from Dashboard")
    p_export.add_argument("--base-url", **base_url_kwargs)
    p_export.add_argument("--store", required=True, choices=STORES.keys(), help="Store key")
    p_export.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    p_export.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    p_export.add_argument("--output-dir", help="Output directory (default: 1_input/<store>)")

    # sync
    p_sync = subparsers.add_parser("sync", help="Upload + Export for all stores")
    p_sync.add_argument("--base-url", **base_url_kwargs)
    p_sync.add_argument("--store", choices=STORES.keys(), help="Single store (default: all)")
    p_sync.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    p_sync.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    p_sync.add_argument("--downloads-dir", default="0_downloads", help="Downloads directory")

    # incremental-export
    p_incr = subparsers.add_parser("incremental-export",
                                   help="Incrementally export rawdata.csv (append new data)")
    p_incr.add_argument("--base-url", **base_url_kwargs)
    p_incr.add_argument("--store", choices=STORES.keys(),
                        help="Single store (default: all stores)")
    p_incr.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    p_incr.add_argument("--start-date",
                        help=f"Start date when no existing data (default: {DEFAULT_START_DATE})")
    p_incr.add_argument("--output-dir",
                        help="Output directory (default: 1_input/<store>)")

    args = parser.parse_args()

    if args.command == "upload":
        cmd_upload(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "incremental-export":
        cmd_incremental_export(args)


if __name__ == "__main__":
    main()
