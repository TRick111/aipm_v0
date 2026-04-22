# BL-0061「AIコア PL作成」 実装計画（v2.1 確定）

- 作成日: 2026-04-22
- 状態: **v2.1 確定（v2.0 の Notion DB 方針を維持、Slack 通知は削除）**
- 実装着手: ✅ **GO**（2026-04-22 14:30 田中さん承認、別エージェントで実装開始）
- 変更履歴:
  - v2.1 (2026-04-22): **Slack 通知を削除**（運用は Notion の Status プロパティで回す）
  - v2.0 (2026-04-22): DB を Neon Postgres から Notion に転換
  - v1.0 (2026-04-22): 初版（Next.js + Prisma + Neon）

---

## ⭐ 実装エージェントへの引き継ぎ事項（最初に読む）

このセクションは **本計画を引き継いで実装するエージェント** 向け。**他の章を読む前に、まずここを読むこと。**

### A. 作業ディレクトリ

- **新規作成**: `~/RestaurantAILab/ai-core-pl/`
  - Dashboard と **兄弟ディレクトリ** として並べる（`~/RestaurantAILab/Dashboard/` の隣）
  - 田中さんの 2026-04-22 14:30 指示に基づく
- **このリポ (aipm_v0) には実装コードを置かない**。aipm_v0 側は Stock メタ + Flow 作業ログのみ

### B. 参考リポ（規約 source of truth）

- `~/RestaurantAILab/Dashboard/` を参照して規約を踏襲
  - Next.js App Router の構成
  - TypeScript 設定
  - Tailwind / `tsconfig.json` / `next.config.js` の流儀
  - **Prisma / Neon 関連は本案では使わない**（流儀だけ参考、依存は入れない）
- ESLint / Prettier 設定は Dashboard と揃えるのが望ましい

### C. GitHub

- **新規リポ作成**: `RestaurantAILab/ai-core-pl`（github.com 上）
  - Visibility: Private（ダッシュボードと揃える）
  - main ブランチで `RestaurantAILab` org を選択
- ローカル `~/RestaurantAILab/ai-core-pl/` を `git init` → remote を貼る
- Dashboard が `dev` ブランチ運用なので、本リポも `main` + `dev` を分ける（PR ベースで進める）

### D. Vercel

- 既存ダッシュボードと **同じ Vercel team**（orgId: `team_SxSmIbPKgsqBRWJz5I9KL4tO`）
- 新規プロジェクトを作成、GitHub `RestaurantAILab/ai-core-pl` と連携
- 環境変数（v2.1: Slack 系は不要）:
  - `NOTION_TOKEN`
  - `NOTION_DB_CASES`
  - `NOTION_DB_REQUESTS`
  - （※ ダッシュボード用 DB クレデンシャルは流用不可。AI-Core 用 Notion を別に用意）

### E. 通知（v2.1 で削除済）

- **Slack Webhook は実装しない**。`@slack/*` パッケージも追加しない
- 新規提出は Notion `Status=未対応` で入る → 田中／町田さんが Notion 側で巡回
- 詳細は §6.6「未対応の捌き方」

### F. 起点 HTML

- `~/Downloads/AI秘書事業_事例集_v1.html`（町田第一さん作成）
- リポにコピーして固定化することを推奨（例: `references/ai-hisho-cases-v1.html`、`.gitignore` 対象外）
- HTML を **直接 git に入れる** か、**抽出後の `data/cases.json` のみ git に入れる** かは判断 OK（前者が再現性高い）

### G. 質問が発生したら

- **AI-Core 用の questions ファイルに集約**する: `Flow/202604/<その日>/AI-Core/questions_to_user_impl.md`（**aipm_v0 側に作る**）
- 加えて aipm_v0 側 INBOX に **🟡 セクションでサマリ追記**: `Flow/202604/2026-04-22/_orchestration/INBOX.md`
- 即時ブロックする質問は 🔴 に置く

### H. 進捗の記録先

- 実装中の作業ログ: `Flow/202604/<実装日>/AI-Core/impl_log.md` を毎日追記
- 完了時:
  - `Stock/RestaurantAILab/AI-Core/README.md` の「現在の状況」に **公開URL / GitHubリポURL** を追記
  - `Stock/RestaurantAILab/AI-Core/log.md` に変更記録
  - `Stock/定型作業/バックログ/Backlog.md` の BL-0061 を `done` に
  - INBOX.md の Q-impl を ✅ 完了セクションへ移動

