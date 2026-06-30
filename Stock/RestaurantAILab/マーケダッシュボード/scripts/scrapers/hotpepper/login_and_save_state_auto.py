"""
HPG（ホットペッパーグルメ）店舗管理画面に **自動ログイン** し storageState を保存。

既存の login_and_save_state.py は手動ログイン用（OTP 入力前提）。
user 回答により 2FA 無しが確認できたので、本スクリプトは自動化版。

ログイン試行: 最大 2 回（user 指示）。失敗で exit 2、2FA/CAPTCHA で exit 3。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import BrowserContext, Page, sync_playwright  # noqa: E402

from _lib.credentials import load_credential  # noqa: E402
from _lib.playwright_helpers import (  # noqa: E402
    UnexpectedAuthChallengeError,
    attempt_login_with_retry,
    state_path_for,
)


STORE_CODE = "pockunpa-okazaki"
SERVICE = "hpg_recruit"
LOGIN_URL = "https://www.cms.hotpepper.jp/CLN/login/"


def _do_login(cred):
    def login(context: BrowserContext, page: Page) -> bool:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        # フォームの実セレクタを探す（id/name の汎用候補）
        page.wait_for_timeout(1500)

        # 実機確認済セレクタ: input[name="userId"] / input[name="password"]
        id_selectors = [
            'input[name="userId"]',
            'input#jscInputUserId',
            'input[name="loginId"]',
            'input[type="text"]',
        ]
        pw_selectors = [
            'input[name="password"]',
            'input.jscPasswordInput',
            'input[type="password"]',
        ]

        id_filled = False
        for s in id_selectors:
            try:
                page.fill(s, cred.login_id, timeout=2000)
                id_filled = True
                break
            except Exception:
                continue
        if not id_filled:
            return False

        pw_filled = False
        for s in pw_selectors:
            try:
                page.fill(s, cred.password, timeout=2000)
                pw_filled = True
                break
            except Exception:
                continue
        if not pw_filled:
            return False

        # submit
        clicked = False
        for sel in [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("ログイン")',
            'input[value*="ログイン"]',
        ]:
            try:
                page.click(sel, timeout=2000)
                clicked = True
                break
            except Exception:
                continue
        if not clicked:
            page.press(pw_selectors[0] if pw_filled else "body", "Enter")

        # HPG は「認証中...」の JS 遷移ページ経由 → /CLN/topMenu/ に遷移する
        # URL が /login/ から離れるのを最大 15 秒待つ
        for _ in range(15):
            page.wait_for_timeout(1000)
            url = page.url
            if "/login/" not in url and "/doLogin" not in url:
                break

        url = page.url
        if "/login" in url or "noLoginError" in url:
            return False
        # topMenu や CLP 系へ遷移していれば成功
        return True

    return login


def main() -> int:
    cred = load_credential(STORE_CODE, SERVICE)
    state_file = state_path_for(SERVICE)
    print(f"[hpg_recruit] target state path: {state_file}", file=sys.stderr)
    with sync_playwright() as pw:
        try:
            context = attempt_login_with_retry(
                pw, service=SERVICE, do_login=_do_login(cred), headless=True
            )
        except UnexpectedAuthChallengeError as e:
            print(f"[FATAL] {e}", file=sys.stderr)
            return 3
        if context is None:
            return 2
        browser = context.browser
        context.close()
        if browser:
            browser.close()
    print(f"[OK] hpg_recruit storageState saved: {state_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
