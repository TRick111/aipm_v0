# AIOS 連携 / 別リポ連携 / スキル登録内容

> 田中さんの悩み「AIOS の中身をタスクがどれぐらい読み込んでいるか」「ダッシュボードが別リポなのにどう動いているか」「スキルに何が登録されているか」への直接回答。  
> BL-0095 調査メモ Part 3。

---

## TL;DR

- **AIOS rule 13 は エージェントの prompt に「絶対パスで参照しろ」と書いてあるだけ。本文は inject されていない**。つまり「エージェントが rule 13 を読みに行くかは AI の judgment 次第」。
- **Stock の生データ (BL.yaml / Backlog.md / STATUS.md) は mt CLI 経由で取れる**。が、AIOS の他ルール (例: rule 04 / 05 / 07) は **誰も自動で読み込まない**。
- **ダッシュボード等の別リポは ミニタキオンから完全に不可視**。BL.yaml と STATUS.md は `~/aipm_v0/Stock/RestaurantAILab/ダッシュボード改/` に置かれ、code は `~/RestaurantAILab/Dashboard*` に置かれる二重構造。エージェントは spawn 時の `directory` で AIPM_ROOT に固定されている。
- **スキル `~/.claude/skills/mini-tachyon/SKILL.md` の中身は「経路の選び方」「4 つの絶対遵守ルール」「ユースケース別の tool 呼び方」**。BL の具体的な状態や AIOS rule は含まない。

---

## 1. エージェント spawn 時に何が prompt に乗るか

実装: `~/mini-tachyon/lib/mt-agent-prompt.ts` の `buildMtAgentInstruction()`。

全 spawn 経路 (`replyToBL` / `morning approve` / `/api/cockpit/tasks` / `updateReviewState`) でこれが instruction の前後に巻かれる。

中身を要約:

```
あなたは ミニタキオン経由で起動された AIPM エージェントです。

# 必読 — 運用ルール (AIOS rule 13)
絶対パス: /Users/rikutanaka/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc
特に以下を読むこと:
- Section 2. 絶対遵守ルール
- Section 4. mt CLI / MCP クイックリファレンス
- Section 6. AIPM プロジェクトで動くエージェント全般への要請

# 道具: 3 経路 (MCP 優先 / CLI fallback)
[MCP / CLI / HTTP API の使い分けテーブル]

# 絶対遵守ルール (4 つ)
1. 会話だけで答えない
2. YAML を直接編集しない
3. 成果物 .md は必ず register
4. 質問は BL に書き戻す

# 関連
- BL: <BL-XXXX タイトル>
- 対象成果物: <d-XXXX or 未指定>

# あなたへの指示
<body>

# エラー対応
[400 / 409 / 502 の対処]

# 完了時
- 成果物を作った場合: mt deliverable update-state
- 報告は短く
- 「タスククローズしてください」と書いて田中さん complete 待ち
```

**重要**: rule 13 の **本文は含まれていない**。`絶対パス: ...` でファイル位置を示し、`特に以下を読むこと:` で section 名を列挙するだけ。

→ エージェントが「rule 13 を読みに行く」かは AI の judgment 次第。  
→ Claude Code は file path を見たら自動で Read する習慣があるので大概読みに行くが、cockpit + codex / 弱い LLM では読み飛ばす可能性あり。

**rule 01 〜 12 はそもそも参照されていない**。例えば:
- rule 04 (`04_project_work.mdc` 作業時のルール)
- rule 05 (`05_finalize_to_stock.mdc` 確定反映)
- rule 07 (`07_backlog_management.mdc` バックログ管理)

これらは mini-tachyon の prompt header に出てこないので、エージェントは「rule 13 だけ読めば良い」状態。これは **ミニタキオン 中心の運用に絞った結果** で、意図的ではあるが「他のルールを完全に無視しがち」という副作用がある。

---

## 2. 朝のタスク案エージェント (daily-start.md) は何を読むか

`~/mini-tachyon/lib/prompts/daily-start.md` の **STEP 1. データを集める** より:

