#!/usr/bin/env node
import { PrismaClient } from '/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules/@prisma/client/index.js';
const DB_URL = "postgresql://neondb_owner:npg_VMDe16xUGaCg@ep-fancy-fog-a1srdl64.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";
const prisma = new PrismaClient({ datasources: { db: { url: DB_URL } } });

// Check both BFA stores
const candidates = ['bfa-001', 'test-003'];
for (const code of candidates) {
  const s = await prisma.store.findUnique({ where: { storeCode: code } });
  console.log(`\n=== ${code} : ${s.id} (${s.storeName}) ===`);

  const sd = await prisma.salesData.aggregate({
    where: { storeId: s.id }, _count: true,
    _min: { entryAt: true }, _max: { entryAt: true }
  });
  console.log(`SalesData: count=${sd._count} range=${sd._min.entryAt} ~ ${sd._max.entryAt}`);

  const ps = await prisma.plDailySales.aggregate({ where: { storeId: s.id }, _count: true, _min: { date: true }, _max: { date: true } });
  console.log(`PL sales: ${ps._count}, ${ps._min.date} ~ ${ps._max.date}`);
  const pe = await prisma.plDailyExpense.aggregate({ where: { storeId: s.id }, _count: true, _min: { date: true }, _max: { date: true } });
  console.log(`PL exp: ${pe._count}, ${pe._min.date} ~ ${pe._max.date}`);
  const ds = await prisma.dailyStoreSummary.count({ where: { storeId: s.id } });
  console.log(`DailySummary: ${ds}`);
  const dr = await prisma.dailyReport.count({ where: { storeId: s.id } });
  console.log(`DailyReport: ${dr}`);
  const mm = await prisma.menuMaster.count({ where: { storeId: s.id } });
  console.log(`Menu: ${mm}`);
}

await prisma.$disconnect();
