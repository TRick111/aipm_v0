#!/usr/bin/env node
/**
 * prod DB から bfa-001 の 2026-01〜04 の monthlyReport レコードをエクスポートしてバックアップ。
 */
import { readFileSync, writeFileSync } from 'fs';
import { PrismaClient } from '@prisma/client';

const ENV_PATH = '/Users/rikutanaka/RestaurantAILab/Dashboard/.env.production';
const env = (() => {
  const txt = readFileSync(ENV_PATH, 'utf8');
  const e = {};
  for (const line of txt.split('\n')) {
    if (line.trim().startsWith('#') || !line.includes('=')) continue;
    const i = line.indexOf('=');
    e[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return e;
})();

if (!env.DATABASE_URL?.includes('ep-rough-bird')) throw new Error('not prod DB');
const prisma = new PrismaClient({ datasources: { db: { url: env.DATABASE_URL } } });

async function main() {
  const store = await prisma.store.findUnique({ where: { storeCode: 'bfa-001' } });
  console.log('store:', store?.id, store?.storeName);
  const recs = await prisma.monthlyReport.findMany({
    where: { storeId: store.id, year: 2026, month: { in: [1, 2, 3, 4] } },
    orderBy: { month: 'asc' },
  });
  console.log('records:', recs.length);
  for (const r of recs) {
    console.log(`  ${r.year}-${String(r.month).padStart(2,'0')}  id=${r.id}  url=${r.blobUrl}  size=${r.fileSize}B`);
  }
  const out = process.argv[2] || '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/_pl_update/_db_backup_pre_upload.json';
  writeFileSync(out, JSON.stringify(recs, null, 2));
  console.log(`✓ saved → ${out}`);
}

main().catch(e => { console.error(e); process.exit(1); }).finally(() => prisma.$disconnect());
