"""
HPG（ホットペッパーグルメ）店舗管理画面にヘッド付きブラウザでログインし、
認証セッションを storageState.json として保存する。

食べログとは別ドメイン（cms.hotpepper.jp）のため、独立したセッション管理。

初回 1 回だけ実行すれば、以降の fetch_all.py は無人で動く。
セッション失効したら再度このスクリプトを実行する。

使い方:
    python3 login_and_save_state.py
    -> Chromium が立ち上がる -> ID/PW を手で入れてログイン
    -> ログイン後の店舗管理画面が見えたら、ターミナルで Enter
    -> state/storageState.json が生成される
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# HPG CMS のログイン入口（直接URLが分からない場合はトップから誘導）
ENTRY_URL = "https://www.cms.hotpepper.jp/CLP/ccm010/showReportListAllForAuth"
STATE_PATH = Path(__file__).parent / "state" / "storageState.json"


def main() -> int:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(ENTRY_URL)

        print("=" * 60)
        print("Chromium が立ち上がりました。")
        print("画面上で HPG 店舗管理画面の ID / PW を入力してログインしてください。")
        print(f"ログイン後 {ENTRY_URL} の口コミ一覧が見えたら、")
        print("このターミナルに戻って Enter を押してください。")
        print("=" * 60)
        input("ログイン完了後、Enter を押す> ")

        # 確認: 認証必要ページに遷移できることをチェック
        page.goto(ENTRY_URL)
        if "noLoginError" in page.url or "login" in page.url.lower():
            print(f"[ERROR] ログインできていません。現在URL: {page.url}", file=sys.stderr)
            browser.close()
            return 1

        context.storage_state(path=str(STATE_PATH))
        print(f"[OK] {STATE_PATH} に保存しました（{STATE_PATH.stat().st_size} bytes）")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
