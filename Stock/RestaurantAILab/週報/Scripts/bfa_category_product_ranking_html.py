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
import re
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
    # 互換性のため --output-html は残しつつ、未指定時は命名規則で自動生成できるようにする
    parser.add_argument("--output-html", required=False, default=None, help="出力HTMLパス（未指定なら --output-dir から自動生成）")
    parser.add_argument("--output-dir", required=False, default=None, help="出力ディレクトリ（--output-html 未指定時に使用）")
    parser.add_argument("--store-name", required=False, default=None, help="ファイル名に入れる店舗名（例: BARFIveArrows）")
    parser.add_argument("--store-code", default=None, help="store_codeで絞り込み（任意）")
    parser.add_argument("--timezone", default="Asia/Tokyo", help="entry_atの変換先TZ（既定: Asia/Tokyo）")
    parser.add_argument("--shift-hour", type=int, default=6, help="0〜(shift-hour-1)は前日営業日扱い（既定: 6）")
    parser.add_argument("--slide", action="store_true", default=False, help="スライド形式（A4横・ページ分割）で出力")
    return parser.parse_args()


def _parse_yyyy_mm_dd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _sanitize_filename_component(s: str) -> str:
    """
    ファイル名に安全に入れられる形にする（最低限のサニタイズ）。
    - スラッシュ等の禁止文字 → '_'
    - 空白 → ''（詰める）
    """
    s = (s or "").strip()
    s = s.replace(" ", "").replace("　", "")
    s = re.sub(r'[\\\\/:"*?<>|]+', "_", s)
    return s


def _guess_store_name(*, sales_data: str, store_code: Optional[str], store_name: Optional[str]) -> str:
    if store_name and store_name.strip():
        return _sanitize_filename_component(store_name)
    if store_code and str(store_code).strip():
        return _sanitize_filename_component(str(store_code))
    # スクリプトがBFA専用なので、分かる場合はBFAを採用
    p = str(sales_data)
    if "BFA" in p or "/BFA/" in p or "\\BFA\\" in p:
        return "BARFIveArrows"
    return "店舗"


def build_default_output_path(*, start_date: date, end_date: date, store_name: str, output_dir: str) -> Path:
    """
    命名規則:
      yyyymmdd_yyyymmdd＜店舗名＞売り上げランキング.html
    """
    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")
    store = _sanitize_filename_component(store_name)
    filename = f"{start}_{end}{store}売り上げランキング.html"
    return Path(output_dir) / filename


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

    # entry_at は JST ナイーブ文字列（Dashboard API が formatUTCtoJST で生成）。
    # tz_localize で TZ 情報のみ付与する（+9hシフトはしない）。
    # 参照: _investigations/2026-06-10_timezone_bug.md
    entry = pd.to_datetime(df["entry_at"], errors="coerce")
    if entry.isna().all():
        raise ValueError("entry_at の日時変換に失敗しました（全件NaT）。CSVの形式を確認してください。")
    df["entry_at_jst"] = entry.dt.tz_localize(timezone)

    # === Sanity check: rawdata.csv の day_of_week 列と JST 解釈の整合性 ===
    # rawdata.csv の day_of_week は Dashboard API が entry_at の暦日（JST）から
    # 算出した曜日を入れているため、entry_at_jst.dt.dayofweek と一致するはず。
    # UTC 誤解釈（+9h シフト）が混入すると本チェックが落ちる。
    if "day_of_week" in df.columns:
        _dow_map_ja = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
        _dow_calc = df["entry_at_jst"].dt.dayofweek.map(_dow_map_ja)
        _mask = df["day_of_week"].notna() & df["entry_at_jst"].notna()
        _total = int(_mask.sum())
        _match = int((_dow_calc[_mask].values == df.loc[_mask, "day_of_week"].values).sum())
        _rate = _match / _total if _total else 0
        print(f"[sanity] entry_at JST 解釈の day_of_week 整合率: {_match}/{_total} = {_rate:.1%}")
        assert _rate >= 0.95, f"day_of_week整合率が95%未満（{_rate:.1%}）。rawdata.csvの時刻列がJSTでない可能性あり。要調査。"

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


def _estimate_card_height(product_count: int, has_top_bottom: bool) -> int:
    """カードの推定高さ（mm単位の概算）を返す。安全マージン10%込み。"""
    header_mm = 15  # ヘッダー＋メタ行
    row_mm = 5      # テーブル1行あたり
    table_header_mm = 6  # theadの高さ
    caption_mm = 5  # caption行
    gap_mm = 4      # カード間余白

    if has_top_bottom:
        base = header_mm + (table_header_mm + caption_mm + row_mm * 5) * 2 + gap_mm
    else:
        base = header_mm + table_header_mm + caption_mm + row_mm * product_count + gap_mm

    return int(base * 1.10)  # 10%安全マージン


