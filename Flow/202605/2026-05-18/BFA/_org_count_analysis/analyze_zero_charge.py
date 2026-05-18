#!/usr/bin/env python3
"""
組数+1問題の原因特定スクリプト
- ヘッダー件数（pipelineが現在数えている数）
- うち 合計=0 件数
- うち カテゴリ=未設定 件数
- うち No charge メニュー件数
- 業務日基準（朝6時境界）
"""
import sys, json, os, pandas as pd

sys.path.insert(0, "/Users/rikutanaka/aipm_v0/Stock/RestaurantAILab/月報/Scripts")
from monthly_report_pipeline import load_provided_csv, to_business_date

MONTHS = [
    ("2026-01", "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/月報_202601/sales_202601_airregi.csv"),
    ("2026-02", "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/月報_202602/sales_202602.csv"),
    ("2026-03", "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/月報_202603/sales_202603.csv"),
    ("2026-04", "/Users/rikutanaka/RestaurantAILab/Dashboard/.local/bulkupload/bfa-001/会計明細_20260401-20260430_LATEST.csv"),
]

OUT = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/_org_count_analysis"

def analyze(month_str, csv_path):
    hdr, det = load_provided_csv(csv_path, month_str)
    n_hdr = len(hdr)

    # 合計=0
    zero_total = hdr[hdr["合計"] == 0]

    # No charge / nocharge メニュー名 を含む取引
    nc_mask = det["メニュー名"].fillna("").str.contains("No charge|nocharge|NoCharge|NO CHARGE", case=False, regex=True, na=False)
    nc_accts = set(det[nc_mask]["取引No"].unique())
    nc_hdr = hdr[hdr["取引No"].isin(nc_accts)]

    # 未設定 カテゴリの取引（明細にカテゴリ=未設定 を含む取引）
    un_mask = det["カテゴリー名"].fillna("").eq("未設定")
    un_accts = set(det[un_mask]["取引No"].unique())
    un_hdr = hdr[hdr["取引No"].isin(un_accts)]

    # 合計=0 と未設定の重なり
    zero_un = hdr[(hdr["合計"] == 0) & (hdr["取引No"].isin(un_accts))]
    zero_nc = hdr[(hdr["合計"] == 0) & (hdr["取引No"].isin(nc_accts))]

    # 補正後組数
    paid_hdr = hdr[hdr["合計"] > 0]
    n_paid = len(paid_hdr)

    info = {
        "month": month_str,
        "csv_path": csv_path,
        "header_count": int(n_hdr),
        "zero_total_count": int(len(zero_total)),
        "zero_total_ids": zero_total["取引No"].astype(str).tolist(),
        "no_charge_account_count": int(len(nc_hdr)),
        "no_charge_account_ids": [str(a) for a in nc_accts],
        "no_charge_zero_total_count": int(len(zero_nc)),
        "untagged_account_count": int(len(un_hdr)),
        "untagged_account_ids": [str(a) for a in un_accts],
        "untagged_zero_total_count": int(len(zero_un)),
        "paid_count_after_exclude_zero": int(n_paid),
        "diff_excluded": int(n_hdr - n_paid),
    }
    return info, zero_total, nc_hdr, un_hdr

def main():
    rows = []
    for ym, p in MONTHS:
        if not os.path.exists(p):
            print(f"  WARN: missing {p}")
            continue
        print(f"=== {ym} ===")
        info, zero_total, nc_hdr, un_hdr = analyze(ym, p)
        rows.append(info)
        print(f"  header_count:        {info['header_count']}")
        print(f"  zero_total_count:    {info['zero_total_count']}")
        print(f"  no_charge_accounts:  {info['no_charge_account_count']}")
        print(f"  untagged_accounts:   {info['untagged_account_count']}")
        print(f"  paid_after_excl:     {info['paid_count_after_exclude_zero']}")
        # show zero-total IDs and detail
        if len(zero_total) > 0:
            print(f"  zero-total IDs: {info['zero_total_ids']}")
        if len(nc_hdr) > 0:
            print(f"  no-charge IDs: {info['no_charge_account_ids']}")
    with open(os.path.join(OUT, "zero_charge_summary.json"), "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n✓ summary saved → {OUT}/zero_charge_summary.json")

if __name__ == "__main__":
    main()
