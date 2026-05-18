#!/usr/bin/env python3
"""
BFA 2026-04 月報 — 分析データ生成（v1.2 イテレーション4）

★最重要変更★: データソースを「提供CSV」に統一
- 4月の集計: 提供CSV `会計明細_20260401-20260430 (1).csv`（Shift-JIS）
- 月次総売上 = ヘッダー行の「合計」列合算 = ¥3,024,490（ユーザー期待値と完全一致）
- 5月比較: 提供CSV `会計明細_20260501-20260531 (1).csv`
- 3月／前年4月の比較: 本番DB rawdata.csv（提供CSVが存在しないため）

ボトル購入:
- 提供CSVには「ボトル購入」カテゴリ自体が存在しない → 該当なし扱い（手動補正もしない）
- 月次合計 ¥3,024,490 にもボトル分は含まれない（提供CSVを正とする）

営業日基準: 6AM境界（既存仕様継承）
"""
import pandas as pd
import json
import os
from datetime import date, timedelta

OUT_DIR = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/_work"
P_APR = "/Users/rikutanaka/Downloads/会計明細_20260401-20260430 (1).csv"
P_MAY = "/Users/rikutanaka/Downloads/会計明細_20260501-20260531 (1).csv"
RAW = "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/月報/1_input/BFA/rawdata.csv"
DAILY = "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/月報/1_input/BFA/DailyReport.csv"
TARGET_MONTH = "2026-04"

os.makedirs(OUT_DIR, exist_ok=True)

CAT_CLASS = {
    "drink": {
        "NEW CLASSIC COCKTAIL","STANDARD COCKTAIL","JAPANESE COCKTAIL",
        "FRUITS COCKTAIL","DESSERT COCKTAIL","ジャパニーズカクテル","カクテル",
        "ジン","テキーラ","ラム","ブランデー","ウォッカ","ウイスキー",
        "ウイスキー（ハイボール・ボトル・オリジナル）","ジャパニーズウイスキー",
        "ワイン","ワイン（グラス）","グラスワイン&ビール","ビール","日本酒",
        "ソフトドリンク","ドリンク","オリジナルカクテル","フルーツカクテル",
        "ノンアルコールカクテル","HAPPYHOUR","黒板メニュー",
    },
    "food": {
        "COLD APPETIZERS","HOT APPETIZERS","MAIN DISHES","DESSERT","BAR SNACKS",
        "BAR SNACKS ","スナック","スナック（ホール）","バースナック","ご飯もの",
        "サラダ","タパス","メイン","デザート","アラカルト","バーフード（キッチン）",
    },
    "course": {"コース&セット"},
    "bottle": {"ボトル購入"},
    "event": {"イベント"},
    "other": {"その他","未設定","席料&ワイン&ビール"},
}
def classify(cat):
    cat = (cat or "").strip()
    for k, vs in CAT_CLASS.items():
        if cat in vs:
            return k
    return "other"

# ============================================
# 1) 提供CSV 読み込み（4月）— SOURCE OF TRUTH
# ============================================
df = pd.read_csv(P_APR, encoding="shift_jis")
# Header rows: 合計 has value
# Detail rows: カテゴリー名 + メニュー名 が両方ある（合計の有無に関わらず）
# 注意: 1行で「ヘッダー＋詳細」を兼ねる行が稀に存在する（例: 単発イベント費用）
df["is_header"] = df["合計"].notna()
df["is_detail"] = df["カテゴリー名"].notna() & df["メニュー名"].notna()

# 会計日時 → business_date (6AM境界)
df["dt"] = pd.to_datetime(df["会計日"] + " " + df["会計時間"], errors="coerce")
def to_bd(d):
    if pd.isna(d): return None
    return (d - pd.Timedelta(days=1)).date() if d.hour < 6 else d.date()
df["business_date"] = df["dt"].apply(to_bd)
df["business_month"] = pd.to_datetime(df["business_date"]).dt.strftime("%Y-%m")