### I. Phase 範囲

- **このタスクは Phase 1（MVP）まで**（§5 を参照、想定 1日 / 実働 6〜6.5h）
- Phase 2 候補（提案書 PDF / 認証 / 集計 / 通知復活）は別バックログ起票で対応

### J. 重要な前提（Backlog 干渉）

- **BL-0054（共用リポジトリ設計、doing）** が並行進行中。本リポは暫定で `RestaurantAILab/ai-core-pl` 個別リポとして立てる。BL-0054 確定後に rename / transfer で吸収可能な構造を保つ
- **BL-0064（Vercel アカウント整理）** は今回触らない（既存ダッシュボードと同 team に置くことで巻き込まれない）

---

---

## 0. ゴール

町田第一さんから受領した HTML（50事例 × 11カテゴリ）を **メニューカタログ** として、クライアントが Web 上でチェック→送信できる選択フォームをデプロイし、選択結果を **Notion DB** に保存して関係者に通知する。

完了条件:
- 公開 URL を開くと PL UI が表示される
- 50 事例のチェック → 送信ができる
- Notion「クライアント依頼」DB にレコードが追加され、関連する事例ページがリレーションで紐づく
- 新規提出は **Status = `未対応`** で入り、田中／町田さんが Notion を開いて確認する運用
- 運用は **Notion 上で完結**（事例追加・依頼閲覧・対応状況更新）。Web 側に admin 画面は持たず、**Slack 通知も使わない**

---

## 1. 確定事項（Q1〜Q3, Q-A〜Q-C）

| 項目 | 確定内容 |
|---|---|
| 起点 HTML | `~/Downloads/AI秘書事業_事例集_v1.html`（町田第一さん作成） |
| UI 方針 | HTML をそのまま土台にし、チェックボックス＋送信機能を後付け |
| GitHub | `RestaurantAILab` org に新規リポ `ai-core-pl` |
| Vercel | 既存ダッシュボードと **同 team**（orgId: `team_SxSmIbPKgsqBRWJz5I9KL4tO`） |
| **DB** | **Notion**（事例一覧 / クライアント依頼 の 2 DB。Postgres は使わない） |
| 価格 (Q-A) | 列だけ確保（`PriceJpy` Number, null可）。MVP は表示しない |
| 機能スコープ (Q-B) | F1〜F3 + F5（Admin = F6 は不要、Notion で代替）／**Slack 通知は削除**（v2.1） |
| Stock 登録 (Q-C) | **PONさん案件方式**: aipm_v0 側はタスク管理用 README/ProjectIndex/log のみ、実体は Markdowns-1（**本日 2026-04-22 完了済**） |

---

## 2. アーキテクチャ（v2.0）

```
[ Browser (Client = 飲食店 or B2B SaaS 経営者) ]
       │ HTTPS
       ▼
[ Vercel: Next.js 16 App Router (RestaurantAILab team / 新規 project) ]
   ├ /                 … PL UI（クライアント情報 + 50事例チェック + 送信）
   ├ /thanks           … 送信完了
   ├ /api/cases        … 事例マスタ取得 (GET)  ※ 当日キャッシュ可
   └ /api/submit       … 送信受付 (POST) → Notion 「クライアント依頼」DB に Insert（Status=未対応）
       │
       ▼
[ Notion ]
   ├ DB: 事例一覧 (ServiceCases)        … HTML から seed した 50 行
   └ DB: クライアント依頼 (ClientRequests) … 提出ごとに 1 行（Status=未対応）+ 選択事例への relation
```

**ポイント**:
- **Postgres / Prisma は使わない**（v1.0 から方針転換）
- **Slack 通知は使わない**（v2.1 で削除）。新規提出は Notion の `Status = 未対応` で入るので、田中／町田さんが定期的に Notion を開いて捌く運用
- **Admin UI は不要**：Notion を直接 Web/モバイルで開けば一覧・絞り込み・対応ステータス更新が可能
- Notion API クライアント: `@notionhq/client`（公式 JS SDK）

---

## 3. リポジトリ構成

