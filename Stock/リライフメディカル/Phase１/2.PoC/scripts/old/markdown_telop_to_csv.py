#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import re
import sys
from typing import List, Tuple

HEADER_NO = "No"
HEADER_THEME = "テーマ"
HEADER_SCENE = "シーン名"
HEADER_TELOP = "テロップ内容"


def parse_markdown_tables(md_text: str) -> List[Tuple[str, str, str, str]]:
    """
    Parse the specific Markdown format used in instagram_telop_noX-Y.md and
    return rows as tuples: (no, theme, scene, telop)
    
    The parser supports multi-line table cells where the second cell spans
    multiple physical lines, with the final line ending with a trailing '|'.
    """
    rows: List[Tuple[str, str, str, str]] = []

    current_no: str = ""
    current_theme: str = ""

    lines = md_text.splitlines()

    # Regex to capture heading lines like: "### No.1 テーマ：..."
    heading_re = re.compile(r"^###\s*No\.(\d+)\s+テーマ：(.+)$")

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Detect heading and set context
        m = heading_re.match(line.strip())
        if m:
            current_no = m.group(1).strip()
            current_theme = m.group(2).strip()
            i += 1
            continue

        # Detect table header row start
        if line.strip().startswith("| "):
            # Look ahead for a separator line of the form |---|---|
            if i + 1 < n and set(lines[i + 1].strip()) <= set("|- ") and "---" in lines[i + 1]:
                # Skip header (two lines)
                i += 2

                # Parse table body rows until a blank line or next heading
                while i < n:
                    body_line = lines[i]
                    stripped = body_line.strip()

                    # Stop conditions: blank line or next heading
                    if not stripped or stripped.startswith("### "):
                        break

                    # Skip separator lines defensively
                    if set(stripped) <= set("|- ") and "---" in stripped:
                        i += 1
                        continue

                    # If row starts with a pipe, it begins a new row
                    if stripped.startswith("| "):
                        # Parse first line of row: split into first and second cell (no trailing pipe required)
                        # Example: | シーン名 | 内容 ...
                        first_line = stripped
                        # Remove the leading pipe and possible trailing pipe (only for splitting convenience)
                        inner = first_line.lstrip("|").rstrip()
                        # Do not rstrip('|') here to preserve the possibility that content ends with ' |'
                        # Split at the first pipe separating scene and content
                        if "|" not in inner:
                            i += 1
                            continue
                        scene_part, content_part = inner.split("|", 1)
                        scene = scene_part.strip()
                        # Normalize the current content accumulator
                        telop_parts: List[str] = []

                        # If the first line finishes the row (ends with a trailing '|'), drop that trailing pipe
                        ends_with_pipe = first_line.endswith("|")
                        # Clean content on this line (remove possible trailing pipe at end)
                        content_piece = content_part
                        if ends_with_pipe and content_piece.endswith("|"):
                            content_piece = content_piece[:-1]
                        telop_parts.append(content_piece.strip())

                        # If not finished, continue accumulating subsequent lines until a line with trailing '|'
                        if not ends_with_pipe:
                            i += 1
                            while i < n:
                                cont_line = lines[i]
                                cont_stripped = cont_line.rstrip()
                                # If we encounter a new row or heading, stop (defensive)
                                if cont_stripped.startswith("| ") or cont_stripped.startswith("### "):
                                    # We didn't find a closing pipe; finalize what we have
                                    break
                                # Detect a final line with a closing pipe at the end
                                if cont_stripped.endswith("|"):
                                    # Append without the trailing pipe
                                    telop_parts.append(cont_stripped[:-1].strip())
                                    i += 1
                                    break
                                else:
                                    telop_parts.append(cont_stripped.strip())
                                    i += 1
                        else:
                            i += 1

                        # Join telop parts with literal newlines (CSV will quote as needed)
                        telop = "\n".join([p for p in (p.strip() for p in telop_parts) if p])
                        # Remove trailing two-space markdown line-break markers
                        telop = re.sub(r"\s{2,}$", "", telop, flags=re.MULTILINE)

                        # Normalize multiple consecutive blank lines in telop
                        telop = re.sub(r"\n{3,}", "\n\n", telop)

                        rows.append((current_no, current_theme, scene, telop))
                        continue
                    else:
                        # Not a row start; advance
                        i += 1
                        continue
                # End of table body loop
                continue
        i += 1

    return rows


def write_csv(rows: List[Tuple[str, str, str, str]], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([HEADER_NO, HEADER_THEME, HEADER_SCENE, HEADER_TELOP])
        for no, theme, scene, telop in rows:
            writer.writerow([no, theme, scene, telop])


def main(argv: List[str]) -> int:
    if len(argv) < 3:
        print("Usage: markdown_telop_to_csv.py <input_md_path> <output_csv_path>")
        return 2
    in_path = argv[1]
    out_path = argv[2]

    if not os.path.exists(in_path):
        print(f"Input not found: {in_path}")
        return 1

    with open(in_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    rows = parse_markdown_tables(md_text)
    write_csv(rows, out_path)

    print(f"Wrote {len(rows)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
