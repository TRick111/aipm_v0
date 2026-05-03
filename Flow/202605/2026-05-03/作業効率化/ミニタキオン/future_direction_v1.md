# BL-0001 — ミニタキオン 今後の方針検討 v1（実装状況・課題・機能棚卸し）

**作成日**: 2026-05-03
**作成者**: AI (mt cockpit-task-f2830076)
**ステータス**: Draft（田中さん review 待ち、`Stock/作業効率化/ミニタキオン/` への確定反映は別途）
**関連 BL**: BL-0001 (新規) / BL-TBD-006 (Phase 3c) / BL-TBD-007 (Phase 3d) / BL-0067 (INBOX 設計)

---

## 0. 目的

田中さん指示:
> ミニタキオンについてもタスクを進めたい。今の実装状況と今後検討しないといけないことをまとめたい。
> 目的として、(1) 今のミニタキオンの実装状況、(2) 今後の課題、(3) 今存在している機能、(4) 存在していない機能 を整理したい。

本ドキュメントはその「棚卸し+方針検討の v1 ドラフト」。次の意思決定の材料にする。

---

## 1. 経緯と位置付け

| 日付 | マイルストーン | 出典 |
|---|---|---|
| 2026-04-25 | V2 設計確定 (INBOX/daily_tasks 廃止スコープ) | `Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md` |
| 2026-04-26 | Phase 4 (HTTP API + mt CLI + skill-calling prompt) 完了 | `Flow/202604/2026-04-26/ミニタキオン/spec_2026-04-26.md` |
| 2026-04-26 以降 | rule (`13_mini_tachyon_protocol.mdc`) で他エージェントに mt CLI 強制 | `.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| 2026-05-03 | 本 BL 起票・実装状況の棚卸し開始 | (本書) |

ミニタキオンは「**田中さん 1 人の AIPM 運用ハブ** (Tachyon Workspace のミニ版)」。Mac mini に launchd 常駐し、Tailscale 経由で iPhone 一画面で叩ける UX が中核。

---

## 2. アーキテクチャ俯瞰 (As-Is)

```
        ┌────────────────────────────────────────────┐
        │  iPhone / Mac (Safari, Tailscale 経由)       │
        │   - ホーム / 全 BL / 詳細 / Deliverables    │
        │   - 朝のタスク案 / 今日の選択              │
        └──────────────┬─────────────────────────────┘
                       │ HTTP (port 3000)
        ┌──────────────▼─────────────────────────────┐
        │  Next.js 15 App (Bun + React)               │
        │   app/                                      │
        │   ├ page.tsx (ホーム)                       │
        │   ├ backlog / bl/[id] / projects/[slug]     │
        │   ├ deliverables/[id] / past-operations     │
        │   └ api/ (REST: bl, deliverables,           │
        │           cockpit, today, projects,         │
        │           morning, evening)                 │
        ├─────────────────────────────────────────────┤
        │  lib/                                       │
        │   ├ yaml.ts / lock.ts (proper-lockfile)     │
        │   ├ flow.ts / stock.ts / index-store.ts     │
        │   ├ orchestration.ts / today-selected.ts    │
        │   ├ cockpit.ts / fallback-instruction.ts    │
        │   ├ markserv.ts (MD レンダリング)           │
        │   ├ prompts/ (daily-start.md, daily-wrapup) │
        │   └ migrate.ts / merge.ts / triage.ts ほか  │
        ├─────────────────────────────────────────────┤
        │  bin/mt (CLI ラッパ → 上記 API を叩くだけ)   │
        ├─────────────────────────────────────────────┤
        │  AGI Cockpit (Electron, 別プロセス)          │
        │   - エージェントを spawn / send / resume     │
        └──────────────┬─────────────────────────────┘
                       │ ファイル監視 (chokidar)
                       ▼
        ┌─────────────────────────────────────────────┐
        │  AIPM ファイルシステム (~/aipm_v0/)          │
        │   - Stock/<cat>/<proj>/backlog/BL-XXXX.yaml │
        │   - Stock/定型作業/バックログ/Backlog.md    │
        │   - Stock/<cat>/<proj>/STATUS.md            │
        │   - Flow/YYYYMM/YYYY-MM-DD/...              │
        └─────────────────────────────────────────────┘
