#!/usr/bin/env python3
"""
BFA 4月月報 HTML生成（v2draft）

入力: analysis.json
出力: ../202604_BFA_月次報告資料_v2draft.html
"""
import json
import os

WORK = os.path.dirname(__file__)
OUT = os.path.join(WORK, "..", "202604_BFA_月次報告資料_v2draft.html")

with open(os.path.join(WORK, "analysis.json"), "r", encoding="utf-8") as f:
    D = json.load(f)

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

# Convenience
M = D["month_kpis"]
m04 = M["2026-04"]
m03 = M.get("2026-03")
m04_py = M.get("2025-04")

# Trend months (oldest first, last = 当月)
trend_months = ["2025-11","2025-12","2026-01","2026-02","2026-03","2026-04"]
trend_data = [(m, M[m]) for m in trend_months if m in M]

# ============================================
# HTMLビルド
# ============================================
TITLE = "BAR FIVE Arrows 月次営業報告"
PERIOD = "2026年4月（2026-04-01 〜 2026-04-30）"
FOOTER_NOTE = "算出根拠: AirRegi 会計明細CSV ／ 営業日基準（0:00-5:59は前日扱い／6AM境界） ／ 集計対象 2026-04-01〜2026-04-30 ／ 一部「ボトル除く」: 月次総売上以外（客単価／週次／日次／曜日別／時間帯別）はボトル購入を除外"

# Slides will be built as a list of dicts then rendered
slides = []

# ───────────────────────────────────────────────
# Slide 1: タイトル
# ───────────────────────────────────────────────
slides.append({
    "type": "title",
    "title": "BAR FIVE Arrows",
    "subtitle": "月次営業報告",
    "period": "2026年4月（4/1 〜 4/30）",
    "note": "第二稿ドラフト v2draft / 2026-05-18 作成",
})

