#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cron環境ではPATHが最小になるため、明示的に補完する
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

python3 "${SCRIPT_DIR}/gmail_daily_reply_report.py"
