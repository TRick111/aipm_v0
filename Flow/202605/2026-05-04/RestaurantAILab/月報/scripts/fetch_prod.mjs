#!/usr/bin/env node
/** Production DB diagnose + fetch BFA April 2026. */
import { PrismaClient } from '/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules/@prisma/client/index.js';
import fs from 'node:fs';
import path from 'node:path';

const PROD_URL = "postgresql://neondb_owner:npg_ST9iQsZ1GOqC@ep-rough-bird-a1ynj8pb.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";
const prisma = new PrismaClient({ datasources: { db: { url: PROD_URL } } });
const OUT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報/data';

const monthStart = new Date(Date.UTC(2026, 3, 1));
const monthEnd = new Date(Date.UTC(2026, 4, 1));

console.log('=== PRODUCTION DB ===');
const stores = await prisma.store.findMany({ select: { id: true, storeCode: true, storeName: true } });
console.log('Stores:', stores.map(s => `${s.storeCode}=${s.storeName}`));

// Find BFA
const bfa = stores.find(s => s.storeCode==='bfa-001') || stores.find(s => /BAR FIVE/i.test(s.storeName));
console.log('BFA store:', bfa);
if (!bfa) { console.log('NOT FOUND'); await prisma.$disconnect(); process.exit(1); }

const sd = await prisma.salesData.aggregate({
  where: { storeId: bfa.id },
  _count: true,
  _min: { entryAt: true }, _max: { entryAt: true }
});
console.log('Sales: count=', sd._count, 'range=', sd._min.entryAt, '~', sd._max.entryAt);

const ps = await prisma.plDailySales.aggregate({ where: { storeId: bfa.id }, _count: true, _min: { date: true }, _max: { date: true } });
console.log('PL sales:', ps._count, ps._min.date, '~', ps._max.date);
const pe = await prisma.plDailyExpense.aggregate({ where: { storeId: bfa.id }, _count: true, _min: { date: true }, _max: { date: true } });
console.log('PL exp:', pe._count, pe._min.date, '~', pe._max.date);
const ds = await prisma.dailyStoreSummary.aggregate({ where: { storeId: bfa.id }, _count: true, _min: { date: true }, _max: { date: true } });
console.log('Daily summaries:', ds._count, ds._min.date, '~', ds._max.date);
const dr = await prisma.dailyReport.aggregate({ where: { storeId: bfa.id }, _count: true, _min: { date: true }, _max: { date: true } });
console.log('Daily reports:', dr._count, dr._min.date, '~', dr._max.date);
const mm = await prisma.menuMaster.count({ where: { storeId: bfa.id } });
console.log('Menu master:', mm);

if (sd._count > 0 && sd._max.entryAt >= monthStart) {
  // Pull April sales
  const sales = await prisma.salesData.findMany({
    where: { storeId: bfa.id, entryAt: { gte: monthStart, lt: monthEnd } },
    include: { items: true },
    orderBy: { entryAt: 'asc' }
  });
  console.log('April sales:', sales.length);
  const ser = sales.map(s => ({
    accountId: s.accountId, entryAt: s.entryAt, exitAt: s.exitAt, dayOfWeek: s.dayOfWeek,
    totalAmount: Number(s.totalAmount), customerCount: s.customerCount, itemCount: s.itemCount,
    hasReservation: s.hasReservation, isCourse: s.isCourse,
    items: s.items.map(it => ({
      menuName: it.menuName, price: Number(it.price), quantity: it.quantity,
      subtotal: Number(it.subtotal), category1: it.category1, category2: it.category2,
      orderedAt: it.orderedAt
    }))
  }));
  fs.writeFileSync(path.join(OUT, 'sales_april_PROD.json'), JSON.stringify(ser));
  console.log('-> sales_april_PROD.json');
}

