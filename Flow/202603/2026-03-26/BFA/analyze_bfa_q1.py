#!/usr/bin/env python3
"""BFA staffing optimization analysis - Q1 2026 (Jan-Mar)
営業日定義: 翌朝9時までの会計は前日の営業日として計上
"""

import pandas as pd
import json

df = pd.read_csv('/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv')
df['exit_at'] = pd.to_datetime(df['exit_at'])
df['hour'] = df['exit_at'].dt.hour

# === 営業日補正: 0:00〜8:59 の会計は前日の営業日に帰属 ===
df['biz_date'] = df['exit_at'].apply(
    lambda t: (t - pd.Timedelta(hours=9)).date() if t.hour < 9 else t.date()
)
df['biz_date'] = pd.to_datetime(df['biz_date'])

dow_map = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
df['biz_dow'] = df['biz_date'].dt.dayofweek.map(dow_map)

# Account-level aggregation
accounts = df.groupby('account_id').agg(
    exit_at=('exit_at', 'first'),
    biz_date=('biz_date', 'first'),
    biz_dow=('biz_dow', 'first'),
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
    hour=('hour', 'first'),
).reset_index()
accounts['account_total'] = accounts['account_total'].astype(float)
accounts['customer_count'] = accounts['customer_count'].astype(int)

# Filter: Q1 2026 (biz_date basis)
q1 = accounts[(accounts['biz_date'] >= '2026-01-01') & (accounts['biz_date'] < '2026-04-01')].copy()
print(f"Q1 2026 (biz_date): {q1['biz_date'].min().date()} to {q1['biz_date'].max().date()}")
print(f"Accounts: {len(q1)}")

# Day-of-week
dow_order = ['月', '火', '水', '木', '金', '土', '日']
dow_en = {'月': 'Mon', '火': 'Tue', '水': 'Wed', '木': 'Thu', '金': 'Fri', '土': 'Sat', '日': 'Sun'}

q1['date_str'] = q1['biz_date'].dt.strftime('%Y-%m-%d')
operating_days = q1.groupby('biz_dow')['date_str'].nunique()

dow_stats = q1.groupby('biz_dow').agg(
    total_sales=('account_total', 'sum'),
    total_customers=('customer_count', 'sum'),
    total_groups=('account_id', 'count'),
).reset_index()
dow_stats['operating_days'] = dow_stats['biz_dow'].map(operating_days)
dow_stats['avg_daily_sales'] = (dow_stats['total_sales'] / dow_stats['operating_days']).round(0)
dow_stats['avg_daily_customers'] = (dow_stats['total_customers'] / dow_stats['operating_days']).round(1)
dow_stats['avg_daily_groups'] = (dow_stats['total_groups'] / dow_stats['operating_days']).round(1)
dow_stats['avg_spend_per_customer'] = (dow_stats['total_sales'] / dow_stats['total_customers']).round(0)
dow_stats['avg_spend_per_group'] = (dow_stats['total_sales'] / dow_stats['total_groups']).round(0)
dow_stats['dow_idx'] = dow_stats['biz_dow'].map(lambda x: dow_order.index(x))
dow_stats = dow_stats.sort_values('dow_idx')

print("\n=== Day-of-week (Q1 2026, biz_date basis) ===")
for _, row in dow_stats.iterrows():
    print(f"{row['biz_dow']}: {int(row['operating_days'])}日, "
          f"¥{int(row['avg_daily_sales']):,}/日, "
          f"{row['avg_daily_customers']:.1f}人, "
          f"客単¥{int(row['avg_spend_per_customer']):,}")

# Hourly (exit_at hour, unchanged)
q1_items = df[(df['biz_date'] >= '2026-01-01') & (df['biz_date'] < '2026-04-01')].copy()
hourly_accounts = q1_items.groupby(['account_id']).agg(
    hour=('hour', 'first'),
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
).reset_index()

hourly_stats = hourly_accounts.groupby('hour').agg(
    total_sales=('account_total', 'sum'),
    total_customers=('customer_count', 'sum'),
    total_groups=('account_id', 'count'),
).reset_index()

total_operating_days = q1['date_str'].nunique()
hourly_stats['avg_daily_sales'] = (hourly_stats['total_sales'] / total_operating_days).round(0)
hourly_stats['avg_daily_customers'] = (hourly_stats['total_customers'] / total_operating_days).round(1)
hourly_stats['avg_daily_groups'] = (hourly_stats['total_groups'] / total_operating_days).round(1)
hourly_stats['sales_pct'] = (hourly_stats['total_sales'] / hourly_stats['total_sales'].sum() * 100).round(1)

