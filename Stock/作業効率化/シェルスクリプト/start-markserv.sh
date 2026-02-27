#!/bin/bash
# Markserv起動スクリプト
# 指定ディレクトリをそれぞれ異なるポートでサーブする
# 同一ネットワーク内の端末からアクセス可能（0.0.0.0バインド）

# --- 設定（ポート|ディレクトリ） ---
PORT1=8810; DIR1="/Users/rikutanaka/aipm_v0"
PORT2=8811; DIR2="/Users/rikutanaka/RestaurantAILab/Markdowns-1"
PORT3=8812; DIR3="/Users/rikutanaka/RestaurantAILab/Dashboard/docs"

# --- Step 1: 既存のmarkservを全て停止 ---
echo "=== 既存markservを停止 ==="
pkill -f "markserv" 2>/dev/null && echo "停止しました" && sleep 2 || echo "動作中のmarkservなし"
echo ""

# LISTENしているプロセスのみチェック（CLOSED等は無視）
is_port_listening() {
  lsof -i :$1 -sTCP:LISTEN -P -n >/dev/null 2>&1
}

# 空きポートを探す（既に割り当てたポートも避ける）
ASSIGNED=""
find_free_port() {
  local p=$1
  while is_port_listening $p || echo "$ASSIGNED" | grep -qw "$p"; do
    p=$((p + 1))
  done
  echo $p
}

start_markserv() {
  local port=$1
  local dir=$2

  port=$(find_free_port $port)
  ASSIGNED="$ASSIGNED $port"

  echo "起動: $dir → port $port"
  (cd "$dir" && nohup markserv -p "$port" --livereloadport false -a 0.0.0.0 --browser false . > /tmp/markserv-$port.log 2>&1 &)
  sleep 1
}

# --- Step 2: 起動 ---
echo "=== Markserv 起動 ==="
start_markserv $PORT1 "$DIR1"
start_markserv $PORT2 "$DIR2"
start_markserv $PORT3 "$DIR3"

echo ""
echo "=== 起動結果 ==="
sleep 2
ps aux | grep "[m]arkserv" | grep -v "start-markserv"
echo ""
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo "ローカルIP: ${LOCAL_IP:-取得失敗}"
