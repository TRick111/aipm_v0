import pandas as pd
from datetime import datetime, timedelta
import sys

# 出力エンコーディングをUTF-8に設定
sys.stdout.reconfigure(encoding='utf-8')

# データ読み込み
df = pd.read_csv('Stock/RestaurantAILab/週報/1_input/BBC/rawdata.csv')

# 日時をJSTに変換
df['entry_at'] = pd.to_datetime(df['entry_at'])
df['eigyobi'] = df['entry_at'].apply(lambda x: (x - timedelta(hours=5)).date())

# W51の期間を計算（2025-12-14 ~ 2025-12-20）
w51_start = pd.to_datetime('2025-12-14').date()
w51_end = pd.to_datetime('2025-12-20').date()

# W52の期間（2025-12-21 ~ 2025-12-27）
w52_start = pd.to_datetime('2025-12-21').date()
w52_end = pd.to_datetime('2025-12-27').date()

# W51のデータ抽出
w51_df = df[(df['eigyobi'] >= w51_start) & (df['eigyobi'] <= w51_end)]
# W52のデータ抽出
w52_df = df[(df['eigyobi'] >= w52_start) & (df['eigyobi'] <= w52_end)]

# 各週の組数（ユニークなaccount_id数）を計算
w51_groups = w51_df['account_id'].nunique()
w52_groups = w52_df['account_id'].nunique()

# 各週の売上、客数も確認
w51_sales = w51_df.groupby('account_id')['account_total'].first().sum()
w51_customers = w51_df.groupby('account_id')['customer_count'].first().sum()

w52_sales = w52_df.groupby('account_id')['account_total'].first().sum()
w52_customers = w52_df.groupby('account_id')['customer_count'].first().sum()

print(f'W51_groups: {w51_groups}')
print(f'W51_sales: {w51_sales:.0f}')
print(f'W51_customers: {w51_customers}')
print(f'W51_avg_spend: {w51_sales/w51_customers:.0f}')
print()
print(f'W52_groups: {w52_groups}')
print(f'W52_sales: {w52_sales:.0f}')
print(f'W52_customers: {w52_customers}')
print(f'W52_avg_spend: {w52_sales/w52_customers:.0f}')
print()
print(f'Group_change_pct: {((w52_groups - w51_groups) / w51_groups * 100):.1f}')
print(f'Sales_change_pct: {((w52_sales - w51_sales) / w51_sales * 100):.1f}')
print(f'Customers_change_pct: {((w52_customers - w51_customers) / w51_customers * 100):.1f}')
