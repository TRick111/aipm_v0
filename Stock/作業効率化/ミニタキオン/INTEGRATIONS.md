# ミニタキオン 設計監査 + 統合方法 (INTEGRATIONS)

最終更新: 2026-05-05 / 対象実装: `/Users/rikutanaka/mini-tachyon/` (HEAD) / mini-tachyon Phase 5c 完了時点

このファイルは Stock 配下の長寿命リファレンス。
1. **Part 1 設計監査**: docs / 実装 / rule mdc の整合性を機械的に照合した結果と提案修正 (修正未実施)
2. **Part 2 起動経路一覧**: ミニタキオンの 5 経路を 1 表にまとめる
3. **Part 3 MCP server 起動手順**: Claude Code / Cursor / Claude Desktop / Cockpit の各 client から MCP server を立ち上げる手順 (この章を最も詳しく)
4. **Part 4 skill の使い方** / **Part 5 既知の制約**

---

# Part 1: 設計監査 (Audit)

## 1.1 チェックした範囲

| 領域 | ファイル |
|---|---|
| 運用ルール (canonical) | `/Users/rikutanaka/aipm_v0/.cursor/rules/aios/ops/13_mini_tachyon_protocol.mdc` |
| 公開 docs | `/Users/rikutanaka/mini-tachyon/docs/CLI.md`, `docs/API.md`, `docs/MCP.md` |
| skill | `/Users/rikutanaka/.claude/skills/mini-tachyon/SKILL.md` |
| サンプル | `/Users/rikutanaka/mini-tachyon/examples/mcp-config.sample.json` |
| プロジェクト STATUS | `/Users/rikutanaka/aipm_v0/Stock/作業効率化/ミニタキオン/STATUS.md` |
| CLI 実装 | `bin/mt` (HELP block + parser + 全 subcommand) |
| MCP 実装 | `bin/mt-mcp` (18 tool 登録) |
| HTTP 実装 | `app/api/**/route.ts`, `lib/api/{bl-write,bl-read,deliverable,finalize,respond}.ts` |
| zod schema | `lib/types.ts`, 各 `lib/api/*.ts` の `*Schema` |
| 組み込み prompt | `lib/mt-agent-prompt.ts`, `lib/fallback-instruction.ts` |
| index ロジック | `lib/index-store.ts` (backstop) |
| orchestration | `lib/orchestration.ts` |
| launchd | `launchd/install.sh`, `~/Library/LaunchAgents/jp.mini-tachyon.plist` |
| package | `package.json`, `README.md`, `CLAUDE.md`, `AGENTS.md` |

## 1.2 整合性 OK の確認

- **MCP tool 数**: docs/MCP.md・rule 13 §1.1 の「18 endpoint」と `bin/mt-mcp` の `server.registerTool` 18 回が一致 (`mt_bl_list/get/create/update/add_decision/add_question/consume_question` 7 + `mt_deliverable_register/get/update_state/add_comment` 4 + `mt_cockpit_spawn/send` 2 + `mt_morning_start/finalize`, `mt_evening_start` 3 + `mt_today_selected/projects_list` 2)。
- **CLI ↔ MCP ↔ docs/MCP.md の表**: docs/MCP.md §「Tool 一覧 (18)」の各 mt CLI 対応が `bin/mt` のサブコマンドと完全一致。
- **AddDecision の zod**: `lib/api/bl-write.ts AddDecisionSchema` の `type/by/content/answers_question_id` が rule 13 §2.3 と完全一致 (`type: answer|commitment|scope_change|deferred`、`by: user|ai`)。スキーマ違反は API 層で 400。
- **register の atomic 性 ↔ index-store backstop**: `lib/api/deliverable.ts registerDeliverable` が `deliverables.yaml` → `BL.deliverable_refs` の順で書き、失敗時の片側更新を `lib/index-store.ts` の `bl_id` 逆引き (line 118-127, ログ key `backstopPatched`) で救う。docs/CLI.md §「Flow ディレクトリ構造」末尾の説明と一致。
- **morning finalize**: docs/API.md / docs/CLI.md / `bin/mt-mcp mt_morning_finalize` / `lib/api/finalize.ts` の `selections[]` schema (`bl/action/spawn_class/next_action`) が完全に揃っている。
- **rule 13 §1.1 `~/mini-tachyon/bin/mt` / `~/mini-tachyon/bin/mt-mcp`** はパスが正しい (rule 13 §1.2 の docs パスも正しい)。

