#!/usr/bin/env python3
"""artifacts を Stock 側から per_conversation/{category}/artifacts/ に集約し、
サマリーmd内の相対パスを ./artifacts/{filename} に書き換える。

Stock側ソース:
  Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/pon-chatgpt-knowledge/
    ChatGPT履歴/{category}/{subcategory}/artifacts/{filename}

新配置:
  Flow/202606/2026-06-05/.../バンコクPonさん案件/output/per_conversation/
    {category}/
      {summary}.md         ← パス書き換え対象
      artifacts/{filename} ← フラット配置（subcategoryフォルダなし）
"""
import re
import shutil
from pathlib import Path

STOCK_ROOT = Path("/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/pon-chatgpt-knowledge/ChatGPT履歴")
FLOW_ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件/output/per_conversation")
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]

# 古い相対パス（5階層上がる）のパターン → 新パス
# 例: ../../../../../Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/pon-chatgpt-knowledge/ChatGPT履歴/美容室/Rapi-rabi/artifacts/{file}
OLD_PATH_PATTERN = re.compile(
    r"(\.\./)+Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/pon-chatgpt-knowledge/ChatGPT履歴/"
    r"(?P<category>[^/]+)/(?P<subcategory>[^/]+)/artifacts/(?P<filename>[^)]+)"
)


def copy_artifacts() -> dict[str, int]:
    """Stockのartifactsをカテゴリ配下にコピー。"""
    counts = {}
    for cat in CATEGORIES:
        cat_src = STOCK_ROOT / cat
        cat_dst = FLOW_ROOT / cat / "artifacts"
        cat_dst.mkdir(parents=True, exist_ok=True)

        copied = 0
        for art in cat_src.rglob("artifacts/*"):
            if not art.is_file():
                continue
            dst_file = cat_dst / art.name
            shutil.copy2(art, dst_file)
            copied += 1
        counts[cat] = copied
    return counts


def rewrite_summary_paths() -> dict[str, int]:
    """各サマリーmd内のartifact相対パスを ./artifacts/{filename} に書き換え。"""
    stats = {"files_scanned": 0, "files_modified": 0, "paths_rewritten": 0}

    for md in FLOW_ROOT.rglob("*.md"):
        # artifacts/配下は除外
        if "/artifacts/" in str(md):
            continue
        stats["files_scanned"] += 1

        content = md.read_text(encoding="utf-8")
        replaced_count = 0

        def replace(m):
            nonlocal replaced_count
            replaced_count += 1
            return f"artifacts/{m.group('filename')}"

        new_content = OLD_PATH_PATTERN.sub(replace, content)
        if replaced_count > 0:
            md.write_text(new_content, encoding="utf-8")
            stats["files_modified"] += 1
            stats["paths_rewritten"] += replaced_count

    return stats


def main():
    print("=== Step 1: Copying artifacts ===")
    counts = copy_artifacts()
    for cat, n in counts.items():
        print(f"  {cat}: {n} files copied")
    print(f"  TOTAL: {sum(counts.values())} files")

    print("\n=== Step 2: Rewriting paths in summaries ===")
    stats = rewrite_summary_paths()
    print(f"  files_scanned:   {stats['files_scanned']}")
    print(f"  files_modified:  {stats['files_modified']}")
    print(f"  paths_rewritten: {stats['paths_rewritten']}")


if __name__ == "__main__":
    main()
