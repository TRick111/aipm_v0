---
date: 2026-06-26
moved_to_today: 2026-07-01
purpose: 過去にやったミニタキオン要件・やりたいことの整理し直し（まだ固まっていない）関連ドキュメントへのリンク集
scope:
  - AIPM Flow（フロート）
  - AIPM Stock（ストック）
  - mini-tachyon リポ
note: ルールの見直しは別エージェントで並走中（結果は本ファイル末尾に追記予定）
history:
  - 2026-06-26 元パス Flow/202606/2026-06-26/作業効率化/ミニタキオン/ で作成
  - 2026-07-01 今日の作業フォルダ Flow/202607/2026-07-01/作業効率化/ミニタキオン/ へ移動。相対リンクは新パス基準に修正済み
---

# ミニタキオン 要件・やりたいこと 再整理ドキュメント リンク集

田中さんの依頼で「過去にやった要件ややりたいことの整理し直し（まだ固まっていない）」を、Flow / Stock / mini-tachyon リポから横断して集めた索引。

最新の到達点は **2026-06-08 の v2 三部作**（task_lifecycle_v2 / data_model_and_usecases / usecase_v2_and_dataflows）。ここで止まったまま固まっていない、という前提で並べている。

---

## 1. AIPM Flow（フロート） — 議論・再整理の連続

新しい順。BL-0095「ミニタキオン アップデート (今日着手分)」配下のリサーチメモ群が中心。

### 1.1 2026-06-08（最新到達点・v2 三部作）

- [task_lifecycle_v2.md](../../../../202606/2026-06-08/作業効率化/ミニタキオン/task_lifecycle_v2.md)
  AI 主導 タスクライフサイクル v2。REMOVED 追加 / REVIEW 5 分岐 / CAPTURE 4 チャネル / ワークフロー案 α〜ε を 1 本に収束。**v1（2026-06-07）の後継。**
- [data_model_and_usecases.md](../../../../202606/2026-06-08/作業効率化/ミニタキオン/data_model_and_usecases.md)
  「spec は BL のプロパティで良いか？」の答え（1 テーブル統合推奨）＋ Mermaid ER ＋ ユースケース一覧。
- [usecase_v2_and_dataflows.md](../../../../202606/2026-06-08/作業効率化/ミニタキオン/usecase_v2_and_dataflows.md)
  ユースケース改定（A6/B4/B5/C2/C3/C5/C6/C7/H 多数を削除統合）＋ 主要ユースケースの Mermaid データフロー図。

### 1.2 2026-06-07

- [task_lifecycle_proposal.md](../../../../202606/2026-06-07/作業効率化/ミニタキオン/task_lifecycle_proposal.md)
  「AI が作業の base、人間はレビュー + 要件定義」方針転換を最初にタスクライフサイクルとして整理。複数案併記の思考整理段階（v1）。

### 1.3 2026-06-05

- [backlog_view_implementation_plan.md](../../../../202606/2026-06-05/作業効率化/ミニタキオン/backlog_view_implementation_plan.md)
  BL 一覧 / カンバンが見えない問題への複数案。YAML SSOT を保つか / SQLite に寄せるか / ハイブリッドか。新規 BL 追加を UI で完結させる検討。

### 1.4 2026-06-03（田中さんの悩み 4 件への回答シリーズ）

BL-0095 調査メモ Part 1〜4。田中さんが疑問として投げた点に 1:1 で答え、推奨アクションまで落としている。

- [01_overview_実装とドキュメントの対応.md](../../../../202606/2026-06-03/作業効率化/ミニタキオン/01_overview_実装とドキュメントの対応.md)
- [02_backlog_管理の実態と番号付け矛盾.md](../../../../202606/2026-06-03/作業効率化/ミニタキオン/02_backlog_管理の実態と番号付け矛盾.md)
- [03_aios連携_別リポ_スキル.md](../../../../202606/2026-06-03/作業効率化/ミニタキオン/03_aios連携_別リポ_スキル.md)
- [04_田中さんの悩みへの回答と推奨アクション.md](../../../../202606/2026-06-03/作業効率化/ミニタキオン/04_田中さんの悩みへの回答と推奨アクション.md)

### 1.5 2026-05-03（v1 棚卸し）

- [future_direction_v1.md](../../../../202605/2026-05-03/作業効率化/ミニタキオン/future_direction_v1.md)
  BL-0001 ドラフト。実装状況 / 今後の課題 / 既存機能 / 不在機能 の 4 軸棚卸し。`Stock` 確定反映は別途 = まだ固まっていない。

---

## 2. AIPM Stock（ストック） — 確定 SoT と未確定 BL

`~/aipm_v0/Stock/作業効率化/ミニタキオン/`

