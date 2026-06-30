#!/usr/bin/env bash
# 食べログノート 3 レポートを過去 12 ヶ月分まとめて取得
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

python3 "$HERE/login_and_save_state.py"
python3 "$HERE/fetch_reservations.py" "$@"
python3 "$HERE/fetch_total_guests.py" "$@"
python3 "$HERE/fetch_courses.py" "$@"
