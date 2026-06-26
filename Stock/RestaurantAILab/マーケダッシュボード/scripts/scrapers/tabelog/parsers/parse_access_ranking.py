#!/usr/bin/env python3
"""食べログ「エリアのアクセス数ランキング」HTML -> CSV パーサ.

マーケダッシュボードの「競合内ポジション」指標用。
- エリア名はページ <title> から抽出（例: "岡崎エリアのアクセス数ランキング" -> "岡崎"）。
- 自店舗の行は `tr#my-ranking` で識別し、`is_own_shop` を true/false で立てる。
"""

import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_INPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/tabelog/raw_html/access_ranking.html"
)
DEFAULT_OUTPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/tabelog/output/access_ranking.csv"
)

HEADER = ["エリア", "順位", "店舗名", "店舗エリア", "ジャンル", "アクセス数", "前月比", "is_own_shop"]

TITLE_AREA_RE = re.compile(r"^\s*(.+?)エリアのアクセス数ランキング")
RANK_RE = re.compile(r"(\d+)")


def to_int(text: str) -> int:
    s = (text or "").strip().replace(",", "")
    if s in ("", "-", "ー", "−"):
        return 0
    return int(s)


def extract_area(soup: BeautifulSoup) -> str:
    title = soup.find("title")
    if title is None or not title.get_text(strip=True):
        raise ValueError("<title> が見つかりません")
    m = TITLE_AREA_RE.match(title.get_text(strip=True))
    if not m:
        raise ValueError(f"タイトルからエリア名を抽出できません: {title.get_text(strip=True)!r}")
    return m.group(1)


def parse(html: str):
    soup = BeautifulSoup(html, "lxml")
    area = extract_area(soup)

    table = soup.find("table", id="data-access-ranking") or soup.find("table")
    if table is None:
        raise ValueError("ランキングテーブルが見つかりません")

    tbody = table.find("tbody") or table

    rows = []
    own_rank = None
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue

        rank_text = tds[0].get_text(" ", strip=True)
        rank_m = RANK_RE.search(rank_text)
        if not rank_m:
            continue
        rank = int(rank_m.group(1))

        shop_name = tds[1].get_text(" ", strip=True)
        shop_area = tds[2].get_text(" ", strip=True)
        genre = tds[3].get_text(" ", strip=True)
        access = to_int(tds[4].get_text(" ", strip=True))
        compare = tds[5].get_text(" ", strip=True) if len(tds) >= 6 else ""

        is_own = tr.get("id") == "my-ranking"
        if is_own:
            own_rank = rank

        rows.append([
            area,
            rank,
            shop_name,
            shop_area,
            genre,
            access,
            compare,
            "true" if is_own else "false",
        ])

    return area, rows, own_rank


def main(argv):
    in_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUT
    out_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUTPUT

    try:
        html = in_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[ERROR] HTML読込失敗: {in_path}: {e}", file=sys.stderr)
        return 1

    try:
        area, rows, own_rank = parse(html)
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
    print(f"エリア: {area}")
    print(f"ヘッダ: {HEADER}")
    print(f"行数: {len(rows)}")
    print(f"自店舗の順位: {own_rank if own_rank is not None else '(検出できず)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
