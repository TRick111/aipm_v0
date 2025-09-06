import csv

csv_path = "お役立ち情報台本.csv"

with open(csv_path, encoding="utf-8") as f:
    reader = list(csv.reader(f))

header_len = len(reader[0])
all_ok = True
for idx, row in enumerate(reader, 1):
    if len(row) != header_len:
        print(f"Line {idx}: 列数が不一致 ({len(row)}列, ヘッダは{header_len}列) → {row}")
        all_ok = False

if all_ok:
    print(f"全{len(reader)}行、すべての行で列数({header_len})が一致しています。")