```
ai-core-pl/
├── app/
│   ├── page.tsx                  # PL UI（HTML を React 化）
│   ├── thanks/page.tsx           # 送信完了
│   └── api/
│       ├── cases/route.ts        # GET 事例一覧（ローカル data/cases.json から返す）
│       └── submit/route.ts       # POST 送信 → Notion Insert（v2.1: Slack なし）
├── components/
│   ├── CaseCard.tsx              # 事例カード（チェックボックス付き）
│   ├── CategoryBlock.tsx         # カテゴリアコーディオン
│   ├── ClientForm.tsx            # クライアント情報入力
│   └── FilterBar.tsx             # role/tools/freq/difficulty/badge フィルタ
├── lib/
│   ├── notion.ts                 # Notion クライアント（singleton）+ ヘルパー
│   └── case-page-map.ts          # data-id → Notion page_id のマップ読み込み
├── data/
│   ├── cases.json                # HTML から抽出した 50 事例（フォーム描画用）
│   └── case-page-map.json        # data-id → Notion page_id（seed 後に出力）
├── scripts/
│   ├── extract-cases.mjs         # HTML パーサ（cheerio）→ cases.json
│   └── seed-notion.mjs           # cases.json → Notion 事例一覧 DB に作成 + map 出力
├── styles/
│   └── tokens.css                # Buddy Design Tokens を CSS 変数で移植
├── public/
├── .env.example
├── package.json
├── next.config.js
└── README.md
```

**主要 deps**: `next@16`, `react@19`, `typescript`, `@notionhq/client`, `cheerio`, `zod`, `tailwindcss`, `shadcn/ui`（任意）

> Slack 関連（`@slack/web-api`, `@slack/webhook`, 独自 `lib/notify.ts` 等）は **v2.1 で依存から削除**。使わない。

---

## 4. Notion DB スキーマ（2 つ）

### 4.1 事例一覧 DB（ServiceCases）

| プロパティ | 型 | 値の例 / 制約 |
|---|---|---|
| Title | Title | `case-title`（例: 「個人活動の可視化（ワーク・アナリティクス）」） |
| ID | Number | `data-id` (1..50)。**ユニーク** |
| Category | Select | A, B, C, D, E, F, G, H, I, J, K |
| Status | Select | `実装済み`, `応用提案` |
| Difficulty | Number | 1, 2, 3 |
| Roles | Multi-select | ceo, hr, sales, cs, backoffice |
| Tools | Multi-select | notion, slack, salesforce, gmail, sheets, recording, jira, ... |
| Frequency | Multi-select | morning, evening, night, weekly, ondemand, event |
| Pain | Rich text | 「こんな悩みに」原文 |
| WhatAIDoes | Rich text | 「AI 秘書がやること」原文 |
| DataFlow | Rich text | 「データの流れ」原文 |
| FrequencyLabel | Rich text | 「頻度・所要時間」原文（例: `毎日 / 完全自動`） |
| Effect | Rich text | 「効果（推定）」原文 |
| ToolsLabel | Rich text | 「使う道具」原文（例: `Slack × Notion × ブラウザ履歴`） |
| PriceJpy | Number | null可 / 将来用 |

### 4.2 クライアント依頼 DB（ClientRequests）

| プロパティ | 型 | 値の例 / 制約 |
|---|---|---|
| Title | Title | `<クライアント名> / <提出日時>` 自動組み立て |
| SubmittedAt | Date | 提出時刻 |
| ClientName | Rich text | 社名 / 店舗名 |
| Contact | Rich text | 連絡先（メール or 電話） |
| Segment | Select | restaurant, b2b_saas, other |
| Notes | Rich text | クライアントからの自由記述 |
| **SelectedCases** | **Relation** → 事例一覧 DB | 選択された事例への複数リレーション |
| Status | Select | 未対応, 対応中, 提案済み, 完了, クローズ |
| InternalNote | Rich text | 自社メモ（クライアント不可視） |

> Notion の Relation は many-to-many をネイティブ対応。Postgres 中間テーブルは不要。

---

## 5. 実装ステップ（Phase 1: MVP）

