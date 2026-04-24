#!/usr/bin/env python3
"""BAR FIVE Arrows リニューアル前後比較分析（2026-04-01〜2026-04-23 / 4/23版）

- After（POS）: 2026-04-01 〜 2026-04-23（23日）  ※4/19, 4/22 は休業
- Before同ウィンドウ: 2026-03-01 〜 2026-03-23（23日）
- Before月全体: 2026-03-01 〜 2026-03-31（31日）
- YoY同ウィンドウ: 2025-04-01 〜 2025-04-23（23日）

出力:
  output_data/  ← 集計CSV / JSON
  charts/        ← 主要 PNG
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    plt.rcParams["font.family"] = "Hiragino Sans"
except Exception:
    pass
plt.rcParams["axes.unicode_minus"] = False

ROOT = "/Users/rikutanaka/aipm_v0"
RAW = f"{ROOT}/Stock/RestaurantAILab/週報/1_input/BFA/rawdata.csv"
OUTDIR = f"{ROOT}/Flow/202604/2026-04-24/バー5アローズ"
DATA = f"{OUTDIR}/output_data"
CHARTS = f"{OUTDIR}/charts"
os.makedirs(DATA, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

# ────────────────── データロード & 整形 ──────────────────
df = pd.read_csv(RAW)
df = df[df["store_code"] == "bfa-001"].copy()
df["entry_ts"] = pd.to_datetime(df["entry_at"])
df["entry_hour"] = df["entry_ts"].dt.hour
# 営業日: 0-5時は前日扱い
df["biz_date"] = df["entry_ts"].apply(
    lambda x: (x - timedelta(hours=5)).date() if x.hour < 5 else x.date()
)
df["biz_date"] = pd.to_datetime(df["biz_date"])

DOW_JP = {0: "月", 1: "火", 2: "水", 3: "木", 4: "金", 5: "土", 6: "日"}
df["dow_jp"] = df["biz_date"].dt.dayofweek.map(DOW_JP)


def time_slot(h: int) -> str:
    if 18 <= h < 20:
        return "18-20"
    if 20 <= h < 22:
        return "20-22"
    if 22 <= h < 24:
        return "22-24"
    if 0 <= h < 5:
        return "24-26(深夜)"
    return "other"


df["time_slot"] = df["entry_hour"].apply(time_slot)

PERIODS = {
    "after":     ("2026-04-01", "2026-04-23", 23),
    "before_w":  ("2026-03-01", "2026-03-23", 23),
    "before_m":  ("2026-03-01", "2026-03-31", 31),
    "yoy_w":     ("2025-04-01", "2025-04-23", 23),
}
LABELS = {
    "after":    "After (4/1-4/23)",
    "before_w": "Before同窓 (3/1-3/23)",
    "before_m": "Before月 (3/1-3/31)",
    "yoy_w":    "YoY (2025/4/1-4/23)",
}


def slice_period(p: str) -> pd.DataFrame:
    s, e, _ = PERIODS[p]
    return df[(df["biz_date"] >= s) & (df["biz_date"] <= e)].copy()


def acct_unique(p: str) -> pd.DataFrame:
    sub = slice_period(p)
    return sub.groupby("account_id", as_index=False).agg(
        account_total=("account_total", "first"),
        customer_count=("customer_count", "first"),
        biz_date=("biz_date", "first"),
        dow_jp=("dow_jp", "first"),
        time_slot=("time_slot", "first"),
        has_reservation=("has_reservation", "first"),
        is_course=("is_course", "first"),
    )


def operating_days(p: str) -> int:
    return max(int(slice_period(p)["biz_date"].nunique()), 1)


def pct_chg(a: float, b: float) -> float:
    return float("nan") if not b else (a / b - 1) * 100


# 営業日数の実態を確認（脚注用）
op_days = {p: operating_days(p) for p in PERIODS}
print("[INFO] operating_days =", op_days)

# ────────────────── A. 全体KPI（日次平均） ──────────────────
kpi_rows = []
for p in PERIODS:
    a = acct_unique(p)
    days = op_days[p]
    sales = a["account_total"].sum()
    custs = a["customer_count"].sum()
    accts = len(a)
    spend_pp = sales / max(custs, 1)
    spend_pa = sales / max(accts, 1)
    grp = a["customer_count"].mean() if accts else 0
    kpi_rows.append({
        "期間": LABELS[p],
        "営業日数": days,
        "売上合計": sales,
        "客数合計": custs,
        "組数合計": accts,
        "日次売上": sales / days,
        "日次客数": custs / days,
        "日次組数": accts / days,
        "客単価": spend_pp,
        "組単価": spend_pa,
        "平均グループサイズ": grp,
    })
kpi_df = pd.DataFrame(kpi_rows)
kpi_df.to_csv(f"{DATA}/A_kpi_summary.csv", index=False, encoding="utf-8-sig")
print(kpi_df.to_string())

# 増減率テーブル（After を基準に Before同窓 / Before月 / YoY と比較）
diff_rows = []
base = kpi_df.set_index("期間").loc[LABELS["after"]]
for p in ["before_w", "before_m", "yoy_w"]:
    cmp = kpi_df.set_index("期間").loc[LABELS[p]]
    diff_rows.append({
        "比較": f"After vs {LABELS[p]}",
        "日次売上_After": base["日次売上"], f"日次売上_{LABELS[p]}": cmp["日次売上"],
        "日次売上_差%": pct_chg(base["日次売上"], cmp["日次売上"]),
        "日次客数_差%": pct_chg(base["日次客数"], cmp["日次客数"]),
        "日次組数_差%": pct_chg(base["日次組数"], cmp["日次組数"]),
        "客単価_差%":   pct_chg(base["客単価"], cmp["客単価"]),
        "組単価_差%":   pct_chg(base["組単価"], cmp["組単価"]),
        "平均GS_差%":   pct_chg(base["平均グループサイズ"], cmp["平均グループサイズ"]),
    })
pd.DataFrame(diff_rows).to_csv(f"{DATA}/A_kpi_pct_change.csv", index=False, encoding="utf-8-sig")

# 日次生データ（After / Before同窓 / Before月 / YoY 全期間）
daily_rows = []
for p in PERIODS:
    a = acct_unique(p)
    daily = a.groupby("biz_date").agg(
        sales=("account_total", "sum"),
        custs=("customer_count", "sum"),
        accts=("account_total", "count"),
    ).reset_index()
    for _, r in daily.iterrows():
        daily_rows.append({
            "period": LABELS[p],
            "biz_date": r["biz_date"].strftime("%Y-%m-%d"),
            "曜日": DOW_JP[r["biz_date"].dayofweek],
            "売上": int(r["sales"]),
            "客数": int(r["custs"]),
            "組数": int(r["accts"]),
            "客単価": int(round(r["sales"] / max(r["custs"], 1))),
            "組単価": int(round(r["sales"] / max(r["accts"], 1))),
        })
pd.DataFrame(daily_rows).to_csv(f"{DATA}/A_daily_raw.csv", index=False, encoding="utf-8-sig")

# 2026 週次推移 (W10〜W17)
weekly_2026 = df[(df["biz_date"] >= "2026-03-02") & (df["biz_date"] <= "2026-04-26")].copy()
weekly_2026["iso"] = weekly_2026["biz_date"].dt.strftime("%G-W%V")
wk_acct = weekly_2026.groupby(["iso", "account_id"], as_index=False).agg(
    account_total=("account_total", "first"),
    customer_count=("customer_count", "first"),
    biz_date=("biz_date", "first"),
)
wk_summary = wk_acct.groupby("iso").agg(
    days=("biz_date", "nunique"),
    sales=("account_total", "sum"),
    custs=("customer_count", "sum"),
    accts=("account_total", "count"),
).reset_index()
wk_summary["日次売上"] = (wk_summary["sales"] / wk_summary["days"]).round().astype(int)
wk_summary["日次客数"] = (wk_summary["custs"] / wk_summary["days"]).round(1)
wk_summary["日次組数"] = (wk_summary["accts"] / wk_summary["days"]).round(1)
wk_summary["客単価"] = (wk_summary["sales"] / wk_summary["custs"].replace(0, np.nan)).round().astype("Int64")
wk_summary.to_csv(f"{DATA}/A_weekly_2026.csv", index=False, encoding="utf-8-sig")

# ────────────────── B. 曜日別 ──────────────────
dow_rows = []
for p in PERIODS:
    a = acct_unique(p)
    sub = slice_period(p)
    for dow in ["月", "火", "水", "木", "金", "土", "日"]:
        a_d = a[a["dow_jp"] == dow]
        days_d = max(int(sub[sub["dow_jp"] == dow]["biz_date"].nunique()), 1)
        dow_rows.append({
            "period": LABELS[p],
            "曜日": dow,
            "日数": days_d,
            "日次売上": round(a_d["account_total"].sum() / days_d),
            "日次客数": round(a_d["customer_count"].sum() / days_d, 1),
            "日次組数": round(len(a_d) / days_d, 1),
            "客単価": round(a_d["account_total"].sum() / max(a_d["customer_count"].sum(), 1)),
        })
dow_df = pd.DataFrame(dow_rows)
dow_df.to_csv(f"{DATA}/B_dow_pivot.csv", index=False, encoding="utf-8-sig")

# ────────────────── C. 時間帯 ──────────────────
slots = ["18-20", "20-22", "22-24", "24-26(深夜)"]
ts_rows = []
for p in PERIODS:
    sub = slice_period(p)
    a_ts = sub.groupby("account_id", as_index=False).agg(
        account_total=("account_total", "first"),
        customer_count=("customer_count", "first"),
        time_slot=("time_slot", "first"),
    )
    days = op_days[p]
    total_sales = a_ts["account_total"].sum()
    total_custs = a_ts["customer_count"].sum()
    for slot in slots:
        sub_s = a_ts[a_ts["time_slot"] == slot]
        ts_rows.append({
            "period": LABELS[p],
            "時間帯": slot,
            "売上": int(sub_s["account_total"].sum()),
            "客数": int(sub_s["customer_count"].sum()),
            "組数": int(len(sub_s)),
            "売上構成比%": round(sub_s["account_total"].sum() / max(total_sales, 1) * 100, 1),
            "客数構成比%": round(sub_s["customer_count"].sum() / max(total_custs, 1) * 100, 1),
            "日次平均売上": round(sub_s["account_total"].sum() / days),
            "日次平均客数": round(sub_s["customer_count"].sum() / days, 1),
        })
pd.DataFrame(ts_rows).to_csv(f"{DATA}/C_timeslot.csv", index=False, encoding="utf-8-sig")

# 1時間刻みテーブル（補足）
hour_rows = []
for p in PERIODS:
    sub = slice_period(p)
    a = sub.groupby("account_id", as_index=False).agg(
        account_total=("account_total", "first"),
        customer_count=("customer_count", "first"),
        entry_hour=("entry_hour", "first"),
    )
    days = op_days[p]
    for h in list(range(18, 24)) + list(range(0, 5)):
        sh = a[a["entry_hour"] == h]
        hour_rows.append({
            "period": LABELS[p],
            "hour": h,
            "日次平均売上": round(sh["account_total"].sum() / days),
            "日次平均客数": round(sh["customer_count"].sum() / days, 2),
            "伝票数": int(len(sh)),
        })
pd.DataFrame(hour_rows).to_csv(f"{DATA}/C_hourly.csv", index=False, encoding="utf-8-sig")

# ────────────────── D. ABC 分析 + 新商品/消滅商品 ──────────────────
def abc_for(p: str) -> pd.DataFrame:
    sub = slice_period(p)
    g = sub.groupby("menu_name", as_index=False).agg(
        category=("category1", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else ""),
        sales=("subtotal", "sum"),
        qty=("quantity", "sum"),
        accts=("account_id", "nunique"),
    ).sort_values("sales", ascending=False).reset_index(drop=True)
    total = g["sales"].sum()
    g["構成比"] = (g["sales"] / total * 100).round(2)
    g["累積構成比"] = g["構成比"].cumsum().round(2)

    def rank(c):
        if c <= 70.0:
            return "A"
        if c <= 90.0:
            return "B"
        return "C"

    g["ランク"] = g["累積構成比"].apply(rank)
    g["#"] = range(1, len(g) + 1)
    return g[["#", "menu_name", "category", "sales", "qty", "accts", "構成比", "累積構成比", "ランク"]]


abc_after = abc_for("after")
abc_before_m = abc_for("before_m")
abc_yoy = abc_for("yoy_w")

abc_after.to_csv(f"{DATA}/D_abc_after.csv", index=False, encoding="utf-8-sig")
abc_before_m.to_csv(f"{DATA}/D_abc_before_month.csv", index=False, encoding="utf-8-sig")
abc_yoy.to_csv(f"{DATA}/D_abc_yoy.csv", index=False, encoding="utf-8-sig")


def abc_summary(g: pd.DataFrame) -> dict:
    total = float(g["sales"].sum())
    out = {}
    for r in ["A", "B", "C"]:
        sub = g[g["ランク"] == r]
        out[r] = {
            "件数": int(len(sub)),
            "売上比%": round(float(sub["sales"].sum()) / max(total, 1) * 100, 1),
            "代表商品TOP3": sub.head(3)["menu_name"].tolist(),
        }
    out["商品数合計"] = int(len(g))
    out["売上合計"] = int(total)
    return out


abc_summary_dict = {
    "after": abc_summary(abc_after),
    "before_month": abc_summary(abc_before_m),
    "yoy": abc_summary(abc_yoy),
}
with open(f"{DATA}/D_abc_summary.json", "w", encoding="utf-8") as f:
    json.dump(abc_summary_dict, f, ensure_ascii=False, indent=2)

# 期間横断: A→B 降格、B→A 昇格、新登場、消滅
def to_set(g):
    return {row["menu_name"]: row["ランク"] for _, row in g.iterrows()}


after_set = to_set(abc_after)
before_set = to_set(abc_before_m)
yoy_set = to_set(abc_yoy)

# 比較: After vs Before月
shift_rows = []
all_items = set(after_set) | set(before_set)
for m in all_items:
    a_r = after_set.get(m, "なし")
    b_r = before_set.get(m, "なし")
    if a_r != b_r:
        shift_rows.append({
            "menu_name": m,
            "Before月_ランク": b_r,
            "After_ランク": a_r,
            "変化": f"{b_r}→{a_r}",
        })
shift_df = pd.DataFrame(shift_rows).sort_values(["変化", "menu_name"])
shift_df.to_csv(f"{DATA}/D_abc_shift_after_vs_beforeM.csv", index=False, encoding="utf-8-sig")

# 新商品 / 消滅商品
new_items = set(slice_period("after")["menu_name"].unique()) - set(slice_period("before_m")["menu_name"].unique())
gone_items = set(slice_period("before_m")["menu_name"].unique()) - set(slice_period("after")["menu_name"].unique())

after_sub = slice_period("after")
new_df = after_sub[after_sub["menu_name"].isin(new_items)].groupby("menu_name", as_index=False).agg(
    category=("category1", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else ""),
    sales=("subtotal", "sum"),
    qty=("quantity", "sum"),
    accts=("account_id", "nunique"),
).sort_values("sales", ascending=False)
n_after_accts = max(after_sub["account_id"].nunique(), 1)
new_df["出現率%"] = (new_df["accts"] / n_after_accts * 100).round(1)
new_df.to_csv(f"{DATA}/D_new_products_after.csv", index=False, encoding="utf-8-sig")

before_sub_m = slice_period("before_m")
gone_df = before_sub_m[before_sub_m["menu_name"].isin(gone_items)].groupby("menu_name", as_index=False).agg(
    category=("category1", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else ""),
    sales=("subtotal", "sum"),
    qty=("quantity", "sum"),
    accts=("account_id", "nunique"),
).sort_values("sales", ascending=False)
gone_df.to_csv(f"{DATA}/D_disappeared_products.csv", index=False, encoding="utf-8-sig")

# カテゴリ別売上構成比
cat_rows = []
for p in PERIODS:
    sub = slice_period(p)
    cs = sub.groupby("category1", dropna=False).agg(
        sales=("subtotal", "sum"),
        qty=("quantity", "sum"),
    ).reset_index()
    total = cs["sales"].sum()
    cs["構成比%"] = (cs["sales"] / max(total, 1) * 100).round(1)
    cs["period"] = LABELS[p]
    cat_rows.append(cs)
cat_all = pd.concat(cat_rows, ignore_index=True)
cat_all.to_csv(f"{DATA}/D_category_pivot.csv", index=False, encoding="utf-8-sig")

# TOP30 商品
def top30(p: str) -> pd.DataFrame:
    sub = slice_period(p)
    g = sub.groupby("menu_name", as_index=False).agg(
        category=("category1", lambda s: s.dropna().mode().iat[0] if not s.dropna().empty else ""),
        sales=("subtotal", "sum"),
        qty=("quantity", "sum"),
        accts=("account_id", "nunique"),
    ).sort_values("sales", ascending=False).head(30)
    total = sub.groupby("menu_name")["subtotal"].sum().sum()
    g["構成比%"] = (g["sales"] / max(total, 1) * 100).round(2)
    g["出現率%"] = (g["accts"] / max(sub["account_id"].nunique(), 1) * 100).round(1)
    g["period"] = LABELS[p]
    return g

top30_all = pd.concat([top30(p) for p in ["after", "before_m", "yoy_w"]], ignore_index=True)
top30_all.to_csv(f"{DATA}/D_top30_products.csv", index=False, encoding="utf-8-sig")

# 商品×期間 long形式（全商品）
long_rows = []
for p in PERIODS:
    sub = slice_period(p)
    g = sub.groupby("menu_name", as_index=False).agg(
        sales=("subtotal", "sum"),
        qty=("quantity", "sum"),
        accts=("account_id", "nunique"),
    )
    g["period"] = LABELS[p]
    long_rows.append(g)
long_df = pd.concat(long_rows, ignore_index=True)
long_df.to_csv(f"{DATA}/D_product_long.csv", index=False, encoding="utf-8-sig")

# ────────────────── E. 客単価分布 + 価格帯 ──────────────────
dist_rows = []
for p in PERIODS:
    a = acct_unique(p)
    a = a[a["customer_count"] > 0].copy()
    a["spend_pp"] = a["account_total"] / a["customer_count"]
    dist_rows.append({
        "period": LABELS[p],
        "n": int(len(a)),
        "平均": int(round(a["spend_pp"].mean())) if len(a) else 0,
        "中央値": int(round(a["spend_pp"].median())) if len(a) else 0,
        "P10": int(round(a["spend_pp"].quantile(0.1))) if len(a) else 0,
        "P25": int(round(a["spend_pp"].quantile(0.25))) if len(a) else 0,
        "P75": int(round(a["spend_pp"].quantile(0.75))) if len(a) else 0,
        "P90": int(round(a["spend_pp"].quantile(0.9))) if len(a) else 0,
    })
pd.DataFrame(dist_rows).to_csv(f"{DATA}/E_spend_distribution.csv", index=False, encoding="utf-8-sig")

bands = [(0, 2000, "~¥2,000"), (2000, 4000, "¥2,000-4,000"), (4000, 6000, "¥4,000-6,000"),
         (6000, 10000, "¥6,000-10,000"), (10000, 20000, "¥10,000-20,000"), (20000, 10**9, "¥20,000~")]
band_rows = []
for p in PERIODS:
    a = acct_unique(p)
    a = a[a["customer_count"] > 0].copy()
    a["spend_pp"] = a["account_total"] / a["customer_count"]
    total = max(len(a), 1)
    for lo, hi, lab in bands:
        n = ((a["spend_pp"] >= lo) & (a["spend_pp"] < hi)).sum()
        band_rows.append({
            "period": LABELS[p],
            "価格帯": lab,
            "組数": int(n),
            "構成比%": round(n / total * 100, 1),
        })
pd.DataFrame(band_rows).to_csv(f"{DATA}/E_price_band.csv", index=False, encoding="utf-8-sig")

# ────────────────── F. グループサイズ ──────────────────
def grp_label(n):
    if n <= 0:
        return "0名(異常値)"
    if n == 1:
        return "1名"
    if n == 2:
        return "2名"
    if 3 <= n <= 4:
        return "3-4名"
    return "5名以上"

grp_rows = []
for p in PERIODS:
    a = acct_unique(p)
    a = a.copy()
    a["grp"] = a["customer_count"].apply(grp_label)
    total = max(len(a), 1)
    counts = a.groupby("grp").size()
    for g in ["1名", "2名", "3-4名", "5名以上"]:
        c = int(counts.get(g, 0))
        grp_rows.append({"period": LABELS[p], "グループ": g, "組数": c, "構成比%": round(c / total * 100, 1)})
    grp_rows.append({"period": LABELS[p], "グループ": "平均GS", "組数": int(len(a)), "構成比%": round(a["customer_count"].mean(), 2)})
pd.DataFrame(grp_rows).to_csv(f"{DATA}/F_group_size.csv", index=False, encoding="utf-8-sig")

# ────────────────── G. 日報テーマ抽出（量的） ──────────────────
DR_PATH = f"{ROOT}/Stock/RestaurantAILab/週報/1_input/BFA/DailyReport.csv"
dr = pd.read_csv(DR_PATH)
dr.columns = ["営業日", "氏名", "来客特徴", "改善ポイント"]
dr["営業日"] = pd.to_datetime(dr["営業日"]).dt.date
dr.to_csv(f"{DATA}/G_dailyreport_full.csv", index=False, encoding="utf-8-sig")

# ────────────────── 図表 ──────────────────
def safe_savefig(name):
    p = f"{CHARTS}/{name}"
    plt.tight_layout()
    plt.savefig(p, dpi=140, bbox_inches="tight")
    plt.close()
    return p

# 1. 日次売上推移（After + Before同窓 + YoY）
fig, ax = plt.subplots(figsize=(11, 5))
for p, color in [("after", "#d9534f"), ("before_w", "#5bc0de"), ("yoy_w", "#999999")]:
    a = acct_unique(p)
    daily = a.groupby("biz_date")["account_total"].sum().reset_index()
    daily["day_idx"] = (daily["biz_date"] - daily["biz_date"].min()).dt.days + 1
    ax.plot(daily["day_idx"], daily["account_total"], marker="o", label=LABELS[p], color=color, linewidth=2)
ax.set_xlabel("Day index (1〜23)")
ax.set_ylabel("日次売上（¥）")
ax.set_title("BFA 日次売上推移：After vs Before同窓 vs YoY")
ax.legend()
ax.grid(alpha=0.3)
safe_savefig("01_daily_sales.png")

# 2. 曜日別比較
fig, ax = plt.subplots(figsize=(10, 5))
order = ["月", "火", "水", "木", "金", "土", "日"]
x = np.arange(len(order))
w = 0.27
for i, (p, c) in enumerate([("after", "#d9534f"), ("before_w", "#5bc0de"), ("yoy_w", "#999999")]):
    sub = dow_df[dow_df["period"] == LABELS[p]].set_index("曜日").reindex(order)
    ax.bar(x + (i - 1) * w, sub["日次売上"], w, label=LABELS[p],
           color=c, edgecolor="white")
ax.set_xticks(x)
ax.set_xticklabels(order)
ax.set_ylabel("日次平均売上（¥）")
ax.set_title("BFA 曜日別 日次平均売上")
ax.legend()
ax.grid(axis="y", alpha=0.3)
safe_savefig("02_dow_compare.png")

# 3. ABCパレート（After）
fig, ax1 = plt.subplots(figsize=(11, 5))
ax1.bar(range(len(abc_after)), abc_after["sales"], color="#d9534f", alpha=0.7)
ax1.set_xlabel("商品（売上降順）")
ax1.set_ylabel("売上（¥）", color="#d9534f")
ax2 = ax1.twinx()
ax2.plot(range(len(abc_after)), abc_after["累積構成比"], color="#222", linewidth=2)
ax2.axhline(70, color="gray", linestyle="--", linewidth=1)
ax2.axhline(90, color="gray", linestyle="--", linewidth=1)
ax2.set_ylabel("累積構成比（%）")
ax2.set_ylim(0, 105)
ax1.set_title(f"BFA ABCパレート（After: 4/1-4/18, 商品数={len(abc_after)}）")
safe_savefig("03_abc_pareto_after.png")

# 4. 時間帯構成
fig, ax = plt.subplots(figsize=(9, 5))
ts_pivot = pd.DataFrame(ts_rows).pivot_table(index="時間帯", columns="period", values="売上構成比%", aggfunc="first")
ts_pivot = ts_pivot.reindex(slots)
ts_pivot[[LABELS[p] for p in ["after", "before_w", "yoy_w"]]].plot(kind="bar", ax=ax,
                                                                color=["#d9534f", "#5bc0de", "#999999"], edgecolor="white")
ax.set_ylabel("売上構成比（%）")
ax.set_title("BFA 時間帯別 売上構成比")
ax.set_xticklabels(slots, rotation=0)
ax.grid(axis="y", alpha=0.3)
safe_savefig("04_timeslot_share.png")

# 5. 価格帯分布
fig, ax = plt.subplots(figsize=(11, 5))
band_pivot = pd.DataFrame(band_rows).pivot_table(index="価格帯", columns="period", values="構成比%", aggfunc="first")
band_pivot = band_pivot.reindex([b[2] for b in bands])
band_pivot[[LABELS[p] for p in ["after", "before_w", "yoy_w"]]].plot(kind="bar", ax=ax,
                                                                  color=["#d9534f", "#5bc0de", "#999999"], edgecolor="white")
ax.set_ylabel("組数構成比（%）")
ax.set_title("BFA 客単価バンド別 組数構成比")
ax.set_xticklabels([b[2] for b in bands], rotation=20)
ax.grid(axis="y", alpha=0.3)
safe_savefig("05_price_band.png")

# 6. 週次トレンド (W10〜W17)
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(wk_summary["iso"], wk_summary["日次売上"], color="#5bc0de", edgecolor="white")
for i, v in enumerate(wk_summary["日次売上"]):
    ax.text(i, v, f"¥{v:,}", ha="center", va="bottom", fontsize=8)
ax.set_ylabel("日次平均売上（¥）")
ax.set_title("BFA 2026 週次（W10〜W17）日次平均売上の推移")
ax.grid(axis="y", alpha=0.3)
safe_savefig("06_weekly_trend.png")

print("\n[OK] 全分析完了")
print("output_data:", os.listdir(DATA))
print("charts:", os.listdir(CHARTS))
