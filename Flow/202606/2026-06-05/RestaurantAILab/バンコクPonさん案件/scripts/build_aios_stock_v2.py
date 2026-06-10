#!/usr/bin/env python3
"""AIOS規約準拠の正しい構造で再構築する。

旧（誤）: ChatGPT履歴_v2/ (Program) → 美容室/ など (Project)
新（正）: 美容室/ (Program) → 過去会話履歴/ (Project)

PONさんは「美容室」「美容専門店」「自社ブランド」「J-Beauty」を既存 Program として
保有している可能性が高いので、Project (過去会話履歴) 単位でコピーできるよう、
各 Project を独立して動かせる構成にする：
- 過去会話履歴/README.md
- 過去会話履歴/ProjectIndex.yaml
- 過去会話履歴/log.md
- 過去会話履歴/_overview/  ← Program別ローカルナレッジ（旧版_overviewを複製）
- 過去会話履歴/{date}_xxx.md (個別サマリー)
- 過去会話履歴/artifacts/

Program レベルにも README.md サンプルを添えるが、PONさん側に既存があれば不要。
"""
import re
import shutil
from pathlib import Path

import yaml

PROJ_ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件")
PER_CONV = PROJ_ROOT / "output/per_conversation"
OLD_OVERVIEW = Path(
    "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/バンコクPonさん案件/"
    "output_2026-04-22/pon-chatgpt-knowledge/ChatGPT履歴/_overview"
)
AIOS_ROOT = PROJ_ROOT / "output/aios_stock_packages"
PROJECT_NAME = "過去会話履歴"
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]
TODAY = "2026-06-05"

