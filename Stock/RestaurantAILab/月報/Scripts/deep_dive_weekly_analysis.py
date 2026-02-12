# -*- coding: utf-8 -*-
"""
月報用 — 週別深掘り分析スクリプト

月内の好調週と不調週を5つの観点で比較分析する。
週報の deep_dive_weekday_analysis.py（曜日深掘り）を月報版（週別深掘り）に変換。

Usage:
    # 自動判定モード（analysis_results.json の best_week/worst_week を使用）
    python deep_dive_weekly_analysis.py -m 2026-01 --auto \
        --sales-data ./1_input/BFA/rawdata.csv \
        -o ./2_output/BFA/2_output_202601

    # 手動指定モード
    python deep_dive_weekly_analysis.py -m 2026-01 \
        --best-week 2026-W02 --worst-week 2026-W04 \
        --sales-data ./1_input/BFA/rawdata.csv \
        -o ./2_output/BFA/2_output_202601
"""

import pandas as pd
import numpy as np
import sys
import argparse
import json
import calendar
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(description='月報用 週別深掘り分析スクリプト')
    parser.add_argument('-m', '--month', required=True, help='対象月（例: 2026-01）')
    parser.add_argument('--best-week', help='好調週（例: 2026-W02）')
    parser.add_argument('--worst-week', help='不調週（例: 2026-W04）')
    parser.add_argument('--auto', action='store_true',
                        help='analysis_results.json から好調/不調週を自動判定')
    parser.add_argument('--sales-data', required=True, help='rawdata.csv のパス')
    parser.add_argument('-o', '--output-dir', required=True, help='出力ディレクトリ')
    parser.add_argument('--export-slide-data', action='store_true',
                        help='スライド用データをテキストファイルに出力')
    return parser.parse_args()


def load_rawdata(sales_path):
    """rawdata.csv を読み込み、営業日基準で変換"""
    df = pd.read_csv(sales_path)
    df['entry_at'] = pd.to_datetime(df['entry_at'], utc=True)
    df['entry_at_jst'] = df['entry_at'].dt.tz_convert('Asia/Tokyo')
    df['business_date'] = df['entry_at_jst'].apply(
        lambda dt: (dt - pd.Timedelta(days=1)).date() if 0 <= dt.hour < 6 else dt.date()
    )
    df['business_date_dt'] = pd.to_datetime(df['business_date'])
    df['year_week'] = df['business_date_dt'].dt.strftime('%G-W%V')
    df['year_month'] = df['business_date_dt'].dt.strftime('%Y-%m')

    # 営業時間（business_hour）
    df['business_hour'] = df['entry_at_jst'].apply(
        lambda dt: dt.hour + 24 if 0 <= dt.hour < 6 else dt.hour
    )

    weekday_map = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
    df['weekday'] = df['business_date_dt'].dt.dayofweek.map(weekday_map)

    return df


def find_best_worst_weeks(output_dir):
    """analysis_results.json から好調/不調週を取得"""
    json_path = Path(output_dir) / 'analysis_results.json'
    if not json_path.exists():
        raise FileNotFoundError(
            f'{json_path} が見つかりません。先に monthly_analysis_script.py を実行してください。'
        )

    with open(json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)

    best_week = results.get('best_week')
    worst_week = results.get('worst_week')

    if not best_week or not worst_week:
        raise ValueError('analysis_results.json に best_week / worst_week が含まれていません。')

    print(f'自動判定結果:')
    print(f'  好調週: {best_week}')
    print(f'  不調週: {worst_week}')
    return best_week, worst_week


