#!/usr/bin/env python3
"""BFA staffing optimization analysis - fact-based report generation"""

import pandas as pd
import json
from collections import defaultdict

# Load data
df = pd.read_csv('/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv')

# Parse dates
df['entry_at'] = pd.to_datetime(df['entry_at'])
df['exit_at'] = pd.to_datetime(df['exit_at'])

# Extract hour from entry_at
df['hour'] = df['entry_at'].dt.hour

# Date range info
print(f"Data range: {df['entry_at'].min()} to {df['entry_at'].max()}")
print(f"Total rows: {len(df)}")

# --- Account-level aggregation (unique transactions) ---
accounts = df.groupby('account_id').agg(
    entry_at=('entry_at', 'first'),
    exit_at=('exit_at', 'first'),
    day_of_week=('day_of_week', 'first'),
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
    hour=('hour', 'first'),
).reset_index()

accounts['account_total'] = accounts['account_total'].astype(float)
accounts['customer_count'] = accounts['customer_count'].astype(int)
accounts['date'] = accounts['entry_at'].dt.date

print(f"Total unique accounts: {len(accounts)}")
print(f"Date range: {accounts['date'].min()} to {accounts['date'].max()}")

# --- Filter to recent period (last 3 months for relevance) ---
# Use all data but also compute recent 3 months separately
cutoff_3m = accounts['entry_at'].max() - pd.Timedelta(days=90)
recent = accounts[accounts['entry_at'] >= cutoff_3m].copy()
print(f"\nRecent 3 months: {recent['date'].min()} to {recent['date'].max()}")
print(f"Recent accounts: {len(recent)}")

# Also compute last 6 months for more stable averages
cutoff_6m = accounts['entry_at'].max() - pd.Timedelta(days=180)
mid = accounts[accounts['entry_at'] >= cutoff_6m].copy()

# --- Day of week mapping for proper ordering ---
dow_order = ['月', '火', '水', '木', '金', '土', '日']
dow_en = {'月': 'Mon', '火': 'Tue', '水': 'Wed', '木': 'Thu', '金': 'Fri', '土': 'Sat', '日': 'Sun'}

# --- 1. Day-of-week analysis (recent 3 months) ---
# Count unique operating days per dow
recent['date_str'] = recent['date'].astype(str)
operating_days = recent.groupby('day_of_week')['date_str'].nunique()

dow_stats = recent.groupby('day_of_week').agg(
    total_sales=('account_total', 'sum'),
    total_customers=('customer_count', 'sum'),
    total_groups=('account_id', 'count'),
).reset_index()

dow_stats['operating_days'] = dow_stats['day_of_week'].map(operating_days)
dow_stats['avg_daily_sales'] = (dow_stats['total_sales'] / dow_stats['operating_days']).round(0)
dow_stats['avg_daily_customers'] = (dow_stats['total_customers'] / dow_stats['operating_days']).round(1)
dow_stats['avg_daily_groups'] = (dow_stats['total_groups'] / dow_stats['operating_days']).round(1)
dow_stats['avg_spend_per_customer'] = (dow_stats['total_sales'] / dow_stats['total_customers']).round(0)
dow_stats['avg_spend_per_group'] = (dow_stats['total_sales'] / dow_stats['total_groups']).round(0)

# Sort by proper day order
dow_stats['dow_idx'] = dow_stats['day_of_week'].map(lambda x: dow_order.index(x))
dow_stats = dow_stats.sort_values('dow_idx')

print("\n=== Day-of-week analysis (recent 3 months) ===")
for _, row in dow_stats.iterrows():
    print(f"{row['day_of_week']}: 営業{int(row['operating_days'])}日, "
          f"日平均売上¥{int(row['avg_daily_sales']):,}, "
          f"日平均来店{row['avg_daily_customers']:.1f}人, "
          f"客単価¥{int(row['avg_spend_per_customer']):,}")

# --- 2. Hourly analysis (recent 3 months) ---
# Need item-level data for hourly analysis tied to entry time
recent_items = df[df['entry_at'] >= cutoff_3m].copy()
hourly_accounts = recent_items.groupby(['account_id', 'hour']).agg(
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
).reset_index()
# Deduplicate: each account counted once at their entry hour
hourly_accounts = hourly_accounts.drop_duplicates(subset='account_id')

hourly_stats = hourly_accounts.groupby('hour').agg(
    total_sales=('account_total', 'sum'),
    total_customers=('customer_count', 'sum'),
    total_groups=('account_id', 'count'),
).reset_index()

# Operating days for hourly normalization
total_operating_days = recent['date_str'].nunique()
hourly_stats['avg_daily_sales'] = (hourly_stats['total_sales'] / total_operating_days).round(0)
hourly_stats['avg_daily_customers'] = (hourly_stats['total_customers'] / total_operating_days).round(1)
hourly_stats['avg_daily_groups'] = (hourly_stats['total_groups'] / total_operating_days).round(1)
hourly_stats['sales_pct'] = (hourly_stats['total_sales'] / hourly_stats['total_sales'].sum() * 100).round(1)
hourly_stats['cumulative_pct'] = hourly_stats['sales_pct'].cumsum().round(1)