PROGRAM_KEYWORDS = {
    "美容室": ["美容室", "サロン", "BELL_otonagami", "Cuus_hair", "Rapi-rabi", "Rio_Hair_Design", "YAMS_hair_cafe", "ベトナム支店"],
    "美容専門店": ["美容専門店", "ネイルサロン", "アイラッシュ", "MONDO_BEAUTY_clinic"],
    "自社ブランド": ["自社ブランド", "商品開発", "DOT", "KINUJO", "ヌリプラ"],
    "J-Beauty": ["J-Beauty", "日本美容", "アカデミー", "イベント", "コスメティクス", "政策_予算", "総合_戦略"],
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


# -------------------------
# Reset
# -------------------------
def reset_root():
    if AIOS_ROOT.exists():
        shutil.rmtree(AIOS_ROOT)
    AIOS_ROOT.mkdir(parents=True)


# -------------------------
# Per-Project build
# -------------------------
def build_project_dir(category: str) -> Path:
    """Returns the project dir: aios_stock_packages/{category}/過去会話履歴/"""
    program_dir = AIOS_ROOT / category
    project_dir = program_dir / PROJECT_NAME
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def copy_summaries_and_artifacts(category: str, project_dir: Path):
    src = PER_CONV / category
    for entry in src.iterdir():
        if entry.is_file() and entry.suffix == ".md":
            shutil.copy2(entry, project_dir / entry.name)
        elif entry.is_dir() and entry.name == "artifacts":
            shutil.copytree(entry, project_dir / "artifacts")


def copy_overview_localized(category: str, project_dir: Path, summaries: list[dict]):
    """旧 _overview をコピー。06_conversations_index.md は Program 内のみで再生成。"""
    dst = project_dir / "_overview"
    shutil.copytree(OLD_OVERVIEW, dst)
    # 旧 06_artifacts_index.md は重いので削除（不要）
    old_art = dst / "06_artifacts_index.md"
    if old_art.exists():
        old_art.unlink()
    # 新規 06_conversations_index.md（このProgramのみ）
    (dst / "06_conversations_index.md").write_text(
        build_conv_index_md(category, summaries), encoding="utf-8"
    )


# -------------------------
# Frontmatter parse
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
    one_liner_match = re.search(r"## ひとことサマリー\n(.+?)(?:\n##|\Z)", text, re.DOTALL)
    if one_liner_match:
        meta["one_liner"] = one_liner_match.group(1).strip().split("\n")[0][:200]
    return meta


def collect_summaries(project_dir: Path) -> list[dict]:
    items = []
    for md in sorted(project_dir.glob("*.md")):
        if md.name in {"README.md"}:
            continue
        meta = parse_summary_meta(md)
        meta["filename"] = md.name
        items.append(meta)
    return items


def collect_artifacts(project_dir: Path) -> list[str]:
    art_dir = project_dir / "artifacts"
    if not art_dir.exists():
        return []
    return sorted(f.name for f in art_dir.iterdir() if f.is_file())


# -------------------------
# Project files
# -------------------------
def build_project_index(category: str, summaries: list[dict], artifacts: list[str]) -> dict:
    files = [
        {"path": "README.md",
         "summary": f"{category} Program > 過去会話履歴 Project の概要・使い方・統計。",
         "keywords": [category, "README", "過去会話履歴"]},
        {"path": "log.md",
         "summary": "プロジェクト変更ログ。",
         "keywords": ["ログ", "変更履歴"]},
        {"path": "_overview/01_PON_persona.md",
         "summary": "PONさんのペルソナ。AIに最初に渡すコンテキスト。",
         "keywords": ["PON", "ペルソナ", "コンテキスト"]},
        {"path": "_overview/02_business_overview.md",
         "summary": "Rios Innovation の事業全体俯瞰（4 Program 横断）。",
         "keywords": ["事業俯瞰", "概要"]},
        {"path": "_overview/03_decisions_log.md",
         "summary": "給与制度・コミッション率・人件費率など過去の決定事項（時系列）。",
         "keywords": ["決定事項", "ログ", "給与", "コミッション"]},
        {"path": "_overview/04_open_ideas.md",
         "summary": "過去に話したが未実行のアイデア集。",
         "keywords": ["未実行アイデア", "ブレスト"]},
        {"path": "_overview/05_people_directory.md",
         "summary": "登場人物・関係者ディレクトリ。",
         "keywords": ["人物", "スタッフ", "関係者"]},
        {"path": "_overview/06_conversations_index.md",
         "summary": f"{category} カテゴリ内の個別会話サマリー {len(summaries)}件 の索引。日付昇順。",
         "keywords": [category, "会話索引"]},
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
        clean = art_name
        for ext in (".md", ".pdf", ".docx"):
            if clean.endswith(ext):
                clean = clean[: -len(ext)]
                break
        files.append({
            "path": f"artifacts/{art_name}",
            "summary": f"会話から生成された成果物: {art_name}",
            "keywords": [category, "artifact", clean],
        })

    return {
        "version": 1,
        "project": PROJECT_NAME,
        "root": f"Stock/{category}/{PROJECT_NAME}",
        "canonical": {"readme": "README.md", "log": "log.md"},
        "files": files,
    }


def build_project_readme(category: str, summaries: list[dict], artifacts: list[str]) -> str:
    subcat_counts: dict[str, int] = {}
    for s in summaries:
        sc = s.get("subcategory", "") or "(未分類)"
        subcat_counts[sc] = subcat_counts.get(sc, 0) + 1
    subcat_lines = "\n".join(f"- **{sc}**: {n}件" for sc, n in sorted(subcat_counts.items(), key=lambda x: -x[1]))

    return f"""# 過去会話履歴

## このProjectについて

PONさん（近藤Pon / Rios Innovation Co., Ltd.）が過去に **ChatGPT** で行ってきた会話のうち、{category} に関連する分を **1会話 = 1サマリー** の粒度で整理した個別ナレッジ集です。

各サマリーには以下が含まれます：
- frontmatter（conversation_id / date / subcategory / artifact_files など）
- ひとことサマリー
- 論点と結論（主語述語が明確な完全文）
- 決定事項・アクション
- 言及された人物・店舗・商品
- 関連 artifacts へのリンク（同階層 `artifacts/`）
- 重要な引用（原文）

## このフォルダの中身

| 項目 | 件数 |
|---|---:|
| 個別会話サマリー (.md) | {len(summaries)} |
| 関連 artifacts (`artifacts/`) | {len(artifacts)} |

### サブカテゴリ内訳

{subcat_lines}

## 使い方（Cursor + AIOS）

### 1. 最初に読むべきファイル

新しい AI セッションを始めるときは、まず以下を会話の冒頭で参照させてください：

- `_overview/01_PON_persona.md` — PONさん全体のビジネスコンテキスト
- このProjectの `README.md`（本ファイル）

これで AI は PONさんが {category} で過去に検討してきた論点を踏まえた回答ができます。

### 2. テーマで探す

- 横断テーマ → `_overview/themes/{{テーマ}}.md`（給与・プロモ・商品・人事・競合・海外・経営指標）
- 過去の決定事項 → `_overview/03_decisions_log.md`
- 未実行アイデア → `_overview/04_open_ideas.md`
- 個別会話索引 → `_overview/06_conversations_index.md`（{len(summaries)}件、日付昇順）

### 3. 個別の論点を深掘り

- `{{date}}_{{slug}}_{{convId8}}.md` のファイル名から該当会話を開く
- frontmatter の `artifact_files` から関連成果物に飛ぶ
- 本文中のリンクから `artifacts/...` を直接開く

### 4. 人物・店舗で検索

- `grep -r "RISA" .` 等で名前を横断検索
- 該当する個別サマリー → frontmatter の subcategory・日付で時系列把握

## 参照のヒント

- サマリーの**論点と結論**は完全な文章で書かれているので、grep の対象になりやすいです
- artifact ファイル名は元会話で AI が生成した実体（提案書・スクリプト・メール文案・分析レポート）

## 関連

- 横断ナレッジ: `_overview/`
- 変更履歴: `log.md`
- 全体カタログ: `Stock/MasterIndex.yaml`
"""


def build_project_log_md(category: str, n_summaries: int, n_artifacts: int) -> str:
    return f"""# log（{category} > 過去会話履歴）

## 目的
- このProjectの変更履歴を記録する。

## 変更履歴

| 日付 | 種別 | ファイル | 変更内容 | 変更理由 |
|---|---|---|---|---|
| {TODAY} | create | `README.md` / `ProjectIndex.yaml` / `log.md` | AIOS Project形式で新規作成 | 過去会話履歴のナレッジ化 |
| {TODAY} | create | `_overview/*` | 旧版 (output_2026-04-22 / ChatGPT履歴) から共通ナレッジを複製 | Project単独で完結させるため |
| {TODAY} | create | 個別会話サマリー {n_summaries}件 | per_conversation/{category}/ から | BL-0087: 1会話=1サマリー粒度のナレッジ化 |
| {TODAY} | create | `artifacts/*` ({n_artifacts}件) | 旧版から流用 | 関連成果物の同階層配置 |
"""


# -------------------------
# Conversations index (per-Program)
# -------------------------
def build_conv_index_md(category: str, summaries: list[dict]) -> str:
    body = [
        f"# 個別会話索引（{category}）",
        "",
        f"このProgramに分類された **{len(summaries)}件** の個別会話サマリーを、日付昇順で索引化したものです。",
        "目的の論点・店舗・人物名で grep して、該当ファイルを開いてください。",
        "",
        "| 日付 | サブカテゴリ | タイトル | ファイル |",
        "|---|---|---|---|",
    ]
    for s in sorted(summaries, key=lambda x: x.get("date", "")):
        date = s.get("date", "")
        subcat = s.get("subcategory", "")
        title = (s.get("title", "") or "").replace("|", " ")
        fn = s["filename"]
        body.append(f"| {date} | {subcat} | {title} | [`{fn}`](../{fn}) |")
    return "\n".join(body)


# -------------------------
# Program README (sample / fallback)
# -------------------------
def build_program_readme(category: str) -> str:
    return f"""# {category}（Program）

> このファイルは **Program README サンプル** です。
> PONさん側 Stock に既に `{category}` Program の README.md がある場合は、そちらを優先してください。
> 既存がない場合のみ、このサンプルを参考に追加してください。

## 背景・目的

{category} に関する PONさん側の Program です。Rios Innovation Co., Ltd. が展開する {category} 事業全体のナレッジを保持します。

## このProgramに含まれるProject

| Project | 概要 |
|---|---|
| `過去会話履歴/` | PONさんが過去にChatGPTで行った会話を、1会話=1サマリー粒度で整理したナレッジ集 |

（PONさん側に既存の Project があれば、ここに追記してください）

## 関係者

- 近藤Pon（Rios Innovation 社長）
- 田中利空（開発・AI 担当）
- 町田大地（AI 担当）

## 関連

- Master Index: `Stock/MasterIndex.yaml`
"""


# -------------------------
# MasterIndex_snippet.yaml (全 Program 共通)
# -------------------------
def build_master_index_snippet(totals: dict[str, dict]) -> dict:
    snippet = {}
    for cat in CATEGORIES:
        snippet[cat] = {
            "summary": f"{cat} Program。Rios Innovation の {cat} 事業に関するナレッジを保持。",
            "keywords": PROGRAM_KEYWORDS.get(cat, [cat]),
            "projects": {
                PROJECT_NAME: {
                    "summary": (
                        f"{cat} に関する PONさんの ChatGPT 過去会話を、"
                        f"1会話=1サマリー粒度（{totals[cat]['summaries']}件 + artifacts {totals[cat]['artifacts']}件）で整理した個別ナレッジ集。"
                    ),
                    "keywords": PROGRAM_KEYWORDS.get(cat, [cat]) + ["過去会話履歴", "ChatGPT", "個別サマリー"],
                    "path": f"Stock/{cat}/{PROJECT_NAME}",
                    "readme": "README.md",
                    "index": "ProjectIndex.yaml",
                }
            },
        }
    return snippet


# -------------------------
# Top-level setup README
# -------------------------
def build_setup_readme(totals: dict[str, dict]) -> str:
    sum_total = sum(v["summaries"] for v in totals.values())
    art_total = sum(v["artifacts"] for v in totals.values())
    rows = "\n".join(
        f"| {cat} | {v['summaries']} | {v['artifacts']} |" for cat, v in totals.items()
    )
    return f"""# AIOS Stock パッケージ（PONさん納品用）

PONさんの ChatGPT 過去会話を、AIOS Stock 規約に沿って **4 Program × 1 Project (過去会話履歴)** で整理した納品物です。

## 統計

| Program | 個別サマリー | artifacts |
|---|---:|---:|
{rows}
| **合計** | **{sum_total}** | **{art_total}** |

## ディレクトリ構造

```
aios_stock_packages/                  ← この納品物の最上位
├── README.md                          ← このファイル
├── MasterIndex_snippet.yaml           ← PONさん側 Stock/MasterIndex.yaml への追記分
├── 美容室/                            ← Program
│   ├── README.md                       (Program README サンプル)
│   └── 過去会話履歴/                  ← Project（これを Stock/美容室/ にコピー）
│       ├── README.md
│       ├── ProjectIndex.yaml
│       ├── log.md
│       ├── _overview/                 ← Program別ローカルナレッジ
│       ├── {{date}}_xxx.md            (141件)
│       └── artifacts/                 (230件)
├── 美容専門店/
├── 自社ブランド/
└── J-Beauty/
```

## PONさん側でのセットアップ（3ステップ）

### Step 1: Project単位でコピー

各 Program 配下の `過去会話履歴/` ディレクトリをそのまま、PONさん側 Stock の該当 Program に配置します。

```bash
# PONさんのAIOSリポジトリのルートで実行
cp -r 美容室/過去会話履歴      ~/path/to/your-aios/Stock/美容室/
cp -r 美容専門店/過去会話履歴  ~/path/to/your-aios/Stock/美容専門店/
cp -r 自社ブランド/過去会話履歴 ~/path/to/your-aios/Stock/自社ブランド/
cp -r J-Beauty/過去会話履歴    ~/path/to/your-aios/Stock/J-Beauty/
```

PONさん側に **Program ディレクトリが存在しない**場合は、先に Program 直下に README.md を作成してください（本パッケージの `{{Program}}/README.md` がサンプルです）。

### Step 2: MasterIndex.yaml に追記

`MasterIndex_snippet.yaml` の内容を、自分の `Stock/MasterIndex.yaml` の対応する Program エントリに追記してください。具体的には、各 Program の `projects:` セクションに `過去会話履歴:` を追加します。

### Step 3: Cursorで使う

新しいチャットを開き、冒頭で以下のように参照します：

> 「Stock/美容室/過去会話履歴/_overview/01_PON_persona.md を読んで、私が誰か理解してください。
> その上で、ラピラピのワタルさん向け給与体系の核心を、過去の整理を踏まえて教えてください。」

AI は `Stock/美容室/過去会話履歴/2026-03-19_美容室再建の給与設計_*.md` を参照し、`artifacts/` 内の最終オファー文まで辿れます。

## AIOS規約への準拠

- ✅ `Stock/<Program>/<Project>/` 階層
- ✅ Program 直下: `README.md`
- ✅ Project 直下: `README.md` / `ProjectIndex.yaml` / `log.md`
- ✅ `ProjectIndex.yaml` に全ファイルを `files` 列挙
- ✅ `MasterIndex_snippet.yaml` で PON 側へマージ可能

## 注意

- スタッフ氏名・給与額・取引先など機微情報を含みます。**privateリポジトリで運用してください**。
- 旧版 `pon-chatgpt-knowledge` (2026-04-22 / `Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/`) と並存可能です。本パッケージはより詳細なサマリー粒度を提供します。
"""


# -------------------------
# Main
# -------------------------
def main():
    print(f"=== Reset {AIOS_ROOT} ===")
    reset_root()

    totals: dict[str, dict] = {}

    for cat in CATEGORIES:
        print(f"\n--- {cat} ---")
        project_dir = build_project_dir(cat)

        # Program README サンプル
        program_readme = AIOS_ROOT / cat / "README.md"
        program_readme.write_text(build_program_readme(cat), encoding="utf-8")

        # サマリーとartifactsコピー
        copy_summaries_and_artifacts(cat, project_dir)
        summaries = collect_summaries(project_dir)
        artifacts = collect_artifacts(project_dir)
        totals[cat] = {"summaries": len(summaries), "artifacts": len(artifacts)}

        # _overview コピー + Program別 conv_index 生成
        copy_overview_localized(cat, project_dir, summaries)

        # ProjectIndex.yaml
        idx = build_project_index(cat, summaries, artifacts)
        (project_dir / "ProjectIndex.yaml").write_text(
            yaml.safe_dump(idx, allow_unicode=True, sort_keys=False, width=200),
            encoding="utf-8",
        )
        # log.md
        (project_dir / "log.md").write_text(
            build_project_log_md(cat, len(summaries), len(artifacts)), encoding="utf-8"
        )
        # Project README
        (project_dir / "README.md").write_text(
            build_project_readme(cat, summaries, artifacts), encoding="utf-8"
        )

        print(f"  Program {cat}/Project {PROJECT_NAME}: summaries={len(summaries)} artifacts={len(artifacts)}")

    # Top-level setup README + MasterIndex_snippet
    (AIOS_ROOT / "README.md").write_text(build_setup_readme(totals), encoding="utf-8")
    (AIOS_ROOT / "MasterIndex_snippet.yaml").write_text(
        "# MasterIndex_snippet.yaml\n"
        "# PONさんの Stock/MasterIndex.yaml の対応する Program エントリに、各 projects.過去会話履歴 を追記してください。\n"
        "# 既に同名の Program がある場合は、その projects: セクションに 過去会話履歴: の枝だけ追加でOKです。\n\n"
        + yaml.safe_dump(build_master_index_snippet(totals), allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )

    print(f"\n=== Done ===")
    print(f"Output: {AIOS_ROOT}")
    for cat, v in totals.items():
        print(f"  {cat}/{PROJECT_NAME}: {v['summaries']} summaries, {v['artifacts']} artifacts")


if __name__ == "__main__":
    main()
