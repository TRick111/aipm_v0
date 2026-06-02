#!/usr/bin/env python3
"""客層分析①②③スライドを W21 HTML に挿入し、スライド番号とprogress-barを再計算。"""

from __future__ import annotations
import re
from pathlib import Path

HTML = Path(__file__).parent / "20260518_20260524_BAR_FIVE_Arrows_週次報告資料.html"
TOTAL = 31  # 新合計枚数

# ----- データ（W21 業務日基準 集計値、analysis_scriptと同convention） -----
DENOM = {
    "sales": 1_580_820,
    "cust": 236,
    "orgs": 72,
}

BFA1 = {
    "sales_m": 83_470,
    "cust_m": 22,
    "orgs_m": 7,
}
BFA2 = {
    "sales_m": 267_500,
    "cust_m": 68,
    "orgs_m": 3,
}
BFA3 = {
    "sales_m": 0,
    "cust_m": 0,
    "orgs_m": 0,
}


def pct(numer: int, denom: int) -> str:
    if denom == 0:
        return "0.0%"
    return f"{numer / denom * 100:.1f}%"


def build_segment_slide(slide_no: int, title: str, icon: str, key: str, msg: str,
                        d: dict, color_main: str, donut_color: str, extra_classification: str,
                        narrative_html: str, footer: str) -> str:
    """客層分析スライドHTMLを生成。"""
    sales_pct = pct(d["sales_m"], DENOM["sales"])
    cust_pct = pct(d["cust_m"], DENOM["cust"])
    orgs_pct = pct(d["orgs_m"], DENOM["orgs"])
    sales_non = DENOM["sales"] - d["sales_m"]
    cust_non = DENOM["cust"] - d["cust_m"]
    orgs_non = DENOM["orgs"] - d["orgs_m"]
    progress = slide_no / TOTAL * 100

    return f"""<!-- ==================== SLIDE {slide_no}: Segment {key} ==================== -->
<div class="slide" id="slide-{slide_no}">
  <div class="slide-header"><h2><span class="section-tag">客層分析</span>{icon} {title}</h2><span class="pn">{slide_no} / {TOTAL}</span><div class="progress-bar" style="width:{progress:.2f}%"></div></div>
  <div class="msg-bar">{msg}</div>
  <div class="classification-bar">
    <ul>
      <li>集計対象: 2026-W21 の業務日（2026/05/18 6:00 〜 2026/05/25 5:59 JST、朝6時境界）</li>
      <li>{extra_classification}</li>
      <li>数値の分母: rawdata.csv（prod DB 正本）業務日基準 — 72組／236人／¥1,580,820</li>
    </ul>
  </div>
  <div class="slide-body with-msg">
    <div class="seg-grid">
      <div class="seg-pane left">
        <h3>💰 売上比率</h3>
        <div class="pct">{sales_pct}</div>
        <div class="row"><span>該当</span><span class="v">¥{d["sales_m"]:,}</span></div>
        <div class="row"><span>非該当</span><span class="v dim">¥{sales_non:,}</span></div>
        <div class="row"><span>合計</span><span class="v dim">¥{DENOM["sales"]:,}</span></div>
      </div>
      <div class="seg-pane middle">
        <h3>👥 客数比率</h3>
        <div class="pct">{cust_pct}</div>
        <div class="row"><span>該当</span><span class="v">{d["cust_m"]:,}人</span></div>
        <div class="row"><span>非該当</span><span class="v dim">{cust_non:,}人</span></div>
        <div class="row"><span>合計</span><span class="v dim">{DENOM["cust"]:,}人</span></div>
      </div>
      <div class="seg-pane right">
        <h3>🧾 組数比率</h3>
        <div class="pct">{orgs_pct}</div>
        <div class="row"><span>該当</span><span class="v">{d["orgs_m"]:,}組</span></div>
        <div class="row"><span>非該当</span><span class="v dim">{orgs_non:,}組</span></div>
        <div class="row"><span>合計</span><span class="v dim">{DENOM["orgs"]:,}組</span></div>
      </div>
      <div class="seg-donut">
        <div class="ttl">{key} vs 非該当（売上ベース）</div>
        <div id="donut-{key.lower()}" data-donut-key="{key.lower()}"
             data-match="{d['sales_m']}" data-non="{sales_non}"
             data-color="{donut_color}" style="height:200px"></div>
        <div class="lg">
          <span><span class="sw" style="background:{donut_color}"></span>{key} ({sales_pct})</span><br>
          <span><span class="sw" style="background:#E2E8F0"></span>非該当</span>
        </div>
      </div>
    </div>
    {narrative_html}
  </div>
  <div class="footer-cite">{footer}</div>
</div>
"""


