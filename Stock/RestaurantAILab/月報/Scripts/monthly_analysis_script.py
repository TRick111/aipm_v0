"""
月報用データ分析スクリプト
- 週報の analysis_script.py を月次版に変換
- 比較軸: 前月比 / 前年同月比 / 過去3ヶ月平均比
- トレンド: 直近6ヶ月推移
- 深掘り: 月内の週別推移 + 好調週/不調週比較
- 商品: TOP15
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
import json
import sys
import argparse
import calendar

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings('ignore')

# ==========================================
# コマンドライン引数
# ==========================================
parser = argparse.ArgumentParser(description='飲食店データ分析スクリプト - 月報作成基礎資料')
parser.add_argument('-m', '--month', type=str, required=True,
                    help='対象月 (例: 2026-01)')
parser.add_argument('-o', '--output-dir', type=str, default=None,
                    help='出力ディレクトリ')
parser.add_argument('--sales-data', type=str, required=True,
                    help='売上データのパス (rawdata.csv)')
parser.add_argument('--reviews-data', type=str, required=True,
                    help='口コミデータのパス (reviews.csv)')
parser.add_argument('--images', action='store_true',
                    help='グラフ画像を出力する（デフォルト: 出力しない）')

args = parser.parse_args()

# パラメータ設定
target_month = args.month  # 'YYYY-MM'
target_year = int(target_month.split('-')[0])
target_month_num = int(target_month.split('-')[1])

# 対象月の開始日・終了日
target_date_start = pd.Timestamp(target_year, target_month_num, 1).date()
last_day = calendar.monthrange(target_year, target_month_num)[1]
target_date_end = pd.Timestamp(target_year, target_month_num, last_day).date()

# month_slug
month_slug = target_month.replace('-', '')  # 2026-01 → 202601

# 出力ディレクトリ
if args.output_dir:
    output_dir = args.output_dir
else:
    output_dir = f'2_output_{month_slug}'

# 中間メモ
memo_content = []

def save_memo(title, content):
    memo_content.append(f"\n## {title}\n{content}\n")
    print(f"\n[メモ] {title}")
    print(content)

# ==========================================
# データ読み込み
# ==========================================
print("=" * 80)
print(f"月報データ分析スクリプト（{target_month}）")
print("=" * 80)

sales_df = pd.read_csv(args.sales_data)
reviews_df = pd.read_csv(args.reviews_data, encoding='utf-8-sig')

# ==========================================
# UTC → JST 変換と営業日定義（週報と同一ロジック）
# ==========================================
sales_df['entry_at'] = pd.to_datetime(sales_df['entry_at'], utc=True)
sales_df['exit_at'] = pd.to_datetime(sales_df['exit_at'], utc=True)
if 'ordered_at' in sales_df.columns:
    sales_df['ordered_at'] = pd.to_datetime(sales_df['ordered_at'], utc=True, errors='coerce')

sales_df['entry_at_jst'] = sales_df['entry_at'].dt.tz_convert('Asia/Tokyo')
sales_df['exit_at_jst'] = sales_df['exit_at'].dt.tz_convert('Asia/Tokyo')

def get_business_date(dt):
    if pd.isna(dt):
        return None
    hour = dt.hour
    if 0 <= hour < 6:
        return (dt - pd.Timedelta(days=1)).date()
    else:
        return dt.date()

sales_df['business_date'] = sales_df['entry_at_jst'].apply(get_business_date)

def get_business_hour(dt):
    if pd.isna(dt):
        return None
    hour = dt.hour
    if 0 <= hour < 6:
        return hour + 24
    else:
        return hour

sales_df['business_hour'] = sales_df['entry_at_jst'].apply(get_business_hour)
sales_df['business_date_dt'] = pd.to_datetime(sales_df['business_date'])
sales_df['year_week'] = sales_df['business_date_dt'].dt.strftime('%G-W%V')
sales_df['year_month'] = sales_df['business_date_dt'].dt.strftime('%Y-%m')
sales_df['date'] = sales_df['business_date']

weekday_map = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
sales_df['weekday'] = sales_df['business_date_dt'].dt.dayofweek.map(weekday_map)

# 口コミデータ
reviews_df['投稿日'] = pd.to_datetime(reviews_df['投稿日'], format='%y/%m/%d', errors='coerce')

# 対象月のデータ
sales_df_filtered = sales_df[(sales_df['date'] >= target_date_start) &
                              (sales_df['date'] <= target_date_end)]

save_memo("データ概要", f"""
- 売上データ期間: {sales_df['date'].min()} ～ {sales_df['date'].max()}
- 売上データ件数: {len(sales_df):,} レコード
- 口コミデータ件数: {len(reviews_df):,} 件
- **対象月: {target_month} ({target_date_start} ～ {target_date_end})**
- 対象月レコード数: {len(sales_df_filtered):,} レコード
- 店舗: {sales_df['store_name'].iloc[0]}
- UTC→JST変換済み / 営業日定義: 0-5時は前日営業日
""")

os.makedirs(output_dir, exist_ok=True)
print(f"\n出力ディレクトリ: {output_dir}")

# ==========================================
# 会計単位集計
# ==========================================
account_df = sales_df.groupby(['account_id', 'business_date', 'year_week', 'year_month', 'weekday', 'business_hour']).agg({
    'account_total': 'first',
    'customer_count': 'first'
}).reset_index()
account_df['date'] = account_df['business_date']

save_memo("データ処理", f"会計単位集計: {len(account_df):,} 件")

# ==========================================
# 1. 月次売上集計
# ==========================================

# ---- 月次集計 ----
monthly_sales = account_df.groupby('year_month').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={
    'account_total': '売上',
    'customer_count': '客数',
    'account_id': '組数'
})
monthly_sales['客単価'] = monthly_sales['売上'] / monthly_sales['客数']

# 営業日数を月ごとに算出
business_days_per_month = account_df.groupby('year_month')['business_date'].nunique()
monthly_sales['営業日数'] = business_days_per_month
monthly_sales['日平均売上'] = monthly_sales['売上'] / monthly_sales['営業日数']
monthly_sales['日平均客数'] = monthly_sales['客数'] / monthly_sales['営業日数']
monthly_sales = monthly_sales.sort_index()

# 対象月データ
target_data = monthly_sales.loc[target_month] if target_month in monthly_sales.index else None
if target_data is None:
    print(f"\n警告: {target_month} のデータが見つかりません")
    print("利用可能な月:", monthly_sales.index.tolist())
    sys.exit(1)

# ---- 比較対象 ----
month_list = sorted(monthly_sales.index.tolist())
target_idx = month_list.index(target_month) if target_month in month_list else -1

# 前月
prev_month = month_list[target_idx - 1] if target_idx > 0 else None
prev_month_data = monthly_sales.loc[prev_month] if prev_month else None

# 前年同月
prev_year_month = f"{target_year - 1}-{target_month_num:02d}"
prev_year_data = monthly_sales.loc[prev_year_month] if prev_year_month in monthly_sales.index else None

# 過去3ヶ月平均（対象月を含まない直前3ヶ月）
if target_idx >= 3:
    ma3_months = month_list[target_idx - 3:target_idx]
    ma3_data = monthly_sales.loc[ma3_months].mean()
    ma3_label = f"過去3ヶ月平均 ({ma3_months[0]}～{ma3_months[-1]})"
elif target_idx > 0:
    ma3_months = month_list[:target_idx]
    ma3_data = monthly_sales.loc[ma3_months].mean()
    ma3_label = f"過去{len(ma3_months)}ヶ月平均 ({ma3_months[0]}～{ma3_months[-1]})"
else:
    ma3_data = None
    ma3_label = None

# 直近6ヶ月リスト
recent_start = max(0, target_idx - 5)
recent_month_list = month_list[recent_start:target_idx + 1]

# ---- 比較メモ ----
comp_memo = f"""
### 対象月 ({target_month})
- 売上: ¥{target_data['売上']:,.0f}
- 客数: {target_data['客数']:.0f}人
- 組数: {target_data['組数']:.0f}組
- 客単価: ¥{target_data['客単価']:,.0f}
- 営業日数: {target_data['営業日数']:.0f}日
- 日平均売上: ¥{target_data['日平均売上']:,.0f}
"""

if prev_month_data is not None:
    comp_memo += f"""