def analyze_week(df, target_week, week_label, target_month):
    """特定の週の深掘り分析を実行"""
    # 対象月に含まれる営業日のみフィルタ（ISO週が月またぎの場合）
    week_data = df[(df['year_week'] == target_week) & (df['year_month'] == target_month)].copy()

    if len(week_data) == 0:
        # 月フィルタなしで再試行（月境界の週の場合）
        week_data = df[df['year_week'] == target_week].copy()
        if len(week_data) == 0:
            print(f'⚠️ {week_label} ({target_week}) のデータが見つかりません。')
            return None

    # 会計単位に集約
    accounts = week_data.groupby('account_id').agg({
        'account_total': 'first',
        'customer_count': 'first',
        'business_date': 'first',
        'business_hour': 'first',
        'weekday': 'first'
    }).reset_index()

    total_sales = accounts['account_total'].sum()
    total_customers = accounts['customer_count'].sum()
    biz_days = week_data['business_date'].nunique()
    daily_avg_sales = total_sales / biz_days if biz_days > 0 else 0

    print()
    print('=' * 60)
    print(f'{week_label}: {target_week}')
    print('=' * 60)

    # === 基本情報 ===
    print()
    print('【基本情報】')
    print(f'  売上: ¥{total_sales:,.0f}')
    print(f'  客数: {total_customers}人')
    print(f'  会計数: {len(accounts)}件')
    print(f'  客単価: ¥{total_sales / total_customers:,.0f}' if total_customers > 0 else '  客単価: N/A')
    print(f'  営業日数: {biz_days}日')
    print(f'  日平均売上: ¥{daily_avg_sales:,.0f}')

    # === 1. 曜日別構成 ===
    print()
    print('【1. 曜日別構成】')
    weekday_order = ['月', '火', '水', '木', '金', '土', '日']
    weekday_analysis = accounts.groupby('weekday').agg({
        'account_total': 'sum',
        'customer_count': 'sum',
        'account_id': 'count'
    }).rename(columns={'account_total': '売上', 'customer_count': '客数', 'account_id': '会計数'})
    weekday_analysis['客単価'] = (weekday_analysis['売上'] / weekday_analysis['客数']).round(0)
    weekday_analysis = weekday_analysis.reindex([w for w in weekday_order if w in weekday_analysis.index])
    print(weekday_analysis.to_string())

    # === 2. 時間帯バケット分析 ===
    print()
    print('【2. 時間帯バケット分析】')

    def time_bucket(hour):
        if 18 <= hour < 20: return '18-20時'
        elif 20 <= hour < 22: return '20-22時'
        elif 22 <= hour < 24: return '22-24時'
        elif 24 <= hour < 27: return '24-26時'
        else: return 'その他'

    accounts['time_bucket'] = accounts['business_hour'].apply(time_bucket)
    bucket_order = ['18-20時', '20-22時', '22-24時', '24-26時', 'その他']
    time_analysis = accounts.groupby('time_bucket').agg({
        'account_id': 'count',
        'customer_count': 'sum',
        'account_total': 'sum'
    }).rename(columns={'account_id': '会計数', 'customer_count': '客数', 'account_total': '売上'})
    time_analysis['売上構成比%'] = (time_analysis['売上'] / time_analysis['売上'].sum() * 100).round(1)
    time_analysis = time_analysis.reindex([b for b in bucket_order if b in time_analysis.index])
    print(time_analysis.to_string())

    # === 3. 会計レベル分析 ===
    print()
    print('【3. 会計レベル分析】')
    account_totals = accounts['account_total'].values
    print(f'  最大会計: ¥{account_totals.max():,.0f}')
    print(f'  最小会計: ¥{account_totals.min():,.0f}')
    print(f'  中央値: ¥{np.median(account_totals):,.0f}')
    print(f'  P10: ¥{np.percentile(account_totals, 10):,.0f}')
    print(f'  P90: ¥{np.percentile(account_totals, 90):,.0f}')
    print(f'  平均: ¥{account_totals.mean():,.0f}')
    print()
    print('  会計金額分布:')
    bins = [0, 5000, 10000, 15000, 20000, 100000]
    labels_price = ['~5千円', '5千~1万', '1万~1.5万', '1.5万~2万', '2万円以上']
    accounts['price_range'] = pd.cut(accounts['account_total'], bins=bins, labels=labels_price, right=False)
    price_dist = accounts.groupby('price_range', observed=False).size().reset_index(name='会計数')
    price_dist['構成比%'] = (price_dist['会計数'] / price_dist['会計数'].sum() * 100).round(1)
    print(price_dist.to_string(index=False))

    # === 4. 商品ミックス分析 ===
    print()
    print('【4. 商品ミックス分析】')
    print('  カテゴリ別売上構成 TOP5:')
    if 'category1' in week_data.columns:
        category_sales = week_data.groupby('category1').agg({
            'subtotal': 'sum',
            'quantity': 'sum'
        }).reset_index()
        category_sales.columns = ['カテゴリ', '売上', '販売数']
        category_sales['構成比%'] = (category_sales['売上'] / category_sales['売上'].sum() * 100).round(1)
        category_sales = category_sales.sort_values('売上', ascending=False)
        print(category_sales.head(5).to_string(index=False))
    else:
        print('  （category1 列なし）')

    print()
    print('  高単価商品 (¥1,500以上) TOP10:')
    if 'price' in week_data.columns:
        high_price = week_data[week_data['price'] >= 1500].copy()
        if len(high_price) > 0:
            hp_summary = high_price.groupby('menu_name').agg({
                'price': ['mean', 'count', 'sum']
            }).reset_index()
            hp_summary.columns = ['商品名', '平均単価', '販売数', '売上合計']
            hp_summary = hp_summary.sort_values('売上合計', ascending=False).head(10)
            print(hp_summary.to_string(index=False))
        else:
            print('    なし')
    else:
        print('  （price 列なし）')

    # === 5. 例外データ確認 ===
    print()
    print('【5. 例外データ確認】')
    print(f'  1名あたり売上 > ¥10,000 の会計: '
          f'{len(accounts[accounts["account_total"] / accounts["customer_count"].clip(lower=1) > 10000])}件')
    print(f'  10名以上のパーティ: {len(accounts[accounts["customer_count"] >= 10])}件')

    return {
        'week': target_week,
        'label': week_label,
        'sales': total_sales,
        'customers': int(total_customers),
        'accounts': len(accounts),
        'avg_per_customer': total_sales / total_customers if total_customers > 0 else 0,
        'biz_days': biz_days,
        'daily_avg_sales': daily_avg_sales,
        'weekday_analysis': weekday_analysis.reset_index().to_dict('records'),
        'time_analysis': time_analysis.reset_index().to_dict('records'),
        'account_stats': {
            'max': float(account_totals.max()),
            'min': float(account_totals.min()),
            'median': float(np.median(account_totals)),
            'p10': float(np.percentile(account_totals, 10)),
            'p90': float(np.percentile(account_totals, 90)),
            'mean': float(account_totals.mean())
        },
        'price_dist': price_dist.to_dict('records'),
        'category_sales': category_sales.head(5).to_dict('records') if 'category1' in week_data.columns else []
    }


