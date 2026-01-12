#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
曜日別深堀分析スクリプト
対象週(2025-W52)の曜日別詳細分析を実施し、週報基礎資料に組み込む内容を生成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# ファイルパス
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(SCRIPT_DIR, "1_input", "rawdata.csv")
OUTPUT_MD = os.path.join(SCRIPT_DIR, "2_output_2025w52", "曜日別深堀分析結果.md")

def load_and_prep_data(csv_path):
    """
    CSVを読み込み、UTC→JST変換、営業日計算を実施
    """
    print("データ読み込み中...")
    df = pd.read_csv(csv_path)

    # UTC → JST 変換 (exit_atを使用)
    df['exit_at'] = pd.to_datetime(df['exit_at'], utc=True)
    df['exit_at_JST'] = df['exit_at'].dt.tz_convert('Asia/Tokyo')

    # 営業日計算 (深夜0-5時は前日の営業日に付け替え)
    df['hour'] = df['exit_at_JST'].dt.hour
    df['date'] = df['exit_at_JST'].dt.date

    # 深夜0-5時は前日の営業日
    df['営業日'] = df.apply(
        lambda row: row['date'] - timedelta(days=1) if row['hour'] < 6 else row['date'],
        axis=1
    )
    df['営業日'] = pd.to_datetime(df['営業日'])

    # 営業時間計算 (24時以降は25, 26...)
    df['営業時間'] = df.apply(
        lambda row: row['hour'] if row['hour'] >= 6 else row['hour'] + 24,
        axis=1
    )

    # 曜日追加
    df['曜日'] = df['営業日'].dt.day_name()
    df['曜日_日本語'] = df['営業日'].dt.day_name().map({
        'Monday': '月曜日',
        'Tuesday': '火曜日',
        'Wednesday': '水曜日',
        'Thursday': '木曜日',
        'Friday': '金曜日',
        'Saturday': '土曜日',
        'Sunday': '日曜日'
    })

    # ISO週番号
    df['年'] = df['営業日'].dt.isocalendar().year
    df['週番号'] = df['営業日'].dt.isocalendar().week

    print(f"データ読み込み完了: {len(df)}行")
    return df


def get_target_and_past_weeks(df, target_year=2025, target_week=52):
    """
    対象週と過去4週間のデータを抽出
    """
    # 対象週
    target_df = df[(df['年'] == target_year) & (df['週番号'] == target_week)].copy()

    # 過去4週間 (W48-W51)
    past_weeks_df = df[
        (df['年'] == target_year) &
        (df['週番号'].between(target_week - 4, target_week - 1))
    ].copy()

    print(f"対象週(W{target_week}): {len(target_df)}行")
    print(f"過去4週間(W{target_week-4}-W{target_week-1}): {len(past_weeks_df)}行")

    return target_df, past_weeks_df


def weekday_summary(df):
    """
    曜日別サマリーを計算
    """
    # 会計単位でユニークな売上を計算（明細データなので重複排除が必要）
    account_level = df.groupby(['account_id', '曜日_日本語', '営業日']).agg({
        'account_total': 'first',  # 会計の総額（同じaccount_idで同じ値）
        'customer_count': 'first'   # 客数（同じaccount_idで同じ値）
    }).reset_index()

    # 曜日別集計
    summary = account_level.groupby('曜日_日本語').agg({
        'account_total': 'sum',
        'account_id': 'count',
        'customer_count': 'sum',
        '営業日': 'nunique'
    }).rename(columns={
        'account_total': '売上',
        'account_id': '会計数',
        'customer_count': '客数',
        '営業日': '営業日数'
    })

    summary['客単価'] = (summary['売上'] / summary['客数']).round(0)

    # 曜日順にソート
    weekday_order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    summary = summary.reindex([w for w in weekday_order if w in summary.index])

    return summary


def weekday_factor_decomposition(target_summary, past_summary):
    """
    ミッドポイント法による曜日別要因分解
    """
    results = []

    for weekday in target_summary.index:
        if weekday not in past_summary.index:
            continue

        # 対象週
        S1 = target_summary.loc[weekday, '売上']
        P1 = target_summary.loc[weekday, '客数']
        A1 = target_summary.loc[weekday, '客単価']

        # 過去4週平均
        S0 = past_summary.loc[weekday, '売上'] / past_summary.loc[weekday, '営業日数']
        P0 = past_summary.loc[weekday, '客数'] / past_summary.loc[weekday, '営業日数']
        A0 = past_summary.loc[weekday, '客単価']

        # 売上差
        delta_S = S1 - S0

        # 客数要因寄与
        contrib_P = (P1 - P0) * (A1 + A0) / 2

        # 客単価要因寄与
        contrib_A = (A1 - A0) * (P1 + P0) / 2

        results.append({
            '曜日': weekday,
            '対象週売上': S1,
            '過去4週平均売上': S0,
            '売上差': delta_S,
            '対象週客数': P1,
            '過去4週平均客数': P0,
            '客数差': P1 - P0,
            '対象週客単価': A1,
            '過去4週平均客単価': A0,
            '客単価差': A1 - A0,
            '客数要因寄与': contrib_P,
            '客単価要因寄与': contrib_A,
            '検算': contrib_P + contrib_A
        })

    return pd.DataFrame(results)


