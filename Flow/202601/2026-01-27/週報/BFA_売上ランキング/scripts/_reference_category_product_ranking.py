# -*- coding: utf-8 -*-
"""
カテゴリ内商品ランキング分析スクリプト

各カテゴリ内の売上TOP10/Bottom10商品を抽出し、
全体売上構成比とカテゴリ内構成比を算出する。

Usage:
    python category_product_ranking.py -w 2026-W03 -e 2026-01-18 --sales-data "path/to/rawdata.csv" -o "output_dir"
"""

import pandas as pd
import numpy as np
import sys
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description='カテゴリ内商品ランキング分析')
    parser.add_argument('-w', '--week', required=True, help='対象週（例: 2026-W03）')
    parser.add_argument('-e', '--end-date', required=True, help='対象週の終了日（例: 2026-01-18）')
    parser.add_argument('--sales-data', required=True, help='売上データのパス（rawdata.csv）')
    parser.add_argument('-o', '--output-dir', required=True, help='出力ディレクトリ')
    return parser.parse_args()


def load_and_process_data(sales_file, target_week, end_date):
    """
    データを読み込み、対象週のデータを抽出
    """
    print(f'データを読み込んでいます: {sales_file}')

    # データ読み込み
    df = pd.read_csv(sales_file)

    # UTC → JST変換
    df['entry_at'] = pd.to_datetime(df['entry_at'], utc=True)
    df['entry_at_jst'] = df['entry_at'].dt.tz_convert('Asia/Tokyo')

    # 営業日定義（JST 0-5時は前日の営業日）
    df['business_date'] = df['entry_at_jst'].apply(
        lambda dt: (dt - pd.Timedelta(days=1)).date() if 0 <= dt.hour < 6 else dt.date()
    )

    # ISO週番号を付与
    df['year_week'] = df.apply(
        lambda row: f"{row['business_date'].isocalendar()[0]}-W{row['business_date'].isocalendar()[1]:02d}",
        axis=1
    )

    # 対象週のデータをフィルタ
    target_data = df[df['year_week'] == target_week].copy()

    if len(target_data) == 0:
        raise ValueError(f'対象週 {target_week} のデータが見つかりません')

    print(f'対象週のレコード数: {len(target_data)}')

    return target_data


def analyze_category_products(df):
    """
    カテゴリ別の商品ランキングを分析
    """
    # 全体売上を計算
    total_sales = df['price'].sum()

    print(f'\n総売上: ¥{total_sales:,.0f}')

    # カテゴリ別・商品別に集計
    product_summary = df.groupby(['category1', 'menu_name']).agg({
        'price': ['sum', 'count']
    }).reset_index()
    product_summary.columns = ['category1', 'menu_name', 'sales', 'quantity']

    # 全体売上構成比を計算
    product_summary['overall_ratio'] = (product_summary['sales'] / total_sales * 100).round(2)

    # カテゴリ別の売上を計算
    category_sales = df.groupby('category1')['price'].sum().reset_index()
    category_sales.columns = ['category1', 'category_sales']

    # カテゴリ別売上をマージ
    product_summary = product_summary.merge(category_sales, on='category1')

    # カテゴリ内構成比を計算
    product_summary['category_ratio'] = (
        product_summary['sales'] / product_summary['category_sales'] * 100
    ).round(2)

    # カテゴリごとにTOP10/Bottom10を抽出
    results = {}

    for category in product_summary['category1'].unique():
        category_data = product_summary[product_summary['category1'] == category].copy()
        category_data = category_data.sort_values('sales', ascending=False)

        # TOP10
        top10 = category_data.head(10).copy()
        top10['rank'] = range(1, len(top10) + 1)

        # Bottom10（売上が小さい順）
        bottom10 = category_data.tail(10).sort_values('sales', ascending=True).copy()
        bottom10['rank'] = range(1, len(bottom10) + 1)

        results[category] = {
            'category_sales': float(category_data['category_sales'].iloc[0]),
            'category_ratio': float((category_data['category_sales'].iloc[0] / total_sales * 100)),
            'product_count': len(category_data),
            'top10': top10[['rank', 'menu_name', 'sales', 'quantity', 'overall_ratio', 'category_ratio']].to_dict('records'),
            'bottom10': bottom10[['rank', 'menu_name', 'sales', 'quantity', 'overall_ratio', 'category_ratio']].to_dict('records')
        }

    return results, total_sales


