# 週報・月報 PDF 出力 — 3パターンの原理と比較

作成日: 2026-05-23
最終更新: 2026-05-23（採用結論を追記）
対象: RestaurantAILab Dashboard (Next.js 14, App Router)
背景: 既存の週報・月報は 16:9 スライドデッキ形式の HTML として Vercel Blob に保存され、iframe で表示中。これを PDF としてダウンロードする機能を3パターン試作・比較した。

---

## 採用結論: Pattern A（window.print() + 印刷用CSS）

3パターンを実装・検証した結果、**Pattern A を本番採用**とした。

### 採用理由

1. **動作が確実**: 3パターンの中で唯一、出力 PDF が綺麗に整っていた（スライド比率 297×167mm のカスタム用紙に1スライド=1ページぴったり）
2. **サーバー負荷ゼロ**: ブラウザの印刷エンジンに丸投げするため、Vercel Function や Chromium バイナリの運用が不要
3. **追加依存ゼロ**: npm パッケージを増やさず、bundle size にも影響なし
4. **出力品質が高い**: ブラウザ印刷経由なので Plotly チャートも自然にレンダリングされる（B のラスタライズより遥かに綺麗）
5. **インフラ要件ゼロ**: Vercel の memory / maxDuration 設定や `@sparticuz/chromium` の保守が不要

### 不採用となった理由

- **Pattern B (html2canvas + jsPDF)**: Plotly チャートのラスタライズ品質が低く、文字や図がぼやける。クライアントメインスレッドを長時間ブロックする。Next.js dev での chunk loading バグもあり相性が悪い。
- **Pattern C (Puppeteer)**: 動作はするが、サーバー側で Chromium を毎回起動するコストと運用負荷が割に合わない。Plotly の品質メリットは Pattern A でも十分達成できたため、わざわざ複雑なインフラを抱える理由がなくなった。

### トレードオフの許容

- ユーザー操作が 2 ステップ（ボタン → 印刷ダイアログで「PDFとして保存」）になる点は許容
- 用紙サイズが「カスタム 297×167mm」になるが、ブラウザの印刷ダイアログでは自動選択される

---

---

## 前提: レポート HTML の構造

```html
<div class="slide">  <!-- width: 1280px; min-height: 720px (16:9 固定) -->
  <div class="slide-header">...</div>
  <div class="slide-body">
    <div class="js-plotly-plot">...</div>  <!-- Plotly チャート -->
  </div>
</div>
<div class="slide">...</div>  <!-- 2枚目 -->
<div class="slide">...</div>  <!-- 3枚目 -->
```

- スライド毎に `page-break-after: always` が CSS に書かれている
- Plotly.js で動的に SVG/Canvas のチャートを描画
- 日本語フォントは Web フォント (Noto Sans JP) を使用
- D3.js も読み込まれる（追加可視化用）

---

## Pattern A: `window.print()` + 印刷用 CSS

### 原理

ブラウザ標準の印刷機能 (`window.print()`) を利用する。レポート HTML に `@media print` の追加 CSS を注入し、ブラウザが「印刷プレビュー」または「PDFとして保存」を経由してPDFを生成する。**PDF生成ロジックはブラウザの内部実装に丸投げ**する形になる。

### データフロー

```
[ボタンクリック]
    ↓
window.open('/api/.../printable')         ← 新タブを開く
    ↓
GET /api/weekly-reports/{id}/printable     ← Next.js API ルート
    ↓
1. Blob から元 HTML をフェッチ
2. injectPrintCss() で <head> 内に印刷用 <style> を注入
3. text/html として返却
    ↓
[新タブで HTML レンダリング]
    ↓
setTimeout(window.print, 1500)             ← Plotly 描画待ち
    ↓
[ブラウザの印刷ダイアログ]
    ↓
ユーザーが「PDFとして保存」を選択
    ↓
[OS の PDF 仮想プリンタが PDF を生成]
```

### 注入する CSS の要点

```css
@page {
  size: 297mm 167.06mm;   /* スライド 1280×720 と同アスペクト比 */
  margin: 0;
}
@media print {
  .slide {
    width: 1280px !important;
    height: 720px !important;
    zoom: 0.881;           /* 1280px を 297mm (≈ 1122px) に縮小 */
    page-break-after: always !important;
    break-after: page !important;
  }
}
```

`@page` でブラウザに渡す用紙サイズをカスタム指定し、CSS の `zoom` でスライドを物理サイズへ縮小する。スライドの 16:9 アスペクト比に合うカスタム用紙サイズにすることで、各ページ 1 スライドぴったりに収まり、A4 縦印刷で生じる空白を解消できる。

