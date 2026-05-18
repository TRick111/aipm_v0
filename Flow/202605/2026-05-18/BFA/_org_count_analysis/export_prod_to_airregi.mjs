#!/usr/bin/env node
/**
 * BFA prod DB から business-month 範囲の sales_data + sales_items を取得し、
 * monthly_report_pipeline.py が読める AirRegi 提供CSV 互換 (Shift-JIS) を生成する。
 *
 * - store: bfa-001
 * - 業務日基準（朝6時境界 / 0:00〜5:59 を前日扱い）
 * - 月内に business_date が入る会計を全件抽出
 * - 各会計について：ヘッダ行1行 + 明細行（sales_items 全部）
 *
 * Usage:
 *   node export_prod_to_airregi.mjs <YYYY-MM> <out.csv> [--include-non-bfa-staff]
 */
import { PrismaClient } from '@prisma/client';
import { readFileSync, writeFileSync } from 'fs';
import iconv from 'iconv-lite';

const ENV_PATH = '/Users/rikutanaka/RestaurantAILab/Dashboard/.env.production';

function loadEnv(file) {
  const txt = readFileSync(file, 'utf8');
  const env = {};
  for (const line of txt.split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.+?)\s*$/);
    if (m && !line.trim().startsWith('#')) env[m[1]] = m[2];
  }
  return env;
}

const env = loadEnv(ENV_PATH);
if (!env.DATABASE_URL) throw new Error('DATABASE_URL not found in .env.production');

const targetMonth = process.argv[2]; // YYYY-MM
const outPath = process.argv[3];
if (!targetMonth || !outPath) {
  console.error('Usage: node export_prod_to_airregi.mjs <YYYY-MM> <out.csv>');
  process.exit(1);
}

const prisma = new PrismaClient({
  datasources: { db: { url: env.DATABASE_URL } },
});

const COLUMNS = [
  '取引No','会計日','会計時間','合計','小計','内消費税','修正金額合計','修正後合計','修正後内消費税',
  '現金','クレジットカード(Airペイ)','交通系電子マネー(Airペイ)','QUICPay(Airペイ)','iD(Airペイ)',
  'QR決済(Airペイ QR)','クレジットカード(オンライン決済)','クレジットカード/電子マネー(Square)',
  'ポイント(Airペイ ポイント)','ポイント(ホットペッパーグルメ)','Pontaポイント(Airウォレット)',
  '金券合計','売掛合計','おつり','現金以外おつり不支払額','全体割引/割増(税込)','個別割引/割増(税込)',
  '割引/割増合計(税込)','人数','商品点数','滞在時間','伝票名','レジ担当者名','ID',
  'カテゴリー名','メニュー名','価格','注文数量',
];

