"""
直送生ホルモンなかせい：組（伝票番号）単位の散布図分析

前提（このCSVでできる範囲の定義）:
- 組 = H.伝票番号（伝票/会計単位）
- 滞在時間 = H.伝票処理日 - H.伝票発行日（伝票ベース）
- 売上 = H.小計（伝票の小計）
- 客単価 = H.小計 / H.客数（合計）
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

# Matplotlib cache directory issue workaround (must be set before importing matplotlib)
THIS_DIR = Path(__file__).resolve().parent
WORK_DIR = THIS_DIR.parent / "work"
WORK_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(WORK_DIR / ".mplconfig"))

import matplotlib  # noqa: E402

# Force non-GUI backend (required for headless/sandboxed execution)
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from scipy import stats  # noqa: E402


def _configure_japanese_font() -> str:
    """Configure Matplotlib/Seaborn to use a Japanese-capable font (avoid mojibake)."""
    candidates = [
        "Hiragino Sans",  # macOS
        "Hiragino Kaku Gothic ProN",
        "Yu Gothic",
        "Meiryo",
        "IPAexGothic",
        "Noto Sans CJK JP",
        "Noto Sans JP",
    ]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((c for c in candidates if c in installed), "sans-serif")

    plt.rcParams["font.family"] = chosen
    plt.rcParams["axes.unicode_minus"] = False
    return chosen


JP_FONT = _configure_japanese_font()


def _trim_upper_tail_xy(df: pd.DataFrame, x: str, y: str, trim_pct: float = 0.10) -> pd.DataFrame:
    """Upper-tail trim consistent with plots: keep <= (1-trim_pct) quantile on both axes."""
    d = df[[x, y]].dropna()
    if not (0 < trim_pct < 1) or len(d) == 0:
        return d
    x_hi = d[x].quantile(1 - trim_pct)
    y_hi = d[y].quantile(1 - trim_pct)
    return d[(d[x] <= x_hi) & (d[y] <= y_hi)]


def _corr_summary(df: pd.DataFrame, x: str, y: str) -> dict:
    d = df[[x, y]].dropna()
    n = int(len(d))
    if n < 3:
        return {"n": n, "pearson_r": None, "pearson_p": None, "spearman_rho": None, "spearman_p": None}
    pr = stats.pearsonr(d[x].to_numpy(), d[y].to_numpy())
    sr = stats.spearmanr(d[x].to_numpy(), d[y].to_numpy())
    return {
        "n": n,
        "pearson_r": float(pr.statistic),
        "pearson_p": float(pr.pvalue),
        "spearman_rho": float(sr.statistic),
        "spearman_p": float(sr.pvalue),
    }

def scatter_facets_two_panels(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    x: str,
    y: str,
    hue: str | None,
    palette: dict[str, str] | None,
    hue_order: list[str] | None,
    title: str,
    left_title: str,
    right_title: str,
    out_path: Path,
    x_label: str | None = None,
    y_label: str | None = None,
    trim_pct: float = 0.10,
) -> None:
    """Two side-by-side scatter panels (same axes)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(
        style="whitegrid",
        font_scale=1.0,
        rc={"font.family": JP_FONT, "axes.unicode_minus": False},
    )

    def _prep(df: pd.DataFrame) -> pd.DataFrame:
        d = df[[x, y] + ([hue] if hue else [])].dropna()
        if 0 < trim_pct < 1 and len(d) > 0:
            x_hi = d[x].quantile(1 - trim_pct)
            y_hi = d[y].quantile(1 - trim_pct)
            d = d[(d[x] <= x_hi) & (d[y] <= y_hi)]
        return d

    ldf = _prep(left)
    rdf = _prep(right)

    # Axis limits (shared) based on combined trimmed data
    combo = pd.concat([ldf, rdf], axis=0, ignore_index=True)
    xlim = (combo[x].min(), combo[x].max()) if len(combo) else (None, None)
    ylim = (combo[y].min(), combo[y].max()) if len(combo) else (None, None)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
    for ax, d, st in [(axes[0], ldf, left_title), (axes[1], rdf, right_title)]:
        sns.scatterplot(
            data=d,
            x=x,
            y=y,
            hue=hue,
            palette=palette,
            hue_order=hue_order,
            alpha=0.65,
            s=35,
            edgecolor="none",
            ax=ax,
        )
        ax.set_title(st)
        ax.set_xlabel(x_label or x)
        ax.set_ylabel(y_label or y)
        if xlim[0] is not None:
            ax.set_xlim(*xlim)
        if ylim[0] is not None:
            ax.set_ylim(*ylim)
        # keep legend only on right
        if ax is axes[0] and ax.get_legend() is not None:
            ax.get_legend().remove()

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


