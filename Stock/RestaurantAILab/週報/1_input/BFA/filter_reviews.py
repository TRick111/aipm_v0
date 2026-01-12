"""
2025年10月27日以降の口コミを削除するスクリプト
"""
import csv
from datetime import datetime

# CSVを読み込み
with open('reviews.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    headers = next(reader)
    rows = list(reader)

print(f'Original review count: {len(rows)}')

# 日付をパースする関数
def parse_date(date_str):
    if not date_str:
        return None
    # '25/09/24 形式を解析
    date_str = date_str.strip().strip("'")
    try:
        # YY/MM/DD形式
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            # 2桁年を4桁に変換（20XX年と仮定）
            year = 2000 + year if year < 100 else year
            return datetime(year, month, day)
    except:
        pass
    return None

# フィルタリング基準日
cutoff_date = datetime(2025, 10, 27)

# 2025年10月27日より前の口コミのみ残す
filtered_rows = []
removed_rows = []
for row in rows:
    post_date_str = row[4]  # 投稿日の列
    post_date = parse_date(post_date_str)
    if post_date is None or post_date < cutoff_date:
        filtered_rows.append(row)
    else:
        removed_rows.append((row[0], post_date_str))  # 投稿者と日付

print(f'\nRemoved reviews ({len(removed_rows)}):')
for name, date in removed_rows:
    print(f'  - {name}: {date}')

print(f'\nRemaining review count: {len(filtered_rows)}')

# CSVに書き戻し
with open('reviews.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(filtered_rows)

print('\nCSV file updated.')


