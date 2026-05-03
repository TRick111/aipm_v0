#!/usr/bin/env python3
"""
v2: PRODUCTION DB + recipe.json + April PL actuals 統合
"""
import json, os, sys, datetime as dt, re
from collections import Counter, defaultdict
from statistics import median, mean

ROOT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報'
DATA_DIR = os.path.join(ROOT, 'data')

sales_apr = json.load(open(f'{DATA_DIR}/sales_april_PROD.json'))
sales_jan_mar = json.load(open(f'{DATA_DIR}/sales_jan_mar_PROD.json'))
sales_y25_apr = json.load(open(f'{DATA_DIR}/sales_2025_apr_PROD.json'))
pl = json.load(open(f'{DATA_DIR}/pl_2026_PROD.json'))
recipe = json.load(open(f'{DATA_DIR}/recipe.json'))
daily_summaries = json.load(open(f'{DATA_DIR}/daily_summaries_PROD.json'))
daily_reports = json.load(open(f'{DATA_DIR}/daily_reports_PROD.json'))
menu_master = json.load(open(f'{DATA_DIR}/menu_master_PROD.json'))

print(f'Sales: 4月={len(sales_apr)} 1-3月={len(sales_jan_mar)} 25/4={len(sales_y25_apr)}', file=sys.stderr)
print(f'Recipe: {len(recipe)}', file=sys.stderr)
print(f'MenuMaster: {len(menu_master)}', file=sys.stderr)

# === 月別フィルタ ===
def month_filter(sales, ym):
    return [s for s in sales if s['entryAt'][:7] == ym]

apr = sales_apr  # 全部4月
mar = month_filter(sales_jan_mar, '2026-03')
feb = month_filter(sales_jan_mar, '2026-02')
jan = month_filter(sales_jan_mar, '2026-01')
y25_apr = sales_y25_apr

# === 月次サマリ ===
def month_summary(accounts):
    if not accounts:
        return {'sales':0,'visits':0,'customers':0,'avg_per_visit':0,'avg_per_person':0,
                'reservation_share':0,'course_share':0,'avg_party_size':0}
    sales = sum(a['totalAmount'] for a in accounts)
    visits = len(accounts)
    customers = sum(a['customerCount'] for a in accounts)
    return {
        'sales': sales,
        'visits': visits,
        'customers': customers,
        'avg_per_visit': sales/visits if visits else 0,
        'avg_per_person': sales/customers if customers else 0,
        'avg_party_size': customers/visits if visits else 0,
        'reservation_share': sum(1 for a in accounts if a['hasReservation'])/visits if visits else 0,
        'course_share': sum(1 for a in accounts if a['isCourse'])/visits if visits else 0,
    }

sum_apr = month_summary(apr)
sum_mar = month_summary(mar)
sum_feb = month_summary(feb)
sum_jan = month_summary(jan)
sum_y25apr = month_summary(y25_apr)

# === 営業日 ===
def biz_days(accounts):
    return len(set(a['entryAt'][:10] for a in accounts))
bd_apr = biz_days(apr)
bd_mar = biz_days(mar)
bd_feb = biz_days(feb)
bd_jan = biz_days(jan)
bd_y25apr = biz_days(y25_apr)
print(f'Biz days: 4月={bd_apr} 3月={bd_mar} 2月={bd_feb} 1月={bd_jan} 25/4={bd_y25apr}', file=sys.stderr)

# 4月のPOS最終日
last_pos_date = max(a['entryAt'][:10] for a in apr)
print(f'Last POS date: {last_pos_date}', file=sys.stderr)

# === 日次推移 ===
day_agg = defaultdict(lambda: {'sales':0,'visits':0,'customers':0,'items':0})
for a in apr:
    d = a['entryAt'][:10]
    day_agg[d]['sales'] += a['totalAmount']
    day_agg[d]['visits'] += 1
    day_agg[d]['customers'] += a['customerCount']
    day_agg[d]['items'] += a['itemCount']
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

