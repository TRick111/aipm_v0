#!/usr/bin/env node
/**
 * AirRegi 売上CSV (会計明細) ダウンロード（Mac, headless）
 * - cred は /tmp/bfa_creds.json (mode 600) からのみ読み込み
 * - 例外メッセージに password 値が混入しないよう、fill / click は専用ラッパー経由のみで実行
 * Usage: node _airregi_dl.mjs 2026 4
 */
import pkg from "/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules/playwright/index.js";
const { chromium } = pkg;
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const TARGET_YEAR = process.argv[2] || "2026";
const TARGET_MONTH = process.argv[3] || "4";

const creds = JSON.parse(fs.readFileSync("/tmp/bfa_creds.json", "utf8"));
const DOWNLOAD_DIR = path.join(os.homedir(), "Downloads");

const LOGIN_URL = "https://connect.airregi.jp/login?client_id=ARG&redirect_uri=https%3A%2F%2Fconnect.airregi.jp%2Foauth%2Fauthorize%3Fclient_id%3DARG%26redirect_uri%3Dhttps%253A%252F%252Fairregi.jp%252FCLP%252Fview%252FcallbackForPlfLogin%252Fauth%26response_type%3Dcode";

function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

/** safeFill: 失敗してもエラーメッセージに value を含めない */
async function safeFill(page, selector, value, label) {
  try {
    await page.locator(selector).first().waitFor({ state: "visible", timeout: 30000 });
    await page.fill(selector, value);
  } catch (e) {
    // Strip any echoed value from the upstream error message
    let msg = String(e?.message || e);
    if (value && msg.includes(value)) {
      msg = msg.replaceAll(value, "****");
    }
    throw new Error(`safeFill(${label}) failed: ${msg.slice(0, 400)}`);
  }
}

