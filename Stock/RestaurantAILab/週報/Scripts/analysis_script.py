import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
import json
import sys
import argparse

# 標準出力のエンコーディングを設定
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings('ignore')

# 日本語フォントの設定（Windows環境向け改善版）
import matplotlib.font_manager as fm

def setup_japanese_font():
    """日本語フォントを確実に設定する"""
    # matplotlibのフォントキャッシュを削除して再構築
    try:
        import shutil
        cache_dir = fm.get_cachedir()
        cache_file = os.path.join(cache_dir, 'fontlist-v330.json')
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print("フォントキャッシュを削除しました")
    except Exception as e:
        print(f"キャッシュ削除エラー（無視可能）: {e}")

    # フォントマネージャーを再構築
    fm._load_fontmanager(try_read_cache=False)

    # システムフォントから日本語フォントを検索
    if sys.platform == 'win32':
        # Windowsフォントディレクトリから直接検索
        font_files = fm.findSystemFonts(fontpaths=['C:\\Windows\\Fonts'], fontext='ttf')

        # 優先度の高い日本語フォントファイル名
        priority_fonts = {
            'yugothic.ttf': 'Yu Gothic',
            'YuGothR.ttc': 'Yu Gothic',
            'YuGothM.ttc': 'Yu Gothic',
            'msgothic.ttc': 'MS Gothic',
            'meiryo.ttc': 'Meiryo',
            'BIZ-UDGothicR.ttc': 'BIZ UDGothic'
        }

        # フォントファイルを検索
        for font_path in font_files:
            font_filename = os.path.basename(font_path).lower()
            for font_file, font_name in priority_fonts.items():
                if font_file.lower() == font_filename:
                    try:
                        # フォントプロパティを取得
                        font_prop = fm.FontProperties(fname=font_path)
                        actual_name = font_prop.get_name()

                        # フォントをmatplotlibに登録
                        fm.fontManager.addfont(font_path)

                        # matplotlibの設定を更新
                        plt.rcParams['font.family'] = actual_name
                        plt.rcParams['font.sans-serif'] = [actual_name] + plt.rcParams['font.sans-serif']

                        print(f"日本語フォント設定完了: {actual_name} ({font_path})")
                        return True
                    except Exception as e:
                        print(f"フォント登録エラー: {font_file} - {e}")
                        continue

        # フォールバック：名前ベースで設定
        print("警告: フォントファイルが見つからないため、名前ベースで設定します")
        plt.rcParams['font.sans-serif'] = ['Yu Gothic', 'MS Gothic', 'Meiryo', 'MS UI Gothic'] + plt.rcParams['font.sans-serif']
        return False
    else:
        # Mac/Linux用
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo'] + plt.rcParams['font.sans-serif']
        return True

# モダンなグラフスタイルの設定（フォント設定の前に実行）
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['axes.edgecolor'] = '#dee2e6'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#dee2e6'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.8
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# フォント設定を実行（seabornの設定後に実行して上書きされないようにする）
setup_japanese_font()
plt.rcParams['axes.unicode_minus'] = False

# カラーパレット定義
COLORS = {
    'primary': '#2E86AB',      # 濃い青
    'secondary': '#A23B72',    # ワインレッド
    'success': '#06A77D',      # 緑
    'warning': '#F18F01',      # オレンジ
    'danger': '#C73E1D',       # 赤
    'info': '#6A4C93',         # 紫
    'muted': '#6C757D',        # グレー
    'gradient': ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#6A4C93'],
}

# 中間メモを保存
memo_content = []

def save_memo(title, content):
    """分析中のメモを保存"""
    memo_content.append(f"\n## {title}\n{content}\n")
    print(f"\n[メモ] {title}")
    print(content)

# ==========================================
# コマンドライン引数のパース
# ==========================================
parser = argparse.ArgumentParser(description='飲食店データ分析スクリプト - 週報作成基礎資料')
parser.add_argument('-w', '--week', type=str, required=True,
                    help='対象週 (例: 2025-W42)')
parser.add_argument('-e', '--end-date', type=str, required=True,
                    help='対象週の終了日 (例: 2025-10-24)')
parser.add_argument('-o', '--output-dir', type=str, default=None,
                    help='出力ディレクトリ (デフォルト: Stock/RestaurantAILab/週報/2_output_{week})')
parser.add_argument('--sales-data', type=str,
                    default=r'Stock\RestaurantAILab\週報\1_input\rawdata.csv',
                    help='売上データのパス')
parser.add_argument('--reviews-data', type=str,
                    default=r'Stock\RestaurantAILab\週報\1_input\reviews.csv',
                    help='口コミデータのパス')
parser.add_argument('--images', action='store_true',
                    help='グラフ画像を出力する（デフォルト: 出力しない）')

args = parser.parse_args()

# パラメータの設定
target_week = args.week
target_date_end = pd.to_datetime(args.end_date).date()
target_date_start = target_date_end - timedelta(days=6)

# 出力ディレクトリの設定
if args.output_dir:
    output_dir = args.output_dir
else:
    week_suffix = target_week.lower().replace('-', '')  # 2025-W42 → 2025w42
    output_dir = f'Stock\\RestaurantAILab\\週報\\2_output_{week_suffix}'

# ==========================================
# データ読み込み
# ==========================================
print("=" * 80)
print(f"飲食店データ分析スクリプト - 週報作成基礎資料（{target_week}）")
print("=" * 80)
save_memo("データ読み込み", "売上データと口コミデータを読み込んでいます...")

sales_df = pd.read_csv(args.sales_data)
reviews_df = pd.read_csv(args.reviews_data, encoding='utf-8-sig')

# ==========================================
# UTC → JST 変換と営業日定義
# ==========================================
# 日付型への変換（UTC）
sales_df['entry_at'] = pd.to_datetime(sales_df['entry_at'], utc=True)
sales_df['exit_at'] = pd.to_datetime(sales_df['exit_at'], utc=True)
if 'ordered_at' in sales_df.columns:
    sales_df['ordered_at'] = pd.to_datetime(sales_df['ordered_at'], utc=True, errors='coerce')

# UTC → JST 変換（+9時間）
sales_df['entry_at_jst'] = sales_df['entry_at'].dt.tz_convert('Asia/Tokyo')
sales_df['exit_at_jst'] = sales_df['exit_at'].dt.tz_convert('Asia/Tokyo')
if 'ordered_at' in sales_df.columns and sales_df['ordered_at'].notna().any():
    sales_df['ordered_at_jst'] = sales_df['ordered_at'].dt.tz_convert('Asia/Tokyo')

# 営業日(business_date)の定義
# 営業時間が18:00〜26:00(翌2:00)前後のため、
# JST 00:00〜05:59 の会計 → 前日の営業日に付け替え
# JST 06:00〜23:59 の会計 → 当日の営業日
def get_business_date(dt):
    """JSTの日時から営業日を計算"""
    if pd.isna(dt):
        return None
    hour = dt.hour
    if 0 <= hour < 6:
        # 深夜帯（0-5時）は前日の営業日
        return (dt - pd.Timedelta(days=1)).date()
    else:
        # 6時以降は当日の営業日
        return dt.date()

sales_df['business_date'] = sales_df['entry_at_jst'].apply(get_business_date)

# business_hour（深夜帯を24時以降で表現）
def get_business_hour(dt):
    """JSTの日時から営業時間を計算（0時→24、1時→25...）"""
    if pd.isna(dt):
        return None
    hour = dt.hour
    if 0 <= hour < 6:
        # 深夜帯は24時以降として表現
        return hour + 24
    else:
        return hour

sales_df['business_hour'] = sales_df['entry_at_jst'].apply(get_business_hour)

# 時間帯バケット（営業時間に合わせた区分）
def get_hour_bucket(hour):
    """営業時間に基づいた時間帯バケット"""
    if pd.isna(hour):
        return 'other'
    if 18 <= hour < 20:
        return '18-19'
    elif 20 <= hour < 22:
        return '20-21'
    elif 22 <= hour < 24:
        return '22-23'
    elif 24 <= hour < 26:
        return '24-25+'
    else:
        return 'other'

sales_df['hour_bucket'] = sales_df['business_hour'].apply(get_hour_bucket)

# 営業日基準での日付、週、月の情報を追加
sales_df['business_date_dt'] = pd.to_datetime(sales_df['business_date'])
sales_df['year'] = sales_df['business_date_dt'].dt.year
sales_df['month'] = sales_df['business_date_dt'].dt.month
sales_df['week'] = sales_df['business_date_dt'].dt.isocalendar().week
sales_df['year_week'] = sales_df['business_date_dt'].dt.strftime('%G-W%V')

# 曜日は営業日基準で再計算
weekday_map = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
sales_df['weekday'] = sales_df['business_date_dt'].dt.dayofweek.map(weekday_map)

