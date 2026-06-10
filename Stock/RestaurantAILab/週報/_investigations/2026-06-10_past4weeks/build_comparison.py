"""バグ値 vs 正値の比較表を組み立てる。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

WEEKS = [19, 20, 21, 22]
STORES = ["BFA", "麻布しき"]


def load_bug_values():
    out = {}
    paths = {
        "BFA": ROOT / "2_output" / "BFA",
        "麻布しき": ROOT / "2_output" / "麻布しき",
    }
    for s in STORES:
        out[s] = {}
        for w in WEEKS:
            j = paths[s] / f"2_output_2026w{w}" / "analysis_results.json"
            d = json.load(open(j))
            tw = d["sales_analysis"]["target_week"]
            out[s][f"2026-W{w}"] = {
                "売上": float(tw["売上"]),
                "客数": int(tw["客数"]),
                "組数": int(tw["組数"]),
                "客単価": float(tw["客単価"]),
            }
    return out


def main():
    bug = load_bug_values()
    correct = json.load(open(HERE / "correct_values.json"))["weekly_kpi"]

    rows = []
    for s in STORES:
        for w in WEEKS:
            wk = f"2026-W{w}"
            b = bug[s][wk]
            c = correct[s][wk]
            for metric in ("売上", "客数", "客単価", "組数"):
                bv = b[metric]
                cv = c[metric]
                diff = bv - cv
                pct = (diff / cv * 100) if cv else 0.0
                rows.append(
                    {
                        "store": s,
                        "week": wk,
                        "metric": metric,
                        "bug": bv,
                        "correct": cv,
                        "diff": diff,
                        "pct": pct,
                    }
                )

    # 出力: markdown + json
    md_lines = [
        "| 店舗 | 週 | 指標 | バグ値 | 正値 | 差分 | 乖離率 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        is_yen = r["metric"] in ("売上", "客単価")
        unit_b = f"¥{r['bug']:,.0f}" if is_yen else f"{r['bug']:.0f}"
        unit_c = f"¥{r['correct']:,.0f}" if is_yen else f"{r['correct']:.0f}"
        unit_d = f"{'¥' if is_yen else ''}{r['diff']:+,.0f}"
        pct_s = f"{r['pct']:+.1f}%"
        md_lines.append(
            f"| {r['store']} | {r['week']} | {r['metric']} | {unit_b} | {unit_c} | {unit_d} | {pct_s} |"
        )

    (HERE / "comparison_table.md").write_text("\n".join(md_lines))
    (HERE / "comparison_rows.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2)
    )
    print("\n".join(md_lines))


if __name__ == "__main__":
    main()
