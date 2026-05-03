#!/usr/bin/env python3
"""
BFA 2026年4月 月報 - 分析計算スクリプト
入力: ~/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv (POS明細)
      ~/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/DailyReport.csv (AI日報)
      data/pl_*.json (Spreadsheetキャッシュ)
出力: data/analytics.json (HTML側で読込)
"""
import csv, json, os, sys, datetime as dt
from collections import Counter, defaultdict
from statistics import median, mean

ROOT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報'
DATA_DIR = os.path.join(ROOT, 'data')
RAW_CSV = '/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv'
DR_CSV  = '/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/DailyReport.csv'

os.makedirs(DATA_DIR, exist_ok=True)

# === 1. POS明細を読む（全月） ===
def parse_dt(s):
    if not s: return None
    return dt.datetime.fromisoformat(s)

raw = []
with open(RAW_CSV, encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        raw.append(row)

print(f'[load] rawdata.csv lines={len(raw)}', file=sys.stderr)

# === 2. 当月(4月) と 前月(3月)、前年同月(2025-04)、前々月(2月) のサブセットを抽出 ===
def month_filter(rows, ym):
    return [r for r in rows if r['entry_at'][:7] == ym]

apr = month_filter(raw, '2026-04')
mar = month_filter(raw, '2026-03')
feb = month_filter(raw, '2026-02')
y2025_apr = month_filter(raw, '2025-04')
print(f'  2026-04: {len(apr)} 2026-03: {len(mar)} 2026-02: {len(feb)} 2025-04: {len(y2025_apr)}', file=sys.stderr)

# === 3. 会計単位の集計（accountごとに最新値を取る） ===
def aggregate_accounts(rows):
    """rowは商品明細単位。会計(account_id)単位にロールアップ。"""
    accs = {}
    for r in rows:
        aid = r['account_id']
        if aid not in accs:
            accs[aid] = {
                'account_id': aid,
                'entry_at': r['entry_at'],
                'exit_at': r['exit_at'],
                'day_of_week': r['day_of_week'],
                'account_total': float(r['account_total'] or 0),
                'customer_count': int(r['customer_count'] or 0),
                'item_count': int(r['item_count'] or 0),
                'has_reservation': r['has_reservation'] == 't',
                'is_course': r['is_course'] == 't',
                'items': [],
            }
        accs[aid]['items'].append({
            'menu_name': r['menu_name'],
            'price': float(r['price'] or 0),
            'quantity': int(r['quantity'] or 0),
            'subtotal': float(r['subtotal'] or 0),
            'category1': r.get('category1','') or '',
            'ordered_at': r.get('ordered_at',''),
        })
    return list(accs.values())

acc_apr = aggregate_accounts(apr)
acc_mar = aggregate_accounts(mar)
acc_feb = aggregate_accounts(feb)
acc_y25apr = aggregate_accounts(y2025_apr)
print(f'  Accounts: 4月={len(acc_apr)} 3月={len(acc_mar)} 2月={len(acc_feb)} 25/4={len(acc_y25apr)}', file=sys.stderr)

# === 4. 月次サマリ計算 ===
def month_summary(accounts):
    if not accounts:
        return {'sales':0,'visits':0,'customers':0,'avg_per_visit':0,'avg_per_person':0,
                'reservation_share':0,'course_share':0,'avg_party_size':0}
    sales = sum(a['account_total'] for a in accounts)
    visits = len(accounts)
    customers = sum(a['customer_count'] for a in accounts)
    return {
        'sales': sales,
        'visits': visits,
        'customers': customers,
        'avg_per_visit': sales/visits if visits else 0,
        'avg_per_person': sales/customers if customers else 0,
        'avg_party_size': customers/visits if visits else 0,
        'reservation_share': sum(1 for a in accounts if a['has_reservation'])/visits if visits else 0,
        'course_share': sum(1 for a in accounts if a['is_course'])/visits if visits else 0,
    }

sum_apr = month_summary(acc_apr)
sum_mar = month_summary(acc_mar)
sum_feb = month_summary(acc_feb)
sum_y25apr = month_summary(acc_y25apr)

# === 5. 日次推移 (4月) ===
day_agg = defaultdict(lambda: {'sales':0,'visits':0,'customers':0,'items':0})
for a in acc_apr:
    d = a['entry_at'][:10]
    day_agg[d]['sales'] += a['account_total']
    day_agg[d]['visits'] += 1
    day_agg[d]['customers'] += a['customer_count']
    day_agg[d]['items'] += a['item_count']

daily = []
for d in sorted(day_agg):
    a = day_agg[d]
    weekday = ['月','火','水','木','金','土','日'][dt.date.fromisoformat(d).weekday()]
    daily.append({
        'date': d, 'weekday': weekday,
        'sales': a['sales'], 'visits': a['visits'],
        'customers': a['customers'], 'items': a['items'],
        'avg_per_visit': a['sales']/a['visits'] if a['visits'] else 0,
        'avg_per_person': a['sales']/a['customers'] if a['customers'] else 0,
    })

# === 6. 曜日別 / 時間帯別 / 曜日x時間帯 ===
weekday_agg = defaultdict(lambda: {'sales':0,'visits':0,'customers':0,'days':0})
day_seen = set()
for a in acc_apr:
    d = a['entry_at'][:10]
    wd = dt.date.fromisoformat(d).weekday()
    weekday_agg[wd]['sales'] += a['account_total']
    weekday_agg[wd]['visits'] += 1
    weekday_agg[wd]['customers'] += a['customer_count']
    if (d,wd) not in day_seen:
        weekday_agg[wd]['days'] += 1
        day_seen.add((d,wd))
weekday_summary = []
for wd in range(7):
    a = weekday_agg[wd]
    label = ['月','火','水','木','金','土','日'][wd]
    weekday_summary.append({
        'weekday': label, 'wd_idx': wd,
        'sales': a['sales'], 'visits': a['visits'], 'customers': a['customers'],
        'days': a['days'],
        'sales_per_day': a['sales']/a['days'] if a['days'] else 0,
        'visits_per_day': a['visits']/a['days'] if a['days'] else 0,
        'avg_per_visit': a['sales']/a['visits'] if a['visits'] else 0,
        'avg_per_person': a['sales']/a['customers'] if a['customers'] else 0,
    })

# 時間帯別: 入店時刻
def time_bucket(hh):
    if hh < 18: return '~18時'
    if hh < 20: return '18-20時'
    if hh < 22: return '20-22時'
    if hh < 24: return '22-24時'
    return '24時~'
hour_agg = defaultdict(lambda: {'sales':0,'visits':0,'customers':0})
for a in acc_apr:
    h = int(a['entry_at'][11:13])
    b = time_bucket(h)
    hour_agg[b]['sales'] += a['account_total']
    hour_agg[b]['visits'] += 1
    hour_agg[b]['customers'] += a['customer_count']

bucket_order = ['~18時','18-20時','20-22時','22-24時','24時~']
hour_summary = []
for b in bucket_order:
    a = hour_agg[b]
    hour_summary.append({
        'bucket': b,
        'sales': a['sales'], 'visits': a['visits'], 'customers': a['customers'],
        'avg_per_visit': a['sales']/a['visits'] if a['visits'] else 0,
        'avg_per_person': a['sales']/a['customers'] if a['customers'] else 0,
    })

# 曜日x時間帯ヒートマップ
heat = defaultdict(lambda: {'sales':0,'visits':0})
for a in acc_apr:
    d = a['entry_at'][:10]
    wd = dt.date.fromisoformat(d).weekday()
    h = int(a['entry_at'][11:13])
    b = time_bucket(h)
    heat[(wd,b)]['sales'] += a['account_total']
    heat[(wd,b)]['visits'] += 1
heatmap = []
for wd in range(7):
    for b in bucket_order:
        a = heat[(wd,b)]
        heatmap.append({
            'weekday': ['月','火','水','木','金','土','日'][wd],
            'wd_idx': wd, 'bucket': b,
            'sales': a['sales'], 'visits': a['visits'],
        })

# === 7. 商品ランキング (4月) ===
def product_agg(accounts):
    p = defaultdict(lambda: {'qty':0,'sales':0,'visits':set(),'cat':''})
    for a in accounts:
        for it in a['items']:
            n = it['menu_name']
            p[n]['qty'] += it['quantity']
            p[n]['sales'] += it['subtotal']
            p[n]['visits'].add(a['account_id'])
            p[n]['cat'] = it['category1'] or p[n]['cat']
    out = []
    for n,v in p.items():
        out.append({
            'name': n, 'category1': v['cat'],
            'qty': v['qty'], 'sales': v['sales'],
            'unique_visits': len(v['visits']),
            'price_avg': v['sales']/v['qty'] if v['qty'] else 0,
        })
    return out

prod_apr = product_agg(acc_apr)
prod_mar = product_agg(acc_mar)
prod_y25apr = product_agg(acc_y25apr)

# Sort
prod_by_qty   = sorted(prod_apr, key=lambda x: -x['qty'])
prod_by_sales = sorted(prod_apr, key=lambda x: -x['sales'])

# 前月比 (3月との出数差)
mar_qty = {p['name']: p['qty'] for p in prod_mar}
y25_qty = {p['name']: p['qty'] for p in prod_y25apr}
for p in prod_apr:
    p['qty_mar'] = mar_qty.get(p['name'], 0)
    p['qty_diff_mom'] = p['qty'] - p['qty_mar']
    p['qty_y25apr'] = y25_qty.get(p['name'], 0)
    p['qty_diff_yoy'] = p['qty'] - p['qty_y25apr']

# === 8. カテゴリ別構成 ===
cat_agg = defaultdict(lambda: {'qty':0,'sales':0})
for p in prod_apr:
    cat_agg[p['category1']]['qty'] += p['qty']
    cat_agg[p['category1']]['sales'] += p['sales']
total_sales = sum(c['sales'] for c in cat_agg.values()) or 1
cat_summary = []
for c,v in sorted(cat_agg.items(), key=lambda x: -x[1]['sales']):
    cat_summary.append({
        'category': c or '(未分類)',
        'qty': v['qty'], 'sales': v['sales'],
        'sales_share': v['sales']/total_sales,
    })

# 同様に3月
cat_agg_mar = defaultdict(lambda: {'qty':0,'sales':0})
for p in prod_mar:
    cat_agg_mar[p['category1']]['qty'] += p['qty']
    cat_agg_mar[p['category1']]['sales'] += p['sales']
mar_total_sales = sum(c['sales'] for c in cat_agg_mar.values()) or 1
cat_summary_mar = {c: v['sales']/mar_total_sales for c,v in cat_agg_mar.items()}
for c in cat_summary:
    c['sales_share_mar'] = cat_summary_mar.get(c['category'], 0) if c['category'] != '(未分類)' else cat_summary_mar.get('', 0)
    c['share_diff'] = c['sales_share'] - c['sales_share_mar']

# === 9. 客単価分布 (4月) ===
single_pp = [a['account_total']/a['customer_count'] for a in acc_apr if a['customer_count']>0]
single_pp_sorted = sorted(single_pp)
def percentile(arr, p):
    if not arr: return 0
    k = (len(arr)-1)*p
    f = int(k); c = min(f+1, len(arr)-1)
    return arr[f] + (arr[c]-arr[f])*(k-f)
spp_stats = {
    'mean': mean(single_pp) if single_pp else 0,
    'median': median(single_pp) if single_pp else 0,
    'p25': percentile(single_pp_sorted, 0.25),
    'p75': percentile(single_pp_sorted, 0.75),
    'p90': percentile(single_pp_sorted, 0.90),
    'min': min(single_pp) if single_pp else 0,
    'max': max(single_pp) if single_pp else 0,
}

# 単価ヒストグラム (1000円刻み)
bins = [0,2000,3000,4000,5000,6000,7000,8000,10000,15000,20000,30000,50000,1e9]
labels = ['~2000','2-3k','3-4k','4-5k','5-6k','6-7k','7-8k','8-10k','10-15k','15-20k','20-30k','30-50k','50k+']
hist = [0]*len(labels)
for v in single_pp:
    for i in range(len(bins)-1):
        if bins[i] <= v < bins[i+1]:
            hist[i] += 1; break
spp_hist = [{'bucket':labels[i],'count':hist[i]} for i in range(len(labels))]

# === 10. 注文点数 / ドリンク2杯目以上比率 ===
def items_per_visit_stats(accounts):
    if not accounts: return {'avg_items':0,'drink_2plus':0}
    avg_items = mean(a['item_count'] for a in accounts)
    # ドリンク2杯目: ドリンクcategory1の合計qtyが2以上の visit
    over2 = 0
    total = 0
    for a in accounts:
        dq = sum(it['quantity'] for it in a['items'] if (it['category1'] or '').strip()=='ドリンク')
        if dq>0:
            total += 1
            if dq >= 2: over2 += 1
    return {
        'avg_items': avg_items,
        'drink_visits': total,
        'drink_2plus_share': over2/total if total else 0,
    }
ipv_apr = items_per_visit_stats(acc_apr)
ipv_mar = items_per_visit_stats(acc_mar)

# === 11. 予約 vs ウォークイン / コース vs 単品 売上構造 ===
def split_segments(accounts):
    out = {'reservation':{'visits':0,'sales':0,'customers':0},
           'walkin':{'visits':0,'sales':0,'customers':0},
           'course':{'visits':0,'sales':0,'customers':0},
           'alacarte':{'visits':0,'sales':0,'customers':0}}
    for a in accounts:
        seg = 'reservation' if a['has_reservation'] else 'walkin'
        out[seg]['visits'] += 1
        out[seg]['sales'] += a['account_total']
        out[seg]['customers'] += a['customer_count']
        seg2 = 'course' if a['is_course'] else 'alacarte'
        out[seg2]['visits'] += 1
        out[seg2]['sales'] += a['account_total']
        out[seg2]['customers'] += a['customer_count']
    return out
seg_apr = split_segments(acc_apr)
seg_mar = split_segments(acc_mar)

# === 12. 大人数(団体)対応 ===
party_dist = Counter()
for a in acc_apr:
    party_dist[a['customer_count']] += 1
party_buckets = {'1人':0,'2人':0,'3-4人':0,'5-9人':0,'10-19人':0,'20人+':0}
party_sales = {k:0 for k in party_buckets}
for a in acc_apr:
    n = a['customer_count']
    k = ('1人' if n==1 else '2人' if n==2 else '3-4人' if n<=4 else '5-9人' if n<=9 else '10-19人' if n<=19 else '20人+')
    party_buckets[k] += 1
    party_sales[k] += a['account_total']
party_summary = [{'bucket':k,'visits':party_buckets[k],'sales':party_sales[k]} for k in party_buckets]

# === 13. AI日報 ===
dr_rows = []
with open(DR_CSV, encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        dr_rows.append(row)

# 日別の特徴/改善ポイントを単純列挙、後でLLM要約せず生のままHTMLに含める
ai_reports = []
for row in dr_rows:
    ai_reports.append({
        'date': row['営業日'],
        'author': row['入力者氏名'],
        'guests': row['①来客特徴'],
        'improvements': row['②改善ポイント'],
    })

# === 14. PL データ (Spreadsheetからキャッシュ) ===
# 既に取得した1月-3月の実績を組み込む
pl_actuals = {
    '2026-01': {
        'sales': {'ドリンク': 1250018, 'フード': 846000, 'コース': 64500, 'イベント': 482200},
        'sales_total': 2642718,
        'expenses': {'食材': 178182, 'ドリンク': 203250, '広告費': 22000, '家賃': 1112859, '人件費': 347258, 'ローン返済': 169154, '水道光熱費': 79854, '管理費': 194481, '備品': 45901, '税金': 0},
        'expenses_total': 2352939,
        'profit': 289779,  # 売上 - 費用 (CLP人件費除く)
    },
    '2026-02': {
        'sales': {'ドリンク': 1510960, 'フード': 461900, 'コース': 413000, 'イベント': 281900},
        'sales_total': 2667760,
        'expenses': {'食材': 210952, 'ドリンク': 420616, '広告費': 103180, '家賃': 1112859, '人件費': 414487, 'ローン返済': 169221, '水道光熱費': 91609, '管理費': 250617, '備品': 58637, '税金': 0},
        'expenses_total': 2832178,
        'profit': -164418,
    },
    '2026-03': {
        'sales': {'ドリンク': 1479150, 'フード': 568250, 'コース': 269500, 'イベント': 470500},
        'sales_total': 2787400,
        'expenses': None,  # データ未入力
        'expenses_total': None,
        'profit': None,
    },
}
pl_budget_apr = {
    'sales': {'ドリンク': 1700000, 'フード': 680000, 'チャーム': 340000, 'コース': 578000, 'イベント': 102000},
    'sales_total': 3400000,
    'expenses': {'食材': 340000, 'ドリンク': 408000, '販売・広告': 238000, '家賃': 1134859, '人件費': 782000, 'ローン返済': 150000, '水道光熱費': 136000, '通信/衛生/管理費': 330000, '備品': 22697, '税金': 13000},
    'expenses_total': 3554556,
    'profit': -154556,
    'CLP人件費': 600000,
    'profit_clp': -754556,
}

# === 15. 4月のPOSベース売上カテゴリ集計 (PL代替指標) ===
# カテゴリ別売上 (POS)
pos_cat = defaultdict(float)
for p in prod_apr:
    pos_cat[p['category1']] += p['sales']

pos_cat_apr = dict(pos_cat)

# === 16. 営業日数 ===
business_days_apr = len(set(a['entry_at'][:10] for a in acc_apr))
business_days_mar = len(set(a['entry_at'][:10] for a in acc_mar))

# === 出力 ===
out = {
    'meta': {
        'store': 'BAR FIVE Arrows (BFA)',
        'store_code': 'bfa-001',
        'period': '2026-04',
        'period_label': '2026年4月',
        'generated_at': dt.datetime.now().isoformat(timespec='seconds'),
        'business_days': business_days_apr,
        'business_days_mar': business_days_mar,
        'data_sources': {
            'pos': 'rawdata.csv (Stock/週報/1_input/BFA)',
            'ai_report': 'DailyReport.csv (Stock/週報/1_input/BFA)',
            'pl_past': 'Spreadsheet 新PL管理（移管前）2026-01,02 actuals + 03 sales',
            'pl_apr_actual': 'NOT AVAILABLE (sheet shows blank/N/A as of 2026-05-04)',
            'pl_apr_budget': 'Spreadsheet 新PL管理（移管前）',
            'recipe': 'NOT AVAILABLE — 商品一覧シート所在確認中 (BL-0082 question)',
        },
    },
    'monthly_summary': {
        'apr': sum_apr, 'mar': sum_mar, 'feb': sum_feb, 'y25_apr': sum_y25apr,
    },
    'daily': daily,
    'weekday_summary': weekday_summary,
    'hour_summary': hour_summary,
    'heatmap': heatmap,
    'products': {
        'top_qty_30': prod_by_qty[:30],
        'top_sales_30': prod_by_sales[:30],
        'all': prod_apr,
    },
    'category_share': cat_summary,
    'avg_per_person_dist': {
        'stats': spp_stats,
        'histogram': spp_hist,
    },
    'items_per_visit': {
        'apr': ipv_apr, 'mar': ipv_mar,
    },
    'segments': {
        'apr': seg_apr, 'mar': seg_mar,
    },
    'party_size': party_summary,
    'pl': {
        'actuals_2026': pl_actuals,
        'budget_april': pl_budget_apr,
        'pos_category_april': pos_cat_apr,
    },
    'ai_reports': ai_reports,
}

OUT_PATH = os.path.join(DATA_DIR, 'analytics.json')
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, default=str)
print(f'[ok] {OUT_PATH} bytes={os.path.getsize(OUT_PATH)}', file=sys.stderr)

# Print summary to stdout for human verification
import json as _j
print(_j.dumps({
    'apr': sum_apr,
    'mar': sum_mar,
    'mom_sales_pct': (sum_apr['sales']/sum_mar['sales']-1)*100 if sum_mar['sales'] else 0,
    'mom_app_pct': (sum_apr['avg_per_person']/sum_mar['avg_per_person']-1)*100 if sum_mar['avg_per_person'] else 0,
    'business_days_apr': business_days_apr,
    'business_days_mar': business_days_mar,
    'top5_qty': [(p['name'], p['qty']) for p in prod_by_qty[:5]],
    'top5_sales': [(p['name'], int(p['sales'])) for p in prod_by_sales[:5]],
    'cat_share_top5': [(c['category'], round(c['sales_share']*100,1)) for c in cat_summary[:5]],
}, ensure_ascii=False, indent=2))
