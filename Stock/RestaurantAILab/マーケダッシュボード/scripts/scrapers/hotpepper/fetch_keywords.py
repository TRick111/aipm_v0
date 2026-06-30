"""
ホットペッパーグルメ 流入ワード CSV を月別に取得。

仕組み:
  - showClientReportFreeword/0/0 で月一覧プルダウン取得
  - <select name="numberCd"> の value を YYYYMM に書き換えて download1() を呼ぶ
  - downloadFreeword/ から CSV (cp932) を取得

使い方:
    python3 fetch_keywords.py                 # 過去 12 ヶ月
    python3 fetch_keywords.py --month 2026-06
    python3 fetch_keywords.py --months 6

出力: sample_data/hotpepper/auto/keywords/<YYYY-MM>.csv
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright  # noqa: E402

from _lib.credentials import get_target_months  # noqa: E402
from _lib.playwright_helpers import open_context_with_state  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "sample_data" / "hotpepper" / "auto" / "keywords"
PAGE_URL = "https://www.cms.hotpepper.jp/CLP/crp040/showClientReportFreeword/0/0"


def parse_args(argv: list[str]) -> list[str]:
    if "--month" in argv:
        i = argv.index("--month")
        return [argv[i + 1]]
    if "--months" in argv:
        i = argv.index("--months")
        return get_target_months(months=int(argv[i + 1]))
    return get_target_months(months=12)


def main() -> int:
    months = parse_args(sys.argv[1:])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = []

    with sync_playwright() as pw:
        ctx, page = open_context_with_state(pw, service="hpg_recruit", headless=True)
        # 1 回だけページを開く
        page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)

        # 利用可能な月を確認（プルダウンに無い月はスキップ）
        available = page.evaluate(
            """() => {
              const s = document.querySelector('select[name="numberCd"]');
              return s ? [...s.options].map(o => o.value) : [];
            }"""
        )
        print(f"[hpg/keywords] available months in dropdown: {len(available)}", file=sys.stderr)

        for ym in months:
            yyyymm = ym.replace("-", "")
            if yyyymm not in available:
                print(f"[hpg/keywords] {ym} not in dropdown, skipping", file=sys.stderr)
                failures.append(ym)
                continue
            # ページ再描画が必要かどうかわからないので毎回 goto しないが、selector が消えていたら再 load
            try:
                page.evaluate(
                    f"""() => {{
                      const s = document.querySelector('select[name="numberCd"]');
                      if (s) s.value = '{yyyymm}';
                    }}"""
                )
                with page.expect_download(timeout=45000) as dl_info:
                    page.evaluate("download1()")
                dl = dl_info.value
                out = OUT_DIR / f"{ym}.csv"
                dl.save_as(str(out))
                # 行数（cp932 想定）
                try:
                    text = out.read_text(encoding="cp932")
                except UnicodeDecodeError:
                    text = out.read_text(encoding="utf-8", errors="replace")
                rows = max(0, text.count("\n") - 2)  # タイトル行 + ヘッダ行を引く
                size = out.stat().st_size
                print(f"[hpg/keywords] {ym} OK: size={size:,}B rows={rows} -> {out}", file=sys.stderr)
                time.sleep(1)
                # ページが download POST で遷移してしまった場合は再 load
                if "showClientReportFreeword" not in page.url:
                    page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1500)
            except Exception as e:  # noqa: BLE001
                print(f"[hpg/keywords] {ym} ERR: {type(e).__name__}: {e}", file=sys.stderr)
                failures.append(ym)
                # 再 load して次の月へ
                try:
                    page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1500)
                except Exception:
                    pass
        ctx.close()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
