import csv
import re

md_path = "お役立ち情報台本.md"
csv_path = "お役立ち情報台本.csv"

rows = []
with open(md_path, encoding="utf-8") as f:
    for line in f:
        if re.match(r'^\|', line):
            row = [cell.strip() for cell in line.strip().strip('|').split('|')]
            rows.append(row)

with open(csv_path, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)
