# BFA 売上ランキング（カテゴリ別 / HTML出力）

## 目的
- 指定した期間（営業日ベース）で、**カテゴリごとに商品売上ランキング**を作り、**きれいなHTMLの表**で出力します。

## 入力
- POSデータ（週報プロジェクトの入力）: `Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv`
  - Flow側にコピー済み: `input/rawdata.csv`

## スクリプト
- `scripts/bfa_category_product_ranking_html.py`
  - 期間指定（`--start-date`, `--end-date`）
  - カテゴリ内の商品数が **10以上** の場合は **Top5 / Bottom5** のみ表示
  - 出力列: 販売数 / 売上 / カテゴリ内構成比 / 全体構成比

## 実行例（macOS / システムpython3）
> pyenvの`.python-version`影響を避けるため、システムpython3を明示します。

```bash
/Library/Developer/CommandLineTools/usr/bin/python3 \
"/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-27/週報/BFA_売上ランキング/scripts/bfa_category_product_ranking_html.py" \
  --sales-data "/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-27/週報/BFA_売上ランキング/input/rawdata.csv" \
  --start-date 2026-01-19 \
  --end-date   2026-01-25 \
  --output-html "/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-27/週報/BFA_売上ランキング/output/bfa_category_product_ranking_2026-01-19_2026-01-25.html"
```

## 重要: rawdataの期間について
現状の `rawdata.csv` は **business_dateの最大が 2026-01-18（= 2026-W03）** です。
そのため、**2026-01-19〜2026-01-25（= 2026-W04）** を指定すると「期間にデータがない」エラーになります。

rawdataのカバー範囲を確認する簡易コマンド:

```bash
/Library/Developer/CommandLineTools/usr/bin/python3 - <<'PY'
import pandas as pd
p="/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-27/週報/BFA_売上ランキング/input/rawdata.csv"
df=pd.read_csv(p)
df["entry_at"]=pd.to_datetime(df["entry_at"], utc=True)
df["entry_at_jst"]=df["entry_at"].dt.tz_convert("Asia/Tokyo")
df["business_date"]=df["entry_at_jst"].apply(lambda dt: (dt-pd.Timedelta(days=1)).date() if 0<=dt.hour<6 else dt.date())
print("business_date min/max:", df["business_date"].min(), df["business_date"].max())
PY
```

## 出力
- `output/` 配下にHTMLが生成されます。
  - 動作確認済み例: `output/bfa_category_product_ranking_2026-01-12_2026-01-18.html`

