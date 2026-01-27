import pandas as pd
import sys
from datetime import datetime

# UTF-8で出力
sys.stdout.reconfigure(encoding='utf-8')

# CSVファイルを読み込む
df = pd.read_csv(r'c:\Users\auk1i\aipm_v0\Stock\RestaurantAILab\週報\1_input\rawdata.csv')

# entry_atから日付を抽出
df['date'] = pd.to_datetime(df['entry_at']).dt.date

# 12月のデータのみ抽出
df_dec = df[(pd.to_datetime(df['entry_at']).dt.month == 12) & (pd.to_datetime(df['entry_at']).dt.year == 2025)]

# 日付ごとの基本集計
print('=== 12月 日別売上サマリー ===\n')
for date in sorted(df_dec['date'].unique()):
    df_day = df_dec[df_dec['date'] == date]

    # 会計ごとにグループ化
    accounts = df_day.groupby('account_id').agg({
        'customer_count': 'first',
        'account_total': 'first'
    })

    total_customers = accounts['customer_count'].sum()
    total_sales = accounts['account_total'].sum()
    num_accounts = len(accounts)
    avg_per_customer = total_sales / total_customers if total_customers > 0 else 0

    print(f'{date}: 売上¥{total_sales:,.0f} / 客数{int(total_customers)}人 / 会計{num_accounts}組 / 客単価¥{avg_per_customer:,.0f}')

# 団体・貸切利用日のリスト（日報から）
group_dates = [
    '2025-12-09', '2025-12-11', '2025-12-12', '2025-12-13',
    '2025-12-16', '2025-12-18', '2025-12-19', '2025-12-27'
]

print('\n\n=== 団体・貸切利用日の詳細分析 ===\n')
for date_str in group_dates:
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    df_day = df_dec[df_dec['date'] == target_date]

    if len(df_day) == 0:
        print(f'【{date_str}】データなし\n')
        continue

    print(f'【{date_str}】')

    # 会計ごとの詳細
    accounts = df_day.groupby('account_id').agg({
        'customer_count': 'first',
        'account_total': 'first',
        'item_count': 'first'
    }).reset_index()

    total_customers = accounts['customer_count'].sum()
    total_sales = accounts['account_total'].sum()
    avg_per_customer = total_sales / total_customers if total_customers > 0 else 0

    print(f'  総売上: ¥{total_sales:,.0f}')
    print(f'  総客数: {int(total_customers)}人')
    print(f'  会計数: {len(accounts)}組')
    print(f'  客単価: ¥{avg_per_customer:,.0f}')

    # 大型団体の会計を特定（5名以上）
    large_groups = accounts[accounts['customer_count'] >= 5].sort_values('customer_count', ascending=False)
    if len(large_groups) > 0:
        print(f'  大型団体:')
        for idx, row in large_groups.iterrows():
            per_person = row['account_total'] / row['customer_count']
            print(f'    - {int(row["customer_count"])}名: ¥{row["account_total"]:,.0f} (1人あたり¥{per_person:,.0f})')

    # メニューランキング（数量ベース、tablecharge除く）
    df_day_menu = df_day[df_day['menu_name'] != 'tablecharge']
    menu_ranking = df_day_menu.groupby('menu_name').agg({
        'quantity': 'sum',
        'subtotal': 'sum'
    }).sort_values('quantity', ascending=False).head(10)

    if len(menu_ranking) > 0:
        print(f'  人気メニュー TOP10:')
        for menu, row in menu_ranking.iterrows():
            print(f'    - {menu}: {int(row["quantity"])}個 (¥{row["subtotal"]:,.0f})')

    print()

# 全体統計
print('\n=== 12月全体の統計 ===')
all_accounts = df_dec.groupby('account_id').agg({
    'customer_count': 'first',
    'account_total': 'first'
})
total_customers_dec = all_accounts['customer_count'].sum()
total_sales_dec = all_accounts['account_total'].sum()
total_accounts_dec = len(all_accounts)
avg_per_customer_dec = total_sales_dec / total_customers_dec if total_customers_dec > 0 else 0

print(f'総売上: ¥{total_sales_dec:,.0f}')
print(f'総客数: {int(total_customers_dec)}人')
print(f'総会計数: {total_accounts_dec}組')
print(f'平均客単価: ¥{avg_per_customer_dec:,.0f}')

# 12月全体の人気メニュー
print('\n=== 12月全体の人気メニュー TOP20 ===')
df_dec_menu = df_dec[df_dec['menu_name'] != 'tablecharge']
menu_ranking_all = df_dec_menu.groupby('menu_name').agg({
    'quantity': 'sum',
    'subtotal': 'sum'
}).sort_values('quantity', ascending=False).head(20)

for menu, row in menu_ranking_all.iterrows():
    print(f'{menu}: {int(row["quantity"])}個 (売上¥{row["subtotal"]:,.0f})')
