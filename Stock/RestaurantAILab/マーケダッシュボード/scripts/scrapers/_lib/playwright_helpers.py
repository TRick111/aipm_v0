"""
Playwright 共通ヘルパー。

設計:
- storageState の管理（path 計算 / 失効検出 / 再認証要求）
- ログイン試行回数制御（user 指示: 最大 2 回 / 失敗で SKIP）
- secret マスク済エラー出力
- 2FA / CAPTCHA 画面検出 → 即停止
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = REPO_ROOT / ".local" / "playwright-state"


# user 指示: ログイン試行は媒体ごと最大 2 回
MAX_LOGIN_ATTEMPTS = 2


class LoginFailedError(RuntimeError):
    """ログインに 2 回失敗した（media を SKIP する判定用）"""


class UnexpectedAuthChallengeError(RuntimeError):
    """2FA / CAPTCHA / 想定外の認証チャレンジを検出（即停止）"""


def state_path_for(service: str) -> Path:
    """service ごとの storageState ファイルパス。

    例: tabelog_owner -> .local/playwright-state/tabelog.json
        hpg_recruit   -> .local/playwright-state/hpg.json
        restaurant_board -> .local/playwright-state/rb.json
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    mapping = {
        "tabelog_owner": "tabelog.json",
        "tabelog_note": "tabelog.json",  # 食べログ owner と共有
        "hpg_recruit": "hpg.json",
        "restaurant_board": "rb.json",
    }
    return STATE_DIR / mapping.get(service, f"{service}.json")


def detect_2fa_or_captcha(page: Page) -> str | None:
    """ページが 2FA / CAPTCHA を要求しているか判定。理由文字列を返す。None なら未検出。

    注意: false positive を避けるため、URL と「目に見えるテキスト」だけで判定。
    HTML 内に reCAPTCHA ライブラリが含まれているだけ（実際には CAPTCHA を出していない）
    のケースは検出しない。
    """
    url = (page.url or "").lower()
    if any(k in url for k in ["two_factor", "twofactor", "/otp", "/mfa"]):
        return f"URL に 2FA 関連キーワード: {url}"

    # body の visible text のみを見る
    try:
        text = page.locator("body").inner_text(timeout=2000)
    except Exception:  # noqa: BLE001
        return None
    lc = text.lower()
    visible_keywords = [
        "ワンタイムパスワード",
        "認証コードを入力",
        "二段階認証",
        "二要素認証",
        "sms認証",
        "画像認証",
        "ロボットではないことを確認",
        "i'm not a robot",
    ]
    for kw in visible_keywords:
        if kw.lower() in lc:
            return f"ページに 2FA/CAPTCHA キーワード検出: '{kw}'"
    return None


def attempt_login_with_retry(
    pw: Playwright,
    *,
    service: str,
    do_login: Callable[[BrowserContext, Page], bool],
    headless: bool = True,
) -> BrowserContext | None:
    """ログインを最大 MAX_LOGIN_ATTEMPTS 回試行。

    do_login(context, page) -> bool: True ならログイン成功と判定
    成功時: storageState を保存し context を返す（呼び出し側は context.browser.close() でクリーンアップ）
    失敗時: None を返す（呼び出し側で SKIP 判断）
    2FA/CAPTCHA 検出時: UnexpectedAuthChallengeError を即送出
    """
    last_error: Exception | None = None
    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        print(f"[{service}] login attempt {attempt}/{MAX_LOGIN_ATTEMPTS}", file=sys.stderr)
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        try:
            ok = do_login(context, page)
            # 2FA / CAPTCHA チェック
            chal = detect_2fa_or_captcha(page)
            if chal:
                browser.close()
                raise UnexpectedAuthChallengeError(f"[{service}] {chal}")

            if ok:
                state_file = state_path_for(service)
                context.storage_state(path=str(state_file))
                print(f"[{service}] login OK, saved storageState -> {state_file}", file=sys.stderr)
                # context を返すので close しない
                return context
            else:
                print(f"[{service}] attempt {attempt} failed", file=sys.stderr)
                browser.close()
        except UnexpectedAuthChallengeError:
            raise
        except Exception as e:  # noqa: BLE001
            last_error = e
            # secret を含む可能性のあるメッセージはマスクしない（呼び出し側で適切に投げる前提）
            print(f"[{service}] attempt {attempt} error: {type(e).__name__}: {e}", file=sys.stderr)
            try:
                browser.close()
            except Exception:  # noqa: BLE001
                pass

    print(
        f"[{service}] login failed {MAX_LOGIN_ATTEMPTS} times. SKIPPING this media.",
        file=sys.stderr,
    )
    if last_error:
        print(f"[{service}] last error: {type(last_error).__name__}", file=sys.stderr)
    return None


def open_context_with_state(
    pw: Playwright,
    *,
    service: str,
    headless: bool = True,
) -> tuple[BrowserContext, Page]:
    """既存 storageState から context を開く。state 不在ならエラー。"""
    state_file = state_path_for(service)
    if not state_file.exists():
        raise RuntimeError(
            f"[{service}] storageState 不在: {state_file}. login スクリプトを先に実行してください。"
        )
    browser = pw.chromium.launch(headless=headless)
    context = browser.new_context(storage_state=str(state_file), accept_downloads=True)
    page = context.new_page()
    return context, page


__all__ = [
    "LoginFailedError",
    "UnexpectedAuthChallengeError",
    "MAX_LOGIN_ATTEMPTS",
    "STATE_DIR",
    "state_path_for",
    "detect_2fa_or_captcha",
    "attempt_login_with_retry",
    "open_context_with_state",
]