# ───────────────────────────────────────────────
# Slide 2: 月間サマリーKPI
# ───────────────────────────────────────────────
slides.append({
    "type": "kpi",
    "title": "月間サマリー（KPI）",
    "subtitle": "営業日基準（6AM境界）／対予算は引用元確認中",
    "kpis": [
        {"label": "売上（総額）", "value": yen(m04["sales_total"]), "comp": [
            ("前月比", diff_pct(m04["sales_total"], m03["sales_total"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["sales_total"], m04_py["sales_total"]) if m04_py else "—"),
            ("対予算", "引用元確認中"),
        ], "note": "ボトル含む"},
        {"label": "うちボトル購入", "value": yen(m04["bottle_sales"]), "comp": [
            ("構成比", pctv(m04["bottle_sales"]/m04["sales_total"]*100)),
            ("4/30 計上", "¥233,184"),
            ("注記", "5/1朝入力分を補正"),
        ]},
        {"label": "売上（ボトル除く）", "value": yen(m04["sales_excl_bottle"]), "comp": [
            ("前月比", diff_pct(m04["sales_excl_bottle"], (m03["sales_excl_bottle"] if m03 else None))),
            ("前年同月比", diff_pct(m04["sales_excl_bottle"], (m04_py["sales_excl_bottle"] if m04_py else None))),
        ]},
        {"label": "客数", "value": f"{m04['customers']:,}人", "comp": [
            ("前月比", diff_pct(m04["customers"], m03["customers"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["customers"], m04_py["customers"]) if m04_py else "—"),
        ]},
        {"label": "客単価", "value": yen(m04["kyakutanka"]), "comp": [
            ("前月比", diff_pct(m04["kyakutanka"], m03["kyakutanka"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["kyakutanka"], m04_py["kyakutanka"]) if m04_py else "—"),
        ], "note": "（売上−ボトル）÷客数"},
        {"label": "営業日数", "value": f"{m04['business_days']}日", "comp": [
            ("前月", f"{m03['business_days']}日" if m03 else "—"),
            ("前年同月", f"{m04_py['business_days']}日" if m04_py else "—"),
        ]},
        {"label": "日平均売上", "value": yen(m04["daily_avg_sales"]), "comp": [
            ("前月比", diff_pct(m04["daily_avg_sales"], m03["daily_avg_sales"]) if m03 else "—"),
            ("前年同月比", diff_pct(m04["daily_avg_sales"], m04_py["daily_avg_sales"]) if m04_py else "—"),
        ], "note": "ボトル除く"},
    ],
    "caption": "売上総額は前年比で減少。客数も前年比減だが、客単価は前年並みを維持。",
})

# ───────────────────────────────────────────────
# Slide 3-5: 6ヶ月推移
# ───────────────────────────────────────────────
slides.append({
    "type": "line_chart",
    "title": "売上推移（直近6ヶ月）",
    "x_label": "月",
    "y_label": "売上（円）",
    "series": [
        {"name": "売上（総額）", "color": "#3B82F6", "data": [(m, k["sales_total"]) for m, k in trend_data]},
        {"name": "売上（ボトル除く）", "color": "#94A3B8", "data": [(m, k["sales_excl_bottle"]) for m, k in trend_data]},
    ],
    "highlight_last": True,
    "annotation": f"当月 {yen(m04['sales_total'])}（ボトル除く {yen(m04['sales_excl_bottle'])}）",
    "caption": "2026-01以降、減少傾向が続いている。4月はボトル購入が押し上げ要因。",
})

slides.append({
    "type": "line_chart",
    "title": "客数推移（直近6ヶ月）",
    "x_label": "月",
    "y_label": "客数（人）",
    "series": [
        {"name": "客数", "color": "#3B82F6", "data": [(m, k["customers"]) for m, k in trend_data]},
    ],
    "highlight_last": True,
    "annotation": f"当月 {m04['customers']}人",
    "caption": "客数は緩やかな減少傾向。3月から4月は微増（+0.7%）に転じている。",
})

slides.append({
    "type": "line_chart",
    "title": "客単価推移（直近6ヶ月）",
    "x_label": "月",
    "y_label": "客単価（円・ボトル除く）",
    "series": [
        {"name": "客単価（ボトル除く）", "color": "#3B82F6", "data": [(m, k["kyakutanka"]) for m, k in trend_data]},
    ],
    "highlight_last": True,
    "annotation": f"当月 {yen(m04['kyakutanka'])}",
    "caption": "客単価は3月のピーク（¥5,599）から4月は¥4,941へ低下。コース・イベント比率が下がった可能性。",
})

# ───────────────────────────────────────────────
# Slide 6: 前年同月比サマリ
# ───────────────────────────────────────────────
slides.append({
    "type": "comparison_table",
    "title": "前年同月比（2025年4月との比較）",
    "headers": ["指標", "2026-04", "2025-04", "前年比"],
    "rows": [
        ["売上（総額）", yen(m04["sales_total"]), yen(m04_py["sales_total"]) if m04_py else "—",
         diff_pct(m04["sales_total"], m04_py["sales_total"]) if m04_py else "—"],
        ["売上（ボトル除く）", yen(m04["sales_excl_bottle"]),
         yen(m04_py["sales_excl_bottle"]) if m04_py else "—",
         diff_pct(m04["sales_excl_bottle"], m04_py["sales_excl_bottle"]) if m04_py else "—"],
        ["客数", f"{m04['customers']:,}人", f"{m04_py['customers']:,}人" if m04_py else "—",
         diff_pct(m04["customers"], m04_py["customers"]) if m04_py else "—"],
        ["客単価（ボトル除く）", yen(m04["kyakutanka"]), yen(m04_py["kyakutanka"]) if m04_py else "—",
         diff_pct(m04["kyakutanka"], m04_py["kyakutanka"]) if m04_py else "—"],
        ["営業日数", f"{m04['business_days']}日", f"{m04_py['business_days']}日" if m04_py else "—", "—"],
        ["日平均売上（ボトル除く）", yen(m04["daily_avg_sales"]),
         yen(m04_py["daily_avg_sales"]) if m04_py else "—",
         diff_pct(m04["daily_avg_sales"], m04_py["daily_avg_sales"]) if m04_py else "—"],
    ],
    "caption": "前年同月対比は売上・客数ともに大きく減少。客単価のみほぼ同水準。",
})

# ───────────────────────────────────────────────
# Slide 7: 【P1-1】インバウンド比率
# ───────────────────────────────────────────────
p11 = D["p1_1_inbound"]
slides.append({
    "type": "three_set",
    "title": "客層分析①：インバウンド比率",
    "subtitle": "メモ欄「海外」部分一致／提供CSVより抽出",
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
        "accounts": (159 - p11["accounts"]),  # April accounts in rawdata = 159
        "customers": m04["customers"] - p11["customers"],
        "sales": m04["sales_total"] - p11["sales"],
        "share_sales": 100 - p11["share_sales"],
        "share_customers": 100 - p11["share_customers"],
    },
    "caption": f"4月はインバウンド客が{p11['customers']}人来店、売上構成比 {p11['share_sales']:.1f}%。Google検索経由の来店が多数。",
})

# ───────────────────────────────────────────────
# Slide 8: 【P1-2】CLP社員比率
# ───────────────────────────────────────────────
p12 = D["p1_2_clp_employee"]
slides.append({
    "type": "three_set",
    "title": "客層分析②：CLP社員比率（単発利用）",
    "subtitle": "メニュー名「CLP」部分一致／※P1-5コース・P1-6その他CLPコースと重複計上",
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
        "accounts": 159 - p12["accounts"],
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
    "title": "客層分析③：イベント比率",
    "subtitle": "カテゴリ「イベント」／4月のみ計上（5月以降は該当なし想定）",
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
        "accounts": 159 - p13["accounts"],
        "customers": m04["customers"] - p13["customers"],
        "sales": m04["sales_total"] - p13["sales"],
        "share_sales": 100 - p13["share_sales"],
        "share_customers": 100 - p13["share_customers"],
    },
    "caption": f"4月のイベント売上は¥{p13['sales']:,.0f}（{p13['share_sales']:.1f}%）。3件のイベントで{p13['customers']}人を集客。",
})

# ───────────────────────────────────────────────
# Slide 10: 【P1-4】ボトル購入
# ───────────────────────────────────────────────
p14 = D["p1_4_bottle"]
slides.append({
    "type": "callout_table",
    "title": "商品構造①：ボトル購入",
    "subtitle": "カテゴリ「ボトル購入」／★日次・曜日・時間帯すべてから除外、月次総売上のみ計上",
    "big": {
        "label": "ボトル購入 4月計上額",
        "value": yen(p14["sales"]),
        "sub": f"会計件数 {p14['accounts']}件 / 客数 {p14['customers']}人 / 月次売上比 {p14['share_sales']:.1f}%",
    },
    "headers": ["項目", "値", "備考"],
    "rows": [
        ["売上（月次計上）", yen(p14["sales"]), "月次総売上にのみ含める"],
        ["会計件数", f"{p14['accounts']}件", "うち手動補正 2件"],
        ["客数", f"{p14['customers']}人", "—"],
        ["前月比較", "前月は¥0", "4月から計上開始（3月以前と単純比較不可）"],
        ["日次・曜日・時間帯", "除外", "単位売上の傾向を歪めないため"],
        ["手動補正", "+ 2件（5/1朝→4/30扱い）", "5/1 08:57, 08:59 入力分（事務処理上）"],
    ],
    "caption": "ボトル購入は月次総売上にのみ含め、それ以外のすべての集計（客単価／週次／日次／曜日別／時間帯別）から除外。",
})

# ───────────────────────────────────────────────
# Slide 11: 【P1-5/6】コース構成比
# ───────────────────────────────────────────────
p15 = D["p1_5_course"]
p16 = D["p1_6_clp_course"]
slides.append({
    "type": "callout_table",
    "title": "商品構造②：コース構成比",
    "subtitle": "カテゴリ「コース&セット」全体 ／ うち「その他CLPコース」の内訳併記",
    "big": {
        "label": "コース全体 4月売上",
        "value": yen(p15["sales"]),
        "sub": f"会計件数 {p15['accounts']}件 / 客数 {p15['customers']}人 / 構成比 {p15['share_sales']:.1f}%",
    },
    "headers": ["区分", "会計件数", "客数", "売上", "構成比"],
    "rows": [
        ["コース全体", f"{p15['accounts']}件", f"{p15['customers']}人", yen(p15["sales"]), pctv(p15["share_sales"])],
        ["うち その他CLPコース", f"{p16['accounts']}件", f"{p16['customers']}人", yen(p16["sales"]), pctv(p16["share_sales"])],
        ["うち その他のコース", f"{p15['accounts']-p16['accounts']}件",
         f"{p15['customers']-p16['customers']}人",
         yen(p15["sales"]-p16["sales"]),
         pctv(p15["share_sales"]-p16["share_sales"])],
    ],
    "caption": f"コース全体の構成比は {p15['share_sales']:.1f}%。うち約半分（{p16['sales']/p15['sales']*100:.0f}%）が「その他CLPコース」。",
})

# ───────────────────────────────────────────────
# Slide 12-13: フード／ドリンク 出数ランキング
# ───────────────────────────────────────────────
food_qty = D["p1_7_food_qty"][:15]
drink_qty = D["p1_7_drink_qty"][:15]
slides.append({
    "type": "rank_table",
    "title": "フード 出数ランキング（上位15）",
    "subtitle": "カテゴリ分類: food / 数量ベース",
    "headers": ["順位", "メニュー名", "出数", "出現会計", "売上", "構成比（数量）"],
    "rows": [[str(i+1), r["menu_name"], f"{r['qty']:.0f}", f"{r['tx']:.0f}件", yen(r["sales"]), pctv(r["share"])]
             for i, r in enumerate(food_qty)],
    "caption": "ワカモレチップス・ミントのジェノベーゼ・ボロネーゼラザニアがフードの出数TOP3。",
})

slides.append({
    "type": "rank_table",
    "title": "ドリンク 出数ランキング（上位15）",
    "subtitle": "カテゴリ分類: drink / 数量ベース",
    "headers": ["順位", "メニュー名", "出数", "出現会計", "売上", "構成比（数量）"],
    "rows": [[str(i+1), r["menu_name"], f"{r['qty']:.0f}", f"{r['tx']:.0f}件", yen(r["sales"]), pctv(r["share"])]
             for i, r in enumerate(drink_qty)],
    "caption": "ハウスハイボール（168杯）が圧倒的1位。森のジントニックがNEW CLASSIC COCKTAILのトップ。",
})

# ───────────────────────────────────────────────
# Slide 14-15: フード／ドリンク 売上ランキング
# ───────────────────────────────────────────────
food_sales = D["p1_8_food_sales"][:15]
drink_sales = D["p1_8_drink_sales"][:15]
slides.append({
    "type": "rank_table",
    "title": "フード 売上ランキング（上位15）",
    "subtitle": "カテゴリ分類: food / 売上ベース",
    "headers": ["順位", "メニュー名", "売上", "出数", "構成比（売上）"],
    "rows": [[str(i+1), r["menu_name"], yen(r["sales"]), f"{r['qty']:.0f}", pctv(r["share"])]
             for i, r in enumerate(food_sales)],
    "caption": "フード売上TOP3 は ワカモレチップス／ミントのジェノベーゼ／ボロネーゼラザニア（出数TOP3と一致）。",
})

slides.append({
    "type": "rank_table",
    "title": "ドリンク 売上ランキング（上位15）",
    "subtitle": "カテゴリ分類: drink / 売上ベース",
    "headers": ["順位", "メニュー名", "売上", "出数", "構成比（売上）"],
    "rows": [[str(i+1), r["menu_name"], yen(r["sales"]), f"{r['qty']:.0f}", pctv(r["share"])]
             for i, r in enumerate(drink_sales)],
    "caption": "ドリンク売上1位はハウスハイボール（¥201,600 / 16.7%）。森のジントニックが2位。",
})

# ───────────────────────────────────────────────
# Slide 16: 週別概況（ボトル除く）
# ───────────────────────────────────────────────
weekly = D["weekly"]
max_w = max(weekly, key=lambda x: x["daily_avg"])
min_w = min(weekly, key=lambda x: x["daily_avg"])
slides.append({
    "type": "bar_chart",
    "title": "週別概況 — 1日あたり売上（日平均・ボトル除く）",
    "x_label": "ISO週",
    "y_label": "日平均売上（円）",
    "bars": [{"name": w["year_week"], "value": w["daily_avg"],
              "color": ("#22C55E" if w["year_week"]==max_w["year_week"] else
                        "#EF4444" if w["year_week"]==min_w["year_week"] else "#3B82F6"),
              "highlight": (w["year_week"] in (max_w["year_week"], min_w["year_week"])),
              "sub": f"営{w['business_days']}日"}
             for w in weekly],
    "legend": [
        {"name": "好調週", "color": "#22C55E"},
        {"name": "通常週", "color": "#3B82F6"},
        {"name": "不調週", "color": "#EF4444"},
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
    "title": "曜日別 日平均売上（ボトル除く）",
    "x_label": "曜日",
    "y_label": "日平均売上（円）",
    "bars": [{"name": w["weekday"], "value": w["daily_avg_sales"],
              "color": ("#22C55E" if w["weekday"]==max_wd["weekday"] else
                        "#EF4444" if w["weekday"]==min_wd["weekday"] else "#3B82F6"),
              "highlight": (w["weekday"] in (max_wd["weekday"], min_wd["weekday"])),
              "sub": f"営{w['business_days']}日"}
             for w in wd],
    "legend": [
        {"name": "好調曜日", "color": "#22C55E"},
        {"name": "通常", "color": "#3B82F6"},
        {"name": "不調曜日", "color": "#EF4444"},
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
    "title": "時間帯別 月間売上（入店時刻ベース・ボトル除く）",
    "x_label": "時間帯",
    "y_label": "月間売上（円）",
    "bars": [{"name": h["hour_bucket"]+"時", "value": h["sales_excl_bottle"],
              "color": "#3B82F6", "highlight": False,
              "sub": f"客{h['customers']}人 ({h['share']:.1f}%)"}
             for h in hr_sorted],
    "legend": [{"name": "月間売上", "color": "#3B82F6"}],
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
    "title": "カテゴリ別 月間売上 上位10",
    "subtitle": "全カテゴリ（ボトル購入含む）",
    "headers": ["順位", "カテゴリ", "月間売上", "数量", "構成比"],
    "rows": [[str(i+1), c["category1"], yen(c["sales"]), f"{c['qty']:.0f}", pctv(c["share"])]
             for i, c in enumerate(cat)],
    "caption": "コース&セットが20.9%で最大。ボトル購入8.0%、その他9.0%（チャージ等）。",
})

# ───────────────────────────────────────────────
# Slide 20: 日報スライド（あれば）
# ───────────────────────────────────────────────
dr = D["daily_reports"]
if dr:
    slides.append({
        "type": "daily_reports",
        "title": "店舗の様子 — 日報より（4月）",
        "subtitle": f"対象月の日報入力件数: {len(dr)}件",
        "reports": [{"date": r["営業日"], "name": r["入力者氏名"],
                     "guests": (r["①来客特徴"] or "")[:300],
                     "improve": (r["②改善ポイント"] or "")[:300]}
                    for r in dr],
        "caption": "4月後半に集中した日報入力。海外ゲスト・コース利用・常連グループの3パターンが繰り返し言及。",
    })

# ───────────────────────────────────────────────
# Slide 21: 強み
# ───────────────────────────────────────────────
slides.append({
    "type": "summary",
    "title": "今月の強み",
    "items": [
        f"インバウンド客が{p11['customers']}人・売上¥{p11['sales']:,.0f}（売上構成比 {p11['share_sales']:.1f}%）。Google検索経由の認知が成果に",
        f"コース利用が好調（{p15['accounts']}件・{p15['customers']}人・¥{p15['sales']:,.0f}／{p15['share_sales']:.1f}%）。CLP関連のコース予約が安定収益源",
        f"金曜日（日平均{yen(max_wd['daily_avg_sales'])}）と土曜日（日平均¥{wd[5]['daily_avg_sales']:,.0f}）が引き続き強い",
        f"ハウスハイボール（168杯／¥201,600）が安定したドリンク主力商品",
        f"4月からボトル販売を計上開始（¥{p14['sales']:,.0f}）。月次売上の押し上げ要因に",
    ],
    "caption": "新規切り口で見ると、インバウンド・CLP・コースが収益の柱として可視化された。",
})

# ───────────────────────────────────────────────
# Slide 22: 課題
# ───────────────────────────────────────────────
slides.append({
    "type": "summary",
    "title": "今月の課題",
    "items": [
        f"売上は前年同月比 {diff_pct(m04['sales_total'], m04_py['sales_total']) if m04_py else '—'}（{yen(m04['sales_total'])} vs {yen(m04_py['sales_total']) if m04_py else '—'}）",
        f"客数は前年同月比 {diff_pct(m04['customers'], m04_py['customers']) if m04_py else '—'}（{m04['customers']}人 vs {m04_py['customers'] if m04_py else '—'}人）",
        f"客単価が前月の¥{m03['kyakutanka']:,.0f}から¥{m04['kyakutanka']:,.0f}に低下（{diff_pct(m04['kyakutanka'], m03['kyakutanka']) if m03 else '—'}）",
        f"月曜日が日平均¥{min_wd['daily_avg_sales']:,.0f}と弱く、火曜・木曜も低調",
        f"24-26時帯の売上が1.3%まで低下。深夜需要の取り込み余地",
    ],
    "caption": "全体トレンドは前年比減。曜日・時間帯の偏りが顕在化しており、平日強化と深夜需要が論点。",
})

# ───────────────────────────────────────────────
# Slide 23: 施策一覧
# ───────────────────────────────────────────────
slides.append({
    "type": "action_table",
    "title": "次月以降の施策案",
    "headers": ["優先", "テーマ", "施策案", "狙い・指標"],
    "rows": [
        ["高", "インバウンド", "Googleマップ口コミ強化（英語応答テンプレ／写真追加）", "海外比率を10%→15%へ"],
        ["高", "客単価回復", "コース後アラカルト追加の常時提案 ／ ペアリングメニュー導入", "客単価¥4,941→¥5,500"],
        ["高", "平日強化", "月曜「インバウンド限定割引」or「平日早割」（18-19時）", "月曜日平均¥49,400→¥75,000"],
        ["中", "ボトル販売", "CLP社員向けボトルキープ施策の継続・定型化", "月次¥23万→¥30万"],
        ["中", "深夜需要", "金土の24-26時限定「ナイトキャップセット」", "24-26時構成比 1.3%→5%"],
        ["低", "日報強化", "4月の日報入力3件は少ない。週次入力リズム化", "月10〜15件入力"],
    ],
    "caption": "高優先3件は前年比減・客単価低下への直接対策。中優先2件は4月の新規収益柱の拡大策。",
})

# ───────────────────────────────────────────────
# Slide 24: 確認事項 / 引用元・注記
# ───────────────────────────────────────────────
slides.append({
    "type": "summary",
    "title": "確認事項・データソース注記",
    "items": [
        "対予算（消化率）: 「【BFA】本部サポート」PLシートに2026-04列がなく、引用元セルが特定できず（要確認）",
        "ボトル購入 ¥233,184 のうち ¥233,184 は 5/1 朝（08:57, 08:59）入力のため4/30営業日へ手動補正",
        "インバウンド／CLP社員（メモ）は提供CSV `会計明細_20260401-20260430` のメモ欄から抽出（30件・3件）",
        "売上データ本体は週報パイプライン経由のダッシュボード本番DB（rawdata.csv）を使用",
        "営業日基準: 0:00〜5:59 を前日扱い（6AM境界・既存仕様）",
        "客単価＝（売上 − ボトル購入）÷ 客数（v1.2仕様）",
        "前年同月比較データ（2025-04）: 売上¥3,802,800／客数777人／営業日30日（rawdata.csv より）",
    ],
    "caption": "本資料の数値再現に必要な情報をすべて注記。第二稿ドラフト（v2draft）として共有。",
})

# ============================================
# CSS / JS (D3.js) + HTML レンダリング
# ============================================
HTML_HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>BAR FIVE Arrows 月次営業報告 — 2026-04 (v2draft)</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  @page { size: 1280px 720px; margin: 0; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
    body { margin: 0; padding: 0; background: #fff; width: 1280px; }
    .slide { page-break-after: always; page-break-inside: avoid; break-after: page; break-inside: avoid;
             box-shadow: none; margin: 0; width: 1280px; height: 720px; }
    .slide:last-child { page-break-after: auto; }
  }
  @media screen {
    body { background: #E2E8F0; font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; }
    .slide { margin: 20px auto; box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
  }
  .slide { width: 1280px; height: 720px; position: relative; overflow: hidden; background: #ffffff;
           font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; color: #1E293B; }
  .slide-header { background: #1E3A5F; color: #fff; padding: 16px 32px; display: flex;
                  flex-direction: column; gap: 4px; }
  .slide-header .h-title { font-size: 26px; font-weight: 800; }
  .slide-header .h-sub { font-size: 14px; font-weight: 400; opacity: 0.85; }
  .slide-body { padding: 24px 32px; height: calc(720px - 100px - 50px); overflow: hidden; }
  .footer-note { position: absolute; bottom: 8px; left: 24px; right: 24px;
                 font-size: 11px; color: #64748B; line-height: 1.4; }
  .caption { font-size: 13px; color: #475569; font-weight: 600; margin-top: 10px;
             padding: 8px 12px; background: #F1F5F9; border-left: 3px solid #3B82F6; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th { background: #1E3A5F; color: #fff; padding: 8px 10px; text-align: left; font-weight: 700; font-size: 13px; }
  td { padding: 7px 10px; border-bottom: 1px solid #E2E8F0; font-size: 13px; }
  tr:nth-child(even) td { background: #F8FAFC; }
  td.num { text-align: right; }
  /* Title slide */
  .slide-title { background: linear-gradient(135deg, #1E3A5F 0%, #0F172A 100%); color: #fff;
                 display: flex; flex-direction: column; justify-content: center; align-items: center; }
  .slide-title h1 { font-size: 60px; font-weight: 800; margin: 0; }
  .slide-title h2 { font-size: 32px; font-weight: 400; margin: 16px 0 0 0; opacity: 0.9; }
  .slide-title .period { font-size: 22px; margin-top: 36px; opacity: 0.85; }
  .slide-title .note { font-size: 14px; margin-top: 18px; opacity: 0.6; }
  /* KPI cards */
  .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px; }
  .kpi-card { background: #F8FAFC; border-left: 4px solid #3B82F6; padding: 12px 14px; min-height: 110px; }
  .kpi-card.bottle { border-left-color: #F97316; }
  .kpi-card.exclbottle { border-left-color: #22C55E; }
  .kpi-card .lab { font-size: 11px; color: #64748B; font-weight: 700; }
  .kpi-card .val { font-size: 24px; font-weight: 800; color: #1E293B; margin-top: 6px; }
  .kpi-card .comp { font-size: 11px; color: #475569; margin-top: 4px; line-height: 1.5; }
  .kpi-card .note { font-size: 10px; color: #94A3B8; margin-top: 4px; font-style: italic; }
  .pos { color: #22C55E; font-weight: 700; }
  .neg { color: #EF4444; font-weight: 700; }
  /* Three-set */
  .three-set { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .three-set .pane { background: #F8FAFC; padding: 16px; border-radius: 6px; border-top: 4px solid #3B82F6; }
  .three-set .pane.right { border-top-color: #94A3B8; }
  .three-set .pane h3 { margin: 0 0 10px 0; font-size: 18px; }
  .three-set .pane .row { display: flex; justify-content: space-between; padding: 6px 0;
                          border-bottom: 1px dashed #E2E8F0; font-size: 14px; }
  .three-set .pane .row .v { font-weight: 800; }
  /* Callout */
  .callout-big { background: #FFF7ED; border: 2px solid #F97316; padding: 18px 24px; text-align: center;
                 margin-bottom: 14px; border-radius: 6px; }
  .callout-big .lab { font-size: 14px; color: #C2410C; font-weight: 700; }
  .callout-big .val { font-size: 46px; color: #1E293B; font-weight: 800; }
  .callout-big .sub { font-size: 13px; color: #475569; margin-top: 4px; }
  /* Bar/Line layout */
  .chart-grid { display: grid; grid-template-columns: 3fr 2fr; gap: 14px; height: 100%; }
  .chart-area { background: #F8FAFC; padding: 6px; }
  .legend { display: flex; gap: 14px; margin-bottom: 6px; padding: 0 0 4px 4px; }
  .legend .item { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: #334155; }
  .legend .swatch { width: 14px; height: 14px; }
  /* Summary list */
  .summary-list { font-size: 16px; line-height: 1.7; }
  .summary-list li { margin-bottom: 10px; padding: 8px 12px; background: #F8FAFC; border-left: 3px solid #3B82F6; }
  /* Daily reports */
  .dr-list { display: flex; flex-direction: column; gap: 10px; }
  .dr-item { background: #F8FAFC; padding: 10px 14px; border-left: 3px solid #3B82F6; font-size: 12px; }
  .dr-item .head { font-weight: 800; color: #1E3A5F; margin-bottom: 4px; }
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
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');
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
    .attr('fill',d=>d.highlight?'#1E293B':'#64748B')
    .text(d=>'¥'+Math.round(d.value).toLocaleString());
  // sub labels
  g.selectAll('text.sub').data(cfg.bars).join('text').attr('class','sub')
    .attr('x',d=>x(d.name)+x.bandwidth()/2).attr('y',h+34)
    .attr('text-anchor','middle').attr('font-size','10px').attr('fill','#94A3B8').text(d=>d.sub||'');
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
  const m = {top:30,right:30,bottom:50,left:80};
  const w = el.clientWidth - m.left - m.right;
  const h = 280 - m.top - m.bottom;
  const svg = d3.select(el).append('svg').attr('width', el.clientWidth).attr('height', 280);
  const g = svg.append('g').attr('transform','translate('+m.left+','+m.top+')');
  const months = cfg.series[0].data.map(d=>d[0]);
  const allVals = cfg.series.flatMap(s=>s.data.map(d=>d[1]));
  const x = d3.scalePoint().domain(months).range([0,w]).padding(0.5);
  const y = d3.scaleLinear().domain([0, d3.max(allVals)*1.15]).range([h,0]);
  // grid
  g.append('g').selectAll('line').data(y.ticks(5)).join('line')
    .attr('x1',0).attr('x2',w).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');
  cfg.series.forEach(s=>{
    const line = d3.line().x(d=>x(d[0])).y(d=>y(d[1]));
    g.append('path').attr('d',line(s.data)).attr('fill','none').attr('stroke',s.color).attr('stroke-width',3);
    g.selectAll('circle.'+s.name.replace(/\\W/g,'_')).data(s.data).join('circle')
      .attr('cx',d=>x(d[0])).attr('cy',d=>y(d[1]))
      .attr('r',(d,i)=>(cfg.highlight_last && i===s.data.length-1) ? 8 : 4)
      .attr('fill',s.color);
  });
  g.append('g').attr('transform','translate(0,'+h+')').call(d3.axisBottom(x)).selectAll('text').attr('font-size','12px');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+d3.format(',.0f')(d))).selectAll('text').attr('font-size','10px');
  // legend
  addLegend(svg, cfg.series.map(s=>({label:s.name,color:s.color})), m.left, 6);
  // annotation
  if(cfg.annotation){
    const lastSerie = cfg.series[0];
    const last = lastSerie.data[lastSerie.data.length-1];
    const xPos = x(last[0]) + m.left - 200;
    const yPos = y(last[1]) + m.top - 6;
    const an = svg.append('g');
    const t = an.append('text').attr('x',xPos).attr('y',yPos)
      .attr('font-size','16px').attr('font-weight','800').attr('fill','#C2410C').text(cfg.annotation);
    const bb = t.node().getBBox();
    an.insert('rect','text').attr('x',bb.x-8).attr('y',bb.y-4).attr('width',bb.width+16).attr('height',bb.height+8)
      .attr('rx',4).attr('fill','#FFF7ED').attr('stroke','#F97316').attr('stroke-width',1.5);
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
    header = f'<div class="slide-header"><div class="h-title">{esc(s["title"])}</div>'
    if s.get("subtitle"):
        header += f'<div class="h-sub">{esc(s["subtitle"])}</div>'
    header += '</div>'
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
        body = f'<div class="kpi-grid">{"".join(cards)}</div>' + caption

    elif s["type"] == "line_chart":
        import json as _json
        cfg = _json.dumps({"series": s["series"], "highlight_last": s.get("highlight_last", False), "annotation": s.get("annotation","")}, ensure_ascii=False)
        body = f'<div data-line=\'{esc(cfg)}\' style="height:300px"></div>' + caption

    elif s["type"] == "comparison_table":
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td class="num">{esc(c) if i>0 else esc(c)}</td>'
                                       if i>0 else f'<td>{esc(c)}</td>'
                                       for i, c in enumerate(r)) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>' + caption

    elif s["type"] == "three_set":
        def pane_html(p, label, cls):
            return (f'<div class="pane {cls}"><h3>{esc(label)}</h3>'
                    f'<div class="row"><span>会計件数</span><span class="v">{p["accounts"]}件</span></div>'
                    f'<div class="row"><span>客数</span><span class="v">{p["customers"]}人 ({p["share_customers"]:.1f}%)</span></div>'
                    f'<div class="row"><span>売上</span><span class="v">{yen(p["sales"])} ({p["share_sales"]:.1f}%)</span></div>'
                    f'</div>')
        body = ('<div class="three-set">'
                + pane_html(s["left"], s["left_label"], "left")
                + pane_html(s["right"], s["right_label"], "right")
                + '</div>' + caption)

    elif s["type"] == "callout_table":
        big = s["big"]
        cb = (f'<div class="callout-big">'
              f'<div class="lab">{esc(big["label"])}</div>'
              f'<div class="val">{esc(big["value"])}</div>'
              f'<div class="sub">{esc(big["sub"])}</div></div>')
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td>{esc(c)}</td>' for c in r) + "</tr>" for r in s["rows"])
        body = cb + f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>' + caption

    elif s["type"] == "rank_table":
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td class="num">{esc(c)}</td>' if i>=2 else f'<td>{esc(c)}</td>'
                                       for i, c in enumerate(r)) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>' + caption

    elif s["type"] == "bar_chart":
        import json as _json
        cfg = _json.dumps({"bars": s["bars"], "legend": s.get("legend", [])}, ensure_ascii=False)
        tt_ths = "".join(f'<th>{esc(h)}</th>' for h in s["table_headers"])
        tt_trs = "".join("<tr>" + "".join(f'<td>{esc(c)}</td>' for c in r) + "</tr>" for r in s["table_rows"])
        body = (f'<div class="chart-grid">'
                f'  <div class="chart-area"><div data-bar=\'{esc(cfg)}\'></div></div>'
                f'  <div><table><thead><tr>{tt_ths}</tr></thead><tbody>{tt_trs}</tbody></table></div>'
                f'</div>' + caption)

    elif s["type"] == "daily_reports":
        items = []
        for r in s["reports"]:
            items.append(f'<div class="dr-item">'
                         f'<div class="head">{esc(r["date"])} {esc(r["name"])}さん</div>'
                         f'<div><strong>来客特徴:</strong> {esc(r["guests"])}</div>'
                         f'<div style="margin-top:4px"><strong>改善ポイント:</strong> {esc(r["improve"])}</div>'
                         f'</div>')
        body = f'<div class="dr-list">{"".join(items)}</div>' + caption

    elif s["type"] == "summary":
        lis = "".join(f'<li>{esc(it)}</li>' for it in s["items"])
        body = f'<ul class="summary-list">{lis}</ul>' + caption

    elif s["type"] == "action_table":
        ths = "".join(f'<th>{esc(h)}</th>' for h in s["headers"])
        trs = "".join("<tr>" + "".join(f'<td>{esc(c)}</td>' for c in r) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>' + caption

    return f'<div class="slide" id="slide-{n}">{header}<div class="slide-body">{body}</div>{footer}</div>\n'

# ============================================
# 出力
# ============================================
parts = [HTML_HEAD]
for i, s in enumerate(slides):
    parts.append(render_slide(i, s))
parts.append(HTML_FOOT)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(parts))

print(f"✓ HTML written: {OUT}")
print(f"  Slides: {len(slides)}")
print(f"  Size: {os.path.getsize(OUT):,} bytes")