| # | タスク | 完了条件 | 想定時間 |
|---|---|---|---|
| P1-1 | GitHub `RestaurantAILab/ai-core-pl` 作成（main protected）+ Next.js 16 init | `npm run dev` でトップが表示 | 30m |
| P1-2 | Buddy Design Tokens を `styles/tokens.css` に移植（HTML の `:root {}` をコピー） | カラー/タイポ/角丸が同等で再現 | 20m |
| P1-3 | HTML → cases.json 抽出スクリプト（`scripts/extract-cases.mjs`、cheerio で `<article class="case">` を走査） | `data/cases.json` に 50 件出力 | 45m |
| P1-4 | Notion 側で 2 DB を手動作成（4.1 / 4.2 のスキーマで） + ワークスペース内 Integration を作成し、両 DB に Connect | DB の URL（≒ database_id）取得 | 30m |
| P1-5 | Notion seed スクリプト（`scripts/seed-notion.mjs`：cases.json を ServiceCases に Create、page_id を `data/case-page-map.json` に保存） | Notion 上に 50 ページ作成、map JSON 出力 | 45m |
| P1-6 | `/api/cases` GET 実装（`data/cases.json` を返すだけ。Notion 取得は不要） | JSON が返る | 15m |
| P1-7 | PL UI 実装 | ローカルで操作・送信できる | 2〜3h |
|       | ・ HTML の構造（topnav / hero / pains / panel / catalog）を踏襲 |  |  |
|       | ・ `<article class="case">` を React `<CaseCard>` 化、内部にチェックボックス |  |  |
|       | ・ 上部に `<ClientForm>`（社名 / 担当 / 連絡先 / セグメント / メモ） |  |  |
|       | ・ HTML の filter UI（role/tools/freq/difficulty/badge）を React で再実装 |  |  |
|       | ・ 「送信」ボタン → `/api/submit` POST |  |  |
| P1-8 | `/api/submit` POST 実装 | Notion 上に行が増え、`Status=未対応` で入っている | 1h |
|       | ・ Zod で入力検証（client + selectedIds[]） |  |  |
|       | ・ `case-page-map.json` で selectedIds → Notion page_id 変換 |  |  |
|       | ・ `notion.pages.create` で ClientRequests に Insert（properties + relation + Status=未対応） |  |  |
|       | ・ レスポンスで `/thanks` へリダイレクト（共有 URL は Phase 2 で検討） |  |  |
| P1-9 | Vercel 接続（同 team / 新規 project）+ env 注入（NOTION_TOKEN, NOTION_DB_REQUESTS, NOTION_DB_CASES）+ デプロイ | 公開 URL で動作確認 | 30m |
| P1-10 | 受け入れ確認（田中＋町田第一さん／町田大地さん）→ 関係者に URL 共有 | 共有 URL で実クライアントが触れる | — |

**目安: 1日（実働 6〜6.5h）** ※ v2.0 から 0.5h 短縮（Slack 削除分）

### Phase 2 候補（別タスク化）

- 提案書 PDF/Markdown 出力（Notion 依頼ページ → テンプレに流し込み）
- 認証（Magic Link / Clerk）— クライアント入力リンクをトークン化
- 集計（カテゴリ別月削減 h 試算）を送信完了画面に表示
- HTML v2 が来た時の差分 upsert スクリプト
- `PriceJpy` の活用（Q-A の (b)/(c) 確定後）

---

## 6. Notion 連携の実装メモ

### 6.1 認証
- Notion ワークスペースで Internal Integration を作成 → Token 取得
- 対象 DB ページの「・・・ → コネクションを追加」で Integration を Connect
- 環境変数: `NOTION_TOKEN`, `NOTION_DB_CASES`, `NOTION_DB_REQUESTS`（**Slack 系の env は不要**）

### 6.2 SDK
- `npm i @notionhq/client`
- `const notion = new Client({ auth: process.env.NOTION_TOKEN })`

### 6.3 Insert 例（クライアント依頼）

```ts
await notion.pages.create({
  parent: { database_id: process.env.NOTION_DB_REQUESTS! },
  properties: {
    Title:        { title: [{ text: { content: `${client.name} / ${nowJst()}` } }] },
    SubmittedAt:  { date: { start: new Date().toISOString() } },
    ClientName:   { rich_text: [{ text: { content: client.name } }] },
    Contact:      { rich_text: [{ text: { content: client.contact ?? '' } }] },
    Segment:      { select: { name: client.segment ?? 'other' } },
    Notes:        { rich_text: [{ text: { content: client.notes ?? '' } }] },
    SelectedCases:{ relation: selectedIds.map(id => ({ id: caseMap[id] })) },
    Status:       { select: { name: '未対応' } },   // v2.1: 新規提出は必ず「未対応」で入る
  },
});
```

