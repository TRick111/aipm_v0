#!/usr/bin/env python3
"""BL-0037 出力を AIPM Project ルールに準拠させる修正スクリプト。

修正内容:
  1. 各サブカテゴリ (leaf) を AIPM Project 化
     - conversations_index.json → ProjectIndex.yaml に置換
     - log.md を追加
     - conversations_index.json は削除
  2. artifacts/*.md の先頭8文字hexプレフィックス（`<hex>_`）を除去
     - 同名衝突時は `_2.md`, `_3.md` などでsuffix付与
  3. README.md / conversations_summary.md / _overview/06_artifacts_index.md 内の
     artifact filename 参照を新名に置換
  4. MasterIndex_snippet.yaml を Project=subcategory 単位で再生成

AI-Core を AIPM Project 参考構造とみなす:
  README.md / ProjectIndex.yaml / log.md
"""
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202604/2026-04-22/バンコクPonさん案件/output/pon-chatgpt-knowledge")
PROGRAM_ROOT = ROOT / "ChatGPT履歴"
OVERVIEW = PROGRAM_ROOT / "_overview"
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]

HEX_PREFIX = re.compile(r"^[a-f0-9]{8}_(.+)$")

SUBCAT_KEYWORDS_BASE = {
    "美容室": ["美容室", "サロン"],
    "美容専門店": ["美容専門店"],
    "自社ブランド": ["自社ブランド", "商品開発"],
    "J-Beauty": ["J-Beauty", "日本美容"],
}


# --- Step 1: artifactのリネーム ---

def rename_artifacts(subcat_dir: Path) -> dict[str, str]:
    """artifacts/ 内で <8hex>_ プレフィックスを除去。衝突時は _2.md, _3.md を付与。
    return: {old_filename: new_filename}"""
    artifacts_dir = subcat_dir / "artifacts"
    if not artifacts_dir.exists():
        return {}
    rename_map: dict[str, str] = {}
    # planned target names → track to detect collisions
    planned_targets: set[str] = set()
    for f in sorted(artifacts_dir.iterdir()):
        if not f.is_file():
            continue
        # すべての artifact 拡張子（.md / .docx / .pdf / .txt 等）を対象
        m = HEX_PREFIX.match(f.name)
        if not m:
            # プレフィックス無しならそのまま（リネーム対象外）
            planned_targets.add(f.name)
            continue
        base = m.group(1)  # e.g., "foo.md"
        candidate = base
        if candidate in planned_targets:
            # 衝突 → suffix付与
            if "." in candidate:
                stem, ext = candidate.rsplit(".", 1)
                ext = "." + ext
            else:
                stem, ext = candidate, ""
            n = 2
            while f"{stem}_{n}{ext}" in planned_targets:
                n += 1
            candidate = f"{stem}_{n}{ext}"
        planned_targets.add(candidate)
        rename_map[f.name] = candidate

    # 実リネーム
    for old, new in rename_map.items():
        (artifacts_dir / old).rename(artifacts_dir / new)
    return rename_map


# --- Step 2: README.md / conversations_summary.md の参照置換 ---

def update_text_references(subcat_dir: Path, rename_map: dict[str, str]):
    if not rename_map:
        return
    for fname in ["README.md", "conversations_summary.md"]:
        fpath = subcat_dir / fname
        if not fpath.exists():
            continue
        content = fpath.read_text(encoding="utf-8")
        changed = False
        for old, new in rename_map.items():
            if old in content:
                content = content.replace(old, new)
                changed = True
        if changed:
            fpath.write_text(content, encoding="utf-8")


# --- Step 3: ProjectIndex.yaml 生成 + conversations_index.json 削除 ---

