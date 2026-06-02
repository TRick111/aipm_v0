# Claude Code で PowerPoint を作るときに、裏で何が動いているか

> ユニゾン社向け営業資料 (10 枚) を python-pptx と pptxGenJs の 2 経路で作ったときの、**実際に動いたモノとフロー**の解説。飯竹さんへの説明用。

---

## 0. まず全体像 (1 枚絵)

```
                ┌───────────────────────┐
                │  田中さんからの指示    │ ← インプット (人間)
                └───────────┬───────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │ メインの Claude Code エージェント   │
        │   - 指示を理解                    │
        │   - 外部情報を取りに行く          │
        │   - 共通仕様書を書く              │
        │   - サブエージェントに作業を投げる │
        └─────┬─────────────────────┬───────┘
              │                     │
              ▼                     ▼
   ┌────────────────┐    ┌─────────────────┐
   │ ① 外部ソース    │    │ ② 共通仕様書    │
   │ uni-s-on.com    │    │ slide_spec.md    │
   │ Playwright で  │    │ design_tokens    │
   │ 画像・色を取得 │    │ .json + 画像群   │
   └────────┬────────┘    └────────┬────────┘
            └──────────┬───────────┘
                       ▼
        ┌───────────────────────────────────┐
        │ ~/.claude/skills/pptx/ (1 つの公式スキル) │
        │   SKILL.md (全体指示)              │
        │   ├─ editing.md       ← Python 用 │
        │   └─ pptxgenjs.md     ← JS 用     │
        └─────┬─────────────────────┬───────┘
              │                     │
              ▼                     ▼
   ┌──────────────────┐  ┌──────────────────┐
   │ サブエージェント A │  │ サブエージェント B │
   │ (Python 担当)     │  │ (JavaScript 担当) │
   │                   │  │                   │
   │ SKILL.md +        │  │ SKILL.md +        │
   │ editing.md を読む │  │ pptxgenjs.md を   │
   │                   │  │ 読む              │
   │       ▼           │  │       ▼           │
   │ /tmp/build.py を  │  │ /tmp/build.cjs を│
   │ その場で書く      │  │ その場で書く      │
   │       ▼           │  │       ▼           │
   │ python3 で実行    │  │ node で実行       │
   └─────────┬─────────┘  └─────────┬─────────┘
             │                      │
             ▼                      ▼
   ┌──────────────────┐  ┌──────────────────┐
   │deck-unison-      │  │deck-unison-      │
   │python-pptx.pptx  │  │pptxgenjs.pptx    │
   └──────────────────┘  └──────────────────┘
              最終生成物 (.pptx)
```

田中さんの「Anthropic の pptx スキルをダウンロードして、サブエージェントが python-pptx と pptxGenJs を呼び出した」という理解は **そのとおり**。下にもう少し細かく分けて書きます。

---

## 1. 登場人物の整理

| カテゴリ | 名前 | 何者 | 場所 |
| --- | --- | --- | --- |
| **スキル (1つだけ)** | Anthropic 公式 `pptx` | LLM 向けの「pptx の作り方指示書」と低レベル部品セット。Python 用と JS 用の作法が **同じスキル内に同梱** | `~/.claude/skills/pptx/` |
| **メインエージェント** | Claude Code (このセッション) | 指示理解 / 外部情報収集 / 仕様書作成 / サブエージェント指揮 | ローカル PC |
| **サブエージェント A** | general-purpose (Python 担当) | スキルを読み、Python コードを書き、実行 | ローカル PC (別コンテキスト) |
| **サブエージェント B** | general-purpose (JS 担当) | スキルを読み、Node コードを書き、実行 | ローカル PC (別コンテキスト) |
| **外部ソース** | uni-s-on.com | ブランドカラー / フォント / 画像の取得元 | Web |
| **インプット** | 田中さんの指示 / ホームページ / 仕様書 | この 3 つから資料が組み上がる | — |
| **中間生成物** | `slide_spec.md`, `design_tokens.json`, `assets/unison/*`, `/tmp/build.*` | 最終 .pptx を作るまでの足場 | プロジェクトフォルダ + /tmp |
| **最終生成物** | `.pptx` | PowerPoint で開けるファイル | プロジェクトフォルダ |

