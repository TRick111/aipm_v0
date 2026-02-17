# Albert - 計画・仕様書 v1

## 1. 概要

**Albert** は、Restaurant AI Lab メンバー3名（吉田・町田・田中）が内部で使うAIエージェント。
LINEグループに常駐し、日常的なAIチャットと業務支援機能を提供する。

## 2. プロジェクト情報

| 項目 | 内容 |
|---|---|
| プロジェクト名 | Albert |
| 所属プログラム | RestaurantAILab |
| 利用者 | 吉田・町田大地・田中利空（3名） |
| インターフェース | LINEグループ |
| ホスティング | Vercel |
| フレームワーク | Next.js (App Router) |

## 3. 機能一覧

### Phase 1（初期リリース）

| # | 機能 | 説明 | 優先度 |
|---|---|---|---|
| F1 | LLMチャット | LINEグループでAlbertに話しかけると、LLMが応答する | 必須 |
| F2 | 日程調整 | 3人のGoogleカレンダーを読み取り、全員が空いている時間帯を提案する | 必須 |

### 将来候補（Phase 2以降）

- タスク管理・リマインド
- 週報データの自動取得・サマリー
- クライアント情報の検索
- 議事録の要約

---

## 4. アーキテクチャ

```
┌─────────────┐     Webhook      ┌──────────────────────┐
│  LINE Group  │ ──────────────> │  Vercel (Next.js)    │
│  (3 members) │ <────────────── │                      │
└─────────────┘   Reply API      │  /api/webhook        │
                                 │    ├── Message Router │
                                 │    ├── LLM Chat      │──> Claude API
                                 │    └── Scheduler     │──> Google Calendar API
                                 └──────────────────────┘
```

### 4.1 処理フロー

1. メンバーがLINEグループでメッセージを送信
2. LINE Platform → Vercel `/api/webhook` にWebhookが飛ぶ
3. Message Router がメッセージ内容を解析:
   - **通常の会話** → Claude API に送信 → 応答をLINEに返す
   - **「日程調整」キーワード検出** → Scheduler モジュールが起動
4. Scheduler:
   - 3人のGoogleカレンダーからFreeBusy情報を取得
   - 共通の空き時間を算出
   - 候補日時をフォーマットしてLINEに返信

### 4.2 メッセージルーティング方式

LINEグループでのメンション or キーワードでAlbertを起動する:

| トリガー | 動作 |
|---|---|
| `@Albert` + 通常テキスト | LLMチャット応答 |
| `@Albert 日程調整` + 条件 | 日程調整機能を起動 |
| メンションなし | 無視（グループの会話を邪魔しない） |

---

## 5. 技術スタック

| レイヤー | 技術 | 備考 |
|---|---|---|
| フレームワーク | Next.js 15 (App Router) | API Routes で Webhook 受信 |
| デプロイ | Vercel | Hobby or Pro プラン |
| 言語 | TypeScript | |
| LLM | Anthropic Claude API (claude-sonnet-4-5-20250929) | コスト効率重視。必要に応じてモデル変更可 |
| メッセージング | LINE Messaging API | Bot + グループ参加 |
| カレンダー | Google Calendar API | サービスアカウント or OAuth 2.0 |
| DB（任意） | Vercel KV (Redis) | 会話履歴・セッション管理用。Phase 1では最小限 |
| 環境変数管理 | Vercel Environment Variables | シークレット管理 |

---

## 6. 機能詳細仕様

### 6.1 F1: LLMチャット

#### 概要
LINEグループで `@Albert` にメンションすると、Claude APIで応答を生成して返信する。

#### 仕様

| 項目 | 内容 |
|---|---|
| トリガー | LINEグループでのメンション (`@Albert`) |
| LLMモデル | Claude Sonnet 4.5 |
| システムプロンプト | Restaurant AI Labの内部AIアシスタントとして振る舞う |
| 会話コンテキスト | 直近N件のメッセージを保持（Phase 1: 10件程度） |
| 最大トークン | 1024 tokens（LINEの表示制約を考慮） |
| エラー時 | 「すみません、エラーが発生しました。もう一度お試しください。」と返信 |

