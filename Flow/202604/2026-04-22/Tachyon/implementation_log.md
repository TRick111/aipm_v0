# BL-0062 低速タキオン 実装ログ

- 作成日: 2026-04-22
- 実装者: エージェント
- 計画書: `implementation_plan.md` v1.1
- 実装場所: `~/tachyon-workspace/tachyon/`（AIPMリポの外、独立repo）
- 作業ディレクトリ（実行時）: `~/tachyon-workspace/projects/slow-exec-{todoId}/`

---

## 2026-04-22 実装開始

### 前提確認
- 既存Tachyonは `main` ブランチで `feat: Slack連携…` commit `78c2718` が最新。
- `.env` に `NOTION_TOKEN` / `NOTION_DB_ToDos` が登録済み（田中さん側で準備完了）
- `@anthropic-ai/claude-agent-sdk@^0.2.75` + `@anthropic-ai/sdk@^0.85.0` インストール済み
- 既存 data/meetings/ 配下に43会議ぶんのlive.md/meta.jsonがあり、E2Eテストに使える
- 既存リポには commit 前の未ステージ変更が多数あり。 低速タキオンの Phase ごとに **別コミット** として積み、既存リアルタイム版（todos.json）には触れない方針。

---

## コミット一覧（Tachyon repo / main ブランチ）

| SHA | Phase | メッセージ要約 |
|---|---|---|
| `7e1f284` | P1 | データモデル — SlowTodoItem型 + slow-todos.ts CRUD |
| `c1f362e` | P2 | 生成エンジン — Anthropic SDK single-turn で SlowTodoItem[] を抽出 |
| `277e474` | P3 | 自動生成フック + 手動再生成API |
| `12d50c4` | P5+P6 | UI SlowTodosPanel + /api/slow-todos/[todoId] + Notion連携 |
| `7b94871` | P7+P7.5 | Agent SDK 実行エンジン + 破壊的コマンドブロック |
| `7de1f13` | P4 | テキストアップロード → 新規会議として取込 |
| `e4da199` | fix | Notion DB プロパティ名を実DB（日本語）に合わせる |
| `c548019` | P9 | E2E スモークスクリプト |

合計 **8 commits**、新規 10 ファイル、変更 3 ファイル。

---

## 新規・変更ファイル

### 新規 (10)
- `types/meeting.ts` (拡張)
- `lib/slow-todos.ts` — slow-todos.json CRUD
- `lib/slow-agent.ts` — 生成コア
- `lib/slow-executor.ts` — 実行コア
- `lib/agent-launcher.ts` — Agent SDK 起動ラッパー（hook含む）
- `lib/exec-logger.ts` — 実行ログ書出し
- `lib/notion-client.ts` — Notion REST API 薄ラッパー
- `components/SlowTodosPanel.tsx` — UI
- `app/api/slow-todos/route.ts` — 一覧GET
- `app/api/slow-todos/generate/route.ts` — 生成トリガー
- `app/api/slow-todos/[todoId]/route.ts` — approve/edit/skip
- `app/api/slow-todos/execute/route.ts` — 実行トリガー
- `app/api/slow-todos/exec-log/route.ts` — 実行ログ参照
- `app/api/slow-todos/import/route.ts` — テキストアップロード
- `scripts/smoke-slow-agent.mjs` — E2E スモーク

### 変更 (3)
- `app/api/close/route.ts` — close時に生成フック追加
- `app/meetings/[id]/page.tsx` — SlowTodosPanel を埋込
- `components/Dashboard.tsx` — 「+ 議事録アップロード」ボタン追加

---

## E2E 動作確認結果

| 会議 | サイズ | 経路 | 結果 |
|---|---|---|---|
| `148239f0b4edfa1c` | 13KB | 既存会議の再生成API | 5 ToDo / 60s・Notion投入成功 (page `34abf91a-5716-8196`) |
| `20e17f4280d55744` | 22KB | smoke-slow-agent.mjs (SDK直叩き) | 5 ToDo / 86s |
| `4ac948550b3e7839` | 新規アップロード | /api/slow-todos/import | 3 ToDo / 15s |
| `4ac948550b3e7839` email draft | 実行経路 | /api/slow-todos/execute | 20s完了、`email_draft.md` 生成、Notion 同期成功 (page `34abf91a-5716-8156`) |
| `4ac948550b3e7839` log append | 実行経路 | /api/slow-todos/execute | 33s完了、cwd外 (Stock/) 書込をエージェント自己判断で拒否 |
| `8629e769a031ab02` sudo rm -rf | 破壊的ToDoテスト | /api/slow-todos/execute | エージェントが実行前に拒否、pre-tool-use hook正規表現も単体検証済 |

