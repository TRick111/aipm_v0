#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
曜日深掘り分析スクリプト
対象週の最も好調だった日と最も不調だった日を詳細分析
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# 設定
SALES_DATA_PATH = r"Stock\RestaurantAILab\週報\1_input\BBC\rawdata.csv"
OUTPUT_DIR = r"Stock\RestaurantAILab\週報\2_output\BBC\2_output_2026w3"
TARGET_WEEK = "2026-W03"
BEST_DAY = "木曜日"  # 最も好調だった日
WORST_DAY = "水曜日"  # 最も不調だった日

# 営業日基準の日付（business_date）
# 2026-W03: 2026-01-12（月）〜 2026-01-18（日）
# 最も好調: 木曜日（2026-01-15）29人、¥265,040
# 最も不調: 水曜日（2026-01-14）4人、¥36,280
BEST_DATE = "2026-01-15"  # 木曜日
WORST_DATE = "2026-01-14"  # 水曜日

print("=" * 80)
print(f"曜日深掘り分析: {BEST_DAY} vs {WORST_DAY}")
print("=" * 80)
print()

# データ読み込み
print("データ読み込み中...")
df = pd.read_csv(SALES_DATA_PATH)

# UTC→JST変換
df['ordered_at_utc'] = pd.to_datetime(df['ordered_at'], utc=True)
df['ordered_at_jst'] = df['ordered_at_utc'].dt.tz_convert('Asia/Tokyo')

# 営業日基準の日付計算（JST 0-5時は前日営業日）
df['business_date'] = df['ordered_at_jst'].apply(
    lambda x: (x - timedelta(hours=5)).date()
)
df['business_hour'] = df['ordered_at_jst'].dt.hour

# 会計レベルの集計
accounts = df.groupby('account_id').agg({
    'business_date': 'first',
    'day_of_week': 'first',
    'account_total': 'first',
    'customer_count': 'first',
    'entry_at': 'first',
    'exit_at': 'first'
}).reset_index()

accounts['entry_at_jst'] = pd.to_datetime(accounts['entry_at'], utc=True).dt.tz_convert('Asia/Tokyo')
accounts['exit_at_jst'] = pd.to_datetime(accounts['exit_at'], utc=True).dt.tz_convert('Asia/Tokyo')
accounts['entry_hour'] = accounts['entry_at_jst'].dt.hour

# 対象日のデータ抽出
best_day_accounts = accounts[accounts['business_date'] == pd.to_datetime(BEST_DATE).date()].copy()
worst_day_accounts = accounts[accounts['business_date'] == pd.to_datetime(WORST_DATE).date()].copy()

best_day_items = df[df['business_date'] == pd.to_datetime(BEST_DATE).date()].copy()
worst_day_items = df[df['business_date'] == pd.to_datetime(WORST_DATE).date()].copy()

print(f"{BEST_DAY}（{BEST_DATE}）のデータ件数: 会計{len(best_day_accounts)}件、明細{len(best_day_items)}件")
print(f"{WORST_DAY}（{WORST_DATE}）のデータ件数: 会計{len(worst_day_accounts)}件、明細{len(worst_day_items)}件")
print()

# ============================================================
# 1. サマリー比較
# ============================================================
print("=" * 80)
print("1. サマリー比較")
print("=" * 80)

def get_summary(accounts_df, items_df, day_name):
    total_sales = accounts_df['account_total'].sum()
    total_customers = accounts_df['customer_count'].sum()
    total_accounts = len(accounts_df)
    avg_account = total_sales / total_accounts if total_accounts > 0 else 0
    avg_customer = total_sales / total_customers if total_customers > 0 else 0

    return {
        '曜日': day_name,
        '会計数': total_accounts,
        '客数': total_customers,
        '売上': f"¥{total_sales:,.0f}",
        '平均会計': f"¥{avg_account:,.0f}",
        '客単価': f"¥{avg_customer:,.0f}"
    }

summary_best = get_summary(best_day_accounts, best_day_items, BEST_DAY)
summary_worst = get_summary(worst_day_accounts, worst_day_items, WORST_DAY)

summary_df = pd.DataFrame([summary_best, summary_worst])
print(summary_df.to_string(index=False))
print()

# ============================================================
# 2. パーティサイズ分析
# ============================================================
print("=" * 80)
print("2. パーティサイズ分析")
print("=" * 80)

