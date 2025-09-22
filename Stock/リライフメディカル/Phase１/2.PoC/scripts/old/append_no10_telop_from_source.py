#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from typing import List

SOURCE_CSV = "/Users/rikutanaka/aipm_v0/Stock/リライフメディカル/Phase１/2.PoC/お役立ち情報台本.csv"
TARGET_CSV = "/Users/rikutanaka/aipm_v0/Flow/202509/2025-09-04/instagram_telop_no1-9.csv"

SCENE_COLUMNS = [
    "フック（0-5秒）",
    "共感（5-12秒）",
    "前提知識（12-21秒）",
    "メイン解説（21-30秒）",
    "解説まとめ（30-32秒）",
    "実践（32-44秒）",
    "CTA（42-45秒）",
]

AS_IS_SCENES = {
    "フック（0-5秒）",
    "共感（5-12秒）",
    "解説まとめ（30-32秒）",
}


def to_bullets(text: str, limit: int = 3) -> str:
    # Simple sentence split by '。' and '、' as hints; pick first non-empty chunks
    # Prioritize '。' endings
    if not text:
        return ""
    candidates: List[str] = []
    # Split by '。'
    for sent in text.split("。"):
        s = sent.strip(" \n\t　")
        if s:
            candidates.append(s)
    # If too short, also split by '、' to increase granularity
    if len(candidates) < limit:
        more: List[str] = []
        for c in candidates:
            if "、" in c:
                parts = [p.strip(" \n\t　") for p in c.split("、") if p.strip(" \n\t　")]
                if parts:
                    more.extend(parts)
        # Prefer more granular items if available
        if more:
            candidates = more
    bullets = [f"・{c}" for c in candidates[:limit]]
    return "\n".join(bullets)


def main() -> int:
    if not os.path.exists(SOURCE_CSV):
        print(f"Source CSV not found: {SOURCE_CSV}")
        return 1
    if not os.path.exists(TARGET_CSV):
        print(f"Target CSV not found: {TARGET_CSV}")
        return 2

    with open(SOURCE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row10 = None
        for r in reader:
            no_str = (r.get("No.") or r.get("No") or "").strip()
            if no_str == "10":
                row10 = r
                break
        if not row10:
            print("No.10 not found in source CSV")
            return 3

    theme = row10.get("テーマ", "").strip()

    # Prepare rows to append
    append_rows: List[List[str]] = []
    for scene in SCENE_COLUMNS:
        raw = row10.get(scene, "").strip()
        if scene in AS_IS_SCENES:
            telop = raw
        else:
            telop = to_bullets(raw, limit=3)
        append_rows.append(["10", theme, scene, telop])

    # Append to target CSV
    with open(TARGET_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(append_rows)

    print(f"Appended {len(append_rows)} rows for No.10 to {TARGET_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


