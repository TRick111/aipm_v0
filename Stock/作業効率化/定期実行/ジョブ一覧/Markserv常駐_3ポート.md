# Markserv 常駐サービス（3ポート）

## このジョブは何をする？

**Markdown をブラウザで閲覧するための markserv プロセスを 3 ポート常駐させます。** 同一LAN内のスマホ/PCから `http://<Mac-mini-LAN-IP>:8810-8812/` でドキュメントを閲覧できます。

| ポート | 内容 | サーブ対象 |
|---|---|---|
| 8810 | AIPM Flow（**今月+先月のみ**） | `~/aipm_v0/.markserv-flow-current/`（YYYYMMのsymlinkを動的に張り替え） |
| 8811 | Markdowns-1 | `~/RestaurantAILab/Markdowns-1/` |
| 8812 | Dashboard/docs | `~/RestaurantAILab/Dashboard/docs/` |

## いつ動く？

- **常時起動**（Mac mini が起動している間は常に立ち上がっている）
- macOS の `launchd` が管理しており、プロセスがクラッシュしても自動再起動
- 月が変わった日 0:05 に Flow の symlink が自動更新（8810のみ再起動）

## どこから動かしている？

- 旧: Cockpit autorun `06e82964` → 毎時 `start-markserv.sh` を kill→再起動していたが、ページ遷移が不安定（特に 8810 が EMFILE でクラッシュ）したため 2026-06-15 に launchd 化
- 現: `~/Library/LaunchAgents/jp.markserv.*.plist`（4ファイル）

## 動かないときの確認ポイント

1. **プロセスとポートの確認**
   ```bash
   launchctl list | grep jp.markserv
   lsof -nP -iTCP -sTCP:LISTEN | grep -E ":(8810|8811|8812)"
   ```
2. **HTTP 応答チェック**
   ```bash
   for p in 8810 8811 8812; do curl -o /dev/null -s -w "$p: HTTP %{http_code}\n" http://127.0.0.1:$p/; done
   ```
3. **ログを見る**
   ```bash
   tail -50 ~/Library/Logs/markserv/aipm-flow.{out,err}.log
   tail -50 ~/Library/Logs/markserv/markdowns-1.{out,err}.log
   tail -50 ~/Library/Logs/markserv/dashboard-docs.{out,err}.log
   tail -50 ~/Library/Logs/markserv/refresh.log
   ```
4. **symlink の張り直しを手動で実行**
   ```bash
   bash ~/aipm_v0/Stock/作業効率化/シェルスクリプト/refresh-markserv-flow.sh
   ```

## 注意事項

- 8810 は `aipm_v0/Flow` 全体ではなく**今月+先月のシンボリックリンクのみ**を serve する。これは Flow 全体だと chokidar が `EMFILE: too many open files` を発生させたため
- 月初をまたぐと自動で symlink が差し替わるが、長期間Macが寝ていて起動した直後は手動で `refresh-markserv-flow.sh` を回すのが安全
- macOSの**ログイン状態でのみ起動**する LaunchAgent。完全に再起動した場合、ログインまで markserv は立ち上がらない

---

## 技術詳細

<details>
<summary>クリックで展開</summary>

### ジョブID
`service_markserv_three_ports`

### 実行基盤
macOS launchd（LaunchAgent、ユーザーセッション）

### 関連ファイル

| 役割 | パス |
|---|---|
| 8810 markserv plist | `~/Library/LaunchAgents/jp.markserv.aipm-flow.plist` |
| 8811 markserv plist | `~/Library/LaunchAgents/jp.markserv.markdowns-1.plist` |
| 8812 markserv plist | `~/Library/LaunchAgents/jp.markserv.dashboard-docs.plist` |
| Flow symlink 更新 plist | `~/Library/LaunchAgents/jp.markserv.aipm-flow.refresh.plist` |
| symlink 更新スクリプト | `~/aipm_v0/Stock/作業効率化/シェルスクリプト/refresh-markserv-flow.sh` |
| 旧起動スクリプト（参考用、未使用） | `~/aipm_v0/Stock/作業効率化/シェルスクリプト/start-markserv.sh` |
| Flow serve view（symlinkの置き場） | `~/aipm_v0/.markserv-flow-current/` |
| ログ出力先 | `~/Library/Logs/markserv/` |

### symlink 更新ロジック

`refresh-markserv-flow.sh` は以下を行う：

1. `date +%Y%m`（今月）と `date -v-1m +%Y%m`（先月）を計算
2. `~/aipm_v0/.markserv-flow-current/` 内の既存 symlink と期待値を比較
3. 変化なし → ログ1行だけ出して exit（no-op）
4. 変化あり → 既存symlink削除 → 新しいsymlinkを張り直し → `launchctl kickstart -k gui/$UID/jp.markserv.aipm-flow` で 8810 のみ再起動
5. `StartCalendarInterval` で毎日 00:05 に発火＋ `RunAtLoad=true` で起動時にも実行

### 起動コマンド（再セットアップ時）

```bash
launchctl load ~/Library/LaunchAgents/jp.markserv.aipm-flow.plist
launchctl load ~/Library/LaunchAgents/jp.markserv.markdowns-1.plist
launchctl load ~/Library/LaunchAgents/jp.markserv.dashboard-docs.plist
launchctl load ~/Library/LaunchAgents/jp.markserv.aipm-flow.refresh.plist
```

### 停止コマンド

```bash
launchctl unload ~/Library/LaunchAgents/jp.markserv.aipm-flow.plist
launchctl unload ~/Library/LaunchAgents/jp.markserv.markdowns-1.plist
launchctl unload ~/Library/LaunchAgents/jp.markserv.dashboard-docs.plist
launchctl unload ~/Library/LaunchAgents/jp.markserv.aipm-flow.refresh.plist
```

### 旧 Cockpit autorun

- ID: `06e82964`（名前: 「Markserv実行」、interval 60分）
- 2026-06-15 に `enabled=false` に変更（巻き戻し用に残置）
- 関連の旧 Markserv 実行タスク（waiting_confirmation で滞留していた10件）は同日に `./cockpit task remove` で掃除済み

### 失敗時の対応

- ポートが LISTEN していない → `launchctl list | grep jp.markserv` で plist がロードされているか確認、`*.err.log` を見る
- EMFILE 系エラーが出た → `.markserv-flow-current/` 配下のsymlink先が膨れていないか確認（誤って Flow 全体や Stock 全体を指していないか）
- symlink が今月+先月になっていない → `refresh-markserv-flow.sh` を手動実行、ログを見る

</details>
