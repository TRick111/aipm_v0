# `.obsidian/workspace.json` のコンフリクト対処法

## workspace.json とは

Obsidianがワークスペースの**UIの状態**をリアルタイムに保存するファイル。具体的には以下の情報が記録される:

- **開いているタブとその順序** — どのマークダウンファイルをどのタブで開いているか
- **サイドバーの状態** — 左サイドバー（ファイルエクスプローラ、検索、ブックマーク）、右サイドバー（バックリンク、タグ、アウトライン等）の開閉・タブ切替状態
- **パネルのレイアウトとサイズ** — サイドバーの横幅（px）、分割ペインの方向
- **アクティブなペイン** — 最後にフォーカスしていたペインのID
- **最近開いたファイルの履歴** — `lastOpenFiles` の配列
- **リボン（左端アイコン列）の表示/非表示設定**

**このファイルは成果物ではなく、Obsidianの「画面設定」が記録されているだけ。**

## なぜコンフリクトが起きるのか

### 根本原因: 複数の場所から同じリポジトリを開いている

| 操作 | workspace.json への影響 |
|---|---|
| Obsidianでファイルを開く/閉じる | タブ情報が即座に書き換わる |
| サイドバーを開閉する | パネル状態が更新される |
| 別のタブに切り替える | `active` や `currentTab` が変わる |
| Cursorでファイルを編集してGit操作する | Obsidianが裏で workspace.json を更新している可能性 |

つまり、**Obsidianを開いているだけで workspace.json は常に変化し続けている**。Cursorでgit pull/commitする瞬間にObsidian側で書き変わったworkspace.jsonとの差分が衝突する。

### 典型的なコンフリクト発生パターン

1. PC-A（Obsidian）で作業 → workspace.json が更新される
2. PC-Bで同じリポジトリをpull → PC-B側のObsidianが別のworkspace.jsonを持っている
3. PC-Bでcommit/push → PC-Aでpullするとコンフリクト

または:

1. Obsidianが workspace.json を更新（バックグラウンド）
2. 同時にCursorからgit操作 → マージ時にコンフリクト

## コンフリクトが起きたときの対処法

### 結論: **どちら側の変更を採用しても問題ない**

workspace.json はUI状態の記録に過ぎないため、どちらのバージョンを採用してもデータは失われない。

### 推奨手順

```bash
# 方法1: 今使っているマシンのObsidianの状態を優先（最も簡単）
git checkout --ours .obsidian/workspace.json
git add .obsidian/workspace.json

# 方法2: リモート側（別マシン）の状態を優先
git checkout --theirs .obsidian/workspace.json
git add .obsidian/workspace.json
```

**どちらを選んでもOK。** Obsidianを再起動すれば現在の画面状態で上書きされる。

### Obsidian上に「Conflict」ファイルが出た場合

Obsidianの一部プラグイン（Obsidian Git等）がコンフリクトを検知すると、`workspace (conflict YYYY-MM-DD).json` のようなファイルが作られることがある。

→ **そのConflictファイルは削除してOK。** 本体の workspace.json さえ残っていればObsidianは正常に動作する。

## 恒久対策: .gitignore に追加する

workspace.json は個人のUI設定であり、Git管理する必要がない。`.gitignore` に追加してしまうのが最善策。

```gitignore
# .gitignore に以下を追加
.obsidian/workspace.json
.obsidian/workspace-mobile.json
```

### 追加手順

```bash
# 1. .gitignore に追加
echo ".obsidian/workspace.json" >> .gitignore
echo ".obsidian/workspace-mobile.json" >> .gitignore

# 2. Gitの追跡から外す（ファイル自体は残る）
git rm --cached .obsidian/workspace.json

# 3. コミット
git add .gitignore
git commit -m "gitignoreにworkspace.jsonを追加（コンフリクト防止）"
```

これ以降、workspace.json はGitで追跡されなくなり、コンフリクトは発生しなくなる。

## 補足: .obsidian で他にも.gitignoreすべきファイル

| ファイル | 内容 | gitignore推奨 |
|---|---|---|
| `workspace.json` | UI状態 | **推奨** |
| `workspace-mobile.json` | モバイルUI状態 | **推奨** |
| `graph.json` | グラフビューの設定 | 任意 |
| `app.json` | アプリ設定 | 共有したいなら残す |
| `appearance.json` | テーマ設定 | 共有したいなら残す |
| `community-plugins.json` | プラグインリスト | 共有したいなら残す |
