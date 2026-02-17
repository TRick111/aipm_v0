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
| カレンダー | Google Calendar API | サービスアカウント方式 |
| DB | Vercel Postgres (Neon) | 会話履歴・ユーザー管理・日程調整ステート |
| ORM | Prisma (v7) | 型安全。Driver Adapter で Vercel Postgres 接続 |
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

## 7. データベース設計

### 7.1 概要

| 項目 | 内容 |
|---|---|
| DB | Vercel Postgres (Neon) |
| ORM | Drizzle ORM |
| マイグレーション | Drizzle Kit (`drizzle-kit push` / `drizzle-kit generate`) |

### 7.2 ER図

```
┌──────────┐     ┌──────────────┐     ┌─────────────────────┐
│  users   │────<│  messages    │     │ schedule_requests    │
└──────────┘     └──────────────┘     └─────────────────────┘
     │                                         │
     │           ┌──────────────────────┐      │
     └──────────<│ schedule_request_    │>─────┘
                 │ members             │
                 └──────────────────────┘
```

### 7.3 テーブル定義

#### users

メンバー情報。LINE UserID と Google カレンダーID の紐付けを管理。

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | `uuid` | PK, default gen | |
| `name` | `text` | NOT NULL | 表示名（吉田、町田、田中） |
| `line_user_id` | `text` | UNIQUE, NOT NULL | LINE の userId |
| `calendar_id` | `text` | | GoogleカレンダーID（メールアドレス） |
| `created_at` | `timestamptz` | NOT NULL, default now | |

#### messages

LLMに渡す会話コンテキスト用。グループ単位で直近N件を保持。

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | `uuid` | PK, default gen | |
| `group_id` | `text` | NOT NULL | LINE グループID |
| `user_id` | `uuid` | FK → users, NULL可 | 発言者（Albertの応答はNULL） |
| `role` | `text` | NOT NULL | `user` / `assistant` |
| `content` | `text` | NOT NULL | メッセージ本文 |
| `created_at` | `timestamptz` | NOT NULL, default now | |

- インデックス: `(group_id, created_at DESC)` → 直近N件取得用

#### schedule_requests

日程調整の「候補提示 → 選択 → 確定」のステート管理。

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | `uuid` | PK, default gen | |
| `group_id` | `text` | NOT NULL | LINE グループID |
| `requester_id` | `uuid` | FK → users, NOT NULL | 調整を依頼した人 |
| `status` | `text` | NOT NULL, default 'pending' | `pending` / `confirmed` / `cancelled` |
| `duration_minutes` | `integer` | NOT NULL, default 60 | ミーティング時間（30/60/90） |
| `date_from` | `date` | NOT NULL | 検索開始日 |
| `date_to` | `date` | NOT NULL | 検索終了日 |
| `time_from` | `time` | NOT NULL, default '10:00' | 検索開始時刻 |
| `time_to` | `time` | NOT NULL, default '19:00' | 検索終了時刻 |
| `candidates` | `jsonb` | | 算出された候補スロット配列 |
| `selected_slot` | `jsonb` | | 確定されたスロット |
| `created_at` | `timestamptz` | NOT NULL, default now | |

`candidates` の例:
```json
[
  {"start": "2026-02-23T14:00:00+09:00", "end": "2026-02-23T14:30:00+09:00"},
  {"start": "2026-02-24T10:00:00+09:00", "end": "2026-02-24T10:30:00+09:00"}
]
```

#### schedule_request_members

日程調整の対象メンバー（基本3人全員。将来2人だけの調整にも対応可）。

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `request_id` | `uuid` | FK → schedule_requests | |
| `user_id` | `uuid` | FK → users | |
| | | PK: `(request_id, user_id)` | 複合主キー |

### 7.4 Drizzle スキーマ（実装イメージ）