def hourly_analysis_by_weekday(df):
    """
    曜日別×時刻別の売上分析
    """
    # 会計単位で集計（重複排除）
    account_level = df.groupby(['account_id', '曜日_日本語', '営業時間']).agg({
        'account_total': 'first',
        'customer_count': 'first'
    }).reset_index()

    # 曜日×時間別集計
    hourly_data = account_level.groupby(['曜日_日本語', '営業時間']).agg({
        'account_total': 'sum',
        'account_id': 'count',
        'customer_count': 'sum'
    }).reset_index()

    hourly_data.columns = ['曜日', '営業時間', '売上', '会計数', '客数']
    hourly_data['客単価'] = (hourly_data['売上'] / hourly_data['客数']).round(0)

    return hourly_data


def weekend_weekday_comparison(df):
    """
    週末(金土日) vs 平日の構成比分析
    """
    # 会計単位で集計（重複排除）
    account_level = df.groupby(['account_id', '曜日_日本語']).agg({
        'account_total': 'first',
        'customer_count': 'first'
    }).reset_index()

    account_level['区分'] = account_level['曜日_日本語'].apply(
        lambda x: '週末' if x in ['金曜日', '土曜日', '日曜日'] else '平日'
    )

    summary = account_level.groupby('区分').agg({
        'account_total': 'sum',
        'account_id': 'count',
        'customer_count': 'sum'
    }).rename(columns={
        'account_total': '売上',
        'account_id': '会計数',
        'customer_count': '客数'
    })

    summary['売上構成比'] = (summary['売上'] / summary['売上'].sum() * 100).round(1)
    summary['客数構成比'] = (summary['客数'] / summary['客数'].sum() * 100).round(1)

    return summary


def analyze_weekly_trends(df, target_year=2025, target_week=52):
    """
    過去4週間の週次推移を曜日別に分析
    """
    # 対象週と過去4週間
    weeks_to_analyze = list(range(target_week - 4, target_week + 1))

    weekly_trends = []

    for week in weeks_to_analyze:
        week_df = df[(df['年'] == target_year) & (df['週番号'] == week)].copy()

        if len(week_df) == 0:
            continue

        # 会計単位で集計
        account_level = week_df.groupby(['account_id', '曜日_日本語']).agg({
            'account_total': 'first',
            'customer_count': 'first'
        }).reset_index()

        # 曜日別集計
        weekday_data = account_level.groupby('曜日_日本語').agg({
            'account_total': 'sum',
            'account_id': 'count',
            'customer_count': 'sum'
        }).rename(columns={
            'account_total': '売上',
            'account_id': '会計数',
            'customer_count': '客数'
        })

        weekday_data['客単価'] = (weekday_data['売上'] / weekday_data['客数']).round(0)
        weekday_data['週番号'] = week

        weekly_trends.append(weekday_data)

    return pd.concat(weekly_trends)


def get_week_date_range(year, week_num):
    """
    ISO週番号から日付範囲を取得
    """
    from datetime import datetime, timedelta
    # ISO週の月曜日を取得
    jan4 = datetime(year, 1, 4)
    week_start = jan4 + timedelta(days=-jan4.weekday(), weeks=week_num-1)
    week_end = week_start + timedelta(days=6)
    return week_start.strftime("%m/%d"), week_end.strftime("%m/%d")


def analyze_party_size(df, weekday):
    """
    特定曜日のパーティサイズ別分析
    """
    weekday_df = df[df['曜日_日本語'] == weekday].copy()

    if len(weekday_df) == 0:
        return pd.DataFrame()

    # 会計単位で集計
    account_level = weekday_df.groupby(['account_id', 'customer_count']).agg({
        'account_total': 'first'
    }).reset_index()

    # パーティサイズの分類
    def classify_party_size(count):
        if count == 1:
            return '1名'
        elif count == 2:
            return '2名'
        elif count <= 4:
            return '3-4名'
        else:
            return '5名以上'

    account_level['パーティサイズ'] = account_level['customer_count'].apply(classify_party_size)

    # パーティサイズごとに集計
    party_summary = account_level.groupby('パーティサイズ').agg({
        'account_id': 'count',
        'customer_count': 'sum',
        'account_total': 'sum'
    }).rename(columns={
        'account_id': '組数',
        'customer_count': '客数',
        'account_total': '売上'
    })

    party_summary['組あたり売上'] = (party_summary['売上'] / party_summary['組数']).round(0)

    # カテゴリ順にソート
    size_order = ['1名', '2名', '3-4名', '5名以上']
    party_summary = party_summary.reindex([s for s in size_order if s in party_summary.index])

    return party_summary


