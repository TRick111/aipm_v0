#!/usr/bin/env python3
"""
月報パイプライン（汎用化版）— v2.0 / 2026-05-18

5Arrowsフィードバック（v1.2 イテレーション1〜4）を恒久反映した正規スクリプト。
4月以降の月報を `_work/` 配下で行ったのと同等の品質で再現可能にする。

★主要仕様（共通ルール.md と整合）★
- データソース: エアレジ会計明細CSV（Shift-JIS）を正
- 集計軸の使い分け:
  * 月次総売上: 売上日時ベース（エアレジ売上分析画面と一致）
  * 週次/日次/曜日/時間帯: 営業日基準（朝6時境界）
- ボトル購入:
  * 月次総売上に含む
  * 週次/日次/曜日/時間帯/客単価分子からは除外
- 客単価2系統: 全部込み（エアメイト比較用）／ボトル除く（経営判断用）
- P1-1〜P1-8 を出力

使い方:
    python monthly_report_pipeline.py \\
      --target-month 2026-04 \\
      --store-code BFA \\
      --sales-csv "/path/to/会計明細_20260401-20260430.csv" \\
      --output-dir "Flow/202605/2026-05-18/BFA/_work/" \\
      [--prev-month-csv "/path/to/会計明細_20260301-20260331.csv"] \\
      [--prev-year-csv "/path/to/会計明細_20250401-20250430.csv"] \\
      [--compare-rawdata "/path/to/rawdata.csv"]  # 比較データ用フォールバック
      [--daily-report-csv "/path/to/DailyReport.csv"]

出力: {output_dir}/analysis.json （build_monthly_html.py で読み込む）
"""
import pandas as pd
import json
import os
import argparse
import sys
import calendar
from datetime import date, timedelta

# ============================================
# カテゴリ分類マスタ（共通ルール.md §6 のマスタを参照）
# ============================================
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
# 共通: 営業日基準（朝6時境界）
# ============================================
def to_business_date(dt):
    if pd.isna(dt): return None
    return (dt - pd.Timedelta(days=1)).date() if dt.hour < 6 else dt.date()

def parse_stay(s):
    try:
        h, m, sec = str(s).split(":")
        return pd.Timedelta(hours=int(h), minutes=int(m), seconds=int(sec))
    except Exception:
        return pd.Timedelta(0)

