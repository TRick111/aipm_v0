# BL-0062 低速タキオン — Implementation Plan v1.1

最終更新: 2026-04-22 17:15 / **status: 🔵 計画 v1.1 確定（実装フェーズ起動待ち）**

## 変更履歴
- **v1.1 (2026-04-22 17:15)**: Q10=B / Q11=A 回答反映 → v1.1 確定。allowedTools=中（fs+web+Bash+Notion MCP+Drive MCP）、承認モード=bypassPermissions 全自動
- v1.1-draft (2026-04-22 17:00): Q8-a を (2) SDK直接 → ハイブリッド（生成=SDK / 実行=Claude Code CLI相当 Agent SDK + Tool Use）に変更。工数 +2〜3h
- v1.0 (2026-04-22 16:05): Q1〜Q9 全回答反映、初期確定版

## 0. エグゼクティブサマリ

- **目的**: 会議終了後に全トランスクリプトを解析して構造化ToDoを生成し、UIでレビュー→承認→AI実行→結果保存までを一気通貫で実現
- **実装場所**: 既存Tachyon（`~/tachyon-workspace/tachyon/`）に機能追加（別リポ作らない）
- **差別化**: リアルタイム版（部分発言反応・全文脈未読）との棲み分け。低速版は全文読み切り＆承認ワークフロー付き
- **実行エンジン**: ToDo **生成**は Anthropic SDK 直接（高速）、ToDo **実行**は **Claude Code CLI 相当**（`@anthropic-ai/claude-agent-sdk` を `bypassPermissions` で起動）でMCP/bash/fs/各種CLIツール利用可
- **総工数見積**: **約17〜20h（Phase1 のみ、v1.1）** / Phase2 (Notion AI直接連携) は別送り
- **前提**: Notion DB・Integration の準備は別途必要（Q-notion-db に準ずる既存フロー流用）

## 1. 確定要件（Q1〜Q9 回答ベース）