# Forward-fill 取引No-related fields to detail rows
# (Actually detail rows share 取引No with their header)
# Get business_date for detail rows by mapping from header
hdr_map = df[df["is_header"]].set_index("取引No")[["business_date","business_month","dt","人数"]]
df["business_date"] = df.apply(
    lambda r: r["business_date"] if r["is_header"] else (hdr_map.loc[r["取引No"],"business_date"] if r["取引No"] in hdr_map.index else None),
    axis=1
)
df["business_month"] = df.apply(
    lambda r: r["business_month"] if r["is_header"] else (hdr_map.loc[r["取引No"],"business_month"] if r["取引No"] in hdr_map.index else None),
    axis=1
)
df["entry_dt"] = df["取引No"].map(lambda x: hdr_map.loc[x,"dt"] if x in hdr_map.index else pd.NaT)
df["人数_account"] = df["取引No"].map(lambda x: hdr_map.loc[x,"人数"] if x in hdr_map.index else 0)

# Filter to 2026-04 business_month (all 166 accounts qualify with 6AM rule)
df04 = df[df["business_month"] == TARGET_MONTH].copy()
hdr04 = df04[df04["is_header"]].copy()
det04 = df04[df04["is_detail"]].copy()  # ヘッダー兼詳細の行も詳細として扱う

print(f"✓ April business_month accounts: {len(hdr04)}")
print(f"✓ April business_month detail rows: {len(det04)}")
print(f"✓ Sum 合計 (header): ¥{hdr04['合計'].sum():,.0f}")
assert int(hdr04["合計"].sum()) == 3024490, f"Total mismatch: {hdr04['合計'].sum()}"
print("✓ Total matches ¥3,024,490")

# ============================================
# 2) Monthly KPI (April)
# ============================================
# ボトル購入の取引特定（提供CSVに2件存在）
bottle_det_apr = det04[det04["カテゴリー名"] == "ボトル購入"]
bottle_accts_apr = set(bottle_det_apr["取引No"].unique())
# ボトル取引の売上 = それらのヘッダーの「合計」合算
bottle_hdr_apr = hdr04[hdr04["取引No"].isin(bottle_accts_apr)]
bottle_sales_apr = float(bottle_hdr_apr["合計"].sum())
bottle_customers_apr = int(bottle_hdr_apr["人数"].sum())

total_sales_apr = float(hdr04["合計"].sum())
customers_apr = int(hdr04["人数"].sum())
accounts_apr = len(hdr04)
biz_days_apr = hdr04["business_date"].nunique()
# 客単価2系統
kyakutanka_with_bottle_apr = total_sales_apr / customers_apr if customers_apr else 0
sales_excl_bottle_apr = total_sales_apr - bottle_sales_apr
kyakutanka_apr = sales_excl_bottle_apr / customers_apr if customers_apr else 0
daily_avg_apr_total = total_sales_apr / biz_days_apr if biz_days_apr else 0
daily_avg_apr = sales_excl_bottle_apr / biz_days_apr if biz_days_apr else 0
print(f"  ボトル取引: {len(bottle_hdr_apr)}件 ¥{bottle_sales_apr:,.0f}（月次合計に含む／日次以下から除外）")

# ============================================
# 3) 比較データ: 2026-03 / 2025-04 (本番DB rawdata.csv)
# ============================================
raw = pd.read_csv(RAW)
raw["entry_jst"] = pd.to_datetime(raw["entry_at"], utc=True).dt.tz_convert("Asia/Tokyo")
def to_bd_dt(d):
    if pd.isna(d): return None
    return (d - pd.Timedelta(days=1)).date() if d.hour < 6 else d.date()
raw["business_date"] = raw["entry_jst"].apply(to_bd_dt)
raw["business_month"] = pd.to_datetime(raw["business_date"]).dt.strftime("%Y-%m")

