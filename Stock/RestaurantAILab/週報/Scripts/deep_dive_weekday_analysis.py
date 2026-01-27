# -*- coding: utf-8 -*-
"""
曜日深掘り分析スクリプト

週報作成後、最も好調だった日と最も不調だった日を深掘り分析するスクリプト。
5つの観点（パーティサイズ、時間帯、会計レベル、商品ミックス、例外データ）で比較分析を行う。

Usage:
    python deep_dive_weekday_analysis.py -w 2026-W01 -e 2026-01-03 --best-date 2025-12-31 --worst-date 2026-01-02

    または weekday_decomposition.csv から自動判定:
    python deep_dive_weekday_analysis.py -w 2026-W01 -e 2026-01-03 --auto
"""

import pandas as pd
import numpy as np
import sys
import argparse
from datetime import datetime
from pathlib import Path

# UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description='曜日深掘り分析スクリプト')
    parser.add_argument('-w', '--week', required=True, help='対象週（例: 2026-W01）')
    parser.add_argument('-e', '--end-date', required=True, help='対象週の終了日（例: 2026-01-03）')
    parser.add_argument('--best-date', help='好調日の日付（例: 2025-12-31）')
    parser.add_argument('--worst-date', help='不調日の日付（例: 2026-01-02）')
    parser.add_argument('--auto', action='store_true', help='weekday_decomposition.csvから自動判定')
    parser.add_argument('--input-dir', default='Stock/RestaurantAILab/週報/1_input',
                        help='入力ディレクトリ（rawdata.csvの場所）')
    parser.add_argument('--output-dir', help='出力ディレクトリ（指定しない場合は2_output_{week}）')
    parser.add_argument('--export-slide-data', action='store_true',
                        help='スライド用データをテキストファイルに出力')
    return parser.parse_args()


def load_rawdata(input_dir):
    """rawdata.csvを読み込み、営業日基準で変換"""
    df = pd.read_csv(f'{input_dir}/rawdata.csv')
    df['entry_at'] = pd.to_datetime(df['entry_at'], utc=True)
    df['entry_at_jst'] = df['entry_at'].dt.tz_convert('Asia/Tokyo')
    df['business_date'] = df['entry_at_jst'].apply(
        lambda dt: (dt - pd.Timedelta(days=1)).date() if 0 <= dt.hour < 6 else dt.date()
    )
    df['hour'] = df['entry_at_jst'].dt.hour
    return df


def find_best_worst_dates(output_dir, week):
    """weekday_decomposition.csvから最も好調な日と不調な日を自動判定"""
    weekday_file = Path(output_dir) / 'weekday_decomposition.csv'
    if not weekday_file.exists():
        raise FileNotFoundError(f'{weekday_file} が見つかりません。先にanalysis_script.pyを実行してください。')

    weekday_df = pd.read_csv(weekday_file)

    # 売上差が最大の曜日と最小の曜日を特定
    best_weekday = weekday_df.loc[weekday_df['売上差'].idxmax()]
    worst_weekday = weekday_df.loc[weekday_df['売上差'].idxmin()]

    print(f'自動判定結果:')
    print(f'  最も好調: {best_weekday["曜日"]} (売上差: ¥{best_weekday["売上差"]:,.0f})')
    print(f'  最も不調: {worst_weekday["曜日"]} (売上差: ¥{worst_weekday["売上差"]:,.0f})')

    # 曜日から具体的な日付を逆算（これは手動で指定する必要がある）
    print('\n⚠️ 注意: 具体的な日付は手動で指定してください。')
    print('例: --best-date 2025-12-31 --worst-date 2026-01-02')
    sys.exit(1)


