#!/bin/bash
# Markserv起動スクリプト
# 指定ディレクトリをそれぞれ異なるポートでサーブする
# 同一ネットワーク内の端末からアクセス可能（0.0.0.0バインド）

declare -A DIRS
DIRS[8810]="/Users/rikutanaka/aipm_v0"
DIRS[8811]="/Users/rikutanaka/RestaurantAILab/Markdowns-1"
DIRS[8812]="/Users/rikutanaka/RestaurantAILab/Dashboard/docs"

for port in 8810 8811 8812; do
  dir="${DIRS[$port]}"
  pid=$(lsof -ti :$port 2>/dev/null)

  if [ -n "$pid" ]; then
    proc=$(ps -p $pid -o comm= 2>/dev/null)
    if echo "$proc" | grep -qi markserv; then
      echo "Port $port: markservが動作中 (PID $pid) → 停止して再起動"
      kill $pid
      sleep 1
    else
      while lsof -ti :$port >/dev/null 2>&1; do
        echo "Port $port: $proc が使用中 → スキップ"
        port=$((port + 1))
      done
      echo "Port $port を代わりに使用"
    fi
  fi

  echo "起動: $dir → port $port"
  nohup markserv -p $port -a 0.0.0.0 "$dir" > /tmp/markserv-$port.log 2>&1 &
done

echo ""
echo "=== 起動結果 ==="
sleep 1
ps aux | grep markserv | grep -v grep
echo ""
echo "ローカルIP: $(ipconfig getifaddr en0 2>/dev/null || echo '取得失敗')"