def month_kpi_from_raw(month_str):
    sub = raw[raw["business_month"] == month_str]
    if len(sub) == 0: return None
    acct = sub.groupby("account_id").agg(
        total=("account_total","first"),
        customers=("customer_count","first"),
        bd=("business_date","first"),
    ).reset_index()
    # bottle from raw
    bottle_rows = sub[sub["category1"]=="ボトル購入"]
    bottle_sales = float(bottle_rows["subtotal"].sum())
    total = float(acct["total"].sum())
    customers = int(acct["customers"].sum())
    bd_unique = acct["bd"].nunique()
    excl_bottle = total - bottle_sales
    return {
        "month": month_str,
        "sales_total": total,
        "bottle_sales": bottle_sales,
        "sales_excl_bottle": excl_bottle,
        "customers": customers,
        "accounts": len(acct),
        "business_days": bd_unique,
        "kyakutanka": excl_bottle / customers if customers else 0,
        "kyakutanka_with_bottle": total / customers if customers else 0,
        "daily_avg_sales": excl_bottle / bd_unique if bd_unique else 0,
        "daily_avg_sales_with_bottle": total / bd_unique if bd_unique else 0,
    }

# April KPI dict (from provided CSV - canonical)
apr_kpi = {
    "month": "2026-04",
    "sales_total": total_sales_apr,
    "bottle_sales": bottle_sales_apr,
    "sales_excl_bottle": sales_excl_bottle_apr,
    "customers": customers_apr,
    "accounts": accounts_apr,
    "business_days": biz_days_apr,
    "kyakutanka": kyakutanka_apr,
    "kyakutanka_with_bottle": kyakutanka_with_bottle_apr,
    "daily_avg_sales": daily_avg_apr,
    "daily_avg_sales_with_bottle": daily_avg_apr_total,
    "source": "提供CSV",
}

# 6-month trend
month_kpis = {"2026-04": apr_kpi}
for m in ["2026-03","2026-02","2026-01","2025-12","2025-11","2025-10",
          "2025-09","2025-08","2025-07","2025-06","2025-05","2025-04"]:
    k = month_kpi_from_raw(m)
    if k:
        k["source"] = "本番DB rawdata.csv"
        month_kpis[m] = k

# ============================================
# 4) Weekly trend (April only - from provided CSV)
# ※ ボトル取引は除外
# ============================================
hdr04["business_date_dt"] = pd.to_datetime(hdr04["business_date"])
hdr04["year_week"] = hdr04["business_date_dt"].dt.strftime("%G-W%V")
# ボトル除外フィルタ
hdr04_no_bottle = hdr04[~hdr04["取引No"].isin(bottle_accts_apr)].copy()
weekly = hdr04_no_bottle.groupby("year_week").agg(
    sales=("合計","sum"),
    customers=("人数","sum"),
    accounts=("取引No","count"),
    business_days=("business_date","nunique"),
).reset_index().sort_values("year_week")
weekly["kyakutanka"] = weekly["sales"] / weekly["customers"]
weekly["daily_avg"] = weekly["sales"] / weekly["business_days"]
# Rename columns to match build_html.py expectations
weekly_list = []
for _, r in weekly.iterrows():
    weekly_list.append({
        "year_week": r["year_week"],
        "sales_excl_bottle": float(r["sales"]),  # April has no bottle
        "customers": int(r["customers"]),
        "accounts": int(r["accounts"]),
        "business_days": int(r["business_days"]),
        "kyakutanka": float(r["kyakutanka"]),
        "daily_avg": float(r["daily_avg"]),
    })

# ============================================
# 5) Daily trend (April) ※ボトル除外
# ============================================
daily = hdr04_no_bottle.groupby("business_date").agg(
    sales=("合計","sum"),
    customers=("人数","sum"),
    accounts=("取引No","count"),
).reset_index().sort_values("business_date")
daily_list = [{"business_date": str(r["business_date"]),
               "sales_excl_bottle": float(r["sales"]),
               "customers": int(r["customers"]),
               "accounts": int(r["accounts"])} for _, r in daily.iterrows()]