def analyze_time_slots(df, weekday):
    """
    特定曜日の時間帯別分析
    """
    weekday_df = df[df['曜日_日本語'] == weekday].copy()

    if len(weekday_df) == 0:
        return pd.DataFrame()

    # 営業時間から時間帯を分類
    def classify_time_slot(hour):
        if 18 <= hour < 20:
            return '18-20時'
        elif 20 <= hour < 22:
            return '20-22時'
        elif 22 <= hour < 24:
            return '22-24時'
        elif hour >= 24 or hour < 2:
            return '24-2時'
        else:
            return 'その他'

    weekday_df['時間帯'] = weekday_df['営業時間'].apply(classify_time_slot)

    # 会計単位で集計
    account_level = weekday_df.groupby(['account_id', '時間帯', 'customer_count']).agg({
        'account_total': 'first'
    }).reset_index()

    # 時間帯ごとに集計
    time_summary = account_level.groupby('時間帯').agg({
        'account_id': 'count',
        'customer_count': 'sum',
        'account_total': 'sum'
    }).rename(columns={
        'account_id': '組数',
        'customer_count': '客数',
        'account_total': '売上'
    })

    # 時間帯順にソート
    time_order = ['18-20時', '20-22時', '22-24時', '24-2時', 'その他']
    time_summary = time_summary.reindex([t for t in time_order if t in time_summary.index])

    return time_summary


def analyze_category_mix(df, weekday):
    """
    特定曜日の商品カテゴリ別分析
    """
    weekday_df = df[df['曜日_日本語'] == weekday].copy()

    if len(weekday_df) == 0:
        return pd.DataFrame()

    # カテゴリ別に集計（行単位の売上）
    category_summary = weekday_df.groupby('category1').agg({
        'subtotal': 'sum',
        'quantity': 'sum'
    }).rename(columns={
        'subtotal': '売上',
        'quantity': '数量'
    })

    # 総売上を計算
    total_sales = category_summary['売上'].sum()
    category_summary['構成比'] = (category_summary['売上'] / total_sales * 100).round(1)

    # 売上順にソート
    category_summary = category_summary.sort_values('売上', ascending=False)

    return category_summary.head(10)  # TOP10のみ


def analyze_unit_price_distribution(df, weekday):
    """
    特定曜日の客単価分布を分析
    """
    weekday_df = df[df['曜日_日本語'] == weekday].copy()

    if len(weekday_df) == 0:
        return {}

    # 会計単位で客単価を計算
    account_level = weekday_df.groupby('account_id').agg({
        'account_total': 'first',
        'customer_count': 'first'
    }).reset_index()

    account_level['客単価'] = account_level['account_total'] / account_level['customer_count']

    unit_prices = account_level['客単価']

    return {
        '最小': unit_prices.min(),
        'P10': unit_prices.quantile(0.1),
        '中央値': unit_prices.median(),
        'P90': unit_prices.quantile(0.9),
        '最大': unit_prices.max()
    }


