# 第6回セッション 内容ドラフト (content draft) — v2

作成日: 2026-04-27
担当: 田中利空 (AI ドラフト by claude)
対象: 近藤Ponさん (Rio's Innovation)
セッション本番: 2026-04-27 (月)
BL: BL-0073

> **v2 改訂点**: 田中さん指示で講義スコープを差し替え。新3本柱は (1) Cursor で AI を自動実行 / (2) 能動的自動実行 + ntfy.sh で iPhone push / (3) Google Calendar 連携。
> outline (`session6_outline_v2.md`) を先に読むこと。
> 旧 v1 の内容は `Flow/202604/2026-04-26/RestaurantAILab/バンコクPonさん案件/session6_content_draft.md` に温存。

---

## 表紙スライド

> **第6回：AI を「能動」に変える — Cursor 自動実行・iPhone push・Google Calendar**
>
> 2026-04-27
> Restaurant AI Lab × Rio's Innovation

---

## Part 0：前回までの振り返り + 今回スコープ変更の説明 (5分)

### スライド構成
- 第5回 (MCP活用) 以降の運用状況の確認
- スコープ変更の説明
  - 旧予定: 繰り返しタスク / iCloud カレンダー / 会話履歴インポート
  - 新スコープ: AI を能動的に動かす3本柱
  - 旧テーマは第7〜8回で扱う

### 進行台本 (田中向け)
- 「**第5回でMCP設定したGoogleサービス、毎日使えてますか？**」を最初に聞く
- 使えていない場合 → 原因を聞く (Cursor を開く頻度が低い／信号機が分からない／鍵が切れた等)
- → ここを起点に「**Cursor を開いてないとAIが動かない問題**」を提起 → Part 2 へ繋ぐ

### スコープ変更の伝え方 (大事)
- 「先週まで定型タスク・iCloud連携・履歴インポートを予定してましたが、**先に『AI を勝手に動かす』方が PONさんの日常変化が大きい** と判断して内容差し替えました」
- 「定型タスクと履歴インポートは第7〜8回で必ずやります。**先送りではなく順番替え** です」
- 旧スライドが手元にあれば「これは次回」と物理的に脇に置く

---

## Part 1：今日やることの全体像 (5分)

### スライド構成

#### スライド 1-1: タイトル
> **「AI を待機から能動に変える」**

#### スライド 1-2: 3本柱
> | テーマ | 解く問題 |
> |--------|---------|
> | Cursor 自動実行 | Cursor を開いていない時間は AI が止まっている |
> | 能動的自動実行 + iPhone push | 結果が手元に届くまで設計しないと使われない |
> | Google Calendar 連携 | 「いつやるか」を AI が知らない |

#### スライド 1-3: Before / After
> ```
> 【Before】                                  【After】
> AIに毎回「ニュース要約して」と依頼           毎朝7時に勝手に要約が iPhone に届く
> カレンダー予定はiPhoneで開いて確認           AIに「来週の予定教えて」で済む
> Cursorを開いている時間しかAIが動かない       Cursorを閉じていてもAIが定時に動く
> ```

#### スライド 1-4: 3本柱の関係
> ```
> ┌──────────────────────────────────────────────┐
> │  AIを「待機」から「能動」に変える             │
> ├──────────────┬──────────────┬─────────────────┤
> │ Cursor自動実行│ 能動トリガ    │ Google Cal連携 │
> │ (起動の自動化)│ (時間/イベント)│ (時間軸の参照) │
> └──────────────┴──────────────┴─────────────────┘
>        ↓               ↓                ↓
>    起動ボタンを    時間/状態を      予定を見ながら
>    AIに押させる    AIに監視させる    AIが提案する
> ```

### 進行台本
- 「**3つは別物だけど、向かう先は同じ。"Cursor 開きっぱなし" を卒業します**」
- 「全部できなくてもOK。**今日のうちに『朝ニュース push』が iPhone に届く** がミニマムゴール」

---

## Part 2：Cursor で AI エージェントを自動実行する方法 (25分)

### 2.1 説明スライド (8分)

#### スライド 2-1: なぜ「Cursor 開きっぱなし」は限界なのか
> - 人間が操作しないと AI は動かない
> - 寝てる時 / 会議中 / 出張中 は AI が止まる
> - 「やる時間に思い出す」が必要 → 結局やらない

#### スライド 2-2: 自動実行の3レイヤー

> | レイヤー | 役割 | 例 |
> |---------|------|----|
> | ① Cursor Background Agent | Cursor 内で並列タスク実行 | 「コードレビュー」「リサーチ」を裏で走らせる |
> | ② claude / claude-code CLI | ターミナルから AI を呼ぶ | `claude -p "今日のニュース要約"` |
> | ③ ローカルスケジューラ | OS が時間で ② を起動 | cron / launchd / Windows タスクスケジューラ |

> **キモ**: ② を ③ で起動すると、**Cursor が開いてなくても定時に AI が動く**

#### スライド 2-3: 実装の最小構成図

> ```
> [launchd 7:00 trigger]
>         │
>         ▼
> [~/scripts/morning_news.sh]    ← シェルスクリプト1本
>         │
>         ▼
> [claude CLI]                    ← AI 呼び出し
>         │
>         ▼
> 出力ファイル / push通知 / メール  ← 結果の届け先
> ```

#### スライド 2-4: PONさん環境想定

> | 環境 | スケジューラ | コマンド呼出し |
> |------|-------------|---------------|
> | macOS (推奨) | launchd | `launchctl load ~/Library/LaunchAgents/...` |
> | macOS (シンプル) | cron | `crontab -e` |
> | Windows | タスクスケジューラ | `schtasks /create ...` or PowerAutomate |
> | iPhone 単体 | 不可 | (受信専用) |

### 2.2 デモ手順 (12分) — Mac/launchd で claude CLI を毎朝7時起動

#### Demo 2-A: claude CLI のインストール確認

```bash
# Cursor チャットで AI に確認させる
claude --version
# 入っていない場合は AI に「Mac に claude-code CLI を入れて」と依頼
# 公式: https://docs.claude.com/claude-code (npm / Homebrew のいずれか)
```

#### Demo 2-B: シェルスクリプトを AI に書かせる

Cursor チャット:

```
~/scripts/morning_news.sh を作ってください。

要件:
- 実行時刻に「今日のニュース要約」を生成
- claude CLI を使う (claude -p "..." で 1 ショット呼び出し)
- 出力は ~/Downloads/morning_news_$(date +%F).md に保存
- 標準出力には JSON で {date, summary} を出す (後で push に流用)
- ログは ~/Library/Logs/morning_news.log に追記
- chmod +x も実行
```

→ AI が以下のような中身を生成:

```bash
#!/usr/bin/env bash
set -euo pipefail

DATE=$(date +%F)
OUT=~/Downloads/morning_news_${DATE}.md
LOG=~/Library/Logs/morning_news.log

echo "[$(date)] start" >> "$LOG"

PROMPT="今日 ${DATE} の主要ニュース 5 本を、
1) 美容業界 2) タイ経済 3) 日本経済 4) AI 業界 5) その他
の順で 200 字以内ずつ要約してください。出力は Markdown で。"

claude -p "$PROMPT" > "$OUT" 2>>"$LOG"

echo "[$(date)] done -> $OUT" >> "$LOG"
echo "{\"date\":\"${DATE}\",\"file\":\"${OUT}\"}"
```

#### Demo 2-C: 試運転

```bash
chmod +x ~/scripts/morning_news.sh
~/scripts/morning_news.sh
# → ~/Downloads/morning_news_2026-04-27.md が生成されるか確認
# → ログ: tail -f ~/Library/Logs/morning_news.log
```

#### Demo 2-D: launchd で毎朝 7:00 に登録

Cursor チャット:

```
~/Library/LaunchAgents/com.pon.morning-news.plist を作ってください。

要件:
- ProgramArguments: ~/scripts/morning_news.sh
- StartCalendarInterval: 毎朝 07:00 (Hour=7, Minute=0)
- StandardOutPath / StandardErrorPath: ~/Library/Logs/morning_news.{out,err}.log
- RunAtLoad は false (load 直後に走らない)
```

→ AI 生成例:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.pon.morning-news</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>$HOME/scripts/morning_news.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>7</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key><string>/Users/USERNAME/Library/Logs/morning_news.out.log</string>
  <key>StandardErrorPath</key><string>/Users/USERNAME/Library/Logs/morning_news.err.log</string>
  <key>RunAtLoad</key><false/>
</dict>
</plist>
```

```bash
# 登録
launchctl load ~/Library/LaunchAgents/com.pon.morning-news.plist

# テスト発火 (7:00を待たない)
launchctl start com.pon.morning-news

# 状態確認
launchctl list | grep morning-news

# 停止 / 解除
launchctl unload ~/Library/LaunchAgents/com.pon.morning-news.plist
```

> ⚠️ launchd は **完全パスを要求** する (`~` 展開が効かないケースあり)。USERNAME 部分は AI に置換してもらう。

### 2.3 cron 版 (シンプル代替) — 補足5分

```bash
# crontab -e で以下追記
0 7 * * * /Users/USERNAME/scripts/morning_news.sh >> /Users/USERNAME/Library/Logs/morning_news.cron.log 2>&1
```

| 比較 | launchd | cron |
|------|---------|------|
| Mac 標準 | ◎ | ○ (互換) |
| スリープ復帰 | 起きた直後に追いかけて実行 | 起動中のみ実行 |
| 設定の難度 | やや高 (XML) | 低 |
| 田中推奨 | **launchd** (PONさん Mac は基本スリープなので) | デモ補足のみ |

### 2.4 想定質問 + 回答テンプレ

| Q | A |
|---|---|
| Cursor Background Agent と CLI どっち？ | **CLI を主軸**。Background Agent は Cursor 開いている時のみ。今日の目的（=Cursor閉じてても動かす）には CLI + スケジューラが必要 |
| シェルスクリプトを AI に書かせるには？ | Cursor チャットで「~/scripts/X.sh を作って。要件は…」と依頼するだけ。AI がファイル作成 + 権限付与まで実行 |
| Windows でも同じこと？ | はい。`claude.exe -p "..."` を `.bat` か PowerShell に書いて、タスクスケジューラから起動。PowerAutomate でも可 |
| 失敗ログはどこ？ | スクリプト側で `>>~/Library/Logs/X.log` を仕込む。launchd なら StandardErrorPath にも自動で出る |
| AI 呼び出しの API クレジットが心配 | claude CLI は Pro / Max 契約配下。1日数回なら気にならない。心配なら `--max-turns 1` などコスト制御 |
| 機密情報をプロンプトに入れたくない | スクリプトは外部 push しない設計にする (Part 3 で扱う ntfy も推測されにくいトピック名を使う) |

---

## Part 3：能動的自動実行 + ntfy.sh で朝ニュース push (25分)

### 3.1 説明スライド (8分)

#### スライド 3-1: 「結果が iPhone に届く」までやらないと使われない
> - Mac のファイルに出ても、PONさんは Mac を開かないと気づかない
> - **iPhone push が来る** = 自分の生活動線に乗る
> - メール / Slack / LINE もあるが、**ntfy.sh が最短で無料**

#### スライド 3-2: ntfy.sh とは (NTY.SH)

> - オープンソースの push 通知サービス。公式 URL: **https://ntfy.sh**
> - 田中さん発言の **「NTY.SH」** = ntfy.sh の表記揺れ。同じサービス
> - **トピック名 = URL** (例: `https://ntfy.sh/<topic_name>`)
> - HTTP POST するだけで、購読中の iPhone / Android / ブラウザに push が飛ぶ
> - 認証なしで使える代わりに、**トピック名がバレると誰でも push できる** → 推測されにくい乱数文字列を含めること

#### スライド 3-3: 朝ニュース push の構成図

> ```
> [launchd 07:00]
>      │
>      ▼
> [morning_news.sh]
>      │
>      ├─ ① claude CLI でニュース要約生成
>      │
>      └─ ② curl で ntfy.sh/<topic> へ POST
>                 │
>                 ▼
>          [iPhone ntfy アプリ] ← 購読中
>                 │
>                 ▼
>            push 通知が届く
> ```

#### スライド 3-4: ntfy.sh の主要パラメータ
> - `Title` ヘッダ: push のタイトル
> - `Priority` ヘッダ: 1=最低 〜 5=最高 (緊急のみ 5、ニュースは 3)
> - `Tags` ヘッダ: 絵文字コード (`newspaper`, `coffee`)
> - 本文: 通知本文 (UTF-8、改行可)
> - `Click` ヘッダ: タップで開く URL (生成 Markdown を Drive にアップして URL を渡せば飛べる)

### 3.2 ハンズオン手順 (15分)

#### Step 1: iPhone に ntfy アプリをインストール (PONさん作業 / 1分)

- App Store で `ntfy` (作者: Philipp Heckel) を検索 → インストール
- 通知許可を ON にする

#### Step 2: トピック名を決める (1分)

- 推測されにくい乱数を含む文字列にする
- 例: `pon-bkk-9k3xQ-morning`
  - `pon-bkk` … 識別子
  - `9k3xQ` … 短いランダム文字列 (この場で AI に5文字生成させる)
  - `morning` … 用途
- 公開トピックなので **このトピックには機密本文を流さない** ルールを徹底

#### Step 3: iPhone アプリでトピックを Subscribe (1分)

- ntfy アプリ → "+" ボタン → "Subscribe to topic" → `pon-bkk-9k3xQ-morning` を入力
- (任意) Server は `https://ntfy.sh` のままで OK

#### Step 4: Mac から疎通テスト (2分)

```bash
curl -d "テスト通知 from Mac" https://ntfy.sh/pon-bkk-9k3xQ-morning
```

→ 数秒以内に iPhone に push が届けば成功 ✅

#### Step 5: morning_news.sh を push 対応に拡張 (5分)

Cursor チャット:

```
~/scripts/morning_news.sh を編集して、ニュース要約を ntfy.sh に push してください。

要件:
- TOPIC=pon-bkk-9k3xQ-morning (環境変数 NTFY_TOPIC で上書き可能に)
- タイトル: "おはようございます (YYYY-MM-DD)"
- 本文: 要約の最初の 1500 文字 (push 上限考慮)
- Priority: 3, Tags: newspaper,coffee
- 失敗してもスクリプト全体は止めない (ログだけ残す)
```

→ AI 生成例 (差分):

```bash
TOPIC="${NTFY_TOPIC:-pon-bkk-9k3xQ-morning}"

# 既存処理で $OUT に Markdown が保存されている前提
BODY=$(head -c 1500 "$OUT")

curl -sS -X POST "https://ntfy.sh/${TOPIC}" \
  -H "Title: おはようございます (${DATE})" \
  -H "Priority: 3" \
  -H "Tags: newspaper,coffee" \
  -d "$BODY" >> "$LOG" 2>&1 || \
  echo "[$(date)] ntfy push failed" >> "$LOG"
```

#### Step 6: 手動で発火させて iPhone まで届くか確認 (2分)

```bash
~/scripts/morning_news.sh
# → iPhone に push が届く
```

#### Step 7: launchd で 07:00 自動起動を再ロード (1分)

```bash
launchctl unload ~/Library/LaunchAgents/com.pon.morning-news.plist
launchctl load   ~/Library/LaunchAgents/com.pon.morning-news.plist
```

→ 完成 🎉 翌朝 7:00 に push が届く

### 3.3 能動的自動実行のレシピ集

| ユースケース | トリガ | 実装スケッチ |
|------------|--------|------------|
| **朝ニュース push** (今日の主役) | launchd 07:00 | 上記 |
| **週次売上サマリ → メール下書き** | launchd 月曜 08:00 | claude で MD → mailto: link を ntfy へ → タップで Mail.app 開く |
| **競合美容室の価格監視** | launchd 22:00 | claude にURL一覧を読ませて変化検知 → 変化あれば push |
| **「会議終わりに録音まとめて」** | 任意ボタン (Apple Shortcuts → Mac へSSH) | iPhone から発火 → Mac の claude が要約 → ntfy で返す |
| **Gmail 受信トリガ** (発展) | Apps Script → webhook | Gmail でラベル付き → Apps Script → claude → ntfy |

### 3.4 安全運用ルール (重要)

> | ルール | 理由 |
> |-------|------|
> | トピック名にランダム文字列を必ず含める | 公開ノードなので推測攻撃される |
> | 機密情報は本文に書かない | 公開ノード経由で流れる |
> | ニュース要約・スケジュール程度に留める | 漏れても被害が小さい用途のみ |
> | 重要度高い用途はセルフホスト or Pro 版へ移行 | エンタープライズ向けは E2E 暗号化あり |

### 3.5 想定質問 + 回答テンプレ

| Q | A |
|---|---|
| ntfy.sh と NTY.SH は同じ？ | **同じ**。公式表記は ntfy.sh、田中さん表現の NTY.SH は同サービスの愛称的表記 |
| トピック名がバレたら？ | **誰でも push できる**。乱数を含めて推測困難に。心配なら定期ローテ |
| 月額いくら？ | **無料** (公開サーバー)。気になるならセルフホスト or Pro (月数ドル) |
| iPhone がスリープでも届く？ | 届く (APNS 経由で OS が起こす) |
| Slack や LINE には？ | 別ツール (Slack webhook / LINE Notify) 併用すれば可。今日はスコープ外 |
| 通知本文に画像は？ | 添付可 (Attach ヘッダで URL 渡し)。今日はテキストのみ |
| 朝に聞きたくない日は？ | iPhone 側で OS の集中モードで遮る or `launchctl unload` で停止 |

---

## Part 4：Google Calendar 連携 (20分)

### 4.1 説明スライド (6分)

#### スライド 4-1: 「いつやるか」を AI に持たせる
> - 予定が AI のコンテキストに入ると、**提案の質が変わる**
> - 例:
>   - 「来週水曜の打合せ前日に、議題から準備メモ作って」
>   - 「今日空いている2時間のうちに、X タスクを終わらせるプラン教えて」
> - PONさんの予定本体は **iCloud カレンダー**。これを Google に集約 or 並行運用するのが今日のテーマ

#### スライド 4-2: 接続方法 3案

> | 方式 | 仕組み | おすすめ | 備考 |
> |------|--------|:-------:|------|
> | **A. Google Calendar MCP** | Cursor から Google API 直叩き | ◎ | OAuth 一度設定すれば一気通貫 |
> | **B. Apps Script トリガ** | カレンダー側で AI 連携を発火 | ○ | 「予定追加→準備メモ生成」自動化向き / 発展 |
> | **C. Apple Calendar 経由** | iCloud に Google アカウント追加 / Cursor は Apple MCP | △ | Mac標準カレンダーから両方扱える |

> **今日のデモは A.Google Calendar MCP**

#### スライド 4-3: PONさん環境前提の選択フロー

> ```
> PONさんは現在 iCloud カレンダー利用中
>                 │
>         ┌───────┴────────┐
>         ▼                ▼
>    完全移行?         並行運用?
>    ・Google集約       ・Mac標準カレンダーで
>    ・iCloud廃止        両方追加 (両方表示)
>         │                │
>    今日試して判断    今日は Google MCP のみ設定し、
>                     iCloud カレンダーはそのまま温存
> ```

> 🔵 **田中の推奨**: **「今日は Google を増設・並行運用」**。完全移行はしない。1週間試してみて PONさんが判断。

### 4.2 ハンズオン手順 (12分) — A. Google Calendar MCP

#### Step 1: Google アカウント確認 (1分)

- PONさんに「Google アカウント (Gmail) ありますか？個人？Workspace？」を確認
- なければ個人 Gmail を作成 (5分かかる場合は Part 4 を後ろにずらす)

#### Step 2: Google Calendar MCP を Cursor に追加 (3分)

Cursor チャット:

```
Google Calendar を Cursor から扱いたいです。
Google Calendar MCP のセットアップを手伝ってください。

要件:
- ~/.cursor/mcp.json に追記
- 読み書き両方できる構成
- スター数が多い公式系のものを優先
- OAuth フローはブラウザで進める想定
```

→ AI が以下のような追記を生成 (実パッケージ名は当日 AI が確認):

```json
{
  "mcpServers": {
    "google-workspace": { "...既存..." },
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "~/.config/google-cal/credentials.json"
      }
    }
  }
}
```

> ⚠️ 当日: 田中側で **その時点で最新・スター多い** Google Calendar MCP を確認しておく。パッケージ名は将来変わる可能性。

#### Step 3: OAuth 認可 (3分)

- Google Cloud Console で OAuth クライアント作成 (もしくは MCP の wizard 任せ)
- ブラウザで Google ログイン → 権限許可 (カレンダー読み書き)
- credentials.json を `~/.config/google-cal/` に配置

> AI に「Google Calendar API を有効化して、OAuth クライアントを作って、credentials.json をどこに置くか教えて」と聞くと、コンソール手順を一通り出してくれる。

#### Step 4: Cursor 完全再起動 (1分)

#### Step 5: 読み込みデモ (2分)

```
今後7日間の Google Calendar 予定を一覧で見せてください。
日付・時間・タイトルだけで OK。
```

→ AI がカレンダーから読み出し → 表示

```
4/29 (水) の予定だけ詳細を見せてください。
```

→ 該当予定の詳細

#### Step 6: 書き込みデモ — 黄信号 (2分)

```
明日 (4/28) の 10:00 に、「PON 自習」というタイトルで
30 分の予定を入れてください。場所は不要。確認後、追加してください。
```

→ AI が確認を取って実行 → Google Calendar / Mac 標準カレンダー / iPhone カレンダーで確認

#### Step 7: 発展デモ (1分)

```
来週 (5/4-5/10) の打合せ予定を一覧して、
それぞれ前日の朝に「議題から準備メモ生成」を実行する仕組みのアイディアを 3 つ提案してください。
今日は実装しない。次回で着手する候補メモとして残してください。
```

→ AI が提案 → Flow/today/ にメモとして保存

### 4.3 iCloud 並行運用パターン (3分)

```
PONさん iPhone
   ├─ iCloud Calendar (個人/家族) ← そのまま温存
   └─ Google Calendar (仕事)     ← AI 連携の主戦場

Mac
   └─ macOS 標準カレンダーアプリ
        ├─ iCloud アカウント
        └─ Google アカウント (アカウント追加)
            → どちらの予定も1画面で表示
```

> AI 連携は **Google 側のみ**。
> iCloud 側は「AI に見せたくない予定 (家族・通院等)」のサンクチュアリ用途で残せる。

#### iCloud 完全移行する場合の手順 (今日はやらない、参考)
1. iCloud カレンダーをエクスポート (Mac標準カレンダーから .ics)
2. Google Calendar に .ics をインポート
3. iPhone の iCloud カレンダー同期を OFF
4. Google アカウントを iPhone に追加 → カレンダー同期 ON
5. 1〜2週間試行 → 問題なければ iCloud 側削除

### 4.4 想定質問 + 回答テンプレ

| Q | A |
|---|---|
| Google Calendar に切り替えると家族の予定も AI に見える？ | カレンダー単位で切り分け可能。共有カレンダーを Google から外せば AI からは見えない |
| iCloud 派の家族と予定共有が崩れる？ | iCloud / Google 双方向で招待は届く。完全移行しなくても問題なし |
| 認証が切れたら？ | Cursor 再起動で再認証。それでもダメなら `~/.cursor/mcp.json` の Google ブロック確認 |
| Apps Script は今日設定する？ | スコープ外。次回以降。今日は MCP 経由の読み書きまで |
| Google Workspace 契約してないけど大丈夫？ | 個人 Gmail でも Calendar API は使える。無料 |
| 仕事用 Google アカウントがある (会社支給)、個人と分けたい | MCP 設定を 2 つに分けて、用途で使い分け可。今日は個人 1 つでスタート推奨 |
| カレンダー名が日本語混じり (例: "🟢仕事") で動かない | UTF-8 で扱える。動かない場合は AI に「カレンダー ID で指定して」と依頼 |

---

## Part 5：まとめ・宿題・次回予告 (5分)

### スライド 5-1: 今日の3つの学び
> 1. **Cursor は CLI + スケジューラで「常駐 AI」になる** — Cursor を開いている時間だけが AI の稼働時間ではない
> 2. **能動的自動実行 + ntfy.sh で iPhone に push** — 結果が手元に届くまで設計するのがポイント
> 3. **Google Calendar MCP で時間軸が AI のコンテキストに入る** — 予定を見ながら準備メモを作れる

### スライド 5-2: 宿題
> 1. **朝ニュース push を3日連続受信** してみる (続くか / ノイズかを判断)
> 2. **能動的に AI に動かしたい時間/イベントを 3 つ書き出す** (週次売上 / 競合価格 / メール下書き 等)
> 3. **Google Calendar を1週間試用** → iCloud 完全移行 / 並行運用 / 戻す のどれにするか判断

### スライド 5-3: 第7回 (予告)
> | テーマ | 内容 |
> |--------|------|
> | 繰り返しタスクの設定 | 旧 v1 で予定していた「定型作業」を扱う。今日の宿題2を実装 |
> | 会話履歴インポート | ChatGPT 履歴を AIOS に取り込み、過去議論を AI から参照 (BL-0037 資産活用) |
> | (任意) Apps Script 連携 | 「予定追加 → 準備メモ生成」のイベントトリガを実装 |

### 進行台本 (田中向け)
- 「**今日できなかった所は次回頭で一緒にやる**」を必ず言う
- 「**3つのうち、明日朝に1つでも push が来れば今日は成功**」とハードルを下げて締める
- 「どれが一番響きました？」で PONさん側に発言させて終わる

---

## 補足資料 (PONさんへ配布する想定)

### A. ハンズオン用の URL / コマンド集

| 項目 | URL / コマンド |
|------|---------------|
| ntfy.sh 公式 | https://ntfy.sh |
| ntfy iPhone アプリ | App Store で「ntfy」検索 |
| Google Calendar MCP (要当日確認) | `npx -y @cocal/google-calendar-mcp` (※当日最新確認) |
| claude CLI 公式 | https://docs.claude.com/claude-code |
| launchd 設定 | `~/Library/LaunchAgents/com.pon.<task>.plist` |
| 疎通テスト | `curl -d "test" https://ntfy.sh/<topic>` |

### B. トピック名の決め方ガイド

> | パターン | 例 | 用途 |
> |---------|----|----|
> | 識別子 + 乱数 + 用途 | `pon-bkk-9k3xQ-morning` | 朝ニュース |
> | 識別子 + 乱数 + 用途 | `pon-bkk-x2pYm-alerts` | 重要アラート |
> | 識別子 + 乱数 + 用途 | `pon-bkk-h7jKn-weekly` | 週次レポート |

> 📌 ルール:
> - 推測されにくい乱数(5文字以上) を必ず含める
> - 機密本文は載せない (タイトルとサマリだけ)
> - バレたら別トピックに切替

### C. launchd トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 7:00 に動かない | スリープ中だった | launchd は復帰時に追いかけ実行する。15分以上ズレるなら StartCalendarInterval 確認 |
| `launchctl load` がエラー | plist の XML が壊れている | `plutil -lint plist パス` で検証 |
| 実行されたが結果が出ない | 環境変数 (PATH) が読めていない | スクリプト先頭で `export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH` |
| claude コマンドが見つからない | フルパスでないと動かない | `which claude` で確認 → スクリプトでフルパス指定 |
| `~` が展開されない | launchd は Shell 経由でないと展開しない | ProgramArguments を `/bin/bash -lc "..."` でラップ |

### D. ntfy push が届かない時のチェックリスト

1. iPhone で ntfy アプリの通知許可が ON か (設定→通知→ntfy)
2. iPhone がオフラインじゃないか
3. Topic 名のスペル / 大文字小文字の一致 (大小区別あり)
4. `curl -v` で HTTP 200 が返っているか
5. 集中モード / 機内モード / おやすみモード を確認
6. 何度も失敗するなら別トピック名でテスト

### E. Google Calendar MCP — OAuth 設定の最短手順

1. Google Cloud Console で新規プロジェクト作成 (PON-AI など)
2. APIs & Services → Calendar API を有効化
3. OAuth 同意画面 → 外部 → アプリ名 / メール 入力
4. 認証情報 → OAuth クライアント ID 作成 (Desktop app)
5. JSON ダウンロード → `~/.config/google-cal/credentials.json` に配置
6. 初回起動時にブラウザで認可 → トークンが保存されて以降は自動

> AI に「Google Cloud Console での Calendar API 有効化と OAuth クライアント作成手順を教えて」と聞けば、画面のキャプチャ付きで案内してくれる。

---

## メモ・未確定事項 (磨き込みフェーズで対応)

- [ ] PONさんの **OS 構成 (Mac / Windows / 併用)** を当日までに確認 → INBOX.md Q1
- [ ] PONさんが **ntfy アプリを iPhone に入れて良いか** (会社端末 MDM 制限の可能性) → INBOX.md Q2
- [ ] PONさんの **Google アカウント保有状況** (個人 / Workspace) → INBOX.md Q3
- [ ] **iCloud → Google 完全移行 / 並行運用** の意向 → INBOX.md Q4
- [ ] **claude-code CLI** の最終インストール方法 (npm / Homebrew / 公式) を当日までに確認・統一
- [ ] launchd plist のテンプレを `Stock/定型作業/` 配下に正本化するかは第7回で判断
- [ ] Google Calendar MCP の **正確なパッケージ名・最新バージョン** を当日までに確認
- [ ] 90 分版 / 120 分版 の切替判断は当日の進行で田中
- [ ] BL-0074 (売上データ AI アクセス) との時間配分 (両方を 1 セッションで扱うか別セッションか)
- [ ] 旧 v1 (定型タスク / Apple MCP / 履歴) の **第7〜8回への振り分け** は今回セッション後に決定
