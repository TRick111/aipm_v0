"""
月別客単価の計算
"""
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('transformed_pos_data_eatin.csv')
df['日付'] = pd.to_datetime(df['H.集計対象営業年月日'])
df['年月'] = df['日付'].dt.to_period('M')

# 月次集計
monthly_df = df.groupby('年月').apply(lambda x: pd.Series({
    '伝票数': x['H.伝票番号'].nunique(),
    '総売上': x.groupby('H.伝票番号')['H.小計'].first().sum(),
    '総客数': x.groupby('H.伝票番号')['H.客数（合計）'].first().sum(),
})).reset_index()

monthly_df['客単価'] = monthly_df['総売上'] / monthly_df['総客数']
monthly_df['年月_str'] = monthly_df['年月'].astype(str)

# 2025年以降のデータを表示
monthly_2025 = monthly_df[monthly_df['年月'] >= '2025-01'].copy()

print('=' * 80)
print('月別客単価一覧（2025年）')
print('=' * 80)
print()
for _, row in monthly_2025.iterrows():
    print(f'{row["年月_str"]:>10} | 客単価: {row["客単価"]:>7.0f}円 | 伝票数: {row["伝票数"]:>5,}件 | 総客数: {row["総客数"]:>6,}人')

print()
print('=' * 80)
print('リニューアル前後の比較')
print('=' * 80)

# 期間別平均
period_a = monthly_2025[(monthly_2025['年月'] >= '2025-05') & (monthly_2025['年月'] <= '2025-07')]
period_b = monthly_2025[(monthly_2025['年月'] >= '2025-10') & (monthly_2025['年月'] <= '2025-12')]

if len(period_a) > 0:
    print(f'\n期間A（5-7月）:')
    for _, row in period_a.iterrows():
        print(f'  {row["年月_str"]}: {row["客単価"]:.0f}円')
    print(f'  平均: {period_a["客単価"].mean():.0f}円')

if len(period_b) > 0:
    print(f'\n期間B（10-12月）:')
    for _, row in period_b.iterrows():
        print(f'  {row["年月_str"]}: {row["客単価"]:.0f}円')
    print(f'  平均: {period_b["客単価"].mean():.0f}円')

if len(period_a) > 0 and len(period_b) > 0:
    change = period_b['客単価'].mean() - period_a['客単価'].mean()
    change_pct = (period_b['客単価'].mean() / period_a['客単価'].mean() - 1) * 100
    print(f'\n変化: {change:+.0f}円 ({change_pct:+.1f}%)')

# 全期間表示
print()
print('=' * 80)
print('全期間の月別客単価（2024年1月以降）')
print('=' * 80)
print()
for _, row in monthly_df.iterrows():
    print(f'{row["年月_str"]:>10} | 客単価: {row["客単価"]:>7.0f}円 | 伝票数: {row["伝票数"]:>5,}件')