def export_slide_data(best_result, worst_result, output_dir):
    """スライド用深掘りデータをテキストファイルに出力"""
    lines = []
    lines.append('=' * 60)
    lines.append('【スライド第2部用・追加】週別深掘り分析データ')
    lines.append('=' * 60)
    lines.append('')

    # サマリー比較表
    lines.append('## 好調週 vs 不調週 — サマリー比較')
    lines.append('')
    lines.append(f'| 指標 | 不調週 ({worst_result["week"]}) | 好調週 ({best_result["week"]}) | 差 |')
    lines.append('|---|---|---|---|')

    diff_sales = best_result['sales'] - worst_result['sales']
    diff_cust = best_result['customers'] - worst_result['customers']
    diff_davg = best_result['daily_avg_sales'] - worst_result['daily_avg_sales']

    lines.append(f'| 売上 | ¥{worst_result["sales"]:,.0f} | ¥{best_result["sales"]:,.0f} | ¥{diff_sales:+,.0f} |')
    lines.append(f'| 客数 | {worst_result["customers"]}人 | {best_result["customers"]}人 | {diff_cust:+d}人 |')
    lines.append(f'| 客単価 | ¥{worst_result["avg_per_customer"]:,.0f} | ¥{best_result["avg_per_customer"]:,.0f} | ¥{best_result["avg_per_customer"] - worst_result["avg_per_customer"]:+,.0f} |')
    lines.append(f'| 営業日数 | {worst_result["biz_days"]}日 | {best_result["biz_days"]}日 | {best_result["biz_days"] - worst_result["biz_days"]:+d}日 |')
    lines.append(f'| 日平均売上 | ¥{worst_result["daily_avg_sales"]:,.0f} | ¥{best_result["daily_avg_sales"]:,.0f} | ¥{diff_davg:+,.0f} |')
    lines.append('')

    # 曜日別比較
    lines.append('## 曜日別売上比較（好調週 vs 不調週）')
    lines.append('')
    lines.append('| 曜日 | 不調週売上 | 好調週売上 | 差額 |')
    lines.append('|---|---|---|---|')
    best_wd = {r['weekday']: r for r in best_result['weekday_analysis']}
    worst_wd = {r['weekday']: r for r in worst_result['weekday_analysis']}
    for day in ['月', '火', '水', '木', '金', '土', '日']:
        b_sales = best_wd.get(day, {}).get('売上', 0)
        w_sales = worst_wd.get(day, {}).get('売上', 0)
        diff = b_sales - w_sales
        lines.append(f'| {day} | ¥{w_sales:,.0f} | ¥{b_sales:,.0f} | ¥{diff:+,.0f} |')
    lines.append('')

    # 時間帯別比較
    lines.append('## 時間帯別売上比較（好調週 vs 不調週）')
    lines.append('')
    lines.append('| 時間帯 | 不調週売上 | 好調週売上 | 差額 |')
    lines.append('|---|---|---|---|')
    best_tb = {r['time_bucket']: r for r in best_result['time_analysis']}
    worst_tb = {r['time_bucket']: r for r in worst_result['time_analysis']}
    for bucket in ['18-20時', '20-22時', '22-24時', '24-26時']:
        b_sales = best_tb.get(bucket, {}).get('売上', 0)
        w_sales = worst_tb.get(bucket, {}).get('売上', 0)
        diff = b_sales - w_sales
        lines.append(f'| {bucket} | ¥{w_sales:,.0f} | ¥{b_sales:,.0f} | ¥{diff:+,.0f} |')
    lines.append('')

    # 会計レベル比較
    lines.append('## 会計レベル比較（好調週 vs 不調週）')
    lines.append('')
    lines.append('| 指標 | 不調週 | 好調週 |')
    lines.append('|---|---|---|')
    for key, label in [('max', '最大会計'), ('min', '最小会計'), ('median', '中央値'),
                        ('p10', 'P10'), ('p90', 'P90'), ('mean', '平均')]:
        lines.append(f'| {label} | ¥{worst_result["account_stats"][key]:,.0f} | ¥{best_result["account_stats"][key]:,.0f} |')
    lines.append('')

    # カテゴリ比較
    lines.append('## カテゴリ別売上 TOP5（好調週 vs 不調週）')
    lines.append('')
    lines.append('| カテゴリ | 不調週売上 | 好調週売上 | 差額 |')
    lines.append('|---|---|---|---|')
    best_cats = {r['カテゴリ']: r['売上'] for r in best_result['category_sales']}
    worst_cats = {r['カテゴリ']: r['売上'] for r in worst_result['category_sales']}
    all_cats = set(list(best_cats.keys())[:5] + list(worst_cats.keys())[:5])
    for cat in sorted(all_cats, key=lambda c: best_cats.get(c, 0), reverse=True):
        b_s = best_cats.get(cat, 0)
        w_s = worst_cats.get(cat, 0)
        lines.append(f'| {cat} | ¥{w_s:,.0f} | ¥{b_s:,.0f} | ¥{b_s - w_s:+,.0f} |')
    lines.append('')

    output_path = Path(output_dir) / 'slide_data_deep_dive.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n[出力] {output_path}')