def generate_insights(decomp_df, target_summary, past_df, target_df, target_year=2025, target_week=52):
    """
    分析結果から洞察を生成（原因分析を含む）
    """
    insights = []

    # 過去4週間の週次推移を取得
    weekly_trends = analyze_weekly_trends(
        pd.concat([past_df, target_df]),
        target_year=target_year,
        target_week=target_week
    )

    # 深堀対象曜日を特定（客数要因・客単価要因の最大プラス/マイナス）
    target_weekdays = set()

    # 客数要因の最大プラス/マイナス
    max_customer_contrib = decomp_df.nlargest(1, '客数要因寄与').iloc[0]
    min_customer_contrib = decomp_df.nsmallest(1, '客数要因寄与').iloc[0]
    target_weekdays.add(max_customer_contrib['曜日'])
    target_weekdays.add(min_customer_contrib['曜日'])

    # 客単価要因の最大プラス/マイナス
    max_price_contrib = decomp_df.nlargest(1, '客単価要因寄与').iloc[0]
    min_price_contrib = decomp_df.nsmallest(1, '客単価要因寄与').iloc[0]
    target_weekdays.add(max_price_contrib['曜日'])
    target_weekdays.add(min_price_contrib['曜日'])

    insights.append("### 深堀対象曜日の原因分析")
    insights.append("")
    insights.append("**深堀対象曜日の選定基準**: 客数要因・客単価要因それぞれで最大プラス/マイナスの曜日を抽出")
    insights.append("")
    insights.append(f"- **客数要因 最大プラス**: {max_customer_contrib['曜日']} (+¥{max_customer_contrib['客数要因寄与']:,.0f})")
    insights.append(f"- **客数要因 最大マイナス**: {min_customer_contrib['曜日']} (¥{min_customer_contrib['客数要因寄与']:,.0f})")
    insights.append(f"- **客単価要因 最大プラス**: {max_price_contrib['曜日']} (+¥{max_price_contrib['客単価要因寄与']:,.0f})")
    insights.append(f"- **客単価要因 最大マイナス**: {min_price_contrib['曜日']} (¥{min_price_contrib['客単価要因寄与']:,.0f})")
    insights.append("")
    insights.append("---")
    insights.append("")

    # 各曜日の原因分析（深堀対象のみ）
    for _, row in decomp_df.iterrows():
        weekday = row['曜日']

        # 深堀対象でない曜日はスキップ
        if weekday not in target_weekdays:
            continue

        # その曜日の過去4週間+対象週のデータを取得
        weekday_trend = weekly_trends[weekly_trends.index == weekday].copy()

        if len(weekday_trend) == 0:
            continue

        # 好調/不調の判定
        sales_diff = row['売上差']
        if sales_diff > 0:
            status = f"好調（売上差+¥{sales_diff:,.0f}）"
        else:
            status = f"不調（売上差¥{sales_diff:,.0f}）"

        insights.append(f"### {weekday}（{status}）")
        insights.append("")

        # ==== 1. 基本指標テーブル ====
        insights.append("#### 基本指標")
        insights.append("")

        # 対象週のデータ
        target_weekday_df = target_df[target_df['曜日_日本語'] == weekday]
        past_weekday_df = past_df[past_df['曜日_日本語'] == weekday]

        # 対象週の指標を計算
        target_accounts = target_weekday_df.groupby('account_id').agg({
            'account_total': 'first',
            'customer_count': 'first'
        }).reset_index()

        target_sales = target_accounts['account_total'].sum()
        target_customers = target_accounts['customer_count'].sum()
        target_account_count = len(target_accounts)
        target_unit_price = target_sales / target_customers if target_customers > 0 else 0

        # 過去4週平均の指標を計算
        past_accounts = past_weekday_df.groupby(['account_id', '営業日']).agg({
            'account_total': 'first',
            'customer_count': 'first'
        }).reset_index()

        past_sales_avg = past_accounts.groupby('営業日')['account_total'].sum().mean()
        past_customers_avg = past_accounts.groupby('営業日')['customer_count'].sum().mean()
        past_account_count_avg = past_accounts.groupby('営業日')['account_id'].count().mean()
        past_unit_price_avg = past_sales_avg / past_customers_avg if past_customers_avg > 0 else 0

        # 変化を計算
        sales_change = target_sales - past_sales_avg
        customers_change = target_customers - past_customers_avg
        account_change = target_account_count - past_account_count_avg
        unit_price_change = target_unit_price - past_unit_price_avg

        sales_change_pct = (sales_change / past_sales_avg * 100) if past_sales_avg > 0 else 0
        customers_change_pct = (customers_change / past_customers_avg * 100) if past_customers_avg > 0 else 0
        account_change_pct = (account_change / past_account_count_avg * 100) if past_account_count_avg > 0 else 0
        unit_price_change_pct = (unit_price_change / past_unit_price_avg * 100) if past_unit_price_avg > 0 else 0

        insights.append("| 指標 | 対象週(W52) | 過去4週平均 | 変化 | 変化率 |")
        insights.append("|------|-------------|-------------|------|--------|")
        insights.append(f"| 売上 | ¥{target_sales:,.0f} | ¥{past_sales_avg:,.0f} | ¥{sales_change:,.0f} | {sales_change_pct:+.1f}% |")
        insights.append(f"| 客数 | {target_customers:.0f}人 | {past_customers_avg:.1f}人 | {customers_change:+.1f}人 | {customers_change_pct:+.1f}% |")
        insights.append(f"| 組数 | {target_account_count:.0f}組 | {past_account_count_avg:.1f}組 | {account_change:+.1f}組 | {account_change_pct:+.1f}% |")
        insights.append(f"| 客単価 | ¥{target_unit_price:,.0f} | ¥{past_unit_price_avg:,.0f} | ¥{unit_price_change:+,.0f} | {unit_price_change_pct:+.1f}% |")
        insights.append("")

        # ==== 2. 原因分析セクション ====
        insights.append(f"#### {weekday}の原因分析")
        insights.append("")

        # 客数の推移から異常値を検出
        weekday_trend_sorted = weekday_trend.sort_values('週番号')
        customer_counts = weekday_trend_sorted['客数'].values
        unit_prices = weekday_trend_sorted['客単価'].values

        # 要因を取得
        customer_contrib = row['客数要因寄与']
        price_contrib = row['客単価要因寄与']

        # 売上への影響度を判定
        is_customer_dominant = abs(customer_contrib) > abs(price_contrib)

        # 原因の特定
        reasons_customer = []
        reasons_price = []

        if len(customer_counts) >= 4:
            past_4_std = customer_counts[:-1].std()
            past_4_mean = customer_counts[:-1].mean()
            current_count = customer_counts[-1]

            # 異常値判定（2σを超えるか）
            if abs(current_count - past_4_mean) > 2 * past_4_std:
                if current_count > past_4_mean:
                    reasons_customer.append(f"対象週の客数({current_count:.0f}人)は過去4週平均({past_4_mean:.1f}人)から+{(current_count - past_4_mean):.1f}人増加。特別なイベント、大口予約、プロモーションの成功などが考えられる。")
                else:
                    reasons_customer.append(f"対象週の客数({current_count:.0f}人)は過去4週平均({past_4_mean:.1f}人)から{(current_count - past_4_mean):.1f}人減少。悪天候、イベント中止、競合店の影響などが考えられる。")
            else:
                # 過去4週に異常値があるか確認
                max_week_idx = customer_counts[:-1].argmax()
                min_week_idx = customer_counts[:-1].argmin()
                max_count = customer_counts[max_week_idx]
                min_count = customer_counts[min_week_idx]
                week_nums = sorted(weekday_trend['週番号'].unique())

                if max_count > past_4_mean + 1.5 * past_4_std:
                    start_date, end_date = get_week_date_range(target_year, int(week_nums[max_week_idx]))
                    reasons_customer.append(f"W{int(week_nums[max_week_idx])}({start_date}-{end_date})に異常高値({max_count:.0f}人)があり、平均を押し上げている。対象週({current_count:.0f}人)は正常範囲内のため、見かけ上の減少であり気にする必要はない。")
                elif min_count < past_4_mean - 1.5 * past_4_std:
                    start_date, end_date = get_week_date_range(target_year, int(week_nums[min_week_idx]))
                    reasons_customer.append(f"W{int(week_nums[min_week_idx])}({start_date}-{end_date})に異常低値({min_count:.0f}人)があり、平均を押し下げている。対象週({current_count:.0f}人)は正常範囲内のため、見かけ上の増加。")
                else:
                    # トレンド分析
                    trend_slope = (customer_counts[-1] - customer_counts[-4]) / 4
                    if abs(trend_slope) > 2:
                        if trend_slope > 0:
                            reasons_customer.append(f"過去4週間で+{trend_slope*4:.1f}人増加。集客施策の効果、口コミの拡散、季節要因などが継続的に作用している。")
                        else:
                            reasons_customer.append(f"過去4週間で{trend_slope*4:.1f}人減少。競合店の影響、季節要因、顧客離れなどの構造的な課題がある可能性。")
                    elif abs(customer_contrib) > 20000:  # 客数要因の寄与が大きい場合
                        if customer_contrib > 0:
                            reasons_customer.append(f"過去4週平均から+{(current_count - past_4_mean):.1f}人増加（客数要因+¥{customer_contrib:,.0f}）。通常の変動範囲内だが、集客が好調。")
                        else:
                            reasons_customer.append(f"過去4週平均から{(current_count - past_4_mean):.1f}人減少（客数要因¥{customer_contrib:,.0f}）。通常の変動範囲内だが、集客に注意。")

        # 客単価の変動分析
        if len(unit_prices) >= 4:
            past_4_price_mean = unit_prices[:-1].mean()
            current_price = unit_prices[-1]
            price_change_pct = ((current_price - past_4_price_mean) / past_4_price_mean) * 100

            if abs(price_change_pct) > 10:
                if price_change_pct > 0:
                    reasons_price.append(f"過去4週平均¥{past_4_price_mean:.0f} → 対象週¥{current_price:.0f} (+{price_change_pct:.1f}%)。高単価メニュー（コース、ワインボトル等）の注文増、または高単価層の来店増が要因。")
                else:
                    reasons_price.append(f"過去4週平均¥{past_4_price_mean:.0f} → 対象週¥{current_price:.0f} ({price_change_pct:.1f}%)。カジュアル層の来店増、低単価メニューへのシフト、または客数増に伴う単価希薄化が要因。")
            elif abs(price_contrib) > 15000:  # 客単価要因の寄与が大きい場合
                if price_contrib > 0:
                    reasons_price.append(f"過去4週平均¥{past_4_price_mean:.0f} → 対象週¥{current_price:.0f} (+{price_change_pct:.1f}%)。")
                else:
                    reasons_price.append(f"過去4週平均¥{past_4_price_mean:.0f} → 対象週¥{current_price:.0f} ({price_change_pct:.1f}%)。")

        # 原因を影響度順に出力
        if is_customer_dominant:
            # 客数要因が支配的
            if reasons_customer:
                insights.append(f"**1. 客数{'増加' if customer_contrib > 0 else '減少'}の背景（¥{customer_contrib:,.0f}寄与）**")
                insights.append("")
                for reason in reasons_customer:
                    insights.append(f"- {reason}")
                insights.append("")
            if reasons_price:
                insights.append(f"**2. 客単価{'上昇' if price_contrib > 0 else '下落'}の要因（¥{price_contrib:,.0f}寄与）**")
                insights.append("")
                for reason in reasons_price:
                    insights.append(f"- {reason}")
                insights.append("")
        else:
            # 客単価要因が支配的
            if reasons_price:
                insights.append(f"**1. 客単価{'上昇' if price_contrib > 0 else '下落'}の要因（¥{price_contrib:,.0f}寄与）**")
                insights.append("")
                for reason in reasons_price:
                    insights.append(f"- {reason}")
                insights.append("")
            if reasons_customer:
                insights.append(f"**2. 客数{'増加' if customer_contrib > 0 else '減少'}の背景（¥{customer_contrib:,.0f}寄与）**")
                insights.append("")
                for reason in reasons_customer:
                    insights.append(f"- {reason}")
                insights.append("")

        # ==== 3. パーティサイズ別分析 ====
        insights.append("#### パーティサイズ別の変化")
        insights.append("")

        target_party = analyze_party_size(target_df, weekday)
        past_party = analyze_party_size(past_df, weekday)

        if not target_party.empty and not past_party.empty:
            # 過去4週の日数で割って平均を計算
            past_days = past_weekday_df['営業日'].nunique()
            if past_days > 0:
                for col in ['組数', '客数', '売上']:
                    past_party[col] = past_party[col] / past_days

            insights.append("| パーティサイズ | 対象週 | 過去4週平均 | 組あたり売上変化 |")
            insights.append("|----------------|--------|-------------|------------------|")

            all_sizes = set(target_party.index) | set(past_party.index)
            for size in ['1名', '2名', '3-4名', '5名以上']:
                if size not in all_sizes:
                    continue

                if size in target_party.index:
                    t_groups = target_party.loc[size, '組数']
                    t_customers = target_party.loc[size, '客数']
                    t_sales = target_party.loc[size, '売上']
                    t_per_group = target_party.loc[size, '組あたり売上']
                else:
                    t_groups = t_customers = t_sales = t_per_group = 0

                if size in past_party.index:
                    p_groups = past_party.loc[size, '組数']
                    p_customers = past_party.loc[size, '客数']
                    p_sales = past_party.loc[size, '売上']
                    p_per_group = past_party.loc[size, '組あたり売上']
                else:
                    p_groups = p_customers = p_sales = p_per_group = 0

                if t_groups > 0 or p_groups > 0:
                    change_per_group = t_per_group - p_per_group if p_per_group > 0 else 0
                    change_pct = (change_per_group / p_per_group * 100) if p_per_group > 0 else 0

                    target_str = f"{t_groups:.0f}組({t_customers:.0f}人) ¥{t_sales:,.0f}" if t_groups > 0 else "なし"
                    past_str = f"{p_groups:.1f}組({p_customers:.1f}人) ¥{p_sales:,.0f}" if p_groups > 0 else "なし"

                    if p_per_group > 0 and t_per_group > 0:
                        change_str = f"¥{p_per_group:,.0f}→¥{t_per_group:,.0f} ({change_pct:+.0f}%)"
                    elif t_per_group > 0:
                        change_str = f"新規出現 (¥{t_per_group:,.0f})"
                    elif p_per_group > 0:
                        change_str = "**消失**"
                    else:
                        change_str = "-"

                    insights.append(f"| {size} | {target_str} | {past_str} | {change_str} |")

            insights.append("")

            # パーティサイズの考察を追加
            party_insights = []
            for size in ['1名', '2名', '3-4名', '5名以上']:
                if size in target_party.index and size in past_party.index:
                    t_groups = target_party.loc[size, '組数']
                    p_groups = past_party.loc[size, '組数']
                    t_per_group = target_party.loc[size, '組あたり売上']
                    p_per_group = past_party.loc[size, '組あたり売上']

                    group_change = t_groups - p_groups
                    per_group_change_pct = ((t_per_group - p_per_group) / p_per_group * 100) if p_per_group > 0 else 0

                    if abs(group_change) > 2:  # 組数変化が大きい
                        if group_change > 0:
                            party_insights.append(f"{size}グループが+{group_change:.0f}組増加")
                        else:
                            party_insights.append(f"{size}グループが{group_change:.0f}組減少")
                    if abs(per_group_change_pct) > 20:  # 組あたり売上の変化が大きい
                        if per_group_change_pct > 0:
                            party_insights.append(f"{size}の組あたり売上が+{per_group_change_pct:.0f}%上昇")
                        else:
                            party_insights.append(f"{size}の組あたり売上が{per_group_change_pct:.0f}%下落")
                elif size in target_party.index and size not in past_party.index:
                    party_insights.append(f"{size}グループが新規出現")
                elif size not in target_party.index and size in past_party.index:
                    party_insights.append(f"{size}グループが消失")

            if party_insights:
                insights.append(f"💡 **ポイント**: {'; '.join(party_insights[:3])}。")
                insights.append("")

        # ==== 4. 時間帯別分析 ====
        insights.append("#### 時間帯別の変化")
        insights.append("")

        target_time = analyze_time_slots(target_df, weekday)
        past_time = analyze_time_slots(past_df, weekday)

        if not target_time.empty and not past_time.empty:
            # 過去4週の日数で割って平均を計算
            for col in ['組数', '客数', '売上']:
                past_time[col] = past_time[col] / past_days

            insights.append("| 時間帯 | 対象週 | 過去4週平均 | 差異 |")
            insights.append("|--------|--------|-------------|------|")

            all_times = set(target_time.index) | set(past_time.index)
            for time_slot in ['18-20時', '20-22時', '22-24時', '24-2時']:
                if time_slot not in all_times:
                    continue

                if time_slot in target_time.index:
                    t_groups = target_time.loc[time_slot, '組数']
                    t_customers = target_time.loc[time_slot, '客数']
                    t_sales = target_time.loc[time_slot, '売上']
                else:
                    t_groups = t_customers = t_sales = 0

                if time_slot in past_time.index:
                    p_groups = past_time.loc[time_slot, '組数']
                    p_customers = past_time.loc[time_slot, '客数']
                    p_sales = past_time.loc[time_slot, '売上']
                else:
                    p_groups = p_customers = p_sales = 0

                sales_diff = t_sales - p_sales

                target_str = f"{t_groups:.0f}組({t_customers:.0f}人) ¥{t_sales:,.0f}" if t_groups > 0 else "なし"
                past_str = f"{p_groups:.1f}組({p_customers:.1f}人) ¥{p_sales:,.0f}" if p_groups > 0 else "なし"
                diff_str = f"{sales_diff:+,.0f}" if (t_groups > 0 or p_groups > 0) else "-"

                # 大幅な変化がある場合は強調
                if abs(sales_diff) > 20000:
                    diff_str = f"**{diff_str}**"

                insights.append(f"| {time_slot} | {target_str} | {past_str} | {diff_str} |")

            insights.append("")

            # 時間帯別の考察を追加
            time_insights = []
            max_sales_diff = 0
            max_time_slot = None
            for time_slot in ['18-20時', '20-22時', '22-24時', '24-2時']:
                if time_slot in target_time.index and time_slot in past_time.index:
                    t_sales = target_time.loc[time_slot, '売上']
                    p_sales = past_time.loc[time_slot, '売上']
                    sales_diff = t_sales - p_sales

                    if abs(sales_diff) > abs(max_sales_diff):
                        max_sales_diff = sales_diff
                        max_time_slot = time_slot

            if max_time_slot and abs(max_sales_diff) > 10000:
                if max_sales_diff > 0:
                    time_insights.append(f"{max_time_slot}の売上が+¥{max_sales_diff:,.0f}と大幅増加")
                else:
                    time_insights.append(f"{max_time_slot}の売上が¥{max_sales_diff:,.0f}と大幅減少")

                # ピーク時間帯かどうかを判定
                if max_time_slot in ['20-22時', '22-24時']:
                    if max_sales_diff < 0:
                        time_insights.append("ピーク時間帯での集客低下が売上減に直結")
                    else:
                        time_insights.append("ピーク時間帯での集客増が売上増に貢献")

            if time_insights:
                insights.append(f"💡 **ポイント**: {'; '.join(time_insights)}。")
                insights.append("")

        # ==== 5. 商品ミックスの変化 ====
        insights.append("#### 商品ミックスの変化")
        insights.append("")

        target_cat = analyze_category_mix(target_df, weekday)
        past_cat = analyze_category_mix(past_df, weekday)

        if not target_cat.empty and not past_cat.empty:
            insights.append("| カテゴリ | 対象週 | 過去4週平均 | 変化 |")
            insights.append("|----------|--------|-------------|------|")

            # TOP5のカテゴリのみ表示
            for i, (cat_name, row_data) in enumerate(target_cat.head(5).iterrows()):
                t_sales = row_data['売上']
                t_ratio = row_data['構成比']

                if cat_name in past_cat.index:
                    # 過去4週の日数で割って平均を計算
                    p_sales = past_cat.loc[cat_name, '売上'] / past_days
                    p_total = past_cat['売上'].sum() / past_days
                    p_ratio = (p_sales / p_total * 100) if p_total > 0 else 0
                    change_pct = ((t_sales - p_sales) / p_sales * 100) if p_sales > 0 else 100
                    change_str = f"{change_pct:+.0f}%"
                else:
                    p_ratio = 0
                    change_str = "新規"

                insights.append(f"| {cat_name} | ¥{t_sales:,.0f} ({t_ratio:.1f}%) | ({p_ratio:.1f}%) | {change_str} |")

            insights.append("")

            # 商品ミックスの考察を追加
            category_insights = []
            for i, (cat_name, row_data) in enumerate(target_cat.head(5).iterrows()):
                t_sales = row_data['売上']
                t_ratio = row_data['構成比']

                if cat_name in past_cat.index:
                    p_sales = past_cat.loc[cat_name, '売上'] / past_days
                    change_pct = ((t_sales - p_sales) / p_sales * 100) if p_sales > 0 else 100

                    if abs(change_pct) > 50 and t_ratio > 5:  # 大幅な変化かつ一定の構成比
                        if change_pct > 0:
                            category_insights.append(f"{cat_name}が+{change_pct:.0f}%増加（構成比{t_ratio:.1f}%）")
                        else:
                            category_insights.append(f"{cat_name}が{change_pct:.0f}%減少（構成比{t_ratio:.1f}%）")
                elif t_ratio > 5:  # 新規カテゴリで一定の構成比
                    category_insights.append(f"{cat_name}が新規出現（構成比{t_ratio:.1f}%）")

            if category_insights:
                insights.append(f"💡 **ポイント**: {'; '.join(category_insights[:2])}。")
                insights.append("")

        # ==== 6. 客単価の分布 ====
        insights.append("#### 客単価の分布")
        insights.append("")

        unit_price_dist = analyze_unit_price_distribution(target_df, weekday)

        if unit_price_dist:
            insights.append("| 指標 | 対象週 |")
            insights.append("|------|--------|")
            insights.append(f"| 最小 | ¥{unit_price_dist['最小']:,.0f} |")
            insights.append(f"| P10 | ¥{unit_price_dist['P10']:,.0f} |")
            insights.append(f"| **中央値** | **¥{unit_price_dist['中央値']:,.0f}** |")
            insights.append(f"| P90 | ¥{unit_price_dist['P90']:,.0f} |")
            insights.append(f"| 最大 | ¥{unit_price_dist['最大']:,.0f} |")
            insights.append("")

            # 客単価分布の考察
            median = unit_price_dist['中央値']
            p90 = unit_price_dist['P90']
            p10 = unit_price_dist['P10']
            spread = p90 - p10

            distribution_insights = []
            if median > 6000:
                distribution_insights.append(f"中央値¥{median:,.0f}と高水準")
            elif median < 4000:
                distribution_insights.append(f"中央値¥{median:,.0f}と低水準")

            if spread < 3000:
                distribution_insights.append("客単価のバラつきが小さく安定")
            elif spread > 6000:
                distribution_insights.append("客単価のバラつきが大きく多様な顧客層")

            if distribution_insights:
                insights.append(f"💡 **ポイント**: {'; '.join(distribution_insights)}。")
                insights.append("")

        insights.append("---")
        insights.append("")

    return "\n".join(insights)