ROOT = Path(
    "/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-28/GFS飲食店分析/直送生ホルモンなかせい"
)
INPUT_CSV = ROOT / "data" / "intermediate" / "transformed_pos_data_eatin.csv"

OUT_CHART_DIR = ROOT / "charts" / "group_scatter"
OUT_DATA_DIR = ROOT / "data" / "output"
OUT_REPORT_DIR = ROOT / "reports"


COL_BILL = "H.伝票番号"
COL_GUESTS = "H.客数（合計）"
COL_SALES = "H.小計"
COL_ITEMS = "H.総商品数"
COL_WEEKDAY = "H.曜日"
COL_BUSINESS_DATE = "H.集計対象営業年月日"
COL_ISSUED_TS = "H.伝票発行日"
COL_SETTLED_TS = "H.伝票処理日"


def _to_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False), errors="coerce")


def load_and_aggregate() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV)

    # Normalize types
    df[COL_BILL] = df[COL_BILL].astype(str)
    df[COL_GUESTS] = _to_numeric(df[COL_GUESTS])
    df[COL_SALES] = _to_numeric(df[COL_SALES])
    df[COL_ITEMS] = _to_numeric(df[COL_ITEMS])

    # datetime
    df[COL_ISSUED_TS] = pd.to_datetime(df[COL_ISSUED_TS], errors="coerce")
    df[COL_SETTLED_TS] = pd.to_datetime(df[COL_SETTLED_TS], errors="coerce")

    g = df.groupby(COL_BILL, dropna=False)

    agg = g.agg(
        business_date=(COL_BUSINESS_DATE, "first"),
        weekday=(COL_WEEKDAY, "first"),
        guests=(COL_GUESTS, "first"),
        sales=(COL_SALES, "first"),
        total_items=(COL_ITEMS, "first"),
        n_rows=(COL_BILL, "size"),
        issued_ts=(COL_ISSUED_TS, "first"),
        settled_ts=(COL_SETTLED_TS, "first"),
    ).reset_index().rename(columns={COL_BILL: "bill_no"})

    # Derived metrics
    agg["duration_min"] = (agg["settled_ts"] - agg["issued_ts"]).dt.total_seconds() / 60.0

    agg["sales_per_guest"] = np.where(
        (agg["guests"] > 0) & agg["sales"].notna(), agg["sales"] / agg["guests"], np.nan
    )
    agg["items_per_guest"] = np.where(
        (agg["guests"] > 0) & agg["total_items"].notna(), agg["total_items"] / agg["guests"], np.nan
    )

    # light cleanup: drop records without sales or without required timestamps
    agg = agg.dropna(subset=["sales", "issued_ts", "settled_ts"]).copy()
    agg = agg[(agg["duration_min"].notna()) & (agg["duration_min"] >= 0)].copy()
    # Exclude negative sales (returns/corrections etc.)
    agg = agg[agg["sales"] >= 0].copy()
    # Entry time (for day split: before/after 16:00)
    agg["entry_hour"] = agg["issued_ts"].dt.hour + agg["issued_ts"].dt.minute / 60.0
    agg["entry_16_bucket"] = np.where(agg["entry_hour"] < 16, "16時前入店", "16時以降入店")

    # Weekday label (Japanese)
    agg["weekday_label"] = agg["weekday"].astype(str)

    # Day-level sales (used for high/low day coloring)
    day_sales = agg.groupby("business_date", dropna=False)["sales"].sum()
    day_median = float(day_sales.median()) if len(day_sales) else float("nan")
    agg["day_sales_total"] = agg["business_date"].map(day_sales)
    agg["day_sales_category"] = np.where(agg["day_sales_total"] >= day_median, "高売上日", "低売上日")

    return agg


