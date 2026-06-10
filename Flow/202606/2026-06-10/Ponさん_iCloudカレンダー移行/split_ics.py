#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ICSファイル分割スクリプト
========================

iCloudカレンダー等からエクスポートした大きな ICS ファイルを、
Googleカレンダーに安全にインポートできるサイズに分割します。

特徴:
- macOS 標準の python3 だけで動く（追加インストール不要）
- VCALENDAR ヘッダ / VTIMEZONE を各分割ファイルに複製するので
  そのまま Google カレンダーにインポートできる
- ICS の行折り返し (line folding) を正しく扱う
- 出力は CRLF（RFC 5545 準拠）

使い方:
    python3 split_ics.py path/to/calendar.ics
    python3 split_ics.py path/to/calendar.ics --events 500
    python3 split_ics.py path/to/calendar.ics --output-dir ./out --events 500
"""

import argparse
import sys
from pathlib import Path


CRLF = "\r\n"


def read_lines_unfolded(path: Path):
    """ICSファイルを読み込み、folding を解いた論理行のリストを返す。

    RFC 5545: 改行直後にスペースまたはタブで始まる行は、前の行の続き。
    （改行とその直後の1文字を取り除いて結合する）
    """
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    physical_lines = text.split("\n")

    logical = []
    for line in physical_lines:
        if line.startswith((" ", "\t")) and logical:
            logical[-1] += line[1:]
        else:
            logical.append(line)
    while logical and logical[-1] == "":
        logical.pop()
    return logical


def parse_calendar(lines):
    """論理行のリストから、ヘッダ / VTIMEZONE群 / VEVENT群 / その他 を抽出。"""
    try:
        start = next(i for i, l in enumerate(lines)
                     if l.strip().upper() == "BEGIN:VCALENDAR")
        end = next(i for i in range(len(lines) - 1, -1, -1)
                   if lines[i].strip().upper() == "END:VCALENDAR")
    except StopIteration:
        raise ValueError(
            "有効な VCALENDAR ブロックが見つかりません。"
            "ICSファイルではない可能性があります。"
        )

    body = lines[start + 1:end]

    header = []
    timezones = []
    events = []
    others = []

    i = 0
    while i < len(body):
        line = body[i]
        upper = line.strip().upper()
        if upper.startswith("BEGIN:"):
            comp_name = upper[len("BEGIN:"):]
            end_marker = "END:" + comp_name
            depth = 1
            j = i + 1
            while j < len(body):
                inner_upper = body[j].strip().upper()
                if inner_upper == "BEGIN:" + comp_name:
                    depth += 1
                elif inner_upper == end_marker:
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j >= len(body):
                raise ValueError(
                    f"{comp_name} に対応する END が見つかりません"
                )
            block = body[i:j + 1]
            if comp_name == "VTIMEZONE":
                timezones.append(block)
            elif comp_name == "VEVENT":
                events.append(block)
            else:
                others.append(block)
            i = j + 1
        else:
            header.append(line)
            i += 1

    return header, timezones, events, others


def fold_line(line: str, limit: int = 75) -> str:
    """RFC 5545 の line folding: 75オクテットごとに CRLF+SP で折り返す。
    UTF-8 のマルチバイト文字を途中で切らない。"""
    encoded = line.encode("utf-8")
    if len(encoded) <= limit:
        return line
    out = []
    cur = bytearray()
    for b in encoded:
        if len(cur) >= limit and (b & 0xC0) != 0x80:
            out.append(bytes(cur).decode("utf-8"))
            cur = bytearray()
        cur.append(b)
    if cur:
        out.append(bytes(cur).decode("utf-8"))
    return (CRLF + " ").join(out)


def write_ics(path: Path, header, timezones, events, others):
    parts = ["BEGIN:VCALENDAR"]
    parts.extend(header)
    for tz in timezones:
        parts.extend(tz)
    for ev in events:
        parts.extend(ev)
    for other in others:
        parts.extend(other)
    parts.append("END:VCALENDAR")

    folded = [fold_line(l) for l in parts]
    content = CRLF.join(folded) + CRLF
    path.write_bytes(content.encode("utf-8"))


def human_size(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def main():
    parser = argparse.ArgumentParser(
        description="ICSファイルを Googleカレンダー向けに分割します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "例:\n"
            "  python3 split_ics.py calendar.ics\n"
            "  python3 split_ics.py calendar.ics --events 500\n"
        ),
    )
    parser.add_argument("input", help="入力ICSファイルのパス")
    parser.add_argument("--events", type=int, default=500,
                        help="1ファイルあたりのイベント数 (デフォルト: 500)")
    parser.add_argument("--output-dir", default=None,
                        help="出力フォルダ (デフォルト: <入力ファイル名>_split)")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"ERROR: 入力ファイルが見つかりません: {input_path}",
              file=sys.stderr)
        sys.exit(1)

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        output_dir = input_path.with_name(input_path.stem + "_split")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"入力ファイル: {input_path}")
    print(f"サイズ:       {human_size(input_path.stat().st_size)}")
    print(f"出力フォルダ: {output_dir}")
    print()

    print("読み込み & 解析中...")
    lines = read_lines_unfolded(input_path)
    header, timezones, events, others = parse_calendar(lines)

    print(f"  VEVENT:          {len(events)} 件")
    print(f"  VTIMEZONE:       {len(timezones)} 件（全分割ファイルに複製）")
    if others:
        print(f"  その他コンポーネント: {len(others)} 件"
              "（最初のファイルにまとめて出力）")
    print()

    if not events:
        print("WARNING: VEVENT が1件も見つかりませんでした。終了します。")
        sys.exit(0)

    chunk_size = args.events
    total_chunks = (len(events) + chunk_size - 1) // chunk_size
    width = len(str(total_chunks))

    print(f"分割中 ({chunk_size} 件/ファイル, 計 {total_chunks} ファイル)...")
    for idx in range(total_chunks):
        chunk_events = events[idx * chunk_size:(idx + 1) * chunk_size]
        chunk_others = others if idx == 0 else []
        out_name = (
            f"{input_path.stem}_part{str(idx + 1).zfill(width)}"
            f"_of_{total_chunks}.ics"
        )
        out_path = output_dir / out_name
        write_ics(out_path, header, timezones, chunk_events, chunk_others)
        size = out_path.stat().st_size
        print(f"  {out_name}  ({len(chunk_events)} 件 / {human_size(size)})")

    print()
    print("完了しました。")
    print("Googleカレンダーに以下の手順でインポートしてください:")
    print("  1. https://calendar.google.com を開く")
    print("  2. 左の「他のカレンダー」横の + → 「インポート」")
    print("  3. 出力フォルダ内の .ics ファイルを 1つずつアップロード")
    print("  4. インポート先カレンダーを指定 → インポート")
    print()
    print("※ 同じイベントを2回入れると重複するため、再実行は注意してください。")


if __name__ == "__main__":
    main()
