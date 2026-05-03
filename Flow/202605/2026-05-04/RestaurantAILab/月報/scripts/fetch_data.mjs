#!/usr/bin/env node
/**
 * BFA 2026年4月 月報 — Dashboard DB データ抽出
 * 出力: data/ 以下にJSON/CSV
 */
import { PrismaClient } from '/Users/rikutanaka/RestaurantAILab/Dashboard/node_modules/@prisma/client/index.js';
import fs from 'node:fs';
import path from 'node:path';

const DB_URL = "postgresql://neondb_owner:npg_VMDe16xUGaCg@ep-fancy-fog-a1srdl64.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";

const prisma = new PrismaClient({
  datasources: { db: { url: DB_URL } }
});

const STORE_CODE = 'bfa-001';
const YEAR = 2026;
const MONTH = 4;

const OUT_DIR = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報/data';
fs.mkdirSync(OUT_DIR, { recursive: true });

const monthStart = new Date(Date.UTC(YEAR, MONTH - 1, 1));
const monthEnd = new Date(Date.UTC(YEAR, MONTH, 1)); // exclusive

// JST date string from Date
function jstDateStr(d) {
  const t = new Date(d.getTime() + 9 * 3600 * 1000);
  return t.toISOString().slice(0, 10);
}

function dow(d) {
  const j = new Date(d.getTime() + 9 * 3600 * 1000);
  return ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][j.getUTCDay()];
}

