#!/usr/bin/env python3
"""
月報 HTML生成（汎用化版）— v2.1 / 2026-05-18

5Arrowsフィードバック（v1.2 イテレーション1〜9）を恒久反映した正規スクリプト。
PL対応 / ダークグリーン基調 / 27枚スライド / 840pxキャンバス / 凡例必須 / 円グラフ /
メッセージ帯 / 分類条件帯（箇条書き）。

使い方:
    python build_monthly_html.py \\
      --analysis-json "path/to/analysis.json" \\
      --output "path/to/YYYYMM_STORE_月次報告資料_v2draft.html" \\
      [--store-name "BAR FIVE Arrows"]
"""
import json
import os
import argparse
import sys
import calendar

_parser = argparse.ArgumentParser(description="月報HTMLビルダー（汎用化版 v2.1）")
_parser.add_argument("--analysis-json", required=True, help="入力 analysis.json")
_parser.add_argument("--output", required=True, help="出力HTMLパス")
_parser.add_argument("--store-name", default="BAR FIVE Arrows", help="店舗名")
_args = _parser.parse_args()

OUT = _args.output
STORE_NAME = _args.store_name
with open(_args.analysis_json, "r", encoding="utf-8") as f:
    D = json.load(f)

_tm = D.get("target_month", "2026-04")
_y, _m = map(int, _tm.split("-"))
_last_day = calendar.monthrange(_y, _m)[1]
_PERIOD_DASH = f"{_y}-{_m:02d}-01〜{_y}-{_m:02d}-{_last_day:02d}"
_PERIOD_JP = f"{_y}年{_m}月1日 0:00 〜 {_m}月{_last_day}日 23:59"
_PERIOD_JP_HEADER = f"{_y}年{_m}月（{_m}/1 〜 {_m}/{_last_day}）"

# ============================================
# 数値フォーマッタ
# ============================================
def yen(n):
    if n is None: return "—"
    return f"¥{int(round(n)):,}"
def pct(p):
    if p is None: return "—"
    return f"{p:+.1f}%"
def pctv(p):
    if p is None: return "—"
    return f"{p:.1f}%"
def diff_pct(cur, prev):
    if prev is None or prev == 0: return "—"
    return f"{(cur/prev-1)*100:+.1f}%"

# Convenience (汎用化: 対象月＝m04 名前を維持してビュー差し替え)
M = D["month_kpis"]
def _prev_month_str(s):
    y,mo=map(int,s.split('-')); mo-=1
    if mo==0: y-=1; mo=12
    return f"{y}-{mo:02d}"
def _prev_year_month_str(s):
    y,mo=map(int,s.split('-')); return f"{y-1}-{mo:02d}"
_TARGET = _tm                  # "2026-02"
_PREV   = _prev_month_str(_tm) # "2026-01"
_PREV_Y = _prev_year_month_str(_tm) # "2025-02"
m04 = M[_TARGET]
m03 = M.get(_PREV)
m04_py = M.get(_PREV_Y)
_MONTH_LABEL = f"{_m}月"  # ex: "2月"

# PL 利用可否（共通ルール §18）
_PL_OK = bool(D.get("pl",{}).get("available")) and bool(D.get("pl",{}).get("expense_breakdown"))

# Trend months: 当月から遡って6ヶ月（古い順）
def _shift(s, k):
    y,mo=map(int,s.split('-'))
    mo-=k
    while mo<=0: y-=1; mo+=12
    return f"{y}-{mo:02d}"
trend_months = [_shift(_TARGET, k) for k in range(5, -1, -1)]
trend_data = [(m, M[m]) for m in trend_months if m in M]

# ============================================
# HTMLビルド
# ============================================
TITLE = f"{STORE_NAME} 月次営業報告"
PERIOD = _PERIOD_JP_HEADER
FOOTER_NOTE = f"出典: エアレジ会計明細 ／ 集計対象: {_PERIOD_DASH}"
MONTHLY_SALES_NOTE = f"※月売上の集計対象: {_PERIOD_JP} の売上日時（エアレジ売上分析画面の表示と一致）。週次・日次・曜日別・時間帯別は営業日基準（朝6時境界）で別途集計。"

# Slides will be built as a list of dicts then rendered
slides = []

# ───────────────────────────────────────────────
# Slide 1: タイトル
# ───────────────────────────────────────────────
slides.append({
    "type": "title",
    "title": STORE_NAME,
    "subtitle": "月次営業報告",
    "period": _PERIOD_JP_HEADER,
    "note": "v1 / 2026-05-18 作成",
})