async function main() {
  log(`Launching Chromium (headless)...`);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    acceptDownloads: true,
    viewport: { width: 1280, height: 900 },
    locale: "ja-JP",
    timezoneId: "Asia/Tokyo",
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
  });
  const page = await context.newPage();

  try {
    log("Navigate to login");
    await page.goto(LOGIN_URL, { waitUntil: "domcontentloaded" });

    // Visible-only selectors (anti-bot decoy inputs `name=dummy0X` are display:none)
    const idSel = 'input[placeholder*="AirID"], input[placeholder*="メール"]';
    const pwSel = 'input[placeholder="パスワード"]';

    log(`Fill login form (id=${creds.id}, password=****)`);
    await safeFill(page, idSel, creds.id, "id");
    await safeFill(page, pwSel, creds.password, "password");

    // Login button: try multiple strategies
    const loginBtn = page
      .locator('button, input[type="submit"], a[role="button"]')
      .filter({ hasText: /^ログイン$/ })
      .first();
    if (!(await loginBtn.count())) {
      // Fallback: any visible button containing ログイン
      await page.getByRole("button", { name: "ログイン" }).first().click();
    } else {
      await loginBtn.click();
    }
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(3000);

    // Possible "choose store" page: pick BAR FIVE Arrows
    if (page.url().includes("choose-store")) {
      log("Choose-store page → click 'BAR FIVE Arrows'");
      await page.click('text=BAR FIVE Arrows');
      await page.waitForLoadState("domcontentloaded");
      await page.waitForTimeout(2500);
    }
    // Login confirmation: should be off /login/* now
    if (page.url().includes("/login") && !page.url().includes("choose-store")) {
      const body = await page.locator("body").innerText().catch(() => "");
      const sanitized = body.replaceAll(creds.password, "****").slice(0, 600);
      throw new Error(`Login failed.\nURL=${page.url()}\nBody: ${sanitized}`);
    }
    log(`Logged in. URL=${page.url()}`);

    log("Navigate to salesList");
    await page.goto("https://airregi.jp/CLP/view/salesList/", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(2500);

    log(`Set year=${TARGET_YEAR} month=${TARGET_MONTH} (selects: 0=集計対象, 1=年, 2=月)`);
    const selects = page.locator("select");
    const selN = await selects.count();
    log(`  found ${selN} select(s)`);
    if (selN < 3) throw new Error("Expected at least 3 selects (集計対象/年/月)");
    // Dump options for diagnosis
    for (let i = 0; i < selN; i++) {
      const opts = await selects.nth(i).evaluate((el) =>
        Array.from(el.options).map((o) => ({ v: o.value, t: o.text }))
      );
      log(`  select#${i} options: ${JSON.stringify(opts).slice(0, 300)}`);
    }
    // Try to find the year & month selects by their option content
    let yearIdx = -1, monthIdx = -1;
    for (let i = 0; i < selN; i++) {
      const opts = await selects.nth(i).evaluate((el) =>
        Array.from(el.options).map((o) => o.value + "|" + o.text)
      );
      const txt = opts.join(",");
      if (yearIdx === -1 && /(2025|2026)/.test(txt) && !/月/.test(txt)) yearIdx = i;
      if (monthIdx === -1 && /(^|,)(1\||4\||4月)/.test(txt) && /月/.test(txt)) monthIdx = i;
    }
    if (yearIdx === -1 || monthIdx === -1) {
      // Fallback: assume 1=year, 2=month
      yearIdx = 1; monthIdx = 2;
    }
    log(`  resolved yearIdx=${yearIdx}, monthIdx=${monthIdx}`);

    // Try selecting by value or label
    async function tryFlex(sel, want) {
      const opts = await sel.evaluate((el) => Array.from(el.options).map((o) => ({ v: o.value, t: o.text })));
      const wantStr = String(want);
      const match = opts.find((o) => o.v === wantStr || o.t === wantStr || o.t === wantStr + "年" || o.t === wantStr + "月");
      if (!match) throw new Error(`No option matches '${want}' in ${JSON.stringify(opts).slice(0,200)}`);
      await sel.selectOption(match.v);
    }
    await tryFlex(selects.nth(yearIdx), TARGET_YEAR);
    await tryFlex(selects.nth(monthIdx), TARGET_MONTH);

    log("Click 表示する");
    const showBtn = page.locator('button:has-text("表示する"), input[type="button"][value*="表示"], input[type="submit"][value*="表示"]').first();
    await Promise.all([
      page.waitForLoadState("domcontentloaded"),
      showBtn.click(),
    ]);
    await page.waitForTimeout(3500);

    log("Click CSVデータをダウンロードする");
    const csvBtn = page.locator('text=CSVデータをダウンロードする').first();
    await csvBtn.scrollIntoViewIfNeeded();
    await csvBtn.click();
    await page.waitForTimeout(1500);

    log("Wait for download (click 会計明細 button in popup)");
    const downloadPromise = page.waitForEvent("download", { timeout: 120000 });

    // Find the 会計明細 popup button via its bounding rect (right-side popup ~y >= 700, x >= 1000)
    // Then perform a real Playwright mouse click via page.mouse.click(x, y)
    const coords = await page.evaluate(() => {
      function visible(el) {
        if (!el || el.offsetParent === null) return false;
        const r = el.getBoundingClientRect();
        return r.width > 5 && r.height > 5;
      }
      const all = Array.from(document.querySelectorAll('button, a, [role="button"], [tabindex]'));
      const matches = all.filter((el) => {
        const t = (el.textContent || "").replace(/\s+/g, "").trim();
        return t.endsWith("会計明細") && !t.includes("CSV") && t.length < 200 && visible(el);
      });
      // Sort by smallest textContent (most specific button)
      matches.sort((a, b) => (a.textContent.length - b.textContent.length));
      const t = matches[0];
      if (!t) return null;
      const r = t.getBoundingClientRect();
      return {
        tag: t.tagName,
        n: matches.length,
        x: r.left + r.width / 2,
        y: r.top + r.height / 2,
        outerHTMLLen: t.outerHTML.length,
      };
    });
    log(`  → popup button coords: ${JSON.stringify(coords)}`);
    if (!coords) throw new Error("会計明細 popup button not found");
    await page.mouse.click(coords.x, coords.y);

    const download = await downloadPromise;
    log(`Download suggested filename: ${download.suggestedFilename()}`);

    const ym = `${TARGET_YEAR}${String(TARGET_MONTH).padStart(2, "0")}`;
    const lastDay = new Date(parseInt(TARGET_YEAR), parseInt(TARGET_MONTH), 0).getDate();
    const targetName = `会計明細-${ym}01-${ym}${String(lastDay).padStart(2, "0")}.csv`;
    const targetPath = path.join(DOWNLOAD_DIR, targetName);
    if (!fs.existsSync(DOWNLOAD_DIR)) fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
    await download.saveAs(targetPath);
    log(`Saved CSV → ${targetPath} (size=${fs.statSync(targetPath).size} bytes)`);

    log("DONE");
    process.exitCode = 0;
  } catch (e) {
    let msg = String(e?.message || e);
    if (creds?.password && msg.includes(creds.password)) {
      msg = msg.replaceAll(creds.password, "****");
    }
    log(`ERROR: ${msg.slice(0, 800)}`);
    log(`Current URL: ${page.url()}`);
    try {
      await page.screenshot({ path: "/tmp/airregi_err.png", fullPage: true });
      log("Screenshot saved to /tmp/airregi_err.png");
    } catch {}
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main();
