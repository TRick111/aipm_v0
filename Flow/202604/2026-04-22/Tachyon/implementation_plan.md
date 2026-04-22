# BL-0062 低速タキオン — Implementation Plan (Draft v0.1)

最終更新: 2026-04-22 / **status: waiting_answers**

> ⚠️ このファイルは **INBOX.md の Q1〜Q7 回答後に確定版 v1.0** に書き換える。現時点は骨子のみ。

## 1. ゴール（完了条件）

- [ ] 会議終了後に `live.md` 全文からToDoを生成するバッチ処理が動く
- [ ] 生成ToDoが指定の出力先（Notion DB / AIPM Backlog / 既存Tachyonのtodos.json）に反映される
- [ ] 人間レビューが必要な運用ならUI/CLIフローがある
- [ ] 既存リアルタイム版と役割分担が明確で、併存しても重複・衝突が起きない

## 2. スコープ境界

### 含む
- 会議close時または手動起動での全文トランスクリプト解析
- LLMによる構造化ToDo抽出（title / description / priority / category / assignee? / sourceText）
- 指定先（Notion DB / AIPM Backlog / todos.json）への書き込み

### 含まない（後続タスク）
- **BL-0048**: リアルタイム版の精度向上 — 別タスク
- **BL-0049**: 生成ToDoとAIPM Backlog の自動連携・BL-ID発番 — ※Q7の回答次第で一部取り込み
- **BL-0063**: OMI連携（音声指示→Tachyon） — 別タスク、ただし将来的に入力ソースとして合流可能性あり

## 3. アーキテクチャ（Q2/Q4/Q5回答後に確定）

### 3.1 仮の全体図（AI推奨ケース: Q2=(a), Q4=(d), Q5=(a) を前提）

```
[既存Tachyon] 会議close → /api/close
                            ↓ (hook)
        [新] POST /api/slow-todos/generate
                            ↓
           lib/slow-agent.ts
             ├─ 1. meta.json + live.md 読込
             ├─ 2. Claude API (Opus) に全文投入（プロンプトは §5）
             ├─ 3. JSON構造化ToDo配列を受領
             ├─ 4. AIPM MasterIndex照合（プロジェクト分類）
             └─ 5. 出力先へ書き込み（Notion DB + AIPM Backlog 等）
                            ↓
         UIに「低速生成完了」通知（approve/skip UI付き・Q6次第）
```

### 3.2 モジュール構成（案A: 既存Tachyonリポ内）
| ファイル | 役割 |
|---|---|
| `tachyon/lib/slow-agent.ts` | バッチ解析のコア（LLM呼び出し・構造化） |
| `tachyon/lib/notion-client.ts` | Notion DB書き込み（Q3で使う場合） |
| `tachyon/lib/aipm-backlog.ts` | AIPM Backlog.md への追記（Q3で使う場合） |
| `tachyon/app/api/slow-todos/generate/route.ts` | 手動起動用エンドポイント |
| `tachyon/app/api/close/route.ts` | 既存を拡張してフック追加 |
| `tachyon/app/meetings/[id]/SlowTodosPanel.tsx` | UI（approve/skip・Q6次第） |
| `tachyon/data/settings.json` | `slowTachyonEnabled`, `notionApiKey`, `notionDbId` 等を追加 |

## 4. 決定待ち項目（INBOX.md Q1〜Q7）

| ID | 論点 | 確定後の影響 |
|---|---|---|
| Q1 | 遅延許容（自動/時間/日次） | トリガー実装粒度 |
| Q2 | 入力ソース（live.md/Notion） + Notion Meeting正体 | データ取得レイヤー |
| Q3 | 出力先（Notion/AIPM/両方） | 書き込みレイヤーと同期設計 |
| Q4 | 起動トリガー | エンドポイント + フック |
| Q5 | 実装場所 | リポジトリ・言語選定 |
| Q6 | 人間レビュー有無 | UI実装量 |
| Q7 | ToDo抽出メタ情報の粒度 | プロンプト設計と後処理 |