# ============================================
# 6) Weekday (April) ※ボトル除外
# ============================================
wmap = {0:"月",1:"火",2:"水",3:"木",4:"金",5:"土",6:"日"}
hdr04["weekday"] = hdr04["business_date_dt"].dt.dayofweek.map(wmap)
hdr04_no_bottle["weekday"] = pd.to_datetime(hdr04_no_bottle["business_date"]).dt.dayofweek.map(wmap)
wd = hdr04_no_bottle.groupby("weekday").agg(
    total_sales=("合計","sum"),
    total_customers=("人数","sum"),
    total_accounts=("取引No","count"),
    business_days=("business_date","nunique"),
).reset_index()
wd["daily_avg_sales"] = wd["total_sales"] / wd["business_days"]
wd["daily_avg_customers"] = wd["total_customers"] / wd["business_days"]
wd["kyakutanka"] = wd["total_sales"] / wd["total_customers"]
order = ["月","火","水","木","金","土","日"]
wd["__o"] = wd["weekday"].apply(lambda x: order.index(x) if x in order else 99)
wd = wd.sort_values("__o").drop(columns="__o")
weekday_list = [{
    "weekday": r["weekday"],
    "total_sales_excl_bottle": float(r["total_sales"]),
    "total_customers": int(r["total_customers"]),
    "total_accounts": int(r["total_accounts"]),
    "business_days": int(r["business_days"]),
    "daily_avg_sales": float(r["daily_avg_sales"]),
    "daily_avg_customers": float(r["daily_avg_customers"]),
    "kyakutanka": float(r["kyakutanka"]),
} for _, r in wd.iterrows()]

# ============================================
# 7) Hour bucket (April) — 入店時刻ベース
# 提供CSVの会計時間 - 滞在時間 = 入店時刻
# ============================================
def parse_stay(s):
    try:
        h, m, sec = str(s).split(":")
        return pd.Timedelta(hours=int(h), minutes=int(m), seconds=int(sec))
    except: return pd.Timedelta(0)

hdr04_no_bottle["stay_td"] = hdr04_no_bottle["滞在時間"].apply(parse_stay)
hdr04_no_bottle["entry_jst"] = hdr04_no_bottle["dt"] - hdr04_no_bottle["stay_td"]
def get_bh(d):
    if pd.isna(d): return None
    return d.hour + 24 if d.hour < 6 else d.hour
hdr04_no_bottle["business_hour"] = hdr04_no_bottle["entry_jst"].apply(get_bh)
def hb(h):
    if h is None: return "other"
    if 18 <= h < 20: return "18-20"
    if 20 <= h < 22: return "20-22"
    if 22 <= h < 24: return "22-24"
    if 24 <= h < 26: return "24-26"
    return "other"
hdr04_no_bottle["hour_bucket"] = hdr04_no_bottle["business_hour"].apply(hb)
hr = hdr04_no_bottle.groupby("hour_bucket").agg(
    sales=("合計","sum"),
    customers=("人数","sum"),
    accounts=("取引No","count"),
).reset_index()
hour_order = ["18-20","20-22","22-24","24-26","other"]
hr["__o"] = hr["hour_bucket"].apply(lambda x: hour_order.index(x) if x in hour_order else 99)
hr = hr.sort_values("__o").drop(columns="__o")
total_hr = hr["sales"].sum()
hr["share"] = hr["sales"] / total_hr * 100 if total_hr else 0
hour_list = [{
    "hour_bucket": r["hour_bucket"],
    "sales_excl_bottle": float(r["sales"]),
    "customers": int(r["customers"]),
    "accounts": int(r["accounts"]),
    "share": float(r["share"]),
} for _, r in hr.iterrows()]

# ============================================
# 8) Category breakdown (April) — 明細行ベース
# ============================================
# Detail 価格×数量 集計
det04["subtotal"] = det04["価格"] * det04["注文数量"]
cat = det04.groupby("カテゴリー名").agg(
    sales=("subtotal","sum"),
    qty=("注文数量","sum"),
).reset_index()
total_det = cat["sales"].sum()
cat["share"] = cat["sales"] / total_det * 100 if total_det else 0
cat = cat.sort_values("sales", ascending=False)
cat_list = [{"category1": r["カテゴリー名"], "sales": float(r["sales"]),
             "qty": float(r["qty"]), "share": float(r["share"])}
            for _, r in cat.head(15).iterrows()]

