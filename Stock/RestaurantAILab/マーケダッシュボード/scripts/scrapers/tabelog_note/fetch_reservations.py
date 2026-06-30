"""
食べログノート 分析ダッシュボードの「当月の予約情報CSV」（= 予約一覧）を月別に取得。

エンドポイント: /tn/download/download_analysis_csv?yearMonth=YYYY-MM&startDay=01
CSV はサンプル「食べログノート_予約一覧_YYYY-MM.csv」（22 列）と同じ形式の想定。

使い方:
    python3 fetch_reservations.py                 # 過去 12 ヶ月
    python3 fetch_reservations.py --month 2026-06
    python3 fetch_reservations.py --months 6

出力: sample_data/tabelog_note/auto/reservations/<YYYY-MM>.csv
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tabelog_note._common import download_csv, parse_months_arg  # noqa: E402


URL = (
    "https://owner.tabelog.com/tn/download/download_analysis_csv"
    "?yearMonth={ym}&startDay=01"
)


def main() -> int:
    months = parse_months_arg(sys.argv[1:])
    result = download_csv(report_type="reservations", url_template=URL, months=months)
    failures = [ym for ym, r in result.items() if not r.get("ok")]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