ポイント: **「python-pptx 用スキル」「pptxGenJs 用スキル」は別物ではない**。Anthropic 公式の 1 つの `pptx` スキルの中に両方の作法が同梱されている。だから DL したのは 1 つだけ。

---

## 2. 使った CLI / API / ライブラリ一覧 (Python と JS 共通)

| 何 | 種別 | 用途 | 経路 |
| --- | --- | --- | --- |
| Playwright MCP | API (ブラウザ自動操作) | uni-s-on.com を開いて色 / フォント / 画像 URL を抽出 | メインエージェント |
| curl | CLI | 画像をローカルにダウンロード | メインエージェント |
| sips | CLI (macOS) | 画像を 1920px にリサイズ | メインエージェント |
| **Anthropic 公式 `pptx` スキル** | スキル | サブエージェントが pptx の作法を学ぶ指示書 | 両サブエージェント |
| python-pptx | Python ライブラリ | pptx の XML をオブジェクト操作で生成 | A のみ |
| python-frontmatter | Python ライブラリ | Markdown のフロントマターを剥がす | A のみ |
| cairosvg | Python ライブラリ | SVG ロゴを PNG に変換 | A のみ |
| lxml | Python ライブラリ | pptx 内部 XML を直接編集 (半透明オーバーレイ等) | A のみ |
| pptxgenjs | Node ライブラリ | pptx を宣言的 API で生成 | B のみ |
| gray-matter | Node ライブラリ | Markdown のフロントマターを剥がす | B のみ |
| markitdown | Python CLI | 生成された pptx からテキスト抽出 (検証) | メインエージェント |
| gws drive | CLI | Google Drive にフォルダ作成 / アップロード | メインエージェント |

---

# 1. Python の場合の流れ

## 1.1 サブエージェント A が受け取ったもの (インプット)

| ファイル | 場所 | 中身 |
| --- | --- | --- |
| `slide_spec.md` | `Flow/.../ユニゾン社/` | 10 スライドの**人間が書いた指示書** (タイトル / レイアウト / 配置 / コピー) |
| `design_tokens.json` | 同上 | 色 (`#7297A9` `#126D64` `#F09D01` `#404040`) / フォント (Noto Sans JP) / サイズ (13.333×7.5 inch) |
| `assets/unison/*.jpg, *.svg` | 同上 | ホームページから取った画像 (ヒーロー 7 枚, ロゴ, CTA 背景 等) |
| `~/.claude/skills/pptx/SKILL.md` + `editing.md` | スキル | pptx 作法の指示書 (Python 経路) |

## 1.2 サブエージェント A の動き (時系列)

```
Step 1  SKILL.md と editing.md を Read で読む
        └─ 「Anthropic Cream の色配分は…」「python-pptx でテンプレを編集する手順は…」
            などの方針を学習

Step 2  slide_spec.md を読む
        └─ 10 スライドのレイアウト・コンテンツを把握

Step 3  design_tokens.json を読む
        └─ 色・フォント・サイズの定数を把握

Step 4  assets/unison/ をリストして使える画像を確認
        └─ SVG ロゴが含まれていることを発見

Step 5  詰まりに対処
        ├─ SVG は python-pptx で直接読めない
        │   → pip install cairosvg で SVG → PNG 変換
        ├─ 半透明オーバーレイは python-pptx の API では不可
        │   → lxml で <a:alpha> を XML に直接注入
        └─ 角丸の上に色帯 → 内側角丸を重ねる工夫

Step 6  /tmp/build_unison_deck.py を一時的に書く (約 600 行)
        └─ Presentation() を作り、10 スライド分の shape / text / image を配置

Step 7  python3 /tmp/build_unison_deck.py で実行
        └─ pptx ファイルが生成される

Step 8  生成物を検証
        ├─ python-pptx で開き直して枚数 10 を確認
        └─ LibreOffice で PDF 化 → 画像化 → 目視チェック

Step 9  /tmp/build_unison_deck.py を削除 (永続化しない)
```

## 1.3 中間生成物 (Python 経路)

| ファイル | 性質 | 残った? |
| --- | --- | --- |
| `/tmp/build_unison_deck.py` | サブエージェントがその場で書いた Python コード | ❌ 実行後に削除 |
| `/tmp/logo-white.png` | cairosvg で変換した PNG ロゴ | ❌ 削除 |
| `/tmp/deck-unison-python-pptx.pdf` | 検証用 PDF (LibreOffice 経由) | ❌ 削除 |
| `/tmp/unison-slide-*.jpg` | 検証用にスライド毎の JPG | ❌ 削除 |

