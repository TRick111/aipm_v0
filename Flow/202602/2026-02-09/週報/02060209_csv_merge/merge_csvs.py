#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV統合（種類ごとに1ファイルへ）

- 入力: Stock/RestaurantAILab/週報/0_downloads/02060209 のCSV群
- 出力: 本スクリプトと同じフォルダに、種類ごとの統合CSV（合計5ファイル）とレポートを生成

方針:
- 各種類ごとに「ヘッダー行」を1つに定義（最初のファイルのヘッダーをcanonicalとする）
- 以降のファイルはヘッダー行を除外して追記
- ヘッダー列順が異なる場合は「列名で突合して並べ替え」して追記
- 空行（フィールドが全て空）は除外し、末尾に余計な空行が残らないようにする
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


INPUT_DIR = Path("/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/0_downloads/02060209")
OUT_DIR = Path("/Users/rikutanaka/aipm_v0/Flow/202602/2026-02-09/週報/02060209_csv_merge")


DATE_RANGE_RE = re.compile(r"(?P<start>\d{8})-(?P<end>\d{8})-")


def try_decode_encoding(path: Path) -> str:
    """
    このフォルダのCSVはUTF-8よりもCP932(Shift-JIS)の可能性が高い。
    まずutf-8-sigを厳格に試し、ダメならcp932に落とす。
    """
    try:
        path.read_text(encoding="utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError:
        return "cp932"


def first_nonempty_line_idx(lines: Iterable[str]) -> Optional[int]:
    for i, line in enumerate(lines):
        if line.strip() != "":
            return i
    return None


def find_azabu_header_idx(lines: Iterable[str]) -> Optional[int]:
    """
    麻布しきのCSVは先頭にメタ情報・説明があり、
    実データのヘッダー行が '"H.' で始まる。
    """
    for i, line in enumerate(lines):
        s = line.lstrip()
        # 説明文にある "H.  -->> ..." を誤検出しないように、必ずCSVヘッダーの '"H.' を条件にする
        if s.startswith('"H.'):
            return i
    return None


def parse_csv_row(line: str) -> List[str]:
    return next(csv.reader([line]))


def iter_lines_from(path: Path, *, encoding: str, start_idx: int) -> Iterator[str]:
    with path.open("r", encoding=encoding, newline="") as f:
        for i, line in enumerate(f):
            if i >= start_idx:
                yield line


def parse_date_range_from_filename(name: str) -> Optional[Tuple[datetime, datetime]]:
    m = DATE_RANGE_RE.search(name)
    if not m:
        return None
    try:
        s = datetime.strptime(m.group("start"), "%Y%m%d")
        e = datetime.strptime(m.group("end"), "%Y%m%d")
        return s, e
    except Exception:
        return None


def ranges_overlap(a: Tuple[datetime, datetime], b: Tuple[datetime, datetime]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


@dataclass
class MergeStats:
    type_name: str
    output_path: Path
    input_files: List[Path]
    encodings: Dict[str, str]
    canonical_header: List[str]
    file_header_orders: Dict[str, List[str]]
    rows_written: int
    empty_rows_skipped: int
    warnings: List[str]


def classify_file(path: Path) -> Optional[str]:
    n = path.name
    if not n.lower().endswith(".csv"):
        return None
    if "別天地 銀座-orders" in n:
        return "bettenti_ginza_orders"
    if "別天地 銀座-transactions" in n:
        return "bettenti_ginza_transactions"
    if "BAR FIVE Arrows" in n:
        return "bar_five_arrows"
    if "かめや駅前店" in n:
        return "kameya_ekimae"
    if "麻布しき" in n:
        return "azabu_shiki"
    return None


def locate_header_line(path: Path, *, encoding: str, type_name: str) -> int:
    with path.open("r", encoding=encoding, newline="") as f:
        if type_name == "azabu_shiki":
            idx = find_azabu_header_idx(f)
        else:
            idx = first_nonempty_line_idx(f)
    if idx is None:
        raise RuntimeError(f"ヘッダー行が見つかりません: {path}")
    return idx


def header_and_reader(
    path: Path, *, encoding: str, header_idx: int
) -> Tuple[List[str], Iterator[List[str]]]:
    lines_iter = iter_lines_from(path, encoding=encoding, start_idx=header_idx)
    reader = csv.reader(lines_iter)
    header = next(reader)  # header row
    return header, reader


def is_effectively_empty_row(row: Sequence[str]) -> bool:
    return all((c.strip() == "") for c in row)


def merge_one_type(type_name: str, files: List[Path], output_path: Path) -> MergeStats:
    if not files:
        raise ValueError(f"files empty for type={type_name}")

    files_sorted = sorted(files, key=lambda p: p.name)
    encodings: Dict[str, str] = {}
    file_header_orders: Dict[str, List[str]] = {}
    warnings: List[str] = []

    # overlap check (filename range)
    ranges: List[Tuple[Path, Tuple[datetime, datetime]]] = []
    for p in files_sorted:
        r = parse_date_range_from_filename(p.name)
        if r:
            ranges.append((p, r))
    for i in range(len(ranges)):
        for j in range(i + 1, len(ranges)):
            if ranges_overlap(ranges[i][1], ranges[j][1]):
                warnings.append(
                    f"期間が重複の可能性: {ranges[i][0].name} と {ranges[j][0].name}（重複分の除去はしていません）"
                )

    # 1) pre-scan headers to build canonical (union) header
    canonical_header: List[str] = []
    for p in files_sorted:
        enc = try_decode_encoding(p)
        encodings[p.name] = enc
        hidx = locate_header_line(p, encoding=enc, type_name=type_name)
        hdr, _ = header_and_reader(p, encoding=enc, header_idx=hidx)
        file_header_orders[p.name] = hdr
        # stable union: keep first-seen order across files_sorted
        for col in hdr:
            if col not in canonical_header:
                canonical_header.append(col)

    # Heuristic warning when multiple formats appear
    unique_header_signatures = {tuple(h) for h in file_header_orders.values()}
    if len(unique_header_signatures) > 1:
        warnings.append(
            "同一種類内でヘッダー形式が複数検出されました（列の和集合ヘッダーに統一し、存在しない列は空欄で埋めています）"
        )

    # writer (UTF-8 with BOM for Excel compatibility)
    rows_written = 0
    empty_rows_skipped = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as out_f:
        writer = csv.writer(out_f, lineterminator="\n")
        writer.writerow(canonical_header)

        def write_rows(src_header: List[str], src_reader: Iterator[List[str]]) -> None:
            nonlocal rows_written, empty_rows_skipped
            src_pos: Dict[str, int] = {name: i for i, name in enumerate(src_header)}

            for row in src_reader:
                if is_effectively_empty_row(row):
                    empty_rows_skipped += 1
                    continue
                # pad just in case
                if len(row) < len(src_header):
                    row = list(row) + [""] * (len(src_header) - len(row))
                out_row: List[str] = []
                for c in canonical_header:
                    i = src_pos.get(c)
                    out_row.append(row[i] if i is not None and i < len(row) else "")
                if is_effectively_empty_row(out_row):
                    empty_rows_skipped += 1
                    continue
                writer.writerow(out_row)
                rows_written += 1

        # write all files (header row skipped via reader)
        for p in files_sorted:
            enc = encodings[p.name]
            hidx = locate_header_line(p, encoding=enc, type_name=type_name)
            header, reader = header_and_reader(p, encoding=enc, header_idx=hidx)
            write_rows(header, reader)

    return MergeStats(
        type_name=type_name,
        output_path=output_path,
        input_files=files_sorted,
        encodings=encodings,
        canonical_header=canonical_header,
        file_header_orders=file_header_orders,
        rows_written=rows_written,
        empty_rows_skipped=empty_rows_skipped,
        warnings=warnings,
    )


def main() -> int:
    if not INPUT_DIR.exists():
        raise SystemExit(f"INPUT_DIR not found: {INPUT_DIR}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    groups: Dict[str, List[Path]] = {}
    for p in sorted(INPUT_DIR.glob("*.csv")):
        t = classify_file(p)
        if not t:
            continue
        groups.setdefault(t, []).append(p)

    # expected 5 groups
    expected = [
        "azabu_shiki",
        "bar_five_arrows",
        "kameya_ekimae",
        "bettenti_ginza_orders",
        "bettenti_ginza_transactions",
    ]
    missing = [k for k in expected if k not in groups]
    if missing:
        raise SystemExit(f"missing groups: {missing}")

    outputs = {
        "azabu_shiki": OUT_DIR / "merged_麻布しき.csv",
        "bar_five_arrows": OUT_DIR / "merged_BAR FIVE Arrows.csv",
        "kameya_ekimae": OUT_DIR / "merged_かめや駅前店.csv",
        "bettenti_ginza_orders": OUT_DIR / "merged_別天地 銀座-orders.csv",
        "bettenti_ginza_transactions": OUT_DIR / "merged_別天地 銀座-transactions.csv",
    }

    stats_all: List[MergeStats] = []
    for t in expected:
        st = merge_one_type(t, groups[t], outputs[t])
        stats_all.append(st)

    report_path = OUT_DIR / "merge_report.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with report_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(f"# CSV統合レポート（02060209）\n\n")
        f.write(f"- 生成日時: {now}\n")
        f.write(f"- 入力フォルダ: `{INPUT_DIR}`\n")
        f.write(f"- 出力フォルダ: `{OUT_DIR}`\n")
        f.write(f"- 出力エンコーディング: **UTF-8(BOM付き / utf-8-sig)**（Excel互換性のため）\n\n")

        for st in stats_all:
            f.write(f"## {st.type_name}\n\n")
            f.write(f"- 出力: `{st.output_path.name}`\n")
            f.write(f"- 入力ファイル数: {len(st.input_files)}\n")
            f.write(f"- 書き込み行数（ヘッダー除く）: {st.rows_written}\n")
            f.write(f"- 除外した空行数: {st.empty_rows_skipped}\n\n")

            if st.warnings:
                f.write("### 注意（検出した点）\n\n")
                for w in st.warnings:
                    f.write(f"- {w}\n")
                f.write("\n")

            f.write("### 入力ファイル\n\n")
            for p in st.input_files:
                f.write(f"- `{p.name}` (encoding={st.encodings.get(p.name)})\n")
            f.write("\n")

            f.write("### ヘッダーとして理解したもの（canonical）\n\n")
            f.write("`" + "`, `".join(st.canonical_header) + "`\n\n")

            # header order diffs (only when different)
            diffs = []
            for fn, hdr in st.file_header_orders.items():
                if hdr != st.canonical_header:
                    diffs.append(fn)
            if diffs:
                f.write("### ヘッダー順の差分\n\n")
                f.write("- canonicalと列順が異なるファイルは、**列名で突合して並べ替え**て追記しました。\n")
                for fn in diffs:
                    f.write(f"  - `{fn}`\n")
                f.write("\n")

    print("Generated:")
    for st in stats_all:
        print(f"- {st.output_path}")
    print(f"- {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

