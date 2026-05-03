#!/usr/bin/env python3
"""
v2: analytics2.json (PROD DB + recipe + April PL actuals) → HTML
"""
import json, os, sys

ROOT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報'
DATA = json.load(open(os.path.join(ROOT, 'data/analytics2.json'), encoding='utf-8'))
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
apr, mar, feb, jan, y25 = m['apr'], m['mar'], m['feb'], m['jan'], m['y25_apr']
bd = DATA['biz_days']
bd_apr = bd['apr']; bd_mar = bd['mar']

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

# 主因
main_driver = DATA['main_driver']
visits_contrib = main_driver['visits_contrib']
unit_contrib = main_driver['unit_contrib']
driver = main_driver['driver']

# PL
pl_april = DATA['pl']['apr']
pl_jan = DATA['pl']['jan']
pl_feb = DATA['pl']['feb']
pl_apr_sales = pl_april.get('sales_total',0)
pl_apr_exp = pl_april.get('expenses_total',0)
pl_apr_profit = pl_apr_sales - pl_apr_exp
budget = DATA['pl']['budget_april']
budget_total = budget['sales_total']
budget_achievement = pl_apr_sales/budget_total if budget_total else 0
pl_apr_food = pl_april.get('expenses',{}).get('食材',0)
pl_apr_drink = pl_april.get('expenses',{}).get('ドリンク',0)
pl_apr_food_drink = pl_apr_food + pl_apr_drink
pl_apr_food_drink_rate = pl_apr_food_drink / pl_apr_sales if pl_apr_sales else 0

# 理論原価 (matched)
tc = DATA['theoretical_cost']
mc = DATA['recipe_match']['summary']
matched_sales = sum(m['sales'] for m in DATA['recipe_match']['matched'])
tc_rate_matched = tc['apr_total'] / matched_sales if matched_sales else 0
pl_food_drink_rate_pos = pl_apr_food_drink / apr['sales'] if apr['sales'] else 0

