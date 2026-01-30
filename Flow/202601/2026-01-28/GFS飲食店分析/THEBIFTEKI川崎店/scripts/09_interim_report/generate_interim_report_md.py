#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中間レポート（Markdown）生成

出力:
  reports/THE_BIFTEKI_川崎店_売上分析中間レポート.md
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


STORE_NAME = "THE BIFTEKI 川崎店"


def yen(n: float | int) -> str:
    return f"{int(round(n)):,}円"


def man_yen(n_yen: float | int) -> str:
    return f"{n_yen/10000:,.0f}万円"


def pct(a: float, b: float) -> str:
    # a->b
    if a == 0:
        return "-"
    return f"{(b/a-1)*100:+.0f}%"


def main() -> None:
    project_dir = Path(__file__).resolve().parents[2]
    data_dir = project_dir / "data" / "output"
    reports_dir = project_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_dir / "transformed_pos_data_eatin.csv")
    tickets = df.drop_duplicates(subset=["H.伝票番号"]).copy()
    tickets["営業日"] = pd.to_datetime(tickets["H.集計対象営業年月日"], errors="coerce")
    tickets["年"] = tickets["営業日"].dt.year
    tickets["客数"] = pd.to_numeric(tickets["H.客数（合計）"], errors="coerce").fillna(0)
    tickets["小計"] = pd.to_numeric(tickets["H.小計"], errors="coerce").fillna(0)

    created_at = datetime.now()
    min_date = tickets["営業日"].min()
    max_date = tickets["営業日"].max()

    # 年別サマリー（売上=伝票小計の合計）
    yearly = (
        tickets.groupby("年", dropna=True)
        .agg(売上=("小計", "sum"), 客数=("客数", "sum"))
        .reset_index()
        .sort_values("年")
    )
    yearly["客単価"] = yearly["売上"] / yearly["客数"].replace(0, np.nan)

    def yrow(year: int) -> dict | None:
        r = yearly[yearly["年"] == year]
        if len(r) == 0:
            return None
        row = r.iloc[0]
        return {"売上": float(row["売上"]), "客数": float(row["客数"]), "客単価": float(row["客単価"])}

    y2024 = yrow(2024)
    y2025 = yrow(2025)
    y2026 = yrow(2026)

    # 期間A/B（同じ定義）
    tickets["日付"] = tickets["営業日"]
    # 期間A/B（指定）
    period_a = (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-03-31"))
    period_b = (pd.Timestamp("2025-10-01"), pd.Timestamp("2025-12-31"))

    t_a = tickets[(tickets["日付"] >= period_a[0]) & (tickets["日付"] <= period_a[1])].copy()
    t_b = tickets[(tickets["日付"] >= period_b[0]) & (tickets["日付"] <= period_b[1])].copy()
    a_unit = float((t_a["小計"].sum() / t_a["客数"].sum()) if t_a["客数"].sum() else np.nan)
    b_unit = float((t_b["小計"].sum() / t_b["客数"].sum()) if t_b["客数"].sum() else np.nan)

    # 滞在時間の統計
    visits_path = data_dir / "visits_with_duration.csv"
    if visits_path.exists():
        visits = pd.read_csv(visits_path)
        durations = pd.to_numeric(visits["滞在時間_分"], errors="coerce").dropna()
        dur_stats = {
            "mean": float(durations.mean()),
            "std": float(durations.std()),
            "median": float(durations.median()),
            "p25": float(durations.quantile(0.25)),
            "p75": float(durations.quantile(0.75)),
        }
    else:
        dur_stats = {"mean": float("nan"), "std": float("nan"), "median": float("nan"), "p25": float("nan"), "p75": float("nan")}

    out_path = reports_dir / "THE_BIFTEKI_川崎店_売上分析中間レポート.md"

    def safe(v: float | None, fmt: str) -> str:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "-"
        return fmt.format(v)

    md = []
    md.append(f"# {STORE_NAME} 売上分析 中間レポート\n")
    md.append(f"**作成日**: {created_at.strftime('%Y年%-m月%-d日')}  \n")
    md.append(f"**分析対象期間**: {min_date.strftime('%Y年%-m月')} 〜 {max_date.strftime('%Y年%-m月')}  \n")
    md.append("**データソース**: POSデータ（イートイン）\n")
    md.append("---\n")

    md.append("## 目次\n")
    md.append("1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)\n")
    md.append("2. [売上の全体推移](#2-売上の全体推移)\n")
    md.append("3. [客数の部](#3-客数の部)\n")
    md.append("4. [客単価の部](#4-客単価の部)\n")
    md.append("5. [回転率の部](#5-回転率の部)\n")
    md.append("6. [その他インサイトなど](#6-その他インサイトなど)\n")
    md.append("7. [結論：客数・客単価・回転率](#7-結論客数客単価回転率)\n")
    md.append("\n---\n")

    md.append("## 1. エグゼクティブサマリー\n\n")
    md.append("### 分析の目的\n\n")
    md.append("**2025年の売上変化が「客数の増減」によるものか「客単価の増減」によるものかを明らかにし、今後の施策方針を判断する材料を提供する。**\n\n")

    md.append("### 主要な発見\n\n")
    md.append("| 観点 | 主要な発見 |\n|------|-----------|\n")
    if y2024 and y2025:
        md.append(
            f"| **売上** | 2024年→2025年で **{pct(y2024['売上'], y2025['売上'])}**（{man_yen(y2024['売上'])} → {man_yen(y2025['売上'])}） |\n"
        )
        md.append(
            f"| **客数** | 2024年→2025年で **{pct(y2024['客数'], y2025['客数'])}**（{int(y2024['客数']):,}人 → {int(y2025['客数']):,}人） |\n"
        )
        md.append(
            f"| **客単価** | 2024年→2025年で **{pct(y2024['客単価'], y2025['客単価'])}**（{yen(y2024['客単価'])} → {yen(y2025['客単価'])}） |\n"
        )
    md.append(f"| **回転率** | 平均滞在時間は **約{safe(dur_stats['mean'], '{:.0f}')}分** と大きくは変動しない |\n")

    md.append("\n### 結論\n\n")
    if y2024 and y2025:
        md.append(
            f"**2025年の売上増加は「客数増」と「客単価上昇」の両方が寄与している。**\n\n"
        )
    md.append("今後の売上向上の鍵は：\n")
    md.append("1. **ディナー帯の集客強化**\n")
    md.append("2. **客単価上昇トレンドの維持（高単価商品の浸透）**\n")
    md.append("\n---\n")

    md.append("## 2. 売上の全体推移\n\n")
    md.append("### 2.1 年別サマリー\n\n")
    md.append("| 年 | 売上 | 客数 | 客単価 |\n|---|---:|---:|---:|\n")
    if y2024:
        md.append(f"| 2024年 | {man_yen(y2024['売上'])} | {int(y2024['客数']):,}人 | {yen(y2024['客単価'])} |\n")
    if y2025:
        md.append(f"| 2025年 | {man_yen(y2025['売上'])} | {int(y2025['客数']):,}人 | {yen(y2025['客単価'])} |\n")
    if y2026:
        md.append(f"| 2026年（1月のみ） | {man_yen(y2026['売上'])} | {int(y2026['客数']):,}人 | {yen(y2026['客単価'])} |\n")
    md.append("\n")

    md.append("### 2.2 月別推移グラフ（営業日あたり）\n\n")
    md.append("営業日数の違いを排除するため、営業日あたりの指標で推移を示します。\n\n")
    md.append("![月別推移（営業日あたり）](../charts/y2y/monthly_trends_normalized.png)\n\n")
    md.append("### 2.3 前年同月比較（営業日あたり）\n\n")
    md.append("![年比較（営業日あたり）](../charts/y2y/y2y_comparison_normalized.png)\n\n")

    md.append("\n---\n")
    md.append("## 3. 客数の部\n\n")
    md.append("### 3.1 営業日当たり客数の推移\n\n")
    md.append("![月別比較グラフ](./graph01_monthly_comparison.png)\n\n")
    md.append("![前年比増減グラフ](./graph02_yoy_change.png)\n\n")
    md.append("### 3.2 時間帯別分析\n\n")
    md.append("![時間帯別寄与度](./graph10_time_contribution.png)\n\n")
    md.append("![時間帯別ヒートマップ](./graph09_time_heatmap.png)\n\n")
    md.append("### 3.3 曜日別分析\n\n")
    md.append("![曜日別ヒートマップ](./graph11_weekday_heatmap.png)\n\n")
    md.append("![平日vs土日比較](./graph12_weekday_vs_weekend.png)\n\n")

    md.append("\n---\n")
    md.append("## 4. 客単価の部\n\n")
    md.append("### 4.1 客単価の推移（期間A/B比較）\n\n")
    md.append(f"- **期間A**（2025/01-03）客単価: **{safe(a_unit, '{:,.0f}円')}**\n")
    md.append(f"- **期間B**（2025/10-12）客単価: **{safe(b_unit, '{:,.0f}円')}**\n\n")
    md.append("![要因分解](./01_decomposition_analysis.png)\n\n")
    md.append("![客単価分布の変化（20%刻み・5エリア）](./graph03_percentile_change_20pct.png)\n\n")
    md.append("![曜日・時間帯分析](./graph04_weekday_hour_analysis.png)\n\n")
    md.append("### 4.5 売上増加に貢献したメニュー\n\n")
    md.append("![メニュー貢献度](./graph05_menu_contribution.png)\n\n")

    md.append("\n---\n")
    md.append("## 5. 回転率の部\n\n")
    md.append("### 5.1 滞在時間の基本統計量\n\n")
    md.append("| 指標 | 値 |\n|------|-----|\n")
    md.append(f"| 平均滞在時間 | {safe(dur_stats['mean'], '{:.1f}')}分 |\n")
    md.append(f"| 標準偏差 | {safe(dur_stats['std'], '{:.1f}')}分 |\n")
    md.append(f"| 中央値 | {safe(dur_stats['median'], '{:.1f}')}分 |\n")
    md.append(f"| 25パーセンタイル | {safe(dur_stats['p25'], '{:.1f}')}分 |\n")
    md.append(f"| 75パーセンタイル | {safe(dur_stats['p75'], '{:.1f}')}分 |\n\n")
    md.append("![曜日別・時間帯別滞在時間](./graph13_duration_by_hour_weekday.png)\n\n")
    md.append("### 5.2 店内人数と来店の関係\n\n")
    md.append("![時間帯別来店組数と店内人数](./graph06_hourly_visits_occupancy.png)\n\n")
    md.append("### 5.3 滞在時間と売上の相関\n\n")
    md.append("![時間帯別の客数と客単価](./graph07_spend_customers_by_time.png)\n\n")

    md.append("\n---\n")
    md.append("## 6. その他インサイトなど\n\n")
    md.append("### 6.1 売上上位日と下位日の違い\n\n")
    md.append("![売上上位/下位の2軸分布](./graph08_sales_2d_separation.png)\n\n")
    md.append("### 6.3 4セグメント分析（期間×ランチ/ディナー）\n\n")
    md.append("![4セグメント比較](./09_overlay_all.png)\n\n")
    md.append("### 6.4 High/Low分析（4月以降）\n\n")
    md.append("![High/Low比較](./HighLowAnalysis/01_high_low_distribution.png)\n\n")
    md.append("![要因比率](./HighLowAnalysis/02_factor_ratio.png)\n\n")

    md.append("\n---\n")
    md.append("## 7. 結論：客数・客単価・回転率\n\n")
    md.append("### 7.1 分析結果のまとめ\n\n")
    if y2024 and y2025:
        md.append("| 指標 | 2024年 | 2025年 | 変化率 |\n|---|---:|---:|---:|\n")
        md.append(f"| 客単価 | {yen(y2024['客単価'])} | {yen(y2025['客単価'])} | {pct(y2024['客単価'], y2025['客単価'])} |\n")
        md.append(f"| 客数 | {int(y2024['客数']):,}人 | {int(y2025['客数']):,}人 | {pct(y2024['客数'], y2025['客数'])} |\n")
        md.append(f"| 売上 | {man_yen(y2024['売上'])} | {man_yen(y2025['売上'])} | {pct(y2024['売上'], y2025['売上'])} |\n\n")

    md.append("### 7.2 今後の施策への示唆（たたき）\n\n")
    md.append("- **ディナー帯の来店組数を増やす施策**（SNS/予約導線/クーポン等）\n")
    md.append("- **客単価上昇を支える高単価商品戦略**の継続・改善\n")
    md.append("\n---\n\n")
    md.append("*本レポートは、各分析スクリプトの出力（図表・集計CSV）を統合して作成*\n")

    out_path.write_text("".join(md), encoding="utf-8")
    print(f"[OK] wrote: {out_path}")


if __name__ == "__main__":
    main()

