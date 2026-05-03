#!/usr/bin/env python3
"""
POS×レシピ マッピング 3区分 詳細をMarkdown表で出力
v2: 田中さん指示で 3月/4月 の出現パターン別に細分化

田中さん背景: 4月リニューアルで商品リストを更新。
→ 4月にPOSあるけど商品リスト(レシピ)にないもの = ★要確認 (リニューアル後追加で登録漏れの疑い)
→ 3月にPOSあったけど商品リストにない = リニューアルで落ちた商品 (情報用)

出力: mapping/pos_recipe_mapping_detail.md
- 区分1: マッチ済 (POSあり × レシピあり) — 両月/4月のみ/3月のみ で再分類
- 区分2: POSあり × レシピなし (要確認) — 両月/4月のみ★/3月のみ で再分類
- 区分3: レシピあり × POSなし — 4月で出ない理由を分析
"""
import json, os, re, datetime as dt
from collections import defaultdict

ROOT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報'
DATA = json.load(open(os.path.join(ROOT, 'data/analytics2.json'), encoding='utf-8'))
recipe = json.load(open(os.path.join(ROOT, 'data/recipe.json'), encoding='utf-8'))

mc = DATA['recipe_match']['summary']
all_pos = DATA['recipe_match']['all_pos_records']

def normalize(s):
    if not s: return ''
    return re.sub(r'[\s 　・/\-_（）()「」『』【】"\'.]','',str(s)).lower()

# レシピ商品名のセット
matched_recipe_names = set()
for r in all_pos:
    if r.get('matched') and r.get('recipe_name'):
        matched_recipe_names.add(r['recipe_name'])

# 区分3 (レシピあり / POSなし): レシピ商品名のうち、4月にも3月にもPOS出現しなかった
recipe_only = []
for r in recipe:
    name = r.get('メニュー名','')
    if not name: continue
    if name in matched_recipe_names: continue
    recipe_only.append(r)

# 月別分類関数
def status(rec):
    am, ap = rec.get('appeared_in_mar'), rec.get('appeared_in_apr')
    if am and ap: return 'both'
    if ap and not am: return 'apr_only'
    if am and not ap: return 'mar_only'
    return 'neither'

# === 区分1: マッチ済 ===
matched_both = [r for r in all_pos if r.get('matched') and status(r)=='both']
matched_apr = [r for r in all_pos if r.get('matched') and status(r)=='apr_only']
matched_mar = [r for r in all_pos if r.get('matched') and status(r)=='mar_only']

# === 区分2: POSあり / レシピなし ===
unmat_both = [r for r in all_pos if not r.get('matched') and status(r)=='both']
unmat_apr = [r for r in all_pos if not r.get('matched') and status(r)=='apr_only']
unmat_mar = [r for r in all_pos if not r.get('matched') and status(r)=='mar_only']

def classify_unmatched(name, cat):
    n = name or ''
    c = cat or ''
    if n in ('tablecharge','No charge','no charge'): return 'チャージ系'
    if 'コース' in n or 'CLP' in n or '飲み放題' in n: return 'コース・飲み放題'
    if 'ハイボール' in n: return 'ハイボール'
    if 'ウイスキー' in c or any(w in n for w in ['余市','タリスカー','グレンリベット','ワイルドターキー','イチローズ','響','山崎','白州','ボウモア','ラフロイグ','フロールデカーニャ','ハイランドパーク','ベンネヴィス','ハーパー','ジョニーウォーカー','グレンフィディック','ニッカ','ロンサカパ','ロイヤルセンテナリオ']): return 'ウイスキー・ラム単品'
    if 'ワイン' in c or 'スパークリング' in n or 'カヴァ' in n: return 'ワイン'
    if 'ビール' in c or 'ビール' in n: return 'ビール'
    if 'テキーラ' in c or 'テキーラ' in n: return 'テキーラ'
    if c in ('その他','未設定','黒板メニュー') or '黒板' in n: return 'その他/未整理'
    return 'レシピ未登録'

# Build markdown
out = []
out.append('# POS × レシピ マッピング 3区分 詳細 (3月/4月分類版)\n')
out.append(f'**生成日**: {dt.date.today().isoformat()}')
out.append('**対象月**: 2026-04 (リニューアル後初月)')
out.append('**比較**: 2026-03 (リニューアル前)')
out.append(f'**POS unique 商品数**: 3月={DATA["recipe_match"]["mar_pos_unique_count"]} / 4月={DATA["recipe_match"]["apr_pos_unique_count"]}')
out.append('**レシピマスタ**: Spreadsheet `1WjJaogeoRzA3BfO8ldohym5lywniVBApg1BxtINs8CA` 商品一覧シート (99品目)\n')
out.append('> 📌 **背景**: 2026年4月にBFAリニューアル実施。商品リスト(レシピ)も同時に更新された。本資料は「4月にPOSにあるが商品リストにない商品」=リニューアル後の登録漏れ候補を特定するために、3月/4月の出現パターンで再分類している。\n')

