---
date: 2026-05-02
type: infra-incident-report
project: ミニタキオン
category: 作業効率化
related_systems: [mini-tachyon, AGI Cockpit, Tailscale]
status: resolved
tags: [migration, network, tailscale, cgnat, launchd]
---

# ミニタキオン インフラ独立化 と Tailscale 接続問題

2026-05-02 に発生した一連のインフラ問題と解決を記録する。
**結論**: ミニタキオンを `~/.agi-tools/mini-tachyon` から `~/mini-tachyon` に独立化、Tailscale 経由でセルラーから接続できない問題は iPhone Tailscale daemon の完全再起動で解決。

---

## 1. 顛末サマリ（時系列）

| 時刻 | できごと |
|---|---|
| 朝 | iPhone (cellular) から `http://100.105.5.39:3000` にアクセス → タイムアウト。同様に AGI Cockpit `https://...:47280` も不通 |
| - | Tailscale 自体は健全（admin console で iPhone も Mac もオンライン、`tailscale ping` で direct P2P 53ms 成立） |
| - | macOS Application Firewall も健全（`node` / `AGI Cockpit.app` ともに permit 済み） |
| - | 当初仮説: Next.js が IPv6 デュアルスタック (`*:3000`) のみで bind されていて Tailscale (utun, IPv4) からの着信を取りこぼし → `package.json` の `start`/`dev` に `-H 0.0.0.0` を追加 |
| - | **修正後一旦復旧したように見えたが、ミニタキオン関連タスクを動かしたら再発**。両ポート (mini-tachyon :3000 / Cockpit :47280) が同時に外部から不通に |
| - | LAN（同じ WiFi）からはアクセス可能。**Tailscale 経由（cellular）だけが不通**であることが判明 |
| 19:00頃 | ミニタキオンを `~/mini-tachyon` に物理的に独立化（Section 2 参照） |
| 20:00頃 | 独立化しても Tailscale 経由の接続問題は解消しない → ネットワーク層の問題と確定 |
| 20:13-20 | Python 簡易サーバ `:8000` を立てて切り分け。**Mac には iPhone のリクエストが届いていて 200 を返しているのに、iPhone のブラウザではレスポンスが受信できない**ことを確認 |
| 20:20頃 | iPhone Tailscale daemon の完全再起動（Section 3）で復旧 |

---

## 2. ミニタキオンの物理独立化

### Why
- 旧配置 `~/.agi-tools/mini-tachyon` だと AGI Cockpit のサブシステムに見えてしまう
- 実態としては独立した Next.js アプリ（データは `~/aipm_v0`、Cockpit には `cockpit` CLI 外部 spawn のみ）
- 切り分け時に「Cockpit と一緒くたに止める」が難しかった

### What
| 項目 | 旧 | 新 |
|---|---|---|
| 配置 | `~/.agi-tools/mini-tachyon` | **`~/mini-tachyon`** |
| launchd ラベル | `jp.agi-tools.mini-tachyon` | **`jp.mini-tachyon`** |
| plist | `~/Library/LaunchAgents/jp.agi-tools.mini-tachyon.plist` | **`~/Library/LaunchAgents/jp.mini-tachyon.plist`** |
| ログ | `~/.agi-tools/mini-tachyon/launchd/` | `~/mini-tachyon/launchd/` |

### コード変更
ハードコードされていた `~/.agi-tools/mini-tachyon` パス参照を全て `~/mini-tachyon` に置換:
- `lib/mt-agent-prompt.ts` (MT_CLI, MT_DOCS_CLI)
- `lib/fallback-instruction.ts` (MT_CLI)
- `lib/prompts/daily-start.md`
- `lib/prompts/daily-wrapup.md`
- `lib/__tests__/prompts.test.ts`
- `app/__tests__/actions.test.ts`
- `docs/CLI.md`

`COCKPIT_BIN` (`lib/cockpit.ts:11-12`) は **意図的に変更なし**。これは Cockpit 側のバイナリパスで、`process.env.COCKPIT_BIN` で上書き可能なので柔軟性を保つ。

### 注意点
旧 plist は退避済 (`jp.agi-tools.mini-tachyon.plist.bak`)。完全削除せず .bak で残してある。

---

## 3. Tailscale 接続問題

### 症状
- iPhone を **同じ WiFi** に繋いでいる時: Tailscale 経由でも LAN 直結でも `100.105.5.39:3000` / `192.168.11.13:3000` で問題なくアクセス可能
- iPhone を **WiFi OFF（cellular のみ）** にすると、Tailscale 経由で `100.105.5.39:3000` にアクセス不能（接続中のままタイムアウト）

### 根本原因
**iPhone Tailscale daemon が cellular 切り替え時に endpoint を更新できていなかった。**

詳細:

1. `tailscale debug peer-endpoint-changes 100.81.170.72` で確認した iPhone のエンドポイント一覧の最終更新が **約1時間半前**（19:00:48）で停止していた
2. Mac は古い endpoint `133.106.35.36:42138`（iPhone が WiFi に繋がっていた時の公開IP）に Tailscale パケットを送り続けていた
3. iPhone → Mac 方向は cellular CGNAT 経由で (おそらく DERP 中継 fallback で) なんとか届いていた → Python サーバには iPhone リクエストが到達して 200 を返していた
4. Mac → iPhone 方向は古い endpoint に飛ばしていたため、レスポンスが iPhone に届かない → ブラウザは「接続中」のままタイムアウト
5. `tailscale ping` だと小さい UDP パケットなので時々通っていたため「Tailscale は健全」に見えた（実際は片方向しか動いていない）

