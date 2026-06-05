#!/usr/bin/env python3
"""225件のChatGPT会話から最初の50件を選定し、10件×5バッチに分割する。

選定基準:
  1. artifacts を生成した会話を優先（ナレッジ価値が高い）
  2. 残りは char_count (assistant 含む全文文字数) の長い順
  3. サブカテゴリの偏りを避けるため、上位選定後にラウンドロビン的に並べ替えはせず
     シンプルに「artifacts 有 → 長文順」で 50 件
"""
import json
from pathlib import Path

CONV_DIR = Path("/Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT分析/pipeline/step1_extracted/conversations")
INDEX_ROOT = Path("/Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行")
OUT_DIR = Path("/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件/scripts/batches")

BATCH_COUNT = 5
PER_BATCH = 10


def load_artifact_conv_ids() -> dict[str, dict]:
    """全 conversations_index.json を舐めて、artifacts 付き会話の (id -> meta) を返す。"""
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
    index = load_artifact_conv_ids()

    all_convs = []
    for json_path in CONV_DIR.glob("*.json"):
        cid = json_path.stem
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

    # Sort: artifacts 有り優先、その中で文字数多い順
    all_convs.sort(key=lambda x: (not x["has_artifacts"], -x["total_chars"]))

    selected = all_convs[:BATCH_COUNT * PER_BATCH]
    print(f"Total available: {len(all_convs)}")
    print(f"Selected: {len(selected)}")
    print(f"  with artifacts: {sum(1 for x in selected if x['has_artifacts'])}")
    print(f"  without artifacts: {sum(1 for x in selected if not x['has_artifacts'])}")

    cat_counts = {}
    for x in selected:
        cat_counts[x["category"]] = cat_counts.get(x["category"], 0) + 1
    print(f"  by category: {cat_counts}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # 全選定リスト
    (OUT_DIR / "selected_50.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 10件×5バッチに分割（カテゴリが偏らないようにラウンドロビンで分配）
    batches = [[] for _ in range(BATCH_COUNT)]
    for i, conv in enumerate(selected):
        batches[i % BATCH_COUNT].append(conv)

    for i, batch in enumerate(batches, start=1):
        (OUT_DIR / f"batch_{i}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"batch_{i}.json: {len(batch)} convs")


if __name__ == "__main__":
    main()