### 2.1 ドキュメント

- [STATUS.md](../../../../../Stock/作業効率化/ミニタキオン/STATUS.md)
  Source of Truth。最新は 2026-05-05 更新で Phase 5 完了 + hotfix 完了の状態。**6 月の v2 議論はまだ反映されていない**ので、ここが要件再整理を取り込んでいない最大の論点。
- [USAGE.md](../../../../../Stock/作業効率化/ミニタキオン/USAGE.md)
  利用者向けマニュアル。
- [INTEGRATIONS.md](../../../../../Stock/作業効率化/ミニタキオン/INTEGRATIONS.md)
  監査 + 起動手順。
- [インフラ独立化とTailscale接続問題_2026-05-02.md](../../../../../Stock/作業効率化/ミニタキオン/インフラ独立化とTailscale接続問題_2026-05-02.md)
  ネットワーク・常駐基盤の現状メモ。

### 2.2 backlog — `BL-TBD-*` が「未確定」

「TBD」プレフィックスが付いた BL は、まさに「まだ固まっていない」やりたいこと群。

| ID | タイトル |
|---|---|
| [BL-TBD-001](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-001.yaml) | Phase 1: View-only MVP |
| [BL-TBD-002](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-002.yaml) | (Phase 1 系) |
| [BL-TBD-003](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-003.yaml) | (Phase 系) |
| [BL-TBD-004](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-004.yaml) | (Phase 系) |
| [BL-TBD-005](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-005.yaml) | (Phase 系) |
| [BL-TBD-006](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-006.yaml) | Phase 3c: 03:00 cron + 承認後自動更新 |
| [BL-TBD-007](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-007.yaml) | Phase 3d: UI polish |
| [BL-TBD-008](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-008.yaml) | (Phase 系) |
| [BL-TBD-009](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-009.yaml) | (Phase 系) |
| [BL-TBD-010](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-010.yaml) | (Phase 系) |
| [BL-TBD-011](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-011.yaml) | Phase 4a: API 化 + CLI wrapper (`mt`) |
| [BL-TBD-012](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-TBD-012.yaml) | Phase 4b: エージェント prompt の skill 化移行 |

確定済 BL:
- [BL-0001.yaml](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-0001.yaml) — 今後の方針検討（v1 棚卸しの本籍）
- [BL-0002.yaml](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-0002.yaml)
- [BL-0095.yaml](../../../../../Stock/作業効率化/ミニタキオン/backlog/BL-0095.yaml) — **アップデート（6 月着手分）の本籍 BL**。Flow の 6/03〜6/08 ドキュメント群はすべてこの BL の調査メモ。

---

## 3. mini-tachyon リポ（`~/mini-tachyon/`） — 実装側のメモ

- [docs/UPDATE_IDEAS.md](../../../../../../mini-tachyon/docs/UPDATE_IDEAS.md)
  「思いつきベースのアップデート案メモ」。明示的に「設計が固まり次第、別ドキュメントに整理する想定の作業メモ」と書かれている。**現状は案 1（今日のタスクへのワンクリック導線）のみ。**
- [docs/API.md](../../../../../../mini-tachyon/docs/API.md)
- [docs/CLI.md](../../../../../../mini-tachyon/docs/CLI.md)
- [docs/MCP.md](../../../../../../mini-tachyon/docs/MCP.md)
- [AGENTS.md](../../../../../../mini-tachyon/AGENTS.md)
- [CLAUDE.md](../../../../../../mini-tachyon/CLAUDE.md)
- [README.md](../../../../../../mini-tachyon/README.md)

---

## 4. 関連メモリ（Claude Code 側）

- `~/.claude/projects/-Users-rikutanaka--agi-tools-data-cockpit-master/memory/project_mini_tachyon.md`
  ミニタキオン プロジェクトの概要メモ（Phase 1〜6 計画、設計書 `Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md` への参照あり）。
- `~/.claude/projects/-Users-rikutanaka--agi-tools-data-cockpit-master/memory/feedback_mini_tachyon_canonical.md`
  mt CLI が SoT、AIPM 配下エージェントは INBOX.md / daily_tasks.md を使わず mt 経由で報告する canonical ルール。

> ※ `design_mobile_review_hub.md` は `Flow/202604/2026-04-25/ミニタキオン/` 配下の **04 月時点の設計確定書**。
> 上記メモから参照されているがリンク切れの可能性あり、要 verify。

---

## 5. ざっくり整理：何がまだ固まっていないか

