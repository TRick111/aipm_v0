#!/usr/bin/env python3
"""食べログ「月間ページレポート PC版」HTML を CSV (ロング型) に変換するパーサ。

入力 HTML は単一テーブル (id=dataex-page-pc):
  列: ページ種別 / PV / 構成比 / 備考
  行: ページ種別 (店舗トップ / メニュー / ...) ×  N行
集計期間は1区間 (例: 2025年5月 - 2026年5月) で月別内訳ではない。
そのため出力は「period_start, period_end, page_type, pv, share_percent, note」のロング型。
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_INPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/tabelog/raw_html/access_report_page.html"
)
DEFAULT_OUTPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/tabelog/output/access_report_page.csv"
)

COLUMNS = ["period_start", "period_end", "page_type", "pv", "share_percent", "note"]

# 「2025年5月 - 2026年5月」のような期間表記を YYYY-MM, YYYY-MM に正規化
PERIOD_RE = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*[-–~〜]\s*(\d{4})\s*年\s*(\d{1,2})\s*月")
# 「YYYYMM」→「YYYY-MM」フォールバック用
YYYYMM_RE = re.compile(r"(\d{4})(\d{2})")


def normalize_ym(year: str, month: str) -> str:
    return f"{int(year):04d}-{int(month):02d}"


def extract_period(soup: BeautifulSoup) -> tuple[str, str]:
    # 1) <title> や <h1> から「YYYY年M月 - YYYY年M月」を抽出
    for tag_name in ("title", "h1"):
        tag = soup.find(tag_name)
        if tag and tag.get_text():
            m = PERIOD_RE.search(tag.get_text())
            if m:
                return normalize_ym(m.group(1), m.group(2)), normalize_ym(m.group(3), m.group(4))
    # 2) <select id="report-month-first/last"> の selected option から YYYYMM を取得
    start = end = None
    for sel_id, dest in (("report-month-first", "start"), ("report-month-last", "end")):
        sel = soup.find("select", id=sel_id)
        if not sel:
            continue
        opt = sel.find("option", selected=True) or sel.find("option")
        if not opt:
            continue
        m = YYYYMM_RE.fullmatch(opt.get("value", "").strip())
        if m:
            ym = normalize_ym(m.group(1), m.group(2))
            if dest == "start":
                start = ym
            else:
                end = ym
    if start and end:
        return start, end
    raise ValueError("期間 (YYYY-MM レンジ) を HTML から抽出できませんでした")


def parse_int(text: str) -> int:
    cleaned = re.sub(r"[,\s]", "", text)
    if cleaned == "" or cleaned == "-":
        return 0
    return int(cleaned)


def parse_percent(text: str) -> float:
    # セル内には <span class="bar"> も含まれるため、末尾の "X.X%" を取り出す
    m = re.search(r"([\d.]+)\s*%", text)
    if not m:
        return 0.0
    return float(m.group(1))


def parse_rows(soup: BeautifulSoup, period_start: str, period_end: str) -> list[dict]:
    table = soup.find("table", id="dataex-page-pc")
    if table is None:
        # フォールバック: クラスで検索
        table = soup.find("table", class_="analytics-data")
    if table is None:
        raise ValueError("対象テーブル (id=dataex-page-pc) が見つかりません")

    rows: list[dict] = []
    for tr in table.select("tbody > tr"):
        page_cell = tr.find("td", class_="page")
        access_cell = tr.find("td", class_="access")
        percent_cell = tr.find("td", class_="percent")
        notes_cell = tr.find("td", class_="notes")
        if not (page_cell and access_cell and percent_cell):
            continue
        page_type = page_cell.get_text(strip=True)
        pv = parse_int(access_cell.get_text(strip=True))
        share = parse_percent(percent_cell.get_text(" ", strip=True))
        note = ""
        if notes_cell:
            note = notes_cell.get_text(" ", strip=True).replace("\xa0", "").strip()
        rows.append(
            {
                "period_start": period_start,
                "period_end": period_end,
                "page_type": page_type,
                "pv": pv,
                "share_percent": share,
                "note": note,
            }
        )
    return rows


def main(argv: list[str]) -> int:
    input_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUT
    output_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUTPUT

    if not input_path.exists():
        print(f"[ERROR] input HTML が存在しません: {input_path}", file=sys.stderr)
        return 1

    try:
        html = input_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "lxml")
        period_start, period_end = extract_period(soup)
        rows = parse_rows(soup, period_start, period_end)
    except Exception as exc:
        print(f"[ERROR] パースに失敗: {exc}", file=sys.stderr)
        return 1

    if not rows:
        print("[ERROR] データ行が0件でした", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"output: {output_path}")
    print(f"columns: {','.join(COLUMNS)}")
    print(f"rows: {len(rows)} (期間 {period_start} - {period_end})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
