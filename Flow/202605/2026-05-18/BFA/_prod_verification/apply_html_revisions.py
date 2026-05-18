#!/usr/bin/env python3
"""
4ヶ月分の月報HTMLに対して、暦日基準 → 業務日基準 の表記置換を実施し、
text_revision_log.md と _prod_verification/final/ を生成する。
"""
import re, shutil, os
from pathlib import Path

ROOT = Path('/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA')
OUT  = ROOT / '_prod_verification' / 'final'
LOG  = ROOT / '_prod_verification' / 'text_revision_log.md'
OUT.mkdir(parents=True, exist_ok=True)

# (src, dst_in_final, month_int, last_day)
MONTHS = [
    (ROOT / '月報_202601' / '202601_BFA_月次報告資料.html', '202601_BFA_月次報告資料.html', 1, 31),
    (ROOT / '月報_202602' / '202602_BFA_月次報告資料.html', '202602_BFA_月次報告資料.html', 2, 28),
    (ROOT / '月報_202603' / '202603_BFA_月次報告資料.html', '202603_BFA_月次報告資料.html', 3, 31),
    (ROOT / '202604_BFA_月次報告資料_v2draft.html',          '202604_BFA_月次報告資料_v2draft.html', 4, 30),
]

log_blocks = []

for src, dst_name, m, last in MONTHS:
    text = src.read_text(encoding='utf-8')
    next_m = m + 1 if m != 12 else 1
    next_y = 2026 if m != 12 else 2027
    nm_str = f"{next_m}/1"

    # 月別の置換ペア
    replacements = [
        # KPIスライド / 分類条件 (with エアレジ言及)
        (f"集計対象: 2026/{m}/1 0:00 〜 {m}/{last} 23:59 の売上日時（エアレジ売上分析画面と一致）",
         f"集計対象: 2026年{m}月の業務日（{m}/1 6:00 〜 {nm_str} 5:59 JST、朝6時境界 ／ エアレジ売上分析画面と一致）"),

        # KPIスライド / 分類条件 (エアレジ言及なし)
        (f"集計対象: 2026/{m}/1 0:00 〜 {m}/{last} 23:59 の売上日時",
         f"集計対象: 2026年{m}月の業務日（{m}/1 6:00 〜 {nm_str} 5:59 JST、朝6時境界）"),

        # フッター注釈の日付範囲（暦日表記をやめて業務日明示）
        (f"集計対象: 2026-{m:02d}-01〜2026-{m:02d}-{last:02d}",
         f"集計対象: 2026年{m}月の業務日（朝6時境界、深夜営業を当日扱い）"),
    ]

    file_diffs = []
    for old, new in replacements:
        cnt = text.count(old)
        if cnt > 0:
            text = text.replace(old, new)
            file_diffs.append((cnt, old, new))

    dst = OUT / dst_name
    dst.write_text(text, encoding='utf-8')

    # build log block
    log_blocks.append(f"### {dst_name}\n")
    log_blocks.append(f"- ソース: `{src}`\n- 出力: `{dst}`\n\n")
    if not file_diffs:
        log_blocks.append("**置換なし**（既に業務日基準表記、または対象文字列が存在しない）\n\n")
    else:
        log_blocks.append("| 件数 | Before | After |\n|---:|---|---|\n")
        for cnt, old, new in file_diffs:
            old_md = old.replace('|', '\\|').replace('\n', ' ')
            new_md = new.replace('|', '\\|').replace('\n', ' ')
            log_blocks.append(f"| {cnt} | `{old_md}` | `{new_md}` |\n")
        log_blocks.append("\n")

    print(f"{dst_name}: {sum(c for c, _, _ in file_diffs)} replacements")

# Write log
LOG.write_text(
    "# HTML テキスト修正ログ（暦日基準 → 業務日基準）\n\n"
    "生成: 2026-05-18 / scope: BFA 4ヶ月分 (2026-01〜04)\n\n"
    "本ログは `apply_html_revisions.py` による一括置換の結果を記録する。\n"
    "元ファイルは触れず、置換結果は `_prod_verification/final/` 配下に出力。\n\n"
    + ''.join(log_blocks),
    encoding='utf-8'
)
print(f"\nLog written: {LOG}")
