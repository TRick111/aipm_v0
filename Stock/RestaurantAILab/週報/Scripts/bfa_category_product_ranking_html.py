#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BFA: カテゴリ別 商品売上ランキング（期間指定）→ HTML出力

要件:
- 期間(start/end)をパラメータで指定（business_dateベース）
- カテゴリ内で「売上金額」降順のランキング
- 商品数が10以上のカテゴリは Top5 / Bottom5 のみ表示
- 出力: 販売数(個数), 売上金額, カテゴリ内構成比, 全体構成比
- HTMLで見やすい表形式で出力

Usage:
  python bfa_category_product_ranking_html.py \
    --sales-data "/path/to/rawdata.csv" \
    --start-date 2026-01-19 \
    --end-date   2026-01-25 \
    --output-html "/path/to/output/category_product_ranking.html"

NOTE:
  週報プロジェクトの `1_input/BFA/rawdata.csv` は「最新週まで入っていること」が前提です。
  もし指定期間が入っていない場合は、エラーメッセージに rawdata 内の business_date 範囲が表示されます。
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BFA カテゴリ別商品売上ランキング（HTML出力）")
    parser.add_argument("--sales-data", required=True, help="売上データCSV（rawdata.csv）")
    parser.add_argument("--start-date", required=True, help="開始日（YYYY-MM-DD, business_date）")
    parser.add_argument("--end-date", required=True, help="終了日（YYYY-MM-DD, business_date）")
    parser.add_argument("--output-html", required=True, help="出力HTMLパス")
    parser.add_argument("--store-code", default=None, help="store_codeで絞り込み（任意）")
    parser.add_argument("--timezone", default="Asia/Tokyo", help="entry_atの変換先TZ（既定: Asia/Tokyo）")
    parser.add_argument("--shift-hour", type=int, default=6, help="0〜(shift-hour-1)は前日営業日扱い（既定: 6）")
    return parser.parse_args()


def _parse_yyyy_mm_dd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _compute_business_date(entry_at_jst: pd.Series, shift_hour: int) -> pd.Series:
    # 営業日定義（JST 0-5時は前日の営業日）
    return entry_at_jst.apply(
        lambda dt: (dt - pd.Timedelta(days=1)).date() if 0 <= dt.hour < shift_hour else dt.date()
    )


