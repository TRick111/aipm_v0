#!/usr/bin/env python3
"""Compare Spreadsheet PL vs DB PL for store bfa-001 (FIVE Arrows).

Generates a Markdown report at:
  /Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/PL差分レポート_bfa-001_v1.md
"""
import json
import re
from collections import defaultdict
from datetime import datetime

SHEET = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/sheet_pl_parsed.json"
DB    = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/db_pl_dump.json"
OUT   = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/PL差分レポート_bfa-001_v1.md"

with open(SHEET) as f:
    sheet = json.load(f)
with open(DB) as f:
    db = json.load(f)

# --- Build DB lookups ---
sc_map = {c["id"]: c["name"].lstrip("🍸🍳🍬🍽️🎉").strip() for c in db["salesCategories"]}
ec_map = {c["id"]: c["name"] for c in db["expenseCategories"]}

db_sales = defaultdict(lambda: defaultdict(float))  # [ym][cat] = amount
for r in db["monthlySales"]:
    db_sales[r["year_month"]][sc_map.get(r["category_id"], "?")] += float(r["total"])

db_exp = defaultdict(lambda: defaultdict(float))
for r in db["monthlyExpenses"]:
    db_exp[r["year_month"]][ec_map.get(r["category_id"], "?")] += float(r["total"])

db_months_sales = sorted(db_sales.keys())
db_months_exp = sorted(db_exp.keys())
db_months_all = sorted(set(db_months_sales) | set(db_months_exp))

# Sheet months (only YYYY-MM ones; skip aggregates and empty months)
sheet_months_with_data = sorted({
    ym for ym, t in sheet["totals"].items()
    if re.match(r"^\d{4}-\d{2}$", ym) and t.get("sales")
})

# --- Category mapping for joint comparison ---
# Spreadsheet sales categories (with emoji stripped) → DB sales categories
# Note: DB sales only has '総売上' populated; detail categories empty.
sales_cat_map_sheet_to_db = {
    "ドリンク": "ドリンク",
    "フード":   "フード",
    "チャーム": "チャーム",
    "コース":   "コース",
    "イベント": "イベント",
    "物販":     None,   # DB に対応カテゴリなし
    "その他":   None,   # DB に対応カテゴリなし
}

# Spreadsheet expense → DB expense
expense_cat_map = {
    "食材":                 "食材",
    "ドリンク":             "ドリンク",
    "販売・広告":           "広告費",          # 名称差・スキーマ差あり
    "家賃":                 "家賃",
    "人件費":               "人件費",
    "CLP人件費":            None,             # DB に対応カテゴリなし
    "備品":                 "備品",
    "ローン返済":           "ローン返済",
    "通信/衛生/管理費etc...": "管理費＋水道光熱費",  # 1→2分割
    "税金":                 None,             # DB に対応カテゴリなし
    "人事関連（採用等）":   None,             # DB に対応カテゴリなし
}

def fmt(n):
    if n is None:
        return "-"
    return f"¥{int(round(n)):,}"

# --- Build report ---
lines = []
lines.append("# PL データ差分レポート — FIVE Arrows (bfa-001)")
lines.append("")
lines.append(f"- 作成日: {datetime.now():%Y-%m-%d}")
lines.append(f"- 作成者: 田中利空（Claude 経由）")
lines.append(f"- 比較対象A（スプレッドシート）: Google Drive `【BFA】本部サポート` / シート `PL`")
lines.append(f"- 比較対象B（本番DB）: Neon `neondb` / `pl_daily_sales` + `pl_daily_expenses` + `pl_monthly_targets`")
lines.append(f"- 対象店舗: FIVE Arrows (`bfa-001`, storeId=`{db['store']['id']}`)")
lines.append("")

