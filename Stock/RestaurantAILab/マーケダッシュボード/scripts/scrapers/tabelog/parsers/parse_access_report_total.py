#!/usr/bin/env python3
"""食べログ「アクセス数レポート（直近1ヶ月）」HTML -> CSV パーサ."""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_INPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/tabelog/raw_html/access_report_total.html"
)
DEFAULT_OUTPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/tabelog/output/access_report_total.csv"
)

HEADER = ["日付", "曜日", "PC", "スマホ", "アプリ", "総合"]

# 例: "2026-05-26 (火)"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*\(([^)]+)\)")


def to_int(text: str) -> int:
    s = text.strip().replace(",", "")
    if s in ("", "-", "ー", "−"):
        return 0
    return int(s)


def parse(html: str) -> list[list]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if table is None:
        raise ValueError("table 要素が見つかりません")

    rows: list[list] = []
    tbody = table.find("tbody") or table
    for tr in tbody.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if len(cells) != 5:
            continue
        m = DATE_RE.search(cells[0])
        if not m:
            # 「合計」行などはスキップ
            continue
        date_str, weekday = m.group(1), m.group(2)
        # 日付フォーマット検証
        datetime.strptime(date_str, "%Y-%m-%d")
        rows.append([
            date_str,
            weekday,
            to_int(cells[1]),
            to_int(cells[2]),
            to_int(cells[3]),
            to_int(cells[4]),
        ])
    return rows


def main(argv: list[str]) -> int:
    in_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUT
    out_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUTPUT

    try:
        html = in_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[ERROR] HTML読込失敗: {in_path}: {e}", file=sys.stderr)
        return 1

    try:
        rows = parse(html)
    except Exception as e:
        print(f"[ERROR] パース失敗: {e}", file=sys.stderr)
        return 1

    if not rows:
        print("[ERROR] 抽出行が0件です", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)

    print(f"出力: {out_path}")
    print(f"ヘッダ: {HEADER}")
    print(f"行数: {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