# === 曜日 / 時間帯 / ヒートマップ ===
weekday_agg = defaultdict(lambda: {'sales':0,'visits':0,'customers':0,'days':0})
day_seen = set()
for a in apr:
    d = a['entryAt'][:10]
    wd = dt.date.fromisoformat(d).weekday()
    weekday_agg[wd]['sales'] += a['totalAmount']
    weekday_agg[wd]['visits'] += 1
    weekday_agg[wd]['customers'] += a['customerCount']
    if (d,wd) not in day_seen:
        weekday_agg[wd]['days'] += 1
        day_seen.add((d,wd))
weekday_summary = []
for wd in range(7):
    a = weekday_agg[wd]
    label = ['月','火','水','木','金','土','日'][wd]
    weekday_summary.append({
        'weekday': label, 'wd_idx': wd,
        'sales': a['sales'], 'visits': a['visits'], 'customers': a['customers'], 'days': a['days'],
        'sales_per_day': a['sales']/a['days'] if a['days'] else 0,
        'visits_per_day': a['visits']/a['days'] if a['days'] else 0,
        'avg_per_visit': a['sales']/a['visits'] if a['visits'] else 0,
        'avg_per_person': a['sales']/a['customers'] if a['customers'] else 0,
    })

def time_bucket(hh):
    if hh < 18: return '~18時'
    if hh < 20: return '18-20時'
    if hh < 22: return '20-22時'
    if hh < 24: return '22-24時'
    return '24時~'
hour_agg = defaultdict(lambda: {'sales':0,'visits':0,'customers':0})
for a in apr:
    # entryAt は UTC (Z 終端)。JST に変換 (+9h)
    et = dt.datetime.fromisoformat(a['entryAt'].replace('Z','+00:00'))
    jst = et + dt.timedelta(hours=9)
    h = jst.hour
    b = time_bucket(h)
    hour_agg[b]['sales'] += a['totalAmount']
    hour_agg[b]['visits'] += 1
    hour_agg[b]['customers'] += a['customerCount']
bucket_order = ['~18時','18-20時','20-22時','22-24時','24時~']
hour_summary = []
for b in bucket_order:
    a = hour_agg[b]
    hour_summary.append({
        'bucket': b, 'sales': a['sales'], 'visits': a['visits'], 'customers': a['customers'],
        'avg_per_visit': a['sales']/a['visits'] if a['visits'] else 0,
        'avg_per_person': a['sales']/a['customers'] if a['customers'] else 0,
    })
heat = defaultdict(lambda: {'sales':0,'visits':0})
for a in apr:
    d = a['entryAt'][:10]
    wd = dt.date.fromisoformat(d).weekday()
    et = dt.datetime.fromisoformat(a['entryAt'].replace('Z','+00:00'))
    jst = et + dt.timedelta(hours=9)
    b = time_bucket(jst.hour)
    heat[(wd,b)]['sales'] += a['totalAmount']
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

# === 商品ランキング ===
def product_agg(accounts):
    p = defaultdict(lambda: {'qty':0,'sales':0,'visits':set(),'cat':''})
    for a in accounts:
        for it in a['items']:
            n = it['menuName']
            p[n]['qty'] += it['quantity']
            p[n]['sales'] += it['subtotal']
            p[n]['visits'].add(a['accountId'])
            p[n]['cat'] = it.get('category1') or p[n]['cat']
    out = []
    for n,v in p.items():
        out.append({
            'name': n, 'category1': v['cat'] or '',
            'qty': v['qty'], 'sales': v['sales'],
            'unique_visits': len(v['visits']),
            'price_avg': v['sales']/v['qty'] if v['qty'] else 0,
        })
    return out

prod_apr = product_agg(apr)
prod_mar = product_agg(mar)
prod_y25apr = product_agg(y25_apr)
mar_qty = {p['name']: p['qty'] for p in prod_mar}
y25_qty = {p['name']: p['qty'] for p in prod_y25apr}
for p in prod_apr:
    p['qty_mar'] = mar_qty.get(p['name'], 0)
    p['qty_diff_mom'] = p['qty'] - p['qty_mar']
    p['qty_y25apr'] = y25_qty.get(p['name'], 0)
    p['qty_diff_yoy'] = p['qty'] - p['qty_y25apr']