lines.append("## 結論サマリ")
lines.append("")
lines.append("**スプレッドシートと本番DBは、対象期間もカテゴリ構造も全く揃っておらず、現時点で「数値が一致しているか」の機械的比較は事実上不可能でした。** 以下が判明した主な差分です。")
lines.append("")
lines.append("| # | 種別 | 内容 |")
lines.append("|---|------|------|")
lines.append("| 1 | 期間不一致 | スプレッドシートPL = 2024-01〜2025-10 の月次実績。本番DB = 2026-01〜2026-05 のみ。**月単位で重なる月がゼロ** |")
lines.append("| 2 | 売上の粒度不一致 | スプレッドシートはドリンク/フード/チャーム/コース/イベント/物販/その他にカテゴリ分解。**DB(`pl_daily_sales`) には「総売上」カテゴリ1本でしか入っていない**（明細カテゴリは0件）|")
lines.append("| 3 | 売上カテゴリ欠落 | DB売上カテゴリに **「物販」「その他」が存在しない** |")
lines.append("| 4 | 費用カテゴリ統合差 | スプレッドシートの **「通信/衛生/管理費etc...」が、DBでは「管理費」+「水道光熱費」に分割** されている |")
lines.append("| 5 | 費用カテゴリ欠落 | DB費用カテゴリに **「CLP人件費」「税金」「人事関連（採用等）」が存在しない** |")
lines.append("| 6 | 費用カテゴリ名称差 | スプレッドシート「販売・広告」 ↔ DB「広告費」（販売費部分が不明確）|")
lines.append("| 7 | 2026-03 抜け | DBに **2026年3月の売上・費用データが一切ない** |")
lines.append("| 8 | 予算データ不在 | `pl_monthly_targets` テーブルに **bfa-001 の行がゼロ件**。Dashboard の予実管理UIは現状空の状態 |")
lines.append("")

lines.append("## 1. 対象期間の比較")
lines.append("")
lines.append("### スプレッドシート `PL` シートに記録のある月")
lines.append("")
lines.append(f"- 月次データ列: **{sheet_months_with_data[0]} 〜 {sheet_months_with_data[-1]}** （{len(sheet_months_with_data)} か月分）")
lines.append("- それ以外に集計列「24年8月〜2025年9月」「25年1月〜2025年9月」を保持")
lines.append("- `2025-11`, `2025-12` のヘッダ列はあるが値は未入力")
lines.append("")
lines.append("### 本番DBに記録のある月")
lines.append("")
lines.append(f"- `pl_daily_sales`: **{', '.join(db_months_sales)}**")
lines.append(f"- `pl_daily_expenses`: **{', '.join(db_months_exp)}**")
lines.append("- 2026-03 は売上・費用ともに **0件**")
lines.append("")
lines.append("### 重なる月")
lines.append("")
overlap = sorted(set(sheet_months_with_data) & set(db_months_all))
if overlap:
    lines.append(f"- {', '.join(overlap)}")
else:
    lines.append("- **なし**（スプレッドシートは2024〜2025、DBは2026のみ）")
lines.append("")

lines.append("## 2. カテゴリ構造の比較")
lines.append("")
lines.append("### 売上カテゴリ")
lines.append("")
lines.append("| スプレッドシート | DB (`pl_sales_categories`) | 備考 |")
lines.append("|------------------|-----------------------------|------|")
for s, d in sales_cat_map_sheet_to_db.items():
    note = "" if d else "DB に対応カテゴリなし"
    lines.append(f"| {s} | {d or '(なし)'} | {note} |")
lines.append("| (なし) | 総売上 | DBで売上が入っている唯一のカテゴリ（1本入力運用）|")
lines.append("")
lines.append("> ⚠ **重要**: DB上の `pl_daily_sales` 41行はすべて「総売上」カテゴリへの入力で、ドリンク/フード/チャーム/コース/イベント の各カテゴリは **0行**。スプレッドシートのような「ドリンクが売上の65%」というカテゴリ別分析を、現状のDBデータからは再現できません。")
lines.append("")

lines.append("### 費用カテゴリ")
lines.append("")
lines.append("| スプレッドシート | DB (`pl_expense_categories`) | 備考 |")
lines.append("|------------------|------------------------------|------|")
for s, d in expense_cat_map.items():
    note = ""
    if d is None:
        note = "DB に対応カテゴリなし"
    elif "＋" in d:
        note = "1→2 分割（スプレッドシート1カテゴリがDBでは2カテゴリ）"
    elif s != d:
        note = "名称差。販売費部分の所在が不明"
    lines.append(f"| {s} | {d or '(なし)'} | {note} |")
lines.append("")

lines.append("## 3. 各データソースの月次サマリ（参考）")
lines.append("")
lines.append("### スプレッドシート: 月次 売上 / 費用 / 利益")
lines.append("")
lines.append("| 月 | 売上 | 費用 | 利益 |")
lines.append("|----|------|------|------|")
for ym in sheet_months_with_data:
    t = sheet["totals"].get(ym, {})
    lines.append(f"| {ym} | {fmt(t.get('sales'))} | {fmt(t.get('expense'))} | {fmt(t.get('profit'))} |")
lines.append("")