```

---

## 3. 実装済み機能 (As-Is) — 詳細

### 3.1 BL ライフサイクル

- **新規作成**: `POST /api/bl` (`mt bl create`) — id 自動採番 / 明示両対応、per-project YAML 自動配置
- **状態遷移**: `PATCH /api/bl/:id` (`mt bl update`) — `pending|in_progress|awaiting_user|looping|planned|completed|blocked` 7 値
- **decision 追加**: `POST /api/bl/:id/decisions` — `answer|commitment|scope_change|deferred` × `user|ai`
- **質問追加**: `POST /api/bl/:id/pending-questions` — `pending_questions[]` に append、UI で田中さん表示
- **質問 consume**: `DELETE /api/bl/:id/pending-questions/:qid` — 単純削除 (decision なし) or `add-decision --answers-question-id` 経由で同時消費
- **list/filter**: `GET /api/bl?state=&project=&ids=&today_selected=1` — 朝採択集計に `today_selected` あり
- **get**: `GET /api/bl/:id` — central Backlog.md fallback も対応

### 3.2 Deliverable ライフサイクル

- **state 遷移**: `PATCH /api/deliverables/:id/state` — `unreviewed|reviewing|done|needs_revision|generating`
- **comment 追加**: `POST /api/deliverables/:id/comments`
- **get**: `GET /api/deliverables/:id`

### 3.3 Daily Loop

- **朝の整理**: `POST /api/morning/start` → `lib/prompts/daily-start.md` を cockpit に spawn → 「今日のタスク案.md」生成 → `mt deliverable update-state ... unreviewed`
- **朝の確定**: `POST /api/morning/finalize` — `--selections '[{bl, action, spawn_class}]'` で採択 BL の状態更新 + クラス A の cockpit spawn + cockpit_task_ids 連携 (atomic)
- **夜の振り返り**: `POST /api/evening/start` → `lib/prompts/daily-wrapup.md` を spawn → `今日の振り返り.md` 生成 → `lib/merge.ts` で Stock STATUS.md マージ

### 3.4 Cockpit 連携

- `POST /api/cockpit/tasks` — 新規 spawn (`instruction, directory, agent-type, name, bl`)
- `POST /api/cockpit/tasks/:tid/send` — 既存タスクへの送信 (3 段 fallback: send → resume → create)

### 3.5 中央集約クエリ

- `GET /api/today/selected` — 朝 [x] 採択 / 今日の decisions / ミニタキオン own active を合算
- `GET /api/projects` — プロジェクト + active BL 数
- `GET /api/bl/...` 全 filter 対応

### 3.6 永続化・整合性

- **proper-lockfile** で YAML / Backlog.md の atomic write
- **zod validate** で全 body / response を検証 (schema 違反は 400)
- **chokidar watcher** で AIPM ファイル変更を即時 UI 反映
- **central-fallback**: per-project YAML がない BL でも中央 Backlog.md から読める

### 3.7 エージェント支援

- `lib/prompts/daily-start.md` (朝のエージェント固定プロンプト)
- `lib/prompts/daily-wrapup.md` (夜のエージェント固定プロンプト)
- `lib/fallback-instruction.ts` — Deliverable 承認 → finalize agent spawn の橋渡し
- `lib/mt-agent-prompt.ts` — エージェント呼出時のプロンプト整形
- `.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` で他エージェントに mt CLI 強制 (rule-following → skill-calling 転換)

### 3.8 UI ページ

| ルート | 役割 |
|---|---|
| `/` ホーム | 「📅 今日の運用」「🔥 今日の選択」「🚀 active BLs」「✅ unreviewed deliverables」 |
| `/backlog` | 全 BL 表 (filter / sort) |
| `/bl/[id]` | BL 詳細 (decisions / pending_questions / deliverable_refs / 操作ボタン) |
| `/deliverables/[id]` | 成果物 (markdown レンダリング via markserv) + comment + state 操作 |
| `/projects/[slug]` | プロジェクト詳細 (active BL 一覧 / STATUS.md preview) |
| `/past-operations` | 過去の Daily Loop アーカイブ (Phase 3d 着手中) |

### 3.9 開発支援

- vitest 単体テスト (172/172 pass、4/27 時点)
- bun + Next.js 15 (App Router、Turbopack ベース)
- launchd plist (`launchd/jp.agi-tools.mini-tachyon.plist`) で port 3000 常駐

---

## 4. 未実装 / 部分実装 機能 — ギャップ分析

### 4.1 既知ギャップ (rule 13 / 既存 BL に明記済)

| # | ギャップ | 関連 BL / 出典 |
|:-:|---|---|
| 1 | **deliverable register API** が未実装 → エージェントが `deliverables.yaml` を直接書く運用 | rule 13 §5.A Scenario C |
| 2 | **bl_id 逆引き機構なし** → 中央 Backlog.md 由来 BL は deliverable_refs を持てない | BL-0070 q-6 / rule 13 |
| 3 | **central-only BL の per-project YAML 昇格 API なし** → 0-byte placeholder ができてしまうと CLI が読めない (今日 BL-0077/0066/0059/0030/0042/0043 で発生) | (本日発見) |
| 4 | **03:00 cron + 承認後自動更新 (Phase 3c)** が in_progress | BL-TBD-006 |
| 5 | **「📅 今日の運用」 UI 拡張 + 「📚 過去の運用」リンク (Phase 3d)** が in_progress | BL-TBD-007 |
| 6 | **INBOX 設計再検討 (Cockpit 統合・対応優先度可視化)** | BL-0067 |
| 7 | **🌙 押し忘れ → 03:00 cron 自動 endDailyLoop** | rule 13 §3.4 (未着工) |

### 4.2 本日新規発見ギャップ

| # | 内容 | 影響 | 優先度 |
|:-:|---|---|---|
| 8 | **0-byte placeholder の自動修復** がない (central → project YAML 移行の途中状態) | 該当 BL の state/decision 操作が IO エラーで通らない | **高** (新規エージェント着手前提) |
| 9 | `mt bl update --state cancelled` が未対応 (`completed` で代用) | 「キャンセル」が「完了」と区別不能 | 中 |
| 10 | エージェントが `cancelled` を意図しても明示できない | 振り返り精度に影響 | 中 |
| 11 | `spawn_class` が `A` 固定の説明が docs に薄い (B/C 起動経路) | 朝の finalize で A 並列のみで完結 | 中 |
| 12 | Daily wrapup のドラフト存在チェック (前日 wrap-up なし時の挙動) のフォールバックが暗黙 | 朝のエージェントが「履歴なし」モード判定する余地 | 低 (動く) |

### 4.3 戦略的に考えるべき機能 (まだ無いが入れる候補)

| # | 提案機能 | 価値 | 概算工数 |
|:-:|---|---|---|
| α | **deliverables 一覧ビュー** (`/deliverables` index、unreviewed/needs_revision フィルタ) | iPhone レビュー導線が更に短くなる | S |
| β | **検索 (BL / Deliverable / プロジェクト横断 keyword search)** | BL 数が 80+ になっても見失わない | M |
| γ | **複数日跨ぎビュー** (この BL は何日連続で today selected? 何回 deferred?) | 滞留 BL の早期発見 | M |
| δ | **モバイル向け音声入力 / 音声 commit** (Deliverable comment / BL decision を声で) | iPhone 操作の体感が劇的に改善 | M |
| ε | **Cockpit task 状況の常時可視化** (どのエージェントが今走ってるか、完了見込み) | 並列起動した時の追跡コスト削減 | M |
| ζ | **MasterIndex / ProjectIndex 自動更新** (確定反映時に MasterIndex.yaml 等を AI に touch させる) | AIOS 6.1 ルールの自動化 | L |
| η | **STATUS.md の自動 sync** (BL state 変更時に STATUS の `current_bl` を自動更新) | rule 13 §5.A Scenario D の手作業を解消 | M |
| θ | **Cockpit 失敗時の Slack/LINE 通知** | エージェント停止に気づかない問題の解決 | S |
| ι | **bl create 時の重複検知 (タイトル類似)** | BL の二重起票を防ぐ | S |
| κ | **「自分宛て pending_questions」一覧** (横串 INBOX 代替) | 田中さんの「次なに」を 1 ページに集約 | M (BL-0067 と統合) |

### 4.4 運用ポリシー上の検討事項 (機能というより方針)

- A. **"キャンセル"概念の正式化**: state enum に `cancelled` を追加するか、`completed` に統一して decision で区別するかの判断
- B. **「今日のタスク案 v1/v2/v3」の差分管理**: 今日のように複数版が出る場合の review_log 表現
- C. **central Backlog.md vs per-project YAML の役割分担**: 今後すべて per-project YAML に寄せるか、中央台帳と二重管理を続けるか (今日発見した 0-byte placeholder 問題は二重管理の副作用)
- D. **prompt-as-code か prompt-as-content か**: `daily-start.md` のような prompt を `Stock/...` 配下の MD として共有財化するか、`lib/prompts/` に閉じ込めるか
- E. **「今日の選択」の自動再採点**: 24h を超えた today_selected を自動でクリア / 再評価する仕組み
- F. **マルチユーザー化**: 田中さん 1 人 → 将来チーム展開する時に必要な切替軸 (ownership / project visibility)

---

## 5. 優先度ロードマップ案 (推奨)

### Sprint 0 — 衛生 (今週末〜来週前半)

- 0-1. 0-byte placeholder 自動修復 (Section 4.2 #8) — bootstrap on read
- 0-2. `cancelled` state を enum に追加 → 旧 `completed (キャンセル意図)` を decision で識別 (Section 4.2 #9-10)
- 0-3. deliverable register API (Section 4.1 #1) — エージェントが `deliverables.yaml` を直接編集しなくて済む
- 0-4. `mt bl create` 時の重複タイトル warning (Section 4.3 ι)

### Sprint 1 — 既存 in_progress の完了 (5/3〜5/10)

- 1-1. Phase 3c: 03:00 cron + 承認後自動更新 (BL-TBD-006)
- 1-2. Phase 3d: 「📅 今日の運用」 UI 拡張 + 「📚 過去の運用」 (BL-TBD-007)
- 1-3. INBOX 設計の再検討 → 「自分宛て pending_questions」一覧 (BL-0067 + 4.3 κ で統合)

### Sprint 2 — レビュー導線・横串 UX (5/10〜5/24)

- 2-1. `/deliverables` index ビュー (Section 4.3 α)
- 2-2. 検索機能 (Section 4.3 β)
- 2-3. 複数日跨ぎビュー (Section 4.3 γ)
- 2-4. STATUS.md 自動 sync (Section 4.3 η)

### Sprint 3 — モバイル UX 強化 (5/24〜)

- 3-1. 音声入力 (Section 4.3 δ)
- 3-2. Cockpit 進捗の常時可視化 (Section 4.3 ε)
- 3-3. 通知拡張 (Section 4.3 θ)

### Backlog (まだ熟していない)

- ζ MasterIndex 自動更新
- F マルチユーザー化
- D prompt-as-code 整理

---

## 6. 田中さんへの確認事項

- [ ] **Sprint 0 の優先順位**: 4 つの衛生タスクを今週中に着地させる方向で OK?
- [ ] **キャンセル状態**: state enum に `cancelled` を追加 (推奨) vs `completed + decision` で運用する 折衷案、どちらが好み?
- [ ] **INBOX 再設計の方向性 (BL-0067)**: 4.3 κ「pending_questions 横串一覧」を最終形にするでよいか?
- [ ] **deliverable register API**: 設計を本 BL の deliverable として続けるか、独立 BL に切り出すか?
- [ ] **本 BL のスコープ**: 棚卸しドキュメントとして本 BL を completed にして、各課題は個別 BL に切り出していくか? もしくは「方針検討」を継続トラッキングする使い方か?
- [ ] **Stock 反映**: 本ドラフトを `Stock/作業効率化/ミニタキオン/future_direction_v1.md` に確定反映するタイミング (今日 / Sprint 0 完了後 / 月次)?

---

## 7. 関連ファイル

- 仕様書: `Flow/202604/2026-04-26/ミニタキオン/spec_2026-04-26.md`
- V2 設計書: `Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md`
- API 仕様: `~/mini-tachyon/docs/API.md`
- CLI 仕様: `~/mini-tachyon/docs/CLI.md`
- ルール: `.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc`
- 既存 BL: BL-TBD-006 / BL-TBD-007 / BL-0067
- 実装: `~/mini-tachyon/`