→ **プロジェクトフォルダには `.pptx` だけ残る**。これが「永続スクリプトを作らない運用」の意味。

## 1.4 最終生成物 (Python 経路)

| ファイル | サイズ | 中身 |
| --- | --- | --- |
| `deck-unison-python-pptx.pptx` | 1.2 MB | テキスト編集可な PowerPoint。10 枚 |

---

# 2. JavaScript の場合の流れ

## 2.1 サブエージェント B が受け取ったもの (インプット)

Python とまったく同じ:
- `slide_spec.md`
- `design_tokens.json`
- `assets/unison/`
- `~/.claude/skills/pptx/SKILL.md` + **`pptxgenjs.md`** (Python の `editing.md` に相当する JS 用ガイド)

→ **共通仕様書を 2 つのサブエージェントが同じように読み、それぞれの言語で実装**するのが今回の構造。

## 2.2 サブエージェント B の動き (時系列)

```
Step 1  SKILL.md と pptxgenjs.md を Read で読む
        └─ 「色は # を付けない hex」「shadow オブジェクト再利用禁止」
            などの pptxGenJs 固有の罠を学習

Step 2  slide_spec.md を読む (Python と同じ)
Step 3  design_tokens.json を読む (同上)
Step 4  assets/unison/ をリスト (同上)

Step 5  詰まりに対処
        ├─ pptxgenjs はグラデーション非対応
        │   → 単色の 2 層マスクで近似
        ├─ SVG ロゴが PowerPoint 側で不安定
        │   → テキスト「UNI'SON」(white, 24pt bold) で代用
        ├─ 比較表のセル枠線色変更 API なし
        │   → 透明矩形を上に重ねて枠装飾
        └─ Hex に # を付けない (pptxgenjs ルール)

Step 6  /tmp/build.cjs を一時的に書く (約 500 行)
        └─ pres.defineSlideMaster() でフッター共通化
            10 スライド分の addText / addImage / addShape / addTable

Step 7  NODE_PATH=/opt/homebrew/lib/node_modules node /tmp/build.cjs で実行
        └─ グローバルの pptxgenjs を解決して pptx を生成

Step 8  生成物を検証
        ├─ python-pptx で開き直して枚数 10 を確認
        └─ markitdown で本文抽出して順序チェック

Step 9  /tmp/build.cjs を削除
        └─ ユニゾン社フォルダに node_modules / package.json が残らないか最終チェック
```

## 2.3 中間生成物 (JS 経路)

| ファイル | 性質 | 残った? |
| --- | --- | --- |
| `/tmp/build.cjs` | サブエージェントがその場で書いた Node コード | ❌ 実行後に削除 |
| (オプション) `package.json` / `node_modules` | local install した場合 | ❌ 今回はグローバル install を NODE_PATH で参照したので作らなかった |

## 2.4 最終生成物 (JS 経路)

| ファイル | サイズ | 中身 |
| --- | --- | --- |
| `deck-unison-pptxgenjs.pptx` | 1.4 MB | テキスト編集可な PowerPoint。10 枚 |

---

# 3. 2 つの経路の「共通」と「個別」

| | Python 経路 | JS 経路 |
| --- | --- | --- |
| インプットの共通仕様書 (`slide_spec.md`) | ✅ 同じ | ✅ 同じ |
| 共通デザイントークン (`design_tokens.json`) | ✅ 同じ | ✅ 同じ |
| 画像 (`assets/unison/`) | ✅ 同じ | ✅ 同じ |
| Anthropic 公式 `pptx` スキル | ✅ 同じスキル | ✅ 同じスキル |
| 読んだガイド md | `editing.md` (Python 用) | `pptxgenjs.md` (JS 用) |
| 使ったライブラリ | python-pptx, cairosvg, lxml | pptxgenjs |
| 一時コードの場所 | `/tmp/*.py` | `/tmp/*.cjs` |
| 実行コマンド | `python3` | `NODE_PATH=... node` |
| 最終 .pptx | 1.2 MB | 1.4 MB |