lines.append("### DB: 月次 売上総額 / 費用総額")
lines.append("")
lines.append("| 月 | 売上(総売上カテゴリ合計) | 費用合計 |")
lines.append("|----|--------------------------|----------|")
for ym in db_months_all:
    s = sum(db_sales.get(ym, {}).values()) if ym in db_sales else None
    e = sum(db_exp.get(ym, {}).values()) if ym in db_exp else None
    lines.append(f"| {ym} | {fmt(s) if s is not None else '-'} | {fmt(e) if e is not None else '-'} |")
lines.append("")

lines.append("### DB: 月×カテゴリ 費用内訳")
lines.append("")
db_exp_cats = sorted({c for m in db_exp.values() for c in m.keys()})
header = "| 月 | " + " | ".join(db_exp_cats) + " | 合計 |"
sep    = "|----|" + "|".join(["---"] * (len(db_exp_cats) + 1)) + "|"
lines.append(header)
lines.append(sep)
for ym in db_months_exp:
    row = [ym] + [fmt(db_exp[ym].get(c)) for c in db_exp_cats] + [fmt(sum(db_exp[ym].values()))]
    lines.append("| " + " | ".join(row) + " |")
lines.append("")

lines.append("## 4. 予算（`pl_monthly_targets`）")
lines.append("")
if db["monthlyTargets"]:
    lines.append("| year_month | sales_target | profit_target | fl_target_ratio |")
    lines.append("|------------|--------------|----------------|------------------|")
    for t in db["monthlyTargets"]:
        lines.append(f"| {t['yearMonth']} | {t['salesTarget']} | {t['profitTarget']} | {t['flTargetRatio']} |")
else:
    lines.append("`pl_monthly_targets` に bfa-001 の行は **0件**。Dashboard の予実管理UIで設定された予算が現状ありません。")
lines.append("")
lines.append("> スプレッドシート `PL` シート側にも独立した「予算列」は存在せず、月次実績のみが記録されています。ご指示の「予算情報」は、別シート（候補: `新PL管理（移管前）`）にある可能性が高いです。要確認。")
lines.append("")

lines.append("## 5. アクションの提案")
lines.append("")
lines.append("1. **データソースの位置付けを確定**")
lines.append("   - スプレッドシート `PL` = 2024-01〜2025-10 の **過去実績アーカイブ**")
lines.append("   - 本番DB = 2026-01 以降の **新運用データ** という前提でよいか、竹矢さん／吉田さんに確認")
lines.append("   - そうであれば、2024-2025の数値は「Dashboard 移行前の参考資料」として **DB側に取り込むか／別表示で扱うか** を決める必要あり")
lines.append("2. **売上カテゴリ運用の見直し**")
lines.append("   - 現状DBは「総売上」1本でしか入っておらず、スプレッドシート同等のカテゴリ別分析ができない")
lines.append("   - クライアント運用が「総額入力のみ」なのか、「カテゴリ別入力すべきだが入力漏れ」なのかを確認")
lines.append("3. **費用カテゴリのマッピング決定**")
lines.append("   - 「通信/衛生/管理費etc...」 ↔ 「管理費＋水道光熱費」の対応関係をどう正規化するか定義")
lines.append("   - スプレッドシートの「販売・広告」「CLP人件費」「税金」「人事関連」を DB の既存カテゴリで吸収するのか、新規カテゴリ追加するのかを決める")
lines.append("4. **2026-03 データ欠損の調査**")
lines.append("   - 入力漏れか、入力UIの不具合か、運用ストップ期間かを確認")
lines.append("5. **`pl_monthly_targets` の入力**")
lines.append("   - 予算情報のソースシート（PL以外）を特定 → DBの予算機能に流し込む手順を立てる")
lines.append("")

lines.append("## 6. 添付ファイル（同フォルダ内）")
lines.append("")
lines.append("| ファイル | 説明 |")
lines.append("|----------|------|")
lines.append("| `pl_sheet_raw.json` | スプレッドシート `PL!A1:BU60` の生レスポンス |")
lines.append("| `sheet_pl_parsed.json` | スプレッドシートPLを月×カテゴリに正規化したJSON |")
lines.append("| `db_pl_dump.json` | 本番DBからの bfa-001 PL関連ダンプ（カテゴリ／月次集計／予算）|")
lines.append("| `dump_db_pl.ts` | DBダンプスクリプト（Prismaクライアント使用） |")
lines.append("| `parse_sheet.py` | スプレッドシート正規化スクリプト |")
lines.append("| `compare_pl.py` | 本レポート生成スクリプト |")
lines.append("")

with open(OUT, "w") as f:
    f.write("\n".join(lines))
print("wrote", OUT)