| 項目 | 決定 | 出典 |
|---|---|---|
| 遅延許容 | 会議終了後 **5分以内** にToDo一覧 | Q1 |
| 入力ソース (Phase1) | `live.md`（Tachyon録音） + **テキストアップロード（.md/.txt）** のみ | Q9-a=(1), Q2-rev=(a) |
| 入力ソース (Phase2) | Notion AI Meeting Notes 連携 | Q2-rev=(a) |
| 起動トリガー | 会議close時の自動起動 + 手動再実行ボタン | Q1, Q4 |
| アップロードUI | **新規「会議」として作成**（source=upload、closedで即作成） | Q9-b=(1) |
| 実装場所 | 既存Tachyonリポ | Q5 |
| ToDoスキーマ | **title / 詳細 / 完了条件 / 関連プロジェクト / AI作業内容 / AI作業の完了条件** | Q7 |
| レビューフロー | **案B: Tachyon UI事前レビュー** — ドラフト表示→承認/編集/スキップ/実行→承認でNotion投入 | Q6-rev=B |
| 実行エンジン | **ハイブリッド**: 生成=Anthropic SDK直接 / 実行=**Claude Code CLI相当（`@anthropic-ai/claude-agent-sdk` + bypassPermissions）** | Q8-a=(2)→(1')（v1.1で変更） |
| 結果保存先 | **Tachyon内 + Notion 両方**（AIPM Flow配下には保存しない） | Q8-b=(3) |
| 失敗時挙動 | UIにエラー表示 + 手動再実行（自動リトライなし） | Q8-c=(1) |
| Notion URL取込 | Phase1では実装しない（Notion側エクスポートMarkdownを通常アップロードで投入） | Q9-c=(1) |

## 2. スコープ境界

### Phase1 に含む
- 会議close時の自動ToDo生成 + 手動再実行
- テキスト（.md/.txt）アップロード → 新規会議として受付 → 通常フローで生成
- Tachyon UIでのドラフト表示（承認/編集/スキップ/実行ボタン）
- **AI実行（Claude Code CLI相当、ツール権限あり）** — Notion更新 / Google Sheets書込 / ファイル生成 / MCP連携 / bash実行 など、tool allowlist で許可されたものに応じて（v1.1）
- 結果の Tachyon + Notion 同期保存
- 作業ディレクトリ隔離（`~/tachyon-workspace/projects/slow-exec-{todoId}/`）
- エラー時のUI表示 + 手動再実行

### 含まない（Phase2 以降）
- **Notion AI Meeting Notes の API直接取得**（Phase2、優先度は運用で判断）
- **音声ファイル（.m4a/.mp3）アップロード**（Q9-a=(1) 明確に対象外）
- **AIPM Flow配下への成果物自動保存**（Q8-b=(3) 明確に対象外）
- **自動リトライ**（Q8-c=(1) 明確に対象外）
- **confidenceベースの自動承認**（Q6-rev でBを選択。将来Cへ進化）
- **BL-ID自動発番 / AIPM Backlog.md 連携**（BL-0049 のスコープ）

### 既存機能との境界
- リアルタイム版 `todos.json` とは**別ファイル** `slow-todos.json` で管理
- 既存の `/api/close` は拡張するが、リアルタイム版のフローは壊さない

## 3. アーキテクチャ

### 3.1 全体データフロー

```
┌─────────────────────────── INPUT ───────────────────────────┐
│ [A] Tachyon録音 → STT → live.md                              │
│ [B] テキストアップロード(.md/.txt) → /api/slow-todos/import  │
│     → 新規会議作成 (status=closed, source=upload)            │
└────────────────────────┬───────────────────────────────────┘
                         ↓ いずれも会議close状態で合流
         ┌───────────────────────────────────┐
         │  /api/close (拡張) がフック          │
         │  または UIの[再生成]ボタン            │
         └───────────────┬───────────────────┘
                         ↓
              ┌──────────────────────┐
              │ lib/slow-agent.ts    │
              │ [生成: SDK直接 single]│
              │  1. live.md全文読込   │
              │  2. MasterIndex読込  │
              │  3. Claude Sonnet    │
              │     4.6でJSON出力     │
              │  4. slow-todos.json   │
              │     にdraft保存      │
              └───────────┬──────────┘
                          ↓
       ┌──────────────────────────────────┐
       │ UI: app/meetings/[id]/            │
       │      SlowTodosPanel.tsx          │
       │  - ドラフトカード一覧              │
       │  - [承認][編集][スキップ][実行]    │
       └───┬────────────┬─────────────────┘
           │ 承認         │ 実行
           ↓            ↓
   ┌──────────┐    ┌──────────────────────────────┐
   │ Notion投入│    │ lib/slow-executor.ts          │
   │(notion-  │    │ 【v1.1】Claude Code CLI相当    │
   │ client)  │    │  - @anthropic-ai/claude-      │
   │          │    │    agent-sdk を spawn         │
   │          │    │  - bypassPermissions          │
   │          │    │  - allowedTools=[…]           │
   │          │    │  - cwd=projects/slow-exec-{id}│
   │          │    │  - MCP / bash / fs / gws      │
   │          │    │    / gh / 各種CLI 利用可       │
   │          │    │  - 完了時 result を JSON化    │
   │          │    └─────────┬────────────────────┘
   └──────────┘              ↓
                  ┌──────────────────────┐
                  │ 結果保存（両方）        │
                  │  - slow-todos.json   │
                  │  - Notion元レコードに │
                  │    result同期          │
                  │  - 成果物ファイルは     │
                  │    cwd配下に保存       │
                  └──────────────────────┘
                          ↓失敗時
                  UI: エラー表示 + [再実行]ボタン
                  + 実行ログ (exec.log) リンク
```

### 3.2 モジュール構成

| ファイル | 役割 | 新規/拡張 |
|---|---|---|
| `lib/slow-agent.ts` | 全文解析→ToDo構造化生成（SDK直接・single-turn） | 新規 |
| `lib/slow-executor.ts` | **Claude Code CLI相当で実行**（Agent SDK + bypassPermissions + allowedTools） | 新規 |
| `lib/agent-launcher.ts` | Agent SDKプロセス起動・ログキャプチャ・タイムアウト・kill | 新規（v1.1） |
| `lib/exec-logger.ts` | 実行ログ書出し（`exec.log`、UIからの参照用） | 新規（v1.1） |
| `lib/notion-client.ts` | Notion DB書込 + 結果同期 | 新規 |
| `lib/slow-todos.ts` | `slow-todos.json` CRUD | 新規 |
| `app/api/slow-todos/generate/route.ts` | 生成トリガー（close時/手動） | 新規 |
| `app/api/slow-todos/execute/route.ts` | 実行トリガー | 新規 |
| `app/api/slow-todos/import/route.ts` | テキストアップロード受付 | 新規 |
| `app/api/slow-todos/[todoId]/route.ts` | 単一ToDoの更新/承認/スキップ | 新規 |
| `app/api/close/route.ts` | 自動生成フック追加 | 拡張 |
| `app/meetings/[id]/SlowTodosPanel.tsx` | UIコンポーネント | 新規 |
| `app/page.tsx` (Dashboard) | 「テキストアップロード」ボタン追加 | 拡張 |
| `data/settings.json` | `notionToken` / `notionDbId` / `slowTachyon` 追加 | 拡張 |
| `types/meeting.ts` | `SlowTodoItem` 型追加 | 拡張 |

### 3.3 データモデル

#### `types/meeting.ts` 追加型
```ts
export interface SlowTodoItem {
  id: string;
  meetingId: string;

  // Q7 スキーマ（ユーザー確定）
  title: string;
  description: string;
  completionCriteria: string;
  relatedProject: string | null;
  aiTaskContent: string;
  aiTaskCompletionCriteria: string;

  // システムメタ
  sourceText: string;
  sourceTimestamp: string;
  confidence: number;
  createdAt: string;

  // ワークフロー
  status: "draft" | "approved" | "skipped" | "running" | "completed" | "failed";
  approvedAt?: string;
  notionPageId?: string;

  // 実行結果
  result?: {
    type: "text" | "document" | "url";
    content: string;
    completedAt: string;
    syncedToNotion: boolean;
  };
  errorMessage?: string;
}
```

#### `meta.json` 拡張
```json
{
  ...existing,
  "source": "tachyon" | "upload",
  "slowTodoStatus": "pending" | "running" | "completed" | "failed",
  "slowTodoGeneratedAt": "ISO",
  "slowTodoCount": 12
}
```

#### 新ファイル: `data/meetings/{id}/slow-todos.json`
`SlowTodoItem[]` の配列。リアルタイム版 `todos.json` とは分離。

## 4. LLMプロンプト設計

### 4.1 生成フェーズ（`lib/slow-agent.ts`）
- **モデル**: Claude Sonnet 4.6（5分要件優先、必要に応じてOpusで精度検証）
- **入力**:
  - 会議メタ（title, createdAt, source, durationSec）
  - `live.md` 全文
  - `Stock/MasterIndex.yaml`（`relatedProject` 抽出用）
- **出力スキーマ**: §3.3 の `SlowTodoItem` 配列（draft状態）+ `summary` + `excludedCandidates`
- **方針**:
  - 全文読み切り → 重複/類似ToDoマージ
  - 明示的な動詞/決定フレーズを優先、雑談は `excludedCandidates` に落とす
  - **「AI作業内容」「AI作業の完了条件」は具体的アクション形式**（曖昧さを残さない）
  - relatedProject は MasterIndex.yaml のProject名と照合、該当なければ null

### 4.2 実行フェーズ（`lib/slow-executor.ts`）【v1.1 更新】
- **実行基盤**: `@anthropic-ai/claude-agent-sdk` の `query()` を `bypassPermissions` + `allowedTools` 指定で起動（既存 `~/tachyon-workspace/agent-sdk-runner.mjs` のパターンを踏襲）
- **モデル**: Claude Sonnet 4.6（CLI相当モード、multi-turn、tool-use可）
- **作業ディレクトリ**: `~/tachyon-workspace/projects/slow-exec-{todoId}/`（隔離、成果物はここに生成）
- **入力（プロンプト）**:
  - 会議メタ（title/date/参加者）+ 元発言（sourceText）
  - `aiTaskContent`（何をするか）
  - `aiTaskCompletionCriteria`（完了基準）
  - 許可ツール一覧と使い方の注記
  - Notion DB の該当レコードID（結果を書き戻す先）
  - AIPMナレッジ参照が必要ならMasterIndex読込を指示
- **出力形式**: 完了時に JSON で標準出力に `{result, filesCreated, notionUpdated, summary}` を書かせて capture（または最終メッセージから抽出）
- **タイムアウト**: 既定 15分、超過で kill → failed ステータス（UIエラー表示）
- **完了判定**: `aiTaskCompletionCriteria` をAIが満たすと自己宣言 → `status: completed`
- **並行実行**: 同一会議内では1タスクずつ直列実行（CPU/API負荷・ログ混線回避）。Phase2で並列化検討

### 4.3 許可ツール（allowedTools）【確定: Q10=B 中】
採用ツール群（`@anthropic-ai/claude-agent-sdk` + MCP）:
- **ファイル操作**（作業dir配下のみ推奨）: `Read` / `Write` / `Edit` / `Glob` / `Grep`
- **Web調査**: `WebFetch` / `WebSearch`
- **Shell**: `Bash`（`gws` CLI でSheets/Docs/Drive/Calendar、`gh` CLI でGitHub起票、`curl` 等）
- **MCP**: Notion MCP（DB拡張操作）+ Google Drive MCP（Drive参照）

除外（Phase1 では入れない）:
- Figma / Canva / Playwright / Vercel 等のMCP — 必要になった時点で個別追加（Phase2）

破壊的コマンドのブロック:
- プロンプト規約で禁止（`rm -rf`、`git reset --hard`、`git push --force`、`DROP TABLE`、`sudo` 等）
- pre-tool-use hook で主要パターンを正規表現マッチして拒否
- 作業dir外への `Write` / `Edit` はパス検証で拒否

### 4.4 承認モード【確定: Q11=A bypassPermissions 全自動】
- Tachyon UIでタスク承認ボタン押下 = ツール使用も含めて完全自動で実行
- 人間ゲートは Q6-rev=B の UI事前レビューに集約（AI作業内容・完了条件を承認した時点で実行委任）
- 実行中の進捗はUIにストリーム表示、緊急停止は [kill] ボタン
- 監査は `exec.log` で全ツール呼び出しを記録（後追い可能）

## 5. API 仕様（Phase1）

| メソッド | ルート | 用途 | 主要ボディ |
|---|---|---|---|
| POST | `/api/slow-todos/generate` | 生成起動（自動/手動） | `{ meetingId }` |
| POST | `/api/slow-todos/import` | テキストアップロード→新規会議作成 | `{ title, transcriptText, source:"upload" }` |
| POST | `/api/slow-todos/[todoId]` | 承認/編集/スキップ | `{ action: "approve"|"edit"|"skip", patch? }` |
| POST | `/api/slow-todos/execute` | 実行起動 | `{ todoId }` |
| GET | `/api/slow-todos?meetingId=xxx` | 一覧取得 | — |

`/api/close` は自動生成フックを追加（既存レスポンスは不変、失敗しても close は成功扱い）。

## 6. Notion DB スキーマ（新規作成依頼が必要）

```
DB名: Meeting ToDos

プロパティ:
- Title (Title)
- Description (Rich text)
- CompletionCriteria (Rich text)
- RelatedProject (Select) — AIPM Programs/Projects
- AITaskContent (Rich text)
- AITaskCompletionCriteria (Rich text)
- Status (Select): draft / approved / running / completed / failed / skipped
- MeetingId (Rich text)
- MeetingTitle (Rich text)
- MeetingDate (Date)
- SourceText (Rich text)
- SourceTimestamp (Rich text)
- Confidence (Number, 0-1)
- Result (Rich text) — 実行結果本体
- ResultCompletedAt (Date)
- TachyonUrl (URL) — Tachyon側の詳細ページへのリンク
```

※ 実装タスク着手時にユーザーへ Notion Integration 発行と DB ID 収集を依頼（AI-Core PL と同じ段取りで `NOTION_TOKEN` / `NOTION_DB_MEETING_TODOS` を受領する）

## 7. 実装フェーズ計画

| Phase | 内容 | 所要 | 依存 |
|---|---|---|---|
| P0 | Notion Integration + DB作成依頼 → 受領 | 0.5h（ユーザー側）| ユーザー |
| P1 | データモデル追加（`types/meeting.ts` / `slow-todos.ts`） | 0.5h | — |
| P2 | 生成コア（`slow-agent.ts` + プロンプト + MasterIndex読込） | 3h | P1 |
| P3 | 自動トリガー（`/api/close` 拡張 + `/api/slow-todos/generate`） | 1h | P2 |
| P4 | テキストアップロード（`/api/slow-todos/import` + ダッシュボードUI） | 1.5h | P1 |
| P5 | UI: SlowTodosPanel（一覧・編集モーダル・承認/スキップ/実行） | 3h | P2 |
| P6 | Notion連携（`notion-client.ts` + 承認時投入） | 2h | P5, P0 |
| **P7** | **実行コア（`slow-executor.ts` + `agent-launcher.ts` + `exec-logger.ts`、Agent SDK起動・タイムアウト・ログ・プロセス管理）** | **4〜5h** | P5, P6, Q10/Q11 |
| **P7.5** | **allowedTools設定 + 作業dir隔離 + 既存MCP接続確認** | **0.5〜1h** | P7 |
| P8 | エラーハンドリング（UIエラー表示 + 実行ログリンク + 手動再実行） | 1h | P7 |
| P9 | 実会議データでのE2Eテスト + プロンプト調整 + ツール動作確認 | 2h | P7, P8 |
| P10 | Stock反映（README / ProjectIndex / log更新） | 0.5h | P9 |

**合計**: **17〜20h**（v1.1、実装側のみ、P0 除く）

### 想定優先順: P1 → P2 → P3 → P5 → P6 → P7 → P8 → P4 → P9 → P10
（アップロード機能P4は後ろにずらして、まずは既存録音→生成の本流を通す）

## 8. 受け入れ基準（Definition of Done）

- [ ] 会議close時に自動で `slow-todos.json` が生成される
- [ ] 5分以内にToDo一覧がUIに出る（30分以内の会議で計測）
- [ ] テキストアップロードから新規会議作成→ToDo生成まで動く
- [ ] UIで承認/編集/スキップ/実行すべてのアクションが動作
- [ ] 承認時にNotion DBに該当ToDoが追加される
- [ ] 実行時に結果がTachyonとNotion両方に書き込まれる
- [ ] 実行失敗時にUIにエラーが表示され、再実行ボタンから復旧できる
- [ ] リアルタイム版（既存 `todos.json`）の挙動が壊れていない（回帰テスト）
- [ ] 実会議データ3件以上での動作確認完了

## 9. リスク・留意点

- **5分以内の制約（生成のみ対象）**: Q1の5分要件は「ToDo一覧が出るまで」。**実行は対象外**（CLI実行は数秒〜15分、UIで進捗表示）
- **生成時の長時間会議**: 90分超会議で `live.md` が数万文字になった場合、Sonnetでも応答時間が微妙。対策: 超過時は「要約→抽出」2段パス or Haikuフォールバック（Phase1.5）
- **プロンプト精度**: リアルタイム版の「部分発言反応」問題を回避できるか、既存30+件の会議データで事前検証（プロンプト反復2〜3回を織り込み済）
- **Notion APIレート**: 1会議で10+ToDoを一括書込する場合、429に注意。逐次投入＋150ms間隔を既定
- **【v1.1】CLI実行時間の可変性**: 数秒〜10分以上と幅が大きい。UIには running 状態 + 経過時間 + kill ボタンを必ず用意。タイムアウト既定15分
- **【v1.1】CLI実行コスト**: Sonnet を multi-turn + tool-use で走らせるため 1タスク $0.1〜$1 程度。月間ToDo数 × 平均実行時間で概算を定期モニタ
- **【v1.1】並行実行制限**: 同時に複数タスクを走らせると API レート/CPU 負荷が急増。同一会議内は直列、複数会議またがる場合もグローバル並列数上限（既定2）を設ける
- **【v1.1】セキュリティ（allowedTools）**: `Bash` を許可する場合、プロンプトで破壊的操作を禁止 + pre-tool-use hook で `rm -rf /`、`git push --force`、`DROP TABLE` などのパターンを弾く
- **【v1.1】プロセス管理**: Agent SDK プロセスは kill 時に zombie にならないよう `SIGTERM → 5秒後 SIGKILL` の段階 kill
- **【v1.1】作業ディレクトリの肥大**: `projects/slow-exec-{todoId}/` を30日後に自動cleanup（TTL cron or 手動スクリプト）
- **エラー復旧**: 手動再実行のみ（Q8-c=(1)）なので、エラー原因がUIで分かる診断ログが重要。実行ログ `exec.log` をUIから参照できるリンクを用意
- **既存リアルタイム版との併存**: 同じ会議で `todos.json`（リアルタイム）と `slow-todos.json`（低速）が両方存在するケースあり。UI上での見せ分けに注意

## 10. 未解決事項 / 次アクション

- [x] Q1〜Q9 すべて回答受領・反映完了
- [x] v1.1 変更: 実行エンジンを Claude Code CLI 相当に変更（2026-04-22 17:00）
- [x] **Q10=B 中** / **Q11=A bypassPermissions 全自動** 確定（2026-04-22 17:15）
- [x] Notion Integration + DB 準備完了（田中さん側 `.env` に NOTION_TOKEN / NOTION_DB_ToDos 登録済み）
- [ ] **次アクション**: 「実装着手 BL-0062」指示 → 別エージェントで実装タスク起動
- [ ] Phase2 候補: Notion AI Meeting Notes 直接取込（Q2-rev=(a) の後続）、AIPM Flow連携 (Q8-b 関連、必要性を運用で判断)、confidenceベース自動承認（Q6-rev=C）、複数タスク並列実行、MCP拡張（Figma/Canva/Playwright 等）
