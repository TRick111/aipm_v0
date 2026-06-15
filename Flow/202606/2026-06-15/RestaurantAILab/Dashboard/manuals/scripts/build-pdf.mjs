// build-pdf.mjs — 飲食店向け_操作マニュアル_v1.md → _v1.pdf
//
// 実行方法:
//   node /Users/rikutanaka/aipm_v0/Flow/202606/2026-06-15/RestaurantAILab/Dashboard/manuals/scripts/build-pdf.mjs
//
// 依存: Dashboard リポ（/Users/rikutanaka/RestaurantAILab/Dashboard）の node_modules に
//   marked / playwright がインストール済みであること。
//   再インストール: cd /Users/rikutanaka/RestaurantAILab/Dashboard && pnpm install
//
// 実装メモ: スクリプトは Dashboard リポの外にあるため、node_modules への
//   絶対パス（file:// URL）を使って ESM import している。

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const DASHBOARD_NODE_MODULES = '/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules';
const { marked } = await import(`file://${DASHBOARD_NODE_MODULES}/marked/lib/marked.esm.js`);
const { chromium } = await import(`file://${DASHBOARD_NODE_MODULES}/playwright/index.mjs`);

const MANUAL_DIR = '/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-15/RestaurantAILab/Dashboard/manuals';
const MD_PATH = resolve(MANUAL_DIR, '飲食店向け_操作マニュアル_v1.md');
const HTML_PATH = resolve(MANUAL_DIR, '飲食店向け_操作マニュアル_v1.html');
const PDF_PATH = resolve(MANUAL_DIR, '飲食店向け_操作マニュアル_v1.pdf');

const md = readFileSync(MD_PATH, 'utf8');
const body = marked.parse(md);

const html = `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>シェフズルーム ダッシュボード 操作マニュアル v1</title>
<style>
  @page { size: A4; margin: 16mm 14mm 18mm 14mm; }
  body { font-family: -apple-system, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif; color: #1a1a1a; line-height: 1.6; font-size: 10.5pt; }
  h1 { font-size: 22pt; margin: 0 0 16pt; border-bottom: 2px solid #e60012; padding-bottom: 6pt; page-break-after: avoid; }
  h2 { font-size: 16pt; margin: 20pt 0 8pt; border-left: 5px solid #e60012; padding-left: 10pt; page-break-after: avoid; }
  h3 { font-size: 13pt; margin: 14pt 0 6pt; color: #333; page-break-after: avoid; }
  h4 { font-size: 11.5pt; margin: 10pt 0 4pt; color: #444; page-break-after: avoid; }
  p { margin: 0 0 8pt; }
  ul, ol { margin: 0 0 8pt; padding-left: 20pt; }
  li { margin-bottom: 3pt; }
  table { border-collapse: collapse; width: 100%; margin: 8pt 0 12pt; font-size: 9.5pt; page-break-inside: avoid; }
  th, td { border: 1px solid #ccc; padding: 4pt 6pt; text-align: left; vertical-align: top; }
  th { background: #f5f5f5; font-weight: 600; }
  code { background: #f3f3f3; padding: 1pt 4pt; border-radius: 3pt; font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9pt; }
  pre { background: #f7f7f7; padding: 8pt; border-radius: 4pt; overflow-x: auto; font-size: 9pt; page-break-inside: avoid; }
  pre code { background: transparent; padding: 0; }
  blockquote { border-left: 4px solid #ddd; margin: 8pt 0; padding: 4pt 12pt; color: #555; background: #fafafa; }
  img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4pt; margin: 6pt 0; page-break-inside: avoid; display: block; }
  hr { border: 0; border-top: 1px dashed #ccc; margin: 16pt 0; }
  a { color: #1a73e8; text-decoration: none; }
</style>
</head>
<body>
${body}
</body>
</html>`;

writeFileSync(HTML_PATH, html);
console.log(`HTML written: ${HTML_PATH}`);

const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.goto(pathToFileURL(HTML_PATH).toString(), { waitUntil: 'load' });
await page.waitForLoadState('networkidle');
await page.pdf({
  path: PDF_PATH,
  format: 'A4',
  printBackground: true,
  margin: { top: '16mm', right: '14mm', bottom: '18mm', left: '14mm' },
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate: '<div style="font-size:8pt;color:#888;width:100%;text-align:center;">シェフズルーム ダッシュボード 操作マニュアル v1 — <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
});
await browser.close();
console.log(`PDF written: ${PDF_PATH}`);
