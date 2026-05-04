#!/usr/bin/env node
/**
 * 本番DB plDailySales を POS基準 (salesData) に整合させる
 *
 * Tanaka 指示 (2026-05-04):
 *   "PL売上はPOS基準で統一。Dashboard 本番DBの値も置き換える"
 *
 * 4月の差分:
 *   4/4:  PL ¥64,810 → POS ¥75,000      (差 +¥10,190)  → UPDATE
 *   4/26: PL ¥0      → POS ¥78,610      (差 +¥78,610)  → INSERT (NEW)
 *   4/29: PL ¥50,000 → POS ¥0           (差 -¥50,000)  → DELETE
 *   4/30: PL ¥346,430→ POS ¥396,430     (差 +¥50,000)  → UPDATE
 *
 * 対象テーブル: pl_daily_sales (model: PlDailySales)
 * 対象店舗:     bfa-001 (FIVE Arrows)
 * 対象カテゴリ: 総売上 (id: af3fdbf7-865c-4bdb-9414-c1a26e1d613a)
 */
import { PrismaClient } from '/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules/@prisma/client/index.js';

const PROD_URL = "postgresql://neondb_owner:npg_ST9iQsZ1GOqC@ep-rough-bird-a1ynj8pb.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";
const prisma = new PrismaClient({ datasources: { db: { url: PROD_URL } } });

const STORE_CODE = 'bfa-001';
const TOTAL_SALES_CAT_ID = 'af3fdbf7-865c-4bdb-9414-c1a26e1d613a';

const updates = [
  { date: '2026-04-04', amount: 75000,  action: 'UPDATE', note: 'POS実績に整合' },
  { date: '2026-04-26', amount: 78610,  action: 'UPSERT', note: 'POS実績に整合 (PL未入力分)' },
  { date: '2026-04-29', amount: 0,      action: 'DELETE', note: 'POS会計0件 / 4/30へ振替分を取消' },
  { date: '2026-04-30', amount: 396430, action: 'UPDATE', note: 'POS実績に整合 (¥+50,000 = 4/29からの振替復元)' },
];

async function main() {
  const store = await prisma.store.findUnique({ where: { storeCode: STORE_CODE } });
  if (!store) throw new Error('Store bfa-001 not found');
  console.log(`Store: ${store.storeName} (${store.id})`);
  console.log();

  for (const u of updates) {
    const dateObj = new Date(`${u.date}T00:00:00.000Z`);
    console.log(`=== ${u.date}: ${u.action} amount=¥${u.amount.toLocaleString()} (${u.note}) ===`);

    // Read existing
    const existing = await prisma.plDailySales.findUnique({
      where: { storeId_date_categoryId: {
        storeId: store.id, date: dateObj, categoryId: TOTAL_SALES_CAT_ID
      }}
    });
    console.log(`  before: ${existing ? '¥'+Number(existing.amount).toLocaleString() : '(not exists)'}`);

    if (u.action === 'DELETE') {
      if (existing) {
        await prisma.plDailySales.delete({
          where: { storeId_date_categoryId: {
            storeId: store.id, date: dateObj, categoryId: TOTAL_SALES_CAT_ID
          }}
        });
        console.log('  → DELETED');
      } else {
        console.log('  → SKIP (already not exists)');
      }
    } else {
      const result = await prisma.plDailySales.upsert({
        where: { storeId_date_categoryId: {
          storeId: store.id, date: dateObj, categoryId: TOTAL_SALES_CAT_ID
        }},
        update: { amount: u.amount },
        create: {
          storeId: store.id,
          date: dateObj,
          categoryId: TOTAL_SALES_CAT_ID,
          amount: u.amount,
        }
      });
      console.log(`  → ${u.action}: ¥${Number(result.amount).toLocaleString()}`);
    }
  }

  // Verify total
  console.log();
  console.log('=== 検証 ===');
  const monthStart = new Date(Date.UTC(2026, 3, 1));
  const monthEnd = new Date(Date.UTC(2026, 4, 1));
  const aprSales = await prisma.plDailySales.findMany({
    where: { storeId: store.id, date: { gte: monthStart, lt: monthEnd },
             categoryId: TOTAL_SALES_CAT_ID },
    orderBy: { date: 'asc' }
  });
  let total = 0;
  for (const r of aprSales) {
    total += Number(r.amount);
  }
  console.log(`4月 PL total売上 (修正後): ¥${total.toLocaleString()}`);
  console.log(`期待値 (POS基準):           ¥3,024,490`);
  console.log(`差:                         ${total === 3024490 ? '✅ OK' : '❌ ¥'+(total-3024490)}`);

  await prisma.$disconnect();
}

main().catch(e => { console.error(e); process.exit(1); });