# ============================================
# 9) P1-1 Inbound (memo 海外)
# ============================================
inbound_hdr = hdr04[hdr04["メモ"].fillna("").str.contains("海外", na=False)]
p1_1 = {
    "label": "インバウンド（メモ「海外」）",
    "accounts": len(inbound_hdr),
    "customers": int(inbound_hdr["人数"].sum()),
    "sales": float(inbound_hdr["合計"].sum()),
    "share_sales": float(inbound_hdr["合計"].sum()) / total_sales_apr * 100 if total_sales_apr else 0,
    "share_customers": int(inbound_hdr["人数"].sum()) / customers_apr * 100 if customers_apr else 0,
}

# ============================================
# 10) P1-2 CLP社員（メニュー名「CLP」部分一致）
# ============================================
clp_det = det04[det04["メニュー名"].fillna("").str.contains("CLP", na=False)]
clp_accts = set(clp_det["取引No"].unique())
clp_hdr = hdr04[hdr04["取引No"].isin(clp_accts)]
p1_2 = {
    "label": "CLP社員（メニュー名「CLP」）",
    "accounts": len(clp_hdr),
    "customers": int(clp_hdr["人数"].sum()),
    "sales": float(clp_hdr["合計"].sum()),
    "share_sales": float(clp_hdr["合計"].sum()) / total_sales_apr * 100 if total_sales_apr else 0,
    "share_customers": int(clp_hdr["人数"].sum()) / customers_apr * 100 if customers_apr else 0,
}

# ============================================
# 11) P1-3 イベント（カテゴリ「イベント」）
# ============================================
event_det = det04[det04["カテゴリー名"] == "イベント"]
event_accts = set(event_det["取引No"].unique())
event_hdr = hdr04[hdr04["取引No"].isin(event_accts)]
p1_3 = {
    "label": "イベント（カテゴリ「イベント」）",
    "accounts": len(event_hdr),
    "customers": int(event_hdr["人数"].sum()),
    "sales": float(event_hdr["合計"].sum()),
    "share_sales": float(event_hdr["合計"].sum()) / total_sales_apr * 100 if total_sales_apr else 0,
    "share_customers": int(event_hdr["人数"].sum()) / customers_apr * 100 if customers_apr else 0,
}

# ============================================
# 12) P1-4 ボトル購入 — 提供CSVに該当カテゴリなし → ¥0
# ============================================
bottle_det = det04[det04["カテゴリー名"] == "ボトル購入"]
bottle_accts = set(bottle_det["取引No"].unique())
bottle_hdr = hdr04[hdr04["取引No"].isin(bottle_accts)]
p1_4 = {
    "label": "ボトル購入（カテゴリ「ボトル購入」）",
    "accounts": len(bottle_hdr),
    "customers": int(bottle_hdr["人数"].sum()),
    "sales": float(bottle_hdr["合計"].sum()),
    "share_sales": float(bottle_hdr["合計"].sum()) / total_sales_apr * 100 if total_sales_apr else 0,
    "share_customers": int(bottle_hdr["人数"].sum()) / customers_apr * 100 if customers_apr else 0,
}

# ============================================
# 13) P1-5 コース＆セット
# ============================================
course_det = det04[det04["カテゴリー名"] == "コース&セット"]
course_accts = set(course_det["取引No"].unique())
course_hdr = hdr04[hdr04["取引No"].isin(course_accts)]
p1_5 = {
    "label": "コース（カテゴリ「コース&セット」）",
    "accounts": len(course_hdr),
    "customers": int(course_hdr["人数"].sum()),
    "sales": float(course_hdr["合計"].sum()),
    "share_sales": float(course_hdr["合計"].sum()) / total_sales_apr * 100 if total_sales_apr else 0,
    "share_customers": int(course_hdr["人数"].sum()) / customers_apr * 100 if customers_apr else 0,
}