> **致命傷なし**。ただし以下の **critical 8 件 / moderate 10 件 / minor 6 件** の不整合あり (主に「旧パス `~/.agi-tools/mini-tachyon/`」の残骸と launchd label の不一致)。

## 1.3 発見した不整合

### Critical (実装と意味が食い違う)

| # | 場所 | 不整合 | 実装の真値 |
|---|---|---|---|
| C1 | `rule 13 mdc:100` | 朝プロンプトの絶対パスを `~/.agi-tools/mini-tachyon/lib/prompts/daily-start.md` と書いている | 実体は `/Users/rikutanaka/mini-tachyon/lib/prompts/daily-start.md` |
| C2 | `rule 13 mdc:117` | 夜プロンプトの絶対パスを `~/.agi-tools/mini-tachyon/lib/prompts/daily-wrapup.md` と書いている | 実体は `/Users/rikutanaka/mini-tachyon/lib/prompts/daily-wrapup.md` |
| C3 | `rule 13 mdc:142` | 「詳細は `~/.agi-tools/mini-tachyon/docs/CLI.md`」と案内している | 実体は `/Users/rikutanaka/mini-tachyon/docs/CLI.md` (rule 13 §1.2 の指示と内部矛盾) |
| C4 | `rule 13 mdc:443` | `mt: command not found` 対処として `~/.agi-tools/mini-tachyon/bin/mt` を絶対パスで使うよう案内 | 実体は `/Users/rikutanaka/mini-tachyon/bin/mt` (`fallback-instruction.ts:9` / `mt-agent-prompt.ts:5` の定数と矛盾) |
| C5 | `rule 13 mdc:444` | `launchctl list jp.agi-tools.mini-tachyon` を案内 | 実際にロードされている label は `jp.mini-tachyon` (`~/Library/LaunchAgents/jp.mini-tachyon.plist` / `launchctl list \| grep tachyon` で確認済み)。古い label で叩いても何も返らない |
| C6 | `docs/CLI.md:189` | 同上 `launchctl list jp.agi-tools.mini-tachyon` | 同上 (rule 13 と同じ古い label) |
| C7 | `launchd/install.sh:9-10` | `SRC=$(...)/jp.agi-tools.mini-tachyon.plist`, `DST=$HOME/Library/LaunchAgents/jp.agi-tools.mini-tachyon.plist` | (a) `launchd/` 配下に plist ファイルが存在しない (`install.sh` / `stdout.log` / `stderr.log` のみ)。`./launchd/install.sh install` を叩くと `cp: no such file or directory` で失敗する。(b) 実稼働の plist は `jp.mini-tachyon.plist` で別 label。install.sh が指す DST ファイルは存在せず、unload/load も noop。**完全に死んでいる** |
| C8 | `README.md:9` | 「起動: launchd で port 3000 常駐 (`launchd/jp.agi-tools.mini-tachyon.plist`)」 | 同上、ファイル不在。実際の plist は `~/Library/LaunchAgents/jp.mini-tachyon.plist` のみ |

### Moderate (古い参照 / 廃止済の参照 / 説明不足)

