# BL-0062 低速タキオン — Implementation Plan v1.0

最終更新: 2026-04-22 16:05 / **status: 🔵 計画確定（実装フェーズ起動待ち）**

## 0. エグゼクティブサマリ

- **目的**: 会議終了後に全トランスクリプトを解析して構造化ToDoを生成し、UIでレビュー→承認→AI実行→結果保存までを一気通貫で実現
- **実装場所**: 既存Tachyon（`~/tachyon-workspace/tachyon/`）に機能追加（別リポ作らない）
- **差別化**: リアルタイム版（部分発言反応・全文脈未読）との棲み分け。低速版は全文読み切り＆承認ワークフロー付き
- **総工数見積**: **約14〜17h（Phase1 のみ）** / **Phase2 (Notion AI直接連携) は別送り**
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
| 実行エンジン | **Tachyon内の軽量エージェント（Anthropic SDK直接呼び出し）** — 単一エンジン | Q8-a=(2) |
| 結果保存先 | **Tachyon内 + Notion 両方**（AIPM Flow配下には保存しない） | Q8-b=(3) |
| 失敗時挙動 | UIにエラー表示 + 手動再実行（自動リトライなし） | Q8-c=(1) |
| Notion URL取込 | Phase1では実装しない（Notion側エクスポートMarkdownを通常アップロードで投入） | Q9-c=(1) |

## 2. スコープ境界

### Phase1 に含む
- 会議close時の自動ToDo生成 + 手動再実行
- テキスト（.md/.txt）アップロード → 新規会議として受付 → 通常フローで生成
- Tachyon UIでのドラフト表示（承認/編集/スキップ/実行ボタン）
- AI実行（Anthropic SDK経由）
- 結果の Tachyon + Notion 同期保存
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
   ┌──────────┐    ┌──────────────────┐
   │ Notion投入│    │ lib/slow-executor.ts │
   │(notion-  │    │  - Anthropic SDK     │
   │ client)  │    │  - 結果をJSONに書戻   │
   └──────────┘    └─────────┬────────────┘
                              ↓
                  ┌──────────────────────┐
                  │ 結果保存（両方）        │
                  │  - slow-todos.json   │
                  │  - Notion元レコードに │
                  │    result同期          │
                  └──────────────────────┘
                          ↓失敗時
                  UI: エラー表示 + [再実行]ボタン
```

### 3.2 モジュール構成

| ファイル | 役割 | 新規/拡張 |
|---|---|---|
| `lib/slow-agent.ts` | 全文解析→ToDo構造化生成 | 新規 |
| `lib/slow-executor.ts` | Anthropic SDK でタスク実行 | 新規 |
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

### 4.2 実行フェーズ（`lib/slow-executor.ts`）
- **モデル**: Claude Sonnet 4.6（SDK直接、single-turn）
- **入力**: `aiTaskContent` + `aiTaskCompletionCriteria` + 会議メタ + 必要に応じAIPMナレッジ参照
- **出力形式**: Markdownテキスト or ドキュメント（ファイル出力が必要な場合は後送り）
- **完了判定**: LLMが `aiTaskCompletionCriteria` を満たすと自己宣言 → `status: completed`

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
| P7 | 実行コア（`slow-executor.ts` + 結果書戻 + Notion同期） | 2h | P5, P6 |
| P8 | エラーハンドリング（UIエラー表示 + 手動再実行） | 1h | P7 |
| P9 | 実会議データでのE2Eテスト + プロンプト調整 | 1.5h | P7, P8 |
| P10 | Stock反映（README / ProjectIndex / log更新） | 0.5h | P9 |

**合計**: **14〜17h**（実装側のみ、P0 除く）

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

- **5分以内の制約**: 90分超会議で `live.md` が数万文字になった場合、Sonnetでも応答時間が微妙。対策: 超過時は「要約→抽出」2段パス or Haikuフォールバック（Phase1.5）
- **プロンプト精度**: リアルタイム版の「部分発言反応」問題を回避できるか、既存30+件の会議データで事前検証（プロンプト反復2〜3回を織り込み済）
- **Notion APIレート**: 1会議で10+ToDoを一括書込する場合、429に注意。逐次投入＋150ms間隔を既定
- **実行タスクの多様性**: Q8-a=(2) で SDK単一エンジンに絞ったため、「アプリ開発」のような大規模タスクは Phase1 では実行成功率が低い。プロンプトで「SDK単発で扱える粒度に分解する」誘導を入れる
- **エラー復旧**: 手動再実行のみ（Q8-c=(1)）なので、エラー原因がUIで分かる診断ログが重要
- **既存リアルタイム版との併存**: 同じ会議で `todos.json`（リアルタイム）と `slow-todos.json`（低速）が両方存在するケースあり。UI上での見せ分けに注意

## 10. 未解決事項 / 次アクション

- [x] Q1〜Q9 すべて回答受領・反映完了
- [ ] **次アクション**: 実装フェーズタスクを起動（作業場所: `~/tachyon-workspace/tachyon/` / 前提: P0 Notion DB作成依頼）
- [ ] Phase2 候補: Notion AI Meeting Notes 直接取込（Q2-rev=(a) の後続）、AIPM Flow連携 (Q8-b 関連、必要性を運用で判断)、confidenceベース自動承認（Q6-rev=C）