# 後方互換性のため、dateカラムも営業日に合わせる
sales_df['date'] = sales_df['business_date']

# 口コミデータの日付処理
reviews_df['投稿日'] = pd.to_datetime(reviews_df['投稿日'], format='%y/%m/%d', errors='coerce')

# 対象週のデータをフィルタリング（営業日基準）
sales_df_filtered = sales_df[(sales_df['date'] >= target_date_start) &
                               (sales_df['date'] <= target_date_end)]

# 営業時間外データの確認
営業時間外 = sales_df[sales_df['hour_bucket'] == 'other']

memo_text = f"""
- 売上データ期間（営業日基準）: {sales_df['date'].min()} ～ {sales_df['date'].max()}
- 売上データ件数: {len(sales_df):,} レコード
- 口コミデータ件数: {len(reviews_df):,} 件
- **対象週: {target_week} ({target_date_start} ～ {target_date_end})**
- 対象週のレコード数: {len(sales_df_filtered):,} レコード
- 店舗: {sales_df['store_name'].iloc[0]}

【時刻・営業日の扱い】
- UTC → JST 変換: すべての時刻を+9時間でJSTに変換済み
- 営業日定義: JST 0-5時の会計は前日の営業日に付け替え
- 営業時間帯: 主に18-25時（深夜は24時以降表記）
- 営業時間外レコード: {len(営業時間外):,} 件 ({len(営業時間外)/len(sales_df)*100:.1f}%)
"""
save_memo("データ概要", memo_text)

# 出力ディレクトリの作成
os.makedirs(output_dir, exist_ok=True)
print(f"\n出力ディレクトリ: {output_dir}")

# ==========================================
# 1. 売上分析
# ==========================================
save_memo("売上分析", """
【目的】対象週の売上傾向を把握し、前週・前月・前年と比較して業績の変化を理解する
【仮説】
- 曜日や時間帯によって売上パターンがあり、ピークタイムを特定できる
- 客単価と客数の変動が売上に大きく影響している
- 前週・前月・前年比較により、季節要因や成長トレンドを把握できる
""")

# 会計単位でのデータ集計（重複除去）
# business_dateとbusiness_hourを使用
account_df = sales_df.groupby(['account_id', 'business_date', 'year_week', 'weekday', 'business_hour', 'hour_bucket']).agg({
    'account_total': 'first',
    'customer_count': 'first'
}).reset_index()

# 後方互換性のため、dateカラムも追加
account_df['date'] = account_df['business_date']

save_memo("データ処理", f"会計単位で集計: {len(account_df):,} 件の会計データ")

# 週次売上集計
weekly_sales = account_df.groupby('year_week').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={
    'account_total': '売上',
    'customer_count': '客数',
    'account_id': '組数'
})
weekly_sales['客単価'] = weekly_sales['売上'] / weekly_sales['客数']
weekly_sales = weekly_sales.sort_index()

# 対象週のデータ取得
latest_week = target_week
latest_week_data = weekly_sales.loc[latest_week] if latest_week in weekly_sales.index else None

if latest_week_data is None:
    print(f"\n警告: {target_week} のデータが見つかりません")
    print("利用可能な週:", weekly_sales.index.tolist())
    sys.exit(1)

# 前週・前月・前年のデータ取得
week_list = sorted(weekly_sales.index.tolist())
latest_week_idx = week_list.index(latest_week) if latest_week in week_list else -1

prev_week = week_list[latest_week_idx - 1] if latest_week_idx > 0 else None
prev_week_data = weekly_sales.loc[prev_week] if prev_week else None

# 直近5週間のリスト（スライドデータ・グラフ用）
recent_start = max(0, latest_week_idx - 4)
recent_week_list = week_list[recent_start:latest_week_idx + 1]

# 前月平均の計算：対象週の開始日から1ヶ月前の月に該当する週の平均
try:
    from datetime import datetime
    # 対象週の開始日を取得
    target_start_date = datetime.strptime(f"{latest_week}-1", "%Y-W%W-%w")
    # 1ヶ月前の月を計算
    prev_month_date = pd.Timestamp(target_start_date) - pd.DateOffset(months=1)
    prev_month_year_month = prev_month_date.strftime('%Y-%m')

    # 前月に該当する週を抽出（営業日基準で前月の月に含まれる週）
    prev_month_weeks = []
    for week in week_list:
        week_start = datetime.strptime(f"{week}-1", "%Y-W%W-%w")
        if week_start.strftime('%Y-%m') == prev_month_year_month:
            prev_month_weeks.append(week)

    # 前月の週の平均を計算
    if prev_month_weeks:
        prev_month_avg = weekly_sales.loc[prev_month_weeks].mean()
        prev_month_data = prev_month_avg
        prev_month_label = f"{prev_month_year_month}月平均"
        # カテゴリ・商品分析用に前月の最終週を保持
        prev_month_week = prev_month_weeks[-1]
    else:
        prev_month_data = None
        prev_month_label = None
        prev_month_week = None
except Exception as e:
    print(f"前月計算エラー: {e}")
    prev_month_data = None
    prev_month_label = None
    prev_month_week = None

# 前年同週の計算
try:
    latest_year = int(latest_week.split('-W')[0])
    latest_week_num = int(latest_week.split('-W')[1])
    prev_year_week = f"{latest_year - 1}-W{latest_week_num:02d}"
    prev_year_data = weekly_sales.loc[prev_year_week] if prev_year_week in weekly_sales.index else None
except:
    prev_year_data = None

# 比較結果のメモ
comparison_memo = f"""
### 対象週 ({latest_week})
- 売上: ¥{latest_week_data['売上']:,.0f}
- 客数: {latest_week_data['客数']:.0f}人
- 組数: {latest_week_data['組数']:.0f}組
- 客単価: ¥{latest_week_data['客単価']:,.0f}
"""

if prev_week_data is not None:
    sales_change = ((latest_week_data['売上'] - prev_week_data['売上']) / prev_week_data['売上'] * 100)
    customer_change = ((latest_week_data['客数'] - prev_week_data['客数']) / prev_week_data['客数'] * 100)
    unit_price_change = ((latest_week_data['客単価'] - prev_week_data['客単価']) / prev_week_data['客単価'] * 100)

    comparison_memo += f"""
### 前週比 ({prev_week})
- 売上: {sales_change:+.1f}% (¥{prev_week_data['売上']:,.0f} → ¥{latest_week_data['売上']:,.0f})
- 客数: {customer_change:+.1f}% ({prev_week_data['客数']:.0f}人 → {latest_week_data['客数']:.0f}人)
- 客単価: {unit_price_change:+.1f}% (¥{prev_week_data['客単価']:,.0f} → ¥{latest_week_data['客単価']:,.0f})
"""

if prev_month_data is not None:
    sales_change_m = ((latest_week_data['売上'] - prev_month_data['売上']) / prev_month_data['売上'] * 100)
    customer_change_m = ((latest_week_data['客数'] - prev_month_data['客数']) / prev_month_data['客数'] * 100)

    comparison_memo += f"""
### 前月平均比 ({prev_month_label})
- 売上: {sales_change_m:+.1f}%
- 客数: {customer_change_m:+.1f}%
"""

if prev_year_data is not None:
    sales_change_y = ((latest_week_data['売上'] - prev_year_data['売上']) / prev_year_data['売上'] * 100)
    customer_change_y = ((latest_week_data['客数'] - prev_year_data['客数']) / prev_year_data['客数'] * 100)

    comparison_memo += f"""
### 前年同週比 ({prev_year_week})
- 売上: {sales_change_y:+.1f}%
- 客数: {customer_change_y:+.1f}%
"""

save_memo("週次売上比較", comparison_memo)

# ==========================================
# スライド用データ出力（テキスト形式）
# ==========================================

# 第1部用：直近5週間トレンドデータ
slide_data_part1 = []
slide_data_part1.append("=" * 60)
slide_data_part1.append("【スライド第1部用】週次トレンドデータ（直近5週間）")
slide_data_part1.append("=" * 60)
slide_data_part1.append("")

# 直近5週間のデータテーブル
slide_data_part1.append("## 直近5週間の推移データ（グラフ用）")
slide_data_part1.append("")
slide_data_part1.append("| 週 | 売上 | 客数 | 客単価 | 組数 |")
slide_data_part1.append("|---|---|---|---|---|")
for week in recent_week_list:
    w_data = weekly_sales.loc[week]
    slide_data_part1.append(f"| {week} | ¥{w_data['売上']:,.0f} | {w_data['客数']:.0f}人 | ¥{w_data['客単価']:,.0f} | {w_data['組数']:.0f}組 |")
slide_data_part1.append("")