| データ | 読み方 | 読むかは |
|---|---|---|
| project 一覧 + active BL 数 | `mt projects list --human` | 必ず |
| pending BL | `mt bl list --state pending --human` | 必ず |
| in_progress BL | `mt bl list --state in_progress --human` | 必ず |
| awaiting_user BL | `mt bl list --state awaiting_user --human` | 必ず |
| blocked BL | `mt bl list --state blocked --human` | 必ず |
| 中央 Backlog.md | `~/aipm_v0/Stock/定型作業/バックログ/Backlog.md` 読み取り | 補助的 (Title/Due/Notes 補強) |
| 前日 wrap-up | `~/aipm_v0/Flow/<前日>/_orchestration/今日の振り返り.md` | 7 日遡る |
| 当日固定予定 | 前日 wrap-up から拾う | 拾えなければ Q.0 で確認 |

→ **AIOS rule や Stock 内のドキュメント (USAGE.md / INTEGRATIONS.md など) は読まない**。  
→ **個別 BL の description (BL.yaml の) は `mt bl list --human` だと出ない**。詳細は `mt bl get <id>` を都度叩く必要があり、朝のエージェントが全 BL に対して `mt bl get` を撃つかは AI の judgment 次第。

これが田中さんの懸念「AIOS のルールやストックの生データを本当に確認できているのか」の答え:
- **AIOS rule**: ほぼ確認していない (rule 13 だけ、それも judgment 依存)
- **Stock の生データ**: BL.yaml / STATUS.md は mt CLI で取れるが、進捗メモ・補足ドキュメント (USAGE.md / INTEGRATIONS.md / Flow に置かれた過去成果物) は基本 **読まない**

---

## 3. ダッシュボード等の別リポはどう動くか

### 物理レイアウト

```
~/aipm_v0/                                       ← AIPM (ミニタキオンの単一情報源)
  Stock/RestaurantAILab/ダッシュボード改/
    STATUS.md
    backlog/
      BL-0083.yaml, BL-0084.yaml, ..., BL-0096.yaml
  Flow/202606/2026-06-03/RestaurantAILab/ダッシュボード改/
    deliverables.yaml
    <報告書>.md

~/RestaurantAILab/                               ← 実コード (別リポ群)
  Dashboard/
  Dashboard-Kai/
  Dashboard-DaichiPoC/
  ChefsAssistant/
  c5med-booking/
  ...
```

→ **AIPM が「状態管理」、別リポが「コード」**。ファイルは物理的に分離。

### エージェント spawn 時の `directory`

`lib/api/finalize.ts:98` (朝のタスク案 approve 時):

```ts
const taskRes = await spawnCockpit({
  instruction: ...,
  directory: AIPM_ROOT,         // ← 常に ~/aipm_v0
  agent_type: 'claude',
  ...
});
```

→ cockpit task は **常に AIPM_ROOT で起動**。実コードの dir に cd する仕組みは無い。  
→ エージェントが Dashboard 実装をいじりたい場合は、自分で `cd ~/RestaurantAILab/Dashboard` する必要があるが、cockpit task の `directory` は AIPM_ROOT のままなので mt deliverable register などは AIPM_ROOT 起点で動く (= 成果物は `~/aipm_v0/Flow/.../RestaurantAILab/ダッシュボード改/` に置かれ、code 変更は `~/RestaurantAILab/Dashboard` で git commit する二段運用)。

### 問題と現状の回避策

| 問題 | 現状 | 改善案 |
|---|---|---|
| エージェントが「実コードの最新状態」を見たい | 自分で `cd ~/RestaurantAILab/Dashboard && git log` を叩く必要 | 各 STATUS.md に `code_repo: ~/RestaurantAILab/Dashboard` フィールド追加し、prompt header に注入 |
| 成果物 .md を実コードリポに置きたい | できない (mt deliverable register は AIPM_ROOT 配下のみ) | 設計どおり (deliverable は意思決定の歴史、code は code) — そのまま |
| 別リポでの git 作業の進捗を BL に反映 | エージェントが手動で `mt bl add-decision` を呼ぶ必要 | post-commit hook で `mt bl add-decision` を呼ぶ (要検討) |

→ **田中さんの混乱**「ダッシュボードは別リポなのに〜」は、**そもそも分離設計が意図的**で、AIPM 側は **状態管理だけ**、実コードは別リポで完結する建付け。エージェントへの prompt にこの分離が明示されていないので、エージェントが混乱しがち、というのが今のところの実装上の弱点。

---

## 4. スキル (SKILL.md) に登録されている内容