def scatter(
    data: pd.DataFrame,
    *,
    x: str,
    y: str,
    hue: str | None,
    palette: dict[str, str] | None = None,
    hue_order: list[str] | None = None,
    style: str | None = None,
    style_order: list[str] | None = None,
    color: str | None = None,
    title: str,
    out_path: Path,
    x_label: str | None = None,
    y_label: str | None = None,
    log_y: bool = False,
    trim_pct: float = 0.10,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sns.set_theme(
        style="whitegrid",
        font_scale=1.05,
        rc={"font.family": JP_FONT, "axes.unicode_minus": False},
    )
    plt.figure(figsize=(12, 7))

    cols = [x, y]
    if hue:
        cols.append(hue)
    if style:
        cols.append(style)
    # de-dup while preserving order
    cols = list(dict.fromkeys(cols))
    plot_df = data[cols].dropna()
    # Trim outliers (upper tail only): for each axis, drop top trim_pct (e.g. 10% => keep <= 90th percentile)
    if 0 < trim_pct < 1 and len(plot_df) > 0:
        x_hi = plot_df[x].quantile(1 - trim_pct)
        y_hi = plot_df[y].quantile(1 - trim_pct)
        plot_df = plot_df[(plot_df[x] <= x_hi) & (plot_df[y] <= y_hi)]
    ax = sns.scatterplot(
        data=plot_df,
        x=x,
        y=y,
        hue=hue,
        palette=palette,
        hue_order=hue_order,
        style=style,
        style_order=style_order,
        color=color,
        alpha=0.55,
        s=30,
        edgecolor="none",
    )

    # regression (no hue)
    try:
        sns.regplot(
            data=plot_df,
            x=x,
            y=y,
            scatter=False,
            lowess=True,
            line_kws={"color": "black", "linewidth": 2, "alpha": 0.9},
            ax=ax,
        )
    except Exception:
        pass

    ax.set_title(title)
    ax.set_xlabel(x_label or x)
    ax.set_ylabel(y_label or y)
    if log_y:
        ax.set_yscale("log")
        ax.set_ylabel((y_label or y) + " (log)")

    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def write_gallery_md(
    images: list[Path],
    metrics_csv: Path,
    *,
    day_sales_median: float | None,
    day_point_images: list[Path],
    daily_metrics_csv: Path | None,
    corr_md: Path | None,
) -> Path:
    OUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_REPORT_DIR / "直送生ホルモンなかせい_組別散布図ギャラリー.md"

    rel_metrics = os.path.relpath(metrics_csv, md_path.parent).replace("\\", "/")
    rel_daily_metrics = (
        os.path.relpath(daily_metrics_csv, md_path.parent).replace("\\", "/")
        if daily_metrics_csv is not None
        else None
    )
    rel_corr = os.path.relpath(corr_md, md_path.parent).replace("\\", "/") if corr_md is not None else None
    lines = []
    lines.append("# 直送生ホルモンなかせい：組（伝票）別 散布図ギャラリー\n")
    lines.append("## 目的\n")
    lines.append("客単価（=小計/客数）に影響していそうな指標（滞在時間・客数など）を、組（伝票）単位で可視化します。\n")
    lines.append("## 注意（定義）\n")
    lines.append("- 組 = `H.伝票番号`\n")
    lines.append("- 滞在時間 = `H.伝票処理日` - `H.伝票発行日`（伝票ベース）\n")
    lines.append("- 負の売上（`H.小計` < 0）の伝票は除外\n")
    lines.append(
        "- 外れ値除外: 各散布図ごとに **x軸/y軸それぞれ上位10%（90パーセンタイル超）を除外**\n"
    )
    if day_sales_median is not None and np.isfinite(day_sales_median):
        lines.append(
            f"- 日別の色分け: 日別売上合計の中央値（{day_sales_median:,.0f}円）を境に **高売上日=赤 / 低売上日=青**\n"
        )
    lines.append(f"- 集計CSV: `{rel_metrics}`\n")
    if rel_daily_metrics:
        lines.append(f"- 日別集計CSV（1点=1日）: `{rel_daily_metrics}`\n")
    if rel_corr:
        lines.append(f"- 相関（ランチ/ディナー別）: `{rel_corr}`\n")
    lines.append("- 日別集計の分割: `H.伝票発行日`（入店）で **16:00以前 / 16:00以降** に分けて日別平均を算出\n")
    lines.append("\n## 図一覧（全期間）\n")

    for p in images:
        rel = os.path.relpath(p, md_path.parent).replace("\\", "/")
        lines.append(f"### {p.stem}\n")
        lines.append(f"![]({rel})\n")

    if day_point_images:
        lines.append("\n## 図一覧（日別：1点=1日、16時前/以後で左右分割）\n")
        for p in day_point_images:
            rel = os.path.relpath(p, md_path.parent).replace("\\", "/")
            lines.append(f"### {p.stem}\n")
            lines.append(f"![]({rel})\n")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    OUT_CHART_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    agg = load_and_aggregate()
    day_sales_median = (
        float(agg["day_sales_total"].dropna().drop_duplicates().median())
        if "day_sales_total" in agg.columns
        else None
    )

    # Save metrics
    metrics_csv = OUT_DATA_DIR / "group_level_metrics_nakasei.csv"
    agg.sort_values(["business_date", "issued_ts", "bill_no"]).to_csv(
        metrics_csv, index=False, encoding="utf-8-sig"
    )

    images: list[Path] = []
    day_point_images: list[Path] = []

    day_palette = {"高売上日": "#e74c3c", "低売上日": "#1f77b4"}  # red / blue

    # --- Correlation report (Lunch/Dinner): duration vs sales_per_guest ---
    corr_md = OUT_REPORT_DIR / "直送生ホルモンなかせい_ランチディナー_滞在時間x客単価_相関.md"
    xcol = "duration_min"
    ycol = "sales_per_guest"
    lunch_raw = agg[agg["entry_16_bucket"] == "16時前入店"].copy()
    dinner_raw = agg[agg["entry_16_bucket"] == "16時以降入店"].copy()
    lunch_trim = _trim_upper_tail_xy(lunch_raw, xcol, ycol, trim_pct=0.10)
    dinner_trim = _trim_upper_tail_xy(dinner_raw, xcol, ycol, trim_pct=0.10)
    l_raw = _corr_summary(lunch_raw, xcol, ycol)
    d_raw = _corr_summary(dinner_raw, xcol, ycol)
    l_trim = _corr_summary(lunch_trim, xcol, ycol)
    d_trim = _corr_summary(dinner_trim, xcol, ycol)

    OUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    corr_lines = []
    corr_lines.append("# 直送生ホルモンなかせい：ランチ/ディナー別 相関（滞在時間 × 客単価）\n")
    corr_lines.append("## 定義\n")
    corr_lines.append("- ランチ = `H.伝票発行日` が 16:00 より前（16時前入店）\n")
    corr_lines.append("- ディナー = `H.伝票発行日` が 16:00 以降（16時以降入店）\n")
    corr_lines.append("- 滞在時間（分）= `H.伝票処理日` - `H.伝票発行日`\n")
    corr_lines.append("- 客単価（円）= `H.小計` / `H.客数（合計）`\n")
    corr_lines.append("- 伝票（組）単位で算出\n")
    corr_lines.append("\n## 相関（外れ値カットなし）\n")
    corr_lines.append("|区分|n|Pearson r|p値|Spearman ρ|p値|\n|---:|---:|---:|---:|---:|---:|\n")
    corr_lines.append(
        f"|ランチ|{l_raw['n']}|{(l_raw['pearson_r'] if l_raw['pearson_r'] is not None else ''):.3f}|{(l_raw['pearson_p'] if l_raw['pearson_p'] is not None else float('nan')):.3g}|{(l_raw['spearman_rho'] if l_raw['spearman_rho'] is not None else ''):.3f}|{(l_raw['spearman_p'] if l_raw['spearman_p'] is not None else float('nan')):.3g}|\n"
    )
    corr_lines.append(
        f"|ディナー|{d_raw['n']}|{(d_raw['pearson_r'] if d_raw['pearson_r'] is not None else ''):.3f}|{(d_raw['pearson_p'] if d_raw['pearson_p'] is not None else float('nan')):.3g}|{(d_raw['spearman_rho'] if d_raw['spearman_rho'] is not None else ''):.3f}|{(d_raw['spearman_p'] if d_raw['spearman_p'] is not None else float('nan')):.3g}|\n"
    )
    corr_lines.append("\n## 相関（上位10%外れ値を除外：x/yともに90パーセンタイル超を除外）\n")
    corr_lines.append("|区分|n|Pearson r|p値|Spearman ρ|p値|\n|---:|---:|---:|---:|---:|---:|\n")
    corr_lines.append(
        f"|ランチ|{l_trim['n']}|{(l_trim['pearson_r'] if l_trim['pearson_r'] is not None else ''):.3f}|{(l_trim['pearson_p'] if l_trim['pearson_p'] is not None else float('nan')):.3g}|{(l_trim['spearman_rho'] if l_trim['spearman_rho'] is not None else ''):.3f}|{(l_trim['spearman_p'] if l_trim['spearman_p'] is not None else float('nan')):.3g}|\n"
    )
    corr_lines.append(
        f"|ディナー|{d_trim['n']}|{(d_trim['pearson_r'] if d_trim['pearson_r'] is not None else ''):.3f}|{(d_trim['pearson_p'] if d_trim['pearson_p'] is not None else float('nan')):.3g}|{(d_trim['spearman_rho'] if d_trim['spearman_rho'] is not None else ''):.3f}|{(d_trim['spearman_p'] if d_trim['spearman_p'] is not None else float('nan')):.3g}|\n"
    )
    corr_md.write_text("\n".join(corr_lines), encoding="utf-8")

    # --- Group-level (1 point = 1 bill) plots ---
    # Required filenames (keep existing names) but Y is now sales_per_guest (客単価)
    out = OUT_CHART_DIR / "sales_vs_duration_min.png"
    lunch_df = agg[agg["entry_16_bucket"] == "16時前入店"].copy()
    dinner_df = agg[agg["entry_16_bucket"] == "16時以降入店"].copy()
    scatter_facets_two_panels(
        lunch_df,
        dinner_df,
        x="duration_min",
        y="sales_per_guest",
        hue="day_sales_category",
        palette=day_palette,
        hue_order=["低売上日", "高売上日"],
        title="客単価 × 滞在時間（ランチ/ディナーで左右分割）",
        left_title="ランチ（16時前入店）",
        right_title="ディナー（16時以降入店）",
        out_path=out,
        x_label="滞在時間（分）",
        y_label="客単価（円）",
        trim_pct=0.10,
    )
    images.append(out)

    out = OUT_CHART_DIR / "sales_vs_guests.png"
    scatter(
        agg,
        x="guests",
        y="sales_per_guest",
        hue="day_sales_category",
        palette=day_palette,
        hue_order=["低売上日", "高売上日"],
        title="客単価 × 客数",
        out_path=out,
        x_label="客数（人）",
        y_label="客単価（円）",
        log_y=False,
    )
    images.append(out)

    out = OUT_CHART_DIR / "sales_vs_duration_min__hue_weekday.png"
    scatter(
        agg,
        x="duration_min",
        y="sales_per_guest",
        hue="day_sales_category",
        palette=day_palette,
        hue_order=["低売上日", "高売上日"],
        style="weekday_label",
        title="客単価 × 滞在時間（色=日別売上の高低、形=曜日）",
        out_path=out,
        x_label="滞在時間（分）",
        y_label="客単価（円）",
        log_y=False,
    )
    images.append(out)

    # Keep file name, but NOT log scale, and plot sales_per_guest
    out3 = OUT_CHART_DIR / "sales_vs_duration_min__logy.png"
    scatter(
        agg,
        x="duration_min",
        y="sales_per_guest",
        hue="day_sales_category",
        palette=day_palette,
        hue_order=["低売上日", "高売上日"],
        title="客単価 × 滞在時間（リニア）",
        out_path=out3,
        x_label="滞在時間（分）",
        y_label="客単価（円）",
        log_y=False,
    )
    images.append(out3)

    # Other helpful group-level plots (客単価が目的)
    out = OUT_CHART_DIR / "sales_vs_total_items.png"
    scatter(
        agg,
        x="total_items",
        y="sales_per_guest",
        hue="day_sales_category",
        palette=day_palette,
        hue_order=["低売上日", "高売上日"],
        title="客単価 × 総商品数",
        out_path=out,
        x_label="総商品数（点）",
        y_label="客単価（円）",
        log_y=False,
    )
    images.append(out)

    out = OUT_CHART_DIR / "sales_vs_items_per_guest.png"
    scatter(
        agg,
        x="items_per_guest",
        y="sales_per_guest",
        hue="day_sales_category",
        palette=day_palette,
        hue_order=["低売上日", "高売上日"],
        title="客単価 × 一人あたり商品数",
        out_path=out,
        x_label="一人あたり商品数（点/人）",
        y_label="客単価（円）",
        log_y=False,
    )
    images.append(out)

    # --- Day-point data (1 point = 1 day) ---
    daily = (
        agg.groupby("business_date", dropna=False)
        .agg(
            day_sales_total=("sales", "sum"),
            mean_duration_min=("duration_min", "mean"),
            mean_sales_per_guest=("sales_per_guest", "mean"),
            mean_guests=("guests", "mean"),
            n_bills=("bill_no", "nunique"),
        )
        .reset_index()
    )
    if len(daily):
        med = float(daily["day_sales_total"].median())
        daily["day_sales_category"] = np.where(daily["day_sales_total"] >= med, "高売上日", "低売上日")
    daily_metrics_csv = OUT_DATA_DIR / "daily_level_metrics_nakasei.csv"
    daily.sort_values(["business_date"]).to_csv(daily_metrics_csv, index=False, encoding="utf-8-sig")

    day_point_dir = OUT_CHART_DIR / "day_points"
    day_point_dir.mkdir(parents=True, exist_ok=True)
    # cleanup legacy day-point outputs (we now split all day-point plots by before/after 16:00)
    for p in day_point_dir.glob("*.png"):
        try:
            p.unlink()
        except Exception:
            pass
    shutil.rmtree(OUT_CHART_DIR / "day_points_non_sales", ignore_errors=True)

    # Day-point (split by entry time): 16時前入店 / 16時以降入店（左右2面）
    daily_split = (
        agg.groupby(["business_date", "entry_16_bucket"], dropna=False)
        .agg(
            mean_duration_min=("duration_min", "mean"),
            mean_sales_per_guest=("sales_per_guest", "mean"),
            mean_guests=("guests", "mean"),
            n_bills=("bill_no", "nunique"),
        )
        .reset_index()
    )
    # attach day-level sales + category (same threshold as `daily`)
    day_sales_map = daily.set_index("business_date")["day_sales_total"].to_dict() if len(daily) else {}
    day_cat_map = daily.set_index("business_date")["day_sales_category"].to_dict() if len(daily) else {}
    daily_split["day_sales_total"] = daily_split["business_date"].map(day_sales_map)
    daily_split["day_sales_category"] = daily_split["business_date"].map(day_cat_map)
    daily_split_metrics_csv = OUT_DATA_DIR / "daily_level_metrics_nakasei_split_before_after16.csv"
    daily_split.sort_values(["business_date", "entry_16_bucket"]).to_csv(
        daily_split_metrics_csv, index=False, encoding="utf-8-sig"
    )

    split_dir = day_point_dir / "split_before_after16"
    split_dir.mkdir(parents=True, exist_ok=True)
    before_df = daily_split[daily_split["entry_16_bucket"] == "16時前入店"].copy()
    after_df = daily_split[daily_split["entry_16_bucket"] == "16時以降入店"].copy()

    # day-point plots (all split)
    split_specs = [
        # 売上系
        ("mean_duration_min", "day_sales_total", "日別売上合計 × 平均滞在時間", "平均滞在時間（分）", "日別売上合計（円）"),
        ("mean_sales_per_guest", "day_sales_total", "日別売上合計 × 平均客単価", "平均客単価（円）", "日別売上合計（円）"),
        ("mean_guests", "day_sales_total", "日別売上合計 × 平均客数", "平均客数（人）", "日別売上合計（円）"),
        ("n_bills", "day_sales_total", "日別売上合計 × 伝票数", "伝票数（件）", "日別売上合計（円）"),
        # 非売上軸同士
        ("mean_duration_min", "mean_sales_per_guest", "平均客単価 × 平均滞在時間", "平均滞在時間（分）", "平均客単価（円）"),
        ("mean_duration_min", "mean_guests", "平均客数 × 平均滞在時間", "平均滞在時間（分）", "平均客数（人）"),
        ("n_bills", "mean_duration_min", "平均滞在時間 × 伝票数", "伝票数（件）", "平均滞在時間（分）"),
        ("n_bills", "mean_guests", "平均客数 × 伝票数", "伝票数（件）", "平均客数（人）"),
        ("mean_sales_per_guest", "mean_guests", "平均客単価 × 平均客数", "平均客数（人）", "平均客単価（円）"),
    ]
    for x, y, title, xl, yl in split_specs:
        out = split_dir / f"{y}_vs_{x}__before_after16.png"
        scatter_facets_two_panels(
            before_df,
            after_df,
            x=x,
            y=y,
            hue="day_sales_category",
            palette=day_palette,
            hue_order=["低売上日", "高売上日"],
            title=f"{title}（色=日別売上の高低）",
            left_title="16時前入店",
            right_title="16時以降入店",
            out_path=out,
            x_label=xl,
            y_label=yl,
            trim_pct=0.10,
        )
        day_point_images.append(out)

    # Group-level: non-sales axes (neither axis is sales / sales_per_guest)
    non_sales_dir = OUT_CHART_DIR / "non_sales"
    non_sales_dir.mkdir(parents=True, exist_ok=True)
    non_sales_specs = [
        ("duration_min", "guests", "客数 × 滞在時間"),
        ("duration_min", "total_items", "総商品数 × 滞在時間"),
        ("guests", "total_items", "総商品数 × 客数"),
        ("guests", "items_per_guest", "一人あたり商品数 × 客数"),
    ]
    for x, y, title in non_sales_specs:
        out = non_sales_dir / f"{y}_vs_{x}.png"
        scatter(
            agg,
            x=x,
            y=y,
            hue="day_sales_category",
            palette=day_palette,
            hue_order=["低売上日", "高売上日"],
            title=f"{title}（色=日別売上の高低）",
            out_path=out,
            x_label={
                "duration_min": "滞在時間（分）",
                "guests": "客数（人）",
                "total_items": "総商品数（点）",
                "items_per_guest": "一人あたり商品数（点/人）",
            }.get(x, x),
            y_label={
                "duration_min": "滞在時間（分）",
                "guests": "客数（人）",
                "total_items": "総商品数（点）",
                "items_per_guest": "一人あたり商品数（点/人）",
            }.get(y, y),
        )
        images.append(out)

    gallery_md = write_gallery_md(
        images,
        metrics_csv,
        day_sales_median=day_sales_median,
        day_point_images=day_point_images,
        daily_metrics_csv=daily_metrics_csv,
        corr_md=corr_md,
    )
    print("Wrote metrics:", metrics_csv)
    print("Wrote charts:", OUT_CHART_DIR)
    print("Wrote gallery:", gallery_md)


if __name__ == "__main__":
    main()

