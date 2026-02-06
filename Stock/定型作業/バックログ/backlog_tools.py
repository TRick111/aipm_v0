#!/usr/bin/env python3
"""
Backlog tools (no external deps).

Source of truth: a single Markdown table in `Backlog.md`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_BACKLOG_PATH = os.path.join(os.path.dirname(__file__), "Backlog.md")


def _parse_iso_date(s: str) -> Optional[dt.date]:
    s = (s or "").strip()
    if not s:
        return None
    return dt.date.fromisoformat(s)


def _priority_rank(p: str) -> int:
    p = (p or "").strip().upper()
    m = re.fullmatch(r"P([0-3])", p)
    if not m:
        return 99
    return int(m.group(1))


def _read_markdown_table(md_path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Find the first table that contains an "ID" header.
    lines = text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "ID" in line and "Status" in line and "Priority" in line:
            start_idx = i
            break

    if start_idx is None or start_idx + 1 >= len(lines):
        raise ValueError("Could not find backlog table header line in markdown.")

    table_lines = []
    for j in range(start_idx, len(lines)):
        ln = lines[j].rstrip("\n")
        if not ln.strip().startswith("|"):
            # Stop at first non-table line after starting.
            if table_lines:
                break
            continue
        table_lines.append(ln)

    if len(table_lines) < 3:
        raise ValueError("Backlog table looks too short (need header, separator, at least one row).")

    # Convert markdown table to CSV text by stripping leading/trailing pipes and trimming spaces.
    # Assumes no escaped pipes inside cells (a documented rule).
    def md_row_to_cells(row: str) -> List[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]

    header = md_row_to_cells(table_lines[0])
    separator = table_lines[1]
    if set(separator.replace("|", "").strip()) <= {"-", ":", " "}:
        pass
    else:
        raise ValueError("Backlog table separator row is invalid.")

    data_rows = [md_row_to_cells(r) for r in table_lines[2:]]

    # Normalize lengths (some rows may have missing trailing empty cells).
    width = len(header)
    normalized_rows = []
    for row in data_rows:
        if len(row) < width:
            row = row + [""] * (width - len(row))
        elif len(row) > width:
            raise ValueError(f"Row has too many columns (expected {width}): {row}")
        normalized_rows.append(row)

    # Build dicts.
    records: List[Dict[str, str]] = []
    for row in normalized_rows:
        rec = dict(zip(header, row))
        # Skip completely empty rows
        if all(not (v or "").strip() for v in rec.values()):
            continue
        records.append(rec)

    return header, records


def _sort_key(rec: Dict[str, str]) -> Tuple[int, int, str]:
    # Priority (P0 best), then due date (earlier first, missing last), then ID.
    pr = _priority_rank(rec.get("Priority", ""))
    due = _parse_iso_date(rec.get("Due", ""))
    due_rank = due.toordinal() if due else 10**9
    return pr, due_rank, (rec.get("ID") or "")


def _filter_status(recs: List[Dict[str, str]], allowed: List[str]) -> List[Dict[str, str]]:
    allowed_set = {a.strip().lower() for a in allowed}
    out = []
    for r in recs:
        st = (r.get("Status") or "").strip().lower()
        if st in allowed_set:
            out.append(r)
    return out


def cmd_list(args: argparse.Namespace) -> int:
    _, recs = _read_markdown_table(args.backlog)
    recs = sorted(recs, key=_sort_key)

    if args.format == "json":
        print(json.dumps(recs, ensure_ascii=False, indent=2))
        return 0

    # markdown
    if not recs:
        print("(no tasks)")
        return 0

    cols = ["ID", "Status", "Priority", "Due", "Title", "Program", "Project", "Tags"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join(["---"] * len(cols)) + "|")
    for r in recs:
        row = [r.get(c, "") for c in cols]
        print("| " + " | ".join(row) + " |")
    return 0


def cmd_today(args: argparse.Namespace) -> int:
    _, recs = _read_markdown_table(args.backlog)
    target = _parse_iso_date(args.date) if args.date else dt.date.today()

    recs = _filter_status(recs, ["todo", "doing", "blocked"])
    out = []
    for r in recs:
        due = _parse_iso_date(r.get("Due", ""))
        if due == target:
            out.append(r)

    out = sorted(out, key=_sort_key)
    print(json.dumps(out, ensure_ascii=False, indent=2) if args.format == "json" else _as_compact_lines(out))
    return 0


def cmd_overdue(args: argparse.Namespace) -> int:
    _, recs = _read_markdown_table(args.backlog)
    today = dt.date.today()

    recs = _filter_status(recs, ["todo", "doing", "blocked"])
    out = []
    for r in recs:
        due = _parse_iso_date(r.get("Due", ""))
        if due and due < today:
            out.append(r)

    out = sorted(out, key=_sort_key)
    print(json.dumps(out, ensure_ascii=False, indent=2) if args.format == "json" else _as_compact_lines(out))
    return 0


def _as_compact_lines(recs: List[Dict[str, str]]) -> str:
    if not recs:
        return "(none)"
    lines = []
    for r in recs:
        lines.append(
            f"{r.get('ID','')}\t{r.get('Priority','')}\t{r.get('Due','')}\t{r.get('Title','')}\t[{r.get('Program','')}/{r.get('Project','')}]"
        )
    return "\n".join(lines)


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backlog", default=DEFAULT_BACKLOG_PATH, help="Path to backlog markdown file")

    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--format", choices=["md", "json"], default="md")
    p_list.set_defaults(func=cmd_list)

    p_today = sub.add_parser("today", help="Show tasks due today (or --date)")
    p_today.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p_today.add_argument("--format", choices=["lines", "json"], default="lines")
    p_today.set_defaults(func=cmd_today)

    p_overdue = sub.add_parser("overdue", help="Show overdue tasks (due < today)")
    p_overdue.add_argument("--format", choices=["lines", "json"], default="lines")
    p_overdue.set_defaults(func=cmd_overdue)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

