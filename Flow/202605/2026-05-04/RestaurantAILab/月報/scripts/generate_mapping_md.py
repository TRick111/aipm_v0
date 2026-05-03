#!/usr/bin/env python3
"""
POS×レシピ マッピング 3区分 詳細をMarkdown表で出力

出力: mapping/pos_recipe_mapping_detail.md
- 区分1: マッチ済 (POS出現あり + レシピあり)
- 区分2: POS出現あり / レシピ未登録
- 区分3: レシピあり / POS出現なし (4月)
"""
import json, os, re, datetime as dt

ROOT = '/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-04/RestaurantAILab/月報'
DATA = json.load(open(os.path.join(ROOT, 'data/analytics2.json'), encoding='utf-8'))
recipe = json.load(open(os.path.join(ROOT, 'data/recipe.json'), encoding='utf-8'))

# レシピ全体 (95品目程度の有効データ)
def normalize(s):
    if not s: return ''
    return re.sub(r'[\s 　・/\-_（）()「」『』【】"\'.]','',str(s)).lower()

# POS出現商品の名寄せ (品目名)
matched_records = DATA['recipe_match']['matched']
unmatched_records = DATA['recipe_match']['unmatched']
matched_pos_names = {m['pos_name'] for m in matched_records}
matched_recipe_names = {m['recipe_name'] for m in matched_records}

# 区分3: レシピあり / POS未出現
recipe_only = []
for r in recipe:
    name = r.get('メニュー名','')
    if not name: continue
    if name in matched_recipe_names: continue
    recipe_only.append(r)

# 未マッチ分類関数 (再利用)
def classify_unmatched(name, cat):
    n = name or ''
    c = cat or ''
    if n in ('tablecharge','No charge','no charge'): return 'チャージ系'
    if 'コース' in n or 'CLP' in n or '飲み放題' in n: return 'コース・飲み放題'
    if 'ハイボール' in n or 'ハウスハイボール' == n: return 'ハイボール'
    if 'ウイスキー' in c or any(w in n for w in ['余市','タリスカー','グレンリベット','ワイルドターキー','イチローズ','響','山崎','白州','ボウモア','ラフロイグ','フロールデカーニャ']): return 'ウイスキー単品ボトル'
    if 'ワイン' in c or 'スパークリング' in n or 'カヴァ' in n: return 'ワイン'
    if 'ビール' in c or 'ビール' in n: return 'ビール'
    if c in ('その他','未設定','黒板メニュー') or '黒板' in n: return 'その他'
    return 'レシピ未登録'

# Build markdown
out = []
out.append(f'# POS × レシピ マッピング 3区分 詳細\n')
out.append(f'**生成日**: {dt.date.today().isoformat()}')
out.append(f'**対象月**: 2026-04')
out.append(f'**POSデータ**: 本番DB salesItems (4/1〜4/26 / 690明細 / {DATA["recipe_match"]["summary"]["total_pos_products"]} ユニーク商品)')
out.append(f'**レシピマスタ**: Spreadsheet `1WjJaogeoRzA3BfO8ldohym5lywniVBApg1BxtINs8CA` 商品一覧シート (99品目)\n')

# サマリ
mc = DATA['recipe_match']['summary']
out.append('## サマリ')
out.append(f'| 区分 | 品目数 | 出数 | 売上 |')
out.append(f'|---|---:|---:|---:|')
matched_sales_total = sum(m['sales'] for m in matched_records)
unmatched_sales_total = sum(m['sales'] for m in unmatched_records)
out.append(f'| 区分1: マッチ済 (POS○ × レシピ○) | {len(matched_records)} | {sum(m["qty"] for m in matched_records):,} | ¥{matched_sales_total:,.0f} |')
out.append(f'| 区分2: POS○ × レシピ✗ (要レシピ登録) | {len(unmatched_records)} | {sum(m["qty"] for m in unmatched_records):,} | ¥{unmatched_sales_total:,.0f} |')
out.append(f'| 区分3: POS✗ × レシピ○ (4月出数なし) | {len(recipe_only)} | — | — |')
out.append('')
out.append(f'**マッチ率**: 品目 {mc["match_rate"]*100:.1f}% / 出数 {mc["qty_match_rate"]*100:.1f}%')
out.append('')
out.append('---')
out.append('')

# 区分1: マッチ済
out.append('## 区分1: マッチ済 (POS出現あり + レシピあり)')
out.append('')
out.append('| # | POS商品名 | レシピ商品名 | 出数 | POS売上 | レシピ売価 | レシピ原価 | 原価率 | 位置付け | レシピカテゴリ |')
out.append('|---:|---|---|---:|---:|---:|---:|---:|---|---|')
matched_sorted = sorted(matched_records, key=lambda x:-x['qty'])
for i,m in enumerate(matched_sorted, 1):
    cr = (m.get('cost_rate') or 0)*100
    out.append(f'| {i} | {m["pos_name"]} | {m["recipe_name"]} | {m["qty"]} | ¥{int(m["sales"]):,} | ¥{int(m.get("price_recipe") or 0):,} | ¥{int(m.get("cost_unit") or 0):,} | {cr:.1f}% | {m.get("位置付け") or "—"} | {m.get("category_recipe") or "—"} |')