def _yaml_escape(s: str) -> str:
    """YAML文字列として安全にエスケープ。"""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def build_project_index(subcat_dir: Path, cat: str, subcat_name: str, idx_data: dict, rename_map: dict[str, str]):
    """ProjectIndex.yaml を生成して書き出し、conversations_index.json を削除。"""
    # artifact metadata: rename reflection
    artifacts = idx_data.get("artifacts", [])
    for a in artifacts:
        old = a.get("file")
        if old in rename_map:
            a["file"] = rename_map[old]

    base_kw = SUBCAT_KEYWORDS_BASE.get(cat, [])

    lines = [
        "version: 1",
        "",
        f'project: "{subcat_name}"',
        f'root: "Stock/ChatGPT履歴/{cat}/{subcat_name}"',
        "",
        "# BL-0037 PONさんChatGPT履歴から生成",
        f"# カテゴリ: {cat} / サブカテゴリ: {subcat_name}",
        "",
        "canonical:",
        '  readme: "README.md"',
        '  log: "log.md"',
        "",
        "files:",
    ]

    # README.md
    lines += [
        '  - path: "README.md"',
        f'    summary: "{_yaml_escape(f"{cat} > {subcat_name} のChatGPT会話履歴プロジェクト概要。サブカテゴリに含まれる会話・成果物・参照ヒント。")}"',
        "    keywords:",
    ]
    for kw in base_kw + [subcat_name]:
        lines.append(f'      - "{kw}"')

    # log.md
    lines += [
        '  - path: "log.md"',
        '    summary: "プロジェクト変更ログ（ファイル作成/編集履歴）"',
        "    keywords:",
        '      - "ログ"',
        '      - "変更履歴"',
    ]

    # conversations_summary.md
    if (subcat_dir / "conversations_summary.md").exists():
        no_art_count = len(idx_data.get("no_artifact_conversations", []))
        lines += [
            '  - path: "conversations_summary.md"',
            f'    summary: "{_yaml_escape(f"会話統合サマリー。時系列・主要トピック・重要な決定事項・登場人物。{no_art_count}件の成果物なし会話を統合。")}"',
            "    keywords:",
        ]
        for kw in base_kw + [subcat_name, "会話サマリー", "決定事項"]:
            lines.append(f'      - "{kw}"')

    # artifacts
    for a in artifacts:
        fname = a.get("file", "")
        desc = _yaml_escape(a.get("description", ""))
        typ = a.get("type", "")
        if not fname:
            continue
        lines.append(f'  - path: "artifacts/{fname}"')
        lines.append(f'    summary: "{desc}"')
        lines.append("    keywords:")
        for kw in base_kw + [subcat_name]:
            lines.append(f'      - "{kw}"')
        if typ:
            lines.append(f'      - "{typ}"')

    (subcat_dir / "ProjectIndex.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # conversations_index.json を削除
    idx_file = subcat_dir / "conversations_index.json"
    if idx_file.exists():
        idx_file.unlink()


# --- Step 4: log.md 生成 ---

def build_log_md(subcat_dir: Path, cat: str, subcat_name: str, rename_count: int):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# log（{subcat_name}）",
        "",
        "## 目的",
        "- このプロジェクトの変更履歴（ファイルの作成/削除/編集）が追えるようにする。",
        "- 変更内容・変更理由は **任意**。",
        "",
        "## 変更履歴",
        "",
        "| 日付 | 種別 | ファイル | 変更内容（任意） | 変更理由（任意） |",
        "|---|---|---|---|---|",
        f"| {today} | create | `README.md` / `conversations_summary.md` / `artifacts/**` | ChatGPT会話履歴（{cat} > {subcat_name}）の初期移行 | BL-0037 Phase1（Step4 deploy） |",
        f"| {today} | create | `ProjectIndex.yaml` / `log.md` | AIPM Project形式に準拠（`conversations_index.json` から変換） | BL-0037 Phase2（AIPM準拠化） |",
    ]
    if rename_count > 0:
        lines.append(
            f"| {today} | rename | `artifacts/*.md` | 先頭 `<8hex>_` プレフィックスを除去（{rename_count}件） | AIPM準拠: 会話IDプレフィックス不要 |"
        )
    lines.append("")
    (subcat_dir / "log.md").write_text("\n".join(lines), encoding="utf-8")


# --- Step 5: 各カテゴリを一周 ---

def iter_subcategories():
    for cat in CATEGORIES:
        cat_dir = PROGRAM_ROOT / cat
        if not cat_dir.is_dir():
            continue
        for sub in sorted(cat_dir.iterdir()):
            if sub.is_dir():
                yield cat, sub.name, sub


