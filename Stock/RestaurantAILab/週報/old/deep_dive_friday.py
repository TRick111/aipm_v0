# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
from datetime import datetime

# UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load data
df = pd.read_csv('Stock/RestaurantAILab/週報/1_input/rawdata.csv')
df['entry_at'] = pd.to_datetime(df['entry_at'], utc=True)
df['entry_at_jst'] = df['entry_at'].dt.tz_convert('Asia/Tokyo')
df['business_date'] = df['entry_at_jst'].apply(
    lambda dt: (dt - pd.Timedelta(days=1)).date() if 0 <= dt.hour < 6 else dt.date()
)

# Filter for Friday
fri = df[df['business_date'] == pd.Timestamp('2026-01-02').date()].copy()
fri['hour'] = fri['entry_at_jst'].dt.hour

print('='*60)
print('金曜日 2026-01-02 (最も不調な日) - 詳細分析')
print('='*60)
print()

# Basic info
print('【基本情報】')
accounts = fri.groupby('account_id').first().reset_index()
total_sales = accounts['account_total'].sum()
total_customers = accounts['customer_count'].sum()
print(f'  総売上: ¥{total_sales:,.0f}')
print(f'  総客数: {total_customers}人')
print(f'  会計数: {len(accounts)}件')
print(f'  平均客単価: ¥{total_sales / total_customers:,.0f}')
print()

# 1. Party size analysis
print('【1. パーティサイズ分析】')
def party_size_category(count):
    if count == 1:
        return '1名'
    elif count == 2:
        return '2名'
    elif count <= 4:
        return '3-4名'
    else:
        return '5名以上'

accounts['party_size'] = accounts['customer_count'].apply(party_size_category)
party_analysis = accounts.groupby('party_size').agg({
    'account_id': 'count',
    'customer_count': 'sum',
    'account_total': 'sum'
}).reset_index()
party_analysis.columns = ['パーティサイズ', '会計数', '客数', '売上']
party_analysis['構成比%'] = (party_analysis['会計数'] / party_analysis['会計数'].sum() * 100).round(1)
party_analysis['平均単価'] = (party_analysis['売上'] / party_analysis['客数']).round(0)
party_analysis = party_analysis.sort_values('パーティサイズ')
print(party_analysis.to_string(index=False))
print()

# 2. Time bucket analysis
print('【2. 時間帯バケット分析】')
accounts_time = fri.groupby('account_id').agg({
    'entry_at_jst': 'first',
    'account_total': 'first',
    'customer_count': 'first'
}).reset_index()
accounts_time['hour'] = accounts_time['entry_at_jst'].dt.hour

def time_bucket(hour):
    if hour < 6:
        return f'{hour:02d}時台(深夜)'
    else:
        return f'{hour:02d}時台'

accounts_time['time_bucket'] = accounts_time['hour'].apply(time_bucket)
time_analysis = accounts_time.groupby('time_bucket').agg({
    'account_id': 'count',
    'customer_count': 'sum',
    'account_total': 'sum'
}).reset_index()
time_analysis.columns = ['時間帯', '会計数', '客数', '売上']
time_analysis['平均客数/会計'] = (time_analysis['客数'] / time_analysis['会計数']).round(1)
time_analysis['平均売上/会計'] = (time_analysis['売上'] / time_analysis['会計数']).round(0)
print(time_analysis.to_string(index=False))
print()

# 3. Account-level analysis
print('【3. 会計レベル分析】')
account_totals = accounts['account_total'].values
print(f'  最大会計: ¥{account_totals.max():,.0f}')
print(f'  最小会計: ¥{account_totals.min():,.0f}')
print(f'  中央値: ¥{np.median(account_totals):,.0f}')
print(f'  P10 (下位10%): ¥{np.percentile(account_totals, 10):,.0f}')
print(f'  P90 (上位10%): ¥{np.percentile(account_totals, 90):,.0f}')
print(f'  平均: ¥{account_totals.mean():,.0f}')
print()
print('  会計金額分布:')
bins = [0, 5000, 10000, 15000, 20000, 100000]
labels = ['~5千円', '5千~1万', '1万~1.5万', '1.5万~2万', '2万円以上']
accounts['price_range'] = pd.cut(accounts['account_total'], bins=bins, labels=labels, right=False)
price_dist = accounts.groupby('price_range').size().reset_index(name='会計数')
price_dist['構成比%'] = (price_dist['会計数'] / price_dist['会計数'].sum() * 100).round(1)
print(price_dist.to_string(index=False))
print()

# 4. Product mix analysis
print('【4. 商品ミックス分析】')
print('  カテゴリ別売上構成:')
category_sales = fri.groupby('category1').agg({
    'price': 'sum',
    'menu_name': 'count'
}).reset_index()
category_sales.columns = ['カテゴリ', '売上', '販売数']
category_sales['構成比%'] = (category_sales['売上'] / category_sales['売上'].sum() * 100).round(1)
category_sales = category_sales.sort_values('売上', ascending=False)
print(category_sales.to_string(index=False))
print()

print('  高単価商品 (¥1,500以上):')
high_price = fri[fri['price'] >= 1500].copy()
if len(high_price) > 0:
    high_price_summary = high_price.groupby('menu_name').agg({
        'price': ['mean', 'count', 'sum']
    }).reset_index()
    high_price_summary.columns = ['商品名', '平均単価', '販売数', '売上合計']
    high_price_summary = high_price_summary.sort_values('売上合計', ascending=False).head(10)
    print(high_price_summary.to_string(index=False))
else:
    print('    なし')
print()

# 5. Exception data check
print('【5. 例外データ確認】')
print('  営業時間外会計 (6時前の入力):')
early_morning = fri[fri['hour'] < 6]
if len(early_morning) > 0:
    early_accounts = early_morning.groupby('account_id').first()
    print(f'    会計数: {len(early_accounts)}件')
    print(f'    売上: ¥{early_accounts["account_total"].sum():,.0f}')
    print(f'    時間帯: {early_morning["hour"].min()}時~{early_morning["hour"].max()}時')
else:
    print('    なし')
print()

print('  特殊な会計パターン:')
print(f'    1名あたり売上 > ¥10,000の会計: {len(accounts[accounts["account_total"]/accounts["customer_count"] > 10000])}件')
print(f'    10名以上のパーティ: {len(accounts[accounts["customer_count"] >= 10])}件')
