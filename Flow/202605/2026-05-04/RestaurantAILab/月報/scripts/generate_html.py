#!/usr/bin/env python3
"""
BFA 2026年4月 月報 HTML生成
- analytics.json を読込
- D3.jsでグラフ描画
- 配色: 月報 = ディープフォレストグリーン (#0F4C3A) + 銅色アクセント (#B45309)
"""
import json, os, sys, datetime as dt, re

ROOT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報'
DATA = json.load(open(os.path.join(ROOT, 'data/analytics.json'), encoding='utf-8'))

OUT = os.path.join(ROOT, '202604_BFA_月報.html')

def fmt_yen(n):
    if n is None: return '—'
    return f'¥{int(round(n)):,}'
def fmt_pct(n):
    if n is None: return '—'
    return f'{n*100:.1f}%'
def fmt_diff(n):
    if n is None: return '—'
    sign = '+' if n>=0 else ''
    return f'{sign}{n*100:.1f}%'
def fmt_int(n):
    if n is None: return '—'
    return f'{int(round(n)):,}'

m = DATA['monthly_summary']
apr, mar, feb, y25 = m['apr'], m['mar'], m['feb'], m['y25_apr']

# 営業日数で日平均を出す（公平比較用）
bd_apr = DATA['meta']['business_days']
bd_mar = DATA['meta']['business_days_mar']
sales_per_day_apr = apr['sales']/bd_apr if bd_apr else 0
sales_per_day_mar = mar['sales']/bd_mar if bd_mar else 0
mom_sales = apr['sales']/mar['sales']-1 if mar['sales'] else 0
mom_per_day = sales_per_day_apr/sales_per_day_mar-1 if sales_per_day_mar else 0
mom_per_person = apr['avg_per_person']/mar['avg_per_person']-1 if mar['avg_per_person'] else 0
mom_visits = apr['visits']/mar['visits']-1 if mar['visits'] else 0
mom_customers = apr['customers']/mar['customers']-1 if mar['customers'] else 0

yoy_sales = apr['sales']/y25['sales']-1 if y25['sales'] else 0
yoy_per_person = apr['avg_per_person']/y25['avg_per_person']-1 if y25['avg_per_person'] else 0
yoy_customers = apr['customers']/y25['customers']-1 if y25['customers'] else 0

# 主因分解 (客数 vs 客単価): 営業日換算で
# (sales_apr - sales_mar_perday_scaled) を客数 vs 単価で寄与分解
mar_per_day_sales = sales_per_day_mar
expected_mar_apr = mar_per_day_sales * bd_apr  # 3月日平均 x 4月営業日
diff_total = apr['sales'] - expected_mar_apr
# 客数寄与: (visits_apr - visits_mar_per_day*bd_apr) * avg_per_visit_mar
v_per_day_mar = mar['visits']/bd_mar if bd_mar else 0
visits_expected = v_per_day_mar * bd_apr
visits_diff = apr['visits'] - visits_expected
visits_contrib = visits_diff * mar['avg_per_visit']
# 単価寄与: visits_apr * (avg_per_visit_apr - avg_per_visit_mar)
unit_contrib = apr['visits'] * (apr['avg_per_visit'] - mar['avg_per_visit'])
main_driver = '客数減' if abs(visits_contrib) > abs(unit_contrib) else '客単価減'

# PL予算到達率
budget = DATA['pl']['budget_april']['sales_total']
budget_achievement = apr['sales']/budget if budget else 0

