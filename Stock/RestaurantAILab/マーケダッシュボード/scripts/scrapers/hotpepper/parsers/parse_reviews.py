#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ホットペッパーグルメ店舗管理画面「口コミ 一覧」(ccm010/showReportListAllForAuth)
の HTML を CSV にパースする。

1ページ最大 20 件。各クチコミは <table class="style01 ..."> 単位で繰り返され、
固有の <span id="contributionDateN"> (投稿日) を含む内側テーブルを 1 件とみなす。

CLI:
    python3 parse_reviews.py [input.html] [output.csv]
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_INPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/hotpepper/raw_html/reviews.html"
)
DEFAULT_OUTPUT = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/マーケダッシュボード/"
    "scripts/scrapers/hotpepper/output/reviews.csv"
)

DATE_RE = re.compile(r"(\d{4})\s*/\s*(\d{1,2})\s*/\s*(\d{1,2})")
STAR_RE = re.compile(r"★\s*([0-9]+(?:\.[0-9])?)")
MEAL_RE = re.compile(r"\[(ランチ|ディナー)\]")
LAST_PROC_RE = re.compile(r"最終審査日\s*" + DATE_RE.pattern)


def normalize_date(text: str) -> str:
    """'2026/06/15' -> '2026-06-15'。失敗時は空文字。"""
    if not text:
        return ""
    m = DATE_RE.search(text)
    if not m:
        return ""
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def extract_post_date(card) -> str:
    el = card.select_one('span[id^="contributionDate"]')
    return normalize_date(el.get_text(strip=True)) if el else ""


def extract_reviewer(card) -> str:
    # hidden input が最も信頼できる (表示名と一致)
    h = card.select_one('input[id^="nicname"]')
    if h and h.get("value"):
        return h.get("value").strip()
    a = card.select_one("td.reportContent a")
    return a.get_text(strip=True) if a else ""


def extract_rating(card) -> str:
    """★N または ★N.N を float 文字列で返す。"""
    td = card.select_one("td.reportContent")
    if not td:
        return ""
    text = td.get_text(" ", strip=True)
    m = STAR_RE.search(text)
    if not m:
        return ""
    try:
        return f"{float(m.group(1))}"
    except ValueError:
        return ""


def extract_comment(card, limit: int = 100) -> str:
    """フル本文 (hidden reportText) を優先し、なければ td テキストの先頭をフォールバック。"""
    h = card.select_one('input[id^="reportText"]')
    if h:
        text = (h.get("value") or "").strip()
        if text:
            text = re.sub(r"\s+", " ", text)
            return text[:limit]
    td = card.select_one("td.reportContent")
    if not td:
        return ""
    text = td.get_text(" ", strip=True)
    # 先頭の "投稿者さん ★N" 等を除去するため、★行の後ろを採用する
    parts = text.split("\n")
    text = " ".join(parts).strip()
    text = re.sub(r"^.*?★[0-9.]+\s*", "", text)
    text = re.sub(r"・・・.*$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def extract_meal_type(card) -> str:
    info = card.select_one("td.reportInfo.ksumi")
    if not info:
        return ""
    m = MEAL_RE.search(info.get_text(" ", strip=True))
    return m.group(1) if m else ""


def extract_last_processing_date(card) -> str:
    el = card.select_one("span.lastProcessingDate")
    if not el:
        return ""
    m = LAST_PROC_RE.search(el.get_text(" ", strip=True))
    if not m:
        return ""
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def extract_review_no(card) -> str:
    """ピックアップボタンの onclick から 20260622A02300 形式の RN を取得。"""
    btn = card.select_one("input.pickupButton")
    if not btn:
        return ""
    onclick = btn.get("onclick", "")
    m = re.search(r"showPickupModal\('([^']+)'", onclick)
    return m.group(1) if m else ""


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    # contributionDateN を含む table を 1 件のレビューとみなす
    rows: list[dict] = []
    for span in soup.select('span[id^="contributionDate"]'):
        # ピックアップモーダル用の hidden span (pickupContributionDate) は除外
        sid = span.get("id", "")
        if not re.match(r"contributionDate\d+$", sid):
            continue
        card = span.find_parent("table")
        if card is None:
            continue
        rows.append(
            {
                "投稿日": extract_post_date(card),
                "総合評価": extract_rating(card),
                "投稿者": extract_reviewer(card),
                "利用シーン": extract_meal_type(card),
                "最終審査日": extract_last_processing_date(card),
                "口コミID": extract_review_no(card),
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
        print("[ERROR] no review entries found", file=sys.stderr)
        return 1

    fieldnames = ["投稿日", "総合評価", "投稿者", "利用シーン", "最終審査日", "口コミID", "本文先頭"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"[ERROR] failed to write csv: {e}", file=sys.stderr)
        return 1

    dates = [r["投稿日"] for r in rows if r["投稿日"]]
    oldest = min(dates) if dates else "(none)"
    newest = max(dates) if dates else "(none)"

    print(f"output: {output_path}")
    print(f"rows  : {len(rows)}")
    print(f"cols  : {', '.join(fieldnames)}")
    print(f"post  : oldest={oldest}  newest={newest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