### 長所
- **追加依存ゼロ**。npm に新規パッケージを追加しない
- **サーバー負荷ゼロ**。クライアント（=ブラウザ）が全部やる
- **品質はブラウザの印刷エンジンが保証**。Plotly チャートも自然に描画される

### 短所
- **ユーザー操作が 2 ステップ**: ボタン → 印刷ダイアログ → PDFとして保存
- **ポップアップブロッカー**で新タブが開かないことがある
- **OS / ブラウザによって UI が異なる**（Chrome / Safari / Firefox / Edge で操作が違う）
- **タイミング依存**: Plotly の描画完了を `setTimeout(1500ms)` で待っているだけなので、巨大なレポートだとチャートが空のまま印刷されるリスク

### 主要ファイル
| ファイル | 役割 |
|---|---|
| `lib/utils/injectPrintCss.ts` | 印刷用 CSS を HTML に注入するヘルパー |
| `app/api/weekly-reports/[id]/printable/route.ts` | Blob から HTML を取得し CSS 注入して返す |
| `app/api/monthly-reports/[id]/printable/route.ts` | 同上（月報） |

---

## Pattern B: `html2canvas` + `jsPDF`（クライアントサイドラスタライズ）

### 原理

1. **`html2canvas`** が DOM ツリーを走査し、`<canvas>` 要素にピクセル単位でラスタライズ（=画像化）する
2. その canvas を PNG として data URL 化
3. **`jsPDF`** で空の PDF 文書を生成し、PNG 画像を `addImage` で各 A4 ページに貼り付ける
4. ブラウザに直接ダウンロードさせる

**HTML をベクトルではなく "画像化" して PDF に貼る** アプローチ。

### データフロー

```
[ボタンクリック]
    ↓
iframe.contentDocument を取得
    ↓
既存の transform: scale(...) を一時的に解除  ← 自然サイズで描画させるため
    ↓
html2canvas(doc.body, { scale: 2, useCORS: true })
    ↓
[DOM を走査して <canvas> にラスタライズ]
    ↓
canvas.toDataURL('image/png')             ← 大きな PNG (data URL)
    ↓
new jsPDF({ format: 'a4' })
    ↓
A4 ページの高さでスライス → addImage を繰り返してマルチページ化
    ↓
pdf.save('weekly-report-{id}.pdf')        ← ブラウザのダウンロードトリガ
```

### マルチページ化のテクニック

A4 縦 1 ページに収まらない長い canvas は、以下の手順でページ毎にスライスする:

```typescript
const pageHeightPx = Math.floor(pageHeightMm * canvas.width / pageWidthMm);
let renderedHeight = 0;
while (renderedHeight < canvas.height) {
  const sliceCanvas = document.createElement('canvas');
  sliceCanvas.width = canvas.width;
  sliceCanvas.height = Math.min(pageHeightPx, canvas.height - renderedHeight);
  sliceCanvas.getContext('2d')!.drawImage(
    canvas, 0, renderedHeight, canvas.width, sliceCanvas.height,
    0, 0, canvas.width, sliceCanvas.height
  );
  pdf.addPage();
  pdf.addImage(sliceCanvas.toDataURL('image/png'), ...);
  renderedHeight += sliceCanvas.height;
}
```

### 長所
- **完全にクライアントで完結**。サーバーに API ルートさえ不要
- **ユーザー操作が 1 ステップ**（ボタン → DL）
- **オフラインでも動く**（理論上）

### 短所
- **画質が劣化**: SVG / Canvas をビットマップに変換するため、文字や図がスケールでぼやける
- **Plotly チャートの再現性が低い**: 内部で WebGL や 動的 SVG を使う部分は html2canvas が正確に画像化できない
- **メインスレッドをブロック**: 大きな DOM のラスタライズは数秒〜十数秒同期処理
- **クロスオリジン画像が制限される**: `useCORS: true` でも CORS 未対応のリソースは描画されない
- **フォント読み込み完了を待たないと、差し替え前のフォントでキャプチャされる**
- **bundle size**: html2canvas (~200KB gz) + jspdf (~150KB gz)

### Next.js 特有のハマりどころ

`dynamic import('html2canvas')` を使うと、Next.js dev mode の webpack が `_next/undefined.js` という壊れた chunk URL を生成することがある。**静的 import (`import html2canvas from 'html2canvas'`)** に変更することで回避できる（`'use client'` ページなので問題なし）。

