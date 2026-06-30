"""
accounts.yaml から認証情報を読み出す共通ユーティリティ。

設計方針:
- 認証値（login_id / password / 2FA seed 等）は **絶対に print / log / repr に晒さない**
- 取得は dict / NamedTuple ではなく、`_Credential` という __repr__ / __str__ をマスクしたクラスで包む
- `same_as` 解決もここで対応（食べログノート→食べログ owner など）

使い方:
    from _lib.credentials import load_credential
    cred = load_credential("pockunpa-okazaki", "tabelog_owner")
    page.fill("#login_id", cred.login_id)
    page.fill("#password", cred.password)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
ACCOUNTS_YAML = REPO_ROOT / "credentials" / "accounts.yaml"


class CredentialError(RuntimeError):
    """認証情報の読み出しに失敗したときに送出"""


@dataclass(frozen=True)
class Credential:
    """1 媒体のログイン情報。__repr__ / __str__ で値を絶対に出さない。"""

    store_code: str
    service: str
    url: str
    login_id: str
    password: str
    two_factor: str
    notes: str

    def __repr__(self) -> str:  # noqa: D401
        return f"Credential(store={self.store_code}, service={self.service}, url={self.url}, login_id=***, password=***)"

    def __str__(self) -> str:
        return self.__repr__()


def _load_yaml() -> dict[str, Any]:
    if not ACCOUNTS_YAML.exists():
        raise CredentialError(
            f"accounts.yaml が見つかりません: {ACCOUNTS_YAML}. "
            f"accounts.example.yaml をコピーして実値を入れてください。"
        )
    with ACCOUNTS_YAML.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise CredentialError("accounts.yaml のルートが dict ではありません")
    return data


def _find_store(data: dict[str, Any], store_code: str) -> dict[str, Any]:
    for store in data.get("stores", []) or []:
        if store.get("store_code") == store_code:
            return store
    raise CredentialError(f"store_code='{store_code}' が accounts.yaml に存在しません")


def load_credential(store_code: str, service: str) -> Credential:
    """指定店舗・指定サービスの認証情報を返す（same_as 解決込み）。

    値は環境変数オーバーライド可能（CI 等で yaml に書かないケース対応）:
        {STORE_CODE}__{SERVICE}__LOGIN_ID
        {STORE_CODE}__{SERVICE}__PASSWORD
    例: POCKUNPA_OKAZAKI__HPG_RECRUIT__LOGIN_ID
    """
    data = _load_yaml()
    store = _find_store(data, store_code)
    accounts = store.get("accounts") or {}
    if service not in accounts:
        raise CredentialError(f"service='{service}' が store='{store_code}' に存在しません")

    svc = accounts[service]
    # same_as 解決: 自分が空 ID/PW で same_as 指定があるなら親を引く
    same_as = (svc.get("same_as") or "").strip()
    if same_as and not (svc.get("login_id") and svc.get("password")):
        parent = accounts.get(same_as)
        if not parent:
            raise CredentialError(
                f"same_as='{same_as}' で参照された親サービスが見つかりません (store={store_code})"
            )
        login_id = parent.get("login_id") or ""
        password = parent.get("password") or ""
        two_factor = parent.get("two_factor") or "none"
        url = svc.get("url") or parent.get("url") or ""
    else:
        login_id = svc.get("login_id") or ""
        password = svc.get("password") or ""
        two_factor = svc.get("two_factor") or "none"
        url = svc.get("url") or ""

    # env override
    env_prefix = f"{store_code.upper().replace('-', '_')}__{service.upper()}__"
    login_id = os.environ.get(env_prefix + "LOGIN_ID", login_id)
    password = os.environ.get(env_prefix + "PASSWORD", password)

    if not login_id or not password:
        raise CredentialError(
            f"login_id / password が空です (store={store_code}, service={service}). "
            f"accounts.yaml を確認するか env {env_prefix}LOGIN_ID / {env_prefix}PASSWORD を設定してください。"
        )

    return Credential(
        store_code=store_code,
        service=service,
        url=url,
        login_id=login_id,
        password=password,
        two_factor=two_factor,
        notes=(svc.get("notes") or ""),
    )


def get_target_months(reference_date: str | None = None, months: int | None = None) -> list[str]:
    """accounts.yaml の target_period に基づき、過去 N ヶ月の YYYY-MM リストを返す（新しい順）。

    引数で override 可能。reference_date 未指定なら本日扱い。
    """
    from datetime import date, timedelta

    data = _load_yaml()
    tp = data.get("target_period", {}) or {}
    ref_str = reference_date or (tp.get("reference_date") or "")
    if ref_str:
        try:
            y, m, d = map(int, ref_str.split("-"))
            ref = date(y, m, d)
        except Exception as e:  # noqa: BLE001
            raise CredentialError(f"reference_date='{ref_str}' のパースに失敗: {e}")
    else:
        ref = date.today()

    n_months = months or int(tp.get("months", 12) or 12)

    # 当月含めて N ヶ月遡る（user 要件: 「少なくとも 2026-06 月分」を含むため）
    # 例: 2026-06-28 / months=12 -> [2026-06, 2026-05, ..., 2025-07]
    result: list[str] = []
    y, m = ref.year, ref.month
    for _ in range(n_months):
        result.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return result


__all__ = ["Credential", "CredentialError", "load_credential", "get_target_months", "ACCOUNTS_YAML"]
