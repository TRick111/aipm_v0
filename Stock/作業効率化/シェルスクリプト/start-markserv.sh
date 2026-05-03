#!/bin/bash
# Markserv起動スクリプト
# 指定ディレクトリをそれぞれ異なるポートでサーブする
# 同一ネットワーク内の端末からアクセス可能（0.0.0.0バインド）

PORTS="8810 8811 8812"
DIR_8810="/Users/rikutanaka/aipm_v0"
DIR_8811="/Users/rikutanaka/RestaurantAILab/Markdowns-1"
DIR_8812="/Users/rikutanaka/RestaurantAILab/Dashboard/docs"

for port in $PORTS; do
  eval "dir=\$DIR_$port"
  pid=$(lsof -ti :$port 2>/dev/null)

  if [ -n "$pid" ]; then
    proc=$(ps -p $pid -o comm= 2>/dev/null)
    if echo "$proc" | grep -qi markserv; then
      echo "Port $port: markservが動作中 (PID $pid) → 停止して再起動"
      kill $pid
      sleep 1
    else
      echo "Port $port: $proc が使用中 → スキップ"
      continue
    fi
  fi

  if [ -d "$dir" ]; then
    lrport=$((35729 + port - 8810))
    echo "起動: $dir → port $port (livereload: $lrport)"
    (cd "$dir" && nohup markserv -p $port --livereloadport $lrport -a 0.0.0.0 . > /tmp/markserv-$port.log 2>&1 &)
  else
    echo "警告: $dir が存在しません → スキップ"
  fi
done

echo ""
echo "=== 起動結果 ==="
sleep 2
ps aux | grep "[m]arkserv" | grep -v bash

echo ""
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "取得失敗")
echo "ローカルIP: $LOCAL_IP"

if [ "$LOCAL_IP" != "取得失敗" ]; then
  echo ""
  echo "アクセスURL:"
  echo "  http://$LOCAL_IP:8810  (aipm_v0)"
  echo "  http://$LOCAL_IP:8811  (Markdowns-1)"
  echo "  http://$LOCAL_IP:8812  (Dashboard/docs)"
fi