# ───────────────────────────────────────────────
# Slide 2: 月間サマリーKPI
# ───────────────────────────────────────────────
slides.append({
    "type": "kpi",
    "icon": "📊",
    "title": "月間サマリー（KPI）",
    "subtitle": None,
    "message_icon": "⚠️",
    "message": f"{_MONTH_LABEL}の売上は{yen(m04['sales_total'])}（前月比 {diff_pct(m04['sales_total'], m03['sales_total']) if m03 else '—'}／前年同月比 {diff_pct(m04['sales_total'], m04_py['sales_total']) if m04_py else '—'}）。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時（エアレジ売上分析画面と一致）",
        "PL系KPI（総費用／営業利益／FL率／人件費率）は【BFA】本部サポート / PLシートに該当月のデータがないため非表示",
    ] if not _PL_OK else [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時（エアレジ売上分析画面と一致）",
        "PL系KPI出典: 当月はダッシュボードDB／過去月は【BFA】本部サポート / PLシート",
        "FL率の分母 = 月次総売上（ボトル含む）。FL率 =（食材+ドリンク）÷ 売上",
    ],
    "kpis": [
        {"label": "💰 売上（総額）", "value": yen(m04["sales_total"]), "comp": [
            ("前月比", diff_pct(m04["sales_total"], m03["sales_total"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["sales_total"], m04_py["sales_total"]) if m04_py else "—"),
        ], "note": "ボトル含む"},
        {"label": "🍾 うちボトル購入", "value": yen(m04["bottle_sales"]), "comp": [
            ("構成比", pctv(m04["bottle_sales"]/m04["sales_total"]*100) if m04["sales_total"] else "—"),
        ]},
        {"label": "💰 売上（ボトル除く）", "value": yen(m04["sales_excl_bottle"]), "comp": [
            ("前月比", diff_pct(m04["sales_excl_bottle"], (m03["sales_excl_bottle"] if m03 else None))),
            ("前年同月比", diff_pct(m04["sales_excl_bottle"], (m04_py["sales_excl_bottle"] if m04_py else None))),
        ]},
        {"label": "👥 客数", "value": f"{m04['customers']:,}人", "comp": [
            ("前月比", diff_pct(m04["customers"], m03["customers"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["customers"], m04_py["customers"]) if m04_py else "—"),
        ]},
        {"label": "💴 客単価（ボトル除く）", "value": yen(m04["kyakutanka"]), "comp": [
            ("前月比", diff_pct(m04["kyakutanka"], m03["kyakutanka"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["kyakutanka"], m04_py["kyakutanka"]) if m04_py else "—"),
        ], "note": "経営判断用 ／ （売上−ボトル）÷客数"},
        {"label": "💴 客単価（全部込み）", "value": yen(m04["kyakutanka_with_bottle"]), "comp": [
            ("前月比", diff_pct(m04["kyakutanka_with_bottle"], m03["kyakutanka_with_bottle"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["kyakutanka_with_bottle"], m04_py["kyakutanka_with_bottle"]) if m04_py else "—"),
        ], "note": "エアメイト/エアレジ比較用 ／ 売上÷客数"},
        {"label": "📅 営業日数", "value": f"{m04['business_days']}日", "comp": [
            ("前月", f"{m03['business_days']}日" if m03 else "—"),
            ("前年同月", f"{m04_py['business_days']}日" if m04_py else "—"),
        ]},
        {"label": "📈 日平均売上", "value": yen(m04["daily_avg_sales"]), "comp": [
            ("前月比", diff_pct(m04["daily_avg_sales"], m03["daily_avg_sales"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["daily_avg_sales"], m04_py["daily_avg_sales"]) if m04_py else "—"),
        ], "note": "ボトル除く"},
    ] + ([
        {"label": "💸 総費用", "value": yen(D["pl"]["expense_total"]), "comp": [
            ("売上比", f"{D['pl']['expense_total']/m04['sales_total']*100:.1f}%"),
        ], "note": "9費目合計"},
        {"label": "📉 営業利益", "value": yen(D["pl"]["op_profit"]), "comp": [
            ("売上 − 費用", "—"),
        ], "note": "赤字計上" if D["pl"]["op_profit"] < 0 else None},
        {"label": "📊 営業利益率", "value": f"{D['pl']['op_profit_rate']:+.1f}%", "comp": [
            ("計算", "営業利益 ÷ 売上"),
        ]},
        {"label": "🍴 FL率", "value": f"{D['pl']['fl_rate']:.1f}%", "comp": [
            ("内訳", "食材+ドリンク"),
            ("目安", "60%前後"),
        ], "note": "売上比"},
        {"label": "👷 人件費率", "value": f"{D['pl']['labor_rate']:.1f}%", "comp": [
            ("内訳", "人件費"),
            ("目安", "30%前後"),
        ], "note": "売上比"},
    ] if _PL_OK else []),
    "caption": f"{_MONTH_LABEL}の売上 {yen(m04['sales_total'])}（前月比 {diff_pct(m04['sales_total'], m03['sales_total']) if m03 else '—'}）。PL系KPIはPLシート未入力のため非表示。" if not _PL_OK else f"{_MONTH_LABEL}実績ベースのKPIサマリー。PLは別スライドで詳細展開。",
})

# ───────────────────────────────────────────────
# Slide 3-5: 6ヶ月推移
# ───────────────────────────────────────────────
slides.append({
    "type": "line_chart",
    "icon": "📈",
    "title": "売上推移（直近6ヶ月）",
    "x_label": "月",
    "y_label": "売上（円）",
    "message_icon": "⚠️",
    "message": f"当月{yen(m04['sales_total'])}は前月{yen(m03['sales_total']) if m03 else '—'}（{diff_pct(m04['sales_total'], m03['sales_total']) if m03 else '—'}）、前年同月{yen(m04_py['sales_total']) if m04_py else '—'}（{diff_pct(m04['sales_total'], m04_py['sales_total']) if m04_py else '—'}）と比較し推移を確認できる。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時（エアレジ売上分析画面と一致）",
        "前年同月以前のデータはダッシュボード経由のエアレジ会計明細",
    ],
    "series": [
        {"name": "売上（総額）", "color": "#1B4D3E", "data": [(m, k["sales_total"]) for m, k in trend_data]},
        {"name": "売上（ボトル除く）", "color": "#C9A961", "data": [(m, k["sales_excl_bottle"]) for m, k in trend_data]},
    ],
    "highlight_last": True,
    "annotation": f"当月 {yen(m04['sales_total'])}（ボトル除く {yen(m04['sales_excl_bottle'])}）",
    "caption": f"直近6ヶ月の売上推移。当月{_MONTH_LABEL}は{yen(m04['sales_total'])}。",
})

slides.append({
    "type": "line_chart",
    "icon": "👥",
    "title": "客数推移（直近6ヶ月）",
    "x_label": "月",
    "y_label": "客数（人）",
    "unit": "人",
    "message_icon": "✅",
    "message": f"客数は前月{m03['customers']}人から当月{m04['customers']}人へ{diff_pct(m04['customers'], m03['customers'])}。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時",
        "客数=会計ヘッダーの『人数』合算（伝票数ではない）",
        "前年同月以前のデータはダッシュボード経由のエアレジ会計明細",
    ],
    "series": [
        {"name": "月次客数（人）", "color": "#1B4D3E", "data": [(m, k["customers"]) for m, k in trend_data]},
    ],
    "highlight_last": True,
    "annotation": f"当月 {m04['customers']}人",
    "caption": f"客数推移。当月{_MONTH_LABEL}は{m04['customers']:,}人。",
})

slides.append({
    "type": "line_chart",
    "icon": "💴",
    "title": "客単価推移（直近6ヶ月）",
    "x_label": "月",
    "y_label": "客単価（円）",
    "message_icon": "⚠️",
    "message": f"客単価（ボトル除く）は前月{yen(m03['kyakutanka'])}から当月{yen(m04['kyakutanka'])}（{diff_pct(m04['kyakutanka'], m03['kyakutanka'])}）。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時",
        "客単価=売上÷客数。実線はボトル購入を分子から除外（経営判断用）",
    ],
    "series": [
        {"name": "客単価（ボトル除く・経営判断用）", "color": "#1B4D3E", "dash": False,
         "data": [(m, k["kyakutanka"]) for m, k in trend_data]},
        {"name": "客単価（全部込み・エアメイト比較用）", "color": "#C9A961", "dash": True,
         "data": [(m, k["kyakutanka_with_bottle"]) for m, k in trend_data]},
    ],
    "highlight_last": True,
    "annotation": f"当月 ボトル除く{yen(m04['kyakutanka'])} / 全部込み{yen(m04['kyakutanka_with_bottle'])}",
    "caption": f"当月{_MONTH_LABEL}の客単価 ボトル除く{yen(m04['kyakutanka'])} / 全部込み{yen(m04['kyakutanka_with_bottle'])}。",
})

# ───────────────────────────────────────────────
# Slide 6: 前年同月比サマリ
# ───────────────────────────────────────────────
slides.append({
    "type": "comparison_table",
    "icon": "📅",
    "title": f"前年同月比（{_PREV_Y}との比較）",
    "message_icon": "⚠️",
    "message": f"売上は前年同月から{diff_pct(m04['sales_total'], m04_py['sales_total']) if m04_py else '—'}、客数は{diff_pct(m04['customers'], m04_py['customers']) if m04_py else '—'}。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時",
        f"前年同月（{_PREV_Y}）はダッシュボード経由のエアレジ会計明細から取得",
    ],
    "headers": ["指標", _TARGET, _PREV_Y, "前年比"],
    "rows": [
        ["売上（総額）", yen(m04["sales_total"]), yen(m04_py["sales_total"]) if m04_py else "—",
         diff_pct(m04["sales_total"], m04_py["sales_total"]) if m04_py else "—"],
        ["売上（ボトル除く）", yen(m04["sales_excl_bottle"]),
         yen(m04_py["sales_excl_bottle"]) if m04_py else "—",
         diff_pct(m04["sales_excl_bottle"], m04_py["sales_excl_bottle"]) if m04_py else "—"],
        ["客数", f"{m04['customers']:,}人", f"{m04_py['customers']:,}人" if m04_py else "—",
         diff_pct(m04["customers"], m04_py["customers"]) if m04_py else "—"],
        ["客単価（ボトル除く・経営判断用）", yen(m04["kyakutanka"]), yen(m04_py["kyakutanka"]) if m04_py else "—",
         diff_pct(m04["kyakutanka"], m04_py["kyakutanka"]) if m04_py else "—"],
        ["客単価（全部込み・エアメイト比較用）", yen(m04["kyakutanka_with_bottle"]),
         yen(m04_py["kyakutanka_with_bottle"]) if m04_py else "—",
         diff_pct(m04["kyakutanka_with_bottle"], m04_py["kyakutanka_with_bottle"]) if m04_py else "—"],
        ["営業日数", f"{m04['business_days']}日", f"{m04_py['business_days']}日" if m04_py else "—", "—"],
        ["日平均売上（ボトル除く）", yen(m04["daily_avg_sales"]),
         yen(m04_py["daily_avg_sales"]) if m04_py else "—",
         diff_pct(m04["daily_avg_sales"], m04_py["daily_avg_sales"]) if m04_py else "—"],
    ],
    "caption": f"前年同月（{_PREV_Y}）との比較サマリ。",
})

# ───────────────────────────────────────────────
# Slide 7: 【P1-1】インバウンド比率
# ───────────────────────────────────────────────
p11 = D["p1_1_inbound"]
slides.append({
    "type": "three_set",
    "icon": "🌏",
    "title": "客層分析①：インバウンド比率",
    "subtitle": "エアレジ会計明細のメモ欄から抽出",
    "message_icon": "✅",
    "message": f"{_MONTH_LABEL}はインバウンド客が{p11['customers']}人来店し、売上構成比{p11['share_sales']:.1f}%を占めた。Google検索経由が主流で、訪日客の取り込みが収益基盤の一角を形成している。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時",
        f"抽出キー: 会計ヘッダーの『メモ』カラムに『海外』を部分一致（{p11['accounts']}件ヒット）",
    ],
    "donut": {"target": "インバウンド", "value": p11["sales"], "rest": m04["sales_total"] - p11["sales"],
              "target_color": "#1B4D3E", "rest_color": "#E2E8F0",
              "center_sub": "売上構成比"},
    "left_label": "インバウンド",
    "right_label": "非インバウンド",
    "left": {
        "accounts": p11["accounts"],
        "customers": p11["customers"],
        "sales": p11["sales"],
        "share_sales": p11["share_sales"],
        "share_customers": p11["share_customers"],
    },
    "right": {
        "accounts": (m04["accounts"] - p11["accounts"]),  # April accounts in provided CSV
        "customers": m04["customers"] - p11["customers"],
        "sales": m04["sales_total"] - p11["sales"],
        "share_sales": 100 - p11["share_sales"],
        "share_customers": 100 - p11["share_customers"],
    },
    "caption": f"{_MONTH_LABEL}はインバウンド客が{p11['customers']}人来店、売上構成比 {p11['share_sales']:.1f}%。Google検索経由の来店が多数。",
})

# ───────────────────────────────────────────────
# Slide 8: 【P1-2】CLP社員比率
# ───────────────────────────────────────────────
p12 = D["p1_2_clp_employee"]
slides.append({
    "type": "three_set",
    "icon": "👤",
    "title": "客層分析②：CLP社員比率（単発利用）",
    "subtitle": "※P1-5コース・P1-6その他CLPコースと重複計上前提",
    "message_icon": "✅",
    "message": f"CLP関連の利用は{p12['accounts']}件・{p12['customers']}人で売上¥{p12['sales']:,.0f}（構成比{p12['share_sales']:.1f}%）を確保し、安定した法人系収益柱となっている。",
    "classification": "CLP社員 = エアレジ会計明細 の明細行『メニュー名』に『CLP』を部分一致で含む取引（注：P1-5コース・P1-6その他CLPコースと同一会計を含み、合計値は二重計上されている）",
    "donut": {"target": "CLP関連", "value": p12["sales"], "rest": m04["sales_total"] - p12["sales"],
              "target_color": "#C9A961", "rest_color": "#E2E8F0",
              "center_sub": "売上構成比"},
    "left_label": "CLP社員",
    "right_label": "それ以外",
    "left": {
        "accounts": p12["accounts"],
        "customers": p12["customers"],
        "sales": p12["sales"],
        "share_sales": p12["share_sales"],
        "share_customers": p12["share_customers"],
    },
    "right": {
        "accounts": m04["accounts"] - p12["accounts"],
        "customers": m04["customers"] - p12["customers"],
        "sales": m04["sales_total"] - p12["sales"],
        "share_sales": 100 - p12["share_sales"],
        "share_customers": 100 - p12["share_customers"],
    },
    "caption": f"CLP関連は{p12['accounts']}件・{p12['customers']}人で売上¥{p12['sales']:,.0f}（{p12['share_sales']:.1f}%）。客単価高めの大口利用。",
})

