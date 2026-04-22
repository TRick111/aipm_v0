# BL-0053 AIOSアップデート（G-Brain統合 + ルール全体見直し） 探索メモ

- 作成日: 2026-04-22
- 担当: 田中利空
- 関連: BL-0053（本タスク・要件詰め） / BL-0054（共用リポジトリ設計・doing、BL-0053完了が前提） / BL-0061（AI-Core PL、PONさん案件方式のStock分離運用を先行導入） / BL-0063（OMI×AIOS統合・検討）
- 状態: **要件詰めフェーズ**（実装は別タスクで起動予定）

---

## 0. 本タスクで「詰める」対象

バックログの現定義は「AIOSアップデート（G-Brain統合 + ルール全体の見直し）」までしか無い。**「アップデート」が何を含むのか** がまず決まっていないので、本 discovery では以下の順で材料を揃える:

1. 現状AIOSルールの棚卸し（粒度・整合性・最近の変更差分）
2. G-Brainの理解（何者か／どこにあるのか／統合とは何か）
3. 論点の抽出（決めるべき軸）
4. 後続 `scope_proposal.md` で3案に落として **ユーザーに選んでもらう**

---

## 1. 現状AIOSルールの棚卸し

### 1.1 ルートファイル（常時参照）

| パス | サイズ | 役割 | 備考 |
|---|---:|---|---|
| `.cursor/rules/aios/00_aios_core.mdc` | 7.7KB | **alwaysApply: true** の核。フォルダ構造 / 参照導線 / Stock更新ポリシー / Index YAMLスキーマ方針 / 運用フロー一覧 | 2026-04-09 最終更新 |
| `.cursor/rules/aios/10_aios_ops_router.mdc` | 2.1KB | ユーザー意図→ops ルール のマッピング表。alwaysApply: false | 2026-04-09 最終更新 |

### 1.2 ops/ 配下（必要時参照・12本）

| 番号 | ファイル | サイズ | 役割 | 最終更新 |
|:---:|---|---:|---|---|
| 01 | `01_program_init.mdc` | 1.7KB | プログラム初期化（Stock/<Program>/作成 + MasterIndex追記） | 2026-01-26 |
| 02 | `02_project_init.mdc` | 2.2KB | プロジェクト初期化（README/ProjectIndex/log 生成 + MasterIndex登録） | 2026-01-26 |
| 03 | `03_daily_task_planning.mdc` | 8.5KB | 朝のタスク計画（AI提案型 / ABC+保留分類 / クラスA詳細要件 / questions_to_user.md 仕様） | **2026-04-22** |
| 04 | `04_project_work.mdc` | 1.7KB | Flow成果物生成（対話→ドラフト）。Stock直接編集禁止 | 2026-01-30 |
| 05 | `05_finalize_to_stock.mdc` | 1.7KB | FlowからStockへ確定反映。MasterIndex/ProjectIndex/README/log 同時更新 | 2026-01-26 |
| 06 | `06_meeting_close.mdc` | 1.3KB | Meetings保存＋関連README追記（Indexは触らない） | 2026-01-26 |
| 07 | `07_backlog_management.mdc` | 2.9KB | Backlog.md（単一のMarkdown表）＋ `backlog_tools.py` | 2026-04-09 |
| 08 | `08_progress_report.mdc` | 1.7KB | 日中の進捗報告（シングルタスク・次のタスク提示） | 2026-03-21 |
| 09 | `09_daily_review.mdc` | 3.8KB | 終業時の日次振り返り（予実・目標ログ・3問ランダム・申し送り） | 2026-03-23 |
| 10 | `10_weekly_review.mdc` | 2.6KB | 週次レビュー | 2026-03-22 |
| 11 | `11_monthly_review.mdc` | 3.0KB | 月次レビュー | 2026-03-21 |
| 12 | `12_parallel_task_orchestration.mdc` | **8.3KB** | **並行タスク運用**（`_orchestration/STATUS.md` と `INBOX.md`、マスター＝ルーター/状態管理者、トリガーワード、フロー図） | **2026-04-22**（新設） |

### 1.3 templates/ 配下（9本）