| 観点 | 最新提案 | 確定済 SoT | ギャップ |
|---|---|---|---|
| タスクライフサイクル | `task_lifecycle_v2.md` (2026-06-08, 8 ステージ) | なし | STATUS.md / ルール側に未反映 |
| ユースケース | `usecase_v2_and_dataflows.md` (2026-06-08, A〜I 大幅削減) | なし | データフロー図止まり、UI 設計に未接続 |
| データモデル | `data_model_and_usecases.md` (1 テーブル統合推奨) | YAML SSOT のまま | DB 採用判断未決 |
| BL 一覧 / カンバン | `backlog_view_implementation_plan.md` (複数案併記) | なし | データ層・UI 層とも未決 |
| 朝のタスク表示ロジック | `04_田中さんの悩み...` で「★/☆ 区別」改善案 | 既存実装どおり | UI 反映未着手 |
| 番号付け一貫性 | `02_backlog_管理...` で問題提起 | BL-TBD-* 多数残存 | TBD → 確定への昇格ルール未策定 |

---

## 6. 並走している作業

- 別エージェント（Explore, very thorough）で AIPM ルール（`~/aipm_v0/.cursor/rules/aios/`）の棚卸し完了。結果を以下「7. ルール棚卸し結果」に格納。

---

## 7. ルール棚卸し結果（別エージェント報告, 2026-06-26）

### 7.1 ルールファイル一覧（タスク管理 / ミニタキオン関連の該当区分付き）

| パス | 役割 | 最終更新 | タスク管理 | ミニタキオン |
|---|---|---|---|---|
| `00_aios_core.mdc` | AIOS Core（常時参照）。全体運用と Index ポリシー | 2026-04-27 | ◯（mmdd_daily_tasks.md 記載あり） | ◯（Section 8 で 13 を canonical 指定） |
| `10_aios_ops_router.mdc` | ユーザー意図 → 運用フローのマッピング | 2026-04-27 | ◯ | ◯（13 を canonical 指定） |
| `01_program_init.mdc` | Program 初期化 | 2026-01-17 | — | — |
| `02_project_init.mdc` | Project 初期化 | 2026-01-17 | — | — |
| `03_daily_task_planning.mdc` | **[DEPRECATED 2026-04-26]** 朝のタスク計画 | 2026-04-27 | ◯（廃止） | ◯（旧運用） |
| `04_project_work.mdc` | プロジェクト作業（Flow Draft） | 2026-01-30 | — | — |
| `05_finalize_to_stock.mdc` | Stock 確定反映 | 2026-01-17 | — | — |
| `06_meeting_close.mdc` | 会議終了処理 | 2026-01-17 | — | — |
| `07_backlog_management.mdc` | バックログ管理（Backlog.md SSoT） | 2026-03-22 | ◯ | ◯（13 と混在中） |
| `08_progress_report.mdc` | 日中の進捗報告（daily_tasks.md 更新） | 2026-03-21 | ◯（廃止対象を参照） | — |
| `09_daily_review.mdc` | **[DEPRECATED 2026-04-26]** 終業時の日次振り返り | 2026-04-27 | ◯（廃止） | ◯（夜の運用は 13 へ） |
| `10_weekly_review.mdc` | 週次振り返り | 2026-03-22 | ◯（現役、データソース曖昧） | — |
| `11_monthly_review.mdc` | 月次振り返り | 2026-03-22 | ◯（現役） | — |
| `12_parallel_task_orchestration.mdc` | **[DEPRECATED 2026-04-26]** 並行タスク運用（INBOX/STATUS/daily_tasks 3 ファイル同期） | 2026-04-27 | ◯（廃止） | ◯（旧運用全体） |
| `13_mini_tachyon_protocol.mdc` | **ミニタキオン プロトコル (canonical)** mt CLI / API による状態管理・Daily Loop | 2026-05-05 | ★★★（新 canonical） | ★★★（単一情報源） |

**テンプレート残存:** `STATUS.template.md` / `INBOX.template.md` / `questions_to_user.template.md` が rule 12 廃止後も `.cursor/rules/aios/templates/` に残っている。

### 7.2 タスク管理フローの重複・矛盾

- **A1: `mmdd_daily_tasks.md` の位置付けが不明確**
  - `00_aios_core.mdc` Section 3 では「日次作業フォルダの起点」と書かれているが、Section 8 と rule 03 で廃止扱い。**Section 3 の更新漏れ**。
- **A2: `08_progress_report.mdc` が廃止対象 daily_tasks.md を直接操作**
  - 13（canonical）は mt CLI 経由を指示。08 を参照したエージェントは廃止フォーマットで動く。
- **A3: 週次・月次レビュー（10/11）のデータソースが曖昧**
  - `daily_tasks.md` を読み込む前提だが、13 では新規生成しない。10/11 の入力源が宙ぶらりん。

### 7.3 ミニタキオン (mt CLI) 運用の重複・矛盾・古い参照