# ============================================
# 14) P1-6 その他CLPコース (menu name)
# ============================================
clpc_det = det04[det04["メニュー名"] == "その他CLPコース"]
clpc_accts = set(clpc_det["取引No"].unique())
clpc_hdr = hdr04[hdr04["取引No"].isin(clpc_accts)]
p1_6 = {
    "label": "その他CLPコース（メニュー名）",
    "accounts": len(clpc_hdr),
    "customers": int(clpc_hdr["人数"].sum()),
    "sales": float(clpc_hdr["合計"].sum()),
    "share_sales": float(clpc_hdr["合計"].sum()) / total_sales_apr * 100 if total_sales_apr else 0,
    "share_customers": int(clpc_hdr["人数"].sum()) / customers_apr * 100 if customers_apr else 0,
}

# ============================================
# 15) P1-7/8 Food/Drink ranking — 入客数列＋平均販売価格＋★乖離
# ============================================
det04["class"] = det04["カテゴリー名"].apply(classify)
# Acct → customer_count map
acct_cust = dict(zip(hdr04["取引No"], hdr04["人数"]))

def rank_by(cls, by):
    sub = det04[det04["class"] == cls].copy()
    # 入客数 = そのメニューを含む会計の人数合算
    menu_to_accts = sub.groupby("メニュー名")["取引No"].apply(lambda s: list(set(s))).reset_index()
    menu_cust = {r["メニュー名"]: sum(int(acct_cust.get(a, 0)) for a in r["取引No"])
                 for _, r in menu_to_accts.iterrows()}
    # 登録価格 = mode
    reg_price = sub.groupby("メニュー名")["価格"].apply(
        lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]).to_dict()
    agg = sub.groupby("メニュー名").agg(
        qty=("注文数量","sum"),
        sales=("subtotal","sum"),
        tx=("取引No","nunique"),
    ).reset_index()
    agg["customers"] = agg["メニュー名"].map(menu_cust).fillna(0).astype(int)
    agg["avg_price"] = (agg["sales"] / agg["qty"]).round(0)
    agg["reg_price"] = agg["メニュー名"].map(reg_price).fillna(0).astype(int)
    agg["price_dev"] = agg.apply(
        lambda r: (r["avg_price"] - r["reg_price"]) / r["reg_price"] * 100
        if r["reg_price"] else 0.0, axis=1)
    agg["price_star"] = agg["price_dev"].abs() >= 5
    if by == "qty":
        agg = agg.sort_values("qty", ascending=False)
        total = sub["注文数量"].sum()
        agg["share"] = agg["qty"] / total * 100
    else:
        agg = agg.sort_values("sales", ascending=False)
        total = sub["subtotal"].sum()
        agg["share"] = agg["sales"] / total * 100
    return [{"menu_name": r["メニュー名"], "qty": float(r["qty"]), "sales": float(r["sales"]),
             "tx": int(r["tx"]), "customers": int(r["customers"]),
             "avg_price": float(r["avg_price"]), "reg_price": int(r["reg_price"]),
             "price_dev": float(r["price_dev"]), "price_star": bool(r["price_star"]),
             "share": float(r["share"])}
            for _, r in agg.head(15).iterrows()]

p1_7_food = rank_by("food", "qty")
p1_7_drink = rank_by("drink", "qty")
p1_8_food = rank_by("food", "sales")
p1_8_drink = rank_by("drink", "sales")

# ============================================
# 16) Daily reports (April)
# ============================================
dr = pd.read_csv(DAILY)
dr_apr = dr[dr["営業日"].astype(str).str.startswith("2026-04")].copy()
daily_reports = dr_apr.to_dict("records")

