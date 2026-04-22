# BL-0062 低速タキオン（会議後ToDo生成）— Discovery Notes

最終更新: 2026-04-22

## 1. タスク定義（バックログより）

- **ID**: BL-0062 / P1 / RestaurantAILab/Tachyon
- **要件**: リアルタイムではなく、**会議終了後に全文トランスクリプトを使ってToDoを生成するモード**
- **Notes**: Notion保存・Notion Meeting連携が理想
- **関連タスク**:
  - BL-0048 (P2, todo): リアルタイム側の「タスク生成精度の向上」— BL-0062とは **別タスク**
  - BL-0049 (P3, todo): タスク管理システムとの接続（生成ToDoを既存システムに自動連携）
  - BL-0047 (P1, done): 音声読み取り精度向上 — 2026-04-22 完了（低速タキオンの前提としてSTTは使える状態）
  - BL-0024 / BL-0025 (P2, todo): 町田・吉田への展開

## 2. 既存Tachyon資産の棚卸し

### 2.1 実装場所
- **リポジトリ**: `~/tachyon-workspace/`（AIPMリポジトリの外、独立）
- **本体アプリ**: `~/tachyon-workspace/tachyon/`（Next.js 16, port 3000, HTTPS）
- **projects/**: エージェントが開発した派生アプリ置き場（`meeting-feedback`等の雛形は存在するが実装なし）
- **Stock**: `Stock/RestaurantAILab/Tachyon/` にはREADME + ProjectIndex.yaml + log.md（メタ情報のみ、コードはなし）

### 2.2 既存Tachyonのアーキテクチャ（要約）

```
[スマホ] 録音 → Tachyon API(HTTPS) → OpenAI STT(gpt-4o-mini-transcribe)
                                    ↓
                        data/meetings/{id}/live.md に追記
                                    ↓（エージェントがポーリング）
           Claude Code CLI / Agent SDK が live.md を読む
                                    ↓
                    POST /api/todos (action=add) で提案登録
                                    ↓（UIに表示）
           ユーザーが approve → running → complete まで状態遷移
```

### 2.3 会議ごとのデータ（`tachyon/data/meetings/{id}/`）
- `meta.json` — id / title / status (`active`|`closed`) / createdAt / closedAt / useAipmKnowledge / slackThreadTs 等
- `live.md` — `[HH:MM:SS] 発言` 形式の時系列トランスクリプト
- `transcript.log` — OpenAI STTの生レスポンス
- `todos.json` — ToDo配列（リアルタイムに追記、現状は「提案のみ」で自動実行しない lightweight モード）
- `topics.json` — 会議トピック抽出結果（新機能、詳細未調査）
- `proposals.json` — 旧仕様の提案フォーマット（新規会議では使われていない模様）
- `agent.log` — エージェント動作ログ

### 2.4 既存APIルート（`tachyon/app/api/`）
| ルート | 用途 |
|---|---|
| `agent/` | エージェント接続通知（acknowledge） |
| `audio/` | 音声チャンク受付 → STT → transcript追記 |
| `close/` | 会議終了（meta.status を closed に） |
| `health/` | ヘルスチェック |
| `meetings/` | 作成/一覧/リネーム |
| `proposals/` | 旧提案API |
| `settings/` | エージェント設定（systemPrompt / instructionTemplate / slack等） |
| `todos/` | ToDo CRUD |
| `topics/` | トピック抽出 |
| `transcript/` | トランスクリプト取得 |

### 2.5 既存ToDoスキーマ（`tachyon/types/meeting.ts` より抜粋）
```ts
interface TodoItem {
  id, title, description, assignee?, 
  priority: "high" | "medium" | "low",
  category: "development" | "research" | "communication" | "other",
  status: "proposed" | "running" | "completed" | "later" | "skipped",
  aiExecutable: boolean, recommendedAction, sourceText, createdAt,
  result?, resultType?: "app" | "text" | "local-files", ...
}
```

### 2.6 現行エージェントモード（`data/settings.json`より）
- `agentMode: "lightweight"` — **提案のみ**、自動実行しないモードが既定
- 実行系は別エージェント（旧来のCLIモードはproposalsを自動実行できる）
- AIPMナレッジ参照モード（`useAipmKnowledge: true`）で AIPMリポのMasterIndex等を読める

### 2.7 Notion連携の現状
- **既存Tachyonには Notion連携は実装されていない**（Slack/Webhook連携のみ）
- 「Notion Meeting」が具体に何を指すかは要確認（Notion AI Meeting Notes / 手動で運用しているNotion DB / BL-0063のOMI連携由来）

## 3. 「低速タキオン」の仮説（AI側の現時点の解釈）

### 3.1 「低速」の定義（推定）
- リアルタイム（数秒〜数十秒でToDoを出す）ではなく、**会議終了後に全文を一括解析して生成する**バッチモード
- 「低速」=「会議の流れを読み切ってから落ち着いてToDoを組み立てる」という意味だと解釈
- これによりリアルタイム版の既知課題（部分発言に反応して誤抽出、文脈欠落、重複）を構造的に解消できる

### 3.2 既存（リアルタイム版）との役割分担の想定

| 観点 | 既存Tachyon（リアルタイム） | 低速タキオン（BL-0062） |
|---|---|---|
| トリガー | 会議中、transcript追記のたび | 会議close時（または手動） |
| 入力 | 直近のlive.md差分 | 全文live.md（または Notion議事録） |
| 利点 | 会議中に提案が上がる即効性 | 全体文脈が見え、精度・重複排除が容易 |
| 出力 | `todos.json`（会議単位） | Notion DB（恒久保存）+ AIPMバックログ？ |
| レビュー | 会議中ユーザーが approve/skip | 後日まとめてレビュー（人間承認を挟めるタイミングが柔軟） |

### 3.3 想定アーキテクチャ（3案）

**案A: 既存Tachyonリポジトリの新モジュール**
- `tachyon/lib/slow-agent.ts` + `app/api/slow-todos/` を追加
- close時に自動トリガー、または手動キック用ルート
- 既存の `todos.json` / `data/meetings/` 資産を再利用

**案B: `projects/slow-tachyon/` として独立Next.jsアプリ**
- 既存Tachyonを読み取り専用で参照（tachyon/data を cross-read）
- UIを別で持つ。既存Tachyonに手を入れずに済む

**案C: AIPMリポ内スクリプト（Next.jsなし）**
- Node.js / Python CLIで `~/tachyon-workspace/tachyon/data/meetings/` をスキャン
- Notion API と直接通信、AIPM Backlog.mdに追記
- UIなし、裏で走るバッチジョブ

現時点のAI推奨: **案A**（データ所在が同一、クライアント実装不要、UI統合簡単）

### 3.4 入力ソースの3案

| 案 | 内容 | メリット | デメリット |
|---|---|---|---|
| (a) 既存Tachyon live.md | close済みlive.mdを全文LLMに投入 | すぐ動かせる、既存資産活用 | Notion MeetingのUIを使う案とは別路線になる |
| (b) Notion Meeting から取得 | Notion DB/ページのトランスクリプトをAPIで取得 | 既にNotion運用しているチームへの馴染み | 「Notion Meeting」の具体像が未確定、Notion AI Notesの仕様次第 |
| (c) 両対応（ハイブリッド） | どちらの入力源でも動く抽象レイヤー | 将来の柔軟性 | 初期実装が重い |

### 3.5 出力先の3案

| 案 | 内容 | メリット | デメリット |
|---|---|---|---|
| (a) Notion DB のみ | チームで共有しやすい、UIが既にある | 運用が他ツールと分散しない | AIPM Backlog との二重管理リスク |
| (b) AIPM Backlog.md | 既存バックログに追記、AIOSの流儀 | 一元管理、Git履歴で追える | チームメンバーがNotionしか見ないと埋もれる |
| (c) 両方 | Notionで共有、AIPMで厳密管理 | 視認性・管理性両立 | 同期設計が必要（どちらがマスターか等） |

## 4. 主要な不明点（INBOXで確認予定）

1. **「低速」の遅延許容**: close直後（数分以内）/ 時間単位 / 翌日でもOK
2. **入力ソース**: 既存Tachyon live.md / Notion Meeting / 両方 — 「Notion Meeting」の定義含む
3. **出力先**: Notion DB のみ / AIPM Backlog / 両方 / 既存Tachyonの `todos.json` にも書く
4. **トリガー**: close時の自動 / 手動キック / cron定期
5. **実装場所**: 既存Tachyonリポ内 / projects/ 配下の独立アプリ / AIPMリポ内CLI
6. **人間レビュー**: 自動投入OK / ドラフト状態でレビュー必須
7. **ToDo粒度・メタ情報**: 担当者・期限・プロジェクト分類まで抽出するか（BL-0049に踏み込むか）
8. **既存リアルタイム版との関係**: 共存（両方走らせる）/ 低速へ一本化 / 当面は手動切替

## 5. 参照資料

- 既存Tachyon仕様: `~/tachyon-workspace/SPEC.md`
- 既存Tachyon CLI用指示書: `~/tachyon-workspace/CLAUDE.md`
- Stock: `Stock/RestaurantAILab/Tachyon/README.md`
- Backlog: `Stock/定型作業/バックログ/Backlog.md` (BL-0062, BL-0048, BL-0049)
- 設定サンプル: `~/tachyon-workspace/tachyon/data/settings.json`
- 型定義: `~/tachyon-workspace/tachyon/types/meeting.ts`
