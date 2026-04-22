# AI-Core PL 実装ログ（BL-0061）

- 作成日: 2026-04-22
- 実装者: エージェント（田中さん 14:30 着手GO）
- 計画書: `implementation_plan.md` v2.1
- 作業ディレクトリ: `~/RestaurantAILab/ai-core-pl/`

---

## 2026-04-22

### ✅ P1-1 リポ作成 + Next.js 16 init

- `~/RestaurantAILab/ai-core-pl/` 新設
- Stack 決定: Next.js 16.2.4 (App Router) + React 19 + TypeScript 5.9 + Tailwind v4 + `@notionhq/client`
- Dashboard の `tsconfig.json` / ESLint 方針に揃えた
- 初期 `package.json` は `next@16.0.0` だったが、CVE-2025-66478 のため `^16.2.4` に上げた
- `references/ai-hisho-cases-v1.html` に 2026-04-22 11:08 版をコピー（再現性確保）
- 配置:
  - `app/`（page / thanks / api/cases / api/submit）
  - `components/`, `lib/`, `data/`, `scripts/`, `styles/`, `references/`
  - `README.md`, `.gitignore`, `.env.example`

### ✅ P1-2 Design Tokens 移植

- `styles/tokens.css` に HTML の `:root {}` をそのままコピー（変更なし）
- `app/globals.css` にグローバル CSS（topnav / hero / section / filter / case card / form / submit bar / thanks / footer）を移植
- Tailwind v4 は `postcss.config.mjs` で `@tailwindcss/postcss` を有効化（一応導入・実際のスタイリングはトークン駆動のクラスベースで進める）

### ✅ P1-3 HTML → cases.json 抽出

- `scripts/extract-cases.mjs` を作成（cheerio で `<article class="case">` を走査）
- `data/cases.json` に 50 件を出力
- カテゴリ内訳: A=5, B=6, C=5, D=5, E=5, F=4, G=5, H=4, I=4, J=3, K=4（計画書通り）
- 抽出フィールド: id / category / categoryName / title / status (実装済み/応用提案) / difficulty / roles / tools / frequency / pain / whatAiDoes / dataFlow / frequencyLabel / effect / toolsLabel / priceJpy(null)

### ✅ P1-4 Notion DB 作成依頼を INBOX へ

- 田中さん手順（Integration 作成 → DB 2つ作成 → Connect → token/ID 回収）を具体化して INBOX の🟡セクションに追加
- 計画書 §4 のスキーマを引用し、Status 「未対応」だけ先に作る運用指示も添えた

### ✅ P1-5 seed-notion.mjs 作成

- `scripts/seed-notion.mjs`: `@notionhq/client` で `data/cases.json` を ServiceCases DB に upsert。`data/case-page-map.json` を出力
- べき等（ID で検索 → 既存なら update、無ければ create）
- 200ms スロットルで Notion レート制限を回避
- `.env.local` の手動パーサ内蔵（dotenv 依存なし）
- 実行は NOTION_TOKEN 受領後（INBOX 回答待ち）

### ✅ P1-6 /api/cases

- `app/api/cases/route.ts`: `revalidate=3600` の Node ランタイム。`data/cases.json` を直接返す
- ローカルで `{ ok: true, count: 50, cases: [...] }` 確認済

### ✅ P1-7 PL UI 実装

- `lib/types.ts` / `lib/cases.ts`（カテゴリメタ）/ `lib/notion.ts`（server-only）/ `lib/case-page-map.ts`
- `components/PLApp.tsx`（メイン client component） + `CaseCard` / `CategoryBlock` / `ClientForm` / `FilterBar`
- HTML の構造（topnav / hero / client form / filter-box / cat-block / submit-bar）を踏襲
- フィルタ: 役割 / ツール / 頻度 / 難易度
- カテゴリ A だけ `defaultOpen`、他はクリックで展開
- チェックで `selected` Set を更新、submit-bar に選択数を表示
- ローカル動作確認（`http://127.0.0.1:3100/`）: 50 case rendered, 11 category, 1 open に一致、チェックで count 更新

### ✅ P1-8 /api/submit

- `app/api/submit/route.ts`: zod で検証（client 3 必須 + selectedIds[1..50]）
- page-map 経由で `selectedIds → Notion page_id` を relation に変換（map 無い場合は relation なしで Insert）
- Notion Insert に **`Status: { select: { name: "未対応" } }`** を明示（v2.1）
- エラー形式: `{ ok: false, error: string, details?: unknown }` で統一
- バリデーション: 空 payload で 400 / 有効 payload で 500 `NOTION_TOKEN is not set`（期待動作）を確認

### ✅ P1-9 GitHub + Vercel デプロイ

- `git init -b main` → 1 コミット目（29 files, 12400+ insertions）
- GitHub: `gh repo create RestaurantAILab/ai-core-pl --private --source . --push` で push
- Vercel: `vercel link --yes --project ai-core-pl --scope restaurant-ai-lab` → GitHub 連携自動
- `vercel deploy`（production） → `https://ai-core-pl.vercel.app/` に ready
- 動作確認:
  - ✅ `GET /` → `<title>AI秘書 導入事例集 — 提供メニュー選択フォーム</title>`
  - ✅ `GET /api/cases` → 50件 JSON
  - ⚠️ `POST /api/submit` → `NOTION_TOKEN is not set`（env 未投入のため期待通り）