// Pull all PL data for 2026
const startY = new Date(Date.UTC(2026, 0, 1));
const endY = new Date(Date.UTC(2026, 5, 1));
const plS = await prisma.plDailySales.findMany({
  where: { storeId: bfa.id, date: { gte: startY, lt: endY } },
});
const plE = await prisma.plDailyExpense.findMany({
  where: { storeId: bfa.id, date: { gte: startY, lt: endY } },
});
const plSCats = await prisma.plSalesCategory.findMany({ where: { storeId: bfa.id } });
const plECats = await prisma.plExpenseCategory.findMany({ where: { storeId: bfa.id }, include: { group: true } });
fs.writeFileSync(path.join(OUT, 'pl_2026_PROD.json'), JSON.stringify({
  sales_categories: plSCats.map(c => ({ id: c.id, name: c.name })),
  expense_categories: plECats.map(c => ({ id: c.id, name: c.name, group: c.group?.name, isFLCost: c.isFLCost })),
  daily_sales: plS.map(r => ({ date: r.date, categoryId: r.categoryId, amount: Number(r.amount) })),
  daily_expenses: plE.map(r => ({ date: r.date, categoryId: r.categoryId, amount: Number(r.amount), expenseType: r.expenseType, memo: r.memo })),
}));
console.log('PL 2026: sales=', plS.length, 'exp=', plE.length);

// Daily store summaries (April)
const sums = await prisma.dailyStoreSummary.findMany({
  where: { storeId: bfa.id, date: { gte: monthStart, lt: monthEnd } },
  orderBy: { date: 'asc' }
});
fs.writeFileSync(path.join(OUT, 'daily_summaries_PROD.json'), JSON.stringify(sums.map(d => ({ date: d.date, content: d.content })), null, 2));
console.log('Daily summaries April:', sums.length);

// Daily reports
const reports = await prisma.dailyReport.findMany({
  where: { storeId: bfa.id, date: { gte: monthStart, lt: monthEnd } },
  include: { member: true, answers: { include: { question: true } } },
  orderBy: { date: 'asc' }
});
fs.writeFileSync(path.join(OUT, 'daily_reports_PROD.json'), JSON.stringify(reports.map(r => ({
  date: r.date, member: r.member?.name, status: r.status,
  answers: r.answers.map(a => ({ question: a.question?.title, summary: a.summary }))
})), null, 2));
console.log('Daily reports April:', reports.length);

// Menu master
const menus = await prisma.menuMaster.findMany({ where: { storeId: bfa.id } });
fs.writeFileSync(path.join(OUT, 'menu_master_PROD.json'), JSON.stringify(menus.map(m => ({
  menuCode: m.menuCode, menuName: m.menuName, category1: m.category1, category2: m.category2,
  menuType: m.menuType, defaultPrice: m.defaultPrice ? Number(m.defaultPrice) : null,
  costRate: m.costRate ? Number(m.costRate) : null,
}))));
console.log('Menu master:', menus.length);

// Past months for comparison
const past = new Date(Date.UTC(2026, 0, 1));
const pastSales = await prisma.salesData.findMany({
  where: { storeId: bfa.id, entryAt: { gte: past, lt: monthStart } },
  include: { items: true }
});
console.log('Past 1-3月 sales:', pastSales.length);
const pastSer = pastSales.map(s => ({
  accountId: s.accountId, entryAt: s.entryAt, exitAt: s.exitAt, dayOfWeek: s.dayOfWeek,
  totalAmount: Number(s.totalAmount), customerCount: s.customerCount, itemCount: s.itemCount,
  hasReservation: s.hasReservation, isCourse: s.isCourse,
  items: s.items.map(it => ({
    menuName: it.menuName, price: Number(it.price), quantity: it.quantity,
    subtotal: Number(it.subtotal), category1: it.category1
  }))
}));
fs.writeFileSync(path.join(OUT, 'sales_jan_mar_PROD.json'), JSON.stringify(pastSer));

// 2025 same month for YoY
const y25start = new Date(Date.UTC(2025, 3, 1));
const y25end = new Date(Date.UTC(2025, 4, 1));
const y25 = await prisma.salesData.findMany({
  where: { storeId: bfa.id, entryAt: { gte: y25start, lt: y25end } },
  include: { items: true }
});
console.log('2025-04 sales:', y25.length);
const y25Ser = y25.map(s => ({
  accountId: s.accountId, entryAt: s.entryAt, dayOfWeek: s.dayOfWeek,
  totalAmount: Number(s.totalAmount), customerCount: s.customerCount, itemCount: s.itemCount,
  hasReservation: s.hasReservation, isCourse: s.isCourse,
  items: s.items.map(it => ({ menuName: it.menuName, quantity: it.quantity, subtotal: Number(it.subtotal), category1: it.category1 }))
}));
fs.writeFileSync(path.join(OUT, 'sales_2025_apr_PROD.json'), JSON.stringify(y25Ser));

await prisma.$disconnect();
console.log('Done.');