# 前年同週比較データ
slide_data_part1.append("## 前年同週比較データ")
slide_data_part1.append("")
if prev_year_data is not None:
    slide_data_part1.append(f"| 指標 | 今週 ({latest_week}) | 前年同週 ({prev_year_week}) | 成長率 |")
    slide_data_part1.append("|---|---|---|---|")
    slide_data_part1.append(f"| 売上 | ¥{latest_week_data['売上']:,.0f} | ¥{prev_year_data['売上']:,.0f} | {(latest_week_data['売上']/prev_year_data['売上']-1)*100:+.1f}% |")
    slide_data_part1.append(f"| 客数 | {latest_week_data['客数']:.0f}人 | {prev_year_data['客数']:.0f}人 | {(latest_week_data['客数']/prev_year_data['客数']-1)*100:+.1f}% |")
    slide_data_part1.append(f"| 客単価 | ¥{latest_week_data['客単価']:,.0f} | ¥{prev_year_data['客単価']:,.0f} | {(latest_week_data['客単価']/prev_year_data['客単価']-1)*100:+.1f}% |")
else:
    slide_data_part1.append("前年同週データなし")
slide_data_part1.append("")

# エグゼクティブサマリー用KPI
slide_data_part1.append("## エグゼクティブサマリー用KPI")
slide_data_part1.append("")
slide_data_part1.append(f"| 指標 | 実績 | 前週比 | 前年比 |")
slide_data_part1.append("|---|---|---|---|")

prev_week_sales_change = f"{(latest_week_data['売上']/prev_week_data['売上']-1)*100:+.1f}%" if prev_week_data is not None else "N/A"
prev_week_cust_change = f"{(latest_week_data['客数']/prev_week_data['客数']-1)*100:+.1f}%" if prev_week_data is not None else "N/A"
prev_week_unit_change = f"{(latest_week_data['客単価']/prev_week_data['客単価']-1)*100:+.1f}%" if prev_week_data is not None else "N/A"

prev_year_sales_change = f"{(latest_week_data['売上']/prev_year_data['売上']-1)*100:+.1f}%" if prev_year_data is not None else "N/A"
prev_year_cust_change = f"{(latest_week_data['客数']/prev_year_data['客数']-1)*100:+.1f}%" if prev_year_data is not None else "N/A"
prev_year_unit_change = f"{(latest_week_data['客単価']/prev_year_data['客単価']-1)*100:+.1f}%" if prev_year_data is not None else "N/A"

slide_data_part1.append(f"| 売上 | ¥{latest_week_data['売上']:,.0f} | {prev_week_sales_change} | {prev_year_sales_change} |")
slide_data_part1.append(f"| 客数 | {latest_week_data['客数']:.0f}人 | {prev_week_cust_change} | {prev_year_cust_change} |")
slide_data_part1.append(f"| 客単価 | ¥{latest_week_data['客単価']:,.0f} | {prev_week_unit_change} | {prev_year_unit_change} |")
slide_data_part1.append("")

# ファイル出力
with open(os.path.join(output_dir, 'slide_data_part1.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(slide_data_part1))

print("\n[出力] slide_data_part1.txt - 第1部用トレンドデータ")

# グラフ作成：週次売上比較（棒グラフ）- モダンデザイン
if args.images and prev_week_data is not None:
    fig, axes = plt.subplots(2, 2, figsize=(17, 11), facecolor='white')
    fig.suptitle('週次指標比較分析', fontsize=18, fontweight='bold', y=0.995, color='#2c3e50')

    # 売上比較
    weeks_labels = []
    sales_values = []
    colors_sales = []

    if prev_year_data is not None:
        weeks_labels.append(f'{prev_year_week}\n(前年)')
        sales_values.append(prev_year_data['売上'])
        colors_sales.append(COLORS['muted'])

    if prev_month_data is not None:
        weeks_labels.append(f'{prev_month_label}\n(前月平均)')
        sales_values.append(prev_month_data['売上'])
        colors_sales.append(COLORS['info'])

    weeks_labels.append(f'{prev_week}\n(前週)')
    sales_values.append(prev_week_data['売上'])
    colors_sales.append(COLORS['primary'])

    weeks_labels.append(f'{latest_week}\n(対象週)')
    sales_values.append(latest_week_data['売上'])
    colors_sales.append(COLORS['warning'])

    bars1 = axes[0, 0].bar(weeks_labels, sales_values, color=colors_sales,
                          edgecolor='white', linewidth=2.5, alpha=0.9, width=0.7)
    axes[0, 0].set_title('売上比較', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[0, 0].set_ylabel('売上 (円)', fontsize=11, fontweight='600')
    axes[0, 0].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)
    axes[0, 0].set_facecolor('#f8f9fa')

    # 各棒の上に金額を表示
    for bar in bars1:
        height = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width()/2., height,
                       f'¥{height:,.0f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                edgecolor='#dee2e6', alpha=0.8, linewidth=1.5))

    # 客数比較
    customer_values = []
    if prev_year_data is not None:
        customer_values.append(prev_year_data['客数'])
    if prev_month_data is not None:
        customer_values.append(prev_month_data['客数'])
    customer_values.append(prev_week_data['客数'])
    customer_values.append(latest_week_data['客数'])

    bars2 = axes[0, 1].bar(weeks_labels, customer_values, color=colors_sales,
                          edgecolor='white', linewidth=2.5, alpha=0.9, width=0.7)
    axes[0, 1].set_title('客数比較', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[0, 1].set_ylabel('客数 (人)', fontsize=11, fontweight='600')
    axes[0, 1].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)
    axes[0, 1].set_facecolor('#f8f9fa')

    for bar in bars2:
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}人',
                       ha='center', va='bottom', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                edgecolor='#dee2e6', alpha=0.8, linewidth=1.5))

    # 客単価比較
    unit_price_values = []
    if prev_year_data is not None:
        unit_price_values.append(prev_year_data['客単価'])
    if prev_month_data is not None:
        unit_price_values.append(prev_month_data['客単価'])
    unit_price_values.append(prev_week_data['客単価'])
    unit_price_values.append(latest_week_data['客単価'])

    bars3 = axes[1, 0].bar(weeks_labels, unit_price_values, color=colors_sales,
                          edgecolor='white', linewidth=2.5, alpha=0.9, width=0.7)
    axes[1, 0].set_title('客単価比較', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[1, 0].set_ylabel('客単価 (円)', fontsize=11, fontweight='600')
    axes[1, 0].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)
    axes[1, 0].set_facecolor('#f8f9fa')

    for bar in bars3:
        height = bar.get_height()
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                       f'¥{height:,.0f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                edgecolor='#dee2e6', alpha=0.8, linewidth=1.5))

    # 組数比較
    group_values = []
    if prev_year_data is not None:
        group_values.append(prev_year_data['組数'])
    if prev_month_data is not None:
        group_values.append(prev_month_data['組数'])
    group_values.append(prev_week_data['組数'])
    group_values.append(latest_week_data['組数'])

    bars4 = axes[1, 1].bar(weeks_labels, group_values, color=colors_sales,
                          edgecolor='white', linewidth=2.5, alpha=0.9, width=0.7)
    axes[1, 1].set_title('組数比較', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[1, 1].set_ylabel('組数', fontsize=11, fontweight='600')
    axes[1, 1].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)
    axes[1, 1].set_facecolor('#f8f9fa')

    for bar in bars4:
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}組',
                       ha='center', va='bottom', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                edgecolor='#dee2e6', alpha=0.8, linewidth=1.5))

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(os.path.join(output_dir, 'weekly_sales_comparison.png'), dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    save_memo("グラフ保存", "週次売上比較グラフ（棒グラフ）を保存しました")

# グラフ作成：週次売上推移（折れ線グラフ）- 過去1ヶ月（直近5週間）
if args.images:
    weekly_sales_recent = weekly_sales.loc[recent_week_list]

    fig, axes = plt.subplots(2, 2, figsize=(17, 11), facecolor='white')
    fig.suptitle('週次推移トレンド分析（直近5週間）', fontsize=18, fontweight='bold', y=0.995, color='#2c3e50')

    # 売上推移
    weekly_sales_recent['売上'].plot(ax=axes[0, 0], marker='o', linewidth=3, markersize=10,
                                    color=COLORS['primary'], markerfacecolor=COLORS['warning'],
                                    markeredgecolor='white', markeredgewidth=2)
    axes[0, 0].set_title('売上推移', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[0, 0].set_ylabel('売上 (円)', fontsize=11, fontweight='600')
    axes[0, 0].grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    axes[0, 0].tick_params(axis='x', rotation=15, labelsize=9)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)
    axes[0, 0].set_facecolor('#f8f9fa')
    axes[0, 0].fill_between(range(len(weekly_sales_recent)), weekly_sales_recent['売上'],
                            alpha=0.2, color=COLORS['primary'])

    # 客数推移
    weekly_sales_recent['客数'].plot(ax=axes[0, 1], marker='o', linewidth=3, markersize=10,
                                    color=COLORS['success'], markerfacecolor=COLORS['warning'],
                                    markeredgecolor='white', markeredgewidth=2)
    axes[0, 1].set_title('客数推移', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[0, 1].set_ylabel('客数 (人)', fontsize=11, fontweight='600')
    axes[0, 1].grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    axes[0, 1].tick_params(axis='x', rotation=15, labelsize=9)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)
    axes[0, 1].set_facecolor('#f8f9fa')
    axes[0, 1].fill_between(range(len(weekly_sales_recent)), weekly_sales_recent['客数'],
                            alpha=0.2, color=COLORS['success'])

    # 客単価推移
    weekly_sales_recent['客単価'].plot(ax=axes[1, 0], marker='o', linewidth=3, markersize=10,
                                      color=COLORS['warning'], markerfacecolor=COLORS['danger'],
                                      markeredgecolor='white', markeredgewidth=2)
    axes[1, 0].set_title('客単価推移', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[1, 0].set_ylabel('客単価 (円)', fontsize=11, fontweight='600')
    axes[1, 0].grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    axes[1, 0].tick_params(axis='x', rotation=15, labelsize=9)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)
    axes[1, 0].set_facecolor('#f8f9fa')
    axes[1, 0].fill_between(range(len(weekly_sales_recent)), weekly_sales_recent['客単価'],
                            alpha=0.2, color=COLORS['warning'])

    # 組数推移
    weekly_sales_recent['組数'].plot(ax=axes[1, 1], marker='o', linewidth=3, markersize=10,
                                    color=COLORS['info'], markerfacecolor=COLORS['warning'],
                                    markeredgecolor='white', markeredgewidth=2)
    axes[1, 1].set_title('組数推移', fontsize=13, fontweight='bold', pad=12, color='#34495e')
    axes[1, 1].set_ylabel('組数', fontsize=11, fontweight='600')
    axes[1, 1].grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    axes[1, 1].tick_params(axis='x', rotation=15, labelsize=9)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)
    axes[1, 1].set_facecolor('#f8f9fa')
    axes[1, 1].fill_between(range(len(weekly_sales_recent)), weekly_sales_recent['組数'],
                            alpha=0.2, color=COLORS['info'])

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(os.path.join(output_dir, 'weekly_sales_trend.png'), dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    save_memo("グラフ保存", f"週次売上推移グラフ（直近5週間）を保存しました")

# ==========================================
# 曜日別売上分析（詳細版：要因分解付き）
# ==========================================
save_memo("曜日別売上分析（要因分解）", """
【目的】曜日別に売上変化を「客数要因」と「客単価要因」に分解し、どの曜日が何によって変化したかを明らかにする
【手法】ミッドポイント法による要因分解
【比較対象】過去4週間の移動平均
""")

# 対象週と過去4週間の曜日別KPI作成
weekday_order = ['月', '火', '水', '木', '金', '土', '日']

# 対象週の曜日別データ
target_week_account = account_df[account_df['year_week'] == latest_week]
weekday_current = target_week_account.groupby('weekday').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
}).rename(columns={
    'account_total': '売上',
    'customer_count': '客数',
    'account_id': '組数'
})
weekday_current['1人単価'] = weekday_current['売上'] / weekday_current['客数']

