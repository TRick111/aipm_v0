"""
食べログノート分析 CSV 取得の共通ロジック。

実機確認した CSV エンドポイント:
- 総客数(日別):  /tn/download/analysis_number_of_bookings_and_people_csv?yearMonth=YYYY-MM&startDay=01
- 予約コース:    /tn/download/analysis_booking_plan_csv?yearMonth=YYYY-MM&startDay=01
- 予約一覧:      /tn/download/download_analysis_csv?yearMonth=YYYY-MM&startDay=01
- 予約経路:      /tn/download/analysis_booking_route_csv?yearMonthFrom=YYYY-MM&yearMonthTo=YYYY-MM+1&startDay=01
- 予約キャンセル: /tn/download/analysis_cancel_csv?yearMonthFrom=...&yearMonthTo=...&startDay=01

文字コード: UTF-8（実機確認、SOP の Shift_JIS 想定とは異なる）
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Iterable

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _lib.credentials import get_target_months  # noqa: E402
from _lib.playwright_helpers import open_context_with_state  # noqa: E402


BASE = "https://owner.tabelog.com"
ANALYSIS_DASHBOARD = BASE + "/tn/analysis?yearMonth={ym}"

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DATA = REPO_ROOT / "sample_data" / "tabelog_note" / "auto"


def parse_months_arg(argv: list[str]) -> list[str]:
    """--month YYYY-MM / --months N をパース。未指定なら過去 12 ヶ月。"""
    if "--month" in argv:
        i = argv.index("--month")
        return [argv[i + 1]]
    if "--months" in argv:
        i = argv.index("--months")
        return get_target_months(months=int(argv[i + 1]))
    return get_target_months(months=12)


def download_csv(
    *,
    report_type: str,
    url_template: str,
    months: Iterable[str],
    headless: bool = True,
) -> dict[str, dict]:
    """月毎に CSV をダウンロードし sample_data/tabelog_note/auto/<report_type>/<YYYY-MM>.csv に保存。

    返り値: {YYYY-MM: {'path': Path, 'size': int, 'rows': int, 'ok': bool, 'error': str?}}
    """
    out_dir = SAMPLE_DATA / report_type
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, dict] = {}

    with sync_playwright() as pw:
        ctx, page = open_context_with_state(pw, service="tabelog_owner", headless=headless)
        # 1 度だけ分析ダッシュボードを開いて session/referer をウォームアップ
        page.goto(ANALYSIS_DASHBOARD.format(ym=list(months)[0]), wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)

        for ym in months:
            url = url_template.format(ym=ym)
            out_path = out_dir / f"{ym}.csv"
            print(f"[tabelog_note/{report_type}] {ym} -> {url}", file=sys.stderr)
            try:
                with page.expect_download(timeout=45000) as dl_info:
                    page.evaluate(f"() => {{ window.location.href = '{url}'; }}")
                dl = dl_info.value
                dl.save_as(str(out_path))
                size = out_path.stat().st_size
                # 行数（UTF-8 想定。失敗したら cp932 で再試行）
                try:
                    text = out_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text = out_path.read_text(encoding="cp932")
                rows = max(0, text.count("\n") - 1)
                result[ym] = {"path": out_path, "size": size, "rows": rows, "ok": True}
                print(
                    f"  OK: size={size:,}B rows={rows} -> {out_path}", file=sys.stderr
                )
                time.sleep(1)  # 礼儀的レート制限
            except Exception as e:  # noqa: BLE001
                result[ym] = {"path": out_path, "size": 0, "rows": 0, "ok": False, "error": f"{type(e).__name__}: {e}"}
                print(f"  ERR: {type(e).__name__}: {e}", file=sys.stderr)
        ctx.close()
    return result
