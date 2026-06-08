# AI 主導 タスクライフサイクル設計 v2

- 作成日: 2026-06-08
- 起票者: master (Claude)
- 関連 BL: BL-0095「ミニタキオン アップデート (今日着手分)」
- 前バージョン: `d-20260607-001` (`task_lifecycle_proposal.md`)
- 関連 doc: `d-20260605-001` (`backlog_view_implementation_plan.md`) — データ層方針

## 0. v1 からの主な変更

1. **REMOVED ステージを追加** — 2〜5 のいずれの段階からも remove 可能
2. **REVIEW からの分岐を 5 通りに明示** — accept / revise / redefine / re-decompose / remove
3. **CAPTURE チャネルを 4 個に統合** — 思いつき + 外部イベント → ✋ Adhoc
4. **ワークフロー案 α〜ε を廃止** — 1 本の統一ライフサイクルに収束
5. **田中さんの 3 つの決定を反映** — DB+グラフ / AI-drafts-spec / cascade-accept-required

---

## 1. 田中さんの意図（再構成）

- 最近の仕事は AI が実行する形に寄っており、コスト中心は「作業時間」ではなく **レビュー時間 + AI への要件伝達時間** に移った
- 目指す姿は「AI が作業の base、人間はレビュー + 要件定義に専念」
- 人間タッチは **「スコープ/受入基準の判断」と「最終 review」** の 2 点を中心に削減する

---

## 2. タスクライフサイクル（v2: 8 ステージ）

### 2.1 全体図

```
                                                        ┌──→ 8. REMOVED
                                                        │   (2〜5 のどこからでも)
                                                        │
1. CAPTURE → 2. DEFINE → 3. DECOMPOSE → 4. EXECUTE → 5. REVIEW → 6. CLOSE → 7. CASCADE → (1.)
                ↑          ↑              ↑              │
                │          │              │              │
                └──────────┴──────────────┴──── REVIEW からの revise loop（3 通り）
```

### 2.2 各ステージの定義

| # | Stage | 内容 | 人間アクション | Trigger out |
|---|---|---|---|---|
| 1 | **CAPTURE** | 1 行の goal を記録 | アドホックなら 1 タップ、それ以外は自動 | 自動 → DEFINE |
| 2 | **DEFINE** | AI が spec 下書き、田中さんが受け入れ基準を編集 | spec 承認（5〜10 分）👁 | done → DECOMPOSE |
| 3 | **DECOMPOSE** | AI が分解提案、または「1 BL でいい」判断 | 承認 / 修正（1〜5 分）👁 | done → EXECUTE |
| 4 | **EXECUTE** | AI が自律実行、deliverable を産出 | なし | 完了 → REVIEW |
| 5 | **REVIEW** | spec と deliverable を照合 | 1 つ選択（下記 5 通り）👁 | 選択次第 |
| 6 | **CLOSE** | state=completed に遷移 | 自動 | 自動 → CASCADE |
| 7 | **CASCADE** | AI が次 BL 候補を提案 | accept / decline 👁 | accept → CAPTURE |
| 8 | **REMOVED** | 廃棄（履歴は残す） | 1 クリック + 理由 1 行 👁 | 終端 |

👁 = 人間タッチがある段階

### 2.3 REVIEW からの分岐（5 通り）

| 選択 | 行き先 | 用途 |
|---|---|---|
| ✅ accept | 6. CLOSE | OK、完了 |
| 🔄 revise (成果物) | 4. EXECUTE | spec は OK、deliverable だけ書き直し |
| 📐 redefine | 2. DEFINE | spec を変える必要がある |
| 🪓 re-decompose | 3. DECOMPOSE | 分解の切り方が悪い、再分解 |
| 🗑 remove | 8. REMOVED | やはり不要 |

### 2.4 REMOVED と CLOSE の違い

- **CLOSE** = 完了して終わった（success）
- **REMOVED** = 完了せずに止めた（abandoned）
- 別状態にすることで「やった/やめた」を分析可能にする（後で振り返って「reject 率の高いプロジェクト」が見える）
- どちらも履歴としてグラフに残る

---

## 3. CAPTURE のチャネル（4 種、統合済）

| Channel | 事前情報 | Trigger |
|---|---|---|
| 🗣 **Meeting** | 議事録 | meeting 完了後、AI が抽出 |
| ⛓ **Cascade** | 前 BL の deliverable | CASCADE accept |
| 🗂 **WBS** | 親 BL の plan | 親 BL の completion / 開始 |
| ✋ **Adhoc** | 田中さんが入力する 1 行 | 田中さんの 1 タップ（旧「思いつき」+ 「外部イベント」を統合） |