| ファイル | 役割 | 備考 |
|---|---|---|
| `MasterIndex.template.yaml` | プログラム/プロジェクトのカタログ | 2026-01-26 |
| `ProgramREADME.template.md` | プログラムREADME（背景/目的/関係者） | 2026-01-26 |
| `README.template.md` | プロジェクトREADME（人間向け入口） | 2026-01-26 |
| `ProjectIndex.template.yaml` | プロジェクト内のファイル参照カタログ（AI向け） | 2026-01-26 |
| `log.template.md` | 変更履歴（軽量・任意フィールド） | 2026-01-26 |
| `STATUS.template.md` | 並行タスクのダッシュボード | 2026-04-22（新設） |
| `INBOX.template.md` | 未対応事項 + 質問/回答欄（一次受け） | 2026-04-22（新設） |
| `questions_to_user.template.md` | タスク固有の質問ログ（任意・アーカイブ用） | 2026-04-22 |

### 1.4 観察された構造・粒度の特徴

- **ルール=Markdown(`.mdc`)**、**データ=YAML(MasterIndex/ProjectIndex)**、**成果物=Markdown**。ファイル駆動でロックイン無し
- **ops 配下の並びは ID順＝利用頻度順** ではなく、フェーズ順（初期化→作業→確定→会議→管理→レビュー）
- **alwaysApply は 00_core のみ**。残りは router 経由で必要時に読み込み（コンテキスト節約のため）
- ルールの **前提（何を守るか）とゴール（完了条件）** がファイルごとに明示されている。AIのチェックリストとして機能
- 03_daily_task_planning が最大（8.5KB）。計画ルールにABC分類・A化のための3項目・質問運用まで全部入り → **役割過多** の疑い
- 12_parallel_task_orchestration（8.3KB）は直近新設。**03との責務重複**（両方に questions_to_user.md の仕様が書かれている）
- テンプレート群に **連番プレフィックスがなく**、参照順序が分かりにくい

### 1.5 最近の変更（2026-04 月 内）

| 日付 | 変更 | 意図（推定） |
|---|---|---|
| 2026-04-09 | `00_aios_core.mdc` / `10_aios_ops_router.mdc` / `07_backlog_management.mdc` を更新 | Backlog運用の追加、coreへの統合 |
| 2026-04-22 | `12_parallel_task_orchestration.mdc` 新設 | 並行タスク運用（クラスAを複数エージェントで同時実行する体制）の導入 |
| 2026-04-22 | `INBOX.template.md` / `STATUS.template.md` 新設、`questions_to_user.template.md` 更新 | 並行運用に対応した質問一次受けの集約先を INBOX に統一 |
| 2026-04-22 | `03_daily_task_planning.mdc` 更新 | ABC+保留分類、A化のための3項目、背景READMEの強制読込み、クラスA詳細要件セクションの追加 |

→ **この1週間で並行運用系が一気に追加された**状態。ルール全体として **整合性の再点検** の時期に入っている。

---

## 2. G-Brainの理解（現時点で分かっていること／分かっていないこと）

### 2.1 既知情報

| 項目 | 内容 | ソース |
|---|---|---|
| 呼称 | **G-Brain**（= 「大地さん共有ライブラリ」） | `Backlog.md` BL-0053 Notes |
| 保有者 | **町田大地さん**（Restaurant AI Lab AI担当） | メモリ `restaurantailab_team.md`、BL-0053 Notes |
| 位置づけ | 「共有ライブラリ」 | 同上。ただし *コードライブラリ* か *ナレッジ/ルールライブラリ* かは未確定 |
| 旧定義との関係 | 旧BL-0053 は「AIコア共有ライブラリ統合」。現BL-0053 は **それを包含した上で AIOSルール全体見直しまで拡張** | Backlog Notes |
| 2026-04-21 の日次 | タスク#3「AIコアと大地さん共有ライブラリの統合タスク整理（45m・BL-0053）」が計画にあった（当日は未着手で残った） | `Flow/202604/2026-04-21/0421_daily_tasks.md` |

### 2.2 探索結果（本日2026-04-22実施）

- `grep -r "g-brain\|gbrain\|g_brain\|大地さん" /Users/rikutanaka/aipm_v0/` → **aipm_v0側での言及は本 BL-0053 周辺のみ**（Backlog / 本日の daily_tasks / STATUS / AI-Core discovery）。実体なし
- `find /Users/rikutanaka -iname "*g-brain*"` → **ローカルに該当ディレクトリ無し**
- `/Users/rikutanaka/RestaurantAILab/`（実装リポ群）配下に g-brain / gbrain / g_brain を含むリポ無し（14リポ確認）
- `/Users/rikutanaka/RestaurantAILab/Markdowns-1/`（成果物リポ）にも言及なし

