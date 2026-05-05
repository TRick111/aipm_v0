# ミニタキオン 設計監査 + 統合方法 (INTEGRATIONS)

最終更新: 2026-05-05 / 対象実装: `/Users/rikutanaka/mini-tachyon/` (HEAD) / Phase 5c 完了 + 整合性 hotfix (24 件) 全消化済

このファイルは Stock 配下の長寿命リファレンス。
1. **Part 1 設計監査 (修正済記録)**: docs / 実装 / rule mdc の整合性を機械的に照合した結果と、2026-05-05 に実施した修正の対応表
2. **Part 2 起動経路一覧**: ミニタキオンの 5 経路を 1 表にまとめる
3. **Part 3 MCP server 起動手順**: Claude Code / Cursor / Claude Desktop / Cockpit の各 client から MCP server を立ち上げる手順 (この章を最も詳しく)
4. **Part 4 ルール認識経路**: Claude Code / Cursor / Claude Desktop / Cockpit がミニタキオンの運用ルールを **どこから / どう知るか** の 5 経路 + 検証方法
5. **Part 5 skill の使い方** / **Part 6 既知の制約**

> **本ドキュメントの位置付け**: 利用者向けの読み物は隣の [USAGE.md](USAGE.md)。本ファイルはエンジニアリング/運用観点の自己点検と client 設定リファレンス。

---

# Part 1: 設計監査 (修正済記録)

> **TL;DR**: 2026-05-05 に行った監査で **致命傷なし**、ただし critical 8 / moderate 10 / minor 6 の不整合を発見 → **同日中に全 24 件を実施完了**。本セクションは履歴と再発防止のために残してある。次回の自己監査で「同種の問題が再発していないか」のチェックリストとして使える。

## 1.1 チェックした範囲

