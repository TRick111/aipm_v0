#!/usr/bin/env python3
"""
build_monthly_html.py が "2026-04" を当月としてハードコードしているため、
analysis.json のキーを当月→"2026-04"、前月→"2026-03"、前年同月→"2025-04"、
直近6ヶ月→["2025-11"..."2026-04"] に揃えた "remapped_analysis.json" を作成し、
HTML を生成。その後 HTML 内の月文字列を本来の月へ置換する。
"""
import json
import subprocess
import sys
import os
import re
from pathlib import Path

HERE = Path(__file__).parent
TARGET_MONTH = "2026-01"
PREV_MONTH = "2025-12"
PY_SAME = "2025-01"  # 前年同月
TREND_SRC = ["2025-08","2025-09","2025-10","2025-11","2025-12","2026-01"]
TREND_DST = ["2025-11","2025-12","2026-01","2026-02","2026-03","2026-04"]
TARGET_M_NUM = 1

with open(HERE / "analysis.json") as f:
    d = json.load(f)

# Remap month_kpis keys
mk = d["month_kpis"]
new_mk = {}
key_map = {
    TARGET_MONTH: "2026-04",
    PREV_MONTH: "2026-03",
    PY_SAME: "2025-04",
}
# trend reassignment
for src, dst in zip(TREND_SRC, TREND_DST):
    if src in key_map:
        continue
    key_map[src] = dst

for old_key, val in mk.items():
    new_key = key_map.get(old_key, old_key)
    val = dict(val)
    val["month"] = new_key
    new_mk[new_key] = val

d["month_kpis"] = new_mk
# Keep target_month true so period strings remain accurate
d["target_month"] = TARGET_MONTH

# Save remapped JSON
remap_path = HERE / "remapped_analysis.json"
with open(remap_path, "w") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f"Remapped: {sorted(new_mk.keys())}")

# Run build script
output_html = HERE / "202601_BFA_月次報告資料.html"
build_script = "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/月報/Scripts/build_monthly_html.py"
res = subprocess.run([
    "python3", build_script,
    "--analysis-json", str(remap_path),
    "--output", str(output_html),
], capture_output=True, text=True)
print("STDOUT:", res.stdout[-500:])
print("STDERR:", res.stderr[-500:])
if res.returncode != 0:
    sys.exit(res.returncode)

# Post-process HTML to fix hardcoded month strings
with open(output_html, "r", encoding="utf-8") as f:
    html = f.read()

# Replace month tags (in order longer-first to avoid partial overlaps)
replacements = [
    ("2026-04", TARGET_MONTH),
    ("2026-03", PREV_MONTH),
    ("2025-04", PY_SAME),
    ("2026/4/1", f"2026/{TARGET_M_NUM}/1"),
    ("2026/4/", f"2026/{TARGET_M_NUM}/"),
    # Japanese month text
    ("4月の", "1月の"),
    ("4月は", "1月は"),
    ("4月から", "1月から"),
    ("4月家賃", "1月家賃"),
    ("4月後半", "1月後半"),
    ("当月（4月）", "当月（1月）"),
    ("「4月」", "「1月」"),
    ("4月のみ計上", "1月のみ計上"),
    # period strings already correctly emitted from _tm
]
for old, new in replacements:
    html = html.replace(old, new)

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML written and post-processed: {output_html}")

# Count slides
slide_count = html.count('class="slide"') or html.count("<section class=\"slide")
print(f"Slide count (approx): {slide_count}")