- スクリーンショット: `/private/tmp/ai-core-pl/{hero,client,catalog}.png`

### ✅ P1-10 AIOS 反映

- `Stock/RestaurantAILab/AI-Core/README.md`: 公開URL / GitHub URL / 進捗ステータス追記
- `Stock/RestaurantAILab/AI-Core/log.md`: 変更履歴追記
- INBOX: 状況を 🔄 に更新し、Notion 接続のみ残っていることを明記

---

## Phase 1 完了度

**コード＆デプロイは 100% 完了**。残は Notion 接続（田中さんの手動作業 15〜20 分）のみ。

| # | タスク | 状態 |
|---|---|---|
| P1-1 | リポ init + Next.js | ✅ |
| P1-2 | tokens.css 移植 | ✅ |
| P1-3 | HTML → cases.json 抽出 | ✅ |
| P1-4 | Notion DB 作成依頼（INBOX） | ✅（田中さん作業待ち） |
| P1-5 | seed-notion.mjs | ✅（実行は token 受領後） |
| P1-6 | /api/cases | ✅ |
| P1-7 | PL UI | ✅ |
| P1-8 | /api/submit | ✅（Notion 接続後に完全機能） |
| P1-9 | GitHub + Vercel | ✅ |
| P1-10 | AIOS 反映 | ✅ |

## 残作業（田中さん Q-notion-db 回答後・エージェント実施）

1. `.env.local` / Vercel env に `NOTION_TOKEN` / `NOTION_DB_CASES` / `NOTION_DB_REQUESTS` を投入
2. `npm run seed`（50件を ServiceCases に upsert、`data/case-page-map.json` を生成）
3. map をコミット → push → Vercel 自動再デプロイ
4. 本番で `/api/submit` をテスト（Notion に行が増えることを確認）
5. Backlog BL-0061 を `done` に、INBOX を ✅ 完了セクションへ移動

---

## 2026-04-22 PM2: 田中さんから .env 受領 → Phase 1 完全完了 🎉

### ✅ Notion seed 実行
- `.env` を `.env.local` にコピー → `npm run seed`
- 50 事例すべて create（updated=0, created=50）
- `data/case-page-map.json` 生成（52行 / 50 ID → page_id）

### ✅ Vercel env 投入
- `vercel env add NOTION_TOKEN production --sensitive`
- `vercel env add NOTION_DB_CASES production`
- `vercel env add NOTION_DB_REQUESTS production`
- 全て `Encrypted` で保存確認

### ⚠️ → ✅ 本番 deploy: Vercel committer policy で 30 分ハマり

**症状**: 新規 push / `vercel deploy --prod` がすべて **0 ms で deploy_failed**。 build container すら立ち上がらない。  
**原因**: Vercel API v13 の `readyStateReason` を直接読んで判明 →
> "The Deployment was blocked because GitHub could not associate the committer with a GitHub user."

`git commit` の committer email が `setup@restaurantailab.core-driven.com` で、これが GitHub の RestaurantAILab user に紐づいていなかった（noreply 形式でも公開メールでもなかった）。  
最初の MVP デプロイは `vercel deploy` の **CLI ローカルアップロード** だったため git committer 検証を経ず成功していた。GitHub integration が一度動き出してから検証が掛かるようになった。

**解決**:
1. `git config user.email` を `197918871+RestaurantAILab@users.noreply.github.com`（RestaurantAILab user の GitHub noreply 形式）に変更
2. `GIT_COMMITTER_EMAIL` env を明示して `git commit --amend --reset-author --allow-empty`
3. `git push --force-with-lease` で再 push
4. 自動デプロイがビルド開始（commit `af777a644...`） → Ready (16秒)

**今後の予防**: 当 repo に `.gitconfig` 同等を設定するか、AI-CoreプロジェクトのDevDocs に「committer email は GitHub noreply を使うこと」と明記。

### ✅ 本番 E2E 動作確認
- `POST https://ai-core-pl.vercel.app/api/submit` → Notion に Insert 成功
- 検証ペイロード: 5 事例選択（#1, #12, #22, #36, #45）
- Notion 側で確認:
  - Title: `【本番テスト2/最終】田中エージェント Phase1完了確認 / 2026-04-22 15:22`
  - Status: **未対応** ✅
  - Segment: b2b_saas
  - SelectedCases (relation): **5 件** すべてリンク済 ✅

### ✅ AIOS 反映
- INBOX `BL-0061` を ✅ 完了セクションに移動
- 完了サマリ + Vercel committer policy の知見も併せて記録
- README / log は前段で更新済み

---

## ✅ Phase 1 最終成果物

| 項目 | 内容 |
|---|---|
| 公開URL | https://ai-core-pl.vercel.app/ |
| GitHub | https://github.com/RestaurantAILab/ai-core-pl (private) |
| Vercel | `restaurant-ai-lab/ai-core-pl`（既存ダッシュボードと同 team） |
| Notion DBs | ServiceCases（50件 seed 済）/ ClientRequests |
| 確認済 | UI / 50事例カタログ / フィルタ / 選択 / 送信 / Notion Insert / Status=未対応 / Relations |
| 残スコープ | Phase 2 候補（PDF出力 / 認証 / 集計 / 通知復活 / HTML v2 差分）は別バックログ |