```typescript
// src/db/schema.ts
import { pgTable, uuid, text, timestamp, integer, time, date, jsonb, primaryKey } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  name: text("name").notNull(),
  lineUserId: text("line_user_id").notNull().unique(),
  calendarId: text("calendar_id"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const messages = pgTable("messages", {
  id: uuid("id").defaultRandom().primaryKey(),
  groupId: text("group_id").notNull(),
  userId: uuid("user_id").references(() => users.id),
  role: text("role").notNull(), // "user" | "assistant"
  content: text("content").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const scheduleRequests = pgTable("schedule_requests", {
  id: uuid("id").defaultRandom().primaryKey(),
  groupId: text("group_id").notNull(),
  requesterId: uuid("requester_id").references(() => users.id).notNull(),
  status: text("status").notNull().default("pending"),
  durationMinutes: integer("duration_minutes").notNull().default(60),
  dateFrom: date("date_from").notNull(),
  dateTo: date("date_to").notNull(),
  timeFrom: time("time_from").notNull().default("10:00"),
  timeTo: time("time_to").notNull().default("19:00"),
  candidates: jsonb("candidates"),
  selectedSlot: jsonb("selected_slot"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const scheduleRequestMembers = pgTable("schedule_request_members", {
  requestId: uuid("request_id").references(() => scheduleRequests.id).notNull(),
  userId: uuid("user_id").references(() => users.id).notNull(),
}, (table) => ({
  pk: primaryKey({ columns: [table.requestId, table.userId] }),
}));
```

---

## 8. プロジェクト構成（ディレクトリ）

```
albert/                        ← Next.js プロジェクトルート
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── webhook/
│   │   │       └── route.ts   ← LINE Webhook エンドポイント
│   │   └── page.tsx           ← 管理画面（将来用。最初は最小）
│   ├── db/
│   │   ├── schema.ts          ← Drizzle テーブル定義
│   │   ├── index.ts           ← DB接続・クライアント
│   │   └── queries.ts         ← 共通クエリ関数
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
├── drizzle/                   ← マイグレーションファイル（自動生成）
├── drizzle.config.ts          ← Drizzle Kit 設定
├── .env.local                 ← ローカル開発用環境変数
├── .env.example               ← 環境変数テンプレート
├── next.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## 9. 環境変数

| 変数名 | 説明 | 取得元 |
|---|---|---|
| `POSTGRES_URL` | Vercel Postgres 接続文字列 | Vercel Storage ダッシュボード |
| `LINE_CHANNEL_SECRET` | LINEチャネルシークレット | LINE Developers Console |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEチャネルアクセストークン | LINE Developers Console |
| `ANTHROPIC_API_KEY` | Claude API キー | Anthropic Console |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | GCPサービスアカウント鍵(JSON, base64) | GCP Console |

---

## 10. セットアップ手順（初期構築）

### 10.1 外部サービス準備

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
   - Vercel Storage → Postgres を追加（Neon）
   - 環境変数を設定（`POSTGRES_URL` は自動設定される）
   - GitHubリポジトリと連携（自動デプロイ）

### 10.2 開発環境

```bash
npx create-next-app@latest albert --typescript --app --tailwind
cd albert
npm install @line/bot-sdk @anthropic-ai/sdk googleapis
npm install drizzle-orm @vercel/postgres
npm install -D drizzle-kit
```

---

## 11. 開発ロードマップ

### Phase 1: MVP

| # | タスク |
|---|---|
| 1 | Next.js プロジェクト作成・Vercelデプロイ・Postgres接続 |
| 2 | DBスキーマ作成（Drizzle）・マイグレーション |
| 3 | LINE Webhook 受信・署名検証・応答の疎通 |
| 4 | Claude API 連結・LLMチャット機能・メッセージ履歴保存 |
| 5 | Google Calendar API 連携・FreeBusy取得 |
| 6 | 日程調整ロジック実装（候補提示・選択・確定） |
| 7 | メッセージルーティング（チャット/日程調整の振り分け） |
| 8 | テスト・デバッグ・調整 |

### Phase 2: 改善（Phase 1完了後）

- 日程調整の確定 → Googleカレンダーに予定作成
- Flex Message（リッチUI）対応
- エラーハンドリング強化

---

## 12. セキュリティ考慮

| 項目 | 対策 |
|---|---|
| LINE Webhook署名検証 | `x-line-signature` ヘッダーでリクエストの正当性を検証 |
| APIキー管理 | Vercel環境変数に格納。コードにハードコードしない |
| カレンダー情報 | FreeBusy（空き/埋まり）のみ取得。予定詳細は取得しない |
| アクセス制限 | LINEグループ内のみ。グループID/ユーザーIDでフィルタ可 |

---

## 13. 制約・前提条件

- Vercel Hobby プランの場合、Serverless Function の実行時間は最大60秒
- LINE Messaging API の応答は、Webhook受信から一定時間以内に返す必要あり（Reply APIは即時、Push APIは任意タイミング）
- Google Calendar FreeBusy API は1リクエストで複数カレンダーを照会可能
- 3名限定の内部ツールのため、スケーラビリティは当面不要
