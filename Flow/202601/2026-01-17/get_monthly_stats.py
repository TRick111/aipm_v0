import pandas as pd

df = pd.read_csv('reviews_output.csv', encoding='utf-8-sig')
df['投稿日_cleaned'] = df['投稿日'].str.replace("'", '', regex=False)
df['投稿日_parsed'] = pd.to_datetime(df['投稿日_cleaned'], format='%y/%m/%d', errors='coerce')
df['year_month'] = df['投稿日_parsed'].dt.to_period('M')

monthly_avg = df.groupby('year_month')['総合評価'].mean()
print('月別平均評価:')
for ym, avg in monthly_avg.items():
    print(f'{ym}: {avg:.2f}')

print(f'\n最高月: {monthly_avg.max():.2f} ({monthly_avg.idxmax()})')
print(f'最低月: {monthly_avg.min():.2f} ({monthly_avg.idxmin()})')
print(f'評価変動幅: {monthly_avg.max() - monthly_avg.min():.2f}')
print(f'標準偏差: {monthly_avg.std():.2f}')