function csvCell(v) {
  if (v == null || v === '') return '';
  const s = String(v);
  // If contains comma or quote, wrap in quotes and escape quotes
  if (s.includes(',') || s.includes('"') || s.includes('\n')) {
    return '"' + s.replace(/"/g, '""') + '"';
  }
  return s;
}

function rowToCsv(row) {
  return COLUMNS.map((c) => csvCell(row[c])).join(',');
}

function toJST(d) {
  // Postgres returns UTC; convert to Asia/Tokyo for display fields
  // We use Intl.DateTimeFormat with timeZone Asia/Tokyo for safety.
  const dt = new Date(d);
  const tz = 'Asia/Tokyo';
  const fmt = (opts) => new Intl.DateTimeFormat('ja-JP', { timeZone: tz, ...opts }).format(dt);
  const y = fmt({ year: 'numeric' }).replace('年','').trim();
  const m = fmt({ month: '2-digit' }).replace('月','').padStart(2,'0').trim();
  const d2 = fmt({ day: '2-digit' }).replace('日','').padStart(2,'0').trim();
  // Use formatToParts for HH:mm:ss
  const parts = new Intl.DateTimeFormat('en-GB', { timeZone: tz, hour12: false,
    hour: '2-digit', minute: '2-digit', second: '2-digit' }).formatToParts(dt);
  const get = (t) => (parts.find(p => p.type === t)?.value ?? '00').padStart(2,'0');
  return {
    date: `${y}/${m.padStart(2,'0')}/${d2.padStart(2,'0')}`,
    time: `${get('hour')}:${get('minute')}:${get('second')}`,
    hour: parseInt(get('hour'), 10),
    isoDate: `${y}-${m.padStart(2,'0')}-${d2.padStart(2,'0')}`,
  };
}

function businessDate(entryAt) {
  // 6AM境界: 0-5時は前日扱い
  const j = toJST(entryAt);
  if (j.hour < 6) {
    const d = new Date(`${j.isoDate}T00:00:00+09:00`);
    d.setUTCDate(d.getUTCDate() - 1);
    const y = d.getUTCFullYear();
    const m = String(d.getUTCMonth() + 1).padStart(2, '0');
    const dd = String(d.getUTCDate()).padStart(2, '0');
    return `${y}-${m}-${dd}`;
  }
  return j.isoDate;
}

function diffHMS(entryAt, exitAt) {
  if (!exitAt || !entryAt) return '00:00:00';
  const sec = Math.max(0, Math.floor((new Date(exitAt).getTime() - new Date(entryAt).getTime()) / 1000));
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}

async function main() {
  const store = await prisma.store.findUnique({
    where: { storeCode: 'bfa-001' },
    select: { id: true, storeCode: true, storeName: true },
  });
  if (!store) throw new Error('store bfa-001 not found in prod DB');
  console.error('Store:', store);

  // Fetch a slightly wider window (prev month last day 0AM JST → next month day 1 06:00 JST)
  // so business-day boundary records are included.
  const [y, mo] = targetMonth.split('-').map(Number);
  // Range UTC: prev month 28th 00:00 UTC to next month 1st 03:00 UTC (safe window covering JST 6AM boundary)
  const startUtc = new Date(Date.UTC(y, mo - 1, 1, -15, 0, 0)); // JST 6AM of first day == UTC 21:00 previous day; we go wider
  const endUtc = new Date(Date.UTC(y, mo, 2, 0, 0, 0)); // wider

  console.error(`Fetching sales_data for ${targetMonth} (UTC ${startUtc.toISOString()} ~ ${endUtc.toISOString()})...`);

  const sales = await prisma.salesData.findMany({
    where: {
      storeId: store.id,
      entryAt: { gte: startUtc, lt: endUtc },
    },
    include: { items: true },
    orderBy: { entryAt: 'asc' },
  });
  console.error(`Fetched ${sales.length} sales rows (raw window). Filtering by business_month=${targetMonth}...`);

  // Filter by business_month
  const targetBM = targetMonth;
  const filtered = sales.filter((s) => businessDate(s.entryAt).slice(0, 7) === targetBM);
  console.error(`After business-month filter: ${filtered.length} accounts`);

  // Build CSV rows: header line per account + items
  const rows = [];
  let totalSales = 0;
  let totalCust = 0;
  for (const s of filtered) {
    const j = toJST(s.entryAt);
    const stay = diffHMS(s.entryAt, s.exitAt);
    const hdr = Object.fromEntries(COLUMNS.map((c) => [c, '']));
    hdr['取引No'] = s.accountId;
    hdr['会計日'] = j.date;
    hdr['会計時間'] = j.time;
    hdr['合計'] = Number(s.totalAmount);
    hdr['小計'] = Number(s.totalAmount);
    hdr['修正後合計'] = Number(s.totalAmount);
    hdr['人数'] = s.customerCount;
    hdr['商品点数'] = s.itemCount;
    hdr['滞在時間'] = stay;
    rows.push(hdr);
    totalSales += Number(s.totalAmount);
    totalCust += Number(s.customerCount);

    for (const it of s.items) {
      const d = Object.fromEntries(COLUMNS.map((c) => [c, '']));
      d['取引No'] = s.accountId;
      d['カテゴリー名'] = it.category1 ?? '';
      d['メニュー名'] = it.menuName ?? '';
      d['価格'] = Number(it.price);
      d['注文数量'] = Number(it.quantity);
      rows.push(d);
    }
  }

  const header = COLUMNS.join(',');
  const body = rows.map(rowToCsv).join('\r\n');
  const csvUtf8 = header + '\r\n' + body + '\r\n';
  const csvSjis = iconv.encode(csvUtf8, 'shift_jis');
  writeFileSync(outPath, csvSjis);
  console.error(`\nWrote ${rows.length + 1} rows (1 header + ${rows.length} data) to ${outPath}`);
  console.error(`Accounts: ${filtered.length}`);
  console.error(`Sum 合計: ¥${totalSales.toLocaleString()}`);
  console.error(`Sum 人数: ${totalCust}`);

  // Also dump a sidecar JSON for quick stats
  const stats = {
    target_month: targetMonth,
    store,
    fetched_at: new Date().toISOString(),
    accounts_total: filtered.length,
    sum_total_amount: totalSales,
    sum_customer_count: totalCust,
    accounts_zero_total: filtered.filter((s) => Number(s.totalAmount) === 0).length,
    accounts_negative_total: filtered.filter((s) => Number(s.totalAmount) < 0).length,
    accounts_positive_total: filtered.filter((s) => Number(s.totalAmount) > 0).length,
    customer_zero_accounts: filtered.filter((s) => Number(s.customerCount) === 0).length,
    business_days_covered: new Set(filtered.map((s) => businessDate(s.entryAt))).size,
    account_ids: filtered.map((s) => ({
      account_id: s.accountId,
      business_date: businessDate(s.entryAt),
      entry_at_utc: s.entryAt.toISOString(),
      total: Number(s.totalAmount),
      customers: s.customerCount,
      item_count: s.itemCount,
    })),
  };
  writeFileSync(outPath.replace(/\.csv$/, '_stats.json'), JSON.stringify(stats, null, 2));
  console.error(`Sidecar stats: ${outPath.replace(/\.csv$/, '_stats.json')}`);
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
