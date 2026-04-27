# 第6回セッション 章立て (outline) — ドラフト v2

作成日: 2026-04-27
担当: 田中利空 (AI ドラフト by claude)
対象: 近藤Ponさん (Rio's Innovation)
セッション本番: 2026-04-27 (月)
所要: 90〜120分目安
BL: BL-0073

> **v2 改訂点 (2026-04-27)**: 田中さん指示により、講義テーマ3本柱を全面差し替え。旧 v1 (繰り返しタスク／iCloudカレンダー連携／会話履歴インポート) を破棄せず、本文献として残しつつ、新スコープへ書き換える。

---

## v1 → v2 差分サマリ

| 項目 | v1 (旧) | v2 (新) |
|------|---------|---------|
| Part 2 | 繰り返しタスクの設定 (Stock/定型作業/) | **Cursor で AI エージェントを自動実行する方法** (cursor agent + シェル / cron / launchd) |
| Part 3 | iCloud カレンダー連携 (Apple MCP) | **AI エージェントの能動的自動実行** (cron / interval / 自動トリガ + ntfy.sh による iPhone push) |
| Part 4 | 会話履歴のインポート (BL-0037 資産活用) | **Google Calendar 連携** (Google MCP / Apps Script / iCloud→Google 移行 or 並行) |
| デモの主役 | Apple MCP / pon-chatgpt-knowledge | **ntfy.sh の朝ニュース push** + **Google Calendar MCP** |

> 旧 v1 の中身 (定型タスク・Apple MCP・履歴インポート) は **将来の第7〜8回** で扱うため、ここでは温存。今回は「**AI を能動的に動かす**」を主軸とする。

---

## 講義テーマ (新3本柱)

1. **Cursor で AI エージェントを自動実行する方法**
   - Cursor の Background Agent / CLI モード を使い、人手を介さず AI に作業させる
   - シェルスクリプト + ローカルスケジューラ (cron / launchd / Windows タスクスケジューラ) で定時起動
2. **AI エージェントの能動的自動実行**
   - 朝ニュースを毎朝自動で iPhone に push (ntfy.sh / 別名 NTY.SH)
   - 価格監視 / 定例レポート / メール下書き生成 など能動的トリガの使いどころ
3. **Google Calendar 連携**
   - Google スキル / Google Calendar MCP 経由でカレンダーを **読む / 書く**
   - PONさんの iCloud → Google 並行運用 or 移行パターンを検討
   - Apps Script で「予定が入ったら AI が準備メモを生成」など発展パターン

> 共通テーマ: **「Cursor を開いていない時間も AI が働く状態」** を作る。前回までの「依頼ベース」から「**能動的トリガベース**」へジャンプアップする回。

---

## 本日のゴール

> **講義が終わった時点で、以下の状態になっている：**
> 1. PONさんの Mac で **「朝7時に AI が今日のニュース要約を生成 → iPhone に push 通知」** が実際に動いている
> 2. cron / launchd で AI エージェントを定時起動する手順を、PONさんが自分で再設定できる
> 3. Google Calendar を **AI から読み書きできる** (Google MCP 設定済み)
> 4. iCloud カレンダー → Google Calendar の併用パターン or 移行可否の判断材料が手元にある
> 5. 「能動的自動実行」のユースケース3つ以上を PONさんが自分で言語化できている

---

## 全体タイムライン (90分版 / カッコ内は120分版)

| 時間 | Part | 内容 |
|:----:|------|------|
| 5分 (10分) | 0 | 前回の振り返り + 今回スコープ変更の説明 |
| 5分 (10分) | 1 | 今日やることの全体像 (Before/After) |
| 25分 (35分) | 2 | **Cursor で AI を自動実行する** (説明 → デモ → ハンズオン) |
| 25分 (30分) | 3 | **能動的自動実行 + ntfy.sh で朝ニュース push** (実装 → iPhone 通知確認) |
| 20分 (25分) | 4 | **Google Calendar 連携** (Google MCP → 読み → 書き → iCloud 並行) |
| 5分 (5分) | 5 | まとめ・宿題・次回予告 |
| 5分 (5分) | Q&A | 想定外の質問対応 |

---

## Part 0 — 前回の振り返り + スコープ変更の説明 (5分)

- 第5回 (MCP活用) 以降の運用状況の確認
- 信号機ルール (🟢🟡🔴) は維持できているか
- **スコープ変更の説明**: 「もともと定型タスク／iCloudカレンダー／履歴を予定していたが、田中側で『AI を能動的に動かす方が PONさんの日常インパクトが大きい』と判断し、今日は能動実行＋Google Calendar に切替」
- 旧テーマは第7〜8回で扱う旨を伝える (置いていかれ感を消す)

---

## Part 1 — 今日やることの全体像 (5分)

### Before / After

```
【Before】                                  【After】
AIに毎回「ニュース要約して」と依頼           毎朝7時に勝手に要約が iPhone に届く
カレンダー予定はiPhoneで開いて確認           AIに「来週の予定教えて」で済む / Googleで一元管理
Cursorを開いている時間しかAIが動かない       Cursorを閉じていてもAIが定時に動く
```

### 3本柱の関係図

```
┌──────────────────────────────────────────────┐
│  AIを「待機」から「能動」に変える             │
├──────────────┬──────────────┬─────────────────┤
│ Cursor自動実行│ 能動トリガ    │ Google Cal連携 │
│ (起動の自動化)│ (時間/イベント)│ (時間軸の参照) │
└──────────────┴──────────────┴─────────────────┘
       ↓               ↓                ↓
   起動ボタンを    時間/状態を      予定を見ながら
   AIに押させる    AIに監視させる    AIが提案する
```

---

## Part 2 — Cursor で AI エージェントを自動実行する方法 (25分)

### 2.1 何が解けるか
- Cursor を開く・閉じる人間操作を **挟まずに** AI に作業させる
- 朝起きる前 / 寝ている間 / 会議中 でも AI が動いている状態をつくる

### 2.2 自動実行の3レイヤー

| レイヤー | 役割 | 例 |
|---------|------|----|
| ① Cursor Background Agent | Cursor 内で並列タスク実行 | 「コードレビュー」「リサーチ」を裏で走らせる |
| ② Cursor CLI / claude-code CLI | ターミナルから AI を呼ぶ | `claude -p "今日のニュース要約"` |
| ③ ローカルスケジューラ | OS が時間で ② を起動 | cron / launchd / Windows タスクスケジューラ |

> **キモ**: ② を ③ で起動すると「Cursor が開いてなくても定時に AI が動く」が実現する。

### 2.3 PONさん環境想定

- macOS: **launchd** (推奨) or **cron**
- Windows: **タスクスケジューラ** + **PowerAutomate**
- iPhone 単体での自動実行は不可 → push 受信専用にする

### 2.4 デモ手順 (Mac/launchd で claude-code CLI を毎朝7時起動)

1. `claude-code` (もしくは `claude` CLI) のインストール確認
2. シェルスクリプト `~/scripts/morning_news.sh` を作成
3. launchd plist (`~/Library/LaunchAgents/com.pon.morning-news.plist`) を作成
4. `launchctl load` で登録
5. 翌朝動作確認 (またはテスト実行)

### 2.5 想定質問 (Part 2)
- Q. Cursor Background Agent と CLI どっちを使えばいい？
- Q. シェルスクリプトの中身を AI に書かせるには？
- Q. Windows でも同じことできる？
- Q. 失敗ログはどこに出る？

---

## Part 3 — 能動的自動実行 + ntfy.sh で朝ニュース push (25分)

### 3.1 何が解けるか
- 「AI が結果を出してくれても **iPhone に届かなければ意味がない**」を解決
- ntfy.sh (別名 **NTY.SH**) を使い、無料・登録不要で iPhone push が打てる

### 3.2 ntfy.sh とは
- オープンソースの push 通知サービス (https://ntfy.sh)
- **トピック名 = URL** で、トピック宛にHTTP POSTすると、購読中の iPhone に push が飛ぶ
- 認証なしで使える (推測されにくいトピック名で運用)
- iPhone アプリ "ntfy" を入れて、自分のトピックを購読するだけ

### 3.3 朝ニュース push の最短経路 (構成図)

```
[launchd 7:00 trigger]
        │
        ▼
[~/scripts/morning_news.sh]
        │
        ├─ ① claude CLI で今日のニュース要約を生成
        │
        └─ ② curl で ntfy.sh/<topic> に POST
                       │
                       ▼
              [iPhone ntfy アプリ] ← 購読中
                       │
                       ▼
                push 通知が届く
```

### 3.4 ハンズオン手順
1. iPhone に **ntfy** アプリをインストール (App Store)
2. PONさん専用トピック名を決める (例: `pon-bkk-9k3xQ-morning`) — 推測されにくい乱数文字列を含める
3. iPhone アプリで該当トピックを Subscribe
4. Mac で `curl -d "テスト" https://ntfy.sh/pon-bkk-9k3xQ-morning` を実行 → iPhone に届くか確認
5. `morning_news.sh` 内で claude 出力を ntfy へ POST する形に拡張
6. launchd で 07:00 に登録

### 3.5 能動的自動実行のユースケース

| ユースケース | トリガ | 実装難度 |
|------------|--------|---------|
| 朝ニュース push (本日デモ) | 時間 (毎日 7:00) | ★ |
| 週次売上サマリ → メール下書き | 時間 (毎週月曜 8:00) | ★★ |
| 価格監視 (競合美容室メニュー価格) | 時間 (毎日 22:00) | ★★ |
| Gmail 受信 → AI 自動仕分け | イベント (Gmail webhook) | ★★★ |
| カレンダー新規予定 → AI が準備メモ生成 | イベント (Apps Script) | ★★★ |

### 3.6 想定質問 (Part 3)
- Q. ntfy.sh と NTY.SH は同じもの？ → **同じ**。表記揺れに注意。公式は ntfy.sh
- Q. トピック名がバレたら誰でも push できるのでは？ → **そう**。推測されにくい文字列にすること。秘密情報は本文に直接書かない
- Q. 月額いくら？ → 無料 (公開サーバー利用時)。気になるならセルフホスト or Pro 版あり
- Q. iPhone がスリープでも届く？ → 届く (APNS 経由)
- Q. Slack や LINE には飛ばせる？ → 別ツール (Slack webhook, LINE Notify) を併用すれば可

---

## Part 4 — Google Calendar 連携 (20分)

### 4.1 何が解けるか
- 「来週の予定教えて」「来週水曜の打合せ前に準備メモ作って」を AI に頼めるようにする
- iCloud → Google Calendar への移行 or 並行運用の判断材料を作る

### 4.2 接続方法 3案

| 方式 | 仕組み | おすすめ度 | 備考 |
|------|--------|:---------:|------|
| **A. Google Calendar MCP** (推奨) | Cursor から Google API 直叩き | ◎ | OAuth 一度設定すれば一気通貫 |
| **B. Apps Script トリガ** | カレンダー側で AI 連携を発火 | ○ | 「予定追加 → 準備メモ生成」自動化向き |
| **C. Apple Calendar 経由** | iCloud 連携先に Google Cal を追加 | △ | Mac標準カレンダーから両方扱える / Cursorからは Apple MCP 経由 |

> 今日のデモは **A. Google Calendar MCP** で進める。

### 4.3 PONさん環境前提の選択フロー

```
PONさんは現在 iCloud カレンダー利用中
                │
        ┌───────┴────────┐
        ▼                ▼
   完全移行?         並行運用?
   ・Google集約       ・Mac標準カレンダーで
   ・iCloud廃止        両方追加 (両方表示)
        │                │
   今日試して判断    今日は Google MCP のみ設定し、
                    iCloud カレンダーはそのまま温存
```

> 当日は **「Google MCP を設定 → 試す → 良ければ家族予定など段階的に Google へ移す」** を提案。

### 4.4 ハンズオン手順 (A. Google Calendar MCP)

1. Cursor チャット: 「Google Calendar を Cursor から扱いたい。MCP の設定を手伝って」
2. AI が `~/.cursor/mcp.json` に Google Calendar MCP を追記
3. OAuth 認可フロー (ブラウザで Google ログイン → 権限許可)
4. Cursor 再起動
5. **読み込みデモ**: 「来週の予定を一覧して」
6. **書き込みデモ (黄信号)**: 「明日 10:00 に『PON自習』を 30 分入れて」
7. **発展デモ**: 「来週水曜の打合せ前日に、議題から準備メモを生成して Stock/定型作業/打合せ準備/ に保存」

### 4.5 iCloud 並行運用パターン (5分)

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

> AI 連携は **Google 側のみ**。iCloud 側は「AI に見せたくない予定 (家族・通院等)」のサンクチュアリ用途で残せる。

### 4.6 想定質問 (Part 4)
- Q. Google Calendar に切り替えると、家族の予定も AI に見える？ → **見せる範囲はカレンダー単位で選べる**。共有カレンダーを Google から外せばOK
- Q. iCloud 派の家族と予定共有が崩れる？ → 招待自体は iCloud / Google 双方向で送れる。完全移行しなくても問題なし
- Q. 認証が切れたらどうする？ → Cursor 再起動で再認証画面が出る。それでもダメなら `~/.cursor/mcp.json` の Google ブロック確認
- Q. Apps Script は今日設定する？ → スコープ外。次回以降。今日は MCP 経由の読み書きまで

---

## Part 5 — まとめ・宿題・次回予告 (5分)

### 今日の3つの学び
1. **Cursor は CLI + スケジューラで「常駐 AI」になる** — Cursor を開いている時間だけが AI の稼働時間ではない
2. **能動的自動実行 + ntfy.sh で iPhone に push** — 結果が手元に届くまで設計するのがポイント
3. **Google Calendar MCP で時間軸が AI のコンテキストに入る** — 予定を見ながら準備メモを作れる

### 宿題
1. 朝ニュース push を **3日連続で受信** してみる (続くか・ノイズかを判断する材料)
2. 自分の業務で「能動的に AI に動いてほしい時間/イベント」を **3つ書き出す**
3. Google Calendar を **1週間試用** し、iCloud 完全移行 / 並行運用 / 戻す のどれにするか判断する

### 次回予告 (第7回 — 仮)
- 旧 v1 で予定していた **繰り返しタスク (定型作業)** を扱う
- 第6回宿題で出た「能動的に動かしたい業務3つ」を実装
- ChatGPT 履歴インポート (BL-0037 の `pon-chatgpt-knowledge` 資産活用)

---

## 当日の準備物チェック

- [ ] PONさん: Mac (Cursor 最新), iPhone (ntfy アプリ事前 DL 推奨)
- [ ] PONさん: Google アカウント (Workspace or 個人) のログイン済み
- [ ] PONさん: iPhone でアプリインストール許可 (ntfy)
- [ ] 田中: claude CLI 動作確認済みの環境を持参 (デモ機用)
- [ ] 田中: launchd plist のサンプルテンプレを Flow 配下に用意
- [ ] 田中: ntfy.sh トピック名のサンプル (推測されにくいランダム文字列パターン)
- [ ] 田中: Google Calendar MCP の最新パッケージ名・OAuth 設定手順を当日までに確認

---

## メモ・未確定事項 (磨き込みフェーズで対応)

- [ ] PONさんの **OS 構成** (Mac のみ / Windows 併用) を当日までに確認 → INBOX.md Q1 で確認
- [ ] PONさんが **ntfy アプリを iPhone に入れて良いか** (会社支給端末の場合 MDM 制限あり) → INBOX.md Q2 で確認
- [ ] PONさんが **Google アカウントを既に持っているか** / Workspace 契約か個人 Google か → INBOX.md Q3 で確認
- [ ] iCloud → Google **完全移行希望か / 並行運用維持か** の意向 → INBOX.md Q4 で確認
- [ ] **claude-code CLI のインストール方法** を PONさん環境想定で当日までに整理 (npm? Homebrew? 公式インストーラ?)
- [ ] launchd / cron どちらをデフォ提示するか (macOS 推奨は launchd だが学習コストは cron の方が低い)
- [ ] 旧 v1 の 3 テーマ (定型作業/Apple MCP/履歴) を **第7〜8回** にどう振り分けるか、当日の進行を見て田中が判断