async function main() {
  // 1. Store
  const store = await prisma.store.findUnique({ where: { storeCode: STORE_CODE } });
  if (!store) throw new Error('Store bfa-001 not found');
  console.log(`Store: ${store.storeName} (${store.id})`);

  fs.writeFileSync(path.join(OUT_DIR, 'store.json'), JSON.stringify({
    id: store.id, storeCode: store.storeCode, storeName: store.storeName
  }, null, 2));

  // 2. Sales data with items (April 2026)
  const sales = await prisma.salesData.findMany({
    where: {
      storeId: store.id,
      entryAt: { gte: monthStart, lt: monthEnd }
    },
    include: { items: true },
    orderBy: { entryAt: 'asc' }
  });
  console.log(`Sales transactions: ${sales.length}`);
  // serialize Decimal -> number
  const salesSer = sales.map(s => ({
    accountId: s.accountId,
    entryAt: s.entryAt,
    exitAt: s.exitAt,
    dayOfWeek: s.dayOfWeek,
    totalAmount: Number(s.totalAmount),
    customerCount: s.customerCount,
    itemCount: s.itemCount,
    hasReservation: s.hasReservation,
    isCourse: s.isCourse,
    items: s.items.map(it => ({
      menuId: it.menuId,
      menuName: it.menuName,
      price: Number(it.price),
      quantity: it.quantity,
      subtotal: Number(it.subtotal),
      category1: it.category1,
      category2: it.category2,
      orderedAt: it.orderedAt,
    }))
  }));
  fs.writeFileSync(path.join(OUT_DIR, 'sales_april.json'), JSON.stringify(salesSer));
  console.log(`-> sales_april.json (${salesSer.length} rows)`);

  // 3. Daily store summary (AI daily summaries)
  const dailySummaries = await prisma.dailyStoreSummary.findMany({
    where: {
      storeId: store.id,
      date: { gte: monthStart, lt: monthEnd }
    },
    orderBy: { date: 'asc' }
  });
  fs.writeFileSync(path.join(OUT_DIR, 'daily_summaries.json'),
    JSON.stringify(dailySummaries.map(d => ({ date: d.date, content: d.content })), null, 2));
  console.log(`-> daily_summaries.json (${dailySummaries.length})`);

  // 4. Daily reports + answers
  const dailyReports = await prisma.dailyReport.findMany({
    where: {
      storeId: store.id,
      date: { gte: monthStart, lt: monthEnd }
    },
    include: {
      member: true,
      answers: { include: { question: true } }
    },
    orderBy: { date: 'asc' }
  });
  fs.writeFileSync(path.join(OUT_DIR, 'daily_reports.json'),
    JSON.stringify(dailyReports.map(r => ({
      date: r.date,
      member: r.member?.name,
      position: r.position,
      status: r.status,
      answers: r.answers.map(a => ({
        question: a.question?.title,
        summary: a.summary,
        conversation: a.conversation,
      }))
    })), null, 2));
  console.log(`-> daily_reports.json (${dailyReports.length})`);

  // 5. PL daily sales / expenses (April 2026)
  const plSalesCats = await prisma.plSalesCategory.findMany({ where: { storeId: store.id } });
  const plExpCats = await prisma.plExpenseCategory.findMany({ where: { storeId: store.id }, include: { group: true } });

  const plDailySales = await prisma.plDailySales.findMany({
    where: { storeId: store.id, date: { gte: monthStart, lt: monthEnd } }
  });
  const plDailyExp = await prisma.plDailyExpense.findMany({
    where: { storeId: store.id, date: { gte: monthStart, lt: monthEnd } }
  });

  fs.writeFileSync(path.join(OUT_DIR, 'pl_categories.json'), JSON.stringify({
    sales: plSalesCats.map(c => ({ id: c.id, name: c.name, displayOrder: c.displayOrder })),
    expense: plExpCats.map(c => ({ id: c.id, name: c.name, group: c.group?.name, isFLCost: c.isFLCost, displayOrder: c.displayOrder })),
  }, null, 2));

  fs.writeFileSync(path.join(OUT_DIR, 'pl_daily_april.json'), JSON.stringify({
    sales: plDailySales.map(r => ({ date: r.date, categoryId: r.categoryId, amount: Number(r.amount) })),
    expense: plDailyExp.map(r => ({ date: r.date, categoryId: r.categoryId, amount: Number(r.amount), expenseType: r.expenseType, memo: r.memo })),
  }, null, 2));
  console.log(`-> pl_daily_april.json sales=${plDailySales.length} exp=${plDailyExp.length}`);

  // 6. Monthly target (April)
  const target = await prisma.plMonthlyTarget.findUnique({
    where: { storeId_yearMonth: { storeId: store.id, yearMonth: `${YEAR}-${String(MONTH).padStart(2,'0')}` } }
  });
  fs.writeFileSync(path.join(OUT_DIR, 'pl_target_april.json'), JSON.stringify(target ? {
    yearMonth: target.yearMonth,
    salesTarget: Number(target.salesTarget),
    salesBreakdown: target.salesBreakdown,
    expenseBudgets: target.expenseBudgets,
    profitTarget: Number(target.profitTarget),
    flTargetRatio: Number(target.flTargetRatio),
  } : null, null, 2));

  // 7. Monthly summary cache
  const monthlySum = await prisma.monthlySummary.findFirst({
    where: { storeId: store.id, yearMonth: `${YEAR}-${String(MONTH).padStart(2,'0')}` }
  });
  fs.writeFileSync(path.join(OUT_DIR, 'monthly_summary_april.json'), JSON.stringify(monthlySum ? {
    yearMonth: monthlySum.yearMonth,
    totalSales: Number(monthlySum.totalSales),
    totalAccounts: monthlySum.totalAccounts,
    totalCustomers: monthlySum.totalCustomers,
    avgUnitPrice: Number(monthlySum.avgUnitPrice),
    avgPerPerson: Number(monthlySum.avgPerPerson),
  } : null, null, 2));

  // 8. Menu master
  const menus = await prisma.menuMaster.findMany({ where: { storeId: store.id } });
  fs.writeFileSync(path.join(OUT_DIR, 'menu_master.json'),
    JSON.stringify(menus.map(m => ({
      id: m.id, menuCode: m.menuCode, menuName: m.menuName,
      category1: m.category1, category2: m.category2, menuType: m.menuType,
      defaultPrice: m.defaultPrice ? Number(m.defaultPrice) : null,
      costRate: m.costRate ? Number(m.costRate) : null,
    })), null, 2));
  console.log(`-> menu_master.json (${menus.length})`);

  // 9. Past months summary for trend (Jan-Mar 2026)
  const pastMonths = ['2026-01', '2026-02', '2026-03'];
  const pastSummaries = [];
  for (const ym of pastMonths) {
    const ms = await prisma.monthlySummary.findFirst({
      where: { storeId: store.id, yearMonth: ym }
    });
    if (ms) {
      pastSummaries.push({
        yearMonth: ms.yearMonth,
        totalSales: Number(ms.totalSales),
        totalAccounts: ms.totalAccounts,
        totalCustomers: ms.totalCustomers,
        avgUnitPrice: Number(ms.avgUnitPrice),
        avgPerPerson: Number(ms.avgPerPerson),
      });
    }
  }
  fs.writeFileSync(path.join(OUT_DIR, 'monthly_summary_past.json'), JSON.stringify(pastSummaries, null, 2));

  // Past PL daily for Jan/Feb/Mar (DB側にあれば)
  const pastStart = new Date(Date.UTC(YEAR, 0, 1));
  const pastPlSales = await prisma.plDailySales.findMany({
    where: { storeId: store.id, date: { gte: pastStart, lt: monthStart } }
  });
  const pastPlExp = await prisma.plDailyExpense.findMany({
    where: { storeId: store.id, date: { gte: pastStart, lt: monthStart } }
  });
  fs.writeFileSync(path.join(OUT_DIR, 'pl_daily_jan_mar.json'), JSON.stringify({
    sales: pastPlSales.map(r => ({ date: r.date, categoryId: r.categoryId, amount: Number(r.amount) })),
    expense: pastPlExp.map(r => ({ date: r.date, categoryId: r.categoryId, amount: Number(r.amount), expenseType: r.expenseType })),
  }));
  console.log(`-> pl_daily_jan_mar.json sales=${pastPlSales.length} exp=${pastPlExp.length}`);

  await prisma.$disconnect();
  console.log('Done.');
}

main().catch(e => { console.error(e); process.exit(1); });