prod_by_qty = sorted(prod_apr, key=lambda x: -x['qty'])
prod_by_sales = sorted(prod_apr, key=lambda x: -x['sales'])

# tablecharge / no charge / 単純チャージ系を除外したランキング (商品戦略章用)
EXCLUDE_FROM_RANKING = {'tablecharge', 'No charge', 'no charge', '丸氷', 'ドリンク'}  # 'ドリンク'は単独カテゴリ名のみ表示の総称
prod_apr_excl = [p for p in prod_apr if p['name'] not in EXCLUDE_FROM_RANKING]
prod_by_qty_excl = sorted(prod_apr_excl, key=lambda x: -x['qty'])
prod_by_sales_excl = sorted(prod_apr_excl, key=lambda x: -x['sales'])

# === レシピマッピング (POS商品名 → recipe商品名) ===
# 名寄せ戦略: 完全一致 + 正規化(空白/記号除去)で再一致
def normalize(s):
    if not s: return ''
    return re.sub(r'[\s 　・/\-_（）()「」『』【】【】"\'.]','',str(s)).lower()

recipe_by_name = {r['メニュー名']: r for r in recipe if r.get('メニュー名')}
recipe_norm = {normalize(r['メニュー名']): r for r in recipe if r.get('メニュー名')}
match_results = []
matched = 0
unmatched = 0
matched_qty = 0
unmatched_qty = 0
total_qty = 0
theoretical_cost_apr = 0  # 月次理論原価
theoretical_sales_apr_matched = 0

for p in prod_apr:
    n = p['name']
    nn = normalize(n)
    r = recipe_by_name.get(n) or recipe_norm.get(nn)
    total_qty += p['qty']
    if r and r.get('原価') is not None:
        matched += 1
        matched_qty += p['qty']
        cost = r['原価'] * p['qty']
        theoretical_cost_apr += cost
        theoretical_sales_apr_matched += p['sales']
        match_results.append({
            'pos_name': n, 'recipe_name': r['メニュー名'], 'qty': p['qty'],
            'price_pos': p['price_avg'], 'price_recipe': r['売価'],
            'cost_unit': r['原価'], 'cost_rate': r['原価率'],
            'theoretical_cost_total': cost,
            'sales': p['sales'],
            '位置付け': r.get('位置付け') or '',
            'category_recipe': r.get('カテゴリ') or '',
            'matched': True,
        })
    else:
        unmatched += 1
        unmatched_qty += p['qty']
        match_results.append({
            'pos_name': n, 'recipe_name': None, 'qty': p['qty'],
            'price_pos': p['price_avg'], 'sales': p['sales'],
            'category_pos': p['category1'],
            'matched': False,
        })

match_summary = {
    'total_pos_products': len(prod_apr),
    'matched_count': matched,
    'unmatched_count': unmatched,
    'match_rate': matched/len(prod_apr) if prod_apr else 0,
    'total_qty': total_qty,
    'matched_qty': matched_qty,
    'unmatched_qty': unmatched_qty,
    'qty_match_rate': matched_qty/total_qty if total_qty else 0,
    'theoretical_cost_apr': theoretical_cost_apr,
    'matched_sales': theoretical_sales_apr_matched,
    'theoretical_cost_rate_matched': theoretical_cost_apr/theoretical_sales_apr_matched if theoretical_sales_apr_matched else 0,
}