### 主要ファイル
| ファイル | 役割 |
|---|---|
| `lib/hooks/useIframePdfDownload.ts` | iframe をキャプチャして PDF を保存するフック |
| `components/PdfDownloadButton.tsx` | spinner / disabled 対応のボタン |

---

## Pattern C: Puppeteer（サーバーサイド Headless Chrome）

### 原理

サーバー側で **実際の Chrome ブラウザをヘッドレスで起動** し、レポート HTML をその中でレンダリングしてから `page.pdf()` API で PDF を生成する。Chrome 自体に PDF 出力機能が組み込まれているため、最も忠実な PDF が得られる。

実は Chrome の「PDFとして保存」と同じエンジンを使っており、Pattern A の遠隔自動化版と捉えることもできる。

### データフロー

```
[ボタンクリック]
    ↓
GET /api/weekly-reports/{id}/pdf           ← Next.js API ルート (Node.js runtime)
    ↓
puppeteer.launch()                          ← Headless Chrome を起動
    ↓
ローカル: 通常の `puppeteer` パッケージから Chromium バイナリ
本番:    `@sparticuz/chromium` + `puppeteer-core` (Vercel Functions 用に圧縮済み Chromium)
    ↓
page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 2 })
    ↓
page.setExtraHTTPHeaders({ cookie: req.cookie })   ← 認証 cookie を転送
    ↓
page.goto('/api/.../html', { waitUntil: 'networkidle0' })
    ↓
[Chrome 内でレポートが完全レンダリングされる
  - Plotly チャート描画
  - D3 補助描画
  - Web フォント読み込み
  - その他の async リソース]
    ↓
page.waitForFunction(() => window.Plotly !== undefined)   ← Plotly ロード待ち
await sleep(800ms)                                        ← 描画完了の余韻
    ↓
page.pdf({
  width: '297mm', height: '167.06mm',     ← スライドアスペクト比
  printBackground: true,
  margin: { top: 0, ... }
})
    ↓
[Chrome 内蔵の PDF エンジンが Buffer を返す]
    ↓
Response (Content-Type: application/pdf, Content-Disposition: attachment)
    ↓
[ブラウザがファイルとして保存]
```

### ローカル vs Vercel 切り替え

```typescript
const isServerless = Boolean(process.env.VERCEL || process.env.AWS_LAMBDA_FUNCTION_NAME);
if (isServerless) {
  // Vercel/Lambda: @sparticuz/chromium は AWS Lambda のサイズ制限に収まるよう
  // Chromium バイナリを brotli 圧縮・依存削減した特別版
  const chromium = (await import('@sparticuz/chromium')).default;
  const puppeteer = await import('puppeteer-core');
  browser = await puppeteer.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: true,
  });
} else {
  // ローカル: フル puppeteer (devDependency) を使う
  // eval('require') で Webpack の静的解析を回避し本番 bundle に含めない
  const puppeteerFull = eval('require')('puppeteer');
  browser = await puppeteerFull.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
}
```

### 長所
- **品質が圧倒的**: 実ブラウザでレンダリングするため、Plotly チャート・カスタムフォント・CSS が完璧に再現される
- **ユーザー操作が 1 ステップ**: ボタン → ファイルがDL
- **HTML/CSS をそのまま使える**: 既存の `@media print` ルールも効く
- **改ページ・ヘッダー/フッターを完全制御**: PDF メタデータも自由
- **クライアントは軽い**: 重い処理はサーバー側

### 短所
- **インフラ依存**: Vercel の Function 設定（memory ≥ 1024MB, maxDuration ≥ 60s, Fluid Compute）が必要
- **コールドスタート**: `@sparticuz/chromium` の解凍に 1〜3秒の追加レイテンシ
- **初回セットアップ**: ローカル開発では `puppeteer browsers install chrome` が必要
- **依存サイズ**: `puppeteer-core` + `@sparticuz/chromium` = 約 50MB（Vercel deploy 時の zip）
- **生成コスト**: 1リクエスト = 1 Chromium 起動。同時並行で殺到するとリソースを食う（→ Vercel Blob にキャッシュする運用がおすすめ）

### 認証の扱い

`/api/.../html` は認証 cookie が必要なエンドポイントなので、Puppeteer が page.goto する前に
リクエスト元の cookie をそのまま転送する:

```typescript
const cookie = req.headers.get('cookie');
if (cookie) await page.setExtraHTTPHeaders({ cookie });
```

これによりユーザーが認可されている範囲でのみ PDF 化される。