# サマリ
out.append('## サマリ')
out.append('')
out.append('| 区分 | 両月 | 4月のみ ★ | 3月のみ | 合計品目 |')
out.append('|---|---:|---:|---:|---:|')
out.append(f'| 区分1: マッチ済 (POS○ × レシピ○) | {len(matched_both)} | {len(matched_apr)} | {len(matched_mar)} | {len(matched_both)+len(matched_apr)+len(matched_mar)} |')
out.append(f'| **区分2: POS○ × レシピ✗ ★要確認★** | {len(unmat_both)} | **{len(unmat_apr)}** | {len(unmat_mar)} | {len(unmat_both)+len(unmat_apr)+len(unmat_mar)} |')
out.append(f'| 区分3: POS✗ × レシピ○ (両月とも未出現) | — | — | — | {len(recipe_only)} |')
out.append('')
out.append('★ **「4月のみ」区分2** が最重要: リニューアル後にPOS出現するも商品リスト未登録の品目。商品リスト更新時の登録漏れ or 急遽追加された未登録商品の可能性。')
out.append('')
out.append('---')
out.append('')

# === 区分1: マッチ済 ===
out.append('## 区分1: マッチ済 (POS出現あり + レシピあり)')
out.append('')

def format_matched_row(i, m):
    cr = (m.get('cost_rate') or 0)*100
    return (f"| {i} | {m['pos_name']} | {m.get('recipe_name') or '—'} | "
            f"{m.get('qty_mar',0)} | {m.get('qty',0)} | "
            f"¥{int(m.get('sales_mar',0)):,} | ¥{int(m.get('sales',0)):,} | "
            f"¥{int(m.get('price_recipe') or 0):,} | ¥{int(m.get('cost_unit') or 0):,} | "
            f"{cr:.1f}% | {m.get('位置付け') or '—'} | {m.get('category_recipe') or '—'} |")

out.append('### 区分1a: 両月 (3月も4月も継続)')
out.append('')
out.append('| # | POS商品名 | レシピ商品名 | 3月出数 | 4月出数 | 3月売上 | 4月売上 | レシピ売価 | レシピ原価 | 原価率 | 位置付け | カテゴリ |')
out.append('|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|')
for i,m in enumerate(sorted(matched_both, key=lambda x:-x['qty']), 1):
    out.append(format_matched_row(i, m))
out.append('')

out.append('### 区分1b: 4月のみ (リニューアル後新規 or 季節商品)')
out.append('')
if matched_apr:
    out.append('| # | POS商品名 | レシピ商品名 | 4月出数 | 4月売上 | レシピ売価 | レシピ原価 | 原価率 | 位置付け | カテゴリ |')
    out.append('|---:|---|---|---:|---:|---:|---:|---:|---|---|')
    for i,m in enumerate(sorted(matched_apr, key=lambda x:-x['qty']), 1):
        cr = (m.get('cost_rate') or 0)*100
        out.append(f"| {i} | {m['pos_name']} | {m.get('recipe_name') or '—'} | {m.get('qty',0)} | ¥{int(m.get('sales',0)):,} | ¥{int(m.get('price_recipe') or 0):,} | ¥{int(m.get('cost_unit') or 0):,} | {cr:.1f}% | {m.get('位置付け') or '—'} | {m.get('category_recipe') or '—'} |")
else:
    out.append('_(該当なし)_')
out.append('')

out.append('### 区分1c: 3月のみ (4月でPOS出現なし — リニューアルで落ちた可能性)')
out.append('')
if matched_mar:
    out.append('| # | POS商品名 | レシピ商品名 | 3月出数 | 3月売上 | レシピ売価 | レシピ原価 | 原価率 | 位置付け | カテゴリ |')
    out.append('|---:|---|---|---:|---:|---:|---:|---:|---|---|')
    for i,m in enumerate(sorted(matched_mar, key=lambda x:-x['qty_mar']), 1):
        cr = (m.get('cost_rate') or 0)*100
        out.append(f"| {i} | {m['pos_name']} | {m.get('recipe_name') or '—'} | {m.get('qty_mar',0)} | ¥{int(m.get('sales_mar',0)):,} | ¥{int(m.get('price_recipe') or 0):,} | ¥{int(m.get('cost_unit') or 0):,} | {cr:.1f}% | {m.get('位置付け') or '—'} | {m.get('category_recipe') or '—'} |")