→ 4 チャネルすべてが **DEFINE に合流** する設計は v1 と同じ

---

## 4. 「私の基本フロー」は α〜ε のどれか？

田中さんの記述:
> 基本的にはタスクがあって、それの実行をして、必要に応じてタスクが分解されたり、派生していったり

**回答: 実質 α (spec-first) + JIT decomposition のミックス**。理由:

- DEFINE は AI が書く → 田中さんが受け入れ基準を編集 = **α の核心**
- DECOMPOSE は「必要に応じて」 = **γ の事前固定 WBS ではなく JIT**
- CASCADE はあるが accept 必須 = **δ/ε のような自律 cascade ではない**

→ **5 案を提示したのは early differentiation の過剰最適化だった**。
実装上は 1 本のライフサイクルで十分で、「介入モード」のような切替は不要。
各ステージのデフォルト挙動が田中さんの方針に揃っていれば、案 α〜ε はすべて表現できる。

---

## 5. WBS の扱い（簡素化）

- **WBS = BL の親子関係**（DB のグラフ構造で表現、`parent_id` フィールド）
- 親 BL = マイルストーン / epic 相当
- 子 BL = 実行単位（=1 セッション、1 deliverable）
- 分解は **JIT**（プロジェクト開始時に全部書かない、必要になった時に DECOMPOSE で作る）
- 親 BL の completion 条件: 全子 BL の completion AND 親 BL 固有の受入基準

---

## 6. 田中さんの今回の決定（記録）

| 項目 | 決定 |
|---|---|
| データモデル | **DB + グラフ構造**（parent_id 付き、items はフラットに並列） |
| DEFINE スタイル | **AI が下書き → 田中さんが受け入れ基準を編集** |
| CASCADE 自動度 | **提案のみ、accept 必須** |
| ミーティング inbox | **後回し**（次フェーズ） |

---

## 7. データモデル（概略）

田中さんの「DB + グラフ構造」決定は、前 doc (`backlog_view_implementation_plan.md`) で言うと **案 C (SQLite SSOT)** の方向。
→ 前 doc の推奨 (B: YAML+SQLite 索引) は **C にアップグレード必要**（別途追記する）

### 7.1 テーブル設計（第 1 案）

```sql
-- BL 本体
CREATE TABLE bls (
  id              TEXT PRIMARY KEY,         -- BL-XXXX
  title           TEXT NOT NULL,
  stage           TEXT NOT NULL,            -- captured/defined/decomposed/executing/reviewing/closed/removed
  parent_id       TEXT,                     -- WBS 親 (null = ルート)
  priority        TEXT,                     -- urgent/high/normal/low
  due             DATE,
  project         TEXT,
  category        TEXT,
  tags            TEXT,                     -- カンマ区切り
  created_at      TIMESTAMP,
  updated_at      TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES bls(id)
);

-- Spec (DEFINE の出力)
CREATE TABLE specs (
  bl_id                TEXT PRIMARY KEY,
  goal                 TEXT,
  acceptance_criteria  TEXT,                 -- markdown list
  constraints          TEXT,
  references_md        TEXT,
  approved_at          TIMESTAMP,
  approved_by          TEXT,                 -- user / ai
  FOREIGN KEY (bl_id) REFERENCES bls(id)
);

-- 成果物
CREATE TABLE deliverables (
  id            TEXT PRIMARY KEY,
  bl_id         TEXT,
  file          TEXT,
  review_state  TEXT,                        -- unreviewed/reviewing/done/needs_revision
  created_at    TIMESTAMP,
  FOREIGN KEY (bl_id) REFERENCES bls(id)
);

-- ステージ遷移ログ（履歴・分析用）
CREATE TABLE transitions (
  id          INTEGER PRIMARY KEY,
  bl_id       TEXT,
  from_stage  TEXT,
  to_stage    TEXT,
  reason      TEXT,                          -- REMOVED 時の理由など
  at          TIMESTAMP,
  by          TEXT,
  FOREIGN KEY (bl_id) REFERENCES bls(id)
);

-- 質問
CREATE TABLE pending_questions (
  id          TEXT PRIMARY KEY,
  bl_id       TEXT,
  content     TEXT,
  asked_at    TIMESTAMP,
  resolved_at TIMESTAMP,
  FOREIGN KEY (bl_id) REFERENCES bls(id)
);

-- 決定事項
CREATE TABLE decisions (
  id        INTEGER PRIMARY KEY,
  bl_id     TEXT,
  at        TIMESTAMP,
  type      TEXT,                            -- answer/commitment/scope_change/deferred
  by        TEXT,                            -- user/ai
  content   TEXT,
  FOREIGN KEY (bl_id) REFERENCES bls(id)
);

-- Cockpit task 紐付け（多対多）
CREATE TABLE bl_cockpit_tasks (
  bl_id            TEXT,
  cockpit_task_id  TEXT,
  PRIMARY KEY (bl_id, cockpit_task_id)
);
```

