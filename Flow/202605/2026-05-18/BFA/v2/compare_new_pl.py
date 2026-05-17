#!/usr/bin/env python3
"""Compare 新PL管理（移管前） sheet with production DB for bfa-001.

Sheet layout (header row 0):
  col 0: '' / row labels block-A
  col 1: '' / row labels block-B (category names)
  col 2,4,6,...: month amounts (2026年1月, 2026年2月, ...)
  col 3,5,7,...: percentages (skip)

Sheet sections (row index):
  実績 売上     : rows 1-4 (ドリンク/フード/コース/イベント), row 5 = 合計
  実績 費用     : rows 6-15 (食材/ドリンク/広告費/家賃/人件費/ローン返済/水道光熱費/管理費/備品/税金),
                  row 16 = 合計
  実績 利益     : row 17 = 合計
  予実比        : rows 19-21 (売上/費用/利益)
  ▼予算 売上    : rows 28-32 (ドリンク/フード/チャーム/コース/イベント), row 33 = 合計
  ▼予算 費用    : rows 34-43 (食材/ドリンク/販売・広告/家賃/人件費/ローン返済/水道光熱費/
                  通信・衛生・管理費etc.../備品/税金), row 44 = 合計
  ▼予算 利益    : row 45 = 合計
  CLP人件費 (実績側 row 47)
  利益（CLP人件費考慮） row 48
"""
import json, re

SHEET_RAW = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/v2/new_pl_raw_clean.json"
DB_DUMP   = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/v2/db_pl_dump.json"
OUT_JSON  = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/v2/comparison.json"

def to_num(s):
    if s is None: return None
    s = str(s).strip()
    if not s: return None
    if s.startswith('#'):  # #DIV/0!, #N/A
        return None
    s = s.replace('¥','').replace(',','').replace(' ','')
    try:
        return float(s)
    except ValueError:
        return None

def normalize_cat(name: str) -> str:
    if name is None: return ''
    # strip emoji prefix common in DB names
    return re.sub(r'^[^\wぁ-んァ-ン一-龥]+', '', name).strip()

def parse_sheet():
    raw = json.load(open(SHEET_RAW))
    vals = raw['values']
    header = vals[0]
    # months: even columns starting at 2
    months = {}  # col_index -> 'YYYY-MM'
    for j in range(2, len(header), 2):
        h = header[j]
        m = re.match(r'^(\d{4})年(\d{1,2})月$', h or '')
        if m:
            months[j] = f"{m.group(1)}-{int(m.group(2)):02d}"

    def cell(row, col):
        if row >= len(vals): return None
        r = vals[row]
        if col >= len(r): return None
        return r[col]

    # --- 実績 ---
    actual_sales_rows = {
        'ドリンク': 1, 'フード': 2, 'コース': 3, 'イベント': 4,
    }
    actual_sales_total_row = 5
    actual_exp_rows = {
        '食材': 6, 'ドリンク': 7, '広告費': 8, '家賃': 9, '人件費': 10,
        'ローン返済': 11, '水道光熱費': 12, '管理費': 13, '備品': 14, '税金': 15,
    }
    actual_exp_total_row = 16
    actual_profit_row = 17

    # --- 予算 ---
    budget_sales_rows = {
        'ドリンク': 28, 'フード': 29, 'チャーム': 30, 'コース': 31, 'イベント': 32,
    }
    budget_sales_total_row = 33
    budget_exp_rows = {
        '食材': 34, 'ドリンク': 35, '販売・広告': 36, '家賃': 37, '人件費': 38,
        'ローン返済': 39, '水道光熱費': 40, '通信/衛生/管理費etc...': 41,
        '備品': 42, '税金': 43,
    }
    budget_exp_total_row = 44
    budget_profit_row = 45

    out = {
        'months': months,  # col -> ym
        'actual': {'sales': {}, 'sales_total': {}, 'expenses': {}, 'expenses_total': {}, 'profit': {}},
        'budget': {'sales': {}, 'sales_total': {}, 'expenses': {}, 'expenses_total': {}, 'profit': {}},
    }

    for col, ym in months.items():
        # actual sales
        for cat, row in actual_sales_rows.items():
            v = to_num(cell(row, col))
            if v is not None:
                out['actual']['sales'].setdefault(ym, {})[cat] = v
        v = to_num(cell(actual_sales_total_row, col))
        if v is not None: out['actual']['sales_total'][ym] = v

        # actual expenses
        for cat, row in actual_exp_rows.items():
            v = to_num(cell(row, col))
            if v is not None:
                out['actual']['expenses'].setdefault(ym, {})[cat] = v
        v = to_num(cell(actual_exp_total_row, col))
        if v is not None: out['actual']['expenses_total'][ym] = v
        v = to_num(cell(actual_profit_row, col))
        if v is not None: out['actual']['profit'][ym] = v

        # budget sales
        for cat, row in budget_sales_rows.items():
            v = to_num(cell(row, col))
            if v is not None:
                out['budget']['sales'].setdefault(ym, {})[cat] = v
        v = to_num(cell(budget_sales_total_row, col))
        if v is not None: out['budget']['sales_total'][ym] = v

        # budget expenses
        for cat, row in budget_exp_rows.items():
            v = to_num(cell(row, col))
            if v is not None:
                out['budget']['expenses'].setdefault(ym, {})[cat] = v
        v = to_num(cell(budget_exp_total_row, col))
        if v is not None: out['budget']['expenses_total'][ym] = v
        v = to_num(cell(budget_profit_row, col))
        if v is not None: out['budget']['profit'][ym] = v

    return out


