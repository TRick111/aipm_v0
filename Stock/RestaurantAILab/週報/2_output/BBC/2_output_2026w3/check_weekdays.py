import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv(r'Stock\RestaurantAILab\週報\1_input\BBC\rawdata.csv')
df['ordered_at_utc'] = pd.to_datetime(df['ordered_at'], utc=True)
df['ordered_at_jst'] = df['ordered_at_utc'].dt.tz_convert('Asia/Tokyo')
df['business_date'] = df['ordered_at_jst'].apply(lambda x: (x - timedelta(hours=5)).date())

# 会計レベルで集計
accounts = df.groupby('account_id').agg({
    'business_date': 'first',
    'day_of_week': 'first',
    'account_total': 'first',
    'customer_count': 'first'
}).reset_index()

# 対象週の範囲
target_week_start = pd.to_datetime('2026-01-12').date()
target_week_end = pd.to_datetime('2026-01-18').date()

target_week = accounts[
    (accounts['business_date'] >= target_week_start) &
    (accounts['business_date'] <= target_week_end)
]

# 営業日ごとの集計
daily_summary = target_week.groupby('business_date').agg({
    'account_id': 'count',
    'customer_count': 'sum',
    'account_total': 'sum'
}).reset_index()

daily_summary['weekday'] = pd.to_datetime(daily_summary['business_date']).dt.day_name()
daily_summary['weekday_jp'] = pd.to_datetime(daily_summary['business_date']).apply(
    lambda x: ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日'][x.weekday()]
)
daily_summary = daily_summary.sort_values('business_date')
daily_summary.columns = ['営業日', '会計数', '客数', '売上', '曜日（英）', '曜日（日）']

print(daily_summary.to_string(index=False))
