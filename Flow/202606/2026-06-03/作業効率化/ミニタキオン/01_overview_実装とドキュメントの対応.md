# ミニタキオン 現状俯瞰 — 実装 / ドキュメント / スキル

> BL-0095 (今日着手分) の調査メモ Part 1。  
> 田中さんの質問「ミニタキオンの今の仕組みを教えて欲しい」への回答。

---

## TL;DR (まず結論)

ミニタキオンは **「YAML / Markdown を直接編集しないで AIPM の状態管理ができる Next.js webapp + CLI + MCP」** という建付けで、以下 4 層に分かれる。

| 層 | 場所 | 役割 |
|---|---|---|
| Web UI | `http://localhost:3000` (launchd 常駐) | 田中さん向けホーム / BL 詳細 / 朝夜運用 |
| HTTP API | Next.js `app/api/*` | zod validate + atomic write のレイヤ |
| CLI | `~/mini-tachyon/bin/mt` | shell からの単発操作 (542 行) |
| MCP server | `~/mini-tachyon/bin/mt-mcp` | LLM 直結 (18 tool、stdio transport) |

**データソース (Source of Truth)** はすべて `~/aipm_v0/` 配下の以下:

- 中央 Backlog 台帳 — `~/aipm_v0/Stock/定型作業/バックログ/Backlog.md`
- per-project BL YAML — `~/aipm_v0/Stock/<category>/<project>/backlog/BL-XXXX.yaml`
- per-project STATUS — `~/aipm_v0/Stock/<category>/<project>/STATUS.md`
- 当日 Flow — `~/aipm_v0/Flow/YYYYMM/YYYY-MM-DD/<category>/<project>/`
- 朝/夜 Orchestration — `~/aipm_v0/Flow/YYYYMM/YYYY-MM-DD/_orchestration/`

ミニタキオン自体はこれらを **読み取り + atomic 書き込み** するだけで、独自のデータベースは持っていない (chokidar で fs を監視して UI に反映する設計)。

---

## 1. リポジトリ / インストール構成

```
~/mini-tachyon/         ← この webapp / CLI / MCP のソース (Next.js)
~/aipm_v0/              ← データ実体 (state) — Stock/Flow
~/.claude/skills/mini-tachyon/SKILL.md   ← Claude Code 向けスキル定義
~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc  ← canonical 運用ルール
```

`mini-tachyon` リポと `aipm_v0` リポは **別物**。mini-tachyon は `AIPM_ROOT` 環境変数 (default `~/aipm_v0`) で `aipm_v0` を指している (`lib/paths.ts:6-10`)。

ダッシュボードなどの 他リポ (`~/RestaurantAILab/Dashboard*` 等) は **ミニタキオンから不可視**。これは意図的な設計で、ミニタキオンは「**AIPM の状態管理 hub**」であり、コードリポジトリのオーケストレータではない (→ 詳細は 03 文書参照)。

---

## 2. 起動 / 常駐

- launchd label: `jp.mini-tachyon` (plist: `~/mini-tachyon/launchd/jp.mini-tachyon.plist`)
- port: 3000
- iPhone から: Tailscale 経由でホーム → ☀️ / 🌙 ボタン

```bash
# 起動状態確認
launchctl list jp.mini-tachyon

# kickstart
launchctl kickstart -k gui/$(id -u)/jp.mini-tachyon

# install スクリプト (`./launchd/install.sh status|restart|install`)
```

cockpit (`~/. agi-tools/data/cockpit/master/bin/cockpit`) は別 process で動いており、ミニタキオンは `mt cockpit spawn` で cockpit binary を呼んで child task を作る (内部で `execFile`)。

---

## 3. 経路 (4 つあるが等価)

| 経路 | 主用途 | 状態 |
|---|---|---|
| Web UI (`localhost:3000`) | 田中さんが直接触る | ✅ 稼働 |
| HTTP API (`/api/*`) | curl / 別言語からの直接呼び出し | ✅ 稼働 |
| mt CLI (`~/mini-tachyon/bin/mt`) | shell / cockpit task の中 | ✅ 稼働 |
| MCP server (`mt-mcp`) | Claude Code 等 MCP 対応 client | ✅ 稼働 (18 tool) |

**重要**: CLI / MCP は HTTP API の薄いラッパで、最終的には同じ Next.js route handler に着地する。だから「CLI から書いて UI に反映されない」は本来ありえない (chokidar が fs 変化を拾って UI 再描画)。

ドキュメント:
- API: `~/mini-tachyon/docs/API.md`
- CLI: `~/mini-tachyon/docs/CLI.md`
- MCP: `~/mini-tachyon/docs/MCP.md`
- Skill: `~/.claude/skills/mini-tachyon/SKILL.md`
- 運用ルール (canonical): `~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc`