# === 未マッチ商品の分類 (理論原価データ確認用) ===
def classify_unmatched(name, cat):
    n = name or ''
    c = cat or ''
    if n in ('tablecharge','No charge','no charge'): return 'チャージ系 (ランキング除外対象)'
    if 'コース' in n or 'CLP' in n or '飲み放題' in n: return 'コース・飲み放題'
    if 'ハイボール' in n or 'ハウスハイボール' == n: return 'ハウスハイボール (要レシピ登録)'
    if 'ウイスキー' in c or any(w in n for w in ['余市','タリスカー','グレンリベット','ワイルドターキー','イチローズ','響','山崎','白州']): return 'ウイスキー単品ボトル'
    if 'ワイン' in c or 'グラス' in c: return 'ワイン (要レシピ登録)'
    if 'ビール' in c or 'ビール' in n: return 'ビール'
    if c == 'その他' or c == '未設定' or '黒板' in n: return 'その他 (POSカテゴリ未整理)'
    return 'レシピ未登録 (要追補)'

unmatched_classification = defaultdict(lambda: {'qty':0,'sales':0,'count':0,'samples':[]})
for m in match_results:
    if m['matched']: continue
    cat = classify_unmatched(m['pos_name'], m.get('category_pos',''))
    unmatched_classification[cat]['qty'] += m['qty']
    unmatched_classification[cat]['sales'] += m['sales']
    unmatched_classification[cat]['count'] += 1
    if len(unmatched_classification[cat]['samples']) < 5:
        unmatched_classification[cat]['samples'].append(m['pos_name'])
unmatched_class_list = [
    {'category':k,'qty':v['qty'],'sales':v['sales'],'count':v['count'],'samples':v['samples']}
    for k,v in sorted(unmatched_classification.items(), key=lambda x:-x[1]['qty'])
]

# === マッチ済品目の原価率分布 (データ妥当性チェック) ===
matched_with_rates = [m for m in match_results if m['matched'] and m.get('cost_rate')]
cost_rate_buckets = {'~10%':0,'10-20%':0,'20-30%':0,'30-40%':0,'40-50%':0,'50%+':0}
for m in matched_with_rates:
    r = m['cost_rate']
    if r < 0.10: cost_rate_buckets['~10%'] += 1
    elif r < 0.20: cost_rate_buckets['10-20%'] += 1
    elif r < 0.30: cost_rate_buckets['20-30%'] += 1
    elif r < 0.40: cost_rate_buckets['30-40%'] += 1
    elif r < 0.50: cost_rate_buckets['40-50%'] += 1
    else: cost_rate_buckets['50%+'] += 1

# === POS価格 vs レシピ売価 不一致の検出 ===
price_mismatches = []
for m in match_results:
    if not m['matched']: continue
    pp = m.get('price_pos') or 0
    rp = m.get('price_recipe') or 0
    if rp and pp and abs(pp-rp) > 50:  # 50円以上の差
        price_mismatches.append({
            'name': m['pos_name'], 'pos_price': pp, 'recipe_price': rp,
            'diff': pp-rp, 'qty': m['qty'],
        })
price_mismatches = sorted(price_mismatches, key=lambda x:-abs(x['diff']))[:15]
print(f'Match rate: {match_summary["match_rate"]*100:.1f}% (qty {match_summary["qty_match_rate"]*100:.1f}%)', file=sys.stderr)
print(f'Theoretical cost: ¥{theoretical_cost_apr:,.0f}', file=sys.stderr)

# === カテゴリ別 ===
cat_agg = defaultdict(lambda: {'qty':0,'sales':0})
for p in prod_apr:
    cat_agg[p['category1']]['qty'] += p['qty']
    cat_agg[p['category1']]['sales'] += p['sales']
total_sales = sum(c['sales'] for c in cat_agg.values()) or 1
cat_summary = []
for c,v in sorted(cat_agg.items(), key=lambda x: -x[1]['sales']):
    cat_summary.append({
        'category': c or '(未分類)', 'qty': v['qty'], 'sales': v['sales'],
        'sales_share': v['sales']/total_sales,
    })
cat_agg_mar = defaultdict(lambda: {'qty':0,'sales':0})
for p in prod_mar:
    cat_agg_mar[p['category1']]['qty'] += p['qty']
    cat_agg_mar[p['category1']]['sales'] += p['sales']
