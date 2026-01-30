#!/usr/bin/env python3
"""
graph13_duration_by_hour_weekday.png を「11時以降」だけで描画し直す。

背景:
- 中間レポート 5.1 のグラフは graph13_duration_by_hour_weekday.png を参照している
- スライド用途で「10時台を含めず、11時から表示」したい
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

# Matplotlib headless + cache dir
ROOT = Path(
    "/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-28/GFS飲食店分析/直送生ホルモンなかせい"
)
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402


def _set_jp_font() -> None:
    candidates = [
        "Hiragino Sans",  # macOS
        "AppleGothic",
        "Yu Gothic",
        "Meiryo",
        "Arial Unicode MS",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    _set_jp_font()

    visits_csv = ROOT / "data" / "intermediate" / "visits_with_duration.csv"
    out_png = ROOT / "reports" / "graph13_duration_by_hour_weekday.png"

    df = pd.read_csv(visits_csv)
    df["入店時刻_dt"] = pd.to_datetime(df["入店時刻"], errors="coerce")
    df["hour"] = df["入店時刻_dt"].dt.hour
    df["dur"] = pd.to_numeric(df["滞在時間_分"], errors="coerce")

    df = df.dropna(subset=["hour", "dur", "曜日"]).copy()
    df = df[df["hour"] >= 11].copy()  # 11時以降のみ

    weekday_order = ["月", "火", "水", "木", "金", "土", "日"]
    hours = list(range(11, 23))  # 11時〜22時

    med = (
        df.groupby(["曜日", "hour"], dropna=False)["dur"]
        .median()
        .reindex(pd.MultiIndex.from_product([weekday_order, hours], names=["曜日", "hour"]))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(14, 6.5))

    colors = {
        "月": "#1976D2",
        "火": "#2196F3",
        "水": "#42A5F5",
        "木": "#64B5F6",
        "金": "#90CAF9",
        "土": "#E53935",
        "日": "#FF7043",
    }
    markers = {"月": "o", "火": "s", "水": "^", "木": "D", "金": "v", "土": "o", "日": "s"}

    for wd in weekday_order:
        tmp = med[med["曜日"] == wd].copy()
        y = tmp["dur"].tolist()
        valid = [(h, v) for h, v in zip(hours, y) if pd.notna(v)]
        if not valid:
            continue
        xs, ys = zip(*valid)
        linewidth = 2.5 if wd in ["土", "日"] else 1.6
        ax.plot(
            xs,
            ys,
            marker=markers[wd],
            label=wd,
            color=colors[wd],
            linewidth=linewidth,
            markersize=6,
        )

    ax.set_xlabel("入店時刻", fontsize=12)
    ax.set_ylabel("中央値滞在時間（分）", fontsize=12)
    ax.set_title("曜日別・入店時刻別の中央値滞在時間（11時以降）", fontsize=14)
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h}:00" for h in hours], rotation=45)
    ax.legend(loc="upper right", title="曜日")
    ax.grid(True, alpha=0.3)

    # make the range readable for the typical 80-100min band but keep headroom
    ax.set_ylim(0, 200)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()

