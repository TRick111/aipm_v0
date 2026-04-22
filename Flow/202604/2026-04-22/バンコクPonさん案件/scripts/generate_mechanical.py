#!/usr/bin/env python3
"""機械生成ファイルを作成する（LLMを使わず、既存データを集約）。

出力:
- ChatGPT履歴/_overview/00_README.md
- ChatGPT履歴/_overview/05_people_directory.md
- ChatGPT履歴/_overview/06_artifacts_index.md
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202604/2026-04-22/バンコクPonさん案件/output/pon-chatgpt-knowledge/ChatGPT履歴")
OVERVIEW = ROOT / "_overview"
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]


def collect_all_subcategory_dirs():
    result = []
    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        for subcat_dir in sorted(cat_dir.iterdir()):
            if subcat_dir.is_dir() and subcat_dir.name != "_overview":
                result.append((cat, subcat_dir.name, subcat_dir))
    return result


def extract_people_from_summary(md_path: Path) -> list[tuple[str, str]]:
    """conversations_summary.md の『登場人物・関係者』表を抽出する。"""
    if not md_path.exists():
        return []
    content = md_path.read_text(encoding="utf-8")
    # 見出し「登場人物・関係者」から次の見出しまでを取得
    m = re.search(r"##\s*登場人物.*?\n(.*?)(?=\n##\s|\Z)", content, re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    people = []
    for line in block.split("\n"):
        line = line.strip()
        if not line or line.startswith("|---") or line.startswith("| 名前") or line.startswith("|名前"):
            continue
        if line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                name, role = parts[0], parts[1]
                if name and role and name != "名前":
                    people.append((name, role))
    return people


def build_people_directory():
    print("Building 05_people_directory.md...")
    # name -> [(role, source_category, source_subcategory), ...]
    registry = defaultdict(list)
    for cat, subcat, subcat_dir in collect_all_subcategory_dirs():
        people = extract_people_from_summary(subcat_dir / "conversations_summary.md")
        for name, role in people:
            registry[name].append((role, cat, subcat))

    lines = [
        "# 登場人物・関係者ディレクトリ",
        "",
        "## このファイルについて",
        "",
        "PONさんの過去ChatGPT会話に登場するスタッフ・取引先・相談相手の一覧です。",
        "各サブカテゴリの `conversations_summary.md` の「登場人物・関係者」表から自動集約しています。",
        "",
        "AIに「Xさん」と言われても文脈が分かるよう、会話開始時に参照してください。",
        "",
        f"## 登場人物サマリ（{len(registry)}名）",
        "",
        "| 名前 | 役割 | 登場するプロジェクト |",
        "|---|---|---|",
    ]
    for name in sorted(registry.keys()):
        entries = registry[name]
        roles = list({e[0] for e in entries})
        locs = sorted({f"{cat}/{subcat}" for _, cat, subcat in entries})
        role_str = " / ".join(roles)
        loc_str = ", ".join(locs)
        lines.append(f"| {name} | {role_str} | {loc_str} |")

    lines += [
        "",
        "## プロジェクト別登場人物",
        "",
    ]
    by_loc = defaultdict(list)
    for name, entries in registry.items():
        for role, cat, subcat in entries:
            by_loc[(cat, subcat)].append((name, role))
    for (cat, subcat), members in sorted(by_loc.items()):
        lines.append(f"### {cat} > {subcat}")
        for name, role in members:
            lines.append(f"- **{name}** — {role}")
        lines.append("")

    lines += [
        "## 使い方",
        "",
        "- 会話冒頭で `01_PON_persona.md` と合わせてこのファイルを参照すると、",
        "  AIは「誰」に言及しているか文脈を保った応答ができます。",
        "- 新しい関係者が出てきたら、対応するサブカテゴリの `conversations_summary.md` に追記してください。",
    ]
    (OVERVIEW / "05_people_directory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def extract_artifact_meta(subcat_dir: Path) -> list[dict]:
    """conversations_index.json から artifacts 情報を抽出する。"""
    idx_file = subcat_dir / "conversations_index.json"
    if not idx_file.exists():
        return []
    data = json.loads(idx_file.read_text(encoding="utf-8"))
    return data.get("artifacts", [])


def build_artifacts_index():
    print("Building 06_artifacts_index.md...")
    lines = [
        "# 成果物（artifacts）目次",
        "",
        "## このファイルについて",
        "",
        "PONさんのChatGPT会話から抽出された **成果物ファイル439件** の全カタログです。",
        "成果物 = PONさんとChatGPTのやり取りで生成されたレポート・提案書・計算・ガイド等の最終出力物。",
        "",
        "テーマごとの俯瞰は `_overview/themes/*.md` を、個別の詳細は各サブカテゴリの README.md を参照してください。",
        "",
    ]

    total = 0
    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        cat_lines = [f"## {cat}", ""]
        cat_total = 0
        for subcat_dir in sorted(cat_dir.iterdir()):
            if not subcat_dir.is_dir():
                continue
            artifacts = extract_artifact_meta(subcat_dir)
            if not artifacts:
                continue
            cat_lines.append(f"### {subcat_dir.name}（{len(artifacts)}件）")
            cat_lines.append("")
            cat_lines.append("| ファイル | 説明 | タイプ |")
            cat_lines.append("|---|---|---|")
            for a in artifacts:
                fname = a.get("file", "")
                desc = a.get("description", "").replace("|", "／")
                typ = a.get("type", "")
                relpath = f"{cat}/{subcat_dir.name}/artifacts/{fname}"
                cat_lines.append(f"| [{fname}]({relpath}) | {desc} | {typ} |")
            cat_lines.append("")
            cat_total += len(artifacts)
        cat_lines[0] = f"## {cat}（{cat_total}件）"
        lines.extend(cat_lines)
        total += cat_total

    lines.append(f"## 合計: {total}件")
    lines.append("")
    lines.append("## 使い方")
    lines.append("")
    lines.append("- ファイル名でGrep: `grep -r 'キーワード' .` で特定成果物を見つけられます")
    lines.append("- 最もアクセス頻度が高いもの: 給与シミュレーション系・提案書系・戦略分析系")
    lines.append("- 過去の数値を参照したい場合: ファイル内に具体値が残っています")
    (OVERVIEW / "06_artifacts_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  artifacts 合計: {total}件")


def build_overview_readme():
    print("Building 00_README.md (overview)...")
    lines = [
        "# _overview/ — Program横断ナレッジ",
        "",
        "## このディレクトリについて",
        "",
        "`ChatGPT履歴/` プログラム全体を俯瞰するためのファイル群です。",
        "個別プロジェクト（美容室/美容専門店/自社ブランド/J-Beauty）を深掘りする前に、",
        "まずここを読むとPONさんの全体像・思考傾向・過去の決定事項が把握できます。",
        "",
        "## ファイル一覧と使い分け",
        "",
        "| ファイル | 用途 | 最初に読むべきか |",
        "|---|---|:---:|",
        "| `01_PON_persona.md` | PONさんは誰・何をしている人か。AIの会話冒頭で参照する | ⭐ 必須 |",
        "| `02_business_overview.md` | 美容室・美容専門店・自社ブランド・J-Beautyの全体俯瞰 | ⭐ 推奨 |",
        "| `03_decisions_log.md` | 給与制度・コミッション率・人件費率など過去の決定事項（時系列） | テーマ依存 |",
        "| `04_open_ideas.md` | 過去に話したが未実行のアイデア集 | ブレスト時 |",
        "| `05_people_directory.md` | 登場人物（スタッフ・取引先・相談相手） | 名前が出たとき |",
        "| `06_artifacts_index.md` | 成果物439件のカタログ | ファイル探したい時 |",
        "| `themes/*.md` | テーマ別ナレッジ（給与・プロモ・商品・人事・競合・海外・経営指標） | 特定論点の深掘り |",
        "",
        "## 典型的な会話パターン（Cursor + AIOS）",
        "",
        "### パターンA: 既存テーマの続きを相談",
        "",
        "例: 「給与制度の続きを相談したい」",
        "",
        "1. AIに `01_PON_persona.md` と `themes/給与制度とスタッフマネジメント.md` を読ませる",
        "2. さらに `03_decisions_log.md` で過去の決定を確認",
        "3. 本題を相談",
        "",
        "### パターンB: 新しい事業判断",
        "",
        "例: 「新店舗をプノンペンに出したい」",
        "",
        "1. `01_PON_persona.md` + `02_business_overview.md`",
        "2. 近い事例として `美容室/ベトナム支店/README.md` + `themes/海外展開とJ-Beauty.md`",
        "3. 本題",
        "",
        "### パターンC: スタッフ個別の話",
        "",
        "例: 「RISAさんに新しい役割を任せたい」",
        "",
        "1. `05_people_directory.md` でRISAさんの登場文脈を確認",
        "2. 該当する `conversations_summary.md` で過去のやり取りを参照",
        "3. 本題",
        "",
        "## 更新について",
        "",
        "- `01_PON_persona.md` / `02_business_overview.md` / `03_decisions_log.md` / `04_open_ideas.md` / `themes/*.md` は Claude Sonnet / Opus で合成",
        "- `05_people_directory.md` / `06_artifacts_index.md` は機械生成（再生成コスト低）",
        "- 新しい会話を追加したい場合は田中さんまで",
    ]
    (OVERVIEW / "00_README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    print("=" * 60)
    print("機械生成ファイル作成")
    print("=" * 60)
    build_overview_readme()
    build_people_directory()
    build_artifacts_index()
    print("完了")


if __name__ == "__main__":
    run()
