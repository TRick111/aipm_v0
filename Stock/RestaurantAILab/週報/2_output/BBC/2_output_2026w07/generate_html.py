#!/usr/bin/env python3
"""Generate BBC W07 weekly report HTML slides."""

import os

TOTAL = 31
STORE = "別天地　銀座"
PERIOD = "2026年第7週（2/9〜2/15）"
WEEK = "2026-W07"

def pbar(n):
    return f'{(n-1)/(TOTAL-1)*100:.1f}%'

def header(title, n, section_tag=None):
    tag = f'<span class="section-tag">{section_tag}</span> ' if section_tag else ''
    return f'<div class="slide-header"><h2>{tag}{title}</h2><span class="pn">{n} / {TOTAL}</span><div class="progress-bar" style="width:{pbar(n)}"></div></div>'

def header_color(title, n, bg):
    return f'<div class="slide-header" style="background:{bg};"><h2>{title}</h2><span class="pn">{n} / {TOTAL}</span><div class="progress-bar" style="width:{pbar(n)}"></div></div>'

def msg(text):
    return f'<div class="msg-bar">{text}</div>'

CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Helvetica Neue','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif;background:#E2E8F0;color:#334155;font-size:20px;}
.slide{width:1280px;height:720px;margin:20px auto;background:#F8FAFC;position:relative;overflow:hidden;page-break-after:always;box-shadow:0 4px 24px rgba(0,0,0,0.12);}
.slide-header{background:#1E3A5F;color:#fff;padding:14px 40px;display:flex;align-items:center;justify-content:space-between;position:relative;min-height:56px;}
.slide-header h2{font-size:32px;font-weight:700;}
.slide-header .pn{font-size:16px;opacity:0.7;}
.progress-bar{position:absolute;bottom:0;left:0;height:3px;background:rgba(255,255,255,0.4);border-radius:0 2px 2px 0;}
.slide-header .section-tag{background:rgba(255,255,255,0.2);padding:4px 12px;border-radius:4px;font-size:14px;font-weight:500;}
.msg-bar{background:#FFF7ED;border-left:5px solid #F97316;padding:12px 40px;font-size:26px;font-weight:800;color:#1E293B;line-height:1.4;}
.slide-body{padding:18px 40px;overflow:hidden;}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:10px;}
.kpi-card{background:#fff;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.06);text-align:center;border-top:4px solid #3B82F6;}
.kpi-label{font-size:17px;color:#64748B;font-weight:600;display:block;}
.kpi-value{font-size:44px;font-weight:800;color:#1E293B;display:block;line-height:1.2;}
.kpi-change{font-size:22px;font-weight:700;display:block;margin-top:4px;}
.kpi-sub{font-size:18px;color:#64748B;display:block;margin-top:2px;}
.positive{color:#22C55E;}
.negative{color:#EF4444;}
.flex-row{display:flex;gap:20px;align-items:flex-start;}
.w50{width:50%;}.w60{width:60%;}.w40{width:40%;}.w33{width:33.33%;}.w67{width:66.67%;}
table.dt{width:100%;border-collapse:collapse;font-size:18px;}
table.dt th{background:#1E3A5F;color:#fff;padding:8px 12px;text-align:center;font-weight:700;font-size:17px;}
table.dt td{padding:8px 12px;border-bottom:1px solid #E2E8F0;text-align:center;font-size:18px;}
table.dt tr:nth-child(even){background:#F8FAFC;}
.hl-row{background:#FFF7ED !important;border-left:4px solid #F97316;}
.hl-row td{font-weight:800;color:#C2410C;}
table.action-table{width:100%;border-collapse:collapse;font-size:15px;}
table.action-table th{background:#1E3A5F;color:#fff;padding:7px 10px;text-align:center;font-weight:700;font-size:15px;}
table.action-table td{padding:7px 10px;border-bottom:1px solid #E2E8F0;vertical-align:top;font-size:15px;}
table.action-table tr:nth-child(even){background:#F8FAFC;}
.card{background:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}
.li-card{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:8px;}
.blockquote{border-left:3px solid #3B82F6;padding:10px 16px;margin:8px 0;background:#F8FAFC;font-size:17px;line-height:1.6;color:#334155;border-radius:0 6px 6px 0;}
.bq-date{font-weight:800;color:#1E293B;font-size:17px;margin-bottom:4px;}
.chart-comment{background:#F1F5F9;border-radius:8px;padding:14px;font-size:17px;line-height:1.7;color:#334155;}
.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:10px;}
.metric-card{background:#fff;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.06);text-align:center;}
.metric-label{font-size:17px;color:#64748B;font-weight:600;}
.metric-value{font-size:40px;font-weight:800;color:#1E293B;}
.sub-heading{font-size:22px;font-weight:800;color:#1E293B;margin-bottom:8px;}
.note-item{font-size:17px;padding:6px 0;border-bottom:1px solid #E2E8F0;line-height:1.5;}
@media print{body{background:#fff;margin:0;padding:0;}.slide{margin:0;box-shadow:none;page-break-after:always;page-break-inside:avoid;break-after:page;break-inside:avoid;}.slide:last-child{page-break-after:auto;}}
@media screen{.slide{margin:20px auto 40px auto;}}
"""

# ===== SLIDES =====
slides = []

# Slide 1: Title
slides.append(f'''<div class="slide" id="slide-1">
<div style="background:linear-gradient(135deg,#1E3A5F 0%,#0F172A 100%);width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:#fff;">
<div style="font-size:18px;letter-spacing:3px;opacity:0.7;margin-bottom:16px;">WEEKLY BUSINESS REPORT</div>
<div style="font-size:48px;font-weight:800;letter-spacing:2px;margin-bottom:8px;">{STORE}</div>
<div style="font-size:28px;font-weight:700;margin-bottom:24px;">週次営業報告</div>
<div style="width:120px;height:3px;background:#3B82F6;margin-bottom:24px;border-radius:2px;"></div>
<div style="font-size:24px;font-weight:600;opacity:0.9;">{PERIOD}</div>
<div style="font-size:18px;margin-top:12px;opacity:0.6;">{WEEK}</div>
</div>
</div>''')

# Slide 2: KPI Highlight
slides.append(f'''{header("今週のハイライト", 2, "第1部")}
{msg("前週比+65.6%と力強く回復したが、金曜日の客数半減と4営業日の4週平均割れが課題")}
<div class="slide-body">
<div class="kpi-grid">
<div class="kpi-card"><span class="kpi-label">売上</span><span class="kpi-value">¥595,960</span><span class="kpi-change positive">▲ 前週比 +65.6%</span><span class="kpi-sub">前月平均比 -1.2%</span></div>
<div class="kpi-card"><span class="kpi-label">客数</span><span class="kpi-value">62<span style="font-size:24px;">人</span></span><span class="kpi-change positive">▲ 前週比 +100.0%</span><span class="kpi-sub">前月平均比 ±0.0%</span></div>
<div class="kpi-card"><span class="kpi-label">客単価</span><span class="kpi-value">¥9,612</span><span class="kpi-change negative">▼ 前週比 -17.2%</span><span class="kpi-sub">前月平均比 -0.4%</span></div>
<div class="kpi-card"><span class="kpi-label">組数</span><span class="kpi-value">21<span style="font-size:24px;">組</span></span><span class="kpi-change positive">▲ 前週比 +162.5%</span><span class="kpi-sub">&nbsp;</span></div>
</div>
<div style="display:flex;gap:12px;margin-top:14px;">
<div class="li-card" style="flex:1;">📈 火曜日が4週平均の<strong>2.15倍</strong>と突出した好調</div>
<div class="li-card" style="flex:1;">📉 金曜日は客数が4週平均の<strong>53.6%</strong>に半減</div>
<div class="li-card" style="flex:1;">📅 水曜日は祝日（建国記念の日）で<strong>3人</strong>のみ</div>
</div>
</div>''')

# Slide 3: Sales Trend
slides.append(f'''{header("売上推移", 3)}
{msg("W06の¥36万から¥60万に急回復。ただしW04-W05の¥88万〜¥95万水準には遠い")}
<div class="slide-body">
<div class="flex-row" style="height:480px;">
<div class="w67"><svg id="chart-sales" width="760" height="460"></svg></div>
<div class="w33" style="display:flex;flex-direction:column;justify-content:center;gap:12px;">
<div class="chart-comment"><strong>トレンド</strong><br>W06の大幅落ち込みから急回復。前週比+65.6%。ただし1月の週平均¥603,483とほぼ同水準に留まる。</div>
</div>
</div>
</div>''')

# Slide 4: Customer Count Trend
slides.append(f'''{header("客数推移", 4)}
{msg("客数はW06の31人から62人へ倍増。1月平均（62人）と同水準に復帰")}
<div class="slide-body">
<div class="flex-row" style="height:480px;">
<div class="w67"><svg id="chart-customers" width="760" height="460"></svg></div>
<div class="w33" style="display:flex;flex-direction:column;justify-content:center;gap:12px;">
<div class="chart-comment"><strong>トレンド</strong><br>客数62人は1月平均と完全一致。W06の31人は特異的な低水準だったことが確認できる。</div>
</div>
</div>
</div>''')

# Slide 5: Unit Price Trend
slides.append(f'''{header("客単価推移", 5)}
{msg("客単価¥9,612は1月平均（¥9,650）並み。W06の高単価（¥11,609）からの正常化")}
<div class="slide-body">
<div class="flex-row" style="height:480px;">
<div class="w67"><svg id="chart-price" width="760" height="460"></svg></div>
<div class="w33" style="display:flex;flex-direction:column;justify-content:center;gap:12px;">
<div class="chart-comment"><strong>トレンド</strong><br>W06は客数31人（少数精鋭）で高単価。W07は客数倍増に伴い単価が正常化。</div>
</div>
</div>
</div>''')

# Slide 6: Month Comparison
slides.append(f'''{header("前月平均比サマリー", 6)}
{msg("売上・客数・客単価の3指標すべてが1月平均とほぼ同水準。安定基調への回復")}
<div class="slide-body">
<div class="metric-grid" style="margin-top:20px;">
<div class="metric-card" style="border-top:4px solid #3B82F6;"><div class="metric-label">売上</div><div class="metric-value" style="color:#3B82F6;">¥595,960</div><div style="font-size:18px;color:#64748B;margin-top:4px;">1月平均 ¥603,483</div><div style="font-size:22px;font-weight:700;color:#EF4444;margin-top:4px;">▼ -1.2%</div></div>
<div class="metric-card" style="border-top:4px solid #3B82F6;"><div class="metric-label">客数</div><div class="metric-value" style="color:#3B82F6;">62<span style="font-size:22px;">人</span></div><div style="font-size:18px;color:#64748B;margin-top:4px;">1月平均 62人</div><div style="font-size:22px;font-weight:700;color:#64748B;margin-top:4px;">±0.0%</div></div>
<div class="metric-card" style="border-top:4px solid #3B82F6;"><div class="metric-label">客単価</div><div class="metric-value" style="color:#3B82F6;">¥9,612</div><div style="font-size:18px;color:#64748B;margin-top:4px;">1月平均 ¥9,650</div><div style="font-size:22px;font-weight:700;color:#EF4444;margin-top:4px;">▼ -0.4%</div></div>
</div>
<div style="margin-top:24px;padding:16px 20px;background:#F0FDF4;border-radius:12px;border-left:5px solid #22C55E;">
<div style="font-size:20px;font-weight:700;color:#166534;">📊 総合評価</div>
<div style="font-size:18px;color:#334155;margin-top:6px;line-height:1.6;">W06の異常低水準から完全に回復し、1月の安定水準に復帰。3指標がすべて±1.2%以内に収まり、基礎体力は維持されている。</div>
</div>
</div>''')

# Slide 7: Weekday Overview
slides.append(f'''{header("曜日別概況", 7, "第2部")}
{msg("5営業日中4日が4週平均割れ。火曜日のみ+¥122,462の大幅プラスで、金曜日の-¥122,700を相殺")}
<div class="slide-body">
<svg id="chart-dow" width="1200" height="460"></svg>
<div style="font-size:16px;color:#64748B;margin-top:4px;">※ 月（2/9）・日（2/15）は営業データなし</div>
</div>''')

# Slide 8: Friday Basic Numbers (Ratio Bar)
slides.append(f'''{header_color("金曜日不調の分析：基本数字", 8, "#EF4444")}
{msg("金曜日は客数が4週平均の53.6%に半減。客単価は+17.1%と上昇したが客数減をカバーできず")}
<div class="slide-body">
<svg id="chart-fri-ratio" width="1200" height="420"></svg>
</div>''')

# Slide 9: Friday Group Size
slides.append(f'''{header_color("金曜日不調の分析：グループ人数", 9, "#EF4444")}
{msg("2名客が4組（80%）と偏重。3-4名グループがゼロで、飲み会・会食需要を取りこぼし")}
<div class="slide-body">
<div class="flex-row">
<div class="w60"><svg id="chart-fri-group" width="680" height="400"></svg></div>
<div class="w40">
<table class="dt" style="margin-top:10px;">
<thead><tr><th>人数</th><th>会計数</th><th>客数</th><th>売上</th><th>平均単価</th></tr></thead>
<tbody>
<tr><td>1名</td><td>0</td><td>0</td><td>¥0</td><td>-</td></tr>
<tr><td>2名</td><td>4</td><td>8</td><td>¥72,830</td><td>¥9,104</td></tr>
<tr style="background:#FEE2E2;"><td style="font-weight:800;color:#EF4444;">⚠️ 3-4名</td><td style="font-weight:800;color:#EF4444;">0</td><td style="font-weight:800;color:#EF4444;">0</td><td style="font-weight:800;color:#EF4444;">¥0</td><td>-</td></tr>
<tr class="hl-row"><td>🏆 5名以上</td><td>1</td><td>7</td><td>¥119,720</td><td>¥17,103</td></tr>
</tbody>
</table>
</div>
</div>
</div>''')

# Slide 10: Friday Time Slot
slides.append(f'''{header_color("金曜日不調の分析：時間帯別売上", 10, "#EF4444")}
{msg("19時台に3会計が集中する一極構造。18時台・20時台は各1会計のみで時間帯分散ができていない")}
<div class="slide-body">
<div class="flex-row">
<div class="w60"><svg id="chart-fri-time" width="680" height="400"></svg></div>
<div class="w40">
<table class="dt" style="margin-top:10px;">
<thead><tr><th>時間帯</th><th>会計数</th><th>客数</th><th>売上</th></tr></thead>
<tbody>
<tr><td>18時台</td><td>1</td><td>2</td><td>¥12,950</td></tr>
<tr class="hl-row"><td>🏆 19時台</td><td>3</td><td>11</td><td>¥158,600</td></tr>
<tr><td>20時台</td><td>1</td><td>2</td><td>¥21,000</td></tr>
</tbody>
</table>
<div class="chart-comment" style="margin-top:12px;">19時台が売上の<strong>82.4%</strong>を占める一極集中。18時台・20時台以降の来店促進が課題。</div>
</div>
</div>
</div>''')

# Slide 11: Friday Product Mix
slides.append(f'''{header_color("金曜日不調の分析：商品別売上", 11, "#EF4444")}
{msg("「別天地一推し」が53.2%と過半を占め、ドリンク追加注文が弱い。コース中心で単品の広がりなし")}
<div class="slide-body">
<div class="flex-row">
<div class="w60">
<table class="dt">
<thead><tr><th>カテゴリ</th><th>今週売上</th><th>構成比</th></tr></thead>
<tbody>
<tr class="hl-row"><td>🏆 別天地一推し</td><td style="text-align:right;">¥18,720</td><td style="text-align:right;font-size:20px;">53.2%</td></tr>
<tr><td>日本酒</td><td style="text-align:right;">¥8,000</td><td style="text-align:right;">22.7%</td></tr>
<tr><td>酒の肴</td><td style="text-align:right;">¥2,970</td><td style="text-align:right;">8.4%</td></tr>
<tr><td>刺身</td><td style="text-align:right;">¥1,380</td><td style="text-align:right;">3.9%</td></tr>
<tr><td>野菜</td><td style="text-align:right;">¥1,080</td><td style="text-align:right;">3.1%</td></tr>
<tr><td>果実酒</td><td style="text-align:right;">¥850</td><td style="text-align:right;">2.4%</td></tr>
<tr><td>焼酎</td><td style="text-align:right;">¥850</td><td style="text-align:right;">2.4%</td></tr>
<tr><td>サワー</td><td style="text-align:right;">¥820</td><td style="text-align:right;">2.3%</td></tr>
<tr><td>ソフトドリンク</td><td style="text-align:right;">¥530</td><td style="text-align:right;">1.5%</td></tr>
</tbody>
</table>
</div>
<div class="w40">
<div class="chart-comment"><strong>⚠️ 課題</strong><br>別天地一推し（しゃぶしゃぶ系）が過半で、ドリンクの追加注文が少ない。火曜日はウイスキー・プレミア限定酒が34%だったのと対照的。</div>
</div>
</div>
</div>''')

# Slide 12: Friday Summary
slides.append(f'''{header_color("金曜日不調の分析：まとめ", 12, "#EF4444")}
{msg("金曜日の不振は「会計数の不足」が根本原因。3-4名グループの獲得と時間帯分散が改善の鍵")}
<div class="slide-body">
<div style="display:flex;gap:16px;margin-top:8px;">
<div class="li-card" style="flex:1;border-top:4px solid #EF4444;">
<div style="font-size:28px;margin-bottom:4px;">🚨</div>
<div style="font-size:18px;font-weight:800;color:#EF4444;">会計数の圧倒的不足</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">5件のみ（4週平均の約半分）。金曜日は本来の最繁日にも関わらず来店が少ない</div>
</div>
<div class="li-card" style="flex:1;border-top:4px solid #EF4444;">
<div style="font-size:28px;margin-bottom:4px;">👥</div>
<div style="font-size:18px;font-weight:800;color:#EF4444;">3-4名グループの不在</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">会食・飲み会層を全く取り込めず。2名客中心の構造に</div>
</div>
<div class="li-card" style="flex:1;border-top:4px solid #EF4444;">
<div style="font-size:28px;margin-bottom:4px;">⚠️</div>
<div style="font-size:18px;font-weight:800;color:#EF4444;">大口1組への依存</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">売上の62%（¥119,720）が7名グループ1組。この1組がなければ¥72,830</div>
</div>
</div>
<div style="margin-top:16px;padding:16px 20px;background:#FEF2F2;border-radius:12px;border-left:5px solid #EF4444;">
<div style="font-size:20px;font-weight:800;color:#991B1B;">📋 改善の方向性</div>
<div style="display:flex;gap:12px;margin-top:8px;">
<div style="flex:1;font-size:17px;color:#334155;">🍽️ 金曜日限定のグループ向けコースプラン設定</div>
<div style="flex:1;font-size:17px;color:#334155;">📱 SNS・Googleビジネスプロフィールでの金曜日発信強化</div>
<div style="flex:1;font-size:17px;color:#334155;">🏢 予約獲得のための法人営業</div>
</div>
</div>
</div>''')

# Slide 13: Tuesday Basic Numbers (Ratio Bar)
slides.append(f'''{header_color("火曜日好調の分析：基本数字", 13, "#22C55E")}
{msg("火曜日は売上が4週平均の2.15倍。客数が2.19倍と大幅に増加し、単価減を補って余りある好調")}
<div class="slide-body">
<svg id="chart-tue-ratio" width="1200" height="420"></svg>
</div>''')

# Slide 14: Tuesday Group Size
slides.append(f'''{header_color("火曜日好調の分析：グループ人数", 14, "#22C55E")}
{msg("2名・3-4名・5名以上がバランスよく来店。特に3-4名の3組（11人）が売上の46%を稼ぐ")}
<div class="slide-body">
<div class="flex-row">
<div class="w60"><svg id="chart-tue-group" width="680" height="400"></svg></div>
<div class="w40">
<table class="dt" style="margin-top:10px;">
<thead><tr><th>人数</th><th>会計数</th><th>客数</th><th>売上</th><th>平均単価</th></tr></thead>
<tbody>
<tr><td>1名</td><td>0</td><td>0</td><td>¥0</td><td>-</td></tr>
<tr><td>2名</td><td>3</td><td>6</td><td>¥53,550</td><td>¥8,925</td></tr>
<tr class="hl-row"><td>🏆 3-4名</td><td>3</td><td>11</td><td>¥105,160</td><td>¥9,560</td></tr>
<tr><td>5名以上</td><td>1</td><td>6</td><td>¥70,160</td><td>¥11,693</td></tr>
</tbody>
</table>
</div>
</div>
</div>''')

# Slide 15: Tuesday Time Slot
slides.append(f'''{header_color("火曜日好調の分析：時間帯別売上", 15, "#22C55E")}
{msg("17時台から来店があり、18-19時台に計6会計・21人が来店。ゴールデンタイムをフル活用")}
<div class="slide-body">
<div class="flex-row">
<div class="w60"><svg id="chart-tue-time" width="680" height="400"></svg></div>
<div class="w40">
<table class="dt" style="margin-top:10px;">
<thead><tr><th>時間帯</th><th>会計数</th><th>客数</th><th>売上</th></tr></thead>
<tbody>
<tr><td>17時台</td><td>1</td><td>2</td><td>¥24,600</td></tr>
<tr class="hl-row"><td>🏆 18時台</td><td>3</td><td>11</td><td>¥105,160</td></tr>
<tr><td>19時台</td><td>3</td><td>10</td><td>¥99,110</td></tr>
</tbody>
</table>
<div class="chart-comment" style="margin-top:12px;">17〜19時台の3時間帯で売上が分散。特に18時台がピークで<strong>45.9%</strong>を占める。</div>
</div>
</div>
</div>''')

# Slide 16: Tuesday Product Mix
slides.append(f'''{header_color("火曜日好調の分析：商品別売上", 16, "#22C55E")}
{msg("カテゴリが5つ以上に分散し、ウイスキー（19.5%）やプレミア限定酒（14.5%）など高単価ドリンクが活発")}
<div class="slide-body">
<div class="flex-row">
<div class="w60">
<table class="dt">
<thead><tr><th>カテゴリ</th><th>今週売上</th><th>構成比</th></tr></thead>
<tbody>
<tr><td>別天地一推し</td><td style="text-align:right;">¥16,600</td><td style="text-align:right;">20.4%</td></tr>
<tr class="hl-row"><td>🥃 ウィスキー・ジン・リキュール</td><td style="text-align:right;">¥15,930</td><td style="text-align:right;font-size:20px;">19.5%</td></tr>
<tr class="hl-row"><td>🍶 プレミア限定酒（日本酒）</td><td style="text-align:right;">¥11,800</td><td style="text-align:right;font-size:20px;">14.5%</td></tr>
<tr><td>日本酒</td><td style="text-align:right;">¥11,360</td><td style="text-align:right;">13.9%</td></tr>
<tr><td>ビール・ノンアルコール</td><td style="text-align:right;">¥6,680</td><td style="text-align:right;">8.2%</td></tr>
<tr><td>刺身</td><td style="text-align:right;">¥5,800</td><td style="text-align:right;">7.1%</td></tr>
<tr><td>野菜</td><td style="text-align:right;">¥5,500</td><td style="text-align:right;">6.7%</td></tr>
<tr><td>酒の肴</td><td style="text-align:right;">¥3,560</td><td style="text-align:right;">4.4%</td></tr>
<tr><td>温菜・揚げ物</td><td style="text-align:right;">¥1,680</td><td style="text-align:right;">2.1%</td></tr>
<tr><td>果実酒</td><td style="text-align:right;">¥920</td><td style="text-align:right;">1.1%</td></tr>
<tr><td>焼酎</td><td style="text-align:right;">¥850</td><td style="text-align:right;">1.0%</td></tr>
<tr><td>サワー</td><td style="text-align:right;">¥820</td><td style="text-align:right;">1.0%</td></tr>
</tbody>
</table>
</div>
<div class="w40">
<div class="chart-comment"><strong>🎯 ポイント</strong><br>高単価ドリンク（ウイスキー+プレミア限定酒）が合計<strong>34.0%</strong>。金曜日は一推し53.2%に集中していたのと対照的にカテゴリが分散。</div>
</div>
</div>
</div>''')

# Slide 17: Tuesday Summary
slides.append(f'''{header_color("火曜日好調の分析：まとめ", 17, "#22C55E")}
{msg("多様なグループ構成+高単価ドリンク消費+時間帯分散の「三拍子」が好調の再現モデル")}
<div class="slide-body">
<div style="display:flex;gap:16px;margin-top:8px;">
<div class="li-card" style="flex:1;border-top:4px solid #22C55E;">
<div style="font-size:28px;margin-bottom:4px;">👥</div>
<div style="font-size:18px;font-weight:800;color:#166534;">多様なグループ構成</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">2名×3組、3-4名×3組、5名以上×1組とバランスよく獲得。特定サイズに偏らない</div>
</div>
<div class="li-card" style="flex:1;border-top:4px solid #22C55E;">
<div style="font-size:28px;margin-bottom:4px;">🍶</div>
<div style="font-size:18px;font-weight:800;color:#166534;">高単価ドリンクの積極注文</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">プレミア限定酒（而今・黒龍）やウイスキーが売上の34%を占め、客単価を底上げ</div>
</div>
<div class="li-card" style="flex:1;border-top:4px solid #22C55E;">
<div style="font-size:28px;margin-bottom:4px;">⏰</div>
<div style="font-size:18px;font-weight:800;color:#166534;">時間帯の分散</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">17時台から来店があり、18-19時台のゴールデンタイムをフル活用</div>
</div>
</div>
<div style="margin-top:16px;padding:16px 20px;background:#F0FDF4;border-radius:12px;border-left:5px solid #22C55E;">
<div style="font-size:20px;font-weight:800;color:#166534;">🔄 再現のポイント</div>
<div style="display:flex;gap:12px;margin-top:8px;">
<div style="flex:1;font-size:17px;color:#334155;">👥 3-4名グループの予約獲得が鍵（火曜はたまたま3組来店）</div>
<div style="flex:1;font-size:17px;color:#334155;">🍶 プレミア限定酒のテーブル提案を全曜日で徹底</div>
<div style="flex:1;font-size:17px;color:#334155;">⏰ 早い時間帯（17-18時台）の来店促進</div>
</div>
</div>
</div>''')

# Slide 18: Weekday Comparison Summary
slides.append(f'''{header("曜日別評価まとめ", 18)}
{msg("金曜日の「会計数不足」と火曜日の「多様なグループ獲得」が明暗を分けた。全曜日で3-4名グループの誘致が最優先課題")}
<div class="slide-body">
<table class="dt" style="font-size:17px;">
<thead><tr><th>観点</th><th style="background:#EF4444;">金曜日（不調）</th><th style="background:#22C55E;">火曜日（好調）</th></tr></thead>
<tbody>
<tr><td style="font-weight:700;">売上</td><td>¥192,550（4週平均比61.1%）</td><td style="color:#166534;font-weight:700;">¥228,870（4週平均比215.1%）</td></tr>
<tr><td style="font-weight:700;">客数</td><td>15人（4週平均比53.6%）</td><td style="color:#166534;font-weight:700;">23人（4週平均比219.0%）</td></tr>
<tr><td style="font-weight:700;">会計数</td><td>5件</td><td style="color:#166534;font-weight:700;">7件</td></tr>
<tr><td style="font-weight:700;">グループ構成</td><td style="color:#EF4444;">2名偏重（80%）</td><td style="color:#166534;font-weight:700;">分散（2名・3-4名・5名以上）</td></tr>
<tr><td style="font-weight:700;">商品構成</td><td style="color:#EF4444;">一推し53.2%に集中</td><td style="color:#166534;font-weight:700;">カテゴリ分散</td></tr>
<tr><td style="font-weight:700;">時間帯</td><td style="color:#EF4444;">19時台一極集中</td><td style="color:#166534;font-weight:700;">17-19時台に分散</td></tr>
</tbody>
</table>
<div style="margin-top:10px;padding:12px 20px;background:#F1F5F9;border-radius:10px;">
<div style="font-size:17px;color:#334155;line-height:1.6;">📊 5営業日中4日が4週平均割れという厳しい週。火曜日の好調がなければ、週間売上は¥367,090（1月平均の61%）に留まっていた。月・日の非稼働と水曜日の祝日影響で、実質的に3.5日分の営業力で¥60万を確保。</div>
</div>
</div>''')

# Slide 19: Category Donut Chart
slides.append(f'''{header("カテゴリ別売上構成比", 19, "第3部")}
{msg("「別天地一推し」が45.6%で圧倒的1位。日本酒系（通常+プレミア）が合計16.1%と2番手")}
<div class="slide-body">
<div class="flex-row" style="height:440px;">
<div class="w60"><svg id="chart-donut" width="680" height="420"></svg></div>
<div class="w40" style="display:flex;flex-direction:column;justify-content:center;">
<table class="dt" style="font-size:17px;">
<thead><tr><th>カテゴリ</th><th>売上</th><th>構成比</th></tr></thead>
<tbody>
<tr class="hl-row"><td>🏆 別天地一推し</td><td style="text-align:right;">¥106,800</td><td style="text-align:right;font-size:20px;">45.6%</td></tr>
<tr><td>日本酒</td><td style="text-align:right;">¥26,060</td><td style="text-align:right;">11.1%</td></tr>
<tr><td>ウィスキー・ジン・リキュール</td><td style="text-align:right;">¥19,080</td><td style="text-align:right;">8.1%</td></tr>
<tr><td>ビール・ノンアルコール</td><td style="text-align:right;">¥14,180</td><td style="text-align:right;">6.1%</td></tr>
<tr><td>酒の肴</td><td style="text-align:right;">¥12,550</td><td style="text-align:right;">5.4%</td></tr>
<tr><td>その他</td><td style="text-align:right;">¥55,670</td><td style="text-align:right;">23.7%</td></tr>
</tbody>
</table>
</div>
</div>
</div>''')

# Slide 20: Hot Categories Deep Dive
slides.append(f'''{header("好調カテゴリの深掘り", 20)}
{msg("「別天地一推し」は和牛しゃぶしゃぶを中心に構成。日本酒は高単価銘柄（黒龍・而今・紀土）が牽引")}
<div class="slide-body">
<div class="flex-row" style="gap:24px;">
<div class="card" style="flex:1;border-top:4px solid #F97316;">
<div class="sub-heading">🍖 別天地一推し（構成比45.6%）</div>
<table class="dt" style="font-size:17px;">
<thead><tr><th>商品</th><th>売上</th><th>構成比</th></tr></thead>
<tbody>
<tr class="hl-row"><td>🏆 和牛のしゃぶしゃぶ（一人前）</td><td style="text-align:right;">¥66,120</td><td style="text-align:right;">28.2%</td></tr>
<tr><td>追加　和牛</td><td style="text-align:right;">¥25,000</td><td style="text-align:right;">10.7%</td></tr>
<tr><td>その他一推し商品</td><td style="text-align:right;">¥15,680</td><td style="text-align:right;">6.7%</td></tr>
</tbody>
</table>
<div style="font-size:17px;color:#334155;margin-top:8px;">💡 しゃぶしゃぶが完全に看板商品として確立。追加注文率も高い</div>
</div>
<div class="card" style="flex:1;border-top:4px solid #3B82F6;">
<div class="sub-heading">🍶 日本酒系（合計16.1%）</div>
<table class="dt" style="font-size:17px;">
<thead><tr><th>銘柄</th><th>売上</th><th>特徴</th></tr></thead>
<tbody>
<tr class="hl-row"><td>🏆 黒龍 しずく（1合）</td><td style="text-align:right;">¥6,000</td><td>最高単価</td></tr>
<tr><td>紀土（2合）</td><td style="text-align:right;">¥5,600</td><td style="color:#22C55E;font-weight:700;">前週比+100.0%</td></tr>
<tr><td>楽器正宗（2合）</td><td style="text-align:right;">¥5,440</td><td style="color:#22C55E;font-weight:700;">前週比+33.3%</td></tr>
</tbody>
</table>
<div style="font-size:17px;color:#334155;margin-top:8px;">💡 2合注文が増加傾向。テーブル提案の効果が出つつある</div>
</div>
</div>
</div>''')

# Slide 21: Product TOP10
slides.append(f'''{header("商品別売上上位10", 21)}
{msg("和牛しゃぶしゃぶ（28.2%）と追加和牛（10.7%）で構成比の約4割。生ビールは前週比-70.2%と大幅減")}
<div class="slide-body">
<table class="dt">
<thead><tr><th>順位</th><th>商品名</th><th>売上</th><th>構成比</th><th>4週平均比</th></tr></thead>
<tbody>
<tr class="hl-row"><td>1</td><td style="text-align:left;">🏆 和牛のしゃぶしゃぶ（一人前）</td><td style="text-align:right;">¥66,120</td><td style="text-align:right;font-size:20px;">28.2%</td><td>-</td></tr>
<tr class="hl-row"><td>2</td><td style="text-align:left;">🏆 追加　和牛（一人前　1/2枚×２）</td><td style="text-align:right;">¥25,000</td><td style="text-align:right;font-size:20px;">10.7%</td><td>-</td></tr>
<tr style="background:#FEE2E2;"><td>3</td><td style="text-align:left;font-weight:800;color:#EF4444;">📉 アサヒスーパードライ（生ビール）</td><td style="text-align:right;font-weight:800;">¥13,500</td><td style="text-align:right;">5.8%</td><td style="color:#EF4444;font-weight:700;">-70.2%</td></tr>
<tr><td>4</td><td style="text-align:left;">酒の肴三種盛り</td><td style="text-align:right;">¥8,900</td><td style="text-align:right;">3.8%</td><td>-</td></tr>
<tr><td>5</td><td style="text-align:left;">（１合）黒龍　福井県　しずく</td><td style="text-align:right;">¥6,000</td><td style="text-align:right;">2.6%</td><td>-</td></tr>
<tr><td>6</td><td style="text-align:left;">鮮魚五点盛り（二人前）</td><td style="text-align:right;">¥5,880</td><td style="text-align:right;">2.5%</td><td>-</td></tr>
<tr><td>7</td><td style="text-align:left;">（２合）紀土　和歌山県　純米大吟醸　柔らか吟醸香</td><td style="text-align:right;">¥5,600</td><td style="text-align:right;">2.4%</td><td style="color:#22C55E;font-weight:700;">+100.0%</td></tr>
<tr><td>8</td><td style="text-align:left;">海鮮玉手箱（二人前）</td><td style="text-align:right;">¥5,520</td><td style="text-align:right;">2.4%</td><td>-</td></tr>
<tr><td>9</td><td style="text-align:left;">（２合）楽器正宗　福島県　特別本醸造　華やかクリア</td><td style="text-align:right;">¥5,440</td><td style="text-align:right;">2.3%</td><td style="color:#22C55E;font-weight:700;">+33.3%</td></tr>
<tr><td>10</td><td style="text-align:left;">からすみ蕎麦しゃぶ（しゃぶしゃぶ注文限定）</td><td style="text-align:right;">¥5,400</td><td style="text-align:right;">2.3%</td><td>-</td></tr>
</tbody>
</table>
</div>''')

# Slide 22: Product Composition Changes
slides.append(f'''{header("商品構成比の変化", 22)}
{msg("生ビールが-6.78ptと最大の減少。コース利用（飲み放題付き）増加により単品ビール注文が激減")}
<div class="slide-body">
<div class="flex-row" style="gap:24px;">
<div style="flex:1;">
<div class="sub-heading" style="color:#22C55E;">📈 構成比増加</div>
<table class="dt" style="font-size:17px;">
<thead><tr><th>商品名</th><th>今週</th><th>前週</th><th>変化</th></tr></thead>
<tbody>
<tr><td style="text-align:left;">（２合）紀土</td><td>2.39%</td><td>2.13%</td><td style="color:#22C55E;font-weight:700;">+0.26pt</td></tr>
<tr><td style="text-align:left;">（２合）楽器正宗</td><td>2.32%</td><td>2.07%</td><td style="color:#22C55E;font-weight:700;">+0.25pt</td></tr>
<tr><td style="text-align:left;">【芋】なかむら</td><td>0.77%</td><td>0.68%</td><td style="color:#22C55E;font-weight:700;">+0.08pt</td></tr>
</tbody>
</table>
</div>
<div style="flex:1;">
<div class="sub-heading" style="color:#EF4444;">📉 構成比減少</div>
<table class="dt" style="font-size:17px;">
<thead><tr><th>商品名</th><th>今週</th><th>前週</th><th>変化</th></tr></thead>
<tbody>
<tr style="background:#FEE2E2;"><td style="text-align:left;font-weight:800;color:#EF4444;">⚠️ アサヒスーパードライ（生ビール）</td><td>5.76%</td><td>12.55%</td><td style="color:#EF4444;font-weight:800;font-size:20px;">-6.78pt</td></tr>
<tr><td style="text-align:left;">碧</td><td>0.42%</td><td>3.73%</td><td style="color:#EF4444;font-weight:700;">-3.31pt</td></tr>
<tr><td style="text-align:left;">（１合）楽器正宗</td><td>0.58%</td><td>2.07%</td><td style="color:#EF4444;font-weight:700;">-1.49pt</td></tr>
</tbody>
</table>
</div>
</div>
</div>''')

# Slide 23: Product Summary
slides.append(f'''{header("商品分析まとめ", 23)}
{msg("「しゃぶしゃぶ×高単価日本酒」が別天地の二本柱。フード単品の充実が次の成長機会")}
<div class="slide-body">
<div class="flex-row" style="gap:24px;margin-top:8px;">
<div class="card" style="flex:1;border-top:4px solid #F97316;">
<div style="font-size:22px;font-weight:800;color:#1E293B;">🍖 しゃぶしゃぶ</div>
<div style="font-size:40px;font-weight:800;color:#F97316;margin:8px 0;">38.9%</div>
<div style="font-size:17px;color:#334155;">代表: 和牛しゃぶしゃぶ・追加和牛</div>
<div style="font-size:17px;color:#64748B;margin-top:4px;">狙い: 集客の核・リピート促進</div>
</div>
<div class="card" style="flex:1;border-top:4px solid #3B82F6;">
<div style="font-size:22px;font-weight:800;color:#1E293B;">🍶 高単価日本酒</div>
<div style="font-size:40px;font-weight:800;color:#3B82F6;margin:8px 0;">16.1%</div>
<div style="font-size:17px;color:#334155;">代表: 黒龍・紀土・楽器正宗</div>
<div style="font-size:17px;color:#64748B;margin-top:4px;">狙い: 客単価の向上</div>
</div>
</div>
<div style="margin-top:16px;padding:16px 20px;background:#FFF7ED;border-radius:12px;border-left:5px solid #F97316;">
<div style="font-size:20px;font-weight:800;color:#9A3412;">🌱 次の成長機会</div>
<div style="display:flex;gap:16px;margin-top:8px;">
<div class="li-card" style="flex:1;">🍽️ <strong>フード単品の充実</strong>: 「つまみ・アテの盛り合わせ」の開発（日報で顧客要望あり）</div>
<div class="li-card" style="flex:1;">🥢 <strong>からすみ蕎麦しゃぶの訴求</strong>: しゃぶしゃぶ注文限定の追加メニューとして構成比2.3%。提案強化で伸びしろあり</div>
</div>
</div>
</div>''')

# Slide 24: Wins
slides.append(f'''{header("今週の総括：強み", 24, "第4部")}
{msg("W06からの力強い回復と火曜日の爆発力が今週最大の収穫")}
<div class="slide-body">
<div style="display:flex;flex-direction:column;gap:14px;margin-top:8px;">
<div class="li-card" style="border-left:5px solid #22C55E;">
<div style="font-size:20px;font-weight:800;color:#166534;">🎯 前週比+65.6%の回復力</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">W06の¥359,880→W07の¥595,960。客数倍増・組数2.6倍で1月平均水準に復帰</div>
</div>
<div class="li-card" style="border-left:5px solid #22C55E;">
<div style="font-size:20px;font-weight:800;color:#166534;">📈 火曜日の大幅好調（4週平均比215.1%）</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">23人・7会計・¥228,870。多様なグループ構成と高単価ドリンク消費が成功モデル</div>
</div>
<div class="li-card" style="border-left:5px solid #22C55E;">
<div style="font-size:20px;font-weight:800;color:#166534;">🏆 看板商品の確立</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">和牛しゃぶしゃぶ+追加和牛で構成比38.9%。高単価日本酒（16.1%）との相乗効果で客単価¥9,612を維持</div>
</div>
</div>
</div>''')

# Slide 25: Challenges
slides.append(f'''{header("今週の総括：課題", 25)}
{msg("金曜日の客数半減と4営業日の4週平均割れが最大の課題。集客基盤の強化が急務")}
<div class="slide-body">
<div style="display:flex;flex-direction:column;gap:14px;margin-top:8px;">
<div class="li-card" style="border-left:5px solid #EF4444;">
<div style="font-size:20px;font-weight:800;color:#991B1B;">🚨 金曜日の客数半減（4週平均比53.6%）</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">15人・5会計のみ。3-4名グループがゼロで飲み会需要を取りこぼし。大口1組への依存構造</div>
</div>
<div class="li-card" style="border-left:5px solid #EF4444;">
<div style="font-size:20px;font-weight:800;color:#991B1B;">⚠️ 5営業日中4日が4週平均割れ</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">火曜日のみがプラスという偏り。安定的な集客基盤が未構築</div>
</div>
<div class="li-card" style="border-left:5px solid #EF4444;">
<div style="font-size:20px;font-weight:800;color:#991B1B;">📉 20時以降の来店ほぼゼロ</div>
<div style="font-size:17px;color:#334155;margin-top:6px;">二次会需要を全く取り込めず、営業時間後半の活用ができていない</div>
</div>
</div>
</div>''')

# Slide 26: Daily Report 1
slides.append(f'''{header("店舗の様子① — コース利用の反応と客層の特徴", 26, "第5部")}
{msg("新コースへの好反応とリーズナブルな価格訴求が来店動機に。バレンタインデーはカップル中心")}
<div class="slide-body">
<div class="sub-heading">🥂 新コースへの好反応とリーズナブルな価格訴求</div>
<div class="blockquote"><div class="bq-date">📅 2月10日（月）財田さん:</div>「20後半〜30前半の男性グループが3時間の飲み放題や豊富なドリンク、料理のボリュームを楽しみ、満足度は★4であった。」</div>
<div class="blockquote"><div class="bq-date">📅 2月10日（月）財田さん:</div>「銀座にしてはリーズナブルな価格で飲み放題付きの美味しいコース料理を提供し、リピーター獲得を目指している。」</div>
<div class="sub-heading" style="margin-top:14px;">💑 バレンタインデーの接客と料理提供</div>
<div class="blockquote"><div class="bq-date">📅 2月14日（金）財田さん:</div>「来店客層は30〜40代のカップル2名と40〜50代のカップル2名であった。」</div>
<div class="blockquote"><div class="bq-date">📅 2月14日（金）財田さん:</div>「30代カップルが提供スピードと接客態度に最も満足した。」「30代カップルは料理提供時に良いリアクションを示した。」</div>
</div>''')

# Slide 27: Daily Report 2
slides.append(f'''{header("店舗の様子② — 単品メニューへの要望とオペレーション課題", 27)}
{msg("単品メニューの充実とすき焼きコースの見た目・オペレーション改善がスタッフからの共通課題")}
<div class="slide-body">
<div class="sub-heading">🍽️ おつまみ・単品メニューの不足</div>
<div class="blockquote"><div class="bq-date">📅 2月10日（月）財田さん:</div>「単品料理の数が少ないため、もう少し増やし、お酒が進むような料理を追加する必要がある。」</div>
<div class="blockquote"><div class="bq-date">📅 2月10日（月）財田さん:</div>「ワインはほとんど注文されないため、飲み放題の内容をハイボール系に見直すことを検討している。」</div>
<div class="sub-heading" style="margin-top:14px;">⚠️ すき焼きコースのオペレーション改善</div>
<div class="blockquote"><div class="bq-date">📅 2月14日（金）財田さん:</div>「コースすき焼きの見た目やオペレーションに改善の必要がある。」「HI（加熱装置）があるにもかかわらず、すき焼きを温められない状況がある。」</div>
<div class="blockquote"><div class="bq-date">📅 2月13日（木）財田さん:</div>「すき焼きコースの見た目があまり良くないため、お客様の満足度が低下している可能性がある。」「すき焼きコースの価格帯に対して、お客様が次回も来店するかどうかは微妙なところである。」</div>
</div>''')

# Slide 28: Daily Report 3
slides.append(f'''{header("店舗の様子③ — 日本酒提案の課題と貸切対応", 28)}
{msg("日本酒の知識不足が原価率悪化のリスク。貸切ニーズへの対応も課題")}
<div class="slide-body">
<div class="sub-heading">🍶 日本酒の知識不足と提案力</div>
<div class="blockquote"><div class="bq-date">📅 2月13日（木）財田さん:</div>「飲み放題のメニューを見直さないと、特に日本酒と焼酎について、減価率が上がる恐れがある。」</div>
<div class="blockquote"><div class="bq-date">📅 2月10日（月）財田さん:</div>「20後半〜30代前半の男性2名がオール単品でしゃぶしゃぶとおつまみを楽しみ、高級日本酒をたくさん飲みながら終始笑顔で過ごしていた。」</div>
<div class="sub-heading" style="margin-top:14px;">🏢 貸切ニーズへの対応</div>
<div class="blockquote"><div class="bq-date">📅 2月10日（月）財田さん:</div>「資生堂スタッフの女性2名は貸切の下見のために来店し、お店が予想より狭いと感じ、満足度は★2であった。」</div>
<div style="margin-top:10px;padding:12px 16px;background:#FFF7ED;border-radius:10px;border-left:4px solid #F97316;">
<div style="font-size:17px;color:#334155;">💡 貸切ニーズは存在するが、店舗面積の制約がある。半貸切プランの整備や、近隣企業向けの少人数貸切プランで対応を検討。</div>
</div>
</div>''')

# Slide 29: Action Plans 1
slides.append(f'''{header("施策一覧①：メニュー・集客", 29, "第6部")}
{msg("メニュー開発10施策と集客・マーケティング10施策で金曜日の不振と全体の集客力強化に取り組む")}
<div class="slide-body" style="padding:12px 40px;">
<div class="flex-row" style="gap:20px;">
<div style="flex:1;">
<div class="sub-heading" style="font-size:18px;">🍽️ メニュー開発</div>
<table class="action-table">
<thead><tr><th style="width:55%;">施策</th><th style="width:45%;">狙い</th></tr></thead>
<tbody>
<tr><td>おつまみ盛り合わせの新設</td><td>フード単品売上の底上げ・客単価向上</td></tr>
<tr><td>日本酒ペアリングセット（3種飲み比べ）</td><td>高単価ドリンクの訴求・体験価値向上</td></tr>
<tr><td>しゃぶしゃぶ追加トッピングの拡充</td><td>追加注文率の向上</td></tr>
<tr><td>すき焼きコースのオペ改善・見た目刷新</td><td>顧客満足度向上・リピート促進</td></tr>
<tr><td>飲み放題メニューのハイボール系強化</td><td>原価率改善・顧客嗜好への対応</td></tr>
<tr><td>ワイン縮小・焼酎拡充</td><td>注文実態に合ったメニュー最適化</td></tr>
<tr><td>金曜限定「3-4名グループ向け会食コース」</td><td>金曜日の会計数増加</td></tr>
<tr><td>季節の日本酒入荷情報のメニュー掲載</td><td>プレミア限定酒の認知度向上</td></tr>
<tr><td>からすみ蕎麦しゃぶの積極提案</td><td>しゃぶしゃぶ関連の追加注文増</td></tr>
<tr><td>20時以降の二次会プラン</td><td>遅い時間帯の来店促進</td></tr>
</tbody>
</table>
</div>
<div style="flex:1;">
<div class="sub-heading" style="font-size:18px;">📱 集客・マーケティング</div>
<table class="action-table">
<thead><tr><th style="width:55%;">施策</th><th style="width:45%;">狙い</th></tr></thead>
<tbody>
<tr><td>Googleビジネスプロフィールの定期更新</td><td>検索経由の新規来店増</td></tr>
<tr><td>Instagram投稿（和牛しゃぶしゃぶの映え写真）</td><td>看板商品の認知拡大</td></tr>
<tr><td>法人向けDM（金曜日の会食プラン案内）</td><td>金曜日のグループ予約獲得</td></tr>
<tr><td>Diniiの予約機能を活用した事前予約促進</td><td>来店の確実性向上</td></tr>
<tr><td>口コミ投稿の依頼（会計時にQRコード配布）</td><td>口コミ経由の新規来店増</td></tr>
<tr><td>祝日向け特別プランの告知</td><td>祝日の集客力向上</td></tr>
<tr><td>近隣企業への訪問営業</td><td>法人利用の開拓</td></tr>
<tr><td>LINE公式アカウントでの金曜日限定クーポン</td><td>金曜日の来店動機づけ</td></tr>
<tr><td>外国人向けメニュー（英語表記）の整備</td><td>インバウンド対応の強化</td></tr>
<tr><td>貸切・半貸切プランの案内ページ整備</td><td>貸切ニーズへの対応</td></tr>
</tbody>
</table>
</div>
</div>
</div>''')

# Slide 30: Action Plans 2
slides.append(f'''{header("施策一覧②：顧客・運営", 30)}
{msg("リピーター育成10施策と運営改善10施策で安定的な集客基盤と顧客体験の向上を図る")}
<div class="slide-body" style="padding:12px 40px;">
<div class="flex-row" style="gap:20px;">
<div style="flex:1;">
<div class="sub-heading" style="font-size:18px;">💎 顧客育成・リピーター</div>
<table class="action-table">
<thead><tr><th style="width:55%;">施策</th><th style="width:45%;">狙い</th></tr></thead>
<tbody>
<tr><td>初回来店客へのサンキューメッセージ送付</td><td>リピート率向上</td></tr>
<tr><td>2回目来店時の特典（日本酒1杯サービス等）</td><td>2回目来店のハードル低下</td></tr>
<tr><td>常連客向けの限定日本酒の先行案内</td><td>ロイヤルカスタマーの育成</td></tr>
<tr><td>記念日利用時のサプライズ演出</td><td>特別な体験価値の提供</td></tr>
<tr><td>コース利用客への次回予約割引</td><td>リピート予約の促進</td></tr>
<tr><td>しゃぶしゃぶ好き向けの新商品先行試食会</td><td>ファンコミュニティの形成</td></tr>
<tr><td>法人接待利用時の請求書対応</td><td>法人利用のハードル低下</td></tr>
<tr><td>来店頻度に応じたポイント制度</td><td>来店頻度の向上</td></tr>
<tr><td>誕生月のお客様への特別コース案内</td><td>特別な来店動機の創出</td></tr>
<tr><td>グループ幹事向けの優遇制度</td><td>幹事を通じたグループ集客</td></tr>
</tbody>
</table>
</div>
<div style="flex:1;">
<div class="sub-heading" style="font-size:18px;">⚙️ 運営改善</div>
<table class="action-table">
<thead><tr><th style="width:55%;">施策</th><th style="width:45%;">狙い</th></tr></thead>
<tbody>
<tr><td>QRコード注文システムの導入</td><td>ドリンク追加注文のハードル低下</td></tr>
<tr><td>半個室のオーダー対応フロー見直し</td><td>呼び出し回数の削減・顧客満足度向上</td></tr>
<tr><td>ホールスタッフの配置最適化</td><td>サービス品質の均一化</td></tr>
<tr><td>料理提供のタイミング管理シート導入</td><td>提供スピードの安定化</td></tr>
<tr><td>すき焼きコースのHI運用マニュアル作成</td><td>オペレーション品質の向上</td></tr>
<tr><td>飲み放題の原価率モニタリング強化</td><td>利益率の改善</td></tr>
<tr><td>金曜日のスタッフ配置強化</td><td>繁忙日のサービス品質確保</td></tr>
<tr><td>会計レベル別の接客対応マニュアル</td><td>高額会計客への適切な対応</td></tr>
<tr><td>月・日の試験営業の検討</td><td>営業日数増加による売上機会拡大</td></tr>
<tr><td>予約管理の一元化（Dinii活用）</td><td>予約漏れ防止・稼働率向上</td></tr>
</tbody>
</table>
</div>
</div>
</div>''')

# Slide 31: Action Plans 3
slides.append(f'''{header("施策一覧③：スタッフ育成", 31)}
{msg("日本酒・焼酎の知識研修とテーブル提案スキルの向上で、客単価を底上げする体制を構築")}
<div class="slide-body" style="padding:12px 40px;">
<div class="sub-heading" style="font-size:20px;">👨‍🍳 スタッフ育成・組織強化</div>
<table class="action-table" style="margin-top:8px;">
<thead><tr><th style="width:5%;">No.</th><th style="width:50%;">施策</th><th style="width:45%;">狙い</th></tr></thead>
<tbody>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">1</td><td>日本酒の基礎知識研修（月1回）</td><td>店長以外もおすすめができる体制構築</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">2</td><td>焼酎・ウイスキーの知識共有シート作成</td><td>ドリンク提案力の底上げ</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">3</td><td>テーブル提案のロールプレイ研修</td><td>追加注文率の向上</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">4</td><td>料理説明のスクリプト整備</td><td>接客品質の均一化</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">5</td><td>新人向けオンボーディングプログラム</td><td>即戦力化までの期間短縮</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">6</td><td>お客様との会話のきっかけ集作成</td><td>コミュニケーション品質の向上</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">7</td><td>繁忙時の動き方マニュアル（ポジション別）</td><td>繁忙時のサービス品質維持</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">8</td><td>高級日本酒の試飲会（スタッフ向け）</td><td>商品知識の体験的理解</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">9</td><td>接客コンテスト（月間MVP表彰）</td><td>モチベーション向上</td></tr>
<tr><td style="text-align:center;font-weight:700;color:#3B82F6;">10</td><td>顧客満足度フィードバックの共有ミーティング</td><td>サービス改善の継続的な取り組み</td></tr>
</tbody>
</table>
</div>''')

# ===== D3.js Scripts =====
D3_SCRIPT = r'''
<script>
const COLORS = {
  positive: '#22C55E', negative: '#EF4444', attention: '#F97316',
  main: '#3B82F6', gray: '#94A3B8', darkText: '#1E293B', lightText: '#64748B'
};

// Helper: add callout
function addCallout(g, x, y, text, opts={}) {
  const {bg='#FFF7ED', border='#F97316', textColor='#1E293B', fontSize='18px', fontWeight='800', anchor='middle'} = opts;
  const cg = g.append('g');
  const t = cg.append('text').attr('x', x).attr('y', y).attr('text-anchor', anchor)
    .attr('font-size', fontSize).attr('font-weight', fontWeight).attr('fill', textColor).text(text);
  const bb = t.node().getBBox();
  cg.insert('rect','text').attr('x', bb.x-10).attr('y', bb.y-5).attr('width', bb.width+20).attr('height', bb.height+10)
    .attr('rx', 6).attr('fill', bg).attr('stroke', border).attr('stroke-width', 1.5);
}

// Helper: trend arrow
function addTrendArrow(svg, svgId, x1, y1, x2, y2, color, label) {
  const mid = 'trend-' + svgId;
  svg.append('defs').append('marker').attr('id', mid)
    .attr('viewBox','0 0 10 10').attr('refX',8).attr('refY',5)
    .attr('markerWidth',8).attr('markerHeight',8).attr('orient','auto-start-reverse')
    .append('path').attr('d','M 0 0 L 10 5 L 0 10 z').attr('fill', color);
  const ag = svg.append('g').attr('opacity', 0.7);
  const offy = y2 < y1 ? 6 : -6;
  ag.append('line').attr('x1', x1+14).attr('y1', y1+offy).attr('x2', x2-14).attr('y2', y2-offy)
    .attr('stroke', color).attr('stroke-width', 3.5).attr('marker-end', 'url(#'+mid+')');
  const mx = (x1+x2)/2, my = (y1+y2)/2;
  ag.append('text').attr('x', mx+25).attr('y', my-8)
    .attr('font-size','16px').attr('font-weight','700').attr('fill', color).text(label);
}

function addBadge(g, cx, cy, text, color, bgColor) {
  const bg2 = g.append('g');
  const bt = bg2.append('text').attr('x', cx).attr('y', cy).attr('text-anchor','middle')
    .attr('font-size','16px').attr('font-weight','800').attr('fill', color).text(text);
  const bb = bt.node().getBBox();
  bg2.insert('rect','text').attr('x', bb.x-6).attr('y', bb.y-3).attr('width', bb.width+12).attr('height', bb.height+6)
    .attr('rx', 4).attr('fill', bgColor).attr('stroke', color).attr('stroke-width', 1.5);
}

// ======= LINE CHARTS (Slides 3-5) =======
function drawLineChart(svgId, data, yLabel, fmt, avg4w) {
  const svg = d3.select('#'+svgId);
  const W = +svg.attr('width'), H = +svg.attr('height');
  const m = {top:50, right:80, bottom:50, left:80};
  const iW = W-m.left-m.right, iH = H-m.top-m.bottom;
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);

  const x = d3.scalePoint().domain(data.map(d=>d.label)).range([0, iW]).padding(0.3);
  const yMin = d3.min(data, d=>d.value)*0.85;
  const yMax = d3.max(data, d=>d.value)*1.1;
  const y = d3.scaleLinear().domain([yMin, yMax]).range([iH, 0]);

  // Grid
  g.selectAll('.grid-line').data(y.ticks(5)).join('line')
    .attr('x1',0).attr('x2',iW).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');

  // 4-week avg line
  if (avg4w) {
    g.append('line').attr('x1',0).attr('x2',iW).attr('y1',y(avg4w)).attr('y2',y(avg4w))
      .attr('stroke','#F97316').attr('stroke-width',1.5).attr('stroke-dasharray','6,4');
    g.append('text').attr('x',iW+4).attr('y',y(avg4w)+4)
      .attr('font-size','14px').attr('fill','#F97316').attr('font-weight','600').text('1月平均');
  }

  // Line
  const line = d3.line().x(d=>x(d.label)).y(d=>y(d.value)).curve(d3.curveMonotoneX);
  g.append('path').datum(data).attr('d', line)
    .attr('fill','none').attr('stroke',COLORS.main).attr('stroke-width',3);

  // Dots
  g.selectAll('.dot').data(data).join('circle')
    .attr('cx',d=>x(d.label)).attr('cy',d=>y(d.value))
    .attr('r', (d,i)=> i===data.length-1 ? 8 : 4)
    .attr('fill', (d,i)=> i===data.length-1 ? COLORS.main : '#fff')
    .attr('stroke', COLORS.main).attr('stroke-width', 2);

  // Data labels
  g.selectAll('.dlabel').data(data).join('text')
    .attr('x', d=>x(d.label)).attr('y', d=>y(d.value)-14)
    .attr('text-anchor','middle')
    .attr('font-size', (d,i)=> i===data.length-1 ? '18px' : '16px')
    .attr('font-weight', (d,i)=> i===data.length-1 ? '800' : '500')
    .attr('fill', (d,i)=> i===data.length-1 ? COLORS.darkText : COLORS.lightText)
    .text(d => fmt(d.value));

  // Trend arrow between last two points
  if (data.length >= 2) {
    const prev = data[data.length-2], curr = data[data.length-1];
    const pct = ((curr.value - prev.value)/prev.value*100).toFixed(1);
    const color = curr.value >= prev.value ? COLORS.positive : COLORS.negative;
    const sign = curr.value >= prev.value ? '+' : '';
    addTrendArrow(g, svgId, x(prev.label), y(prev.value), x(curr.label), y(curr.value), color, sign+pct+'%');
  }

  // Axes
  g.append('g').attr('transform', `translate(0,${iH})`).call(d3.axisBottom(x))
    .selectAll('text').attr('font-size','16px');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d => fmt(d)))
    .selectAll('text').attr('font-size','14px');
}

// Sales trend
drawLineChart('chart-sales',
  [{label:'W03',value:720750},{label:'W04',value:953210},{label:'W05',value:880430},{label:'W06',value:359880},{label:'W07',value:595960}],
  '売上', v => '¥'+v.toLocaleString(), 603483
);

// Customer trend
drawLineChart('chart-customers',
  [{label:'W03',value:80},{label:'W04',value:89},{label:'W05',value:89},{label:'W06',value:31},{label:'W07',value:62}],
  '客数', v => v+'人', 62
);

// Price trend
drawLineChart('chart-price',
  [{label:'W03',value:9009},{label:'W04',value:10710},{label:'W05',value:9892},{label:'W06',value:11609},{label:'W07',value:9612}],
  '客単価', v => '¥'+v.toLocaleString(), 9650
);

// ======= WEEKDAY GROUPED BAR (Slide 7) =======
(function(){
  const svg = d3.select('#chart-dow');
  const W = +svg.attr('width'), H = +svg.attr('height');
  const m = {top:50, right:40, bottom:50, left:80};
  const iW = W-m.left-m.right, iH = H-m.top-m.bottom;
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);

  const data = [
    {day:'火', thisW:228870, avg:106408, diff:122462},
    {day:'水', thisW:23940, avg:114753, diff:-90813},
    {day:'木', thisW:120930, avg:140310, diff:-19380},
    {day:'金', thisW:192550, avg:315250, diff:-122700},
    {day:'土', thisW:29670, avg:48633, diff:-18963}
  ];

  const x0 = d3.scaleBand().domain(data.map(d=>d.day)).range([0,iW]).padding(0.25);
  const x1 = d3.scaleBand().domain(['thisW','avg']).range([0, x0.bandwidth()]).padding(0.1);
  const yMax = d3.max(data, d=>Math.max(d.thisW, d.avg))*1.15;
  const y = d3.scaleLinear().domain([0, yMax]).range([iH, 0]);

  // Grid
  g.selectAll('.gl').data(y.ticks(5)).join('line')
    .attr('x1',0).attr('x2',iW).attr('y1',d=>y(d)).attr('y2',d=>y(d))
    .attr('stroke','#E2E8F0').attr('stroke-dasharray','3,3');

  // Highlight bands for worst days
  data.forEach(d => {
    if (d.day === '金') {
      g.append('rect').attr('x', x0(d.day)-4).attr('y', 0).attr('width', x0.bandwidth()+8).attr('height', iH)
        .attr('fill', '#FEF2F2').attr('rx', 6).attr('opacity', 0.5);
    }
    if (d.day === '火') {
      g.append('rect').attr('x', x0(d.day)-4).attr('y', 0).attr('width', x0.bandwidth()+8).attr('height', iH)
        .attr('fill', '#F0FDF4').attr('rx', 6).attr('opacity', 0.5);
    }
  });

  // Bars
  data.forEach(d => {
    const barColor = d.diff > 0 ? COLORS.positive : (d.diff < -100000 ? COLORS.negative : COLORS.main);
    g.append('rect')
      .attr('x', x0(d.day)+x1('thisW')).attr('y', y(d.thisW))
      .attr('width', x1.bandwidth()).attr('height', iH-y(d.thisW))
      .attr('fill', barColor).attr('rx', 4);
    g.append('rect')
      .attr('x', x0(d.day)+x1('avg')).attr('y', y(d.avg))
      .attr('width', x1.bandwidth()).attr('height', iH-y(d.avg))
      .attr('fill', COLORS.gray).attr('rx', 4);
    // Labels
    g.append('text').attr('x', x0(d.day)+x1('thisW')+x1.bandwidth()/2).attr('y', y(d.thisW)-6)
      .attr('text-anchor','middle').attr('font-size', Math.abs(d.diff)>100000?'17px':'15px')
      .attr('font-weight', Math.abs(d.diff)>100000?'800':'500')
      .attr('fill', Math.abs(d.diff)>100000 ? barColor : COLORS.lightText)
      .text('¥'+d.thisW.toLocaleString());
  });

  // Callouts for best/worst
  const tue = data[0];
  addCallout(g, x0(tue.day)+x0.bandwidth()/2, y(tue.thisW)-30, '+¥122,462', {bg:'#F0FDF4', border:'#22C55E', textColor:'#166534'});
  const fri = data[3];
  const friX = x0(fri.day)+x0.bandwidth()/2;
  addCallout(g, friX-40, y(fri.avg)-30, '-¥122,700', {bg:'#FEF2F2', border:'#EF4444', textColor:'#991B1B', anchor:'end'});

  // Legend
  const lg = g.append('g').attr('transform', `translate(${iW-200}, -30)`);
  lg.append('rect').attr('width',14).attr('height',14).attr('fill',COLORS.main).attr('rx',2);
  lg.append('text').attr('x',20).attr('y',12).attr('font-size','16px').attr('fill',COLORS.darkText).text('今週');
  lg.append('rect').attr('x',80).attr('width',14).attr('height',14).attr('fill',COLORS.gray).attr('rx',2);
  lg.append('text').attr('x',100).attr('y',12).attr('font-size','16px').attr('fill',COLORS.darkText).text('4週平均');

  g.append('g').attr('transform', `translate(0,${iH})`).call(d3.axisBottom(x0))
    .selectAll('text').attr('font-size','18px').attr('font-weight','700');
  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+(d/10000).toFixed(0)+'万'))
    .selectAll('text').attr('font-size','14px');
})();

// ======= RATIO BAR CHARTS (Slides 8, 13) =======
function drawRatioBar(svgId, labels, thisW, avg4, fmtFns, barColors) {
  const svg = d3.select('#'+svgId);
  const W = +svg.attr('width'), H = +svg.attr('height');
  const m = {top:30, right:200, bottom:30, left:140};
  const iW = W-m.left-m.right, iH = H-m.top-m.bottom;
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);

  const ratios = thisW.map((v,i) => v/avg4[i]*100);
  const maxR = Math.max(250, d3.max(ratios)*1.1);

  const y = d3.scaleBand().domain(labels).range([0, iH]).padding(0.35);
  const x = d3.scaleLinear().domain([0, maxR]).range([0, iW]);

  // 100% line
  g.append('line').attr('x1', x(100)).attr('x2', x(100)).attr('y1', 0).attr('y2', iH)
    .attr('stroke', '#1E293B').attr('stroke-width', 2.5).attr('stroke-dasharray', '8,4');
  g.append('text').attr('x', x(100)).attr('y', -8).attr('text-anchor','middle')
    .attr('font-size','14px').attr('font-weight','700').attr('fill','#1E293B').text('4週平均=100%');

  labels.forEach((label, i) => {
    const r = ratios[i];
    const color = r < 80 ? COLORS.negative : r > 120 ? COLORS.positive : COLORS.main;
    // Bar
    g.append('rect').attr('x', 0).attr('y', y(label)).attr('width', x(r)).attr('height', y.bandwidth())
      .attr('fill', color).attr('rx', 4);
    // Outline for min/max
    if (r === Math.min(...ratios) || r === Math.max(...ratios)) {
      g.append('rect').attr('x', -1.5).attr('y', y(label)-1.5)
        .attr('width', x(r)+3).attr('height', y.bandwidth()+3)
        .attr('fill','none').attr('stroke', color).attr('stroke-width', 3).attr('rx', 5);
    }
    // Ratio label
    g.append('text').attr('x', x(r)+8).attr('y', y(label)+y.bandwidth()/2-8)
      .attr('font-size','22px').attr('font-weight','800').attr('fill', color)
      .text(r.toFixed(1)+'%');
    // Actual value
    g.append('text').attr('x', x(r)+8).attr('y', y(label)+y.bandwidth()/2+14)
      .attr('font-size','16px').attr('font-weight','500').attr('fill', COLORS.lightText)
      .text(fmtFns[i](thisW[i]) + ' (4週平均: ' + fmtFns[i](avg4[i]) + ')');
    // Badge
    if (r < 60) addBadge(g, x(r)+140, y(label)+y.bandwidth()/2-8, '▼ 要改善', COLORS.negative, '#FEF2F2');
    if (r > 200) addBadge(g, x(r)+140, y(label)+y.bandwidth()/2-8, '★ 好調', COLORS.positive, '#F0FDF4');
    // Label
    g.append('text').attr('x', -8).attr('y', y(label)+y.bandwidth()/2+6)
      .attr('text-anchor','end').attr('font-size','18px').attr('font-weight','700').attr('fill',COLORS.darkText)
      .text(label);
  });
}

// Friday ratio bars
drawRatioBar('chart-fri-ratio',
  ['売上', '客数', '客単価'],
  [192550, 15, 12837],
  [315250, 28, 10958],
  [v=>'¥'+v.toLocaleString(), v=>v+'人', v=>'¥'+v.toLocaleString()]
);

// Tuesday ratio bars
drawRatioBar('chart-tue-ratio',
  ['売上', '客数', '客単価'],
  [228870, 23, 9951],
  [106408, 10.5, 11397],
  [v=>'¥'+v.toLocaleString(), v=>v+'人', v=>'¥'+v.toLocaleString()]
);

// ======= HORIZONTAL BAR CHARTS (Groups & Time) =======
function drawHBar(svgId, data, valueKey, labelKey, fmt) {
  const svg = d3.select('#'+svgId);
  const W = +svg.attr('width'), H = +svg.attr('height');
  const m = {top:30, right:120, bottom:30, left:100};
  const iW = W-m.left-m.right, iH = H-m.top-m.bottom;
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);

  const y = d3.scaleBand().domain(data.map(d=>d[labelKey])).range([0, iH]).padding(0.3);
  const maxV = d3.max(data, d=>d[valueKey])*1.15 || 1;
  const x = d3.scaleLinear().domain([0, maxV]).range([0, iW]);

  const maxVal = d3.max(data, d=>d[valueKey]);

  data.forEach(d => {
    const isMax = d[valueKey] === maxVal && d[valueKey] > 0;
    const color = isMax ? COLORS.attention : COLORS.main;
    g.append('rect').attr('x', 0).attr('y', y(d[labelKey])).attr('width', x(d[valueKey])).attr('height', y.bandwidth())
      .attr('fill', color).attr('rx', 4).attr('opacity', isMax ? 1 : 0.7);
    if (isMax && d[valueKey] > 0) {
      g.append('rect').attr('x', -1.5).attr('y', y(d[labelKey])-1.5)
        .attr('width', x(d[valueKey])+3).attr('height', y.bandwidth()+3)
        .attr('fill','none').attr('stroke', color).attr('stroke-width', 3).attr('rx', 5);
      addBadge(g, x(d[valueKey])+60, y(d[labelKey])-8, 'MAX', COLORS.attention, '#FFF7ED');
    }
    g.append('text').attr('x', x(d[valueKey])+8).attr('y', y(d[labelKey])+y.bandwidth()/2+5)
      .attr('font-size', isMax?'18px':'16px').attr('font-weight', isMax?'800':'500')
      .attr('fill', isMax ? COLORS.darkText : COLORS.lightText)
      .text(fmt(d[valueKey]));
    g.append('text').attr('x', -8).attr('y', y(d[labelKey])+y.bandwidth()/2+5)
      .attr('text-anchor','end').attr('font-size','16px').attr('font-weight','600').attr('fill',COLORS.darkText)
      .text(d[labelKey]);
  });
}

// Friday group size
drawHBar('chart-fri-group',
  [{g:'1名',s:0},{g:'2名',s:72830},{g:'3-4名',s:0},{g:'5名以上',s:119720}],
  's', 'g', v => '¥'+v.toLocaleString()
);

// Friday time slot
drawHBar('chart-fri-time',
  [{t:'18時台',s:12950},{t:'19時台',s:158600},{t:'20時台',s:21000}],
  's', 't', v => '¥'+v.toLocaleString()
);

// Tuesday group size
drawHBar('chart-tue-group',
  [{g:'1名',s:0},{g:'2名',s:53550},{g:'3-4名',s:105160},{g:'5名以上',s:70160}],
  's', 'g', v => '¥'+v.toLocaleString()
);

// Tuesday time slot
drawHBar('chart-tue-time',
  [{t:'17時台',s:24600},{t:'18時台',s:105160},{t:'19時台',s:99110}],
  's', 't', v => '¥'+v.toLocaleString()
);

// ======= DONUT CHART (Slide 19) =======
(function(){
  const svg = d3.select('#chart-donut');
  const W = +svg.attr('width'), H = +svg.attr('height');
  const cx = W/2 - 20, cy = H/2;
  const radius = Math.min(cx, cy) - 40;
  const g = svg.append('g').attr('transform', `translate(${cx},${cy})`);

  const data = [
    {label:'別天地一推し', value:106800, pct:'45.6%'},
    {label:'日本酒', value:26060, pct:'11.1%'},
    {label:'ウィスキー・ジン・リキュール', value:19080, pct:'8.1%'},
    {label:'ビール・ノンアルコール', value:14180, pct:'6.1%'},
    {label:'酒の肴', value:12550, pct:'5.4%'},
    {label:'その他', value:55670, pct:'23.7%'}
  ];
  const colors = ['#F97316','#3B82F6','#8B5CF6','#22C55E','#EC4899','#CBD5E1'];

  const pie = d3.pie().value(d=>d.value).sort(null);
  const arc = d3.arc().innerRadius(radius*0.52).outerRadius(radius);
  const arcs = pie(data);

  // Segments
  g.selectAll('.seg').data(arcs).join('path')
    .attr('d', (d,i) => {
      if (i===0) {
        const [ccx, ccy] = arc.centroid(d);
        const dist = Math.sqrt(ccx*ccx+ccy*ccy);
        const a = d3.arc().innerRadius(radius*0.52).outerRadius(radius);
        return 'M0,0' + a(d).replace('M','L').slice(0,-1) + 'Z';
      }
      return arc(d);
    })
    .attr('fill', (d,i) => colors[i])
    .attr('stroke','#fff').attr('stroke-width', 2)
    .attr('transform', (d,i) => {
      if (i===0) {
        const [ccx, ccy] = arc.centroid(d);
        const dist = Math.sqrt(ccx*ccx+ccy*ccy) || 1;
        return `translate(${ccx/dist*18},${ccy/dist*18})`;
      }
      return '';
    });

  // Labels on segments
  arcs.forEach((d,i) => {
    if (d.data.value/d3.sum(data,d2=>d2.value) > 0.05) {
      const [lx, ly] = arc.centroid(d);
      const off = i===0 ? 18 : 0;
      const dist = Math.sqrt(lx*lx+ly*ly) || 1;
      g.append('text')
        .attr('x', lx + (i===0 ? lx/dist*off : 0))
        .attr('y', ly + (i===0 ? ly/dist*off : 0))
        .attr('text-anchor','middle').attr('dy','0.35em')
        .attr('font-size','16px').attr('font-weight','700')
        .attr('fill', i<=3 ? '#fff' : '#1E293B')
        .text(d.data.pct);
    }
  });

  // Center text
  g.append('text').attr('y', -10).attr('text-anchor','middle')
    .attr('font-size','18px').attr('fill',COLORS.lightText).text('合計');
  g.append('text').attr('y', 20).attr('text-anchor','middle')
    .attr('font-size','26px').attr('font-weight','800').attr('fill',COLORS.darkText).text('¥234,340');

  // Leader line for largest segment — force label to upper-right area to avoid clipping
  const maxSlice = arcs[0];
  const centroid0 = arc.centroid(maxSlice);
  const dist0 = Math.sqrt(centroid0[0]*centroid0[0]+centroid0[1]*centroid0[1]) || 1;
  const explodeOff = [centroid0[0]/dist0*18, centroid0[1]/dist0*18];
  // Start point on outer edge of exploded segment
  const midAngle = (maxSlice.startAngle + maxSlice.endAngle) / 2 - Math.PI/2;
  const outerR = radius + 30;
  const outerPt = [Math.cos(midAngle)*outerR + explodeOff[0], Math.sin(midAngle)*outerR + explodeOff[1]];
  // Fixed label position: upper-right, safely inside SVG
  const labelEndX = 160, labelEndY = -radius - 20;
  const labelTextX = labelEndX + 6;

  g.append('polyline')
    .attr('points', `${outerPt[0]},${outerPt[1]} ${labelEndX},${labelEndY}`)
    .attr('fill','none').attr('stroke','#F97316').attr('stroke-width',2);
  g.append('text')
    .attr('x', labelTextX).attr('y', labelEndY+5)
    .attr('text-anchor', 'start')
    .attr('font-size','17px').attr('font-weight','800').attr('fill','#F97316')
    .text('別天地一推し 45.6%');
})();

</script>
'''

# ===== ASSEMBLE HTML =====
html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{STORE} 週次営業報告 — {WEEK}</title>
<script src="https://d3js.org/d3.v7.min.js"><\/script>
<style>
{CSS}
</style>
</head>
<body>
'''

for i, slide_html in enumerate(slides):
    if i == 0:
        html += f'\n<!-- ===== SLIDE {i+1} ===== -->\n{slide_html}\n'
    else:
        html += f'\n<!-- ===== SLIDE {i+1} ===== -->\n<div class="slide" id="slide-{i+1}">\n{slide_html}\n</div>\n'

html += D3_SCRIPT
html += '\n</body>\n</html>'

# Fix script tag escape
html = html.replace('<\\/script>', '</script>')

outdir = os.path.dirname(os.path.abspath(__file__))
outpath = os.path.join(outdir, '20260209_20260215_別天地_銀座_週次報告資料.html')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Generated: {outpath}')
print(f'Slides: {len(slides)}')
print(f'File size: {len(html):,} bytes')