def save_results(results, total_sales, output_dir, target_week):
    """
    分析結果を保存
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # JSON形式で保存
    json_file = output_path / 'category_product_ranking.json'
    output_data = {
        'meta': {
            'target_week': target_week,
            'total_sales': float(total_sales),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'categories': results
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f'\nJSON保存: {json_file}')

    # CSV形式で保存（カテゴリ別）
    for category, data in results.items():
        # TOP10
        top10_df = pd.DataFrame(data['top10'])
        top10_file = output_path / f'category_{category}_top10.csv'
        top10_df.to_csv(top10_file, index=False, encoding='utf-8-sig')

        # Bottom10
        bottom10_df = pd.DataFrame(data['bottom10'])
        bottom10_file = output_path / f'category_{category}_bottom10.csv'
        bottom10_df.to_csv(bottom10_file, index=False, encoding='utf-8-sig')

    print(f'CSV保存: カテゴリ別ファイルを {output_path} に保存しました')

    # サマリーレポートを作成
    create_summary_report(results, total_sales, output_path, target_week)


def create_summary_report(results, total_sales, output_path, target_week):
    """
    サマリーレポートをMarkdown形式で作成
    """
    report_file = output_path / 'category_product_ranking_report.md'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f'# カテゴリ内商品ランキング分析レポート\n\n')
        f.write(f'**対象週**: {target_week}\n')
        f.write(f'**総売上**: ¥{total_sales:,.0f}\n')
        f.write(f'**分析日**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write('---\n\n')

        # カテゴリを売上順にソート
        sorted_categories = sorted(
            results.items(),
            key=lambda x: x[1]['category_sales'],
            reverse=True
        )

        for category, data in sorted_categories:
            f.write(f'## {category}\n\n')
            f.write(f'- **カテゴリ売上**: ¥{data["category_sales"]:,.0f}\n')
            f.write(f'- **全体構成比**: {data["category_ratio"]:.2f}%\n')
            f.write(f'- **商品数**: {data["product_count"]}種類\n\n')

            # TOP10
            f.write(f'### TOP10商品\n\n')
            f.write('| 順位 | 商品名 | 売上 | 販売数 | 全体構成比 | カテゴリ内構成比 |\n')
            f.write('|------|--------|------|--------|-----------|----------------|\n')
            for item in data['top10']:
                f.write(f'| {item["rank"]} | {item["menu_name"]} | ¥{item["sales"]:,.0f} | '
                       f'{item["quantity"]}個 | {item["overall_ratio"]:.2f}% | {item["category_ratio"]:.2f}% |\n')
            f.write('\n')

            # Bottom10
            f.write(f'### Bottom10商品\n\n')
            f.write('| 順位 | 商品名 | 売上 | 販売数 | 全体構成比 | カテゴリ内構成比 |\n')
            f.write('|------|--------|------|--------|-----------|----------------|\n')
            for item in data['bottom10']:
                f.write(f'| {item["rank"]} | {item["menu_name"]} | ¥{item["sales"]:,.0f} | '
                       f'{item["quantity"]}個 | {item["overall_ratio"]:.2f}% | {item["category_ratio"]:.2f}% |\n')
            f.write('\n')
            f.write('---\n\n')

    print(f'レポート保存: {report_file}')


def main():
    """メイン処理"""
    args = parse_args()

    print('='*80)
    print('カテゴリ内商品ランキング分析スクリプト')
    print('='*80)
    print(f'対象週: {args.week}')
    print(f'終了日: {args.end_date}')
    print(f'出力先: {args.output_dir}')
    print()

    # データ読み込みと処理
    df = load_and_process_data(args.sales_data, args.week, args.end_date)

    # カテゴリ別商品ランキング分析
    results, total_sales = analyze_category_products(df)

    # 結果を保存
    save_results(results, total_sales, args.output_dir, args.week)

    # サマリーを表示
    print('\n' + '='*80)
    print('カテゴリ別サマリー')
    print('='*80)

    sorted_categories = sorted(
        results.items(),
        key=lambda x: x[1]['category_sales'],
        reverse=True
    )

    for category, data in sorted_categories:
        print(f'\n【{category}】')
        print(f'  売上: ¥{data["category_sales"]:,.0f} ({data["category_ratio"]:.2f}%)')
        print(f'  商品数: {data["product_count"]}種類')
        print(f'  TOP商品: {data["top10"][0]["menu_name"]} (¥{data["top10"][0]["sales"]:,.0f})')

    print('\n' + '='*80)
    print('分析完了')
    print('='*80)


if __name__ == '__main__':
    main()