| # | 場所 | 不整合 |
|---|---|---|
| M1 | `Stock/作業効率化/ミニタキオン/STATUS.md:110` | 「実装ディレクトリ (予定): `~/.agi-tools/mini-tachyon/`」— 既に `~/mini-tachyon/` で稼働済 |
| M2 | `Stock/作業効率化/ミニタキオン/STATUS.md:7-23` | `updated_at: 2026-04-26T23:30:00+09:00` / `next_action`「Cockpit task 9682a8f0 で... 朝の整理 v2 dogfood 中」/「進行中」の 🟢 entry が **9 日前のスナップショット**。Phase 5 完了 (BL-0001 決定 2026-05-05T04:55:00.000Z) が反映されていない |
| M3 | `lib/api/deliverable.ts:37` | `AddCommentSchema.by` が `z.string().optional()` で **enum 未制約**。一方 `docs/API.md:124-130`・`SKILL.md` は `by: "user"\|"ai"` のように記載。実装は任意文字列を受け入れる |
| M4 | `bin/mt-mcp:393-401` | `mt_deliverable_add_comment` の `by: z.string().optional()` も同様に enum 未制約。tool description にも user/ai と書かれていない |
| M5 | `app/api/cockpit/tasks/route.ts:29` | `wrap_with_mt_prompt: boolean` パラメータが実装されているが `docs/API.md` に未記載、CLI / MCP 経由でも露出していない (`bin/mt cockpit spawn` は常に default = wrap される) |
| M6 | `bin/mt` HELP block (line 119-145) | `mt bl create` / `mt bl update` の `--due` フラグが実装上存在するが (line 167, 168 で送信)、HELP に記載なし。`mt deliverable register` の `--created-by` も同様 |
| M7 | `docs/CLI.md` BL 操作セクション | `mt bl create --due 2026-04-30` 例が無い (API.md には `due` 記載あり)。CLI 利用者が due を渡せることに気付きづらい |
| M8 | `examples/mcp-config.sample.json` | サンプルが Claude Desktop 系の `~/.claude/mcp_servers.json` 想定のみ。Cursor 用の `~/.cursor/mcp.json` / Claude Code の `~/.claude/settings.json mcpServers` 形式が同梱されていない (docs/MCP.md は両方記載済) |
| M9 | `rule 13 mdc:188-189` | INBOX/daily_tasks 旧運用の voice command 「INBOX」を「今日の選択」に置換する記述があるが、`mt today selected` は最新仕様と整合 (これは OK)。ただし「☀️ を 8:30 までに押し忘れ → 警告バッジ」(§3.4) は実装側に対応コードが見当たらず、**spec only / 未実装**の可能性 (要 dev 側の存否確認) |
| M10 | `lib/cockpit.ts:12` | cockpit 実行ファイルパスを `/Users/rikutanaka/.agi-tools/data/cockpit/master/bin/cockpit` でハードコード (env 上書きはあるが default が `~/.agi-tools/...`)。プロジェクト全体で「`~/.agi-tools/` 廃止」という方針と無いまぜ。cockpit 本体はまだそこに住んでいるので壊れてはいない、が方針整理が必要 |

### Minor (表記揺れ / 未使用 flag / 古いコメント)

| # | 場所 | 内容 |
|---|---|---|
| m1 | `bin/mt-mcp:13-21` のコメント例 | client 設定の例が `~/.claude/mcp_servers.json` のみ。docs/MCP.md と粒度が違う (docs はもっと詳しい) |
| m2 | `docs/CLI.md:154` `mt deliverable register` 例 | `d-orchestration-20260426-morning` という日付例がそのまま (一見 `register` 対象が orchestration に見えるが、実は orchestration は register 経由で作らない。誤読を招く) |
| m3 | `bin/mt parseArgs` (line 28-37) | `--flag` の次が `--xxx` で始まる場合は boolean 化する仕様。`--text --foo bar` のように 値の先頭が `--` だと値が消える (現状の引数群では問題ない、今後 `--text` に `--` で始まる本文を渡す未来仕様で罠) |
| m4 | `rule 13 mdc:26` の Phase 5a 説明と §1.3 の表 | Phase 5a の文言は「18 endpoint」、§1.3 の表中 MCP の説明は drift 表現。同じ意味だが粒度ぶれ |
| m5 | `docs/MCP.md:36-44` Claude Desktop の例 | `~/.claude/mcp_servers.json` か `~/.claude/settings.json` の `mcpServers` キーかを「あるいは」で並記 (現状: Claude Desktop は前者、Claude Code は後者または `claude mcp add` CLI)。client 別に表で整理した方が誤導しにくい |
| m6 | `STATUS.md:121` | `Cockpit CLI: /Users/rikutanaka/.agi-tools/data/cockpit/master/bin/cockpit` ※ M10 と表裏 |

