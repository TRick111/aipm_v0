#!/usr/bin/env python3
"""
食べログ口コミ取得スクリプト

Playwright で店舗管理画面にログインし、口コミ返信ページのHTMLを取得。
BeautifulSoup でパースして CSV に出力する。

Usage:
    python tabelog_reviews.py --store bfa
    python tabelog_reviews.py --all
    python tabelog_reviews.py --store bfa --week 2026-W16
    python tabelog_reviews.py --store bfa --headed
    python tabelog_reviews.py --store bfa -o /path/to/output/
"""

import argparse
import csv
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------

LOGIN_URL = "https://owner.tabelog.com/owner_account/login"
REPLY_TOP_URL = "https://owner.tabelog.com/owner_rst/reply_top"
DEFAULT_CONFIG = Path(__file__).parent / "tabelog_config.yaml"


def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_store_config(config: dict, store_id: str) -> dict:
    for store in config["stores"]:
        if store["id"] == store_id:
            return store
    raise ValueError(f"Store '{store_id}' not found in config")


# ---------------------------------------------------------------------------
# Playwright: ログイン → HTML取得 → コンテキスト破棄
# ---------------------------------------------------------------------------

def fetch_reviews_html(store: dict, headless: bool = True) -> list[str]:
    """1店舗分の口コミページHTMLを全ページ取得して返す。"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # --- ログイン ---
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        page.fill("#login_id", store["owner_login_id"])
        page.fill("#password", store["owner_password"])

        with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
            page.click("button[type=submit]")

        if "login" in page.url:
            raise RuntimeError(f"Login failed for {store['name']}")

        # --- 口コミ返信ページ（全件取得） ---
        all_html = []
        page_num = 1

        while True:
            params = f"?srt=update&sby=desc&PG={page_num}&smp=2&lc=0"
            url = REPLY_TOP_URL + params

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(1)

            # 口コミ要素の存在確認
            count = page.evaluate(
                "() => document.querySelectorAll('.review-wrap').length"
            )
            if count == 0:
                break

            html = page.content()
            all_html.append(html)
            print(f"    Page {page_num}: {count} reviews")

            # 次ページリンクの存在確認
            has_next = page.evaluate("""() => {
                const next = document.querySelector('.next a, a.next');
                return next !== null;
            }""")

            if not has_next:
                break
            page_num += 1

        # --- コンテキスト破棄（ログアウト相当） ---
        context.close()
        browser.close()

    return all_html


# ---------------------------------------------------------------------------
# BeautifulSoup: HTML → 構造化データ
# ---------------------------------------------------------------------------

def parse_reviews(html_list: list[str]) -> list[dict]:
    """HTML文字列のリストから口コミデータを抽出する。"""
    reviews = []
    seen_titles = set()

    for html in html_list:
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.select(".review-wrap"):
            title = _extract_title(item)
            reviewer = _extract_reviewer(item)
            post_date = _extract_post_date(item)
            dedup_key = f"{reviewer}:{post_date}:{title}"
            if dedup_key in seen_titles:
                continue
            seen_titles.add(dedup_key)

            detail_ratings = _extract_detail_ratings(item)

            review = {
                "投稿者": reviewer,
                "口コミタイトル": title,
                "口コミ内容": _extract_comment(item),
                "総合点数": _extract_total_score(item),
                "投稿日": _extract_post_date(item),
                "訪問日": _extract_visit_date(item),
                "口コミタイプ": _extract_review_type(item),
                "使った金額_夜": _extract_price(item, "dinner"),
                "料理・味": detail_ratings.get("料理・味", ""),
                "サービス": detail_ratings.get("サービス", ""),
                "雰囲気": detail_ratings.get("雰囲気", ""),
                "CP": detail_ratings.get("CP", ""),
                "酒・ドリンク": detail_ratings.get("酒・ドリンク", ""),
                "いいね数": _extract_likes(item),
            }
            reviews.append(review)

    return reviews


def _extract_reviewer(item) -> str:
    el = item.select_one(".reviewer-name a span")
    if not el:
        return ""
    name = el.get_text(strip=True)
    # "ねこのこ全国ぐるめ（418）" → "ねこのこ全国ぐるめ"
    name = re.sub(r"\s*（\d+）$", "", name)
    return name


def _extract_title(item) -> str:
    el = item.select_one("p.title a, p.title")
    return el.get_text(strip=True) if el else ""


def _extract_comment(item) -> str:
    el = item.select_one("div.comment p, div.comment")
    if not el:
        return ""
    for br in el.find_all("br"):
        br.replace_with("\n")
    return el.get_text().strip()


def _extract_total_score(item) -> str:
    el = item.select_one("b.c-rating-v2__val--strong")
    return el.get_text(strip=True) if el else ""


def _extract_post_date(item) -> str:
    el = item.select_one("p.entry-date .date")
    if not el:
        return ""
    return el.get_text(strip=True)


def _extract_visit_date(item) -> str:
    el = item.select_one("span.visit .date")
    if not el:
        return ""
    return el.get_text(strip=True)


def _extract_review_type(item) -> str:
    if item.select_one(".c-rating-v2__time--dinner"):
        return "夜"
    if item.select_one(".c-rating-v2__time--lunch"):
        return "昼"
    return ""


def _extract_price(item, meal_type: str = "dinner") -> str:
    class_map = {"dinner": ".dinner", "lunch": ".lunch"}
    selector = class_map.get(meal_type, ".dinner")
    # 価格は .dinner の隣の strong/text に含まれる
    price_li = item.select_one(f"ul.prices li.rate:has({selector})")
    if price_li:
        strong = price_li.select_one("strong")
        if strong:
            val = strong.get_text(strip=True)
            return "" if val in ("－", "-") else val
    return ""


def _extract_detail_ratings(item) -> dict:
    result = {}
    for li in item.select("ul.ratings li.rate"):
        label_el = li.select_one("span.item")
        score_el = li.select_one("strong")
        if label_el and score_el:
            label = label_el.get_text(strip=True)
            score = score_el.get_text(strip=True)
            if score in ("－", "-", "–"):
                score = ""
            result[label] = score
    return result


def _extract_likes(item) -> str:
    el = item.select_one(".review-footer .like-count__count")
    return el.get_text(strip=True) if el else "0"


# ---------------------------------------------------------------------------
# フィルタ
# ---------------------------------------------------------------------------

def parse_iso_week(week_str: str) -> tuple[datetime, datetime]:
    """'2026-W16' → (月曜, 日曜)"""
    m = re.match(r"(\d{4})-W(\d{1,2})", week_str)
    if not m:
        raise ValueError(f"Invalid week format: {week_str}")
    year, week = int(m.group(1)), int(m.group(2))
    monday = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
    sunday = monday + timedelta(days=6)
    return monday, sunday


def parse_date_str(date_str: str) -> datetime | None:
    """'25/09/24 → datetime, '24/11 → datetime(month only)"""
    date_str = date_str.strip().strip("'")
    parts = date_str.split("/")
    try:
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            y = 2000 + y if y < 100 else y
            return datetime(y, m, d)
        elif len(parts) == 2:
            y, m = int(parts[0]), int(parts[1])
            y = 2000 + y if y < 100 else y
            return datetime(y, m, 1)
    except (ValueError, IndexError):
        pass
    return None


def filter_by_week(reviews: list[dict], week_str: str) -> list[dict]:
    """投稿日が指定週に含まれる口コミを返す。
    訪問日は月精度のみのため、投稿日でフィルタする。
    """
    monday, sunday = parse_iso_week(week_str)
    filtered = []
    for r in reviews:
        post_date = parse_date_str(r.get("投稿日", ""))
        if post_date and monday <= post_date <= sunday:
            filtered.append(r)
    return filtered


def filter_by_visit_month(reviews: list[dict], week_str: str) -> list[dict]:
    """訪問月が対象週の月と一致する口コミを返す。"""
    monday, sunday = parse_iso_week(week_str)
    target_months = {(monday.year, monday.month), (sunday.year, sunday.month)}
    filtered = []
    for r in reviews:
        visit = parse_date_str(r.get("訪問日", ""))
        if visit and (visit.year, visit.month) in target_months:
            filtered.append(r)
    return filtered


# ---------------------------------------------------------------------------
# CSV出力
# ---------------------------------------------------------------------------

CSV_HEADERS = [
    "投稿者",
    "口コミタイトル",
    "口コミ内容",
    "総合点数",
    "投稿日",
    "訪問日",
    "口コミタイプ",
    "使った金額_夜",
    "料理・味",
    "サービス",
    "雰囲気",
    "CP",
    "酒・ドリンク",
    "いいね数",
]


def write_csv(reviews: list[dict], output_path: Path):
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in reviews:
            writer.writerow(r)


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def process_store(
    store: dict,
    output_dir: Path,
    week: str | None,
    headless: bool,
) -> list[dict]:
    """1店舗分の処理"""
    print(f"\n{'='*60}")
    print(f"  {store['name']} ({store['id']})")
    print(f"{'='*60}")

    print("  Fetching...")
    html_list = fetch_reviews_html(store, headless=headless)
    print(f"  Fetched {len(html_list)} page(s)")

    reviews = parse_reviews(html_list)
    print(f"  Parsed {len(reviews)} reviews total")

    if week:
        by_post = filter_by_week(reviews, week)
        by_visit = filter_by_visit_month(reviews, week)
        # 投稿日でフィルタ（週報向け: その週に新しく投稿された口コミ）
        reviews = by_post
        print(f"  Filtered to {len(reviews)} reviews posted in {week}"
              f" (visit month match: {len(by_visit)})")

    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{week}" if week else ""
    filename = f"reviews_{store['id']}{suffix}.csv"
    output_path = output_dir / filename
    write_csv(reviews, output_path)
    print(f"  Output: {output_path} ({len(reviews)} rows)")

    return reviews


def main():
    parser = argparse.ArgumentParser(description="食べログ口コミ取得")
    parser.add_argument("--store", help="Store ID (e.g. bfa)")
    parser.add_argument("--all", action="store_true", help="全店舗を処理")
    parser.add_argument("--week", help="ISO week filter (e.g. 2026-W16)")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("-o", "--output", default=".")
    parser.add_argument("--headed", action="store_true", help="ブラウザ表示")
    args = parser.parse_args()

    if not args.store and not args.all:
        parser.error("--store or --all is required")

    config = load_config(Path(args.config))
    output_dir = Path(args.output)
    headless = not args.headed

    if args.all:
        stores = [s for s in config["stores"] if s.get("owner_login_id")]
    else:
        stores = [get_store_config(config, args.store)]

    total = 0
    for store in stores:
        reviews = process_store(store, output_dir, args.week, headless)
        total += len(reviews)

    print(f"\nDone. {total} reviews across {len(stores)} store(s).")


if __name__ == "__main__":
    main()
