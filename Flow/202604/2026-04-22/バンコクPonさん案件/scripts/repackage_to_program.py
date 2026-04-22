#!/usr/bin/env python3
"""Step4 deploy の出力を PONさん向け AIOS Program 構造に再パッケージする。

入力: /Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行/
出力: /Users/rikutanaka/aipm_v0/Flow/202604/2026-04-22/バンコクPonさん案件/output/pon-chatgpt-knowledge/

構造:
  pon-chatgpt-knowledge/
    README.md                      (repo-level, how-to-integrate)
    ChatGPT履歴/                   (drop-in AIOS Program)
      README.md                    (Program README)
      _overview/                   (cross-cutting knowledge — filled by batch)
        themes/
      美容室/                       (Project)
        README.md                  (Project README = Step4 category README)
        ProjectIndex.yaml          (new, generated)
        log.md                     (new, generated)
        {subcategory}/ ...
      美容専門店/ ...
      自社ブランド/ ...
      J-Beauty/ ...
    MasterIndex_snippet.yaml       (for merging into PONさん's Stock/MasterIndex.yaml)
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

SRC = Path("/Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT移行")
DST_ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202604/2026-04-22/バンコクPonさん案件/output/pon-chatgpt-knowledge")
PROGRAM_NAME = "ChatGPT履歴"
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]

PROGRAM_KEYWORDS = {
    "美容室": ["美容室", "サロン", "Rapi-rabi", "YAMS", "Cuus", "BELL", "Rio", "ベトナム", "給与", "プロモーション"],
    "美容専門店": ["美容専門店", "ネイル", "アイラッシュ", "MONDO", "アートメイク", "脱毛"],
    "自社ブランド": ["自社ブランド", "ヌリプラ", "DOT", "KINUJO", "カラー剤", "シャンプー", "EC", "店販"],
    "J-Beauty": ["J-Beauty", "日本美容", "アカデミー", "政策", "イベント", "コスメティクス", "インフルエンサー", "テック"],
}


def reset_dst():
    if DST_ROOT.exists():
        shutil.rmtree(DST_ROOT)
    DST_ROOT.mkdir(parents=True)


def count_files(d: Path, pattern: str = "*") -> int:
    return sum(1 for _ in d.rglob(pattern) if _.is_file())


def copy_category(cat: str) -> dict:
    """カテゴリをプロジェクトとしてコピーし、メタ情報を返す。"""
    src_cat = SRC / cat
    dst_cat = DST_ROOT / PROGRAM_NAME / cat
    shutil.copytree(src_cat, dst_cat)

    subcats = sorted([p.name for p in dst_cat.iterdir() if p.is_dir()])
    return {
        "category": cat,
        "subcategories": subcats,
        "md_count": count_files(dst_cat, "*.md"),
        "artifact_count": count_files(dst_cat / "artifacts" if (dst_cat / "artifacts").exists() else dst_cat, "*.md") - count_files(dst_cat, "*.md"),
    }


def write_project_index_yaml(cat: str, subcats: list[str]):
    """各ProjectのProjectIndex.yamlを生成。"""
    cat_dir = DST_ROOT / PROGRAM_NAME / cat
    lines = [
        "version: 1",
        "",
        "# ProjectIndex.yaml（AI専用）",
        f"# 目的: {cat} プロジェクト内のファイルへの参照インデックス",
        "",
        f'project: "{cat}"',
        f'root: "Stock/{PROGRAM_NAME}/{cat}"',
        "",
        "canonical:",
        '  readme: "README.md"',
        '  log: "log.md"',
        "",
        "files:",
        '  - path: "README.md"',
        f'    summary: "{cat}カテゴリ全体の概要。サブカテゴリ一覧・参照順序・PONさんの思考や検討内容の俯瞰。"',
        "    keywords:",
    ]
    for kw in PROGRAM_KEYWORDS[cat][:8]:
        lines.append(f'      - "{kw}"')
    lines.append('  - path: "log.md"')
    lines.append(f'    summary: "{cat}プロジェクトの変更ログ。"')
    lines.append("    keywords:")
    lines.append('      - "ログ"')

    for subcat in subcats:
        subcat_dir = cat_dir / subcat
        if not subcat_dir.is_dir():
            continue
        lines.append("")
        lines.append(f'  - path: "{subcat}/README.md"')
        lines.append(f'    summary: "{cat} > {subcat}のChatGPT過去会話サマリーと成果物一覧。"')
        lines.append("    keywords:")
        lines.append(f'      - "{cat}"')
        lines.append(f'      - "{subcat}"')
        # conversations_summary.md
        if (subcat_dir / "conversations_summary.md").exists():
            lines.append(f'  - path: "{subcat}/conversations_summary.md"')
            lines.append(f'    summary: "{cat} > {subcat}の会話統合サマリー（時系列・決定事項・登場人物含む）。"')
            lines.append("    keywords:")
            lines.append(f'      - "{cat}"')
            lines.append(f'      - "{subcat}"')
            lines.append('      - "会話サマリー"')

    (cat_dir / "ProjectIndex.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_project_log_md(cat: str, meta: dict):
    """各Projectのlog.mdを生成。"""
    cat_dir = DST_ROOT / PROGRAM_NAME / cat
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""# {cat} 変更ログ

## {today} — 初期移行（PONさん向けAIOS Program）

- ChatGPT会話履歴から {cat} カテゴリの会話・成果物を整理
- サブカテゴリ数: {len(meta['subcategories'])}
- サブカテゴリ: {', '.join(meta['subcategories'])}
- 出典: PONさんのChatGPT export（2026-03-23 時点のデータ）
- 生成方法: Anthropic Batch API（Claude Sonnet/Opus）による要約・構造化

## 参照
- 生成パイプライン詳細: [田中さん側 ChatGPT分析 ディレクトリ](https://github.com/) (田中さん側リポジトリに保管)
"""
    (cat_dir / "log.md").write_text(content, encoding="utf-8")