# ----- BFA-1 インバウンド -----
slide_bfa1 = build_segment_slide(
    slide_no=24,
    title="客層分析①：インバウンド比率",
    icon="🌏",
    key="インバウンド",
    msg="💡 インバウンド客 7組22人で売上¥83,470（5.3%）。客数比率9.3%・組数比率9.7%と一定の海外顧客接点が機能",
    d=BFA1,
    color_main="#3B82F6",
    donut_color="#3B82F6",
    extra_classification=(
        "抽出キー: BFA-1 ＝ エアレジ会計明細『メモ』カラムに「海外」を部分一致（§B-3）。"
        "メモ「海外」記入運用は2026-04開始（§B-7） — W21終了日2026-05-24 ≥ 2026-04 のため表示"
    ),
    narrative_html=(
        '<div class="seg-summary">該当 <b>7組</b>（2026-05-19・5/21・5/22×3・5/23×2）。'
        'エアレジメモ一致は <b>9件</b> だが、業務日が2026-05-25にずれる2件はW22側に計上。'
        '客単価 ¥83,470 ÷ 22人 = <b>¥3,794/人</b> と通常BAR平均より低めだが、'
        '組数構成比9.7%はGoogle検索経由の海外客が定常化していることを示唆。</div>'
    ),
    footer="出典: エアレジ会計明細（メモ欄）／ 分母: rawdata.csv 業務日基準 ／ 集計対象: 2026-W21 の業務日（朝6時境界）",
)

# ----- BFA-2 CLP社員 -----
slide_bfa2 = build_segment_slide(
    slide_no=25,
    title="客層分析②：CLP社員（単発利用）比率",
    icon="👤",
    key="CLP関連",
    msg="✅ CLP関連 3組68人で売上¥267,500（16.9%）。客数構成比28.8%とグループ大口利用が安定した法人収益柱",
    d=BFA2,
    color_main="#22C55E",
    donut_color="#22C55E",
    extra_classification=(
        "抽出キー: BFA-2 ＝ rawdata.csv 明細行『メニュー名』に「CLP」を部分一致（§B-3）／"
        "BFA-5（コース）・BFA-6（その他CLPコース）と同一会計を含み合計値は二重計上前提"
    ),
    narrative_html=(
        '<div class="seg-summary">3組のみで <b>68人</b> を取り込み、1組あたり <b>22.7人</b> の大型グループ利用。'
        '平均単価 ¥267,500 ÷ 68人 = <b>¥3,934/人</b> と全体¥6,698と比べ低めだが、'
        '組数比率4.2% × 客数比率28.8% の "少数で多人数" 構造で固定収益を下支え。</div>'
    ),
    footer="出典: エアレジ会計明細（メニュー名）／ 集計対象: 2026-W21 の業務日（朝6時境界）",
)

