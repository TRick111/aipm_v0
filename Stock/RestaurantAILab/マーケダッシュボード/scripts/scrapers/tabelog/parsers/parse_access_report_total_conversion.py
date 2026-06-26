#!/usr/bin/env python3
"""
食べログ店舗管理画面「来店指標（TEL数・ネット予約数など）」HTML -> CSV パーサ.

入力: access_report_total_conversion.html
出力: 月別ワイド形式 CSV
列  : 年月, 通話成立数, ネット予約組数, 地図印刷PV, 全体PV
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


DEFAULT_INPUT = (
    Path(__file__).resolve().parent.parent
    / "raw_html"
    / "access_report_total_conversion.html"
)
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "output"
    / "access_report_total_conversion.csv"
)

HEADERS = ["年月", "通話成立数", "ネット予約組数", "地図印刷PV", "全体PV"]

YM_RE = re.compile(r"^\s*(\d{4})[-/](\d{1,2})\s*$")


def to_int(s: str):
    """3桁区切り除去, '-' は空欄, 数値は int 化."""
    if s is None:
        return ""
    t = s.strip().replace(",", "").replace("\xa0", "")
    if t in ("", "-", "ー", "—"):
        return ""
    try:
        return int(t)
    except ValueError:
        try:
            return float(t)
        except ValueError:
            return ""


def normalize_ym(raw: str) -> str:
    m = YM_RE.match(raw or "")
    if not m:
        raise ValueError(f"年月の形式が不正: {raw!r}")
    year, month = m.group(1), int(m.group(2))
    return f"{year}-{month:02d}"


def parse(html_path: Path) -> list[dict]:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", id="data-cvr-alldevice")
    if table is None:
        raise RuntimeError("対象テーブル (#data-cvr-alldevice) が見つかりません")

    tbody = table.find("tbody")
    if tbody is None:
        raise RuntimeError("tbody が見つかりません")

    rows: list[dict] = []
    for tr in tbody.find_all("tr", recursive=False):
        th = tr.find("th", attrs={"scope": "row"})
        if th is None:
            # device-more 等のサマリ行はスキップ
            continue

        ym = normalize_ym(th.get_text(strip=True))
        tds = tr.find_all("td", recursive=False)
        # 期待順序: [総合, TEL通話成立数, ネット予約組数, 地図印刷PV, 全体PV, PC, SP, アプリ]
        if len(tds) < 5:
            raise RuntimeError(
                f"{ym}: td が不足しています (got {len(tds)}, expected >= 5)"
            )

        rows.append({
            "年月": ym,
            "通話成立数": to_int(tds[1].get_text()),
            "ネット予約組数": to_int(tds[2].get_text()),
            "地図印刷PV": to_int(tds[3].get_text()),
            "全体PV": to_int(tds[4].get_text()),
        })

    if not rows:
        raise RuntimeError("データ行が 0 件でした")

    return rows


def write_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # UTF-8 BOM なし
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        in_path, out_path = DEFAULT_INPUT, DEFAULT_OUTPUT
    elif len(argv) == 3:
        in_path = Path(argv[1])
        out_path = Path(argv[2])
    else:
        print(
            "Usage: parse_access_report_total_conversion.py <input.html> <output.csv>",
            file=sys.stderr,
        )
        return 1

    if not in_path.exists():
        print(f"ERROR: 入力ファイルが存在しません: {in_path}", file=sys.stderr)
        return 1

    try:
        rows = parse(in_path)
        write_csv(rows, out_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: {out_path}")
    print(f"  rows   : {len(rows)}")
    print(f"  columns: {HEADERS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