### 主要ファイル
| ファイル | 役割 |
|---|---|
| `lib/pdf/renderPdf.ts` | Puppeteer を起動して URL を PDF Buffer に変換する共通関数 |
| `app/api/weekly-reports/[id]/pdf/route.ts` | 週報 PDF ルート（認証 + cookie 転送 + renderPdf 呼び出し） |
| `app/api/monthly-reports/[id]/pdf/route.ts` | 同上（月報） |
| `vercel.json` | Function ごとに memory=1024MB, maxDuration=60s を指定 |

---

## 比較サマリ

| 観点 | A: window.print | B: html2canvas+jsPDF | C: Puppeteer |
|---|---|---|---|
| **PDF 品質** | ◎ (ブラウザ印刷エンジン) | △ (ラスタライズ画像) | ◎ (Headless Chrome) |
| **Plotly チャート再現性** | ◎ | × (ぼやけ・崩れあり) | ◎ |
| **ユーザー操作** | 2ステップ | 1ステップ | 1ステップ |
| **追加依存** | なし | html2canvas, jspdf (~350KB gz) | puppeteer-core, @sparticuz/chromium (~50MB) |
| **サーバー負荷** | なし | なし | あり (1req=1Chromium) |
| **クライアント負荷** | 低 | 高 (数秒〜十数秒ブロック) | 低 |
| **コールドスタート影響** | なし | なし | 1〜3秒 |
| **Vercel デプロイ設定** | 不要 | 不要 | memory, maxDuration 設定必須 |
| **オフライン動作** | × (要 print dialog) | ◯ (理論上) | × |
| **失敗時のリトライ性** | ユーザー任せ | エラーUI | サーバーログ・キャッシュ可 |
| **キャッシュ戦略** | 不要 | 不要 | Vercel Blob に生成済み PDF を保存可 |

---

## 採用判断のおすすめ

このプロジェクトの場合 → **Pattern C (Puppeteer)** が本命。

理由:
1. レポートに **Plotly チャートが多用**されており、ラスタライズ系（B）は品質を担保できない
2. 顧客（飲食店）に PDF を渡す業務用途のため、**印刷ダイアログを経由しない 1 ステップ DL** が望ましい
3. Vercel Fluid Compute 環境なので **Headless Chrome の運用コストが現実的**
4. 同じ週/月の PDF は内容が変わらないので、**初回生成 → Vercel Blob にキャッシュ** すれば 2 回目以降は無料

ただし C はインフラ設定が必要なので、**プロトタイプ段階や Plotly を使わないレポートなら A も十分** 戦力になる。B はこのプロジェクトには不向き（Plotly との相性が悪い）。

---

## 今後の拡張案

### Pattern C のキャッシュ化

```typescript
// 擬似コード
const cacheKey = `${reportId}.pdf`;
const cached = await blob.head(cacheKey);
if (cached) return Response.redirect(cached.url);

const pdf = await renderPdfFromUrl(htmlUrl, cookie);
await blob.put(cacheKey, pdf, { access: 'public' });
return new Response(pdf, { headers: { 'Content-Type': 'application/pdf' } });
```

レポートは月次・週次で確定したら不変なので、Blob にキャッシュすると Puppeteer 起動コストが完全に消える。

### バッチ生成 (Vercel Cron)

毎週月曜 0:00 に Cron で全店舗の前週分 PDF を一括生成 → Blob にキャッシュ。これによりユーザーがダウンロードする瞬間は常にキャッシュヒットで即時 DL になる。

### PDF にヘッダー/フッター追加

Puppeteer の `page.pdf({ displayHeaderFooter: true, headerTemplate, footerTemplate })` で店舗名・期間・ページ番号などを各ページに付与できる。

---

## 動作確認用 worktree（2026-05-23 時点）

3パターンとも独立した git worktree + feature ブランチで稼働中:

| Pattern | ブランチ | dev サーバー |
|---|---|---|
| A | `feature/pdf-pattern-a` | http://localhost:3010 |
| B | `feature/pdf-pattern-b` | http://localhost:3011 |
| C | `feature/pdf-pattern-c` | http://localhost:3012 |

サンプル URL（BAR FIVE Arrows / weekly 2026-W08）:
```
http://localhost:3010/store/bfa-001/weekly-reports/527388dc-792a-4d06-a695-25085013cbc0
http://localhost:3011/store/bfa-001/weekly-reports/527388dc-792a-4d06-a695-25085013cbc0
http://localhost:3012/store/bfa-001/weekly-reports/527388dc-792a-4d06-a695-25085013cbc0
```