### 6.6 未対応の捌き方（Slack 通知の代替）

- 田中／町田さんは、**Notion 側で「クライアント依頼」DB を `Status=未対応` でフィルタしたビュー**を用意しておく
- モバイル Notion アプリからも開ける
- 捌いたら `Status` を `対応中 / 提案済み / 完了 / クローズ` に更新
- 頻度の推奨: 1 日 1 回（朝）、または案件期待数が増えたら Notion の Reminder / Automation で自動通知（将来拡張）

### 6.4 シードのべき等性
- `seed-notion.mjs` は ID プロパティでクエリ → 既存ページがあれば update、無ければ create（upsert）
- HTML が改版された場合も再実行で差分反映できる

### 6.5 レート制限
- Notion API は 3 req/sec 程度を目安に。50 件 seed なら 1 リクエスト/200ms 程度で十分余裕

---

## 7. リスク & 暫定方針

| リスク | 対策 |
|---|---|
| Notion API のレート制限 | seed は 200ms 間隔でスロットル。POST /api/submit は単発なので問題なし |
| Notion DB スキーマ変更時に SDK 側のプロパティ名がズレる | DB 名・プロパティ名を `lib/notion.ts` の定数に集約。変更は1ファイル |
| Integration token の流出 | Vercel env のみに保存、`.env.example` には変数名のみ |
| 「価格」決定が後ろ倒し | DBに `PriceJpy` 列だけ確保。UI 表示は後から有効化 |
| BL-0054 共用リポ設計と衝突 | リポは個別にスタートし、決定後 transfer / rename |
| BL-0064 Vercel 整理と衝突 | 既存ダッシュボードと同 team に置くため巻き込まれない |
| 文言（B2B SaaS vs 飲食店）のズレ | UI は HTML 文言ベース。クライアント側の `Segment` で記録、Phase 2 で文言切替検討 |
| HTML の v2 が来る | extract-cases / seed-notion を冪等化、`data-id` を主キー固定で upsert |

---

## 8. AIOS 反映状況（本日 2026-04-22 完了分）

- ✅ `Stock/RestaurantAILab/AI-Core/` 新設（README / ProjectIndex.yaml / log.md）
- ✅ `Stock/MasterIndex.yaml` の RestaurantAILab program に AI-Core プロジェクトを追加
- ✅ `Stock/定型作業/バックログ/Backlog.md` BL-0061 Notes を更新
- ⏳ 実装完了時:
  - PL の公開 URL とリポ URL を `Stock/RestaurantAILab/AI-Core/README.md`「現在の状況」に追記
  - `log.md` に変更記録
  - BL-0061 を `done` に更新

> 成果物本体（事例コンテンツ等）は `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/` 側で保守。aipm_v0 側はタスク管理メタ情報のみ（PONさん案件と同じ運用）。

---

## 9. 残課題（実装中に並行確認）

- (Q-A 派生) 50 事例の **仮単価** を Notion 上で町田第一さん／町田大地さんが追記する運用にするかどうか
- 文言ローカライズ（B2B SaaS → 飲食店向け）が必要なら、別 PR で対応
- 通知を将来復活させる場合の選択肢（Notion Automation / LINE Bot 経由 / Email）

---

## 10. 参照ファイル

- HTML: `~/Downloads/AI秘書事業_事例集_v1.html`
- 探索メモ: `Flow/202604/2026-04-22/AI-Core/discovery_notes.md`
- 残質問: `Flow/202604/2026-04-22/AI-Core/questions_to_user.md`
- Stock: `Stock/RestaurantAILab/AI-Core/`（README / ProjectIndex / log）
- 既存ダッシュボード規約参照元: `~/RestaurantAILab/Dashboard/`（Vercel team / GitHub org / Next.js）
- AIOS テンプレ: `.cursor/rules/aios/templates/{README,ProjectIndex,log}.template.*`