# ───────────────────────────────────────────────
# Slide 9: 【P1-3】イベント比率
# ───────────────────────────────────────────────
p13 = D["p1_3_event"]
slides.append({
    "type": "three_set",
    "icon": "🎉",
    "title": "客層分析③：イベント比率",
    "subtitle": f"対象月: {_MONTH_LABEL}",
    "message_icon": "✅",
    "message": f"{_MONTH_LABEL}のイベント売上は¥{p13['sales']:,.0f}（売上構成比{p13['share_sales']:.1f}%）、{p13['accounts']}件・{p13['customers']}人。",
    "classification": "イベント = エアレジ会計明細 の明細行『カテゴリ』が『イベント』に完全一致する取引（CLP主催セミナー／イベント等を含む）",
    "donut": {"target": "イベント", "value": p13["sales"], "rest": m04["sales_total"] - p13["sales"],
              "target_color": "#2D6B4F", "rest_color": "#E2E8F0",
              "center_sub": "売上構成比"},
    "left_label": "イベント",
    "right_label": "通常営業",
    "left": {
        "accounts": p13["accounts"],
        "customers": p13["customers"],
        "sales": p13["sales"],
        "share_sales": p13["share_sales"],
        "share_customers": p13["share_customers"],
    },
    "right": {
        "accounts": m04["accounts"] - p13["accounts"],
        "customers": m04["customers"] - p13["customers"],
        "sales": m04["sales_total"] - p13["sales"],
        "share_sales": 100 - p13["share_sales"],
        "share_customers": 100 - p13["share_customers"],
    },
    "caption": f"{_MONTH_LABEL}のイベント売上は¥{p13['sales']:,.0f}（{p13['share_sales']:.1f}%）。{p13['accounts']}件・{p13['customers']}人。",
})

# ───────────────────────────────────────────────
# Slide 10: 【P1-4】ボトル購入
# ───────────────────────────────────────────────
p14 = D["p1_4_bottle"]
slides.append({
    "type": "callout_table",
    "icon": "🍾",
    "title": "商品構造①：ボトル購入",
    "subtitle": "POSカテゴリ「ボトル購入」全件",
    "message_icon": "💡",
    "message": f"{_MONTH_LABEL}から開始したボトル販売は2件で¥{p14['sales']:,.0f}を計上し、月次売上の{p14['share_sales']:.1f}%を占める新規収益柱となった（前月¥0）。",
    "classification": "ボトル購入 = エアレジ会計明細 の明細行『カテゴリ』が『ボトル購入』（SAKAYA用／仕入れボトル／CLP利用分等の内訳は区別せず合算）／集計範囲: 月次総売上のみ含む。日次・曜日別・時間帯別・週次・客単価分子からはすべて除外。",
    "donut": {"target": "ボトル購入", "value": p14["sales"], "rest": m04["sales_total"] - p14["sales"],
              "target_color": "#C9A961", "rest_color": "#E2E8F0",
              "center_sub": "売上構成比"},
    "big": {
        "label": f"ボトル購入 {_MONTH_LABEL}計上額",
        "value": yen(p14["sales"]),
        "sub": f"会計件数 {p14['accounts']}件 / 客数 {p14['customers']}人 / 月次売上比 {p14['share_sales']:.1f}%",
    },
    "headers": ["項目", "値", "備考"],
    "rows": [
        ["売上（月次計上）", yen(p14["sales"]), "月次総売上にのみ含める"],
        ["会計件数", f"{p14['accounts']}件", "うち手動補正 2件"],
        ["客数", f"{p14['customers']}人", "—"],
        ["前月比較", yen(m03["bottle_sales"]) if m03 else "—", "—"],
        ["日次・曜日・時間帯", "除外", "単位売上の傾向を歪めないため"],
        ["手動補正", "+ 2件（5/1朝→4/30扱い）", "5/1 08:57, 08:59 入力分（事務処理上）"],
    ],
    "caption": "ボトル購入は月次総売上にのみ含め、それ以外のすべての集計（客単価／週次／日次／曜日別／時間帯別）から除外。",
})

# ───────────────────────────────────────────────
# Slide 11: 【P1-5】コース構成比
# ───────────────────────────────────────────────
p15 = D["p1_5_course"]
p16 = D["p1_6_clp_course"]
slides.append({
    "type": "callout_table",
    "icon": "🍽️",
    "title": "商品構造②：コース構成比（P1-5）",
    "subtitle": "うち『その他CLPコース』(P1-6) の内訳併記／詳細は次スライド",
    "message_icon": "✅",
    "message": f"コース全体は{p15['accounts']}件・{p15['customers']}人で売上¥{p15['sales']:,.0f}（売上構成比{p15['share_sales']:.1f}%）を確保し、月次最大の売上カテゴリとなっている。",
    "classification": "コース = POSカテゴリ『コース&セット』全件（CLPコース・その他CLPコース等の内訳含む）／エアレジ会計明細 明細行のカテゴリで判別",
    "donut": {"target": "コース全体", "value": p15["sales"], "rest": m04["sales_total"] - p15["sales"],
              "target_color": "#1B4D3E", "rest_color": "#E2E8F0",
              "center_sub": "売上構成比"},
    "big": {
        "label": f"コース全体 {_MONTH_LABEL}売上",
        "value": yen(p15["sales"]),
        "sub": f"会計件数 {p15['accounts']}件 / 入客数 {p15['customers']}人 / 売上構成比 {p15['share_sales']:.1f}% / 客数構成比 {p15['share_customers']:.1f}%",
    },
    "headers": ["区分", "会計件数", "入客数", "売上", "売上構成比"],
    "rows": [
        ["コース全体", f"{p15['accounts']}件", f"{p15['customers']}人", yen(p15["sales"]), pctv(p15["share_sales"])],
        ["うち その他CLPコース（P1-6）", f"{p16['accounts']}件", f"{p16['customers']}人", yen(p16["sales"]), pctv(p16["share_sales"])],
        ["うち その他のコース", f"{p15['accounts']-p16['accounts']}件",
         f"{p15['customers']-p16['customers']}人",
         yen(p15["sales"]-p16["sales"]),
         pctv(p15["share_sales"]-p16["share_sales"])],
    ],
    "caption": f"コース全体の構成比は {p15['share_sales']:.1f}%。うち約半分（売上ベースで{p16['sales']/p15['sales']*100:.0f}%）が「その他CLPコース」。詳細は次スライド参照。",
})

# ───────────────────────────────────────────────
# Slide 11.5: 【P1-6】その他CLPコース（独立スライド・修正2）
# ───────────────────────────────────────────────
non_clp_course_sales = m04["sales_total"] - p16["sales"]
non_clp_course_customers = m04["customers"] - p16["customers"]
slides.append({
    "type": "three_set",
    "icon": "🥂",
    "title": "商品構造③：その他CLPコース（P1-6）",
    "subtitle": "P1-5「コース&セット」の内訳",
    "message_icon": "💡",
    "message": f"その他CLPコースは{p16['accounts']}件・{p16['customers']}人で売上¥{p16['sales']:,.0f}（売上構成比{p16['share_sales']:.1f}%）と高単価利用（1人あたり¥{p16['sales']/p16['customers']:,.0f}）を実現している。",
    "classification": "その他CLPコース = エアレジ会計明細 の明細行『メニュー名』が『その他CLPコース』に完全一致する取引（P1-5『コース&セット』カテゴリの内訳のうち、CLP社員以外の法人案件等）",
    "donut": {"target": "その他CLPコース", "value": p16["sales"], "rest": m04["sales_total"] - p16["sales"],
              "target_color": "#2D6B4F", "rest_color": "#E2E8F0",
              "center_sub": "売上構成比"},
    "left_label": "その他CLPコース",
    "right_label": "その他全会計",
    "left": {
        "accounts": p16["accounts"],
        "customers": p16["customers"],
        "sales": p16["sales"],
        "share_sales": p16["share_sales"],
        "share_customers": p16["share_customers"],
    },
    "right": {
        "accounts": m04["accounts"] - p16["accounts"],
        "customers": non_clp_course_customers,
        "sales": non_clp_course_sales,
        "share_sales": 100 - p16["share_sales"],
        "share_customers": 100 - p16["share_customers"],
    },
    "caption": f"その他CLPコースは{p16['accounts']}件・{p16['customers']}人で売上¥{p16['sales']:,.0f}（{p16['share_sales']:.1f}%）。客単価 ¥{p16['sales']/p16['customers']:,.0f}/人と高単価利用。",
})

# ───────────────────────────────────────────────
# Slide 12-13: フード／ドリンク 出数ランキング（修正1: 入客数 + 修正4: 平均販売価格）
# ───────────────────────────────────────────────
food_qty = D["p1_7_food_qty"][:15]
drink_qty = D["p1_7_drink_qty"][:15]

def fmt_price_cell(r):
    """平均販売価格セル: 登録価格と乖離 ±5%以上なら★マーク"""
    star = "★" if r["price_star"] else ""
    return f'{star}{yen(r["avg_price"])}'

def rank_rows(items):
    return [[str(i+1), r["menu_name"], f"{r['qty']:.0f}", f"{r['customers']}人",
             yen(r["sales"]), fmt_price_cell(r), pctv(r["share"])]
            for i, r in enumerate(items)]

def rank_rows_sales(items):
    return [[str(i+1), r["menu_name"], yen(r["sales"]), f"{r['qty']:.0f}", f"{r['customers']}人",
             fmt_price_cell(r), pctv(r["share"])]
            for i, r in enumerate(items)]

RANK_CAPTION_NOTE = "★ = 平均販売価格と登録価格の乖離が±5%以上（ダブル販売・特別価格等の存在を示唆）"

slides.append({
    "type": "rank_table",
    "icon": "🍽️",
    "title": "フード 出数ランキング（上位15）",
    "subtitle": "数量ベース",
    "message_icon": "✅",
    "message": "ワカモレチップス（32食・83人）・ミントのジェノベーゼ・ボロネーゼラザニアがフード出数TOP3を構成し、シェア型アペタイザーが定番化している。",
    "classification": [
        "対象: 共通ルール『カテゴリ分類マスタ』で food タグのカテゴリ群（COLD/HOT APPETIZERS, MAIN DISHES, DESSERT, BAR SNACKS, スナック等）",
        "入客数: そのメニューを含む会計の『人数』合算（同一会計の複数明細でも人数は1回のみ）",
        "★ = 平均販売価格と登録価格の乖離±5%以上",
    ],
    "headers": ["順位", "メニュー名", "出数", "入客数", "売上", "平均販売価格", "構成比（数量）"],
    "rows": rank_rows(food_qty),
    "caption": f"ワカモレチップス（32食/83人）・ミントのジェノベーゼ・ボロネーゼラザニアがフードの出数TOP3。{RANK_CAPTION_NOTE}",
})