# === HTML生成 ===
# Inline styles - 月報は深いフォレストグリーン+ボルドー赤+ゴールド
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#EFEAE3;font-family:'Helvetica Neue','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif;color:#2A2421;font-size:20px;line-height:1.5}
.slide{width:1280px;height:720px;position:relative;overflow:hidden;background:#fff;margin:0 auto}
@media screen{.slide{margin:0 auto 28px;box-shadow:0 4px 20px rgba(0,0,0,.12)}}
@page{size:1280px 720px;margin:0}
@media print{*{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}body{margin:0;padding:0;background:#fff;width:1280px}.slide{page-break-after:always;page-break-inside:avoid;break-after:page;break-inside:avoid;box-shadow:none;margin:0;width:1280px;height:720px}.slide:last-child{page-break-after:auto}}
/* 月報 配色: ディープフォレスト + 銅 + ゴールド */
.slide-title{background:linear-gradient(135deg,#0F4C3A 0%,#08321F 60%,#1F1A18 100%);display:flex;flex-direction:column;justify-content:center;align-items:center;color:#fff}
.slide-title h1{font-size:54px;font-weight:800;letter-spacing:3px;margin-top:20px}
.slide-title h2{font-size:30px;font-weight:400;margin-top:14px;opacity:.9}
.slide-title .badge{background:#B45309;color:#fff;padding:8px 22px;border-radius:30px;font-size:18px;font-weight:700;letter-spacing:2px;margin-bottom:10px}
.slide-title p{font-size:18px;margin-top:24px;opacity:.7}
.slide-title .accent{font-size:14px;letter-spacing:6px;color:#B45309;margin-top:16px;font-weight:700}
.slide-header{background:#0F4C3A;color:#fff;padding:14px 40px;display:flex;align-items:center;justify-content:space-between}
.slide-header h2{font-size:30px;font-weight:700}
.slide-header .ch-badge{background:#B45309;color:#fff;padding:4px 14px;border-radius:20px;font-size:16px;font-weight:700;margin-right:12px}
.slide-header .pn{font-size:15px;opacity:.7}
.msg-bar{background:#FDF7ED;border-left:5px solid #B45309;padding:12px 40px;font-size:21px;font-weight:700;color:#1F1A18}
.slide-body{padding:14px 40px;overflow:hidden;height:calc(100% - 110px)}
.kpi-grid{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:8px}
.kpi-card{background:#F5F1EA;border:1px solid #D9CCB6;border-radius:12px;padding:14px 16px;text-align:center;flex:1;min-width:170px;max-width:230px}
.kpi-label{display:block;font-size:16px;color:#73625A;margin-bottom:4px;font-weight:600}
.kpi-value{display:block;font-size:36px;font-weight:800;color:#1F1A18;line-height:1.1}
.kpi-sub{display:block;font-size:16px;margin-top:2px;font-weight:600}
.kpi-change{display:block;font-size:18px;font-weight:700;margin-top:6px}
.pos{color:#0F4C3A}.neg{color:#B91C1C}.neu{color:#73625A}
.warn{color:#B45309}
.two-col{display:flex;gap:22px;height:100%}
.col-chart{flex:2}.col-text{flex:1;font-size:18px;line-height:1.6}
.col-half{flex:1}
.dt{width:100%;border-collapse:collapse;font-size:18px}
.dt th{background:#0F4C3A;color:#fff;padding:9px 12px;text-align:left;font-weight:700;font-size:17px}
.dt td{padding:7px 12px;border-bottom:1px solid #E5DCC9}
.dt tr:nth-child(even) td{background:#F9F6F0}
.dt .r{text-align:right}.dt .b{font-weight:700}.dt .c{text-align:center}
.dt .highlight-row td{background:#FDF7ED;font-weight:700}
.dt .best td{background:#EAF5EE}.dt .worst td{background:#FBEDED}
.dt.sm{font-size:16px}.dt.sm th{padding:6px 10px;font-size:14px}.dt.sm td{padding:5px 10px}
.sec-title{font-size:24px;font-weight:800;color:#1F1A18;margin:8px 0 6px;padding-left:12px;border-left:5px solid #0F4C3A}
.sec-title.g{border-color:#0F4C3A}.sec-title.r{border-color:#B91C1C}.sec-title.o{border-color:#B45309}.sec-title.b{border-color:#1E40AF}
.bl{list-style:none;padding:0}
.bl li{padding:5px 0 5px 22px;position:relative;font-size:18px;line-height:1.6}
.bl li::before{content:'●';position:absolute;left:0;color:#0F4C3A;font-size:11px;top:11px}
.bl.g li::before{color:#0F4C3A}.bl.r li::before{color:#B91C1C}.bl.o li::before{color:#B45309}
.nl{list-style:none;padding:0;counter-reset:nl}
.nl li{padding:6px 0 6px 36px;position:relative;font-size:18px;line-height:1.5;counter-increment:nl}
.nl li::before{content:counter(nl);position:absolute;left:0;width:26px;height:26px;background:#0F4C3A;color:#fff;border-radius:50%;text-align:center;line-height:26px;font-size:14px;font-weight:700}
.nl.g li::before{background:#0F4C3A}.nl.r li::before{background:#B91C1C}.nl.o li::before{background:#B45309}
.qb{border-left:4px solid #0F4C3A;padding:9px 16px;margin:6px 0;background:#F5F1EA;font-size:17px;line-height:1.5}
.qb .qd{font-weight:700;color:#1F1A18;margin-bottom:3px;font-size:17px}
.note-box{background:#EAF5EE;border-radius:10px;border-left:5px solid #0F4C3A;padding:12px 18px;margin-top:8px;font-size:18px;line-height:1.5;font-weight:600}
.warn-box{background:#FBEDED;border-radius:10px;border-left:5px solid #B91C1C;padding:12px 18px;margin-top:8px;font-size:18px;line-height:1.5;font-weight:600}
.info-box{background:#FDF7ED;border-radius:10px;border-left:5px solid #B45309;padding:12px 18px;margin-top:8px;font-size:18px;line-height:1.5;font-weight:600}
.card{background:#F9F6F0;border:1px solid #E5DCC9;border-radius:12px;padding:14px 18px;margin:6px 0}
.card-title{font-size:20px;font-weight:800;margin-bottom:4px}
.card-title.g{color:#0F4C3A}.card-title.r{color:#B91C1C}.card-title.o{color:#B45309}
.big-num{font-size:42px;font-weight:800;line-height:1.1;color:#1F1A18}
.big-label{font-size:16px;color:#73625A;font-weight:600}
.emphasis{font-size:26px;font-weight:800}
strong{font-weight:700}
.assumption-box{background:#FFF;border:1px dashed #B45309;border-radius:10px;padding:14px 20px;margin-top:14px;font-size:15px;line-height:1.5}
.assumption-box h4{color:#B45309;font-size:17px;margin-bottom:6px}
.assumption-box ul{padding-left:22px}
.assumption-box li{font-size:14px;padding:1px 0}
.tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:14px;font-weight:700;margin-right:6px}
.tag-kanban{background:#0F4C3A;color:#fff}
.tag-junkanban{background:#B45309;color:#fff}
.tag-seiri{background:#B91C1C;color:#fff}
.tag-data{background:#73625A;color:#fff}
.data-gap{background:#FBEDED;border:2px dashed #B91C1C;color:#B91C1C;padding:10px 16px;border-radius:8px;font-weight:700;margin:8px 0}
"""

# JS for D3 charts
JS_CHARTS = """
const DATA = __DATA_PLACEHOLDER__;

function fmtYen(n){return '¥'+Math.round(n).toLocaleString('ja-JP')}
function fmtK(n){if(Math.abs(n)>=1e6)return Math.round(n/1e5)/10+'M'; if(Math.abs(n)>=1e3)return Math.round(n/100)/10+'k'; return n.toString()}

// === Chart 1: 日次売上推移 (折れ線+棒) ===
function chartDaily(){
  const el = document.getElementById('chart-daily');
  if(!el) return;
  const W=1100,H=320,M={t:30,r:60,b:55,l:70};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const data = DATA.daily.map(d=>({date:d.date, sales:d.sales, customers:d.customers, weekday:d.weekday}));
  const x = d3.scaleBand().domain(data.map(d=>d.date)).range([M.l,W-M.r]).padding(0.2);
  const y = d3.scaleLinear().domain([0, d3.max(data,d=>d.sales)*1.15]).range([H-M.b,M.t]);
  const y2 = d3.scaleLinear().domain([0, d3.max(data,d=>d.customers)*1.15]).range([H-M.b,M.t]);
  // bars (sales)
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.date)).attr('y',d=>y(d.sales)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.sales))
    .attr('fill',d=>['土','金'].includes(d.weekday)?'#B45309':'#0F4C3A')
    .attr('opacity',0.85);
  // line (customers)
  const line = d3.line().x(d=>x(d.date)+x.bandwidth()/2).y(d=>y2(d.customers));
  svg.append('path').datum(data).attr('fill','none').attr('stroke','#1F1A18').attr('stroke-width',2.5).attr('d',line);
  svg.append('g').selectAll('circle').data(data).enter().append('circle')
    .attr('cx',d=>x(d.date)+x.bandwidth()/2).attr('cy',d=>y2(d.customers))
    .attr('r',3).attr('fill','#1F1A18');
  // x axis
  svg.append('g').attr('transform',`translate(0,${H-M.b})`)
    .call(d3.axisBottom(x).tickFormat(d=>d.slice(8)+'\\n'+data.find(x=>x.date===d).weekday).tickSize(4))
    .selectAll('text').style('font-size','11px');
  // y axis sales
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+fmtK(d)));
  // y axis customers
  svg.append('g').attr('transform',`translate(${W-M.r},0)`).call(d3.axisRight(y2).ticks(5));
  // labels
  svg.append('text').attr('x',M.l).attr('y',M.t-10).attr('font-size',13).attr('fill','#0F4C3A').text('■ 売上 (棒, 左軸) / ▲ 客数 (折線, 右軸)');
}

// === Chart 2: 曜日別ヒートマップ ===
function chartHeatmap(){
  const el = document.getElementById('chart-heatmap');
  if(!el) return;
  const W=1100,H=300,M={t:30,r:30,b:40,l:80};
  const wds=['月','火','水','木','金','土','日'];
  const buckets=['~18時','18-20時','20-22時','22-24時','24時~'];
  const heat = DATA.heatmap;
  const cellW=(W-M.l-M.r)/buckets.length;
  const cellH=(H-M.t-M.b)/wds.length;
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const maxV = d3.max(heat,d=>d.sales);
  const color = d3.scaleSequential([0,maxV],d3.interpolateGreens);
  for(const d of heat){
    const i = wds.indexOf(d.weekday); const j = buckets.indexOf(d.bucket);
    if(i<0||j<0) continue;
    svg.append('rect').attr('x',M.l+j*cellW).attr('y',M.t+i*cellH)
      .attr('width',cellW-2).attr('height',cellH-2)
      .attr('fill', d.sales>0?color(d.sales):'#F0EBE0').attr('rx',4);
    if(d.sales>0){
      svg.append('text').attr('x',M.l+j*cellW+cellW/2).attr('y',M.t+i*cellH+cellH/2-2)
        .attr('text-anchor','middle').attr('font-size',12).attr('font-weight',700)
        .attr('fill', d.sales>maxV*0.5?'#fff':'#1F1A18').text(fmtK(d.sales));
      svg.append('text').attr('x',M.l+j*cellW+cellW/2).attr('y',M.t+i*cellH+cellH/2+12)
        .attr('text-anchor','middle').attr('font-size',10)
        .attr('fill', d.sales>maxV*0.5?'#fff':'#73625A').text(d.visits+'件');
    }
  }
  // labels
  for(let i=0;i<wds.length;i++){
    svg.append('text').attr('x',M.l-10).attr('y',M.t+i*cellH+cellH/2+5)
      .attr('text-anchor','end').attr('font-size',13).attr('font-weight',700).text(wds[i]);
  }
  for(let j=0;j<buckets.length;j++){
    svg.append('text').attr('x',M.l+j*cellW+cellW/2).attr('y',M.t-8)
      .attr('text-anchor','middle').attr('font-size',12).attr('font-weight',700).text(buckets[j]);
  }
}

// === Chart 3: 商品出数Top15 (横棒) ===
function chartTopProducts(){
  const el = document.getElementById('chart-products');
  if(!el) return;
  const data = DATA.products.top_qty_30.slice(0,15);
  const W=1100,H=400,M={t:20,r:80,b:30,l:230};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const y = d3.scaleBand().domain(data.map(d=>d.name)).range([M.t,H-M.b]).padding(0.15);
  const x = d3.scaleLinear().domain([0,d3.max(data,d=>d.qty)*1.1]).range([M.l,W-M.r]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',M.l).attr('y',d=>y(d.name)).attr('width',d=>x(d.qty)-M.l).attr('height',y.bandwidth())
    .attr('fill','#0F4C3A').attr('opacity',0.85);
  svg.append('g').selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.qty)+5).attr('y',d=>y(d.name)+y.bandwidth()/2+4)
    .attr('font-size',12).attr('fill','#1F1A18').attr('font-weight',700)
    .text(d=>d.qty);
  // y axis (product names)
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).tickSize(0))
    .selectAll('text').style('font-size','12px').style('font-weight','600');
  svg.selectAll('.domain').remove();
}

// === Chart 4: カテゴリ別売上構成 (積み上げ) ===
function chartCategory(){
  const el = document.getElementById('chart-category');
  if(!el) return;
  const data = DATA.category_share.slice(0,8);
  const W=1100,H=320,M={t:30,r:30,b:60,l:60};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(data.map(d=>d.category)).range([M.l,W-M.r]).padding(0.25);
  const y = d3.scaleLinear().domain([0,d3.max(data,d=>d.sales)*1.15]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.category)).attr('y',d=>y(d.sales)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.sales)).attr('fill','#0F4C3A').attr('opacity',0.85);
  svg.append('g').selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.category)+x.bandwidth()/2).attr('y',d=>y(d.sales)-6)
    .attr('text-anchor','middle').attr('font-size',13).attr('fill','#1F1A18').attr('font-weight',700)
    .text(d=>(d.sales_share*100).toFixed(1)+'%');
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x))
    .selectAll('text').attr('transform','rotate(-25)').attr('text-anchor','end').style('font-size','11px');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+fmtK(d)));
}

// === Chart 5: 客単価ヒストグラム ===
function chartPpHist(){
  const el = document.getElementById('chart-pphist');
  if(!el) return;
  const data = DATA.avg_per_person_dist.histogram;
  const W=1100,H=280,M={t:20,r:30,b:50,l:60};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(data.map(d=>d.bucket)).range([M.l,W-M.r]).padding(0.1);
  const y = d3.scaleLinear().domain([0,d3.max(data,d=>d.count)*1.15]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.bucket)).attr('y',d=>y(d.count)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.count)).attr('fill','#B45309').attr('opacity',0.85);
  svg.append('g').selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.bucket)+x.bandwidth()/2).attr('y',d=>y(d.count)-4)
    .attr('text-anchor','middle').attr('font-size',12).attr('fill','#1F1A18').text(d=>d.count||'');
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x))
    .selectAll('text').style('font-size','11px');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5));
}

// === Chart 6: 月次推移(売上/利益) ===
function chartMonthlyTrend(){
  const el = document.getElementById('chart-monthly-trend');
  if(!el) return;
  // POS売上は月次でJan-Apr計算
  const months = ['2026-01','2026-02','2026-03','2026-04'];
  const sales = [
    DATA.pl.actuals_2026['2026-01'].sales_total,
    DATA.pl.actuals_2026['2026-02'].sales_total,
    DATA.pl.actuals_2026['2026-03'].sales_total,
    DATA.monthly_summary.apr.sales,
  ];
  const exp = [
    DATA.pl.actuals_2026['2026-01'].expenses_total,
    DATA.pl.actuals_2026['2026-02'].expenses_total,
    null, null  // 3,4月実績未確定
  ];
  const budget_apr_sales = DATA.pl.budget_april.sales_total;
  const budget_apr_exp = DATA.pl.budget_april.expenses_total;

  const W=1100,H=320,M={t:40,r:40,b:50,l:80};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(months).range([M.l,W-M.r]).padding(0.3);
  const allVals = [...sales,...exp.filter(v=>v!=null), budget_apr_sales, budget_apr_exp];
  const y = d3.scaleLinear().domain([0, d3.max(allVals)*1.15]).range([H-M.b,M.t]);
  // sales line
  const lineS = d3.line().x((d,i)=>x(months[i])+x.bandwidth()/2).y(d=>y(d));
  svg.append('path').datum(sales).attr('fill','none').attr('stroke','#0F4C3A').attr('stroke-width',3).attr('d',lineS);
  svg.selectAll('circle.s').data(sales).enter().append('circle').attr('class','s')
    .attr('cx',(d,i)=>x(months[i])+x.bandwidth()/2).attr('cy',d=>y(d)).attr('r',5).attr('fill','#0F4C3A');
  svg.selectAll('text.s').data(sales).enter().append('text').attr('class','s')
    .attr('x',(d,i)=>x(months[i])+x.bandwidth()/2).attr('y',d=>y(d)-10)
    .attr('text-anchor','middle').attr('font-size',12).attr('font-weight',700).attr('fill','#0F4C3A')
    .text(d=>'¥'+fmtK(d));
  // expense bars
  for(let i=0;i<exp.length;i++){
    if(exp[i]==null) continue;
    svg.append('rect').attr('x',x(months[i])).attr('y',y(exp[i])).attr('width',x.bandwidth())
      .attr('height',H-M.b-y(exp[i])).attr('fill','#B91C1C').attr('opacity',0.65);
    svg.append('text').attr('x',x(months[i])+x.bandwidth()/2).attr('y',y(exp[i])-4)
      .attr('text-anchor','middle').attr('font-size',11).attr('font-weight',700).attr('fill','#B91C1C').text('¥'+fmtK(exp[i]));
  }
  // budget april (dashed)
  svg.append('line').attr('x1',x(months[3])).attr('x2',x(months[3])+x.bandwidth())
    .attr('y1',y(budget_apr_sales)).attr('y2',y(budget_apr_sales))
    .attr('stroke','#B45309').attr('stroke-width',2).attr('stroke-dasharray','5,4');
  svg.append('text').attr('x',x(months[3])+x.bandwidth()/2).attr('y',y(budget_apr_sales)-6)
    .attr('text-anchor','middle').attr('font-size',11).attr('fill','#B45309').attr('font-weight',700)
    .text('予算 ¥'+fmtK(budget_apr_sales));
  // axes
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x));
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(6).tickFormat(d=>'¥'+fmtK(d)));
  // legend
  svg.append('text').attr('x',M.l).attr('y',M.t-15).attr('font-size',13).attr('fill','#0F4C3A').attr('font-weight',700).text('● 売上 (折線)  ');
  svg.append('text').attr('x',M.l+130).attr('y',M.t-15).attr('font-size',13).attr('fill','#B91C1C').attr('font-weight',700).text('■ 費用 (棒)  ');
  svg.append('text').attr('x',M.l+220).attr('y',M.t-15).attr('font-size',13).attr('fill','#B45309').attr('font-weight',700).text('--- 予算');
}

// === Chart 7: 客層 (人数別) ===
function chartParty(){
  const el = document.getElementById('chart-party');
  if(!el) return;
  const data = DATA.party_size;
  const W=540,H=240,M={t:20,r:30,b:30,l:80};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const y = d3.scaleBand().domain(data.map(d=>d.bucket)).range([M.t,H-M.b]).padding(0.15);
  const x = d3.scaleLinear().domain([0,d3.max(data,d=>d.visits)*1.15]).range([M.l,W-M.r]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',M.l).attr('y',d=>y(d.bucket)).attr('width',d=>x(d.visits)-M.l).attr('height',y.bandwidth())
    .attr('fill','#0F4C3A');
  svg.selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.visits)+5).attr('y',d=>y(d.bucket)+y.bandwidth()/2+4)
    .attr('font-size',12).attr('font-weight',700).text(d=>d.visits+'件');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).tickSize(0))
    .selectAll('text').style('font-size','12px').style('font-weight','600');
  svg.selectAll('.domain').remove();
}

// === Chart 8: 時間帯別 ===
function chartHour(){
  const el = document.getElementById('chart-hour');
  if(!el) return;
  const data = DATA.hour_summary;
  const W=540,H=240,M={t:20,r:30,b:50,l:60};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(data.map(d=>d.bucket)).range([M.l,W-M.r]).padding(0.2);
  const y = d3.scaleLinear().domain([0,d3.max(data,d=>d.sales)*1.15]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.bucket)).attr('y',d=>y(d.sales)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.sales)).attr('fill','#B45309').attr('opacity',0.85);
  svg.selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.bucket)+x.bandwidth()/2).attr('y',d=>y(d.sales)-4)
    .attr('text-anchor','middle').attr('font-size',11).attr('font-weight',700).attr('fill','#1F1A18')
    .text(d=>'¥'+fmtK(d.sales));
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x)).selectAll('text').style('font-size','11px');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+fmtK(d)));
}

document.addEventListener('DOMContentLoaded',()=>{
  chartDaily(); chartHeatmap(); chartTopProducts(); chartCategory();
  chartPpHist(); chartMonthlyTrend(); chartParty(); chartHour();
});
"""

# === スライド組み立て ===
slides = []
TOTAL = 16  # 表紙 + 0章サマリ + 1〜9章 + 付録3枚 + 末尾

# Slide 1: 表紙
slides.append(f'''<div class="slide slide-title" id="slide-1">
<div class="badge">📅 月報 (Monthly)</div>
<h1>BAR FIVE Arrows</h1>
<h2>月次経営判断資料</h2>
<p>2026年4月（2026-04-01 〜 2026-04-30）</p>
<div class="accent">EXECUTIVE MONTHLY REVIEW</div>
<p style="margin-top:36px;font-size:13px;opacity:.5">分析観点ガイド v2 準拠 / 全10章フル章立て</p>
</div>''')

# Slide 2: 前提ボックス & 目次
top_qty3 = DATA['products']['top_qty_30'][:3]
slides.append(f'''<div class="slide" id="slide-2">
<div class="slide-header"><h2><span class="ch-badge">前提</span>本月報の読み方</h2><span class="pn">2 / {TOTAL}</span></div>
<div class="msg-bar">月報＝経営判断書 / 週報＝施策修正書 / 日報＝兆候キャッチ — 本書は意思決定論点に絞る</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title o">数字の起点（前提）</div>
<ul class="bl o">
<li><strong>会計単位</strong>: POS account_id 単位 (1グループ＝1会計)</li>
<li><strong>客数</strong>: 会計人数 (customer_count) の合計</li>
<li><strong>客単価</strong>: 売上 ÷ 会計人数 (一人あたり)</li>
<li><strong>金額</strong>: POS account_total (税込推定。明示なし)</li>
<li><strong>営業日</strong>: POS会計が1件以上発生した日 (4月: {bd_apr}日 / 3月: {bd_mar}日)</li>
</ul>
<div class="sec-title r">データ欠損 (要追補)</div>
<div class="data-gap">⚠ <strong>2026年4月のPL実績</strong> (食材/ドリンク/人件費等) が新PL管理シートに未入力。第4章は <strong>予算 vs 1-2月実績の延長線</strong> で構成。</div>
<div class="data-gap">⚠ <strong>レシピシート(99品目原価)</strong> の所在未確定。第4章(B) <strong>理論原価分析は名寄せ完了後に追補</strong>。</div>
</div>
<div class="col-half">
<div class="sec-title">章立て (10章構成)</div>
<table class="dt sm">
<tr><td class="b c" style="width:40px">0</td><td>エグゼクティブサマリ</td></tr>
<tr><td class="b c">1</td><td>売上構造の判定 (客数 vs 単価)</td></tr>
<tr><td class="b c">2</td><td>商品戦略の判定 (看板/整理候補)</td></tr>
<tr><td class="b c">3</td><td>客単価の作られ方</td></tr>
<tr><td class="b c">4</td><td><strong>利益構造の判定 ★最重要</strong></td></tr>
<tr><td class="b c">5</td><td>コンセプト定着度</td></tr>
<tr><td class="b c">6</td><td>曜日／時間帯サマリ</td></tr>
<tr><td class="b c">7</td><td>施策の結論</td></tr>
<tr><td class="b c">8</td><td>構造的ボトルネック</td></tr>
<tr><td class="b c">9</td><td>翌月の意思決定論点 (3〜5本)</td></tr>
</table>
<div class="info-box">レビュー観点: 同梱の <code>review_checklist.md</code> 参照</div>
</div>
</div>
</div>
</div>''')

# Slide 3: 第0章 エグゼクティブサマリ
# 結論3行 + 翌月論点3つ
exec_concl = []
# 1. 売上着地と主因
exec_concl.append(f"<strong>当月売上は{fmt_yen(apr['sales'])}</strong>（24営業日）。日平均は<strong>{fmt_yen(sales_per_day_apr)}</strong>で前月比{fmt_diff(mom_per_day)}。日平均で見ても明確な減少トレンドで、<strong>主因は{main_driver}</strong>（営業日換算で客数寄与{fmt_yen(visits_contrib)}, 単価寄与{fmt_yen(unit_contrib)}）。")
# 2. PL状況
exec_concl.append(f"<strong>4月予算{fmt_yen(budget)}に対し売上達成率{(budget_achievement*100):.1f}%</strong>。1-2月の利益推移（1月+¥290k → 2月▲¥164k）と4月予算（▲¥155k見込）から、<strong>4月実績未入力ながら赤字基調が継続</strong>している前提で経営判断を要する。")
# 3. コンセプト方面
course_share_apr = apr['course_share']
course_share_mar = mar['course_share']
exec_concl.append(f"<strong>コース利用率{(course_share_apr*100):.1f}%</strong>（3月{(course_share_mar*100):.1f}%から大幅低下）。一方で<strong>1組あたり人数は{apr['avg_party_size']:.1f}人</strong>と3月の{mar['avg_party_size']:.1f}人より増加 → <strong>団体・大人数比率は上がったがコース化が機能していない</strong>。コース提案の動線が壊れている兆候。")

next_decisions = [
    "コース提案フロー再構築 — 4月コース利用率1.6%は構造的逸脱（3月10.1%）。価格訴求／提案タイミング／メニュー構成の3点を月内に再設計するか判断する。",
    "5月の集客強化策の選定 — POS営業日24日／日平均¥95.9k は4月予算到達ラインを大きく下回る。SNS投下／予約導線（4月予約0%）／媒体の中で「翌月に効く」1-2本を特定する。",
    "PL実績入力ガバナンス — 4月実績が連休明け時点で未入力のままだと月報の利益判断ができない。月初5営業日以内のPL確定をルール化するか判断する。",
]

slides.append(f'''<div class="slide" id="slide-3">
<div class="slide-header"><h2><span class="ch-badge">第0章</span>エグゼクティブサマリ</h2><span class="pn">3 / {TOTAL}</span></div>
<div class="msg-bar">結論3行 + 翌月の意思決定論点3つ</div>
<div class="slide-body">
<div class="kpi-grid" style="margin-bottom:6px">
<div class="kpi-card"><span class="kpi-label">売上</span><span class="kpi-value">{fmt_yen(apr['sales'])}</span><span class="kpi-change neg">{fmt_diff(mom_sales)} 前月比</span><span class="kpi-sub neg">{fmt_diff(yoy_sales)} 前年比</span></div>
<div class="kpi-card"><span class="kpi-label">客数</span><span class="kpi-value">{fmt_int(apr['customers'])}<small style="font-size:18px">人</small></span><span class="kpi-change neg">{fmt_diff(mom_customers)} 前月比</span><span class="kpi-sub neg">{fmt_diff(yoy_customers)} 前年比</span></div>
<div class="kpi-card"><span class="kpi-label">客単価</span><span class="kpi-value">{fmt_yen(apr['avg_per_person'])}</span><span class="kpi-change neg">{fmt_diff(mom_per_person)} 前月比</span><span class="kpi-sub neg">{fmt_diff(yoy_per_person)} 前年比</span></div>
<div class="kpi-card"><span class="kpi-label">日平均売上</span><span class="kpi-value" style="font-size:30px">{fmt_yen(sales_per_day_apr)}</span><span class="kpi-change neg">{fmt_diff(mom_per_day)} 前月比</span><span class="kpi-sub">営業日 {bd_apr}日</span></div>
<div class="kpi-card"><span class="kpi-label">予算到達</span><span class="kpi-value warn">{(budget_achievement*100):.1f}<small>%</small></span><span class="kpi-change warn">予算 {fmt_yen(budget)}</span><span class="kpi-sub warn">未達 {fmt_yen(budget-apr['sales'])}</span></div>
</div>
<div class="sec-title r">⚠ 結論3行</div>
<ol class="nl r">
<li>{exec_concl[0]}</li>
<li>{exec_concl[1]}</li>
<li>{exec_concl[2]}</li>
</ol>
<div class="sec-title o">→ 翌月の意思決定論点（第9章で詳述）</div>
<ol class="nl o">
<li>{next_decisions[0]}</li>
<li>{next_decisions[1]}</li>
<li>{next_decisions[2]}</li>
</ol>
</div>
</div>''')

# Slide 4: 第1章 売上構造の判定 (客数 vs 客単価)
slides.append(f'''<div class="slide" id="slide-4">
<div class="slide-header"><h2><span class="ch-badge">第1章</span>売上構造の判定</h2><span class="pn">4 / {TOTAL}</span></div>
<div class="msg-bar">主因は <strong>{main_driver}</strong>: 客数寄与{fmt_yen(visits_contrib)} vs 単価寄与{fmt_yen(unit_contrib)} (営業日換算)</div>
<div class="slide-body">
<div id="chart-daily" style="height:330px"></div>
<div class="two-col" style="margin-top:6px">
<div class="col-half">
<div class="sec-title">月次主因分解 (営業日換算)</div>
<table class="dt sm">
<tr><th>項目</th><th class="r">4月実績</th><th class="r">3月実績</th><th class="r">差分(月)</th></tr>
<tr><td>売上</td><td class="r b">{fmt_yen(apr['sales'])}</td><td class="r">{fmt_yen(mar['sales'])}</td><td class="r neg">{fmt_diff(mom_sales)}</td></tr>
<tr><td>会計件数</td><td class="r b">{apr['visits']}</td><td class="r">{mar['visits']}</td><td class="r neg">{fmt_diff(mom_visits)}</td></tr>
<tr><td>客数</td><td class="r b">{apr['customers']}</td><td class="r">{mar['customers']}</td><td class="r neg">{fmt_diff(mom_customers)}</td></tr>
<tr><td>1組人数</td><td class="r b">{apr['avg_party_size']:.2f}人</td><td class="r">{mar['avg_party_size']:.2f}人</td><td class="r pos">+{(apr['avg_party_size']-mar['avg_party_size']):.2f}</td></tr>
<tr><td>客単価(1人)</td><td class="r b">{fmt_yen(apr['avg_per_person'])}</td><td class="r">{fmt_yen(mar['avg_per_person'])}</td><td class="r neg">{fmt_diff(mom_per_person)}</td></tr>
<tr class="highlight-row"><td>日平均売上</td><td class="r b">{fmt_yen(sales_per_day_apr)}</td><td class="r">{fmt_yen(sales_per_day_mar)}</td><td class="r neg b">{fmt_diff(mom_per_day)}</td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title r">主因の特定 (1行で明言)</div>
<div class="warn-box"><strong>{main_driver}が決定的に効いた</strong>。営業日換算の差分内訳: 客数{fmt_yen(visits_contrib)} / 単価{fmt_yen(unit_contrib)}</div>
<ul class="bl">
<li><strong>会計件数</strong>: 188 → 126 ({fmt_diff(mom_visits)}) = <strong>62件減</strong></li>
<li><strong>1組人数</strong>: 2.77 → 3.62人 (+0.85) = <strong>団体化</strong>進行</li>
<li><strong>客単価</strong>: ¥5,609 → ¥5,046 = <strong>1人あたり▲563円</strong></li>
<li><strong>予約比率</strong>: 4月 {(apr['reservation_share']*100):.1f}% (POS上0件) ⚠</li>
<li><strong>コース率</strong>: 10.1% → 1.6% = <strong>急落</strong></li>
</ul>
<div class="info-box">団体化(1組+0.85人)は来たが、コース提案がほぼ機能せず1人あたり単価が落ちた構造</div>
</div>
</div>
</div>
</div>''')

# Slide 5: 第1章補足 - 日次変動と予約/ウォークイン
seg = DATA['segments']['apr']
seg_m = DATA['segments']['mar']
top3_days = sorted(DATA['daily'], key=lambda d:-d['sales'])[:3]
worst3_days = sorted(DATA['daily'], key=lambda d:d['sales'])[:3]
slides.append(f'''<div class="slide" id="slide-5">
<div class="slide-header"><h2><span class="ch-badge">第1章補足</span>日次変動・客層別売上</h2><span class="pn">5 / {TOTAL}</span></div>
<div class="msg-bar">団体貸切が売上の山を作る一方、予約POS記録ゼロは入力欠落の疑い</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title g">月内ベスト3日 (売上)</div>
<table class="dt sm">
<tr><th>日付</th><th>曜日</th><th class="r">売上</th><th class="r">会計</th><th class="r">客数</th><th class="r">1人単価</th></tr>
{''.join(f"<tr class='best'><td>{d['date'][5:]}</td><td>{d['weekday']}</td><td class='r b'>{fmt_yen(d['sales'])}</td><td class='r'>{d['visits']}</td><td class='r'>{d['customers']}</td><td class='r'>{fmt_yen(d['avg_per_person'])}</td></tr>" for d in top3_days)}
</table>
<div class="sec-title r" style="margin-top:14px">月内ワースト3日 (売上)</div>
<table class="dt sm">
<tr><th>日付</th><th>曜日</th><th class="r">売上</th><th class="r">会計</th><th class="r">客数</th><th class="r">1人単価</th></tr>
{''.join(f"<tr class='worst'><td>{d['date'][5:]}</td><td>{d['weekday']}</td><td class='r b'>{fmt_yen(d['sales'])}</td><td class='r'>{d['visits']}</td><td class='r'>{d['customers']}</td><td class='r'>{fmt_yen(d['avg_per_person'])}</td></tr>" for d in worst3_days)}
</table>
</div>
<div class="col-half">
<div class="sec-title o">予約 vs ウォークイン (4月)</div>
<table class="dt sm">
<tr><th>区分</th><th class="r">会計</th><th class="r">売上</th><th class="r">構成比</th></tr>
<tr><td>予約あり</td><td class="r">{seg['reservation']['visits']}</td><td class="r">{fmt_yen(seg['reservation']['sales'])}</td><td class="r">{seg['reservation']['sales']/apr['sales']*100:.1f}%</td></tr>
<tr><td>ウォークイン</td><td class="r b">{seg['walkin']['visits']}</td><td class="r b">{fmt_yen(seg['walkin']['sales'])}</td><td class="r b">{seg['walkin']['sales']/apr['sales']*100:.1f}%</td></tr>
</table>
<div class="data-gap" style="margin-top:8px">⚠ POS記録上「予約あり」が0件。<strong>POSで予約フラグが入力されていない可能性</strong>。日報には貸切等の予約言及あり (4/3 24名様部門送別会など)</div>
<div class="sec-title o" style="margin-top:14px">コース vs アラカルト</div>
<table class="dt sm">
<tr><th>区分</th><th class="r">会計</th><th class="r">売上</th><th class="r">単価</th></tr>
<tr><td>コース</td><td class="r b">{seg['course']['visits']}</td><td class="r b">{fmt_yen(seg['course']['sales'])}</td><td class="r b">{fmt_yen(seg['course']['sales']/seg['course']['visits']) if seg['course']['visits'] else '—'}</td></tr>
<tr><td>アラカルト</td><td class="r">{seg['alacarte']['visits']}</td><td class="r">{fmt_yen(seg['alacarte']['sales'])}</td><td class="r">{fmt_yen(seg['alacarte']['sales']/seg['alacarte']['visits']) if seg['alacarte']['visits'] else '—'}</td></tr>
</table>
<div class="info-box">コース2件で売上¥117,000(構成5.1%)。3月の19件・¥626kから激減</div>
</div>
</div>
</div>
</div>''')

# Slide 6: 第2章 商品戦略の判定 - Top出数
top10_qty = DATA['products']['top_qty_30'][:12]
top10_sales = DATA['products']['top_sales_30'][:12]
slides.append(f'''<div class="slide" id="slide-6">
<div class="slide-header"><h2><span class="ch-badge">第2章</span>商品戦略の判定 — 出数Top15</h2><span class="pn">6 / {TOTAL}</span></div>
<div class="msg-bar">tablecharge / ハウスハイボール / 森のジントニックの3軸が出数を支える</div>
<div class="slide-body">
<div id="chart-products" style="height:380px"></div>
<div class="two-col" style="margin-top:6px">
<div class="col-half">
<div class="sec-title o">注釈</div>
<ul class="bl">
<li><strong>tablecharge (290件)</strong>: 全会計に発生する課金。会計数の指標</li>
<li><strong>ハウスハイボール (152本)</strong>: 出数1位の単独ドリンク → <span class="tag tag-kanban">看板</span>候補の確固たる地位</li>
<li><strong>森のジントニック (82本)</strong>: BFAコンセプト商品 → <span class="tag tag-kanban">看板</span>定着</li>
<li><strong>ガージェリー (39本)</strong>: ビール系の中核 → <span class="tag tag-junkanban">準看板</span></li>
</ul>
</div>
<div class="col-half">
<div class="sec-title o">レシピマスタ未取得のため判定保留 (4/30時点)</div>
<div class="data-gap">⚠ 99品目の<strong>原価/位置付けタグ</strong>が未連携。<br>看板/準看板/整理候補の<strong>正式選定は名寄せマスタ完成後</strong>。本資料では<strong>POS出数・売上のみで暫定推定</strong>。</div>
</div>
</div>
</div>
</div>''')

# Slide 7: 第2章補足 売上ランキング
slides.append(f'''<div class="slide" id="slide-7">
<div class="slide-header"><h2><span class="ch-badge">第2章補足</span>売上Top10 / カテゴリ構成</h2><span class="pn">7 / {TOTAL}</span></div>
<div class="msg-bar">売上1位は「その他CLPコース」¥280k — コース系2品で売上構造の<strong>15%</strong>を占有</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">商品別売上Top10</div>
<table class="dt sm">
<tr><th class="c">#</th><th>商品名</th><th class="r">売上</th><th class="r">出数</th><th class="r">前月比</th></tr>
{''.join(f"<tr><td class='c b'>{i+1}</td><td>{p['name']}</td><td class='r b'>{fmt_yen(p['sales'])}</td><td class='r'>{p['qty']}</td><td class='r {('pos' if p['qty_diff_mom']>=0 else 'neg')}'>{p['qty_diff_mom']:+d}</td></tr>" for i,p in enumerate(top10_sales[:10]))}
</table>
</div>
<div class="col-half">
<div id="chart-category" style="height:330px"></div>
<table class="dt sm" style="margin-top:8px">
<tr><th>カテゴリ</th><th class="r">構成比</th><th class="r">前月差</th></tr>
{''.join(f"<tr><td>{c['category'][:20]}</td><td class='r b'>{c['sales_share']*100:.1f}%</td><td class='r {('pos' if c['share_diff']>=0 else 'neg')}'>{c['share_diff']*100:+.1f}pt</td></tr>" for c in DATA['category_share'][:6])}
</table>
</div>
</div>
</div>
</div>''')

# Slide 8: 第2章 整理候補 (推定)
# 出数2件以下 + 売上の少ないものをピックアップ
low_movers = [p for p in DATA['products']['all'] if 1 <= p['qty'] <= 3 and p['sales'] < 5000]
low_movers_top = sorted(low_movers, key=lambda x:x['sales'])[:15]
risen = sorted([p for p in DATA['products']['all'] if p['qty_diff_mom']>=5], key=lambda x:-x['qty_diff_mom'])[:8]
fallen = sorted([p for p in DATA['products']['all'] if p['qty_mar']>=5], key=lambda x:x['qty_diff_mom'])[:8]

slides.append(f'''<div class="slide" id="slide-8">
<div class="slide-header"><h2><span class="ch-badge">第2章補足</span>動きの大きい商品 / 整理候補</h2><span class="pn">8 / {TOTAL}</span></div>
<div class="msg-bar">前月から大きく動いた商品 / 月内ほぼ動かない商品の名指し</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title g">出数 急上昇 Top8 (前月比)</div>
<table class="dt sm">
<tr><th>商品名</th><th class="r">4月</th><th class="r">3月</th><th class="r">差分</th></tr>
{''.join(f"<tr><td>{p['name'][:22]}</td><td class='r b'>{p['qty']}</td><td class='r'>{p['qty_mar']}</td><td class='r pos b'>+{p['qty_diff_mom']}</td></tr>" for p in risen)}
</table>
<div class="sec-title r" style="margin-top:10px">出数 急減少 Top8 (前月比)</div>
<table class="dt sm">
<tr><th>商品名</th><th class="r">4月</th><th class="r">3月</th><th class="r">差分</th></tr>
{''.join(f"<tr><td>{p['name'][:22]}</td><td class='r b'>{p['qty']}</td><td class='r'>{p['qty_mar']}</td><td class='r neg b'>{p['qty_diff_mom']:+d}</td></tr>" for p in fallen)}
</table>
</div>
<div class="col-half">
<div class="sec-title r">整理候補（暫定: 月内出数1-3 + 売上5k未満）</div>
<table class="dt sm">
<tr><th>商品名</th><th class="r">出数</th><th class="r">売上</th><th>カテゴリ</th></tr>
{''.join(f"<tr><td>{p['name'][:22]}</td><td class='r'>{p['qty']}</td><td class='r'>{fmt_yen(p['sales'])}</td><td>{p['category1'][:14]}</td></tr>" for p in low_movers_top[:12])}
</table>
<div class="data-gap" style="margin-top:8px">⚠ 整理判定の最終決裁は<strong>原価データ取得後</strong>。粗利貢献を加味する必要</div>
</div>
</div>
</div>
</div>''')

# Slide 9: 第3章 客単価分布
spp = DATA['avg_per_person_dist']['stats']
slides.append(f'''<div class="slide" id="slide-9">
<div class="slide-header"><h2><span class="ch-badge">第3章</span>客単価の作られ方</h2><span class="pn">9 / {TOTAL}</span></div>
<div class="msg-bar">中央値¥{int(spp['median']):,} / 平均¥{int(spp['mean']):,} — 中央値&lt;平均で<strong>少数の高単価会計が平均を押上げ</strong></div>
<div class="slide-body">
<div id="chart-pphist" style="height:280px"></div>
<div class="two-col" style="margin-top:8px">
<div class="col-half">
<div class="sec-title">客単価サマリ</div>
<table class="dt sm">
<tr><th>指標</th><th class="r">値</th></tr>
<tr><td>平均客単価</td><td class="r b">{fmt_yen(spp['mean'])}</td></tr>
<tr><td>中央値</td><td class="r b">{fmt_yen(spp['median'])}</td></tr>
<tr><td>25パーセンタイル</td><td class="r">{fmt_yen(spp['p25'])}</td></tr>
<tr><td>75パーセンタイル</td><td class="r">{fmt_yen(spp['p75'])}</td></tr>
<tr><td>90パーセンタイル</td><td class="r">{fmt_yen(spp['p90'])}</td></tr>
<tr><td>最高単価</td><td class="r warn">{fmt_yen(spp['max'])}</td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title o">注文構造</div>
<table class="dt sm">
<tr><th>指標</th><th class="r">4月</th><th class="r">3月</th></tr>
<tr><td>1会計あたり点数</td><td class="r b">{DATA['items_per_visit']['apr']['avg_items']:.2f}点</td><td class="r">{DATA['items_per_visit']['mar']['avg_items']:.2f}点</td></tr>
<tr><td>ドリンク2杯目以上比率</td><td class="r b">{DATA['items_per_visit']['apr']['drink_2plus_share']*100:.1f}%</td><td class="r">{DATA['items_per_visit']['mar']['drink_2plus_share']*100:.1f}%</td></tr>
<tr><td>コース利用率</td><td class="r b">{(apr['course_share']*100):.1f}%</td><td class="r">{(mar['course_share']*100):.1f}%</td></tr>
</table>
<div class="warn-box" style="margin-top:8px">客単価の主たる作られ方は <strong>「ドリンク2杯目以上 + 看板ジン or ハイボール」</strong>。コース構造が機能していない4月は中位帯（4-7k）が薄い分布。</div>
</div>
</div>
</div>
</div>''')

# Slide 10: 第4章 利益構造 (PL Trend) ★最重要
slides.append(f'''<div class="slide" id="slide-10">
<div class="slide-header"><h2><span class="ch-badge">第4章 ★</span>利益構造の判定 — PL推移と固定費耐性</h2><span class="pn">10 / {TOTAL}</span></div>
<div class="msg-bar">1月+¥289k → 2月▲¥164k → 3月（費用未入力）→ 4月予算▲¥155k想定。<strong>固定費 ¥1.7M前後の損益分岐に届かない月が続く</strong></div>
<div class="slide-body">
<div id="chart-monthly-trend" style="height:330px"></div>
<div class="two-col" style="margin-top:6px">
<div class="col-half">
<div class="sec-title">主要費目構成 (1月実績)</div>
<table class="dt sm">
<tr><th>費目</th><th class="r">1月</th><th class="r">2月</th><th class="r">変動性</th></tr>
<tr><td>家賃 (固定)</td><td class="r">¥1,112,859</td><td class="r">¥1,112,859</td><td>固定</td></tr>
<tr><td>人件費</td><td class="r">¥347,258</td><td class="r">¥414,487</td><td>準固定</td></tr>
<tr><td>食材</td><td class="r">¥178,182</td><td class="r">¥210,952</td><td>変動</td></tr>
<tr><td>ドリンク仕入</td><td class="r">¥203,250</td><td class="r">¥420,616</td><td>変動</td></tr>
<tr><td>水道光熱費</td><td class="r">¥79,854</td><td class="r">¥91,609</td><td>準固定</td></tr>
<tr><td>管理費</td><td class="r">¥194,481</td><td class="r">¥250,617</td><td>準変動</td></tr>
<tr><td>ローン返済</td><td class="r">¥169,154</td><td class="r">¥169,221</td><td>固定</td></tr>
<tr class="highlight-row"><td>合計</td><td class="r b">¥2,352,939</td><td class="r b">¥2,832,178</td><td></td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title r">損益分岐ラインへのギャップ</div>
<table class="dt sm">
<tr><th>シナリオ</th><th class="r">必要売上</th><th class="r">4月実績</th><th class="r">ギャップ</th></tr>
<tr><td>1月費用ベース</td><td class="r">¥2,352,939</td><td class="r b">{fmt_yen(apr['sales'])}</td><td class="r {'pos' if apr['sales']>=2352939 else 'neg'} b">{fmt_yen(apr['sales']-2352939)}</td></tr>
<tr><td>2月費用ベース</td><td class="r">¥2,832,178</td><td class="r b">{fmt_yen(apr['sales'])}</td><td class="r neg b">{fmt_yen(apr['sales']-2832178)}</td></tr>
<tr><td>4月予算ベース</td><td class="r">¥3,554,556</td><td class="r b">{fmt_yen(apr['sales'])}</td><td class="r neg b">{fmt_yen(apr['sales']-3554556)}</td></tr>
<tr><td>+CLP人件費(¥600k)</td><td class="r">¥4,154,556</td><td class="r b">{fmt_yen(apr['sales'])}</td><td class="r neg b">{fmt_yen(apr['sales']-4154556)}</td></tr>
</table>
<div class="warn-box" style="margin-top:8px"><strong>4月実績費用が2月並に膨らんだ場合、単月赤字▲¥531k</strong> (CLP人件費考慮なし)。CLP含めると▲¥1.13M。</div>
</div>
</div>
</div>
</div>''')

# Slide 11: 第4章補足 理論原価 (Placeholder)
pos_cat_summary = DATA['pl']['pos_category_april']
top_cat_lines = sorted(pos_cat_summary.items(), key=lambda x:-x[1])[:8]
slides.append(f'''<div class="slide" id="slide-11">
<div class="slide-header"><h2><span class="ch-badge">第4章補足</span>理論原価分析 (名寄せ完成後に追補)</h2><span class="pn">11 / {TOTAL}</span></div>
<div class="msg-bar">レシピマスタ確定後、商品出数 × 原価 で月次理論原価を確定し実原価との乖離を判定する</div>
<div class="slide-body">
<div class="data-gap" style="font-size:18px">⚠ <strong>レシピシート (商品一覧99品目) の所在が未確定</strong>のため、本スライドは<strong>計算枠組みと暫定数字</strong>のみ。最終理論原価率・乖離率は次回月報で追補。</div>
<div class="two-col" style="margin-top:8px">
<div class="col-half">
<div class="sec-title">理論原価計算式</div>
<div class="card">
<div class="big-num" style="font-size:22px">月次理論原価 = Σ ( 商品別月内出数(POS) × 商品別原価(レシピ) )</div>
</div>
<div class="sec-title o" style="margin-top:10px">本月の前提</div>
<ul class="bl o">
<li>4月総売上: <strong>{fmt_yen(apr['sales'])}</strong> (POS合計)</li>
<li>商品ユニーク数: <strong>{len(DATA['products']['all'])}品目</strong> (POS出数1以上)</li>
<li>レシピマスタ品目: <strong>99品目</strong> (要連携)</li>
<li>名寄せ未確定品目数: 不明 (確定後に欠損率を本スライドへ転載)</li>
</ul>
</div>
<div class="col-half">
<div class="sec-title">POSカテゴリ別売上 (理論原価分析の入口)</div>
<table class="dt sm">
<tr><th>カテゴリ</th><th class="r">売上</th><th class="r">構成比</th></tr>
{''.join(f"<tr><td>{(c[0] or '(未分類)')[:18]}</td><td class='r b'>{fmt_yen(c[1])}</td><td class='r'>{c[1]/apr['sales']*100:.1f}%</td></tr>" for c in top_cat_lines)}
</table>
<div class="info-box" style="margin-top:8px">レシピ連携後、<strong>カテゴリ別実原価率 vs 理論原価率</strong>を算出して乖離トップ3を特定する。</div>
</div>
</div>
</div>
</div>''')

# Slide 12: 第5章 コンセプト定着度
# 早時間動き
early_visits = sum(h['visits'] for h in DATA['hour_summary'] if h['bucket'] in ['~18時','18-20時'])
total_visits = apr['visits']
early_share = early_visits/total_visits if total_visits else 0
late_visits = sum(h['visits'] for h in DATA['hour_summary'] if h['bucket'] in ['22-24時','24時~'])
late_share = late_visits/total_visits if total_visits else 0
weekend_sales = sum(w['sales'] for w in DATA['weekday_summary'] if w['weekday'] in ['金','土'])
weekday_sales = sum(w['sales'] for w in DATA['weekday_summary'] if w['weekday'] not in ['金','土','日'])
sun_sales = next((w['sales'] for w in DATA['weekday_summary'] if w['weekday']=='日'),0)
weekend_share = (weekend_sales)/apr['sales'] if apr['sales'] else 0

# 看板商品の安定性
mori = next((p for p in DATA['products']['all'] if p['name']=='森のジントニック'),None)
hbh = next((p for p in DATA['products']['all'] if p['name']=='ハウスハイボール'),None)

slides.append(f'''<div class="slide" id="slide-12">
<div class="slide-header"><h2><span class="ch-badge">第5章</span>コンセプト定着度 — 「使いやすいダイニングバー／ラウンジ」化</h2><span class="pn">12 / {TOTAL}</span></div>
<div class="msg-bar">当月評価: <strong>停滞</strong> — 看板商品は安定もコース構造が逆行、平日早時間の伸びは限定的</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">用途タグ別 (POS+日報からの推定指標)</div>
<table class="dt sm">
<tr><th>軸</th><th class="r">4月</th><th class="r">参考(3月)</th><th class="c">評価</th></tr>
<tr><td>早時間 (~20時) 構成</td><td class="r b">{early_share*100:.1f}%</td><td class="r">—</td><td class="c warn">→</td></tr>
<tr><td>深夜 (22時~) 構成</td><td class="r b">{late_share*100:.1f}%</td><td class="r">—</td><td class="c warn">→</td></tr>
<tr><td>金土依存度</td><td class="r b">{weekend_share*100:.1f}%</td><td class="r">—</td><td class="c warn">→</td></tr>
<tr><td>コース利用率</td><td class="r b">{apr['course_share']*100:.1f}%</td><td class="r">{mar['course_share']*100:.1f}%</td><td class="c neg">↓ 逆行</td></tr>
<tr><td>1組人数</td><td class="r b">{apr['avg_party_size']:.2f}人</td><td class="r">{mar['avg_party_size']:.2f}人</td><td class="c pos">↑ 進行</td></tr>
</table>
<div class="sec-title o" style="margin-top:10px">看板商品の月次安定度</div>
<table class="dt sm">
<tr><th>商品</th><th class="r">4月</th><th class="r">3月</th><th class="c">判定</th></tr>
<tr><td>ハウスハイボール</td><td class="r b">{hbh['qty'] if hbh else 0}</td><td class="r">{hbh['qty_mar'] if hbh else 0}</td><td class="c {'pos' if hbh and hbh['qty_diff_mom']>=0 else 'neg'}">{('安定' if hbh and abs(hbh['qty_diff_mom'])<10 else ('上昇' if hbh and hbh['qty_diff_mom']>=10 else '低下'))}</td></tr>
<tr><td>森のジントニック</td><td class="r b">{mori['qty'] if mori else 0}</td><td class="r">{mori['qty_mar'] if mori else 0}</td><td class="c {'pos' if mori and mori['qty_diff_mom']>=0 else 'neg'}">{('安定' if mori and abs(mori['qty_diff_mom'])<10 else ('上昇' if mori and mori['qty_diff_mom']>=10 else '低下'))}</td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title">日報から読む来店動機 (4月20日分集計)</div>
<ul class="bl">
<li><strong>海外客比率が高い</strong>: フィンランド/Google検索流入/接待観光がほぼ毎日記載</li>
<li><strong>団体送別会・部門会</strong>: 4/3 24名貸切, 4/2 同窓会2次会など複数</li>
<li><strong>常連の戻り</strong>: アールガット好き等、リピート言及が複数日に確認</li>
<li><strong>チョコレート (お通し)</strong>が会話の起点となる場面が多い</li>
<li><strong>「甘くないカクテル」</strong>提案リスト未整備が複数回課題化</li>
</ul>
<div class="warn-box" style="margin-top:8px"><strong>判定: 停滞</strong>。看板（ハイボール・ジン）は機能、海外客流入の構造化も観察できるが、コース提案の機能不全と平日早時間（食事用途）の構成比未公開で「ダイニングバー化」進度の確認は次回精査必要。</div>
</div>
</div>
</div>
</div>''')

# Slide 13: 第6章 曜日/時間帯ヒートマップ
strong_wd = sorted(DATA['weekday_summary'], key=lambda w:-w['sales_per_day'])[:2]
weak_wd = [w for w in sorted(DATA['weekday_summary'], key=lambda w:w['sales_per_day']) if w['days']>0][:2]

slides.append(f'''<div class="slide" id="slide-13">
<div class="slide-header"><h2><span class="ch-badge">第6章</span>曜日／時間帯サマリ</h2><span class="pn">13 / {TOTAL}</span></div>
<div class="msg-bar">強化曜日: <strong>{strong_wd[0]['weekday']}・{strong_wd[1]['weekday']}</strong> / 改善曜日: <strong>{weak_wd[0]['weekday']}・{weak_wd[1]['weekday']}</strong> (営業日あたり)</div>
<div class="slide-body">
<div id="chart-heatmap" style="height:300px"></div>
<div class="two-col" style="margin-top:8px">
<div class="col-half">
<div class="sec-title">曜日別 (営業日あたり)</div>
<table class="dt sm">
<tr><th>曜日</th><th class="r">営業日</th><th class="r">日平均売上</th><th class="r">日平均会計</th><th class="r">単価</th></tr>
{''.join(f"<tr class='{('best' if w['weekday']==strong_wd[0]['weekday'] else 'worst' if (w['days']>0 and w['weekday']==weak_wd[0]['weekday']) else '')}'>"
         f"<td class='b'>{w['weekday']}</td><td class='r'>{w['days']}</td><td class='r b'>{fmt_yen(w['sales_per_day']) if w['days']>0 else '—'}</td><td class='r'>{w['visits_per_day']:.1f}</td><td class='r'>{fmt_yen(w['avg_per_person']) if w['days']>0 else '—'}</td></tr>"
         for w in DATA['weekday_summary'])}
</table>
</div>
<div class="col-half">
<div id="chart-hour" style="height:240px"></div>
<div class="info-box" style="margin-top:6px">時間帯別: 20-22時台が売上の山。22-24時の深夜帯が客単価最高ゾーン。早時間（~20時）構成が低めなのが「ダイニングバー化」未達の根拠。</div>
</div>
</div>
</div>
</div>''')

# Slide 14: 第7章 施策の結論 + 第8章 構造的ボトルネック
# 日報から拾える改善ポイント・施策言及
issue_keywords = {}
for ar in DATA['ai_reports']:
    txt = ar.get('improvements','')
    for kw in ['チョコレート','英語','カクテル','補充','ロス','人員','日報','改行','スタッフ','メニュー','レシピ']:
        if kw in txt:
            issue_keywords[kw] = issue_keywords.get(kw,0)+1

slides.append(f'''<div class="slide" id="slide-14">
<div class="slide-header"><h2><span class="ch-badge">第7・8章</span>施策の結論 / 構造的ボトルネック</h2><span class="pn">14 / {TOTAL}</span></div>
<div class="msg-bar">施策ベース判断は限定的 — 業務改善カテゴリの再発: 補充オペ / 英語対応 / 甘くないカクテル提案</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title o">第7章 — 月内施策の結論</div>
<table class="dt sm">
<tr><th>施策</th><th>狙い</th><th class="c">継続/修正/停止</th></tr>
<tr><td>チョコレート お通し定常化</td><td>会話起点・購入導線</td><td class="c pos b">継続</td></tr>
<tr><td>多言語対応強化</td><td>海外客リピート</td><td class="c warn b">修正 (英語ガイド整備)</td></tr>
<tr><td>甘くないカクテル提案リスト整備</td><td>提案揺れ解消</td><td class="c warn b">修正 (作成中)</td></tr>
<tr><td>団体貸切受け入れ</td><td>大口売上</td><td class="c pos b">継続</td></tr>
<tr><td>コース予約導線</td><td>客単価底上げ</td><td class="c neg b">修正 (機能不全)</td></tr>
</table>
<div class="warn-box" style="margin-top:8px">⚠ 媒体施策（食べログ/Google/HP）/ SNS施策の効果数値が日報からは確認できず。第7章の本格的検証は<strong>施策ログ + UTMトラッキング</strong>整備後</div>
</div>
<div class="col-half">
<div class="sec-title r">第8章 — 改善ポイント月内頻出 (日報集計)</div>
<table class="dt sm">
<tr><th>キーワード</th><th class="r">月内出現</th><th>分類</th></tr>
{''.join(f"<tr><td>{k}</td><td class='r b'>{v}</td><td>{('オペ/仕組み' if k in ['補充','スタッフ','人員','日報','改行'] else '商品/接客' if k in ['チョコレート','カクテル','メニュー','レシピ'] else '商品/言語')}</td></tr>" for k,v in sorted(issue_keywords.items(),key=lambda x:-x[1])[:10])}
</table>
<div class="sec-title o" style="margin-top:8px">原因分類の比率 (推定)</div>
<ul class="bl o">
<li>仕組み: <strong>補充ペース / 役割分担 / システム入力</strong> — オペ整備で解消可</li>
<li>人: <strong>提案揺れ (甘くないカクテル) / 接客トーク標準化</strong> — トレーニング材料化</li>
<li>商品: <strong>コース提案フロー</strong> — メニュー設計から再構築</li>
</ul>
<div class="info-box" style="margin-top:6px">属人性リスク: 大泉さん入力の日報が大半 → <strong>記録の属人化</strong>が次の構造課題</div>
</div>
</div>
</div>
</div>''')

# Slide 15: 第9章 翌月の意思決定論点
slides.append(f'''<div class="slide" id="slide-15">
<div class="slide-header"><h2><span class="ch-badge">第9章</span>翌月（5月）の意思決定論点 — 4本</h2><span class="pn">15 / {TOTAL}</span></div>
<div class="msg-bar">「検討する」「様子を見る」を排し、5月内に判断する論点だけに絞る</div>
<div class="slide-body">
<div class="card">
<div class="card-title r">論点1 — コース提案フロー再構築 (Owner判定 / 5月10日まで)</div>
<div>4月コース利用率1.6% (3月10.1%)。価格訴求／提案タイミング／メニュー構成の3点で <strong>「コース化が再構造的に成立する設計」</strong>を引くか、<strong>コース概念を諦めて単品ハイチケットに振る</strong>かを判断する。判断材料: 4月コース2件の中身分析、3月コース19件の中身分析、団体予約のコース化率。</div>
</div>
<div class="card">
<div class="card-title o">論点2 — 5月集客強化策 (Owner判定 / 5月7日まで)</div>
<div>4月日平均¥95.9k → 5月予算 (推定¥3.4M前後) 到達には日平均+¥17k必要。<strong>SNS投下／Google MAP最適化／予約導線改修</strong>のいずれに5月の追加予算を寄せるかを1本に絞る。判断材料: 4月の流入チャネル分布 (POSで取れない場合は5月から計測機構を入れる前提で意思決定)。</div>
</div>
<div class="card">
<div class="card-title">論点3 — PL確定ガバナンス (Manager判定 / 5月5日まで)</div>
<div>4月実績PLが連休明け時点で未入力 → <strong>月初5営業日以内のPL確定</strong>をルール化するか。判断材料: 入力責任者・データ入力導線・遅延理由の特定。決まり次第5月分から適用。</div>
</div>
<div class="card">
<div class="card-title">論点4 — 「甘くないカクテル」と英語対応資料の整備 (5月20日まで)</div>
<div>日報で複数回再発する課題。<strong>レシピ提案リスト + 英語ガイド</strong>を整備し、属人解消する。判断材料: 整備担当者の指名と完了日のコミット。</div>
</div>
</div>
</div>''')

# Slide 16: 付録 - 前提と注釈
slides.append(f'''<div class="slide" id="slide-16">
<div class="slide-header"><h2><span class="ch-badge">付録</span>前提・データソース・レビュー観点</h2><span class="pn">16 / {TOTAL}</span></div>
<div class="msg-bar">本資料の出典・前提・追補必要事項の総まとめ</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">データソース</div>
<table class="dt sm">
<tr><th>区分</th><th>ソース</th><th class="c">状態</th></tr>
<tr><td>POS明細</td><td>rawdata.csv (Stock/週報/1_input/BFA)</td><td class="c pos">✓</td></tr>
<tr><td>AI日報 (4月20日分)</td><td>DailyReport.csv (同上)</td><td class="c pos">✓</td></tr>
<tr><td>PL 1-2月実績</td><td>Spreadsheet 新PL管理（移管前）</td><td class="c pos">✓</td></tr>
<tr><td>PL 3月実績</td><td>同上 (売上のみ確定)</td><td class="c warn">部分</td></tr>
<tr><td>PL 4月実績</td><td>未入力</td><td class="c neg">✗</td></tr>
<tr><td>PL 4月予算</td><td>Spreadsheet</td><td class="c pos">✓</td></tr>
<tr><td>レシピシート (商品99品目)</td><td>所在確認中 (BL-0082 質問中)</td><td class="c neg">✗</td></tr>
<tr><td>名寄せマスタ</td><td>姉妹タスク生成中</td><td class="c neg">✗</td></tr>
</table>
<div class="sec-title o" style="margin-top:10px">数字定義・前提</div>
<ul class="bl">
<li>金額 = POS account_total (税込前提)</li>
<li>客数 = customer_count 合計</li>
<li>営業日 = POSに会計1件以上の日</li>
<li>客単価 = 売上 ÷ 客数 (1人あたり)</li>
<li>主因分解 = 営業日換算</li>
</ul>
</div>
<div class="col-half">
<div class="sec-title">追補必要事項</div>
<ol class="nl r">
<li>4月PL実績入力 → 第4章 利益判定の確定</li>
<li>レシピシート確定 → 第4章(B) 理論原価分析</li>
<li>商品位置付けタグ (看板/準看板/スピード)</li>
<li>POS予約フラグの入力ガバナンス</li>
<li>媒体・施策ログの形式化 (第7章の本格分析向け)</li>
</ol>
<div class="sec-title o" style="margin-top:10px">レビュー観点 (review_checklist.md 参照)</div>
<ul class="bl o">
<li>主因分解の解釈は妥当か (客数 vs 単価)</li>
<li>整理候補の名指しが粗利を考慮できているか</li>
<li>5月意思決定論点は「判断する」か (検討/様子見でない)</li>
<li>固定費耐性の前提値 (¥1.7M前後) は最新か</li>
<li>看板商品の選定は POS×レシピ後で再判定するか</li>
</ul>
<div class="info-box" style="margin-top:8px">本資料は <strong>初版</strong>。データ確定後に <strong>第4章・第2章 (整理候補)</strong> を中心に更新版を発行する想定。</div>
</div>
</div>
</div>
</div>''')

# Combine
data_json = json.dumps(DATA, ensure_ascii=False, default=str)
js = JS_CHARTS.replace('__DATA_PLACEHOLDER__', data_json)

html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BAR FIVE Arrows 月次経営判断資料 — 2026年4月</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>{CSS}</style>
</head>
<body>
{chr(10).join(slides)}
<script>
{js}
</script>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[ok] {OUT} ({os.path.getsize(OUT)/1024:.1f} KB, {len(slides)} slides)')
