"""
食べログノート 分析-予約コース CSV を月別に取得。

使い方:
    python3 fetch_courses.py                 # 過去 12 ヶ月
    python3 fetch_courses.py --month 2026-06
    python3 fetch_courses.py --months 6      # 過去 6 ヶ月

出力: sample_data/tabelog_note/auto/courses/<YYYY-MM>.csv
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tabelog_note._common import download_csv, parse_months_arg  # noqa: E402


URL = (
    "https://owner.tabelog.com/tn/download/analysis_booking_plan_csv"
    "?yearMonth={ym}&startDay=01"
)


def main() -> int:
    months = parse_months_arg(sys.argv[1:])
    result = download_csv(report_type="courses", url_template=URL, months=months)
    failures = [ym for ym, r in result.items() if not r.get("ok")]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