slides.append({
    "type": "rank_table",
    "icon": "🍹",
    "title": "ドリンク 出数ランキング（上位15）",
    "subtitle": "数量ベース",
    "message_icon": "✅",
    "message": "ハウスハイボール（168杯・111人）が圧倒的1位を獲得し、森のジントニック（87杯・116人）が定番カクテルの主力として続いた。",
    "classification": [
        "対象: 共通ルール『カテゴリ分類マスタ』で drink タグのカテゴリ群（NEW CLASSIC COCKTAIL, JAPANESE COCKTAIL, ウイスキー, ジン, ワイン, ビール, ソフトドリンク等）",
        "入客数: そのメニューを含む会計の『人数』合算",
        "★ = 平均販売価格と登録価格の乖離±5%以上",
    ],
    "headers": ["順位", "メニュー名", "出数", "入客数", "売上", "平均販売価格", "構成比（数量）"],
    "rows": rank_rows(drink_qty),
    "caption": f"ハウスハイボール（168杯/111人）が圧倒的1位。森のジントニックがNEW CLASSIC COCKTAILのトップ（87杯/116人）。{RANK_CAPTION_NOTE}",
})

# ───────────────────────────────────────────────
# Slide 14-15: フード／ドリンク 売上ランキング
# ───────────────────────────────────────────────
food_sales = D["p1_8_food_sales"][:15]
drink_sales = D["p1_8_drink_sales"][:15]
slides.append({
    "type": "rank_table",
    "icon": "🍽️",
    "title": "フード 売上ランキング（上位15）",
    "subtitle": "売上ベース",
    "message_icon": "💡",
    "message": "フード売上TOP3はワカモレチップス／ミントのジェノベーゼ／ボロネーゼラザニアで出数TOP3と一致しており、シェア型アペタイザーが収益も同時にけん引している。",
    "classification": [
        "対象: 共通ルール『カテゴリ分類マスタ』で food タグのカテゴリ群",
        "売上 = subtotal（価格×数量）合算 ／ 平均販売価格 = 売上÷出数",
        "★ = 平均販売価格と登録価格の乖離±5%以上",
    ],
    "headers": ["順位", "メニュー名", "売上", "出数", "入客数", "平均販売価格", "構成比（売上）"],
    "rows": rank_rows_sales(food_sales),
    "caption": f"フード売上TOP3 は ワカモレチップス／ミントのジェノベーゼ／ボロネーゼラザニア（出数TOP3と一致）。{RANK_CAPTION_NOTE}",
})

slides.append({
    "type": "rank_table",
    "icon": "🍹",
    "title": "ドリンク 売上ランキング（上位15）",
    "subtitle": "売上ベース",
    "message_icon": "✅",
    "message": "ドリンク売上1位はハウスハイボール（¥201,600・16.7%）で、森のジントニック（¥129,000）が2位を確保した。低単価×高回転の構造が収益基盤となっている。",
    "classification": [
        "対象: 共通ルール『カテゴリ分類マスタ』で drink タグのカテゴリ群",
        "売上 = subtotal（価格×数量）合算 ／ 平均販売価格 = 売上÷出数",
        "★ = 平均販売価格と登録価格が±5%以上乖離（ダブル販売・特別価格等の存在を示唆）",
    ],
    "headers": ["順位", "メニュー名", "売上", "出数", "入客数", "平均販売価格", "構成比（売上）"],
    "rows": rank_rows_sales(drink_sales),
    "caption": f"ドリンク売上1位はハウスハイボール（¥201,600 / 16.7%）。森のジントニックが2位。{RANK_CAPTION_NOTE}",
})

# ───────────────────────────────────────────────
# Slide 16: 週別概況（ボトル除く）
# ───────────────────────────────────────────────
weekly = D["weekly"]
max_w = max(weekly, key=lambda x: x["daily_avg"])
min_w = min(weekly, key=lambda x: x["daily_avg"])
slides.append({
    "type": "bar_chart",
    "icon": "📅",
    "title": "週別概況 — 1日あたり売上（日平均・ボトル除く）",
    "message_icon": "💡",
    "message": f"{_MONTH_LABEL}の週別日平均売上は W16（4/13週）が{yen(max_w['daily_avg'])}/日と最高を記録し、W15（4/6週）が{yen(min_w['daily_avg'])}/日と最低となり、月内で約2倍の振れ幅が発生した。",
    "classification": [
        "営業日基準（朝6時境界 ／ 0:00〜5:59 は前日扱い）",
        "日平均売上 = 週の売上 ÷ 営業日数（営業日数差を吸収）",
        "ボトル除外: POSカテゴリ『ボトル購入』（週次の傾向を歪めないため）",
    ],
    "x_label": "ISO週",
    "y_label": "日平均売上（円）",
    "bars": [{"name": w["year_week"], "value": w["daily_avg"],
              "color": ("#2D6B4F" if w["year_week"]==max_w["year_week"] else
                        "#8B3A3A" if w["year_week"]==min_w["year_week"] else "#1B4D3E"),
              "highlight": (w["year_week"] in (max_w["year_week"], min_w["year_week"])),
              "sub": f"営{w['business_days']}日"}
             for w in weekly],
    "legend": [
        {"name": "好調週", "color": "#2D6B4F"},
        {"name": "通常週", "color": "#1B4D3E"},
        {"name": "不調週", "color": "#8B3A3A"},
    ],
    "table_headers": ["週", "営業日数", "客数", "売上(ボトル除く)", "日平均売上", "客単価"],
    "table_rows": [[w["year_week"], f"{w['business_days']}日", f"{w['customers']}人",
                    yen(w["sales_excl_bottle"]), yen(w["daily_avg"]), yen(w["kyakutanka"])]
                   for w in weekly],
    "caption": f"好調週は {max_w['year_week']}（日平均{yen(max_w['daily_avg'])}）／不調週は {min_w['year_week']}（{yen(min_w['daily_avg'])}）。",
})

# ───────────────────────────────────────────────
# Slide 17: 曜日別日平均（ボトル除く）
# ───────────────────────────────────────────────
wd = D["weekday"]
max_wd = max(wd, key=lambda x: x["daily_avg_sales"])
min_wd = min(wd, key=lambda x: x["daily_avg_sales"])
slides.append({
    "type": "bar_chart",
    "icon": "📅",
    "title": "曜日別 日平均売上（ボトル除く）",
    "message_icon": "💡",
    "message": f"金曜日が日平均{yen(max_wd['daily_avg_sales'])}と最強の曜日となった一方、月曜日が{yen(min_wd['daily_avg_sales'])}と最弱で、平日強化が継続課題となっている。",
    "classification": [
        "営業日基準（朝6時境界 ／ 0:00〜5:59 は前日扱い）",
        f"曜日 = 営業日付の曜日（{_MONTH_LABEL}: 月{wd[0]['business_days']}日／火{wd[1]['business_days']}日／水{wd[2]['business_days']}日／木{wd[3]['business_days']}日／金{wd[4]['business_days']}日／土{wd[5]['business_days']}日／日{wd[6]['business_days']}日）",
        "ボトル除外: POSカテゴリ『ボトル購入』（曜日傾向を歪めないため）",
    ],
    "x_label": "曜日",
    "y_label": "日平均売上（円）",
    "bars": [{"name": w["weekday"], "value": w["daily_avg_sales"],
              "color": ("#2D6B4F" if w["weekday"]==max_wd["weekday"] else
                        "#8B3A3A" if w["weekday"]==min_wd["weekday"] else "#1B4D3E"),
              "highlight": (w["weekday"] in (max_wd["weekday"], min_wd["weekday"])),
              "sub": f"営{w['business_days']}日"}
             for w in wd],
    "legend": [
        {"name": "好調曜日", "color": "#2D6B4F"},
        {"name": "通常", "color": "#1B4D3E"},
        {"name": "不調曜日", "color": "#8B3A3A"},
    ],
    "table_headers": ["曜日", "営業日数", "日平均客数", "客単価", "日平均売上"],
    "table_rows": [[w["weekday"], f"{w['business_days']}日", f"{w['daily_avg_customers']:.1f}人",
                    yen(w["kyakutanka"]), yen(w["daily_avg_sales"])]
                   for w in wd],
    "caption": f"金曜日（{yen(max_wd['daily_avg_sales'])}）が最強、月曜日（{yen(min_wd['daily_avg_sales'])}）が最弱。",
})

# ───────────────────────────────────────────────
# Slide 18: 時間帯別月間売上（ボトル除く）
# ───────────────────────────────────────────────
hr = [h for h in D["hour"] if h["hour_bucket"] != "other"]
hr_sorted = sorted(hr, key=lambda x: ["18-20","20-22","22-24","24-26"].index(x["hour_bucket"]))
slides.append({
    "type": "bar_chart",
    "icon": "🕐",
    "title": "時間帯別 月間売上（入店時刻ベース・ボトル除く）",
    "message_icon": "💡",
    "message": "20-22時帯が売上のピーク（43.3%）を形成し、深夜帯（24-26時）は1.3%まで縮小しているため、深夜需要の取り込みが収益拡大の余地となる。",
    "classification": [
        "入店時刻ベース（会計時間 − 滞在時間）",
        "バケット: 18-20 / 20-22 / 22-24 / 24-26時（営業日基準・朝6時境界）",
        "ボトル除外: POSカテゴリ『ボトル購入』（時間帯傾向を歪めないため）",
    ],
    "x_label": "時間帯",
    "y_label": "月間売上（円）",
    "bars": [{"name": h["hour_bucket"]+"時", "value": h["sales_excl_bottle"],
              "color": "#1B4D3E", "highlight": False,
              "sub": f"客{h['customers']}人 ({h['share']:.1f}%)"}
             for h in hr_sorted],
    "legend": [{"name": "月間売上", "color": "#1B4D3E"}],
    "table_headers": ["時間帯", "売上(ボトル除く)", "客数", "構成比"],
    "table_rows": [[h["hour_bucket"]+"時", yen(h["sales_excl_bottle"]), f"{h['customers']}人", pctv(h["share"])]
                   for h in hr_sorted],
    "caption": "20-22時帯が売上のピーク（43.3%）。24時以降は1.3%と少ない。",
})

