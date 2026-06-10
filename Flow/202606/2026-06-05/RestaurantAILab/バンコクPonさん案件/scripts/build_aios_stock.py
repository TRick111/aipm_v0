#!/usr/bin/env python3
"""個別会話サマリー（226件）+ artifacts（439件）を AIOS Stock 互換構造に整形する。

出力: Flow/.../output/aios_stock/ChatGPT履歴_v2/

PONさん側の Stock に drop-in 可能な単独 Program として完結させる。
旧版 (output_2026-04-22 / pon-chatgpt-knowledge) と並存できるよう「_v2」で区別。

構成:
  ChatGPT履歴_v2/
    README.md                      ← Program README
    MasterIndex_snippet.yaml       ← PONさん側 MasterIndex に追記する分
    _overview/                     ← 旧版から流用 + 新規 conversations_index.md
    {category}/                    ← 4 Projects
      README.md
      ProjectIndex.yaml
      log.md
      {date}_{slug}_{convId8}.md   ← サマリー
      artifacts/
"""
import re
import shutil
from datetime import datetime
from pathlib import Path

import yaml

PROJ_ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件")
PER_CONV = PROJ_ROOT / "output/per_conversation"
OLD_OVERVIEW = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/バンコクPonさん案件/"
    "output_2026-04-22/pon-chatgpt-knowledge/ChatGPT履歴/_overview"
)
AIOS_ROOT = PROJ_ROOT / "output/aios_stock/ChatGPT履歴_v2"
PROGRAM_NAME = "ChatGPT履歴_v2"
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]
TODAY = "2026-06-05"

