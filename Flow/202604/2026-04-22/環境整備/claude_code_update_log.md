# Claude Code アップデート作業ログ（Mac）

- 対象: BL-0060「Claude Code アップデート」
- 実施日: 2026-04-22
- 対象端末: Mac（このMac、arm64 / Homebrew 管理）

## 1. 配布形態の変更状況（公式ドキュメント調査結果）

公式ドキュメント（https://code.claude.com/docs/en/setup）を確認した結論:

- **npm 配布は廃止されていない**。今も `npm install -g @anthropic-ai/claude-code` で導入できる
- ただし**推奨は Native Installer に変わった**（公式 setup ページの最初のタブ＝Recommended）
- npm 版は内部的に「optional dependency 経由で同じ native binary を取得し postinstall でリンクする」仕組みに変わっている。つまり npm でも実体は Native Binary（Node.js は走らない）
- Native Installer はバックグラウンド自動更新あり。Homebrew Cask / WinGet / npm は手動更新

### 公式の現行配布チャネル（2026-04-22 時点）

| 配布形態 | コマンド | 自動更新 | 備考 |
|---|---|---|---|
| **Native Installer（推奨）** | `curl -fsSL https://claude.ai/install.sh \| bash` | あり | `~/.local/bin/claude` に入る |
| Homebrew Cask（stable） | `brew install --cask claude-code` | なし（`brew upgrade`） | 約1週遅れの安定版 |
| Homebrew Cask（latest） | `brew install --cask claude-code@latest` | なし（`brew upgrade`） | 最新追従 |
| WinGet（Windows） | `winget install Anthropic.ClaudeCode` | なし | Windows 用 |
| npm | `npm install -g @anthropic-ai/claude-code` | なし | 引き続き利用可 |

「`npm` 廃止？」というユーザー認識は半分正解で、**廃止ではないが推奨ではなくなった**が正確。

## 2. 移行前の状態（Before）

| 項目 | 値 |
|---|---|
| `which claude` | `/opt/homebrew/bin/claude`（symlink） |
| 実体 | `/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe` |
| 実体ファイル種別 | Mach-O 64-bit executable arm64 |
| `claude --version` | `2.1.117 (Claude Code)` |
| 配布元 | npm global（Homebrew の node 経由） |
| 自動更新 | なし |

`npm view @anthropic-ai/claude-code version` も `2.1.117` を返しており、npm チャネルの最新には到達していた。だが Native の `latest` チャネルには **2.1.119** が公開されていたため、npm 経由だと2バージョン遅れていた状態。

### 関連設定ファイル（移行で壊さないことを確認したもの）

- `~/.claude/settings.json`（4102B）: AGI Cockpit 連携の hooks（SessionStart / UserPromptSubmit / Notification / Stop / PreToolUse / PostToolUse）と `skipDangerousModePermissionPrompt: true`、`enabledPlugins: vercel@claude-plugins-official`
- `~/.claude/settings.local.json`（102B）: `Bash(npm install:*)` / `Bash(markserv:*)` の permission allow
- `~/.claude.json`（約63KB）: プロジェクト履歴・MCP 設定など

これらは `npm uninstall -g` でも削除されないが、念のため `Flow/202604/2026-04-22/環境整備/claude_backup/` にバックアップを取得。

## 3. 移行手順（実施したもの）

### Step 1: バックアップ

```bash
mkdir -p Flow/202604/2026-04-22/環境整備/claude_backup
cp ~/.claude/settings.json       Flow/202604/2026-04-22/環境整備/claude_backup/settings.json.bak
cp ~/.claude/settings.local.json Flow/202604/2026-04-22/環境整備/claude_backup/settings.local.json.bak
cp ~/.claude.json                Flow/202604/2026-04-22/環境整備/claude_backup/claude.json.bak
```

### Step 2: npm 版をアンインストール

```bash
npm uninstall -g @anthropic-ai/claude-code
# → removed 2 packages in 215ms
```

確認: `/opt/homebrew/bin/claude` が消え、`/opt/homebrew/lib/node_modules/@anthropic-ai/` が空になったこと、`which claude` が `claude not found` になったことを確認。

### Step 3: Native Installer で導入

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

出力抜粋:

```
✔ Claude Code successfully installed!
  Version: 2.1.119
  Location: ~/.local/bin/claude
```

### Step 4: PATH 解決と動作確認

`hash -r` でシェルのコマンドキャッシュをクリアした後:

```bash
which claude     # /Users/rikutanaka/.local/bin/claude
claude --version # 2.1.119 (Claude Code)
```

`~/.local/bin/claude` は `~/.local/share/claude/versions/2.1.119` への symlink。`~/.local/bin` は `/opt/homebrew/bin` より PATH 上で先に評価される並びになっているため、シェル再起動後も新バイナリが優先される。

### Step 5: 設定ファイルの無事を確認

```bash
diff ~/.claude/settings.json       Flow/.../claude_backup/settings.json.bak       # 差分なし
diff ~/.claude/settings.local.json Flow/.../claude_backup/settings.local.json.bak # 差分なし
```

`~/.claude.json` もサイズが移行前後で 68883 → 68925 と微増しただけ（セッション情報の追記）。

## 4. 移行後の状態（After）

| 項目 | 値 |
|---|---|
| `which claude` | `/Users/rikutanaka/.local/bin/claude`（symlink） |
| 実体 | `/Users/rikutanaka/.local/share/claude/versions/2.1.119` |
| `claude --version` | `2.1.119 (Claude Code)` |
| 配布元 | Native Installer |
| 自動更新 | あり（バックグラウンドで `latest` チャネルを追従） |

## 5. 今後の運用メモ

- **自動更新で十分**。次回以降のバージョン上げのために手動オペレーションは原則不要
- 即時更新したい場合は `claude update`
- 万一更新を止めたい場合は `~/.claude/settings.json` の `env.DISABLE_AUTOUPDATER=1` を追加
- リリースチャネルを `stable`（約1週遅れ・大規模リグレッションをスキップ）に切り替えたい場合は `/config` → Auto-update channel、または `settings.json` に `"autoUpdatesChannel": "stable"`
- 旧 npm 由来の `~/.npm/_logs/` などには影響なし。`/opt/homebrew/lib/node_modules/@anthropic-ai/` は空ディレクトリのまま残るが実害なし
- バックアップ `claude_backup/` は本作業の確認が済んだら削除可

## 6. 残タスク

- Windows 端末は手順書 `claude_code_update_windows.md` を参照して別途実施
- 完了後に `Stock/定型作業/バックログ/Backlog.md` の BL-0060 Notes を更新
