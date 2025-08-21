#!/usr/bin/env bash
set -euo pipefail

# merge_same_speaker.sh
# 目的: "話者: 発言" 形式の議事録で、同一話者の連続行を1行にまとめる
# 対応: 半角コロン(:)・全角コロン(：)どちらにも対応
# 使い方:
#   1) 標準出力へ出す:  ./merge_same_speaker.sh input.vtt > output.vtt
#   2) 上書き(-i):      ./merge_same_speaker.sh -i input.vtt
#   3) 明示出力(-o):    ./merge_same_speaker.sh -o output.vtt input.vtt

usage() {
  echo "Usage: $0 [-i] [-o output_file] input_file" >&2
  exit 1
}

inplace=false
out_file=""
while getopts ":io:" opt; do
  case "$opt" in
    i) inplace=true ;;
    o) out_file="$OPTARG" ;;
    *) usage ;;
  esac
done
shift $((OPTIND-1))

[[ $# -eq 1 ]] || usage
in_file="$1"
[[ -f "$in_file" ]] || { echo "Input not found: $in_file" >&2; exit 1; }

awk '
  function ltrim(s){ sub(/^\s+/, "", s); return s }
  function rtrim(s){ sub(/\s+$/, "", s); return s }
  function trim(s){ return rtrim(ltrim(s)) }
  function flush(){
    if (buffer != "") {
      print last_speaker ": " buffer
      buffer = ""; last_speaker = ""
    }
  }
  {
    # 対象行判定: 最初のコロン(半角/全角)で話者と本文を分離
    if (match($0, /[：:]/)) {
      col = RSTART
      speaker = trim(substr($0, 1, col-1))
      text    = substr($0, col+1)
      text    = ltrim(text)  # コロン後の空白を除去

      if (last_speaker == "" || last_speaker == speaker) {
        if (buffer == "") {
          last_speaker = speaker
          buffer = text
        } else {
          # 前後の句読点を考慮しつつスペース結合（単純にスペースで連結）
          sep = " "
          if (buffer ~ /[。．.!?！？]$/ || text ~ /^[、。．,!?！？]/) sep = ""
          buffer = buffer sep text
        }
      } else {
        flush()
        last_speaker = speaker
        buffer = text
      }
    } else {
      # 話者行でない場合は、バッファを吐き出してそのまま出力
      flush()
      print $0
    }
  }
  END { flush() }
' "$in_file" > "${out_file:-/dev/stdout}"

if $inplace; then
  tmp_file="$(mktemp "${in_file##*/}.XXXXXX")"
  awk '
    function ltrim(s){ sub(/^\s+/, "", s); return s }
    function rtrim(s){ sub(/\s+$/, "", s); return s }
    function trim(s){ return rtrim(ltrim(s)) }
    function flush(){ if (buffer != "") { print last_speaker ": " buffer; buffer = ""; last_speaker = "" } }
    {
      if (match($0, /[：:]/)) {
        col = RSTART
        speaker = trim(substr($0, 1, col-1))
        text    = substr($0, col+1)
        text    = ltrim(text)
        if (last_speaker == "" || last_speaker == speaker) {
          if (buffer == "") { last_speaker = speaker; buffer = text }
          else {
            sep = " "; if (buffer ~ /[。．.!?！？]$/ || text ~ /^[、。．,!?！？]/) sep = ""
            buffer = buffer sep text
          }
        } else {
          flush(); last_speaker = speaker; buffer = text
        }
      } else { flush(); print $0 }
    }
    END { flush() }
  ' "$in_file" > "$tmp_file"
  cp -p -- "$in_file" "$in_file.bak"
  mv -- "$tmp_file" "$in_file"
fi


