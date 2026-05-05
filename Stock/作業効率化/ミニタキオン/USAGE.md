# ミニタキオン USAGE — 田中さん向け運用リファレンス

> 最初に読むべき 1 枚。コマンド集ではなく「何のためにあって、どう日常運用するか」の読み物。
> 詳細は本ドキュメントの末尾「10. 関連ドキュメント」を参照。
>
> Last updated: 2026-05-05

---

## 1. これは何

**ミニタキオン (mini-tachyon)** は AIPM (`~/aipm_v0/`) の **タスク状態管理ハブ**。
プロジェクト STATUS.md / BL-XXXX.yaml / deliverables.yaml の散文同期 (旧 INBOX.md / mmdd_daily_tasks.md ベースの 3 ファイル運用) を廃止し、その責務をすべて引き受ける **単一情報源 (Source of Truth)**。Mac mini 上で常駐し、iPhone Safari からも Tailscale 経由で内線アクセスできるモバイル一画面ツール。エージェント (Claude / Codex / Cockpit) が状態を書き換えるときは必ず HTTP API 経由になり、zod 検証 + atomic write でドリフトを構造的に防ぐ。

---

## 2. 誰のためのものか / 解決する痛み

読者: **田中さん本人**。長期的には他協力者にも展開可能。

| 痛み (Before) | ミニタキオンの解決策 |
|---|---|
| STATUS / INBOX / daily_tasks の **3 ファイル散文同期** が認知負荷高、エージェントごとにドリフト | 構造化 YAML + UI、書き込みは API 経由のみ |
| AI のフィードバック反映が会話で消えて UI に残らない | `mt bl add-decision` / `mt bl add-question` で必ず BL に書き戻す |
| AI 成果物 (.md) を iPhone でレビューしながら次指示を口述する動線が無い | BL 詳細画面 → 成果物 → コメント送信が 1 画面 |
| 「今日 [x] 採択した BL は何」「私の番」が project 横断で見えない | ホーム画面にトリアージグループ (私の番 / AI の番 / 完了 / ブロック) |
| 過去 deliverable / 過去の運用が掘り出せない | 「📚 過去の運用」リンク + index-store の bl_id 逆引き backstop |

---

## 3. 構成と起動状態の確認

### 3.1 構成の住所

| 役割 | 場所 |
|---|---|
| Web UI / HTTP API | `http://localhost:3000` (Tailscale: `http://rikus-mac-mini-3.tailad7d87.ts.net:3000`) |
| 常駐 | launchd service `jp.agi-tools.mini-tachyon` |
| mt CLI | `/Users/rikutanaka/mini-tachyon/bin/mt` |
| MCP server (stdio) | `/Users/rikutanaka/mini-tachyon/bin/mt-mcp` |
| Claude Code skill | `~/.claude/skills/mini-tachyon/SKILL.md` |
| 運用ルール (canonical) | `~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| 設計書 (オリジナル) | `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md` |

### 3.2 データ (Source of Truth)

```
~/aipm_v0/
├── Stock/<category>/<project>/STATUS.md            # プロジェクト状態
├── Stock/<category>/<project>/backlog/BL-*.yaml    # BL 定義 + Q&A + decisions
├── Stock/定型作業/バックログ/Backlog.md             # 中央 Backlog 台帳
└── Flow/<yyyymm>/<YYYY-MM-DD>/
    ├── _orchestration/                              # 朝/夜エージェント領域
    └── <category>/<project>/deliverables.yaml       # 当日成果物メタ
```

### 3.3 生きてるかどうか確認

```bash
# launchd 状態
launchctl list jp.agi-tools.mini-tachyon

# API ヘルス (UI トップを叩く)
curl -fsS http://localhost:3000 -o /dev/null && echo OK

# CLI で smoke test
/Users/rikutanaka/mini-tachyon/bin/mt projects list --human
```

落ちている時は `launchctl kickstart -k gui/$(id -u)/jp.agi-tools.mini-tachyon` で再起動。

### 3.4 経路の使い分け

| 経路 | 推奨ケース |
|---|---|
| **Web UI** | iPhone / Safari、田中さん本人の操作 |
| **MCP server** (`mt_*` tool) | Claude Code / Cursor / Cockpit の MCP 対応セッション (drift しにくい) |
| **mt CLI** | terminal、shell pipeline、MCP 未対応の cockpit task |
| **HTTP API** | curl テスト、別言語からの呼び出し |
| **/mini-tachyon skill** | Claude Code 内でユースケース別手順を見ながら作業 |

すべて同じ Next.js HTTP API を叩くので結果は等価。**MCP が使える環境では MCP を優先**。

---

## 4. 画面の見方

iPhone Safari で `http://rikus-mac-mini-3.tailad7d87.ts.net:3000` を開く。