mar_total = sum(c['sales'] for c in cat_agg_mar.values()) or 1
mar_share = {c: v['sales']/mar_total for c,v in cat_agg_mar.items()}
for c in cat_summary:
    key = '' if c['category']=='(未分類)' else c['category']
    c['sales_share_mar'] = mar_share.get(key, 0)
    c['share_diff'] = c['sales_share'] - c['sales_share_mar']

# === 客単価分布 ===
single_pp = [a['totalAmount']/a['customerCount'] for a in apr if a['customerCount']>0]
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
bins = [0,2000,3000,4000,5000,6000,7000,8000,10000,15000,20000,30000,50000,1e9]
labels = ['~2000','2-3k','3-4k','4-5k','5-6k','6-7k','7-8k','8-10k','10-15k','15-20k','20-30k','30-50k','50k+']
hist = [0]*len(labels)
for v in single_pp:
    for i in range(len(bins)-1):
        if bins[i] <= v < bins[i+1]:
            hist[i] += 1; break
spp_hist = [{'bucket':labels[i],'count':hist[i]} for i in range(len(labels))]

# === 注文構造 ===
def items_per_visit_stats(accounts):
    if not accounts: return {'avg_items':0,'drink_2plus_share':0,'drink_visits':0}
    avg_items = mean(a['itemCount'] for a in accounts)
    over2 = 0; total = 0
    for a in accounts:
        dq = sum(it['quantity'] for it in a['items'] if (it.get('category1') or '').strip()=='ドリンク')
        if dq>0:
            total += 1
            if dq >= 2: over2 += 1
    return {'avg_items': avg_items, 'drink_visits': total,
            'drink_2plus_share': over2/total if total else 0}
ipv_apr = items_per_visit_stats(apr)
ipv_mar = items_per_visit_stats(mar)

# === セグメント ===
def split_segments(accounts):
    out = {'reservation':{'visits':0,'sales':0,'customers':0},
           'walkin':{'visits':0,'sales':0,'customers':0},
           'course':{'visits':0,'sales':0,'customers':0},
           'alacarte':{'visits':0,'sales':0,'customers':0}}
    for a in accounts:
        seg = 'reservation' if a['hasReservation'] else 'walkin'
        out[seg]['visits'] += 1; out[seg]['sales'] += a['totalAmount']; out[seg]['customers'] += a['customerCount']
        seg2 = 'course' if a['isCourse'] else 'alacarte'
        out[seg2]['visits'] += 1; out[seg2]['sales'] += a['totalAmount']; out[seg2]['customers'] += a['customerCount']
    return out
seg_apr = split_segments(apr)
seg_mar = split_segments(mar)

# === 客層 (人数別) ===
party_buckets = {'1人':0,'2人':0,'3-4人':0,'5-9人':0,'10-19人':0,'20人+':0}
party_sales = {k:0 for k in party_buckets}
for a in apr:
    n = a['customerCount']
    k = ('1人' if n==1 else '2人' if n==2 else '3-4人' if n<=4 else '5-9人' if n<=9 else '10-19人' if n<=19 else '20人+')
    party_buckets[k] += 1
    party_sales[k] += a['totalAmount']
party_summary = [{'bucket':k,'visits':party_buckets[k],'sales':party_sales[k]} for k in party_buckets]

# === PL 月次集計 (PROD) ===
pl_sales_cats = {c['id']: c['name'] for c in pl['sales_categories']}
pl_exp_cats = {c['id']: c for c in pl['expense_categories']}

pl_monthly = defaultdict(lambda: {'sales': defaultdict(float), 'expenses': defaultdict(float),
                                   'sales_total':0,'expenses_total':0,'profit':0})
for r in pl['daily_sales']:
    m = r['date'][:7]
    cat = pl_sales_cats.get(r['categoryId'], '?')
    pl_monthly[m]['sales'][cat] += r['amount']
    pl_monthly[m]['sales_total'] += r['amount']
for r in pl['daily_expenses']:
    m = r['date'][:7]
    cat = pl_exp_cats.get(r['categoryId'], {}).get('name','?')
    pl_monthly[m]['expenses'][cat] += r['amount']
    pl_monthly[m]['expenses_total'] += r['amount']
