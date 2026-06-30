"""
レストランボード 予約一覧 CSV を月別に取得。

仕組み（2 段階非同期 + メッセージから DL）:
  1. POST /CLP/api/getReserveCsv/create  body: {storeList:[...], dispStartDate:YYYYMMDD, dispEndDate:YYYYMMDD}
     - storeList は対象店舗のみ（getAirIdStoreList で取得した一覧から store_name 一致を 1 店舗選ぶ）
     - dispStartDate / dispEndDate で期間指定（最大 10,000 件まで）
  2. /CLP/view/message/ システム通知タブをポーリング
  3. 「ダウンロードする」ボタン (= /CLP/view/csvDl/message?msgNo=NNN) を押下 → CSV ダウンロード

使い方:
    python3 fetch_reservations.py                     # 過去 12 ヶ月（月別）
    python3 fetch_reservations.py --month 2026-06
    python3 fetch_reservations.py --months 6
    python3 fetch_reservations.py --bulk 12           # 12 ヶ月 1 リクエストで試行（10,000 件超過リスク）

出力: sample_data/restaurant_board/auto/<YYYY-MM>.csv
        ＋（--bulk 時）sample_data/restaurant_board/auto/<YYYY-MM>_to_<YYYY-MM>.csv

対象店舗: accounts.yaml の store_code に基づく（ここでは "韓国屋台ポックンパ　ネネチキン　東岡崎店" のみ）
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright  # noqa: E402

from _lib.credentials import get_target_months  # noqa: E402
from _lib.playwright_helpers import open_context_with_state  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "sample_data" / "restaurant_board" / "auto"
LIST_URL = "https://restaurant-board.com/CLP/view/reserveListWeb/"
MSG_URL = "https://restaurant-board.com/CLP/view/message/"
CREATE_API = "https://restaurant-board.com/CLP/api/getReserveCsv/create"
STORE_LIST_API = "https://restaurant-board.com/CLP/api/getAirIdStoreList/execute"

TARGET_STORE_NAME_PARTS = ["ポックンパ", "ネネチキン", "東岡崎"]


def parse_args(argv: list[str]) -> tuple[list[tuple[str, str]], str]:
    """戻り値: (期間リスト[(start_YYYYMMDD, end_YYYYMMDD)], label)

    label: ファイル名サフィックス（月別なら YYYY-MM、bulk なら YYYY-MM_to_YYYY-MM）
    """
    if "--bulk" in argv:
        i = argv.index("--bulk")
        n = int(argv[i + 1])
        months = get_target_months(months=n)
        oldest = months[-1]
        newest = months[0]
        y1, m1 = map(int, oldest.split("-"))
        y2, m2 = map(int, newest.split("-"))
        start = date(y1, m1, 1)
        # 月末
        from calendar import monthrange
        end_day = monthrange(y2, m2)[1]
        end = date(y2, m2, end_day)
        return [(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))], f"{oldest}_to_{newest}"
    if "--month" in argv:
        i = argv.index("--month")
        ym = argv[i + 1]
        from calendar import monthrange
        y, m = map(int, ym.split("-"))
        last = monthrange(y, m)[1]
        return [(f"{y:04d}{m:02d}01", f"{y:04d}{m:02d}{last:02d}")], ym
    n = 12
    if "--months" in argv:
        i = argv.index("--months")
        n = int(argv[i + 1])
    months = get_target_months(months=n)
    out: list[tuple[str, str]] = []
    from calendar import monthrange
    for ym in months:
        y, m = map(int, ym.split("-"))
        last = monthrange(y, m)[1]
        out.append((f"{y:04d}{m:02d}01", f"{y:04d}{m:02d}{last:02d}"))
    return out, "monthly"


def _extract_api_key(page) -> str | None:
    """ページ HTML から apikeycd を抽出。"""
    return page.evaluate(
        """() => {
          const html = document.documentElement.outerHTML;
          const m = html.match(/apikeycd['"]?\\s*[:=]\\s*['"]([A-Z0-9]+)/i);
          return m ? m[1] : null;
        }"""
    )


def get_target_store(ctx, page, storeId_hint: str = "KR00892810") -> dict | None:
    """getAirIdStoreList API を叩いて対象店舗の {storeId, storeName, storeNo} を返す。"""
    api_key = _extract_api_key(page)
    headers = {"content-type": "application/json", "accept": "application/json"}
    if api_key:
        headers["apikeycd"] = api_key
    res = ctx.request.post(
        STORE_LIST_API,
        data=json.dumps({"storeId": storeId_hint}),
        headers=headers,
    )
    if res.status != 200:
        print(f"  [rb] getAirIdStoreList HTTP {res.status}", file=sys.stderr)
        return None
    data = res.json()
    # 実機 API は {"results": {"storeList": [...]}} を返す
    candidates: list = []
    if isinstance(data, dict):
        if isinstance(data.get("results"), dict) and isinstance(data["results"].get("storeList"), list):
            candidates = data["results"]["storeList"]
        elif isinstance(data.get("storeList"), list):
            candidates = data["storeList"]
        elif isinstance(data.get("data"), dict) and isinstance(data["data"].get("storeList"), list):
            candidates = data["data"]["storeList"]
    elif isinstance(data, list):
        candidates = data

    target = None
    for s in candidates:
        name = str(s.get("storeName", ""))
        if all(p in name for p in TARGET_STORE_NAME_PARTS):
            target = s
            break
    if target:
        return {
            "storeId": target.get("storeId"),
            "storeName": target.get("storeName"),
            "storeNo": target.get("storeNo"),
        }
    return None


def trigger_create_and_download(ctx, page, *, target_store: dict, start: str, end: str) -> Path | None:
    """1 期間分: API で create → メッセージ画面で「ダウンロードする」を押下 → CSV を返す。"""
    payload = {
        "storeList": [target_store],
        "dispStartDate": start,
        "dispEndDate": end,
    }
    print(f"  [rb] POST create {start}-{end}", file=sys.stderr)
    api_key = _extract_api_key(page)
    headers = {"content-type": "application/json", "accept": "application/json"}
    if api_key:
        headers["apikeycd"] = api_key
    res = ctx.request.post(
        CREATE_API,
        data=json.dumps(payload),
        headers=headers,
    )
    if res.status != 200:
        print(f"  [rb] create HTTP {res.status}: {res.text()[:200]}", file=sys.stderr)
        return None
    # 非同期キューに投入された。メッセージページをポーリング
    # 「指定日：YYYY/MM/DD」が start/end と一致する通知を探す
    # 注意: 同期通知メッセージに開始日のみ含まれる場合と、開始-終了の両方含まれる場合がある
    # 表記揺れ対応のため、開始日 YYYY/MM/DD 文字列のみで一致判定する
    start_disp = f"{start[:4]}/{start[4:6]}/{start[6:8]}"
    end_disp = f"{end[:4]}/{end[4:6]}/{end[6:8]}"
    deadline = time.time() + 180
    matched_btn_index: int | None = None
    while time.time() < deadline:
        page.goto(MSG_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        # システム通知タブ
        try:
            page.click('text=システム通知', timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        # 最新の CSVファイル作成 完了通知を探す (start/end が含まれる通知の button index を返す)
        idx = page.evaluate(
            """(args) => {
              const {startDisp, endDisp} = args;
              const buttons = [...document.querySelectorAll('button')].filter(b => (b.innerText||'').trim() === 'ダウンロードする');
              for (let i = 0; i < buttons.length; i++) {
                const b = buttons[i];
                let p = b;
                for (let j = 0; j < 10; j++) {
                  if (!p.parentElement) break;
                  p = p.parentElement;
                  const t = (p.innerText||'');
                  if (t.includes('CSVファイル作成') && t.includes('完了')) {
                    if (t.includes(startDisp) && t.includes(endDisp)) {
                      return i;
                    }
                    break;
                  }
                }
              }
              return -1;
            }""",
            {"startDisp": start_disp, "endDisp": end_disp},
        )
        if idx >= 0:
            matched_btn_index = idx
            break
        print(f"    waiting for CSV ready ({start_disp}-{end_disp})... ({int(deadline - time.time())}s left)", file=sys.stderr)
        time.sleep(5)

    if matched_btn_index is None:
        print(f"  [rb] timed out waiting for CSV msg ({start}-{end})", file=sys.stderr)
        return None

    # Click the matched ダウンロードする button by index
    try:
        with page.expect_download(timeout=30000) as dl_info:
            page.evaluate(
                """(idx) => {
                  const buttons = [...document.querySelectorAll('button')].filter(b => (b.innerText||'').trim() === 'ダウンロードする');
                  if (buttons[idx]) buttons[idx].click();
                }""",
                matched_btn_index,
            )
        dl = dl_info.value
        return dl
    except Exception as e:  # noqa: BLE001
        print(f"  [rb] download click failed: {e}", file=sys.stderr)
        return None


def main() -> int:
    periods, label = parse_args(sys.argv[1:])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    with sync_playwright() as pw:
        ctx, page = open_context_with_state(pw, service="restaurant_board", headless=True)
        # ウォームアップ
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        target_store = get_target_store(ctx, page)
        if not target_store:
            print("[rb] target store not found via getAirIdStoreList", file=sys.stderr)
            ctx.close()
            return 2
        print(f"[rb] target store: {target_store.get('storeName')} (storeId={target_store.get('storeId')})", file=sys.stderr)

        for start, end in periods:
            ym_label = f"{start[:4]}-{start[4:6]}" if label == "monthly" else label
            print(f"[rb] period {start}-{end} -> sample_data/.../{ym_label}.csv", file=sys.stderr)
            dl = trigger_create_and_download(ctx, page, target_store=target_store, start=start, end=end)
            if dl is None:
                failures.append(ym_label)
                continue
            out_path = OUT_DIR / f"{ym_label}.csv"
            dl.save_as(str(out_path))
            size = out_path.stat().st_size
            try:
                text = out_path.read_text(encoding="cp932")
            except UnicodeDecodeError:
                text = out_path.read_text(encoding="utf-8", errors="replace")
            rows = max(0, text.count("\n") - 1)
            print(f"  [rb] OK: size={size:,}B rows={rows} -> {out_path}", file=sys.stderr)
            # 礼儀的レート制限（次の create リクエストの前）
            time.sleep(2)
        ctx.close()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
