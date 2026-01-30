#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE BIFTEKI 川崎店: 売上分析パイプライン（Flow用）

目的:
- data/input/*.csv（cp932 + 先頭10行メタ + 11行目ヘッダ）を統合
- EAT INのみを抽出し、data/output に分析用ファイルを揃える
- 図表（reports/*.png, charts/y2y/*.png）と中間レポート（reports/*.md）を生成

実行:
  /usr/bin/python3 scripts/run_pipeline.py
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np


STORE_NAME = "THE BIFTEKI 川崎店"
PERIOD_A_START = pd.Timestamp("2025-01-01")
PERIOD_A_END = pd.Timestamp("2025-03-31")
PERIOD_B_START = pd.Timestamp("2025-10-01")
PERIOD_B_END = pd.Timestamp("2025-12-31")


@dataclass(frozen=True)
class Paths:
    project_dir: Path

    @property
    def input_dir(self) -> Path:
        return self.project_dir / "data" / "input"

    @property
    def intermediate_dir(self) -> Path:
        return self.project_dir / "data" / "intermediate"

    @property
    def output_dir(self) -> Path:
        return self.project_dir / "data" / "output"

    @property
    def reports_dir(self) -> Path:
        return self.project_dir / "reports"

    @property
    def charts_y2y_dir(self) -> Path:
        return self.project_dir / "charts" / "y2y"

    @property
    def mplconfig_dir(self) -> Path:
        return self.project_dir / ".mplconfig"

    @property
    def scripts_dir(self) -> Path:
        return self.project_dir / "scripts"


def run(cmd: list[str], cwd: Path, env: dict[str, str]) -> None:
    print(f"\n$ (cd {cwd}) {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd), env=env, check=True)


def merge_inputs_to_intermediate(paths: Paths) -> Path:
    """
    input/*.csv（先頭10行メタ）を統合し、
    intermediate/merged_pos_data.csv（ヘッダ+データのみ）を生成する。
    """
    in_files = sorted(paths.input_dir.glob("*.csv"))
    if not in_files:
        raise FileNotFoundError(f"input CSV not found: {paths.input_dir}")

    out_path = paths.intermediate_dir / "merged_pos_data.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    encoding = "cp932"
    canonical_cols: list[str] | None = None
    total_rows = 0

    def read_header_cols(fp: Path) -> list[str]:
        with open(fp, "r", encoding=encoding, newline="") as rf:
            # 先頭10行はメタ情報、11行目がCSVヘッダ
            for _ in range(10):
                next(rf)
            header_line = next(rf)
        cols = next(csv.reader([header_line]))
        return [c.strip() for c in cols]

    # 1) canonical header を決める（最初のファイルから）
    canonical_cols = read_header_cols(in_files[0])
    # たまにオーダーメモ列が入るケースがあるため、下流が期待する列だけに正規化する
    # （transform_pos_data.py 等は D.オーダー日時 を使うが D.オーダーメモ は使わない）
    if "D.オーダーメモ" in canonical_cols:
        canonical_cols = [c for c in canonical_cols if c != "D.オーダーメモ"]

    # 2) 出力（列名ベースで整列して書き出し）
    with open(out_path, "w", encoding=encoding, newline="") as wf:
        writer = csv.writer(wf, lineterminator="\n", quoting=csv.QUOTE_ALL)
        writer.writerow(canonical_cols)

        for f in in_files:
            file_cols = read_header_cols(f)
            # 余計な列は無視、足りない列は空で埋める
            if "D.オーダーメモ" in file_cols and "D.オーダーメモ" not in canonical_cols:
                pass

            idx_map = {c: i for i, c in enumerate(file_cols)}
            with open(f, "r", encoding=encoding, newline="") as rf:
                # skip meta + header line
                for _ in range(11):
                    next(rf)
                reader = csv.reader(rf)
                for row in reader:
                    out_row = []
                    for col in canonical_cols:
                        j = idx_map.get(col)
                        out_row.append(row[j] if (j is not None and j < len(row)) else "")
                    writer.writerow(out_row)
                    total_rows += 1

    print(f"[OK] merged: {out_path} (rows={total_rows:,}, files={len(in_files)})")
    return out_path


def generate_customer_count_outputs(paths: Paths) -> None:
    """
    generate_graphs.py が読むCSV群（02..06）を data/output に生成。
    """
    data_file = paths.output_dir / "transformed_pos_data_eatin.csv"
    df = pd.read_csv(data_file)

    # 伝票単位（H.小計/客数は明細で重複するため）
    tickets = df.drop_duplicates(subset=["H.伝票番号"]).copy()
    tickets["営業日"] = pd.to_datetime(tickets["H.集計対象営業年月日"], format="%Y/%m/%d", errors="coerce")
    tickets["伝票発行日時"] = pd.to_datetime(tickets["H.伝票発行日"], format="%Y/%m/%d %H:%M:%S", errors="coerce")
    tickets["時間"] = tickets["伝票発行日時"].dt.hour
    tickets["年"] = tickets["営業日"].dt.year
    tickets["月"] = tickets["営業日"].dt.month
    tickets["曜日"] = tickets["H.曜日"]
    tickets["客数"] = pd.to_numeric(tickets["H.客数（合計）"], errors="coerce").fillna(0).astype(int)

    def get_time_period(hour: int) -> str:
        if 11 <= hour < 15:
            return "ランチ(11-15時)"
        if 15 <= hour < 17:
            return "アイドル(15-17時)"
        if 17 <= hour < 22:
            return "ディナー(17-22時)"
        return "その他"

    def get_hour_group(hour: int) -> str:
        # 06_customer_count と同じラベル
        if hour < 11:
            return "11時前"
        if hour < 12:
            return "11時台"
        if hour < 13:
            return "12時台"
        if hour < 14:
            return "13時台"
        if hour < 15:
            return "14時台"
        if hour < 16:
            return "15時台"
        if hour < 17:
            return "16時台"
        if hour < 18:
            return "17時台"
        if hour < 19:
            return "18時台"
        if hour < 20:
            return "19時台"
        if hour < 21:
            return "20時台"
        if hour < 22:
            return "21時台"
        return "22時以降"

    tickets["時間帯"] = tickets["時間"].fillna(-1).astype(int).apply(get_time_period)
    tickets["時間グループ"] = tickets["時間"].fillna(-1).astype(int).apply(get_hour_group)

    # 年月別サマリ
    operating_days = tickets.groupby(["年", "月"])["営業日"].nunique().reset_index()
    operating_days.columns = ["年", "月", "営業日数"]
    monthly_customers = tickets.groupby(["年", "月"])["客数"].sum().reset_index()
    monthly_customers.columns = ["年", "月", "総客数"]
    monthly_summary = operating_days.merge(monthly_customers, on=["年", "月"], how="inner")
    monthly_summary["営業日当たり客数"] = monthly_summary["総客数"] / monthly_summary["営業日数"]
    monthly_summary.to_csv(paths.output_dir / "02_monthly_summary.csv", index=False, encoding="utf-8-sig")

    years_in_data = sorted([y for y in monthly_summary["年"].dropna().unique().tolist() if pd.notna(y)])
    if 2024 in years_in_data and 2025 in years_in_data:
        year1, year2 = 2024, 2025
    else:
        year1, year2 = years_in_data[-2], years_in_data[-1]

    df_y1 = tickets[tickets["年"] == year1].copy()
    df_y2 = tickets[tickets["年"] == year2].copy()

    weekday_order = {"月": 0, "火": 1, "水": 2, "木": 3, "金": 4, "土": 5, "日": 6}

    # 月×曜日
    daily_stats = df_y1.groupby(["月", "曜日", "営業日"]).agg(客数=("客数", "sum")).reset_index()
    stats_y1 = daily_stats.groupby(["月", "曜日"]).agg(
        営業日数=("営業日", "count"),
        日当たり客数=("客数", "mean"),
    ).reset_index()
    stats_y1.columns = ["月", "曜日", f"{year1}_営業日数", f"{year1}_日当たり客数"]

    daily_stats = df_y2.groupby(["月", "曜日", "営業日"]).agg(客数=("客数", "sum")).reset_index()
    stats_y2 = daily_stats.groupby(["月", "曜日"]).agg(
        営業日数=("営業日", "count"),
        日当たり客数=("客数", "mean"),
    ).reset_index()
    stats_y2.columns = ["月", "曜日", f"{year2}_営業日数", f"{year2}_日当たり客数"]

    weekday_month = stats_y1.merge(stats_y2, on=["月", "曜日"], how="outer")
    weekday_month["差分_日当たり客数"] = weekday_month[f"{year2}_日当たり客数"] - weekday_month[f"{year1}_日当たり客数"]
    weekday_month["曜日順"] = weekday_month["曜日"].map(weekday_order)
    weekday_month = weekday_month.sort_values(["月", "曜日順"])
    weekday_month.to_csv(paths.output_dir / "03_weekday_month_comparison.csv", index=False, encoding="utf-8-sig")

    # 月×時間帯
    daily_stats = df_y1.groupby(["月", "時間帯", "営業日"]).agg(客数=("客数", "sum")).reset_index()
    stats_y1 = daily_stats.groupby(["月", "時間帯"]).agg(
        営業日数=("営業日", "count"),
        日当たり客数=("客数", "mean"),
    ).reset_index()
    stats_y1.columns = ["月", "時間帯", f"{year1}_営業日数", f"{year1}_日当たり客数"]

    daily_stats = df_y2.groupby(["月", "時間帯", "営業日"]).agg(客数=("客数", "sum")).reset_index()
    stats_y2 = daily_stats.groupby(["月", "時間帯"]).agg(
        営業日数=("営業日", "count"),
        日当たり客数=("客数", "mean"),
    ).reset_index()
    stats_y2.columns = ["月", "時間帯", f"{year2}_営業日数", f"{year2}_日当たり客数"]

    time_month = stats_y1.merge(stats_y2, on=["月", "時間帯"], how="outer")
    time_month["差分_日当たり客数"] = time_month[f"{year2}_日当たり客数"] - time_month[f"{year1}_日当たり客数"]
    time_order = {"ランチ(11-15時)": 0, "アイドル(15-17時)": 1, "ディナー(17-22時)": 2, "その他": 3}
    time_month["時間帯順"] = time_month["時間帯"].map(time_order)
    time_month = time_month.sort_values(["月", "時間帯順"])
    time_month.to_csv(paths.output_dir / "04_time_month_comparison.csv", index=False, encoding="utf-8-sig")

    # 05: factor summary（各月で増加最大の曜日/時間帯）
    results: list[dict] = []
    for month in range(1, 13):
        y1_month = monthly_summary[(monthly_summary["年"] == year1) & (monthly_summary["月"] == month)]
        y2_month = monthly_summary[(monthly_summary["年"] == year2) & (monthly_summary["月"] == month)]
        if len(y1_month) == 0 or len(y2_month) == 0:
            continue
        total_diff = float(y2_month["営業日当たり客数"].values[0] - y1_month["営業日当たり客数"].values[0])

        wdat = weekday_month[weekday_month["月"] == month].copy()
        if len(wdat) > 0 and wdat["差分_日当たり客数"].notna().any():
            max_row = wdat.loc[wdat["差分_日当たり客数"].idxmax()]
            max_weekday = max_row["曜日"]
            max_weekday_diff = float(max_row["差分_日当たり客数"])
        else:
            max_weekday, max_weekday_diff = "-", 0.0

        tdat = time_month[time_month["月"] == month].copy()
        if len(tdat) > 0 and tdat["差分_日当たり客数"].notna().any():
            max_row = tdat.loc[tdat["差分_日当たり客数"].idxmax()]
            max_time = max_row["時間帯"]
            max_time_diff = float(max_row["差分_日当たり客数"])
        else:
            max_time, max_time_diff = "-", 0.0

        results.append(
            {
                "月": month,
                f"{year1}年_営業日当たり客数": float(y1_month["営業日当たり客数"].values[0]),
                f"{year2}年_営業日当たり客数": float(y2_month["営業日当たり客数"].values[0]),
                "総差分": total_diff,
                "最大増加曜日": max_weekday,
                "曜日別最大差分": max_weekday_diff,
                "最大増加時間帯": max_time,
                "時間帯別最大差分": max_time_diff,
            }
        )
    pd.DataFrame(results).to_csv(paths.output_dir / "05_factor_summary.csv", index=False, encoding="utf-8-sig")

    # 06: hour_month_comparison（1時間単位）
    daily_stats = df_y1.groupby(["月", "時間グループ", "営業日"]).agg(客数=("客数", "sum")).reset_index()
    stats_y1 = daily_stats.groupby(["月", "時間グループ"]).agg(
        営業日数=("営業日", "count"),
        日当たり客数=("客数", "mean"),
    ).reset_index()
    stats_y1.columns = ["月", "時間グループ", f"{year1}_営業日数", f"{year1}_日当たり客数"]

    daily_stats = df_y2.groupby(["月", "時間グループ", "営業日"]).agg(客数=("客数", "sum")).reset_index()
    stats_y2 = daily_stats.groupby(["月", "時間グループ"]).agg(
        営業日数=("営業日", "count"),
        日当たり客数=("客数", "mean"),
    ).reset_index()
    stats_y2.columns = ["月", "時間グループ", f"{year2}_営業日数", f"{year2}_日当たり客数"]

    hour_month = stats_y1.merge(stats_y2, on=["月", "時間グループ"], how="outer")
    hour_month["差分_日当たり客数"] = hour_month[f"{year2}_日当たり客数"] - hour_month[f"{year1}_日当たり客数"]
    hour_order = [
        "11時前",
        "11時台",
        "12時台",
        "13時台",
        "14時台",
        "15時台",
        "16時台",
        "17時台",
        "18時台",
        "19時台",
        "20時台",
        "21時台",
        "22時以降",
    ]
    hour_month["時間順"] = hour_month["時間グループ"].apply(lambda x: hour_order.index(x) if x in hour_order else 99)
    hour_month = hour_month.sort_values(["月", "時間順"])
    hour_month.to_csv(paths.output_dir / "06_hour_month_comparison.csv", index=False, encoding="utf-8-sig")

    print("[OK] customer_count outputs: 02..06_*.csv")


def generate_daily_by_segment(paths: Paths) -> None:
    """
    overlay_comparison.py が読む data/output/daily_by_segment.csv を生成。
    セグメント定義:
      - cutoff: 2025-04-01（Before/After）
      - daypart: order_hour < 16 を Lunch、それ以外を Dinner
    """
    df = pd.read_csv(paths.output_dir / "transformed_pos_data_eatin.csv")
    df["H.集計対象営業年月日"] = pd.to_datetime(df["H.集計対象営業年月日"], errors="coerce")
    df["D.オーダー日時"] = pd.to_datetime(df["D.オーダー日時"], errors="coerce")
    df["order_hour"] = df["D.オーダー日時"].dt.hour

    # 期間A/B×ランチ/ディナー（6.3用）
    # - period: Before=期間A(1-3月), After=期間B(10-12月)
    # - 期間A/B以外のデータは4セグメント図から除外
    def _period_label(d: pd.Timestamp) -> str | None:
        if pd.isna(d):
            return None
        if PERIOD_A_START <= d <= PERIOD_A_END:
            return "Before"
        if PERIOD_B_START <= d <= PERIOD_B_END:
            return "After"
        return None

    df["period"] = df["H.集計対象営業年月日"].apply(_period_label)
    df = df[df["period"].notna()].copy()
    df["daypart"] = np.where(df["order_hour"] < 16, "Lunch", "Dinner")
    df["segment"] = df["period"] + "_" + df["daypart"]

    results = []
    for segment in sorted(df["segment"].dropna().unique().tolist()):
        seg_df = df[df["segment"] == segment].copy()
        # 売上（明細合計）
        daily_sales = seg_df.groupby("H.集計対象営業年月日").agg(total_sales=("D.価格", "sum")).reset_index()
        # 伝票数（ユニーク）
        daily_sales["slip_count"] = seg_df.groupby("H.集計対象営業年月日")["H.伝票番号"].nunique().values
        # 客数（伝票単位で重複排除）
        slip_customers = seg_df.drop_duplicates(subset=["H.伝票番号"])[
            ["H.集計対象営業年月日", "H.伝票番号", "H.客数（合計）"]
        ].copy()
        slip_customers["H.客数（合計）"] = pd.to_numeric(slip_customers["H.客数（合計）"], errors="coerce").fillna(0)
        daily_customers = slip_customers.groupby("H.集計対象営業年月日").agg(total_customers=("H.客数（合計）", "sum")).reset_index()

        daily = daily_sales.merge(daily_customers, on="H.集計対象営業年月日", how="left")
        daily = daily.rename(columns={"H.集計対象営業年月日": "date"})
        daily["segment"] = segment
        daily["period"] = segment.split("_")[0]
        daily["daypart"] = segment.split("_")[1]
        daily["avg_spend_per_customer"] = daily["total_sales"] / daily["total_customers"]
        daily["weekday"] = pd.to_datetime(daily["date"]).dt.dayofweek
        daily["weekday_name"] = pd.to_datetime(daily["date"]).dt.day_name()
        results.append(daily)

    out = pd.concat(results, ignore_index=True) if results else pd.DataFrame()
    out.to_csv(paths.output_dir / "daily_by_segment.csv", index=False, encoding="utf-8-sig")
    print("[OK] daily_by_segment.csv")


def main() -> None:
    paths = Paths(project_dir=Path(__file__).resolve().parents[1])

    # env（matplotlibキャッシュをFlow配下へ）
    paths.mplconfig_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["MPLCONFIGDIR"] = str(paths.mplconfig_dir)

    # 0) 入力統合（meta行を除去して merged_pos_data.csv を作る）
    merge_inputs_to_intermediate(paths)

    # 1) 変換（商品コード/商品名/ベース価格付与）
    #    transform_pos_data.py は cwd の merged_pos_data.csv を読む前提
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "01_data_prep" / "transform_pos_data.py")],
        cwd=paths.intermediate_dir,
        env=env,
    )

    # 2) EAT IN抽出（data/intermediate に出る）
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "01_data_prep" / "split_by_category.py")],
        cwd=paths.intermediate_dir,
        env=env,
    )

    # 3) 分析用の基準データを data/output に配置
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        paths.intermediate_dir / "transformed_pos_data_eatin.csv",
        paths.output_dir / "transformed_pos_data_eatin.csv",
    )

    # 4) 客数系の中間CSV（02..06）
    generate_customer_count_outputs(paths)

    # 5) 回転率（滞在時間/店内人数）
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "02_duration" / "analyze_turnover.py")],
        cwd=paths.output_dir,
        env=env,
    )

    # 6) y2y（charts/y2y）
    paths.charts_y2y_dir.mkdir(parents=True, exist_ok=True)
    run(
        [
            "/usr/bin/python3",
            str(paths.scripts_dir / "05_y2y" / "y2y_analysis.py"),
            "--store-root",
            str(paths.project_dir),
            "--input",
            str(paths.output_dir / "transformed_pos_data_eatin.csv"),
            "--out-dir",
            str(paths.charts_y2y_dir),
        ],
        cwd=paths.project_dir,
        env=env,
    )

    # 7) セグメント（daily_by_segment.csv → overlay画像）
    generate_daily_by_segment(paths)
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "08_segment" / "overlay_comparison.py")],
        cwd=paths.project_dir,
        env=env,
    )
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "08_segment" / "high_low_analysis.py")],
        cwd=paths.project_dir,
        env=env,
    )

    # 8) 客単価包括分析（reports/*）
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "07_customer_price" / "comprehensive_analysis.py")],
        cwd=paths.project_dir,
        env=env,
    )

    # 9) 中間レポート用グラフ（reports/graph01..）
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "09_interim_report" / "generate_graphs.py")],
        cwd=paths.project_dir,
        env=env,
    )

    # 10) 中間レポートMD
    run(
        ["/usr/bin/python3", str(paths.scripts_dir / "09_interim_report" / "generate_interim_report_md.py")],
        cwd=paths.project_dir,
        env=env,
    )

    print("\n=== DONE ===")
    print(f"reports: {paths.reports_dir}")


if __name__ == "__main__":
    main()

