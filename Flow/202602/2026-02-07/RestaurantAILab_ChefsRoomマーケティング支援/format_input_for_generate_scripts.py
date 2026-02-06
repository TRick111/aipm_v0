#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow/…/input.csv（ブロック型: 1本が複数行）を、
generate_scripts_with_gemini.py が読める「1行=1テーマ」CSVに整形する。

出力:
- script_input/input_for_generate_scripts_72.csv
- script_input/format_report.md
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


IN_PATH = Path(__file__).resolve().parent / "input.csv"
OUT_DIR = Path(__file__).resolve().parent / "script_input"
OUT_CSV = OUT_DIR / "input_for_generate_scripts_72.csv"
OUT_REPORT = OUT_DIR / "format_report.md"


HEADER_RE = re.compile(r"^(\d+)\n(.+)$")


@dataclass
class Block:
    seq: int  # 1..72 (出現順)
    raw_no: int
    category: str
    memo_raw: str
    rows: List[List[str]]


def clean_text(s: str) -> str:
    s = (s or "").strip()
    # 余分な連続空白・改行を整える（CSV上は改行OKだが、テーマは見やすくする）
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def clean_memo(memo_raw: str) -> str:
    memo = memo_raw or ""
    memo = re.sub(r"^\s*ネタメモ：\s*", "", memo)
    return clean_text(memo)


def iter_blocks(path: Path) -> Iterable[Block]:
    cur: Optional[Block] = None
    seq = 0
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        for row in r:
            # ブロック開始行: row[0]=='' かつ row[1] が "{num}\n{category}"
            if len(row) >= 4 and (row[0] or "").strip() == "":
                m = HEADER_RE.match(row[1] or "")
                if m:
                    if cur is not None:
                        yield cur
                    seq += 1
                    raw_no = int(m.group(1))
                    category = (m.group(2) or "").strip()
                    memo_raw = row[3] or ""
                    cur = Block(
                        seq=seq,
                        raw_no=raw_no,
                        category=category,
                        memo_raw=memo_raw,
                        rows=[],
                    )
            if cur is not None:
                cur.rows.append(row)

    if cur is not None:
        yield cur


def extract_by_scene(block: Block, scene_no: str) -> str:
    """
    ブロック内の scene_no（列4）に対応するテキスト（列5）を最初に見つかったものから返す。
    """
    for row in block.rows:
        if len(row) < 5:
            continue
        scene = (row[3] or "").strip()
        text = (row[4] or "").strip()
        if scene == scene_no and text:
            return text
    return ""


def extract_fields(block: Block) -> Dict[str, str]:
    """
    generate_scripts_with_gemini.py が参照するキー:
    - テーマ or タイトル
    - フック（またはフック（0-5秒））
    - 解決策
    - エンド
    """
    memo = clean_memo(block.memo_raw)

    # まずは「狙いの行」から抽出
    hook = extract_by_scene(block, "1")
    solution = extract_by_scene(block, "13")
    ending = extract_by_scene(block, "17")

    hook = clean_text(hook)
    solution = clean_text(solution)
    ending = clean_text(ending)

    # 欠損時のフォールバック（最低限テーマだけは埋める）
    if not hook:
        hook = memo
    if not solution:
        solution = ""
    if not ending:
        ending = ""

    theme = memo or hook or f"テーマ{block.seq}"
    theme = clean_text(theme.replace("\n", " "))  # テーマは1行に寄せる

    return {
        "テーマ": theme,
        "タイトル": theme,
        "フック": hook,
        "解決策": solution,
        "エンド": ending,
        "ネタメモ": memo,
        "カテゴリ": block.category,
        "元No": str(block.raw_no),
        "管理No": str(block.seq),
    }


def main() -> int:
    if not IN_PATH.exists():
        raise SystemExit(f"入力が見つかりません: {IN_PATH}")

    blocks = list(iter_blocks(IN_PATH))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = [extract_fields(b) for b in blocks]

    # 検証
    total = len(rows)
    missing_theme = sum(1 for r in rows if not (r.get("テーマ") or "").strip())
    missing_hook = sum(1 for r in rows if not (r.get("フック") or "").strip())
    missing_sol = sum(1 for r in rows if not (r.get("解決策") or "").strip())
    missing_end = sum(1 for r in rows if not (r.get("エンド") or "").strip())

    # 書き出し（余計な列があってもスクリプト側は無視するのでOK）
    headers = [
        "管理No",
        "テーマ",
        "タイトル",
        "フック",
        "解決策",
        "エンド",
        "ネタメモ",
        "カテゴリ",
        "元No",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # レポート
    with OUT_REPORT.open("w", encoding="utf-8") as f:
        f.write("# input.csv 整形レポート\n\n")
        f.write(f"- 入力: `{IN_PATH}`\n")
        f.write(f"- 出力: `{OUT_CSV}`\n")
        f.write(f"- ブロック数（=動画案数）: **{total}**\n\n")
        f.write("## 欠損（空欄）カウント\n\n")
        f.write(f"- テーマ: {missing_theme}\n")
        f.write(f"- フック: {missing_hook}\n")
        f.write(f"- 解決策: {missing_sol}\n")
        f.write(f"- エンド: {missing_end}\n\n")
        f.write("## 先頭5件（テーマ）\n\n")
        for r in rows[:5]:
            f.write(f"- {r['管理No']}. {r['テーマ']}\n")
        f.write("\n")

    print(f"OK: wrote {total} rows -> {OUT_CSV}")
    print(f"Report -> {OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