→ **G-Brain本体は田中さんのローカル資産ではない**。大地さんのローカル／別リポ／GitHub private 組織リポのいずれかに存在する前提で話を進める必要がある。**BL-0053の要件詰めは「田中さんだけでは完結しない」** — 大地さんへのヒアリング（もしくは共有依頼）が最初のブロッカーになる。

### 2.3 「統合」の取りうる意味（仮置き）

G-Brainが何物かにより、"統合" の意味が大きく変わる。現時点での仮置きタクソノミー:

| G-Brainの実体 | "統合" の意味 | AIOS側の想定改修 |
|---|---|---|
| (α) **AI向けルール/プロンプト集**（Cursor rules / Claude Code 用 instructions 等） | AIOSルール本体に内容を取り込む、または参照する | `.cursor/rules/aios/` へのマージ／別ディレクトリ併置／外部参照パス追加 |
| (β) **コード共有ライブラリ**（TypeScript / Python パッケージ等） | AI-Core 配下のプロジェクトが `npm install` / `pip install` で共通利用できる状態にする | AIOSは **直接は関与しない**。BL-0054（共用リポ設計）の管轄に寄る。AIOSは「共有ライブラリを使う時の運用ルール」を1〜2条追加する程度 |
| (γ) **ナレッジ/ドキュメント集**（Markdownノウハウ・事例・テンプレ） | Stock/ 配下に program として取り込む、または参照リンクを整備 | MasterIndex への追加。`Stock/<Program>/` の新設 or 外部リポへのポインタ |
| (δ) **ツール/スクリプト集**（CLI / automation scripts） | コマンド実行をAIOS運用ルールが呼び出せるようにする | ops に運用呼び出しを1本追加、Stockにコマンドカタログを置く |
| (ε) **上記の複合** | 役割ごとに (α)〜(δ) を使い分け | 複合的な改修が必要 |

→ **G-Brainが (α)〜(ε) のどれかを特定すること** が、本タスクの最初の質問になる。

---

## 3. 「ルール全体の見直し」で潜在的に論点になりそうな箇所

現状AIOSの棚卸しから、「G-Brain統合」と切り離しても改善余地が見える箇所:

### 3.1 responsibility重複 / 粒度不均衡

- **03_daily_task_planning と 12_parallel_task_orchestration の責務重複**
  - `questions_to_user.md` のフォーマット定義が両方に存在
  - マスター役／エージェント役／ユーザー役の区別が 12 側でしか明示されていない
  - `INBOX.md` 一次受けルールが 12 に追加されたが、03 側は旧記述（questions_to_user.md 中心）のまま → **エージェントが混乱する可能性**
- **05_finalize_to_stock と 06_meeting_close の差分が小さい**
  - どちらも「保存 + README/log更新」。Index更新の有無だけが違う。1本に統合してバリアント注記で足りるかも
- **日次/週次/月次レビュー（09/10/11）のフォーマットが似すぎ**
  - weekly → monthly は集計単位が違うだけ。テンプレート化してルールを短くできる

### 3.2 ルール名・ディレクトリ構造

- ops のナンバリングは「1桁で12番」まで到達。今後13,14 …と増える想定なら **0埋め（01〜99）** に揃えるべき（現状は 01〜12 で既に0埋め風だが、番号の意味付けは曖昧）
- `aios/templates/` に INBOX/STATUS 等が混在。**「日次運用テンプレ」と「プロジェクト/プログラム初期化テンプレ」** でサブディレクトリに切ると見通しが良い

### 3.3 マルチリポ横断運用の整備

- 現状AIOSは **`aipm_v0` 単一リポ前提** の書きぶり
- 実運用では既に:
  - `~/RestaurantAILab/Markdowns-1/`（成果物リポ、AI-Core master）
  - `~/RestaurantAILab/ai-core-pl/`（実装コード、BL-0061で新設）
  - `~/RestaurantAILab/Dashboard/` 等の実装リポ群
  - **G-Brain（所在不明だが明確に aipm_v0 外）**
- **BL-0061 で確立した「PONさん案件方式」**（aipm_v0はメタ/タスク管理、実体は別リポ）が既に1例発生 → 一般化してルール化する候補
- BL-0054（共用リポジトリ設計）が先行 doing になっているが **「BL-0053完了が前提」** と本日の daily_tasks に明記されている → AIOSが「マルチリポ運用の型」を先に定めないと BL-0054 は落とし所が決められない