def analyze_day(df, target_date, day_label):
    """特定の日の深掘り分析を実行"""
    # データフィルタ
    day_data = df[df['business_date'] == pd.Timestamp(target_date).date()].copy()

    if len(day_data) == 0:
        print(f'⚠️ {day_label} ({target_date}) のデータが見つかりません。')
        return None

    # 会計単位に集約
    accounts = day_data.groupby('account_id').first().reset_index()
    total_sales = accounts['account_total'].sum()
    total_customers = accounts['customer_count'].sum()

    print('='*60)
    print(f'{day_label} {target_date} - 詳細分析')
    print('='*60)
    print()

    # 基本情報
    print('【基本情報】')
    print(f'  総売上: ¥{total_sales:,.0f}')
    print(f'  総客数: {total_customers}人')
    print(f'  会計数: {len(accounts)}件')
    print(f'  平均客単価: ¥{total_sales / total_customers:,.0f}')
    print()

    # 1. パーティサイズ分析
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

    # 2. 時間帯バケット分析
    print('【2. 時間帯バケット分析】')
    accounts_time = day_data.groupby('account_id').agg({
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

    # 3. 会計レベル分析
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

    # 4. 商品ミックス分析
    print('【4. 商品ミックス分析】')
    print('  カテゴリ別売上構成:')
    category_sales = day_data.groupby('category1').agg({
        'price': 'sum',
        'menu_name': 'count'
    }).reset_index()
    category_sales.columns = ['カテゴリ', '売上', '販売数']
    category_sales['構成比%'] = (category_sales['売上'] / category_sales['売上'].sum() * 100).round(1)
    category_sales = category_sales.sort_values('売上', ascending=False)
    print(category_sales.to_string(index=False))
    print()

    print('  高単価商品 (¥1,500以上):')
    high_price = day_data[day_data['price'] >= 1500].copy()
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

    # 5. 例外データ確認
    print('【5. 例外データ確認】')
    print('  営業時間外会計 (6時前の入力):')
    early_morning = day_data[day_data['hour'] < 6]
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
    print()

    return {
        'date': target_date,
        'label': day_label,
        'sales': total_sales,
        'customers': total_customers,
        'accounts': len(accounts),
        'avg_per_customer': total_sales / total_customers,
        'party_analysis': party_analysis,
        'time_analysis': time_analysis,
        'account_stats': {
            'max': account_totals.max(),
            'min': account_totals.min(),
            'median': np.median(account_totals),
            'p10': np.percentile(account_totals, 10),
            'p90': np.percentile(account_totals, 90),
            'mean': account_totals.mean()
        },
        'price_dist': price_dist,
        'category_sales': category_sales
    }


def main():
    """メイン処理"""
    args = parse_args()

    # 出力ディレクトリの決定
    if args.output_dir:
        output_dir = args.output_dir
    else:
        week_str = args.week.lower().replace('-', '')
        output_dir = f'Stock/RestaurantAILab/週報/2_output_{week_str}'

    print('='*60)
    print('曜日深掘り分析スクリプト')
    print('='*60)
    print(f'対象週: {args.week}')
    print(f'終了日: {args.end_date}')
    print(f'出力先: {output_dir}')
    print()

    # 自動判定モード
    if args.auto:
        find_best_worst_dates(output_dir, args.week)
        return

    # 手動指定モード
    if not args.best_date or not args.worst_date:
        print('エラー: --best-date と --worst-date を指定するか、--auto を使用してください。')
        sys.exit(1)

    # データ読み込み
    print('データを読み込んでいます...')
    df = load_rawdata(args.input_dir)
    print(f'総レコード数: {len(df):,}')
    print()

    # 好調日の分析
    best_result = analyze_day(df, args.best_date, '最も好調な日')

    # 不調日の分析
    worst_result = analyze_day(df, args.worst_date, '最も不調な日')

    # 比較サマリー
    if best_result and worst_result:
        print('='*60)
        print('比較サマリー')
        print('='*60)
        print(f'売上差: ¥{best_result["sales"] - worst_result["sales"]:,.0f} '
              f'({(best_result["sales"] - worst_result["sales"]) / worst_result["sales"] * 100:+.1f}%)')
        print(f'客数差: {best_result["customers"] - worst_result["customers"]}人 '
              f'({(best_result["customers"] - worst_result["customers"]) / worst_result["customers"] * 100:+.1f}%)')
        print(f'会計数差: {best_result["accounts"] - worst_result["accounts"]}件 '
              f'({(best_result["accounts"] - worst_result["accounts"]) / worst_result["accounts"] * 100:+.1f}%)')
        print()

    print('='*60)
    print('分析完了')
    print('='*60)


if __name__ == '__main__':
    main()
