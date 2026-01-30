#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月別KPI（営業日あたり）を生成し、推移グラフを出力する。

- 対象: BIFTEKI互換の中間CSV（transformed_pos_data_eatin.csv）
- 集計単位: 伝票（=1組）
- Daypart: 入店時刻（H.伝票発行日）の hour により
    - Lunch: <16
    - Dinner: >=16
- 除外: 3月（月=3）は除外（部分データの混入を避ける）

出力:
- reports/monthly_kpis.csv（合計/Lunch/Dinnerの月次KPI）
- reports/monthly_sales_per_day.png
- reports/monthly_customers_per_day.png
- reports/monthly_spend_per_customer.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm


def set_japanese_font() -> None:
    candidates = ["Hiragino Sans", "AppleGothic", "Apple SD Gothic Neo", "Arial Unicode MS", "Yu Gothic", "Meiryo"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store-root", required=True)
    parser.add_argument("--input", default=None, help="中間CSV（未指定なら <store-root>/data/intermediate/transformed_pos_data_eatin.csv）")
    parser.add_argument("--out-dir", default=None, help="出力先（未指定なら <store-root>/reports）")
    parser.add_argument("--cutoff-hour", type=int, default=16, help="ランチ/ディナー境界（入店時刻のhour）")
    parser.add_argument("--exclude-month", type=int, default=3, help="除外する月（デフォルト: 3月）")
    args = parser.parse_args()

    store_root = Path(args.store_root).resolve()
    input_csv = Path(args.input) if args.input else store_root / "data/intermediate/transformed_pos_data_eatin.csv"
    out_dir = Path(args.out_dir) if args.out_dir else store_root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    set_japanese_font()

    usecols = ["H.伝票番号", "H.集計対象営業年月日", "H.伝票発行日", "H.客数（合計）", "H.小計"]
    df = pd.read_csv(input_csv, usecols=usecols)

    # 伝票単位にユニーク化
    slip = df.drop_duplicates(subset=["H.伝票番号"]).copy()
    slip["biz_date"] = pd.to_datetime(slip["H.集計対象営業年月日"], errors="coerce")
    slip["entry_dt"] = pd.to_datetime(slip["H.伝票発行日"], errors="coerce")
    slip["sales"] = pd.to_numeric(slip["H.小計"], errors="coerce").fillna(0)
    slip["customers"] = pd.to_numeric(slip["H.客数（合計）"], errors="coerce").fillna(0)
    slip = slip.dropna(subset=["biz_date", "entry_dt"])
    slip = slip[slip["customers"] > 0]

    slip["y"] = slip["biz_date"].dt.year
    slip["m"] = slip["biz_date"].dt.month
    # 3月除外
    if args.exclude_month:
        slip = slip[slip["m"] != args.exclude_month]

    slip["daypart"] = slip["entry_dt"].dt.hour.apply(lambda h: "Lunch" if int(h) < args.cutoff_hour else "Dinner")

    # 日次（daypart別）
    by_day_part = slip.groupby(["biz_date", "daypart"]).agg(
        sales=("sales", "sum"),
        customers=("customers", "sum"),
        tickets=("H.伝票番号", "count"),
    ).reset_index()
    by_day_part["y"] = by_day_part["biz_date"].dt.year
    by_day_part["m"] = by_day_part["biz_date"].dt.month

    # 月次KPI（daypart別）
    month_part = by_day_part.groupby(["y", "m", "daypart"]).agg(
        operating_days=("biz_date", "nunique"),
        sales=("sales", "sum"),
        customers=("customers", "sum"),
        tickets=("tickets", "sum"),
    ).reset_index()
    month_part["sales_per_day"] = month_part["sales"] / month_part["operating_days"]
    month_part["customers_per_day"] = month_part["customers"] / month_part["operating_days"]
    month_part["spend_per_customer"] = month_part["sales"] / month_part["customers"].replace({0: pd.NA})

    # 月次KPI（合計）
    by_day_total = slip.groupby(["biz_date"]).agg(
        sales=("sales", "sum"),
        customers=("customers", "sum"),
        tickets=("H.伝票番号", "count"),
    ).reset_index()
    by_day_total["y"] = by_day_total["biz_date"].dt.year
    by_day_total["m"] = by_day_total["biz_date"].dt.month
    month_total = by_day_total.groupby(["y", "m"]).agg(
        operating_days=("biz_date", "nunique"),
        sales=("sales", "sum"),
        customers=("customers", "sum"),
        tickets=("tickets", "sum"),
    ).reset_index()
    month_total["sales_per_day"] = month_total["sales"] / month_total["operating_days"]
    month_total["customers_per_day"] = month_total["customers"] / month_total["operating_days"]
    month_total["spend_per_customer"] = month_total["sales"] / month_total["customers"].replace({0: pd.NA})
    month_total["daypart"] = "Total"

    out_df = pd.concat([month_total, month_part], ignore_index=True).sort_values(["y", "m", "daypart"])
    out_df.to_csv(out_dir / "monthly_kpis.csv", index=False, encoding="utf-8")

    # plot helpers
    def plot_metric(metric: str, title: str, ylabel: str, filename: str) -> None:
        # x-axis: yyyy/mm
        xkeys = month_total.sort_values(["y", "m"])[["y", "m"]].drop_duplicates()
        xlabels = [f"{int(y)}/{int(m):02d}" for y, m in zip(xkeys["y"], xkeys["m"])]

        def series_for(dp: str) -> list[float]:
            src = out_df[out_df["daypart"] == dp].copy()
            src = src.merge(xkeys, on=["y", "m"], how="right").sort_values(["y", "m"])
            return src[metric].astype(float).fillna(0).tolist()

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(xlabels, series_for("Total"), marker="o", label="合計")
        ax.plot(xlabels, series_for("Lunch"), marker="o", label=f"ランチ（入店<{args.cutoff_hour}時）")
        ax.plot(xlabels, series_for("Dinner"), marker="o", label=f"ディナー（入店>={args.cutoff_hour}時）")
        ax.set_title(title)
        ax.set_xlabel("月（3月除外）")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(out_dir / filename, dpi=150)
        plt.close()

    plot_metric("sales_per_day", "月別：営業日あたり売上（合計/ランチ/ディナー）", "売上（円/日）", "monthly_sales_per_day.png")
    plot_metric("customers_per_day", "月別：営業日あたり客数（合計/ランチ/ディナー）", "客数（人/日）", "monthly_customers_per_day.png")
    plot_metric("spend_per_customer", "月別：客単価（合計/ランチ/ディナー）", "客単価（円/人）", "monthly_spend_per_customer.png")

    print("wrote:", out_dir / "monthly_kpis.csv")
    print("wrote:", out_dir / "monthly_sales_per_day.png")
    print("wrote:", out_dir / "monthly_customers_per_day.png")
    print("wrote:", out_dir / "monthly_spend_per_customer.png")


if __name__ == "__main__":
    main()