def parse_db():
    d = json.load(open(DB_DUMP))
    sales_cat = {c['id']: normalize_cat(c['name']) for c in d['salesCategories']}
    exp_cat   = {c['id']: normalize_cat(c['name']) for c in d['expenseCategories']}
    db = {
        'sales_categories': sales_cat,
        'expense_categories': exp_cat,
        'sales': {},      # ym -> cat -> amount
        'expenses': {},   # ym -> cat -> amount
        'targets': d.get('monthlyTargets', []),
    }
    for r in d['monthlySales']:
        ym = r['year_month']; cat = sales_cat.get(r['category_id'], r['category_id'])
        db['sales'].setdefault(ym, {})[cat] = float(r['total'])
    for r in d['monthlyExpenses']:
        ym = r['year_month']; cat = exp_cat.get(r['category_id'], r['category_id'])
        db['expenses'].setdefault(ym, {})[cat] = float(r['total'])
    return db


def main():
    sheet = parse_sheet()
    db    = parse_db()
    result = {'sheet': sheet, 'db': db}
    with open(OUT_JSON, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Print quick summary
    print('=== Sheet months ===', sorted(set(sheet['months'].values())))
    print('=== Sheet actuals months with data ===',
          sorted(sheet['actual']['sales_total'].keys() | sheet['actual']['expenses_total'].keys()))
    print('=== DB sales months ===', sorted(db['sales'].keys()))
    print('=== DB expenses months ===', sorted(db['expenses'].keys()))
    print('=== DB targets count ===', len(db['targets']))

    # Build per-month comparison for overlapping months
    months_overlap = set()
    for ym in (set(sheet['actual']['sales_total'].keys()) |
               set(sheet['actual']['expenses_total'].keys())):
        if ym in db['sales'] or ym in db['expenses']:
            months_overlap.add(ym)
    print('=== Overlap months ===', sorted(months_overlap))

    print('\n--- Sheet actual sales by month ---')
    for ym in sorted(sheet['actual']['sales_total'].keys()):
        print(f'{ym}: total={sheet["actual"]["sales_total"][ym]:,.0f} cats={sheet["actual"]["sales"].get(ym,{})}')
    print('\n--- Sheet actual expenses by month ---')
    for ym in sorted(sheet['actual']['expenses_total'].keys()):
        print(f'{ym}: total={sheet["actual"]["expenses_total"][ym]:,.0f}')
        for cat, v in sheet['actual']['expenses'].get(ym, {}).items():
            print(f'   {cat}: {v:,.0f}')

    print('\n--- DB sales ---')
    for ym in sorted(db['sales'].keys()):
        for cat, v in db['sales'][ym].items():
            print(f'{ym} {cat}: {v:,.0f}')
    print('\n--- DB expenses ---')
    for ym in sorted(db['expenses'].keys()):
        for cat, v in db['expenses'][ym].items():
            print(f'{ym} {cat}: {v:,.0f}')

if __name__ == '__main__':
    main()
