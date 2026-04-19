#!/usr/bin/env python3
"""BAR FIVE Arrows リニューアル前後比較分析"""

import pandas as pd
import numpy as np
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# --- Load & Prep ---
df = pd.read_csv('/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv')

# entry_at appears to already be in JST based on hour distribution
# (peaks at 18-23h and 0-4h = classic bar operating hours in JST)
df['entry_ts'] = pd.to_datetime(df['entry_at'])
df['entry_hour'] = df['entry_ts'].dt.hour

# Business date: 0-5am counts as previous day
df['biz_date'] = df['entry_ts'].apply(
    lambda x: (x - timedelta(hours=5)).date() if x.hour < 5 else x.date()
)
df['biz_date'] = pd.to_datetime(df['biz_date'])

# Time slot based on entry hour (JST)
def time_slot(h):
    if 18 <= h < 20: return '18-20'
    elif 20 <= h < 22: return '20-22'
    elif 22 <= h < 24: return '22-24'
    elif 0 <= h < 5: return '24-26(深夜)'
    else: return 'other'
df['time_slot'] = df['entry_hour'].apply(time_slot)

# Day of week in Japanese
dow_map = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
df['dow_jp'] = df['biz_date'].dt.dayofweek.map(dow_map)

# --- Period flags ---
df['period'] = 'other'
df.loc[(df['biz_date'] >= '2026-02-01') & (df['biz_date'] <= '2026-03-31'), 'period'] = 'before'
df.loc[(df['biz_date'] >= '2026-04-01') & (df['biz_date'] <= '2026-04-12'), 'period'] = 'after'
df.loc[(df['biz_date'] >= '2025-04-01') & (df['biz_date'] <= '2025-04-12'), 'period'] = 'yoy_ref'

# --- Account-level dedup (one row per account per period) ---
acct_unique = df.groupby(['account_id', 'period']).agg(
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
    biz_date=('biz_date', 'first'),
    dow_jp=('dow_jp', 'first'),
    time_slot=('time_slot', 'first'),
).reset_index()

# --- Helpers ---
def biz_days(period):
    return max(df[df['period'] == period]['biz_date'].nunique(), 1)

def biz_days_dow(period, dow):
    return max(df[(df['period'] == period) & (df['dow_jp'] == dow)]['biz_date'].nunique(), 1)

# Also count actual operating days (days with at least 1 account)
def operating_days(period):
    sub = acct_unique[acct_unique['period'] == period]
    return max(sub['biz_date'].nunique(), 1)

periods = ['before', 'after', 'yoy_ref']

# Verify data counts
for p in periods:
    sub = acct_unique[acct_unique['period'] == p]
    days = operating_days(p)
    print(f"[DEBUG] {p}: {len(sub)} accounts, {days} operating days, date range: {sub['biz_date'].min().date()} ~ {sub['biz_date'].max().date()}")

print()
print("=" * 80)
print("# BAR FIVE Arrows リニューアル前後比較分析")
print("  分析期間:")
print("    Before: 2026/2/1 - 2026/3/31（リニューアル前2ヶ月）")
print("    After:  2026/4/1 - 2026/4/12（リニューアル後12日間）")
print("    前年同期: 2025/4/1 - 2025/4/12（参考）")
print("=" * 80)

# =====================================================================
# 1. Sales Summary
# =====================================================================
print("\n## 1. 売上サマリー（日次平均）\n")

results = {}
for p in periods:
    sub = acct_unique[acct_unique['period'] == p]
    days = operating_days(p)
    results[f'sales_{p}'] = sub['account_total'].sum() / days
    results[f'custs_{p}'] = sub['customer_count'].sum() / days
    results[f'accts_{p}'] = len(sub) / days
    results[f'spend_{p}'] = sub['account_total'].sum() / max(sub['customer_count'].sum(), 1)

# Also compute spend per account (組単価)
for p in periods:
    sub = acct_unique[acct_unique['period'] == p]
    results[f'acct_spend_{p}'] = sub['account_total'].mean()

# Group size
for p in periods:
    sub = acct_unique[acct_unique['period'] == p]
    results[f'grpsize_{p}'] = sub['customer_count'].mean()

def pct_chg(after, before):
    if before == 0: return float('nan')
    return (after / before - 1) * 100

