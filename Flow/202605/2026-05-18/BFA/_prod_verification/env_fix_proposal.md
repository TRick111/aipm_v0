# `.env.production` 修正提案

## 問題

`scripts/upload-monthly-report.mjs --env prod` 実行時、HTTP API 経由（API_BASE が指す URL）で書き込みが行われる設計だが、現状の `.env.production` の `API_BASE` が **`http://localhost:3001`** を指しており、ローカル起動した `pnpm dev:prod`（prod DB 接続のローカル Next.js）に POST されるはずが、実際には開発側サーバー（dev DB 接続）が誤って起動した状態だと dev DB に書き込まれてしまう事故が起きた。

実際、本タスク冒頭の Phase 0 で「過去のサブA/B/C/Dがアップロードした 4 ヶ月分の月報は **prod DB ではなく dev DB（ep-fancy-fog）に書き込まれていた**」ことが判明している。

## 提案する修正

`.env.production` の `API_BASE` を以下のいずれかにする：

### 案 1（推奨）: prod DB 直接書き込みスクリプトを使う運用に切り替え、API_BASE を廃止

- `upload-monthly-report.mjs` を **deprecate** し、本タスクで新規追加した `scripts/upload-monthly-report-prod-direct.mjs` を正規ツールにする
- prod DB 書き込みは Prisma + `@vercel/blob` 直 → ローカル開発サーバーの起動有無に依存しない
- `.env.production` から `API_BASE` を削除（または `# DEPRECATED` でコメントアウト）

### 案 2: API_BASE を Vercel の prod URL に変更し、Vercel 認証を付ける

- 例: `API_BASE=https://restaurant-ai-lab.vercel.app`
- ただし「Vercel本番URLはチーム認証で保護されているため、直接アクセス不可」とのことなので、認証用 Bearer トークン or Cookie の追加注入が必要
- 実装コスト：高

### 案 3: API_BASE をそのまま `http://localhost:3001` に残す（現状維持）+ 安全ガード追加

- 代わりに `upload-monthly-report.mjs` の冒頭で「`pnpm dev:prod` が起動していること & DATABASE_URL が prod を向いていること」をヘルスチェックする処理を追加
- 例: `/api/health` を作って `connected_db_host` を返し、`ep-rough-bird` 以外なら abort
- 実装コスト：中

## 推奨

**案 1**を推奨。

理由：
- 本タスクでデバッグ済みの `upload-monthly-report-prod-direct.mjs` が動作確認済み
- HTTP 経由よりも直接 Prisma + Blob のほうが副作用が少なく、ローカルサーバーが何を向いているかの問題が起きない
- 既存の `upload-monthly-report.mjs` は dev DB アップロード用として残す（`--env dev` のみで使用）

## 具体的なファイル修正案（案 1 採用時）

`/Users/rikutanaka/RestaurantAILab/Dashboard/.env.production`:

```diff
- # API base URL for CLI scripts (--env prod)
- # ローカルサーバーを本番DB接続で起動して使う（pnpm dev:prod → port 3001）
- API_BASE=http://localhost:3001
+ # NOTE (2026-05-18): API 経由の prod アップロードは廃止。
+ # prod DB への書き込みは `scripts/upload-monthly-report-prod-direct.mjs` を使うこと。
+ # 本ファイルの API_BASE は dev サーバーを誤って向く事故があったため削除済み。
+ # dev DB への書き込みは .env.local / .env.development で別管理。
```

`/Users/rikutanaka/RestaurantAILab/Dashboard/CLAUDE.md`:

```diff
- **本番DBへのスクリプト実行ルール**:
- - HTTP APIスクリプト（`--env prod`）は、必ず **ローカルサーバー経由** で実行すること
- - `pnpm dev:prod` で本番DB接続のサーバーを port 3001 に起動 → スクリプトを `--env prod` で実行
- - Vercel本番URLはチーム認証で保護されているため、直接アクセス不可
- - 詳細: `docs/02_operations/ローカル本番環境の実行方法.md`
+ **本番DBへのスクリプト実行ルール**:
+ - 月報アップロードは `scripts/upload-monthly-report-prod-direct.mjs` を使う（API 経由しない直接書き込み）
+ - 直接書き込み版は `.env.production` から DATABASE_URL と BLOB_READ_WRITE_TOKEN を読み、prod DB に Prisma 経由で INSERT
+ - 旧 `upload-monthly-report.mjs --env prod` 経由は dev DB 行きの事故があったため使用禁止
```

## ユーザー判断

本提案はコード変更を伴うため、本タスクのスコープ外。マスター判断で別チケット化して実施を推奨。
