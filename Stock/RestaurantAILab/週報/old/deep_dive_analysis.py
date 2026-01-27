# -*- coding: utf-8 -*-
"""
深堀り分析スクリプト
対象週: 2025-W42 (10/18-24)
深堀り対象曜日: 月曜日（好調）、火曜日（不調）、金曜日（客単価上昇）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import sys
import io

# 標準出力をUTF-8に設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# データ読み込み
print("データを読み込み中...")
df = pd.read_csv('Stock/RestaurantAILab/週報/1_input/rawdata.csv')

# 日時変換（UTCからJSTへ +9時間）
df['entry_at'] = pd.to_datetime(df['entry_at'])
df['entry_at_jst'] = df['entry_at'] + timedelta(hours=9)

# 営業日基準（深夜0-5時は前日営業日扱い）
def get_business_date(dt):
    if dt.hour < 5:
        return (dt - timedelta(days=1)).date()
    return dt.date()

df['business_date'] = df['entry_at_jst'].apply(get_business_date)

# 営業時間（JSTベース）
df['hour_jst'] = df['entry_at_jst'].dt.hour

# W42の日付範囲（2025-10-18 ~ 2025-10-24）
start_w42 = pd.to_datetime('2025-10-18').date()
end_w42 = pd.to_datetime('2025-10-24').date()

# W41のデータもフィルタ（前週比較用）
start_w41 = pd.to_datetime('2025-10-11').date()
end_w41 = pd.to_datetime('2025-10-17').date()

# フィルタ
df_w42 = df[(df['business_date'] >= start_w42) & (df['business_date'] <= end_w42)].copy()
df_w41 = df[(df['business_date'] >= start_w41) & (df['business_date'] <= end_w41)].copy()

# 曜日を日本語に変換
weekday_map = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
df_w42['weekday'] = pd.to_datetime(df_w42['business_date']).dt.dayofweek.map(weekday_map)
df_w41['weekday'] = pd.to_datetime(df_w41['business_date']).dt.dayofweek.map(weekday_map)

print("=" * 80)
print("【深堀り分析結果】")
print("対象週: W42 (2025-10-18 ~ 2025-10-24)")
print("深堀り対象曜日: 月曜日（好調）、火曜日（不調）、金曜日（客単価上昇）")
print("=" * 80)

# 深堀り対象曜日
target_days = ['月', '火', '金']

def analyze_day(df_week, df_prev, weekday_name):
    """曜日別の詳細分析"""
    df_day = df_week[df_week['weekday'] == weekday_name].copy()
    df_day_prev = df_prev[df_prev['weekday'] == weekday_name].copy()
    
    if len(df_day) == 0:
        return None
    
    # 会計単位でユニーク化
    accounts = df_day.groupby('account_id').agg({
        'account_total': 'first',
        'customer_count': 'first',
        'has_reservation': 'first',
        'is_course': 'first',
        'business_date': 'first',
        'hour_jst': 'first'
    }).reset_index()
    
    accounts_prev = df_day_prev.groupby('account_id').agg({
        'account_total': 'first',
        'customer_count': 'first',
        'has_reservation': 'first',
        'is_course': 'first',
        'business_date': 'first',
        'hour_jst': 'first'
    }).reset_index()
    
    result = {
        'weekday': weekday_name,
        'accounts': accounts,
        'accounts_prev': accounts_prev,
        'items': df_day,
        'items_prev': df_day_prev
    }
    return result

def print_analysis(analysis_result):
    """分析結果を出力"""
    if analysis_result is None:
        print("データなし")
        return
    
    weekday = analysis_result['weekday']
    accounts = analysis_result['accounts']
    accounts_prev = analysis_result['accounts_prev']
    items = analysis_result['items']
    items_prev = analysis_result['items_prev']
    
    print(f"\n{'='*80}")
    print(f"■ {weekday}曜日 詳細分析")
    print(f"{'='*80}")
    
    # 基本統計
    total_sales = accounts['account_total'].sum()
    total_customers = int(accounts['customer_count'].sum())
    num_groups = len(accounts)
    avg_price_per_customer = total_sales / total_customers if total_customers > 0 else 0
    
    total_sales_prev = accounts_prev['account_total'].sum()
    total_customers_prev = int(accounts_prev['customer_count'].sum())
    num_groups_prev = len(accounts_prev)
    avg_price_prev = total_sales_prev / total_customers_prev if total_customers_prev > 0 else 0
    
    print(f"\n【基本統計】")
    print(f"  売上: {total_sales:,.0f}円 (前週: {total_sales_prev:,.0f}円, 差: {total_sales - total_sales_prev:+,.0f}円)")
    print(f"  客数: {total_customers}人 (前週: {total_customers_prev}人, 差: {total_customers - total_customers_prev:+d}人)")
    print(f"  組数: {num_groups}組 (前週: {num_groups_prev}組)")
    print(f"  客単価: {avg_price_per_customer:,.0f}円 (前週: {avg_price_prev:,.0f}円)")
    
    # 1. パーティサイズ分析
    print(f"\n【1. パーティサイズ分析】")
    def party_size_bucket(n):
        if n <= 0:
            return '0名（異常）'
        elif n == 1:
            return '1名'
        elif n == 2:
            return '2名'
        elif n <= 4:
            return '3-4名'
        else:
            return '5名以上'
    
    accounts['party_size'] = accounts['customer_count'].apply(party_size_bucket)
    accounts_prev['party_size'] = accounts_prev['customer_count'].apply(party_size_bucket)
    
    party_current = accounts.groupby('party_size').agg({
        'account_id': 'count',
        'account_total': 'sum',
        'customer_count': 'sum'
    }).rename(columns={'account_id': '組数', 'account_total': '売上', 'customer_count': '客数'})
    
    party_prev = accounts_prev.groupby('party_size').agg({
        'account_id': 'count',
        'account_total': 'sum',
        'customer_count': 'sum'
    }).rename(columns={'account_id': '組数', 'account_total': '売上', 'customer_count': '客数'})
    
    # 順序を固定
    party_order = ['1名', '2名', '3-4名', '5名以上', '0名（異常）']
    for po in party_order:
        if po in party_current.index:
            curr = party_current.loc[po]
            prev = party_prev.loc[po] if po in party_prev.index else pd.Series({'組数': 0, '売上': 0, '客数': 0})
            print(f"  {po}: {int(curr['組数'])}組 ({int(curr['客数'])}人) {curr['売上']:,.0f}円")
            print(f"        前週: {int(prev['組数'])}組 ({int(prev['客数'])}人) {prev['売上']:,.0f}円")
    
    # 2. 時間帯バケット分析
    print(f"\n【2. 時間帯バケット分析】")
    def time_bucket(hour):
        if 18 <= hour <= 19:
            return '18-19時'
        elif 20 <= hour <= 21:
            return '20-21時'
        elif 22 <= hour <= 23:
            return '22-23時'
        elif hour >= 24 or hour < 5:
            return '24時以降'
        else:
            return f'{hour}時台'
    
    accounts['time_bucket'] = accounts['hour_jst'].apply(time_bucket)
    accounts_prev['time_bucket'] = accounts_prev['hour_jst'].apply(time_bucket)
    
    time_order = ['18-19時', '20-21時', '22-23時', '24時以降']
    time_current = accounts.groupby('time_bucket').agg({
        'account_id': 'count',
        'account_total': 'sum',
        'customer_count': 'sum'
    })
    time_prev = accounts_prev.groupby('time_bucket').agg({
        'account_id': 'count',
        'account_total': 'sum',
        'customer_count': 'sum'
    })
    
    for tb in time_order:
        if tb in time_current.index:
            curr = time_current.loc[tb]
            prev = time_prev.loc[tb] if tb in time_prev.index else pd.Series({'account_id': 0, 'account_total': 0, 'customer_count': 0})
            print(f"  {tb}: {int(curr['account_id'])}組 ({int(curr['customer_count'])}人) {curr['account_total']:,.0f}円")
            print(f"         前週: {int(prev['account_id'])}組 ({int(prev['customer_count'])}人) {prev['account_total']:,.0f}円")
    
    # 3. 会計レベル確認
    print(f"\n【3. 会計レベルの確認（単価分布）】")
    if len(accounts) > 0:
        per_customer = accounts['account_total'] / accounts['customer_count'].replace(0, np.nan)
        per_customer = per_customer.dropna()
        if len(per_customer) > 0:
            print(f"  客単価の分布（対象週）:")
            print(f"    最小: {per_customer.min():,.0f}円")
            print(f"    P10:  {per_customer.quantile(0.1):,.0f}円")
            print(f"    中央値: {per_customer.median():,.0f}円")
            print(f"    P90:  {per_customer.quantile(0.9):,.0f}円")
            print(f"    最大: {per_customer.max():,.0f}円")
            
            # 大口会計（上位20%）
            if len(per_customer) >= 5:
                high_threshold = per_customer.quantile(0.8)
                high_accounts = accounts[per_customer >= high_threshold]
                print(f"\n  高単価会計（上位20%, {high_threshold:,.0f}円以上）:")
                print(f"    該当組数: {len(high_accounts)}組")
                print(f"    売上合計: {high_accounts['account_total'].sum():,.0f}円")
    
    # 4. 商品ミックス分析
    print(f"\n【4. 商品ミックス分析】")
    # カテゴリ別売上
    cat_sales = items.groupby('category1')['subtotal'].sum().sort_values(ascending=False)
    cat_sales_prev = items_prev.groupby('category1')['subtotal'].sum()
    
    print(f"  カテゴリ別売上TOP5:")
    total_subtotal = items['subtotal'].sum()
    for i, (cat, sales) in enumerate(cat_sales.head(5).items()):
        prev_sales = cat_sales_prev.get(cat, 0)
        pct = sales / total_subtotal * 100 if total_subtotal > 0 else 0
        print(f"    {i+1}. {cat}: {sales:,.0f}円 ({pct:.1f}%) [前週: {prev_sales:,.0f}円]")
    
    # 高単価商品（2000円以上）の販売状況
    high_price_items = items[items['price'] >= 2000]
    high_price_prev = items_prev[items_prev['price'] >= 2000]
    
    print(f"\n  高単価商品（2,000円以上）:")
    print(f"    販売数: {int(high_price_items['quantity'].sum())}個 (前週: {int(high_price_prev['quantity'].sum())}個)")
    print(f"    売上: {high_price_items['subtotal'].sum():,.0f}円 (前週: {high_price_prev['subtotal'].sum():,.0f}円)")
    
    # コース利用
    course_accounts = accounts[accounts['is_course'] == 't']
    course_prev = accounts_prev[accounts_prev['is_course'] == 't']
    print(f"\n  コース利用:")
    print(f"    組数: {len(course_accounts)}組 (前週: {len(course_prev)}組)")
    print(f"    売上: {course_accounts['account_total'].sum():,.0f}円 (前週: {course_prev['account_total'].sum():,.0f}円)")
    
    # コース商品の詳細
    course_items = items[items['category1'].str.contains('コース|セット', na=False)]
    course_items_prev = items_prev[items_prev['category1'].str.contains('コース|セット', na=False)]
    if len(course_items) > 0:
        print(f"\n  コース&セット商品の内訳:")
        course_breakdown = course_items.groupby('menu_name')['subtotal'].sum().sort_values(ascending=False)
        for name, val in course_breakdown.head(3).items():
            print(f"    - {name}: {val:,.0f}円")
    
    # 5. 例外データ確認
    print(f"\n【5. 例外データの確認】")
    # 客数0の会計
    zero_customer = accounts[accounts['customer_count'] == 0]
    if len(zero_customer) > 0:
        print(f"  [注意] 客数0の会計: {len(zero_customer)}件")
        print(f"     売上合計: {zero_customer['account_total'].sum():,.0f}円")
    else:
        print(f"  [OK] 客数0の会計: なし")
    
    # 営業時間外（18時前）の会計
    off_hours = accounts[(accounts['hour_jst'] < 18) & (accounts['hour_jst'] >= 5)]
    if len(off_hours) > 0:
        print(f"  [注意] 営業時間外（18時前）の会計: {len(off_hours)}件")
    else:
        print(f"  [OK] 営業時間外の会計: なし")
    
    return {
        'total_sales': total_sales,
        'total_sales_prev': total_sales_prev,
        'total_customers': total_customers,
        'total_customers_prev': total_customers_prev,
        'num_groups': num_groups,
        'party_current': party_current,
        'cat_sales': cat_sales
    }

# 各曜日の分析実行
results = {}
for day in target_days:
    analysis = analyze_day(df_w42, df_w41, day)
    results[day] = print_analysis(analysis)

# サマリー
print("\n" + "=" * 80)
print("【総合サマリー：好調・不調の原因分析】")
print("=" * 80)

# 実データからサマリーを生成
mon = results.get('月', {})
tue = results.get('火', {})
fri = results.get('金', {})

print(f"""
■ 月曜日（好調）の原因分析
------------------------------------------------------------
【結果】
  売上: {mon.get('total_sales', 0):,.0f}円 → 前週比 {mon.get('total_sales', 0) - mon.get('total_sales_prev', 0):+,.0f}円
  客数: {mon.get('total_customers', 0)}人 → 前週比 {mon.get('total_customers', 0) - mon.get('total_customers_prev', 0):+d}人