def _load_rawdata_csv(path, target_month):
    """rawdata.csv（DB正規化版・UTF-8）を AirRegi提供CSV互換の hdr / det DataFrame に変換する。

    rawdata.csv のスキーマ (一例):
        store_code, store_name, account_id, entry_at, exit_at, day_of_week,
        account_total, customer_count, item_count, has_reservation, is_course,
        menu_name, price, quantity, subtotal, category1, ordered_at, cost_rate
    """
    raw = pd.read_csv(path)
    # JST 化
    raw["entry_jst"] = pd.to_datetime(raw["entry_at"], utc=True).dt.tz_convert("Asia/Tokyo")
    raw["exit_jst"]  = pd.to_datetime(raw["exit_at"],  utc=True).dt.tz_convert("Asia/Tokyo")
    raw["dt"] = raw["exit_jst"]  # 会計日時 = exit
    raw["business_date"] = raw["dt"].apply(to_business_date)
    raw["business_month"] = pd.to_datetime(raw["business_date"]).dt.strftime("%Y-%m")
    raw = raw[raw["business_month"] == target_month].copy()

    # ヘッダー行（取引ごとに1行）
    hdr_src = raw.groupby("account_id", as_index=False).agg(
        total=("account_total", "first"),
        customers=("customer_count", "first"),
        bd=("business_date", "first"),
        bm=("business_month", "first"),
        entry=("entry_jst", "first"),
        exit_=("exit_jst", "first"),
    )
    def stay_str(r):
        try:
            td = (r["exit_"] - r["entry"])
            total = int(td.total_seconds())
            if total < 0: total = 0
            h, rem = divmod(total, 3600); m, s = divmod(rem, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"
        except Exception:
            return "00:00:00"
    hdr = pd.DataFrame({
        "取引No": hdr_src["account_id"],
        "合計":   hdr_src["total"],
        "人数":   hdr_src["customers"],
        "business_date": hdr_src["bd"],
        "business_month": hdr_src["bm"],
        "dt": hdr_src["exit_"],
        "滞在時間": hdr_src.apply(stay_str, axis=1),
    })

    # 明細行
    det = pd.DataFrame({
        "取引No": raw["account_id"],
        "メニュー名": raw["menu_name"],
        "カテゴリー名": raw["category1"],
        "価格": raw["price"],
        "注文数量": raw["quantity"],
        "business_date": raw["business_date"],
        "business_month": raw["business_month"],
    })
    return hdr, det

# ============================================
# 提供CSV読み込み（Shift-JIS）→ ヘッダー/明細分離
# ============================================
def load_provided_csv(path, target_month):
    """提供CSV(Shift-JIS／AirRegi)もしくは rawdata.csv(UTF-8／DB正規化) を読み込み、
    target_month に business_month が一致する会計を抽出する。

    Returns:
        hdr_df: ヘッダー行（合計あり）
        det_df: 明細行（カテゴリ＋メニュー名あり）
    """
    # 先頭バイトを覗いて rawdata.csv (UTF-8, "store_code"始まり) か AirRegi提供CSV(Shift-JIS) か判定
    with open(path, "rb") as fh:
        head = fh.read(64)
    if head.lstrip().startswith(b'"store_code"') or head.lstrip().startswith(b"store_code"):
        return _load_rawdata_csv(path, target_month)
    df = pd.read_csv(path, encoding="shift_jis")
    df["is_header"] = df["合計"].notna()
    df["is_detail"] = df["カテゴリー名"].notna() & df["メニュー名"].notna()

    df["dt"] = pd.to_datetime(df["会計日"] + " " + df["会計時間"], errors="coerce")
    df["business_date"] = df["dt"].apply(to_business_date)
    df["business_month"] = pd.to_datetime(df["business_date"]).dt.strftime("%Y-%m")

    # detail rows: business_dateをヘッダーから補完
    hdr_map = df[df["is_header"]].set_index("取引No")[["business_date","business_month","dt","人数"]]
    def fill(r, col):
        if r["is_header"]: return r[col]
        return hdr_map.loc[r["取引No"], col] if r["取引No"] in hdr_map.index else None
    for col in ["business_date","business_month"]:
        df[col] = df.apply(lambda r: fill(r, col), axis=1)

    df04 = df[df["business_month"] == target_month].copy()
    hdr04 = df04[df04["is_header"]].copy()
    det04 = df04[df04["is_detail"]].copy()
    return hdr04, det04

# ============================================
# Monthly KPI
# ============================================
def calc_monthly_kpi(hdr, det):
    """月次KPI（売上日時ベース）"""
    bottle_det = det[det["カテゴリー名"] == "ボトル購入"]
    bottle_accts = set(bottle_det["取引No"].unique())
    bottle_hdr = hdr[hdr["取引No"].isin(bottle_accts)]
    bottle_sales = float(bottle_hdr["合計"].sum())
    bottle_customers = int(bottle_hdr["人数"].sum())

    total = float(hdr["合計"].sum())
    customers = int(hdr["人数"].sum())
    accounts = len(hdr)
    biz_days = hdr["business_date"].nunique()
    excl_bottle = total - bottle_sales
    return {
        "sales_total": total,
        "bottle_sales": bottle_sales,
        "bottle_accounts": len(bottle_hdr),
        "bottle_customers": bottle_customers,
        "sales_excl_bottle": excl_bottle,
        "customers": customers,
        "accounts": accounts,
        "business_days": biz_days,
        "kyakutanka": excl_bottle / customers if customers else 0,           # 経営判断用
        "kyakutanka_with_bottle": total / customers if customers else 0,      # エアメイト比較用
        "daily_avg_sales": excl_bottle / biz_days if biz_days else 0,
        "daily_avg_sales_with_bottle": total / biz_days if biz_days else 0,
        "bottle_account_ids": list(bottle_accts),
    }

def kpi_from_rawdata(rawdata_path, month_str):
    """比較データ（前月／前年同月）を rawdata.csv から取得"""
    if not rawdata_path or not os.path.exists(rawdata_path): return None
    raw = pd.read_csv(rawdata_path)
    raw["entry_jst"] = pd.to_datetime(raw["entry_at"], utc=True).dt.tz_convert("Asia/Tokyo")
    raw["business_date"] = raw["entry_jst"].apply(to_business_date)
    raw["business_month"] = pd.to_datetime(raw["business_date"]).dt.strftime("%Y-%m")
    sub = raw[raw["business_month"] == month_str]
    if len(sub) == 0: return None
    acct = sub.groupby("account_id").agg(
        total=("account_total","first"),
        customers=("customer_count","first"),
        bd=("business_date","first"),
    ).reset_index()
    bottle_rows = sub[sub["category1"]=="ボトル購入"]
    bottle_sales = float(bottle_rows["subtotal"].sum())
    total = float(acct["total"].sum())
    customers = int(acct["customers"].sum())
    bd_unique = acct["bd"].nunique()
    excl_bottle = total - bottle_sales
    return {
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

# ============================================
# Weekly / Daily / Weekday / Hour (営業日基準・ボトル除外)
# ============================================
def calc_weekly(hdr_no_bottle):
    hdr_no_bottle = hdr_no_bottle.copy()
    hdr_no_bottle["bd_dt"] = pd.to_datetime(hdr_no_bottle["business_date"])
    hdr_no_bottle["year_week"] = hdr_no_bottle["bd_dt"].dt.strftime("%G-W%V")
    agg = hdr_no_bottle.groupby("year_week").agg(
        sales=("合計","sum"),
        customers=("人数","sum"),
        accounts=("取引No","count"),
        business_days=("business_date","nunique"),
    ).reset_index().sort_values("year_week")
    return [{
        "year_week": r["year_week"],
        "sales_excl_bottle": float(r["sales"]),
        "customers": int(r["customers"]),
        "accounts": int(r["accounts"]),
        "business_days": int(r["business_days"]),
        "kyakutanka": float(r["sales"]) / int(r["customers"]) if r["customers"] else 0,
        "daily_avg": float(r["sales"]) / int(r["business_days"]) if r["business_days"] else 0,
    } for _, r in agg.iterrows()]

def calc_daily(hdr_no_bottle):
    agg = hdr_no_bottle.groupby("business_date").agg(
        sales=("合計","sum"),
        customers=("人数","sum"),
        accounts=("取引No","count"),
    ).reset_index().sort_values("business_date")
    return [{"business_date": str(r["business_date"]),
             "sales_excl_bottle": float(r["sales"]),
             "customers": int(r["customers"]),
             "accounts": int(r["accounts"])} for _, r in agg.iterrows()]

def calc_weekday(hdr_no_bottle):
    wmap = {0:"月",1:"火",2:"水",3:"木",4:"金",5:"土",6:"日"}
    hdr_no_bottle = hdr_no_bottle.copy()
    hdr_no_bottle["weekday"] = pd.to_datetime(hdr_no_bottle["business_date"]).dt.dayofweek.map(wmap)
    agg = hdr_no_bottle.groupby("weekday").agg(
        total_sales=("合計","sum"),
        total_customers=("人数","sum"),
        total_accounts=("取引No","count"),
        business_days=("business_date","nunique"),
    ).reset_index()
    order = ["月","火","水","木","金","土","日"]
    agg["__o"] = agg["weekday"].apply(lambda x: order.index(x) if x in order else 99)
    agg = agg.sort_values("__o").drop(columns="__o")
    return [{
        "weekday": r["weekday"],
        "total_sales_excl_bottle": float(r["total_sales"]),
        "total_customers": int(r["total_customers"]),
        "total_accounts": int(r["total_accounts"]),
        "business_days": int(r["business_days"]),
        "daily_avg_sales": float(r["total_sales"]) / int(r["business_days"]) if r["business_days"] else 0,
        "daily_avg_customers": float(r["total_customers"]) / int(r["business_days"]) if r["business_days"] else 0,
        "kyakutanka": float(r["total_sales"]) / int(r["total_customers"]) if r["total_customers"] else 0,
    } for _, r in agg.iterrows()]

def calc_hour(hdr_no_bottle):
    hdr_no_bottle = hdr_no_bottle.copy()
    hdr_no_bottle["stay_td"] = hdr_no_bottle["滞在時間"].apply(parse_stay)
    hdr_no_bottle["entry_jst"] = hdr_no_bottle["dt"] - hdr_no_bottle["stay_td"]
    def gbh(d):
        if pd.isna(d): return None
        return d.hour + 24 if d.hour < 6 else d.hour
    hdr_no_bottle["business_hour"] = hdr_no_bottle["entry_jst"].apply(gbh)
    def hb(h):
        if h is None: return "other"
        if 18 <= h < 20: return "18-20"
        if 20 <= h < 22: return "20-22"
        if 22 <= h < 24: return "22-24"
        if 24 <= h < 26: return "24-26"
        return "other"
    hdr_no_bottle["hour_bucket"] = hdr_no_bottle["business_hour"].apply(hb)
    agg = hdr_no_bottle.groupby("hour_bucket").agg(
        sales=("合計","sum"),
        customers=("人数","sum"),
        accounts=("取引No","count"),
    ).reset_index()
    hour_order = ["18-20","20-22","22-24","24-26","other"]
    agg["__o"] = agg["hour_bucket"].apply(lambda x: hour_order.index(x) if x in hour_order else 99)
    agg = agg.sort_values("__o").drop(columns="__o")
    total = agg["sales"].sum()
    agg["share"] = agg["sales"] / total * 100 if total else 0
    return [{
        "hour_bucket": r["hour_bucket"],
        "sales_excl_bottle": float(r["sales"]),
        "customers": int(r["customers"]),
        "accounts": int(r["accounts"]),
        "share": float(r["share"]),
    } for _, r in agg.iterrows()]

# ============================================
# Category breakdown
# ============================================
def calc_category(det):
    det = det.copy()
    det["subtotal"] = det["価格"] * det["注文数量"]
    cat = det.groupby("カテゴリー名").agg(
        sales=("subtotal","sum"),
        qty=("注文数量","sum"),
    ).reset_index()
    total = cat["sales"].sum()
    cat["share"] = cat["sales"] / total * 100 if total else 0
    cat = cat.sort_values("sales", ascending=False)
    return [{"category1": r["カテゴリー名"], "sales": float(r["sales"]),
             "qty": float(r["qty"]), "share": float(r["share"])}
            for _, r in cat.head(15).iterrows()]

# ============================================
# P1-1〜P1-6
# ============================================
def calc_p1(hdr, det, kpi_total_sales, kpi_customers):
    """P1-1〜P1-6 を一括計算"""
    out = {}

    def make_section(label, accts_set, note=None):
        section_hdr = hdr[hdr["取引No"].isin(accts_set)]
        sales = float(section_hdr["合計"].sum())
        customers = int(section_hdr["人数"].sum())
        d = {
            "label": label,
            "accounts": len(section_hdr),
            "customers": customers,
            "sales": sales,
            "share_sales": sales / kpi_total_sales * 100 if kpi_total_sales else 0,
            "share_customers": customers / kpi_customers * 100 if kpi_customers else 0,
        }
        if note: d["note"] = note
        return d

    # P1-1 インバウンド（メモ「海外」）
    if "メモ" in hdr.columns:
        inb_hdr = hdr[hdr["メモ"].fillna("").str.contains("海外", na=False)]
    else:
        inb_hdr = hdr.iloc[0:0]  # メモ列が無いCSVに備える
    out["p1_1_inbound"] = {
        "label": "インバウンド（メモ「海外」）",
        "accounts": len(inb_hdr),
        "customers": int(inb_hdr["人数"].sum()),
        "sales": float(inb_hdr["合計"].sum()),
        "share_sales": float(inb_hdr["合計"].sum()) / kpi_total_sales * 100 if kpi_total_sales else 0,
        "share_customers": int(inb_hdr["人数"].sum()) / kpi_customers * 100 if kpi_customers else 0,
    }
    # P1-2 CLP社員（メニュー名「CLP」部分一致）
    clp_det = det[det["メニュー名"].fillna("").str.contains("CLP", na=False)]
    out["p1_2_clp_employee"] = make_section("CLP社員（メニュー名「CLP」）", set(clp_det["取引No"].unique()))
    # P1-3 イベント
    ev_det = det[det["カテゴリー名"] == "イベント"]
    out["p1_3_event"] = make_section("イベント（カテゴリ「イベント」）", set(ev_det["取引No"].unique()))
    # P1-4 ボトル購入
    bot_det = det[det["カテゴリー名"] == "ボトル購入"]
    out["p1_4_bottle"] = make_section("ボトル購入（カテゴリ「ボトル購入」）", set(bot_det["取引No"].unique()))
    # P1-5 コース
    co_det = det[det["カテゴリー名"] == "コース&セット"]
    out["p1_5_course"] = make_section("コース（カテゴリ「コース&セット」）", set(co_det["取引No"].unique()))
    # P1-6 その他CLPコース（メニュー名完全一致）
    clpc_det = det[det["メニュー名"] == "その他CLPコース"]
    out["p1_6_clp_course"] = make_section("その他CLPコース（メニュー名）", set(clpc_det["取引No"].unique()))
    return out

# ============================================
# P1-7 / P1-8 ランキング
# ============================================
def calc_rank(det, hdr, cls, by, top_n=15):
    det = det.copy()
    det["subtotal"] = det["価格"] * det["注文数量"]
    det["class"] = det["カテゴリー名"].apply(classify)
    sub = det[det["class"] == cls]
    if len(sub) == 0: return []
    acct_cust = dict(zip(hdr["取引No"], hdr["人数"]))
    menu_to_accts = sub.groupby("メニュー名")["取引No"].apply(lambda s: list(set(s))).reset_index()
    menu_cust = {r["メニュー名"]: sum(int(acct_cust.get(a, 0)) for a in r["取引No"])
                 for _, r in menu_to_accts.iterrows()}
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
            for _, r in agg.head(top_n).iterrows()]

# ============================================
# Daily reports
# ============================================
def load_daily_reports(daily_csv, target_month):
    if not daily_csv or not os.path.exists(daily_csv): return []
    dr = pd.read_csv(daily_csv)
    sub = dr[dr["営業日"].astype(str).str.startswith(target_month)]
    return sub.to_dict("records")

# ============================================
# PL分析（v2.1 新設・2026-05-18 イテレーション9恒久反映）
# ============================================
#   - 当月PL: --pl-source dashboard-db で --pl-dashboard-dump（JSON）から取得
#   - 過去月PL: --pl-source sheet で --pl-sheet-parsed（JSON）から取得
#   - 出典は分類条件帯で明示（HTMLビルダー側）
# ============================================

def calc_fl_rate(food_cost, drink_cost, total_sales):
    """FL率 = (食材+ドリンク) ÷ 月次総売上（ボトル含む）"""
    if not total_sales:
        return None
    return (food_cost + drink_cost) / total_sales * 100

def calc_labor_rate(labor_cost, total_sales):
    """人件費率 = 人件費 ÷ 月次総売上（ボトル含む）"""
    if not total_sales:
        return None
    return labor_cost / total_sales * 100

def calc_op_profit(total_sales, total_expense):
    """営業利益 = 売上 − 総費用"""
    return total_sales - total_expense

def calc_op_profit_rate(total_sales, total_expense):
    """営業利益率 = 営業利益 ÷ 売上"""
    if not total_sales:
        return None
    return (total_sales - total_expense) / total_sales * 100

def load_pl_dashboard_dump(json_path):
    """ダッシュボードDBダンプJSONを読み込む（当月用）

    期待スキーマ:
        {
          "expenseCategories": [{"id":..., "name":...}, ...],
          "monthlyExpenses": [{"year_month":"YYYY-MM", "category_id":..., "total":"...."}, ...],
          "monthlySales":    [{"year_month":"YYYY-MM", "total":"..."}, ...]   (optional)
        }
    """
    with open(json_path) as f:
        raw = json.load(f)
    exp_cat_map = {c["id"]: c["name"] for c in raw["expenseCategories"]}
    monthly_exp = {}      # {ym: {cat_name: total}}
    monthly_exp_total = {}
    for e in raw["monthlyExpenses"]:
        ym = e["year_month"]
        cat = exp_cat_map.get(e["category_id"], "その他")
        v = float(e["total"])
        monthly_exp.setdefault(ym, {})[cat] = v
        monthly_exp_total[ym] = monthly_exp_total.get(ym, 0) + v
    monthly_sales_pl = {}
    for s in raw.get("monthlySales", []):
        ym = s["year_month"]
        monthly_sales_pl[ym] = monthly_sales_pl.get(ym, 0) + float(s["total"])
    return {
        "expenses_by_month": monthly_exp,
        "expense_totals": monthly_exp_total,
        "sales_by_month": monthly_sales_pl,
    }

def load_pl_sheet_parsed(json_path):
    """【BFA】本部サポート / PLシート のパース結果JSONを読み込む（過去月用）

    期待スキーマ（推奨）:
        {
          "expenses_by_month": {"YYYY-MM": {"家賃": 1234567, "ドリンク": ...}, ...},
          "expense_totals":    {"YYYY-MM": 1234567, ...},
          "sales_by_month":    {"YYYY-MM": 1234567, ...}
        }

    互換のため、 dashboard-db ダンプ形式も受け付ける（categoriesがあれば変換）
    """
    with open(json_path) as f:
        raw = json.load(f)
    if "expenseCategories" in raw and "monthlyExpenses" in raw:
        # dashboard 形式
        return load_pl_dashboard_dump(json_path)
    return {
        "expenses_by_month": raw.get("expenses_by_month", {}),
        "expense_totals": raw.get("expense_totals", {}),
        "sales_by_month": raw.get("sales_by_month", {}),
    }

def build_pl_data(target_month, pl_source_current, pl_source_past, total_sales_target):
    """月報用PLデータをまとめる

    Args:
        target_month: 対象月 YYYY-MM
        pl_source_current: dict (当月分のPLデータ) {expenses_by_month, expense_totals, sales_by_month}
        pl_source_past: dict (過去月分) 同形式 or None
        total_sales_target: 対象月の月次総売上（ボトル含む）

    Returns:
        analysis.json に入れる "pl" セクション
    """
    # 当月データ
    apr_exp = pl_source_current["expenses_by_month"].get(target_month, {})
    apr_exp_total = pl_source_current["expense_totals"].get(target_month, 0)
    # 過去月用ソースに当月分が入っているケースにも対応
    if (not apr_exp or apr_exp_total == 0) and pl_source_past:
        if target_month in pl_source_past.get("expenses_by_month", {}):
            apr_exp = pl_source_past["expenses_by_month"].get(target_month, {})
            apr_exp_total = pl_source_past["expense_totals"].get(target_month, 0)
    fl_cost = apr_exp.get("食材", 0) + apr_exp.get("ドリンク", 0)
    labor_cost = apr_exp.get("人件費", 0)
    op_profit = calc_op_profit(total_sales_target, apr_exp_total)
    op_profit_rate = calc_op_profit_rate(total_sales_target, apr_exp_total)
    fl_rate = calc_fl_rate(apr_exp.get("食材", 0), apr_exp.get("ドリンク", 0), total_sales_target)
    labor_rate = calc_labor_rate(labor_cost, total_sales_target)

    # 費目別ランキング
    exp_breakdown = sorted(
        [{"category": cat, "amount": amt,
          "share": (amt / total_sales_target * 100) if total_sales_target else 0}
         for cat, amt in apr_exp.items()],
        key=lambda x: -x["amount"]
    )

    # 推移用（当月＋過去月をマージ）
    all_expenses = dict(pl_source_current["expenses_by_month"])
    all_totals = dict(pl_source_current["expense_totals"])
    all_sales = dict(pl_source_current.get("sales_by_month", {}))
    source_per_month = {m: "ダッシュボードDB" for m in all_expenses.keys()}
    if pl_source_past:
        for ym, ex in pl_source_past["expenses_by_month"].items():
            if ym not in all_expenses:
                all_expenses[ym] = ex
                source_per_month[ym] = "【BFA】本部サポート / PLシート"
        for ym, tot in pl_source_past["expense_totals"].items():
            all_totals.setdefault(ym, tot)
        for ym, sl in pl_source_past.get("sales_by_month", {}).items():
            all_sales.setdefault(ym, sl)

    # 当月売上はエアレジを優先
    all_sales[target_month] = total_sales_target

    pl_trend = []
    for ym in sorted(all_expenses.keys()):
        ex = all_expenses.get(ym, {})
        total = all_totals.get(ym, 0)
        sales = all_sales.get(ym, 0)
        pl_trend.append({
            "month": ym,
            "sales": sales,
            "total_expense": total,
            "op_profit": calc_op_profit(sales, total) if sales else -total,
            "op_profit_rate": calc_op_profit_rate(sales, total) if sales else None,
            "fl_rate": calc_fl_rate(ex.get("食材", 0), ex.get("ドリンク", 0), sales) if sales else None,
            "labor_rate": calc_labor_rate(ex.get("人件費", 0), sales) if sales else None,
            "exp_breakdown": ex,
            "source": source_per_month.get(ym, "—"),
        })

    months_available = sorted(all_expenses.keys())
    # 当月の費用データが取れていなければ「available=False」として
    # 上流のHTMLビルダーに「データなし」スライド表示を任せる
    target_has_data = (apr_exp_total > 0) or (len(apr_exp) > 0)
    return {
        "available": bool(target_has_data),
        "unavailable_reason": None if target_has_data else (
            "【BFA】本部サポート / PLシート に対象月のデータがないため出力していません"
        ),
        "month_target": target_month,
        "expense_total": apr_exp_total,
        "op_profit": op_profit,
        "op_profit_rate": op_profit_rate,
        "fl_cost": fl_cost,
        "fl_rate": fl_rate,
        "labor_cost": labor_cost,
        "labor_rate": labor_rate,
        "expense_breakdown": exp_breakdown,
        "trend": pl_trend,
        "months_available": months_available,
        "source_current": "ダッシュボードDB",
        "source_past": "【BFA】本部サポート / PLシート",
        "sales_for_pl_calc": total_sales_target,
        "fl_denominator_note": "FL率の分母 = 月次総売上（ボトル含む）",
    }

# ============================================
# Main
# ============================================
def main():
    p = argparse.ArgumentParser(description="月報パイプライン（汎用化版 v2.1 ／ PL対応）")
    p.add_argument("--target-month", required=True, help="対象月 YYYY-MM (例: 2026-04)")
    p.add_argument("--store-code", required=True, help="店舗コード (例: BFA)")
    p.add_argument("--sales-csv", required=True, help="提供CSV (会計明細_YYYYMMDD-YYYYMMDD.csv, Shift-JIS)")
    p.add_argument("--output-dir", required=True, help="出力ディレクトリ (analysis.json)")
    p.add_argument("--compare-rawdata", help="比較データ用 rawdata.csv（前月／前年同月）")
    p.add_argument("--daily-report-csv", help="日報CSV")
    # PL関連（v2.1 新設）
    p.add_argument("--pl-source", choices=["dashboard-db", "sheet", "both"], default=None,
                   help="PLデータ取得元。dashboard-db=当月用ダンプJSON、sheet=過去月用PLシートJSON、both=両方併用")
    p.add_argument("--pl-dashboard-dump", help="ダッシュボードDBダンプJSON（当月PL用）")
    p.add_argument("--pl-sheet-parsed", help="【BFA】本部サポート/PLシートのパース結果JSON（過去月PL用）")
    args = p.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 1) 提供CSV読み込み
    print(f"[{args.store_code} {args.target_month}] Loading: {args.sales_csv}")
    hdr, det = load_provided_csv(args.sales_csv, args.target_month)
    print(f"  Header rows (accounts): {len(hdr)}")
    print(f"  Detail rows: {len(det)}")

    # 2) Monthly KPI
    kpi = calc_monthly_kpi(hdr, det)
    print(f"  Monthly total: ¥{kpi['sales_total']:,.0f}")
    print(f"  Bottle: ¥{kpi['bottle_sales']:,.0f} ({kpi['bottle_accounts']} accounts)")
    print(f"  Customers: {kpi['customers']}, Business days: {kpi['business_days']}")

    # 3) Bottle 除外
    bottle_ids = set(kpi["bottle_account_ids"])
    hdr_no_bottle = hdr[~hdr["取引No"].isin(bottle_ids)].copy()

    # 4) 各集計
    weekly = calc_weekly(hdr_no_bottle)
    daily_list = calc_daily(hdr_no_bottle)
    weekday = calc_weekday(hdr_no_bottle)
    hour = calc_hour(hdr_no_bottle)
    category = calc_category(det)
    p1 = calc_p1(hdr, det, kpi["sales_total"], kpi["customers"])
    p1_7_food = calc_rank(det, hdr, "food", "qty")
    p1_7_drink = calc_rank(det, hdr, "drink", "qty")
    p1_8_food = calc_rank(det, hdr, "food", "sales")
    p1_8_drink = calc_rank(det, hdr, "drink", "sales")

    # 5) 比較データ（rawdata.csv から）
    month_kpis = {args.target_month: {**kpi, "month": args.target_month, "source": "提供CSV"}}
    if args.compare_rawdata:
        y, m = map(int, args.target_month.split("-"))
        # 直近6ヶ月＋前年同月
        for offset in range(1, 6):
            m2 = m - offset
            y2 = y
            while m2 <= 0:
                m2 += 12; y2 -= 1
            label = f"{y2}-{m2:02d}"
            k = kpi_from_rawdata(args.compare_rawdata, label)
            if k:
                k["month"] = label
                k["source"] = "ダッシュボード経由"
                month_kpis[label] = k
        # 前年同月
        py_label = f"{y-1}-{m:02d}"
        k = kpi_from_rawdata(args.compare_rawdata, py_label)
        if k:
            k["month"] = py_label
            k["source"] = "ダッシュボード経由"
            month_kpis[py_label] = k

    # 6) 日報
    daily_reports = load_daily_reports(args.daily_report_csv, args.target_month)

    # 6-α) PL データ（v2.1 新設）
    pl_data = {"available": False, "reason": "PLソース未指定"}
    if args.pl_source:
        try:
            current = None
            past = None
            if args.pl_source in ("dashboard-db", "both") and args.pl_dashboard_dump:
                current = load_pl_dashboard_dump(args.pl_dashboard_dump)
                print(f"  PL current loaded: {len(current['expenses_by_month'])} months from dashboard-db dump")
            if args.pl_source in ("sheet", "both") and args.pl_sheet_parsed:
                past = load_pl_sheet_parsed(args.pl_sheet_parsed)
                print(f"  PL past loaded: {len(past['expenses_by_month'])} months from PL sheet")
            # sheet 単独指定なら sheet を current 扱いに
            if not current and past:
                current = past
                past = None
            if current:
                pl_data = build_pl_data(args.target_month, current, past, kpi["sales_total"])
                if pl_data["available"]:
                    print(f"  PL ─ 総費用: ¥{pl_data['expense_total']:,.0f}  営業利益: ¥{pl_data['op_profit']:,.0f} ({pl_data['op_profit_rate']:+.1f}%)")
                    print(f"      FL率: {pl_data['fl_rate']:.1f}%  人件費率: {pl_data['labor_rate']:.1f}%")
        except Exception as e:
            pl_data = {"available": False, "error": str(e)}
            print(f"  PL load failed: {e}")

    # 7) Output
    out = {
        "target_month": args.target_month,
        "store_code": args.store_code,
        "generated_at": pd.Timestamp.now(tz="Asia/Tokyo").isoformat(),
        "data_source": {
            "main_sales": args.sales_csv,
            "comparison_rawdata": args.compare_rawdata,
            "daily_reports": args.daily_report_csv,
            "pl_dashboard_dump": args.pl_dashboard_dump,
            "pl_sheet_parsed": args.pl_sheet_parsed,
        },
        "month_kpis": month_kpis,
        "weekly": weekly,
        "daily": daily_list,
        "weekday": weekday,
        "hour": hour,
        "category": category,
        **p1,
        "p1_7_food_qty": p1_7_food,
        "p1_7_drink_qty": p1_7_drink,
        "p1_8_food_sales": p1_8_food,
        "p1_8_drink_sales": p1_8_drink,
        "daily_reports": daily_reports,
        "pl": pl_data,
    }

    def default(o):
        if isinstance(o, (pd.Timestamp, date)): return str(o)
        if hasattr(o, "item"): return o.item()
        return str(o)

    out_path = os.path.join(args.output_dir, "analysis.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=default)

    print(f"\n✓ analysis.json written → {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