### 前月比 ({prev_month})
- 売上: {(target_data['売上']/prev_month_data['売上']-1)*100:+.1f}%
- 客数: {(target_data['客数']/prev_month_data['客数']-1)*100:+.1f}%
- 客単価: {(target_data['客単価']/prev_month_data['客単価']-1)*100:+.1f}%
- 日平均売上: {(target_data['日平均売上']/prev_month_data['日平均売上']-1)*100:+.1f}%
"""

if prev_year_data is not None:
    comp_memo += f"""
### 前年同月比 ({prev_year_month})
- 売上: {(target_data['売上']/prev_year_data['売上']-1)*100:+.1f}%
- 客数: {(target_data['客数']/prev_year_data['客数']-1)*100:+.1f}%
- 客単価: {(target_data['客単価']/prev_year_data['客単価']-1)*100:+.1f}%
"""

save_memo("月次売上比較", comp_memo)

# ==========================================
# 2. スライド第1部用データ出力（月次トレンド）
# ==========================================
slide1 = []
slide1.append("=" * 60)
slide1.append("【スライド第1部用】月次トレンドデータ（直近6ヶ月）")
slide1.append("=" * 60)
slide1.append("")

# 直近6ヶ月推移テーブル
slide1.append("## 直近6ヶ月の推移データ（グラフ用）")
slide1.append("")
slide1.append("| 月 | 売上 | 客数 | 客単価 | 組数 | 営業日数 | 日平均売上 |")
slide1.append("|---|---|---|---|---|---|---|")
for m in recent_month_list:
    d = monthly_sales.loc[m]
    slide1.append(f"| {m} | ¥{d['売上']:,.0f} | {d['客数']:.0f}人 | ¥{d['客単価']:,.0f} | {d['組数']:.0f}組 | {d['営業日数']:.0f}日 | ¥{d['日平均売上']:,.0f} |")
slide1.append("")

# 前年同月比較
slide1.append("## 前年同月比較データ")
slide1.append("")
if prev_year_data is not None:
    slide1.append(f"| 指標 | 当月 ({target_month}) | 前年同月 ({prev_year_month}) | 成長率 |")
    slide1.append("|---|---|---|---|")
    slide1.append(f"| 売上 | ¥{target_data['売上']:,.0f} | ¥{prev_year_data['売上']:,.0f} | {(target_data['売上']/prev_year_data['売上']-1)*100:+.1f}% |")
    slide1.append(f"| 客数 | {target_data['客数']:.0f}人 | {prev_year_data['客数']:.0f}人 | {(target_data['客数']/prev_year_data['客数']-1)*100:+.1f}% |")
    slide1.append(f"| 客単価 | ¥{target_data['客単価']:,.0f} | ¥{prev_year_data['客単価']:,.0f} | {(target_data['客単価']/prev_year_data['客単価']-1)*100:+.1f}% |")
    slide1.append(f"| 日平均売上 | ¥{target_data['日平均売上']:,.0f} | ¥{prev_year_data['日平均売上']:,.0f} | {(target_data['日平均売上']/prev_year_data['日平均売上']-1)*100:+.1f}% |")
else:
    slide1.append("前年同月データなし")
slide1.append("")

# KPIサマリー
slide1.append("## 月間サマリー用KPI")
slide1.append("")
slide1.append("| 指標 | 実績 | 前月比 | 前年同月比 |")
slide1.append("|---|---|---|---|")

def pct_change(cur, prev):
    if prev is not None and prev != 0:
        return f"{(cur/prev-1)*100:+.1f}%"
    return "N/A"

pm_sales = pct_change(target_data['売上'], prev_month_data['売上']) if prev_month_data is not None else "N/A"
pm_cust  = pct_change(target_data['客数'], prev_month_data['客数']) if prev_month_data is not None else "N/A"
pm_unit  = pct_change(target_data['客単価'], prev_month_data['客単価']) if prev_month_data is not None else "N/A"
pm_davg  = pct_change(target_data['日平均売上'], prev_month_data['日平均売上']) if prev_month_data is not None else "N/A"

py_sales = pct_change(target_data['売上'], prev_year_data['売上']) if prev_year_data is not None else "N/A"
py_cust  = pct_change(target_data['客数'], prev_year_data['客数']) if prev_year_data is not None else "N/A"
py_unit  = pct_change(target_data['客単価'], prev_year_data['客単価']) if prev_year_data is not None else "N/A"
py_davg  = pct_change(target_data['日平均売上'], prev_year_data['日平均売上']) if prev_year_data is not None else "N/A"

slide1.append(f"| 売上 | ¥{target_data['売上']:,.0f} | {pm_sales} | {py_sales} |")
slide1.append(f"| 客数 | {target_data['客数']:.0f}人 | {pm_cust} | {py_cust} |")
slide1.append(f"| 客単価 | ¥{target_data['客単価']:,.0f} | {pm_unit} | {py_unit} |")
slide1.append(f"| 営業日数 | {target_data['営業日数']:.0f}日 | — | — |")
slide1.append(f"| 日平均売上 | ¥{target_data['日平均売上']:,.0f} | {pm_davg} | {py_davg} |")
slide1.append("")

with open(os.path.join(output_dir, 'slide_data_part1.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(slide1))
print("[出力] slide_data_part1.txt")

# ==========================================
# 3. 月内の週別推移（第2部用）
# ==========================================

# 対象月に含まれる週を抽出（営業日ベース）
target_month_accounts = account_df[account_df['year_month'] == target_month]
weekly_in_month = target_month_accounts.groupby('year_week').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={
    'account_total': '売上',
    'customer_count': '客数',
    'account_id': '組数'
})
weekly_in_month['客単価'] = weekly_in_month['売上'] / weekly_in_month['客数']

# 営業日数
weekly_bdays = target_month_accounts.groupby('year_week')['business_date'].nunique()
weekly_in_month['営業日数'] = weekly_bdays
weekly_in_month['日平均売上'] = weekly_in_month['売上'] / weekly_in_month['営業日数']
weekly_in_month = weekly_in_month.sort_index()

# 前年同週比較
weekly_in_month_with_yoy = weekly_in_month.copy()

# 週次全体データ
weekly_all = account_df.groupby('year_week').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={
    'account_total': '売上',
    'customer_count': '客数',
    'account_id': '組数'
})
weekly_all['客単価'] = weekly_all['売上'] / weekly_all['客数']

yoy_data = []
for week in weekly_in_month.index:
    try:
        w_year = int(week.split('-W')[0])
        w_num = int(week.split('-W')[1])
        prev_year_week = f"{w_year - 1}-W{w_num:02d}"
        if prev_year_week in weekly_all.index:
            yoy_data.append({
                'year_week': week,
                '前年同週売上': weekly_all.loc[prev_year_week, '売上'],
                '前年比': (weekly_in_month.loc[week, '売上'] / weekly_all.loc[prev_year_week, '売上'] - 1) * 100
            })
        else:
            yoy_data.append({'year_week': week, '前年同週売上': None, '前年比': None})
    except:
        yoy_data.append({'year_week': week, '前年同週売上': None, '前年比': None})

yoy_df = pd.DataFrame(yoy_data).set_index('year_week')

# 好調週 / 不調週（日平均売上ベース）
if len(weekly_in_month) >= 2:
    best_week = weekly_in_month['日平均売上'].idxmax()
    worst_week = weekly_in_month['日平均売上'].idxmin()
    best_data = weekly_in_month.loc[best_week]
    worst_data = weekly_in_month.loc[worst_week]
else:
    best_week = worst_week = None
    best_data = worst_data = None

# ---- 曜日別分析（月全体の傾向）----
weekday_order = ['月', '火', '水', '木', '金', '土', '日']

target_month_acct = account_df[account_df['year_month'] == target_month]
weekday_month = target_month_acct.groupby('weekday').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={'account_total': '売上', 'customer_count': '客数', 'account_id': '組数'})
weekday_month['客単価'] = weekday_month['売上'] / weekday_month['客数']

# 曜日ごとの営業日数
weekday_bdays_month = target_month_acct.groupby('weekday')['business_date'].nunique()
weekday_month['営業日数'] = weekday_bdays_month
weekday_month['日平均売上'] = weekday_month['売上'] / weekday_month['営業日数']
weekday_month['日平均客数'] = weekday_month['客数'] / weekday_month['営業日数']
weekday_month['日平均客単価'] = weekday_month['客単価']  # 既に平均
weekday_month = weekday_month.reindex([w for w in weekday_order if w in weekday_month.index])

# 前月の曜日別（比較用）
if prev_month:
    prev_month_acct = account_df[account_df['year_month'] == prev_month]
    weekday_prev = prev_month_acct.groupby('weekday').agg({
        'account_total': 'sum',
        'customer_count': 'sum',
        'account_id': 'count'
    }).rename(columns={'account_total': '売上', 'customer_count': '客数', 'account_id': '組数'})
    weekday_prev['客単価'] = weekday_prev['売上'] / weekday_prev['客数']
    prev_bdays = prev_month_acct.groupby('weekday')['business_date'].nunique()
    weekday_prev['営業日数'] = prev_bdays
    weekday_prev['日平均売上'] = weekday_prev['売上'] / weekday_prev['営業日数']
    weekday_prev = weekday_prev.reindex([w for w in weekday_order if w in weekday_prev.index])
else:
    weekday_prev = pd.DataFrame()

# ---- 時間帯別集計（月全体）----
def get_time_bucket_label(hour):
    if 18 <= hour < 20: return '18-20時'
    elif 20 <= hour < 22: return '20-22時'
    elif 22 <= hour < 24: return '22-24時'
    elif 24 <= hour < 26: return '24-26時'
    else: return 'その他'

hourly_month = target_month_acct.groupby('business_hour').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).sort_index()
hourly_month['time_bucket'] = [get_time_bucket_label(h) for h in hourly_month.index]

hourly_bucket = hourly_month.groupby('time_bucket').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'sum'
})
bucket_order = ['18-20時', '20-22時', '22-24時', '24-26時', 'その他']
hourly_bucket = hourly_bucket.reindex([b for b in bucket_order if b in hourly_bucket.index])
total_hourly_sales = hourly_bucket['account_total'].sum()
hourly_bucket['構成比'] = hourly_bucket['account_total'] / total_hourly_sales * 100

# ---- 第2部テキスト出力 ----
slide2 = []
slide2.append("=" * 60)
slide2.append("【スライド第2部用】週別推移・深掘り + 曜日別 + 時間帯別")
slide2.append("=" * 60)
slide2.append("")

# 週別概況
slide2.append("## 月内の週別推移")
slide2.append("")
slide2.append("| 週 | 売上 | 客数 | 客単価 | 営業日数 | 日平均売上 | 前年同週比 |")
slide2.append("|---|---|---|---|---|---|---|")
for week in weekly_in_month.index:
    w = weekly_in_month.loc[week]
    yoy_pct = f"{yoy_df.loc[week, '前年比']:+.1f}%" if week in yoy_df.index and pd.notna(yoy_df.loc[week, '前年比']) else "N/A"
    slide2.append(f"| {week} | ¥{w['売上']:,.0f} | {w['客数']:.0f}人 | ¥{w['客単価']:,.0f} | {w['営業日数']:.0f}日 | ¥{w['日平均売上']:,.0f} | {yoy_pct} |")
slide2.append("")

# 好調/不調週
if best_week and worst_week:
    slide2.append(f"## 深掘り対象週")
    slide2.append(f"- 好調週: {best_week} (日平均売上: ¥{best_data['日平均売上']:,.0f})")
    slide2.append(f"- 不調週: {worst_week} (日平均売上: ¥{worst_data['日平均売上']:,.0f})")
    slide2.append("")

    for label, wk, wd in [("好調週", best_week, best_data), ("不調週", worst_week, worst_data)]:
        slide2.append(f"### {label}（{wk}）基本数字")
        slide2.append("")
        slide2.append("| 指標 | 実績 | 月平均 |")
        slide2.append("|---|---|---|")
        month_avg = weekly_in_month.mean()
        slide2.append(f"| 売上 | ¥{wd['売上']:,.0f} | ¥{month_avg['売上']:,.0f} |")
        slide2.append(f"| 客数 | {wd['客数']:.0f}人 | {month_avg['客数']:.0f}人 |")
        slide2.append(f"| 客単価 | ¥{wd['客単価']:,.0f} | ¥{month_avg['客単価']:,.0f} |")
        slide2.append(f"| 日平均売上 | ¥{wd['日平均売上']:,.0f} | ¥{month_avg['日平均売上']:,.0f} |")
        slide2.append("")

# 曜日別分析
slide2.append("## 曜日別日平均（当月）")
slide2.append("")
slide2.append("| 曜日 | 日平均売上 | 日平均客数 | 客単価 | 営業日数 | 前月比(売上) |")
slide2.append("|---|---|---|---|---|---|")
for day in weekday_month.index:
    d = weekday_month.loc[day]
    if not weekday_prev.empty and day in weekday_prev.index:
        pm_chg = f"{(d['日平均売上']/weekday_prev.loc[day, '日平均売上']-1)*100:+.1f}%"
    else:
        pm_chg = "N/A"
    slide2.append(f"| {day} | ¥{d['日平均売上']:,.0f} | {d['日平均客数']:.1f}人 | ¥{d['客単価']:,.0f} | {d['営業日数']:.0f}日 | {pm_chg} |")
slide2.append("")

# 時間帯別分析
slide2.append("## 時間帯別月間売上")
slide2.append("")
slide2.append("| 時間帯 | 月間売上 | 構成比 | 月間客数 |")
slide2.append("|---|---|---|---|")
for bucket in hourly_bucket.index:
    r = hourly_bucket.loc[bucket]
    slide2.append(f"| {bucket} | ¥{r['account_total']:,.0f} | {r['構成比']:.1f}% | {r['customer_count']:.0f}人 |")
slide2.append("")

with open(os.path.join(output_dir, 'slide_data_part2.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(slide2))
print("[出力] slide_data_part2.txt")

# ==========================================
# 4. カテゴリ・商品分析（第3部用）
# ==========================================

# カテゴリ別（対象月）
cat_monthly = sales_df[sales_df['year_month'] == target_month].groupby('category1').agg({
    'subtotal': 'sum',
    'quantity': 'sum'
}).reset_index().sort_values('subtotal', ascending=False)
cat_total = cat_monthly['subtotal'].sum()
cat_monthly['構成比'] = cat_monthly['subtotal'] / cat_total * 100

# 前月カテゴリ
if prev_month:
    cat_prev = sales_df[sales_df['year_month'] == prev_month].groupby('category1').agg({'subtotal': 'sum'}).reset_index()
    cat_prev_total = cat_prev['subtotal'].sum()
    cat_prev['構成比'] = cat_prev['subtotal'] / cat_prev_total * 100 if cat_prev_total > 0 else 0
    cat_prev = cat_prev.set_index('category1')
else:
    cat_prev = pd.DataFrame()

# 商品別（対象月 TOP15）
prod_monthly = sales_df[sales_df['year_month'] == target_month].groupby('menu_name').agg({
    'subtotal': 'sum',
    'quantity': 'sum'
}).reset_index().sort_values('subtotal', ascending=False)
prod_total = prod_monthly['subtotal'].sum()
prod_monthly['構成比'] = prod_monthly['subtotal'] / prod_total * 100

# 前月商品
if prev_month:
    prod_prev = sales_df[sales_df['year_month'] == prev_month].groupby('menu_name').agg({'subtotal': 'sum'}).reset_index()
    prod_prev_total = prod_prev['subtotal'].sum()
    prod_prev['構成比'] = prod_prev['subtotal'] / prod_prev_total * 100 if prod_prev_total > 0 else 0
    prod_prev = prod_prev.set_index('menu_name')
else:
    prod_prev = pd.DataFrame()

# ---- 第3部テキスト出力 ----
slide3 = []
slide3.append("=" * 60)
slide3.append("【スライド第3部用】商品・カテゴリ分析データ")
slide3.append("=" * 60)
slide3.append("")

# カテゴリ
slide3.append("## カテゴリ別月間売上（円グラフ用）")
slide3.append("")
slide3.append("| カテゴリ | 月間売上 | 構成比 | 販売数 | 前月比(構成比) |")
slide3.append("|---|---|---|---|---|")
for _, row in cat_monthly.iterrows():
    cat = row['category1']
    pm_pt = ""
    if not cat_prev.empty and cat in cat_prev.index:
        pm_pt = f"{row['構成比'] - cat_prev.loc[cat, '構成比']:+.1f}pt"
    else:
        pm_pt = "—"
    slide3.append(f"| {cat} | ¥{row['subtotal']:,.0f} | {row['構成比']:.1f}% | {row['quantity']:.0f}個 | {pm_pt} |")
slide3.append("")

# 商品TOP15
slide3.append("## 商品別売上TOP15（月間）")
slide3.append("")
slide3.append("| 順位 | 商品名 | 月間売上 | 構成比 | 前月比(構成比) |")
slide3.append("|---|---|---|---|---|")
for i, (_, row) in enumerate(prod_monthly.head(15).iterrows(), 1):
    prod = row['menu_name']
    pm_pt = ""
    if not prod_prev.empty and prod in prod_prev.index:
        pm_pt = f"{row['構成比'] - prod_prev.loc[prod, '構成比']:+.2f}pt"
    else:
        pm_pt = "NEW"
    slide3.append(f"| {i} | {prod} | ¥{row['subtotal']:,.0f} | {row['構成比']:.1f}% | {pm_pt} |")
slide3.append("")

# 構成比増減
if not prod_prev.empty:
    changes = []
    for _, row in prod_monthly.iterrows():
        prod = row['menu_name']
        if prod in prod_prev.index:
            changes.append({
                'product': prod,
                'current': row['構成比'],
                'prev': prod_prev.loc[prod, '構成比'],
                'change': row['構成比'] - prod_prev.loc[prod, '構成比']
            })
    changes_df = pd.DataFrame(changes)
    if not changes_df.empty:
        slide3.append("## 構成比増加TOP5（前月比）")
        slide3.append("")
        slide3.append("| 商品名 | 当月構成比 | 前月構成比 | 変化 |")
        slide3.append("|---|---|---|---|")
        for _, r in changes_df.nlargest(5, 'change').iterrows():
            slide3.append(f"| {r['product']} | {r['current']:.2f}% | {r['prev']:.2f}% | {r['change']:+.2f}pt |")
        slide3.append("")

        slide3.append("## 構成比減少TOP5（前月比）")
        slide3.append("")
        slide3.append("| 商品名 | 当月構成比 | 前月構成比 | 変化 |")
        slide3.append("|---|---|---|---|")
        for _, r in changes_df.nsmallest(5, 'change').iterrows():
            slide3.append(f"| {r['product']} | {r['current']:.2f}% | {r['prev']:.2f}% | {r['change']:+.2f}pt |")
        slide3.append("")

with open(os.path.join(output_dir, 'slide_data_part3.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(slide3))
print("[出力] slide_data_part3.txt")

# ==========================================
# 5. 口コミ分析（月間）
# ==========================================
latest_date_dt = pd.to_datetime(target_date_end)
start_date_dt = pd.to_datetime(target_date_start)

month_reviews = reviews_df[
    (reviews_df['投稿日'] >= start_date_dt) &
    (reviews_df['投稿日'] <= latest_date_dt)
].copy()

reviews_memo = f"""
### 対象月の口コミ ({target_date_start} ～ {target_date_end})
- 新規投稿数: {len(month_reviews)}件
"""

if len(month_reviews) > 0:
    reviews_memo += f"- 平均評価: {month_reviews['総合点数'].mean():.2f}点\n"
else:
    reviews_memo += "- 対象月に新規投稿はありませんでした\n"

save_memo("月間口コミ", reviews_memo)

# ==========================================
# 6. データ保存
# ==========================================

# JSON
analysis_results = {
    'meta': {
        'analysis_date': str(datetime.now()),
        'target_month': target_month,
        'target_date_start': str(target_date_start),
        'target_date_end': str(target_date_end),
        'store_name': sales_df['store_name'].iloc[0]
    },
    'monthly_kpi': {
        'target': {
            '売上': float(target_data['売上']),
            '客数': int(target_data['客数']),
            '組数': int(target_data['組数']),
            '客単価': float(target_data['客単価']),
            '営業日数': int(target_data['営業日数']),
            '日平均売上': float(target_data['日平均売上']),
        },
        'prev_month': {
            'month': prev_month,
            '売上': float(prev_month_data['売上']) if prev_month_data is not None else None,
            '客数': int(prev_month_data['客数']) if prev_month_data is not None else None,
            '客単価': float(prev_month_data['客単価']) if prev_month_data is not None else None,
        } if prev_month_data is not None else None,
        'prev_year': {
            'month': prev_year_month,
            '売上': float(prev_year_data['売上']) if prev_year_data is not None else None,
            '客数': int(prev_year_data['客数']) if prev_year_data is not None else None,
            '客単価': float(prev_year_data['客単価']) if prev_year_data is not None else None,
        } if prev_year_data is not None else None,
    },
    'weekly_in_month': weekly_in_month.reset_index().to_dict('records'),
    'best_week': best_week,
    'worst_week': worst_week,
    'category_analysis': cat_monthly.to_dict('records'),
    'product_analysis': prod_monthly.head(15).to_dict('records'),
    'reviews_count': len(month_reviews),
}

with open(os.path.join(output_dir, 'analysis_results.json'), 'w', encoding='utf-8') as f:
    json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)

# CSV
monthly_sales.to_csv(os.path.join(output_dir, 'monthly_sales.csv'), encoding='utf-8-sig')
weekly_in_month.to_csv(os.path.join(output_dir, 'weekly_in_month.csv'), encoding='utf-8-sig')
weekday_month.to_csv(os.path.join(output_dir, 'weekday_monthly.csv'), encoding='utf-8-sig')
hourly_month.to_csv(os.path.join(output_dir, 'hourly_monthly.csv'), encoding='utf-8-sig')
cat_monthly.to_csv(os.path.join(output_dir, 'category_monthly.csv'), encoding='utf-8-sig', index=False)
prod_monthly.to_csv(os.path.join(output_dir, 'product_monthly.csv'), encoding='utf-8-sig', index=False)

if not month_reviews.empty:
    month_reviews.to_csv(os.path.join(output_dir, 'reviews_monthly.csv'), encoding='utf-8-sig', index=False)

# メモ保存
with open(os.path.join(output_dir, 'analysis_memo.txt'), 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write(f"月報分析メモ ({target_month})\n")
    f.write("=" * 80 + "\n")
    for memo in memo_content:
        f.write(memo)

# 完了
output_summary = f"""
分析完了！結果は {output_dir} に保存されました。

【スライド用データ（テキスト形式）】
- slide_data_part1.txt: 第1部用（月次トレンド6ヶ月、KPI、前年同月比較）
- slide_data_part2.txt: 第2部用（週別推移、好調/不調週、曜日別、時間帯別）
- slide_data_part3.txt: 第3部用（カテゴリ構成比、商品TOP15、構成比増減）

【データファイル（CSV/JSON）】
- analysis_results.json: 分析結果
- monthly_sales.csv: 月次売上データ（全期間）
- weekly_in_month.csv: 月内の週別推移
- weekday_monthly.csv: 曜日別集計（対象月）
- hourly_monthly.csv: 時間帯別集計（対象月）
- category_monthly.csv: カテゴリ別月間売上
- product_monthly.csv: 商品別月間売上
- reviews_monthly.csv: 対象月の口コミ
- analysis_memo.txt: 分析メモ
"""

save_memo("完了", output_summary)

print("\n" + "=" * 80)
print("月報分析完了")
print("=" * 80)