- **B1: Backlog.md 管理が 07 と 13 で二重規定**
  - 07: Backlog.md（Markdown 表）を SSoT として手書き編集
  - 13: `mt bl create` で API が atomic 更新
  - 10（router）: 「07 を使え。ただし mini-tachyon 連携必須」 → 三重で指示が分かれている。
- **B2: 質問・決定・成果物のスキーマが 12 と 13 で異なる**
  - 12: `questions_to_user.md` / `INBOX.md` の自由テキスト
  - 13: `mt bl add-question` / `mt bl add-decision`（zod 検証 YAML）
  - rule 13 では「既存 INBOX.md は履歴として残す」と言いつつ、新規エージェントが BL に追加すると二重フォーマットが発生。
- **B3: Deliverable 登録の Flow パスが単層 / 2 層で曖昧**
  - 13 Scenario C で「どちらでも可」とあるが、既存プロジェクトは単層、新規は 2 層の混在リスク。
- **B4: 古い参照切れ**
  - 10_weekly_review.mdc は廃止対象 daily_tasks.md を読み込む前提のまま。

### 7.4 `_orchestration` フォルダの現状扱い

**「部分廃止 / 部分維持」の不安定状態。**

| ファイル | 状態 |
|---|---|
| `_orchestration/INBOX.md` | **廃止済（2026-04-26）** ミニタキオン UI に置換 |
| `_orchestration/STATUS.md` | **廃止済（2026-04-26）** Stock 配下 PROJECT STATUS.md に統一 |
| `_orchestration/<Project>/questions_to_user.md` | **廃止済（2026-04-26）** BL.pending_questions に統一 |
| `_orchestration/今日のタスク案.md` | **新 canonical（rule 13 §3.1）** 朝のエージェント生成、deliverable 登録 |
| `_orchestration/今日の振り返り.md` | **新 canonical（rule 13 §3.2）** 夜のエージェント生成、Stock STATUS にマージ |
| `_orchestration/deliverables.yaml` | **新規定義（rule 13 Scenario C）** `bl_id: null` の Daily Loop 専用、BL 紐付き成果物は書かない |

**根拠**: `00_aios_core.mdc` §8 と `13_mini_tachyon_protocol.mdc` 冒頭で廃止対象が明示されている一方、`00_aios_core.mdc` §3（フォルダ構造）には `_orchestration` の説明が一切ない（更新漏れ）。

### 7.5 推奨リファクタ方向（優先度付き）

- **P0: `00_aios_core.mdc` §3 を現在の canonical に更新**
  `mmdd_daily_tasks.md` を「起点」とする記述を削除し、`_orchestration/` の役割（今日のタスク案 / 振り返り / deliverables.yaml）を追記。
- **P1: `08_progress_report.mdc` を rule 13 に統合 or DEPRECATED 化**
  進捗報告は `mt bl update` に一本化する旨を冒頭で宣言。
- **P2: `07_backlog_management.mdc` と `13_mini_tachyon_protocol.mdc` の責務分離**
  07 を「既存 Backlog.md の参照・抽出・棚卸し」専用に縮退、新規作成・状態変更は 13 に集約。router (10) の「07 + mini-tachyon 連携」表記も 13 単独に修正。
- **P3: 廃止テンプレートを `_deprecated/` 配下に隔離**
  STATUS / INBOX / questions_to_user テンプレートに deprecation notice を付けて移動。
- **P4: rule 13 に埋め込まれた `~/mini-tachyon/lib/prompts/daily-start.md` 等の絶対パスを抽象化**
  AIOS ルール本体には「朝/夜エージェントが何をするか」だけを書き、実装パスは mini-tachyon リポ側に分離。
- **P5: `00_aios_core.mdc` §8 の運用フロー表を「現役 / 廃止予告」で 2 分割**
  廃止対象が ※ 注釈で見落とされやすい。表を分けて廃止予告を目立たせる。

### 7.6 追加所見

- **逆参照の欠落**: 廃止ルール（03/09/12）から canonical（13）への導線がない。廃止ルール冒頭に「新しい正規ルート」セクションを追加して 13 の該当 Scenario を案内すべき。
- **Flow フォルダ構造の決定版が無い**: 単層 / 2 層の混在は `00_aios_core.mdc` §3 で標準を明記して解消する。

### 7.7 結論

現在のルール群は **2026-04-26 の rule 13 導入リファクタの途中段階**で停止している。古いルール（03/09/12）が廃止扱いで残り、`00_aios_core.mdc` の更新漏れと router (10) の不一貫が「タスク管理 / ミニタキオン」周りで矛盾を生んでいる。
P0〜P3 を片付ければ「rule 13 + mini-tachyon が単一情報源」が成立する見込み。
