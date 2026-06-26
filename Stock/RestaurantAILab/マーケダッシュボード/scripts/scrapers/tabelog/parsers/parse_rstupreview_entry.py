#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
食べログ店舗管理画面「お店が選ぶ ピックアップ！口コミ」の選択ページ
(rstupreview_entry) の HTML を CSV にパースする。

カード構造: <div class="rvw-item js-rvw-clickable-area"> ... </div>
1ページ最大 20 件。来店日 (YYYY/MM 訪問) を YYYY-MM-01 として正規化する。

CLI:
    python3 parse_rstupreview_entry.py [input.html] [output.csv]
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_INPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/tabelog/raw_html/rstupreview_entry.html"
)
DEFAULT_OUTPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/tabelog/output/rstupreview_entry.csv"
)

VISIT_RE = re.compile(r"(\d{4})\s*/\s*(\d{1,2})\s*訪問")
RATING_CLASS_RE = re.compile(r"c-rating-v2--val(\d+)")


def normalize_visit_date(text: str) -> str:
    """'2026/01訪問' -> '2026-01-01'。失敗時は空文字。"""
    if not text:
        return ""
    m = VISIT_RE.search(text)
    if not m:
        return ""
    year = int(m.group(1))
    month = int(m.group(2))
    try:
        return datetime(year, month, 1).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def extract_rating(card) -> str:
    """総合評価 (例: '3.5')。<b class="c-rating-v2__val ..."> から取得。"""
    total = card.select_one("p.rvw-item__ratings-total")
    if total:
        val = total.select_one("b.c-rating-v2__val")
        if val:
            t = val.get_text(strip=True)
            if t and t != "-":
                return t
        # フォールバック: class 名の val35 -> 3.5
        cls = " ".join(total.get("class", []))
        m = RATING_CLASS_RE.search(cls)
        if m:
            raw = m.group(1)
            if raw == "0":
                return ""
            # "35" -> "3.5", "50" -> "5.0"
            if len(raw) >= 2:
                return f"{raw[:-1]}.{raw[-1]}"
    return ""


def extract_reviewer(card) -> str:
    el = card.select_one('span[property="v:reviewer"]')
    return el.get_text(strip=True) if el else ""


def extract_visit_date(card) -> str:
    el = card.select_one("div.rvw-item__date")
    if not el:
        return ""
    return normalize_visit_date(el.get_text(" ", strip=True))


def extract_comment(card, limit: int = 100) -> str:
    el = card.select_one("div.rvw-item__rvw-comment")
    if not el:
        return ""
    text = el.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.rvw-item.js-rvw-clickable-area")
    rows: list[dict] = []
    for card in cards:
        rows.append(
            {
                "来店日": extract_visit_date(card),
                "総合評価": extract_rating(card),
                "投稿者": extract_reviewer(card),
                "本文先頭": extract_comment(card, 100),
            }
        )
    return rows


def main(argv: list[str]) -> int:
    input_path = Path(argv[1]) if len(argv) >= 2 else DEFAULT_INPUT
    output_path = Path(argv[2]) if len(argv) >= 3 else DEFAULT_OUTPUT

    if not input_path.exists():
        print(f"[ERROR] input not found: {input_path}", file=sys.stderr)
        return 1

    try:
        html = input_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] failed to read input: {e}", file=sys.stderr)
        return 1

    try:
        rows = parse(html)
    except Exception as e:
        print(f"[ERROR] parse failed: {e}", file=sys.stderr)
        return 1

    if not rows:
        print("[ERROR] no review cards found", file=sys.stderr)
        return 1

    fieldnames = ["来店日", "総合評価", "投稿者", "本文先頭"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"[ERROR] failed to write csv: {e}", file=sys.stderr)
        return 1

    visit_dates = [r["来店日"] for r in rows if r["来店日"]]
    oldest = min(visit_dates) if visit_dates else "(none)"
    newest = max(visit_dates) if visit_dates else "(none)"

    print(f"output: {output_path}")
    print(f"rows  : {len(rows)}")
    print(f"cols  : {', '.join(fieldnames)}")
    print(f"visit : oldest={oldest}  newest={newest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
