# credentials/ — マーケダッシュボード生データ取得用 認証情報

このディレクトリは **生データ取得（食べログ / 食べログノート / HPG / RB）に使う ID/PW を置く専用の場所** です。

## ファイル

| ファイル | git 管理 | 内容 |
|---|:---:|---|
| `accounts.example.yaml` | ✅ コミット | テンプレート（フィールド構造の参照用） |
| `accounts.yaml` | ❌ **gitignore で除外** | 実値を書く場所。これを取得スクリプト／SOP が読む |
| `README.md` | ✅ コミット | 本ファイル |

## 使い方

```bash
cd Stock/RestaurantAILab/マーケダッシュボード/credentials/
cp accounts.example.yaml accounts.yaml
# accounts.yaml をエディタで開いて埋める
```

`accounts.yaml` は親ディレクトリの `.gitignore` で除外済（`credentials/accounts.yaml`）。**間違って `git add credentials/` しても accounts.yaml は staged にならない**。テンプレート側（`accounts.example.yaml`）と本 README のみがコミット対象。

## セキュリティ運用ルール

- **絶対に `accounts.yaml` をコミットしない**。`git status` でステージ前に確認
- リポジトリ外（1Password 等）への移行は AIPM 進捗管理表 T-17 で議論中。それまでの暫定保管場所として本ディレクトリを使用
- accounts.yaml を読むのは:
  - 取得 SOP 実行時の手動参照（user の手元のみ）
  - 将来追加する Playwright スクレイパ（環境変数経由 or ファイル直読）
- パスワードを誤って log / 標準出力に出さないこと（スクレイパ実装時に注意）

## 関連

- 取得手順 SOP: `../docs/取得SOP/README.md`
- 既存スクレイパ実装: `../scripts/scrapers/`
- 既存スキル: `tabelog-marketing-scrape`