print("\n=== Hourly analysis (recent 3 months) ===")
for _, row in hourly_stats.sort_values('hour').iterrows():
    h = int(row['hour'])
    print(f"{h:02d}:00-{h+1:02d}:00: 売上{row['sales_pct']:.1f}%, "
          f"日平均¥{int(row['avg_daily_sales']):,}, "
          f"来店{row['avg_daily_customers']:.1f}人")

# --- 3. Late-night analysis (23:00+) ---
late_night = hourly_stats[hourly_stats['hour'] >= 23]
late_night_sales = late_night['total_sales'].sum()
late_night_pct = late_night_sales / hourly_stats['total_sales'].sum() * 100
late_night_customers = late_night['total_customers'].sum()

print(f"\n=== Late night (23:00+) ===")
print(f"Sales: ¥{late_night_sales:,.0f} ({late_night_pct:.1f}%)")
print(f"Customers: {late_night_customers}")

# Also check 23:30+ impact (accounts entering after 23:30)
recent_items_2330 = df[df['entry_at'] >= cutoff_3m].copy()
recent_items_2330['minute'] = recent_items_2330['entry_at'].dt.minute
accounts_after_2330 = recent_items_2330[
    (recent_items_2330['hour'] == 23) & (recent_items_2330['minute'] >= 30) |
    (recent_items_2330['hour'] >= 24)  # won't happen but just in case
].groupby('account_id').agg(
    account_total=('account_total', 'first'),
    customer_count=('customer_count', 'first'),
).reset_index()

sales_after_2330 = accounts_after_2330['account_total'].astype(float).sum()
pct_after_2330 = sales_after_2330 / hourly_stats['total_sales'].sum() * 100
customers_after_2330 = accounts_after_2330['customer_count'].astype(int).sum()

print(f"\n=== After 23:30 ===")
print(f"Sales: ¥{sales_after_2330:,.0f} ({pct_after_2330:.1f}%)")
print(f"Customers: {customers_after_2330}")

# --- 4. Cross analysis: day x hour ---
cross = recent.groupby(['day_of_week', 'hour']).agg(
    total_sales=('account_total', 'sum'),
    total_customers=('customer_count', 'sum'),
    groups=('account_id', 'count'),
).reset_index()

# Late night by day of week
late_by_dow = cross[cross['hour'] >= 23].groupby('day_of_week').agg(
    late_sales=('total_sales', 'sum'),
    late_customers=('total_customers', 'sum'),
).reset_index()

dow_totals = recent.groupby('day_of_week')['account_total'].sum().reset_index()
dow_totals.columns = ['day_of_week', 'dow_total_sales']
late_by_dow = late_by_dow.merge(dow_totals, on='day_of_week', how='left')
late_by_dow['late_pct'] = (late_by_dow['late_sales'] / late_by_dow['dow_total_sales'] * 100).round(1)

print("\n=== Late night by day of week ===")
for _, row in late_by_dow.iterrows():
    print(f"{row['day_of_week']}: 23時以降売上 ¥{row['late_sales']:,.0f} ({row['late_pct']:.1f}%)")

# --- Save results as JSON ---
results = {
    'period': {
        'start': str(recent['date'].min()),
        'end': str(recent['date'].max()),
        'total_operating_days': int(total_operating_days),
    },
    'dow_stats': [],
    'hourly_stats': [],
    'late_night': {
        'after_23': {
            'sales': float(late_night_sales),
            'pct': float(late_night_pct),
            'customers': int(late_night_customers),
        },
        'after_2330': {
            'sales': float(sales_after_2330),
            'pct': float(pct_after_2330),
            'customers': int(customers_after_2330),
        },
    },
    'late_by_dow': [],
}

for _, row in dow_stats.iterrows():
    results['dow_stats'].append({
        'day': row['day_of_week'],
        'day_en': dow_en[row['day_of_week']],
        'operating_days': int(row['operating_days']),
        'total_sales': float(row['total_sales']),
        'avg_daily_sales': float(row['avg_daily_sales']),
        'avg_daily_customers': float(row['avg_daily_customers']),
        'avg_daily_groups': float(row['avg_daily_groups']),
        'avg_spend_per_customer': float(row['avg_spend_per_customer']),
        'avg_spend_per_group': float(row['avg_spend_per_group']),
    })

for _, row in hourly_stats.sort_values('hour').iterrows():
    results['hourly_stats'].append({
        'hour': int(row['hour']),
        'total_sales': float(row['total_sales']),
        'avg_daily_sales': float(row['avg_daily_sales']),
        'avg_daily_customers': float(row['avg_daily_customers']),
        'avg_daily_groups': float(row['avg_daily_groups']),
        'sales_pct': float(row['sales_pct']),
        'cumulative_pct': float(row['cumulative_pct']),
    })

for _, row in late_by_dow.iterrows():
    results['late_by_dow'].append({
        'day': row['day_of_week'],
        'late_sales': float(row['late_sales']),
        'late_pct': float(row['late_pct']),
        'late_customers': int(row['late_customers']),
    })

output_path = '/Users/rikutanaka/aipm_v0/Flow/202603/2026-03-26/BFA/analysis_results.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nResults saved to {output_path}")