#### LINE Bot 設定

- **Bot種別**: Messaging API チャネル
- **グループ参加**: 許可
- **Webhook URL**: `https://<app>.vercel.app/api/webhook`
- **応答モード**: Webhook のみ（自動応答OFF）

### 6.2 F2: 日程調整

#### 概要
3人のGoogleカレンダーを参照し、全員が空いているミーティング可能時間を提案する。

#### 仕様

| 項目 | 内容 |
|---|---|
| トリガー | `@Albert 日程調整` + オプションで条件指定 |
| 対象カレンダー | 吉田・町田・田中 の3名のGoogleカレンダー |
| 検索範囲 | デフォルト: 翌日〜7日間 |
| 検索時間帯 | デフォルト: 10:00〜19:00（指定可） |
| ミーティング時間 | デフォルト: 60分（30分/90分も指定可） |
| 除外 | 土日祝（デフォルト。含めることも可） |
| 最大候補数 | 5件 |

#### ユーザーインタラクション例

```
ユーザー: @Albert 日程調整 来週30分
Albert:
  来週（2/23〜2/27）で全員空いている30分の候補です:

  1. 2/23(月) 14:00〜14:30
  2. 2/24(火) 10:00〜10:30
  3. 2/24(火) 16:00〜16:30
  4. 2/26(木) 11:00〜11:30
  5. 2/27(金) 15:00〜15:30

  どの時間がよいですか？番号で選んでください。
```

```
ユーザー: @Albert 日程調整 今週 夕方以降
Albert:
  今週（2/17〜2/21）17:00以降で全員空いている60分の候補です:

  1. 2/18(火) 17:00〜18:00
  2. 2/20(木) 18:00〜19:00

  どの時間がよいですか？
```

#### Google Calendar API アクセス方式

**推奨: サービスアカウント方式**

| 方式 | メリット | デメリット |
|---|---|---|
| サービスアカウント | トークン更新不要、サーバー間通信向き | 各ユーザーがカレンダー共有設定必要 |
| OAuth 2.0 | ユーザー認可フローが標準的 | リフレッシュトークン管理が必要 |

**サービスアカウント方式の手順:**
1. GCPプロジェクトでサービスアカウントを作成
2. 各メンバーが自分のGoogleカレンダーの設定で、サービスアカウントのメールアドレスに「予定の表示（時間枠のみ）」権限を付与
3. サービスアカウントの鍵JSONをVercel環境変数に格納
4. FreeBusy API で空き情報のみ取得（予定の詳細は取得しない = プライバシー配慮）

#### 空き時間算出ロジック

```
入力:
  - 検索期間（開始日〜終了日）
  - 検索時間帯（開始時刻〜終了時刻）
  - ミーティング所要時間
  - 3名のカレンダーID

処理:
  1. Google Calendar FreeBusy API で3名の busy 時間を取得
  2. 検索期間内の各日について:
     a. 検索時間帯内で、3名とも busy でないスロットを抽出
     b. 連続する空き時間が所要時間以上のものを候補とする
  3. 候補を日時順にソートし、最大N件を返す

出力:
  - 候補日時リスト（開始〜終了）
```

---

## 7. プロジェクト構成（ディレクトリ）