for m in pl_monthly:
    pl_monthly[m]['profit'] = pl_monthly[m]['sales_total'] - pl_monthly[m]['expenses_total']

pl_april = pl_monthly.get('2026-04', {})

# === PL 1-3月: スプレッドシート (新PL管理（移管前）) を採用 ===
# 田中さん指示: 1-3月はスプレッドシート、4月はDB
pl_jan = {
    'sales_total': 2642718,
    'sales': {'ドリンク': 1250018, 'フード': 846000, 'コース': 64500, 'イベント': 482200},
    'expenses_total': 2352939,
    'expenses': {
        '食材': 178182, 'ドリンク': 203250, '広告費': 22000,
        '家賃': 1112859, '人件費': 347258, 'ローン返済': 169154,
        '水道光熱費': 79854, '管理費': 194481, '備品': 45901, '税金': 0,
    },
    'profit': 2642718 - 2352939,
    'source': 'spreadsheet',
}
pl_feb = {
    'sales_total': 2667760,
    'sales': {'ドリンク': 1510960, 'フード': 461900, 'コース': 413000, 'イベント': 281900},
    'expenses_total': 2832178,
    'expenses': {
        '食材': 210952, 'ドリンク': 420616, '広告費': 103180,
        '家賃': 1112859, '人件費': 414487, 'ローン返済': 169221,
        '水道光熱費': 91609, '管理費': 250617, '備品': 58637, '税金': 0,
    },
    'profit': 2667760 - 2832178,
    'source': 'spreadsheet',
}
pl_mar = {
    'sales_total': 2787400,
    'sales': {'ドリンク': 1479150, 'フード': 568250, 'コース': 269500, 'イベント': 470500},
    'expenses_total': None,  # 3月費用は未入力 (シート上 #N/A)
    'expenses': {},
    'profit': None,
    'source': 'spreadsheet (sales only; expenses #N/A)',
}
# 4月はDBデータをそのまま使用 (pl_april に source 情報を追加)
pl_april['source'] = 'production DB (some categories not yet entered)'

# === 4月予算 (本部サポートシートから既知) ===
budget_apr = {
    'sales_total': 3400000,
    'expenses_total': 3554556,
    'profit': -154556,
    'CLP人件費': 600000,
    'sales_breakdown': {'ドリンク':1700000,'フード':680000,'チャーム':340000,'コース':578000,'イベント':102000},
}

# === 主因分解 (営業日換算) ===
visits_per_day_mar = sum_mar['visits']/bd_mar
visits_expected = visits_per_day_mar * bd_apr
visits_diff = sum_apr['visits'] - visits_expected
visits_contrib = visits_diff * sum_mar['avg_per_visit']
unit_contrib = sum_apr['visits'] * (sum_apr['avg_per_visit'] - sum_mar['avg_per_visit'])

# === AI日報 ===
ai_reports_apr = []
for r in daily_reports:
    answers_dict = {a['question']: a['summary'] for a in r['answers']}
    ai_reports_apr.append({
        'date': r['date'],
        'member': r['member'],
        'guests': answers_dict.get('①来客特徴') or answers_dict.get('来客特徴') or '',
        'improvements': answers_dict.get('②改善ポイント') or answers_dict.get('改善ポイント') or '',
        'all_answers': answers_dict,
    })

