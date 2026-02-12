#!/usr/bin/env python3
"""Generate the weekly report HTML slide deck for BAR FIVE Arrows 2026-W04."""

import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "20260119_20260125_BAR_FIVE_Arrows_週次報告資料.html")

# Color palette
HEADER = "#1E3A5F"
POSITIVE = "#22C55E"
NEGATIVE = "#EF4444"
ATTENTION = "#F97316"
CURRENT = "#3B82F6"
COMPARISON = "#94A3B8"
BG = "#F8FAFC"
TEXT = "#334155"
HEADING = "#1E293B"

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BAR FIVE Arrows 週次営業報告 2026-W04</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: #e2e8f0; color: {TEXT}; }}
.slide {{ width: 1280px; height: 720px; margin: 20px auto; background: {BG}; overflow: hidden; position: relative; page-break-after: always; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
.slide:last-child {{ page-break-after: avoid; }}
.slide-header {{ background: {HEADER}; color: white; padding: 16px 40px; font-size: 22px; font-weight: 700; display: flex; align-items: center; gap: 12px; height: 60px; }}
.slide-header .section-tag {{ background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: 500; }}
.slide-body {{ padding: 24px 40px; height: 636px; }}
.kpi-cards {{ display: flex; gap: 16px; justify-content: center; margin: 16px 0; }}
.kpi-card {{ background: white; border-radius: 12px; padding: 20px 24px; flex: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; border-top: 4px solid {CURRENT}; }}
.kpi-card.negative {{ border-top-color: {NEGATIVE}; }}
.kpi-card.positive {{ border-top-color: {POSITIVE}; }}
.kpi-label {{ font-size: 14px; color: {COMPARISON}; margin-bottom: 6px; font-weight: 600; }}
.kpi-value {{ font-size: 32px; font-weight: 800; color: {HEADING}; margin-bottom: 8px; }}
.kpi-change {{ font-size: 13px; display: flex; gap: 12px; justify-content: center; }}
.kpi-change span {{ padding: 2px 8px; border-radius: 4px; }}
.neg {{ color: {NEGATIVE}; background: #FEF2F2; }}
.pos {{ color: {POSITIVE}; background: #F0FDF4; }}
.message-box {{ background: linear-gradient(135deg, {HEADER}08, {HEADER}15); border-left: 4px solid {HEADER}; padding: 14px 20px; margin-top: 16px; font-size: 14px; line-height: 1.7; border-radius: 0 8px 8px 0; }}
.note-box {{ background: #FEF3C7; border-left: 4px solid {ATTENTION}; padding: 10px 16px; font-size: 13px; border-radius: 0 6px 6px 0; margin-top: 12px; }}
.chart-container {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.two-col {{ display: flex; gap: 24px; }}
.two-col > div {{ flex: 1; }}
.metric-cards {{ display: flex; gap: 16px; margin-bottom: 16px; }}
.metric-card {{ background: white; border-radius: 12px; padding: 16px 20px; flex: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
.metric-card .label {{ font-size: 13px; color: {COMPARISON}; font-weight: 600; margin-bottom: 4px; }}
.metric-card .value {{ font-size: 28px; font-weight: 800; color: {HEADING}; }}
.metric-card .sub {{ font-size: 12px; margin-top: 4px; }}
.gauge-card {{ background: white; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); flex: 1; }}
.gauge-card .gauge-label {{ font-size: 15px; color: {COMPARISON}; font-weight: 600; margin-bottom: 8px; }}
.gauge-card .gauge-value {{ font-size: 42px; font-weight: 900; }}
.gauge-card .gauge-eval {{ font-size: 14px; margin-top: 6px; padding: 4px 12px; border-radius: 20px; display: inline-block; }}
h3.section-title {{ font-size: 17px; color: {HEADING}; margin-bottom: 12px; font-weight: 700; }}
table.data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
table.data-table th {{ background: {HEADER}; color: white; padding: 8px 12px; text-align: left; font-weight: 600; }}
table.data-table td {{ padding: 7px 12px; border-bottom: 1px solid #E2E8F0; }}
table.data-table tr:nth-child(even) {{ background: #F8FAFC; }}
table.data-table tr:hover {{ background: #EFF6FF; }}
.compare-table {{ display: flex; gap: 0; }}
.compare-col {{ flex: 1; padding: 16px 20px; }}
.compare-col.wed {{ background: linear-gradient(135deg, #FEF2F2, #FFF5F5); border-radius: 12px 0 0 12px; }}
.compare-col.fri {{ background: linear-gradient(135deg, #F0FDF4, #F5FFF5); border-radius: 0 12px 12px 0; }}
.compare-col h4 {{ font-size: 16px; margin-bottom: 12px; font-weight: 700; }}
.bullet-list {{ list-style: none; padding: 0; }}
.bullet-list li {{ padding: 10px 14px; margin-bottom: 8px; background: white; border-radius: 8px; font-size: 13px; line-height: 1.6; box-shadow: 0 1px 4px rgba(0,0,0,0.04); display: flex; gap: 10px; }}
.bullet-list li .icon {{ font-size: 18px; flex-shrink: 0; }}
.bullet-list li .text {{ flex: 1; }}
.bullet-list li strong {{ color: {HEADING}; }}
.action-table {{ width: 100%; border-collapse: collapse; font-size: 11.5px; }}
.action-table th {{ background: {HEADER}; color: white; padding: 6px 8px; text-align: left; font-weight: 600; }}
.action-table td {{ padding: 5px 8px; border-bottom: 1px solid #E2E8F0; }}
.action-table tr:nth-child(even) {{ background: #F8FAFC; }}
.action-cat-title {{ font-size: 15px; font-weight: 700; color: {HEADING}; margin-bottom: 8px; padding: 6px 12px; background: linear-gradient(90deg, {HEADER}15, transparent); border-radius: 4px; }}
.pillar-card {{ background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 12px; }}
.pillar-card h4 {{ font-size: 14px; color: {HEADER}; font-weight: 700; margin-bottom: 8px; }}
.share-item {{ display: flex; align-items: center; gap: 8px; padding: 6px 10px; margin-bottom: 4px; border-radius: 6px; font-size: 13px; }}
.share-item.up {{ background: #F0FDF4; }}
.share-item.down {{ background: #FEF2F2; }}
.share-item .arrow {{ font-weight: 700; font-size: 15px; }}
.success-item {{ background: white; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border-left: 4px solid {POSITIVE}; }}
.challenge-item {{ background: white; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border-left: 4px solid {NEGATIVE}; }}
.success-item h4, .challenge-item h4 {{ font-size: 14px; font-weight: 700; margin-bottom: 4px; }}
.success-item p, .challenge-item p {{ font-size: 12px; line-height: 1.5; color: {TEXT}; }}
svg text {{ font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; }}
@media print {{
  body {{ background: white; }}
  .slide {{ box-shadow: none; margin: 0; }}
}}
</style>
</head>
<body>

<!-- Slide 1: Title -->
<div class="slide" id="slide1">
  <div style="background: linear-gradient(135deg, {HEADER}, #0F172A); width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center;">
    <div style="font-size: 14px; letter-spacing: 4px; opacity: 0.7; margin-bottom: 20px;">WEEKLY BUSINESS REPORT</div>
    <h1 style="font-size: 44px; font-weight: 900; margin-bottom: 16px; letter-spacing: 2px;">BAR FIVE Arrows</h1>
    <h2 style="font-size: 28px; font-weight: 400; margin-bottom: 32px;">週次営業報告</h2>
    <div style="width: 80px; height: 3px; background: {CURRENT}; margin-bottom: 32px;"></div>
    <div style="font-size: 20px; font-weight: 300;">2026年第4週</div>
    <div style="font-size: 18px; font-weight: 300; opacity: 0.8; margin-top: 8px;">1月19日（月）〜 1月25日（日）</div>
    <div style="position: absolute; bottom: 24px; font-size: 12px; opacity: 0.5;">20260119_20260125週次報告資料</div>
  </div>
</div>

<!-- Slide 2: Executive Summary -->
<div class="slide" id="slide2">
  <div class="slide-header"><span class="section-tag">第1部</span>エグゼクティブサマリー</div>
  <div class="slide-body">
    <div class="kpi-cards">
      <div class="kpi-card negative">
        <div class="kpi-label">売上</div>
        <div class="kpi-value">¥628,140</div>
        <div class="kpi-change"><span class="neg">▼ 前週比 -22.9%</span><span class="neg">▼ 前年比 -29.1%</span></div>
      </div>
      <div class="kpi-card negative">
        <div class="kpi-label">客数</div>
        <div class="kpi-value">116人</div>
        <div class="kpi-change"><span class="neg">▼ 前週比 -12.1%</span><span class="neg">▼ 前年比 -21.1%</span></div>
      </div>
      <div class="kpi-card negative">
        <div class="kpi-label">客単価</div>
        <div class="kpi-value">¥5,415</div>
        <div class="kpi-change"><span class="neg">▼ 前週比 -12.3%</span><span class="neg">▼ 前年比 -10.1%</span></div>
      </div>
      <div class="kpi-card negative">
        <div class="kpi-label">組数</div>
        <div class="kpi-value">36組</div>
        <div class="kpi-change"><span class="neg">▼ 前週比 -18.2%</span><span style="color:{COMPARISON}; font-size:12px;">前年比 —</span></div>
      </div>
    </div>
    <div style="display:flex; gap:12px; margin-top:16px;">
      <div style="flex:1; background:white; border-radius:10px; padding:14px 18px; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <h3 style="font-size:14px; color:{HEADING}; margin-bottom:8px;">特記事項</h3>
        <ul style="font-size:13px; line-height:1.8; padding-left:18px; color:{TEXT};">
          <li>売上・客数・客単価の3指標すべてが前週比・前年比ともにマイナス</li>
          <li style="color:{POSITIVE}; font-weight:600;">金曜日のみ好調：売上¥231,520（4週平均比+65.4%）、客数35人（同+41.1%）</li>
          <li style="color:{NEGATIVE}; font-weight:600;">水曜日が最大の課題：売上¥42,810（4週平均比30.1%）、客数11人（同37.0%）</li>
        </ul>
      </div>
    </div>
    <div class="message-box">
      <strong>「全指標が前週比・前年比で下落。金曜日の大幅好調（+¥91,528）でも水曜日の不振（-¥99,620）を補えず、平日全体の底上げが急務」</strong>
    </div>
  </div>
</div>

<!-- Slide 3: Sales Trend -->
<div class="slide" id="slide3">
  <div class="slide-header"><span class="section-tag">第1部</span>売上トレンド（直近5週間）</div>
  <div class="slide-body">
    <div class="two-col">
      <div style="flex:2;">
        <div class="chart-container" style="height:480px;">
          <svg id="chart-sales-trend" width="720" height="440"></svg>
        </div>
      </div>
      <div style="flex:1;">
        <div style="background:white; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:12px;">
          <h3 style="font-size:14px; color:{HEADING}; margin-bottom:8px;">前年同週比較</h3>
          <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;"><span>今週 (W04)</span><span style="font-weight:700;">¥628,140</span></div>
          <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;"><span>前年 (2025-W04)</span><span style="font-weight:700;">¥885,840</span></div>
          <div style="display:flex; justify-content:space-between; font-size:13px; color:{NEGATIVE}; font-weight:700; border-top:1px solid #E2E8F0; padding-top:6px;"><span>前年比</span><span>▼ -29.1%（-¥257,700）</span></div>
        </div>
        <div class="message-box" style="font-size:12px;">
          <strong>「W03で回復基調（¥815,130）に乗ったが、W04で¥628,140に再下落。前年同週比-29.1%と3割近い減少で、1月閑散期の影響が深刻」</strong>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Slide 4: Customer Trend -->
<div class="slide" id="slide4">
  <div class="slide-header"><span class="section-tag">第1部</span>客数トレンド（直近5週間）</div>
  <div class="slide-body">
    <div class="two-col">
      <div style="flex:2;">
        <div class="chart-container" style="height:480px;">
          <svg id="chart-cust-trend" width="720" height="440"></svg>
        </div>
      </div>
      <div style="flex:1;">
        <div style="background:white; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:12px;">
          <h3 style="font-size:14px; color:{HEADING}; margin-bottom:8px;">前年同週比較</h3>
          <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;"><span>今週 (W04)</span><span style="font-weight:700;">116人</span></div>
          <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;"><span>前年 (2025-W04)</span><span style="font-weight:700;">147人</span></div>
          <div style="display:flex; justify-content:space-between; font-size:13px; color:{NEGATIVE}; font-weight:700; border-top:1px solid #E2E8F0; padding-top:6px;"><span>前年比</span><span>▼ -21.1%（-31人）</span></div>
        </div>
        <div class="message-box" style="font-size:12px;">
          <strong>「W03の132人から16人減少。前年同週147人からは31人減（前年比-21.1%）。特に水曜日の客数11人（4週平均29.7人）と火曜日の6人（同18.7人）が全体を大きく押し下げた」</strong>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Slide 5: Unit Price Trend -->
<div class="slide" id="slide5">
  <div class="slide-header"><span class="section-tag">第1部</span>客単価トレンド（直近5週間）</div>
  <div class="slide-body">
    <div class="two-col">
      <div style="flex:2;">
        <div class="chart-container" style="height:480px;">
          <svg id="chart-price-trend" width="720" height="440"></svg>
        </div>
      </div>
      <div style="flex:1;">
        <div style="background:white; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:12px;">
          <h3 style="font-size:14px; color:{HEADING}; margin-bottom:8px;">前年同週比較</h3>
          <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;"><span>今週 (W04)</span><span style="font-weight:700;">¥5,415</span></div>
          <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;"><span>前年 (2025-W04)</span><span style="font-weight:700;">¥6,026</span></div>
          <div style="display:flex; justify-content:space-between; font-size:13px; color:{NEGATIVE}; font-weight:700; border-top:1px solid #E2E8F0; padding-top:6px;"><span>前年比</span><span>▼ -10.1%（-¥611）</span></div>
        </div>
        <div class="message-box" style="font-size:12px;">
          <strong>「W01〜W03にかけて¥4,784→¥6,175と上昇傾向だったが、W04で¥5,415に急落。前年比でも-10.1%と下回り、低単価利用客の増加が要因」</strong>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Slide 6: YoY Summary -->
<div class="slide" id="slide6">
  <div class="slide-header"><span class="section-tag">第1部</span>前年同週比サマリー</div>
  <div class="slide-body">
    <div class="kpi-cards" style="margin-top:24px;">
      <div class="gauge-card">
        <div class="gauge-label">売上</div>
        <div class="gauge-value" style="color:{NEGATIVE};">-29.1%</div>
        <div class="gauge-eval" style="background:#FEF2F2; color:{NEGATIVE};">▼▼ 大幅減</div>
        <div style="margin-top:12px; font-size:13px; color:{TEXT};">¥885,840 → ¥628,140<br>差額: <strong style="color:{NEGATIVE};">-¥257,700</strong></div>
      </div>
      <div class="gauge-card">
        <div class="gauge-label">客数</div>
        <div class="gauge-value" style="color:{NEGATIVE};">-21.1%</div>
        <div class="gauge-eval" style="background:#FEF2F2; color:{NEGATIVE};">▼▼ 大幅減</div>
        <div style="margin-top:12px; font-size:13px; color:{TEXT};">147人 → 116人<br>差額: <strong style="color:{NEGATIVE};">-31人</strong></div>
      </div>
      <div class="gauge-card">
        <div class="gauge-label">客単価</div>
        <div class="gauge-value" style="color:{NEGATIVE};">-10.1%</div>
        <div class="gauge-eval" style="background:#FEF2F2; color:{NEGATIVE};">▼ 減少</div>
        <div style="margin-top:12px; font-size:13px; color:{TEXT};">¥6,026 → ¥5,415<br>差額: <strong style="color:{NEGATIVE};">-¥611</strong></div>
      </div>
    </div>
    <div style="background:white; border-radius:12px; padding:16px 20px; margin-top:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
      <h3 style="font-size:14px; color:{HEADING}; margin-bottom:8px;">前年同週との主な違い</h3>
      <ul style="font-size:13px; line-height:1.8; padding-left:18px;">
        <li>前年W04は売上¥885,840に対し、今年は¥628,140と¥257,700の差</li>
        <li>客数は147人→116人で31人減。客単価は¥6,026→¥5,415で¥611の低下</li>
        <li>客数減（-21.1%）と客単価減（-10.1%）の複合要因で売上が約3割減少</li>
      </ul>
    </div>
    <div class="message-box">
      <strong>「前年同週比で3指標すべてが下落。売上-29.1%は客数減と客単価減の両面から生じており、集客力と単価向上の双方に課題がある」</strong>
    </div>
  </div>
</div>

<!-- Slide 7: Day-of-Week Overview -->
<div class="slide" id="slide7">
  <div class="slide-header"><span class="section-tag">第2部</span>曜日別概況</div>
  <div class="slide-body">
    <div class="chart-container" style="height:420px;">
      <svg id="chart-weekday" width="1180" height="380"></svg>
    </div>
    <div class="message-box" style="font-size:13px;">
      <strong>「7日中6日が4週平均を下回り、金曜日のみプラス。水曜日（-¥99,620）の不振が最大で、客数要因（-¥80,788）が主因。金曜日（+¥91,528）は客数・客単価の両面でプラスだが、全体を補えず」</strong>
    </div>
  </div>
</div>

<!-- Slide 8: Wednesday Basic Numbers -->
<div class="slide" id="slide8">
  <div class="slide-header"><span class="section-tag">第2部</span>水曜日（不調）の分析：基本数字</div>
  <div class="slide-body">
    <div class="metric-cards">
      <div class="metric-card" style="border-top:4px solid {NEGATIVE};">
        <div class="label">売上</div>
        <div class="value" style="color:{NEGATIVE};">¥42,810</div>
        <div class="sub neg">4週平均比 30.1%（-¥99,620）</div>
      </div>
      <div class="metric-card" style="border-top:4px solid {NEGATIVE};">
        <div class="label">客数</div>
        <div class="value" style="color:{NEGATIVE};">11人</div>
        <div class="sub neg">4週平均比 37.0%（-18.7人）</div>
      </div>
      <div class="metric-card" style="border-top:4px solid {NEGATIVE};">
        <div class="label">客単価</div>
        <div class="value" style="color:{NEGATIVE};">¥3,892</div>
        <div class="sub neg">4週平均比 81.7%（-¥872）</div>
      </div>
      <div class="metric-card" style="border-top:4px solid {COMPARISON};">
        <div class="label">会計数</div>
        <div class="value">3件</div>
        <div class="sub" style="color:{COMPARISON};">—</div>
      </div>
    </div>
    <div class="chart-container" style="height:300px;">
      <svg id="chart-wed-basic" width="1180" height="260"></svg>
    </div>
    <div class="message-box" style="font-size:13px;">
      <strong>「売上は4週平均のわずか30.1%。客数11人（4週平均比37.0%）と3分の1以下に激減したことが主因。客単価も¥3,892と低く、会計3件と営業として成立していない水準」</strong>
    </div>
  </div>
</div>

<!-- Slide 9: Wednesday Group Size -->
<div class="slide" id="slide9">
  <div class="slide-header"><span class="section-tag">第2部</span>水曜日（不調）の分析：グループ人数</div>
  <div class="slide-body">
    <div class="chart-container" style="height:400px;">
      <svg id="chart-wed-group" width="1180" height="360"></svg>
    </div>
    <div class="message-box" style="font-size:12px; margin-top:12px;">
      <strong>「3組のみの来店で、各サイズが1組ずつ。5名以上グループは1組5人（売上¥19,580）のみで、4週平均では5名以上が1組平均13人程度の来店があったことを考えると、大口グループの不在が売上差の大部分を説明する」</strong>
    </div>
  </div>
</div>

<!-- Slide 10: Wednesday Time Bucket -->
<div class="slide" id="slide10">
  <div class="slide-header"><span class="section-tag">第2部</span>水曜日（不調）の分析：時間帯別売上</div>
  <div class="slide-body">
    <div class="chart-container" style="height:400px;">
      <svg id="chart-wed-time" width="1180" height="360"></svg>
    </div>
    <div class="message-box" style="font-size:12px; margin-top:12px;">
      <strong>「プライムタイム（20-24時）に来店したのは20時台の1組4人（¥7,810）のみ。売上の81.8%（¥35,000）が深夜帯（24-26時）に集中しており、実質的な営業がほぼ成立していなかった」</strong>
    </div>
  </div>
</div>

<!-- Slide 11: Wednesday Product Mix -->
<div class="slide" id="slide11">
  <div class="slide-header"><span class="section-tag">第2部</span>水曜日（不調）の分析：商品別売上</div>
  <div class="slide-body">
    <div class="two-col">
      <div style="flex:1.3;">
        <div class="chart-container" style="height:340px;">
          <svg id="chart-wed-product" width="580" height="300"></svg>
        </div>
      </div>
      <div style="flex:1;">
        <div style="background:white; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <h3 style="font-size:14px; color:{HEADING}; margin-bottom:10px;">高単価商品（¥1,500以上）上位</h3>
          <table class="data-table">
            <tr><td>山崎12年</td><td style="text-align:right;">¥3,500</td><td style="text-align:right;color:{COMPARISON};">1杯</td></tr>
            <tr><td>白州</td><td style="text-align:right;">¥1,800</td><td style="text-align:right;color:{COMPARISON};">1杯</td></tr>
            <tr><td>Hojicha Negroni</td><td style="text-align:right;">¥1,700</td><td style="text-align:right;color:{COMPARISON};">1杯</td></tr>
            <tr><td>グレンアラヒー8年</td><td style="text-align:right;">¥1,600</td><td style="text-align:right;color:{COMPARISON};">1杯</td></tr>
            <tr><td>パナメラ・カルベネ・ソーヴィニョン</td><td style="text-align:right;">¥1,600</td><td style="text-align:right;color:{COMPARISON};">1杯</td></tr>
          </table>
        </div>
      </div>
    </div>
    <div class="message-box" style="font-size:12px; margin-top:12px;">
      <strong>「コース・イベント利用がゼロで、すべてアラカルト注文。ウイスキー系が42.7%を占めるが販売数が少なく、客単価を押し上げるまでに至らず。フード注文もアラカルト（10.1%）のみで低調」</strong>
    </div>
  </div>
</div>

<!-- Slide 12: Wednesday Summary -->
<div class="slide" id="slide12">
  <div class="slide-header"><span class="section-tag">第2部</span>水曜日（不調）の分析：まとめ</div>
  <div class="slide-body">
    <h3 class="section-title" style="color:{NEGATIVE};">不調の主要因（3点）</h3>
    <ul class="bullet-list">
      <li><div class="icon" style="color:{NEGATIVE};">1</div><div class="text"><strong>会計数の圧倒的不足（3件のみ）</strong><br>プライムタイム（20-24時）に来店したのは1組4名のみ。集客そのものが成立していない</div></li>
      <li><div class="icon" style="color:{NEGATIVE};">2</div><div class="text"><strong>コース・イベント利用の不在</strong><br>金曜日はイベント利用+コースで大口売上を確保したが、水曜日はアラカルト注文のみ。客単価向上の仕組みがなかった</div></li>
      <li><div class="icon" style="color:{NEGATIVE};">3</div><div class="text"><strong>大口グループの不在</strong><br>5名以上が1組5人（¥19,580）のみ。金曜は5名以上2組27人で¥181,170を記録しており、グループ客の有無が売上を決定的に左右</div></li>
    </ul>
    <h3 class="section-title" style="margin-top:12px;">来週に向けた課題</h3>
    <div style="display:flex; gap:8px;">
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">水曜日のグループ予約獲得（平日限定コースプラン、近隣企業への営業）</div>
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">プライムタイム（20-24時）の集客強化（水曜限定ハッピーアワー、SNS告知）</div>
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">コース提案の徹底（ウォークイン客にもショートコースを提案）</div>
    </div>
    <div class="message-box" style="margin-top:12px; font-size:13px;">
      <strong>「水曜日の不調は根本的に来店客がいなかったことが原因。個々の会計金額は悪くないため（平均¥14,270）、予約獲得とプライムタイムの集客が回復の鍵」</strong>
    </div>
  </div>
</div>

<!-- Slide 13: Friday Basic Numbers -->
<div class="slide" id="slide13">
  <div class="slide-header"><span class="section-tag">第2部</span>金曜日（好調）の分析：基本数字</div>
  <div class="slide-body">
    <div class="metric-cards">
      <div class="metric-card" style="border-top:4px solid {POSITIVE};">
        <div class="label">売上</div>
        <div class="value" style="color:{POSITIVE};">¥231,520</div>
        <div class="sub pos">4週平均比 +65.4%（+¥91,528）</div>
      </div>
      <div class="metric-card" style="border-top:4px solid {POSITIVE};">
        <div class="label">客数</div>
        <div class="value" style="color:{POSITIVE};">35人</div>
        <div class="sub pos">4週平均比 +41.1%（+10.2人）</div>
      </div>
      <div class="metric-card" style="border-top:4px solid {POSITIVE};">
        <div class="label">客単価</div>
        <div class="value" style="color:{POSITIVE};">¥6,615</div>
        <div class="sub pos">4週平均比 +16.8%（+¥953）</div>
      </div>
      <div class="metric-card" style="border-top:4px solid {COMPARISON};">
        <div class="label">会計数</div>
        <div class="value">6件</div>
        <div class="sub" style="color:{COMPARISON};">—</div>
      </div>
    </div>
    <div class="chart-container" style="height:300px;">
      <svg id="chart-fri-basic" width="1180" height="260"></svg>
    </div>
    <div class="message-box" style="font-size:13px;">
      <strong>「売上・客数・客単価の3指標すべてが4週平均を大幅に上回る。売上は4週平均比+65.4%で週唯一のプラス曜日。客数+41.1%と客単価+16.8%の両面で貢献」</strong>
    </div>
  </div>
</div>

<!-- Slide 14: Friday Group Size -->
<div class="slide" id="slide14">
  <div class="slide-header"><span class="section-tag">第2部</span>金曜日（好調）の分析：グループ人数</div>
  <div class="slide-body">
    <div class="chart-container" style="height:400px;">
      <svg id="chart-fri-group" width="1180" height="360"></svg>
    </div>
    <div class="message-box" style="font-size:12px; margin-top:12px;">
      <strong>「5名以上グループ2組（計27人）が売上¥181,170で全体の78.3%を占める。大口グループ獲得が金曜好調の最大要因。1組あたり単価も¥6,710と高水準で、コース・イベント利用が単価を押し上げた」</strong>
    </div>
  </div>
</div>

<!-- Slide 15: Friday Time Bucket -->
<div class="slide" id="slide15">
  <div class="slide-header"><span class="section-tag">第2部</span>金曜日（好調）の分析：時間帯別売上</div>
  <div class="slide-body">
    <div class="chart-container" style="height:400px;">
      <svg id="chart-fri-time" width="1180" height="360"></svg>
    </div>
    <div class="message-box" style="font-size:12px; margin-top:12px;">
      <strong>「19時台に20名の大口グループ（イベント利用、¥165,000）が来店し、売上の71.3%を占める。22-24時台にも4組14人が来店し¥59,950を記録。早い時間帯と深夜前の2つの山で売上を積み上げた」</strong>
    </div>
  </div>
</div>

<!-- Slide 16: Friday Product Mix -->
<div class="slide" id="slide16">
  <div class="slide-header"><span class="section-tag">第2部</span>金曜日（好調）の分析：商品別売上</div>
  <div class="slide-body">
    <div class="two-col">
      <div style="flex:1.3;">
        <div class="chart-container" style="height:340px;">
          <svg id="chart-fri-product" width="580" height="300"></svg>
        </div>
      </div>
      <div style="flex:1;">
        <div style="background:white; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <h3 style="font-size:14px; color:{HEADING}; margin-bottom:10px;">高単価商品（¥1,500以上）上位</h3>
          <table class="data-table">
            <tr><td>イベント費用</td><td style="text-align:right;">¥55,000</td><td style="text-align:right;color:{COMPARISON};">1件</td></tr>
            <tr><td>パ・フェネオン</td><td style="text-align:right;">¥10,000</td><td style="text-align:right;color:{COMPARISON};">1本</td></tr>
            <tr><td>その他CLPコース</td><td style="text-align:right;">¥5,500</td><td style="text-align:right;color:{COMPARISON};">1件</td></tr>
            <tr><td>Syndicate</td><td style="text-align:right;">¥5,400</td><td style="text-align:right;color:{COMPARISON};">3杯</td></tr>
            <tr><td>ゴールデンタイムフィズ</td><td style="text-align:right;">¥5,100</td><td style="text-align:right;color:{COMPARISON};">3杯</td></tr>
          </table>
        </div>
      </div>
    </div>
    <div class="message-box" style="font-size:12px; margin-top:12px;">
      <strong>「イベント費用（¥55,000）がカテゴリ最大で構成比48.2%。20名グループのイベント利用が売上を決定的に押し上げた。カクテル系（オリジナル+ジャパニーズ）も合計24.8%を占め、ドリンク注文も活発」</strong>
    </div>
  </div>
</div>

<!-- Slide 17: Friday Summary -->
<div class="slide" id="slide17">
  <div class="slide-header"><span class="section-tag">第2部</span>金曜日（好調）の分析：まとめ</div>
  <div class="slide-body">
    <h3 class="section-title" style="color:{POSITIVE};">好調の主要因（3点）</h3>
    <ul class="bullet-list">
      <li><div class="icon" style="color:{POSITIVE};">1</div><div class="text"><strong>5名以上グループ2組で売上の78.3%</strong><br>計27人・¥181,170。特に19時台の20名イベント利用（¥165,000）が圧倒的</div></li>
      <li><div class="icon" style="color:{POSITIVE};">2</div><div class="text"><strong>客数・客単価の両面でプラス</strong><br>客数35人（4週平均比+41.1%）、客単価¥6,615（同+16.8%）。量と質の両立を実現</div></li>
      <li><div class="icon" style="color:{POSITIVE};">3</div><div class="text"><strong>イベント＋カクテルの好商品ミックス</strong><br>イベント48.2%+カクテル系24.8%で売上の73.0%を確保</div></li>
    </ul>
    <h3 class="section-title" style="margin-top:12px;">成功パターンの再現性</h3>
    <div style="display:flex; gap:8px;">
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">イベント・貸切予約の獲得を平日にも展開（法人向け営業強化）</div>
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">グループ客への積極的なコース・飲み放題提案</div>
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">「花金」需要を活かした金曜日の予約促進を継続</div>
    </div>
    <div class="message-box" style="margin-top:12px; font-size:13px;">
      <strong>「金曜日の成功は『大口グループの獲得 × イベント利用 × 高単価カクテル』の組み合わせ。この成功パターンを他の曜日にも横展開することが、売上底上げの最短ルート」</strong>
    </div>
  </div>
</div>

<!-- Slide 18: Day Comparison -->
<div class="slide" id="slide18">
  <div class="slide-header"><span class="section-tag">第2部</span>曜日別評価まとめ</div>
  <div class="slide-body">
    <div class="compare-table">
      <div class="compare-col wed">
        <h4 style="color:{NEGATIVE};">不調（水曜 1/21）</h4>
        <table class="data-table" style="font-size:12px;">
          <tr><td style="font-weight:600;">売上</td><td>¥42,810（4週平均の30.1%）</td></tr>
          <tr><td style="font-weight:600;">客数</td><td>11人（3件）</td></tr>
          <tr><td style="font-weight:600;">客単価</td><td>¥3,892</td></tr>
          <tr><td style="font-weight:600;">5名以上</td><td>1組5人（¥19,580）</td></tr>
          <tr><td style="font-weight:600;">コース・イベント</td><td>なし</td></tr>
          <tr><td style="font-weight:600;">時間帯</td><td>深夜帯に偏り（81.8%）</td></tr>
        </table>
      </div>
      <div class="compare-col fri">
        <h4 style="color:{POSITIVE};">好調（金曜 1/23）</h4>
        <table class="data-table" style="font-size:12px;">
          <tr><td style="font-weight:600;">売上</td><td>¥231,520（4週平均の165.4%）</td></tr>
          <tr><td style="font-weight:600;">客数</td><td>35人（6件）</td></tr>
          <tr><td style="font-weight:600;">客単価</td><td>¥6,615</td></tr>
          <tr><td style="font-weight:600;">5名以上</td><td>2組27人（¥181,170）</td></tr>
          <tr><td style="font-weight:600;">コース・イベント</td><td>イベント¥55,000+コース¥5,500</td></tr>
          <tr><td style="font-weight:600;">時間帯</td><td>19時台+22-24時台に分散</td></tr>
        </table>
      </div>
    </div>
    <div style="display:flex; gap:12px; margin-top:16px;">
      <div style="flex:1; background:white; border-radius:10px; padding:12px 16px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <div style="font-size:12px; color:{COMPARISON};">プラス曜日（金曜のみ）</div>
        <div style="font-size:24px; font-weight:800; color:{POSITIVE};">+¥91,528</div>
      </div>
      <div style="flex:1; background:white; border-radius:10px; padding:12px 16px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <div style="font-size:12px; color:{COMPARISON};">マイナス曜日（月火水木土日）</div>
        <div style="font-size:24px; font-weight:800; color:{NEGATIVE};">-¥290,423</div>
      </div>
      <div style="flex:1; background:{HEADER}; border-radius:10px; padding:12px 16px; text-align:center; color:white;">
        <div style="font-size:12px; opacity:0.7;">差引（4週平均比）</div>
        <div style="font-size:24px; font-weight:800;">-¥198,895</div>
      </div>
    </div>
    <div class="message-box" style="margin-top:12px; font-size:13px;">
      <strong>「好調日と不調日の差はグループ客の有無に尽きる。金曜日の+¥91,528はマイナス合計（-¥290,423）の約3分の1に過ぎず、平日全体の集客回復が最優先課題」</strong>
    </div>
  </div>
</div>

<!-- Slide 19: Category Donut -->
<div class="slide" id="slide19">
  <div class="slide-header"><span class="section-tag">第3部</span>カテゴリ別売上構成比</div>
  <div class="slide-body">
    <div class="two-col">
      <div style="flex:1;">
        <div class="chart-container" style="height:460px; display:flex; justify-content:center; align-items:center;">
          <svg id="chart-category-donut" width="480" height="420"></svg>
        </div>
      </div>
      <div style="flex:1;">
        <h3 class="section-title">カテゴリ別詳細</h3>
        <table class="data-table" style="font-size:12px;">
          <thead><tr><th>カテゴリ</th><th style="text-align:right;">売上</th><th style="text-align:right;">構成比</th><th style="text-align:right;">前週比</th></tr></thead>
          <tbody>
            <tr><td>コース&amp;セット</td><td style="text-align:right;">¥140,000</td><td style="text-align:right;">23.0%</td><td style="text-align:right;color:{POSITIVE};">+6.3pt</td></tr>
            <tr><td>未設定</td><td style="text-align:right;">¥84,000</td><td style="text-align:right;">13.8%</td><td style="text-align:right;color:{POSITIVE};">+6.7pt</td></tr>
            <tr><td>イベント</td><td style="text-align:right;">¥55,000</td><td style="text-align:right;">9.0%</td><td style="text-align:right;color:{POSITIVE};">+8.9pt</td></tr>
            <tr><td>ウイスキー</td><td style="text-align:right;">¥41,100</td><td style="text-align:right;">6.8%</td><td style="text-align:right;color:{POSITIVE};">+2.0pt</td></tr>
            <tr><td>その他</td><td style="text-align:right;">¥38,800</td><td style="text-align:right;">6.4%</td><td style="text-align:right;color:{POSITIVE};">+0.8pt</td></tr>
            <tr><td>ジャパニーズカクテル</td><td style="text-align:right;">¥38,500</td><td style="text-align:right;">6.3%</td><td style="text-align:right;color:{NEGATIVE};">-2.7pt</td></tr>
            <tr><td>スナック</td><td style="text-align:right;">¥35,000</td><td style="text-align:right;">5.8%</td><td style="text-align:right;">+0.0pt</td></tr>
            <tr><td>オリジナルカクテル</td><td style="text-align:right;">¥30,000</td><td style="text-align:right;">4.9%</td><td style="text-align:right;color:{POSITIVE};">+0.8pt</td></tr>
            <tr><td>ワイン（グラス）</td><td style="text-align:right;">¥29,600</td><td style="text-align:right;">4.9%</td><td style="text-align:right;color:{NEGATIVE};">-1.5pt</td></tr>
            <tr><td>アラカルト</td><td style="text-align:right;">¥24,800</td><td style="text-align:right;">4.1%</td><td style="text-align:right;color:{NEGATIVE};">-1.0pt</td></tr>
            <tr><td>その他カテゴリ</td><td style="text-align:right;">¥111,340</td><td style="text-align:right;">18.0%</td><td style="text-align:right;">—</td></tr>
          </tbody>
        </table>
        <div class="message-box" style="margin-top:8px; font-size:11px;">
          <strong>「コース&amp;セットが23.0%で最大カテゴリ（前週比+6.3pt）。イベント（9.0%、+8.9pt）が金曜のイベント利用で急伸。一方、ジャパニーズカクテル（6.3%、-2.7pt）とワイン（グラス）（4.9%、-1.5pt）が減少」</strong>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Slide 20: Strong Categories -->
<div class="slide" id="slide20">
  <div class="slide-header"><span class="section-tag">第3部</span>好調カテゴリの深掘り</div>
  <div class="slide-body">
    <div class="two-col" style="gap:20px;">
      <div>
        <div class="pillar-card" style="border-top:4px solid {POSITIVE};">
          <h4>コース&amp;セット（構成比23.0%、+6.3pt）</h4>
          <table class="data-table" style="font-size:12px;">
            <tr><td>今週売上</td><td style="text-align:right; font-weight:700;">¥140,000</td></tr>
            <tr><td>前週売上</td><td style="text-align:right;">¥136,133</td></tr>
            <tr><td>変化</td><td style="text-align:right; color:{POSITIVE};">+2.8%</td></tr>
            <tr><td>構成比変化</td><td style="text-align:right; color:{POSITIVE};">16.7% → 23.0%（+6.3pt）</td></tr>
          </table>
          <ul style="font-size:12px; line-height:1.6; padding-left:16px; margin-top:8px;">
            <li>その他CLPコース（¥110,000）とショートコース（¥30,000）が主力</li>
            <li>グループ客のコース利用が定着し、安定した売上基盤を形成</li>
          </ul>
        </div>
      </div>
      <div>
        <div class="pillar-card" style="border-top:4px solid {POSITIVE};">
          <h4>イベント（構成比9.0%、+8.9pt）</h4>
          <table class="data-table" style="font-size:12px;">
            <tr><td>今週売上</td><td style="text-align:right; font-weight:700;">¥55,000</td></tr>
            <tr><td>前週売上</td><td style="text-align:right;">¥815</td></tr>
            <tr><td>変化</td><td style="text-align:right; color:{POSITIVE};">大幅増</td></tr>
            <tr><td>構成比変化</td><td style="text-align:right; color:{POSITIVE};">0.1% → 9.0%（+8.9pt）</td></tr>
          </table>
          <ul style="font-size:12px; line-height:1.6; padding-left:16px; margin-top:8px;">
            <li>金曜日の20名グループによるイベント利用が発生</li>
            <li>1件で¥55,000の高効率な売上獲得に成功</li>
          </ul>
        </div>
      </div>
    </div>
    <div class="message-box" style="margin-top:16px; font-size:13px;">
      <strong>「コース系（23.0%）とイベント（9.0%）で合計32.0%。予約・団体需要を着実に獲得できた週だが、イベントは1件のみで再現性が課題」</strong>
    </div>
  </div>
</div>

<!-- Slide 21: Product TOP10 -->
<div class="slide" id="slide21">
  <div class="slide-header"><span class="section-tag">第3部</span>商品別売上上位10商品</div>
  <div class="slide-body">
    <table class="data-table" style="font-size:12.5px;">
      <thead><tr><th style="width:40px;">順位</th><th>商品名</th><th style="text-align:right;">今週売上</th><th style="text-align:right;">構成比</th><th style="text-align:right;">4週平均</th><th style="text-align:right;">4週平均比</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>その他CLPコース</td><td style="text-align:right; font-weight:700;">¥110,000</td><td style="text-align:right;">18.1%</td><td style="text-align:right;">¥102,333</td><td style="text-align:right; color:{POSITIVE};">+7.5%</td></tr>
        <tr><td>2</td><td>7000円飲み放題付（2時間制）</td><td style="text-align:right; font-weight:700;">¥84,000</td><td style="text-align:right;">13.8%</td><td style="text-align:right;">¥74,500</td><td style="text-align:right; color:{POSITIVE};">+12.8%</td></tr>
        <tr><td>3</td><td>イベント費用</td><td style="text-align:right; font-weight:700;">¥55,000</td><td style="text-align:right;">9.0%</td><td style="text-align:right;">—</td><td style="text-align:right;">—</td></tr>
        <tr><td>4</td><td>tablecharge</td><td style="text-align:right; font-weight:700;">¥38,500</td><td style="text-align:right;">6.3%</td><td style="text-align:right;">¥44,875</td><td style="text-align:right; color:{NEGATIVE};">-14.2%</td></tr>
        <tr><td>5</td><td>ショートコース(食事のみ)+チャージ込み＋サ別</td><td style="text-align:right; font-weight:700;">¥30,000</td><td style="text-align:right;">4.9%</td><td style="text-align:right;">—</td><td style="text-align:right;">—</td></tr>
        <tr><td>6</td><td>ガージェリー</td><td style="text-align:right; font-weight:700;">¥19,500</td><td style="text-align:right;">3.2%</td><td style="text-align:right;">¥22,425</td><td style="text-align:right; color:{NEGATIVE};">-13.0%</td></tr>
        <tr><td>7</td><td>ハウスハイボール</td><td style="text-align:right; font-weight:700;">¥13,000</td><td style="text-align:right;">2.1%</td><td style="text-align:right;">¥14,625</td><td style="text-align:right; color:{NEGATIVE};">-11.1%</td></tr>
        <tr><td>8</td><td>シャーリーテンプル</td><td style="text-align:right; font-weight:700;">¥11,700</td><td style="text-align:right;">1.9%</td><td style="text-align:right;">¥4,225</td><td style="text-align:right; color:{POSITIVE}; font-weight:700;">+176.9%</td></tr>
        <tr><td>9</td><td>チーズ盛り合わせ</td><td style="text-align:right; font-weight:700;">¥11,000</td><td style="text-align:right;">1.8%</td><td style="text-align:right;">¥7,700</td><td style="text-align:right; color:{POSITIVE};">+42.9%</td></tr>
        <tr><td>10</td><td>サングリア赤 1,800円</td><td style="text-align:right; font-weight:700;">¥10,800</td><td style="text-align:right;">1.8%</td><td style="text-align:right;">¥6,300</td><td style="text-align:right; color:{POSITIVE};">+71.4%</td></tr>
      </tbody>
    </table>
    <div class="message-box" style="margin-top:16px; font-size:13px;">
      <strong>「上位3商品（コース+飲み放題+イベント）で売上の40.9%を占める。シャーリーテンプル（4週平均比+176.9%）やサングリア赤（同+71.4%）が急成長。一方でtablecharge（-14.2%）やガージェリー（-13.0%）は来店客数減を直接反映」</strong>
    </div>
  </div>
</div>

<!-- Slide 22: Product Share Changes -->
<div class="slide" id="slide22">
  <div class="slide-header"><span class="section-tag">第3部</span>商品構成比の変化</div>
  <div class="slide-body">
    <div class="two-col" style="gap:20px;">
      <div>
        <h3 class="section-title" style="color:{POSITIVE};">▲ 構成比増加上位5商品（前週比）</h3>
        <div class="share-item up"><span class="arrow" style="color:{POSITIVE};">▲</span><span style="flex:1;">7000円飲み放題付（2時間制）</span><span style="font-weight:700; color:{POSITIVE};">+6.66pt</span></div>
        <div class="share-item up"><span class="arrow" style="color:{POSITIVE};">▲</span><span style="flex:1;">デバルド・ロッソ</span><span style="font-weight:700; color:{POSITIVE};">+1.47pt</span></div>
        <div class="share-item up"><span class="arrow" style="color:{POSITIVE};">▲</span><span style="flex:1;">その他CLPコース</span><span style="font-weight:700; color:{POSITIVE};">+1.37pt</span></div>
        <div class="share-item up"><span class="arrow" style="color:{POSITIVE};">▲</span><span style="flex:1;">シャーリーテンプル</span><span style="font-weight:700; color:{POSITIVE};">+1.26pt</span></div>
        <div class="share-item up"><span class="arrow" style="color:{POSITIVE};">▲</span><span style="flex:1;">tablecharge</span><span style="font-weight:700; color:{POSITIVE};">+0.91pt</span></div>
      </div>
      <div>
        <h3 class="section-title" style="color:{NEGATIVE};">▼ 構成比減少上位5商品（前週比）</h3>
        <div class="share-item down"><span class="arrow" style="color:{NEGATIVE};">▼</span><span style="flex:1;">本わさびジンソニック</span><span style="font-weight:700; color:{NEGATIVE};">-1.74pt</span></div>
        <div class="share-item down"><span class="arrow" style="color:{NEGATIVE};">▼</span><span style="flex:1;">クラシックカクテル</span><span style="font-weight:700; color:{NEGATIVE};">-1.43pt</span></div>
        <div class="share-item down"><span class="arrow" style="color:{NEGATIVE};">▼</span><span style="flex:1;">禁断パスタ</span><span style="font-weight:700; color:{NEGATIVE};">-1.31pt</span></div>
        <div class="share-item down"><span class="arrow" style="color:{NEGATIVE};">▼</span><span style="flex:1;">山葵と梨のスマッシュ</span><span style="font-weight:700; color:{NEGATIVE};">-0.92pt</span></div>
        <div class="share-item down"><span class="arrow" style="color:{NEGATIVE};">▼</span><span style="flex:1;">梅酒</span><span style="font-weight:700; color:{NEGATIVE};">-0.87pt</span></div>
      </div>
    </div>
    <div class="message-box" style="margin-top:20px; font-size:13px;">
      <strong>「飲み放題（+6.66pt）とCLPコース（+1.37pt）が大幅増で、コース系への集中が進行。一方、看板カテゴリのジャパニーズカクテル（本わさびジンソニック-1.74pt、山葵と梨のスマッシュ-0.92pt）が軒並み減少しており、訴求の再強化が必要」</strong>
    </div>
  </div>
</div>

<!-- Slide 23: Product Analysis Summary -->
<div class="slide" id="slide23">
  <div class="slide-header"><span class="section-tag">第3部</span>商品分析まとめ</div>
  <div class="slide-body">
    <h3 class="section-title">商品戦略の2本柱</h3>
    <div class="two-col" style="gap:16px; margin-bottom:12px;">
      <div class="pillar-card" style="border-left:4px solid {CURRENT};">
        <h4 style="font-size:15px;">コース（効率）</h4>
        <div style="font-size:12px; color:{COMPARISON}; margin-bottom:6px;">CLPコース、飲み放題、ショートコース</div>
        <div style="display:flex; gap:16px;">
          <div><span style="font-size:11px; color:{COMPARISON};">今週売上</span><br><span style="font-size:22px; font-weight:800;">¥224,000</span></div>
          <div><span style="font-size:11px; color:{COMPARISON};">構成比</span><br><span style="font-size:22px; font-weight:800;">36.8%</span></div>
        </div>
        <div style="font-size:12px; margin-top:6px; color:{TEXT};">予約客の安定売上基盤</div>
      </div>
      <div class="pillar-card" style="border-left:4px solid {ATTENTION};">
        <h4 style="font-size:15px;">看板商品（差別化）</h4>
        <div style="font-size:12px; color:{COMPARISON}; margin-bottom:6px;">ジャパニーズカクテル、ウイスキー</div>
        <div style="display:flex; gap:16px;">
          <div><span style="font-size:11px; color:{COMPARISON};">今週売上</span><br><span style="font-size:22px; font-weight:800;">¥79,600</span></div>
          <div><span style="font-size:11px; color:{COMPARISON};">構成比</span><br><span style="font-size:22px; font-weight:800;">13.1%</span></div>
        </div>
        <div style="font-size:12px; margin-top:6px; color:{TEXT};">ブランド力・高単価の源泉</div>
      </div>
    </div>
    <div style="text-align:center; font-size:14px; font-weight:700; color:{HEADING}; margin:8px 0;">2本柱合計：構成比 <span style="color:{CURRENT};">49.9%</span> / 売上 <span style="color:{CURRENT};">¥303,600</span></div>
    <h3 class="section-title" style="margin-top:12px;">今後の方向性</h3>
    <div style="display:flex; gap:8px;">
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">コース予約の継続促進（効率性維持、平日への横展開）</div>
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">ジャパニーズカクテルの再訴求（季節限定メニュー投入、SNS映えビジュアルの発信）</div>
      <div style="flex:1; background:white; border-radius:8px; padding:10px 14px; font-size:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">ノンアルコールカクテルの成長（シャーリーテンプル+176.9%）を活かした多様な顧客対応</div>
    </div>
    <div class="message-box" style="margin-top:12px; font-size:13px;">
      <strong>「コース系が構成比36.8%で安定基盤を形成。ただし看板のジャパニーズカクテルが弱含みで、ブランド差別化の維持にはメニュー刷新と訴求強化が不可欠」</strong>
    </div>
  </div>
</div>

<!-- Slide 24: Weekly Strengths -->
<div class="slide" id="slide24">
  <div class="slide-header"><span class="section-tag">第4部</span>今週の総括：強み</div>
  <div class="slide-body">
    <div class="success-item">
      <h4 style="color:{POSITIVE};">1. 金曜日が4週平均比+65.4%の大幅好調</h4>
      <p>売上¥231,520、客数35人（4週平均比+41.1%）、客単価¥6,615（同+16.8%）<br>5名以上グループ2組（27人）の獲得が売上の78.3%を生み出した<br>イベント利用×コース×カクテルの好循環モデルが実現</p>
    </div>
    <div class="success-item">
      <h4 style="color:{POSITIVE};">2. コース&amp;セットの構成比拡大（23.0%、+6.3pt）</h4>
      <p>飲み放題付コース（¥84,000）とCLPコース（¥110,000）が堅調<br>予約・グループ客のコース利用が定着し、安定的な売上基盤を形成</p>
    </div>
    <div class="success-item">
      <h4 style="color:{POSITIVE};">3. ノンアルコール・ワイン系商品の成長</h4>
      <p>シャーリーテンプルが4週平均比+176.9%（¥4,225→¥11,700）<br>サングリア赤が同+71.4%（¥6,300→¥10,800）<br>多様な飲酒スタイルへの対応が機能し始めている</p>
    </div>
    <div class="message-box" style="margin-top:12px; font-size:13px;">
      <strong>「金曜日の成功パターン確立、コース利用の定着、ノンアルコール需要の取り込みと、質的な強みは確実に積み上がっている」</strong>
    </div>
  </div>
</div>

<!-- Slide 25: Weekly Challenges -->
<div class="slide" id="slide25">
  <div class="slide-header"><span class="section-tag">第4部</span>今週の総括：課題</div>
  <div class="slide-body">
    <div class="challenge-item">
      <h4 style="color:{NEGATIVE};">1. 水曜日の壊滅的な客数減（4週平均の37.0%）</h4>
      <p>客数11人・会計3件。プライムタイムは1組のみ<br>コース・イベント利用ゼロで売上¥42,810にとどまる<br>4週平均比-¥99,620は週全体のマイナスの約35%を占める</p>
    </div>
    <div class="challenge-item">
      <h4 style="color:{NEGATIVE};">2. 木曜日の客単価大幅低下（4週平均比-28.3%）</h4>
      <p>客数14人は4週平均並みだが、客単価¥5,365（4週平均¥7,481）と-28.3%<br>高単価商品（ウイスキー、コース）の注文が減り、客単価要因で-¥29,889のマイナス</p>
    </div>
    <div class="challenge-item">
      <h4 style="color:{NEGATIVE};">3. ジャパニーズカクテルの構成比低下（-2.7pt）</h4>
      <p>本わさびジンソニック（-1.74pt）、山葵と梨のスマッシュ（-0.92pt）が揃って減少<br>看板カテゴリの弱体化はブランドの差別化力低下に直結</p>
    </div>
    <div class="message-box" style="margin-top:12px; font-size:13px;">
      <strong>「平日（特に火・水）の集客力低下が最大の課題。客数が4週平均の3分の1以下の曜日が2日あり、予約獲得の仕組みづくりが急務。看板商品の再活性化も不可欠」</strong>
    </div>
  </div>
</div>

<!-- Slide 26: Action Plans 1 -->
<div class="slide" id="slide26">
  <div class="slide-header"><span class="section-tag">第5部</span>施策一覧（1）：メニュー・集客</div>
  <div class="slide-body" style="padding:16px 30px;">
    <div class="two-col" style="gap:16px;">
      <div>
        <div class="action-cat-title">メニュー開発</div>
        <table class="action-table">
          <thead><tr><th style="width:28px;">No.</th><th>施策内容</th><th>狙い</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>ジャパニーズカクテル新作発表（冬季限定：柚子・生姜系）</td><td>看板カテゴリの話題性創出</td></tr>
            <tr><td>2</td><td>バレンタイン限定カクテルの開発</td><td>2月イベント需要の獲得</td></tr>
            <tr><td>3</td><td>ペアリングメニュー導入（カクテル×フード）</td><td>客単価向上・滞在時間延長</td></tr>
            <tr><td>4</td><td>ウイスキーテイスティングセット（3種）常設化</td><td>高単価商品の訴求</td></tr>
            <tr><td>5</td><td>深夜限定メニュー（23時以降の軽食セット）</td><td>深夜帯の差別化</td></tr>
            <tr><td>6</td><td>2-3名向け平日限定カジュアルコース</td><td>平日少人数の予約促進</td></tr>
            <tr><td>7</td><td>ノンアルコールカクテルの拡充</td><td>多様な顧客層への対応</td></tr>
            <tr><td>8</td><td>季節限定ウイスキーフライト</td><td>来店動機づけ</td></tr>
            <tr><td>9</td><td>おつまみ3種セット（¥1,500）導入</td><td>フード注文の敷居を下げる</td></tr>
            <tr><td>10</td><td>ハッピーアワー限定メニュー（18-20時）</td><td>早い時間帯の来店促進</td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <div class="action-cat-title">集客・マーケティング</div>
        <table class="action-table">
          <thead><tr><th style="width:28px;">No.</th><th>施策内容</th><th>狙い</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>火・水曜日限定ハッピーアワー実施</td><td>平日不調曜日の集客強化</td></tr>
            <tr><td>2</td><td>Instagram投稿の強化（ジャパニーズカクテル中心）</td><td>看板商品の認知拡大</td></tr>
            <tr><td>3</td><td>木曜「プレ花金」プロモーション</td><td>木曜集客・客単価の改善</td></tr>
            <tr><td>4</td><td>法人・近隣企業向け団体プラン営業</td><td>大口予約の獲得</td></tr>
            <tr><td>5</td><td>Google口コミ投稿促進（QRコード設置、特典付き）</td><td>口コミ数増加・検索順位向上</td></tr>
            <tr><td>6</td><td>SNS限定クーポン配布</td><td>新規顧客獲得</td></tr>
            <tr><td>7</td><td>LINE公式アカウントでのリピーター向け配信</td><td>再来店率の向上</td></tr>
            <tr><td>8</td><td>金曜日イベント成功パターンの平日展開</td><td>貸切・イベント利用の開拓</td></tr>
            <tr><td>9</td><td>予約サイトでのコース訴求強化（写真・説明文更新）</td><td>コース利用率の維持</td></tr>
            <tr><td>10</td><td>深夜帯の来店割引（23時以降チャージ無料）</td><td>深夜帯の集客強化</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- Slide 27: Action Plans 2 -->
<div class="slide" id="slide27">
  <div class="slide-header"><span class="section-tag">第5部</span>施策一覧（2）：顧客・運営</div>
  <div class="slide-body" style="padding:16px 30px;">
    <div class="two-col" style="gap:16px;">
      <div>
        <div class="action-cat-title">顧客育成・リピーター</div>
        <table class="action-table">
          <thead><tr><th style="width:28px;">No.</th><th>施策内容</th><th>狙い</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>リピーター限定特典（スタンプカード）導入</td><td>再来店促進</td></tr>
            <tr><td>2</td><td>早期予約割引</td><td>予約数の安定化</td></tr>
            <tr><td>3</td><td>グループ予約特典（ウェルカムドリンクサービス）</td><td>団体客獲得</td></tr>
            <tr><td>4</td><td>常連客への好み記録・パーソナル提案</td><td>高単価顧客の維持</td></tr>
            <tr><td>5</td><td>口コミ投稿で次回割引クーポン配布</td><td>口コミ投稿促進</td></tr>
            <tr><td>6</td><td>紹介特典（友人紹介でドリンク1杯サービス）</td><td>新規客の獲得</td></tr>
            <tr><td>7</td><td>誕生日・記念日サービス（特別カクテルプレゼント）</td><td>特別感の演出</td></tr>
            <tr><td>8</td><td>SNSフォロー特典（初回ドリンク割引）</td><td>フォロワー増加</td></tr>
            <tr><td>9</td><td>常連客向けウイスキー試飲会（月1回）</td><td>ロイヤル顧客の育成</td></tr>
            <tr><td>10</td><td>VIP顧客向け新メニュー先行体験</td><td>ロイヤル顧客の囲い込み</td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <div class="action-cat-title">運営改善</div>
        <table class="action-table">
          <thead><tr><th style="width:28px;">No.</th><th>施策内容</th><th>狙い</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>時間帯別スタッフ配置の最適化</td><td>オペレーション効率化</td></tr>
            <tr><td>2</td><td>低稼働曜日（火・水）のシフト調整</td><td>コスト最適化</td></tr>
            <tr><td>3</td><td>予約管理の効率化（デジタル台帳の活用）</td><td>予約漏れ防止</td></tr>
            <tr><td>4</td><td>22-24時ピーク時間帯の回転率向上</td><td>売上最大化</td></tr>
            <tr><td>5</td><td>団体予約時のオペレーション整備</td><td>大口対応力の向上</td></tr>
            <tr><td>6</td><td>在庫管理の最適化（ウイスキー発注量見直し）</td><td>機会損失の防止</td></tr>
            <tr><td>7</td><td>週次データレビューの習慣化</td><td>PDCAサイクルの確立</td></tr>
            <tr><td>8</td><td>予約率の目標設定と追跡</td><td>予約獲得の意識づけ</td></tr>
            <tr><td>9</td><td>フードメニューの提供スピード改善</td><td>顧客満足度向上</td></tr>
            <tr><td>10</td><td>深夜帯（24時以降）のオペレーション見直し</td><td>深夜売上の安定化</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- Slide 28: Action Plans 3 -->
<div class="slide" id="slide28">
  <div class="slide-header"><span class="section-tag">第5部</span>施策一覧（3）：スタッフ育成</div>
  <div class="slide-body" style="padding:16px 30px;">
    <div style="max-width:800px; margin:0 auto;">
      <div class="action-cat-title">スタッフ育成・組織強化</div>
      <table class="action-table" style="font-size:13px;">
        <thead><tr><th style="width:36px;">No.</th><th>施策内容</th><th>狙い</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>ジャパニーズカクテル提案トレーニング</td><td>看板商品の訴求力回復</td></tr>
          <tr><td>2</td><td>追加注文促進の声がけ研修</td><td>客単価向上</td></tr>
          <tr><td>3</td><td>ウイスキー知識研修（産地・製法・テイスティング）</td><td>高単価商品の提案力強化</td></tr>
          <tr><td>4</td><td>接客ロールプレイング（グループ客対応）</td><td>大口顧客の満足度向上</td></tr>
          <tr><td>5</td><td>コース提案トーク術の確立</td><td>コース利用率の維持・向上</td></tr>
          <tr><td>6</td><td>会計時の口コミ依頼トーク確立</td><td>口コミ投稿増加</td></tr>
          <tr><td>7</td><td>SNS発信スキルの共有（撮影・投稿のコツ）</td><td>マーケティングの内製化</td></tr>
          <tr><td>8</td><td>深夜帯接客スキル強化</td><td>高単価時間帯の最大化</td></tr>
          <tr><td>9</td><td>新人育成プログラム整備</td><td>即戦力化</td></tr>
          <tr><td>10</td><td>月間MVP制度の導入（売上貢献・接客評価）</td><td>モチベーション向上</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
// ============================================================
// D3.js Chart Rendering
// ============================================================
const COLORS = {{
  header: '{HEADER}', positive: '{POSITIVE}', negative: '{NEGATIVE}',
  attention: '{ATTENTION}', current: '{CURRENT}', comparison: '{COMPARISON}',
  bg: '{BG}', text: '{TEXT}', heading: '{HEADING}'
}};

function formatYen(v) {{ return '¥' + v.toLocaleString(); }}

// --- Line chart helper ---
function drawLineChart(svgId, data, yLabel, yFormat, avgValue, avgLabel) {{
  const svg = d3.select('#' + svgId);
  const w = +svg.attr('width'), h = +svg.attr('height');
  const margin = {{top: 40, right: 40, bottom: 50, left: 80}};
  const iw = w - margin.left - margin.right, ih = h - margin.top - margin.bottom;
  const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

  const x = d3.scalePoint().domain(data.map(d => d.label)).range([0, iw]).padding(0.3);
  const yMax = d3.max(data, d => d.value) * 1.2;
  const y = d3.scaleLinear().domain([0, yMax]).range([ih, 0]);

  // Grid
  g.selectAll('.grid').data(y.ticks(5)).join('line').attr('class','grid')
    .attr('x1',0).attr('x2',iw).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');

  // Axes
  g.append('g').attr('transform', `translate(0,${{ih}})`).call(d3.axisBottom(x)).selectAll('text').style('font-size','13px');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d => yFormat(d))).selectAll('text').style('font-size','11px');

  // Average dashed line
  if (avgValue) {{
    g.append('line').attr('x1',0).attr('x2',iw).attr('y1',y(avgValue)).attr('y2',y(avgValue))
      .attr('stroke', COLORS.comparison).attr('stroke-dasharray','6,4').attr('stroke-width',1.5);
    g.append('text').attr('x', iw - 4).attr('y', y(avgValue) - 6).attr('text-anchor','end')
      .attr('fill', COLORS.comparison).attr('font-size','11px').text(avgLabel || '4週平均');
  }}

  // Line
  const line = d3.line().x(d => x(d.label)).y(d => y(d.value)).curve(d3.curveMonotoneX);
  g.append('path').datum(data).attr('d', line).attr('fill','none').attr('stroke', COLORS.current).attr('stroke-width', 2.5);

  // Dots
  g.selectAll('.dot').data(data).join('circle').attr('class','dot')
    .attr('cx', d => x(d.label)).attr('cy', d => y(d.value))
    .attr('r', (d, i) => i === data.length - 1 ? 8 : 4)
    .attr('fill', (d, i) => i === data.length - 1 ? COLORS.current : 'white')
    .attr('stroke', COLORS.current).attr('stroke-width', 2);

  // Callout on last point
  const last = data[data.length - 1];
  g.append('text').attr('x', x(last.label)).attr('y', y(last.value) - 16)
    .attr('text-anchor','middle').attr('fill', COLORS.heading).attr('font-size','14px').attr('font-weight','700')
    .text(yFormat(last.value));
}}

// Slide 3: Sales Trend
drawLineChart('chart-sales-trend',
  [{{label:'W52',value:1058610}},{{label:'W01',value:473660}},{{label:'W02',value:534580}},{{label:'W03',value:815130}},{{label:'W04',value:628140}}],
  '売上', formatYen, (1058610+473660+534580+815130)/4, '4週平均');

// Slide 4: Customer Trend
drawLineChart('chart-cust-trend',
  [{{label:'W52',value:191}},{{label:'W01',value:99}},{{label:'W02',value:89}},{{label:'W03',value:132}},{{label:'W04',value:116}}],
  '客数', v => v + '人', (191+99+89+132)/4, '4週平均');

// Slide 5: Unit Price Trend
drawLineChart('chart-price-trend',
  [{{label:'W52',value:5542}},{{label:'W01',value:4784}},{{label:'W02',value:6007}},{{label:'W03',value:6175}},{{label:'W04',value:5415}}],
  '客単価', formatYen, (5542+4784+6007+6175)/4, '4週平均');

// --- Slide 7: Day-of-week Grouped Bar ---
(function() {{
  const svg = d3.select('#chart-weekday');
  const w = +svg.attr('width'), h = +svg.attr('height');
  const margin = {{top: 30, right: 30, bottom: 50, left: 80}};
  const iw = w - margin.left - margin.right, ih = h - margin.top - margin.bottom;
  const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

  const days = ['月','火','水','木','金','土','日'];
  const thisWeek = [72820, 40150, 42810, 75110, 231520, 117710, 48020];
  const avg4w = [113817, 100743, 142430, 110710, 139992, 150170, 69173];
  const diffs = ['-¥40,997', '-¥60,593', '-¥99,620', '-¥35,600', '+¥91,528', '-¥32,460', '-¥21,153'];

  const x0 = d3.scaleBand().domain(days).range([0, iw]).padding(0.25);
  const x1 = d3.scaleBand().domain(['今週','4週平均']).range([0, x0.bandwidth()]).padding(0.08);
  const yMax = 250000;
  const y = d3.scaleLinear().domain([0, yMax]).range([ih, 0]);

  g.selectAll('.grid').data(y.ticks(5)).join('line').attr('class','grid')
    .attr('x1',0).attr('x2',iw).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');

  g.append('g').attr('transform', `translate(0,${{ih}})`).call(d3.axisBottom(x0)).selectAll('text').style('font-size','14px').style('font-weight','700');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d => '¥' + (d/1000) + 'k')).selectAll('text').style('font-size','11px');

  days.forEach((day, i) => {{
    const gDay = g.append('g').attr('transform', `translate(${{x0(day)}},0)`);
    const barColor = day === '金' ? COLORS.positive : day === '水' ? COLORS.negative : COLORS.current;
    // This week
    gDay.append('rect').attr('x', x1('今週')).attr('y', y(thisWeek[i])).attr('width', x1.bandwidth()).attr('height', ih - y(thisWeek[i])).attr('fill', barColor).attr('rx', 3);
    // 4wk avg
    gDay.append('rect').attr('x', x1('4週平均')).attr('y', y(avg4w[i])).attr('width', x1.bandwidth()).attr('height', ih - y(avg4w[i])).attr('fill', COLORS.comparison).attr('rx', 3).attr('opacity', 0.5);
  }});

  // Callouts for best/worst
  const friIdx = 4, wedIdx = 2;
  g.append('text').attr('x', x0('金') + x0.bandwidth()/2).attr('y', y(thisWeek[friIdx]) - 8)
    .attr('text-anchor','middle').attr('fill', COLORS.positive).attr('font-size','12px').attr('font-weight','700').text('+¥91,528');
  g.append('text').attr('x', x0('水') + x0.bandwidth()/2).attr('y', y(thisWeek[wedIdx]) - 8)
    .attr('text-anchor','middle').attr('fill', COLORS.negative).attr('font-size','12px').attr('font-weight','700').text('-¥99,620');

  // Legend
  const leg = g.append('g').attr('transform', `translate(${{iw - 200}}, -10)`);
  leg.append('rect').attr('x',0).attr('y',0).attr('width',14).attr('height',14).attr('fill', COLORS.current).attr('rx',2);
  leg.append('text').attr('x',18).attr('y',11).attr('font-size','12px').attr('fill', COLORS.text).text('今週');
  leg.append('rect').attr('x',60).attr('y',0).attr('width',14).attr('height',14).attr('fill', COLORS.comparison).attr('opacity',0.5).attr('rx',2);
  leg.append('text').attr('x',78).attr('y',11).attr('font-size','12px').attr('fill', COLORS.text).text('4週平均');
}})();

// --- Wednesday & Friday comparison bar charts ---
function drawCompBar(svgId, labels, thisW, avg4, color) {{
  const svg = d3.select('#' + svgId);
  const w = +svg.attr('width'), h = +svg.attr('height');
  const margin = {{top: 20, right: 30, bottom: 40, left: 90}};
  const iw = w - margin.left - margin.right, ih = h - margin.top - margin.bottom;
  const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

  const x = d3.scaleLinear().domain([0, d3.max([...thisW, ...avg4]) * 1.2]).range([0, iw]);
  const y0 = d3.scaleBand().domain(labels).range([0, ih]).padding(0.3);
  const y1 = d3.scaleBand().domain(['今週','4週平均']).range([0, y0.bandwidth()]).padding(0.1);

  g.append('g').call(d3.axisLeft(y0)).selectAll('text').style('font-size','12px');

  labels.forEach((label, i) => {{
    const gg = g.append('g').attr('transform', `translate(0,${{y0(label)}})`);
    gg.append('rect').attr('x',0).attr('y', y1('今週')).attr('width', x(thisW[i])).attr('height', y1.bandwidth()).attr('fill', color).attr('rx',3);
    gg.append('text').attr('x', x(thisW[i]) + 4).attr('y', y1('今週') + y1.bandwidth()/2 + 4).attr('font-size','11px').attr('fill', COLORS.heading).text(thisW[i] > 1000 ? formatYen(thisW[i]) : thisW[i]);
    if (avg4[i] > 0) {{
      gg.append('rect').attr('x',0).attr('y', y1('4週平均')).attr('width', x(avg4[i])).attr('height', y1.bandwidth()).attr('fill', COLORS.comparison).attr('opacity',0.4).attr('rx',3);
    }}
  }});
}}

// Slide 8: Wed basic
drawCompBar('chart-wed-basic', ['売上','客数','客単価'], [42810, 11, 3892], [142430, 29.7, 4764], COLORS.negative);

// Slide 13: Fri basic
drawCompBar('chart-fri-basic', ['売上','客数','客単価'], [231520, 35, 6615], [139992, 24.8, 5662], COLORS.positive);

// --- Group size bar chart ---
function drawGroupChart(svgId, data, color) {{
  const svg = d3.select('#' + svgId);
  const w = +svg.attr('width'), h = +svg.attr('height');
  const margin = {{top: 30, right: 40, bottom: 50, left: 100}};
  const iw = w - margin.left - margin.right, ih = h - margin.top - margin.bottom;
  const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

  const labels = data.map(d => d.label);
  const x = d3.scaleLinear().domain([0, d3.max(data, d => d.sales) * 1.2 || 25000]).range([0, iw]);
  const y = d3.scaleBand().domain(labels).range([0, ih]).padding(0.3);

  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-size','13px');
  g.selectAll('.grid').data(x.ticks(5)).join('line')
    .attr('x1',d=>x(d)).attr('x2',d=>x(d)).attr('y1',0).attr('y2',ih)
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');

  data.forEach(d => {{
    g.append('rect').attr('x',0).attr('y',y(d.label)).attr('width',x(d.sales)).attr('height',y.bandwidth()).attr('fill',color).attr('rx',4);
    g.append('text').attr('x', x(d.sales) + 6).attr('y', y(d.label) + y.bandwidth()/2 + 4)
      .attr('font-size','12px').attr('fill', COLORS.heading)
      .text(`${{d.groups}}組 / ${{d.customers}}人 / ${{formatYen(d.sales)}}`);
  }});

  // Title
  svg.append('text').attr('x', w/2).attr('y', 18).attr('text-anchor','middle')
    .attr('font-size','14px').attr('font-weight','700').attr('fill', COLORS.heading).text('グループ人数別');
}}

// Slide 9: Wed group
drawGroupChart('chart-wed-group', [
  {{label:'1名', groups:0, customers:0, sales:0}},
  {{label:'2名', groups:1, customers:2, sales:15420}},
  {{label:'3-4名', groups:1, customers:4, sales:7810}},
  {{label:'5名以上', groups:1, customers:5, sales:19580}}
], COLORS.negative);

// Slide 14: Fri group
drawGroupChart('chart-fri-group', [
  {{label:'1名', groups:1, customers:1, sales:6570}},
  {{label:'2名', groups:2, customers:4, sales:21340}},
  {{label:'3-4名', groups:1, customers:3, sales:22440}},
  {{label:'5名以上', groups:2, customers:27, sales:181170}}
], COLORS.positive);

// --- Time bucket bar chart ---
function drawTimeChart(svgId, data, color) {{
  const svg = d3.select('#' + svgId);
  const w = +svg.attr('width'), h = +svg.attr('height');
  const margin = {{top: 30, right: 40, bottom: 50, left: 100}};
  const iw = w - margin.left - margin.right, ih = h - margin.top - margin.bottom;
  const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

  const labels = data.map(d => d.label);
  const maxVal = d3.max(data, d => d.sales) * 1.2 || 40000;
  const x = d3.scaleLinear().domain([0, maxVal]).range([0, iw]);
  const y = d3.scaleBand().domain(labels).range([0, ih]).padding(0.3);

  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-size','13px');

  data.forEach(d => {{
    if (d.sales > 0) {{
      g.append('rect').attr('x',0).attr('y',y(d.label)).attr('width',x(d.sales)).attr('height',y.bandwidth()).attr('fill',color).attr('rx',4);
    }}
    g.append('text').attr('x', d.sales > 0 ? x(d.sales) + 6 : 6).attr('y', y(d.label) + y.bandwidth()/2 + 4)
      .attr('font-size','12px').attr('fill', COLORS.heading)
      .text(`${{formatYen(d.sales)}} / ${{d.checks}}件 / ${{d.customers}}人`);
  }});

  // Annotation
  const maxItem = data.reduce((a,b) => a.sales > b.sales ? a : b);
  if (maxItem.sales > 0) {{
    const pct = ((maxItem.sales / data.reduce((s,d)=>s+d.sales,0))*100).toFixed(1);
    g.append('text').attr('x', x(maxItem.sales)/2).attr('y', y(maxItem.label) - 6)
      .attr('text-anchor','middle').attr('font-size','11px').attr('fill', color).attr('font-weight','700')
      .text(`売上の${{pct}}%`);
  }}

  svg.append('text').attr('x', w/2).attr('y', 18).attr('text-anchor','middle')
    .attr('font-size','14px').attr('font-weight','700').attr('fill', COLORS.heading).text('時間帯別売上');
}}

// Slide 10: Wed time
drawTimeChart('chart-wed-time', [
  {{label:'18-20時', sales:0, checks:0, customers:0}},
  {{label:'20-22時', sales:7810, checks:1, customers:4}},
  {{label:'22-24時', sales:0, checks:0, customers:0}},
  {{label:'24-26時', sales:35000, checks:2, customers:7}}
], COLORS.negative);

// Slide 15: Fri time
drawTimeChart('chart-fri-time', [
  {{label:'18-20時', sales:165000, checks:1, customers:20}},
  {{label:'20-22時', sales:0, checks:0, customers:0}},
  {{label:'22-24時', sales:59950, checks:4, customers:14}},
  {{label:'24-26時', sales:6570, checks:1, customers:1}}
], COLORS.positive);

// --- Product horizontal bar chart ---
function drawProductChart(svgId, data, color) {{
  const svg = d3.select('#' + svgId);
  const w = +svg.attr('width'), h = +svg.attr('height');
  const margin = {{top: 20, right: 100, bottom: 30, left: 180}};
  const iw = w - margin.left - margin.right, ih = h - margin.top - margin.bottom;
  const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

  const labels = data.map(d => d.name);
  const maxVal = d3.max(data, d => d.sales) * 1.15;
  const x = d3.scaleLinear().domain([0, maxVal]).range([0, iw]);
  const y = d3.scaleBand().domain(labels).range([0, ih]).padding(0.25);

  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-size','11px');

  data.forEach(d => {{
    g.append('rect').attr('x',0).attr('y',y(d.name)).attr('width',x(d.sales)).attr('height',y.bandwidth()).attr('fill',color).attr('rx',3).attr('opacity',0.85);
    g.append('text').attr('x', x(d.sales) + 4).attr('y', y(d.name) + y.bandwidth()/2 + 4)
      .attr('font-size','10px').attr('fill', COLORS.heading).text(`${{formatYen(d.sales)}} (${{d.share}})`);
  }});
}}

// Slide 11: Wed products
drawProductChart('chart-wed-product', [
  {{name:'ジャパニーズウイスキー', sales:5300, share:'23.3%'}},
  {{name:'ウイスキー', sales:4400, share:'19.4%'}},
  {{name:'ビール', sales:2600, share:'11.5%'}},
  {{name:'ワイン（グラス）', sales:2400, share:'10.6%'}},
  {{name:'アラカルト', sales:2300, share:'10.1%'}},
  {{name:'その他', sales:5730, share:'25.1%'}}
], COLORS.negative);

// Slide 16: Fri products
drawProductChart('chart-fri-product', [
  {{name:'イベント', sales:55000, share:'48.2%'}},
  {{name:'オリジナルカクテル', sales:19400, share:'17.0%'}},
  {{name:'ワイン', sales:10000, share:'8.8%'}},
  {{name:'ジャパニーズカクテル', sales:8900, share:'7.8%'}},
  {{name:'スナック', sales:7200, share:'6.3%'}},
  {{name:'その他', sales:13520, share:'11.9%'}}
], COLORS.positive);

// --- Slide 19: Donut chart ---
(function() {{
  const svg = d3.select('#chart-category-donut');
  const w = +svg.attr('width'), h = +svg.attr('height');
  const radius = Math.min(w, h) / 2 - 20;
  const g = svg.append('g').attr('transform', `translate(${{w/2}},${{h/2}})`);

  const data = [
    {{name:'コース&セット', value:140000, color:'#3B82F6'}},
    {{name:'未設定', value:84000, color:'#64748B'}},
    {{name:'イベント', value:55000, color:'#F97316'}},
    {{name:'ウイスキー', value:41100, color:'#8B5CF6'}},
    {{name:'その他', value:38800, color:'#94A3B8'}},
    {{name:'ジャパニーズカクテル', value:38500, color:'#06B6D4'}},
    {{name:'スナック', value:35000, color:'#10B981'}},
    {{name:'オリジナルカクテル', value:30000, color:'#EC4899'}},
    {{name:'ワイン（グラス）', value:29600, color:'#F43F5E'}},
    {{name:'アラカルト', value:24800, color:'#EAB308'}},
    {{name:'その他カテゴリ', value:111340, color:'#CBD5E1'}}
  ];

  const pie = d3.pie().value(d => d.value).sort(null);
  const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius);
  const arcLabel = d3.arc().innerRadius(radius * 0.75).outerRadius(radius * 0.75);

  const arcs = g.selectAll('.arc').data(pie(data)).join('g').attr('class','arc');
  arcs.append('path').attr('d', arc).attr('fill', d => d.data.color).attr('stroke','white').attr('stroke-width',2);

  // Labels for slices > 5%
  const total = d3.sum(data, d => d.value);
  arcs.filter(d => d.data.value / total > 0.05).append('text')
    .attr('transform', d => `translate(${{arcLabel.centroid(d)}})`)
    .attr('text-anchor','middle').attr('font-size','10px').attr('fill','white').attr('font-weight','600')
    .text(d => `${{(d.data.value / total * 100).toFixed(1)}}%`);

  // Center text
  g.append('text').attr('text-anchor','middle').attr('y',-8).attr('font-size','14px').attr('fill', COLORS.heading).attr('font-weight','700').text('総売上');
  g.append('text').attr('text-anchor','middle').attr('y',16).attr('font-size','18px').attr('fill', COLORS.heading).attr('font-weight','800').text('¥628,140');
}})();

</script>
</body>
</html>"""

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML file written to: {OUTPUT_PATH}")
print(f"File size: {os.path.getsize(OUTPUT_PATH):,} bytes")
