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

---

# ====== 本格営業資料 (UNI'SON 多店舗 FC 本部向け) ======

シンプル箇条書きでは 3 方法の差が出なかったので、**多店舗 FC 本部向けの本格営業資料 10 枚** で再検証。共通仕様書 [`slide_spec.md`](slide_spec.md) と デザイントークン [`design_tokens.json`](design_tokens.json) を 3 方法とも厳守、画像はユニゾン社ホームページから引用 ([`assets/unison/`](assets/unison/))。

## 本格版の成果物

| ファイル | サイズ | 中身 |
| --- | --- | --- |
| [slide_spec.md](slide_spec.md) | 14 KB | 共通仕様書 (10 スライドのレイアウト + コピー) |
| [design_tokens.json](design_tokens.json) | 2 KB | Playwright で抽出: 色 (#7297A9 #126D64 #F09D01 #404040) + Noto Sans JP |
| assets/unison/ | 約 7 MB | ロゴ (white/primary) + ヒーロー画像 7 枚 + CTA 背景 等 |
| **deck-unison-python-pptx.pptx** | 1.2 MB | テキスト編集可 ✅ |
| **deck-unison-pptxgenjs.pptx** | 1.4 MB | テキスト編集可 ✅ |
| **deck-unison-marp.pptx** | 5.5 MB | 画像化 (LibreOffice 未導入のため `--pptx-editable` 不可) |
| themes/unison.css | 18 KB | Marp 専用テーマ (13 カスタムクラス、Noto Sans JP 読込) |
| unison-deck.md | 14 KB | Marp ソース (HTML + Markdown + CSS クラス参照) |
| deck-unison-marp.html | 148 KB | Marp 中間 HTML (見た目確認用) |

## 仕様書を 3 方法でどこまで再現できたか

| 仕様要素 | python-pptx | pptxGenJs | Marp |
| --- | --- | --- | --- |
| フルブリード画像 + オーバーレイ | ◎ lxml で `a:alpha` 注入し透明度を直制御 | ○ 単色 + 2 層マスクで近似 | ◎ CSS gradient で完全表現 |
| ロゴ SVG | ○ cairosvg で PNG 化して埋込 | △ テキスト「UNI'SON」で代用 | ◎ SVG をそのまま参照 |
| 半透明オーバーレイ | ◎ lxml 注入 | △ 透明度の組合せ近似 | ◎ rgba() CSS |
| グラデーション | △ 多層化で近似 | × 非対応 → 単色多層化 | ◎ CSS gradient ネイティブ |
| 3 カラム / 2 列カード | ◎ shape を座標で配置 | ◎ shape を座標で配置 | ◎ flex / grid で柔軟 |
| 矢印フロー | ◎ `MSO_SHAPE.RIGHT_ARROW` | ◎ `rightArrow` shape | ◎ 文字 `→` + CSS 装飾 |
| 比較表 (列の強調枠) | ◎ + UNI'SON 列にオレンジ 3pt 枠 | ○ 透明矩形オーバーレイで枠装飾 | ◎ CSS で完全制御 |
| 引用カード (縦バー + 大引用符) | ◎ shape + 大フォント | ◎ Georgia 88pt | ◎ CSS |
| 絵文字アイコン (📍📱🗺) | △ カテゴリバッジに置換 | △ Unicode 図形 (◉▥◈) で代替 | ◎ そのまま表示 |
| 自由レイアウトの試行錯誤 | △ 座標を全て手計算 | △ 座標を全て手計算 | ◎ CSS flex/grid で即座に組換 |
| **PowerPoint で再編集** | ◎ テキスト・図形すべて編集可 | ◎ テキスト・図形すべて編集可 | × 画像化のため一切不可 |
| **ファイルサイズ** | 1.2 MB | 1.4 MB | 5.5 MB |

## 営業資料用途での向き不向き (今回の検証から)

| 観点 | python-pptx | pptxGenJs | Marp |
| --- | --- | --- | --- |
| 営業現場で **PowerPoint で微調整して使い回す** | ◎ 最有力 | ◎ 最有力 | × 不向き |
| **テンプレ書換型** (会社テンプレに差し込む) | ◎ 既存 .pptx 読込が強い | △ マスター定義から組む | × HTML/CSS 別世界 |
| **コードで量産** (n 社分を CSV から一括生成) | ◎ Python + pandas が刺さる | ◎ Web アプリ連携が自然 | △ Markdown 量産は可能だが画像化が重い |
| **デザイン試行錯誤の速さ** | △ 座標調整が地味に重い | △ 同上 | ◎ CSS の即時性が圧勝 |
| **見た目の最終品質** | ◎ XML 直叩きまでやれば何でも可 | ○ グラデ等の制約あり | ◎ CSS で何でも可 |
| **Claude Code との相性** | ◎ サブエージェントが Python 書くだけ | ◎ サブエージェントが JS 書くだけ | ◎ Markdown + CSS で構造が明示的 |

## 結論 (現時点の所感)

- **本部営業資料の本命は python-pptx**: 編集可・テンプレ流用・XML 直叩きで「諦める要素」が一番少ない
- **pptxGenJs はサーバ連携・量産が必要なときの代替**: Web アプリ / Slack Bot から pptx を吐く用途では JS のままで完結する利点が効く
- **Marp は「営業資料の前段ドラフト」「社内勉強会」「投影専用」に最適**: 編集の必要がない読み物 / プレゼン投影には CSS の自由度と更新速度で一番速い。**ただし営業現場で PowerPoint で開いて編集する用途には不向き**

## 詰まりどころログ (サブエージェント報告から)

- **python-pptx**: `cairosvg` 追加 install 必要 / 角丸矩形上の色帯は内側角丸を重ねないとコブが出る / 半透明は lxml で `a:alpha` 注入 / 日本語折返しでフォントを 1-2pt 落とす場面が複数
- **pptxGenJs**: グラデ非対応のため Slide 1 のグラデは 2 層マスクで近似 / 比較表のセル枠線色変更は API なし → 透明矩形オーバーレイ / Hiragino + SVG の組合せが PowerPoint 側で不安定だったのでロゴはテキスト代用
- **Marp**: Default テーマが `section` に `align-content: safe center center` を当てており全要素が垂直中央に寄ってしまう → `align-content: start !important` で根本解決 / インライン style の `background-image: url(...)` は `--allow-local-files` でも解決されない → `<img class="bg">` に書き換え / スライド単位のビジュアル検証は `marp --images png` が便利

## 本格版の再生成

```bash
cd /Users/rikutanaka/aipm_v0/Flow/202606/2026-06-02/ユニゾン社

# 方法A: サブエージェントに依頼 (Claude Code の Agent ツール)
#   「~/.claude/skills/pptx/SKILL.md と editing.md を読み、slide_spec.md と design_tokens.json と assets/unison/ を使って
#    python-pptx で deck-unison-python-pptx.pptx を生成。SVG ロゴは cairosvg で PNG 化、半透明は lxml の a:alpha 注入で表現」

# 方法B: サブエージェントに依頼
#   「~/.claude/skills/pptx/SKILL.md と pptxgenjs.md を読み、slide_spec.md/design_tokens.json/assets/unison/ を使って
#    pptxGenJs で deck-unison-pptxgenjs.pptx を生成。NODE_PATH=/opt/homebrew/lib/node_modules で実行」

# 方法C: Marp CLI 直
marp unison-deck.md --html --allow-local-files --theme-set themes/unison.css -o deck-unison-marp.html
marp unison-deck.md --pptx --allow-local-files --theme-set themes/unison.css -o deck-unison-marp.pptx
```