# === Output ===
out = {
    'meta': {
        'store': 'BAR FIVE Arrows (BFA / FIVE Arrows)',
        'store_code': 'bfa-001',
        'period': '2026-04',
        'period_label': '2026年4月',
        'data_source': 'Production DB (ep-rough-bird) + Recipe Sheet 1WjJaogeoRzA3BfO8ldohym5lywniVBApg1BxtINs8CA',
        'generated_at': dt.datetime.now().isoformat(timespec='seconds'),
        'business_days': bd_apr,
        'business_days_mar': bd_mar,
        'last_pos_date': last_pos_date,
        'data_freshness_note': f'POS最終日 {last_pos_date} (4/27-30 未連携の可能性 → 月末売上の見落とし) ',
        'pl_data_status': 'April PL actuals: PROD DBから取得 (一部費目: 人件費・水道光熱費・ローン返済・税金は未入力)',
        'recipe_match_rate': f'品目数 {match_summary["match_rate"]*100:.1f}% / 出数 {match_summary["qty_match_rate"]*100:.1f}%',
    },
    'monthly_summary': {
        'apr': sum_apr, 'mar': sum_mar, 'feb': sum_feb, 'jan': sum_jan, 'y25_apr': sum_y25apr,
    },
    'biz_days': {'apr': bd_apr, 'mar': bd_mar, 'feb': bd_feb, 'jan': bd_jan, 'y25_apr': bd_y25apr},
    'main_driver': {
        'visits_diff_vs_expected': visits_diff,
        'visits_contrib': visits_contrib,
        'unit_contrib': unit_contrib,
        'driver': '客数減' if abs(visits_contrib) > abs(unit_contrib) else '客単価減',
    },
    'daily': daily,
    'weekday_summary': weekday_summary,
    'hour_summary': hour_summary,
    'heatmap': heatmap,
    'products': {
        'top_qty_30': prod_by_qty[:30],
        'top_sales_30': prod_by_sales[:30],
        'top_qty_30_excl': prod_by_qty_excl[:30],   # tablecharge等を除外
        'top_sales_30_excl': prod_by_sales_excl[:30],
        'all': prod_apr,
        'excluded_from_ranking': sorted(EXCLUDE_FROM_RANKING),
    },
    'category_share': cat_summary,
    'avg_per_person_dist': {'stats': spp_stats, 'histogram': spp_hist},
    'items_per_visit': {'apr': ipv_apr, 'mar': ipv_mar},
    'segments': {'apr': seg_apr, 'mar': seg_mar},
    'party_size': party_summary,
    'pl': {
        'monthly_actuals': dict(pl_monthly),  # DB-derived
        'apr': pl_april,                       # DB
        'jan': pl_jan, 'feb': pl_feb, 'mar': pl_mar,  # spreadsheet (Tanaka指示)
        'budget_april': budget_apr,
    },
    'recipe_match': {
        'summary': match_summary,
        'matched': [m for m in match_results if m['matched']],
        'unmatched': [m for m in match_results if not m['matched']],
        'unmatched_classification': unmatched_class_list,
        'cost_rate_buckets': cost_rate_buckets,
        'price_mismatches': price_mismatches,
    },
    'theoretical_cost': {
        'apr_total': theoretical_cost_apr,
        'apr_matched_sales': theoretical_sales_apr_matched,
        'theoretical_cost_rate_matched': match_summary['theoretical_cost_rate_matched'],
        'pl_food_drink_apr': pl_april.get('expenses', {}).get('食材',0) + pl_april.get('expenses', {}).get('ドリンク',0) if pl_april else 0,
    },
    'ai_reports': ai_reports_apr,
    'daily_summaries': [{'date':d['date'],'content':d['content']} for d in daily_summaries],
}

OUT_PATH = os.path.join(DATA_DIR, 'analytics2.json')
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, default=str)
print(f'[ok] {OUT_PATH} ({os.path.getsize(OUT_PATH)/1024:.1f} KB)', file=sys.stderr)

# Verification
print(json.dumps({
    'apr_summary': sum_apr,
    'mar_summary': sum_mar,
    'pl_april_sales': pl_april.get('sales_total') if pl_april else None,
    'pl_april_expenses': pl_april.get('expenses_total') if pl_april else None,
    'pl_april_breakdown': dict(pl_april.get('expenses', {})) if pl_april else None,
    'theoretical_cost_apr': theoretical_cost_apr,
    'pl_food+drink_apr': pl_april.get('expenses',{}).get('食材',0) + pl_april.get('expenses',{}).get('ドリンク',0) if pl_april else 0,
    'match_rate_qty': f'{match_summary["qty_match_rate"]*100:.1f}%',
}, ensure_ascii=False, indent=2))