def main():
    """
    メイン処理
    """
    print("=" * 60)
    print("曜日別深堀分析開始")
    print("=" * 60)

    # データ読み込み
    df = load_and_prep_data(INPUT_CSV)

    # 対象週と過去4週間のデータ取得
    target_df, past_df = get_target_and_past_weeks(df, target_year=2025, target_week=52)

    # 曜日別サマリー
    print("\n対象週の曜日別サマリー計算中...")
    target_summary = weekday_summary(target_df)

    print("過去4週間の曜日別サマリー計算中...")
    past_summary = weekday_summary(past_df)

    # 要因分解
    print("要因分解計算中...")
    decomp_df = weekday_factor_decomposition(target_summary, past_summary)

    # 時刻別分析
    print("時刻別分析中...")
    target_hourly = hourly_analysis_by_weekday(target_df)

    # 洞察生成
    print("洞察生成中...")
    insights_text = generate_insights(decomp_df, target_summary, past_df, target_df)

    # マークダウン出力生成
    output_lines = []
    output_lines.append("# 曜日別深堀分析結果 (2025-W52)")
    output_lines.append("")
    output_lines.append("**分析日**: " + datetime.now().strftime("%Y-%m-%d"))
    output_lines.append("**対象週**: 2025年12月22日～28日 (2025-W52)")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")

    # 1. 曜日別サマリー
    output_lines.append("## 1. 曜日別サマリー（対象週）")
    output_lines.append("")
    output_lines.append("| 曜日 | 売上 | 客数 | 客単価 |")
    output_lines.append("|------|------|------|--------|")
    for weekday, row in target_summary.iterrows():
        output_lines.append(f"| {weekday} | ¥{row['売上']:,.0f} | {row['客数']:.0f}人 | ¥{row['客単価']:,.0f} |")
    output_lines.append("")

    # 2. 要因分解
    output_lines.append("## 2. 曜日別要因分解（対象週 vs 過去4週間平均）")
    output_lines.append("")
    output_lines.append("| 曜日 | 売上差 | 客数要因寄与 | 客単価要因寄与 | 客数差 | 客単価差 |")
    output_lines.append("|------|--------|-------------|---------------|--------|---------|")
    for _, row in decomp_df.iterrows():
        output_lines.append(
            f"| {row['曜日']} | ¥{row['売上差']:,.0f} | "
            f"¥{row['客数要因寄与']:,.0f} | ¥{row['客単価要因寄与']:,.0f} | "
            f"{row['客数差']:.1f}人 | ¥{row['客単価差']:.0f} |"
        )
    output_lines.append("")

    # 3. 深堀対象曜日の詳細分析
    output_lines.append("## 3. 深堀対象曜日の詳細分析")
    output_lines.append("")
    output_lines.append(insights_text)
    output_lines.append("")

    # ファイル出力
    output_text = "\n".join(output_lines)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f"\n分析結果を出力しました: {OUTPUT_MD}")
    print("=" * 60)
    print("分析完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
