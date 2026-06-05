# BL 一覧 / カンバンビュー 実装方針（複数案）

- 作成日: 2026-06-05
- 起票者: master (Claude)
- 関連 BL: BL-0095「ミニタキオン アップデート (今日着手分)」
  - 特に Q2「P2 (UI に「+ 新規 BL」モーダル追加)」と直接関連
- 目的: BL 一覧が見れない / カンバンが無い問題を解決する手段を、データ層と UI 層の両軸で複数案提示し、決定可能な状態にする

---

## 1. 背景と論点

### 現状の課題（田中さんの言葉から）
- BL の **一覧が見れない**（モバイルでも Cursor 上でも一望性が低い）
- 新規 BL 追加が mini-tachyon からできず、Cockpit / Cursor 経由になっていて不整合の温床
- BL クローズの判断材料がそろわない
- AIPM リポジトリで最終的に管理し続けたい（Linear 等の SaaS に逃がしたくない）

### 論点
- **データ層**: 現行 YAML SSOT を保つか / SQLite 等 DB に寄せるか / ハイブリッドか
- **UI 層**: 一覧（テーブル）とカンバン（ボード）を mini-tachyon 内に実装するか / 外部ツールに任せるか
- **AIPM Git 適合**: BL の議論履歴 (decisions[], pending_questions[]) が diff レビューできること

---

## 2. 評価軸

| 軸 | 説明 |
|---|---|
| AIPM Git 適合度 | BL の本文・議論履歴が `git log` / `git diff` で追える |
| クエリ性能 | 100〜500 BL 規模で一覧/フィルタ/ソートが軽快 |
| 整合性 | 並行書き込み / スキーマ違反を構造的に防げる |
| 実装工数 | mini-tachyon への追加実装量（週末単位で見積） |
| 段階移行性 | 既存運用を壊さず徐々に移行できる |
| ロックイン | 方針転換コスト（後戻りできるか） |

---

## 3. アプローチ案

### A. YAML 据え置き + mini-tachyon UI 拡張

**概要**
- 既存の `Stock/<category>/<project>/backlog/BL-XXXX.yaml` を変えない
- mini-tachyon に `/backlog`（一覧）と `/board`（カンバン）ページを追加
- 既存 `lib/index-store.ts` の in-memory index にフィルタ/ソート/ページネーション機能を足す
- 書込は引き続き mt CLI / MCP / HTTP API 経由（atomic write 維持）

**データフロー**
```
YAML (SSOT)
  ├── chokidar watch ──► in-memory index ──► HTTP API ──► UI
  └◄── atomic write ──── mt CLI / MCP / API（書込）
```

**Pros**
- 追加データ層なし、現運用と完全互換
- AIPM Git で BL.yaml が引き続き diff レビュー可能
- 実装工数最小、ロックイン無

**Cons**
- BL が 500+ になると in-memory index 再構築が visible になる
- カンバンの drag-drop で「列内順序」を保存しようとすると BL.yaml に `order` フィールド追加が必要 → Git noise
- 横断集計（成果物 cross BL 等）は全件 scan

**工数感**: 2〜3 週末（UI 中心）

---

### B. YAML SSOT + SQLite 索引キャッシュ

**概要**
- BL.yaml は引き続き SSOT
- chokidar watch で SQLite (better-sqlite3) にインデックスを同期
- 一覧/カンバン UI は SQLite 経由でクエリ
- 書込は API → YAML が先、SQLite は事後 reindex（再起動時は full rebuild）

**データフロー**
```
mt CLI / MCP / API ──atomic write──► YAML (SSOT)
                                          │
                                          ▼ chokidar
                                     SQLite (索引/キャッシュ)
                                          │
                                          ▼
                                     UI（一覧/カンバン query）
```

**Pros**
- 一覧クエリ高速（`SELECT ... WHERE state IN ... ORDER BY priority LIMIT 50`）
- 全文検索が容易（SQLite FTS5）
- SQLite ファイルは `.gitignore` → AIPM リポは汚れない
- 壊れたら捨てて作り直せる（YAML が真実なので回復可能）

**Cons**
- 二重管理（同期コードのテストが必要）
- 再起動時の rebuild に数秒〜
- カンバン列内順序を YAML に持たせる課題は A と同じ

**工数感**: 3〜4 週末

---

### C. SQLite SSOT + 日次 YAML/MD エクスポート

**概要**
- BL の SSOT を SQLite に移す
- 編集はすべて API / UI 経由（YAML の手書き禁止を制度化）
- 1 日 1 回（夜の振り返り後 or 03:00 cron）で SQLite → `BL-XXXX.yaml` 一式をエクスポート、Git commit
- AIPM Git は「日次スナップショット」になる