def analyze_party_size(accounts_df, day_name):
    accounts_df['party_size'] = accounts_df['customer_count'].apply(
        lambda x: '1名' if x == 1 else ('2名' if x == 2 else ('3-4名' if 3 <= x <= 4 else '5名以上'))
    )

    party_analysis = accounts_df.groupby('party_size').agg({
        'account_id': 'count',
        'customer_count': 'sum',
        'account_total': 'sum'
    }).reset_index()
    party_analysis.columns = ['パーティサイズ', '会計数', '客数', '売上']
    party_analysis['平均会計'] = party_analysis['売上'] / party_analysis['会計数']
    party_analysis['客単価'] = party_analysis['売上'] / party_analysis['客数']
    party_analysis['構成比'] = (party_analysis['売上'] / party_analysis['売上'].sum() * 100).round(1)

    party_analysis = party_analysis.sort_values('売上', ascending=False)

    print(f"\n【{day_name}】")
    print(party_analysis.to_string(index=False))

    return party_analysis

party_best = analyze_party_size(best_day_accounts, BEST_DAY)
party_worst = analyze_party_size(worst_day_accounts, WORST_DAY)
print()

# ============================================================
# 3. 時間帯バケット分析
# ============================================================
print("=" * 80)
print("3. 時間帯バケット分析（営業時間基準）")
print("=" * 80)

def analyze_time_bucket(accounts_df, day_name):
    # 入店時間でバケット化
    def get_time_bucket(hour):
        if 16 <= hour < 18:
            return '16-18時'
        elif 18 <= hour < 20:
            return '18-20時'
        elif 20 <= hour < 22:
            return '20-22時'
        elif 22 <= hour < 24:
            return '22-24時'
        else:
            return 'その他'

    accounts_df['time_bucket'] = accounts_df['entry_hour'].apply(get_time_bucket)

    time_analysis = accounts_df.groupby('time_bucket').agg({
        'account_id': 'count',
        'customer_count': 'sum',
        'account_total': 'sum'
    }).reset_index()
    time_analysis.columns = ['時間帯', '会計数', '客数', '売上']
    time_analysis['平均会計'] = time_analysis['売上'] / time_analysis['会計数']
    time_analysis['構成比'] = (time_analysis['売上'] / time_analysis['売上'].sum() * 100).round(1)

    # 時間帯順にソート
    time_order = ['16-18時', '18-20時', '20-22時', '22-24時', 'その他']
    time_analysis['sort_key'] = time_analysis['時間帯'].apply(lambda x: time_order.index(x) if x in time_order else 999)
    time_analysis = time_analysis.sort_values('sort_key').drop('sort_key', axis=1)

    print(f"\n【{day_name}】")
    print(time_analysis.to_string(index=False))

    return time_analysis

time_best = analyze_time_bucket(best_day_accounts, BEST_DAY)
time_worst = analyze_time_bucket(worst_day_accounts, WORST_DAY)
print()

# ============================================================
# 4. 会計レベル分析
# ============================================================
print("=" * 80)
print("4. 会計レベル分析")
print("=" * 80)

def analyze_account_level(accounts_df, day_name):
    account_totals = accounts_df['account_total'].values

    if len(account_totals) == 0:
        print(f"\n【{day_name}】データなし")
        return

    # 統計量
    stats = {
        '最大会計': f"¥{account_totals.max():,.0f}",
        '最小会計': f"¥{account_totals.min():,.0f}",
        '中央値': f"¥{np.median(account_totals):,.0f}",
        'P10': f"¥{np.percentile(account_totals, 10):,.0f}",
        'P90': f"¥{np.percentile(account_totals, 90):,.0f}",
        '平均': f"¥{account_totals.mean():,.0f}"
    }

    print(f"\n【{day_name}】")
    for key, value in stats.items():
        print(f"{key}: {value}")

    # 会計金額分布
    def get_price_range(price):
        if price < 5000:
            return '~5千円'
        elif price < 10000:
            return '5千~1万円'
        elif price < 15000:
            return '1万~1.5万円'
        elif price < 20000:
            return '1.5万~2万円'
        else:
            return '2万円以上'

    accounts_df['price_range'] = accounts_df['account_total'].apply(get_price_range)

    price_dist = accounts_df.groupby('price_range').agg({
        'account_id': 'count'
    }).reset_index()
    price_dist.columns = ['価格帯', '会計数']
    price_dist['構成比'] = (price_dist['会計数'] / price_dist['会計数'].sum() * 100).round(1)

    # 価格帯順にソート
    price_order = ['~5千円', '5千~1万円', '1万~1.5万円', '1.5万~2万円', '2万円以上']
    price_dist['sort_key'] = price_dist['価格帯'].apply(lambda x: price_order.index(x) if x in price_order else 999)
    price_dist = price_dist.sort_values('sort_key').drop('sort_key', axis=1)

    print("\n会計金額分布:")
    print(price_dist.to_string(index=False))

    return stats, price_dist

