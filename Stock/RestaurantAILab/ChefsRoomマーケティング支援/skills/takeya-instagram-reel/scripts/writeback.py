#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成済み output CSV からスプレッドシート向け batchUpdate ボディを構築する。

呼び出し例:
  python3 writeback.py \
      --in /path/to/output_takeya_YYYY-MM-DD.csv \
      --mapping /path/to/input_takeya_YYYY-MM-DD.csv \
      [--keep-seed]              # シーン1/13/17 を上書きせず保持
      > /tmp/batch_body.json

  gws sheets spreadsheets values batchUpdate \
      --params '{"spreadsheetId":"<ID>"}' \
      --json "$(cat /tmp/batch_body.json)"

ファイル要件:
  - output CSV: 列 `No, テーマ, シーン1〜シーン17, 参考例ID` (generate_scripts_with_gemini.py の出力)
  - input CSV: 列 `_シート, _動画番号` を含む (extract_input.py の出力)

join はインデックス順 (同じ順序で生成された前提)。
ブロック N の E 列範囲: (N-1)*20 + 3 〜 (N-1)*20 + 19  (1-indexed)
"""

import argparse
import csv
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True, help="output CSV (シーンが入っている)")
    ap.add_argument("--mapping", required=True, help="input CSV (_シート/_動画番号 が入っている)")
    ap.add_argument("--keep-seed", action="store_true",
                    help="シーン1/13/17 を上書きせず、2-12 と 14-16 のみ書き込む")
    args = ap.parse_args()

    with open(args.in_csv, encoding="utf-8") as f:
        out_rows = list(csv.DictReader(f))
    with open(args.mapping, encoding="utf-8") as f:
        map_rows = list(csv.DictReader(f))

    if len(out_rows) != len(map_rows):
        print(f"行数不一致: out={len(out_rows)} mapping={len(map_rows)}", file=sys.stderr)
        return 1

    if "_シート" not in map_rows[0] or "_動画番号" not in map_rows[0]:
        print("mapping CSV に '_シート' / '_動画番号' 列がありません", file=sys.stderr)
        return 1

    value_ranges = []
    for o, m in zip(out_rows, map_rows):
        sheet = m["_シート"]
        vid = int(m["_動画番号"])
        base = (vid - 1) * 20 + 2  # シーン N の行 = base + N

        if args.keep_seed:
            # シーン2-12, 14-16 のみ。連続しないので 2 つの range に分ける。
            v_2_12 = [[o[f"シーン{i}"]] for i in range(2, 13)]
            value_ranges.append({
                "range": f"{sheet}!E{base+2}:E{base+12}",
                "majorDimension": "ROWS",
                "values": v_2_12,
            })
            v_14_16 = [[o[f"シーン{i}"]] for i in range(14, 17)]
            value_ranges.append({
                "range": f"{sheet}!E{base+14}:E{base+16}",
                "majorDimension": "ROWS",
                "values": v_14_16,
            })
        else:
            # 全 17 シーン一括上書き
            values = [[o[f"シーン{i}"]] for i in range(1, 18)]
            value_ranges.append({
                "range": f"{sheet}!E{base+1}:E{base+17}",
                "majorDimension": "ROWS",
                "values": values,
            })

    body = {"valueInputOption": "RAW", "data": value_ranges}
    print(json.dumps(body, ensure_ascii=False))

    print(f"\nValueRange 数: {len(value_ranges)}", file=sys.stderr)
    total_cells = sum(len(d["values"]) for d in value_ranges)
    print(f"総セル数: {total_cells}", file=sys.stderr)
    print(f"最初: {value_ranges[0]['range']}", file=sys.stderr)
    print(f"最後: {value_ranges[-1]['range']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
