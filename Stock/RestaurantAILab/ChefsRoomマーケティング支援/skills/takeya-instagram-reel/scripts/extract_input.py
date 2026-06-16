#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竹矢Instagramスプレッドシートの target シートを読み、台本生成用 input CSV を作る。

事前準備:
  対象シートを `gws sheets +read` で取得し、 `/tmp/takeya_sheets/<safe_name>.json`
  に保存しておく。keyring 行は `sed '/^Using keyring/d'` で除去。

呼び出し例:
  python3 extract_input.py \
      --src-dir /tmp/takeya_sheets \
      --sheets "727-8/7,8/8-8/19,8/20-8/31" \
      --out /path/to/input_takeya_YYYY-MM-DD.csv

ブロックレイアウト (20 行 / 動画, 1-indexed):
  row 1  : タイトル行 (D列 = "ネタメモ：xxx")
  row 2  : ヘッダ
  row 3  : シーン1 (フック)
  row 15 : シーン13 (解決)
  row 19 : シーン17 (エンド)
  row 20 : 空行

スキップ条件: シーン1 (フック) が空 → テーマ未決定とみなしスキップ。
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def cell(row, idx: int) -> str:
    if idx < len(row):
        v = row[idx]
        return str(v).strip() if v is not None else ""
    return ""


def extract_title(title_row) -> str:
    raw = cell(title_row, 3)
    cleaned = re.sub(r"^ネタメモ[：:]\s*", "", raw, flags=re.DOTALL)
    cleaned = re.sub(r"\s*\n\s*", " ", cleaned).strip()
    return cleaned


def safe_sheet_filename(name: str) -> str:
    """シート名をファイル名に使える形式に変換 (/ -> _, 末尾空白除去)"""
    return name.replace("/", "_").rstrip()


def parse_sheet(json_path: Path, sheet_name: str, base_no: int):
    """1 シート分の動画ブロックをパースして dict のリストを返す。"""
    if not json_path.exists():
        return [], [], f"ファイルなし: {json_path}"
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [], [], f"JSONパース失敗: {e}"

    values = data.get("values", [])
    rows, skipped = [], []
    for block_idx in range(12):  # 最大 12 動画/シート
        start = block_idx * 20
        if start + 19 > len(values):
            break
        title_row = values[start]
        scene1_row = values[start + 2]
        scene13_row = values[start + 14]
        scene17_row = values[start + 18]

        # タイトル行が完全に空ならブロック自体が存在しない
        if not any(cell(title_row, i) for i in range(5)):
            continue

        title = extract_title(title_row)
        hook = cell(scene1_row, 4)
        solution = cell(scene13_row, 4)
        ending = cell(scene17_row, 4)

        if not hook:
            skipped.append((sheet_name, block_idx + 1, title or "(タイトルなし)"))
            continue

        rows.append({
            "No": base_no + len(rows) + 1,
            "タイトル": title,
            "フック": hook,
            "解決策": solution,
            "エンド": ending,
            "_シート": sheet_name,
            "_動画番号": block_idx + 1,
        })
    return rows, skipped, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-dir", required=True, help="JSONダンプの置き場 (e.g. /tmp/takeya_sheets)")
    ap.add_argument("--sheets", required=True, help="対象シート名のカンマ区切り (例: 727-8/7,8/8-8/19)")
    ap.add_argument("--out", required=True, help="出力 CSV パス")
    args = ap.parse_args()

    src_dir = Path(args.src_dir)
    sheet_names = [s.strip() for s in args.sheets.split(",") if s.strip()]

    all_rows = []
    all_skipped = []
    summary = []

    for sheet_name in sheet_names:
        json_path = src_dir / f"{safe_sheet_filename(sheet_name)}.json"
        rows, skipped, err = parse_sheet(json_path, sheet_name, base_no=len(all_rows))
        if err:
            summary.append((sheet_name, 0, 0, err))
            continue
        all_rows.extend(rows)
        all_skipped.extend(skipped)
        # `kept` を再採番 (累積 No)
        summary.append((sheet_name, len(rows) + len(skipped), len(rows), ""))

    # No を 1 から振り直し
    for i, r in enumerate(all_rows, 1):
        r["No"] = i

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["No", "タイトル", "フック", "解決策", "エンド", "処理済み", "_シート", "_動画番号"])
        for r in all_rows:
            writer.writerow([
                r["No"], r["タイトル"], r["フック"], r["解決策"], r["エンド"], "",
                r["_シート"], r["_動画番号"],
            ])

    print("=== シート別サマリ ===", file=sys.stderr)
    for name, total, kept, note in summary:
        mark = "✓" if kept > 0 else "-"
        extra = f" ({note})" if note else ""
        print(f"  {mark} {name}: 検出 {total} / テーマ済 {kept}{extra}", file=sys.stderr)
    print(f"\n出力: {out_path}", file=sys.stderr)
    print(f"合計行数: {len(all_rows)}", file=sys.stderr)
    if all_skipped:
        print(f"スキップ: {len(all_skipped)} 件 (シーン1 空)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
