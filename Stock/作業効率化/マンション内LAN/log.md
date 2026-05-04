# log: マンション内LAN

## 2026-05-04
- プロジェクト bootstrap
- 2回目のネットワーク診断を実施
  - ユーザーから症状ヒアリング: 「初回アクセス遅・2回目以降速」「PC/スマホ両方」「セルラーは速」「過去 MTU 1024 で改善」
  - ルーター管理画面のスクショ確認 → WAN IP が `192.168.6.114` で**ダブル NAT 確定**
  - traceroute / dig / ping / curl を実行
    - traceroute: hop1 192.168.11.1 → hop2 192.168.6.241 → hop3 219.59.90.205（グローバル）
    - DNS: 1.1.1.1 経由 5〜8ms（無実）
    - ICMP: 1.1.1.1 への通常 ping すら 3 回中 2 回ロス（重度のレート制限／フィルタ）
    - curl: TCP `CONN` がぴったり 1.000 秒のケースが複数（**TCP SYN 再送 = initial RTO 1 秒**のサイン）
    - グローバル IP: `219.59.90.206`
- 真因仮説を更新: 「ダブル NAT + 上位機器のセッション／レート制限」「ICMP フィルタによる PMTU 黒穴」
  - 「初回遅い・2 回目速い」体感の正体は、ブラウザの HTTP keep-alive / DNS / TLS セッションキャッシュで 2 回目は新規接続フェーズが省略されるため
- 対策候補を整理:
  1. Cloudflare WARP（無料）導入 ← MTU 変更不要・即効性大・第一候補
  2. ブラウザを HTTP/3 (QUIC) 優先利用
  3. Buffalo の IPv6 設定は「使用しない」維持
  4. 根治: マンション管理会社へ「ダブル NAT 解消 / 上位ルーター再起動 / セッション制限緩和」を相談
  5. 個別回線契約（光コンセントがあれば）— 当面は対象外
- 詳細レポートを `診断レポート_2026-05-04.md` に保存

### 同日 (2026-05-04) WARP 検証
- `brew install --cask cloudflare-warp` で導入（パスワード入力はユーザー手動）
- 初期状態は `Mode: DnsOverHttps`（=1.1.1.1 のみ、トンネル無し）
- フルトンネル化を試行
  - まず `warp-cli mode warp+doh`（既定 MASQUE）→ `CF_DNS_LOOKUP_FAILURE`
  - 仮説「上位が UDP/443 MASQUE を遮断」→ `warp-cli tunnel protocol set WireGuard` に切替
  - 再度 `warp-cli mode warp+doh` → 同じく `CF_DNS_LOOKUP_FAILURE`、ハッピーアイボール `162.159.192.3:2408` 宛で 13 秒粘って失敗
  - 但し curl では `https://www.cloudflare.com/cdn-cgi/trace` が `warp=on` で着弾（`ip=2a09:bac1:3b00:10::16:231 / colo=NRT`）→ トンネルは「片肺」状態
- 切戻し: `warp-cli mode doh`（ユーザー手動）。プロトコルは WireGuard のまま保持
- ユーザー判断で「DoH のみで体感が改善している」ためプラン A（utun MTU 1024 手動）は保留
- DoH のみ状態で curl ベンチ再実施 → **「CONN ぴったり 1.000 秒」現象が完全消失**
  - 例: yahoo.co.jp 1 回目 CONN `1.019s → 0.031s`、yahoo 2 回目 `1.010s → 0.010s`、asahi 2 回目 `1.008s → 0.011s`
- 推察: マンション上位の DNS 経路に介入／レート制限あり。DoH（TLS）でカプセル化したことで透過介入を回避できた
- 1〜2 日運用してぶり返しが無ければ本採用、再発したらプラン A（utun MTU 1024）へ進む
- 切り戻しワンライナー（緊急時）: `warp-cli mode doh ; warp-cli tunnel protocol reset`