def write_program_readme(project_metas: list[dict]):
    """Program（ChatGPT履歴）直下のREADME.md を生成。"""
    total_conv = 120  # manifest from step3
    total_artifacts = 439
    lines = [
        "# ChatGPT履歴（PONさん過去AI対話ナレッジベース）",
        "",
        "## このフォルダは何か",
        "",
        "PONさん（近藤Pon / Rios Innovation Co., Ltd.）がこれまでChatGPTで行ってきた会話を、",
        "**AIとの継続的な対話の基盤**として再利用できるよう、AIOS準拠の形式で整理したナレッジベースです。",
        "",
        "PONさんが Cursor + AIOS 環境で新しい会話を始める際、このディレクトリをコンテキストとして参照することで、",
        "過去に検討した給与制度・プロモーション戦略・商品開発・海外展開などの経緯を踏まえた対話が可能になります。",
        "",
        "## 統計",
        "",
        "| 項目 | 数 |",
        "|---|---:|",
        "| プロジェクト（カテゴリ） | 4 |",
        "| サブカテゴリ（店舗・事業単位） | 21 |",
        f"| 統合サマリー対象会話 | {total_conv}件 |",
        f"| 成果物ファイル | {total_artifacts}件 |",
        "| 横断ナレッジ（_overview/） | 13ファイル |",
        "",
        "## ディレクトリ構造",
        "",
        "```",
        "ChatGPT履歴/",
        "├── README.md                     ← このファイル",
        "├── _overview/                    ← Program横断ナレッジ（最初に読む）",
        "│   ├── 00_README.md              ← _overview/ の使い方",
        "│   ├── 01_PON_persona.md         ← AIに最初に渡すペルソナ定義",
        "│   ├── 02_business_overview.md   ← 事業全体像",
        "│   ├── 03_decisions_log.md       ← 決定事項の時系列ログ",
        "│   ├── 04_open_ideas.md          ← 未実行アイデア集",
        "│   ├── 05_people_directory.md    ← 登場人物・関係者",
        "│   ├── 06_artifacts_index.md     ← 成果物439件の目次",
        "│   └── themes/                   ← テーマ別ナレッジ（7本）",
        "│",
        "├── 美容室/                        ← Project",
        "├── 美容専門店/                    ← Project",
        "├── 自社ブランド/                  ← Project",
        "└── J-Beauty/                      ← Project",
        "",
        "各 Project 配下:",
        "    README.md            （プロジェクト全体の概要）",
        "    ProjectIndex.yaml    （AIが参照するインデックス）",
        "    log.md               （変更履歴）",
        "    {サブカテゴリ}/",
        "        README.md                  （サブカテゴリのREADME）",
        "        conversations_summary.md   （会話サマリー）",
        "        conversations_index.json   （会話インデックス）",
        "        artifacts/                 （ChatGPTで生成した成果物）",
        "```",
        "",
        "## 使い方（Cursor + AIOS）",
        "",
        "### 1. 新しいAIセッションを始めるとき",
        "",
        "CursorでAIに質問する前に、以下を会話の冒頭で参照してください:",
        "",
        "- `_overview/01_PON_persona.md` — PONさんのビジネスコンテキスト",
        "- 該当するProjectの `README.md`（例: 給与制度の話なら `美容室/README.md`）",
        "",
        "AIはこれらを読んで、PONさんの過去の検討経緯を踏まえた回答ができます。",
        "",
        "### 2. 特定テーマについて深掘りする",
        "",
        "横断テーマで探す場合は `_overview/themes/{テーマ}.md` を参照。",
        "",
        "- 給与・コミッション・評価制度 → `themes/給与制度とスタッフマネジメント.md`",
        "- プロモーション・マーケ → `themes/プロモーション・マーケティング.md`",
        "- 商品開発・ブランド → `themes/商品開発・ブランド戦略.md`",
        "- 人事評価・採用 → `themes/人事評価・採用.md`",
        "- 競合・市場 → `themes/競合分析と市場対応.md`",
        "- 海外展開・J-Beauty → `themes/海外展開とJ-Beauty.md`",
        "- 経営指標・財務 → `themes/経営指標・財務管理.md`",
        "",
        "### 3. 過去の決定事項を確認する",
        "",
        "`_overview/03_decisions_log.md` に、給与制度・コミッション率・人件費率など過去の決定事項が時系列でまとまっています。",
        "",
        "### 4. 未実行のアイデアを拾う",
        "",
        "`_overview/04_open_ideas.md` に、ChatGPTで話したが実装未了のアイデアがストックされています。",
        "",
        "## Projects一覧",
        "",
    ]

    for meta in project_metas:
        cat = meta["category"]
        lines.append(f"### {cat}/")
        lines.append(f"サブカテゴリ {len(meta['subcategories'])}件")
        for s in meta["subcategories"]:
            lines.append(f"- `{s}/`")
        lines.append("")

    lines += [
        "## データ出典",
        "",
        "- PONさんのChatGPT会話履歴 export（2026-03-23 取得）",
        "- 225件の会話を抽出 → 120件を統合サマリー化 + 成果物439件を保全",
        "- 生成パイプライン: Anthropic Batch API（Claude Sonnet/Opus）",
        "- 生成実行日: 2026-04-22（by 田中さん + Claude Code）",
        "",
        "## 更新方針",
        "",
        "新しいChatGPT会話を追加したい場合は、田中さん経由で再エクスポート → 同じパイプラインで更新します。",
        "",
        "## 関連",
        "",
        "- プログラム全体の背景: `_overview/00_README.md`",
        "- MasterIndexへの追加: リポジトリルートの `MasterIndex_snippet.yaml` を参照",
    ]

    (DST_ROOT / PROGRAM_NAME / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_repo_readme(project_metas: list[dict]):
    """リポジトリルートのREADME.mdを生成。"""
    lines = [
        "# pon-chatgpt-knowledge",
        "",
        "PONさん（近藤Pon / Rios Innovation Co., Ltd.）のChatGPT会話履歴から整理した、",
        "**Cursor + AIOS 環境にdrop-inできる AIOS Program**です。",
        "",
        "## 中身",
        "",
        "- `ChatGPT履歴/` — AIOS Program（drop-in可）",
        "  - `_overview/` — Program横断ナレッジ（ペルソナ・テーマ別・決定ログ・アイデア・人物・成果物目次）",
        "  - `美容室/`, `美容専門店/`, `自社ブランド/`, `J-Beauty/` — 4つの Project",
        "- `MasterIndex_snippet.yaml` — PONさんの `Stock/MasterIndex.yaml` にマージするスニペット",
        "",
        "## PONさん側でのセットアップ（3ステップ）",
        "",
        "### Step 1. Stock に配置",
        "",
        "```bash",
        "# PONさんのAIOSリポジトリのルートで実行",
        "cp -r ChatGPT履歴 ~/path/to/your-aios/Stock/",
        "```",
        "",
        "### Step 2. MasterIndex.yaml にエントリを追加",
        "",
        "`MasterIndex_snippet.yaml` の内容を、自分の `Stock/MasterIndex.yaml` の末尾（Programsセクション内）に追記してください。",
        "",
        "### Step 3. 使ってみる",
        "",
        "Cursor で新しいチャットを開き、こう聞いてみてください:",
        "",
        "> 「Stock/ChatGPT履歴/_overview/01_PON_persona.md を読んで、自分は誰か理解してほしい。その上で、今月の給与制度についての改善案を提案して」",
        "",
        "AIは過去の給与制度の検討経緯を踏まえた提案をしてくれます。",
        "",
        "詳しい使い方は `ChatGPT履歴/README.md` を参照してください。",
        "",
        "## 秘密情報について",
        "",
        "このリポジトリには以下の情報が含まれます:",
        "",
        "- スタッフ氏名、給与額、コミッション率",
        "- 取引先情報、意思決定の経緯",
        "- 経営指標、売上目標",
        "",
        "**privateリポジトリとして運用してください。** PONさん本人とアクセス必要な関係者のみCollaboratorに追加する想定です。",
        "",
        "## 生成元",
        "",
        "- PONさんのChatGPT会話履歴export（2026-03-23 取得）",
        "- Anthropic Batch API (Claude Sonnet 4 + Opus 4.5) による整理",
        "- 生成実行: 2026-04-22（田中利空 + Claude Code）",
        "",
        "## ライセンス",
        "",
        "Rios Innovation Co., Ltd. 内部ナレッジベース。無断で外部共有しないでください。",
    ]
    (DST_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_masterindex_snippet():
    lines = [
        "# MasterIndex_snippet.yaml",
        "# PONさんのAIOS Stock/MasterIndex.yaml の Programs セクションに、",
        "# 以下のエントリを追記してください。",
        "",
        "ChatGPT履歴:",
        '  summary: "PONさんの過去のChatGPT会話履歴を、AIとの継続対話の基盤として整理したナレッジベース。"',
        "  keywords:",
        '    - "ChatGPT"',
        '    - "過去会話"',
        '    - "ナレッジベース"',
        '    - "PON"',
        '    - "Rios Innovation"',
        '    - "美容室"',
        '    - "美容専門店"',
        '    - "自社ブランド"',
        '    - "J-Beauty"',
        '    - "給与制度"',
        '    - "プロモーション"',
        '    - "商品開発"',
        '    - "海外展開"',
        "  projects:",
        "    美容室:",
        '      summary: "PONさんが経営する複数の美容室ブランド（Rapi-rabi, YAMS, Cuu\'s, BELL, Rio）の運営全般のChatGPT会話。給与制度・プロモーション・海外展開など。"',
        "      keywords:",
        '        - "美容室"',
        '        - "サロン経営"',
        '        - "給与制度"',
        '        - "プロモーション"',
        '        - "Rapi-rabi"',
        '        - "YAMS"',
        '        - "ベトナム支店"',
        '      path: "Stock/ChatGPT履歴/美容室"',
        '      readme: "README.md"',
        '      index: "ProjectIndex.yaml"',
        "    美容専門店:",
        '      summary: "ネイルサロン、アイラッシュ、MONDO BEAUTY clinic など美容専門店業態のChatGPT会話。"',
        "      keywords:",
        '        - "美容専門店"',
        '        - "ネイル"',
        '        - "アイラッシュ"',
        '        - "MONDO"',
        '        - "クリニック"',
        '      path: "Stock/ChatGPT履歴/美容専門店"',
        '      readme: "README.md"',
        '      index: "ProjectIndex.yaml"',
        "    自社ブランド:",
        '      summary: "ヌリプラ（カラー剤）、DOT（シャンプー/トリートメント）、KINUJO（提携）など自社ブランド・商品開発のChatGPT会話。"',
        "      keywords:",
        '        - "自社ブランド"',
        '        - "ヌリプラ"',
        '        - "DOT"',
        '        - "KINUJO"',
        '        - "EC展開"',
        '        - "商品開発"',
        '      path: "Stock/ChatGPT履歴/自社ブランド"',
        '      readme: "README.md"',
        '      index: "ProjectIndex.yaml"',
        "    J-Beauty:",
        '      summary: "日本美容のタイ展開、政策連携、アカデミー構想、イベント企画などのChatGPT会話。"',
        "      keywords:",
        '        - "J-Beauty"',
        '        - "日本美容"',
        '        - "アカデミー"',
        '        - "政策"',
        '        - "タイ進出"',
        '        - "インフルエンサー"',
        '      path: "Stock/ChatGPT履歴/J-Beauty"',
        '      readme: "README.md"',
        '      index: "ProjectIndex.yaml"',
    ]
    (DST_ROOT / "MasterIndex_snippet.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    print("=" * 60)
    print("AIOS再パッケージング開始")
    print("=" * 60)
    reset_dst()

    # Program directory
    (DST_ROOT / PROGRAM_NAME / "_overview" / "themes").mkdir(parents=True, exist_ok=True)

    project_metas = []
    for cat in CATEGORIES:
        meta = copy_category(cat)
        write_project_index_yaml(cat, meta["subcategories"])
        write_project_log_md(cat, meta)
        project_metas.append(meta)
        print(f"  ✓ {cat}: {len(meta['subcategories'])} subcategories, {meta['md_count']} MD files")

    write_program_readme(project_metas)
    write_repo_readme(project_metas)
    write_masterindex_snippet()

    # 統計サマリ
    total_md = sum(1 for _ in DST_ROOT.rglob("*.md") if _.is_file())
    total_files = sum(1 for _ in DST_ROOT.rglob("*") if _.is_file())
    print("=" * 60)
    print(f"完了: {DST_ROOT}")
    print(f"  Markdownファイル: {total_md}")
    print(f"  総ファイル数: {total_files}")
    print("=" * 60)


if __name__ == "__main__":
    run()