def fix_all_subcategories() -> dict[str, dict[str, str]]:
    """全サブカテゴリを AIPM 準拠に修正。
    return: {subcat_path_str: rename_map}"""
    all_renames = {}
    for cat, subcat_name, subcat_dir in iter_subcategories():
        idx_file = subcat_dir / "conversations_index.json"
        idx_data = {}
        if idx_file.exists():
            idx_data = json.loads(idx_file.read_text(encoding="utf-8"))
        rename_map = rename_artifacts(subcat_dir)
        update_text_references(subcat_dir, rename_map)
        build_project_index(subcat_dir, cat, subcat_name, idx_data, rename_map)
        build_log_md(subcat_dir, cat, subcat_name, len(rename_map))
        all_renames[f"{cat}/{subcat_name}"] = rename_map
        if rename_map:
            print(f"  ✓ {cat}/{subcat_name}: {len(rename_map)} artifacts renamed, ProjectIndex.yaml + log.md created")
        else:
            print(f"  ✓ {cat}/{subcat_name}: ProjectIndex.yaml + log.md created")
    return all_renames


# --- Step 6: _overview/06_artifacts_index.md の再生成 ---

def rebuild_artifacts_index():
    print("\nRebuilding _overview/06_artifacts_index.md ...")
    lines = [
        "# 成果物（artifacts）目次",
        "",
        "## このファイルについて",
        "",
        "PONさんのChatGPT会話から抽出された **成果物ファイル439件** の全カタログです。",
        "成果物 = PONさんとChatGPTのやり取りで生成されたレポート・提案書・計算・ガイド等の最終出力物。",
        "",
        "各ファイルは `<カテゴリ>/<サブカテゴリ>/artifacts/<ファイル名>.md` に配置されています。",
        "テーマごとの俯瞰は `_overview/themes/*.md` を、個別の詳細は各サブカテゴリの README.md を参照してください。",
        "",
    ]
    total = 0
    for cat in CATEGORIES:
        cat_dir = PROGRAM_ROOT / cat
        cat_lines = [f"## {cat}", ""]
        cat_total = 0
        for subcat_dir in sorted(cat_dir.iterdir()):
            if not subcat_dir.is_dir():
                continue
            artifacts_dir = subcat_dir / "artifacts"
            if not artifacts_dir.exists():
                continue
            # ProjectIndex.yaml から artifact metadata を読み取る
            pidx = subcat_dir / "ProjectIndex.yaml"
            # 手抜きパース: `path: "artifacts/xxx.md"` と `summary: "..."` のペア
            entries = []
            if pidx.exists():
                content = pidx.read_text(encoding="utf-8").splitlines()
                i = 0
                while i < len(content):
                    line = content[i].strip()
                    m = re.match(r'-\s*path:\s*"artifacts/(.+?)"$', line)
                    if m:
                        fname = m.group(1)
                        # 次の summary: 行を探す
                        summary = ""
                        if i + 1 < len(content):
                            m2 = re.match(r'summary:\s*"(.*)"$', content[i + 1].strip())
                            if m2:
                                summary = m2.group(1)
                        entries.append((fname, summary))
                    i += 1
            if not entries:
                continue
            cat_lines.append(f"### {subcat_dir.name}（{len(entries)}件）")
            cat_lines.append("")
            cat_lines.append("| ファイル | 説明 |")
            cat_lines.append("|---|---|")
            for fname, summary in entries:
                relpath = f"../{cat}/{subcat_dir.name}/artifacts/{fname}"
                safe_summary = summary.replace("|", "／")
                cat_lines.append(f"| [{fname}]({relpath}) | {safe_summary} |")
            cat_lines.append("")
            cat_total += len(entries)
        cat_lines[0] = f"## {cat}（{cat_total}件）"
        lines.extend(cat_lines)
        total += cat_total
    lines.append(f"## 合計: {total}件")
    lines.append("")
    lines.append("## 使い方")
    lines.append("")
    lines.append("- ファイル名でGrep: `grep -r 'キーワード' .` で特定成果物を見つけられます")
    lines.append("- 過去の数値・ノウハウを参照したい場合: ファイル内に具体値が残っています")
    lines.append("- AIOSの ProjectIndex.yaml からも同じファイルにアクセス可")
    (OVERVIEW / "06_artifacts_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  total artifacts: {total}")


# --- Step 7: MasterIndex_snippet.yaml の再生成（Project=subcategory単位） ---