### 3.4 外部ライブラリ/外部ルールの取り込み型がない

- Cursor Rules を外部パッケージ化して pull する仕組みは Cursor 側にはない（2026-04時点。`.cursor/rules/`配下に直接配置する方式）
- G-Brainがルール集だった場合、**コピー vs 参照 vs submodule/symlink** の意思決定が必要

### 3.5 後方互換性

- 既存 Flow/Stock の中身（過去のREADME/Index/log）はルール変更を前提にしていない
- ルール本文や命名規則を変えると、**過去分ファイルが新ルールに違反する状態** が発生
- "過去分は現状維持 / 新規だけ新ルール適用" という運用ルール（migration policy）が必要

---

## 4. 隣接バックログとの関係

| BL | 状態 | 本タスクとの関係 |
|---|---|---|
| BL-0054 共用リポジトリ・ファイル共有設計 | doing | **BL-0053完了が前提**（0422 daily_tasks / backlog Notes）。AIOS がマルチリポ運用の型を決めないと BL-0054 の設計範囲が定まらない |
| BL-0061 AI-Core PL 作成 | doing（実装フェーズ） | **PONさん案件方式の先行事例**（aipm_v0はメタ・実体は別リポ）。このパターンを AIOS ルールに昇格させるかが論点 |
| BL-0063 OMI と AIOS の統合検討 | todo | 外部入力（OMIデバイス→音声→AIOS）の設計。AIOS側に「外部入力の取り込み型」がないと詰まる可能性 |

---

## 5. 決めないと前に進まないこと（論点リスト）

A. **スコープ（最大の論点・3案提示予定）**
   1. 最小: G-Brain統合の型だけ定義
   2. 中間: G-Brain統合 + AIOSルール整合性リファクタ
   3. 最大: AIOS再設計（マルチリポ運用の型を含む全面改定）

B. **G-Brainの実体特定（スコープ確定の前提）**
   - 大地さんから内容/所在を聞く必要がある（田中さんのローカルに無い）
   - タクソノミー (α)〜(ε) のどれに相当するかを特定する

C. **統合方式**
   - コピー（AIOS内に取り込む）／参照（外部パスを記載）／混在
   - G-Brainと AIOS のどちらを master とするか、同期方針

D. **後方互換性方針**
   - 過去分は現状維持のみ（新規だけ新ルール）
   - 過去分も一括マイグレーション
   - マイグレーションスクリプトを用意

E. **責務重複の解消**
   - 03（日次計画）と 12（並行運用）のうち、**並行運用側に寄せる** のか **日次計画を主にして12 を補足に格下げ** するのか

F. **いつやるか / 誰がやるか**
   - 大地さんとのすり合わせが不可欠なら、本タスクは **田中さん単独では Phase 1（棚卸し + たたき台）までしか進められない**
   - Phase 2（G-Brain実装統合）は大地さん合流後

---

## 6. 参照ファイル一覧（本タスクで読み込んだもの）

- `.cursor/rules/aios/00_aios_core.mdc`
- `.cursor/rules/aios/10_aios_ops_router.mdc`
- `.cursor/rules/aios/ops/01_program_init.mdc` 〜 `12_parallel_task_orchestration.mdc`
- `.cursor/rules/aios/templates/*.{md,yaml}`（9ファイル）
- `Stock/定型作業/バックログ/Backlog.md`（BL-0053 / BL-0054 / BL-0061 / BL-0063）
- `Stock/MasterIndex.yaml`（先頭部、現状のProgram/Project構造確認）
- `Flow/202604/2026-04-21/0421_daily_tasks.md`（BL-0053 タスク#3 の初出）
- `Flow/202604/2026-04-22/0422_daily_tasks.md`（BL-0053 今日扱い）
- `Flow/202604/2026-04-22/_orchestration/{INBOX,STATUS}.md`
- `Flow/202604/2026-04-22/AI-Core/{discovery_notes,implementation_plan}.md`（G-Brain言及・PONさん案件方式の発生源）

## 7. 次アクション（本タスク内）

1. `scope_proposal.md` を作成（案A/B/C・メリデメ・所要時間・前提条件）
2. `_orchestration/INBOX.md` に 🟡確認・判断 として **「BL-0053 AIOS+G-Brain統合」** セクションを追加。最初の質問は **スコープ選定**、追加質問はG-Brain特定と分担方針の必要最小限
3. ユーザー回答後 → `implementation_plan.md` を作成し `waiting_confirmation` で承認依頼