# 過去4週間の移動平均（対象週を含まない直前の4週間）
# 対象週のインデックス位置を取得
if latest_week_idx >= 4:
    # 過去4週間のリストを取得（対象週の直前4週間）
    ma_weeks = week_list[latest_week_idx - 4:latest_week_idx]

    # 過去4週間の各週の曜日別データを取得
    ma_weeks_data = []
    for week in ma_weeks:
        week_account = account_df[account_df['year_week'] == week]
        weekday_week = week_account.groupby('weekday').agg({
            'account_total': 'sum',
            'customer_count': 'sum',
            'account_id': 'count'
        }).rename(columns={
            'account_total': '売上',
            'customer_count': '客数',
            'account_id': '組数'
        })
        weekday_week['1人単価'] = weekday_week['売上'] / weekday_week['客数']
        ma_weeks_data.append(weekday_week)

    # 過去4週間の平均を計算（曜日ごと）
    weekday_ma4 = pd.concat(ma_weeks_data).groupby(level=0).mean()
    ma_label = f"過去4週間平均 ({ma_weeks[0]}～{ma_weeks[-1]})"
else:
    # データが4週間未満の場合は、利用可能な全週の平均を使用
    if latest_week_idx > 0:
        ma_weeks = week_list[:latest_week_idx]
        ma_weeks_data = []
        for week in ma_weeks:
            week_account = account_df[account_df['year_week'] == week]
            weekday_week = week_account.groupby('weekday').agg({
                'account_total': 'sum',
                'customer_count': 'sum',
                'account_id': 'count'
            }).rename(columns={
                'account_total': '売上',
                'customer_count': '客数',
                'account_id': '組数'
            })
            weekday_week['1人単価'] = weekday_week['売上'] / weekday_week['客数']
            ma_weeks_data.append(weekday_week)

        weekday_ma4 = pd.concat(ma_weeks_data).groupby(level=0).mean()
        ma_label = f"過去{len(ma_weeks)}週間平均 ({ma_weeks[0]}～{ma_weeks[-1]})"
    else:
        weekday_ma4 = pd.DataFrame()
        ma_label = None