# ============================================
# 16-α) PL データ（ダッシュボード本番DBダンプから集計）★v1.2 イテレーション7 新設
# ============================================
PL_JSON = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/db_pl_dump.json"
pl_data = {}
try:
    with open(PL_JSON) as f:
        pl_raw = json.load(f)
    exp_cat_map = {c["id"]: c["name"] for c in pl_raw["expenseCategories"]}
    sales_cat_map = {c["id"]: c["name"] for c in pl_raw.get("salesCategories", [])}

    # 月別費用合計（費目別＋月合計）
    monthly_exp = {}  # {ym: {cat_name: total}}
    monthly_exp_total = {}  # {ym: total}
    for e in pl_raw["monthlyExpenses"]:
        ym = e["year_month"]
        cat = exp_cat_map.get(e["category_id"], "その他")
        v = float(e["total"])
        monthly_exp.setdefault(ym, {})[cat] = v
        monthly_exp_total[ym] = monthly_exp_total.get(ym, 0) + v

    # 月別売上（PL側からも取得、エアレジと比較）
    monthly_sales_pl = {}
    for s in pl_raw["monthlySales"]:
        ym = s["year_month"]
        monthly_sales_pl[ym] = monthly_sales_pl.get(ym, 0) + float(s["total"])

    # 4月PL指標
    apr_exp = monthly_exp.get(TARGET_MONTH, {})
    apr_exp_total = monthly_exp_total.get(TARGET_MONTH, 0)
    sales_for_pl = total_sales_apr  # エアレジ4月売上 ¥3,024,490
    apr_op_profit = sales_for_pl - apr_exp_total
    apr_op_profit_rate = (apr_op_profit / sales_for_pl * 100) if sales_for_pl else 0
    # FL率 = (食材 + ドリンク) / 売上
    fl_cost = apr_exp.get("食材", 0) + apr_exp.get("ドリンク", 0)
    fl_rate = (fl_cost / sales_for_pl * 100) if sales_for_pl else 0
    labor_cost = apr_exp.get("人件費", 0)
    labor_rate = (labor_cost / sales_for_pl * 100) if sales_for_pl else 0

    # 費目別ランキング（4月）— 降順
    exp_breakdown = sorted(
        [{"category": cat, "amount": amt, "share": (amt / sales_for_pl * 100) if sales_for_pl else 0}
         for cat, amt in apr_exp.items()],
        key=lambda x: -x["amount"]
    )

    # 6ヶ月推移用（過去月）
    months_for_trend = sorted(monthly_exp.keys())
    pl_trend = []
    for ym in months_for_trend:
        ex = monthly_exp.get(ym, {})
        total = monthly_exp_total.get(ym, 0)
        sales_pl_m = monthly_sales_pl.get(ym, 0)
        # エアレジ売上があれば優先
        if ym == TARGET_MONTH:
            sales_for = sales_for_pl
        else:
            sales_for = sales_pl_m
        fl_m = ex.get("食材", 0) + ex.get("ドリンク", 0)
        labor_m = ex.get("人件費", 0)
        pl_trend.append({
            "month": ym,
            "sales": sales_for,
            "total_expense": total,
            "op_profit": (sales_for - total) if sales_for else -total,
            "op_profit_rate": ((sales_for - total) / sales_for * 100) if sales_for else None,
            "fl_rate": (fl_m / sales_for * 100) if sales_for else None,
            "labor_rate": (labor_m / sales_for * 100) if sales_for else None,
            "exp_breakdown": ex,
        })

    pl_data = {
        "available": True,
        "month_target": TARGET_MONTH,
        "expense_total": apr_exp_total,
        "op_profit": apr_op_profit,
        "op_profit_rate": apr_op_profit_rate,
        "fl_cost": fl_cost,
        "fl_rate": fl_rate,
        "labor_cost": labor_cost,
        "labor_rate": labor_rate,
        "expense_breakdown": exp_breakdown,
        "trend": pl_trend,
        "months_available": months_for_trend,
        "months_missing": ["2026-03"] if "2026-03" not in months_for_trend else [],
        "source": "ダッシュボード本番DB",
        "sales_for_pl_calc": sales_for_pl,
    }
    print(f"\n  PL ─ 総費用: ¥{apr_exp_total:,.0f}  営業利益: ¥{apr_op_profit:,.0f} ({apr_op_profit_rate:+.1f}%)")
    print(f"      FL率: {fl_rate:.1f}%  人件費率: {labor_rate:.1f}%")
    print(f"      費目内訳:")
    for e in exp_breakdown:
        print(f"        {e['category']}: ¥{e['amount']:,.0f} ({e['share']:.1f}% of sales)")
    print(f"      PL推移月: {months_for_trend}  欠損: {pl_data['months_missing']}")
