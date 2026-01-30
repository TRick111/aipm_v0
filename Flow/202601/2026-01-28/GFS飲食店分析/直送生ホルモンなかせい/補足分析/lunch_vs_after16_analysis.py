import pandas as pd
from datetime import time
from pathlib import Path

INPUT_CSV = Path("/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-28/GFS飲食店分析/直送生ホルモンなかせい/data/intermediate/transformed_pos_data_eatin.csv")
OUT_DIR = Path("/Users/rikutanaka/aipm_v0/Flow/202601/2026-01-28/GFS飲食店分析/直送生ホルモンなかせい/補足分析")

# Definitions
START_BIZ_DATE = pd.Timestamp("2025-05-01")
LUNCH_START = time(12, 0, 0)
LUNCH_END = time(16, 0, 0)  # lunch: [12:00, 16:00)

def aggregate_by_time_window(
    df: pd.DataFrame,
    *,
    time_source_col: str,
    month_col: str = "month",
) -> pd.DataFrame:
    """
    Aggregate monthly group counts by time-of-day buckets:
      - lunch: [12:00, 16:00)
      - after16: [16:00, 24:00)
      - other: [00:00, 12:00)
    """
    t = pd.to_datetime(df[time_source_col], errors="coerce")
    ct = t.dt.time
    is_lunch = (ct >= LUNCH_START) & (ct < LUNCH_END)
    is_after16 = ct >= LUNCH_END

    out = (
        df.assign(is_lunch=is_lunch, is_after16=is_after16)
        .groupby(month_col)
        .agg(
            lunch_groups=("is_lunch", "sum"),
            after16_groups=("is_after16", "sum"),
            total_groups=("H.伝票番号", "count"),
        )
        .reset_index()
    )
    out["other_groups"] = out["total_groups"] - out["lunch_groups"] - out["after16_groups"]
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    usecols = [
        "H.伝票番号",
        "H.集計対象営業年月日",
        "H.伝票発行日",
        "H.伝票処理日",
    ]
    df = pd.read_csv(INPUT_CSV, usecols=usecols)

    # 1 receipt = 1 group
    # Use receipt number + business date as the unique key. (Header timestamps can vary slightly in some systems.)
    df = df.drop_duplicates(subset=["H.伝票番号", "H.集計対象営業年月日"]).copy()

    biz = pd.to_datetime(df["H.集計対象営業年月日"], errors="coerce")
    entry = pd.to_datetime(df["H.伝票発行日"], errors="coerce")
    checkout = pd.to_datetime(df["H.伝票処理日"], errors="coerce")

    df["biz_date"] = biz
    df["entry_dt"] = entry
    df["checkout_dt"] = checkout

    df = df[df["biz_date"] >= START_BIZ_DATE].copy()

    df["month"] = df["biz_date"].dt.to_period("M").astype(str)

    # A) Checkout-time definition (kept for reference)
    out_checkout = aggregate_by_time_window(df, time_source_col="checkout_dt")
    out_checkout_csv = OUT_DIR / "lunch_vs_after16_by_month_checkout.csv"
    out_checkout.to_csv(out_checkout_csv, index=False, encoding="utf-8")

    out_checkout_md = OUT_DIR / "lunch_vs_after16_by_month_checkout.md"
    md_lines = []
    md_lines.append("# ランチ帯（12:00-16:00会計）vs 16:00以降 会計組数（月別）\n")
    md_lines.append("## 前提\n")
    md_lines.append("- 対象データ: transformed_pos_data_eatin.csv（EAT IN）\n")
    md_lines.append("- 1組=1伝票（`H.伝票番号`）として集計（商品明細行は重複除外）\n")
    md_lines.append("- 月の区切り: `H.集計対象営業年月日` の年月\n")
    md_lines.append("- ランチ: 会計時刻（`H.伝票処理日`）が 12:00〜16:00（16:00は含まない）\n")
    md_lines.append("- 16:00以降: 会計時刻が 16:00以降\n")
    md_lines.append("- 参考: other_groups は 12:00より前の会計（ランチでも16:00以降でもない）\n")
    md_lines.append("## 結果（2025-05以降）\n")
    md_lines.append("| 月 | ランチ(12-16)組数 | 16:00以降組数 | その他(12:00前) | 合計 |\n")
    md_lines.append("|---|---:|---:|---:|---:|\n")
    for _, r in out_checkout.iterrows():
        md_lines.append(
            f"| {r['month']} | {int(r['lunch_groups'])} | {int(r['after16_groups'])} | {int(r['other_groups'])} | {int(r['total_groups'])} |\n"
        )
    out_checkout_md.write_text("".join(md_lines), encoding="utf-8")

    # B) Entry-time definition (requested)
    out_entry = aggregate_by_time_window(df, time_source_col="entry_dt")
    out_entry_csv = OUT_DIR / "lunch_vs_after16_by_month_entry.csv"
    out_entry.to_csv(out_entry_csv, index=False, encoding="utf-8")

    out_entry_md = OUT_DIR / "lunch_vs_after16_by_month_entry.md"
    md_lines = []
    md_lines.append("# ランチ帯（12:00-16:00入店）vs 16:00以降 入店組数（月別）\n")
    md_lines.append("## 前提\n")
    md_lines.append("- 対象データ: transformed_pos_data_eatin.csv（EAT IN）\n")
    md_lines.append("- 1組=1伝票（`H.伝票番号`）として集計（商品明細行は重複除外）\n")
    md_lines.append("- 月の区切り: `H.集計対象営業年月日` の年月\n")
    md_lines.append("- ランチ: 入店時刻（`H.伝票発行日`）が 12:00〜16:00（16:00は含まない）\n")
    md_lines.append("- 16:00以降: 入店時刻が 16:00以降\n")
    md_lines.append("- 参考: other_groups は 12:00より前の入店（ランチでも16:00以降でもない）\n")
    md_lines.append("## 結果（2025-05以降）\n")
    md_lines.append("| 月 | ランチ(12-16)組数 | 16:00以降組数 | その他(12:00前) | 合計 |\n")
    md_lines.append("|---|---:|---:|---:|---:|\n")
    for _, r in out_entry.iterrows():
        md_lines.append(
            f"| {r['month']} | {int(r['lunch_groups'])} | {int(r['after16_groups'])} | {int(r['other_groups'])} | {int(r['total_groups'])} |\n"
        )
    out_entry_md.write_text("".join(md_lines), encoding="utf-8")

    print(f"Wrote: {out_checkout_csv}")
    print(f"Wrote: {out_checkout_md}")
    print(f"Wrote: {out_entry_csv}")
    print(f"Wrote: {out_entry_md}")


if __name__ == "__main__":
    main()