# 曜日別要因分解（ミッドポイント法）
if not weekday_ma4.empty:
    weekday_decomposition = []

    for day in weekday_order:
        if day in weekday_current.index and day in weekday_ma4.index:
            # 対象週・過去4週間平均のデータ
            S1 = weekday_current.loc[day, '売上']
            P1 = weekday_current.loc[day, '客数']
            A1 = weekday_current.loc[day, '1人単価']

            S0 = weekday_ma4.loc[day, '売上']
            P0 = weekday_ma4.loc[day, '客数']
            A0 = weekday_ma4.loc[day, '1人単価']

            # 売上差
            delta_S = S1 - S0

            # ミッドポイント法による要因分解
            if P0 > 0 and P1 > 0:
                contrib_P = (P1 - P0) * (A1 + A0) / 2  # 客数要因
                contrib_A = (A1 - A0) * (P1 + P0) / 2  # 客単価要因
            else:
                # P=0の例外処理：差分はすべて客数要因に寄せる
                contrib_P = delta_S
                contrib_A = 0

            weekday_decomposition.append({
                '曜日': day,
                '対象週売上': S1,
                '過去4週平均売上': S0,
                '売上差': delta_S,
                '対象週客数': P1,
                '過去4週平均客数': P0,
                '客数差': P1 - P0,
                '対象週1人単価': A1,
                '過去4週平均1人単価': A0,
                '1人単価差': A1 - A0,
                '客数要因寄与': contrib_P,
                '客単価要因寄与': contrib_A,
                '検算': contrib_P + contrib_A
            })
        elif day in weekday_current.index:
            # 過去4週間にデータが無い場合
            S1 = weekday_current.loc[day, '売上']
            P1 = weekday_current.loc[day, '客数']
            A1 = weekday_current.loc[day, '1人単価']

            weekday_decomposition.append({
                '曜日': day,
                '対象週売上': S1,
                '過去4週平均売上': 0,
                '売上差': S1,
                '対象週客数': P1,
                '過去4週平均客数': 0,
                '客数差': P1,
                '対象週1人単価': A1,
                '過去4週平均1人単価': 0,
                '1人単価差': A1,
                '客数要因寄与': S1,
                '客単価要因寄与': 0,
                '検算': S1
            })

    weekday_decomp_df = pd.DataFrame(weekday_decomposition)

    # メモ作成
    weekday_decomp_memo = f"### 曜日別売上の要因分解 ({latest_week} vs {ma_label})\n\n"

    for _, row in weekday_decomp_df.iterrows():
        day = row['曜日']
        delta_S = row['売上差']
        contrib_P = row['客数要因寄与']
        contrib_A = row['客単価要因寄与']

        weekday_decomp_memo += f"**{day}曜日**\n"
        weekday_decomp_memo += f"- 売上差: ¥{delta_S:,.0f}\n"
        weekday_decomp_memo += f"  - 客数要因: ¥{contrib_P:,.0f} (客数 {row['過去4週平均客数']:.1f}人 → {row['対象週客数']:.0f}人)\n"
        weekday_decomp_memo += f"  - 客単価要因: ¥{contrib_A:,.0f} (単価 ¥{row['過去4週平均1人単価']:,.0f} → ¥{row['対象週1人単価']:,.0f})\n\n"

    # 最大プラス・マイナスの抽出
    max_plus_covers = weekday_decomp_df.loc[weekday_decomp_df['客数要因寄与'].idxmax()]
    max_minus_covers = weekday_decomp_df.loc[weekday_decomp_df['客数要因寄与'].idxmin()]
    max_plus_unit = weekday_decomp_df.loc[weekday_decomp_df['客単価要因寄与'].idxmax()]
    max_minus_unit = weekday_decomp_df.loc[weekday_decomp_df['客単価要因寄与'].idxmin()]

    weekday_decomp_memo += f"""
### 深掘り対象曜日
- 客数要因 最大プラス: **{max_plus_covers['曜日']}曜日** (¥{max_plus_covers['客数要因寄与']:,.0f})
- 客数要因 最大マイナス: **{max_minus_covers['曜日']}曜日** (¥{max_minus_covers['客数要因寄与']:,.0f})
- 客単価要因 最大プラス: **{max_plus_unit['曜日']}曜日** (¥{max_plus_unit['客単価要因寄与']:,.0f})
- 客単価要因 最大マイナス: **{max_minus_unit['曜日']}曜日** (¥{max_minus_unit['客単価要因寄与']:,.0f})
"""

    save_memo("曜日別要因分解", weekday_decomp_memo)

    # ==========================================
    # 第2部用：曜日別概況データ出力（スライド用テキスト）
    # ==========================================
    slide_data_part2 = []
    slide_data_part2.append("=" * 60)
    slide_data_part2.append("【スライド第2部用】曜日別詳細分析データ")
    slide_data_part2.append("=" * 60)
    slide_data_part2.append("")

    # 曜日別概況テーブル（スライド7用）
    slide_data_part2.append("## スライド7: 曜日別概況（グラフ用データ）")
    slide_data_part2.append("")
    slide_data_part2.append("| 曜日 | 対象週売上 | 4週平均 | 差額 | 客数要因 | 客単価要因 |")
    slide_data_part2.append("|---|---|---|---|---|---|")
    for _, row in weekday_decomp_df.iterrows():
        slide_data_part2.append(f"| {row['曜日']} | ¥{row['対象週売上']:,.0f} | ¥{row['過去4週平均売上']:,.0f} | ¥{row['売上差']:,.0f} | ¥{row['客数要因寄与']:,.0f} | ¥{row['客単価要因寄与']:,.0f} |")
    slide_data_part2.append("")

    # 好調/不調曜日の特定
    best_day_row = weekday_decomp_df.loc[weekday_decomp_df['売上差'].idxmax()]
    worst_day_row = weekday_decomp_df.loc[weekday_decomp_df['売上差'].idxmin()]

    slide_data_part2.append("## 深掘り対象曜日")
    slide_data_part2.append(f"- 好調曜日: {best_day_row['曜日']}曜日 (売上差: ¥{best_day_row['売上差']:,.0f})")
    slide_data_part2.append(f"- 不調曜日: {worst_day_row['曜日']}曜日 (売上差: ¥{worst_day_row['売上差']:,.0f})")
    slide_data_part2.append("")

    # 好調/不調曜日の基本数字（スライド8, 13用）
    for label, day_row in [("不調", worst_day_row), ("好調", best_day_row)]:
        slide_data_part2.append(f"## {label}曜日（{day_row['曜日']}）基本数字（スライド用）")
        slide_data_part2.append("")
        slide_data_part2.append("| 指標 | 対象週 | 4週平均 | 達成率 |")
        slide_data_part2.append("|---|---|---|---|")
        sales_rate = (day_row['対象週売上'] / day_row['過去4週平均売上'] * 100) if day_row['過去4週平均売上'] > 0 else 0
        cust_rate = (day_row['対象週客数'] / day_row['過去4週平均客数'] * 100) if day_row['過去4週平均客数'] > 0 else 0
        unit_rate = (day_row['対象週1人単価'] / day_row['過去4週平均1人単価'] * 100) if day_row['過去4週平均1人単価'] > 0 else 0
        slide_data_part2.append(f"| 売上 | ¥{day_row['対象週売上']:,.0f} | ¥{day_row['過去4週平均売上']:,.0f} | {sales_rate:.1f}% |")
        slide_data_part2.append(f"| 客数 | {day_row['対象週客数']:.0f}人 | {day_row['過去4週平均客数']:.1f}人 | {cust_rate:.1f}% |")
        slide_data_part2.append(f"| 客単価 | ¥{day_row['対象週1人単価']:,.0f} | ¥{day_row['過去4週平均1人単価']:,.0f} | {unit_rate:.1f}% |")
        slide_data_part2.append("")

    # ファイル出力
    with open(os.path.join(output_dir, 'slide_data_part2.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(slide_data_part2))

    print("\n[出力] slide_data_part2.txt - 第2部用曜日別データ")

    # グラフ作成：要因分解の可視化（要因分解のみ）- モダンデザイン
    if args.images:
        fig, ax = plt.subplots(figsize=(15, 7), facecolor='white')

        # 客数要因と客単価要因の寄与
        x = np.arange(len(weekday_decomp_df))
        width = 0.38

        bars1 = ax.bar(x - width/2, weekday_decomp_df['客数要因寄与'], width,
                       label='客数要因', color=COLORS['primary'],
                       edgecolor='white', linewidth=2, alpha=0.9)
        bars2 = ax.bar(x + width/2, weekday_decomp_df['客単価要因寄与'], width,
                       label='客単価要因', color=COLORS['warning'],
                       edgecolor='white', linewidth=2, alpha=0.9)

        # 値ラベルの追加
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if abs(height) > 1000:  # 小さい値は表示しない
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'¥{height:,.0f}',
                           ha='center', va='bottom' if height > 0 else 'top',
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                    edgecolor='#dee2e6', alpha=0.7, linewidth=1))

        ax.set_xlabel('曜日', fontsize=12, fontweight='600')
        ax.set_ylabel('寄与額 (円)', fontsize=12, fontweight='600')
        ax.set_title(f'曜日別売上差の要因分解 ({latest_week} vs {ma_label})',
                     fontsize=15, fontweight='bold', pad=15, color='#2c3e50')
        ax.set_xticks(x)
        ax.set_xticklabels(weekday_decomp_df['曜日'], fontsize=11, fontweight='bold')
        ax.axhline(y=0, color='#34495e', linestyle='-', linewidth=1.5, alpha=0.7)
        ax.legend(loc='upper left', fontsize=11, frameon=True, fancybox=True, shadow=True)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor('#f8f9fa')

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'weekday_decomposition.png'), dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()

        save_memo("グラフ保存", "曜日別要因分解グラフを保存しました（過去4週間平均との比較）")

    # CSV保存
    weekday_decomp_df.to_csv(os.path.join(output_dir, 'weekday_decomposition.csv'),
                             encoding='utf-8-sig', index=False)
else:
    weekday_decomp_df = pd.DataFrame()
    save_memo("曜日別要因分解", "過去4週間のデータが無いため、要因分解をスキップしました")

# 対象週の曜日別売上メモ（グラフは不要）
if not weekday_current.empty:
    # 曜日順にソート
    weekday_current_ordered = weekday_current.reindex([w for w in weekday_order if w in weekday_current.index])

    weekday_memo = f"### 対象週 ({latest_week}) の曜日別売上\n"
    for day in weekday_current_ordered.index:
        data = weekday_current_ordered.loc[day]
        weekday_memo += f"- {day}曜日: 売上 ¥{data['売上']:,.0f}, 客数 {data['客数']:.0f}人, 客単価 ¥{data['1人単価']:,.0f}\n"

    save_memo("曜日別分析（対象週）", weekday_memo)

# 時間別売上分析（business_hour基準）
hourly_sales = account_df.groupby('business_hour').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'count'
})
hourly_sales['客単価'] = hourly_sales['account_total'] / hourly_sales['customer_count']
hourly_sales = hourly_sales.sort_index()

peak_hour = hourly_sales['account_total'].idxmax()

# 時間帯表記の調整（24→0時、25→1時等）
def format_hour(h):
    if h >= 24:
        return f"{h-24}時（深夜）"
    else:
        return f"{h}時"

hourly_memo = f"""
### 時間別売上（営業時間基準）
- ピーク時間帯: {format_hour(peak_hour)} (売上 ¥{hourly_sales.loc[peak_hour, 'account_total']:,.0f})
- 営業時間帯: {format_hour(hourly_sales.index.min())} ～ {format_hour(hourly_sales.index.max())}
- 深夜売上（24-25時台）の比率: {hourly_sales.loc[hourly_sales.index >= 24, 'account_total'].sum() / hourly_sales['account_total'].sum() * 100:.1f}%
"""
save_memo("時間別分析", hourly_memo)