### 4.1 ホーム — トリアージ

| グループ | 入る条件 | 何を見る |
|---|---|---|
| 🔥 **私の番** | AI 質問が未回答 / 未レビュー成果物あり / state が awaiting_user / looping | 上から順に処理する |
| 🟢 **AI の番** | state が in_progress 等で AI 作業中 | 進捗確認のみ |
| ✅ **完了** | 当日 completed | 振り返り |
| ❌ **ブロック** | state=blocked | blocker を解消する |

下部に **🗂 プロジェクト一覧 (active BL 数つき)** と **📅 今日の運用 / 📚 過去の運用** リンク。
ホームは **「今日の選択」BL にフィルタ済**。全 active BL は別ページ `/backlog`。

### 4.2 プロジェクト詳細

STATUS.md を frontmatter + body で表示、その下に当該プロジェクトの BL 一覧。STATUS.md は markdown レンダリング、`@tailwindcss/typography` で読みやすく整形。

### 4.3 BL 詳細

レイアウト順 (重要):

1. **AI からの成果物** (hero) — `deliverable_refs` から逆引き、未レビューが上
2. **AI へのフィードバック** — pending_questions / decisions の時系列
3. 詳細メタ (cockpit_task_ids、created_at など) は折りたたみ

→ 田中さんは「未レビュー成果物 → 内容確認 → コメント or done」の動線で 1 画面完結。

### 4.4 当日の運用 / 過去の運用

`Flow/<today>/_orchestration/` の朝のタスク案 / 夜の振り返り deliverable を表示。「📚 過去の運用」から日別アーカイブを辿れる。

### 4.5 Backlog 一覧

`/backlog` で全 active BL を project 横断で表示 (中央 `Stock/定型作業/バックログ/Backlog.md` から自動集約)。

---

## 5. 朝の運用 (☀️ daily start)

### 5.1 ボタン → タスク採択までの流れ

1. iPhone でホームを開き **☀️ 今日を始める** を押下
2. ミニタキオンが Cockpit task を spawn (固定プロンプト `~/.agi-tools/mini-tachyon/lib/prompts/daily-start.md`)
3. 朝のエージェントが:
   - 中央 `Backlog.md` から active BL を抽出
   - 前日 (最大 7 日遡る) の `今日の振り返り.md` を参照
   - **4/24 形式の Project 別テーブル** で「今日のタスク案」を生成
   - `Flow/<today>/_orchestration/今日のタスク案.md` に保存
   - `mt deliverable update-state <id> --state unreviewed` で完了登録
4. 田中さんがタスク案を BL ごとに **判定マーク** で採択

### 5.2 判定マークの意味

| マーク | action | 起こること |
|---|---|---|
| `[x]` | approve | BL.state=in_progress、`spawn_class: A` なら cockpit task を auto-spawn して BL.cockpit_task_ids に紐付け |
| `[-]` | defer | BL.state=planned (今日はやらない、後回し) |
| `[ ]` | skip | 何もしない (案だけ提示で見送り) |

`✍️ 回答` 欄に書き込んだ内容は、フィードバック処理エージェントが `mt bl add-decision --type answer --by user` で各 BL に分解 append する。

### 5.3 承認後の挙動

田中さんが **done + コメント送信** すると:
- ミニタキオンが `lib/fallback-instruction.ts` でフィードバック処理エージェントを spawn
- そのエージェントが `mt morning finalize <deliverable_id> --selections '[{"bl":"BL-XXXX","action":"approve","spawn_class":"A"}]'` を呼ぶ
- API が atomic に: 採択 BL の state 更新 + クラス A 案件の cockpit spawn + cockpit_task_ids 連携

### 5.4 AI 並列本数の目安

`spawn_class: A` (cockpit task spawn 対象) は同時 2-3 本までを目安に。それ以上は `defer` にしておく。

### 5.5 押し忘れた時

`☀️` を 8:30 までに押し忘れ → ホームに警告バッジ (自動実行はしない)。後から押せば OK。

---

## 6. 夜の運用 (🌙 daily wrapup)

iPhone でホームから **🌙 今日を締める** を押下。固定プロンプト `~/.agi-tools/mini-tachyon/lib/prompts/daily-wrapup.md` 通りに:

1. 当日完了したこと / 残課題 / 翌日への申し送りを集計
2. `Flow/<today>/_orchestration/今日の振り返り.md` に保存
3. `lib/merge.ts` で当日 Flow → Stock STATUS.md にマージ
   - 履歴セクション: append (重複なし)
   - 完了済セクション: union
   - 次アクション / ブロッカー / 概要: Flow の最新内容で上書き

押し忘れた場合のセーフティネット: **03:00 cron** が自動 `endDailyLoop` を実行 (Phase 3c 実装予定 / BL-TBD-006)。翌朝の整理エージェントは「前日 wrap-up なし」を検知して履歴なしモードで進行する。

---

## 7. BL ライフサイクル

### 7.1 状態遷移

```
pending → in_progress → awaiting_user → completed
            │              ↑    │
            ↓              │    ↓
         blocked      (回答で再開)  planned (defer)
```

| state | 意味 |
|---|---|
| `pending` | 未着手、Backlog から拾ってきたばかり |
| `in_progress` | 朝採択 [x] or 手動着手 |
| `awaiting_user` | AI 完了、田中さんレビュー待ち (UI で「私の番」入り) |
| `looping` | 田中さんから次指示を送った直後 (再 AI ターン) |
| `planned` | 朝採択 [-] (defer)、今日はやらないが planned |
| `completed` | 完了 (`completed_at` 自動セット) |
| `blocked` | blocker あり |

### 7.2 decisions と pending_questions の使い分け

| 場面 | 書く先 | コマンド |
|---|---|---|
| AI が田中さんに確認したい質問 | `pending_questions[]` (キュー) | `mt bl add-question <id> --content "..."` |
| 田中さんの回答 | `decisions[]` に `type: answer, by: user` | `mt bl add-decision <id> --type answer --by user --content "..." --answers-question-id <qid>` |
| AI 自身のコミット宣言 / 進捗メモ | `decisions[]` に `type: commitment, by: ai` | `mt bl add-decision <id> --type commitment --by ai --content "..."` |
| スコープ変更 | `decisions[]` に `type: scope_change` | `mt bl add-decision <id> --type scope_change ...` |

回答する時に `--answers-question-id` を指定すると、対応する pending_question が consume されて UI から消える (decisions に対応関係が残る)。

### 7.3 成果物登録

```bash
# 1. .md を canonical Flow dir に書き出す (mt が BL から自動算出)
#    ~/aipm_v0/Flow/<yyyymm>/<YYYY-MM-DD>/<category>/<project>/<basename>.md

# 2. atomic 登録 (deliverables.yaml + BL.deliverable_refs 両方を 1 発)
/Users/rikutanaka/mini-tachyon/bin/mt deliverable register \
  --bl BL-XXXX \
  --file <basename>.md \
  --title "..." \
  --agent claude
```

`--id` 省略時は `d-<YYYYMMDD>-<NNN>` で自動採番。register 直後の review_state は `unreviewed`。

---

## 8. やってはいけないこと

### 8.1 YAML / 状態管理ファイルの直接編集

`Stock/.../BL-*.yaml`、`Flow/.../deliverables.yaml`、`STATUS.md` frontmatter を **エディタや echo / sed / awk で直接書き換えない**。スキーマ違反 (例: `decisions[].by: 田中` のような独自値、独自フィールド追加) は zod が 400 で reject するが、UI 側からは「保存したのに反映されない」状態になる。

> **歴史的エピソード (2026-05-05 BL-0015 で発覚)**
> 失業保険の調査レポートを Cockpit エージェントが生成し、`deliverables.yaml` だけ手書きで append したが `BL-0015.yaml` の `deliverable_refs` を更新し忘れ → BL 詳細画面に成果物が出ない bug。原因は (1) atomic な register API が未整備、(2) prompt が rule mdc 経由の rule-following で drift しやすい、の二点。
> → この事件をきっかけに `mt deliverable register --bl <id> --file <basename>` (atomic に両方を更新) と Phase 5 (MCP server + skill 化) が正式着手された。**deliverables.yaml の手書き禁止** はこの再発防止ルール。

### 8.2 廃止済ファイルを新規作成しない

| 旧 (廃止) | 今やるべきこと |
|---|---|
| `_orchestration/INBOX.md` | `mt bl add-question` / `mt bl add-decision` |
| `mmdd_daily_tasks.md` | ☀️ ボタン → 朝のタスク案 deliverable |
| `questions_to_user.md` | `mt bl add-question` |
| 「STATUS / INBOX / daily_tasks の 3 ファイル同期」 | mt CLI / MCP / UI 経由の API 1 本に集約 |

