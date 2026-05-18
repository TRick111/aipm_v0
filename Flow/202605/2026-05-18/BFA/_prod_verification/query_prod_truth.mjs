#!/usr/bin/env node
/**
 * Phase 1-1: prod DB から BFA(bfa-001) の月次売上 truth を取得する。
 *
 * - 集計範囲: JST (Asia/Tokyo) で各月の 1日 00:00:00 〜 月末 23:59:59
 *   (entry_at AT TIME ZONE 'Asia/Tokyo')
 * - 出力: prod_monthly_truth.json
 */

import { PrismaClient } from '@prisma/client';
import { readFileSync, writeFileSync } from 'fs';
import path from 'path';

const ENV_PATH = '/Users/rikutanaka/RestaurantAILab/Dashboard/.env.production';
const OUT_PATH = path.resolve(
  '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/_prod_verification/prod_monthly_truth.json'
);

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

const prisma = new PrismaClient({
  datasources: { db: { url: env.DATABASE_URL } },
});

async function main() {
  const store = await prisma.store.findUnique({
    where: { storeCode: 'bfa-001' },
    select: { id: true, storeCode: true, storeName: true },
  });
  if (!store) throw new Error('store bfa-001 not found in prod DB');
  console.log('Store:', store);

  const months = ['2026-01', '2026-02', '2026-03', '2026-04'];
  const result = { store, generatedAt: new Date().toISOString(), months: {} };

  for (const m of months) {
    const [y, mo] = m.split('-').map(Number);
    const startStr = `${y}-${String(mo).padStart(2, '0')}-01`;
    const lastDay = new Date(Date.UTC(y, mo, 0)).getUTCDate();
    const endStr = `${y}-${String(mo).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

    // Aggregate by entry_at (JST) within month
    const rows = await prisma.$queryRaw`
      SELECT
        COUNT(*)::int AS accounts,
        COALESCE(SUM(total_amount), 0)::numeric AS sales_total,
        COALESCE(SUM(customer_count), 0)::int AS customers
      FROM sales_data
      WHERE store_id = ${store.id}::uuid
        AND (entry_at AT TIME ZONE 'Asia/Tokyo')::date
            BETWEEN ${startStr}::date AND ${endStr}::date
    `;
    const r = rows[0];
    result.months[m] = {
      range: `${startStr} ~ ${endStr} (JST entry_at)`,
      accounts: Number(r.accounts),
      sales_total: Number(r.sales_total),
      customers: Number(r.customers),
    };
    console.log(`${m}: accounts=${r.accounts}, sales=¥${Number(r.sales_total).toLocaleString()}, customers=${r.customers}`);
  }

  writeFileSync(OUT_PATH, JSON.stringify(result, null, 2));
  console.log(`\nWrote: ${OUT_PATH}`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
