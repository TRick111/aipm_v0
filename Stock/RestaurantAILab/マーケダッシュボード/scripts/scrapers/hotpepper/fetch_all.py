"""
HPG 店舗管理画面の保存済み storageState.json を使い、CSV エクスポートできない
ページの HTML を raw_html/ に保存する。

事前条件: login_and_save_state.py で state/storageState.json を生成済み。

使い方:
    python3 fetch_all.py            # 全 HTML 取得対象を取得
    python3 fetch_all.py PAGE_KEY   # 1 ページだけ取得（キーは PAGES 辞書参照）

備考:
    Excel / CSV ダウンロード型（クライアントレポート、流入ワード）は本スクリプト対象外。
    別 fetcher（fetch_excel_reports.py 等、Phase 1.1 で実装）で扱う。
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
STATE_PATH = BASE_DIR / "state" / "storageState.json"
RAW_DIR = BASE_DIR / "raw_html"

# CSV/Excel エクスポート不可で DOM パース必須のページ
PAGES = {
    "reviews": "https://www.cms.hotpepper.jp/CLP/ccm010/showReportListAllForAuth",
}


def main(only: str | None = None) -> int:
    if not STATE_PATH.exists():
        print(
            f"[ERROR] {STATE_PATH} が存在しません。"
            f"先に login_and_save_state.py を実行してログイン状態を保存してください。",
            file=sys.stderr,
        )
        return 1

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    targets = {only: PAGES[only]} if only else PAGES

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATE_PATH))
        page = context.new_page()

        for name, url in targets.items():
            print(f"[fetch] {name}: {url}")
            response = page.goto(url, wait_until="networkidle")
            if response is None or response.status >= 400:
                status = response.status if response else "no-response"
                print(f"  [WARN] HTTP {status} returned, skipping", file=sys.stderr)
                continue
            if "noLoginError" in page.url or "login" in page.url.lower():
                print(
                    f"  [ERROR] セッション失効。再度 login_and_save_state.py を実行してください。",
                    file=sys.stderr,
                )
                browser.close()
                return 2

            html = page.content()
            out_path = RAW_DIR / f"{name}.html"
            out_path.write_text(html, encoding="utf-8")
            print(f"  -> {out_path} ({out_path.stat().st_size:,} bytes)")

        browser.close()
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg and arg not in PAGES:
        print(f"unknown page key: {arg}. choices={list(PAGES)}", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(arg))