過去日 (`Flow/<過去日>/`) の INBOX.md / daily_tasks.md は履歴アーカイブとしてそのまま残す。**新規には作らない**。

### 8.3 「会話で答えるだけ」で終わらせない

田中さんから質問・指示を受けたら、応答は必ず以下のいずれかで mini-tachyon UI に反映:

- 短い factual 回答 → `mt bl add-decision <id> --type commitment --by ai --content "..."`
- 別の質問が必要 → `mt bl add-question <id> --content "..."`
- 新規成果物 .md → `mt deliverable register --bl <id> --file <basename>.md --title "..."`
- 改訂 → 該当 markdown 編集 + `mt deliverable update-state <id> --state unreviewed`

会話だけで終わると UI に何も残らず、田中さんから見えない。

### 8.4 スキーマの自由解釈

- `decisions[].by` は `user | ai` のみ (「田中」「master」禁止)
- `decisions[].type` は `answer | commitment | scope_change | deferred` のみ
- review_state は `unreviewed | reviewing | done | needs_revision | generating` の 5 値のみ
- 独自フィールド (`id`, `summary`, `items` 等) を勝手に追加しない

---

## 9. トラブルシュート

| 症状 | 対応 |
|---|---|
| `mt: command not found` | `/Users/rikutanaka/mini-tachyon/bin/mt` を絶対パスで使う、または `sudo ln -s /Users/rikutanaka/mini-tachyon/bin/mt /usr/local/bin/mt` |
| UI に書いたはずの変更が反映されない | (1) chokidar 取りこぼし → 5 分待つと fallback rebuild、(2) スキーマ違反で reject されている → `mt bl get <id>` で実際の状態確認 |
| `error: network` | mini-tachyon 落ちてる → `launchctl list jp.agi-tools.mini-tachyon` 確認、`launchctl kickstart -k gui/$(id -u)/jp.agi-tools.mini-tachyon` で再起動 |
| `error: validation` (400) | 引数が schema 違反。エラーメッセージ `detail.issues[]` を読んで再試行 |
| `error: conflict` (409) | optimistic lock 失敗 → `mt bl get <id>` で最新 `updated_at` を取り直して `--expected-updated-at` 付きで再送 |
| `error: cockpit` (502) | cockpit binary 経路で失敗 → `detail.attempts[]` で send/resume/create のどこで死んだか確認、cockpit が立ってるか `cockpit task list` |
| 過去 deliverable が UI に出ない | active BL の `deliverable_refs` に id があるか確認。無ければ `mt deliverable register` を再実行 (BL.refs 未登録でも index-store の bl_id 逆引きで backstop されるが、register の方が永続化される) |
| deliverable が「AI 生成中 (generating)」のまま固まった | エージェントが interrupted で state 更新できなかった可能性 → `mt deliverable update-state <id> --state unreviewed` で手動補正 |
| iPhone から繋がらない | iPhone が Tailscale にログインしているか確認。Mac mini 側 `launchctl list` でポート 3000 が listening になっているか |

---

## 10. 関連ドキュメント

| 種別 | パス |
|---|---|
| 運用ルール (canonical) | `~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| プロジェクト STATUS | `~/aipm_v0/Stock/作業効率化/ミニタキオン/STATUS.md` |
| 設計書 (オリジナル) | `~/aipm_v0/Flow/202604/2026-04-25/ミニタキオン/design_mobile_review_hub.md` |
| CLI 仕様 | `~/mini-tachyon/docs/CLI.md` |
| HTTP API 仕様 | `~/mini-tachyon/docs/API.md` |
| MCP server 仕様 | `~/mini-tachyon/docs/MCP.md` |
| Claude Code skill | `~/.claude/skills/mini-tachyon/SKILL.md` |
| BL-0001 (方針検討ハブ) | `~/aipm_v0/Stock/作業効率化/ミニタキオン/backlog/BL-0001.yaml` |
| BL-0015 (deliverable_refs 取りこぼし bug の元事例) | `~/aipm_v0/Stock/生活管理/雑事/backlog/BL-0015.yaml` |

困ったらまず `13_mini_tachyon_protocol.mdc` を読む。コマンドのリファレンスは `docs/CLI.md`、API スキーマ詳細は `docs/API.md`、MCP tool 一覧は `docs/MCP.md`。