---

## 4. API endpoint 全覧 (実装ベース)

`app/api/` ツリーを全走査して列挙:

```
/api/bl                          GET  list + POST create        (zod: CreateBLSchema)
/api/bl/[id]                     GET  + PATCH                   (PatchBLSchema)
/api/bl/[id]/decisions           POST                            (AddDecisionSchema)
/api/bl/[id]/pending-questions   POST                            (AddQuestionSchema)
/api/bl/[id]/pending-questions/[qid]  DELETE                    (consume)
/api/deliverables/[id]           GET
/api/deliverables/register       POST                            (register: yaml + BL.refs atomic)
/api/deliverables/[id]/state     PATCH                           (review_state)
/api/deliverables/[id]/comments  POST                            (review_log append)
/api/cockpit/tasks               POST                            (spawn — wrap_with_mt_prompt auto)
/api/cockpit/tasks/[tid]/send    POST                            (三段 fallback)
/api/morning/start               POST                            (placeholder + cockpit spawn)
/api/morning/finalize            POST                            ([x] 採択 atomic)
/api/evening/start               POST
/api/today/selected              GET
/api/projects                    GET                             (active BL 数 + slug)
```

数えると **16 route**。MCP は 18 tool を公開 (`mt bl consume-question` などが route として別エンドポイント化されていないが MCP 側では別 tool になっている、API では DELETE /pending-questions/[qid] に相当)。

---

## 5. ドキュメントとの突合 — どこが一致 / どこがズレているか

| トピック | ドキュメント | 実装 | 一致? |
|---|---|---|---|
| 経路の優先度 | MCP > CLI > HTTP | ✅ 同じ Next.js route に着地 | OK |
| 朝のタスク案 生成元 | `daily-start.md` (固定 prompt) | `lib/prompts/daily-start.md` を `lib/api/finalize.ts`/`lib/fallback-instruction.ts` から読む | OK |
| 夜の振り返り 生成元 | `daily-wrapup.md` | 同上 | OK |
| BL ID 採番 | 「per-project YAML 自動採番」(docs/CLI.md) | `nextNumericBLId(category, project)` が **project dir だけ** スキャン (`lib/api/bl-paths.ts:50-65`) | ⚠️ **問題あり** (詳細 02) |
| 「今日の選択」3 ルール | (a) 朝 [x] / (b) 今日 decisions / (c) own active | 同じ (`lib/today-selected.ts:90-100`) | OK |
| 新規 BL 作成 (UI) | docs では言及なし | UI に **フォーム / ボタン無し**。`/api/bl` POST は CLI / MCP / curl のみ | ⚠️ ギャップ |
| AIOS rule 読み込み | rule 13 を「読め」と instruction header に書く (`lib/mt-agent-prompt.ts:78`) | **本文は injection せず参照だけ** | △ (詳細 03) |
| 別リポの code | docs 上記述なし | `AIPM_ROOT` 固定で `~/aipm_v0` 外は見えない | △ (詳細 03) |

要するに **「文書化されているところは概ね実装と一致」** だが、**「文書化されていない暗黙の制約」 (BL ID の per-project スコープ / UI に new BL form 無し / AIPM 外の不可視) が田中さんの困惑の原因**。

---

## 6. データの読み方 (index-store の全体像)

UI / API / CLI / MCP どれも結局は **`lib/index-store.ts` の `getIndex()`** から読む。挙動:

1. `buildProjectsFromStock()` で `Stock/<category>/<project>/` を全走査し
   - `STATUS.md` の frontmatter を読む
   - `backlog/BL-*.yaml` を全部 load
   - project と BL を Map に詰める
2. `readCentralBacklog()` で `Stock/定型作業/バックログ/Backlog.md` の `## Tasks` テーブルを parse
3. `mergeCentralBLs()` で per-project vs 中央 の id 衝突を解消 (per-project 優先、中央のみは仮想 project として merge)
4. `loadDeliverablesByRefs()` で BL.deliverable_refs を解決
5. 当日 `_orchestration/deliverables.yaml` を upsert
6. 各 project の Flow STATUS.md があれば Stock STATUS.md を上書き

index は **module-level singleton** (`globalThis.__miniTachyonIndex`) で、`rebuildIndex()` (mutation 系 API から呼ばれる) と chokidar 監視で再構築する。

---

## 続き

- 02: バックログ管理の実態と番号付けの不整合 → `02_backlog_管理の実態と番号付け矛盾.md`
- 03: AIOS 連携 / 別リポ連携 / スキル登録内容 → `03_aios連携_別リポ_スキル.md`
- 04: 4 つの悩みへの回答 + 推奨アクション → `04_田中さんの悩みへの回答と推奨アクション.md`
