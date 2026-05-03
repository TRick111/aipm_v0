#!/usr/bin/env node
import { PrismaClient } from '/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules/@prisma/client/index.js';
const DB_URL = "postgresql://neondb_owner:npg_VMDe16xUGaCg@ep-fancy-fog-a1srdl64.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";
const prisma = new PrismaClient({ datasources: { db: { url: DB_URL } } });

const store = await prisma.store.findUnique({ where: { storeCode: 'bfa-001' } });
console.log('Store:', store.id, store.storeName);

// Check sales data range
const minMax = await prisma.salesData.aggregate({
  where: { storeId: store.id },
  _min: { entryAt: true },
  _max: { entryAt: true },
  _count: true,
});
console.log('Sales: count=', minMax._count, 'min=', minMax._min.entryAt, 'max=', minMax._max.entryAt);

// PL sales
const ps = await prisma.plDailySales.aggregate({
  where: { storeId: store.id },
  _min: { date: true }, _max: { date: true }, _count: true
});
console.log('PL daily sales: count=', ps._count, 'min=', ps._min.date, 'max=', ps._max.date);

// PL expense
const pe = await prisma.plDailyExpense.aggregate({
  where: { storeId: store.id },
  _min: { date: true }, _max: { date: true }, _count: true
});
console.log('PL daily expense: count=', pe._count, 'min=', pe._min.date, 'max=', pe._max.date);

// Daily summaries
const ds = await prisma.dailyStoreSummary.aggregate({
  where: { storeId: store.id },
  _min: { date: true }, _max: { date: true }, _count: true
});
console.log('Daily summaries: count=', ds._count, 'min=', ds._min.date, 'max=', ds._max.date);

// Daily reports
const dr = await prisma.dailyReport.aggregate({
  where: { storeId: store.id },
  _min: { date: true }, _max: { date: true }, _count: true
});
console.log('Daily reports: count=', dr._count, 'min=', dr._min.date, 'max=', dr._max.date);

// Menu master
const mm = await prisma.menuMaster.count({ where: { storeId: store.id } });
console.log('MenuMaster:', mm);

// Monthly summary
const allMs = await prisma.monthlySummary.findMany({
  where: { storeId: store.id },
  orderBy: { yearMonth: 'asc' }
});
console.log('Monthly summaries:', allMs.map(m => `${m.yearMonth}:${Number(m.totalSales)}`).join(', '));

// All stores (perhaps another store_code pattern for BFA?)
const allStores = await prisma.store.findMany({ select: { id: true, storeCode: true, storeName: true } });
console.log('All stores:', allStores);

await prisma.$disconnect();