CATEGORY_KEYWORDS = {
    "美容室": ["美容室", "サロン", "BELL_otonagami", "Cuus_hair", "Rapi-rabi", "Rio_Hair_Design", "YAMS_hair_cafe", "ベトナム支店"],
    "美容専門店": ["美容専門店", "ネイルサロン", "アイラッシュ", "MONDO_BEAUTY_clinic"],
    "自社ブランド": ["自社ブランド", "商品開発", "DOT", "KINUJO", "ヌリプラ"],
    "J-Beauty": ["J-Beauty", "日本美容", "アカデミー", "イベント", "コスメティクス", "政策_予算", "総合_戦略"],
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


# -------------------------
# 1. ディレクトリリセット & コピー
# -------------------------
def reset_root():
    if AIOS_ROOT.exists():
        shutil.rmtree(AIOS_ROOT)
    AIOS_ROOT.mkdir(parents=True)


def copy_overview():
    """旧版の _overview をコピー（06_artifacts_index.md は新版で置き換えるので除外しない）。"""
    dst = AIOS_ROOT / "_overview"
    shutil.copytree(OLD_OVERVIEW, dst)


def copy_category(cat: str):
    src = PER_CONV / cat
    dst = AIOS_ROOT / cat
    shutil.copytree(src, dst)


# -------------------------
# 2. サマリーmd メタ取得
# -------------------------
def parse_summary_meta(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    # ひとことサマリーを抽出（## ひとことサマリー の次の段落）
    one_liner_match = re.search(r"## ひとことサマリー\n(.+?)(?:\n##|\Z)", text, re.DOTALL)
    if one_liner_match:
        meta["one_liner"] = one_liner_match.group(1).strip().split("\n")[0][:200]
    return meta


def collect_summaries(category: str) -> list[dict]:
    items = []
    cat_dir = AIOS_ROOT / category
    for md in sorted(cat_dir.glob("*.md")):
        if md.name == "README.md":
            continue
        meta = parse_summary_meta(md)
        meta["filename"] = md.name
        items.append(meta)
    return items


def collect_artifacts(category: str) -> list[str]:
    art_dir = AIOS_ROOT / category / "artifacts"
    return sorted(f.name for f in art_dir.iterdir() if f.is_file())


# -------------------------
# 3. ProjectIndex.yaml
# -------------------------
def build_project_index(category: str, summaries: list[dict], artifacts: list[str]):
    files = [
        {"path": "README.md",
         "summary": f"{category} カテゴリのProject概要。会話サマリー件数・artifacts件数・参照のヒント。",
         "keywords": [category, "README"]},
        {"path": "log.md",
         "summary": "プロジェクト変更ログ（ファイルの作成/編集履歴）",
         "keywords": ["ログ", "変更履歴"]},
    ]
    for s in summaries:
        files.append({
            "path": s["filename"],
            "summary": s.get("one_liner") or s.get("title", ""),
            "keywords": [
                category,
                s.get("subcategory", ""),
                s.get("title", ""),
                s.get("date", ""),
            ],
        })
    for art_name in artifacts:
        files.append({
            "path": f"artifacts/{art_name}",
            "summary": f"会話から生成された成果物: {art_name}",
            "keywords": [category, "artifact", art_name.removesuffix(".md").removesuffix(".pdf").removesuffix(".docx")],
        })

    index = {
        "version": 1,
        "project": category,
        "root": f"Stock/{PROGRAM_NAME}/{category}",
        "canonical": {"readme": "README.md", "log": "log.md"},
        "files": files,
    }
    return index


# -------------------------
# 4. Project README
# -------------------------
def build_project_readme(category: str, summaries: list[dict], artifacts: list[str]) -> str:
    subcat_counts: dict[str, int] = {}
    for s in summaries:
        sc = s.get("subcategory", "") or "(未分類)"
        subcat_counts[sc] = subcat_counts.get(sc, 0) + 1
    subcat_lines = "\n".join(f"- **{sc}**: {n}件" for sc, n in sorted(subcat_counts.items(), key=lambda x: -x[1]))

    sample_titles = "\n".join(
        f"- `{s['filename']}` — {s.get('title', '')}"
        for s in summaries[:5]
    )

    return f"""# {category}

## このProjectについて

PONさんのChatGPT過去会話のうち、**{category}** カテゴリに分類された会話を個別サマリー化したものです。
各 `.md` は1会話 = 1サマリーで、論点・結論・決定事項・登場人物・関連 artifacts・重要引用を含みます。

## このフォルダの中身

| 項目 | 件数 |
|---|---:|
| 個別会話サマリー (.md) | {len(summaries)} |
| 関連 artifacts (`artifacts/`) | {len(artifacts)} |

### サブカテゴリ内訳

{subcat_lines}

### サマリーファイル例（先頭5件）

{sample_titles}

## 使い方

### 個別サマリーを直接読む
ファイル名 `{{date}}_{{slug}}_{{convId8}}.md` のうち、知りたい論点を含むものを開いてください。frontmatter（YAML）に conversation_id・category・subcategory・artifact_files が入っており、関連 artifacts は本文中の相対パス `artifacts/...` から辿れます。

### Project全体の傾向を掴む
- `../_overview/themes/` のテーマ別ナレッジから入る
- `../_overview/03_decisions_log.md` で過去の決定事項を確認
- このフォルダ内で `grep` などで人物名・店舗名・商品名を横断検索

## 参照のヒント

- 個別サマリーの**論点と結論**は主語述語が明確な文章で書かれているため、grep の対象になりやすいです
- artifact ファイルは元の会話で AI が生成した成果物（提案書・スクリプト・メール文案等）の実体です。サマリーで概要を掴んだあと、必要に応じて参照してください

## 関連

- Program README: `../README.md`
- 横断ナレッジ: `../_overview/`
- 変更履歴: `log.md`
"""


# -------------------------
# 5. Project log.md
# -------------------------
def build_project_log_md(category: str, n_summaries: int, n_artifacts: int) -> str:
    return f"""# log（{category}）

## 目的
- このProjectの変更履歴を記録する。

## 変更履歴

| 日付 | 種別 | ファイル | 変更内容 | 変更理由 |
|---|---|---|---|---|
| {TODAY} | create | `README.md` / `ProjectIndex.yaml` / `log.md` | AIOS Project形式で新規作成 | ChatGPT履歴_v2 の整備 |
| {TODAY} | create | 個別会話サマリー {n_summaries}件 | per_conversation/ から流用 | BL-0087: 個別会話粒度のナレッジ化 |
| {TODAY} | create | `artifacts/*` ({n_artifacts}件) | 旧版 (output_2026-04-22) から流用 | 同上 |
"""


# -------------------------
# 6. Program README
# -------------------------
def build_program_readme(totals: dict[str, dict]) -> str:
    sum_total = sum(v["summaries"] for v in totals.values())
    art_total = sum(v["artifacts"] for v in totals.values())
    cat_table = "\n".join(
        f"| {cat} | {v['summaries']} | {v['artifacts']} |"
        for cat, v in totals.items()
    )

    return f"""# {PROGRAM_NAME}

## このProgramについて

PONさん（近藤Pon / Rios Innovation Co., Ltd.）の過去のChatGPT会話履歴を、**1会話=1サマリー**の粒度で AIOS ナレッジに統合したナレッジベースです。

旧版 (`ChatGPT履歴` / 2026-04-22 生成) はサブカテゴリ単位の総体サマリーでしたが、本v2では：

- 個別会話単位のサマリー **{sum_total}件**（論点・結論・決定事項・関連artifacts・重要引用）
- 関連 artifacts **{art_total}件** を同階層に同梱

これにより、特定の決定がどの会話で生まれたかを会話レベルで辿れます。

## ディレクトリ構造

```
{PROGRAM_NAME}/
├── README.md                     ← このファイル
├── MasterIndex_snippet.yaml      ← PONさんの Stock/MasterIndex.yaml に追記する分
├── _overview/                    ← Program横断ナレッジ（最初に読む）
│   ├── 00_README.md
│   ├── 01_PON_persona.md         ← AIに最初に渡すペルソナ
│   ├── 02_business_overview.md   ← 事業全体像
│   ├── 03_decisions_log.md       ← 決定事項の時系列ログ
│   ├── 04_open_ideas.md          ← 未実行アイデア集
│   ├── 05_people_directory.md    ← 登場人物・関係者
│   ├── 06_artifacts_index.md     ← (旧)成果物目次
│   ├── 06_conversations_index.md ← (新) 226件の個別会話索引
│   └── themes/                   ← テーマ別ナレッジ7本
├── 美容室/                       ← Project
├── 美容専門店/                   ← Project
├── 自社ブランド/                 ← Project
└── J-Beauty/                     ← Project
```

各 Project 直下に：
- `README.md` / `ProjectIndex.yaml` / `log.md`（AIOS規約）
- 個別会話サマリー (`{{date}}_{{slug}}_{{convId8}}.md`)
- `artifacts/` ディレクトリ

## 統計

| Project | 個別サマリー | artifacts |
|---|---:|---:|
{cat_table}
| **合計** | **{sum_total}** | **{art_total}** |

## PONさん側でのセットアップ（3ステップ）

### Step 1. Stockに配置

```bash
# PONさんのAIOSリポジトリのルートで
cp -r {PROGRAM_NAME} ~/path/to/your-aios/Stock/
```

### Step 2. MasterIndex.yaml に追記

`MasterIndex_snippet.yaml` の内容を、自分の `Stock/MasterIndex.yaml` の Programs セクションに追記してください。

### Step 3. 使ってみる

Cursorで新しいチャットを開き、以下のように冒頭で参照する：

> 「Stock/{PROGRAM_NAME}/_overview/01_PON_persona.md を読んで、私が誰か理解してください。
> その上で、ラピラピのワタルさん向け給与体系の核心を、過去の整理を踏まえて教えてください。」

AI が `美容室/2026-03-19_美容室再建の給与設計_*.md` を参照し、artifacts まで辿れます。

## 旧版との関係

| 観点 | 旧版 (`ChatGPT履歴`) | 新版 (`{PROGRAM_NAME}`) |
|---|---|---|
| Project数 | 21（subcategory単位） | 4（category単位） |
| 会話サマリー粒度 | サブカテゴリ単位の総体 | **1会話=1サマリー** |
| サマリー件数 | 21 | **{sum_total}** |
| artifacts | 同梱 | 同梱（フラット配置） |
| 並存 | — | 旧と独立、両方Stockに置ける |

両方Stockに置いた場合、PONさんは状況に応じて使い分けできます：
- 大まかなテーマで掴みたい → 旧版
- 「あの決定はどの会話で？」→ 新版

## 秘密情報について

スタッフ氏名・給与額・取引先など機微情報を含みます。**privateリポジトリで運用してください**。

## 生成元

- PONさんのChatGPT会話履歴 export (2026-03-23 取得 / 654会話)
- うち4カテゴリに該当する225会話を1会話=1サマリーで整形（{TODAY} 生成）
- 田中利空 + Claude Code（Master + Sub-agent並列）

## ライセンス

Rios Innovation Co., Ltd. 内部ナレッジベース。無断で外部共有しないでください。
"""


# -------------------------
# 7. MasterIndex_snippet.yaml
# -------------------------
def build_master_index_snippet(totals: dict[str, dict]) -> dict:
    return {
        PROGRAM_NAME: {
            "summary": (
                "PONさんの過去ChatGPT会話履歴を1会話=1サマリー粒度で整理したナレッジベース（v2）。"
                "旧 ChatGPT履歴 と並存可。個別会話の論点・決定事項・関連artifactsを辿れる。"
            ),
            "keywords": [
                "ChatGPT", "過去会話", "ナレッジベース", "PON", "Rios Innovation",
                "美容室", "美容専門店", "自社ブランド", "J-Beauty",
                "給与制度", "プロモーション", "商品開発", "海外展開",
                "1会話1サマリー", "詳細サマリー", "v2",
            ],
            "projects": {
                cat: {
                    "summary": f"{cat} カテゴリの個別会話サマリー {v['summaries']}件 + 関連artifacts {v['artifacts']}件。",
                    "keywords": CATEGORY_KEYWORDS.get(cat, [cat]),
                    "path": f"Stock/{PROGRAM_NAME}/{cat}",
                    "readme": "README.md",
                    "index": "ProjectIndex.yaml",
                }
                for cat, v in totals.items()
            },
        }
    }


# -------------------------
# 8. _overview/06_conversations_index.md
# -------------------------
def build_conversations_index_md(all_summaries: dict[str, list[dict]]) -> str:
    body = [
        "# 個別会話索引（226件）",
        "",
        "Programを横断して、全ての個別会話サマリーを **カテゴリ → 日付昇順** で索引化したものです。",
        "目的の論点・店舗・人物名で grep して、該当ファイルを開いてください。",
        "",
    ]
    total = 0
    for cat in CATEGORIES:
        items = all_summaries[cat]
        items_sorted = sorted(items, key=lambda x: x.get("date", ""))
        total += len(items_sorted)
        body.append(f"## {cat} ({len(items_sorted)}件)")
        body.append("")
        body.append("| 日付 | サブカテゴリ | タイトル | ファイル |")
        body.append("|---|---|---|---|")
        for s in items_sorted:
            date = s.get("date", "")
            subcat = s.get("subcategory", "")
            title = (s.get("title", "") or "").replace("|", " ")
            fn = s["filename"]
            body.append(f"| {date} | {subcat} | {title} | [`{fn}`](../{cat}/{fn}) |")
        body.append("")
    body.insert(1, f"\n合計 **{total}件**")
    return "\n".join(body)


# -------------------------
# 9. main
# -------------------------
def main():
    print(f"=== Step 1: Reset {AIOS_ROOT} ===")
    reset_root()

    print("=== Step 2: Copy _overview from old version ===")
    copy_overview()

    print("=== Step 3: Copy per_conversation/{category}/ to each Project ===")
    for cat in CATEGORIES:
        copy_category(cat)
        print(f"  {cat}")

    totals: dict[str, dict] = {}
    all_summaries: dict[str, list[dict]] = {}

    print("=== Step 4: Build per-Project metafiles ===")
    for cat in CATEGORIES:
        summaries = collect_summaries(cat)
        artifacts = collect_artifacts(cat)
        all_summaries[cat] = summaries
        totals[cat] = {"summaries": len(summaries), "artifacts": len(artifacts)}

        # README.md
        readme = build_project_readme(cat, summaries, artifacts)
        (AIOS_ROOT / cat / "README.md").write_text(readme, encoding="utf-8")

        # ProjectIndex.yaml
        idx = build_project_index(cat, summaries, artifacts)
        (AIOS_ROOT / cat / "ProjectIndex.yaml").write_text(
            yaml.safe_dump(idx, allow_unicode=True, sort_keys=False, width=200),
            encoding="utf-8",
        )

        # log.md
        log = build_project_log_md(cat, len(summaries), len(artifacts))
        (AIOS_ROOT / cat / "log.md").write_text(log, encoding="utf-8")

        print(f"  {cat}: summaries={len(summaries)} artifacts={len(artifacts)}")

    print("=== Step 5: Program README + MasterIndex_snippet ===")
    (AIOS_ROOT / "README.md").write_text(build_program_readme(totals), encoding="utf-8")
    (AIOS_ROOT / "MasterIndex_snippet.yaml").write_text(
        "# MasterIndex_snippet.yaml\n"
        "# PONさんのAIOS Stock/MasterIndex.yaml の Programs セクションに、以下を追記してください。\n\n"
        + yaml.safe_dump(build_master_index_snippet(totals), allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )

    print("=== Step 6: _overview/06_conversations_index.md (新規) ===")
    (AIOS_ROOT / "_overview" / "06_conversations_index.md").write_text(
        build_conversations_index_md(all_summaries), encoding="utf-8"
    )

    print("\n=== Done ===")
    print(f"Output: {AIOS_ROOT}")
    for cat, v in totals.items():
        print(f"  {cat}: {v['summaries']} summaries, {v['artifacts']} artifacts")
    grand_summary = sum(v["summaries"] for v in totals.values())
    grand_art = sum(v["artifacts"] for v in totals.values())
    print(f"  TOTAL: {grand_summary} summaries + {grand_art} artifacts")


if __name__ == "__main__":
    main()
