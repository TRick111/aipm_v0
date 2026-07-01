"""
食べログ店舗管理画面に **非対話** でログインし、storageState.json を保存する。

accounts.yaml から認証情報を読み込む。2FA 無い前提。
ログインに失敗したら例外で終了（ロック回避のため試行 1 回のみ）。

使い方:
    python3 login_and_save_state_auto.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright  # noqa: E402

from _lib.credentials import load_credential  # noqa: E402


LOGIN_URL = "https://owner.tabelog.com/owner_account/login/"
POST_LOGIN_URL_HINT = "https://owner.tabelog.com/owner_rst/"
STATE_PATH = Path(__file__).parent / "state" / "storageState.json"
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    cred = load_credential("pockunpa-okazaki", "tabelog_owner")
    if not cred.login_id or not cred.password:
        print("[ERROR] accounts.yaml の tabelog_owner が空です", file=sys.stderr)
        return 2

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL, wait_until="networkidle")
        page.get_by_role("textbox", name="ログインID").fill(cred.login_id)
        page.get_by_role("textbox", name="パスワード").fill(cred.password)
        page.get_by_role("button", name="ログインする").click()
        page.wait_for_load_state("networkidle", timeout=15000)

        if "login" in page.url:
            print(
                f"[ERROR] ログイン失敗（URL: {page.url}）。ID/PW を確認してください。",
                file=sys.stderr,
            )
            browser.close()
            return 1

        print(f"[OK] ログイン成功 → {page.url}")
        context.storage_state(path=str(STATE_PATH))
        print(f"[OK] state 保存: {STATE_PATH} ({STATE_PATH.stat().st_size:,} bytes)")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
