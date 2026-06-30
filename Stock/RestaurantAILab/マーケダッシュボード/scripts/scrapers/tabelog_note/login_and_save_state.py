"""
食べログ owner ログイン → storageState 保存。

食べログノート（/tn/ 系）は同じ owner.tabelog.com ドメインなので、
本スクリプトで保存した storageState を以下が共有する:
- 食べログノート 予約一覧
- 食べログノート 予約コース
- 食べログノート 分析（総客数）

ログイン試行は最大 2 回（user 指示）。失敗で exit 2（SKIP 用）。
2FA / CAPTCHA 検出時は exit 3（即停止）。
"""

from __future__ import annotations

import sys
from pathlib import Path

# scripts/scrapers をモジュール検索パスに
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import BrowserContext, Page, sync_playwright  # noqa: E402

from _lib.credentials import load_credential  # noqa: E402
from _lib.playwright_helpers import (  # noqa: E402
    UnexpectedAuthChallengeError,
    attempt_login_with_retry,
    state_path_for,
)


STORE_CODE = "pockunpa-okazaki"
SERVICE = "tabelog_owner"
LOGIN_URL = "https://owner.tabelog.com/owner_account/login/"


def _do_login(cred) -> callable:
    def login(context: BrowserContext, page: Page) -> bool:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        # owner.tabelog.com のログインフォーム
        # 実機確認済セレクタ: input#login_id / input#password
        try:
            page.wait_for_selector("input#login_id", timeout=15000)
        except Exception:
            # ログイン済へ自動遷移しているケース
            if "/owner_account/login" not in page.url:
                return True
            raise

        page.fill("input#login_id", cred.login_id)
        page.fill("input#password", cred.password)

        # submit button
        for sel in [
            'button[type="submit"]',
            'input[type="submit"]',
            'button.oc-button',
            'form button',
        ]:
            try:
                page.click(sel, timeout=2000)
                break
            except Exception:
                continue
        else:
            # Enter で送信
            page.press("input#password", "Enter")

        # 遷移待ち
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass

        url = page.url
        # 成功判定: ログイン URL を離脱
        if "/owner_account/login" in url:
            return False
        return True

    return login


def main() -> int:
    cred = load_credential(STORE_CODE, SERVICE)
    state_file = state_path_for(SERVICE)
    print(f"[tabelog_owner] target state path: {state_file}", file=sys.stderr)

    with sync_playwright() as pw:
        try:
            context = attempt_login_with_retry(
                pw,
                service=SERVICE,
                do_login=_do_login(cred),
                headless=True,
            )
        except UnexpectedAuthChallengeError as e:
            print(f"[FATAL] {e}", file=sys.stderr)
            return 3

        if context is None:
            print("[tabelog_owner] SKIP: login failed 2 times", file=sys.stderr)
            return 2

        # クリーンアップ
        browser = context.browser
        context.close()
        if browser:
            browser.close()

    print(f"[OK] tabelog_owner storageState saved: {state_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