def render_slide_html(
    *,
    start_date: date,
    end_date: date,
    store_code: Optional[str],
    shift_hour: int,
    category_df: pd.DataFrame,
    product_df: pd.DataFrame,
) -> str:
    """スライド形式（A4横・ページ分割）でHTML出力。"""
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
        h = hashlib.md5(name.encode("utf-8")).hexdigest()
        idx = int(h[:8], 16) % len(palette)
        return palette[idx]

    # カテゴリ（売上順）
    cat = category_df.copy()
    cat = cat.sort_values("category_sales", ascending=False)

    # ── カテゴリカードHTML生成 ──
    card_list: list[dict] = []  # {html, height_mm, category}
    for _, crow in cat.iterrows():
        category = str(crow["category1"])
        cat_sales = float(crow["category_sales"])

        p = product_df.loc[product_df["category1"] == category].copy()
        p = p.sort_values(["sales", "menu_name"], ascending=[False, True])
        product_count = len(p)
        has_top_bottom = product_count >= 10

        header_color = category_color(category)
        overall_pct = float(crow["overall_share_pct"]) if "overall_share_pct" in crow.index else 0.0
        header = (
            f"<div class='cat-header' style='background:{header_color}'>"
            f"<span class='cat-title'>{category}</span>"
            f"</div>"
            f"<div class='cat-meta'>"
            f"<span><b>カテゴリ売上</b>: {_fmt_currency(cat_sales)}（全体の{overall_pct:.1f}%）</span>"
            f"<span><b>商品数</b>: {product_count}</span>"
            f"</div>"
        )

        if has_top_bottom:
            top = p.head(5).copy()
            bottom = p.tail(5).sort_values(["sales", "menu_name"], ascending=[True, True]).copy()
            top["順位"] = range(1, len(top) + 1)
            bottom["順位"] = range(1, len(bottom) + 1)
            top_disp = pd.DataFrame({
                "順位": top["順位"], "商品名": top["menu_name"],
                "販売数": top["quantity"].map(_fmt_int),
                "売上": top["sales"].map(_fmt_currency),
                "カテゴリ内構成比": top["category_share_pct"].map(_fmt_pct),
            })
            bottom_disp = pd.DataFrame({
                "順位": bottom["順位"], "商品名": bottom["menu_name"],
                "販売数": bottom["quantity"].map(_fmt_int),
                "売上": bottom["sales"].map(_fmt_currency),
                "カテゴリ内構成比": bottom["category_share_pct"].map(_fmt_pct),
            })
            body = (
                _make_table_html(top_disp, caption="Top 5（売上降順）")
                + _make_table_html(bottom_disp, caption="Bottom 5（売上昇順）")
            )
        else:
            p["順位"] = range(1, len(p) + 1)
            disp = pd.DataFrame({
                "順位": p["順位"], "商品名": p["menu_name"],
                "販売数": p["quantity"].map(_fmt_int),
                "売上": p["sales"].map(_fmt_currency),
                "カテゴリ内構成比": p["category_share_pct"].map(_fmt_pct),
            })
            body = _make_table_html(disp, caption="ランキング（売上降順）")

        card_html = f"<div class='cat-card'>{header}{body}</div>"
        est_h = _estimate_card_height(product_count, has_top_bottom)
        card_list.append({"html": card_html, "height_mm": est_h, "category": category})

    # ── カードをスライド（ページ）にグルーピング ──
    # CSSグリッド2列: 行ごとに2カードが並び、行高さは高い方に合う
    # A4横 210mm - topbar 8mm - footer 6mm - body padding 20mm
    MAX_SLIDE_HEIGHT = 176

    # まずカードを2個ずつ行ペアにまとめる
    row_pairs: list[dict] = []
    for i in range(0, len(card_list), 2):
        pair = card_list[i:i + 2]
        row_h = max(c["height_mm"] for c in pair)
        row_pairs.append({"cards": pair, "height_mm": row_h})

    # 行ペアをスライドに詰める
    slides: list[list[dict]] = []
    current_rows: list[dict] = []
    current_h = 0
    for row in row_pairs:
        if current_h + row["height_mm"] <= MAX_SLIDE_HEIGHT:
            current_rows.append(row)
            current_h += row["height_mm"]
        else:
            if current_rows:
                slides.append([c for r in current_rows for c in r["cards"]])
            current_rows = [row]
            current_h = row["height_mm"]
    if current_rows:
        slides.append([c for r in current_rows for c in r["cards"]])

    # ── タイトルスライド ──
    title = "🏆 カテゴリ別 売り上げランキング"
    subtitle = f"対象期間: {start_date} 〜 {end_date}"

    # カテゴリサマリ表（タイトルスライド用）── 上位12件 + 残りを「その他」に集約
    MAX_SUMMARY_ROWS = 12
    cat_summary_rows = ""
    cat_rows = list(cat.iterrows())
    shown = cat_rows[:MAX_SUMMARY_ROWS]
    rest = cat_rows[MAX_SUMMARY_ROWS:]

    for _, crow in shown:
        cname = str(crow["category1"])
        csales = float(crow["category_sales"])
        cpct = float(crow["overall_share_pct"]) if "overall_share_pct" in crow.index else 0.0
        color = category_color(cname)
        bar_w = max(cpct * 2.5, 2)
        cat_summary_rows += (
            f"<tr>"
            f"<td><span class='color-dot' style='background:{color}'></span>{cname}</td>"
            f"<td class='r'>{_fmt_currency(csales)}</td>"
            f"<td class='r'>{cpct:.1f}%</td>"
            f"<td><div class='bar' style='width:{bar_w}px;background:{color}'></div></td>"
            f"</tr>"
        )
    if rest:
        rest_sales = sum(float(crow["category_sales"]) for _, crow in rest)
        rest_pct = sum(float(crow.get("overall_share_pct", 0.0)) for _, crow in rest)
        cat_summary_rows += (
            f"<tr>"
            f"<td><span class='color-dot' style='background:#bbb'></span>他 {len(rest)}カテゴリ</td>"
            f"<td class='r'>{_fmt_currency(rest_sales)}</td>"
            f"<td class='r'>{rest_pct:.1f}%</td>"
            f"<td><div class='bar' style='width:{max(rest_pct*2.5,2)}px;background:#bbb'></div></td>"
            f"</tr>"
        )

    title_slide = f"""
    <div class="slide title-slide">
      <div class="slide-header">
        <h1>{title}</h1>
        <p class="slide-sub">{subtitle}</p>
      </div>
      <div class="title-content">
        <div class="kpi-row">
          <div class="kpi"><span class="kpi-label">総売上</span><span class="kpi-value">{_fmt_currency(total_sales)}</span></div>
          <div class="kpi"><span class="kpi-label">カテゴリ数</span><span class="kpi-value">{len(cat)}</span></div>
        </div>
        <table class="summary-tbl">
          <thead><tr><th>カテゴリ</th><th class="r">売上</th><th class="r">構成比</th><th></th></tr></thead>
          <tbody>{cat_summary_rows}</tbody>
        </table>
      </div>
      <div class="slide-footer">BAR FIVE Arrows ─ Weekly Sales Report</div>
    </div>
    """

    # ── コンテンツスライド ──
    content_slides_html = ""
    for i, slide_cards in enumerate(slides):
        cards_html = "".join(c["html"] for c in slide_cards)
        page_num = i + 2  # 1はタイトルスライド
        content_slides_html += f"""
    <div class="slide">
      <div class="slide-topbar">
        <span>{title}</span>
        <span>{subtitle}</span>
      </div>
      <div class="slide-body">
        <div class="card-grid">
          {cards_html}
        </div>
      </div>
      <div class="slide-footer">BAR FIVE Arrows ─ Weekly Sales Report　　{page_num} / {len(slides) + 1}</div>
    </div>
    """

    css = """
    @page {
      size: A4 landscape;
      margin: 0;
    }
    *, *::before, *::after {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    html, body {
      margin: 0; padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Hiragino Sans', 'Noto Sans JP', Arial, sans-serif;
      color: #1f2a44;
      background: #e8ecf2;
    }

    /* ── スライド共通 ── */
    .slide {
      width: 297mm; height: 210mm;
      background: #ffffff;
      position: relative;
      overflow: hidden;
      page-break-after: always;
      margin: 0 auto 20px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.12);
      display: flex;
      flex-direction: column;
    }
    .slide:last-child { page-break-after: auto; }

    @media print {
      body { background: #fff; }
      .slide {
        box-shadow: none;
        margin: 0;
        page-break-after: always;
      }
      .slide:last-child { page-break-after: auto; }
    }

    /* ── タイトルスライド ── */
    .title-slide .slide-header {
      background: linear-gradient(135deg, #1e4fd6 0%, #1943b7 100%);
      color: #fff;
      padding: 18mm 32mm 10mm;
    }
    .title-slide .slide-header h1 {
      margin: 0; font-size: 30px; font-weight: 900; letter-spacing: 0.5px;
    }
    .title-slide .slide-header .slide-sub {
      margin: 6px 0 0; font-size: 15px; opacity: 0.92;
    }
    .title-content {
      flex: 1;
      padding: 6mm 32mm 0;
      overflow: hidden;
    }
    .kpi-row {
      display: flex; gap: 24px; margin-bottom: 10px;
    }
    .kpi {
      background: #f0f4ff;
      border: 1px solid #e0e6f5;
      border-radius: 10px;
      padding: 8px 24px;
      display: flex; flex-direction: column; align-items: center;
    }
    .kpi-label { font-size: 10px; color: #6b7a99; font-weight: 600; }
    .kpi-value { font-size: 24px; font-weight: 900; color: #1e4fd6; margin-top: 2px; }

    .summary-tbl {
      width: 100%; border-collapse: collapse; font-size: 11px;
    }
    .summary-tbl th {
      background: #f0f4ff; border-bottom: 2px solid #d0d8ee;
      padding: 4px 10px; text-align: left; font-weight: 700; font-size: 10px; color: #4a5a80;
    }
    .summary-tbl td {
      padding: 3px 10px; border-bottom: 1px solid #eef1f7;
    }
    .summary-tbl .r { text-align: right; }
    .color-dot {
      display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 6px; vertical-align: middle;
    }
    .bar {
      height: 10px; border-radius: 4px; min-width: 2px;
    }

    /* ── コンテンツスライド ── */
    .slide-topbar {
      background: linear-gradient(135deg, #1e4fd6, #1943b7);
      color: #fff;
      padding: 8px 24px;
      display: flex; justify-content: space-between; align-items: center;
      font-size: 12px; font-weight: 700;
      flex-shrink: 0;
    }
    .slide-body {
      flex: 1;
      padding: 10px 20px;
      overflow: hidden;
    }
    .card-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      height: 100%;
      align-content: start;
    }
    .slide-footer {
      background: #f4f7fb;
      border-top: 1px solid #e5eaf3;
      padding: 5px 24px;
      font-size: 10px;
      color: #6b7a99;
      text-align: right;
      flex-shrink: 0;
    }

    /* ── カテゴリカード ── */
    .cat-card {
      background: #fff;
      border: 1px solid #e5eaf3;
      border-radius: 10px;
      overflow: hidden;
    }
    .cat-header {
      padding: 6px 10px;
      color: #fff;
      font-weight: 800;
      font-size: 13px;
    }
    .cat-title { font-size: 13px; }
    .cat-meta {
      padding: 5px 10px 0;
      color: #6b7a99;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      font-size: 10px;
    }
    .cat-meta b { color: #1f2a44; }

    table.tbl {
      width: 100%; border-collapse: collapse; margin: 4px 0 6px;
    }
    table.tbl caption {
      text-align: left; color: #6b7a99; padding: 0 10px 4px;
      font-weight: 700; font-size: 10px;
    }
    table.tbl thead th {
      background: #f0f4ff; color: #1f2a44;
      border-top: 1px solid #e5eaf3; border-bottom: 1px solid #e5eaf3;
      padding: 4px 8px; font-size: 10px; text-align: left;
    }
    table.tbl td {
      border-bottom: 1px solid #eef1f7; padding: 3px 8px; font-size: 10px;
    }
    table.tbl tr:nth-child(even) td { background: #fbfcff; }
    table.tbl td:nth-child(1) { width: 32px; }
    table.tbl td:nth-child(3), table.tbl td:nth-child(4), table.tbl td:nth-child(5) { text-align: right; }
    """

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  {title_slide}
  {content_slides_html}
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

    store_name = _guess_store_name(sales_data=args.sales_data, store_code=args.store_code, store_name=args.store_name)
    if args.output_html:
        out = Path(args.output_html)
    else:
        if not args.output_dir:
            raise ValueError("--output-html 未指定の場合は --output-dir を指定してください。")
        out = build_default_output_path(
            start_date=start,
            end_date=end,
            store_name=store_name,
            output_dir=args.output_dir,
        )

    df = load_sales_data(
        args.sales_data,
        start,
        end,
        timezone=args.timezone,
        shift_hour=args.shift_hour,
        store_code=args.store_code,
    )

    category_df, product_df = build_rankings(df)

    render_fn = render_slide_html if args.slide else render_html
    html = render_fn(
        start_date=start,
        end_date=end,
        store_code=args.store_code,
        shift_hour=args.shift_hour,
        category_df=category_df,
        product_df=product_df,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"HTML出力: {out}")


if __name__ == "__main__":
    main()