# 時間帯バケット別集計（スライド用）
def get_time_bucket_label(hour):
    if 18 <= hour < 20:
        return '18-20時'
    elif 20 <= hour < 22:
        return '20-22時'
    elif 22 <= hour < 24:
        return '22-24時'
    elif 24 <= hour < 26:
        return '24-26時'
    else:
        return 'その他'

hourly_sales['time_bucket'] = [get_time_bucket_label(h) for h in hourly_sales.index]
hourly_bucket = hourly_sales.groupby('time_bucket').agg({
    'account_total': 'sum',
    'customer_count': 'sum',
    'account_id': 'sum'
})
# 順序を指定
bucket_order = ['18-20時', '20-22時', '22-24時', '24-26時', 'その他']
hourly_bucket = hourly_bucket.reindex([b for b in bucket_order if b in hourly_bucket.index])

# 時間帯別データ出力（スライド用）
time_bucket_data = []
time_bucket_data.append("")
time_bucket_data.append("## 時間帯別売上（全体・スライド用）")
time_bucket_data.append("")
time_bucket_data.append("| 時間帯 | 売上 | 客数 | 会計数 |")
time_bucket_data.append("|---|---|---|---|")
for bucket in hourly_bucket.index:
    row = hourly_bucket.loc[bucket]
    time_bucket_data.append(f"| {bucket} | ¥{row['account_total']:,.0f} | {row['customer_count']:.0f}人 | {row['account_id']:.0f}件 |")

# slide_data_part2に追記
with open(os.path.join(output_dir, 'slide_data_part2.txt'), 'a', encoding='utf-8') as f:
    f.write('\n'.join(time_bucket_data))

# グラフ作成：時間別売上
if args.images:
    fig, ax = plt.subplots(figsize=(14, 5))

    # X軸ラベルを見やすく調整
    hour_labels = [format_hour(h) for h in hourly_sales.index]
    x_pos = np.arange(len(hourly_sales))

    bars = ax.bar(x_pos, hourly_sales['account_total'], color='lightcoral', edgecolor='black')

    # 深夜帯（24時以降）を異なる色で強調
    for i, hour in enumerate(hourly_sales.index):
        if hour >= 24:
            bars[i].set_color('darkred')
            bars[i].set_alpha(0.7)

    ax.set_title('時間別売上（営業時間基準：深夜は24時以降表記）', fontsize=14, fontweight='bold')
    ax.set_ylabel('売上 (円)', fontsize=12)
    ax.set_xlabel('時間帯', fontsize=12)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(hour_labels, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    # ピーク時間帯を強調
    peak_idx = list(hourly_sales.index).index(peak_hour)
    ax.axvline(x=peak_idx, color='red', linestyle='--', alpha=0.7, linewidth=2, label=f'ピーク: {format_hour(peak_hour)}')
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'hourly_sales.png'), dpi=150, bbox_inches='tight')
    plt.close()

# ==========================================
# 2. 商品分析
# ==========================================
save_memo("商品分析", """
【目的】どのカテゴリの商品が売れているか、構成比の変化を把握し、商品戦略に活かす
【仮説】
- 特定のカテゴリに人気が集中している
- 時期によって売れるカテゴリが変わる（季節性）
- 構成比の変化から顧客の嗜好変化を読み取れる
- 不人気カテゴリの改善余地がある
""")

# カテゴリ別売上（週次）
category_weekly = sales_df.groupby(['year_week', 'category1']).agg({
    'subtotal': 'sum',
    'quantity': 'sum'
}).reset_index()

# 対象週のカテゴリ別売上
latest_week_category = category_weekly[category_weekly['year_week'] == latest_week].copy()
latest_week_category = latest_week_category.sort_values('subtotal', ascending=False)
total_sales = latest_week_category['subtotal'].sum()
latest_week_category['構成比'] = latest_week_category['subtotal'] / total_sales * 100

# 前週のカテゴリ別売上
if prev_week:
    prev_week_category = category_weekly[category_weekly['year_week'] == prev_week].copy()
    prev_week_total = prev_week_category['subtotal'].sum()
    prev_week_category['構成比'] = prev_week_category['subtotal'] / prev_week_total * 100 if prev_week_total > 0 else 0
    prev_week_category = prev_week_category.set_index('category1')
else:
    prev_week_category = pd.DataFrame()

# 前月のカテゴリ別売上
if prev_month_week:
    prev_month_category = category_weekly[category_weekly['year_week'] == prev_month_week].copy()
    prev_month_total = prev_month_category['subtotal'].sum()
    prev_month_category['構成比'] = prev_month_category['subtotal'] / prev_month_total * 100 if prev_month_total > 0 else 0
    prev_month_category = prev_month_category.set_index('category1')
else:
    prev_month_category = pd.DataFrame()

# カテゴリランキングのメモ
category_memo = f"### 対象週 ({latest_week}) カテゴリ別ランキング\n"
for idx, row in latest_week_category.head(10).iterrows():
    category = row['category1']
    sales = row['subtotal']
    ratio = row['構成比']
    qty = row['quantity']

    # 前週比
    prev_change = ""
    if not prev_week_category.empty and category in prev_week_category.index:
        prev_ratio = prev_week_category.loc[category, '構成比']
        change = ratio - prev_ratio
        prev_change = f" (前週比: {change:+.1f}pt)"

    category_memo += f"{idx+1}. {category}: ¥{sales:,.0f} ({ratio:.1f}%, {qty:.0f}個){prev_change}\n"

save_memo("カテゴリランキング", category_memo)

# ==========================================
# 第3部用：カテゴリ・商品分析データ出力（スライド用テキスト）
# ==========================================
slide_data_part3 = []
slide_data_part3.append("=" * 60)
slide_data_part3.append("【スライド第3部用】商品・カテゴリ分析データ")
slide_data_part3.append("=" * 60)
slide_data_part3.append("")

# カテゴリ別構成比データ（スライド19用）
slide_data_part3.append("## スライド19: カテゴリ別売上構成比（円グラフ用データ）")
slide_data_part3.append("")
slide_data_part3.append("| カテゴリ | 売上 | 構成比 | 販売数 |")
slide_data_part3.append("|---|---|---|---|")
for _, row in latest_week_category.iterrows():
    slide_data_part3.append(f"| {row['category1']} | ¥{row['subtotal']:,.0f} | {row['構成比']:.1f}% | {row['quantity']:.0f}個 |")
slide_data_part3.append("")