## 5. LLMプロンプト設計（ドラフト）

### 5.1 入力
- `meta.json`（会議タイトル・日時・参加者情報があれば）
- `live.md` 全文（時系列発言）
- （Q7=(c)以上の場合）`Stock/MasterIndex.yaml` の全Project情報

### 5.2 出力スキーマ（Q7回答で調整）
```json
{
  "todos": [
    {
      "title": "...",
      "description": "...",
      "priority": "high|medium|low",
      "category": "development|research|communication|other",
      "assignee": "田中|吉田|町田|大地|null",
      "dueDate": "YYYY-MM-DD|null",
      "program": "RestaurantAILab|作業効率化|...",
      "project": "Tachyon|AI-Core|...",
      "sourceText": "元発言の引用（タイムスタンプ付き）",
      "confidence": 0.0-1.0
    }
  ],
  "summary": "会議の要旨（3行）",
  "excludedCandidates": [
    { "text": "...", "reason": "不確定/雑談/重複" }
  ]
}
```

### 5.3 システムプロンプト骨子
- 全文を読み切ってから抽出（リアルタイムとの差別化）
- 重複・類似ToDoはマージ
- 明示的な動詞/決定フレーズ（「〜する」「〜しよう」「〜してください」）を優先
- 雑談・仮定の議論は `excludedCandidates` に落とす
- confidence 0.7以上のみ投入候補

## 6. データモデル変更

### 6.1 `meta.json` 拡張（案）
```json
{
  ...
  "slowTodoStatus": "pending|running|completed|failed",
  "slowTodoGeneratedAt": "ISO",
  "slowTodoCount": 12
}
```

### 6.2 新ファイル: `data/meetings/{id}/slow-todos.json`
- 低速生成結果を別ファイルに保存（リアルタイムの `todos.json` と混ぜない）
- レビュー後に approved を Notion/Backlog に反映

## 7. 実装フェーズ計画（仮）

| Phase | 内容 | 所要 | 依存 |
|---|---|---|---|
| P1 | Q1〜Q7 確定 → 計画 v1.0 化 | 0.5h | 本INBOX回答 |
| P2 | LLM抽出コア実装（`slow-agent.ts` + プロンプト） | 3h | P1 |
| P3 | 出力先アダプタ（Notion/AIPM/todos.json） | 2〜4h | P1, P2 |
| P4 | トリガー実装（API / closeフック） | 1.5h | P2, P3 |
| P5 | UI/レビュー画面（Q6次第、省略可能性あり） | 2〜4h | P3 |
| P6 | 実会議でのE2Eテスト + プロンプト調整 | 2h | P4 |
| P7 | Stock反映（README更新 / ProjectIndex更新 / log追記） | 0.5h | P6 |

**仮合計**: 11.5〜14.5h（Q5=(a), Q6=(a), Q3=(a)のミニマル構成なら ~7h）

## 8. リスク・留意点

- **プロンプト精度**: リアルタイム版で既知の「部分発言に反応」問題を回避できるか、実会議データで要検証（テストデータは `~/tachyon-workspace/tachyon/data/meetings/` に30+件あり、再生可能）
- **Notion API レート**: 1会議で数十ToDoを一括書込する場合に注意。バルク書込 or 逐次+レート制御
- **二重管理リスク**: Notion + AIPM Backlog 両出力時、どちらがマスターか明確にしないと同期地獄になる → Q3で確定
- **既存リアルタイム版との衝突**: 同じ `todos.json` に書かないこと。別ファイル `slow-todos.json` に分離する方針

## 9. 未解決事項 Log

- [ ] Q1〜Q7 回答受領（INBOX.md）
- [ ] Notion Meeting の正体確定（Q2サブ質問）
- [ ] （確定後）`implementation_plan.md` を v1.0 に書き換え、実装タスクへ引継ぎ