out.append('')
out.append('---')
out.append('')

# 区分2: POS出現あり / レシピ未登録
out.append('## 区分2: POS出現あり / レシピシート未登録 (要レシピ追加)')
out.append('')
out.append('未マッチ品目は分類別にグルーピング。「商品一覧シート」に登録すべきもの / 「オペ用簡易レシピ」シート側に既にあるもの / 飲み放題コースなど分割が必要なもの に分類できる。')
out.append('')

# 分類別にグループ化
from collections import defaultdict
um_by_class = defaultdict(list)
for u in unmatched_records:
    um_by_class[classify_unmatched(u['pos_name'], u.get('category_pos',''))].append(u)

class_order = [
    ('ハイボール', '🍹 単独で出数最大。原価式の確定が最重要'),
    ('コース・飲み放題', '🍽️ コース別の構成商品分解 + 原価設定が必要'),
    ('ウイスキー単品ボトル', '🥃 オペ用簡易レシピシートに別途記載されている可能性'),
    ('ワイン', '🍷 ボトル/グラス販売の区別が必要'),
    ('ビール', '🍺 単純な原価率設定で対応可'),
    ('レシピ未登録', '❓ 商品名の正規化 or 別シートからの取り込みが必要'),
    ('その他', '🔧 POSカテゴリ「未設定」「その他」「黒板メニュー」など'),
    ('チャージ系', '⚙ tablecharge等。商品戦略ランキングからは除外済'),
]

for cls, desc in class_order:
    items = um_by_class.get(cls, [])
    if not items: continue
    out.append(f'### {cls} ({len(items)}品目 / {sum(i["qty"] for i in items):,}出数 / ¥{sum(i["sales"] for i in items):,.0f})')
    out.append(f'_{desc}_')
    out.append('')
    out.append('| # | POS商品名 | POSカテゴリ | 出数 | 売上 | 平均価格 |')
    out.append('|---:|---|---|---:|---:|---:|')
    for i,u in enumerate(sorted(items, key=lambda x:-x['qty']), 1):
        avg = (u['sales']/u['qty']) if u['qty'] else 0
        out.append(f'| {i} | {u["pos_name"]} | {u.get("category_pos") or "—"} | {u["qty"]} | ¥{int(u["sales"]):,} | ¥{int(avg):,} |')
    out.append('')

out.append('---')
out.append('')

# 区分3: レシピあり / POS出現なし (4月)
out.append('## 区分3: レシピシートあり / POS出現なし (4月)')
out.append('')
out.append('レシピマスタには登録されているが、4月のPOSデータには出現しなかった商品。販売停止 / 季節商品 / メニュー入れ替え など複数の理由が考えられる。')
out.append('')
# 種別/カテゴリでまとめ
out.append('| # | レシピ商品名 | 種別 | カテゴリ | 位置付け | 売価 | 原価 | 原価率 |')
out.append('|---:|---|---|---|---|---:|---:|---:|')
def sort_key(r):
    return (r.get('種別') or '', r.get('カテゴリ') or '', r.get('メニュー名') or '')
recipe_only_sorted = sorted(recipe_only, key=sort_key)
for i,r in enumerate(recipe_only_sorted, 1):
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
    out.append(f'| {p["name"]} | ¥{int(p["pos_price"]):,} | ¥{int(p["recipe_price"]):,} | ¥{int(p["diff"]):+,} | {p["qty"]} |')
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
out.append('1. **ハウスハイボール 原価設定** (区分2 / 152本 / ¥182,400) — 単独最重要')
out.append('2. **コース・飲み放題 6品目の原価分解** (区分2 / 128本 / ¥785,000) — コース内構成商品の按分が必要')
out.append('3. **ウイスキー単品ボトル 28品目** (区分2) — オペ用簡易レシピシートからの取り込み (`1WjJaog...` の別シート)')
out.append('4. **ワイン・スパークリング 5品目** (区分2) — ボトル/グラスの区別を含めて再登録')
out.append('5. **POS価格 vs レシピ売価 不一致 3件の整合確認** — 特にテバルド・ビアンコ/ロッソ (¥6,500 vs ¥1,200)')
out.append('6. **区分3 (レシピあり/POS出現なし) のレビュー** — メニュー落ちか季節商品か仕分け、商品一覧シートに販売停止フラグを立てるなど')
out.append('')

OUT_PATH = os.path.join(ROOT, 'mapping/pos_recipe_mapping_detail.md')
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print(f'[ok] {OUT_PATH} ({os.path.getsize(OUT_PATH)/1024:.1f} KB, {len(out)} lines)')