# Bar header
TOTAL = 18

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#EFEAE3;font-family:'Helvetica Neue','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif;color:#2A2421;font-size:20px;line-height:1.5}
.slide{width:1280px;height:720px;position:relative;overflow:hidden;background:#fff;margin:0 auto}
@media screen{.slide{margin:0 auto 28px;box-shadow:0 4px 20px rgba(0,0,0,.12)}}
@page{size:1280px 720px;margin:0}
@media print{*{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}body{margin:0;padding:0;background:#fff;width:1280px}.slide{page-break-after:always;page-break-inside:avoid;break-after:page;break-inside:avoid;box-shadow:none;margin:0;width:1280px;height:720px}.slide:last-child{page-break-after:auto}}
/* 月報配色: ディープフォレスト + 銅 + ゴールド */
.slide-title{background:linear-gradient(135deg,#0F4C3A 0%,#08321F 60%,#1F1A18 100%);display:flex;flex-direction:column;justify-content:center;align-items:center;color:#fff}
.slide-title h1{font-size:54px;font-weight:800;letter-spacing:3px;margin-top:20px}
.slide-title h2{font-size:30px;font-weight:400;margin-top:14px;opacity:.9}
.slide-title .badge{background:#B45309;color:#fff;padding:8px 22px;border-radius:30px;font-size:18px;font-weight:700;letter-spacing:2px;margin-bottom:10px}
.slide-title p{font-size:18px;margin-top:24px;opacity:.7}
.slide-title .accent{font-size:14px;letter-spacing:6px;color:#B45309;margin-top:16px;font-weight:700}
.slide-header{background:#0F4C3A;color:#fff;padding:14px 40px;display:flex;align-items:center;justify-content:space-between}
.slide-header h2{font-size:28px;font-weight:700}
.slide-header .ch-badge{background:#B45309;color:#fff;padding:4px 14px;border-radius:20px;font-size:16px;font-weight:700;margin-right:12px}
.slide-header .pn{font-size:15px;opacity:.7}
.msg-bar{background:#FDF7ED;border-left:5px solid #B45309;padding:11px 40px;font-size:20px;font-weight:700;color:#1F1A18}
.slide-body{padding:14px 40px;overflow:hidden;height:calc(100% - 110px)}
.kpi-grid{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:8px}
.kpi-card{background:#F5F1EA;border:1px solid #D9CCB6;border-radius:12px;padding:14px 16px;text-align:center;flex:1;min-width:170px;max-width:230px}
.kpi-label{display:block;font-size:16px;color:#73625A;margin-bottom:4px;font-weight:600}
.kpi-value{display:block;font-size:34px;font-weight:800;color:#1F1A18;line-height:1.1}
.kpi-sub{display:block;font-size:15px;margin-top:2px;font-weight:600}
.kpi-change{display:block;font-size:17px;font-weight:700;margin-top:6px}
.pos{color:#0F4C3A}.neg{color:#B91C1C}.neu{color:#73625A}.warn{color:#B45309}
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
.dt.sm{font-size:15px}.dt.sm th{padding:6px 10px;font-size:14px}.dt.sm td{padding:5px 10px}
.dt.xs{font-size:13px}.dt.xs th{padding:4px 8px;font-size:12px}.dt.xs td{padding:3px 8px}
.sec-title{font-size:22px;font-weight:800;color:#1F1A18;margin:8px 0 6px;padding-left:12px;border-left:5px solid #0F4C3A}
.sec-title.g{border-color:#0F4C3A}.sec-title.r{border-color:#B91C1C}.sec-title.o{border-color:#B45309}.sec-title.b{border-color:#1E40AF}
.bl{list-style:none;padding:0}
.bl li{padding:5px 0 5px 22px;position:relative;font-size:17px;line-height:1.5}
.bl li::before{content:'●';position:absolute;left:0;color:#0F4C3A;font-size:11px;top:11px}
.bl.g li::before{color:#0F4C3A}.bl.r li::before{color:#B91C1C}.bl.o li::before{color:#B45309}
.nl{list-style:none;padding:0;counter-reset:nl}
.nl li{padding:6px 0 6px 36px;position:relative;font-size:17px;line-height:1.5;counter-increment:nl}
.nl li::before{content:counter(nl);position:absolute;left:0;width:26px;height:26px;background:#0F4C3A;color:#fff;border-radius:50%;text-align:center;line-height:26px;font-size:14px;font-weight:700}
.nl.g li::before{background:#0F4C3A}.nl.r li::before{background:#B91C1C}.nl.o li::before{background:#B45309}
.qb{border-left:4px solid #0F4C3A;padding:8px 14px;margin:5px 0;background:#F5F1EA;font-size:15px;line-height:1.4}
.qb .qd{font-weight:700;color:#1F1A18;margin-bottom:3px;font-size:16px}
.note-box{background:#EAF5EE;border-radius:10px;border-left:5px solid #0F4C3A;padding:12px 18px;margin-top:8px;font-size:17px;line-height:1.5;font-weight:600}
.warn-box{background:#FBEDED;border-radius:10px;border-left:5px solid #B91C1C;padding:12px 18px;margin-top:8px;font-size:17px;line-height:1.5;font-weight:600}
.info-box{background:#FDF7ED;border-radius:10px;border-left:5px solid #B45309;padding:12px 18px;margin-top:8px;font-size:17px;line-height:1.5;font-weight:600}
.card{background:#F9F6F0;border:1px solid #E5DCC9;border-radius:12px;padding:12px 16px;margin:5px 0}
.card-title{font-size:19px;font-weight:800;margin-bottom:4px}
.card-title.g{color:#0F4C3A}.card-title.r{color:#B91C1C}.card-title.o{color:#B45309}
.big-num{font-size:42px;font-weight:800;line-height:1.1;color:#1F1A18}
.big-label{font-size:15px;color:#73625A;font-weight:600}
.emphasis{font-size:24px;font-weight:800}
strong{font-weight:700}
.tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:13px;font-weight:700;margin-right:6px}
.tag-kanban{background:#0F4C3A;color:#fff}
.tag-junkanban{background:#B45309;color:#fff}
.tag-seiri{background:#B91C1C;color:#fff}
.data-gap{background:#FBEDED;border:2px dashed #B91C1C;color:#B91C1C;padding:8px 14px;border-radius:8px;font-weight:700;margin:6px 0;font-size:15px}
svg{max-width:100%;height:auto;display:block}
/* compact mode: スライドが縦に収まらない場合の圧縮 */
.compact .slide-body{padding:10px 36px}
.compact .sec-title{font-size:19px;margin:5px 0 4px}
.compact .msg-bar{padding:8px 36px;font-size:18px}
.compact .dt{font-size:15px}
.compact .dt th{padding:6px 10px;font-size:14px}
.compact .dt td{padding:5px 10px}
.compact .dt.sm{font-size:14px}
.compact .dt.sm th{padding:5px 8px;font-size:13px}
.compact .dt.sm td{padding:4px 8px}
.compact .dt.xs{font-size:12px}
.compact .dt.xs th{padding:3px 6px;font-size:11px}
.compact .dt.xs td{padding:2px 6px}
.compact .bl li{padding:3px 0 3px 22px;font-size:15px;line-height:1.4}
.compact .nl li{padding:4px 0 4px 36px;font-size:15px;line-height:1.4}
.compact .note-box,.compact .warn-box,.compact .info-box,.compact .data-gap{padding:8px 14px;font-size:14px;line-height:1.4;margin-top:5px}
.compact .kpi-card{padding:10px 12px}
.compact .kpi-value{font-size:30px}
.compact .kpi-label{font-size:14px}
.compact .kpi-sub{font-size:13px}
.compact .kpi-change{font-size:15px}
.compact .card{padding:9px 13px;margin:4px 0}
.compact .card-title{font-size:17px}
"""

JS_CHARTS = """
const DATA = __DATA_PLACEHOLDER__;
function fmtYen(n){return '¥'+Math.round(n).toLocaleString('ja-JP')}
function fmtK(n){if(Math.abs(n)>=1e6)return Math.round(n/1e5)/10+'M'; if(Math.abs(n)>=1e3)return Math.round(n/100)/10+'k'; return n.toString()}

function chartDaily(){
  const el = document.getElementById('chart-daily'); if(!el) return;
  const W=1100,H=320,M={t:30,r:60,b:55,l:70};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const data = DATA.daily.map(d=>({date:d.date, sales:d.sales, customers:d.customers, weekday:d.weekday}));
  const x = d3.scaleBand().domain(data.map(d=>d.date)).range([M.l,W-M.r]).padding(0.2);
  const y = d3.scaleLinear().domain([0, d3.max(data,d=>d.sales)*1.15]).range([H-M.b,M.t]);
  const y2 = d3.scaleLinear().domain([0, d3.max(data,d=>d.customers)*1.15]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.date)).attr('y',d=>y(d.sales)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.sales))
    .attr('fill',d=>['土','金'].includes(d.weekday)?'#B45309':'#0F4C3A')
    .attr('opacity',0.85);
  const line = d3.line().x(d=>x(d.date)+x.bandwidth()/2).y(d=>y2(d.customers));
  svg.append('path').datum(data).attr('fill','none').attr('stroke','#1F1A18').attr('stroke-width',2.5).attr('d',line);
  svg.append('g').selectAll('circle').data(data).enter().append('circle')
    .attr('cx',d=>x(d.date)+x.bandwidth()/2).attr('cy',d=>y2(d.customers))
    .attr('r',3).attr('fill','#1F1A18');
  svg.append('g').attr('transform',`translate(0,${H-M.b})`)
    .call(d3.axisBottom(x).tickFormat(d=>{const wd=data.find(x=>x.date===d).weekday; return d.slice(8)+'('+wd+')';}).tickSize(4))
    .selectAll('text').style('font-size','10px');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+fmtK(d)));
  svg.append('g').attr('transform',`translate(${W-M.r},0)`).call(d3.axisRight(y2).ticks(5));
  svg.append('text').attr('x',M.l).attr('y',M.t-10).attr('font-size',13).attr('fill','#0F4C3A').text('■ 売上 (棒, 左軸) / ▲ 客数 (折線, 右軸)');
}

function chartHeatmap(){
  const el = document.getElementById('chart-heatmap'); if(!el) return;
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
  for(let i=0;i<wds.length;i++){
    svg.append('text').attr('x',M.l-10).attr('y',M.t+i*cellH+cellH/2+5)
      .attr('text-anchor','end').attr('font-size',13).attr('font-weight',700).text(wds[i]);
  }
  for(let j=0;j<buckets.length;j++){
    svg.append('text').attr('x',M.l+j*cellW+cellW/2).attr('y',M.t-8)
      .attr('text-anchor','middle').attr('font-size',12).attr('font-weight',700).text(buckets[j]);
  }
}

function chartTopProducts(){
  const el = document.getElementById('chart-products'); if(!el) return;
  // tablecharge等を除外したランキングを使用
  const data = (DATA.products.top_qty_30_excl || DATA.products.top_qty_30).slice(0,12);
  // W:H比をslide-body幅(~1208px)に合わせ aspect-ratio を制御
  const W=1208,H=290,M={t:15,r:70,b:22,l:220};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const y = d3.scaleBand().domain(data.map(d=>d.name)).range([M.t,H-M.b]).padding(0.15);
  const x = d3.scaleLinear().domain([0,d3.max(data,d=>d.qty)*1.1]).range([M.l,W-M.r]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',M.l).attr('y',d=>y(d.name)).attr('width',d=>x(d.qty)-M.l).attr('height',y.bandwidth())
    .attr('fill','#0F4C3A').attr('opacity',0.85);
  svg.selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.qty)+5).attr('y',d=>y(d.name)+y.bandwidth()/2+4)
    .attr('font-size',12).attr('fill','#1F1A18').attr('font-weight',700).text(d=>d.qty);
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).tickSize(0))
    .selectAll('text').style('font-size','12px').style('font-weight','600');
  svg.selectAll('.domain').remove();
}

function chartCategory(){
  const el = document.getElementById('chart-category'); if(!el) return;
  const data = DATA.category_share.slice(0,8);
  const W=1100,H=320,M={t:30,r:30,b:60,l:60};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(data.map(d=>d.category)).range([M.l,W-M.r]).padding(0.25);
  const y = d3.scaleLinear().domain([0,d3.max(data,d=>d.sales)*1.15]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.category)).attr('y',d=>y(d.sales)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.sales)).attr('fill','#0F4C3A').attr('opacity',0.85);
  svg.selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.category)+x.bandwidth()/2).attr('y',d=>y(d.sales)-6)
    .attr('text-anchor','middle').attr('font-size',13).attr('fill','#1F1A18').attr('font-weight',700)
    .text(d=>(d.sales_share*100).toFixed(1)+'%');
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x))
    .selectAll('text').attr('transform','rotate(-25)').attr('text-anchor','end').style('font-size','11px');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>'¥'+fmtK(d)));
}

function chartPpHist(){
  const el = document.getElementById('chart-pphist'); if(!el) return;
  const data = DATA.avg_per_person_dist.histogram;
  const W=1100,H=280,M={t:20,r:30,b:50,l:60};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(data.map(d=>d.bucket)).range([M.l,W-M.r]).padding(0.1);
  const y = d3.scaleLinear().domain([0,d3.max(data,d=>d.count)*1.15]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.bucket)).attr('y',d=>y(d.count)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.count)).attr('fill','#B45309').attr('opacity',0.85);
  svg.selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.bucket)+x.bandwidth()/2).attr('y',d=>y(d.count)-4)
    .attr('text-anchor','middle').attr('font-size',12).attr('fill','#1F1A18').text(d=>d.count||'');
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x))
    .selectAll('text').style('font-size','11px');
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5));
}

function chartMonthlyPL(){
  const el = document.getElementById('chart-monthly-pl'); if(!el) return;
  const months = ['2026-01','2026-02','2026-03','2026-04'];
  // 1-3月はスプレッドシート / 4月はDB (Tanaka指示)
  const sales = [
    DATA.pl.jan.sales_total,
    DATA.pl.feb.sales_total,
    DATA.pl.mar.sales_total,
    DATA.pl.apr.sales_total || DATA.monthly_summary.apr.sales,
  ];
  const exp = [
    DATA.pl.jan.expenses_total,
    DATA.pl.feb.expenses_total,
    DATA.pl.mar.expenses_total,  // null (3月費用未入力)
    DATA.pl.apr.expenses_total,
  ];
  // 売上 と 費用 を横並びの棒グラフ (利益は表示しない)
  // W:H比をcontainer divに合わせ aspect-ratio を制御 (slide-body幅~1208px)
  const W=1208,H=230,M={t:32,r:30,b:38,l:65};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x0 = d3.scaleBand().domain(months).range([M.l,W-M.r]).padding(0.25);
  const x1 = d3.scaleBand().domain(['sales','exp']).range([0, x0.bandwidth()]).padding(0.1);
  const maxV = d3.max([...sales,...exp.filter(v=>v!=null)])*1.18;
  const y = d3.scaleLinear().domain([0, maxV]).range([H-M.b,M.t]);

  // 売上バー
  for(let i=0;i<sales.length;i++){
    if(sales[i]==null) continue;
    svg.append('rect')
      .attr('x', x0(months[i])+x1('sales'))
      .attr('y', y(sales[i]))
      .attr('width', x1.bandwidth())
      .attr('height', y(0)-y(sales[i]))
      .attr('fill','#0F4C3A').attr('opacity',0.92);
    svg.append('text')
      .attr('x', x0(months[i])+x1('sales')+x1.bandwidth()/2)
      .attr('y', y(sales[i])-4)
      .attr('text-anchor','middle').attr('font-size',11).attr('font-weight',700).attr('fill','#0F4C3A')
      .text('¥'+fmtK(sales[i]));
  }
  // 費用バー
  for(let i=0;i<exp.length;i++){
    if(exp[i]==null){
      // データなし表示
      svg.append('text')
        .attr('x', x0(months[i])+x1('exp')+x1.bandwidth()/2)
        .attr('y', H-M.b-6)
        .attr('text-anchor','middle').attr('font-size',10).attr('fill','#73625A').attr('font-style','italic')
        .text('—');
      continue;
    }
    svg.append('rect')
      .attr('x', x0(months[i])+x1('exp'))
      .attr('y', y(exp[i]))
      .attr('width', x1.bandwidth())
      .attr('height', y(0)-y(exp[i]))
      .attr('fill','#B91C1C').attr('opacity',0.85);
    svg.append('text')
      .attr('x', x0(months[i])+x1('exp')+x1.bandwidth()/2)
      .attr('y', y(exp[i])-4)
      .attr('text-anchor','middle').attr('font-size',11).attr('font-weight',700).attr('fill','#B91C1C')
      .text('¥'+fmtK(exp[i]));
  }
  // 4月予算の売上ラインを参考表示
  const ba = DATA.pl.budget_april.sales_total;
  svg.append('line')
    .attr('x1', x0(months[3])+x1('sales')-2)
    .attr('x2', x0(months[3])+x1('sales')+x1.bandwidth()+2)
    .attr('y1', y(ba)).attr('y2', y(ba))
    .attr('stroke','#B45309').attr('stroke-width',2).attr('stroke-dasharray','5,4');
  svg.append('text')
    .attr('x', x0(months[3])+x1('sales')+x1.bandwidth()/2)
    .attr('y', y(ba)-18)
    .attr('text-anchor','middle').attr('font-size',10).attr('fill','#B45309').attr('font-weight',700)
    .text('予算¥'+fmtK(ba));

  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x0));
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(6).tickFormat(d=>'¥'+fmtK(d)));
  // 凡例 (上部に少しコンパクトに配置)
  svg.append('rect').attr('x',M.l).attr('y',M.t-20).attr('width',10).attr('height',10).attr('fill','#0F4C3A');
  svg.append('text').attr('x',M.l+15).attr('y',M.t-11).attr('font-size',12).attr('fill','#0F4C3A').attr('font-weight',700).text('売上');
  svg.append('rect').attr('x',M.l+70).attr('y',M.t-20).attr('width',10).attr('height',10).attr('fill','#B91C1C').attr('opacity',0.85);
  svg.append('text').attr('x',M.l+85).attr('y',M.t-11).attr('font-size',12).attr('fill','#B91C1C').attr('font-weight',700).text('費用');
  svg.append('text').attr('x',M.l+150).attr('y',M.t-11).attr('font-size',11).attr('fill','#B45309').attr('font-weight',700).text('--- 4月予算');
}

function chartParty(){
  const el = document.getElementById('chart-party'); if(!el) return;
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

function chartHour(){
  const el = document.getElementById('chart-hour'); if(!el) return;
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

function chartCostRate(){
  const el = document.getElementById('chart-costrate'); if(!el) return;
  // 月次 食材+ドリンク費 / 売上 (1-3月はスプレッドシート / 4月はDB)
  const sources = [
    {month:'2026-01', d: DATA.pl.jan},
    {month:'2026-02', d: DATA.pl.feb},
    {month:'2026-04', d: DATA.pl.apr},  // 3月は費用未入力
  ];
  const data = sources.map(({month,d})=>{
    const s = d.sales_total||0;
    const e = d.expenses||{};
    const fd = (e['食材']||0)+(e['ドリンク']||0);
    return {month, rate: s? fd/s : 0, fd, sales: s};
  });
  const W=540,H=240,M={t:30,r:30,b:40,l:60};
  const svg = d3.select(el).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`);
  const x = d3.scaleBand().domain(data.map(d=>d.month)).range([M.l,W-M.r]).padding(0.3);
  const y = d3.scaleLinear().domain([0, d3.max(data,d=>d.rate)*1.2]).range([H-M.b,M.t]);
  svg.append('g').selectAll('rect').data(data).enter().append('rect')
    .attr('x',d=>x(d.month)).attr('y',d=>y(d.rate)).attr('width',x.bandwidth())
    .attr('height',d=>H-M.b-y(d.rate)).attr('fill','#B91C1C').attr('opacity',0.8);
  svg.selectAll('text.lbl').data(data).enter().append('text').attr('class','lbl')
    .attr('x',d=>x(d.month)+x.bandwidth()/2).attr('y',d=>y(d.rate)-6)
    .attr('text-anchor','middle').attr('font-size',13).attr('font-weight',700).text(d=>(d.rate*100).toFixed(1)+'%');
  svg.append('g').attr('transform',`translate(0,${H-M.b})`).call(d3.axisBottom(x));
  svg.append('g').attr('transform',`translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(d=>(d*100).toFixed(0)+'%'));
  svg.append('text').attr('x',M.l).attr('y',M.t-10).attr('font-size',12).attr('fill','#B91C1C').attr('font-weight',700).text('食材+ドリンク仕入 / 売上');
}

document.addEventListener('DOMContentLoaded',()=>{
  chartDaily(); chartHeatmap(); chartTopProducts(); chartCategory();
  chartPpHist(); chartMonthlyPL(); chartParty(); chartHour(); chartCostRate();
});
"""

slides = []

# Slide 1: 表紙
slides.append(f'''<div class="slide slide-title" id="slide-1">
<div class="badge">📅 月報 (Monthly)</div>
<h1>BAR FIVE Arrows</h1>
<h2>月次経営判断資料</h2>
<p>2026年4月（2026-04-01 〜 2026-04-30）</p>
<div class="accent">EXECUTIVE MONTHLY REVIEW</div>
<p style="margin-top:36px;font-size:12px;opacity:.5">分析観点ガイド v2 準拠 / 全10章フル章立て / Production DB v2026-05-04</p>
</div>''')

# Slide 2: 前提・目次
slides.append(f'''<div class="slide" id="slide-2">
<div class="slide-header"><h2><span class="ch-badge">前提</span>本月報の読み方</h2><span class="pn">2 / {TOTAL}</span></div>
<div class="msg-bar">月報＝経営判断書 / 週報＝施策修正書 / 日報＝兆候キャッチ — 本書は意思決定論点に絞る</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title o">数字の起点（前提）</div>
<ul class="bl o">
<li><strong>会計単位</strong>: POS account_id (1グループ＝1会計)</li>
<li><strong>客数</strong>: customer_count 合計</li>
<li><strong>客単価</strong>: 売上 ÷ 客数 (一人あたり)</li>
<li><strong>金額</strong>: POS account_total (税込前提)</li>
<li><strong>営業日</strong>: POS会計1件以上の日 (4月: <strong>{bd_apr}日</strong> / 3月: <strong>{bd_mar}日</strong>)</li>
<li><strong>集計対象期間</strong>: 2026-04-01〜04-26 ({bd_apr}営業日)</li>
<li><strong>レシピ名寄せ率</strong>: 出数{mc['qty_match_rate']*100:.1f}% (matched品目を理論原価分析の母集団とする)</li>
</ul>
<div class="sec-title o">データソース構成</div>
<div class="info-box" style="font-size:14px"><strong>POS</strong>: 本番DB (Production Neon) salesData / 4月会計126件 / 客数456人<br>
<strong>PL 1-3月</strong>: 新PL管理（移管前）スプレッドシート / <strong>4月PL</strong>: 本番DB plDailyExpense<br>
<strong>レシピマスタ</strong>: 商品一覧シート 99品目 (うち売価+原価入力済 63品目)<br>
<strong>AI日報</strong>: 本番DB dailyReport / 4月26件</div>
</div>
<div class="col-half">
<div class="sec-title">章立て (10章構成)</div>
<table class="dt sm">
<tr><td class="b c" style="width:40px">0</td><td>エグゼクティブサマリ</td></tr>
<tr><td class="b c">1</td><td>売上構造の判定 (客数 vs 単価)</td></tr>
<tr><td class="b c">2</td><td>商品戦略の判定 (看板/整理候補)</td></tr>
<tr><td class="b c">3</td><td>客単価の作られ方</td></tr>
<tr><td class="b c">4</td><td><strong>利益構造の判定 ★最重要</strong></td></tr>
<tr><td class="b c">4B</td><td>理論原価分析 (POS×レシピ)</td></tr>
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

# Slide 3: 第0章エグゼクティブサマリ
exec_concl = []
exec_concl.append(f"<strong>当月POS売上は{fmt_yen(apr['sales'])}</strong>（{bd_apr}営業日 / {apr['visits']}会計）。日平均は<strong>{fmt_yen(sales_per_day_apr)}</strong>で前月比{fmt_diff(mom_per_day)}。日平均で見ても明確な減少で、<strong>主因は{driver}</strong>（客数寄与{fmt_yen(visits_contrib)} / 単価寄与{fmt_yen(unit_contrib)}）")
exec_concl.append(f"<strong>4月PL: 売上{fmt_yen(pl_apr_sales)} / 計上費用{fmt_yen(pl_apr_exp)} (食材・ドリンク・広告費・家賃・備品・管理費)</strong>。1-2月実績の人件費 (¥347〜414k) / 水道光熱費 (¥80〜92k) / ローン返済 (¥169k) を加算した実態費用は<strong>¥3,000k規模</strong>。予算到達率{(budget_achievement*100):.1f}%、CLP人件費を含めた最終利益は<strong>▲¥800k〜▲¥1Mレンジ</strong>")
exec_concl.append(f"<strong>コース利用率1.6%</strong> (3月10.1%) で大幅低下 / 1組人数{apr['avg_party_size']:.1f}人 (3月{mar['avg_party_size']:.1f}) で団体化進行 → <strong>団体は来たがコース化が機能せず1人単価が落ちた</strong>構造")

next_decisions = [
    "コース提案フロー再構築 — 4月コース利用率1.6%は構造逸脱。価格訴求/提案動線/メニュー構成の3点を月内に再設計する",
    "5月集客強化策の選定 — 日平均売上¥100k は予算到達ラインを大きく下回る。SNS/Google/予約導線の中で5月単月に効く1-2本を特定する",
    "リニューアル後のレシピ補完 — 4月にPOS出現するが商品リストに無い品目23件 (飲み放題コース・ラム/ウイスキー単品・ワイン) を商品マスタに追加登録する",
]

slides.append(f'''<div class="slide" id="slide-3">
<div class="slide-header"><h2><span class="ch-badge">第0章</span>エグゼクティブサマリ</h2><span class="pn">3 / {TOTAL}</span></div>
<div class="msg-bar">結論3行 + 翌月の意思決定論点3つ</div>
<div class="slide-body">
<div class="kpi-grid">
<div class="kpi-card"><span class="kpi-label">PL売上</span><span class="kpi-value">{fmt_yen(pl_apr_sales)}</span><span class="kpi-change warn">予算{(budget_achievement*100):.1f}%</span><span class="kpi-sub neg">未達 {fmt_yen(budget_total-pl_apr_sales)}</span></div>
<div class="kpi-card"><span class="kpi-label">客数 (POS)</span><span class="kpi-value">{fmt_int(apr['customers'])}<small style="font-size:18px">人</small></span><span class="kpi-change neg">{fmt_diff(mom_customers)} 前月</span><span class="kpi-sub neg">{fmt_diff(yoy_customers)} 前年</span></div>
<div class="kpi-card"><span class="kpi-label">客単価 (POS)</span><span class="kpi-value">{fmt_yen(apr['avg_per_person'])}</span><span class="kpi-change neg">{fmt_diff(mom_per_person)} 前月</span><span class="kpi-sub neg">{fmt_diff(yoy_per_person)} 前年</span></div>
<div class="kpi-card"><span class="kpi-label">計上費用</span><span class="kpi-value">{fmt_yen(pl_apr_exp)}</span><span class="kpi-change warn">対予算 {(pl_apr_exp/budget['expenses_total']*100):.0f}%</span><span class="kpi-sub neu">予算 {fmt_yen(budget['expenses_total'])}</span></div>
<div class="kpi-card"><span class="kpi-label">推計最終利益</span><span class="kpi-value neg">▲¥0.8〜1M</span><span class="kpi-change neg">CLP含 / 1-2月平均ベース</span><span class="kpi-sub neg">予算 {fmt_yen(budget['profit'])}</span></div>
</div>
<div class="sec-title r" style="margin-top:6px">⚠ 結論3行</div>
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

# Slide 4: 第1章 売上構造
slides.append(f'''<div class="slide compact" id="slide-4">
<div class="slide-header"><h2><span class="ch-badge">第1章</span>売上構造の判定</h2><span class="pn">4 / {TOTAL}</span></div>
<div class="msg-bar">主因は <strong>{driver}</strong>: 客数寄与{fmt_yen(visits_contrib)} vs 単価寄与{fmt_yen(unit_contrib)} (営業日換算)</div>
<div class="slide-body">
<div id="chart-daily" style="height:280px"></div>
<div class="two-col" style="margin-top:6px">
<div class="col-half">
<div class="sec-title">月次主因分解 (営業日換算)</div>
<table class="dt sm">
<tr><th>項目</th><th class="r">4月実績</th><th class="r">3月実績</th><th class="r">差分</th></tr>
<tr><td>POS売上</td><td class="r b">{fmt_yen(apr['sales'])}</td><td class="r">{fmt_yen(mar['sales'])}</td><td class="r neg">{fmt_diff(mom_sales)}</td></tr>
<tr><td>会計件数</td><td class="r b">{apr['visits']}</td><td class="r">{mar['visits']}</td><td class="r neg">{fmt_diff(mom_visits)}</td></tr>
<tr><td>客数</td><td class="r b">{apr['customers']}</td><td class="r">{mar['customers']}</td><td class="r neg">{fmt_diff(mom_customers)}</td></tr>
<tr><td>1組人数</td><td class="r b">{apr['avg_party_size']:.2f}人</td><td class="r">{mar['avg_party_size']:.2f}人</td><td class="r pos">+{(apr['avg_party_size']-mar['avg_party_size']):.2f}</td></tr>
<tr><td>客単価(1人)</td><td class="r b">{fmt_yen(apr['avg_per_person'])}</td><td class="r">{fmt_yen(mar['avg_per_person'])}</td><td class="r neg">{fmt_diff(mom_per_person)}</td></tr>
<tr class="highlight-row"><td>日平均売上</td><td class="r b">{fmt_yen(sales_per_day_apr)}</td><td class="r">{fmt_yen(sales_per_day_mar)}</td><td class="r neg b">{fmt_diff(mom_per_day)}</td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title r">主因の特定</div>
<div class="warn-box"><strong>{driver}が決定的に効いた</strong>。営業日換算の差分内訳: 客数{fmt_yen(visits_contrib)} / 単価{fmt_yen(unit_contrib)}</div>
<ul class="bl">
<li><strong>会計件数</strong>: 188 → 126 ({fmt_diff(mom_visits)}) = <strong>62件減</strong></li>
<li><strong>1組人数</strong>: {mar['avg_party_size']:.2f} → {apr['avg_party_size']:.2f}人 = <strong>団体化</strong>進行</li>
<li><strong>客単価</strong>: {fmt_yen(mar['avg_per_person'])} → {fmt_yen(apr['avg_per_person'])} = <strong>1人▲{int(mar['avg_per_person']-apr['avg_per_person']):,}円</strong></li>
<li><strong>コース率</strong>: 10.1% → <strong>1.6%</strong> = 急落</li>
</ul>
<div class="info-box">団体化(1組+0.85人)は来たが、コース提案がほぼ機能せず1人あたり単価が落ちた構造</div>
</div>
</div>
</div>
</div>''')

# Slide 5: 第1章補足 - 日次変動 + コース vs アラカルト (予約フラグはデータ未取得につき記載なし)
top3_days = sorted(DATA['daily'], key=lambda d:-d['sales'])[:3]
worst3_days = sorted([d for d in DATA['daily'] if d['sales']>0], key=lambda d:d['sales'])[:3]
seg = DATA['segments']['apr']
seg_m = DATA['segments']['mar']
slides.append(f'''<div class="slide" id="slide-5">
<div class="slide-header"><h2><span class="ch-badge">第1章補足</span>日次変動・コース／アラカルト構成</h2><span class="pn">5 / {TOTAL}</span></div>
<div class="msg-bar">月内ベスト日が団体貸切で売上の山を作るも、コース利用が3月19件→4月2件へ激減</div>
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
<div class="sec-title o">コース vs アラカルト (4月)</div>
<table class="dt sm">
<tr><th>区分</th><th class="r">会計</th><th class="r">売上</th><th class="r">構成比</th><th class="r">会計単価</th></tr>
<tr><td>コース</td><td class="r b">{seg['course']['visits']}</td><td class="r b">{fmt_yen(seg['course']['sales'])}</td><td class="r b">{seg['course']['sales']/apr['sales']*100:.1f}%</td><td class="r">{fmt_yen(seg['course']['sales']/seg['course']['visits']) if seg['course']['visits'] else '—'}</td></tr>
<tr><td>アラカルト</td><td class="r">{seg['alacarte']['visits']}</td><td class="r">{fmt_yen(seg['alacarte']['sales'])}</td><td class="r">{seg['alacarte']['sales']/apr['sales']*100:.1f}%</td><td class="r">{fmt_yen(seg['alacarte']['sales']/seg['alacarte']['visits']) if seg['alacarte']['visits'] else '—'}</td></tr>
</table>
<div class="sec-title o" style="margin-top:14px">3月との比較</div>
<table class="dt sm">
<tr><th>指標</th><th class="r">4月</th><th class="r">3月</th><th class="r">差</th></tr>
<tr><td>コース会計件数</td><td class="r b">{seg['course']['visits']}</td><td class="r">{seg_m['course']['visits']}</td><td class="r neg b">{seg['course']['visits']-seg_m['course']['visits']:+d}</td></tr>
<tr><td>コース売上</td><td class="r b">{fmt_yen(seg['course']['sales'])}</td><td class="r">{fmt_yen(seg_m['course']['sales'])}</td><td class="r neg b">{fmt_yen(seg['course']['sales']-seg_m['course']['sales'])}</td></tr>
<tr><td>コース利用率</td><td class="r b">{apr['course_share']*100:.1f}%</td><td class="r">{mar['course_share']*100:.1f}%</td><td class="r neg b">{(apr['course_share']-mar['course_share'])*100:+.1f}pt</td></tr>
</table>
<div class="warn-box" style="margin-top:8px">コース2件・¥117kは3月19件・¥626kから激減 (会計件数▲17 / 売上▲¥509k)。<strong>コース提案ファネルの再構築が論点</strong> (第9章 論点1)</div>
</div>
</div>
</div>
</div>''')

# Slide 6: 第2章 商品戦略 (出数Top15 / tablecharge等除外)
def get_p(name, key):
    return next((p[key] for p in DATA['products']['all'] if p['name']==name), 0)
slides.append(f'''<div class="slide compact" id="slide-6">
<div class="slide-header"><h2><span class="ch-badge">第2章</span>商品戦略の判定 — 出数Top12 (チャージ除外)</h2><span class="pn">6 / {TOTAL}</span></div>
<div class="msg-bar">ハウスハイボール (152) / 森のジントニック (82) / ガージェリー (39) の3軸が出数を支える</div>
<div class="slide-body">
<div id="chart-products" style="margin-bottom:12px"></div>
<div class="two-col" style="margin-top:6px">
<div class="col-half">
<div class="sec-title o">名指し看板 (確固たる地位)</div>
<table class="dt sm">
<tr><th>商品</th><th class="r">4月出数</th><th class="r">3月</th><th class="r">差</th><th class="c">タグ</th></tr>
<tr class="best"><td>ハウスハイボール</td><td class="r b">152</td><td class="r">{get_p('ハウスハイボール','qty_mar')}</td><td class="r pos">{get_p('ハウスハイボール','qty_diff_mom'):+d}</td><td class="c"><span class="tag tag-kanban">看板</span></td></tr>
<tr class="best"><td>森のジントニック</td><td class="r b">82</td><td class="r">{get_p('森のジントニック','qty_mar')}</td><td class="r pos">{get_p('森のジントニック','qty_diff_mom'):+d}</td><td class="c"><span class="tag tag-kanban">看板</span></td></tr>
<tr><td>ガージェリー</td><td class="r b">39</td><td class="r">{get_p('ガージェリー','qty_mar')}</td><td class="r {'pos' if get_p('ガージェリー','qty_diff_mom')>=0 else 'neg'}">{get_p('ガージェリー','qty_diff_mom'):+d}</td><td class="c"><span class="tag tag-junkanban">準看板</span></td></tr>
<tr><td>BAR専用チョコレート</td><td class="r b">38</td><td class="r">{get_p('BAR 専用チョコレート','qty_mar')}</td><td class="r">{get_p('BAR 専用チョコレート','qty_diff_mom'):+d}</td><td class="c"><span class="tag tag-kanban">看板</span></td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title o">注釈</div>
<ul class="bl o">
<li><strong>tablecharge等は除外</strong>: 全会計に自動付与されるチャージは商品戦略判断の対象外 ({', '.join(DATA['products']['excluded_from_ranking'])})</li>
<li><strong>ハウスハイボール (152本)</strong>: 看板地位を維持。ウイスキー類の入口商品として機能</li>
<li><strong>森のジントニック (82本)</strong>: BFAコンセプト看板。安定出数</li>
<li><strong>ガージェリー (39本)</strong>: ビール系中核。準看板</li>
<li>飲み放題コース (3種計71件) で売上 ¥474k = 全売上の20.6%</li>
</ul>
<div class="info-box" style="margin-top:6px">レシピマスタ99品目のうち51品目がPOS連携済 (出数43.3%)。残り出数56.7%は <strong>ハイボール / ウイスキー単品 / 飲み放題コース</strong> でレシピ未登録 → 第4章Bでデータ詳細を提示</div>
</div>
</div>
</div>
</div>''')

# Slide 7: 第2章補足 売上ランキング+カテゴリ
# レイアウト: 左カラム 60% (商品Top10) / 右カラム 40% (カテゴリチャート+表)
# flex を使わず width 直接指定で確実に
top10_sales = DATA['products']['top_sales_30_excl'][:10]  # tablecharge等除外
slides.append(f'''<div class="slide" id="slide-7">
<div class="slide-header"><h2><span class="ch-badge">第2章補足</span>売上Top10 / カテゴリ構成</h2><span class="pn">7 / {TOTAL}</span></div>
<div class="msg-bar">売上1位は「その他CLPコース」¥280k — コース系で売上の<strong>26.8%</strong>を占有 (チャージ除外ベース)</div>
<div class="slide-body">
<div style="display:flex;gap:22px;height:100%">
<div style="width:60%;flex-shrink:0">
<div class="sec-title">商品別売上Top10 (チャージ除外)</div>
<table class="dt sm" style="width:100%;table-layout:fixed">
<colgroup><col style="width:32px"/><col/><col style="width:110px"/><col style="width:55px"/><col style="width:65px"/></colgroup>
<tr><th class="c">#</th><th>商品名</th><th class="r">売上</th><th class="r">出数</th><th class="r">前月差</th></tr>
{''.join(f"<tr><td class='c b'>{i+1}</td><td>{p['name']}</td><td class='r b'>{fmt_yen(p['sales'])}</td><td class='r'>{p['qty']}</td><td class='r {('pos' if p['qty_diff_mom']>=0 else 'neg')}'>{p['qty_diff_mom']:+d}</td></tr>" for i,p in enumerate(top10_sales[:10]))}
</table>
</div>
<div style="width:40%;flex-shrink:0">
<div class="sec-title">カテゴリ構成 (4月)</div>
<div id="chart-category" style="height:240px"></div>
<table class="dt xs" style="margin-top:4px;width:100%;table-layout:fixed">
<colgroup><col/><col style="width:60px"/><col style="width:65px"/></colgroup>
<tr><th>カテゴリ</th><th class="r">構成比</th><th class="r">前月差</th></tr>
{''.join(f"<tr><td>{c['category'][:18]}</td><td class='r b'>{c['sales_share']*100:.1f}%</td><td class='r {('pos' if c['share_diff']>=0 else 'neg')}'>{c['share_diff']*100:+.1f}pt</td></tr>" for c in DATA['category_share'][:6])}
</table>
</div>
</div>
</div>
</div>''')

# Slide 8: 第2章 動きの大きい商品 / 整理候補
risen = sorted([p for p in DATA['products']['all'] if p['qty_diff_mom']>=5], key=lambda x:-x['qty_diff_mom'])[:8]
fallen = sorted([p for p in DATA['products']['all'] if p['qty_mar']>=5], key=lambda x:x['qty_diff_mom'])[:8]
low_movers = [p for p in DATA['products']['all'] if 1 <= p['qty'] <= 3 and p['sales'] < 5000]
low_movers_top = sorted(low_movers, key=lambda x:x['sales'])[:12]

slides.append(f'''<div class="slide" id="slide-8">
<div class="slide-header"><h2><span class="ch-badge">第2章補足</span>動きの大きい商品 / 整理候補</h2><span class="pn">8 / {TOTAL}</span></div>
<div class="msg-bar">前月から大きく動いた商品 / 月内ほぼ動かない商品の名指し</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title g">出数 急上昇 Top8 (前月比)</div>
<table class="dt sm">
<tr><th>商品名</th><th class="r">4月</th><th class="r">3月</th><th class="r">差</th></tr>
{''.join(f"<tr><td>{p['name'][:24]}</td><td class='r b'>{p['qty']}</td><td class='r'>{p['qty_mar']}</td><td class='r pos b'>+{p['qty_diff_mom']}</td></tr>" for p in risen)}
</table>
<div class="sec-title r" style="margin-top:10px">出数 急減少 Top8 (前月比)</div>
<table class="dt sm">
<tr><th>商品名</th><th class="r">4月</th><th class="r">3月</th><th class="r">差</th></tr>
{''.join(f"<tr><td>{p['name'][:24]}</td><td class='r b'>{p['qty']}</td><td class='r'>{p['qty_mar']}</td><td class='r neg b'>{p['qty_diff_mom']:+d}</td></tr>" for p in fallen)}
</table>
</div>
<div class="col-half">
<div class="sec-title r">整理候補（月内出数1-3 + 売上5k未満 / 名指し）</div>
<table class="dt xs">
<tr><th>商品名</th><th class="r">出数</th><th class="r">売上</th><th>カテゴリ</th></tr>
{''.join(f"<tr><td>{p['name'][:24]}</td><td class='r'>{p['qty']}</td><td class='r'>{fmt_yen(p['sales'])}</td><td>{(p['category1'] or '-')[:14]}</td></tr>" for p in low_movers_top[:14])}
</table>
<div class="data-gap" style="margin-top:6px">⚠ 整理判定の最終決裁は<strong>原価データ取得後</strong>。粗利貢献を加味する必要 (低単価×低出数でも高粗利率なら継続価値あり)</div>
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
<div class="warn-box" style="margin-top:8px">客単価の主たる作られ方は <strong>「ドリンク2杯目以上 + 看板ジン or ハイボール」</strong>。コース構造が機能していない4月は中位帯（4-7k）が薄い分布</div>
</div>
</div>
</div>
</div>''')

# Slide 10: 第4章 利益構造 ★最重要 (1-3月: スプレッドシート / 4月: DB)
exp_sorted = sorted([(k,v) for k,v in pl_april.get('expenses',{}).items()], key=lambda x:-x[1])
slides.append(f'''<div class="slide compact" id="slide-10">
<div class="slide-header"><h2><span class="ch-badge">第4章 ★</span>利益構造の判定 — PL推移と固定費耐性</h2><span class="pn">10 / {TOTAL}</span></div>
<div class="msg-bar">月次の売上 vs 費用を並列確認: 1月¥2.6M / 2月¥2.7M (赤字) / 3月¥2.8M / 4月¥2.9M — 4月は計上中の費目あり (人件費・水光熱費・ローン返済)</div>
<div class="slide-body">
<div id="chart-monthly-pl" style="margin-bottom:14px"></div>
<div class="two-col">
<div class="col-half">
<div class="sec-title" style="margin-top:0">4月PL費用 (本番DB計上分)</div>
<table class="dt xs">
<tr><th>費目</th><th class="r">4月実績</th><th class="r">vs 1月</th><th class="r">vs 2月</th></tr>
{''.join(f"<tr><td>{k}</td><td class='r b'>{fmt_yen(v)}</td><td class='r'>{fmt_yen(v-pl_jan.get('expenses',{}).get(k,0))}</td><td class='r'>{fmt_yen(v-pl_feb.get('expenses',{}).get(k,0))}</td></tr>" for k,v in exp_sorted)}
<tr class="highlight-row"><td>計上小計</td><td class="r b">{fmt_yen(pl_apr_exp)}</td><td class="r">{fmt_yen(pl_apr_exp-pl_jan.get('expenses_total',0))}</td><td class="r">{fmt_yen(pl_apr_exp-pl_feb.get('expenses_total',0))}</td></tr>
</table>
<div style="font-size:12px;color:#1F1A18;margin-top:4px">月次計上分 (人件費・水光熱費・ローン返済) を1-2月実績ベースで加算: <strong>¥+600〜700k</strong> → 実態費用 <strong>約¥3.0M</strong></div>
<div style="font-size:11px;color:#73625A;margin-top:2px">📌 ソース: 1-3月=新PL管理シート / 4月=本番DB plDailyExpense</div>
</div>
<div class="col-half">
<div class="sec-title r" style="margin-top:0">損益分岐ラインへのギャップ</div>
<table class="dt xs">
<tr><th>シナリオ</th><th class="r">必要売上</th><th class="r">ギャップ</th></tr>
<tr><td>1月費用ベース</td><td class="r">{fmt_yen(pl_jan.get('expenses_total',0))}</td><td class="r {'pos' if pl_apr_sales>=pl_jan.get('expenses_total',0) else 'neg'} b">{fmt_yen(pl_apr_sales-pl_jan.get('expenses_total',0))}</td></tr>
<tr><td>2月費用ベース</td><td class="r">{fmt_yen(pl_feb.get('expenses_total',0))}</td><td class="r neg b">{fmt_yen(pl_apr_sales-pl_feb.get('expenses_total',0))}</td></tr>
<tr><td>4月予算費用ベース</td><td class="r">{fmt_yen(budget['expenses_total'])}</td><td class="r neg b">{fmt_yen(pl_apr_sales-budget['expenses_total'])}</td></tr>
<tr><td>+CLP人件費(¥600k)</td><td class="r">{fmt_yen(budget['expenses_total']+600000)}</td><td class="r neg b">{fmt_yen(pl_apr_sales-budget['expenses_total']-600000)}</td></tr>
</table>
<div style="font-size:12px;color:#1F1A18;margin-top:6px;font-weight:700;background:#FBEDED;border-left:4px solid #B91C1C;padding:6px 10px;border-radius:4px">4月計上¥{int(pl_apr_exp/1000):,}k + 月次費目加算で実態約¥{int((pl_apr_exp+700000)/1000):,}k → CLP人件費(¥600k)を含む最終利益は<strong>▲¥800k〜▲¥1M</strong>レンジ</div>
</div>
</div>
</div>
</div>''')

# Slide 11: 第4章(B) 理論原価 — まずデータ取得状況を確認 (考察前)
# 田中さん指示で 3月/4月 出現パターン別に再分類
all_pos = DATA['recipe_match']['all_pos_records']
def st(rec):
    am, ap = rec.get('appeared_in_mar'), rec.get('appeared_in_apr')
    if am and ap: return 'both'
    if ap: return 'apr_only'
    if am: return 'mar_only'
    return 'neither'
mat_both = [r for r in all_pos if r.get('matched') and st(r)=='both']
mat_apr = [r for r in all_pos if r.get('matched') and st(r)=='apr_only']
mat_mar = [r for r in all_pos if r.get('matched') and st(r)=='mar_only']
unm_both = [r for r in all_pos if not r.get('matched') and st(r)=='both']
unm_apr = [r for r in all_pos if not r.get('matched') and st(r)=='apr_only']
unm_mar = [r for r in all_pos if not r.get('matched') and st(r)=='mar_only']
unm_apr_qty = sum(r['qty'] for r in unm_apr)
unm_apr_sales = sum(r['sales'] for r in unm_apr)
# 区分3 = POSなし × レシピあり (両月)
matched_recipe_names_set = {r['recipe_name'] for r in all_pos if r.get('matched') and r.get('recipe_name')}
recipe_full_count = 99  # 商品一覧シート総数
recipe_only_count = recipe_full_count - len(matched_recipe_names_set)

slides.append(f'''<div class="slide compact" id="slide-11">
<div class="slide-header"><h2><span class="ch-badge">第4章(B)-i</span>理論原価 — POS×レシピ マッピング状況 (3/4月別)</h2><span class="pn">11 / {TOTAL}</span></div>
<div class="msg-bar">4月リニューアルを踏まえて 3月/4月 出現別に分類。<strong>区分2a (4月のみ×レシピなし) {len(unm_apr)}品目</strong>を5月のレシピ補完対象とする</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">マッピング 3区分 × 月別</div>
<table class="dt sm">
<tr><th>区分</th><th class="r c">両月</th><th class="r c">4月のみ ★</th><th class="r c">3月のみ</th></tr>
<tr><td>区分1: マッチ済</td><td class="r b">{len(mat_both)}</td><td class="r b">{len(mat_apr)}</td><td class="r">{len(mat_mar)}</td></tr>
<tr class="highlight-row"><td>区分2: POS○ × レシピ✗</td><td class="r b">{len(unm_both)}</td><td class="r b warn">{len(unm_apr)}</td><td class="r">{len(unm_mar)}</td></tr>
<tr><td>区分3: POS✗ × レシピ○</td><td class="r" colspan="3">— 両月とも出現なし: {recipe_only_count}品目 ※詳細は別Markdown</td></tr>
</table>
<div class="warn-box" style="margin-top:6px;font-size:14px"><strong>★区分2a (4月のみ×レシピなし) {len(unm_apr)}品目 / {unm_apr_qty}出数 / ¥{int(unm_apr_sales):,}</strong> = リニューアル後POSに出るが商品リストに無い → 商品マスタ追加登録の要否を確認</div>
<div class="sec-title o" style="margin-top:6px">マッチ済 原価率 分布チェック</div>
<table class="dt xs">
<tr><th>原価率帯</th><th class="r">品目数</th><th>判定</th></tr>
{''.join(f"<tr><td>{k}</td><td class='r b'>{v}</td><td>{'妥当' if 0<v<25 else '高原価率' if v>=25 else '—'}</td></tr>" for k,v in DATA['recipe_match']['cost_rate_buckets'].items())}
</table>
</div>
<div class="col-half">
<div class="sec-title r">区分2a (★4月のみ×レシピなし) 内訳</div>
<table class="dt xs">
<tr><th>POS商品名</th><th class="r">出数</th><th class="r">売上</th><th>カテゴリ</th></tr>
{''.join(f"<tr><td>{r['pos_name'][:20]}</td><td class='r b'>{r['qty']}</td><td class='r'>¥{int(r['sales']):,}</td><td>{(r.get('category_pos') or '-')[:10]}</td></tr>" for r in sorted(unm_apr, key=lambda x:-x['qty'])[:12])}
</table>
<div class="info-box" style="margin-top:6px;font-size:13px">飲み放題コース系 (5000円/7000円) と ラム/テキーラ等の単品ボトルが大半。5月内に商品マスタへ追加登録する</div>
</div>
</div>
</div>
</div>''')

# Slide 12: 第4章(B)-ii データ補完計画 + POS↔レシピ価格不一致チェック
pms = DATA['recipe_match']['price_mismatches']
slides.append(f'''<div class="slide" id="slide-12">
<div class="slide-header"><h2><span class="ch-badge">第4章(B)-ii</span>データ補完計画 / POS価格 vs レシピ売価チェック</h2><span class="pn">12 / {TOTAL}</span></div>
<div class="msg-bar">matched 51品目の理論原価率 <strong>{tc_rate_matched*100:.1f}%</strong> / 全体の F&D 率 (PL食材+ドリンク÷売上) <strong>{(pl_apr_food_drink/pl_apr_sales*100):.1f}%</strong> — 5月のレシピ補完で母集団を拡大する</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">matched理論原価率と PL F&D 率</div>
<table class="dt sm">
<tr><th>指標</th><th class="r">値</th></tr>
<tr><td>matched理論原価 (4月)</td><td class="r b">{fmt_yen(tc['apr_total'])}</td></tr>
<tr><td>matched売上</td><td class="r">{fmt_yen(matched_sales)}</td></tr>
<tr class="highlight-row"><td>matched理論原価率</td><td class="r b">{tc_rate_matched*100:.1f}%</td></tr>
<tr><td>PL食材+ドリンク (4月計上)</td><td class="r">{fmt_yen(pl_apr_food_drink)}</td></tr>
<tr><td>PL F&D率 (vs PL売上)</td><td class="r b">{(pl_apr_food_drink/pl_apr_sales*100):.1f}%</td></tr>
</table>
<div class="sec-title o" style="margin-top:10px">5月の補完アクション (4項目)</div>
<ol class="nl o">
<li>オペ用簡易レシピ取り込み: ハイボール (152本) / ウイスキー単品 (28品/83本) / コース・飲み放題 (6品/128本) を商品マスタに追加登録</li>
<li>レシピ「位置付け」タグの埋め (99品中51品目が空欄)</li>
<li>POS価格 vs レシピ売価 不一致3件の整合 (右表参照)</li>
<li>POSカテゴリ「未設定」「その他」の整理 (飲み放題コース系)</li>
</ol>
</div>
<div class="col-half">
<div class="sec-title">POS価格 vs レシピ売価 不一致 (差¥50以上)</div>
<table class="dt sm">
<tr><th>商品</th><th class="r">POS価格</th><th class="r">レシピ価格</th><th class="r">差</th><th class="r">出数</th></tr>
{''.join(f"<tr><td>{p['name'][:18]}</td><td class='r b'>¥{int(p['pos_price']):,}</td><td class='r'>¥{int(p['recipe_price']):,}</td><td class='r {'pos' if p['diff']>=0 else 'neg'} b'>¥{int(p['diff']):+,}</td><td class='r'>{p['qty']}</td></tr>" for p in pms[:10])}
</table>
<div class="info-box" style="margin-top:8px;font-size:14px"><strong>テバルド・ビアンコ/ロッソ</strong>: POS¥6,500 (ボトル価格) vs レシピ¥1,200 (グラス価格) — レシピ側にボトル価格を別行追加で対応</div>
<div class="sec-title" style="margin-top:6px">F&D率 月次推移 (1-3月=シート / 4月=DB)</div>
<div id="chart-costrate" style="height:200px"></div>
</div>
</div>
</div>
</div>''')

# Slide 13: 第5章 コンセプト定着度
early_visits = sum(h['visits'] for h in DATA['hour_summary'] if h['bucket'] in ['~18時','18-20時'])
late_visits = sum(h['visits'] for h in DATA['hour_summary'] if h['bucket'] in ['22-24時','24時~'])
total_visits = apr['visits']
weekend_sales = sum(w['sales'] for w in DATA['weekday_summary'] if w['weekday'] in ['金','土'])
weekend_share = weekend_sales/apr['sales'] if apr['sales'] else 0
mori = next((p for p in DATA['products']['all'] if p['name']=='森のジントニック'),None)
hbh = next((p for p in DATA['products']['all'] if p['name']=='ハウスハイボール'),None)
slides.append(f'''<div class="slide" id="slide-13">
<div class="slide-header"><h2><span class="ch-badge">第5章</span>コンセプト定着度 — 「使いやすいダイニングバー／ラウンジ」化</h2><span class="pn">13 / {TOTAL}</span></div>
<div class="msg-bar">当月評価: <strong>停滞</strong> — 看板商品は安定もコース構造が逆行、平日早時間の伸びは限定的</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">用途タグ別 (POS+日報からの推定指標)</div>
<table class="dt sm">
<tr><th>軸</th><th class="r">4月</th><th class="r">参考(3月)</th><th class="c">評価</th></tr>
<tr><td>早時間(~20時) 構成</td><td class="r b">{early_visits/total_visits*100:.1f}%</td><td class="r">—</td><td class="c warn">→</td></tr>
<tr><td>深夜(22時~) 構成</td><td class="r b">{late_visits/total_visits*100:.1f}%</td><td class="r">—</td><td class="c warn">→</td></tr>
<tr><td>金土依存度</td><td class="r b">{weekend_share*100:.1f}%</td><td class="r">—</td><td class="c warn">→</td></tr>
<tr><td>コース利用率</td><td class="r b">{apr['course_share']*100:.1f}%</td><td class="r">{mar['course_share']*100:.1f}%</td><td class="c neg">↓ 逆行</td></tr>
<tr><td>1組人数</td><td class="r b">{apr['avg_party_size']:.2f}人</td><td class="r">{mar['avg_party_size']:.2f}人</td><td class="c pos">↑ 進行</td></tr>
</table>
<div class="sec-title o" style="margin-top:10px">看板商品の月次安定度</div>
<table class="dt sm">
<tr><th>商品</th><th class="r">4月</th><th class="r">3月</th><th class="c">判定</th></tr>
<tr><td>ハウスハイボール</td><td class="r b">{hbh['qty'] if hbh else 0}</td><td class="r">{hbh['qty_mar'] if hbh else 0}</td><td class="c {'pos' if hbh and hbh['qty_diff_mom']>=0 else 'neg'} b">{('上昇' if hbh and hbh['qty_diff_mom']>=10 else '安定' if hbh and abs(hbh['qty_diff_mom'])<10 else '低下')}</td></tr>
<tr><td>森のジントニック</td><td class="r b">{mori['qty'] if mori else 0}</td><td class="r">{mori['qty_mar'] if mori else 0}</td><td class="c {'pos' if mori and mori['qty_diff_mom']>=0 else 'neg'} b">{('上昇' if mori and mori['qty_diff_mom']>=10 else '安定' if mori and abs(mori['qty_diff_mom'])<10 else '低下')}</td></tr>
</table>
</div>
<div class="col-half">
<div class="sec-title">日報から読む来店動機 (4月{len(DATA['ai_reports'])}日分集計)</div>
<ul class="bl">
<li><strong>海外客比率が高い</strong>: フィンランド/Google検索流入/接待観光が頻出</li>
<li><strong>団体送別会・部門会</strong>: 4/3 24名貸切, 4/2 同窓会2次会など複数</li>
<li><strong>常連の戻り</strong>: アールガット好き等、リピート言及あり</li>
<li><strong>チョコレート (お通し)</strong>が会話の起点になる場面が多い</li>
<li><strong>「甘くないカクテル」</strong>提案リスト未整備が複数日に再発</li>
<li><strong>食材ロス記入欄</strong>の改善要望が日報側からも出ている</li>
</ul>
<div class="warn-box" style="margin-top:8px"><strong>判定: 停滞</strong>。看板（ハイボール・ジン）は機能、海外客流入の構造化は観察できるが、コース提案の機能不全と平日早時間（食事用途）の伸び鈍化で「ダイニングバー化」進度は不明確</div>
</div>
</div>
</div>
</div>''')

# Slide 14: 第6章 曜日/時間帯
strong_wd = sorted(DATA['weekday_summary'], key=lambda w:-w['sales_per_day'])[:2]
weak_wd = [w for w in sorted(DATA['weekday_summary'], key=lambda w:w['sales_per_day']) if w['days']>0][:2]

slides.append(f'''<div class="slide compact" id="slide-14">
<div class="slide-header"><h2><span class="ch-badge">第6章</span>曜日／時間帯サマリ</h2><span class="pn">14 / {TOTAL}</span></div>
<div class="msg-bar">強化曜日: <strong>{strong_wd[0]['weekday']}・{strong_wd[1]['weekday']}</strong> / 改善曜日: <strong>{weak_wd[0]['weekday']}・{weak_wd[1]['weekday']}</strong> (営業日あたり)</div>
<div class="slide-body">
<div id="chart-heatmap" style="height:240px"></div>
<div class="two-col" style="margin-top:6px">
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
<div id="chart-hour" style="height:200px"></div>
<div class="info-box" style="margin-top:5px">時間帯: 20-22時台が売上の山。22-24時の深夜帯が客単価最高ゾーン。<strong>早時間(~20時)構成{early_visits/total_visits*100:.1f}%</strong>が「ダイニングバー化」未達の根拠</div>
</div>
</div>
</div>
</div>''')

# Slide 15: 第7章 + 第8章
issue_keywords = {}
for ar in DATA['ai_reports']:
    txt = (ar.get('improvements','') or '')
    for kw in ['チョコレート','英語','カクテル','補充','ロス','人員','日報','改行','スタッフ','メニュー','レシピ','提案','在庫']:
        if kw in txt:
            issue_keywords[kw] = issue_keywords.get(kw,0)+1

slides.append(f'''<div class="slide" id="slide-15">
<div class="slide-header"><h2><span class="ch-badge">第7・8章</span>施策の結論 / 構造的ボトルネック</h2><span class="pn">15 / {TOTAL}</span></div>
<div class="msg-bar">施策ベース判断は限定的 — 業務改善カテゴリの再発: 補充オペ / 英語対応 / 甘くないカクテル提案</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title o">第7章 — 月内施策の結論</div>
<table class="dt sm">
<tr><th>施策</th><th>狙い</th><th class="c">継続/修正/停止</th></tr>
<tr><td>チョコレートお通し定常化</td><td>会話起点・購入導線</td><td class="c pos b">継続</td></tr>
<tr><td>多言語対応強化</td><td>海外客リピート</td><td class="c warn b">修正</td></tr>
<tr><td>甘くないカクテル提案リスト</td><td>提案揺れ解消</td><td class="c warn b">修正(作成中)</td></tr>
<tr><td>団体貸切受け入れ</td><td>大口売上</td><td class="c pos b">継続</td></tr>
<tr><td>コース予約導線</td><td>客単価底上げ</td><td class="c neg b">修正(機能不全)</td></tr>
</table>
<div class="warn-box" style="margin-top:8px">⚠ 媒体施策（食べログ/Google/HP）/ SNS施策の効果数値が日報からは読めず。第7章の本格的検証は<strong>施策ログ + UTM</strong>整備後</div>
</div>
<div class="col-half">
<div class="sec-title r">第8章 — 改善ポイント月内頻出 (日報集計)</div>
<table class="dt sm">
<tr><th>キーワード</th><th class="r">月内出現</th><th>分類</th></tr>
{''.join(f"<tr><td>{k}</td><td class='r b'>{v}</td><td>{('オペ/仕組み' if k in ['補充','スタッフ','人員','日報','改行','在庫'] else '商品/接客' if k in ['チョコレート','カクテル','メニュー','レシピ','提案'] else '商品/言語')}</td></tr>" for k,v in sorted(issue_keywords.items(),key=lambda x:-x[1])[:10])}
</table>
<div class="sec-title o" style="margin-top:6px">原因分類の比率 (推定)</div>
<ul class="bl o">
<li>仕組み: <strong>補充/役割分担/システム入力</strong> — オペ整備で解消可</li>
<li>人: <strong>提案揺れ/接客トーク標準化</strong> — トレーニング材料化</li>
<li>商品: <strong>コース提案フロー</strong> — メニュー設計から再構築</li>
</ul>
<div class="info-box" style="margin-top:6px">属人性リスク: 大泉さん入力の日報が大半 → <strong>記録の属人化</strong>が次の構造課題</div>
</div>
</div>
</div>
</div>''')

# Slide 16: 第9章 翌月の意思決定論点 (4本)
slides.append(f'''<div class="slide" id="slide-16">
<div class="slide-header"><h2><span class="ch-badge">第9章</span>翌月（5月）の意思決定論点 — 4本</h2><span class="pn">16 / {TOTAL}</span></div>
<div class="msg-bar">「検討する」「様子を見る」を排し、5月内に判断する論点だけに絞る</div>
<div class="slide-body">
<div class="card">
<div class="card-title r">論点1 — コース提案フロー再構築 (Owner判定 / 5月10日まで)</div>
<div>4月コース利用率1.6% (3月10.1%)。価格訴求／提案タイミング／メニュー構成の3点で <strong>「コース化が再構造的に成立する設計」</strong>を引くか、<strong>コース概念を諦めて単品ハイチケットに振る</strong>かを判断する。判断材料: 4月コース2件の中身分析、3月コース19件の中身分析、団体予約のコース化率。</div>
</div>
<div class="card">
<div class="card-title o">論点2 — 5月集客強化策の選定 (Owner判定 / 5月7日まで)</div>
<div>4月日平均¥{int(sales_per_day_apr/1000):,}k → 5月予算到達には日平均+¥17k必要。<strong>SNS投下／Google MAP最適化／予約導線改修</strong>のいずれに5月の追加予算を寄せるかを1本に絞る。判断材料: 4月の流入チャネル分布 (POS未取得なら5月から計測機構を入れる前提で意思決定)。</div>
</div>
<div class="card">
<div class="card-title">論点3 — PL月次計上ガバナンス (Manager判定 / 5月5日まで)</div>
<div>月次計上費目 (人件費・水道光熱費・ローン返済・税金) を <strong>月初5営業日以内に確定するルールを制定</strong>する。担当者・入力導線・締切日を決定し5月分から適用。</div>
</div>
<div class="card">
<div class="card-title">論点4 — レシピ名寄せ補完 / オペ用簡易レシピの母集団化 (5月20日まで)</div>
<div>名寄せ出数比率 {mc['qty_match_rate']*100:.1f}% (ハイボール/ウイスキー/飲み放題/黒板メニューがレシピ未登録)。<strong>オペ用簡易レシピシート (40+品目) を商品一覧へ取り込み</strong>、<strong>「甘くないカクテル」提案リスト</strong>を整備する。担当者を指名し完了日をコミット。</div>
</div>
</div>
</div>''')

# Slide 17: 付録 - データソース・前提
slides.append(f'''<div class="slide compact" id="slide-17">
<div class="slide-header"><h2><span class="ch-badge">付録</span>前提・データソース・追補項目</h2><span class="pn">17 / {TOTAL}</span></div>
<div class="msg-bar">本資料の出典・前提・追補必要事項の総まとめ</div>
<div class="slide-body">
<div class="two-col">
<div class="col-half">
<div class="sec-title">データソース</div>
<table class="dt sm">
<tr><th>区分</th><th>ソース</th><th class="c">状態</th></tr>
<tr><td>POS明細</td><td>Production DB salesData</td><td class="c pos">✓</td></tr>
<tr><td>POS集計対象</td><td>2026-04-01〜04-26 ({bd_apr}営業日 / 126会計)</td><td class="c pos">✓</td></tr>
<tr><td>AI日報</td><td>Production DB dailyReport ({len(DATA['ai_reports'])}件)</td><td class="c pos">✓</td></tr>
<tr><td>店舗日次サマリ</td><td>Production DB dailyStoreSummary ({len(DATA['daily_summaries'])}件)</td><td class="c pos">✓</td></tr>
<tr><td>PL 1-2月実績</td><td>Spreadsheet 新PL管理（移管前）</td><td class="c pos">✓</td></tr>
<tr><td>PL 4月計上分</td><td>Production DB plDailyExpense ({fmt_yen(pl_apr_exp)} / 食材・ドリンク・広告費・家賃・備品・管理費)</td><td class="c pos">✓</td></tr>
<tr><td>PL 4月予算</td><td>Spreadsheet 新PL管理（移管前）</td><td class="c pos">✓</td></tr>
<tr><td>レシピシート (99品目)</td><td>Spreadsheet 1WjJaog... 商品一覧</td><td class="c pos">✓</td></tr>
<tr><td>名寄せマスタ</td><td>POS×レシピ exact + 正規化マッチ (出数{mc['qty_match_rate']*100:.1f}%)</td><td class="c pos">✓</td></tr>
</table>
<div class="sec-title o" style="margin-top:6px">数字定義・前提</div>
<ul class="bl">
<li>金額 = POS account_total (税込前提)</li>
<li>客数 = customer_count 合計 / 営業日 = POS会計あり日</li>
<li>客単価 = 売上 ÷ 客数 (1人あたり)</li>
<li>主因分解 = 営業日換算 / 寄与額の絶対値で判定</li>
</ul>
</div>
<div class="col-half">
<div class="sec-title">5月のデータ運用アクション</div>
<ol class="nl o">
<li>PL月次計上 (人件費・水道光熱費・ローン返済・税金) を月初5営業日以内に確定するルール化</li>
<li>レシピ「オペ用簡易レシピ」40+品目を商品一覧シートへ取り込み (名寄せ率の母集団拡大)</li>
<li>商品位置付けタグ (看板/準看板/スピード) を全99品目に埋める</li>
<li>区分2a 23品目 (4月のみ × レシピなし) を商品リストへ追加登録</li>
<li>媒体・施策ログ + UTM計測の整備 (第7章の本格分析対応)</li>
</ol>
<div class="sec-title o" style="margin-top:6px">レビュー観点 (review_checklist.md 参照)</div>
<ul class="bl o">
<li>主因分解の解釈は妥当か (客数 vs 単価)</li>
<li>整理候補の名指しが粗利を考慮できているか</li>
<li>5月意思決定論点は「判断する」か (検討/様子見でない)</li>
<li>固定費耐性の前提値 (¥1.7M前後) は最新か</li>
</ul>
<div class="info-box" style="margin-top:6px">本資料は2026年4月度 BFA 本番月報 (確定版)。次回月報作成時は <code>月報作成手順書_v2.md</code> を参照</div>
</div>
</div>
</div>
</div>''')

# Slide 18: 末尾 (チェックサム + 次回月報のメモ)
slides.append(f'''<div class="slide slide-title" id="slide-18" style="background:linear-gradient(135deg,#08321F 0%,#0F4C3A 100%)">
<h2 style="font-size:36px">本月報の生成情報</h2>
<div style="margin-top:30px;font-size:18px;line-height:2">
<p>店舗: <strong>BAR FIVE Arrows</strong> (store_code=bfa-001)</p>
<p>対象期間: <strong>2026年4月 (POS最終日 {DATA['meta']['last_pos_date']})</strong></p>
<p>生成日時: <strong>{DATA['meta']['generated_at']}</strong></p>
<p>レシピ名寄せ率: <strong>品目{mc['match_rate']*100:.1f}% / 出数{mc['qty_match_rate']*100:.1f}%</strong></p>
<p style="margin-top:30px;opacity:.8">— 構成: 分析観点ガイド v2 §2 章立て準拠 (10章) —</p>
</div>
<div class="accent" style="margin-top:30px">END OF MONTHLY REPORT</div>
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
print(f'[ok] {OUT} ({os.path.getsize(OUT)/1024:.1f} KB, {len(slides)} slides)', file=sys.stderr)