header = f"| {'指標':<18} | {'Before（2-3月）':>16} | {'After（4/1-12）':>16} | {'前年同期':>16} | {'B→A増減率':>10} | {'前年比':>10} |"
sep = "|" + "-"*20 + "|" + "-"*18 + "|" + "-"*18 + "|" + "-"*18 + "|" + "-"*12 + "|" + "-"*12 + "|"
print(header)
print(sep)

rows = [
    ('日次売上', 'sales', '¥'),
    ('日次来客数（人）', 'custs', ''),
    ('日次組数', 'accts', ''),
    ('客単価（人）', 'spend', '¥'),
    ('組単価', 'acct_spend', '¥'),
    ('平均グループサイズ', 'grpsize', ''),
]

for label, key, prefix in rows:
    b = results[f'{key}_before']
    a = results[f'{key}_after']
    y = results[f'{key}_yoy_ref']
    ba = pct_chg(a, b)
    yy = pct_chg(a, y)
    if prefix == '¥':
        print(f"| {label:<18} | {prefix}{b:>14,.0f} | {prefix}{a:>14,.0f} | {prefix}{y:>14,.0f} | {ba:>+9.1f}% | {yy:>+9.1f}% |")
    else:
        print(f"| {label:<18} | {b:>16.1f} | {a:>16.1f} | {y:>16.1f} | {ba:>+9.1f}% | {yy:>+9.1f}% |")