except Exception as e:
    pl_data = {"available": False, "error": str(e)}
    print(f"PL data load failed: {e}")

# ============================================
# 17) Write JSON
# ============================================
out = {
    "target_month": TARGET_MONTH,
    "generated_at": pd.Timestamp.now(tz="Asia/Tokyo").isoformat(),
    "data_source": {
        "april_sales": "提供CSV `会計明細_20260401-20260430 (1).csv` (Shift-JIS)",
        "comparison_months": "本番DB `Stock/RestaurantAILab/月報/1_input/BFA/rawdata.csv`",
        "daily_reports": "本番DB DailyReport.csv",
        "april_total_verified": "¥3,024,490",
    },
    "month_kpis": month_kpis,
    "weekly": weekly_list,
    "daily": daily_list,
    "weekday": weekday_list,
    "hour": hour_list,
    "category": cat_list,
    "p1_1_inbound": p1_1,
    "p1_2_clp_employee": p1_2,
    "p1_3_event": p1_3,
    "p1_4_bottle": p1_4,
    "p1_5_course": p1_5,
    "p1_6_clp_course": p1_6,
    "p1_7_food_qty": p1_7_food,
    "p1_7_drink_qty": p1_7_drink,
    "p1_8_food_sales": p1_8_food,
    "p1_8_drink_sales": p1_8_drink,
    "daily_reports": daily_reports,
    "pl": pl_data,
}

def default(o):
    if isinstance(o, (pd.Timestamp, date)):
        return str(o)
    if hasattr(o, "item"):
        return o.item()
    return str(o)

with open(os.path.join(OUT_DIR, "analysis.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=default)

print()
print("="*60)
print(f"✓ analysis.json written")
print(f"  4月総売上 (提供CSV): ¥{total_sales_apr:,.0f}  ← 期待¥3,024,490")
print(f"  4月客数: {customers_apr}人")
print(f"  4月客単価: ¥{kyakutanka_apr:,.0f}")
print(f"  4月営業日数: {biz_days_apr}日")
print(f"  4月日平均売上: ¥{daily_avg_apr:,.0f}")
print(f"  4月会計件数: {accounts_apr}件")
print()
print(f"  P1-1 インバウンド: {p1_1['accounts']}件 / {p1_1['customers']}人 / ¥{p1_1['sales']:,.0f} ({p1_1['share_sales']:.1f}%)")
print(f"  P1-2 CLP社員: {p1_2['accounts']}件 / {p1_2['customers']}人 / ¥{p1_2['sales']:,.0f} ({p1_2['share_sales']:.1f}%)")
print(f"  P1-3 イベント: {p1_3['accounts']}件 / {p1_3['customers']}人 / ¥{p1_3['sales']:,.0f} ({p1_3['share_sales']:.1f}%)")
print(f"  P1-4 ボトル購入: {p1_4['accounts']}件 / ¥{p1_4['sales']:,.0f} (提供CSV該当なし)")
print(f"  P1-5 コース: {p1_5['accounts']}件 / {p1_5['customers']}人 / ¥{p1_5['sales']:,.0f} ({p1_5['share_sales']:.1f}%)")
print(f"  P1-6 その他CLPコース: {p1_6['accounts']}件 / {p1_6['customers']}人 / ¥{p1_6['sales']:,.0f} ({p1_6['share_sales']:.1f}%)")
print()
# 差額説明
mar_t = month_kpis.get("2026-03", {}).get("sales_total")
yr_t = month_kpis.get("2025-04", {}).get("sales_total")
print(f"  比較データ（本番DB）:")
print(f"    2026-03: ¥{mar_t:,.0f}" if mar_t else "    2026-03: N/A")
print(f"    2025-04: ¥{yr_t:,.0f}" if yr_t else "    2025-04: N/A")