### 補足: なぜ起きたか
- このMacは **double NAT** 環境（router の WAN 側 IP が `192.168.6.114` という ISP CGNAT）
- iPhone も日本のキャリア cellular で **CGNAT** 配下
- 両側 CGNAT で direct P2P (NAT越え) が脆く、iPhone のネットワーク変化を追従できなかった

### Mac 側で試したけど効かなかったこと
- `tailscale down && tailscale up` (Mac 側だけ再接続) → 効果なし、direct path が同じ古い IP に戻る
- `tailscale debug restun` → magicsock 再構築。瞬間的に DERP に倒れるがすぐ direct に戻る
- `tailscale debug force-prefer-derp 7` (Tokyo を強制) → これは home DERP 設定であって peer 通信を強制 DERP にするものではなかった。直結に戻る
- `package.json` で `-H 0.0.0.0` 強制 → これは別問題（IPv6 dual-stack のみで bind されていた）でいずれにせよ必要だった修正

### 効いた解決策（再発時の手順）

**iPhone 側で完全リセット**。Tailscale アプリの Connect トグルだけでは効かない。daemon ごと殺す:

```
1. iPhone でコントロールセンター → 機内モード ON
2. 5秒待つ（cellular が完全に切断される）
3. 機内モードを OFF（cellular 再接続。新しいキャリア IP を取得）
4. WiFi は引き続き OFF のまま
5. Tailscale アプリをアプリスイッチャから完全終了（上スワイプで殺す）
6. 30秒待つ
7. Tailscale アプリを再度開く
8. メイン画面の Connect トグルが ON、Connected 表示、Mac が緑のドット
9. Tailscale アプリを開いたまま Chrome に切り替え（フォアグラウンドにしておく）
10. 目的の URL にアクセス
```

これで iPhone Tailscale daemon が完全に再起動して、新しい cellular IP で endpoint を STUN 経由で再登録する。Mac 側にも新しい endpoint 情報が伝わる。

---

## 4. 教訓・今後の運用

### 既知の挙動（再発時に思い出すこと）
- **Mac→iPhone の `tailscale ping` が成功するからと言って、TCP HTTP が双方向に通っているとは限らない**。pingは小UDP、HTTPは大TCPで挙動が違う。iPhone から実際にHTTPを叩くまで「外部からアクセス可能」とは判定できない
- **iPhone の Connect トグル ON/OFF だけでは endpoint refresh できない**。daemon 再起動が必要 = アプリ強制終了が必須
- **iPhone がネットワーク切り替え（WiFi↔cellular）した直後はしばらく不安定**。`tailscale debug peer-endpoint-changes` で endpoint 更新時刻を確認すると、何時間も古いままになっていることがある
- **macOS Tailscale CLI** は symlink ではなく shell wrapper でないと bundleIdentifier エラーで起動しない (`io.tailscale.ipn.macsys` 版)。`/Applications/Tailscale.app/Contents/Resources/InstallTailscaleCLI.scpt` 経由で正規インストールするか、`#!/bin/sh\nexec ...` の wrapper を `/usr/local/bin/tailscale` に書く

### Next.js の bind に関する別の罠
- Next.js は `-H` 指定なしだと macOS では IPv6 デュアルスタック (`*:3000`) のみで bind され、Tailscale (utun, IPv4) からの着信を取りこぼすことがある
- **対策**: `package.json` の `start` / `dev` に **`-H 0.0.0.0`** を必ず付ける
- launchd plist の `EnvironmentVariables` で `HOSTNAME=0.0.0.0` を設定しても、Next.js のバージョンによっては argv の `-H` が優先される。**`-H` 引数で指定するのが確実**
- これはミニタキオン以外の Next.js プロジェクトでも初期化時に同じ修正を入れるべき（メモリの `feedback_tachyon_network.md` 参照）

### 移行による副次効果
- mini-tachyon と AGI Cockpit を物理的に分離したので、今後は片方を完全停止するのが launchctl 1コマンドで済む（切り分けが容易）
- `~/.agi-tools/` 配下が Cockpit 専用になったので、誤操作リスクが減った

---

## 5. 検証用に立てた一時的なテスト基盤（撤去済 or 撤去推奨）

| 何 | 状態 |
|---|---|
| Python `:8000` (`python3 -m http.server 8000 --bind 0.0.0.0`) | 動作中 (PID 10508)。**用済みなので `kill 10508` 推奨** |
| Tailscale CLI shell wrapper `/usr/local/bin/tailscale` | 残しておくと今後の切り分けが速い、削除不要 |
| `~/Library/LaunchAgents/jp.agi-tools.mini-tachyon.plist.bak` | 移行ロールバック用に1〜2週間残す。問題なければ削除 |

---

## 6. 関連メモ

- `~/.claude/projects/-Users-rikutanaka--agi-tools-data-cockpit-master/memory/feedback_tachyon_network.md` — `-H 0.0.0.0` ルール
- `~/.claude/projects/-Users-rikutanaka--agi-tools-data-cockpit-master/memory/feedback_port_assignments.md` — ポート割当（3000空き、3001以降既存PJ）
- `~/.claude/plans/mini-tachyon-mini-tachyon-mini-tachyon-calm-pascal.md` — 今回の移行プラン
- `~/aipm_v0/Stock/作業効率化/環境整備/ネットワーク最適化診断_2026-04-22.md` — 過去のネットワーク診断