## 1.4 提案修正 (実施しない、報告のみ)

| # | 提案修正 (1 行) |
|---|---|
| C1 | `rule 13 mdc:100` を `/Users/rikutanaka/mini-tachyon/lib/prompts/daily-start.md` に置換 |
| C2 | `rule 13 mdc:117` を `/Users/rikutanaka/mini-tachyon/lib/prompts/daily-wrapup.md` に置換 |
| C3 | `rule 13 mdc:142` を `/Users/rikutanaka/mini-tachyon/docs/CLI.md` に置換 |
| C4 | `rule 13 mdc:443` の絶対パス・symlink 例を `/Users/rikutanaka/mini-tachyon/bin/mt` に統一 |
| C5 | `rule 13 mdc:444` の `launchctl list jp.agi-tools.mini-tachyon` / `launchctl kickstart -k gui/$(id -u)/jp.agi-tools.mini-tachyon` を **`jp.mini-tachyon`** に置換 |
| C6 | `docs/CLI.md:189` の launchctl 例を `jp.mini-tachyon` に置換 |
| C7 | `launchd/install.sh` を「現行 plist (`jp.mini-tachyon.plist`) を `launchd/` 配下に置く + label 統一」または「installed plist を `~/Library/LaunchAgents/jp.mini-tachyon.plist` を canonical として README に直接書く」のいずれか。現状の install.sh は実行不能 |
| C8 | `README.md:9` を `~/Library/LaunchAgents/jp.mini-tachyon.plist` (canonical) に書き直す。または C7 と合わせて plist を repo に commit する |
| M1 | `STATUS.md:110` 関連リンクの「実装ディレクトリ (予定): `~/.agi-tools/mini-tachyon/`」を `~/mini-tachyon/` に置換し「(予定)」を外す |
| M2 | `STATUS.md` frontmatter / 「次のアクション」/「進行中」を Phase 5 完了反映に更新 (current_bl: BL-0001、updated_at: 2026-05-05) |
| M3,M4 | `AddCommentSchema.by` と `mt_deliverable_add_comment.by` を `z.enum(["user","ai"]).optional()` に絞る (または docs/SKILL を「任意文字列可」に揃える) |
| M5 | `docs/API.md` に `wrap_with_mt_prompt: boolean (default true)` を追記。`bin/mt cockpit spawn` に `--no-wrap` フラグを足してもよい (任意) |
| M6 | `bin/mt` HELP に `--due`, `--created-by` を追記 |
| M7 | `docs/CLI.md` の `mt bl create` 例に `--due 2026-04-30` を追加 |
| M8 | `examples/mcp-config.sample.json` に Cursor / Claude Code 形式のサンプルも併記 (またはファイル分割) |
| M9 | rule 13 §3.4 「警告バッジ」が未実装なら「Phase 6+ で実装予定」と明記、実装済なら根拠コードを参照 |
| M10 | `lib/cockpit.ts:12` 既定値を環境変数 `COCKPIT_BIN` に集約し default を README に記載 (現状コメントのみ) |
| m1 | `bin/mt-mcp` 冒頭コメントを「詳細は `docs/MCP.md`」に短縮 |
| m2 | `docs/CLI.md:154` 例の id を BL 系 `d-20260505-001` に変更 |
| m3 | `bin/mt parseArgs` を `--key=value` 形式 or `getopts` 風に強化 (現状の罠を埋める、優先度低) |
| m4-m6 | 表記揺れ統一 (任意) |

---

# Part 2: 起動経路一覧

ミニタキオンを叩く 5 経路。すべて同じ Next.js HTTP API (`http://localhost:3000/api/*`) を経由するので結果は完全に等価。**MCP が使える環境では MCP を最優先**。