# ----- BFA-3 イベント -----
slide_bfa3 = f"""<!-- ==================== SLIDE 26: Segment イベント ==================== -->
<div class="slide" id="slide-26">
  <div class="slide-header"><h2><span class="section-tag">客層分析</span>🎉 客層分析③：イベント比率</h2><span class="pn">26 / 31</span><div class="progress-bar" style="width:{26/31*100:.2f}%"></div></div>
  <div class="msg-bar">💡 W21はイベント開催ゼロ。4月の¥430K（14.2%）と対比し、5月後半は通常BAR営業＋大口ワインに収益が集中した週</div>
  <div class="classification-bar">
    <ul>
      <li>集計対象: 2026-W21 の業務日（2026/05/18 6:00 〜 2026/05/25 5:59 JST、朝6時境界）</li>
      <li>抽出キー: BFA-3 ＝ rawdata.csv 明細行『カテゴリ』が「イベント」に完全一致（§B-3）</li>
      <li>運用注釈: 4月のイベント月（¥430K / 109人）と対比、W21はイベント枠ゼロの通常運用週</li>
      <li>数値の分母: rawdata.csv（prod DB 正本）業務日基準 — 72組／236人／¥1,580,820</li>
    </ul>
  </div>
  <div class="slide-body with-msg">
    <div class="seg-grid">
      <div class="seg-pane left">
        <h3>💰 売上比率</h3>
        <div class="pct">0.0%</div>
        <div class="row"><span>該当</span><span class="v">¥0</span></div>
        <div class="row"><span>非該当</span><span class="v dim">¥1,580,820</span></div>
        <div class="row"><span>合計</span><span class="v dim">¥1,580,820</span></div>
      </div>
      <div class="seg-pane middle">
        <h3>👥 客数比率</h3>
        <div class="pct">0.0%</div>
        <div class="row"><span>該当</span><span class="v">0人</span></div>
        <div class="row"><span>非該当</span><span class="v dim">236人</span></div>
        <div class="row"><span>合計</span><span class="v dim">236人</span></div>
      </div>
      <div class="seg-pane right">
        <h3>🧾 組数比率</h3>
        <div class="pct">0.0%</div>
        <div class="row"><span>該当</span><span class="v">0組</span></div>
        <div class="row"><span>非該当</span><span class="v dim">72組</span></div>
        <div class="row"><span>合計</span><span class="v dim">72組</span></div>
      </div>
      <div class="seg-donut">
        <div class="ttl">イベント vs 非該当（売上ベース）</div>
        <div class="seg-zero" style="margin-top:6px;">
          <div class="big">0件</div>
          <div class="lb">W21 イベント該当ゼロ</div>
        </div>
        <div class="lg" style="margin-top:6px;">
          <span><span class="sw" style="background:#F97316"></span>イベント (0%)</span><br>
          <span><span class="sw" style="background:#E2E8F0"></span>通常営業 (100%)</span>
        </div>
      </div>
    </div>
    <div class="seg-summary">W21の売上¥1.58Mは通常BAR営業＋水曜の大口ワイン¥613Kによる構造（イベント要因 <b>ゼロ</b>）。
    4月の¥430K（14.2%）が示した「イベント主導型収益柱」は5月後半に持続せず、再現のためのイベント企画ロードマップ整備が次月以降の課題。</div>
  </div>
  <div class="footer-cite">出典: エアレジ会計明細（カテゴリ）／ 集計対象: 2026-W21 の業務日（朝6時境界）</div>
</div>
"""

new_slides_html = "\n" + slide_bfa1 + "\n" + slide_bfa2 + "\n" + slide_bfa3


# ----- HTML 読み込み -----
text = HTML.read_text(encoding="utf-8")

# 1) 既存の "X / 28" を "X / 31" にリプレース
text = re.sub(r"(\d+) / 28(?=\s*<)", lambda m: f"{m.group(1)} / {TOTAL}", text)

# 2) 既存スライド 2..23 の progress-bar 幅を再計算（28 → 31 基準）
# 既存値は 2/28..23/28 ベース、新値は 2/31..23/31
old_to_new = {}
for i in range(2, 24):
    old_pct = i / 28 * 100
    new_pct = i / TOTAL * 100
    old_str = f'width:{old_pct:.2f}%'
    new_str = f'width:{new_pct:.2f}%'
    old_to_new[old_str] = new_str
for old, new in old_to_new.items():
    text = text.replace(old, new)

# 3) 既存スライド 24..28 を 27..31 にリナンバー（前から順に置換）
# slide-N → slide-(N+3) for N in 28..24 (逆順で衝突回避)
for old_n in range(28, 23, -1):
    new_n = old_n + 3
    new_pct = new_n / TOTAL * 100
    old_pct = old_n / 28 * 100  # 旧 progress 値（28 ベース）
    # slide-N の id
    text = text.replace(f'id="slide-{old_n}"', f'id="slide-{new_n}"', 1)
    # "N / 28" → "(new_n) / 31"  ※（2は既に置換済なのでスキップ）
    # 既に "X / 31" に置換済みなので "N / 31" → "(new_n) / 31" として再置換
    # 直前のslide-IDが書き換わっているのでブロック単位で1個ずつ
    text = re.sub(rf'(<h2><span class="section-tag">[^<]+</span>[^<]+</h2><span class="pn">){old_n} / {TOTAL}(</span>)',
                  rf'\g<1>{new_n} / {TOTAL}\g<2>', text, count=1)
    # progress-bar 幅: 旧 (N/28) → 新 (new_n/31)
    text = text.replace(f'width:{old_pct:.2f}%', f'width:{new_pct:.2f}%', 1)

