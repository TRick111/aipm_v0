# Core Driven HP

株式会社 Core Driven のコーポレートサイト (https://core-driven.com) の改修プロジェクト。

## 構成

- ホスティング: Xserver (`sv12363.xserver.jp`, ユーザー `my0126`)
- WordPress: 7.0
- テーマ: SWELL（子テーマ `swell_child`）
- SEO プラグイン: SEO SIMPLE PACK 3.6.2
- ローカル参照 HTML: `/Users/rikutanaka/Downloads/coredriven_html_inspect/`
- フロントページ: 固定ページ ID 10 (`/`)
- WP-CLI alias: `~/.wp-cli/config.yml` の `@coredriven`（接続は SSH host `xserver-coredriven`）

## 接続

```bash
# SSH
ssh xserver-coredriven

# WP-CLI（サーバー側 PHP 8.3 を明示）
ssh xserver-coredriven 'cd ~/core-driven.com/public_html && /usr/bin/php8.3 -d error_reporting=E_ERROR /usr/bin/wp <command>'
```

## ディレクトリ

- `backup/` — 設定変更前のスナップショット (タイムスタンプ付き)
- `proposals/` — Meta Title / Description の提案 (CSV / JSON)
- `investigations/` — レイアウト崩れ調査のスクショ・差分ログ
- `STATUS.md` — 進捗
