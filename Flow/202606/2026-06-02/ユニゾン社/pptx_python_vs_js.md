# python-pptx と pptxGenJs の違い (と同じ点)

> Claude Code から PowerPoint を生成する 2 方法の比較。検証日: 2026-06-02 / ユニゾン社 多店舗 FC 本部向け営業資料 10 枚で実証。

## 0. 使ったスキルについて

**ダウンロードしたのは Anthropic 公式 `pptx` スキル 1 つだけ**。`~/.claude/skills/pptx/` に配置されており、内部に以下が同梱:

```
~/.claude/skills/pptx/
├── SKILL.md           ← 全体指示書 (LLM 向け、デザイン原則も)
├── editing.md         ← python-pptx 寄りの XML 編集ガイド
├── pptxgenjs.md       ← pptxGenJs 用ガイド
└── scripts/           ← pack / unpack / validate / add_slide 等の低レベル共通部品
    └── office/        ← OOXML 操作の補助
```

→ 「python-pptx 用スキル」「pptxGenJs 用スキル」が**別々にあるわけではない**。**同じスキルが両方の作法を内包**している。

**今回の使われ方**:
- サブエージェント A (python-pptx) → `SKILL.md` + `editing.md` を読み、その場で Python コードを書いて実行
- サブエージェント B (pptxGenJs) → `SKILL.md` + `pptxgenjs.md` を読み、その場で Node コードを書いて実行
- スキルが「完成済みコンバーター」を提供したわけではなく、**LLM が指示書を読んでコードを書く**運用

---

## 1. 同じ点 — そもそも .pptx の仕組みは同一

`.pptx` は **ZIP ファイルで、中身は XML** (国際標準 ECMA-376 / Office Open XML)。試しに unzip するとこんな構造:

```
deck.pptx (実体は ZIP)
├── [Content_Types].xml
├── ppt/
│   ├── presentation.xml          ← スライド一覧と全体設定
│   ├── slides/slide1.xml         ← スライド 1 の全内容 (XML)
│   ├── slides/slide2.xml
│   ├── slideLayouts/...          ← レイアウトテンプレ
│   ├── slideMasters/...          ← マスタースライド
│   ├── theme/theme1.xml          ← 色とフォント
│   └── media/image1.jpg          ← 埋込画像 (バイナリ)
└── _rels/                         ← 内部参照リンク
```

**python-pptx も pptxGenJs も、究極的にはこの XML を組み立てて ZIP に固めるラッパー**。生成物に本質的な差は出ない。

```
仕様 → ライブラリ呼び出し → XML 文字列生成 → ZIP に詰める → .pptx
                ↑
        ここが Python か JS かの違いだけ
```

---

## 2. 違う点

### 2.1 API の書き味

**python-pptx** — オブジェクトを段階的に操作する Pythonic スタイル

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation("template.pptx")
slide = prs.slides.add_slide(prs.slide_layouts[5])
tx = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(2))
p = tx.text_frame.paragraphs[0]
p.text = "見出し"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = RGBColor(0x12, 0x6D, 0x64)
```

**pptxGenJs** — オプションをまとめて渡す宣言的スタイル (JSON 親和)

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const s = pres.addSlide();
s.addText("見出し", {
  x: 1, y: 1, w: 8, h: 2,
  fontSize: 28, bold: true, color: "126D64"
});
pres.writeFile({ fileName: "deck.pptx" });
```

→ JS の方が記述量は少ない。Python は属性を 1 つずつ触れる分、**細かい制御で勝つ**。

### 2.2 既存テンプレ .pptx の扱い

| 機能 | python-pptx | pptxGenJs |
| --- | --- | --- |
| 既存 .pptx を **読み込んで編集** | ◎ 非常に強い (XML 直叩き可) | △ 弱い (基本ゼロから生成) |
| 既存テンプレに **差し込み** | ◎ レイアウト・マスタースライドを継承可 | △ マスター定義はコードから作るのが基本 |
| ゼロから生成 | ◎ | ◎ |

**コーポレートテンプレ .pptx に毎週データを流し込む** ような業務利用は、python-pptx が圧倒的に楽。

### 2.3 詰まったときの逃げ道の深さ

今回の実装で実際に発生した詰まりと、それぞれの対処:

| 詰まり | python-pptx の対処 | pptxGenJs の対処 |
| --- | --- | --- |
| 半透明オーバーレイ | ◎ `lxml` で `<a:alpha>` を XML に直接注入 | △ 透明度の重ね合わせで近似 |
| グラデーション背景 | △ 多層レイヤーで近似 | × 非対応、単色 2 層マスクで近似 |
| SVG ロゴ | ○ `cairosvg` で PNG 化して埋込 | △ テキスト代用が無難 |
| 比較表のセル枠線色 | ○ XML 編集で対応 | △ 透明矩形オーバーレイで装飾 |
| 角丸矩形の上に色帯を載せる | ○ 内側角丸の重ね方を XML で調整 | ○ 同様の重ね方が可能 |