# ───────────────────────────────────────────────
# Slide 19: カテゴリ別売上構成比
# ───────────────────────────────────────────────
cat = D["category"][:10]
slides.append({
    "type": "rank_table",
    "icon": "🗂️",
    "title": "カテゴリ別 月間売上 上位10",
    "subtitle": "全カテゴリ（ボトル購入含む）",
    "message_icon": "💡",
    "message": "コース&セットが構成比20.9%で最大カテゴリとなり、NEW CLASSIC COCKTAIL（9.4%）・ボトル購入（8.0%）が続いた。コース・カクテル・新規ボトルの3軸が収益構造を形成している。",
    "classification": [
        f"集計対象: {_y}/{_m}/1 0:00 〜 {_m}/{_last_day} 23:59 の売上日時",
        "POSカテゴリ別の月間売上（subtotal = 価格×数量 合算）",
        "ボトル購入含む全カテゴリ",
    ],
    "headers": ["順位", "カテゴリ", "月間売上", "数量", "構成比"],
    "rows": [[str(i+1), c["category1"], yen(c["sales"]), f"{c['qty']:.0f}", pctv(c["share"])]
             for i, c in enumerate(cat)],
    "caption": "コース&セットが20.9%で最大。ボトル購入8.0%、その他9.0%（チャージ等）。",
})

# ═══════════════════════════════════════════════
# PL分析セクション
# 出典: ダッシュボードDB（当月） ／ 【BFA】本部サポート / PLシート（過去月）
# 共通ルール §18: データが無い場合は「データなし」明示スライドに置換
# ═══════════════════════════════════════════════
PL = D["pl"]
_PL_OK = bool(PL.get("available")) and bool(PL.get("expense_breakdown"))

if _PL_OK:
    # ─── PL-1: PLサマリー ───
    slides.append({
        "type": "callout_table",
        "icon": "💰",
        "title": f"PLサマリー（{_MONTH_LABEL}実績）",
        "subtitle": "売上はエアレジ会計明細／費用はダッシュボードDB",
        "message_icon": "⚠️",
        "message": f"{_MONTH_LABEL}は売上¥{m04['sales_total']:,.0f}に対して費用¥{PL['expense_total']:,.0f}、営業利益¥{PL['op_profit']:,.0f}（{PL['op_profit_rate']:+.1f}%）。",
        "classification": [
            "売上の出典: エアレジ会計明細（提供CSV）の月次総売上（ボトル含む）",
            "費用の出典: ダッシュボードDB / PLシート（9費目）",
            f"対象期間: {_TARGET} 月次集計",
        ],
        "big": {
            "label": "営業利益（売上 − 費用）",
            "value": yen(PL["op_profit"]),
            "sub": f"売上 {yen(m04['sales_total'])} − 費用 {yen(PL['expense_total'])} ／ 利益率 {PL['op_profit_rate']:+.1f}%",
        },
        "headers": ["費目", "実績", "売上比"],
        "rows": [[e["category"], yen(e["amount"]), f"{e['share']:.1f}%"]
                 for e in PL["expense_breakdown"]],
        "caption": f"最大費目は{PL['expense_breakdown'][0]['category']}（{PL['expense_breakdown'][0]['share']:.1f}%）。",
    })
    # ─── PL-2: 費用推移 ───
    main_cats = ["家賃","ドリンク","食材","人件費"]
    def get_series(cat):
        return [(t["month"], t["exp_breakdown"].get(cat, 0)) for t in PL["trend"]]
    pl2_series = [
        {"name": "家賃", "color": "#1B4D3E", "data": get_series("家賃")},
        {"name": "ドリンク", "color": "#C9A961", "data": get_series("ドリンク"), "dash": True},
        {"name": "食材", "color": "#2D6B4F", "data": get_series("食材")},
        {"name": "人件費", "color": "#8B3A3A", "data": get_series("人件費"), "dash": True},
    ]
    slides.append({
        "type": "line_chart",
        "icon": "📈",
        "title": "費用推移（主要費目）",
        "x_label": "月",
        "y_label": "費用（円）",
        "message_icon": "⚠️",
        "message": "家賃が固定費として最大の重し。",
        "classification": [
            "出典: 当月はダッシュボードDB／過去月は【BFA】本部サポート / PLシート",
            "主要4費目のみ表示。残り5費目はPL-1スライド参照",
        ],
        "series": pl2_series,
        "highlight_last": True,
        "caption": "家賃・ドリンク原価が構造的に高い固定費。",
    })
    # ─── PL-3: インサイト ───
    slides.append({
        "type": "summary",
        "icon": "💡",
        "title": "PLからのインサイト",
        "message_icon": "💡",
        "message": f"{_MONTH_LABEL}の営業利益¥{PL['op_profit']:,.0f}（{PL['op_profit_rate']:+.1f}%）。",
        "classification": [
            "FL率の分母 = 月次総売上（ボトル含む）",
            "目安は飲食業の一般的な水準（FL率60%／人件費率30%）",
        ],
        "items": [
            f"営業利益 ¥{PL['op_profit']:,.0f}（{PL['op_profit_rate']:+.1f}%）",
            f"FL率 {PL['fl_rate']:.1f}%（目安60%）",
            f"人件費率 {PL['labor_rate']:.1f}%（目安30%）",
        ],
        "caption": "PLは継続モニタリングが必要。",
    })
else:
    # ─── PL データなしフォールバック（共通ルール §18） ───
    _PL_MSG = "【BFA】本部サポート / PLシート に該当月のデータがないため出力していません"
    for _t, _icon in [
        (f"PLサマリー（{_MONTH_LABEL}実績）", "💰"),
        ("費用推移（主要費目）", "📈"),
        ("PLからのインサイト", "💡"),
    ]:
        slides.append({
            "type": "summary",
            "icon": _icon,
            "title": _t,
            "message_icon": "ℹ️",
            "message": _PL_MSG,
            "classification": [
                "対象月: " + _TARGET,
                "PLソース: 【BFA】本部サポート / PLシート",
                "状態: 当該月の行が未入力",
            ],
            "items": [
                "PL系KPI（総費用／営業利益／FL率／人件費率）は本スライドでは表示しません",
                "PLシートに当該月の入力が反映され次第、本スライドを再生成してください",
            ],
            "caption": _PL_MSG,
        })

# ───────────────────────────────────────────────
# 日報スライド（v1.2 イテレーション9: PL分析の直後・強み/課題/施策の直前に配置）
# ───────────────────────────────────────────────
dr = D["daily_reports"]
if dr:
    slides.append({
        "type": "daily_reports",
        "icon": "📝",
        "title": f"店舗の様子 — 日報より（{_MONTH_LABEL}）",
        "subtitle": f"対象月の日報入力件数: {len(dr)}件",
        "message_icon": "💡",
        "message": f"対象月の日報入力件数: {len(dr)}件。",
        "classification": [
            f"対象期間: {_y}-{_m:02d}-01〜{_y}-{_m:02d}-{_last_day:02d} の日報入力分",
            "引用項目: ①来客特徴、②改善ポイント",
        ],
        "reports": [{"date": r["営業日"], "name": r["入力者氏名"],
                     "guests": (r["①来客特徴"] or "")[:300],
                     "improve": (r["②改善ポイント"] or "")[:300]}
                    for r in dr],
        "caption": f"日報入力 {len(dr)}件のサマリ。",
    })

# ───────────────────────────────────────────────
# Slide: 強み
# ───────────────────────────────────────────────
slides.append({
    "type": "summary",
    "icon": "✅",
    "title": "今月の強み",
    "message_icon": "✅",
    "message": f"{_MONTH_LABEL}実績の強みサマリ。",
    "classification": [
        "抽出基準: 前年比 or 前月比でプラス、構成比10%超、または新規収益柱となった指標",
    ],
    "items": [
        f"インバウンド客が{p11['customers']}人・売上¥{p11['sales']:,.0f}（売上構成比 {p11['share_sales']:.1f}%）。Google検索経由の認知が成果に",
        f"コース利用が好調（{p15['accounts']}件・{p15['customers']}人・¥{p15['sales']:,.0f}／{p15['share_sales']:.1f}%）。CLP関連のコース予約が安定収益源",
        f"金曜日（日平均{yen(max_wd['daily_avg_sales'])}）と土曜日（日平均¥{wd[5]['daily_avg_sales']:,.0f}）が引き続き強い",
        f"ハウスハイボール（168杯／¥201,600）が安定したドリンク主力商品",
        f"{_MONTH_LABEL}からボトル販売を計上開始（¥{p14['sales']:,.0f}）。月次売上の押し上げ要因に",
    ],
    "caption": "新規切り口で見ると、インバウンド・CLP・コースが収益の柱として可視化された。",
})