else:
    out.append('_(該当なし)_')
out.append('')
out.append('---')
out.append('')

# === 区分2: POS出現あり / レシピなし ===
out.append('## 区分2: POS出現あり / レシピシート未登録 ★要確認★')
out.append('')
out.append('### 区分2a: 4月のみ × レシピなし ★最重要 (リニューアル後追加で登録漏れの疑い)')
out.append('')
out.append('リニューアル(4月)以降にPOSに登場したが商品一覧シートに無い商品。**商品マスタ追加登録の要否を確認**。')
out.append('')
if unmat_apr:
    # 分類別グルーピング
    by_class_apr = defaultdict(list)
    for u in unmat_apr:
        by_class_apr[classify_unmatched(u['pos_name'], u.get('category_pos',''))].append(u)
    for cls in sorted(by_class_apr.keys(), key=lambda k:-sum(u['qty'] for u in by_class_apr[k])):
        items = by_class_apr[cls]
        sub_qty = sum(u['qty'] for u in items)
        sub_sales = sum(u['sales'] for u in items)
        out.append(f'#### {cls} ({len(items)}品目 / {sub_qty}出数 / ¥{sub_sales:,.0f})')
        out.append('')
        out.append('| # | POS商品名 | POSカテゴリ | 4月出数 | 4月売上 | 平均価格 |')
        out.append('|---:|---|---|---:|---:|---:|')
        for i,u in enumerate(sorted(items, key=lambda x:-x['qty']), 1):
            avg = u['sales']/u['qty'] if u['qty'] else 0
            out.append(f"| {i} | {u['pos_name']} | {u.get('category_pos') or '—'} | {u['qty']} | ¥{int(u['sales']):,} | ¥{int(avg):,} |")
        out.append('')
else:
    out.append('_(該当なし)_')
    out.append('')

out.append('### 区分2b: 両月 × レシピなし (恒常的に商品リスト未登録)')
out.append('')
out.append('3月にも4月にもPOSに出るが商品リストに無い商品。長期的に登録されていないため、登録要否の判断が必要。')
out.append('')
if unmat_both:
    by_class_both = defaultdict(list)
    for u in unmat_both:
        by_class_both[classify_unmatched(u['pos_name'], u.get('category_pos',''))].append(u)
    for cls in sorted(by_class_both.keys(), key=lambda k:-sum(u['qty'] for u in by_class_both[k])):
        items = by_class_both[cls]
        sub_qty4 = sum(u['qty'] for u in items)
        sub_qty3 = sum(u['qty_mar'] for u in items)
        out.append(f'#### {cls} ({len(items)}品目 / 3月{sub_qty3}本 / 4月{sub_qty4}本)')
        out.append('')
        out.append('| # | POS商品名 | POSカテゴリ | 3月出数 | 4月出数 | 3月売上 | 4月売上 |')
        out.append('|---:|---|---|---:|---:|---:|---:|')
        for i,u in enumerate(sorted(items, key=lambda x:-x['qty']), 1):
            out.append(f"| {i} | {u['pos_name']} | {u.get('category_pos') or '—'} | {u.get('qty_mar',0)} | {u['qty']} | ¥{int(u.get('sales_mar',0)):,} | ¥{int(u['sales']):,} |")
        out.append('')
else:
    out.append('_(該当なし)_')
    out.append('')

out.append('### 区分2c: 3月のみ × レシピなし (リニューアルで落ちた商品)')
out.append('')
out.append('3月にPOSにあったが4月では出現しない、かつ商品リストにも無い商品。情報用 (アクションは不要)。')
out.append('')
if unmat_mar:
    by_class_mar = defaultdict(list)
    for u in unmat_mar:
        by_class_mar[classify_unmatched(u['pos_name'], u.get('category_pos',''))].append(u)
    out.append('| 分類 | 品目数 | 3月出数 | 3月売上 |')
    out.append('|---|---:|---:|---:|')
    for cls in sorted(by_class_mar.keys(), key=lambda k:-sum(u['qty_mar'] for u in by_class_mar[k])):
        items = by_class_mar[cls]
        out.append(f"| {cls} | {len(items)} | {sum(u['qty_mar'] for u in items):,} | ¥{sum(u['sales_mar'] for u in items):,.0f} |")
    out.append('')
    out.append('<details>')
    out.append('<summary>個別品目を見る (102件)</summary>')
    out.append('')
    out.append('| # | POS商品名 | POSカテゴリ | 3月出数 | 3月売上 |')
    out.append('|---:|---|---|---:|---:|')
    for i,u in enumerate(sorted(unmat_mar, key=lambda x:-x['qty_mar']), 1):
        out.append(f"| {i} | {u['pos_name']} | {u.get('category_pos') or '—'} | {u['qty_mar']} | ¥{int(u['sales_mar']):,} |")
    out.append('</details>')
    out.append('')