stats_best, price_dist_best = analyze_account_level(best_day_accounts, BEST_DAY)
stats_worst, price_dist_worst = analyze_account_level(worst_day_accounts, WORST_DAY)
print()

# ============================================================
# 5. 商品ミックス分析
# ============================================================
print("=" * 80)
print("5. 商品ミックス分析")
print("=" * 80)

def analyze_product_mix(items_df, day_name):
    # カテゴリ別売上TOP5
    category_sales = items_df.groupby('category1').agg({
        'subtotal': 'sum',
        'quantity': 'sum'
    }).reset_index()
    category_sales.columns = ['カテゴリ', '売上', '販売数']
    category_sales['構成比'] = (category_sales['売上'] / category_sales['売上'].sum() * 100).round(1)
    category_sales = category_sales.sort_values('売上', ascending=False).head(5)

    print(f"\n【{day_name}】カテゴリ別売上TOP5")
    print(category_sales.to_string(index=False))

    # 高単価商品（¥1,500以上）の販売状況
    high_price_items = items_df[items_df['price'] >= 1500].copy()
    if len(high_price_items) > 0:
        high_price_sales = high_price_items['subtotal'].sum()
        high_price_qty = high_price_items['quantity'].sum()
        total_sales = items_df['subtotal'].sum()
        high_price_ratio = (high_price_sales / total_sales * 100) if total_sales > 0 else 0

        print(f"\n高単価商品（¥1,500以上）:")
        print(f"  販売数: {high_price_qty}個")
        print(f"  売上: ¥{high_price_sales:,.0f}")
        print(f"  構成比: {high_price_ratio:.1f}%")

        # TOP5高単価商品
        high_price_top = high_price_items.groupby('menu_name').agg({
            'subtotal': 'sum',
            'quantity': 'sum',
            'price': 'first'
        }).reset_index()
        high_price_top.columns = ['商品名', '売上', '販売数', '単価']
        high_price_top = high_price_top.sort_values('売上', ascending=False).head(5)

        print("\n  高単価商品TOP5:")
        print(high_price_top.to_string(index=False))
    else:
        print(f"\n高単価商品（¥1,500以上）: なし")

    return category_sales

product_mix_best = analyze_product_mix(best_day_items, BEST_DAY)
product_mix_worst = analyze_product_mix(worst_day_items, WORST_DAY)
print()

# ============================================================
# 6. 例外データ確認
# ============================================================
print("=" * 80)
print("6. 例外データ確認")
print("=" * 80)

def check_exceptions(accounts_df, items_df, day_name):
    # 営業時間外会計（深夜0-6時）
    late_night = accounts_df[
        (accounts_df['entry_hour'] >= 0) & (accounts_df['entry_hour'] < 6)
    ]

    # 高額会計（1人あたり¥10,000超）
    high_per_customer = accounts_df[
        (accounts_df['account_total'] / accounts_df['customer_count']) > 10000
    ]

    # 大人数パーティ（10名以上）
    large_party = accounts_df[accounts_df['customer_count'] >= 10]

    print(f"\n【{day_name}】")
    print(f"営業時間外会計（深夜0-6時）: {len(late_night)}件")
    if len(late_night) > 0:
        print(f"  総売上: ¥{late_night['account_total'].sum():,.0f}")

    print(f"高額会計（1人単価¥10,000超）: {len(high_per_customer)}件")
    if len(high_per_customer) > 0:
        print(f"  総売上: ¥{high_per_customer['account_total'].sum():,.0f}")

    print(f"大人数パーティ（10名以上）: {len(large_party)}件")
    if len(large_party) > 0:
        print(f"  総客数: {large_party['customer_count'].sum()}名")
        print(f"  総売上: ¥{large_party['account_total'].sum():,.0f}")

check_exceptions(best_day_accounts, best_day_items, BEST_DAY)
check_exceptions(worst_day_accounts, worst_day_items, WORST_DAY)
print()

print("=" * 80)
print("分析完了")
print("=" * 80)
