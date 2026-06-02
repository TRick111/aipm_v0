# Claude Code から PowerPoint を作る 3 方法 — 検証セット

ユニゾン社向けに、Claude Code が**ローカル PC のデータを参照しながら** PowerPoint を生成する 3 方法 (python-pptx / pptxGenJs / Marp) を同一内容で比較するためのデモ一式。

## 成果物

| ファイル | 中身 | 役割 |
| --- | --- | --- |
| `deck.md` | フロントマター + 5 スライド (Marp 互換 `---` 区切り) | **共通入力**。3 方法すべてのソース |
| `themes/anthropic-cream.css` | 配色定義 (#F5EFE0 / #1A1A1A / #CC785C) | **配色 Source of Truth** (Marp 用)。ブランド差し替えはまずここ |
| `assets/cream-template.pptx` | ワイド 13.333×7.5in + Cream 背景 + アクセントバー 1 枚 | python-pptx 用の空テンプレ |
| `deck-python-pptx.pptx` (36 KB) | 5 スライド、テキスト編集可 | 方法A 出力 |
| `deck-pptxgenjs.pptx` (150 KB) | 5 スライド、テキスト編集可 | 方法B 出力 |
| `deck-marp.pptx` (882 KB) | 5 スライド、**背景画像化** (テキスト不可) | 方法C 出力 |

## 各 .pptx の再現手順

### 共通: 1 回だけのインストール
```bash
# Anthropic 公式 pptx スキル (python-pptx と pptxGenJs の作法ガイド + ユーティリティ)
git clone --depth 1 https://github.com/anthropics/skills.git /tmp/anthropic-skills && \
  cp -r /tmp/anthropic-skills/skills/pptx ~/.claude/skills/pptx

# ランタイム
python3 -m pip install --user --break-system-packages python-pptx python-frontmatter 'markitdown[pptx]'
npm i -g pptxgenjs gray-matter
brew install marp-cli
# 編集可 Marp pptx が欲しい場合のみ
# brew install --cask libreoffice
```

### 方法A: python-pptx (サブエージェント経由)
Claude Code 上で `Agent` ツール (general-purpose) を起動し、以下を依頼:

> 「`~/.claude/skills/pptx/SKILL.md` と `editing.md` を読んで、`deck.md` を **python-pptx** で `deck-python-pptx.pptx` に変換せよ。テンプレは `assets/cream-template.pptx`。各スライドに Cream 背景 (#F5EFE0) + 下部アクセントバー (#CC785C) を敷き、日本語フォントは Hiragino Sans を `eastAsian` で明示。Markdown 5 スライド目の `|` 表は PowerPoint 表として再現。**永続スクリプトは作らず**、一時ファイルで実行して削除」

### 方法B: pptxGenJs (サブエージェント経由)
同じく `Agent` ツールで:

> 「`~/.claude/skills/pptx/SKILL.md` と `pptxgenjs.md` を読んで、`deck.md` を **pptxGenJs** で `deck-pptxgenjs.pptx` に変換せよ。`pres.layout = LAYOUT_WIDE`、背景 #F5EFE0、本文 #1A1A1A、`fontFace: 'Hiragino Sans'`。アクセントバーは `addShape` で全スライドに。グローバル install を解決するには `NODE_PATH=$(npm root -g) node /tmp/script.cjs` で実行。**ユニゾン社フォルダに `package.json`/`node_modules` を残さない**」

### 方法C: Marp (CLI 直叩き)
```bash
cd /Users/rikutanaka/aipm_v0/Flow/202606/2026-06-02/ユニゾン社
marp deck.md --pptx --allow-local-files \
  --theme-set themes/anthropic-cream.css \
  -o deck-marp.pptx

# 編集可能版が欲しいときは LibreOffice を入れてから:
# marp deck.md --pptx --pptx-editable --allow-local-files --theme-set themes/anthropic-cream.css -o deck-marp-editable.pptx
```

## 検証

```bash
# スライド枚数確認 (3 ファイル × 5 枚)
python3 -c "from pptx import Presentation; [print(f, '->', len(Presentation(f).slides)) for f in ['deck-python-pptx.pptx','deck-pptxgenjs.pptx','deck-marp.pptx']]"

# 内容回帰 (python-pptx と pptxgenjs の本文が一致するか)
~/Library/Python/3.14/bin/markitdown deck-python-pptx.pptx > /tmp/a.txt
~/Library/Python/3.14/bin/markitdown deck-pptxgenjs.pptx  > /tmp/b.txt
diff /tmp/a.txt /tmp/b.txt   # 体裁差のみで内容は同じはず (Marp は画像化のため比較対象外)

# 目視
open deck-python-pptx.pptx deck-pptxgenjs.pptx deck-marp.pptx
```

## ユニゾン社の本物のブランドカラー / ロゴが来たら

1. `themes/anthropic-cream.css` の `#F5EFE0`/`#1A1A1A`/`#CC785C` を差し替える
2. `assets/cream-template.pptx` を作り直す (背景色とアクセントバー)
3. サブエージェント依頼文の配色 hex 値を更新

→ 3 方法すべてに伝播。共通 `deck.md` の中身はそのまま使い回せる。

## 想定される詰まりどころ

- **公式 pptx スキルが Claude Code に読まれない**: `~/.claude/skills/pptx/` 配置後、Claude Code セッションを再起動 (起動時に SKILL.md が自動ロードされる)。`/pptx` が skills 一覧に出ていれば OK
- **Python の `--user --break-system-packages`**: macOS の Homebrew Python は PEP 668 で外部管理判定されるため、必須。VS Code 連携や本格運用なら venv 化推奨
- **Node のグローバル解決**: サブエージェントが `require()` に失敗するなら `NODE_PATH=$(npm root -g)` を環境変数で渡す
- **Marp の `--pptx` 既定は背景画像化**: PowerPoint で文字編集不可。編集可 pptx には `--pptx-editable` + LibreOffice (`brew install --cask libreoffice`) 必須
- **Marp で日本語豆腐化**: `themes/anthropic-cream.css` で `@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP...')` 必須、`--allow-local-files` も忘れずに

## 編集性チェック (実機で田中さんが試す欄)

| 方法 | 1 ページ目を PowerPoint で開いて文字編集 → 保存 |
| --- | --- |
| python-pptx | (未確認) |
| pptxGenJs | (未確認) |
| Marp (画像化) | 文字編集不可 (画像化のため) |
| Marp (`--pptx-editable`) | (LibreOffice 未導入のため未生成) |