**データフロー**
```
UI / mt CLI / MCP ──► API ──► SQLite (SSOT)
                                  │
                                  ▼ 03:00 cron
                              YAML エクスポート ──► git commit ──► AIPM repo
```

**Pros**
- トランザクション / JOIN / 複雑クエリが自然
- UI 実装が一番素直（state, order, assignee, estimate, 等を自由に持てる）
- スケーラブル（10000+ BL でも余裕）

**Cons**
- ⚠️ AIPM の SSOT が外に出る。Git で見ても最新 24h が反映されていない可能性
- エクスポート↔インポート整合 bug が一番怖い経路（マスタ差し戻し時に事故りやすい）
- 既存 100 件の BL.yaml を SQLite に移すマイグレーションが大仕事
- 「YAML を直接 vim で 1 文字直す」escape hatch がなくなる
- Cursor のエージェントは SQLite 直接 or HTTP 経由が必要 → 環境依存が増える

**工数感**: 5〜7 週末（マイグレーション含む）

---

### D. ハイブリッド: BL メタは SQLite SSOT / 本文は YAML SSOT

**概要**
- 一覧で必要な軽量フィールド（`state`, `priority`, `due`, `tags`, `column_order`, `last_viewed_at` 等）は SQLite SSOT
- BL の本文相当（`title`, `description`, `decisions[]`, `pending_questions[]`, `deliverable_refs[]`, `cockpit_task_ids[]`）は YAML SSOT
- UI 一覧/カンバンは SQLite から、詳細画面は YAML から
- 書込は API が両方を atomic に更新（または変更領域に応じて片方）

**データフロー**
```
UI / mt CLI / MCP ──► API ──┬──► SQLite（軽量メタ）─► UI 一覧/カンバン
                            └──► YAML（本文/履歴）─► UI 詳細 / git log
```

**Pros**
- 一覧パフォーマンス最強、しかも BL の議論ログは AIPM Git で diff レビュー可能
- 高頻度操作（state 変更, カンバン drag-drop, ソート順記憶）は SQLite だけで完結 → Git noise ゼロ
- 本文（決定事項・質問）は引き続き YAML diff で歴史に残る

**Cons**
- 2 軸の整合性管理が常時必要（教育コスト・テストコスト）
- 「どっちが SSOT？」を文書で常に明示する必要
- マイグレーション中の二重書込み bug 余地

**工数感**: 4〜5 週末

---

### E. Linear 連携（rejected）

**評価のみ・採用しない前提で記載**

- BL.yaml にあるローカル情報（`cockpit_task_ids`, `decisions[].by=ai`, `deliverable_refs`）は Linear のスキーマに自然には乗らない
- ローカル PC でのみ動く agent との連携が Linear API 経由になり遅延・複雑化
- AIPM Git 要件と直交（同期コードを永続的に抱える）
- → **SSOT 候補からは除外**。「外部共有用 read-only mirror」用途に限定可

---

## 4. 比較表

| 軸 | A: YAML据置 | B: YAML+SQLite索引 | C: SQLite SSOT | D: ハイブリッド |
|---|---|---|---|---|
| AIPM Git 適合 | ◎ | ◎ | △（日次） | ○（本文のみ） |
| 一覧パフォ | △（500件で重め） | ◎ | ◎ | ◎ |
| 整合性 | ○（YAML atomic） | ○ | ◎ | △（2軸） |
| 実装工数 | 小 (2-3w) | 中 (3-4w) | 大 (5-7w) | 中-大 (4-5w) |
| 段階移行 | ◎ | ◎ | △ | ○ |
| ロックイン | 無 | 無 | YAML 廃止に近い | 中 |
| Git diff レビュー | ◎ 全部 | ◎ 全部 | △ 日次のみ | ○ 本文のみ |
| カンバン列内順序 | △（YAML に書く） | △（同上） | ◎ | ◎（SQLite） |

---

## 5. 推奨パス: **B から始めて、必要に応じて D に染み出す**

**理由**

1. 現時点で BL は 約 100 件、年内 200〜300 件想定 → A でも回るが、カンバン drag-drop の順序を YAML に書くと Git ノイズが累積する
2. B は YAML SSOT（= AIPM Git 適合）を守りつつ、UI 速度を確保できる → 「AIPM リポで管理したい」を最優先したい人に最適
3. 将来「カンバン列内順序」「ソート設定の記憶」「last_viewed_at」のような high-churn な軽量メタを SQLite SSOT に逃したくなったら、B から D に部分移行できる
4. C は魅力的だが「AIPM リポで管理したい」と本質的に衝突。SSOT を外に出すコストを今払う理由は薄い