| 経路 | 状態 | 起動方法 | 用途 |
|---|---|---|---|
| **Web UI** | port 3000 launchd 常駐 (label `jp.mini-tachyon`) | `launchctl list jp.mini-tachyon` で確認 / `launchctl kickstart -k gui/$(id -u)/jp.mini-tachyon` で再起動 | iPhone (Tailscale 経由) / Mac ブラウザから手動操作 |
| **HTTP API** | 上記サーバが提供 | `curl http://localhost:3000/api/bl/BL-0001` 等 | curl デバッグ / 別言語クライアント / 自動テスト |
| **mt CLI** | 既設 (`bin/mt`, bun 実行) | `/Users/rikutanaka/mini-tachyon/bin/mt --help` | shell pipeline / 緊急手動 / MCP 未対応エージェント |
| **MCP server** | Phase 5a 〜 (`bin/mt-mcp`, stdio transport) | client が子プロセスとして spawn (Part 3 参照) | Claude Code / Cursor / Claude Desktop の tool calling — drift しにくい (推奨) |
| **Claude Code skill** | Phase 5b 〜 (`~/.claude/skills/mini-tachyon/SKILL.md`) | `/mini-tachyon` で発火 | ユースケース別手順 (A-F) を参照しながら作業 |

> **正確な launchd label**: `jp.mini-tachyon` (rule 13 §7 / docs/CLI.md トラブルシュートに書かれている `jp.agi-tools.mini-tachyon` は **古い、動かない**)。

---

# Part 3: MCP server 起動手順 (詳細)

ミニタキオンの MCP server は `bin/mt-mcp` (stdio transport)。
すべての client は **子プロセスとして spawn する** だけ。実体は `http://localhost:3000/api/*` を fetch する shim なので、**先にミニタキオン本体 (port 3000) が立っていることが前提**。

```bash
# 0. ミニタキオン本体が立っているか
launchctl list | grep jp.mini-tachyon          # PID が出れば OK
curl -fsS http://localhost:3000/api/projects | head -1
# 落ちていれば: launchctl kickstart -k gui/$(id -u)/jp.mini-tachyon
```

## 3.1 Claude Code (CLI / VSCode 拡張)

### 設定ファイル方式

`~/.claude/mcp_servers.json` に以下を **append**。ファイルが無ければ新規作成:

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

`~/.cursor/mcp.json`:

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

`~/Library/Application Support/Claude/claude_desktop_config.json`:

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

# Part 4: skill (`/mini-tachyon`) の使い方

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

# Part 5: 既知の制約

| 項目 | 内容 |
|---|---|
| ホスト | 単一 Mac (Mac mini) で port 3000 launchd 常駐。冗長化 / 別ホストへのフェイルオーバー無し |
| ネットワーク | Tailscale 内 / localhost のみ。認証無し (信頼境界は Tailscale net) |
| MCP transport | stdio 専用。HTTP / SSE transport は未対応 (子プロセス spawn できない client は CLI fallback) |
| MCP outputSchema | 未定義。各 tool は `structuredContent` に raw JSON を返すだけで、client 側に schema を強制しない (description ベースで型判断) |
| Cockpit | MCP 非対応。cockpit task の中の claude / codex CLI セッションは `mt-agent-prompt.ts` の wrap 経由で MCP / CLI を自律選択する設計 |
| Phase 6 (Telegram 通知) | **未着手**。BL-0001 decisions 末尾に「Phase 6 (Telegram 通知) は依然後回し」と記録あり (2026-05-05) |
| 警告バッジ (☀️ 8:30 押し忘れ) | rule 13 §3.4 に spec あり、実装側コード未確認 (M9) |
| `add-comment` の `by` フィールド | サーバ側で enum 未制約 (M3, M4)。任意文字列が通る |
| `wrap_with_mt_prompt` | API 実装ありだが docs / CLI / MCP 未公開 (M5) |
| launchd plist | repo に commit されておらず (`launchd/jp.agi-tools.mini-tachyon.plist` は不在)、`install.sh` 実行不能 (C7) — 現行の `~/Library/LaunchAgents/jp.mini-tachyon.plist` は手動配置されたものが稼働中 |
