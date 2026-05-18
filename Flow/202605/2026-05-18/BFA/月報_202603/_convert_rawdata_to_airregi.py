#!/usr/bin/env python3
"""rawdata.csv (UTF-8) → AirRegi 提供CSV format (Shift-JIS) 変換。

monthly_report_pipeline.py が期待する列をエミュレートする。
ヘッダ行：取引No / 会計日 / 会計時間 / 合計 / 人数 / 商品点数 / 滞在時間
明細行：取引No / カテゴリー名 / メニュー名 / 価格 / 注文数量
"""
import csv, sys
from datetime import datetime, timezone, timedelta
import pandas as pd

if len(sys.argv) != 4:
    print("usage: _convert_rawdata_to_airregi.py <in.csv> <out.csv> <YYYY-MM>")
    sys.exit(1)
src, dst, target_month = sys.argv[1:4]

COLUMNS = [
    "取引No","会計日","会計時間","合計","小計","内消費税","修正金額合計","修正後合計","修正後内消費税",
    "現金","クレジットカード(Airペイ)","交通系電子マネー(Airペイ)","QUICPay(Airペイ)","iD(Airペイ)",
    "QR決済(Airペイ QR)","クレジットカード(オンライン決済)","クレジットカード/電子マネー(Square)",
    "ポイント(Airペイ ポイント)","ポイント(ホットペッパーグルメ)","Pontaポイント(Airウォレット)",
    "金券合計","売掛合計","おつり","現金以外おつり不支払額","全体割引/割増(税込)","個別割引/割増(税込)",
    "割引/割増合計(税込)","人数","商品点数","滞在時間","伝票名","レジ担当者名","ID",
    "カテゴリー名","メニュー名","価格","注文数量",
]

df = pd.read_csv(src)
# entry_at は UTC として保存されているので JST に変換
df["entry_jst"] = pd.to_datetime(df["entry_at"], utc=True).dt.tz_convert("Asia/Tokyo")
df["exit_jst"]  = pd.to_datetime(df["exit_at"],  utc=True).dt.tz_convert("Asia/Tokyo")
df["business_month"] = (df["entry_jst"] - pd.Timedelta(hours=5)).dt.strftime("%Y-%m")
# 営業月で絞り込み（5AM境界）
sub = df[df["business_month"] == target_month].copy()
print(f"Filtered rows for {target_month}: {len(sub)}", file=sys.stderr)

# 取引(account)ごとにヘッダ＋明細
rows = []
for acct_id, grp in sub.groupby("account_id", sort=False):
    first = grp.iloc[0]
    dt = first["entry_jst"]
    cust = int(first["customer_count"]) if pd.notna(first["customer_count"]) else 0
    total = float(first["account_total"]) if pd.notna(first["account_total"]) else 0
    item_count = int(first["item_count"]) if pd.notna(first["item_count"]) else int(grp["quantity"].sum())
    stay = first["exit_jst"] - first["entry_jst"]
    stay_h = int(stay.total_seconds() // 3600) if stay.total_seconds() > 0 else 0
    stay_m = int((stay.total_seconds() % 3600) // 60) if stay.total_seconds() > 0 else 0
    stay_s = int(stay.total_seconds() % 60) if stay.total_seconds() > 0 else 0
    stay_str = f"{stay_h:02d}:{stay_m:02d}:{stay_s:02d}"
    hdr = {c: "" for c in COLUMNS}
    hdr["取引No"] = acct_id
    hdr["会計日"] = dt.strftime("%Y/%m/%d")
    hdr["会計時間"] = dt.strftime("%H:%M:%S")
    hdr["合計"] = int(total)
    hdr["小計"] = int(total)
    hdr["修正後合計"] = int(total)
    hdr["人数"] = cust
    hdr["商品点数"] = item_count
    hdr["滞在時間"] = stay_str
    rows.append(hdr)
    for _, r in grp.iterrows():
        d = {c: "" for c in COLUMNS}
        d["取引No"] = acct_id
        d["ID"] = ""
        d["カテゴリー名"] = r.get("category1", "") if pd.notna(r.get("category1")) else ""
        d["メニュー名"] = r.get("menu_name", "") if pd.notna(r.get("menu_name")) else ""
        try:
            d["価格"] = int(float(r["price"])) if pd.notna(r["price"]) and str(r["price"]).strip() != "" else 0
        except Exception:
            d["価格"] = 0
        try:
            d["注文数量"] = int(float(r["quantity"])) if pd.notna(r["quantity"]) else 0
        except Exception:
            d["注文数量"] = 0
        rows.append(d)

with open(dst, "w", encoding="shift_jis", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"Wrote {len(rows)} rows to {dst}", file=sys.stderr)