# Sort by operational order for cumulative
op_order = [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5]
hourly_stats['op_idx'] = hourly_stats['hour'].map(lambda h: op_order.index(h) if h in op_order else 99)
hourly_stats = hourly_stats.sort_values('op_idx')
hourly_stats['cumulative_pct'] = hourly_stats['sales_pct'].cumsum().round(1)

total_sales = hourly_stats['total_sales'].sum()

print(f"\nOperating days: {total_operating_days}")
print("\n=== Hourly (Q1 2026, by exit_at) ===")
for _, row in hourly_stats.iterrows():
    h = int(row['hour'])
    print(f"{h:02d}時台: {row['sales_pct']:.1f}% (累積{row['cumulative_pct']:.1f}%), "
          f"¥{int(row['avg_daily_sales']):,}/日, {row['avg_daily_customers']:.1f}人")

# Late night
late_hours_23plus = [23, 0, 1, 2, 3, 4, 5]
late_all = hourly_stats[hourly_stats['hour'].isin(late_hours_23plus)]
late_sales = late_all['total_sales'].sum()
late_pct = late_sales / total_sales * 100

after_0_hours = [0, 1, 2, 3, 4, 5]
after_0 = hourly_stats[hourly_stats['hour'].isin(after_0_hours)]
sales_0 = after_0['total_sales'].sum()
pct_0 = sales_0 / total_sales * 100

# 23:30+
q1_items['minute'] = q1_items['exit_at'].dt.minute
accts_2330 = q1_items[
    ((q1_items['hour'] == 23) & (q1_items['minute'] >= 30)) |
    (q1_items['hour'].isin(after_0_hours))
].groupby('account_id').agg(
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
).reset_index()
sales_2330 = accts_2330['account_total'].astype(float).sum()
pct_2330 = sales_2330 / total_sales * 100
cust_2330 = accts_2330['customer_count'].astype(int).sum()

print(f"\n23時以降会計: ¥{late_sales:,.0f} ({late_pct:.1f}%)")
print(f"23:30以降会計: ¥{sales_2330:,.0f} ({pct_2330:.1f}%), {cust_2330}人")
print(f"0時以降会計: ¥{sales_0:,.0f} ({pct_0:.1f}%)")

# Avg daily
avg_daily = total_sales / total_operating_days
print(f"\n日平均売上: ¥{avg_daily:,.0f}")
print(f"月間概算(30日): ¥{avg_daily * 30:,.0f}")

# Save JSON
results = {
    'period': {
        'start': str(q1['biz_date'].min().date()),
        'end': str(q1['biz_date'].max().date()),
        'total_operating_days': int(total_operating_days),
        'label': '2026年1月〜3月',
        'note': '営業日定義: 翌朝9時までの会計は前日分として計上',
    },
    'summary': {
        'total_sales': float(total_sales),
        'avg_daily_sales': round(avg_daily),
        'total_customers': int(q1['customer_count'].sum()),
        'avg_daily_customers': round(q1['customer_count'].sum() / total_operating_days, 1),
    },
    'dow_stats': [],
    'hourly_stats': [],
    'late_night': {
        'after_23': {'sales': float(late_sales), 'pct': round(late_pct, 1)},
        'after_2330': {'sales': float(sales_2330), 'pct': round(pct_2330, 1), 'customers': int(cust_2330)},
        'after_0': {'sales': float(sales_0), 'pct': round(pct_0, 1)},
    },
}

for _, r in dow_stats.iterrows():
    results['dow_stats'].append({
        'day': r['biz_dow'], 'day_en': dow_en[r['biz_dow']],
        'operating_days': int(r['operating_days']),
        'total_sales': float(r['total_sales']),
        'avg_daily_sales': float(r['avg_daily_sales']),
        'avg_daily_customers': float(r['avg_daily_customers']),
        'avg_daily_groups': float(r['avg_daily_groups']),
        'avg_spend_per_customer': float(r['avg_spend_per_customer']),
        'avg_spend_per_group': float(r['avg_spend_per_group']),
    })

for _, r in hourly_stats.iterrows():
    results['hourly_stats'].append({
        'hour': int(r['hour']),
        'total_sales': float(r['total_sales']),
        'avg_daily_sales': float(r['avg_daily_sales']),
        'avg_daily_customers': float(r['avg_daily_customers']),
        'avg_daily_groups': float(r['avg_daily_groups']),
        'sales_pct': float(r['sales_pct']),
        'cumulative_pct': float(r['cumulative_pct']),
    })

with open('/Users/rikutanaka/aipm_v0/Flow/202603/2026-03-26/BFA/analysis_q1.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nSaved to analysis_q1.json")