**ポイント**: 共通仕様書を 1 本書いておけば、**サブエージェントを並列で 2 つ起動するだけで両方の .pptx が同時にできる**。仕様書を変更すれば両方に伝播。これがスキル運用の威力。

---

# 4. このプロジェクト全体の作業フロー (時系列)

```
1. 田中さん:「3 方法 (python-pptx / pptxGenJs / Marp) を比較したい」
       ↓
2. メインエージェント: 公式 pptx スキルをクローン
       git clone .../anthropics/skills → ~/.claude/skills/pptx/
       ↓
3. ランタイムをインストール
       pip install python-pptx, cairosvg, frontmatter, markitdown
       npm i -g pptxgenjs gray-matter
       ↓
4. 田中さん:「もっと本格的な営業資料で。多店舗 FC 本部向け。
              ホームページから画像と色を取って」
       ↓
5. メインエージェント: Playwright で uni-s-on.com を開く
       ├─ 色を抽出: #7297A9 / #126D64 / #F09D01
       ├─ フォント: Noto Sans JP
       └─ 画像 URL リストを作成
       ↓
6. メインエージェント: 画像を curl でダウンロード → sips でリサイズ
       → assets/unison/
       ↓
7. メインエージェント: design_tokens.json と slide_spec.md を書く
       ├─ slide_spec.md: 10 スライドのレイアウト + コピー
       └─ design_tokens.json: 色 / フォント / サイズの定数
       ↓
8. メインエージェント: サブエージェント 2 つを並列起動
       ├─ A: 「python-pptx で deck-unison-python-pptx.pptx を作って」
       └─ B: 「pptxGenJs で deck-unison-pptxgenjs.pptx を作って」
       ↓
9. サブエージェント A / B が並行して動く
       ├─ A: editing.md を読む → /tmp/build.py 書く → 実行 → 削除
       └─ B: pptxgenjs.md を読む → /tmp/build.cjs 書く → 実行 → 削除
       ↓
10. メインエージェント: 生成された 2 つの .pptx を検証
       ├─ python-pptx で開き直して枚数確認
       └─ markitdown で本文一致確認
       ↓
11. メインエージェント: README に「実装できた / 諦めた要素」を表で記録
       ↓
12. 田中さん:「Drive にアップして」
       ↓
13. メインエージェント: gws drive CLI で
       ├─ "Uni'son社" フォルダ作成
       ├─ "PPT例" サブフォルダ作成
       └─ 2 つの .pptx をアップロード
```

ステップ 5 〜 9 のところで、**人間が書いた中間生成物 (slide_spec.md / design_tokens.json) と、サブエージェントが内部的に書いた一時コードを区別する**のが重要。前者は再現性のために残し、後者は捨てる、というのが Anthropic 公式スキルの運用作法。

---

# 5. 飯竹さんへの説明用 ひとことサマリ

- **スキル = 「LLM への作り方ガイド」+「低レベル部品」のセット**。完成済みアプリではない
- **サブエージェント = スキルを読んで、その場でコードを書いて実行する独立した LLM**。終わったらコードは捨てる
- **共通仕様書 (Markdown + JSON) を 1 本書く**だけで、2 言語の .pptx が並行生成できる
- **人間が書いたファイルは残し、LLM が一時的に書いたコードは捨てる**のが運用のキモ

---

## 付録: ファイル配置 (作業後)

```
Flow/202606/2026-06-02/ユニゾン社/
├── slide_spec.md                       ← 仕様書 (人間が書く)
├── design_tokens.json                  ← 色 / フォント (人間が書く)
├── assets/unison/                      ← 画像 (外部ソースから DL)
├── deck-unison-python-pptx.pptx        ← 最終生成物 (Python 経路)
├── deck-unison-pptxgenjs.pptx          ← 最終生成物 (JS 経路)
├── README.md                           ← 経緯と所見
├── pptx_python_vs_js.md                ← Python と JS の違い比較
└── スライド生成フロー_python_vs_js.md   ← この資料

~/.claude/skills/pptx/                  ← Anthropic 公式スキル (1 度だけ DL)
├── SKILL.md
├── editing.md                          ← Python 用ガイド
├── pptxgenjs.md                        ← JS 用ガイド
└── scripts/                            ← 低レベル部品
```
