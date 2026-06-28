"""
food.tabelog.com の保存済み storageState.json を使い、CSV エクスポートできない
5 ページの HTML を raw_html/ に保存する。

事前条件: login_and_save_state.py で state/storageState.json を生成済み。

使い方:
    python3 fetch_all.py            # 全 5 ページ取得
    python3 fetch_all.py PAGE_KEY   # 1 ページだけ取得（キーは PAGES 辞書参照）
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
STATE_PATH = BASE_DIR / "state" / "storageState.json"
RAW_DIR = BASE_DIR / "raw_html"

# CSV エクスポートできない 5 ページの URL マップ
# キー = raw_html 配下の .html ファイル名（拡張子なし）
#
# access_report_total: 月次表示（13ヶ月分の月別集計）。`?display_type=monthly` 必須。
#   日次（直近1ヶ月）が欲しい場合は `?display_type=daily` か無印 URL を使う。
# access_report_page: 月指定する場合は `?start_month=YYYYMM&end_month=YYYYMM` を付与。
#   このスクリプトでは引数 `target_month` (YYYY-MM) を渡せばその月だけに絞れる。
#   未指定時は管理画面デフォルト（直近 13ヶ月集計）。
PAGES = {
    "access_report_total": "https://owner.tabelog.com/owner_rst/access_report_total?display_type=monthly",
    "access_report_page": "https://owner.tabelog.com/owner_rst/access_report_page",
    "access_report_total_conversion": "https://owner.tabelog.com/owner_rst/access_report_total_conversion",
    "rstupreview_entry": "https://owner.tabelog.com/owner_rst/rstupreview_entry/?srt=visit&sby=desc&PG=1&smp=2&lc=0",
    "access_ranking": "https://owner.tabelog.com/owner_rst/access_ranking",
}


def url_for(name: str, target_month: str | None = None) -> str:
    """name に対応する URL を返す。target_month=YYYY-MM のとき access_report_page を月絞り込み."""
    url = PAGES[name]
    if name == "access_report_page" and target_month:
        ym = target_month.replace("-", "")
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}start_month={ym}&end_month={ym}"
    return url


def main(only: str | None = None, target_month: str | None = None) -> int:
    if not STATE_PATH.exists():
        print(
            f"[ERROR] {STATE_PATH} が存在しません。"
            f"先に login_and_save_state.py を実行してログイン状態を保存してください。",
            file=sys.stderr,
        )
        return 1

    raw_dir = RAW_DIR / target_month if target_month else RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)
    names = [only] if only else list(PAGES.keys())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATE_PATH))
        page = context.new_page()

        for name in names:
            url = url_for(name, target_month)
            print(f"[fetch] {name}: {url}")
            response = page.goto(url, wait_until="networkidle")
            if response is None or response.status >= 400:
                status = response.status if response else "no-response"
                print(f"  [WARN] HTTP {status} returned, skipping", file=sys.stderr)
                continue
            if "login" in page.url:
                print(
                    f"  [ERROR] セッション失効。再度 login_and_save_state.py を実行してください。",
                    file=sys.stderr,
                )
                browser.close()
                return 2

            html = page.content()
            out_path = raw_dir / f"{name}.html"
            out_path.write_text(html, encoding="utf-8")
            print(f"  -> {out_path} ({out_path.stat().st_size:,} bytes)")

        browser.close()
    return 0


if __name__ == "__main__":
    # 使い方:
    #   python3 fetch_all.py                       # 全 5 ページを raw_html/ 直下に保存
    #   python3 fetch_all.py PAGE_KEY              # 1 ページのみ
    #   python3 fetch_all.py PAGE_KEY YYYY-MM      # 1 ページを特定月で取得・raw_html/YYYY-MM/ に保存
    #   python3 fetch_all.py - YYYY-MM             # 全 5 ページを特定月で取得（access_report_page のみ月パラメータ適用）
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    month_arg = sys.argv[2] if len(sys.argv) > 2 else None
    if arg == "-":
        arg = None
    if arg and arg not in PAGES:
        print(f"unknown page key: {arg}. choices={list(PAGES)}", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(arg, month_arg))