→ **どちらも本質的には XML を吐いているので「やれば全部できる」が、深い修正に行ったときに XML へ降りられるのは python-pptx の方が自然**。

### 2.4 エコシステムと周辺ライブラリ

| | python-pptx | pptxGenJs |
| --- | --- | --- |
| 初版 | 2014 年 | 2015 年 |
| GitHub Stars | 約 2.7k | 約 2.5k |
| **データ連携の厚み** | ◎ pandas / numpy / matplotlib / Pillow / openpyxl | ○ Node エコシステム (express, csv-parser, sharp 等) |
| **画像加工** | ◎ Pillow が同言語で完結 | ○ sharp などを併用 |
| **グラフ・表** | ◎ matplotlib で PNG 化して埋込 / 内蔵 chart 対応 | ○ chart.js 等の併用 |
| **ブラウザで動くか** | × Python ランタイム必須 | ◎ React / Vue でも動く |
| **サーバサイド自動化** | ◎ cron + Python が王道 | ◎ Node.js API サーバが自然 |
| **競合ライブラリ** | Aspose.Slides (商用), Spire.Presentation (商用), python-docx-templates | (実質 pptxgenjs 一択) |
| Stack Overflow 等の解説の厚み | ◎ 業務利用の歴が長く豊富 | ○ 増加中だが Python ほどではない |

### 2.5 デプロイ・運用環境

| 環境 | python-pptx | pptxGenJs |
| --- | --- | --- |
| ローカル PC で 1 回叩く | ◎ | ◎ |
| **社内のデータ分析環境 (Jupyter, pandas)** | ◎ そのまま使える | △ Python から呼ぶのは面倒 |
| **Web アプリで「ダウンロード」ボタン** | △ サーバに Python 環境必要 | ◎ Node 1 つで完結 / ブラウザ生成も可 |
| **Slack / Discord Bot から返す** | ○ | ◎ Bot 本体が Node なら同一プロセス |
| **GitHub Actions 等の CI で量産** | ◎ | ◎ |

---

## 3. 使い分けの判断軸

```
┌─────────────────────────────────────────────────────┐
│ 既存の会社テンプレ .pptx を読み込んで差し込みたい？  │
│   YES → python-pptx (一択)                          │
│   NO  → 下へ                                        │
├─────────────────────────────────────────────────────┤
│ 隣にあるデータ環境は？                              │
│   Excel / CSV / pandas / DB → python-pptx           │
│   Web アプリ / Node サーバ / Bot → pptxGenJs        │
├─────────────────────────────────────────────────────┤
│ ブラウザで生成したい？                              │
│   YES → pptxGenJs (一択)                            │
│   NO  → どちらでも (好きな言語で)                   │
├─────────────────────────────────────────────────────┤
│ 最終的にピクセルパーフェクトに追い込みたい？        │
│   YES → python-pptx (XML 直叩きの逃げ道が深い)      │
│   NO  → どちらでも                                  │
└─────────────────────────────────────────────────────┘
```

---

## 4. まとめ

1. **生成物 (.pptx) の品質に本質的な差はない** — 両者とも同じ XML を書き出すラッパー
2. **「Python vs JS どっちが書きやすいか」より、「データの隣にいるのはどっちか」で選ぶ**
3. **既存テンプレ .pptx を扱う案件は迷わず python-pptx** — pptxGenJs の苦手分野
4. **Web アプリ / ブラウザ / Bot 連携は pptxGenJs** — 同一ランタイムで完結する利点が効く
5. **AI に書かせる (Claude Code 経由) なら両者互角** — 違いは詰まったときの逃げ道の深さ
6. **「python-pptx 用スキル」「pptxGenJs 用スキル」は別物ではない** — Anthropic 公式 `pptx` スキル 1 つが両方をカバー

---

## 5. 今回の実物の出力 (参考リンク)

| 方法 | ローカル | Google Drive |
| --- | --- | --- |
| python-pptx | [deck-unison-python-pptx.pptx](deck-unison-python-pptx.pptx) (1.2 MB) | [開く](https://docs.google.com/presentation/d/1TkGGQYW4zI0AR6NM9PXr6yOS0dDFPOKH/edit) |
| pptxGenJs | [deck-unison-pptxgenjs.pptx](deck-unison-pptxgenjs.pptx) (1.4 MB) | [開く](https://docs.google.com/presentation/d/1YaY8toVx4AktEvqSwhtg3eszvrI06Z6m/edit) |

両者を実際に開き比べると、**ぱっと見の品質差はほとんどないこと**が確認できる。
