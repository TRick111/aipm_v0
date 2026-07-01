"""
食べログ本体 5 ページを 月別ループで取得し、sample_data/tabelog/YYYY-MM/ に整理。

- access_report_page: 月別ループ (?start_month=YYYYMM&end_month=YYYYMM)
- access_report_total: 月別ループ (?display_type=daily&start_month=YYYYMM&end_month=YYYYMM)
- access_report_total_conversion: 1 回で 13ヶ月分 → 各月フォルダに同じ CSV をコピー
- access_ranking: 当月スナップショット → 最新月のみに配置（過去月分は取れない）
- rstupreview_entry: 全期間 → 各月フォルダに同じ CSV をコピー

使い方:
    python3 fetch_monthly_batch.py --months 12                   # 過去12ヶ月
    python3 fetch_monthly_batch.py --start 2025-07 --end 2026-04 # 期間指定
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright  # noqa: E402


BASE_DIR = Path(__file__).parent
STATE_PATH = BASE_DIR / "state" / "storageState.json"
RAW_DIR = BASE_DIR / "raw_html"
OUTPUT_DIR = BASE_DIR / "output"
REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = REPO_ROOT / "sample_data" / "tabelog"
PARSERS_DIR = BASE_DIR / "parsers"


def gen_months(start_ym: str, end_ym: str) -> list[str]:
    """start_ym から end_ym まで（両端含む、古い順）"""
    y1, m1 = map(int, start_ym.split("-"))
    y2, m2 = map(int, end_ym.split("-"))
    result = []
    y, m = y1, m1
    while (y, m) <= (y2, m2):
        result.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def fetch_month(page, month: str) -> None:
    """特定月の access_report_page + access_report_total (daily) を取得。他はスキップ。"""
    ym = month.replace("-", "")
    month_dir = RAW_DIR / month
    month_dir.mkdir(parents=True, exist_ok=True)

    # access_report_page: 月絞り
    url = f"https://owner.tabelog.com/owner_rst/access_report_page?start_month={ym}&end_month={ym}"
    print(f"  [fetch page] {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    (month_dir / "access_report_page.html").write_text(page.content(), encoding="utf-8")

    # access_report_total: 日別 + 月絞り
    url = f"https://owner.tabelog.com/owner_rst/access_report_total?display_type=daily&start_month={ym}&end_month={ym}"
    print(f"  [fetch total] {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    (month_dir / "access_report_total.html").write_text(page.content(), encoding="utf-8")


def parse_and_place(month: str, common_csvs: dict[str, Path]) -> None:
    """月別 HTML をパース → sample_data/tabelog/YYYY-MM/ に配置。共通 CSV もコピー。"""
    month_dir_html = RAW_DIR / month
    sample_month = SAMPLE_DIR / month
    sample_month.mkdir(parents=True, exist_ok=True)

    # 月別パース: access_report_page, access_report_total
    for name in ["access_report_page", "access_report_total"]:
        html = month_dir_html / f"{name}.html"
        csv = sample_month / f"{name}.csv"
        parser = PARSERS_DIR / f"parse_{name}.py"
        result = subprocess.run(
            ["python3", str(parser), str(html), str(csv)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [WARN] {name}: {result.stderr.strip()}", file=sys.stderr)
        else:
            print(f"  [parse] {csv.name} OK")

    # 共通 CSV をコピー
    for name, src in common_csvs.items():
        dst = sample_month / f"{name}.csv"
        shutil.copy2(src, dst)
        print(f"  [copy] {dst.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, help="過去 N ヶ月（前月から遡る）")
    parser.add_argument("--start", type=str, help="開始月 YYYY-MM")
    parser.add_argument("--end", type=str, help="終了月 YYYY-MM")
    args = parser.parse_args()

    if not STATE_PATH.exists():
        print(f"[ERROR] {STATE_PATH} が無い。login_and_save_state_auto.py を先に実行", file=sys.stderr)
        return 1

    # 期間決定
    if args.months:
        today = date.today()
        # 前月から N ヶ月遡る（今月は含めない）
        months_list = []
        y, m = today.year, today.month
        for _ in range(args.months):
            m -= 1
            if m < 1:
                m = 12
                y -= 1
            months_list.append(f"{y:04d}-{m:02d}")
        months_list.reverse()  # 古い順
    elif args.start and args.end:
        months_list = gen_months(args.start, args.end)
    else:
        print("[ERROR] --months または --start/--end のいずれか必須", file=sys.stderr)
        return 2

    print(f"[batch] 対象月 ({len(months_list)}件): {months_list[0]} 〜 {months_list[-1]}")

    # 共通 CSV は事前に output/ にあるはず（fetch_all.py で先に取得済）
    common_csvs = {
        "access_report_total_conversion": OUTPUT_DIR / "access_report_total_conversion.csv",
        "access_ranking": OUTPUT_DIR / "access_ranking.csv",
        "rstupreview_entry": OUTPUT_DIR / "rstupreview_entry.csv",
    }
    for name, path in common_csvs.items():
        if not path.exists():
            print(f"[ERROR] 共通 CSV 未生成: {path}。先に fetch_all.py + parsers を実行してください", file=sys.stderr)
            return 3

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATE_PATH))
        page = context.new_page()

        for month in months_list:
            print(f"\n=== {month} ===")
            try:
                fetch_month(page, month)
                parse_and_place(month, common_csvs)
            except Exception as e:
                print(f"  [WARN] {month} 失敗: {e}", file=sys.stderr)

        browser.close()

    print(f"\n[batch] 完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
