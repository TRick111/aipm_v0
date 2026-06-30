"""
レストランボード（restaurant-board.com）に自動ログインし storageState を保存。

ログイン試行: 最大 2 回。失敗で exit 2。2FA/CAPTCHA で exit 3。
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
SERVICE = "restaurant_board"
LOGIN_URL = "https://restaurant-board.com/CLP/view/login/"  # connect.airregi.jp に OAuth リダイレクトされる
# AirID が複数店舗を持つ場合、ログイン後 choose-store ページで店舗を選ぶ必要がある
TARGET_STORE_NAME_PARTS = ["ポックンパ", "ネネチキン", "東岡崎"]  # AND 検索キーワード


def _do_login(cred):
    def login(context: BrowserContext, page: Page) -> bool:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # connect.airregi.jp の OAuth ログイン: input[name="username"] / input[name="password"]
        # (dummy01..dummy04 のダミー入力は無視。実本体は id=account / id=password)
        id_selectors = [
            'input#account',
            'input[name="username"]:not([name="dummy01"]):not([name="dummy03"])',
        ]
        pw_selectors = [
            'input#password.js-password',
            'input#password',
            'input[name="password"]:not([name="dummy02"]):not([name="dummy04"])',
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

        for s in pw_selectors:
            try:
                page.fill(s, cred.password, timeout=2000)
                break
            except Exception:
                continue

        # submit
        for sel in [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("ログイン")',
            'input[value*="ログイン"]',
            '.loginBtn',
        ]:
            try:
                page.click(sel, timeout=2000)
                break
            except Exception:
                continue
        else:
            page.press("body", "Enter")

        # JS 遷移を待つ
        for _ in range(15):
            page.wait_for_timeout(1000)
            url = page.url
            if "choose-store" in url:
                break
            if "restaurant-board.com" in url and "/login" not in url.lower() and "/view/login/" not in url.lower():
                return True

        # choose-store ページの場合は対象店舗のリンクをクリック
        if "choose-store" in page.url:
            kw_pattern = "&".join(TARGET_STORE_NAME_PARTS)  # info only
            print(f"  [restaurant_board] choose-store page detected, picking '{kw_pattern}'", file=sys.stderr)
            try:
                clicked = page.evaluate(
                    """(parts) => {
                      const anchors = [...document.querySelectorAll('a')];
                      const a = anchors.find(e => {
                        const t = (e.innerText||'').trim();
                        return parts.every(p => t.includes(p));
                      });
                      if (a) { a.click(); return true; }
                      return false;
                    }""",
                    TARGET_STORE_NAME_PARTS,
                )
                if not clicked:
                    print("  [restaurant_board] target store not found in choose-store list", file=sys.stderr)
                    return False
            except Exception as e:  # noqa: BLE001
                print(f"  [restaurant_board] choose-store click err: {e}", file=sys.stderr)
                return False

            # 店舗選択後の遷移待ち
            for _ in range(20):
                page.wait_for_timeout(1000)
                u = page.url
                if "restaurant-board.com" in u and "choose-store" not in u and "/view/login/" not in u:
                    break

        url = page.url
        if "/view/login/" in url or "connect.airregi.jp/login" in url:
            return False
        if "choose-store" in url:
            return False
        return "restaurant-board.com" in url


    return login


def main() -> int:
    cred = load_credential(STORE_CODE, SERVICE)
    state_file = state_path_for(SERVICE)
    print(f"[restaurant_board] target state path: {state_file}", file=sys.stderr)
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
    print(f"[OK] restaurant_board storageState saved: {state_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