def load_sales_data(
    sales_csv: str,
    start_date: date,
    end_date: date,
    *,
    timezone: str,
    shift_hour: int,
    store_code: Optional[str] = None,
) -> pd.DataFrame:
    df = pd.read_csv(sales_csv)

    # 必須カラムチェック（不足してもエラーが分かりやすいように）
    required_cols = {"entry_at", "menu_name", "category1"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"必須カラムが見つかりません: {sorted(missing)}")

    # entry_at: UTC前提 → JST変換
    entry = pd.to_datetime(df["entry_at"], utc=True, errors="coerce")
    if entry.isna().all():
        raise ValueError("entry_at の日時変換に失敗しました（全件NaT）。CSVの形式を確認してください。")
    df["entry_at_jst"] = entry.dt.tz_convert(timezone)
    df["business_date"] = _compute_business_date(df["entry_at_jst"], shift_hour=shift_hour)

    available_min = df["business_date"].min()
    available_max = df["business_date"].max()

    # 期間フィルタ（inclusive）
    mask = (df["business_date"] >= start_date) & (df["business_date"] <= end_date)
    df = df.loc[mask].copy()

    if store_code:
        if "store_code" not in df.columns:
            raise ValueError("--store-code が指定されましたが、CSVに store_code 列がありません。")
        df = df.loc[df["store_code"] == store_code].copy()

    if df.empty:
        raise ValueError(
            "指定期間にデータがありません: "
            f"{start_date} 〜 {end_date} / "
            f"データに含まれるbusiness_date範囲: {available_min} 〜 {available_max}"
        )

    # 売上列の決定: subtotal優先、なければ price*quantity
    if "subtotal" in df.columns:
        df["_sales"] = pd.to_numeric(df["subtotal"], errors="coerce").fillna(0.0)
    else:
        price = pd.to_numeric(df.get("price"), errors="coerce").fillna(0.0)
        qty = pd.to_numeric(df.get("quantity"), errors="coerce").fillna(0.0)
        df["_sales"] = price * qty

    if "quantity" in df.columns:
        df["_qty"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
    else:
        # quantity列が無い場合は行数を販売数とする（最後の手段）
        df["_qty"] = 1.0

    df["category1"] = df["category1"].fillna("未設定").astype(str)
    df["menu_name"] = df["menu_name"].fillna("(不明)").astype(str)
    return df


@dataclass(frozen=True)
class CategoryMeta:
    category_sales: float
    category_share_overall_pct: float
    product_count: int


def build_rankings(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    戻り値:
      - category_summary: カテゴリ別サマリ
      - product_summary:  カテゴリ×商品別サマリ（構成比付き）
    """
    total_sales = float(df["_sales"].sum())
    if total_sales <= 0:
        # 0売上でも比率計算できるように（0割を避ける）
        total_sales = 0.0

    product = (
        df.groupby(["category1", "menu_name"], dropna=False)
        .agg(sales=("_sales", "sum"), quantity=("_qty", "sum"))
        .reset_index()
    )

    category = (
        df.groupby(["category1"], dropna=False)
        .agg(category_sales=("_sales", "sum"))
        .reset_index()
    )

    # マージして構成比
    product = product.merge(category, on="category1", how="left")
    if total_sales > 0:
        product["overall_share_pct"] = (product["sales"] / total_sales * 100.0)
        category["overall_share_pct"] = (category["category_sales"] / total_sales * 100.0)
    else:
        product["overall_share_pct"] = 0.0
        category["overall_share_pct"] = 0.0

    # カテゴリ内構成比
    product["category_share_pct"] = product.apply(
        lambda r: (r["sales"] / r["category_sales"] * 100.0) if r["category_sales"] else 0.0, axis=1
    )

    # 表示用の丸めは最後に（集計はfloatのまま保持）
    return category, product


def _fmt_currency(yen: float) -> str:
    return f"¥{yen:,.0f}"


def _fmt_int(n: float) -> str:
    # quantityがfloatになっても見た目は整数寄せ（小数がある場合はそのまま）
    if float(n).is_integer():
        return f"{int(n):,}"
    return f"{n:,.2f}"


def _fmt_pct(p: float) -> str:
    return f"{p:.2f}%"


def _make_table_html(df: pd.DataFrame, *, caption: Optional[str] = None) -> str:
    # pandasのHTMLを使い、classを付与してCSSで整形
    html = df.to_html(index=False, escape=True, classes=["tbl"], border=0)
    if caption:
        # `<table ...>` の直後に `<caption>` を挿入
        html = html.replace(">", f"><caption>{caption}</caption>", 1)
    return html


def render_html(
    *,
    start_date: date,
    end_date: date,
    store_code: Optional[str],
    shift_hour: int,
    category_df: pd.DataFrame,
    product_df: pd.DataFrame,
) -> str:
    total_sales = float(category_df["category_sales"].sum())

    palette = [
        "#ef5350",  # red
        "#42a5f5",  # blue
        "#66bb6a",  # green
        "#ab47bc",  # purple
        "#ffa726",  # orange
        "#26c6da",  # cyan
        "#78909c",  # blue grey
        "#ffca28",  # amber
    ]

    def category_color(name: str) -> str:
        # stable hash → color index
        h = hashlib.md5(name.encode("utf-8")).hexdigest()
        idx = int(h[:8], 16) % len(palette)
        return palette[idx]

    # カテゴリ（売上順）
    cat = category_df.copy()
    cat = cat.sort_values("category_sales", ascending=False)

    sections: list[str] = []

    # 各カテゴリのランキング
    for _, crow in cat.iterrows():
        category = str(crow["category1"])
        cat_sales = float(crow["category_sales"])

        p = product_df.loc[product_df["category1"] == category].copy()
        p = p.sort_values(["sales", "menu_name"], ascending=[False, True])
        product_count = len(p)

        header_color = category_color(category)
        header = (
            f"<div class='cat-header' style='background:{header_color}'>"
            f"<span class='cat-title'>{category}</span>"
            f"</div>"
            f"<div class='cat-meta'>"
            f"<span><b>カテゴリ売上</b>: {_fmt_currency(cat_sales)}</span>"
            f"<span><b>商品数</b>: {product_count}</span>"
            f"</div>"
        )

        if product_count >= 10:
            top = p.head(5).copy()
            bottom = p.tail(5).sort_values(["sales", "menu_name"], ascending=[True, True]).copy()

            top["順位"] = range(1, len(top) + 1)
            bottom["順位"] = range(1, len(bottom) + 1)

            top_disp = pd.DataFrame(
                {
                    "順位": top["順位"],
                    "商品名": top["menu_name"],
                    "販売数": top["quantity"].map(_fmt_int),
                    "売上": top["sales"].map(_fmt_currency),
                    "カテゴリ内構成比": top["category_share_pct"].map(_fmt_pct),
                }
            )
            bottom_disp = pd.DataFrame(
                {
                    "順位": bottom["順位"],
                    "商品名": bottom["menu_name"],
                    "販売数": bottom["quantity"].map(_fmt_int),
                    "売上": bottom["sales"].map(_fmt_currency),
                    "カテゴリ内構成比": bottom["category_share_pct"].map(_fmt_pct),
                }
            )

            body = (
                _make_table_html(top_disp, caption="Top 5（売上降順）")
                + _make_table_html(bottom_disp, caption="Bottom 5（売上昇順）")
            )
        else:
            p["順位"] = range(1, len(p) + 1)
            disp = pd.DataFrame(
                {
                    "順位": p["順位"],
                    "商品名": p["menu_name"],
                    "販売数": p["quantity"].map(_fmt_int),
                    "売上": p["sales"].map(_fmt_currency),
                    "カテゴリ内構成比": p["category_share_pct"].map(_fmt_pct),
                }
            )
            body = _make_table_html(disp, caption="ランキング（売上降順）")

        sections.append(f"<section class='cat-card'>{header}{body}</section>")

    # ヘッダー表示用（ユーザー要望）
    title = "🏆 売り上げランキング"
    subtitle = f"対象期間: {start_date} 〜 {end_date}　｜　総売上: {_fmt_currency(total_sales)}"

    css = """
    :root {
      --bg:#f4f7fb;
      --text:#1f2a44;
      --muted:#6b7a99;
      --line:#e5eaf3;
      --card:#ffffff;
      --shadow: 0 6px 18px rgba(31,42,68,0.10);
      --header:#1e4fd6;
    }
    /* PDF印刷で色が落ちるのを防ぐ（ブラウザ側の設定も必要な場合あり） */
    html, body, * {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Hiragino Sans', 'Noto Sans JP', Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    .topbar {
      background: linear-gradient(180deg, #1e4fd6, #1943b7);
      color: #fff;
      padding: 18px 20px;
      box-shadow: 0 10px 22px rgba(0,0,0,0.12);
    }
    .topbar h1 { margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.2px; }
    .topbar .sub { margin: 6px 0 0; opacity: 0.95; font-size: 13px; }
    .container { max-width: 1100px; margin: 18px auto 40px; padding: 0 16px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    @media (max-width: 860px) {
      .grid { grid-template-columns: 1fr; }
    }
    .cat-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .cat-header {
      padding: 10px 12px;
      color: #fff;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .cat-title { font-size: 14px; }
    .cat-meta {
      padding: 10px 12px 0;
      color: var(--muted);
      display:flex;
      gap: 14px;
      flex-wrap: wrap;
      font-size: 12px;
    }
    .cat-meta b { color: var(--text); }
    table.tbl {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 12px;
    }
    table.tbl caption {
      text-align: left;
      color: var(--muted);
      padding: 0 12px 8px;
      font-weight: 700;
      font-size: 12px;
    }
    table.tbl thead th {
      background: #f0f4ff;
      color: var(--text);
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
      font-size: 12px;
      text-align: left;
      position: sticky;
      top: 0;
    }
    table.tbl td {
      border-bottom: 1px solid var(--line);
      padding: 7px 10px;
      font-size: 12px;
      background: #fff;
    }
    table.tbl tr:nth-child(even) td { background: #fbfcff; }
    table.tbl td:nth-child(1) { width: 56px; }
    /* 右寄せ: 販売数/売上/構成比 */
    table.tbl td:nth-child(3), table.tbl td:nth-child(4), table.tbl td:nth-child(5) { text-align: right; }
    .footer { color: var(--muted); font-size: 12px; margin-top: 14px; }

    @media print {
      @page { margin: 10mm; }
      body { background: #ffffff !important; }
      .topbar {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      .cat-card, .cat-header, table.tbl thead th, table.tbl td {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      /* 影は印刷で汚く見えることがあるので弱める */
      .cat-card { box-shadow: none !important; }
    }
    """

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # カテゴリカード部分は2列グリッドで配置
    grid_html = "<div class='grid'>" + "".join(sections) + "</div>"

    html = f"""<!doctype html>
    <html lang="ja">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>{title}</title>
      <style>{css}</style>
    </head>
    <body>
      <header class="topbar">
        <h1>{title}</h1>
        <p class="sub">{subtitle}</p>
      </header>
      <main class="container">
        {grid_html}
      </main>
    </body>
    </html>
    """
    return html


def main() -> None:
    args = parse_args()
    start = _parse_yyyy_mm_dd(args.start_date)
    end = _parse_yyyy_mm_dd(args.end_date)
    if start > end:
        raise ValueError("start-date は end-date 以下にしてください。")

    df = load_sales_data(
        args.sales_data,
        start,
        end,
        timezone=args.timezone,
        shift_hour=args.shift_hour,
        store_code=args.store_code,
    )

    category_df, product_df = build_rankings(df)
    html = render_html(
        start_date=start,
        end_date=end,
        store_code=args.store_code,
        shift_hour=args.shift_hour,
        category_df=category_df,
        product_df=product_df,
    )

    out = Path(args.output_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"HTML出力: {out}")


if __name__ == "__main__":
    main()