def main():
    args = parse_args()

    target_month = args.month
    output_dir = args.output_dir

    print('=' * 60)
    print('月報用 週別深掘り分析スクリプト')
    print('=' * 60)
    print(f'対象月: {target_month}')
    print(f'出力先: {output_dir}')
    print()

    # 好調/不調週の決定
    if args.auto:
        best_week, worst_week = find_best_worst_weeks(output_dir)
    elif args.best_week and args.worst_week:
        best_week = args.best_week
        worst_week = args.worst_week
    else:
        print('エラー: --best-week と --worst-week を指定するか、--auto を使用してください。')
        sys.exit(1)

    print(f'好調週: {best_week}')
    print(f'不調週: {worst_week}')
    print()

    # データ読み込み
    print('データを読み込んでいます...')
    df = load_rawdata(args.sales_data)
    print(f'総レコード数: {len(df):,}')

    # 分析実行
    best_result = analyze_week(df, best_week, '好調週', target_month)
    worst_result = analyze_week(df, worst_week, '不調週', target_month)

    # 比較サマリー
    if best_result and worst_result:
        print()
        print('=' * 60)
        print('比較サマリー')
        print('=' * 60)
        diff_sales = best_result['sales'] - worst_result['sales']
        diff_cust = best_result['customers'] - worst_result['customers']
        diff_davg = best_result['daily_avg_sales'] - worst_result['daily_avg_sales']

        print(f'  売上差: ¥{diff_sales:+,.0f}')
        print(f'  客数差: {diff_cust:+d}人')
        print(f'  日平均売上差: ¥{diff_davg:+,.0f}')
        print()

        # JSON出力
        deep_dive_results = {
            'best_week': best_result,
            'worst_week': worst_result,
            'comparison': {
                'sales_diff': diff_sales,
                'customer_diff': diff_cust,
                'daily_avg_diff': diff_davg
            }
        }
        json_path = Path(output_dir) / 'deep_dive_results.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(deep_dive_results, f, ensure_ascii=False, indent=2, default=str)
        print(f'[出力] {json_path}')

        # スライド用データ出力（常に出力）
        export_slide_data(best_result, worst_result, output_dir)

    print()
    print('=' * 60)
    print('週別深掘り分析 完了')
    print('=' * 60)


if __name__ == '__main__':
    main()