- リアルタイム版 `todos.json` には一切触れず、共存確認済み
- `next build` passes（全23ルート、6つが新規 slow-todos 配下）

---

## DoD チェック（計画書§8）

| 項目 | 結果 |
|---|---|
| 会議close時に自動で `slow-todos.json` が生成される | ✅ `/api/close` フック経由 |
| 5分以内にToDo一覧がUIに出る（30分以内会議で計測） | ✅ 13KB/60s, 22KB/86s（Sonnet 4.6） |
| テキストアップロードから新規会議作成→ToDo生成まで動く | ✅ 15sで完了（Dashboardの「議事録アップロード」ボタン） |
| UIで承認/編集/スキップ/実行すべてのアクションが動作 | ✅ SlowTodosPanel / `/api/slow-todos/[todoId]` / `/execute` |
| 承認時にNotion DBに該当ToDoが追加される | ✅ 実DB `Tachyon ToDos` に pageId 付与 |
| 実行時に結果がTachyonとNotion両方に書き込まれる | ✅ `slow-todos.json` + `syncSlowTodoResultToNotion` |
| 実行失敗時にUIにエラーが表示され、再実行ボタンから復旧できる | ✅ `errorMessage` + [再実行] ボタン |
| リアルタイム版（既存 `todos.json`）の挙動が壊れていない | ✅ 別ファイル・別APIで分離 |
| 実会議データ3件以上での動作確認完了 | ✅ 3会議（うち1件は新規アップロード）+ 破壊的テスト1件 |

全項目 ✅。

---

## 実装時間（総計）

- 開始: 2026-04-22 頃（本セッション内で完結）
- P1〜P10 合計: 約 **2〜3 時間**（type check / build / smoke / E2E すべて含む）

計画書見積（17〜20h）より大幅に短縮。要因:
- 既存 `lib/meetings.ts` / `lib/todos.ts` / `lib/proposal-agent.ts` のパターンが完成度高く、流用できた
- Notion SDK を導入せず REST で済ませたため、npm install や env 追加が不要だった
- `@anthropic-ai/claude-agent-sdk` の `query()` が docstring 通りに動き、hook 実装も1回で動作
- 実DBのプロパティ名ミスマッチは E2E で即座に検出・即修正（e4da199）

---

## 既知の残課題 / Phase2 候補

| 項目 | 優先度 | 備考 |
|---|---|---|
| Notion AI Meeting Notes 直接取込 | 中 | Q2-rev=(a) の Phase2。APIアクセス方法を調査要 |
| confidence ベース自動承認 | 低 | Q6-rev=C への進化。Phase1は全件UI承認で運用 |
| 複数ToDo並列実行 | 低 | 現状は同一会議内直列・グローバル2件まで。CPU/API負荷検証後に引き上げ |
| MCP 追加（Figma/Canva/Playwright/Vercel 等） | 中 | allowedTools に `mcp__...` を追加すれば動く。現状は Notion/Drive MCP も未設定 |
| 超長会議（120k文字超）の分割圧縮 | 低 | 現状は末尾優先 truncate。全30分会議は問題なし、1時間超会議が出たら対応 |
| Tachyon URL が https://localhost:3000 固定 | 小 | `TACHYON_BASE_URL` env で上書き可。リモート公開時に見直し |
| exec-log のローテーション/TTL | 小 | 30日後自動削除（cron）は Phase2 で |
| proposal-agent.ts （リアルタイム）との完全互換性 | 確認済 | todos.json と slow-todos.json は完全別管理 |

---

## 運用メモ

- Notion DB 実名は **`Tachyon ToDos`** (DB ID: `f4955bf10715433ab5b528176a33a0f6`)。プロパティは **日本語** (`タイトル` / `詳細` / `完了条件` / `関連プロジェクト` / `AI作業内容` / `AI作業の完了条件` / `Status` / `会議ID` / `会議タイトル` / `会議日時` / `元発言` / `発言タイムスタンプ` / `Confidence` / `実行結果` / `結果完了日時` / `Tachyon URL`)
- `関連プロジェクト` select は新しいプロジェクト名を渡すと自動で options に追加される（Notion の標準動作）
- 生成モデル切替: `SLOW_TACHYON_MODEL` 環境変数で上書き可（デフォルト `claude-sonnet-4-5-20250929`）
- Tachyon URL 切替: `TACHYON_BASE_URL` 環境変数で上書き可（デフォルト `https://localhost:3000`）