### 7.2 stage と従来 state の関係

旧スキーマでは `state` (todo/in_progress/blocked/awaiting_user/completed/...) を使っていたが、
v2 では **stage** に一本化して以下で表現:

| 旧 state | 新 stage |
|---|---|
| todo | captured / defined / decomposed |
| in_progress | executing |
| awaiting_user | reviewing |
| blocked | (どの stage でも `blocked: true` フラグで表現) |
| completed | closed |
| (新規) | removed |

→ カンバン列も stage 軸（captured / defined / decomposed / executing / reviewing / closed）で並べる

---

## 8. 人間タッチポイントの合計

各ステージのタッチ時間目安:

| Stage | 時間 | 内容 |
|---|---|---|
| 2. DEFINE 承認 | 5〜10 分 | 受入基準の編集 |
| 3. DECOMPOSE 承認 | 1〜5 分 | 「1 BL でいい」も多い |
| 5. REVIEW | 3〜10 分 | spec 照合 + 5 択選択 |
| 7. CASCADE 承認 | 1〜3 分 | 新 BL accept / decline |
| (任意) 8. REMOVED | 30 秒 | 理由 1 行 |

→ 1 BL あたり合計 **10〜30 分** の人間時間。
deliverable サイズが大きい時は REVIEW が伸びる、小さい時は DECOMPOSE が省略される、で実質変動。

---

## 9. mini-tachyon への含意（必要機能）

| 機能 | 既存 | v2 で必要 |
|---|:-:|:-:|
| BL CRUD | ✅ | DB ベースに置換 |
| Spec 構造化フィールド (goal/AC/constraints/refs) | ❌ | ✅ |
| Stage 駆動の状態管理 | △ (state ベース) | ✅ |
| REVIEW 5 択 UI | △ (done/needs_revision のみ) | ✅ |
| 親子 BL 表示（ツリー / WBS view） | ❌ | ✅ |
| カンバン (stage 列) | ❌ | ✅ |
| CASCADE 提案画面 | ❌ | ✅ |
| REMOVED 一覧（理由付き、後で見返せる） | ❌ | ✅ |
| 質問バッチ画面 | △ | ✅ (拡張) |

---

## 10. 開く論点（残り）

決定済 (§6) を除いた残り:

1. **親子関係の表現**: 1 段だけ vs 多段木 vs DAG（複数親）
   - 推奨: 多段木 (parent_id 1 つ、深さ制限なし)
2. **DEFINE スキーマ厳格度**: zod 厳格 vs markdown 自由
   - 推奨: 4 フィールド (goal / AC / constraints / refs) は固定、各値は markdown
3. **CASCADE 提案数の上限**: 1 つ vs 複数
   - 推奨: 最大 3 つまで、田中さんは複数 accept 可
4. **REMOVED の理由カテゴリ**: enum vs free text
   - 推奨: enum (out_of_scope / duplicate / superseded / abandoned / wrong_priority) + free text
5. **DB エンジン**: SQLite vs Postgres
   - 推奨: SQLite（embedded、single user、現状の launchd 運用と相性◎）
6. **stage の数の最終確認**: 7 + REMOVED = 8 で OK か
7. **マイグレーション計画**: 既存 100+ BL.yaml の DB import 手順
8. **DB ファイルの置き場所**: `~/mini-tachyon/data/cockpit.db` (gitignore) で OK か
9. **「stage を巻き戻した」履歴の表示**: transitions テーブルから UI で見せるか
10. **REMOVED 後の復活**: 一度 REMOVED した BL を呼び戻せるか

---

## 11. 次のアクション

1. 本 v2 を mini-tachyon UI でレビュー（accept / revise どちらでも次に進める）
2. § 10 の論点を `pending_questions` として BL-0095 に立てる
3. 前 doc (`backlog_view_implementation_plan.md`) の推奨を C にアップグレードする旨を追記
4. 確定後、以下を別 BL として切り出す:
   - (a) DB スキーマ確定 + マイグレーションスクリプト
   - (b) Spec 構造化フィールドの UI/API
   - (c) Stage 駆動の状態管理への切替
   - (d) 親子 BL / WBS ツリー表示
   - (e) REVIEW 5 択 + CASCADE 提案画面