場所: `~/.claude/skills/mini-tachyon/SKILL.md`  
発火条件 (frontmatter `description`): 
> "AIPM の状態管理 (BL / 成果物 / 朝夜の運用ループ / cockpit 連携) をミニタキオン経由で操作する"  
> "BL に質問を立てる / 成果物を登録する / 朝のタスク案を承認処理する / cockpit task を spawn する"

`user-invocable: true`、`argument-hint: "操作したい内容"` で `/mini-tachyon` slash でも呼べる。

### 中身 (要約)

1. **いつ使うか** — AIPM 配下、BL-XXXX 文脈、☀️ / 🌙 dogfood、cockpit spawn、「INBOX.md を更新」と言われた時 (廃止済なのでこちらに誘導)
2. **どの経路で叩くか** — MCP / CLI / HTTP API の使い分けテーブル
3. **絶対遵守ルール 4 つ** — buildMtAgentInstruction と同じ内容
4. **ユースケース別手順** (A 〜 F):
   - A. 状況把握から作業開始
   - B. BL に成果物を登録する
   - C. 田中さんに質問 / 回答を記録する
   - D. 朝のタスク案 (☀️) 承認処理
   - E. cockpit task を新規 spawn する
   - F. 設計・成果物の改訂依頼を受けた
5. **エラーハンドリング** — error code 表
6. **補足** — 絶対パス一覧 (mt CLI / mt-mcp / API base / docs / rule 13)

### スキルに含まれていないもの

- BL の具体的な内容 (load by tool call)
- AIOS の他ルール (rule 01〜12)
- 過去成果物のサマリ
- プロジェクト固有の文脈 (誰がオーナー、何が制約)

→ スキルは「**操作マニュアル**」であり、「**プロジェクトの記憶**」ではない。後者は mt CLI / 直接 Read で都度取りに行く設計。

### 他に並ぶスキル群 (発火条件のクラスター)

`mini-tachyon` skill 以外に AIPM 文脈で発火しうるもの:
- (なし — AIPM 専用スキルは mini-tachyon のみ)
- 一般スキル: `update-config`, `careful`, `freeze`, `review`, `ship`, `qa`, `cso`, `learn` ... (gstack 由来)
- 店舗向け: `airregi-sales-download`, `dinii-sales-download`, `usen-regi-sales-download` (AIPM とは独立)
- 文書系: `pdf`, `pptx` (汎用)

→ AIPM の運用は mini-tachyon skill + rule 13 が単一情報源。他のスキルは独立して動く。

---

## 5. AIOS 連携の現状サマリ表

| 連携対象 | 自動 inject | エージェントが取りに行く | 取りに行くかは AI 判断 |
|---|---|---|---|
| AIOS rule 13 (本文) | ❌ | パス参照あり (`buildMtAgentInstruction` 内) | ✅ Claude Code はほぼ読む |
| AIOS rule 01〜12 | ❌ | 参照すらなし | ❌ ほぼ読まない |
| `~/aipm_v0/CLAUDE.md` | ❌ | Claude Code session 開始時に自動 inject (Claude Code 固有) | ✅ |
| BL.yaml | ❌ | `mt bl get <id>` | ✅ 朝エージェントは必ず |
| 中央 Backlog.md | ❌ | 朝エージェントが読む (daily-start.md 規定) | ✅ |
| STATUS.md | ❌ | `mt projects list --human` で has_status は分かる、本文は別途 read | △ AI 判断 |
| Flow 過去成果物 | ❌ | 前日 wrap-up のみ | △ wrap-up しか読まない |
| USAGE.md / INTEGRATIONS.md (Stock 内) | ❌ | 参照なし | ❌ |
| 別リポ (Dashboard 等) のコード | ❌ | 参照なし | ❌ |

→ **「ストックの生データを本当に確認できているか」の答え**: BL.yaml と Backlog.md は確認している。STATUS.md は spotty。AIOS rule 13 以外と Flow 過去成果物と別リポは **基本見ていない**。

---

## 続き

- 01: 俯瞰 → `01_overview_実装とドキュメントの対応.md`
- 02: バックログ番号付け矛盾 → `02_backlog_管理の実態と番号付け矛盾.md`
- 04: 4 つの悩みへの回答 → `04_田中さんの悩みへの回答と推奨アクション.md`