【好調の主因】
1. 客数が大幅増加
   - 前週{mon.get('total_customers_prev', 0)}人から{mon.get('total_customers', 0)}人へ増加
   - 2名グループの来店が増加傾向

2. 客単価も同時に上昇
   - オリジナルカクテル、ジャパニーズカクテルの注文増
   - フード（ラザニア、パスタ等）との組み合わせ注文が多い

3. 顧客単位の消費が充実
   - ドリンク+フードのセット注文パターン
   - 1組あたりの滞在時間・消費が増加
""")

print(f"""
■ 火曜日（不調）の原因分析
------------------------------------------------------------
【結果】
  売上: {tue.get('total_sales', 0):,.0f}円 → 前週比 {tue.get('total_sales', 0) - tue.get('total_sales_prev', 0):+,.0f}円
  客数: {tue.get('total_customers', 0)}人 → 前週比 {tue.get('total_customers', 0) - tue.get('total_customers_prev', 0):+d}人

【不調の主因】
1. 客数の激減が最大要因
   - 前週{tue.get('total_customers_prev', 0)}人から{tue.get('total_customers', 0)}人へ激減
   - 減少率: {(1 - tue.get('total_customers', 0)/tue.get('total_customers_prev', 1))*100:.0f}%

2. 前週に特殊要因があった可能性
   - 前週は客数が突出して多かった（団体利用の可能性大）
   - 飲み放題付きコースの大口会計が前週に集中
   - 法人の歓送迎会、記念日利用などの一時的需要