def rebuild_masterindex_snippet():
    print("\nRebuilding MasterIndex_snippet.yaml ...")
    lines = [
        "# MasterIndex_snippet.yaml",
        "# PONさんのAIOS Stock/MasterIndex.yaml の Programs セクションに、",
        "# 以下のエントリを追記してください。",
        "#",
        "# 本Programは「ChatGPT履歴」で、21個のProject（= サブカテゴリ単位）を含みます。",
        "# カテゴリ（美容室/美容専門店/自社ブランド/J-Beauty）はProject名のprefixとして表現しています。",
        "",
        "ChatGPT履歴:",
        '  summary: "PONさんの過去のChatGPT会話履歴を、AIとの継続対話の基盤として整理したナレッジベース。4カテゴリ21プロジェクトの構成。"',
        "  keywords:",
    ]
    for kw in [
        "ChatGPT", "過去会話", "ナレッジベース", "PON", "Rios Innovation",
        "美容室", "美容専門店", "自社ブランド", "J-Beauty",
        "給与制度", "プロモーション", "商品開発", "海外展開",
    ]:
        lines.append(f'    - "{kw}"')
    lines.append("  projects:")

    # 各サブカテゴリを Project として列挙（<Category>_<Subcategory>）
    for cat in CATEGORIES:
        cat_dir = PROGRAM_ROOT / cat
        for subcat_dir in sorted(cat_dir.iterdir()):
            if not subcat_dir.is_dir():
                continue
            subcat = subcat_dir.name
            project_key = f"{cat}_{subcat}"
            base_kw = SUBCAT_KEYWORDS_BASE.get(cat, [])
            lines.append(f"    {project_key}:")
            lines.append(
                f'      summary: "{cat} > {subcat} のChatGPT会話履歴。" '
            )
            # summary 正しい書き方に直す（上の行はerror）
    lines_fixed = []
    for cat in CATEGORIES:
        cat_dir = PROGRAM_ROOT / cat
        for subcat_dir in sorted(cat_dir.iterdir()):
            if not subcat_dir.is_dir():
                continue
            subcat = subcat_dir.name
            project_key = f"{cat}_{subcat}"
            base_kw = SUBCAT_KEYWORDS_BASE.get(cat, [])
            lines_fixed.append(f"    {project_key}:")
            lines_fixed.append(
                f'      summary: "{cat} > {subcat} のChatGPT会話履歴プロジェクト。"'
            )
            lines_fixed.append("      keywords:")
            for kw in base_kw + [subcat]:
                lines_fixed.append(f'        - "{kw}"')
            lines_fixed.append(f'      path: "Stock/ChatGPT履歴/{cat}/{subcat}"')
            lines_fixed.append('      readme: "README.md"')
            lines_fixed.append('      index: "ProjectIndex.yaml"')

    # rebuild lines without the buggy block
    lines = [
        "# MasterIndex_snippet.yaml",
        "# PONさんのAIOS Stock/MasterIndex.yaml の Programs セクションに、",
        "# 以下のエントリを追記してください。",
        "#",
        "# 本Programは「ChatGPT履歴」で、21個のProject（= サブカテゴリ単位）を含みます。",
        "# カテゴリ（美容室/美容専門店/自社ブランド/J-Beauty）はProject名のprefixとして表現。",
        "",
        "ChatGPT履歴:",
        '  summary: "PONさんの過去のChatGPT会話履歴を、AIとの継続対話の基盤として整理したナレッジベース。4カテゴリ21プロジェクト構成。"',
        "  keywords:",
    ]
    for kw in [
        "ChatGPT", "過去会話", "ナレッジベース", "PON", "Rios Innovation",
        "美容室", "美容専門店", "自社ブランド", "J-Beauty",
        "給与制度", "プロモーション", "商品開発", "海外展開",
    ]:
        lines.append(f'    - "{kw}"')
    lines.append("  projects:")
    lines.extend(lines_fixed)

    (ROOT / "MasterIndex_snippet.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- 実行 ---

def run():
    print("=" * 60)
    print("AIPM準拠修正: サブカテゴリを Project 形式に、artifact prefix除去")
    print("=" * 60)
    all_renames = fix_all_subcategories()
    rebuild_artifacts_index()
    rebuild_masterindex_snippet()

    # 集計
    total_renames = sum(len(m) for m in all_renames.values())
    total_subcats = len(all_renames)
    print()
    print("=" * 60)
    print(f"  サブカテゴリ修正: {total_subcats} / artifact rename: {total_renames}")
    print(f"  各サブカテゴリに ProjectIndex.yaml + log.md 配置、conversations_index.json 削除")
    print(f"  _overview/06_artifacts_index.md / MasterIndex_snippet.yaml 再生成")
    print("=" * 60)


if __name__ == "__main__":
    run()