# 4) 新スライド 24-26 をslide 23 と 旧slide-24（現在slide-27）の間に挿入
# 挿入アンカーは slide-27 の HTMLコメント "<!-- ==================== SLIDE 24: Weekly Strengths ==================== -->"
anchor_old = "<!-- ==================== SLIDE 24: Weekly Strengths ==================== -->"
anchor_new = "<!-- ==================== SLIDE 27: Weekly Strengths ==================== -->"
# 旧アンカーを新名前へ
text = text.replace(anchor_old, anchor_new, 1)
# その前に新スライドを挿入
text = text.replace(anchor_new, new_slides_html + "\n" + anchor_new, 1)

# 5) 旧スライドコメントも更新
text = text.replace(
    "<!-- ==================== SLIDE 25: Weekly Challenges ==================== -->",
    "<!-- ==================== SLIDE 28: Weekly Challenges ==================== -->", 1)
text = text.replace(
    "<!-- ==================== SLIDE 26: Actions 1 - Menu & Marketing ==================== -->",
    "<!-- ==================== SLIDE 29: Actions 1 - Menu & Marketing ==================== -->", 1)
text = text.replace(
    "<!-- ==================== SLIDE 27: Actions 2 - Customer & Operations ==================== -->",
    "<!-- ==================== SLIDE 30: Actions 2 - Customer & Operations ==================== -->", 1)
text = text.replace(
    "<!-- ==================== SLIDE 28: Actions 3 - Staff Training ==================== -->",
    "<!-- ==================== SLIDE 31: Actions 3 - Staff Training ==================== -->", 1)

# 6) Plotly Donut 描画スクリプトを Plotly セクションの末尾に追加
donut_js = """
// ===== Segment Donuts (Plotly, v1.1 追加 / 共通ルール K-5) =====
document.querySelectorAll('[data-donut-key]').forEach(function(el){
  var match = parseFloat(el.getAttribute('data-match'));
  var non = parseFloat(el.getAttribute('data-non'));
  var color = el.getAttribute('data-color') || '#3B82F6';
  var total = match + non;
  var pct = total ? (match/total*100) : 0;
  var key = el.getAttribute('data-donut-key');
  var trace = {
    type: 'pie', hole: 0.55,
    labels: [key, '非該当'],
    values: [match, non],
    pull: [0.08, 0],
    marker: {colors: [color, '#E2E8F0'], line:{color:'#ffffff', width:2}},
    textinfo: 'none',
    hoverinfo: 'label+percent+value',
    sort: false, direction: 'clockwise'
  };
  var layout = {
    margin:{t:0,r:0,b:0,l:0},
    showlegend: false,
    annotations:[{
      text: '<b>'+pct.toFixed(1)+'%</b><br><span style="font-size:10px;color:#6B7280">売上構成比</span>',
      showarrow:false, font:{size:22,color:color}
    }],
    paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)'
  };
  Plotly.newPlot(el, [trace], layout, {displayModeBar:false, responsive:true});
});
"""

# Plotly セクション末尾(最初の "</script>" 直前)に donut_js を挿入
marker = "// ==================== CHARTS (Plotly.js) ===================="
# 最初のscript閉じタグの前に挿入: '<script>' の対になる '</script>' を順番に探す
plotly_start = text.find("<!-- ==================== CHARTS (Plotly.js) ==================== -->")
assert plotly_start != -1, "Plotly section marker not found"
script_open = text.find("<script>", plotly_start)
script_close = text.find("</script>", script_open)
assert script_close != -1, "Plotly closing script tag not found"
text = text[:script_close] + donut_js + text[script_close:]

HTML.write_text(text, encoding="utf-8")
print("✅ HTML 更新完了:", HTML)
print(f"   - 全 {TOTAL} 枚に拡張")
print(f"   - スライド 24/25/26: 客層分析①②③（インバウンド / CLP / イベント）")
print(f"   - 旧 24-28 を 27-31 にリナンバー")
print(f"   - progress-bar / slide-id / pn を全件更新")