# ファイル出力（後で追記）
with open(os.path.join(output_dir, 'slide_data_part3.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(slide_data_part3))

print("\n[出力] slide_data_part3.txt - 第3部用商品・カテゴリデータ")

# グラフ作成：カテゴリ別売上構成比（円グラフ）- モダンデザイン
if args.images:
    fig, ax = plt.subplots(figsize=(13, 9), facecolor='white')
    colors = sns.color_palette('husl', len(latest_week_category))

    # 円グラフの描画（エクスプローション効果付き）
    explode = [0.05 if i == 0 else 0.02 for i in range(len(latest_week_category))]  # 最大カテゴリを強調
    wedges, texts, autotexts = ax.pie(
        latest_week_category['subtotal'],
        labels=latest_week_category['category1'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        explode=explode,
        textprops={'fontsize': 11, 'weight': 'bold'},
        pctdistance=0.85
    )

    # ラベルのスタイル設定
    for text in texts:
        text.set_fontsize(12)
        text.set_fontweight('bold')
        text.set_color('#2c3e50')

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    ax.set_title(f'カテゴリ別売上構成比 ({latest_week})', fontsize=16, fontweight='bold',
                pad=20, color='#2c3e50')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'category_sales.png'), dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

# カテゴリ別構成比の時系列データを作成（自然言語分析用）
save_memo("カテゴリ構成比時系列データ作成", "各週のカテゴリ別構成比を計算しています...")
category_composition_trend = []
for week in category_weekly['year_week'].unique():
    week_data = category_weekly[category_weekly['year_week'] == week].copy()
    week_total = week_data['subtotal'].sum()
    week_data['構成比'] = (week_data['subtotal'] / week_total * 100) if week_total > 0 else 0
    week_data['week'] = week
    category_composition_trend.append(week_data[['week', 'category1', 'subtotal', 'quantity', '構成比']])

category_composition_df = pd.concat(category_composition_trend, ignore_index=True)
category_composition_df = category_composition_df.sort_values(['week', '構成比'], ascending=[True, False])

# ==========================================
# 2.3. 商品別分析（NEW）
# ==========================================
save_memo("商品別分析", """
【目的】個別商品レベルでの売れ筋・死に筋を特定し、メニュー改訂の判断材料とする
【仮説】
- 特定の商品に売上が集中している
- 構成比の変化から商品人気の変動を読み取れる
- 売れ筋商品と死に筋商品が明確に分かれる
""")

# 商品別売上（週次）
product_weekly = sales_df.groupby(['year_week', 'menu_name']).agg({
    'subtotal': 'sum',
    'quantity': 'sum'
}).reset_index()

# 最新週の商品別売上
latest_week_product = product_weekly[product_weekly['year_week'] == latest_week].copy()
latest_week_product = latest_week_product.sort_values('subtotal', ascending=False)
total_sales_product = latest_week_product['subtotal'].sum()
latest_week_product['構成比'] = latest_week_product['subtotal'] / total_sales_product * 100

# 前週の商品別売上
if prev_week:
    prev_week_product = product_weekly[product_weekly['year_week'] == prev_week].copy()
    prev_week_product_total = prev_week_product['subtotal'].sum()
    prev_week_product['構成比'] = prev_week_product['subtotal'] / prev_week_product_total * 100 if prev_week_product_total > 0 else 0
    prev_week_product = prev_week_product.set_index('menu_name')
else:
    prev_week_product = pd.DataFrame()

# 前月の商品別売上
if prev_month_week:
    prev_month_product = product_weekly[product_weekly['year_week'] == prev_month_week].copy()
    prev_month_product_total = prev_month_product['subtotal'].sum()
    prev_month_product['構成比'] = prev_month_product['subtotal'] / prev_month_product_total * 100 if prev_month_product_total > 0 else 0
    prev_month_product = prev_month_product.set_index('menu_name')
else:
    prev_month_product = pd.DataFrame()

# 商品別ランキングのメモ
product_memo = f"### 対象週 ({latest_week}) 商品別ランキング TOP20\n"
for idx, row in latest_week_product.head(20).iterrows():
    product = row['menu_name']
    sales = row['subtotal']
    ratio = row['構成比']
    qty = row['quantity']

    # 前週比
    prev_change = ""
    if not prev_week_product.empty and product in prev_week_product.index:
        prev_ratio = prev_week_product.loc[product, '構成比']
        change = ratio - prev_ratio
        prev_change = f" (前週比: {change:+.2f}pt)"

    product_memo += f"{idx+1}. {product}: ¥{sales:,.0f} ({ratio:.2f}%, {qty:.0f}個){prev_change}\n"

save_memo("商品別ランキング", product_memo)

# 過去4週間の商品別売上平均を計算（スライド用）
if latest_week_idx >= 4:
    ma4_product_weeks = week_list[latest_week_idx - 4:latest_week_idx]
    ma4_product_data = product_weekly[product_weekly['year_week'].isin(ma4_product_weeks)]
    ma4_product_avg = ma4_product_data.groupby('menu_name').agg({
        'subtotal': 'mean',
        'quantity': 'mean'
    }).reset_index()
    ma4_product_avg.columns = ['menu_name', '4週平均売上', '4週平均数量']
    ma4_product_avg = ma4_product_avg.set_index('menu_name')
else:
    ma4_product_avg = pd.DataFrame()

# 商品TOP10データ（スライド21用）- 4週平均比較付き
slide_data_part3_products = []
slide_data_part3_products.append("")
slide_data_part3_products.append("## スライド21: 商品別売上TOP10（グラフ用データ）")
slide_data_part3_products.append("")
slide_data_part3_products.append("| 商品名 | 対象週売上 | 構成比 | 4週平均 | 成長率 |")
slide_data_part3_products.append("|---|---|---|---|---|")

for _, row in latest_week_product.head(10).iterrows():
    product_name = row['menu_name']
    sales = row['subtotal']
    ratio = row['構成比']
    if not ma4_product_avg.empty and product_name in ma4_product_avg.index:
        ma4_sales = ma4_product_avg.loc[product_name, '4週平均売上']
        growth = (sales / ma4_sales - 1) * 100 if ma4_sales > 0 else 0
        slide_data_part3_products.append(f"| {product_name} | ¥{sales:,.0f} | {ratio:.1f}% | ¥{ma4_sales:,.0f} | {growth:+.1f}% |")
    else:
        slide_data_part3_products.append(f"| {product_name} | ¥{sales:,.0f} | {ratio:.1f}% | - | - |")
slide_data_part3_products.append("")

# 構成比増減商品リスト（スライド22用）
slide_data_part3_products.append("## スライド22: 構成比増減商品（前週比）")
slide_data_part3_products.append("")
if not prev_week_product.empty:
    # 対象週と前週の構成比を比較
    composition_changes = []
    for _, row in latest_week_product.iterrows():
        product_name = row['menu_name']
        current_ratio = row['構成比']
        if product_name in prev_week_product.index:
            prev_ratio = prev_week_product.loc[product_name, '構成比']
            change = current_ratio - prev_ratio
            composition_changes.append({
                'product': product_name,
                'current': current_ratio,
                'prev': prev_ratio,
                'change': change
            })

    composition_df = pd.DataFrame(composition_changes)
    if not composition_df.empty:
        # 増加TOP5
        top_increase = composition_df.nlargest(5, 'change')
        slide_data_part3_products.append("### 構成比増加TOP5")
        slide_data_part3_products.append("")
        slide_data_part3_products.append("| 商品名 | 今週構成比 | 前週構成比 | 変化 |")
        slide_data_part3_products.append("|---|---|---|---|")
        for _, row in top_increase.iterrows():
            slide_data_part3_products.append(f"| {row['product']} | {row['current']:.2f}% | {row['prev']:.2f}% | {row['change']:+.2f}pt |")
        slide_data_part3_products.append("")

        # 減少TOP5
        top_decrease = composition_df.nsmallest(5, 'change')
        slide_data_part3_products.append("### 構成比減少TOP5")
        slide_data_part3_products.append("")
        slide_data_part3_products.append("| 商品名 | 今週構成比 | 前週構成比 | 変化 |")
        slide_data_part3_products.append("|---|---|---|---|")
        for _, row in top_decrease.iterrows():
            slide_data_part3_products.append(f"| {row['product']} | {row['current']:.2f}% | {row['prev']:.2f}% | {row['change']:+.2f}pt |")
        slide_data_part3_products.append("")
else:
    slide_data_part3_products.append("前週データがないため比較不可")
    slide_data_part3_products.append("")

# slide_data_part3.txtに追記
with open(os.path.join(output_dir, 'slide_data_part3.txt'), 'a', encoding='utf-8') as f:
    f.write('\n'.join(slide_data_part3_products))

# グラフ作成：商品別売上構成比（円グラフ、TOP10 + その他）- モダンデザイン
if args.images:
    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')

    top10_products = latest_week_product.head(10).copy()
    other_sales = latest_week_product.iloc[10:]['subtotal'].sum() if len(latest_week_product) > 10 else 0

    # TOP10 + その他のデータを作成
    pie_labels = top10_products['menu_name'].tolist()
    pie_values = top10_products['subtotal'].tolist()

    if other_sales > 0:
        pie_labels.append('その他')
        pie_values.append(other_sales)

    # カラーパレット（TOP10は明るい色、その他はグレー）
    colors = sns.color_palette('husl', 10)
    if other_sales > 0:
        colors = list(colors) + ['#bdc3c7']

    # エクスプローション（TOP3を強調）
    explode = [0.08, 0.05, 0.03] + [0.01] * (len(pie_values) - 3)

    wedges, texts, autotexts = ax.pie(
        pie_values,
        labels=pie_labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=45,
        explode=explode,
        textprops={'fontsize': 10, 'weight': 'bold'},
        pctdistance=0.82
    )

    # ラベルのスタイル設定
    for text in texts:
        text.set_fontsize(11)
        text.set_fontweight('bold')
        text.set_color('#2c3e50')

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    ax.set_title(f'商品別売上構成比 TOP10 + その他 ({latest_week})', fontsize=16, fontweight='bold',
                pad=20, color='#2c3e50')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_products.png'), dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

# 商品別構成比の時系列データを作成（自然言語分析用）
save_memo("商品構成比時系列データ作成", "各週の商品別構成比を計算しています（TOP20商品のみ）...")
top20_product_names = latest_week_product.head(20)['menu_name'].tolist()
product_composition_trend = []
for week in product_weekly['year_week'].unique():
    week_data = product_weekly[product_weekly['year_week'] == week].copy()
    week_total = week_data['subtotal'].sum()
    week_data['構成比'] = (week_data['subtotal'] / week_total * 100) if week_total > 0 else 0
    # TOP20商品のみに絞る
    week_data_top = week_data[week_data['menu_name'].isin(top20_product_names)]
    week_data_top = week_data_top.copy()
    week_data_top['week'] = week
    product_composition_trend.append(week_data_top[['week', 'menu_name', 'subtotal', 'quantity', '構成比']])

product_composition_df = pd.concat(product_composition_trend, ignore_index=True)
product_composition_df = product_composition_df.sort_values(['week', '構成比'], ascending=[True, False])

# ==========================================
# 3. 口コミ分析
# ==========================================
save_memo("口コミ分析", """
【目的】顧客の声を収集し、満足度や改善点を把握する
【仮説】
- 口コミから顧客の満足度や不満点が明確になる
- 高評価・低評価の理由から改善すべき点が見つかる
- 口コミの内容から顧客の期待値を理解できる
""")

# 対象週の口コミ抽出
latest_date_dt = pd.to_datetime(target_date_end)
week_start_dt = pd.to_datetime(target_date_start)

latest_week_reviews = reviews_df[
    (reviews_df['投稿日'] >= week_start_dt) &
    (reviews_df['投稿日'] <= latest_date_dt)
].copy()

reviews_memo = f"""
### 対象週の口コミ ({target_date_start} ～ {target_date_end})
- 新規投稿数: {len(latest_week_reviews)}件
"""

if len(latest_week_reviews) > 0:
    avg_score = latest_week_reviews['総合点数'].mean()
    reviews_memo += f"- 平均評価: {avg_score:.2f}点\n\n"

    for idx, row in latest_week_reviews.iterrows():
        reviews_memo += f"""
#### {row['投稿者']} ({row['投稿日'].date()})
- 評価: {row['総合点数']}点
- タイトル: {row['口コミタイトル']}
- 内容: {row['口コミ内容'][:200]}{'...' if len(str(row['口コミ内容'])) > 200 else ''}
- 使用金額: {row['使った金額_夜']}
---
"""
else:
    reviews_memo += "- 対象週に新規投稿はありませんでした\n"

save_memo("対象週の口コミ", reviews_memo)

# 口コミ評価の推移（月次）
reviews_df['year_month'] = reviews_df['投稿日'].dt.strftime('%Y-%m')
monthly_reviews = reviews_df.groupby('year_month').agg({
    '総合点数': 'mean',
    '投稿者': 'count'
}).rename(columns={'投稿者': '投稿数'})

if args.images and len(monthly_reviews) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    monthly_reviews['総合点数'].plot(ax=axes[0], marker='o', linewidth=2, markersize=6, color='green')
    axes[0].set_title('月次平均評価推移', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('平均評価 (点)', fontsize=12)
    axes[0].set_ylim(0, 5)
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)

    monthly_reviews['投稿数'].plot(kind='bar', ax=axes[1], color='skyblue', edgecolor='black')
    axes[1].set_title('月次口コミ投稿数', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('投稿数 (件)', fontsize=12)
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'reviews_trend.png'), dpi=150, bbox_inches='tight')
    plt.close()

# ==========================================
# 結果の保存
# ==========================================
save_memo("データ保存", "分析結果をJSON、CSVファイルに保存しています...")

# 分析結果をJSON形式で保存
analysis_results = {
    'meta': {
        'analysis_date': str(datetime.now()),
        'data_period_start': str(sales_df['date'].min()),
        'data_period_end': str(sales_df['date'].max()),
        'target_week': latest_week,
        'target_date_start': str(target_date_start),
        'target_date_end': str(target_date_end),
        'store_name': sales_df['store_name'].iloc[0]
    },
    'sales_analysis': {
        'target_week': {
            '売上': float(latest_week_data['売上']) if latest_week_data is not None else None,
            '客数': int(latest_week_data['客数']) if latest_week_data is not None else None,
            '組数': int(latest_week_data['組数']) if latest_week_data is not None else None,
            '客単価': float(latest_week_data['客単価']) if latest_week_data is not None else None
        },
        'comparisons': {
            'previous_week': {
                'week': prev_week,
                'data': {
                    '売上': float(prev_week_data['売上']) if prev_week_data is not None else None,
                    '客数': int(prev_week_data['客数']) if prev_week_data is not None else None,
                    '客単価': float(prev_week_data['客単価']) if prev_week_data is not None else None
                }
            } if prev_week_data is not None else None,
            'previous_month': {
                'week': prev_month_week,
                'data': {
                    '売上': float(prev_month_data['売上']) if prev_month_data is not None else None,
                    '客数': int(prev_month_data['客数']) if prev_month_data is not None else None,
                    '客単価': float(prev_month_data['客単価']) if prev_month_data is not None else None
                }
            } if prev_month_data is not None else None,
            'previous_year': {
                'week': prev_year_week,
                'data': {
                    '売上': float(prev_year_data['売上']) if prev_year_data is not None else None,
                    '客数': int(prev_year_data['客数']) if prev_year_data is not None else None,
                    '客単価': float(prev_year_data['客単価']) if prev_year_data is not None else None
                }
            } if prev_year_data is not None else None
        }
    },
    'category_analysis': {
        'target_week': latest_week_category.to_dict('records'),
        'previous_week': prev_week_category.to_dict() if not prev_week_category.empty else None,
        'previous_month': prev_month_category.to_dict() if not prev_month_category.empty else None
    },
    'product_analysis': {
        'target_week': latest_week_product.to_dict('records'),
        'previous_week': prev_week_product.to_dict() if not prev_week_product.empty else None,
        'previous_month': prev_month_product.to_dict() if not prev_month_product.empty else None
    },
    'reviews_analysis': {
        'target_week_count': len(latest_week_reviews),
        'target_week_reviews': latest_week_reviews.to_dict('records')
    }
}

with open(os.path.join(output_dir, 'analysis_results.json'), 'w', encoding='utf-8') as f:
    json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)