```
albert/                        ← Next.js プロジェクトルート
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── webhook/
│   │   │       └── route.ts   ← LINE Webhook エンドポイント
│   │   └── page.tsx           ← 管理画面（将来用。最初は最小）
│   ├── lib/
│   │   ├── line/
│   │   │   ├── client.ts      ← LINE Messaging API クライアント
│   │   │   ├── parser.ts      ← メッセージ解析・ルーティング
│   │   │   └── types.ts       ← LINE 型定義
│   │   ├── llm/
│   │   │   ├── chat.ts        ← Claude API 呼び出し
│   │   │   └── prompts.ts     ← システムプロンプト定義
│   │   ├── calendar/
│   │   │   ├── client.ts      ← Google Calendar API クライアント
│   │   │   ├── freebusy.ts    ← FreeBusy 取得ロジック
│   │   │   └── scheduler.ts   ← 空き時間算出ロジック
│   │   └── config.ts          ← 環境変数・定数
│   └── types/
│       └── index.ts           ← 共通型定義
├── .env.local                 ← ローカル開発用環境変数
├── .env.example               ← 環境変数テンプレート
├── next.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## 8. 環境変数

| 変数名 | 説明 | 取得元 |
|---|---|---|
| `LINE_CHANNEL_SECRET` | LINEチャネルシークレット | LINE Developers Console |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEチャネルアクセストークン | LINE Developers Console |
| `ANTHROPIC_API_KEY` | Claude API キー | Anthropic Console |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | GCPサービスアカウント鍵(JSON, base64) | GCP Console |
| `CALENDAR_IDS` | 3名のカレンダーID（カンマ区切り） | 各自のGoogleカレンダー設定 |

---

## 9. セットアップ手順（初期構築）

### 9.1 外部サービス準備

1. **LINE Developers Console**
   - Messaging API チャネルを作成
   - チャネルシークレット・アクセストークンを取得
   - Webhook URL を設定（Vercelデプロイ後）
   - グループ参加を許可

2. **Google Cloud Platform**
   - プロジェクト作成
   - Google Calendar API を有効化
   - サービスアカウントを作成し、鍵JSONをダウンロード
   - 3名それぞれがカレンダー設定でサービスアカウントに共有

3. **Anthropic**
   - API キーを取得

4. **Vercel**
   - プロジェクトを作成
   - 環境変数を設定
   - GitHubリポジトリと連携（自動デプロイ）

### 9.2 開発環境

```bash
npx create-next-app@latest albert --typescript --app --tailwind
cd albert
npm install @line/bot-sdk @anthropic-ai/sdk googleapis
```

---

## 10. 開発ロードマップ

### Phase 1: MVP（目標: 2週間）

| # | タスク | 見積 |
|---|---|---|
| 1 | Next.js プロジェクト作成・Vercelデプロイ | 0.5日 |
| 2 | LINE Webhook 受信・応答の疎通 | 1日 |
| 3 | Claude API 連結・LLMチャット機能 | 1日 |
| 4 | Google Calendar API 連携・FreeBusy取得 | 1日 |
| 5 | 日程調整ロジック実装 | 1〜2日 |
| 6 | メッセージルーティング（チャット/日程調整の振り分け） | 0.5日 |
| 7 | テスト・デバッグ・調整 | 2〜3日 |

### Phase 2: 改善（Phase 1完了後）

- 会話履歴の永続化（Vercel KV）
- 日程調整の確定 → Googleカレンダーに予定作成
- Flex Message（リッチUI）対応
- エラーハンドリング強化

---

## 11. セキュリティ考慮

| 項目 | 対策 |
|---|---|
| LINE Webhook署名検証 | `x-line-signature` ヘッダーでリクエストの正当性を検証 |
| APIキー管理 | Vercel環境変数に格納。コードにハードコードしない |
| カレンダー情報 | FreeBusy（空き/埋まり）のみ取得。予定詳細は取得しない |
| アクセス制限 | LINEグループ内のみ。グループID/ユーザーIDでフィルタ可 |

---

## 12. 制約・前提条件

- Vercel Hobby プランの場合、Serverless Function の実行時間は最大60秒
- LINE Messaging API の応答は、Webhook受信から一定時間以内に返す必要あり（Reply APIは即時、Push APIは任意タイミング）
- Google Calendar FreeBusy API は1リクエストで複数カレンダーを照会可能
- 3名限定の内部ツールのため、スケーラビリティは当面不要