# ───────────────────────────────────────────────
# Slide 22: 課題
# ───────────────────────────────────────────────
slides.append({
    "type": "summary",
    "icon": "⚠️",
    "title": "今月の課題",
    "message_icon": "⚠️",
    "message": f"前年同月（{_PREV_Y}）比較、曜日・時間帯の偏り、客単価変動など、当月{_MONTH_LABEL}の課題ポイントを抽出。",
    "classification": [
        "抽出基準: 前年比 or 前月比でマイナス、曜日・時間帯で著しく低い水準、客単価低下セグメント",
    ] + (["PL赤字要因も含む"] if _PL_OK else ["PL系課題は本月PLデータ未入力のため非表示"]),
    "items": [
        f"売上は前年同月比 {diff_pct(m04['sales_total'], m04_py['sales_total']) if m04_py else '—'}（{yen(m04['sales_total'])} vs {yen(m04_py['sales_total']) if m04_py else '—'}）",
        f"客数は前年同月比 {diff_pct(m04['customers'], m04_py['customers']) if m04_py else '—'}（{m04['customers']}人 vs {m04_py['customers'] if m04_py else '—'}人）",
        f"客単価（ボトル除く）は前月¥{m03['kyakutanka']:,.0f} → 当月¥{m04['kyakutanka']:,.0f}（{diff_pct(m04['kyakutanka'], m03['kyakutanka']) if m03 else '—'}）",
        f"曜日別最弱は{min_wd['weekday']}曜（日平均¥{min_wd['daily_avg_sales']:,.0f}）",
        f"時間帯別の偏り: 主力は20-22時帯、深夜帯（24-26時）の取り込み余地",
    ] + ([
        f"【PL】営業利益 ¥{PL['op_profit']:,.0f}（{PL['op_profit_rate']:+.1f}%）",
        f"【PL】FL率 {PL['fl_rate']:.1f}% ／ 人件費率 {PL['labor_rate']:.1f}%",
    ] if _PL_OK else [
        "【PL】当月のPLデータは【BFA】本部サポート / PLシートに未入力のため本スライドでは省略",
    ]),
    "caption": f"当月{_MONTH_LABEL}の課題サマリ。" + ("PL観点も追加。" if _PL_OK else "PL系はデータ反映後に再生成推奨。"),
})

# ───────────────────────────────────────────────
# Slide 23: 施策一覧
# ───────────────────────────────────────────────
slides.append({
    "type": "action_table",
    "icon": "🎯",
    "title": "次月以降の施策案",
    "message_icon": "💡",
    "message": "高優先は売上回復＋PL赤字脱却の直接対策、中優先は新規収益柱（ボトル・深夜需要）の拡大策、PL観点（固定費見直し・人件費適正化）を新規施策として追加した。",
    "classification": [
        "優先順位: 高=売上構造／PL赤字の即時改善、中=新規収益柱の拡大、低=運用体制の継続改善",
    ],
    "headers": ["優先", "テーマ", "施策案", "狙い・指標"],
    "rows": [
        ["高", "インバウンド", "Googleマップ口コミ強化（英語応答テンプレ／写真追加）", f"海外比率（インバウンド構成比）の引き上げ"],
        ["高", "客単価回復", "コース後アラカルト追加の常時提案 ／ ペアリングメニュー導入", f"客単価 ¥{m04['kyakutanka']:,.0f} → +¥500を目標"],
        ["高", "平日強化", f"{min_wd['weekday']}曜の集客テコ入れ（早割・限定セット 等）", f"{min_wd['weekday']}曜日平均 ¥{min_wd['daily_avg_sales']:,.0f} 改善"],
        ["中", "ボトル販売", "CLP社員向けボトルキープ施策の継続・定型化", "月次ボトル売上の安定計上"],
        ["中", "深夜需要", "金土の24-26時限定「ナイトキャップセット」", "24-26時の構成比引き上げ"],
        ["低", "日報強化", f"{_MONTH_LABEL}の日報入力{len(dr)}件。週次入力リズム化", "月10〜15件入力"],
    ] + ([
        ["高", "PL赤字脱却", f"売上回復＋固定費見直しの両輪", f"営業利益 {PL['op_profit_rate']:+.1f}% → 黒字化"],
        ["中", "固定費見直し", "家賃交渉 ／ ローン借換検討", "固定費比率の圧縮"],
        ["中", "人件費適正化", "オーナー稼働の可視化 ／ スポット人員投入の費用対効果検証", f"人件費率 {PL['labor_rate']:.1f}% → 適正化"],
    ] if _PL_OK else []),
    "caption": f"次月以降の施策案サマリ。" + ("PL観点も追加。" if _PL_OK else ""),
})

# v1.2 イテレーション9: 確認事項スライド（旧 Slide 24）は削除
# データソース注記は各スライドの分類条件帯に分散