**却下したくない論点**
- 「diff レビューで BL の議論履歴を全部追いたい」が strong → B 一択
- 「とにかく速く UI が欲しい、AIPM Git は犠牲にしてもよい」→ C も再検討余地

---

## 6. 段階移行案（B 採用前提）

### Phase 1: 一覧ビュー（1 週末）
- `/backlog` ページ追加: `state` / `priority` / `project` / `tag` フィルタ + 列ソート + 全文検索
- API: `GET /api/backlog/list?state=&project=&q=&sort=...`
- 既存 in-memory index で実装（SQLite はまだ入れない）
- 中央 `Backlog.md` の射影として描画（per-project YAML との整合チェック付き）

### Phase 2: カンバンビュー（1 週末）
- `/board` ページ: 列 = state、列内ソート = priority desc, due asc
- drag-drop で **state 変更のみ**（列内順序は持たない、計算で決める）
- API: `POST /api/bl/<id>/move` で state 遷移
- モバイル UX は「タップ → state 変更モーダル」も用意（drag-drop が iPhone Safari で快適でない場合の代替）

### Phase 3: SQLite 索引化（1 週末）
- better-sqlite3 導入、chokidar → reindex job
- 一覧・カンバンのクエリを SQLite に切替
- in-memory index は backward fallback として残す
- SQLite ファイル: `~/mini-tachyon/data/index.db`（gitignore）

### Phase 4（option）: カンバン列内順序 + 軽量メタを SQLite SSOT 化（1 週末）
- D の発想を局所導入
- `bl_kanban_order` テーブルだけ SQLite SSOT（YAML には書かない）
- `last_viewed_at` / `pinned` 等の view-state 系も SQLite
- これで Git noise を完全に避けつつ UX を上げられる

### Phase 5（option）: 新規 BL 追加 UI（既存 BL-0095 Q2 と統合）
- `/backlog` ヘッダ + `/board` 各列に「+ 新規 BL」ボタン
- モーダル: `title`（必須）/ `project`（必須・autocomplete）/ `category`（自動推定 + override）/ `priority` / `due` / `description`
- 内部で `mt bl create` 相当の API を叩く
- 既存 BL-TBD-007（Phase 3d UI 拡張）のスコープに足すか、独立 BL にするかは別途決定

---

## 7. 別途決めるべき論点

1. **kanban の列定義**
   - 既存 BL state（todo / in_progress / awaiting_user / blocked / completed / planned）をそのまま列にする？
   - 「今日採択」を独立列にすると、列が多すぎて mobile で見にくくなる懸念
   - 案: 列は `todo / in_progress / awaiting_user / done` の 4 列に集約、`blocked` はバッジ表示、`planned` はフィルタで隠す
2. **mobile drag-drop UX**
   - iPhone Safari で快適か検証必要
   - 代替: タップ → ボトムシートで state 選択
3. **BL クローズ UX**（前回議論の宿題）
   - カンバン done 列にドラッグ = BL `completed` 自動遷移？
   - or 「完了確認」モーダルで `decisions` に completion note を append させる？
4. **Backlog.md の扱い**
   - B/D 採用後、Backlog.md は read-only な射影として再生成する vs 完全廃止
   - rule 07 を deprecated 宣言する必要あり
5. **BL-TBD-XXX シリーズ**
   - 既存 placeholder ID を BL-0XXX に renumber するか
   - BL-0095 Q3 で既に未解決 → 本ドキュメントと併せて方針決定
6. **SQLite ファイルの置き場所**
   - 推奨: `~/mini-tachyon/data/index.db`（gitignore）
   - launchd の `WorkingDirectory` 配下で完結
7. **マイグレーション**
   - 既存 100 件の BL.yaml を SQLite に初期 import するスクリプト（B Phase 3）
   - 初回起動時 auto-build で済む設計が望ましい
8. **BL ID 採番の global 化**
   - BL-0095 Q1 と独立だが、本実装と同時に片付けたい
   - 現状は per-project 採番で BL-0001 が複数プロジェクトに存在 → 一覧で区別不能になる

---

## 8. 次のアクション提案

1. 本ドキュメントを mini-tachyon UI でレビュー（done / needs_revision）
2. アプローチ A〜D のどれを採用するか決める（推奨: B）
3. 採用後、§6 の Phase 1 から着手 BL を切る
4. §7 の論点 1〜8 のうち、Phase 1 と並行で決めるべきものを別 deliverable / 別 BL に分解

