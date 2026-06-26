#!/usr/bin/env bash
# 食べログ 5 ページの fetch + parse をまとめて実行する。
# 事前条件: login_and_save_state.py で state/storageState.json を生成済み。
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Fetch all 5 pages"
python3 fetch_all.py

echo ""
echo "==> Parse all 5 pages"
for parser in parsers/parse_*.py; do
  name=$(basename "$parser" .py | sed 's/^parse_//')
  echo "[parse] $name"
  python3 "$parser" "raw_html/${name}.html" "output/${name}.csv"
done

echo ""
echo "==> Done. Outputs:"
ls -la output/