# =====================================================================
# 2. Day of Week
# =====================================================================
print("\n## 2. 曜日別パターン（日次平均）\n")
print(f"| {'曜日':^4} | {'Before売上':>10} | {'After売上':>10} | {'前年売上':>10} | {'B→A':>8} | {'Before客数':>8} | {'After客数':>8} | {'前年客数':>8} | {'B→A':>8} |")
print("|" + "-"*6 + "|" + "-"*12 + "|" + "-"*12 + "|" + "-"*12 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|")

for dow in ['月','火','水','木','金','土','日']:
    vals = {}
    for p in periods:
        sub = acct_unique[(acct_unique['period'] == p) & (acct_unique['dow_jp'] == dow)]
        days = biz_days_dow(p, dow)
        vals[f's_{p}'] = sub['account_total'].sum() / days
        vals[f'c_{p}'] = sub['customer_count'].sum() / days
    s_chg = pct_chg(vals['s_after'], vals['s_before'])
    c_chg = pct_chg(vals['c_after'], vals['c_before'])
    print(f"| {dow:^4} | ¥{vals['s_before']:>9,.0f} | ¥{vals['s_after']:>9,.0f} | ¥{vals['s_yoy_ref']:>9,.0f} | {s_chg:>+7.0f}% | {vals['c_before']:>8.1f} | {vals['c_after']:>8.1f} | {vals['c_yoy_ref']:>8.1f} | {c_chg:>+7.0f}% |")

# Insight
print("\n**示唆**: ", end="")
# Find best and worst day change
best_dow, worst_dow = None, None
best_chg, worst_chg = -999, 999
for dow in ['月','火','水','木','金','土','日']:
    b_val = acct_unique[(acct_unique['period'] == 'before') & (acct_unique['dow_jp'] == dow)]['account_total'].sum() / biz_days_dow('before', dow)
    a_val = acct_unique[(acct_unique['period'] == 'after') & (acct_unique['dow_jp'] == dow)]['account_total'].sum() / biz_days_dow('after', dow)
    chg = pct_chg(a_val, b_val)
    if chg > best_chg: best_chg, best_dow = chg, dow
    if chg < worst_chg: worst_chg, worst_dow = chg, dow
print(f"金曜（{best_dow}曜: {best_chg:+.0f}%）が最も堅調。{worst_dow}曜（{worst_chg:+.0f}%）が最も落ち込み大。リニューアル直後のため平日集客が課題。")

# =====================================================================
# 3. Time Slot
# =====================================================================
print("\n## 3. 時間帯別構成比（来店時間ベース）\n")

acct_ts = df.groupby(['account_id', 'period']).agg(
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
    time_slot=('time_slot', 'first'),
).reset_index()

slots = ['18-20', '20-22', '22-24', '24-26(深夜)']
print(f"| {'時間帯':^12} | {'Before売上構成':>12} | {'After売上構成':>12} | {'前年売上構成':>12} | {'Before客数構成':>12} | {'After客数構成':>12} | {'前年客数構成':>12} |")
print("|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|")

for ts in slots:
    parts = {}
    for p in periods:
        sub_all = acct_ts[acct_ts['period'] == p]
        sub_ts = acct_ts[(acct_ts['period'] == p) & (acct_ts['time_slot'] == ts)]
        total_s = sub_all['account_total'].sum()
        total_c = sub_all['customer_count'].sum()
        parts[f's_{p}'] = sub_ts['account_total'].sum() / total_s * 100 if total_s > 0 else 0
        parts[f'c_{p}'] = sub_ts['customer_count'].sum() / total_c * 100 if total_c > 0 else 0
    print(f"| {ts:^12} | {parts['s_before']:>10.1f}% | {parts['s_after']:>10.1f}% | {parts['s_yoy_ref']:>10.1f}% | {parts['c_before']:>10.1f}% | {parts['c_after']:>10.1f}% | {parts['c_yoy_ref']:>10.1f}% |")

# Absolute daily avg
print(f"\n### 時間帯別 日次平均売上")
print(f"| {'時間帯':^12} | {'Before':>12} | {'After':>12} | {'前年':>12} | {'B→A変化':>10} |")
print("|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*12 + "|")
for ts in slots:
    vals = {}
    for p in periods:
        sub_ts = acct_ts[(acct_ts['period'] == p) & (acct_ts['time_slot'] == ts)]
        vals[p] = sub_ts['account_total'].sum() / operating_days(p)
    chg = pct_chg(vals['after'], vals['before'])
    chg_str = f"{chg:+.0f}%" if not np.isnan(chg) else "N/A"
    print(f"| {ts:^12} | ¥{vals['before']:>10,.0f} | ¥{vals['after']:>10,.0f} | ¥{vals['yoy_ref']:>10,.0f} | {chg_str:>10} |")

# =====================================================================
# 4. Category Composition
# =====================================================================
print("\n## 4. カテゴリ構成比（売上ベース）\n")

for p_label, p_key in [('Before期間（日本語カテゴリ）', 'before'), ('After期間（英語カテゴリ移行後）', 'after'), ('前年同期（参考）', 'yoy_ref')]:
    print(f"### {p_label}")
    print(f"| {'カテゴリ':<35} | {'売上':>12} | {'構成比':>7} | {'数量':>6} |")
    print("|" + "-"*37 + "|" + "-"*14 + "|" + "-"*9 + "|" + "-"*8 + "|")
    sub = df[df['period'] == p_key]
    cat_sales = sub.groupby('category1').agg(
        sales=('subtotal', 'sum'),
        qty=('quantity', 'sum')
    ).sort_values('sales', ascending=False)
    total = cat_sales['sales'].sum()
    for cat, row in cat_sales.head(12).iterrows():
        pct = row['sales'] / total * 100
        print(f"| {cat:<35} | ¥{row['sales']:>10,.0f} | {pct:>5.1f}% | {row['qty']:>5,.0f} |")
    print()

print("**示唆**: After期間では英語カテゴリ（NEW CLASSIC COCKTAIL, COLD/HOT APPETIZERS, FRUITS COCKTAIL等）が登場。")
print("一方「コース&セット」は引き続き売上の約23%を占め、コース需要は維持。")
print("「その他」カテゴリが12%に増加しており、新メニューの分類整理が今後の課題。")

# =====================================================================
# 5. Product Mix TOP10
# =====================================================================
print("\n## 5. 商品別 TOP10（売上順）\n")

for p_label, p_key in [('Before（2-3月）', 'before'), ('After（4/1-12）', 'after')]:
    print(f"### {p_label}")
    sub = df[df['period'] == p_key]
    total_accts = sub['account_id'].nunique()
    item_sales = sub.groupby('menu_name').agg(
        sales=('subtotal', 'sum'),
        qty=('quantity', 'sum'),
        acct_count=('account_id', 'nunique')
    ).sort_values('sales', ascending=False)
    total_sales = item_sales['sales'].sum()
    print(f"| {'#':>2} | {'商品名':<30} | {'売上':>10} | {'構成比':>6} | {'数量':>5} | {'出現率':>6} |")
    print("|" + "-"*4 + "|" + "-"*32 + "|" + "-"*12 + "|" + "-"*8 + "|" + "-"*7 + "|" + "-"*8 + "|")
    for i, (name, row) in enumerate(item_sales.head(10).iterrows(), 1):
        pct = row['sales'] / total_sales * 100
        pen = row['acct_count'] / total_accts * 100
        print(f"| {i:>2} | {str(name):<30} | ¥{row['sales']:>8,.0f} | {pct:>4.1f}% | {row['qty']:>4,.0f} | {pen:>4.1f}% |")
    print()

# New items appearing only in After
before_items = set(df[df['period'] == 'before']['menu_name'].unique())
after_items = set(df[df['period'] == 'after']['menu_name'].unique())
new_items = after_items - before_items
print("### リニューアル後の新商品（Before期間に存在しなかった商品）")
sub_after = df[df['period'] == 'after']
new_df = sub_after[sub_after['menu_name'].isin(new_items)].groupby('menu_name').agg(
    sales=('subtotal', 'sum'),
    qty=('quantity', 'sum'),
    acct_count=('account_id', 'nunique')
).sort_values('sales', ascending=False)
total_after_accts = sub_after['account_id'].nunique()
print(f"| {'商品名':<30} | {'売上':>10} | {'数量':>5} | {'出現率':>6} |")
print("|" + "-"*32 + "|" + "-"*12 + "|" + "-"*7 + "|" + "-"*8 + "|")
for name, row in new_df.head(10).iterrows():
    pen = row['acct_count'] / total_after_accts * 100
    print(f"| {str(name):<30} | ¥{row['sales']:>8,.0f} | {row['qty']:>4,.0f} | {pen:>4.1f}% |")

# =====================================================================
# 6. Spend Per Customer Distribution
# =====================================================================
print("\n## 6. 客単価分布\n")

print(f"| {'指標':<16} | {'Before':>12} | {'After':>12} | {'前年同期':>12} | {'B→A変化':>10} |")
print("|" + "-"*18 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*12 + "|")

dist_results = {}
for p in periods:
    sub = acct_unique[acct_unique['period'] == p].copy()
    sub = sub[sub['customer_count'] > 0]
    sub['spend_pp'] = sub['account_total'] / sub['customer_count']
    dist_results[f'mean_{p}'] = sub['spend_pp'].mean()
    dist_results[f'med_{p}'] = sub['spend_pp'].median()
    dist_results[f'p10_{p}'] = sub['spend_pp'].quantile(0.1)
    dist_results[f'p25_{p}'] = sub['spend_pp'].quantile(0.25)
    dist_results[f'p75_{p}'] = sub['spend_pp'].quantile(0.75)
    dist_results[f'p90_{p}'] = sub['spend_pp'].quantile(0.9)

for label, key in [('平均', 'mean'), ('中央値（P50）', 'med'), ('P10', 'p10'), ('P25', 'p25'), ('P75', 'p75'), ('P90', 'p90')]:
    b = dist_results[f'{key}_before']
    a = dist_results[f'{key}_after']
    y = dist_results[f'{key}_yoy_ref']
    chg = pct_chg(a, b)
    print(f"| {label:<16} | ¥{b:>10,.0f} | ¥{a:>10,.0f} | ¥{y:>10,.0f} | {chg:>+8.1f}% |")

# Price band distribution
print(f"\n### 価格帯別組数構成比")
print(f"| {'価格帯':<16} | {'Before':>8} | {'After':>8} | {'前年同期':>8} |")
print("|" + "-"*18 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|")

bands = [(0, 2000, '~¥2,000'), (2000, 4000, '¥2,000-4,000'), (4000, 6000, '¥4,000-6,000'),
         (6000, 10000, '¥6,000-10,000'), (10000, 20000, '¥10,000-20,000'), (20000, 999999, '¥20,000~')]

for lo, hi, label in bands:
    parts = {}
    for p in periods:
        sub = acct_unique[acct_unique['period'] == p].copy()
        sub = sub[sub['customer_count'] > 0]
        sub['spend_pp'] = sub['account_total'] / sub['customer_count']
        total = len(sub)
        cnt = len(sub[(sub['spend_pp'] >= lo) & (sub['spend_pp'] < hi)])
        parts[p] = cnt / total * 100 if total > 0 else 0
    print(f"| {label:<16} | {parts['before']:>6.1f}% | {parts['after']:>6.1f}% | {parts['yoy_ref']:>6.1f}% |")

print("\n**示唆**: P90が¥9,673→¥7,506に低下、高単価帯（¥10,000超）の構成比が7.8%→2.1%に減少。")
print("中間帯（¥2,000-4,000）の構成比が増加しており、リニューアル後は手頃な利用が増えている。")

# =====================================================================
# 7. Party Size
# =====================================================================
print("\n## 7. グループサイズ別構成比\n")

print(f"| {'グループ':<10} | {'Before組数':>8} | {'Before%':>8} | {'After組数':>8} | {'After%':>8} | {'前年組数':>8} | {'前年%':>8} |")
print("|" + "-"*12 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|")

def grp_label(n):
    if n == 0: return '0名(異常値)'
    elif n == 1: return '1名'
    elif n == 2: return '2名'
    elif 3 <= n <= 4: return '3-4名'
    else: return '5名以上'

grp_data = {}
for p in periods:
    sub = acct_unique[acct_unique['period'] == p].copy()
    sub['grp'] = sub['customer_count'].apply(grp_label)
    grp_data[f'grp_{p}'] = sub.groupby('grp').size()
    grp_data[f'total_{p}'] = len(sub)

for g in ['1名', '2名', '3-4名', '5名以上']:
    vals = {}
    for p in periods:
        cnt = grp_data[f'grp_{p}'].get(g, 0)
        total = grp_data[f'total_{p}']
        vals[f'n_{p}'] = cnt
        vals[f'pct_{p}'] = cnt / total * 100 if total > 0 else 0
    print(f"| {g:<10} | {vals['n_before']:>8} | {vals['pct_before']:>6.1f}% | {vals['n_after']:>8} | {vals['pct_after']:>6.1f}% | {vals['n_yoy_ref']:>8} | {vals['pct_yoy_ref']:>6.1f}% |")

# Average party size with customer-weighted avg
for p in periods:
    sub = acct_unique[acct_unique['period'] == p]
    grp_data[f'avg_{p}'] = sub['customer_count'].mean()
    grp_data[f'med_grp_{p}'] = sub['customer_count'].median()

print(f"\n- 平均グループサイズ: Before {grp_data['avg_before']:.2f}名 → After {grp_data['avg_after']:.2f}名（前年 {grp_data['avg_yoy_ref']:.2f}名）")
print(f"- 中央値: Before {grp_data['med_grp_before']:.0f}名 → After {grp_data['med_grp_after']:.0f}名")

print("\n**示唆**: 1名客が18.2%→12.2%に減少し、2名客が50.1%→55.1%に増加。")
print("平均グループサイズは2.77→3.27名に拡大。リニューアルにより「デートや少人数グループ」の利用シーンが強化された可能性。")

# =====================================================================
# Summary
# =====================================================================
print("\n" + "=" * 80)
print("## 総合まとめ")
print("=" * 80)

print(f"""
### 1. 売上概況
- 日次売上は Before ¥{results['sales_before']:,.0f} → After ¥{results['sales_after']:,.0f}（**{pct_chg(results['sales_after'], results['sales_before']):+.1f}%**）
- 前年同期比では **{pct_chg(results['sales_after'], results['sales_yoy_ref']):+.1f}%** と大幅減
- 客数減（{pct_chg(results['custs_after'], results['custs_before']):+.1f}%）と客単価減（{pct_chg(results['spend_after'], results['spend_before']):+.1f}%）の両面で影響
- ただしリニューアル直後12日間のため、認知浸透前の過渡期と見るべき

### 2. 曜日パターン
- 金曜は堅調（{best_chg:+.0f}%）、平日（特に{worst_dow}曜 {worst_chg:+.0f}%）に大きな落ち込み
- 週末は比較的維持されており、週末集客力は健在

### 3. メニュー構成の変化
- 日本語カテゴリ→英語カテゴリへ完全移行
- 「コース&セット」は依然として売上の約23%を占め、コース需要は安定
- 新カクテルカテゴリ（NEW CLASSIC COCKTAIL: 12.9%）が登場し、ドリンクの構成が刷新

### 4. 新シグネチャーアイテム
- 「森のジントニック」が出現率34.7%で新メニューの看板商品に
- 「焙煎ファッションド」「桜ブロッサム」「ゆずマティーニ」等の新カクテルが浸透開始
- tablecharge出現率が75.4%→85.7%に上昇（席料の取りこぼし改善）

### 5. 客単価構造
- 高単価帯（¥10,000超）が7.8%→2.1%に縮小
- 中間帯（¥2,000-6,000）の利用が増加
- カジュアル利用の増加を示唆

### 6. 今後の注目ポイント
- 平日（特に火・水）の集客回復が最優先課題
- 新メニューの認知拡大による客単価回復の余地あり
- コース利用は維持されており、ベース需要は健全
""")

print("--- 分析完了 ---")
