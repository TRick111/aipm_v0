#!/usr/bin/env python3
"""Stockのartifact実体は prefix なし、しかしサマリー内リンクは prefix 付き、という不整合を修正。

修正方針:
- Flowの per_conversation/{category}/artifacts/ の中身を一旦削除
- Stock の実ファイル（prefix なし）を Flow にそのままコピー
- サマリー md 内の `artifacts/{convId8}_xxx.md` → `artifacts/{xxx.md}` (prefix 除去)
"""
import re
import shutil
from pathlib import Path

STOCK_ROOT = Path("/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/pon-chatgpt-knowledge/ChatGPT履歴")
FLOW_ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件/output/per_conversation")
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]

# artifacts/{convId8}_{filename} → artifacts/{filename}
PREFIX_PATTERN = re.compile(r"artifacts/([0-9a-f]{8})_(?P<rest>[^)\s]+)")


def reset_and_copy_artifacts() -> dict[str, int]:
    counts = {}
    for cat in CATEGORIES:
        cat_dst = FLOW_ROOT / cat / "artifacts"
        if cat_dst.exists():
            shutil.rmtree(cat_dst)
        cat_dst.mkdir(parents=True, exist_ok=True)

        cat_src = STOCK_ROOT / cat
        copied = 0
        for art in cat_src.rglob("artifacts/*"):
            if not art.is_file():
                continue
            dst_file = cat_dst / art.name
            shutil.copy2(art, dst_file)
            copied += 1
        counts[cat] = copied
    return counts


def strip_prefix_in_summaries() -> dict[str, int]:
    stats = {"files_scanned": 0, "files_modified": 0, "paths_rewritten": 0}

    for md in FLOW_ROOT.rglob("*.md"):
        if "/artifacts/" in str(md):
            continue
        stats["files_scanned"] += 1

        content = md.read_text(encoding="utf-8")
        replaced = 0

        def replace(m):
            nonlocal replaced
            replaced += 1
            return f"artifacts/{m.group('rest')}"

        new_content = PREFIX_PATTERN.sub(replace, content)
        if replaced > 0:
            md.write_text(new_content, encoding="utf-8")
            stats["files_modified"] += 1
            stats["paths_rewritten"] += replaced

    return stats


def verify_links() -> dict[str, list]:
    """サマリー内の artifacts/* リンクが実ファイルに存在するかチェック。"""
    broken = []
    LINK_PATTERN = re.compile(r"artifacts/([^)\s]+\.md)")

    for md in FLOW_ROOT.rglob("*.md"):
        if "/artifacts/" in str(md):
            continue
        category = md.parent.name
        content = md.read_text(encoding="utf-8")
        for m in LINK_PATTERN.finditer(content):
            filename = m.group(1)
            target = FLOW_ROOT / category / "artifacts" / filename
            if not target.exists():
                broken.append((str(md), filename))

    return {"broken_count": len(broken), "examples": broken[:5]}


def main():
    print("=== Step 1: Reset Flow artifacts + recopy from Stock ===")
    counts = reset_and_copy_artifacts()
    for cat, n in counts.items():
        print(f"  {cat}: {n} files")
    print(f"  TOTAL: {sum(counts.values())}")

    print("\n=== Step 2: Strip convId prefix from summary paths ===")
    stats = strip_prefix_in_summaries()
    print(f"  files_scanned:   {stats['files_scanned']}")
    print(f"  files_modified:  {stats['files_modified']}")
    print(f"  paths_rewritten: {stats['paths_rewritten']}")

    print("\n=== Step 3: Verify all summary→artifact links resolve ===")
    v = verify_links()
    print(f"  broken_count: {v['broken_count']}")
    for src, missing in v["examples"]:
        print(f"  MISSING: {missing}  (from {src})")


if __name__ == "__main__":
    main()
