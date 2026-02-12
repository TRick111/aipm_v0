#!/usr/bin/env python3
"""Generate the weekly report HTML slide deck for BAR FIVE Arrows 2026-W04.
Design: msg-bar pattern from monthly report reference, 1.5x font sizes."""

import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "20260119_20260125_BAR_FIVE_Arrows_週次報告資料.html")

H = "#1E3A5F"  # header
P = "#22C55E"   # positive
N = "#EF4444"   # negative
A = "#F97316"   # attention
C = "#3B82F6"   # current
G = "#94A3B8"   # comparison/gray
BG = "#F8FAFC"
T = "#334155"   # text
HD = "#1E293B"  # heading

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BAR FIVE Arrows 週次営業報告 2026-W04</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#E2E8F0;font-family:'Helvetica Neue','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif;color:{T};font-size:20px}}
.slide{{width:1280px;height:720px;position:relative;overflow:hidden;background:#fff;margin:0 auto}}
@media screen{{.slide{{margin:0 auto 40px;box-shadow:0 4px 20px rgba(0,0,0,.12)}}}}
@page{{size:1280px 720px;margin:0}}
@media print{{*{{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}}body{{margin:0;padding:0;background:#fff;width:1280px}}.slide{{page-break-after:always;page-break-inside:avoid;break-after:page;break-inside:avoid;box-shadow:none;margin:0}}.slide:last-child{{page-break-after:auto}}}}
.slide-title{{background:linear-gradient(135deg,{H} 0%,#0F172A 100%);display:flex;flex-direction:column;justify-content:center;align-items:center;color:#fff}}
.slide-title h1{{font-size:48px;font-weight:800;letter-spacing:2px}}
.slide-title h2{{font-size:28px;font-weight:400;margin-top:12px;opacity:.9}}
.slide-title p{{font-size:18px;margin-top:24px;opacity:.7}}
.slide-header{{background:{H};color:#fff;padding:14px 40px;display:flex;align-items:center;justify-content:space-between}}
.slide-header h2{{font-size:32px;font-weight:700}}
.slide-header .pn{{font-size:16px;opacity:.7}}
.msg-bar{{background:#FFF7ED;border-left:5px solid {A};padding:12px 40px;font-size:27px;font-weight:700;color:{HD};line-height:1.4}}
.slide-body{{padding:14px 40px;overflow:hidden}}
.kpi-grid{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:6px}}
.kpi-card{{background:{BG};border:1px solid #E2E8F0;border-radius:12px;padding:14px 16px;text-align:center;flex:1;min-width:170px;max-width:240px}}
.kpi-label{{display:block;font-size:17px;color:#64748B;margin-bottom:4px}}
.kpi-value{{display:block;font-size:44px;font-weight:800;color:{HD}}}
.kpi-sub{{display:block;font-size:18px;margin-top:2px}}
.kpi-change{{display:block;font-size:22px;font-weight:700;margin-top:4px}}
.pos{{color:{P}}}.neg{{color:{N}}}.neu{{color:#64748B}}
.two-col{{display:flex;gap:24px}}.col-chart{{flex:2}}.col-text{{flex:1;font-size:20px;line-height:1.7}}
.dt{{width:100%;border-collapse:collapse;font-size:20px}}
.dt th{{background:{H};color:#fff;padding:10px 14px;text-align:left;font-weight:700;font-size:19px}}
.dt td{{padding:9px 14px;border-bottom:1px solid #E2E8F0}}
.dt tr:nth-child(even) td{{background:{BG}}}
.dt .r{{text-align:right}}.dt .b{{font-weight:700}}
.dt .best td{{background:#F0FDF4}}.dt .worst td{{background:#FEF2F2}}
.dt.sm{{font-size:18px}}.dt.sm th{{padding:8px 10px;font-size:17px}}.dt.sm td{{padding:7px 10px}}
.sec-title{{font-size:26px;font-weight:800;color:{HD};margin:8px 0 6px;padding-left:14px;border-left:5px solid {C}}}
.sec-title.g{{border-color:{P}}}.sec-title.r{{border-color:{N}}}.sec-title.o{{border-color:{A}}}
.bl{{list-style:none;padding:0}}
.bl li{{padding:6px 0 6px 22px;position:relative;font-size:20px;line-height:1.6}}
.bl li::before{{content:'●';position:absolute;left:0;color:{C};font-size:12px;top:12px}}
.bl.g li::before{{color:{P}}}.bl.r li::before{{color:{N}}}
.nl{{list-style:none;padding:0;counter-reset:nl}}
.nl li{{padding:7px 0 7px 36px;position:relative;font-size:20px;line-height:1.5;counter-increment:nl}}
.nl li::before{{content:counter(nl);position:absolute;left:0;width:28px;height:28px;background:{C};color:#fff;border-radius:50%;text-align:center;line-height:28px;font-size:16px;font-weight:700}}
.nl.g li::before{{background:{P}}}.nl.r li::before{{background:{N}}}
.note-box{{background:#F0FDF4;border-radius:10px;border-left:5px solid {P};padding:12px 20px;margin-top:8px;font-size:20px;line-height:1.6;font-weight:600}}
.warn-box{{background:#FEF2F2;border-radius:10px;border-left:5px solid {N};padding:12px 20px;margin-top:8px;font-size:20px;line-height:1.6;font-weight:600}}
.info-box{{background:#EFF6FF;border-radius:10px;border-left:5px solid {C};padding:12px 20px;margin-top:8px;font-size:20px;line-height:1.6;font-weight:600}}
.card{{background:{BG};border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;margin:6px 0}}
.card-title{{font-size:22px;font-weight:800;margin-bottom:4px}}
.card-title.g{{color:{P}}}.card-title.r{{color:{N}}}
.big-num{{font-size:48px;font-weight:800;line-height:1.2}}
.big-label{{font-size:18px;color:#64748B;font-weight:600}}
.emphasis{{font-size:28px;font-weight:800}}
.at{{width:100%;border-collapse:collapse;font-size:18px}}
.at th{{background:{H};color:#fff;padding:8px 12px;text-align:left;font-size:16px}}
.at td{{padding:7px 12px;border-bottom:1px solid #E2E8F0}}
.at tr:nth-child(even) td{{background:{BG}}}
.at .no{{width:32px;text-align:center;font-weight:700;color:{C}}}
.compare{{display:flex;gap:20px}}.compare>div{{flex:1}}
strong{{font-weight:700}}
svg text{{font-family:'Helvetica Neue','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif}}
</style>
</head>
<body>

<!-- Slide 1: Title -->
<div class="slide slide-title" id="s1">
<div style="font-size:14px;letter-spacing:4px;opacity:.7;margin-bottom:20px">WEEKLY BUSINESS REPORT</div>
<h1>BAR FIVE Arrows</h1>
<h2>週次営業報告</h2>
<div style="width:80px;height:3px;background:{C};margin:24px 0"></div>
<p>2026年第4週 / 1月19日（月）〜 1月25日（日）</p>
<div style="position:absolute;bottom:24px;font-size:14px;opacity:.5">20260119_20260125週次報告資料</div>
</div>

<!-- Slide 2: Executive Summary -->
<div class="slide" id="s2">
<div class="slide-header"><h2>エグゼクティブサマリー</h2><span class="pn">2 / 28</span></div>
<div class="msg-bar">全指標が前週比・前年比で下落。金曜日の大幅好調でも水曜日の不振を補えず、平日全体の底上げが急務</div>
<div class="slide-body">
<div class="kpi-grid">
<div class="kpi-card"><span class="kpi-label">売上</span><span class="kpi-value" style="font-size:36px">¥628,140</span><span class="kpi-change neg">▼ 前週比 -22.9%</span><span class="kpi-sub neg">▼ 前年比 -29.1%</span></div>
<div class="kpi-card"><span class="kpi-label">客数</span><span class="kpi-value">116<small style="font-size:28px">人</small></span><span class="kpi-change neg">▼ 前週比 -12.1%</span><span class="kpi-sub neg">▼ 前年比 -21.1%</span></div>
<div class="kpi-card"><span class="kpi-label">客単価</span><span class="kpi-value">¥5,415</span><span class="kpi-change neg">▼ 前週比 -12.3%</span><span class="kpi-sub neg">▼ 前年比 -10.1%</span></div>
<div class="kpi-card"><span class="kpi-label">組数</span><span class="kpi-value">36<small style="font-size:28px">組</small></span><span class="kpi-change neg">▼ 前週比 -18.2%</span><span class="kpi-sub neu">前年比 —</span></div>
</div>
<div class="note-box" style="border-color:{P}"><strong style="color:{P}">金曜日のみ好調</strong>：売上¥231,520（4週平均比+65.4%）、客数35人（同+41.1%）</div>
<div class="warn-box"><strong style="color:{N}">水曜日が最大の課題</strong>：売上¥42,810（4週平均比30.1%）、客数11人（同37.0%）</div>
</div>
</div>

<!-- Slide 3: Sales Trend -->
<div class="slide" id="s3">
<div class="slide-header"><h2>売上トレンド（直近5週間）</h2><span class="pn">3 / 28</span></div>
<div class="msg-bar">W03で回復基調に乗ったがW04で再下落。前年同週比-29.1%と3割近い減少</div>
<div class="slide-body">
<div class="two-col">
<div class="col-chart"><div id="chart-3" style="width:760px;height:420px"></div></div>
<div class="col-text">
<div class="sec-title r">前年同週比較</div>
<div style="text-align:center;margin:12px 0"><span class="big-label">今週 (W04)</span><br><span class="big-num neg">¥628,140</span><br><span style="font-size:20px;color:#64748B">前年同週 ¥885,840</span><br><span class="emphasis neg" style="margin-top:6px;display:inline-block">▼ -29.1%（-¥257,700）</span></div>
</div></div>
</div>
</div>

<!-- Slide 4: Customer Trend -->
<div class="slide" id="s4">
<div class="slide-header"><h2>客数トレンド（直近5週間）</h2><span class="pn">4 / 28</span></div>
<div class="msg-bar">水曜日の客数11人と火曜日の6人が全体を大きく押し下げ、前年比-21.1%</div>
<div class="slide-body">
<div class="two-col">
<div class="col-chart"><div id="chart-4" style="width:760px;height:420px"></div></div>
<div class="col-text">
<div class="sec-title r">前年同週比較</div>
<div style="text-align:center;margin:12px 0"><span class="big-label">今週 (W04)</span><br><span class="big-num neg">116<small style="font-size:28px">人</small></span><br><span style="font-size:20px;color:#64748B">前年同週 147人</span><br><span class="emphasis neg" style="margin-top:6px;display:inline-block">▼ -21.1%（-31人）</span></div>
</div></div>
</div>
</div>

<!-- Slide 5: Unit Price Trend -->
<div class="slide" id="s5">
<div class="slide-header"><h2>客単価トレンド（直近5週間）</h2><span class="pn">5 / 28</span></div>
<div class="msg-bar">W01〜W03にかけて上昇傾向だったが、W04で¥5,415に急落。前年比-10.1%</div>
<div class="slide-body">
<div class="two-col">
<div class="col-chart"><div id="chart-5" style="width:760px;height:420px"></div></div>
<div class="col-text">
<div class="sec-title r">前年同週比較</div>
<div style="text-align:center;margin:12px 0"><span class="big-label">今週 (W04)</span><br><span class="big-num neg">¥5,415</span><br><span style="font-size:20px;color:#64748B">前年同週 ¥6,026</span><br><span class="emphasis neg" style="margin-top:6px;display:inline-block">▼ -10.1%（-¥611）</span></div>
</div></div>
</div>
</div>

<!-- Slide 6: YoY Summary -->
<div class="slide" id="s6">
<div class="slide-header"><h2>前年同週比サマリー</h2><span class="pn">6 / 28</span></div>
<div class="msg-bar">前年同週比で3指標すべてが下落。売上-29.1%は客数減と客単価減の複合要因</div>
<div class="slide-body">
<div class="kpi-grid" style="margin-top:12px">
<div class="kpi-card"><span class="kpi-label">売上</span><span class="kpi-value neg" style="font-size:48px">-29.1%</span><span class="kpi-change neg">▼▼ 大幅減</span><span class="kpi-sub">¥885,840 → ¥628,140</span></div>
<div class="kpi-card"><span class="kpi-label">客数</span><span class="kpi-value neg" style="font-size:48px">-21.1%</span><span class="kpi-change neg">▼▼ 大幅減</span><span class="kpi-sub">147人 → 116人</span></div>
<div class="kpi-card"><span class="kpi-label">客単価</span><span class="kpi-value neg" style="font-size:48px">-10.1%</span><span class="kpi-change neg">▼ 減少</span><span class="kpi-sub">¥6,026 → ¥5,415</span></div>
</div>
<div class="info-box" style="margin-top:16px">
<ul class="bl" style="margin:0"><li>前年W04は売上¥885,840に対し、今年は¥628,140と<strong>¥257,700の差</strong></li><li>客数は147人→116人で31人減。客単価は¥6,026→¥5,415で¥611の低下</li><li>客数減（-21.1%）と客単価減（-10.1%）の複合要因で売上が約3割減少</li></ul>
</div>
</div>
</div>

<!-- Slide 7: Day-of-Week Overview -->
<div class="slide" id="s7">
<div class="slide-header"><h2>曜日別概況</h2><span class="pn">7 / 28</span></div>
<div class="msg-bar">7日中6日が4週平均を下回り、金曜日のみプラス。水曜日（-¥99,620）の不振が最大</div>
<div class="slide-body">
<div id="chart-7" style="width:1180px;height:370px"></div>
</div>
</div>

<!-- Slide 8: Wednesday Basic Numbers -->
<div class="slide" id="s8">
<div class="slide-header"><h2>水曜日（不調）の分析：基本数字</h2><span class="pn">8 / 28</span></div>
<div class="msg-bar">売上は4週平均のわずか30.1%。会計3件と営業として成立していない水準</div>
<div class="slide-body">
<div class="kpi-grid">
<div class="kpi-card"><span class="kpi-label">売上</span><span class="kpi-value neg">¥42,810</span><span class="kpi-change neg">4週平均比 30.1%</span></div>
<div class="kpi-card"><span class="kpi-label">客数</span><span class="kpi-value neg">11<small style="font-size:28px">人</small></span><span class="kpi-change neg">4週平均比 37.0%</span></div>
<div class="kpi-card"><span class="kpi-label">客単価</span><span class="kpi-value neg">¥3,892</span><span class="kpi-change neg">4週平均比 81.7%</span></div>
<div class="kpi-card"><span class="kpi-label">会計数</span><span class="kpi-value">3<small style="font-size:28px">件</small></span><span class="kpi-change neu">—</span></div>
</div>
<div id="chart-8" style="width:1180px;height:240px;margin-top:8px"></div>
</div>
</div>

<!-- Slide 9: Wednesday Group Size -->
<div class="slide" id="s9">
<div class="slide-header"><h2>水曜日（不調）の分析：グループ人数</h2><span class="pn">9 / 28</span></div>
<div class="msg-bar">3組のみの来店。大口グループの不在が売上差の大部分を説明する</div>
<div class="slide-body"><div id="chart-9" style="width:1180px;height:370px"></div>
<div class="info-box" style="font-size:18px">5名以上グループは1組5人（売上¥19,580）のみ。4週平均では5名以上が1組平均13人程度の来店があった</div>
</div>
</div>

<!-- Slide 10: Wednesday Time Bucket -->
<div class="slide" id="s10">
<div class="slide-header"><h2>水曜日（不調）の分析：時間帯別売上</h2><span class="pn">10 / 28</span></div>
<div class="msg-bar">プライムタイム（20-24時）は1組のみ。売上の81.8%が深夜帯に集中</div>
<div class="slide-body"><div id="chart-10" style="width:1180px;height:370px"></div>
</div>
</div>

<!-- Slide 11: Wednesday Product Mix -->
<div class="slide" id="s11">
<div class="slide-header"><h2>水曜日（不調）の分析：商品別売上</h2><span class="pn">11 / 28</span></div>
<div class="msg-bar">コース・イベント利用がゼロ。ウイスキー系が42.7%を占めるが販売数が少ない</div>
<div class="slide-body">
<div class="two-col">
<div class="col-chart"><div id="chart-11" style="width:620px;height:340px"></div></div>
<div class="col-text">
<div class="sec-title">高単価商品（¥1,500以上）</div>
<table class="dt sm"><tr><td class="b">山崎12年</td><td class="r">¥3,500</td><td class="r" style="color:#64748B">1杯</td></tr>
<tr><td class="b">白州</td><td class="r">¥1,800</td><td class="r" style="color:#64748B">1杯</td></tr>
<tr><td class="b">Hojicha Negroni</td><td class="r">¥1,700</td><td class="r" style="color:#64748B">1杯</td></tr>
<tr><td class="b">グレンアラヒー8年</td><td class="r">¥1,600</td><td class="r" style="color:#64748B">1杯</td></tr>
<tr><td class="b">パナメラ・カルベネ・ソーヴィニョン</td><td class="r">¥1,600</td><td class="r" style="color:#64748B">1杯</td></tr></table>
</div></div>
</div>
</div>

<!-- Slide 12: Wednesday Summary -->
<div class="slide" id="s12">
<div class="slide-header"><h2>水曜日（不調）の分析：まとめ</h2><span class="pn">12 / 28</span></div>
<div class="msg-bar">水曜日の不調は根本的に来店客がいなかったことが原因。予約獲得が回復の鍵</div>
<div class="slide-body">
<div class="sec-title r">不調の主要因（3点）</div>
<ol class="nl r">
<li><strong>会計数の圧倒的不足（3件のみ）</strong>：プライムタイム（20-24時）に来店したのは1組4名のみ。集客そのものが成立していない</li>
<li><strong>コース・イベント利用の不在</strong>：金曜日はイベント利用+コースで大口売上を確保したが、水曜日はアラカルト注文のみ</li>
<li><strong>大口グループの不在</strong>：5名以上が1組5人（¥19,580）のみ。金曜は5名以上2組27人で¥181,170を記録</li>
</ol>
<div class="sec-title" style="margin-top:12px">来週に向けた課題</div>
<ul class="bl"><li>水曜日のグループ予約獲得（平日限定コースプラン、近隣企業への営業）</li><li>プライムタイム（20-24時）の集客強化（水曜限定ハッピーアワー、SNS告知）</li><li>コース提案の徹底（ウォークイン客にもショートコースを提案）</li></ul>
</div>
</div>

<!-- Slide 13: Friday Basic Numbers -->
<div class="slide" id="s13">
<div class="slide-header"><h2>金曜日（好調）の分析：基本数字</h2><span class="pn">13 / 28</span></div>
<div class="msg-bar">売上・客数・客単価すべてが4週平均を大幅に上回る。週唯一のプラス曜日</div>
<div class="slide-body">
<div class="kpi-grid">
<div class="kpi-card"><span class="kpi-label">売上</span><span class="kpi-value pos">¥231,520</span><span class="kpi-change pos">▲ 4週平均比 +65.4%</span></div>
<div class="kpi-card"><span class="kpi-label">客数</span><span class="kpi-value pos">35<small style="font-size:28px">人</small></span><span class="kpi-change pos">▲ 4週平均比 +41.1%</span></div>
<div class="kpi-card"><span class="kpi-label">客単価</span><span class="kpi-value pos">¥6,615</span><span class="kpi-change pos">▲ 4週平均比 +16.8%</span></div>
<div class="kpi-card"><span class="kpi-label">会計数</span><span class="kpi-value">6<small style="font-size:28px">件</small></span><span class="kpi-change neu">—</span></div>
</div>
<div id="chart-13" style="width:1180px;height:240px;margin-top:8px"></div>
</div>
</div>

<!-- Slide 14: Friday Group Size -->
<div class="slide" id="s14">
<div class="slide-header"><h2>金曜日（好調）の分析：グループ人数</h2><span class="pn">14 / 28</span></div>
<div class="msg-bar">5名以上グループ2組（計27人）が売上の78.3%を占める。大口グループ獲得が最大要因</div>
<div class="slide-body"><div id="chart-14" style="width:1180px;height:370px"></div>
</div>
</div>

<!-- Slide 15: Friday Time Bucket -->
<div class="slide" id="s15">
<div class="slide-header"><h2>金曜日（好調）の分析：時間帯別売上</h2><span class="pn">15 / 28</span></div>
<div class="msg-bar">19時台に20名の大口イベント利用（¥165,000）が来店し、売上の71.3%を占める</div>
<div class="slide-body"><div id="chart-15" style="width:1180px;height:370px"></div>
</div>
</div>

<!-- Slide 16: Friday Product Mix -->
<div class="slide" id="s16">
<div class="slide-header"><h2>金曜日（好調）の分析：商品別売上</h2><span class="pn">16 / 28</span></div>
<div class="msg-bar">イベント費用（¥55,000）が構成比48.2%。カクテル系も合計24.8%で注文活発</div>
<div class="slide-body">
<div class="two-col">
<div class="col-chart"><div id="chart-16" style="width:620px;height:340px"></div></div>
<div class="col-text">
<div class="sec-title g">高単価商品（¥1,500以上）</div>
<table class="dt sm"><tr><td class="b">イベント費用</td><td class="r">¥55,000</td><td class="r" style="color:#64748B">1件</td></tr>
<tr><td class="b">パ・フェネオン</td><td class="r">¥10,000</td><td class="r" style="color:#64748B">1本</td></tr>
<tr><td class="b">その他CLPコース</td><td class="r">¥5,500</td><td class="r" style="color:#64748B">1件</td></tr>
<tr><td class="b">Syndicate</td><td class="r">¥5,400</td><td class="r" style="color:#64748B">3杯</td></tr>
<tr><td class="b">ゴールデンタイムフィズ</td><td class="r">¥5,100</td><td class="r" style="color:#64748B">3杯</td></tr></table>
</div></div>
</div>
</div>

<!-- Slide 17: Friday Summary -->
<div class="slide" id="s17">
<div class="slide-header"><h2>金曜日（好調）の分析：まとめ</h2><span class="pn">17 / 28</span></div>
<div class="msg-bar">成功は『大口グループ × イベント利用 × 高単価カクテル』の組み合わせ。他曜日への横展開が最短ルート</div>
<div class="slide-body">
<div class="sec-title g">好調の主要因（3点）</div>
<ol class="nl g">
<li><strong>5名以上グループ2組で売上の78.3%</strong>：計27人・¥181,170。特に19時台の20名イベント利用（¥165,000）が圧倒的</li>
<li><strong>客数・客単価の両面でプラス</strong>：客数35人（4週平均比+41.1%）、客単価¥6,615（同+16.8%）。量と質の両立</li>
<li><strong>イベント＋カクテルの好商品ミックス</strong>：イベント48.2%+カクテル系24.8%で売上の73.0%を確保</li>
</ol>
<div class="sec-title" style="margin-top:12px">成功パターンの再現性</div>
<ul class="bl"><li>イベント・貸切予約の獲得を平日にも展開（法人向け営業強化）</li><li>グループ客への積極的なコース・飲み放題提案</li><li>「花金」需要を活かした金曜日の予約促進を継続</li></ul>
</div>
</div>

<!-- Slide 18: Day Comparison -->
<div class="slide" id="s18">
<div class="slide-header"><h2>曜日別評価まとめ</h2><span class="pn">18 / 28</span></div>
<div class="msg-bar">好調日と不調日の差はグループ客の有無に尽きる。平日全体の集客回復が最優先課題</div>
<div class="slide-body">
<div class="compare">
<div><div class="sec-title r">不調（水曜 1/21）</div>
<table class="dt sm"><tr><td class="b">売上</td><td>¥42,810（4週平均の30.1%）</td></tr><tr><td class="b">客数</td><td>11人（3件）</td></tr><tr><td class="b">客単価</td><td>¥3,892</td></tr><tr><td class="b">5名以上</td><td>1組5人（¥19,580）</td></tr><tr><td class="b">コース・イベント</td><td>なし</td></tr><tr><td class="b">時間帯</td><td>深夜帯に偏り（81.8%）</td></tr></table></div>
<div><div class="sec-title g">好調（金曜 1/23）</div>
<table class="dt sm"><tr><td class="b">売上</td><td>¥231,520（4週平均の165.4%）</td></tr><tr><td class="b">客数</td><td>35人（6件）</td></tr><tr><td class="b">客単価</td><td>¥6,615</td></tr><tr><td class="b">5名以上</td><td>2組27人（¥181,170）</td></tr><tr><td class="b">コース・イベント</td><td>イベント¥55,000+コース¥5,500</td></tr><tr><td class="b">時間帯</td><td>19時台+22-24時台に分散</td></tr></table></div>
</div>
<div style="display:flex;gap:14px;margin-top:10px">
<div style="flex:1;background:{BG};border-radius:10px;padding:10px 16px;text-align:center"><span class="big-label">プラス（金曜のみ）</span><br><span class="emphasis pos">+¥91,528</span></div>
<div style="flex:1;background:{BG};border-radius:10px;padding:10px 16px;text-align:center"><span class="big-label">マイナス（月火水木土日）</span><br><span class="emphasis neg">-¥290,423</span></div>
<div style="flex:1;background:{H};border-radius:10px;padding:10px 16px;text-align:center;color:#fff"><span style="font-size:18px;opacity:.7">差引（4週平均比）</span><br><span class="emphasis">-¥198,895</span></div>
</div>
</div>
</div>

<!-- Slide 19: Category Donut -->
<div class="slide" id="s19">
<div class="slide-header"><h2>カテゴリ別売上構成比</h2><span class="pn">19 / 28</span></div>
<div class="msg-bar">コース&amp;セットが23.0%で最大。イベント（+8.9pt）が急伸、ジャパニーズカクテル（-2.7pt）が減少</div>
<div class="slide-body">
<div class="two-col">
<div class="col-chart" style="display:flex;justify-content:center;align-items:center"><svg id="chart-19" width="440" height="400"></svg></div>
<div class="col-text">
<table class="dt sm">
<tr><th>カテゴリ</th><th class="r">売上</th><th class="r">構成比</th><th class="r">前週比</th></tr>
<tr><td class="b">コース&amp;セット</td><td class="r">¥140,000</td><td class="r">23.0%</td><td class="r pos">+6.3pt</td></tr>
<tr><td class="b">未設定</td><td class="r">¥84,000</td><td class="r">13.8%</td><td class="r pos">+6.7pt</td></tr>
<tr><td class="b">イベント</td><td class="r">¥55,000</td><td class="r">9.0%</td><td class="r pos">+8.9pt</td></tr>
<tr><td>ウイスキー</td><td class="r">¥41,100</td><td class="r">6.8%</td><td class="r pos">+2.0pt</td></tr>
<tr><td>その他</td><td class="r">¥38,800</td><td class="r">6.4%</td><td class="r pos">+0.8pt</td></tr>
<tr><td>ジャパニーズカクテル</td><td class="r">¥38,500</td><td class="r">6.3%</td><td class="r neg">-2.7pt</td></tr>
<tr><td>スナック</td><td class="r">¥35,000</td><td class="r">5.8%</td><td class="r">+0.0pt</td></tr>
<tr><td>オリジナルカクテル</td><td class="r">¥30,000</td><td class="r">4.9%</td><td class="r pos">+0.8pt</td></tr>
<tr><td>ワイン（グラス）</td><td class="r">¥29,600</td><td class="r">4.9%</td><td class="r neg">-1.5pt</td></tr>
<tr><td>アラカルト</td><td class="r">¥24,800</td><td class="r">4.1%</td><td class="r neg">-1.0pt</td></tr>
</table>
</div></div>
</div>
</div>

<!-- Slide 20: Strong Categories -->
<div class="slide" id="s20">
<div class="slide-header"><h2>好調カテゴリの深掘り</h2><span class="pn">20 / 28</span></div>
<div class="msg-bar">コース系（23.0%）とイベント（9.0%）で合計32.0%。イベントは1件のみで再現性が課題</div>
<div class="slide-body">
<div class="compare">
<div><div class="card" style="border-left:5px solid {P}"><div class="card-title g">コース&amp;セット（構成比23.0%、+6.3pt）</div>
<table class="dt sm" style="margin-top:6px"><tr><td>今週売上</td><td class="r b">¥140,000</td></tr><tr><td>前週売上</td><td class="r">¥136,133</td></tr><tr><td>変化</td><td class="r pos">+2.8%</td></tr><tr><td>構成比変化</td><td class="r pos">16.7% → 23.0%（+6.3pt）</td></tr></table>
<ul class="bl g" style="margin-top:6px"><li>その他CLPコース（¥110,000）とショートコース（¥30,000）が主力</li><li>グループ客のコース利用が定着し、安定した売上基盤を形成</li></ul>
</div></div>
<div><div class="card" style="border-left:5px solid {P}"><div class="card-title g">イベント（構成比9.0%、+8.9pt）</div>
<table class="dt sm" style="margin-top:6px"><tr><td>今週売上</td><td class="r b">¥55,000</td></tr><tr><td>前週売上</td><td class="r">¥815</td></tr><tr><td>変化</td><td class="r pos">大幅増</td></tr><tr><td>構成比変化</td><td class="r pos">0.1% → 9.0%（+8.9pt）</td></tr></table>
<ul class="bl g" style="margin-top:6px"><li>金曜日の20名グループによるイベント利用が発生</li><li>1件で¥55,000の高効率な売上獲得に成功</li></ul>
</div></div>
</div>
</div>
</div>

<!-- Slide 21: Product TOP10 -->
<div class="slide" id="s21">
<div class="slide-header"><h2>商品別売上上位10商品</h2><span class="pn">21 / 28</span></div>
<div class="msg-bar">上位3商品（コース+飲み放題+イベント）で売上の40.9%。シャーリーテンプル+176.9%が急成長</div>
<div class="slide-body">
<table class="dt sm">
<tr><th style="width:36px">順位</th><th>商品名</th><th class="r">今週売上</th><th class="r">構成比</th><th class="r">4週平均</th><th class="r">4週平均比</th></tr>
<tr class="best"><td class="b">1</td><td>その他CLPコース</td><td class="r b">¥110,000</td><td class="r">18.1%</td><td class="r">¥102,333</td><td class="r pos">+7.5%</td></tr>
<tr class="best"><td class="b">2</td><td>7000円飲み放題付（2時間制）</td><td class="r b">¥84,000</td><td class="r">13.8%</td><td class="r">¥74,500</td><td class="r pos">+12.8%</td></tr>
<tr class="best"><td class="b">3</td><td>イベント費用</td><td class="r b">¥55,000</td><td class="r">9.0%</td><td class="r">—</td><td class="r">—</td></tr>
<tr><td class="b">4</td><td>tablecharge</td><td class="r b">¥38,500</td><td class="r">6.3%</td><td class="r">¥44,875</td><td class="r neg">-14.2%</td></tr>
<tr><td class="b">5</td><td>ショートコース(食事のみ)+チャージ込み＋サ別</td><td class="r b">¥30,000</td><td class="r">4.9%</td><td class="r">—</td><td class="r">—</td></tr>
<tr><td class="b">6</td><td>ガージェリー</td><td class="r b">¥19,500</td><td class="r">3.2%</td><td class="r">¥22,425</td><td class="r neg">-13.0%</td></tr>
<tr><td class="b">7</td><td>ハウスハイボール</td><td class="r b">¥13,000</td><td class="r">2.1%</td><td class="r">¥14,625</td><td class="r neg">-11.1%</td></tr>
<tr><td class="b">8</td><td>シャーリーテンプル</td><td class="r b">¥11,700</td><td class="r">1.9%</td><td class="r">¥4,225</td><td class="r pos" style="font-weight:700">+176.9%</td></tr>
<tr><td class="b">9</td><td>チーズ盛り合わせ</td><td class="r b">¥11,000</td><td class="r">1.8%</td><td class="r">¥7,700</td><td class="r pos">+42.9%</td></tr>
<tr><td class="b">10</td><td>サングリア赤 1,800円</td><td class="r b">¥10,800</td><td class="r">1.8%</td><td class="r">¥6,300</td><td class="r pos">+71.4%</td></tr>
</table>
</div>
</div>

<!-- Slide 22: Product Share Changes -->
<div class="slide" id="s22">
<div class="slide-header"><h2>商品構成比の変化</h2><span class="pn">22 / 28</span></div>
<div class="msg-bar">飲み放題（+6.66pt）が大幅増。看板のジャパニーズカクテルが軒並み減少、訴求再強化が必要</div>
<div class="slide-body">
<div class="compare">
<div><div class="sec-title g">▲ 構成比増加上位5商品（前週比）</div>
<table class="dt sm"><tr><th>商品名</th><th class="r">今週</th><th class="r">前週</th><th class="r">変化</th></tr>
<tr><td>7000円飲み放題付（2時間制）</td><td class="r">13.81%</td><td class="r">7.15%</td><td class="r pos b">+6.66pt</td></tr>
<tr><td>デバルド・ロッソ</td><td class="r">1.78%</td><td class="r">0.31%</td><td class="r pos b">+1.47pt</td></tr>
<tr><td>その他CLPコース</td><td class="r">18.09%</td><td class="r">16.72%</td><td class="r pos b">+1.37pt</td></tr>
<tr><td>シャーリーテンプル</td><td class="r">1.92%</td><td class="r">0.66%</td><td class="r pos b">+1.26pt</td></tr>
<tr><td>tablecharge</td><td class="r">6.33%</td><td class="r">5.42%</td><td class="r pos b">+0.91pt</td></tr></table></div>
<div><div class="sec-title r">▼ 構成比減少上位5商品（前週比）</div>
<table class="dt sm"><tr><th>商品名</th><th class="r">今週</th><th class="r">前週</th><th class="r">変化</th></tr>
<tr><td>本わさびジンソニック</td><td class="r">1.48%</td><td class="r">3.22%</td><td class="r neg b">-1.74pt</td></tr>
<tr><td>クラシックカクテル</td><td class="r">0.51%</td><td class="r">1.94%</td><td class="r neg b">-1.43pt</td></tr>
<tr><td>禁断パスタ</td><td class="r">0.30%</td><td class="r">1.61%</td><td class="r neg b">-1.31pt</td></tr>
<tr><td>山葵と梨のスマッシュ</td><td class="r">1.13%</td><td class="r">2.05%</td><td class="r neg b">-0.92pt</td></tr>
<tr><td>梅酒</td><td class="r">0.20%</td><td class="r">1.07%</td><td class="r neg b">-0.87pt</td></tr></table></div>
</div>
</div>
</div>

<!-- Slide 23: Product Analysis Summary -->
<div class="slide" id="s23">
<div class="slide-header"><h2>商品分析まとめ</h2><span class="pn">23 / 28</span></div>
<div class="msg-bar">コース系が構成比36.8%で安定基盤。看板のジャパニーズカクテルが弱含みで差別化維持にはメニュー刷新が不可欠</div>
<div class="slide-body">
<div class="sec-title">商品戦略の2本柱</div>
<div class="compare">
<div><div class="card" style="border-left:5px solid {C}"><div class="card-title" style="color:{C}">コース（効率）</div>
<p style="font-size:18px;color:#64748B;margin-bottom:4px">CLPコース、飲み放題、ショートコース</p>
<div style="display:flex;gap:24px"><div><span class="big-label">今週売上</span><br><span class="big-num" style="font-size:36px">¥224,000</span></div><div><span class="big-label">構成比</span><br><span class="big-num" style="font-size:36px">36.8%</span></div></div>
<p style="font-size:18px;margin-top:4px">予約客の安定売上基盤</p></div></div>
<div><div class="card" style="border-left:5px solid {A}"><div class="card-title" style="color:{A}">看板商品（差別化）</div>
<p style="font-size:18px;color:#64748B;margin-bottom:4px">ジャパニーズカクテル、ウイスキー</p>
<div style="display:flex;gap:24px"><div><span class="big-label">今週売上</span><br><span class="big-num" style="font-size:36px">¥79,600</span></div><div><span class="big-label">構成比</span><br><span class="big-num" style="font-size:36px">13.1%</span></div></div>
<p style="font-size:18px;margin-top:4px">ブランド力・高単価の源泉</p></div></div>
</div>
<div style="text-align:center;font-size:22px;font-weight:700;color:{HD};margin:10px 0">2本柱合計：構成比 <span style="color:{C}">49.9%</span> / 売上 <span style="color:{C}">¥303,600</span></div>
</div>
</div>

<!-- Slide 24: Weekly Strengths -->
<div class="slide" id="s24">
<div class="slide-header"><h2>今週の総括：強み</h2><span class="pn">24 / 28</span></div>
<div class="msg-bar">金曜日の成功パターン確立、コース利用の定着、ノンアルコール需要の取り込みと、質的な強みは確実に積み上がっている</div>
<div class="slide-body">
<ol class="nl g">
<li><strong>金曜日が4週平均比+65.4%の大幅好調</strong>：売上¥231,520、客数35人（+41.1%）、客単価¥6,615（+16.8%）。5名以上グループ2組（27人）が売上の78.3%を生み出した</li>
<li><strong>コース&amp;セットの構成比拡大（23.0%、+6.3pt）</strong>：飲み放題付コース（¥84,000）とCLPコース（¥110,000）が堅調。予約・グループ客のコース利用が定着</li>
<li><strong>ノンアルコール・ワイン系商品の成長</strong>：シャーリーテンプル4週平均比+176.9%（¥4,225→¥11,700）、サングリア赤+71.4%（¥6,300→¥10,800）。多様な飲酒スタイルへの対応が機能</li>
</ol>
</div>
</div>

<!-- Slide 25: Weekly Challenges -->
<div class="slide" id="s25">
<div class="slide-header"><h2>今週の総括：課題</h2><span class="pn">25 / 28</span></div>
<div class="msg-bar">平日（特に火・水）の集客力低下が最大の課題。予約獲得の仕組みづくりが急務</div>
<div class="slide-body">
<ol class="nl r">
<li><strong>水曜日の壊滅的な客数減（4週平均の37.0%）</strong>：客数11人・会計3件。コース・イベント利用ゼロで売上¥42,810。4週平均比-¥99,620は週全体のマイナスの約35%</li>
<li><strong>木曜日の客単価大幅低下（4週平均比-28.3%）</strong>：客数14人は4週平均並みだが、客単価¥5,365（4週平均¥7,481）と-28.3%。客単価要因で-¥29,889</li>
<li><strong>ジャパニーズカクテルの構成比低下（-2.7pt）</strong>：本わさびジンソニック（-1.74pt）、山葵と梨のスマッシュ（-0.92pt）が揃って減少。看板カテゴリの弱体化はブランドの差別化力低下に直結</li>
</ol>
</div>
</div>

<!-- Slide 26: Action Plans 1 -->
<div class="slide" id="s26">
<div class="slide-header"><h2>施策一覧（1）：メニュー・集客</h2><span class="pn">26 / 28</span></div>
<div class="msg-bar">看板カテゴリの話題性創出と平日不調曜日の集客が最優先</div>
<div class="slide-body" style="padding:10px 30px">
<div class="compare" style="gap:16px">
<div><div class="sec-title o">メニュー開発</div>
<table class="at"><tr><th class="no">No</th><th>施策内容</th><th>狙い</th></tr>
<tr><td class="no">1</td><td>ジャパニーズカクテル新作発表（冬季限定）</td><td>話題性創出</td></tr>
<tr><td class="no">2</td><td>バレンタイン限定カクテルの開発</td><td>イベント需要</td></tr>
<tr><td class="no">3</td><td>ペアリングメニュー導入</td><td>客単価向上</td></tr>
<tr><td class="no">4</td><td>ウイスキーテイスティングセット常設化</td><td>高単価訴求</td></tr>
<tr><td class="no">5</td><td>深夜限定メニュー（23時以降）</td><td>深夜帯差別化</td></tr>
<tr><td class="no">6</td><td>平日限定カジュアルコース</td><td>予約促進</td></tr>
<tr><td class="no">7</td><td>ノンアルコールカクテル拡充</td><td>多様な顧客層</td></tr>
<tr><td class="no">8</td><td>季節限定ウイスキーフライト</td><td>来店動機</td></tr>
<tr><td class="no">9</td><td>おつまみ3種セット（¥1,500）</td><td>フード注文促進</td></tr>
<tr><td class="no">10</td><td>ハッピーアワー限定メニュー</td><td>早期来店促進</td></tr></table></div>
<div><div class="sec-title o">集客・マーケティング</div>
<table class="at"><tr><th class="no">No</th><th>施策内容</th><th>狙い</th></tr>
<tr><td class="no">1</td><td>火・水曜日限定ハッピーアワー</td><td>平日集客強化</td></tr>
<tr><td class="no">2</td><td>Instagram投稿強化</td><td>認知拡大</td></tr>
<tr><td class="no">3</td><td>木曜「プレ花金」プロモーション</td><td>木曜改善</td></tr>
<tr><td class="no">4</td><td>法人向け団体プラン営業</td><td>大口予約獲得</td></tr>
<tr><td class="no">5</td><td>Google口コミ投稿促進</td><td>検索順位向上</td></tr>
<tr><td class="no">6</td><td>SNS限定クーポン配布</td><td>新規獲得</td></tr>
<tr><td class="no">7</td><td>LINE公式でリピーター配信</td><td>再来店率向上</td></tr>
<tr><td class="no">8</td><td>金曜成功パターンの平日展開</td><td>イベント開拓</td></tr>
<tr><td class="no">9</td><td>予約サイトのコース訴求強化</td><td>コース利用維持</td></tr>
<tr><td class="no">10</td><td>深夜帯来店割引</td><td>深夜集客</td></tr></table></div>
</div>
</div>
</div>

<!-- Slide 27: Action Plans 2 -->
<div class="slide" id="s27">
<div class="slide-header"><h2>施策一覧（2）：顧客・運営</h2><span class="pn">27 / 28</span></div>
<div class="msg-bar">リピーター育成と予約管理の効率化で安定した売上基盤を構築</div>
<div class="slide-body" style="padding:10px 30px">
<div class="compare" style="gap:16px">
<div><div class="sec-title o">顧客育成・リピーター</div>
<table class="at"><tr><th class="no">No</th><th>施策内容</th><th>狙い</th></tr>
<tr><td class="no">1</td><td>リピーター限定特典（スタンプカード）</td><td>再来店促進</td></tr>
<tr><td class="no">2</td><td>早期予約割引</td><td>予約安定化</td></tr>
<tr><td class="no">3</td><td>グループ予約特典</td><td>団体客獲得</td></tr>
<tr><td class="no">4</td><td>常連客への好み記録・パーソナル提案</td><td>高単価顧客維持</td></tr>
<tr><td class="no">5</td><td>口コミ投稿で次回割引クーポン</td><td>口コミ促進</td></tr>
<tr><td class="no">6</td><td>紹介特典（友人紹介でドリンク1杯）</td><td>新規獲得</td></tr>
<tr><td class="no">7</td><td>誕生日・記念日サービス</td><td>特別感演出</td></tr>
<tr><td class="no">8</td><td>SNSフォロー特典</td><td>フォロワー増</td></tr>
<tr><td class="no">9</td><td>常連客向けウイスキー試飲会</td><td>ロイヤル育成</td></tr>
<tr><td class="no">10</td><td>VIP向け新メニュー先行体験</td><td>囲い込み</td></tr></table></div>
<div><div class="sec-title o">運営改善</div>
<table class="at"><tr><th class="no">No</th><th>施策内容</th><th>狙い</th></tr>
<tr><td class="no">1</td><td>時間帯別スタッフ配置の最適化</td><td>効率化</td></tr>
<tr><td class="no">2</td><td>低稼働曜日のシフト調整</td><td>コスト最適化</td></tr>
<tr><td class="no">3</td><td>予約管理の効率化</td><td>予約漏れ防止</td></tr>
<tr><td class="no">4</td><td>ピーク時間帯の回転率向上</td><td>売上最大化</td></tr>
<tr><td class="no">5</td><td>団体予約時のオペ整備</td><td>大口対応力</td></tr>
<tr><td class="no">6</td><td>在庫管理の最適化</td><td>機会損失防止</td></tr>
<tr><td class="no">7</td><td>週次データレビューの習慣化</td><td>PDCA確立</td></tr>
<tr><td class="no">8</td><td>予約率の目標設定と追跡</td><td>予約意識づけ</td></tr>
<tr><td class="no">9</td><td>フード提供スピード改善</td><td>満足度向上</td></tr>
<tr><td class="no">10</td><td>深夜帯オペレーション見直し</td><td>深夜安定化</td></tr></table></div>
</div>
</div>
</div>

<!-- Slide 28: Action Plans 3 -->
<div class="slide" id="s28">
<div class="slide-header"><h2>施策一覧（3）：スタッフ育成</h2><span class="pn">28 / 28</span></div>
<div class="msg-bar">看板商品の訴求力回復と客単価向上を支えるスタッフスキル強化</div>
<div class="slide-body" style="padding:10px 30px">
<div style="max-width:900px;margin:0 auto">
<div class="sec-title o">スタッフ育成・組織強化</div>
<table class="at" style="font-size:20px"><tr><th class="no" style="font-size:18px">No</th><th style="font-size:18px">施策内容</th><th style="font-size:18px">狙い</th></tr>
<tr><td class="no">1</td><td>ジャパニーズカクテル提案トレーニング</td><td>看板商品の訴求力回復</td></tr>
<tr><td class="no">2</td><td>追加注文促進の声がけ研修</td><td>客単価向上</td></tr>
<tr><td class="no">3</td><td>ウイスキー知識研修（産地・製法・テイスティング）</td><td>高単価商品の提案力強化</td></tr>
<tr><td class="no">4</td><td>接客ロールプレイング（グループ客対応）</td><td>大口顧客の満足度向上</td></tr>
<tr><td class="no">5</td><td>コース提案トーク術の確立</td><td>コース利用率の維持・向上</td></tr>
<tr><td class="no">6</td><td>会計時の口コミ依頼トーク確立</td><td>口コミ投稿増加</td></tr>
<tr><td class="no">7</td><td>SNS発信スキルの共有（撮影・投稿のコツ）</td><td>マーケティングの内製化</td></tr>
<tr><td class="no">8</td><td>深夜帯接客スキル強化</td><td>高単価時間帯の最大化</td></tr>
<tr><td class="no">9</td><td>新人育成プログラム整備</td><td>即戦力化</td></tr>
<tr><td class="no">10</td><td>月間MVP制度の導入（売上貢献・接客評価）</td><td>モチベーション向上</td></tr></table>
</div>
</div>
</div>

<script>
const COL = {{h:'{H}',p:'{P}',n:'{N}',a:'{A}',c:'{C}',g:'{G}',t:'{T}',hd:'{HD}'}};
function fmtY(v){{return'¥'+v.toLocaleString()}}

// Line chart helper
function drawLine(containerId,data,yFmt,avgVal){{
  const el=document.getElementById(containerId);if(!el)return;
  const w=parseInt(el.style.width),h=parseInt(el.style.height);
  const svg=d3.select('#'+containerId).append('svg').attr('width',w).attr('height',h);
  const m={{top:30,right:30,bottom:40,left:70}},iw=w-m.left-m.right,ih=h-m.top-m.bottom;
  const g=svg.append('g').attr('transform',`translate(${{m.left}},${{m.top}})`);
  const x=d3.scalePoint().domain(data.map(d=>d.l)).range([0,iw]).padding(.3);
  const yMax=d3.max(data,d=>d.v)*1.2;
  const y=d3.scaleLinear().domain([0,yMax]).range([ih,0]);
  g.selectAll('.gr').data(y.ticks(5)).join('line').attr('x1',0).attr('x2',iw).attr('y1',d=>y(d)).attr('y2',d=>y(d)).attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');
  g.append('g').attr('transform',`translate(0,${{ih}})`).call(d3.axisBottom(x)).selectAll('text').style('font-size','14px');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d=>yFmt(d))).selectAll('text').style('font-size','13px');
  if(avgVal){{g.append('line').attr('x1',0).attr('x2',iw).attr('y1',y(avgVal)).attr('y2',y(avgVal)).attr('stroke',COL.a).attr('stroke-dasharray','6,4').attr('stroke-width',1.5);
  g.append('text').attr('x',iw-4).attr('y',y(avgVal)-6).attr('text-anchor','end').attr('fill',COL.a).attr('font-size','13px').attr('font-weight','600').text('4週平均');}}
  const line=d3.line().x(d=>x(d.l)).y(d=>y(d.v)).curve(d3.curveMonotoneX);
  g.append('path').datum(data).attr('d',line).attr('fill','none').attr('stroke',COL.c).attr('stroke-width',2.5);
  g.selectAll('.dot').data(data).join('circle').attr('cx',d=>x(d.l)).attr('cy',d=>y(d.v)).attr('r',(d,i)=>i===data.length-1?8:4).attr('fill',(d,i)=>i===data.length-1?COL.c:'white').attr('stroke',COL.c).attr('stroke-width',2);
  const last=data[data.length-1];
  g.append('rect').attr('x',x(last.l)-50).attr('y',y(last.v)-34).attr('width',100).attr('height',24).attr('rx',4).attr('fill','#FFF7ED').attr('stroke',COL.a).attr('stroke-width',1.5);
  g.append('text').attr('x',x(last.l)).attr('y',y(last.v)-17).attr('text-anchor','middle').attr('fill',COL.hd).attr('font-size','15px').attr('font-weight','700').text(yFmt(last.v));
}}
drawLine('chart-3',[{{l:'W52',v:1058610}},{{l:'W01',v:473660}},{{l:'W02',v:534580}},{{l:'W03',v:815130}},{{l:'W04',v:628140}}],fmtY,(1058610+473660+534580+815130)/4);
drawLine('chart-4',[{{l:'W52',v:191}},{{l:'W01',v:99}},{{l:'W02',v:89}},{{l:'W03',v:132}},{{l:'W04',v:116}}],v=>v+'人',(191+99+89+132)/4);
drawLine('chart-5',[{{l:'W52',v:5542}},{{l:'W01',v:4784}},{{l:'W02',v:6007}},{{l:'W03',v:6175}},{{l:'W04',v:5415}}],fmtY,(5542+4784+6007+6175)/4);

// Slide 7: Day-of-week bar chart
(function(){{
  const el=document.getElementById('chart-7');if(!el)return;
  const w=1180,h=370;
  const svg=d3.select('#chart-7').append('svg').attr('width',w).attr('height',h);
  const m={{top:20,right:20,bottom:45,left:70}},iw=w-m.left-m.right,ih=h-m.top-m.bottom;
  const g=svg.append('g').attr('transform',`translate(${{m.left}},${{m.top}})`);
  const days=['月','火','水','木','金','土','日'],tw=[72820,40150,42810,75110,231520,117710,48020],av=[113817,100743,142430,110710,139992,150170,69173];
  const x0=d3.scaleBand().domain(days).range([0,iw]).padding(.25);
  const x1=d3.scaleBand().domain(['tw','av']).range([0,x0.bandwidth()]).padding(.08);
  const y=d3.scaleLinear().domain([0,250000]).range([ih,0]);
  g.selectAll('.gr').data(y.ticks(5)).join('line').attr('x1',0).attr('x2',iw).attr('y1',d=>y(d)).attr('y2',d=>y(d)).attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');
  g.append('g').attr('transform',`translate(0,${{ih}})`).call(d3.axisBottom(x0)).selectAll('text').style('font-size','16px').style('font-weight','700');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+(d/1000)+'k')).selectAll('text').style('font-size','13px');
  days.forEach((d,i)=>{{const gg=g.append('g').attr('transform',`translate(${{x0(d)}},0)`);
  const col=d==='金'?COL.p:d==='水'?COL.n:COL.c;
  gg.append('rect').attr('x',x1('tw')).attr('y',y(tw[i])).attr('width',x1.bandwidth()).attr('height',ih-y(tw[i])).attr('fill',col).attr('rx',3);
  gg.append('rect').attr('x',x1('av')).attr('y',y(av[i])).attr('width',x1.bandwidth()).attr('height',ih-y(av[i])).attr('fill',COL.g).attr('rx',3).attr('opacity',.5);}});
  // Callouts
  g.append('rect').attr('x',x0('金')+x0.bandwidth()/2-50).attr('y',y(tw[4])-30).attr('width',100).attr('height',22).attr('rx',4).attr('fill','#F0FDF4').attr('stroke',COL.p);
  g.append('text').attr('x',x0('金')+x0.bandwidth()/2).attr('y',y(tw[4])-14).attr('text-anchor','middle').attr('fill',COL.p).attr('font-size','14px').attr('font-weight','700').text('+¥91,528');
  g.append('rect').attr('x',x0('水')+x0.bandwidth()/2-50).attr('y',y(tw[2])-30).attr('width',100).attr('height',22).attr('rx',4).attr('fill','#FEF2F2').attr('stroke',COL.n);
  g.append('text').attr('x',x0('水')+x0.bandwidth()/2).attr('y',y(tw[2])-14).attr('text-anchor','middle').attr('fill',COL.n).attr('font-size','14px').attr('font-weight','700').text('-¥99,620');
  // Legend
  const lg=g.append('g').attr('transform',`translate(${{iw-200}},-5)`);
  lg.append('rect').attr('width',14).attr('height',14).attr('fill',COL.c).attr('rx',2);lg.append('text').attr('x',18).attr('y',12).attr('font-size','14px').text('今週');
  lg.append('rect').attr('x',60).attr('width',14).attr('height',14).attr('fill',COL.g).attr('opacity',.5).attr('rx',2);lg.append('text').attr('x',78).attr('y',12).attr('font-size','14px').text('4週平均');
}})();

// Comparison bar (Wed/Fri basic)
function drawCompH(containerId,labels,vals,avgs,col){{
  const el=document.getElementById(containerId);if(!el)return;
  const w=1180,h=240;
  const svg=d3.select('#'+containerId).append('svg').attr('width',w).attr('height',h);
  const m={{top:15,right:30,bottom:20,left:90}},iw=w-m.left-m.right,ih=h-m.top-m.bottom;
  const g=svg.append('g').attr('transform',`translate(${{m.left}},${{m.top}})`);
  const xMax=d3.max([...vals,...avgs])*1.2;
  const x=d3.scaleLinear().domain([0,xMax]).range([0,iw]);
  const y0=d3.scaleBand().domain(labels).range([0,ih]).padding(.3);
  const y1=d3.scaleBand().domain(['tw','av']).range([0,y0.bandwidth()]).padding(.1);
  g.append('g').call(d3.axisLeft(y0)).selectAll('text').style('font-size','16px');
  labels.forEach((l,i)=>{{const gg=g.append('g').attr('transform',`translate(0,${{y0(l)}})`);
  gg.append('rect').attr('y',y1('tw')).attr('width',x(vals[i])).attr('height',y1.bandwidth()).attr('fill',col).attr('rx',3);
  gg.append('text').attr('x',x(vals[i])+6).attr('y',y1('tw')+y1.bandwidth()/2+5).attr('font-size','14px').attr('fill',COL.hd).attr('font-weight','700').text(vals[i]>1000?fmtY(vals[i]):vals[i]);
  if(avgs[i]>0)gg.append('rect').attr('y',y1('av')).attr('width',x(avgs[i])).attr('height',y1.bandwidth()).attr('fill',COL.g).attr('opacity',.4).attr('rx',3);}});
}}
drawCompH('chart-8',['売上','客数','客単価'],[42810,11,3892],[142430,29.7,4764],COL.n);
drawCompH('chart-13',['売上','客数','客単価'],[231520,35,6615],[139992,24.8,5662],COL.p);

// Group size bar
function drawGroupH(containerId,data,col){{
  const el=document.getElementById(containerId);if(!el)return;
  const w=1180,h=370;
  const svg=d3.select('#'+containerId).append('svg').attr('width',w).attr('height',h);
  const m={{top:20,right:40,bottom:30,left:100}},iw=w-m.left-m.right,ih=h-m.top-m.bottom;
  const g=svg.append('g').attr('transform',`translate(${{m.left}},${{m.top}})`);
  const labels=data.map(d=>d.l);
  const xMax=d3.max(data,d=>d.s)*1.2||25000;
  const x=d3.scaleLinear().domain([0,xMax]).range([0,iw]);
  const y=d3.scaleBand().domain(labels).range([0,ih]).padding(.3);
  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-size','16px');
  data.forEach(d=>{{if(d.s>0)g.append('rect').attr('x',0).attr('y',y(d.l)).attr('width',x(d.s)).attr('height',y.bandwidth()).attr('fill',col).attr('rx',4);
  g.append('text').attr('x',d.s>0?x(d.s)+8:8).attr('y',y(d.l)+y.bandwidth()/2+5).attr('font-size','15px').attr('fill',COL.hd).attr('font-weight','600').text(`${{d.g}}組 / ${{d.c}}人 / ${{fmtY(d.s)}}`);}});
}}
drawGroupH('chart-9',[{{l:'1名',g:0,c:0,s:0}},{{l:'2名',g:1,c:2,s:15420}},{{l:'3-4名',g:1,c:4,s:7810}},{{l:'5名以上',g:1,c:5,s:19580}}],COL.n);
drawGroupH('chart-14',[{{l:'1名',g:1,c:1,s:6570}},{{l:'2名',g:2,c:4,s:21340}},{{l:'3-4名',g:1,c:3,s:22440}},{{l:'5名以上',g:2,c:27,s:181170}}],COL.p);

// Time bucket bar
function drawTimeH(containerId,data,col){{
  const el=document.getElementById(containerId);if(!el)return;
  const w=1180,h=370;
  const svg=d3.select('#'+containerId).append('svg').attr('width',w).attr('height',h);
  const m={{top:20,right:40,bottom:30,left:100}},iw=w-m.left-m.right,ih=h-m.top-m.bottom;
  const g=svg.append('g').attr('transform',`translate(${{m.left}},${{m.top}})`);
  const labels=data.map(d=>d.l);
  const xMax=d3.max(data,d=>d.s)*1.2||40000;
  const x=d3.scaleLinear().domain([0,xMax]).range([0,iw]);
  const y=d3.scaleBand().domain(labels).range([0,ih]).padding(.3);
  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-size','16px');
  const total=data.reduce((a,d)=>a+d.s,0);
  data.forEach(d=>{{if(d.s>0)g.append('rect').attr('x',0).attr('y',y(d.l)).attr('width',x(d.s)).attr('height',y.bandwidth()).attr('fill',col).attr('rx',4);
  g.append('text').attr('x',d.s>0?x(d.s)+8:8).attr('y',y(d.l)+y.bandwidth()/2+5).attr('font-size','15px').attr('fill',COL.hd).attr('font-weight','600').text(`${{fmtY(d.s)}} / ${{d.k}}件 / ${{d.c}}人`);}});
  const mx=data.reduce((a,b)=>a.s>b.s?a:b);
  if(mx.s>0&&total>0){{const pct=((mx.s/total)*100).toFixed(1);
  g.append('rect').attr('x',x(mx.s)/2-40).attr('y',y(mx.l)-26).attr('width',100).attr('height',22).attr('rx',4).attr('fill','#FFF7ED').attr('stroke',COL.a);
  g.append('text').attr('x',x(mx.s)/2+10).attr('y',y(mx.l)-10).attr('text-anchor','middle').attr('fill',COL.a).attr('font-size','13px').attr('font-weight','700').text('売上の'+pct+'%');}}
}}
drawTimeH('chart-10',[{{l:'18-20時',s:0,k:0,c:0}},{{l:'20-22時',s:7810,k:1,c:4}},{{l:'22-24時',s:0,k:0,c:0}},{{l:'24-26時',s:35000,k:2,c:7}}],COL.n);
drawTimeH('chart-15',[{{l:'18-20時',s:165000,k:1,c:20}},{{l:'20-22時',s:0,k:0,c:0}},{{l:'22-24時',s:59950,k:4,c:14}},{{l:'24-26時',s:6570,k:1,c:1}}],COL.p);

// Product horizontal bar
function drawProdH(containerId,data,col){{
  const el=document.getElementById(containerId);if(!el)return;
  const w=620,h=340;
  const svg=d3.select('#'+containerId).append('svg').attr('width',w).attr('height',h);
  const m={{top:10,right:120,bottom:20,left:180}},iw=w-m.left-m.right,ih=h-m.top-m.bottom;
  const g=svg.append('g').attr('transform',`translate(${{m.left}},${{m.top}})`);
  const labels=data.map(d=>d.n);
  const xMax=d3.max(data,d=>d.s)*1.15;
  const x=d3.scaleLinear().domain([0,xMax]).range([0,iw]);
  const y=d3.scaleBand().domain(labels).range([0,ih]).padding(.25);
  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-size','14px');
  data.forEach(d=>{{g.append('rect').attr('x',0).attr('y',y(d.n)).attr('width',x(d.s)).attr('height',y.bandwidth()).attr('fill',col).attr('rx',3).attr('opacity',.85);
  g.append('text').attr('x',x(d.s)+4).attr('y',y(d.n)+y.bandwidth()/2+5).attr('font-size','13px').attr('fill',COL.hd).attr('font-weight','600').text(`${{fmtY(d.s)}} (${{d.p}})`);}});
}}
drawProdH('chart-11',[{{n:'ジャパニーズウイスキー',s:5300,p:'23.3%'}},{{n:'ウイスキー',s:4400,p:'19.4%'}},{{n:'ビール',s:2600,p:'11.5%'}},{{n:'ワイン（グラス）',s:2400,p:'10.6%'}},{{n:'アラカルト',s:2300,p:'10.1%'}},{{n:'その他',s:5730,p:'25.1%'}}],COL.n);
drawProdH('chart-16',[{{n:'イベント',s:55000,p:'48.2%'}},{{n:'オリジナルカクテル',s:19400,p:'17.0%'}},{{n:'ワイン',s:10000,p:'8.8%'}},{{n:'ジャパニーズカクテル',s:8900,p:'7.8%'}},{{n:'スナック',s:7200,p:'6.3%'}},{{n:'その他',s:13520,p:'11.9%'}}],COL.p);

// Donut chart
(function(){{
  const svg=d3.select('#chart-19');
  const w=+svg.attr('width'),h=+svg.attr('height'),r=Math.min(w,h)/2-20;
  const g=svg.append('g').attr('transform',`translate(${{w/2}},${{h/2}})`);
  const data=[{{n:'コース&セット',v:140000,co:'#3B82F6'}},{{n:'未設定',v:84000,co:'#64748B'}},{{n:'イベント',v:55000,co:'#F97316'}},{{n:'ウイスキー',v:41100,co:'#8B5CF6'}},{{n:'その他',v:38800,co:'#94A3B8'}},{{n:'ジャパニーズカクテル',v:38500,co:'#06B6D4'}},{{n:'スナック',v:35000,co:'#10B981'}},{{n:'オリジナルカクテル',v:30000,co:'#EC4899'}},{{n:'ワイン（グラス）',v:29600,co:'#F43F5E'}},{{n:'アラカルト',v:24800,co:'#EAB308'}},{{n:'その他カテゴリ',v:111340,co:'#CBD5E1'}}];
  const pie=d3.pie().value(d=>d.v).sort(null);
  const arc=d3.arc().innerRadius(r*.5).outerRadius(r);
  const arcLabel=d3.arc().innerRadius(r*.75).outerRadius(r*.75);
  const total=d3.sum(data,d=>d.v);
  const arcs=g.selectAll('.arc').data(pie(data)).join('g');
  arcs.append('path').attr('d',arc).attr('fill',d=>d.data.co).attr('stroke','white').attr('stroke-width',2);
  arcs.filter(d=>d.data.v/total>.05).append('text').attr('transform',d=>`translate(${{arcLabel.centroid(d)}})`).attr('text-anchor','middle').attr('font-size','12px').attr('fill','white').attr('font-weight','600').text(d=>`${{(d.data.v/total*100).toFixed(1)}}%`);
  g.append('text').attr('text-anchor','middle').attr('y',-8).attr('font-size','16px').attr('fill',COL.hd).attr('font-weight','700').text('総売上');
  g.append('text').attr('text-anchor','middle').attr('y',18).attr('font-size','22px').attr('fill',COL.hd).attr('font-weight','800').text('¥628,140');
}})();
</script>
</body>
</html>"""

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML written: {OUTPUT_PATH}")
print(f"Size: {os.path.getsize(OUTPUT_PATH):,} bytes")
