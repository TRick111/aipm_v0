import pandas as pd
import sys
from datetime import datetime

# UTF-8で出力
sys.stdout.reconfigure(encoding='utf-8')

# CSVファイルを読み込む
df = pd.read_csv(r'c:\Users\auk1i\aipm_v0\Stock\RestaurantAILab\週報\1_input\rawdata.csv')

# entry_atから日付を抽出
df['date'] = pd.to_datetime(df['entry_at']).dt.date

# 12月29-31日のデータを抽出
target_dates = ['2025-12-29', '2025-12-30', '2025-12-31']
df_target = df[df['date'].astype(str).isin(target_dates)]

print('=== 12月29-31日の詳細分析 ===\n')

for date_str in target_dates:
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    df_day = df_target[df_target['date'] == target_date]

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

    # 4名以上のグループを特定
    large_groups = accounts[accounts['customer_count'] >= 4].sort_values('customer_count', ascending=False)
    if len(large_groups) > 0:
        print(f'  4名以上のグループ:')
        for idx, row in large_groups.iterrows():
            print(f'    - {int(row["customer_count"])}名: ¥{row["account_total"]:,.0f} (1人あたり¥{row["account_total"]/row["customer_count"]:,.0f})')

            # このグループの注文内容を表示
            group_items = df_day[df_day['account_id'] == row['account_id']]
            menu_summary = group_items.groupby('menu_name').agg({
                'quantity': 'sum',
                'subtotal': 'sum'
            }).sort_values('subtotal', ascending=False)

            print(f'      主な注文:')
            for menu, data in menu_summary.head(5).iterrows():
                print(f'        {menu}: {int(data["quantity"])}個 (¥{data["subtotal"]:,.0f})')

    # 全体の人気メニュー TOP10
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
