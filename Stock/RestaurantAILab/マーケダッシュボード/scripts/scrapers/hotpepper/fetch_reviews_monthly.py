"""
ホットペッパーグルメ クチコミ一覧を **ページング走査** して取得し、投稿月別 CSV に分割保存。

仕組み:
  1. storageState を再利用してログイン済セッションで /CLP/ccm010/showReportListAll?pn=N にアクセス
  2. 各ページの HTML を parsers/parse_reviews.parse() で解析
  3. 最古投稿日が「12 ヶ月前」より古くなったらページング停止
  4. 取得したレビューを投稿月別に集計し sample_data/hotpepper/auto/reviews/<YYYY-MM>.csv に書き出す

使い方:
    python3 fetch_reviews_monthly.py                 # 過去 12 ヶ月（既定）
    python3 fetch_reviews_monthly.py --months 6      # 過去 6 ヶ月
    python3 fetch_reviews_monthly.py --max-pages 30  # ページ数の上限（保険）

出力: sample_data/hotpepper/auto/reviews/<YYYY-MM>.csv
"""

from __future__ import annotations

import csv
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from _lib.credentials import get_target_months  # noqa: E402
from _lib.playwright_helpers import open_context_with_state  # noqa: E402

# 既存パーサ流用
from parsers.parse_reviews import parse as parse_reviews_html  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "sample_data" / "hotpepper" / "auto" / "reviews"
LIST_URL = "https://www.cms.hotpepper.jp/CLP/ccm010/showReportListAll?pn={pn}"
ENTRY_URL = "https://www.cms.hotpepper.jp/CLP/ccm010/showReportListAllForAuth"

FIELDNAMES = ["投稿日", "総合評価", "投稿者", "利用シーン", "最終審査日", "口コミID", "本文先頭"]


def parse_args(argv: list[str]) -> tuple[list[str], int]:
    months_list = get_target_months(months=12)
    n = 12
    if "--months" in argv:
        i = argv.index("--months")
        n = int(argv[i + 1])
        months_list = get_target_months(months=n)
    max_pages = 30
    if "--max-pages" in argv:
        i = argv.index("--max-pages")
        max_pages = int(argv[i + 1])
    return months_list, max_pages


def main() -> int:
    months_list, max_pages = parse_args(sys.argv[1:])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 取得対象月の集合（YYYY-MM）
    target_set = set(months_list)
    oldest_target = min(months_list)  # 'YYYY-MM'
    oldest_y, oldest_m = map(int, oldest_target.split("-"))
    oldest_date = date(oldest_y, oldest_m, 1)
    print(f"[hpg/reviews] target months: {len(target_set)} (oldest={oldest_target})", file=sys.stderr)

    all_rows: list[dict] = []
    seen_ids: set[str] = set()

    with sync_playwright() as pw:
        ctx, page = open_context_with_state(pw, service="hpg_recruit", headless=True)
        # 初回ロードで認証チェック
        page.goto(ENTRY_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        if "login" in page.url.lower() or "noLoginError" in page.url:
            print("[hpg/reviews] storageState expired. Re-run login_and_save_state_auto.py", file=sys.stderr)
            ctx.close()
            return 2

        stop_paging = False
        for pn in range(1, max_pages + 1):
            url = LIST_URL.format(pn=pn)
            print(f"[hpg/reviews] fetching page {pn}: {url}", file=sys.stderr)
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(800)
                if resp is None or resp.status >= 400:
                    print(f"  [WARN] HTTP {resp.status if resp else '?'}, stopping", file=sys.stderr)
                    break
                if "login" in page.url.lower() and "noLogin" not in page.url:
                    print("  [WARN] redirected to login, stopping", file=sys.stderr)
                    break
                html = page.content()
                rows = parse_reviews_html(html)
                if not rows:
                    print(f"  page {pn} returned 0 reviews -> stop", file=sys.stderr)
                    break
                # de-dupe by 口コミID
                new_rows = [r for r in rows if r.get("口コミID") and r["口コミID"] not in seen_ids]
                for r in new_rows:
                    seen_ids.add(r["口コミID"])
                all_rows.extend(new_rows)
                # 最古投稿日を見る
                dates = sorted(r["投稿日"] for r in rows if r.get("投稿日"))
                oldest_on_page = dates[0] if dates else None
                print(f"  page {pn}: {len(rows)} rows ({len(new_rows)} new). oldest={oldest_on_page}", file=sys.stderr)
                if oldest_on_page:
                    y, m, d = map(int, oldest_on_page.split("-"))
                    if date(y, m, d) < oldest_date:
                        print(f"  oldest review {oldest_on_page} < target start {oldest_target}, stopping", file=sys.stderr)
                        stop_paging = True
                if len(rows) < 20:
                    # 1 ページ 20 件未満なら最終ページ扱い
                    print("  page returned <20 rows -> last page", file=sys.stderr)
                    stop_paging = True
                if stop_paging:
                    break
                time.sleep(1)
            except Exception as e:  # noqa: BLE001
                print(f"  page {pn} ERR: {type(e).__name__}: {e}", file=sys.stderr)
                break
        ctx.close()

    print(f"[hpg/reviews] total fetched: {len(all_rows)} reviews", file=sys.stderr)

    # 投稿月別に集計
    by_month: dict[str, list[dict]] = defaultdict(list)
    for r in all_rows:
        d = r.get("投稿日") or ""
        if len(d) < 7:
            continue
        ym = d[:7]  # YYYY-MM
        if ym not in target_set:
            continue
        by_month[ym].append(r)

    # 書き出し
    written: list[tuple[str, int]] = []
    for ym in sorted(by_month.keys()):
        out = OUT_DIR / f"{ym}.csv"
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
            w.writerows(sorted(by_month[ym], key=lambda r: r.get("投稿日") or ""))
        written.append((ym, len(by_month[ym])))
        print(f"  -> {out}: {len(by_month[ym])} rows", file=sys.stderr)

    # 0 件月用に空ファイルを生成（後段集計の存在チェック簡略化のため、ヘッダのみ書く）
    for ym in target_set:
        if ym in by_month:
            continue
        out = OUT_DIR / f"{ym}.csv"
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
        print(f"  -> {out}: 0 rows (header only)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
