// Dump PL data for store bfa-001 from production DB.
// Reads DATABASE_URL_UNPOOLED from ~/RestaurantAILab/Dashboard/.env.production.
//
// Usage:
//   cd ~/RestaurantAILab/Dashboard
//   DATABASE_URL="$(grep ^DATABASE_URL_UNPOOLED .env.production | cut -d= -f2-)" \
//     npx tsx /Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/dump_db_pl.ts
import { PrismaClient } from "@prisma/client";
import * as fs from "node:fs";

const prisma = new PrismaClient();

async function main() {
  // 1. Resolve store
  const store = await prisma.store.findFirst({
    where: { storeCode: "bfa-001" },
    select: { id: true, storeCode: true, name: true },
  });
  if (!store) {
    console.error("Store bfa-001 not found");
    process.exit(1);
  }
  console.error("store:", store);

  // 2. Categories
  const salesCats = await prisma.plSalesCategory.findMany({
    where: { storeId: store.id },
    select: { id: true, name: true, displayOrder: true, isActive: true },
    orderBy: { displayOrder: "asc" },
  });
  const expCats = await prisma.plExpenseCategory.findMany({
    where: { storeId: store.id },
    select: { id: true, name: true, displayOrder: true, isActive: true, groupId: true },
    orderBy: { displayOrder: "asc" },
  });
  const expGroups = await prisma.plExpenseCategoryGroup.findMany({
    where: { storeId: store.id },
    select: { id: true, name: true, displayOrder: true, isActive: true },
    orderBy: { displayOrder: "asc" },
  });

  // 3. Monthly aggregated sales
  const salesRows: { year_month: string; category_id: string; total: string }[] = await prisma.$queryRawUnsafe(`
    SELECT to_char(date, 'YYYY-MM') AS year_month,
           category_id::text        AS category_id,
           SUM(amount)::text        AS total
    FROM pl_daily_sales
    WHERE store_id = '${store.id}'::uuid
    GROUP BY 1, 2
    ORDER BY 1, 2
  `);

  const expRows: { year_month: string; category_id: string; total: string }[] = await prisma.$queryRawUnsafe(`
    SELECT to_char(date, 'YYYY-MM') AS year_month,
           category_id::text        AS category_id,
           SUM(amount)::text        AS total
    FROM pl_daily_expenses
    WHERE store_id = '${store.id}'::uuid
    GROUP BY 1, 2
    ORDER BY 1, 2
  `);

  // 4. Monthly targets
  const targets = await prisma.plMonthlyTarget.findMany({
    where: { storeId: store.id },
    orderBy: { yearMonth: "asc" },
  });

  const out = {
    store,
    salesCategories: salesCats,
    expenseCategories: expCats,
    expenseGroups: expGroups,
    monthlySales: salesRows,
    monthlyExpenses: expRows,
    monthlyTargets: targets.map((t) => ({
      yearMonth: t.yearMonth,
      salesTarget: t.salesTarget?.toString() ?? null,
      profitTarget: t.profitTarget?.toString() ?? null,
      flTargetRatio: t.flTargetRatio?.toString() ?? null,
      salesBreakdown: t.salesBreakdown,
      expenseBudgets: t.expenseBudgets,
    })),
  };

  const outPath = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/v2/db_pl_dump.json";
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.error("wrote", outPath);
}

main().finally(async () => {
  await prisma.$disconnect();
});
