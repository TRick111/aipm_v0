"""
過去4週分のTZバグ影響度調査 - 独立再計算スクリプト

目的:
  rawdata.csv を JST naive のまま直読みし、業務日（朝6時境界）で再集計する。
  既存 Scripts/* には一切依存しない独立ロジック。

仕様:
  - entry_at: JST naive 文字列 → pd.to_datetime() でそのまま読む（utc=True を絶対に付けない）
  - business_date: (entry_at - 6h).date()   （0-5時台を前日営業日として括る）
  - year_week:    business_date の ISO週 (%G-W%V)
  - 集計単位:     account_id 重複排除 → drop_duplicates でユニーク会計のみ
  - KPI:
      売上    = sum(account_total)
      客数    = sum(customer_count)
      組数    = nunique(account_id)
      客単価  = 売上 / 客数  ※既存JSONの定義と整合（per-customer）
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent

STORES = {
    "BFA": ("bfa-001", ROOT / "1_input" / "BFA" / "rawdata.csv"),
    "麻布しき": ("shiki-001", ROOT / "1_input" / "麻布しき" / "rawdata.csv"),
}

TARGET_WEEKS = ["2026-W19", "2026-W20", "2026-W21", "2026-W22"]
# ISO週 → 月曜〜日曜の業務日範囲
WEEK_RANGES = {
    "2026-W19": ("2026-05-04", "2026-05-10"),
    "2026-W20": ("2026-05-11", "2026-05-17"),
    "2026-W21": ("2026-05-18", "2026-05-24"),
    "2026-W22": ("2026-05-25", "2026-05-31"),
}


def load_and_prepare(store_code: str, path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"store_code": "string"})
    df = df[df["store_code"] == store_code].copy()
    # JST naive のまま読む（utc=True 禁止）
    df["entry_at"] = pd.to_datetime(df["entry_at"], errors="coerce")
    df = df.dropna(subset=["entry_at"]).copy()
    # 業務日: 朝6時境界
    df["biz_date"] = (df["entry_at"] - pd.Timedelta(hours=6)).dt.date
    df["biz_dt"] = pd.to_datetime(df["biz_date"])
    df["year_week"] = df["biz_dt"].dt.strftime("%G-W%V")
    df["weekday"] = df["biz_dt"].dt.strftime("%a")  # Mon..Sun
    df["hour"] = df["entry_at"].dt.hour
    # account_total / customer_count を数値化
    df["account_total"] = pd.to_numeric(df["account_total"], errors="coerce")
    df["customer_count"] = pd.to_numeric(df["customer_count"], errors="coerce")
    return df


def weekly_kpi(df: pd.DataFrame) -> pd.DataFrame:
    """account_id 単位で重複排除してから週次集計"""
    acc = df.drop_duplicates(subset="account_id", keep="first").copy()
    g = (
        acc.groupby("year_week")
        .agg(
            sales=("account_total", "sum"),
            customers=("customer_count", "sum"),
            accounts=("account_id", "nunique"),
        )
        .reset_index()
    )
    g["客単価"] = g["sales"] / g["customers"]
    return g


def weekday_kpi(df: pd.DataFrame, year_week: str) -> pd.DataFrame:
    acc = df[df["year_week"] == year_week].drop_duplicates(subset="account_id").copy()
    g = (
        acc.groupby(["biz_dt", "weekday"])
        .agg(
            sales=("account_total", "sum"),
            customers=("customer_count", "sum"),
            accounts=("account_id", "nunique"),
        )
        .reset_index()
        .sort_values("biz_dt")
    )
    g["客単価"] = g["sales"] / g["customers"]
    return g


def hourly_dist(df: pd.DataFrame, year_week: str) -> pd.DataFrame:
    """対象週の時間帯別売上（entry_at の hour 直読み）。account_id重複排除した会計単位。"""
    sub = df[df["year_week"] == year_week].drop_duplicates(subset="account_id").copy()
    g = (
        sub.groupby("hour")
        .agg(sales=("account_total", "sum"), accounts=("account_id", "nunique"))
        .reset_index()
    )
    total = g["sales"].sum()
    g["share"] = g["sales"] / total if total else 0
    return g


def main() -> int:
    summary = {}
    weekday_dump = {}
    hourly_dump = {}
    raw_diag = {}

    for shop_name, (store_code, path) in STORES.items():
        print(f"=== {shop_name} ({store_code}) ===", file=sys.stderr)
        df = load_and_prepare(store_code, path)
        # フィルタ: W19-W22 のみ
        sub = df[df["year_week"].isin(TARGET_WEEKS)].copy()

        wk = weekly_kpi(sub)
        # week ごとに比較しやすい辞書化
        summary[shop_name] = {}
        for _, row in wk.iterrows():
            summary[shop_name][row["year_week"]] = {
                "売上": float(row["sales"]),
                "客数": int(row["customers"]) if pd.notna(row["customers"]) else 0,
                "組数": int(row["accounts"]),
                "客単価": float(row["客単価"]) if pd.notna(row["客単価"]) else 0.0,
            }

        weekday_dump[shop_name] = {}
        hourly_dump[shop_name] = {}
        for w in TARGET_WEEKS:
            wd = weekday_kpi(df, w)
            weekday_dump[shop_name][w] = [
                {
                    "biz_dt": r["biz_dt"].strftime("%Y-%m-%d"),
                    "weekday": r["weekday"],
                    "sales": float(r["sales"]),
                    "customers": int(r["customers"]) if pd.notna(r["customers"]) else 0,
                    "accounts": int(r["accounts"]),
                    "客単価": float(r["客単価"]) if pd.notna(r["客単価"]) else 0.0,
                }
                for _, r in wd.iterrows()
            ]
            hr = hourly_dist(df, w)
            hourly_dump[shop_name][w] = [
                {
                    "hour": int(r["hour"]),
                    "sales": float(r["sales"]),
                    "accounts": int(r["accounts"]),
                    "share": float(r["share"]) if pd.notna(r["share"]) else 0.0,
                }
                for _, r in hr.iterrows()
            ]

        # 診断: 21時以降 / 0-5時 の構成比
        sub_all = df[df["year_week"].isin(TARGET_WEEKS)].drop_duplicates("account_id")
        h = sub_all["hour"]
        total_sales = sub_all["account_total"].sum()
        late_eve = sub_all[h.between(21, 23)]["account_total"].sum()
        midnight = sub_all[h.between(0, 5)]["account_total"].sum()
        raw_diag[shop_name] = {
            "total_sales_W19_W22": float(total_sales),
            "share_21_23": float(late_eve / total_sales) if total_sales else 0.0,
            "share_0_5": float(midnight / total_sales) if total_sales else 0.0,
            "n_accounts_W19_W22": int(sub_all["account_id"].nunique()),
        }

    out = {
        "method": "JST直読み・朝6時境界・account_id重複排除",
        "weekly_kpi": summary,
        "weekday_breakdown": weekday_dump,
        "hourly_distribution": hourly_dump,
        "diagnostics": raw_diag,
    }
    out_path = OUT_DIR / "correct_values.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"wrote: {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