# CSV形式でも保存
weekly_sales.to_csv(os.path.join(output_dir, 'weekly_sales.csv'), encoding='utf-8-sig')
if not weekday_decomp_df.empty:
    weekday_decomp_df.to_csv(os.path.join(output_dir, 'weekday_decomposition.csv'), encoding='utf-8-sig', index=False)
hourly_sales.to_csv(os.path.join(output_dir, 'hourly_sales.csv'), encoding='utf-8-sig')
latest_week_category.to_csv(os.path.join(output_dir, 'category_latest.csv'), encoding='utf-8-sig', index=False)
latest_week_product.to_csv(os.path.join(output_dir, 'product_latest.csv'), encoding='utf-8-sig', index=False)

# 構成比時系列データの保存（自然言語分析用）NEW!
category_composition_df.to_csv(os.path.join(output_dir, 'category_composition_trend.csv'), encoding='utf-8-sig', index=False)
product_composition_df.to_csv(os.path.join(output_dir, 'product_composition_trend.csv'), encoding='utf-8-sig', index=False)

if not latest_week_reviews.empty:
    latest_week_reviews.to_csv(os.path.join(output_dir, 'reviews_latest_week.csv'), encoding='utf-8-sig', index=False)

# 中間メモの保存
memo_file = os.path.join(output_dir, 'analysis_memo.txt')
with open(memo_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write(f"分析中間メモ ({target_week})\n")
    f.write("=" * 80 + "\n")
    for memo in memo_content:
        f.write(memo)

# 出力ファイルリスト
output_files_list = f"""
分析完了！結果は {output_dir} に保存されました。

【スライド用データ（テキスト形式）】※ 常に出力
- slide_data_part1.txt: 第1部用（週次トレンド、KPI、前年比較）
- slide_data_part2.txt: 第2部用（曜日別概況、深掘り対象曜日、時間帯別）
- slide_data_part3.txt: 第3部用（カテゴリ構成比、商品TOP10、構成比増減）

【データファイル（CSV/JSON）】※ 常に出力
- analysis_results.json: 分析結果（JSON、商品別データ含む）
- weekly_sales.csv: 週次売上データ
- weekday_decomposition.csv: 曜日別要因分解データ
- hourly_sales.csv: 時間別売上データ
- category_latest.csv: 対象週カテゴリ別売上
- product_latest.csv: 対象週商品別売上
- category_composition_trend.csv: カテゴリ別構成比時系列データ
- product_composition_trend.csv: 商品別構成比時系列データ（TOP20）
- reviews_latest_week.csv: 対象週の口コミ
- analysis_memo.txt: 分析中間メモ
"""

if args.images:
    output_files_list += """
【グラフ画像（PNG）】※ --images 指定時のみ出力
- weekly_sales_comparison.png: 週次売上比較（棒グラフ）
- weekly_sales_trend.png: 週次売上推移（折れ線グラフ）
- weekday_decomposition.png: 曜日別要因分解グラフ
- hourly_sales.png: 時間別売上グラフ
- category_sales.png: カテゴリ別売上構成比（円グラフ）
- top_products.png: 商品別売上構成比TOP10（円グラフ）
- reviews_trend.png: 口コミ評価推移
"""
else:
    output_files_list += """
【グラフ画像】スキップ（--images 未指定）
"""

save_memo("完了", output_files_list)

print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