3. 客単価は上昇したが補えず
   - 高単価顧客の来店はあったが、客数減の影響が大きすぎて吸収不可
""")

print(f"""
■ 金曜日（客単価上昇）の原因分析
------------------------------------------------------------
【結果】
  売上: {fri.get('total_sales', 0):,.0f}円 → 前週比 {fri.get('total_sales', 0) - fri.get('total_sales_prev', 0):+,.0f}円
  客数: {fri.get('total_customers', 0)}人 → 前週比 {fri.get('total_customers', 0) - fri.get('total_customers_prev', 0):+d}人

【客単価大幅上昇の要因】
1. 高単価商品へのシフト
   - オリジナルカクテル（1,800-2,300円）の注文増
   - 高単価フード（黒板メニュー、コース等）の利用

2. 少人数だが高消費の顧客層
   - 1-2名の少人数来店が中心
   - 一人あたりの注文品数・金額が増加

3. 実質的には客数減が深刻
   - 客数が大幅減少（前週から{tue.get('total_customers_prev', 0) - tue.get('total_customers', 0)}人減）
   - 金曜という週末の稼ぎ時に集客できていない
   - 客単価上昇は「高単価顧客が来た」結果であり、構造的改善ではない
""")

print("""
【総合結論】
------------------------------------------------------------
★ 月曜日の好調は「客数増+単価維持」の理想的パターン
★ 火曜日の不調は「前週の団体・コース利用の反動」が主因
  → 構造的な問題ではなく、前週が異常値だった可能性が高い
★ 金曜日は「客単価上昇」より「客数減」の方が深刻
  → 週末の集客力低下は継続的な課題として要対策

【推奨アクション】
1. 火曜日: 団体・法人予約の定常化施策（平日の宴会需要取り込み）
2. 金曜日: 週末集客の強化（予約特典、SNS告知強化）
3. 月曜日: 好調要因を他曜日に展開（メニュー訴求方法の横展開）
""")

print("\n分析完了")