else:
    out.append('_(該当なし)_')
    out.append('')
out.append('---')
out.append('')

# === 区分3: レシピあり / POSなし ===
out.append('## 区分3: レシピシートあり / POS出現なし (3月も4月も売上ゼロ)')
out.append('')
out.append(f'レシピマスタには登録されているが、3月・4月どちらのPOSにも出現しなかった商品 ({len(recipe_only)}品目)。')
out.append('販売停止 / 季節商品 / メニュー入れ替えが必要 / レシピ名とPOS名のズレ など複数の要因が考えられる。')
out.append('')
out.append('| # | レシピ商品名 | 種別 | カテゴリ | 位置付け | 売価 | 原価 | 原価率 |')
out.append('|---:|---|---|---|---|---:|---:|---:|')
for i,r in enumerate(sorted(recipe_only, key=lambda x: ((x.get('カテゴリ') or ''), (x.get('メニュー名') or ''))), 1):
    cr = (r.get('原価率') or 0)*100
    price = r.get('売価')
    cost = r.get('原価')
    out.append(f"| {i} | {r['メニュー名']} | {r.get('種別') or '—'} | {r.get('カテゴリ') or '—'} | {r.get('位置付け') or '—'} | {('¥%d' % int(price)) if price else '—'} | {('¥%d' % int(cost)) if cost else '—'} | {('%.1f%%' % cr) if cr else '—'} |")
out.append('')

# Footnote
out.append('---')
out.append('')
out.append('## 補足')
out.append('')
out.append('### 名寄せロジック')
out.append('1. **完全一致**: POS `menu_name` == レシピ `メニュー名`')
out.append('2. **正規化マッチ**: 空白・記号・括弧類を除去して小文字化した文字列で再一致')
out.append('3. **未マッチ**: 上記2段でヒットしなかったPOS商品はすべて区分2 へ')
out.append('')
out.append('### POS価格 vs レシピ売価 不一致 (差¥50以上)')
out.append('')
out.append('レシピ売価とPOS実績価格に差がある商品。<u>ボトル/グラス混在</u>や<u>価格改定の未反映</u>が疑われる。')
out.append('')
out.append('| POS商品名 | POS実績価格 | レシピ売価 | 差 | POS出数 |')
out.append('|---|---:|---:|---:|---:|')
for p in DATA['recipe_match']['price_mismatches']:
    out.append(f"| {p['name']} | ¥{int(p['pos_price']):,} | ¥{int(p['recipe_price']):,} | ¥{int(p['diff']):+,} | {p['qty']} |")
out.append('')
out.append('### マッチ済品目の原価率分布')
out.append('')
out.append('| 原価率帯 | 品目数 |')
out.append('|---|---:|')
for k,v in DATA['recipe_match']['cost_rate_buckets'].items():
    out.append(f'| {k} | {v} |')
out.append('')
out.append('---')
out.append('')
out.append('## 補完アクション (5月内)')
out.append('')
out.append(f'### 最優先 (区分2a 4月のみ × レシピなし — {len(unmat_apr)}品目)')
out.append('リニューアル時に商品リストへ追加すべきだった商品。一つずつ確認し、必要なものはレシピ登録、不要なら無視/POS削除。')
out.append('')
out.append(f'### 次優先 (区分2b 両月 × レシピなし — {len(unmat_both)}品目)')
out.append('恒常的に登録されていない商品 (ハウスハイボール / 飲み放題コース等)。原価設計を要する。')
out.append('')
out.append(f'### 情報整理 (区分1c 3月のみ マッチ済 — {len(matched_mar)}品目 / 区分2c 3月のみ レシピなし — {len(unmat_mar)}品目)')
out.append('リニューアルで落ちた商品。商品一覧シートに「販売停止」フラグを立てる/削除する判断。')
out.append('')
out.append(f'### 区分3 レビュー — {len(recipe_only)}品目')
out.append('レシピ登録済だが3月も4月もPOS出現なし。メニューに置いているのに売れていないのか/POSへの単品登録漏れか/レシピ名とPOS名のズレかを判定。')
out.append('')

OUT_PATH = os.path.join(ROOT, 'mapping/pos_recipe_mapping_detail.md')
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print(f'[ok] {OUT_PATH} ({os.path.getsize(OUT_PATH)/1024:.1f} KB, {len(out)} lines)')