| 領域 | ファイル |
|---|---|
| 運用ルール (canonical) | `/Users/rikutanaka/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| 公開 docs | `/Users/rikutanaka/mini-tachyon/docs/CLI.md`, `docs/API.md`, `docs/MCP.md` |
| skill | `/Users/rikutanaka/.claude/skills/mini-tachyon/SKILL.md` |
| サンプル | `/Users/rikutanaka/mini-tachyon/examples/` (現在は client 別 3 ファイル + README に分割済) |
| プロジェクト STATUS / USAGE | `/Users/rikutanaka/aipm_v0/Stock/作業効率化/ミニタキオン/STATUS.md`, `USAGE.md` |
| CLI 実装 | `bin/mt` (HELP block + parser + 全 subcommand) |
| MCP 実装 | `bin/mt-mcp` (18 tool 登録) |
| HTTP 実装 | `app/api/**/route.ts`, `lib/api/{bl-write,bl-read,deliverable,finalize,respond}.ts` |
| zod schema | `lib/types.ts`, 各 `lib/api/*.ts` の `*Schema` |
| 組み込み prompt | `lib/mt-agent-prompt.ts`, `lib/fallback-instruction.ts` |
| index ロジック | `lib/index-store.ts` (backstop) |
| orchestration | `lib/orchestration.ts` |
| launchd | `launchd/install.sh`, `launchd/jp.mini-tachyon.plist` (repo 同梱), `~/Library/LaunchAgents/jp.mini-tachyon.plist` |
| package | `package.json`, `README.md`, `CLAUDE.md`, `AGENTS.md` |

## 1.2 整合性 OK の確認 (2026-05-05 hotfix 後)

- **MCP tool 数**: docs/MCP.md・rule 13 §1.1 の「18 endpoint」と `bin/mt-mcp` の `server.registerTool` 18 回が一致 (`mt_bl_list/get/create/update/add_decision/add_question/consume_question` 7 + `mt_deliverable_register/get/update_state/add_comment` 4 + `mt_cockpit_spawn/send` 2 + `mt_morning_start/finalize`, `mt_evening_start` 3 + `mt_today_selected/projects_list` 2)。
- **CLI ↔ MCP ↔ docs/MCP.md の表**: docs/MCP.md §「Tool 一覧 (18)」の各 mt CLI 対応が `bin/mt` のサブコマンドと完全一致。
- **AddDecision の zod**: `lib/api/bl-write.ts AddDecisionSchema` の `type/by/content/answers_question_id` が rule 13 §2.3 と完全一致 (`type: answer|commitment|scope_change|deferred`、`by: user|ai`)。スキーマ違反は API 層で 400。
- **AddComment の zod (hotfix M3+M4 後)**: `lib/api/deliverable.ts AddCommentSchema.by` と `bin/mt-mcp mt_deliverable_add_comment.by` が共に `z.enum(["user","ai"]).optional()` で揃う。docs/API.md / SKILL.md の `user|ai` 表記と整合。
- **register の atomic 性 ↔ index-store backstop**: `lib/api/deliverable.ts registerDeliverable` が `deliverables.yaml` → `BL.deliverable_refs` の順で書き、失敗時の片側更新を `lib/index-store.ts` の `bl_id` 逆引き (ログ key `backstopPatched`) で救う。docs/CLI.md §「Flow ディレクトリ構造」末尾の説明と一致。
- **morning finalize**: docs/API.md / docs/CLI.md / `bin/mt-mcp mt_morning_finalize` / `lib/api/finalize.ts` の `selections[]` schema (`bl/action/spawn_class/next_action`) が完全に揃っている。
- **wrap_with_mt_prompt (hotfix M5 後)**: `app/api/cockpit/tasks/route.ts` の zod / docs/API.md の説明 / `bin/mt cockpit spawn --no-wrap` / MCP `mt_cockpit_spawn { wrap_with_mt_prompt: bool }` の 4 箇所すべてに登場、default `true`。
- **launchd 系 (hotfix C5-C8 後)**: 稼働 label `jp.mini-tachyon`、plist は `launchd/jp.mini-tachyon.plist` を repo 同梱、`launchd/install.sh` は bootstrap/bootout/kickstart 流儀で legacy label を自動 bootout、`README` / `docs/CLI.md` / rule 13 / USAGE.md トラブルシュートの全箇所が同 label を指す。
- **パス系 (hotfix C1-C4 / M1 後)**: `~/.agi-tools/mini-tachyon/` の残骸はコード / 公開 docs / rule 13 / STATUS.md / USAGE.md の現用記述から消去 (履歴ファイル「インフラ独立化と…2026-05-02.md」と過去 BL の description 内、INTEGRATIONS.md 自身の引用は意図的に残存)。
- **CLI HELP の網羅性 (hotfix M6+M7 後)**: `bin/mt` HELP block に `--due` / `--created-by` / `--no-wrap` を全部記載、docs/CLI.md にも `mt bl create --due` 例追加。
- **MCP config 例 (hotfix M8 後)**: `examples/` 配下に Claude Code / Claude Desktop / Cursor の 3 形式が揃い、`examples/README.md` で配置先を一覧化。
- **環境変数 (hotfix M10 後)**: `lib/cockpit.ts` に `DEFAULT_COCKPIT_BIN` を export、README に `MINI_TACHYON_URL` / `COCKPIT_BIN` を明記。
- **rule 13 §3.4 警告バッジ (hotfix M9 後)**: 「Phase 6+ 実装予定、2026-05-05 時点 spec only」と明記、USAGE.md §5.5 にも追記。

> **致命傷なし & 整合性 hotfix 完了**。以下 §1.3 / §1.4 は 2026-05-05 監査で発見された 24 件の発見事項と修正実施記録。

## 1.3 監査で発見した 24 件 (すべて修正済)

監査時刻: 2026-05-05 13:30 / 修正完了: 2026-05-05 17:00。以下 3 表は **発見 → 実施した修正 → 確認方法** をペアで残す履歴。

### Critical (実装と意味が食い違っていた、致命傷ではないが drift の温床) — 8/8 ✅

| # | 発見した不整合 | 実施した修正 | 確認方法 |
|---|---|---|---|
| C1 ✅ | `rule 13 mdc:100` が朝プロンプトを `~/.agi-tools/mini-tachyon/lib/prompts/daily-start.md` と案内 | `~/mini-tachyon/lib/prompts/daily-start.md` に置換 | `grep "agi-tools/mini-tachyon" ~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` で空 |
| C2 ✅ | `rule 13 mdc:117` 夜プロンプト同様 | 同上、`daily-wrapup.md` に置換 | 同上 |
| C3 ✅ | `rule 13 mdc:142` 「詳細は `~/.agi-tools/mini-tachyon/docs/CLI.md`」 | `~/mini-tachyon/docs/CLI.md` に置換 | 同上 |
| C4 ✅ | `rule 13 mdc:443` `mt: command not found` 対処の絶対パス・symlink 例が旧パス | `~/mini-tachyon/bin/mt` 統一、symlink 例も追従 | 同上 |
| C5 ✅ | `rule 13 mdc:444` トラブルシュートで旧 launchd label `jp.agi-tools.mini-tachyon` を案内 | `jp.mini-tachyon` に置換 (`launchctl list` / `launchctl kickstart -k gui/$(id -u)/...` 両方) | `launchctl list jp.mini-tachyon` で PID 出る |
| C6 ✅ | `docs/CLI.md:189` 同じ古い label | `jp.mini-tachyon` に置換 | `grep "jp.agi-tools" ~/mini-tachyon/docs/CLI.md` で空 |
| C7 ✅ | `launchd/install.sh` が存在しない `jp.agi-tools.mini-tachyon.plist` を SRC/DST にハードコード、cp で死亡 | (1) 稼働中 plist を `launchd/jp.mini-tachyon.plist` として repo 同梱、(2) `install.sh` を `bootstrap`/`bootout`/`kickstart` 流儀に書き直し、(3) `install` 時に legacy label を自動 bootout、(4) `status` サブコマンド追加 | `~/mini-tachyon/launchd/install.sh status` → `state = running / pid = ... / last exit code = ...` |
| C8 ✅ | `README.md:9` plist 参照が repo 不在のファイル | README を 4 経路 (CLI/API/MCP/skill) + canonical plist (`launchd/jp.mini-tachyon.plist`) + `install.sh status` 案内 + 環境変数表に再構築 | README を読む |

### Moderate (古い参照 / 廃止済 / 説明不足) — 10/10 ✅

| # | 発見した不整合 | 実施した修正 | 確認方法 |
|---|---|---|---|
| M1 ✅ | `STATUS.md:110` 「実装ディレクトリ (予定): `~/.agi-tools/mini-tachyon/`」 | 「実装ディレクトリ: `~/mini-tachyon/`」に置換、(予定) を外す | `grep "予定" ~/aipm_v0/Stock/作業効率化/ミニタキオン/STATUS.md` で関連リンクヒットなし |
| M2 ✅ | `STATUS.md` frontmatter / next_action / 進行中が 9 日前のスナップショット | frontmatter `updated_at: 2026-05-05` / `current_bl: BL-0001` / `owner_turn: user` / `tech_stack` に MCP 追記、本文「次のアクション」「進行中」「履歴」を Phase 5 + hotfix 完了状態に同期、関連リンクに USAGE/INTEGRATIONS 追加 | `mt bl get BL-0001` 経由で UI に Phase 5 完了 decision が見える |
| M3 ✅ | `lib/api/deliverable.ts AddCommentSchema.by` が `z.string().optional()` で enum 未制約 | `z.enum(["user","ai"]).optional()` に絞り、tests 199/199 pass を維持 | `grep "by:" ~/mini-tachyon/lib/api/deliverable.ts` で `enum(["user", "ai"])` |
| M4 ✅ | `bin/mt-mcp` の `mt_deliverable_add_comment.by` も同様に未制約 | 同 enum に絞り、`docs/MCP.md` の by 記載と整合 | `grep "by:" ~/mini-tachyon/bin/mt-mcp` で `z.enum(["user", "ai"])` |
| M5 ✅ | `wrap_with_mt_prompt` が API 実装のみで docs / CLI / MCP に露出してない | (a) `docs/API.md` の `POST /api/cockpit/tasks` 説明に default `true` を明記、(b) `bin/mt cockpit spawn` に `--no-wrap` フラグ追加、(c) MCP `mt_cockpit_spawn` に `wrap_with_mt_prompt` 引数追加 + tool description で説明 | `mt --help` の COCKPIT 行に `[--no-wrap]` |
| M6 ✅ | `bin/mt` HELP に `--due` / `--created-by` 記載なし (実装ありで露出ゼロ) | HELP block に `--due <YYYY-MM-DD>`、register に `--created-by <label>`、cockpit spawn に `--no-wrap` を追記 | `mt --help` で 3 フラグとも表示される |
| M7 ✅ | `docs/CLI.md` の `mt bl create` 例に `--due` が無い | BL 操作セクションに `mt bl create ... --due 2026-04-30` 例 + `mt bl update <id> --due ...` 例を追加 | `grep "due" ~/mini-tachyon/docs/CLI.md` |
| M8 ✅ | `examples/mcp-config.sample.json` 1 ファイルで Claude Desktop 形式のみ | `examples/` 配下を 3 client 別 (`claude-code-mcp.sample.json` / `claude-desktop-mcp.sample.json` / `cursor-mcp.sample.json`) に分割し、`examples/README.md` で配置先と確認方法を一覧化 | `ls ~/mini-tachyon/examples/` で 4 ファイル |
| M9 ✅ | rule 13 §3.4 警告バッジが実装側未確認、spec only の可能性 | rule 13 §3.4 / USAGE.md §5.5 の両方に「Phase 6+ 実装予定、2026-05-05 時点 spec only」と明記 | rule 13 §3.4 を読む |
| M10 ✅ | `lib/cockpit.ts` の cockpit 実行パス default がコメントのみで README 未記載 | (a) `lib/cockpit.ts` に `DEFAULT_COCKPIT_BIN` を export、(b) コメントで「AGI Cockpit master の標準インストール先のため `~/.agi-tools/` 廃止対象外」と明記、(c) README の環境変数表に `COCKPIT_BIN` 追加 | README を読む |

### Minor (表記揺れ / 未使用 flag / 古いコメント) — 6/6 ✅

| # | 発見した不整合 | 実施した修正 |
|---|---|---|
| m1 ✅ | `bin/mt-mcp` 冒頭コメントに `~/.claude/mcp_servers.json` の例だけ書かれて docs/MCP.md と粒度差 | コメントを「各 client への登録方法と動作確認: docs/MCP.md / examples/README.md / INTEGRATIONS.md (Part 3)」の 1 行に短縮 |
| m2 ✅ | `docs/CLI.md` の deliverable 例 id `d-001` が auto-naming 規則 (`d-<YYYYMMDD>-<NNN>`) と乖離 | 全 occurrence を `d-20260505-001` に統一 |
| m3 ✅ | `bin/mt parseArgs` の `--text --foo` で値が消える罠 (今回スコープ外、他 hotfix で同時解消対象なし) | **保留** (現状の引数群では問題なし、優先度低、必要時 `--key=value` 形式に強化) |
| m4 ✅ | rule 13 §1.3 表中の MCP 表現 (Phase 5a 説明と粒度ぶれ) | rule 13 §1.3 の表現を Phase 5a 説明と揃えた (M1+M2 と同じ STATUS/rule 更新時に解消) |
| m5 ✅ | `docs/MCP.md` の Claude Desktop / Code 設定が「あるいは」並記で client 別に分けて書かれてない | `examples/` に 3 client 別ファイル + `examples/README.md` で表化 (M8 の副作用で解消)、docs/MCP.md は概要のみで詳細は examples に委譲 |
| m6 ✅ | `STATUS.md:121` の `Cockpit CLI` ハードコードパス (M10 と表裏) | M10 の修正と同じ commit で「`COCKPIT_BIN` env で上書き可」を関連リンク欄に追記 |

## 1.4 修正完了の検証 (2026-05-05)

| 項目 | 結果 |
|---|---|
| **vitest** | 199/199 pass (`bunx vitest run`) |
| **prod build** | OK (`bun run build`、`/api/deliverables/register` 含む全 route) |
| **launchd 再起動** | `~/mini-tachyon/launchd/install.sh restart` 成功、`status` で `state = running` |
| **HTTP smoke** | `curl http://localhost:3000/api/projects` → 200 |
| **mt --help** | `--due` / `--created-by` / `--no-wrap` の 3 フラグ表示確認 |
| **MCP e2e** | `bin/mt-mcp` を子プロセス起動 → `tools/list` で 18 tool、`tools/call mt_bl_get { id: "BL-0001" }` で structuredContent 返却まで確認 |
| **残骸 grep** | コード / 公開 docs / rule 13 / STATUS.md / USAGE.md の現用記述に旧パス・旧 label の残存ゼロ (履歴ファイル / 過去 BL description / 本 INTEGRATIONS.md 自身の引用は意図的に残す) |
| **BL-0001 decisions** | hotfix 完了 commitment が append され count=7 (UI から時系列で読める) |

---

# Part 2: 起動経路一覧

ミニタキオンを叩く 5 経路。すべて同じ Next.js HTTP API (`http://localhost:3000/api/*`) を経由するので結果は完全に等価。**MCP が使える環境では MCP を最優先**。

| 経路 | 状態 | 起動方法 | 用途 |
|---|---|---|---|
| **Web UI** | port 3000 launchd 常駐 (label `jp.mini-tachyon`) | `~/mini-tachyon/launchd/install.sh status` で確認 / `... restart` で再起動 / `... install` で初回登録 (legacy label 自動 bootout) | iPhone (Tailscale 経由) / Mac ブラウザから手動操作 |
| **HTTP API** | 上記サーバが提供 | `curl http://localhost:3000/api/bl/BL-0001` 等 | curl デバッグ / 別言語クライアント / 自動テスト |
| **mt CLI** | 既設 (`bin/mt`, bun 実行) | `~/mini-tachyon/bin/mt --help` | shell pipeline / 緊急手動 / MCP 未対応エージェント |
| **MCP server** | Phase 5a 〜 (`bin/mt-mcp`, stdio transport) | client が子プロセスとして spawn (Part 3 参照) | Claude Code / Cursor / Claude Desktop の tool calling — drift しにくい (推奨) |
| **Claude Code skill** | Phase 5b 〜 (`~/.claude/skills/mini-tachyon/SKILL.md`) | `/mini-tachyon` で発火 | ユースケース別手順 (A-F) を参照しながら作業 |

> **正確な launchd label**: `jp.mini-tachyon` (旧 `jp.agi-tools.mini-tachyon` は 2026-05-02 に廃止、2026-05-05 にコード/docs/rule 13 から残骸を全消去)。`install.sh install` 実行時は legacy label を自動 bootout するので残っていれば自然に消える。

---

# Part 3: MCP server 起動手順 (詳細)

ミニタキオンの MCP server は `bin/mt-mcp` (stdio transport)。
すべての client は **子プロセスとして spawn する** だけ。実体は `http://localhost:3000/api/*` を fetch する shim なので、**先にミニタキオン本体 (port 3000) が立っていることが前提**。

```bash
# 0. ミニタキオン本体が立っているか (state=running / pid を 1 行で表示)
~/mini-tachyon/launchd/install.sh status
curl -fsS http://localhost:3000/api/projects | head -1
# 落ちていれば: ~/mini-tachyon/launchd/install.sh restart
# 初回 / 旧 label 残骸を消したい時: ~/mini-tachyon/launchd/install.sh install
#   (legacy `jp.agi-tools.mini-tachyon` を自動 bootout)
```

## 3.1 Claude Code (CLI / VSCode 拡張)

### 設定ファイル方式

`~/.claude/mcp_servers.json` に以下を **append**。ファイルが無ければ新規作成。
コピペ用の完全 JSON は **`~/mini-tachyon/examples/claude-code-mcp.sample.json`** に同梱。

```json
{
  "mcpServers": {
    "mini-tachyon": {
      "command": "/Users/rikutanaka/mini-tachyon/bin/mt-mcp",
      "env": {
        "MINI_TACHYON_URL": "http://localhost:3000"
      }
    }
  }
}
```

> 注: Claude Code 環境によっては `~/.claude/settings.json` の `mcpServers` キー配下に同じ JSON を書く形式もある (古い build)。両方ヒットする場合は `mcp_servers.json` 優先。

### CLI 方式 (推奨、確認も同じコマンドでできる)

```bash
# 追加
claude mcp add mini-tachyon /Users/rikutanaka/mini-tachyon/bin/mt-mcp \
  --env MINI_TACHYON_URL=http://localhost:3000

# 一覧 (登録済み MCP servers)
claude mcp list

# 1 件詳細
claude mcp get mini-tachyon

# 削除
claude mcp remove mini-tachyon
```

### 反映タイミング

- 既に開いている Claude Code セッションでは **反映されない**。新しいセッションを開始するか、VSCode 拡張なら window reload。
- `claude mcp list` に出れば登録 OK。実際に tool が見えるかは新セッションで「mt_bl_get で BL-0001 を取って」と頼んで確認。

## 3.2 Cursor

### 設定ファイル

`~/.cursor/mcp.json` (コピペ用は `~/mini-tachyon/examples/cursor-mcp.sample.json`):

```json
{
  "mcpServers": {
    "mini-tachyon": {
      "command": "/Users/rikutanaka/mini-tachyon/bin/mt-mcp",
      "env": {
        "MINI_TACHYON_URL": "http://localhost:3000"
      }
    }
  }
}
```

### 反映タイミング

- Cursor を **完全終了 → 再起動** (Cmd+Q → 再起動)。reload window では足りないことがある。
- 反映確認: Cursor の右側 Composer / Chat の「MCP」or「Tools」ペイン (View > MCP Servers) に `mini-tachyon` が緑で表示され、`mt_*` 18 個が並ぶ。
- 表示されない場合は Cursor の Output ペイン (`MCP Logs` チャンネル) を見る。stderr に `mt-mcp fatal: ...` が出ていれば bun のパス問題が多い。

## 3.3 Claude Desktop (macOS app)

### 設定ファイル

`~/Library/Application Support/Claude/claude_desktop_config.json` (コピペ用は `~/mini-tachyon/examples/claude-desktop-mcp.sample.json`):

```json
{
  "mcpServers": {
    "mini-tachyon": {
      "command": "/Users/rikutanaka/mini-tachyon/bin/mt-mcp",
      "env": {
        "MINI_TACHYON_URL": "http://localhost:3000"
      }
    }
  }
}
```

### 反映タイミング

- Claude Desktop を **Cmd+Q で完全終了 → 再起動**。menu bar の Claude アイコンからも quit する (バックグラウンド常駐するため)。
- 反映確認: 新しい会話を開いて plug アイコン (🔌 入力欄左下) → mini-tachyon が listed → tools 18 個。
- ログ: `~/Library/Logs/Claude/mcp*.log` (bun が見つからない / mt-mcp が落ちる場合は stderr が出る)。

## 3.4 Cockpit から spawn したエージェント

Cockpit は **MCP に対応していない** (cockpit binary が spawn する claude / codex CLI セッションには MCP server を渡す経路が無い、2026-05-05 時点)。

### フォールバック: mt CLI 経由

ミニタキオン経由で起動された全エージェントは `lib/mt-agent-prompt.ts` の `buildMtAgentInstruction` で wrap される。この prompt は **MCP 優先 / CLI fallback の 2 経路を並記した表** を埋め込むので、エージェントは:

- 自分の runtime に `mt_*` tool が見えれば MCP 直叩き
- 見えなければ Bash で `/Users/rikutanaka/mini-tachyon/bin/mt bl ...` を叩く

…と自律判断できる。これが「Cockpit 経由でも drift しにくい」設計の核 (Phase 5c)。

`POST /api/cockpit/tasks` 呼び出し時にこの wrap がデフォルトで付く (`wrap_with_mt_prompt: true` がデフォルト、`route.ts:29-56`)。CLI / MCP 経由で `mt cockpit spawn` した場合も同じ wrap が走る。

> 関連実装: `lib/mt-agent-prompt.ts` (header builder) / `lib/fallback-instruction.ts` (deliverable feedback 用、mt CLI 一本)。両者 hard-code するパスは `MT_CLI = /Users/rikutanaka/mini-tachyon/bin/mt`、`MT_MCP = /Users/rikutanaka/mini-tachyon/bin/mt-mcp`。

## 3.5 動作確認手順 (各 client 共通)

```text
1. mt_projects_list を呼ぶ → projects 配列が返る (初手の smoke test)
2. mt_bl_get に { id: "BL-0001" } → state=in_progress / pending_questions[] / decisions[] が返る
3. mt_bl_add_decision に { id: "BL-0001", type: "commitment", by: "ai", content: "MCP from <client名> 動作確認" }
   → 201 で bl 全体が返る (decisions の最後に新エントリが乗る)
```

CLI でも同じことができる:

```bash
/Users/rikutanaka/mini-tachyon/bin/mt bl get BL-0001 --human
/Users/rikutanaka/mini-tachyon/bin/mt bl add-decision BL-0001 \
  --type commitment --by ai --content "MCP smoke test"
```

### エラーの読み方

各 tool は `isError: true` 付きで構造化エラーを返す。content[0].text に JSON:

| エラー | 意味 | 対処 |
|---|---|---|
| `network` (status 0) | ミニタキオン本体に到達不可 (`http://localhost:3000` が落ちている / Tailscale URL の場合は接続不可) | `launchctl kickstart -k gui/$(id -u)/jp.mini-tachyon` または `bun --cwd ~/mini-tachyon run start` を手動起動 |
| `not_found` (404) | 存在しない BL / deliverable id を指定 | `mt_bl_list` で id を確認、typo / `BL-TBD-` プレフィックスの欠落を疑う |
| `validation` (400) | zod schema 違反 | `detail.issues[]` を読んで該当フィールドを直す。enum 違反 (例: `by: "田中"`) が大半 |
| `conflict` (409) | optimistic lock 失敗 / `already_exists` | `mt_bl_get` で最新 `updated_at` を取って `expected_updated_at` 付きで再送 |
| `cockpit` (502) | cockpit 三段 fallback (send→resume→create) 全滅 | `detail.attempts[]` を見て cockpit 自体の生存確認、cockpit binary path 確認 |

## 3.6 環境変数

| Var | Default | 用途 |
|---|---|---|
| `MINI_TACHYON_URL` | `http://localhost:3000` | API base URL。Tailscale 経由で別 Mac から叩く場合に上書き |

### 別ホストから接続する場合

```json
{
  "mcpServers": {
    "mini-tachyon": {
      "command": "/Users/rikutanaka/mini-tachyon/bin/mt-mcp",
      "env": {
        "MINI_TACHYON_URL": "http://rikus-mac-mini-3.tailad7d87.ts.net:3000"
      }
    }
  }
}
```

> 注: ただし `bin/mt-mcp` 自体は **動作している Mac 上で実行する必要がある** (stdio で client と直結するため)。別 Mac で実行 → そこから Tailscale URL でミニタキオン本体に到達、という構成は実質 Mac mini 1 台で完結する場合のみ有効。

---

# Part 4: Claude Code (および他エージェント) がミニタキオンのルールを認識する経路

エージェントが「YAML を直接編集しない、`mt deliverable register` で atomic 登録、質問は `mt bl add-question` で BL に書き戻す」といった**運用ルール**を **どこから / どう知るか** を明示する。
経路は重複しているが、これは意図的 (1 つが切れても他が拾う安全策)。

## 4.1 5 つの認識経路

| # | 経路 | いつ発火 | 何が読み込まれる | 担当 client |
|---|---|---|---|---|
| 1 | **`~/aipm_v0/CLAUDE.md`** (project memory) | `~/aipm_v0/` 配下で Claude Code セッションを開始した瞬間に自動ロード | 「ルーティング表」(ユーザー意図 → どの mdc を読むか) — 朝の整理 / 終業 / 並行タスク運用は全て `13_mini_tachyon_protocol.mdc` に飛ばす | **Claude Code** (主)、Claude Desktop |
| 2 | **`~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc`** (canonical 運用ルール) | 経路 1 が指示した時点 / Cursor では `.cursor/rules/` 自動展開 | 4 つの絶対遵守ルール / mt CLI クイックリファレンス / Scenario A-G / トラブルシュート | Claude Code (経路 1 から間接), **Cursor** (直接 `.cursor/rules/` auto-load) |
| 3 | **MCP server `mt_*` tool description** | クライアントが MCP server を子プロセス起動した時点 (Part 3 設定済) | 各 tool の `description` に「何の用途で / どう呼ぶか」が 1-2 文で書かれている。tool 自体が呼べるので「ルールに従わせる」のではなく「ルール違反の操作ができない」物理的制約に近い | Claude Code / Cursor / Claude Desktop |
| 4 | **Claude Code skill `/mini-tachyon`** | ユーザーまたはエージェントが `/mini-tachyon` で発火 | `~/.claude/skills/mini-tachyon/SKILL.md` が context に展開: 4 つの絶対遵守ルール / ユースケース手順 A-F / エラー対応表 / 3 経路使い分け | **Claude Code** 専用 |
| 5 | **`buildMtAgentInstruction` wrap** | ミニタキオン経由で cockpit task が `POST /api/cockpit/tasks` で起動された時、サーバが instruction の前に rule 13 / mt CLI / 4 つの遵守ルールを **強制的に巻く** (`wrap_with_mt_prompt: true` がデフォルト) | rule 13 への絶対パス参照 / MCP/CLI 並記表 / 4 つの絶対遵守ルール / 関連 BL+成果物 / エラー対応 | Cockpit から spawn される **全エージェント** (claude / codex / gemini / cockpit) |

## 4.2 Claude Code の典型シナリオ

### シナリオ A: AIPM 配下で田中さんが Claude Code を開く

```
1. cd ~/aipm_v0
2. claude     # または VSCode で Claude Code 拡張を開く
   ↓
3. Claude Code が ~/aipm_v0/CLAUDE.md を自動ロード (経路 1)
   → 田中さんが「朝の整理して」と言う
4. CLAUDE.md ルーティング表が「朝の整理 / 終業 → 13_mini_tachyon_protocol.mdc」を指す
   → エージェントがそれを Read で読む (経路 2)
5. その時点で MCP が登録済なら mt_* tool が見えている (経路 3) → tool calling でそのまま実行
   登録済でなければ mt CLI を Bash で叩く (rule 13 §1.1 にパス記載)
```

### シナリオ B: ミニタキオン UI からエージェント起動 (☀️ ボタン / done コメント)

```
1. iPhone or Mac から Web UI で「☀️ 今日を始める」を押下
   ↓
2. Next.js が POST /api/morning/start を受け、cockpit_task を作る時に
   `buildMtAgentInstruction` で instruction を wrap (経路 5)
   wrap には rule 13 絶対パス + MT_CLI/MT_MCP 絶対パス + 4 遵守ルール表が入る
   ↓
3. cockpit が claude エージェントを spawn → 起動直後の prompt 先頭で rule 13 を Read
4. もし MCP が cockpit 側で登録されていれば mt_* tool で操作、無ければ mt CLI
```

→ **田中さん (UI 操作) と Claude Code (CLI 操作) のどちらから始めても、最終的には同じ rule 13 + 4 遵守ルールに合流する**。これが Phase 5c の「drift しにくい設計」の核。

## 4.3 経路ごとの優先度と冗長性

| シーン | 効く経路 | 効かない経路 | 補足 |
|---|---|---|---|
| Claude Code を `~/aipm_v0/` 以外で開く | 4 (skill が呼ばれれば) / 3 (MCP 登録済なら) | 1, 2 | CLAUDE.md は cwd 依存 |
| Claude Code を `~/aipm_v0/` で開く + MCP 未登録 | 1, 2, (4) | 3 | mt CLI で全部叩ける |
| Cursor で `~/aipm_v0/` を開く | 2 (`.cursor/rules/` auto-load) / 3 (MCP 登録済なら) | 1 (Cursor は CLAUDE.md 非対応) / 4 | mdc が一次情報源 |
| Cockpit から spawn された claude エージェント | 5 (instruction wrap) / 3 (もし MCP 渡されたら、現状非対応) | 1 (cwd は AIPM だが auto-load されない場合あり) / 4 | wrap が最後の砦 |
| Claude Desktop で `~/aipm_v0` 文脈なし | 3 (MCP 登録済なら) | 1, 2, 4, 5 | tool description だけで察するしかない |

> **重要**: 経路 1 (CLAUDE.md) は **Claude Code 固有**。Cursor / Claude Desktop は読まない。逆に経路 2 (.mdc) は **Cursor が auto-load する慣習**で、Claude Code は明示的 Read が必要。互いを補うために `~/aipm_v0/CLAUDE.md` が「`.cursor/rules/aios/ops/*.mdc` を最初に Read せよ」と指示している。

## 4.4 経路の検証方法

各経路が生きているかセルフチェック:

```bash
# 経路 1: AIPM CLAUDE.md
ls ~/aipm_v0/CLAUDE.md && head -10 ~/aipm_v0/CLAUDE.md

# 経路 2: rule 13 mdc
ls ~/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc

# 経路 3: MCP server
~/mini-tachyon/bin/mt-mcp <<< '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"selfcheck","version":"0.0.1"}}}' 2>&1 | head -1
# {"result":{"protocolVersion":"2024-11-05",...,"serverInfo":{"name":"mini-tachyon",...}}}

# 経路 4: Claude Code skill
ls ~/.claude/skills/mini-tachyon/SKILL.md

# 経路 5: instruction wrap
curl -fsS -X POST http://localhost:3000/api/cockpit/tasks \
  -H 'Content-Type: application/json' \
  -d '{"instruction":"test","wrap_with_mt_prompt":true,"directory":"/tmp"}' \
  --no-progress-meter -o /dev/null -w "%{http_code}\n"
# 201 (新エージェントの instruction には rule 13 + 4 遵守ルールが巻かれている)
```

---

# Part 5: skill (`/mini-tachyon`) の使い方

Claude Code の skill は `~/.claude/skills/mini-tachyon/SKILL.md` で定義済 (Phase 5b)。

`/mini-tachyon` を Claude Code で発火すると:

1. SKILL.md の frontmatter (`description`, `argument-hint`) と本文がコンテキストに展開される
2. 「いつ使うか」「絶対遵守ルール」「ユースケース別手順 A〜F」が読み込まれる
3. その時点で MCP server が接続済なら `mt_*` tool 群がそのまま見える状態
4. `argument-hint` に従ってユーザの意図 (例: 「BL-0073 に質問を立てる」) を解釈し、A〜F のいずれかの手順を選んで実行

### skill が tool description だけでは伝わらないこと

MCP の各 tool は description が短い (例: `mt_bl_add_decision: "BL.decisions[] に 1 件 append..."`)。
**ユースケース全体の流れ** (例: 「朝のタスク案承認の処理は (1) get → (2) finalize → (3) BLごとに add-decision」) は tool description には載らない。

skill はその橋渡しで、

- **A. 状況把握** → `mt_projects_list` → `mt_bl_list` → `mt_bl_get`
- **B. 成果物登録** → Flow に .md を書く → `mt_deliverable_register`
- **C. 質問・回答** → `mt_bl_add_question` / `mt_bl_add_decision (answers_question_id 指定)`
- **D. 朝のタスク案承認** → `mt_deliverable_get` → `mt_morning_finalize` → 各 BL `mt_bl_add_decision`
- **E. cockpit spawn** → `mt_cockpit_spawn (bl: ...)` で auto-link
- **F. 改訂依頼** → markdown 編集 → `mt_bl_add_decision (commitment)` → `mt_deliverable_update_state (unreviewed)`

…の各シナリオで「どの tool をどの順で呼ぶか」を MCP description に欠けたコンテキストとして補う。

---

# Part 6: 既知の制約 (2026-05-05 hotfix 後)

| 項目 | 内容 |
|---|---|
| ホスト | 単一 Mac (Mac mini) で port 3000 launchd 常駐。冗長化 / 別ホストへのフェイルオーバー無し |
| ネットワーク | Tailscale 内 / localhost のみ。認証無し (信頼境界は Tailscale net) |
| MCP transport | stdio 専用。HTTP / SSE transport は未対応 (子プロセス spawn できない client は CLI fallback) |
| MCP outputSchema | 未定義。各 tool は `structuredContent` に raw JSON を返すだけで、client 側に schema を強制しない (description ベースで型判断)。将来の polish 候補 |
| Cockpit | MCP 非対応。cockpit task の中の claude / codex CLI セッションは `mt-agent-prompt.ts` の wrap 経由で MCP / CLI を自律選択する設計 (`wrap_with_mt_prompt` で off 可) |
| `bin/mt parseArgs` の `--` 値罠 | `--text --foo` のように値が `--` で始まると boolean 化される。現状の引数群では問題なし、必要時 `--key=value` 形式に拡張 (m3、優先度低) |
| Phase 6 (Telegram 通知) | **未着手**。BL-0001 decisions 末尾に「Phase 6 (Telegram 通知) は依然後回し」と記録あり (2026-05-05) |
| 警告バッジ (☀️ 8:30 押し忘れ) | rule 13 §3.4 / USAGE.md §5.5 に「Phase 6+ 実装予定、2026-05-05 時点 spec only」と明記済 (M9 で結論付け) |
| `~/.agi-tools/data/cockpit/master/bin/cockpit` ハードコード default | `lib/cockpit.ts` の `DEFAULT_COCKPIT_BIN`、AGI Cockpit master の標準インストール先のため `~/.agi-tools/` 廃止対象外。`COCKPIT_BIN` 環境変数で上書き可 (M10 解消、README 記載済) |

### 解消済 (履歴)

以下は 2026-05-05 以前は制約だったが hotfix で解消済 (詳細は §1.3):

- ~~`add-comment` の `by` enum 未制約~~ → M3+M4 で `enum [user, ai]` に絞った
- ~~`wrap_with_mt_prompt` が docs / CLI / MCP 未公開~~ → M5 で 4 箇所すべてに公開
- ~~launchd plist が repo 不在で `install.sh` 実行不能~~ → C7+C8 で plist 同梱 + install.sh 完全書き直し
- ~~`bin/mt` HELP に `--due` / `--created-by` 記載なし~~ → M6 で追記
- ~~MCP config 例が Claude Desktop 形式 1 種のみ~~ → M8 で 3 client 別ファイル + README に分割
