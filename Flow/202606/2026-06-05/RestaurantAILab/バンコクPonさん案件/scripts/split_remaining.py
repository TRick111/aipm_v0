#!/usr/bin/env python3
"""残り224件 (既存49件再生成 + 未処理175件) を 10件×23バッチに分割。

- 6921aecb (再生成済みサンプル) はスキップ
- artifacts 有り優先、その中で長文順
- カテゴリ偏りを避けるためラウンドロビン分配
"""
import json
from pathlib import Path

CONV_DIR = Path("/Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT分析/pipeline/step1_extracted/conversations")
INDEX_ROOT = Path("/Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行")
OUT_DIR = Path("/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件/scripts/batches/round2")

PER_BATCH = 10
SKIP_IDS = {"6921aecb-f0c8-8321-9066-2418c46a224d"}  # 再生成済みサンプル


def load_index() -> dict[str, dict]:
    result = {}
    for idx_path in INDEX_ROOT.rglob("conversations_index.json"):
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        category = data.get("category", "")
        subcategory = data.get("subcategory_dir", "")
        for a in data.get("artifacts", []):
            cid = a["conversation_id"]
            result.setdefault(cid, {
                "category": category,
                "subcategory": subcategory,
                "title": a.get("title", ""),
                "date": a.get("date", ""),
                "has_artifacts": True,
                "artifact_files": [],
            })
            result[cid]["artifact_files"].append(a.get("file", ""))
        for c in data.get("no_artifact_conversations", []):
            cid = c["conversation_id"]
            if cid not in result:
                result[cid] = {
                    "category": category,
                    "subcategory": subcategory,
                    "title": c.get("title", ""),
                    "date": c.get("date", ""),
                    "has_artifacts": False,
                    "artifact_files": [],
                }
    return result


def total_chars(conv_json_path: Path) -> int:
    data = json.loads(conv_json_path.read_text(encoding="utf-8"))
    return sum(m.get("char_count", 0) for m in data.get("messages", []))


def main():
    index = load_index()

    all_convs = []
    for json_path in CONV_DIR.glob("*.json"):
        cid = json_path.stem
        if cid in SKIP_IDS:
            continue
        meta = index.get(cid, {})
        all_convs.append({
            "conversation_id": cid,
            "json_path": str(json_path),
            "category": meta.get("category", "未分類"),
            "subcategory": meta.get("subcategory", ""),
            "title": meta.get("title", ""),
            "date": meta.get("date", ""),
            "has_artifacts": meta.get("has_artifacts", False),
            "artifact_files": meta.get("artifact_files", []),
            "total_chars": total_chars(json_path),
        })

    # artifacts 有り優先、その中で長文順
    all_convs.sort(key=lambda x: (not x["has_artifacts"], -x["total_chars"]))

    total = len(all_convs)
    batch_count = (total + PER_BATCH - 1) // PER_BATCH
    print(f"Total: {total} convs → {batch_count} batches")

    cat_counts = {}
    for x in all_convs:
        cat_counts[x["category"]] = cat_counts.get(x["category"], 0) + 1
    print(f"  by category: {cat_counts}")
    print(f"  with artifacts: {sum(1 for x in all_convs if x['has_artifacts'])}")
    print(f"  without artifacts: {sum(1 for x in all_convs if not x['has_artifacts'])}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ラウンドロビン分配（カテゴリ偏りを抑制）
    batches = [[] for _ in range(batch_count)]
    for i, conv in enumerate(all_convs):
        batches[i % batch_count].append(conv)

    for i, batch in enumerate(batches, start=1):
        (OUT_DIR / f"batch_{i:02d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  batch_{i:02d}.json: {len(batch)} convs")


if __name__ == "__main__":
    main()
