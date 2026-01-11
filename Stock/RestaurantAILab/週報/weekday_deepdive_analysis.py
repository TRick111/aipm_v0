"""
曜日別売上の深堀分析スクリプト

対象週と前週の曜日別売上差を以下の観点で詳細分析:
1. パーティサイズ分析（1名/2名/3-4名/5名以上）
2. 時間帯バケット分析（18-19時、20-21時等）
3. 会計レベルの確認（大口会計、単価分布）
4. 商品ミックス分析（高単価商品、カテゴリ別）
5. 例外データの確認（営業時間外、特殊計上）
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ================================================================================
# 設定
# ================================================================================
TARGET_WEEK = "2025-W52"
TARGET_END_DATE = "2025-12-31"
SALES_DATA_PATH = "Stock/RestaurantAILab/週報/1_input/rawdata.csv"
OUTPUT_DIR = "Stock/RestaurantAILab/週報/2_output_2025w52"

# 対象週の開始日を計算（ISO週番号から）
year, week = TARGET_WEEK.split('-W')
year, week = int(year), int(week)
target_end = pd.to_datetime(TARGET_END_DATE)
target_start = target_end - timedelta(days=6)

# 前週の期間
prev_end = target_start - timedelta(days=1)
prev_start = prev_end - timedelta(days=6)

print("="*80)
print(f"曜日別売上 深堀分析スクリプト - {TARGET_WEEK}")
print("="*80)
print(f"\n対象週: {target_start.date()} ～ {target_end.date()}")
print(f"前週: {prev_start.date()} ～ {prev_end.date()}")

# ================================================================================
# データ読み込み
# ================================================================================
print("\n[1] データ読み込み中...")

df = pd.read_csv(SALES_DATA_PATH, encoding='utf-8-sig')
print(f"   - 全レコード数: {len(df):,}件")

# カラム名を日本語にマッピング
column_map = {
    'entry_at': '日時',
    'account_id': '支払ID',
    'account_total': '会計合計',
    'customer_count': '人数',
    'menu_name': '商品名',
    'price': '単価',
    'quantity': '数量',
    'subtotal': '売上',
    'category1': 'カテゴリ1',
    'ordered_at': '注文時刻'
}

# 日時変換（UTC → JST、営業日調整）
df['日時_UTC'] = pd.to_datetime(df['entry_at'])
df['日時_JST'] = df['日時_UTC'] + pd.Timedelta(hours=9)

# 営業日の定義: JST 0-5時は前日の営業日として扱う
df['営業日'] = df['日時_JST'].apply(
    lambda x: (x - pd.Timedelta(hours=5)).date()
)

# 曜日（営業日ベース）
df['曜日'] = pd.to_datetime(df['営業日']).dt.day_name()
df['曜日_日本語'] = pd.to_datetime(df['営業日']).dt.dayofweek.map({
    0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'
})

# 時刻（営業時間基準）
df['時刻_JST'] = df['日時_JST'].dt.hour

# カラム名を統一
df['支払ID'] = df['account_id']
df['人数'] = df['customer_count']
df['商品名'] = df['menu_name']
df['単価'] = df['price']
df['数量'] = df['quantity']
df['売上'] = df['subtotal']
df['カテゴリ1'] = df['category1']

# 対象期間でフィルタ
df['営業日_dt'] = pd.to_datetime(df['営業日'])
df_target = df[(df['営業日_dt'] >= target_start) & (df['営業日_dt'] <= target_end)].copy()
df_prev = df[(df['営業日_dt'] >= prev_start) & (df['営業日_dt'] <= prev_end)].copy()

print(f"   - 対象週レコード: {len(df_target):,}件")
print(f"   - 前週レコード: {len(df_prev):,}件")

# ================================================================================
# 会計単位集計
# ================================================================================
print("\n[2] 会計単位集計中...")

def aggregate_by_payment(df_input):
    """会計単位で集計"""
    agg_data = df_input.groupby(['営業日', '曜日_日本語', '支払ID']).agg({
        '売上': 'sum',
        '人数': 'first',  # 会計単位で人数は一意
        '商品名': 'count',  # 注文アイテム数
        '時刻_JST': 'first'  # 会計時刻
    }).reset_index()

    agg_data.columns = ['営業日', '曜日', '支払ID', '売上', '人数', 'アイテム数', '会計時刻']
    agg_data['客単価'] = agg_data['売上'] / agg_data['人数']

    return agg_data

df_target_agg = aggregate_by_payment(df_target)
df_prev_agg = aggregate_by_payment(df_prev)

print(f"   - 対象週会計数: {len(df_target_agg):,}件")
print(f"   - 前週会計数: {len(df_prev_agg):,}件")

# ================================================================================
# 分析1: パーティサイズ分析
# ================================================================================
print("\n[3] パーティサイズ分析...")

def classify_party_size(num_people):
    """パーティサイズ分類"""
    if num_people == 1:
        return '1名'
    elif num_people == 2:
        return '2名'
    elif 3 <= num_people <= 4:
        return '3-4名'
    else:
        return '5名以上'

df_target_agg['パーティサイズ'] = df_target_agg['人数'].apply(classify_party_size)
df_prev_agg['パーティサイズ'] = df_prev_agg['人数'].apply(classify_party_size)

# 曜日別パーティサイズ集計
party_target = df_target_agg.groupby(['曜日', 'パーティサイズ']).agg({
    '支払ID': 'count',
    '人数': 'sum',
    '売上': 'sum'
}).rename(columns={'支払ID': '会計数'}).reset_index()

party_prev = df_prev_agg.groupby(['曜日', 'パーティサイズ']).agg({
    '支払ID': 'count',
    '人数': 'sum',
    '売上': 'sum'
}).rename(columns={'支払ID': '会計数'}).reset_index()

# パーティサイズ構成比
def calc_party_composition(df_party, period_name):
    """パーティサイズ構成比計算"""
    result = []
    for dow in df_party['曜日'].unique():
        dow_data = df_party[df_party['曜日'] == dow]
        total_count = dow_data['会計数'].sum()
        total_people = dow_data['人数'].sum()
        total_sales = dow_data['売上'].sum()

        for _, row in dow_data.iterrows():
            result.append({
                '期間': period_name,
                '曜日': dow,
                'パーティサイズ': row['パーティサイズ'],
                '会計数': row['会計数'],
                '会計数構成比': row['会計数'] / total_count * 100 if total_count > 0 else 0,
                '人数': row['人数'],
                '人数構成比': row['人数'] / total_people * 100 if total_people > 0 else 0,
                '売上': row['売上'],
                '売上構成比': row['売上'] / total_sales * 100 if total_sales > 0 else 0,
            })

    return pd.DataFrame(result)

party_target_comp = calc_party_composition(party_target, '対象週')
party_prev_comp = calc_party_composition(party_prev, '前週')
party_comparison = pd.concat([party_prev_comp, party_target_comp], ignore_index=True)

# ================================================================================
# 分析2: 時間帯バケット分析
# ================================================================================
print("\n[4] 時間帯バケット分析...")

def classify_time_bucket(hour):
    """時間帯バケット分類"""
    if 18 <= hour <= 19:
        return '18-19時'
    elif 20 <= hour <= 21:
        return '20-21時'
    elif 22 <= hour <= 23:
        return '22-23時'
    elif hour == 24 or hour == 0:
        return '24-25時'
    elif hour == 25 or hour == 1:
        return '25-26時'
    else:
        return 'その他'

df_target_agg['時間帯'] = df_target_agg['会計時刻'].apply(classify_time_bucket)
df_prev_agg['時間帯'] = df_prev_agg['会計時刻'].apply(classify_time_bucket)

# 曜日×時間帯集計
time_target = df_target_agg.groupby(['曜日', '時間帯']).agg({
    '支払ID': 'count',
    '人数': 'sum',
    '売上': 'sum'
}).rename(columns={'支払ID': '会計数'}).reset_index()

time_prev = df_prev_agg.groupby(['曜日', '時間帯']).agg({
    '支払ID': 'count',
    '人数': 'sum',
    '売上': 'sum'
}).rename(columns={'支払ID': '会計数'}).reset_index()

# 時間帯構成比
def calc_time_composition(df_time, period_name):
    """時間帯構成比計算"""
    result = []
    for dow in df_time['曜日'].unique():
        dow_data = df_time[df_time['曜日'] == dow]
        total_count = dow_data['会計数'].sum()
        total_people = dow_data['人数'].sum()
        total_sales = dow_data['売上'].sum()

        for _, row in dow_data.iterrows():
            result.append({
                '期間': period_name,
                '曜日': dow,
                '時間帯': row['時間帯'],
                '会計数': row['会計数'],
                '会計数構成比': row['会計数'] / total_count * 100 if total_count > 0 else 0,
                '人数': row['人数'],
                '人数構成比': row['人数'] / total_people * 100 if total_people > 0 else 0,
                '売上': row['売上'],
                '売上構成比': row['売上'] / total_sales * 100 if total_sales > 0 else 0,
            })

    return pd.DataFrame(result)

time_target_comp = calc_time_composition(time_target, '対象週')
time_prev_comp = calc_time_composition(time_prev, '前週')
time_comparison = pd.concat([time_prev_comp, time_target_comp], ignore_index=True)

# ================================================================================
# 分析3: 会計レベルの確認
# ================================================================================
print("\n[5] 会計レベル分析...")

def calc_transaction_stats(df_agg, period_name):
    """会計単位の統計"""
    result = []
    for dow in df_agg['曜日'].unique():
        dow_data = df_agg[df_agg['曜日'] == dow]

        result.append({
            '期間': period_name,
            '曜日': dow,
            '会計数': len(dow_data),
            '総売上': dow_data['売上'].sum(),
            '総客数': dow_data['人数'].sum(),
            '平均客単価': dow_data['客単価'].mean(),
            '客単価中央値': dow_data['客単価'].median(),
            '客単価P10': dow_data['客単価'].quantile(0.1),
            '客単価P90': dow_data['客単価'].quantile(0.9),
            '客単価最大': dow_data['客単価'].max(),
            '客単価最小': dow_data['客単価'].min(),
            '大口会計数_10K以上': len(dow_data[dow_data['売上'] >= 10000]),
            '大口会計売上_10K以上': dow_data[dow_data['売上'] >= 10000]['売上'].sum(),
        })

    return pd.DataFrame(result)

transaction_target = calc_transaction_stats(df_target_agg, '対象週')
transaction_prev = calc_transaction_stats(df_prev_agg, '前週')
transaction_comparison = pd.concat([transaction_prev, transaction_target], ignore_index=True)

# ================================================================================
# 分析4: 商品ミックス分析
# ================================================================================
print("\n[6] 商品ミックス分析...")

# 高単価商品の定義（単価1,500円以上）
HIGH_PRICE_THRESHOLD = 1500

# カテゴリ別・曜日別集計
def calc_product_mix(df_input, period_name):
    """商品ミックス分析"""
    # 曜日情報は既にdf_inputに含まれている
    df_with_dow = df_input.copy()

    # 高単価フラグ
    df_with_dow['高単価'] = df_with_dow['単価'] >= HIGH_PRICE_THRESHOLD

    result = []
    for dow in df_with_dow['曜日_日本語'].dropna().unique():
        dow_data = df_with_dow[df_with_dow['曜日_日本語'] == dow]
        total_sales = dow_data['売上'].sum()
        total_quantity = dow_data['数量'].sum()

        # カテゴリ別
        category_data = dow_data.groupby('カテゴリ1').agg({
            '売上': 'sum',
            '数量': 'sum'
        }).reset_index()

        # 高単価商品
        high_price_sales = dow_data[dow_data['高単価']]['売上'].sum()
        high_price_quantity = dow_data[dow_data['高単価']]['数量'].sum()

        result.append({
            '期間': period_name,
            '曜日': dow,
            '総売上': total_sales,
            '総数量': total_quantity,
            '高単価売上': high_price_sales,
            '高単価数量': high_price_quantity,
            '高単価売上比率': high_price_sales / total_sales * 100 if total_sales > 0 else 0,
            '高単価数量比率': high_price_quantity / total_quantity * 100 if total_quantity > 0 else 0,
            'カテゴリ数': len(category_data),
            'TOP3カテゴリ': ', '.join(category_data.nlargest(3, '売上')['カテゴリ1'].tolist()),
        })

    return pd.DataFrame(result)

product_target = calc_product_mix(df_target, '対象週')
product_prev = calc_product_mix(df_prev, '前週')
product_comparison = pd.concat([product_prev, product_target], ignore_index=True)

# ================================================================================
# 分析5: 例外データの確認
# ================================================================================
print("\n[7] 例外データ確認...")

def check_anomalies(df_input, df_agg, period_name):
    """例外データのチェック"""
    result = []

    for dow in df_agg['曜日'].unique():
        dow_data = df_agg[df_agg['曜日'] == dow]
        dow_raw = df_input[df_input['曜日_日本語'] == dow]

        # 営業時間外（18時前、26時以降）
        out_of_hours = dow_data[
            (dow_data['会計時刻'] < 18) | (dow_data['会計時刻'] >= 26)
        ]

        # tablecharge以外の特殊計上
        special_items = dow_raw[dow_raw['商品名'].str.contains('table|charge|サービス|調整', case=False, na=False)]

        # 極端な会計（客単価1万円以上または500円未満）
        extreme_bills = dow_data[
            (dow_data['客単価'] >= 10000) | (dow_data['客単価'] < 500)
        ]

        result.append({
            '期間': period_name,
            '曜日': dow,
            '営業時間外会計数': len(out_of_hours),
            '営業時間外売上': out_of_hours['売上'].sum() if len(out_of_hours) > 0 else 0,
            '特殊計上アイテム数': len(special_items),
            '特殊計上売上': special_items['売上'].sum() if len(special_items) > 0 else 0,
            '極端会計数': len(extreme_bills),
            '極端会計売上': extreme_bills['売上'].sum() if len(extreme_bills) > 0 else 0,
        })

    return pd.DataFrame(result)

anomaly_target = check_anomalies(df_target, df_target_agg, '対象週')
anomaly_prev = check_anomalies(df_prev, df_prev_agg, '前週')
anomaly_comparison = pd.concat([anomaly_prev, anomaly_target], ignore_index=True)

# ================================================================================
# 結果保存
# ================================================================================
print("\n[8] 結果保存中...")

# JSON形式で保存
output_data = {
    'meta': {
        'target_week': TARGET_WEEK,
        'target_period': f"{target_start.date()} ~ {target_end.date()}",
        'prev_period': f"{prev_start.date()} ~ {prev_end.date()}",
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    },
    'party_size_analysis': party_comparison.to_dict(orient='records'),
    'time_bucket_analysis': time_comparison.to_dict(orient='records'),
    'transaction_stats': transaction_comparison.to_dict(orient='records'),
    'product_mix_analysis': product_comparison.to_dict(orient='records'),
    'anomaly_check': anomaly_comparison.to_dict(orient='records'),
}

output_path = f"{OUTPUT_DIR}/weekday_deepdive_analysis.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"   [OK] 分析結果を保存: {output_path}")

# CSV形式でも保存
party_comparison.to_csv(f"{OUTPUT_DIR}/party_size_analysis.csv", index=False, encoding='utf-8-sig')
time_comparison.to_csv(f"{OUTPUT_DIR}/time_bucket_analysis.csv", index=False, encoding='utf-8-sig')
transaction_comparison.to_csv(f"{OUTPUT_DIR}/transaction_stats.csv", index=False, encoding='utf-8-sig')
product_comparison.to_csv(f"{OUTPUT_DIR}/product_mix_analysis.csv", index=False, encoding='utf-8-sig')
anomaly_comparison.to_csv(f"{OUTPUT_DIR}/anomaly_check.csv", index=False, encoding='utf-8-sig')

print(f"   [OK] CSV形式でも保存完了")

# ================================================================================
# サマリー出力
# ================================================================================
print("\n" + "="*80)
print("分析サマリー")
print("="*80)

print("\n【パーティサイズ分析】")
print("対象週の曜日別パーティサイズ構成:")
for dow in sorted(party_target_comp['曜日'].unique()):
    print(f"\n  {dow}曜日:")
    dow_data = party_target_comp[party_target_comp['曜日'] == dow]
    for _, row in dow_data.iterrows():
        print(f"    {row['パーティサイズ']}: 会計{row['会計数']:.0f}件 ({row['会計数構成比']:.1f}%), "
              f"売上JPY{row['売上']:,.0f} ({row['売上構成比']:.1f}%)")

print("\n【時間帯バケット分析】")
print("対象週の曜日別ピーク時間帯:")
for dow in sorted(time_target_comp['曜日'].unique()):
    dow_data = time_target_comp[time_target_comp['曜日'] == dow].sort_values('売上', ascending=False)
    if len(dow_data) > 0:
        top_time = dow_data.iloc[0]
        print(f"  {dow}曜日: {top_time['時間帯']} - 売上JPY{top_time['売上']:,.0f} ({top_time['売上構成比']:.1f}%)")

print("\n【会計レベル統計】")
for _, row in transaction_target.iterrows():
    print(f"\n  {row['曜日']}曜日:")
    print(f"    客単価中央値: JPY{row['客単価中央値']:,.0f} (平均: JPY{row['平均客単価']:,.0f})")
    print(f"    客単価分布: P10=JPY{row['客単価P10']:,.0f}, P90=JPY{row['客単価P90']:,.0f}")
    print(f"    大口会計(JPY10K以上): {row['大口会計数_10K以上']:.0f}件, 売上JPY{row['大口会計売上_10K以上']:,.0f}")

print("\n【商品ミックス】")
for _, row in product_target.iterrows():
    print(f"\n  {row['曜日']}曜日:")
    print(f"    高単価商品(JPY1,500以上): 売上比率{row['高単価売上比率']:.1f}%, 数量比率{row['高単価数量比率']:.1f}%")
    print(f"    TOP3カテゴリ: {row['TOP3カテゴリ']}")

print("\n【例外データ】")
for _, row in anomaly_target.iterrows():
    print(f"  {row['曜日']}曜日: 営業時間外{row['営業時間外会計数']:.0f}件, "
          f"特殊計上{row['特殊計上アイテム数']:.0f}件, 極端会計{row['極端会計数']:.0f}件")

print("\n" + "="*80)
print("分析完了!")
print("="*80)