# ============================================
# CSS / JS (D3.js) + HTML レンダリング
# ============================================
HTML_HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>__STORE__ 月次営業報告 — __TM__ (v2draft)</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  /* v1.2 イテレーション3: 縦キャンバスを 720→840px に拡張（はみ出し解消） */
  @page { size: 1280px 840px; margin: 0; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    body { margin: 0; padding: 0; background: #fff; width: 1280px; }
    .slide { page-break-after: always; page-break-inside: avoid; break-after: page; break-inside: avoid;
             box-shadow: none; margin: 0; width: 1280px; height: 840px; }
    .slide:last-child { page-break-after: auto; }
  }
  @media screen {
    body { background: #E2E8F0; font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; }
    .slide { margin: 20px auto; box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
  }
  /* ★ v1.2 イテレーション4: ダークグリーン基調のカラーパレット
     - メイン #1B4D3E (深緑) / アクセント #C9A961 (落ち着いたゴールド)
     - 強調プラス #2D6B4F / 強調マイナス #8B3A3A (暗赤茶) / 中立 #6B7280 */
  .slide { width: 1280px; height: 840px; position: relative; overflow: hidden; background: #FBFAF5;
           font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; color: #1F2A28; }
  .slide-header { background: #1B4D3E; color: #F5F2E8; padding: 14px 32px; display: flex;
                  flex-direction: column; gap: 3px; border-bottom: 3px solid #C9A961; }
  .slide-header .h-title { font-size: 26px; font-weight: 800; }
  .slide-header .h-sub { font-size: 13px; font-weight: 400; opacity: 0.85; }
  /* メッセージ帯 — 動詞のある結論一文（ダークグリーン濃淡） */
  .slide-message { background: #EFEFE6; border-left: 6px solid #1B4D3E;
                   padding: 12px 20px; margin: 0;
                   font-size: 17px; font-weight: 700; color: #1B4D3E; line-height: 1.45; }
  /* 分類条件帯 — このページの集計条件を箇条書きで明示（v1.2 イテレーション5 厳格化） */
  .slide-classification { background: #F0EEE2; border-left: 4px solid #6B8E7F;
                          padding: 8px 18px; margin: 0;
                          font-size: 12px; color: #2D5F4E; line-height: 1.55; }
  .slide-classification .label { font-weight: 800; color: #1B4D3E; display: block; margin-bottom: 2px; }
  .slide-classification ul { margin: 0; padding-left: 18px; }
  .slide-classification li { margin: 1px 0; }
  .slide-body { padding: 16px 28px; height: calc(840px - 110px - 50px - 40px - 50px); overflow: hidden; }
  .footer-note { position: absolute; bottom: 8px; left: 24px; right: 24px;
                 font-size: 11px; color: #6B7280; line-height: 1.4; }
  .caption { font-size: 12px; color: #2D5F4E; font-weight: 600; margin-top: 8px;
             padding: 6px 10px; background: #F0EEE2; border-left: 3px solid #1B4D3E;
             position: absolute; left: 28px; right: 28px; bottom: 34px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { background: #1B4D3E; color: #F5F2E8; padding: 6px 9px; text-align: left; font-weight: 700; font-size: 12px; }
  td { padding: 5px 9px; border-bottom: 1px solid #D6D0BD; font-size: 12px; line-height: 1.3; color: #1F2A28; }
  tr:nth-child(even) td { background: #F0EEE2; }
  td.num { text-align: right; }
  /* Title slide — dark green gradient */
  .slide-title { background: linear-gradient(135deg, #1B4D3E 0%, #0F2D24 100%); color: #F5F2E8;
                 display: flex; flex-direction: column; justify-content: center; align-items: center; }
  .slide-title h1 { font-size: 60px; font-weight: 800; margin: 0; color: #F5F2E8; }
  .slide-title h2 { font-size: 32px; font-weight: 400; margin: 16px 0 0 0; opacity: 0.9; color: #C9A961; }
  .slide-title .period { font-size: 22px; margin-top: 36px; opacity: 0.85; }
  .slide-title .note { font-size: 14px; margin-top: 18px; opacity: 0.6; }
  /* KPI cards — dark green base */
  .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 10px; }
  .kpi-card { background: #FBFAF5; border-top: 4px solid #1B4D3E; padding: 10px 12px; min-height: 100px;
              box-shadow: 0 1px 3px rgba(27,77,62,0.08); }
  .kpi-card.bottle { border-top-color: #C9A961; }
  .kpi-card.exclbottle { border-top-color: #2D6B4F; }
  .kpi-card .lab { font-size: 11px; color: #2D5F4E; font-weight: 700; }
  .kpi-card .val { font-size: 22px; font-weight: 800; color: #1B4D3E; margin-top: 4px; }
  .kpi-card .comp { font-size: 10.5px; color: #2D5F4E; margin-top: 4px; line-height: 1.5; }
  .kpi-card .note { font-size: 9.5px; color: #6B7280; margin-top: 3px; font-style: italic; }
  .pos { color: #2D6B4F; font-weight: 700; }
  .neg { color: #8B3A3A; font-weight: 700; }
  /* Three-set with donut */
  .three-set { display: grid; grid-template-columns: 220px 1fr 1fr; gap: 14px; align-items: start; }
  .three-set.no-donut { grid-template-columns: 1fr 1fr; }
  .three-set .donut-area { background: #F0EEE2; padding: 8px; border-radius: 6px; text-align: center; }
  .three-set .donut-area .ttl { font-size: 12px; font-weight: 700; color: #1B4D3E; margin-bottom: 2px; }
  .three-set .pane { background: #FBFAF5; padding: 14px; border-radius: 6px; border-top: 4px solid #1B4D3E;
                     box-shadow: 0 1px 3px rgba(27,77,62,0.08); }
  .three-set .pane.right { border-top-color: #C9A961; }
  .three-set .pane h3 { margin: 0 0 8px 0; font-size: 16px; color: #1B4D3E; }
  .three-set .pane .row { display: flex; justify-content: space-between; padding: 5px 0;
                          border-bottom: 1px dashed #D6D0BD; font-size: 13px; }
  .three-set .pane .row .v { font-weight: 800; color: #1F2A28; }
  /* Donut chart container (for KPI ratio slides) */
  .donut-row { display: flex; gap: 12px; align-items: center; justify-content: center;
               background: #F0EEE2; padding: 8px; border-radius: 6px; margin-bottom: 10px; }
  .donut-row .donut-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .donut-row .donut-item .label { font-size: 12px; font-weight: 700; color: #1B4D3E; }
  .donut-row .donut-legend { font-size: 11px; color: #2D5F4E; }
  .donut-row .donut-legend .sw { display: inline-block; width: 10px; height: 10px; margin-right: 4px; vertical-align: middle; }
  /* Callout — dark green */
  .callout-big { background: #F0EEE2; border: 2px solid #1B4D3E; padding: 18px 24px; text-align: center;
                 margin-bottom: 14px; border-radius: 6px; }
  .callout-big .lab { font-size: 14px; color: #1B4D3E; font-weight: 700; }
  .callout-big .val { font-size: 46px; color: #1B4D3E; font-weight: 800; }
  .callout-big .sub { font-size: 13px; color: #2D5F4E; margin-top: 4px; }
  /* Bar/Line layout */
  .chart-grid { display: grid; grid-template-columns: 3fr 2fr; gap: 14px; height: 100%; }
  .chart-area { background: #FBFAF5; padding: 6px; }
  .legend { display: flex; gap: 14px; margin-bottom: 6px; padding: 0 0 4px 4px; }
  .legend .item { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: #1B4D3E; }
  .legend .swatch { width: 14px; height: 14px; }
  /* Summary list */
  .summary-list { font-size: 16px; line-height: 1.7; }
  .summary-list li { margin-bottom: 10px; padding: 8px 12px; background: #F0EEE2; border-left: 3px solid #1B4D3E; color: #1F2A28; }
  /* Daily reports */
  .dr-list { display: flex; flex-direction: column; gap: 10px; }
  .dr-item { background: #F0EEE2; padding: 10px 14px; border-left: 3px solid #1B4D3E; font-size: 12px; color: #1F2A28; }
  .dr-item .head { font-weight: 800; color: #1B4D3E; margin-bottom: 4px; }
</style>
</head>
<body>
"""

HTML_FOOT = """
<script>
// Legend helper
function addLegend(svg, items, x, y) {
  const g = svg.append('g').attr('class','legend').attr('transform','translate('+x+','+y+')');
  items.forEach((it,i)=>{
    const row = g.append('g').attr('transform','translate(0,'+(i*22)+')');
    row.append('rect').attr('width',14).attr('height',14).attr('fill',it.color);
    row.append('text').attr('x',20).attr('y',12).attr('font-size','14px').attr('font-weight','700').text(it.label);
  });
}

// Donut chart helper (v1.2 イテレーション3 新設)
document.querySelectorAll('[data-donut]').forEach(el=>{
  const cfg = JSON.parse(el.getAttribute('data-donut'));
  const size = cfg.size || 200;
  const r = size/2 - 8;
  const ir = r * 0.55;
  const svg = d3.select(el).append('svg').attr('width', size).attr('height', size);
  const g = svg.append('g').attr('transform', 'translate('+size/2+','+size/2+')');
  const pie = d3.pie().value(d=>d.value).sort(null);
  const arc = d3.arc().innerRadius(ir).outerRadius(r);
  g.selectAll('path').data(pie(cfg.slices)).join('path')
    .attr('d',arc).attr('fill',d=>d.data.color).attr('stroke','#fff').attr('stroke-width',2);
  // center label: percentage of the first slice (target)
  const first = cfg.slices[0];
  const total = cfg.slices.reduce((s,d)=>s+d.value,0);
  const pctText = total ? (first.value/total*100).toFixed(1)+'%' : '—';
  g.append('text').attr('text-anchor','middle').attr('y',0)
    .attr('font-size','22px').attr('font-weight','800').attr('fill','#1B4D3E').text(pctText);
  g.append('text').attr('text-anchor','middle').attr('y',18)
    .attr('font-size','10px').attr('fill','#6B7280').text(cfg.center_sub || '');
});

// Draw bar charts
document.querySelectorAll('[data-bar]').forEach(el=>{
  const cfg = JSON.parse(el.getAttribute('data-bar'));
  const m = {top:30,right:30,bottom:60,left:80};
  const w = el.clientWidth - m.left - m.right;
  const h = 280 - m.top - m.bottom;
  const svg = d3.select(el).append('svg').attr('width', el.clientWidth).attr('height', 280);
  const g = svg.append('g').attr('transform','translate('+m.left+','+m.top+')');
  const x = d3.scaleBand().domain(cfg.bars.map(b=>b.name)).range([0,w]).padding(0.3);
  const y = d3.scaleLinear().domain([0, d3.max(cfg.bars,b=>b.value)*1.18]).range([h,0]);
  // grid
  g.append('g').selectAll('line').data(y.ticks(5)).join('line')
    .attr('x1',0).attr('x2',w).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#D6D0BD').attr('stroke-dasharray','3,3');
  // bars
  g.selectAll('rect.bar').data(cfg.bars).join('rect').attr('class','bar')
    .attr('x',d=>x(d.name)).attr('width',x.bandwidth())
    .attr('y',d=>y(d.value)).attr('height',d=>h-y(d.value))
    .attr('fill',d=>d.color);
  // value labels
  g.selectAll('text.val').data(cfg.bars).join('text').attr('class','val')
    .attr('x',d=>x(d.name)+x.bandwidth()/2).attr('y',d=>y(d.value)-6)
    .attr('text-anchor','middle')
    .attr('font-size',d=>d.highlight?'15px':'12px')
    .attr('font-weight',d=>d.highlight?'800':'600')
    .attr('fill',d=>d.highlight?'#1B4D3E':'#6B7280')
    .text(d=>'¥'+Math.round(d.value).toLocaleString());
  // sub labels
  g.selectAll('text.sub').data(cfg.bars).join('text').attr('class','sub')
    .attr('x',d=>x(d.name)+x.bandwidth()/2).attr('y',h+34)
    .attr('text-anchor','middle').attr('font-size','10px').attr('fill','#C9A961').text(d=>d.sub||'');
  // axes
  g.append('g').attr('transform','translate(0,'+h+')')
    .call(d3.axisBottom(x)).selectAll('text').attr('font-size','12px').attr('font-weight','700');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+d3.format(',.0f')(d))).selectAll('text').attr('font-size','10px');
  // legend
  if(cfg.legend && cfg.legend.length){
    addLegend(svg, cfg.legend.map(l=>({label:l.name,color:l.color})), m.left, 6);
  }
});

// Draw line charts
document.querySelectorAll('[data-line]').forEach(el=>{
  const cfg = JSON.parse(el.getAttribute('data-line'));
  const m = {top:60,right:30,bottom:50,left:80};
  const w = el.clientWidth - m.left - m.right;
  const h = 300 - m.top - m.bottom;
  const svg = d3.select(el).append('svg').attr('width', el.clientWidth).attr('height', 300);
  const g = svg.append('g').attr('transform','translate('+m.left+','+m.top+')');
  const months = cfg.series[0].data.map(d=>d[0]);
  const allVals = cfg.series.flatMap(s=>s.data.map(d=>d[1]));
  const x = d3.scalePoint().domain(months).range([0,w]).padding(0.5);
  const y = d3.scaleLinear().domain([0, d3.max(allVals)*1.15]).range([h,0]);
  // grid
  g.append('g').selectAll('line').data(y.ticks(5)).join('line')
    .attr('x1',0).attr('x2',w).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#D6D0BD').attr('stroke-dasharray','3,3');
  cfg.series.forEach((s, idx)=>{
    const line = d3.line().x(d=>x(d[0])).y(d=>y(d[1]));
    const path = g.append('path').attr('d',line(s.data)).attr('fill','none')
      .attr('stroke',s.color).attr('stroke-width',3);
    if (s.dash) path.attr('stroke-dasharray','8,4');
    g.selectAll('circle.s'+idx).data(s.data).join('circle').attr('class','s'+idx)
      .attr('cx',d=>x(d[0])).attr('cy',d=>y(d[1]))
      .attr('r',(d,i)=>(cfg.highlight_last && i===s.data.length-1) ? 8 : 4)
      .attr('fill',s.color);
  });
  g.append('g').attr('transform','translate(0,'+h+')').call(d3.axisBottom(x)).selectAll('text').attr('font-size','12px');
  const unit = cfg.unit || '円';
  const tickFmt = d=> (unit==='円' ? '¥' : '') + d3.format(',.0f')(d) + (unit!=='円' ? unit : '');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(tickFmt)).selectAll('text').attr('font-size','10px');
  // legend (top-left, with dash hint for dashed series)
  const lg = svg.append('g').attr('class','legend').attr('transform','translate('+m.left+',8)');
  cfg.series.forEach((s, i)=>{
    const row = lg.append('g').attr('transform','translate('+(i*340)+',0)');
    row.append('line').attr('x1',0).attr('x2',24).attr('y1',8).attr('y2',8)
      .attr('stroke',s.color).attr('stroke-width',3)
      .attr('stroke-dasharray', s.dash ? '6,3' : null);
    row.append('text').attr('x',30).attr('y',12).attr('font-size','12px').attr('font-weight','700').attr('fill','#1B4D3E').text(s.name);
  });
  // unit hint legend at top-right
  svg.append('text').attr('x', el.clientWidth - 12).attr('y', 14)
    .attr('text-anchor','end').attr('font-size','11px').attr('fill','#6B7280')
    .text('単位: ' + (cfg.unit || '円') + ' / 出典: エアレジ会計明細');
  // annotation
  if(cfg.annotation){
    const lastSerie = cfg.series[0];
    const last = lastSerie.data[lastSerie.data.length-1];
    const xPos = x(last[0]) + m.left - 320;
    const yPos = y(last[1]) + m.top - 6;
    const an = svg.append('g');
    const t = an.append('text').attr('x',xPos).attr('y',yPos)
      .attr('font-size','13px').attr('font-weight','800').attr('fill','#1B4D3E').text(cfg.annotation);
    const bb = t.node().getBBox();
    an.insert('rect','text').attr('x',bb.x-8).attr('y',bb.y-4).attr('width',bb.width+16).attr('height',bb.height+8)
      .attr('rx',4).attr('fill','#F0EEE2').attr('stroke','#C9A961').attr('stroke-width',1.5);
  }
});
</script>
</body>
</html>"""

# ============================================
# レンダリング関数
# ============================================
import html as html_lib

def esc(s):
    return html_lib.escape(str(s)) if s is not None else ""

def fmt_comp(c):
    txt = esc(c)
    if isinstance(c, str):
        if c.startswith("+"):
            return f'<span class="pos">▲ {esc(c)}</span>'
        if c.startswith("-"):
            return f'<span class="neg">▼ {esc(c)}</span>'
    return txt

def render_slide(idx, s):
    n = idx + 1
    if s["type"] == "title":
        return f"""
<div class="slide slide-title" id="slide-{n}">
  <h1>{esc(s['title'])}</h1>
  <h2>{esc(s['subtitle'])}</h2>
  <p class="period">{esc(s['period'])}</p>
  <p class="note">{esc(s.get('note',''))}</p>
</div>
"""
    # v1.2 イテレーション3: タイトルに絵文字を先頭付与（slide定義の "icon" を使う）
    icon = s.get("icon", "")
    title_with_icon = (icon + " " + s["title"]) if icon else s["title"]
    header = f'<div class="slide-header"><div class="h-title">{esc(title_with_icon)}</div>'
    if s.get("subtitle"):
        header += f'<div class="h-sub">{esc(s["subtitle"])}</div>'
    header += '</div>'
    # メッセージ帯（必須）— 動詞のある結論一文
    msg_text = s.get("message", "")
    msg_icon = s.get("message_icon", "")
    msg_full = (msg_icon + " " + msg_text) if msg_icon else msg_text
    message_bar = (f'<div class="slide-message">{esc(msg_full)}</div>'
                   if msg_text else '')
    # 分類条件帯（オプション）— list[str] でも str でも受け付ける（v1.2 イテレーション5）
    classif = s.get("classification", "")
    if isinstance(classif, list) and classif:
        items_html = "".join(f"<li>{esc(it)}</li>" for it in classif)
        classif_bar = (f'<div class="slide-classification">'
                       f'<span class="label">分類条件 / 集計範囲</span>'
                       f'<ul>{items_html}</ul></div>')
    elif isinstance(classif, str) and classif:
        classif_bar = (f'<div class="slide-classification">'
                       f'<span class="label">分類条件 / 集計範囲</span>'
                       f'<ul><li>{esc(classif)}</li></ul></div>')
    else:
        classif_bar = ''
    footer = f'<div class="footer-note">{esc(FOOTER_NOTE)}</div>'
    caption = f'<div class="caption">{esc(s.get("caption",""))}</div>' if s.get("caption") else ""
    body = ""

    if s["type"] == "kpi":
        cards = []
        for k in s["kpis"]:
            cls = "kpi-card"
            if "ボトル" in k["label"] and "除く" not in k["label"]:
                cls += " bottle"
            elif "除く" in k["label"]:
                cls += " exclbottle"
            comp = "<br>".join(f'<span>{esc(lab)}: {fmt_comp(val)}</span>' for lab, val in k["comp"])
            note = f'<div class="note">{esc(k.get("note",""))}</div>' if k.get("note") else ""
            cards.append(f'<div class="{cls}"><div class="lab">{esc(k["label"])}</div>'
                         f'<div class="val">{k["value"]}</div>'
                         f'<div class="comp">{comp}</div>{note}</div>')
        body = f'<div class="kpi-grid">{"".join(cards)}</div>'

    elif s["type"] == "line_chart":
        import json as _json
        # ensure each series has 'dash' field (default False)
        series = [{**ser, "dash": ser.get("dash", False)} for ser in s["series"]]
        cfg = _json.dumps({
            "series": series,
            "highlight_last": s.get("highlight_last", False),
            "annotation": s.get("annotation",""),
            "unit": s.get("unit", "円"),
        }, ensure_ascii=False)
        body = f'<div data-line=\'{esc(cfg)}\' style="height:320px"></div>'

    elif s["type"] == "comparison_table":
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td class="num">{esc(c) if i>0 else esc(c)}</td>'
                                       if i>0 else f'<td>{esc(c)}</td>'
                                       for i, c in enumerate(r)) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'

    elif s["type"] == "three_set":
        def pane_html(p, label, cls):
            return (f'<div class="pane {cls}"><h3>{esc(label)}</h3>'
                    f'<div class="row"><span>会計件数</span><span class="v">{p["accounts"]}件</span></div>'
                    f'<div class="row"><span>入客数</span><span class="v">{p["customers"]}人 ({p["share_customers"]:.1f}%)</span></div>'
                    f'<div class="row"><span>売上</span><span class="v">{yen(p["sales"])} ({p["share_sales"]:.1f}%)</span></div>'
                    f'</div>')
        # v1.2 イテレーション3: 円グラフ統合
        donut_html = ""
        cls_grid = "no-donut"
        if s.get("donut"):
            import json as _j
            dn = s["donut"]
            cfg = _j.dumps({
                "size": 200,
                "center_sub": dn.get("center_sub","売上構成比"),
                "slices": [
                    {"label": dn["target"], "value": dn["value"], "color": dn["target_color"]},
                    {"label": "その他", "value": dn["rest"], "color": dn["rest_color"]},
                ]
            }, ensure_ascii=False)
            donut_html = (f'<div class="donut-area">'
                          f'<div class="ttl">{esc(dn["target"])} vs その他</div>'
                          f'<div data-donut=\'{esc(cfg)}\'></div>'
                          f'<div class="donut-legend" style="margin-top:6px">'
                          f'<span><span class="sw" style="background:{dn["target_color"]}"></span>{esc(dn["target"])}</span> '
                          f'<span style="margin-left:10px"><span class="sw" style="background:{dn["rest_color"]}"></span>その他</span>'
                          f'</div></div>')
            cls_grid = ""
        body = (f'<div class="three-set {cls_grid}">'
                + donut_html
                + pane_html(s["left"], s["left_label"], "left")
                + pane_html(s["right"], s["right_label"], "right")
                + '</div>')

    elif s["type"] == "callout_table":
        big = s["big"]
        cb = (f'<div class="callout-big">'
              f'<div class="lab">{esc(big["label"])}</div>'
              f'<div class="val">{esc(big["value"])}</div>'
              f'<div class="sub">{esc(big["sub"])}</div></div>')
        # v1.2 イテレーション3: 円グラフ統合（オプション）
        donut_html = ""
        if s.get("donut"):
            import json as _j
            dn = s["donut"]
            cfg = _j.dumps({
                "size": 180,
                "center_sub": dn.get("center_sub","売上構成比"),
                "slices": [
                    {"label": dn["target"], "value": dn["value"], "color": dn["target_color"]},
                    {"label": "その他", "value": dn["rest"], "color": dn["rest_color"]},
                ]
            }, ensure_ascii=False)
            donut_html = (f'<div class="donut-row">'
                          f'<div class="donut-item"><div class="label">{esc(dn["target"])} vs その他</div>'
                          f'<div data-donut=\'{esc(cfg)}\'></div></div>'
                          f'<div class="donut-legend">'
                          f'<div><span class="sw" style="background:{dn["target_color"]}"></span>{esc(dn["target"])}: {yen(dn["value"])} ({dn["value"]/(dn["value"]+dn["rest"])*100:.1f}%)</div>'
                          f'<div><span class="sw" style="background:{dn["rest_color"]}"></span>その他: {yen(dn["rest"])} ({dn["rest"]/(dn["value"]+dn["rest"])*100:.1f}%)</div>'
                          f'</div></div>')
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td>{esc(c)}</td>' for c in r) + "</tr>" for r in s["rows"])
        body = cb + donut_html + f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'

    elif s["type"] == "rank_table":
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td class="num">{esc(c)}</td>' if i>=2 else f'<td>{esc(c)}</td>'
                                       for i, c in enumerate(r)) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'

    elif s["type"] == "bar_chart":
        import json as _json
        cfg = _json.dumps({"bars": s["bars"], "legend": s.get("legend", [])}, ensure_ascii=False)
        tt_ths = "".join(f'<th>{esc(h)}</th>' for h in s["table_headers"])
        tt_trs = "".join("<tr>" + "".join(f'<td>{esc(c)}</td>' for c in r) + "</tr>" for r in s["table_rows"])
        body = (f'<div class="chart-grid">'
                f'  <div class="chart-area"><div data-bar=\'{esc(cfg)}\'></div></div>'
                f'  <div><table><thead><tr>{tt_ths}</tr></thead><tbody>{tt_trs}</tbody></table></div>'
                f'</div>')

    elif s["type"] == "daily_reports":
        items = []
        for r in s["reports"]:
            items.append(f'<div class="dr-item">'
                         f'<div class="head">{esc(r["date"])} {esc(r["name"])}さん</div>'
                         f'<div><strong>来客特徴:</strong> {esc(r["guests"])}</div>'
                         f'<div style="margin-top:4px"><strong>改善ポイント:</strong> {esc(r["improve"])}</div>'
                         f'</div>')
        body = f'<div class="dr-list">{"".join(items)}</div>'

    elif s["type"] == "summary":
        lis = "".join(f'<li>{esc(it)}</li>' for it in s["items"])
        body = f'<ul class="summary-list">{lis}</ul>'

    elif s["type"] == "action_table":
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td>{esc(c)}</td>' for c in r) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'

    return (f'<div class="slide" id="slide-{n}">'
            f'{header}{message_bar}{classif_bar}'
            f'<div class="slide-body">{body}</div>{caption}{footer}</div>\n')

# ============================================
# 出力
# ============================================
parts = [HTML_HEAD.replace("__STORE__", STORE_NAME).replace("__TM__", _tm)]
for i, s in enumerate(slides):
    parts.append(render_slide(i, s))
parts.append(HTML_FOOT)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(parts))

print(f"✓ HTML written: {OUT}")
print(f"  Slides: {len(slides)}")
print(f"  Size: {os.path.getsize(OUT):,} bytes")
