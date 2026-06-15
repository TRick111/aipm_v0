#!/bin/bash
# markserv 8810 (aipm_v0/Flow) の serve 対象を「実行時の今月+先月」に動的に保つ
# 毎日呼ばれ、月が変わった瞬間に自動でリンクが差し替わり markserv を再起動する。
# 月が変わっていなければ no-op (ログ1行のみ)。

set -euo pipefail

TARGET_DIR="/Users/rikutanaka/aipm_v0/.markserv-flow-current"
FLOW_DIR="/Users/rikutanaka/aipm_v0/Flow"
LOG_DIR="/Users/rikutanaka/Library/Logs/markserv"
LOG_FILE="$LOG_DIR/refresh.log"
LABEL="jp.markserv.aipm-flow"

mkdir -p "$LOG_DIR"
mkdir -p "$TARGET_DIR"

CURRENT=$(date +%Y%m)
PREV=$(date -v-1m +%Y%m)

EXPECTED=$(printf "%s\n%s\n" "$PREV" "$CURRENT" | sort -u | tr '\n' ' ')
CURRENT_LINKS=$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -type l -exec basename {} \; 2>/dev/null | sort -u | tr '\n' ' ')

if [ "$EXPECTED" = "$CURRENT_LINKS" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') no-change: [$CURRENT_LINKS]" >> "$LOG_FILE"
  exit 0
fi

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') refresh-markserv-flow (change detected) ==="
  echo "expected=[$EXPECTED] current=[$CURRENT_LINKS]"

  find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -type l -delete 2>/dev/null || true

  for m in "$PREV" "$CURRENT"; do
    src="$FLOW_DIR/$m"
    dst="$TARGET_DIR/$m"
    if [ -d "$src" ]; then
      ln -s "$src" "$dst"
      echo "linked: $dst -> $src"
    else
      echo "warn: $src not found, skipped"
    fi
  done

  if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
    echo "kickstart: $LABEL"
    launchctl kickstart -k "gui/$UID/$LABEL" || true
  else
    echo "info: $LABEL not loaded yet; skip kickstart"
  fi
} >> "$LOG_FILE" 2>&1
