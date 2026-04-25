# Claude Code アップデート手順書（Windows 端末向け）

- 対象: BL-0060「Claude Code アップデート」 — Windows 端末分
- 作成日: 2026-04-22
- 前提: Mac 側は Native Installer に切替済み（`claude_code_update_log.md` 参照）。Windows も同じく **Native Installer（推奨）** に揃える方針。

## 0. 結論（先に読む用の3行）

1. PowerShell を**管理者でなく通常権限で**開く
2. `irm https://claude.ai/install.ps1 | iex` を実行
3. 新しい PowerShell ウィンドウで `claude --version` を確認

設定ファイル（`%USERPROFILE%\.claude\settings.json` 等）は**そのまま残る**ので、既存方式が npm/WinGet/Cask いずれであっても、先にそれを uninstall してから Native Installer で入れ直すのが基本ライン。

## 1. 事前確認（現状把握）

PowerShell で以下を実行し、現状を記録する。

```powershell
# どこに入っているか
Get-Command claude

# バージョン
claude --version

# 設定ファイル位置
ls $env:USERPROFILE\.claude\
ls $env:USERPROFILE\.claude.json
```

`Get-Command claude` の Source 列を見て、現在の配布形態を判定する:

| Source の例 | 配布形態 | 後段で使う uninstall 手順 |
|---|---|---|
| `...\npm\claude.cmd` または `...\nodejs\...` | npm global | §3-A |
| `...\WindowsApps\...Anthropic.ClaudeCode...` | WinGet | §3-B |
| `%USERPROFILE%\.local\bin\claude.exe` | Native Installer（既に推奨形態） | §3-C |
| `...\Homebrew\...`（WSL内） | Homebrew Cask（WSL） | WSL 用手順を別途参照 |

## 2. 設定ファイルのバックアップ（必須）

念のため、Windows 側でも設定をバックアップする。

```powershell
$bk = "$env:USERPROFILE\Desktop\claude_backup_2026-04-22"
New-Item -ItemType Directory -Path $bk -Force | Out-Null
Copy-Item "$env:USERPROFILE\.claude\settings.json"       "$bk\settings.json.bak"        -ErrorAction SilentlyContinue
Copy-Item "$env:USERPROFILE\.claude\settings.local.json" "$bk\settings.local.json.bak"  -ErrorAction SilentlyContinue
Copy-Item "$env:USERPROFILE\.claude.json"                "$bk\claude.json.bak"          -ErrorAction SilentlyContinue
ls $bk
```

## 3. 既存版のアンインストール

### 3-A. npm 版を使っていた場合

```powershell
npm uninstall -g @anthropic-ai/claude-code
```

完了後、`Get-Command claude` が解決しなくなることを確認。

### 3-B. WinGet 版を使っていた場合

```powershell
winget uninstall Anthropic.ClaudeCode
```

### 3-C. すでに Native Installer の場合

uninstall 不要。§4 に進むだけで上書き更新される。即時更新したいだけなら `claude update` でも OK。

## 4. Native Installer で導入

PowerShell（**通常権限で OK、管理者は不要**）で:

```powershell
irm https://claude.ai/install.ps1 | iex
```

CMD を使っている場合は:

```bat
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> 判別方法: プロンプトが `PS C:\>` なら PowerShell、`C:\>` のみなら CMD。

インストール先は `%USERPROFILE%\.local\bin\claude.exe`（Mac の `~/.local/bin/claude` と同等）。

## 5. PATH と動作確認

インストーラが PATH を通すが、**現在開いている PowerShell ウィンドウは古い PATH のまま**なので、必ず**新しい PowerShell ウィンドウ**を開いて以下を実行する:

```powershell
Get-Command claude
# Source が %USERPROFILE%\.local\bin\claude.exe になっていること

claude --version
# 2.1.119 以降になっていること（2026-04-22 時点の latest）

claude doctor
# 設定・依存関係に異常がないこと
```

PATH が通っていない場合の応急対応:

```powershell
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
```

恒久化するには「設定 > システム > バージョン情報 > システムの詳細設定 > 環境変数」でユーザー環境変数 `Path` の先頭に `%USERPROFILE%\.local\bin` を追加。

## 6. Windows 特有の注意点

| 注意点 | 詳細 |
|---|---|
| **Git for Windows 必須** | Native Windows で動かすには `https://git-scm.com/downloads/win` の Git for Windows が必要（内部で Git Bash を使う）。WSL で動かす場合は不要 |
| **管理者権限は不要** | むしろ管理者で実行するとパス周りが個人ユーザーから見えなくなるので**避ける** |
| **PowerShell 実行ポリシー** | `irm \| iex` がブロックされたら `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` で緩める（端末1台のみのスコープ） |
| **PATH 反映タイミング** | 新規 PowerShell ウィンドウを開かないと古い PATH のまま。VS Code 内のターミナルも開き直す |
| **WSL と Native は別物** | WSL Ubuntu 側にも `claude` を入れている場合、それは別のインストールなので別途 `curl \| bash` で更新する。Windows Native と WSL のどちらを使うかは `git-scm.com` の Git for Windows の有無と PATH 解決順で決まる |
| **WinGet 版を残しておく場合** | `winget upgrade Anthropic.ClaudeCode` を定期実行する運用も可能。だが Mac との運用統一の観点で Native Installer を推奨 |
| **`claude update`** | 即時更新したいときの統一コマンド。Native 版でのみ機能 |

## 7. 自動更新の確認・調整

Native Installer 版はデフォルトで自動更新が有効。挙動を変えたい場合:

```jsonc
// %USERPROFILE%\.claude\settings.json
{
  "autoUpdatesChannel": "stable",   // "latest"（デフォ）または "stable"（約1週遅れ）
  "env": {
    "DISABLE_AUTOUPDATER": "1"      // 自動更新を完全に止めたい場合のみ
  }
}
```

## 8. 完了確認チェックリスト

- [ ] `Get-Command claude` の Source が `%USERPROFILE%\.local\bin\claude.exe`
- [ ] `claude --version` が 2.1.119 以降
- [ ] `claude doctor` がエラーを出さない
- [ ] `%USERPROFILE%\.claude\settings.json` 等の既存設定が消えていない
- [ ] 新規 PowerShell から `claude` を起動し、ログイン状態が維持されている

## 9. ロールバック（万一）

新版で問題が起きたら:

```powershell
# Native 版を削除
Remove-Item -Path "$env:USERPROFILE\.local\bin\claude.exe"          -Force
Remove-Item -Path "$env:USERPROFILE\.local\share\claude" -Recurse   -Force

# npm 版に戻す（一時的に）
npm install -g @anthropic-ai/claude-code

# またはバックアップ済みの設定を復元
Copy-Item "$env:USERPROFILE\Desktop\claude_backup_2026-04-22\settings.json.bak"        "$env:USERPROFILE\.claude\settings.json"       -Force
Copy-Item "$env:USERPROFILE\Desktop\claude_backup_2026-04-22\settings.local.json.bak"  "$env:USERPROFILE\.claude\settings.local.json" -Force
Copy-Item "$env:USERPROFILE\Desktop\claude_backup_2026-04-22\claude.json.bak"          "$env:USERPROFILE\.claude.json"                -Force
```

`~/.claude/` は Native でも npm でも共通で参照するので、配布形態を戻しても設定は引き継がれる。
