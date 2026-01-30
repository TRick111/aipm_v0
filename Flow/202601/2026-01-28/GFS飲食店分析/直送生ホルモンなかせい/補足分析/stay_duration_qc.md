# 滞在時間QC（入店=H.伝票発行日 / 退店=H.伝票処理日）
- 対象CSV: transformed_pos_data_eatin.csv
- 集計単位: 1組=1伝票（H.伝票番号）。商品明細行は重複除外

## 欠損・異常の件数
- rows: 7779
- entry_missing: 0
- exit_missing: 0
- biz_missing: 0
- duration_missing: 0
- duration_negative: 0
- duration_ge_5h: 13
- duration_ge_8h: 3
- duration_ge_10h: 3
- duration_ge_24h: 0

## 滞在時間（分）の分布
```count    7779.000000
mean       91.094817
std        44.076098
min         0.000000
50%        85.883333
90%       141.233333
95%       162.821667
99%       225.399667
max      1124.983333
Name: stay_minutes, dtype: float64```
## 参考: 異常候補の上位30件
- CSV: stay_duration_top30.csv
