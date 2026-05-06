# BL-0079 — Phase 0 実行ログ

**作業日**: 2026-05-06
**作業者**: AI (mt cockpit-task ab2f1e5a) / SSH 経由
**実行根拠**: `04_migration_plan.md` Phase 0 / 田中さん承認 (5/6 「OK、進めてください」)
**対象**: TOP (ID=10) を AI HTML 化、tmp/front.php を最小化

このドキュメントは Phase 0 (TOP 置換) の作業時系列ログ。各 Step の実行コマンド・出力・結果・所要時間を記録。

---

## 環境情報

| 項目 | 値 |
|---|---|
| リモートホスト | my0126@my0126.xsrv.jp:10022 |
| リモートサーバ | sv12363 (Linux Ubuntu 22.04) |
| ドキュメントルート | /home/my0126/core-driven.com/public_html |
| PHP (WP-CLI 用) | /opt/php-8.3.30/bin/php |
| WordPress | 6.9.4 |
| アクティブテーマ | swell_child (親 swell v2.12.0) |
| 対象固定ページ | ID=10 / slug=top / status=publish |
| バックアップ保管先 (リモート) | ~/backups/coredriven/20260506_phase0/ |
| バックアップ保管先 (ローカル) | ~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/ |

---

## Step 0.1 — リモートでバックアップ取得 ✅ 完了

**開始**: 2026-05-06 10:06 JST
**所要**: 1 分

### 0.1.1 tmp/front.php 物理バックアップ

```bash
ssh xserver '
mkdir -p ~/backups/coredriven/20260506_phase0
TS=$(date +%Y%m%d_%H%M%S)
cd ~/core-driven.com/public_html/wp-content/themes/swell_child
cp tmp/front.php tmp/front.php.backup_$TS
cp tmp/front.php ~/backups/coredriven/20260506_phase0/tmp_front.php.original
'
```

**結果**:
- TS=`20260506_100631`
- `tmp/front.php.backup_20260506_100631` 作成 (112,025 bytes / 元と同サイズ)
- `~/backups/coredriven/20260506_phase0/tmp_front.php.original` も保存

### 0.1.2 swell_child フォルダ全体スナップショット

```bash
cd ~/core-driven.com/public_html/wp-content/themes
tar czf ~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz swell_child
```

**結果**:
- `swell_child_snapshot.tar.gz` 作成 (403,158 bytes ≈ 393 KB)
- 全 PHP / CSS / JS / SCSS を含む

### 0.1.3 WP DB ダンプ

```bash
PHP=/opt/php-8.3.30/bin/php
$PHP /usr/bin/wp db export ~/backups/coredriven/20260506_phase0/db_dump.sql --add-drop-table --path=$DOC
```

**結果**:
- `db_dump.sql` 作成 (3,342,743 bytes ≈ 3.2 MB)
- 全テーブル + DROP TABLE 文付き (=完全リストア可能)
- WP-CLI 出力: `Success: Exported to '/home/my0126/backups/coredriven/20260506_phase0/db_dump.sql'.`

### バックアップディレクトリ最終状態

```
~/backups/coredriven/20260506_phase0/
├── db_dump.sql                    (3,342,743 bytes)
├── swell_child_snapshot.tar.gz    (  403,158 bytes)
└── tmp_front.php.original         (  112,025 bytes)
```

---

## Step 0.1.4 — ローカルへの二重保管 ✅ 完了

**所要**: 5 秒

```bash
scp -P 10022 my0126@my0126.xsrv.jp:~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz \
    ~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/backup_swell_child_phase0.tar.gz
```

**結果**: ローカルに `backup_swell_child_phase0.tar.gz` (403,158 bytes) 保存

## Step 0.1.5 — TOP post_content ローカル保存 ✅ 完了

```bash
ssh xserver 'wp post get 10 --field=post_content --path=...' > backup_top_post_content_20260506.html
```

**結果**: `backup_top_post_content_20260506.html` 作成 (**0 bytes**)
**所見**: TOP (ID=10) の post_content は **空** = 想定通り (見えていたコンテンツは tmp/front.php 由来)。

## バックアップ完了状態

| 種類 | リモート | ローカル | サイズ |
|---|:-:|:-:|---|
| tmp/front.php (アトミック復旧用) | ✅ tmp/front.php.backup_20260506_100631 | - | 112,025 bytes |
| tmp/front.php (バックアップディレクトリ) | ✅ tmp_front.php.original | - | 112,025 bytes |
| swell_child snapshot | ✅ | ✅ backup_swell_child_phase0.tar.gz | 403,158 bytes |
| WP DB dump | ✅ db_dump.sql | - | 3,342,743 bytes |
| TOP post_content (Phase 0 前) | - | ✅ backup_top_post_content_20260506.html | 0 bytes (空) |

---

## Step 0.2 — 画像 5 枚アップロード ✅ 完了

**開始**: 2026-05-06 10:08 JST
**所要**: 30 秒

```bash
ssh xserver 'mkdir -p ~/core-driven.com/public_html/wp-content/uploads/coredriven-html'
cd ~/Downloads/coredriven_html_inspect/assets
scp -P 10022 logo-core-driven.png logo.svg tanaka.jpg machida.jpg yoshida.webp \
    my0126@...:~/core-driven.com/public_html/wp-content/uploads/coredriven-html/
ssh xserver 'cd ~/.../coredriven-html/ && chmod 644 *.png *.svg *.jpg *.webp'
```

**結果**: 全 5 ファイルアップロード + パーミッション 644 設定

| ファイル | サイズ | HTTP |
|---|---|:-:|
| logo-core-driven.png | 24,746 | 200 ✅ |
| logo.svg | 945 | 200 ✅ |
| tanaka.jpg | 1,259,169 | 200 ✅ |
| machida.jpg | 294,412 | 200 ✅ |
| yoshida.webp | 45,992 | 200 ✅ |

**追加発見**: 同フォルダに田中さんが先ほど手動アップロードした形跡 (`logo-core-driven.jpeg` / `logo.jpeg` / `yoshida.jpeg`) があったが、AI HTML が参照しているのは `.png` / `.svg` / `.webp` なので影響なし。

---

## Step 0.3 — /contact-new/ 一時公開 ✅ 完了

**所要**: 2 秒

```bash
ssh xserver 'wp post update 708 --post_status=publish --path=...'
```

**結果**: `Success: Updated post 708.` / status: `publish`
**意図**: TOP の「相談する」ボタン (= /contact-new/) が 404 にならないよう、暫定的に公開状態にする。中身は空のままで Phase 1 で AI HTML を投入予定。

---

## Step 0.4 — tmp/front.php 最小化 ✅ 完了

**開始**: 2026-05-06 10:09 JST
**所要**: 1 分

### 0.4.1 ローカルで最小化版 PHP 作成
- `/tmp/tmp_front_minimal.php` (30 行 / 約 1 KB)
- `the_content()` ループだけで TOP 固定ページの post_content を出力する設計

### 0.4.2 構文チェック
- ローカル: PHP 未インストールでスキップ
- リモート (PHP 8.3.30): **`No syntax errors detected`** ✅

### 0.4.3 アトミック置換
```bash
ssh xserver 'cd ~/.../swell_child/tmp && mv front.php.new front.php'
```

**結果**:
| ファイル | サイズ |
|---|---|
| front.php (新) | **1,081 bytes** |
| front.php.backup_20260506_100631 (旧) | 112,025 bytes |

→ 縮小率 99% (旧 112KB → 新 1KB)

### 0.4.4 動作確認
```bash
curl -sI "https://core-driven.com/" → HTTP/2 200 OK ✅
curl -sL "https://core-driven.com/" | grep "すべての人や企業" → 0 件 ✅
```

→ 旧 tmp/front.php の直書きコンテンツが完全に消えた。HTML 化前の「ヘッダー + 空白 + フッター」状態に到達。

---

## Step 0.5 — TOP post_content に AI HTML 投入 ✅ 完了

**開始**: 2026-05-06 10:09 JST
**所要**: 30 秒

### 0.5.1 AI HTML をリモートに転送
```bash
scp -P 10022 coredriven_top_paste_ready_v2.html (36,321 bytes) my0126@...:/tmp/
```

### 0.5.2 WP-CLI で post_content 更新
```bash
wp post update 10 --post_content="$(cat /tmp/coredriven_top_paste_v2.html)"
```

**結果**: `Success: Updated post 10.`
- New post_content length: **36,323 bytes** ✅
- post_status: `publish` ✅

### 0.5.3 公開後の自動検証

| 検査項目 | 期待 | 結果 |
|---|---|:-:|
| HTTP ステータス | 200 | **200** ✅ |
| Hero「経営者の熱意を実現する」出現 | ≥1 | **2** ✅ |
| Members「田中」(RIKU TANAKA) | 1 | **1** ✅ |
| Members「吉田」(MASANAGA YOSHIDA) | 1 | **1** ✅ |
| Members「町田」(DAICHI MACHIDA) | 1 | **1** ✅ |
| 新画像パス `/wp-content/uploads/coredriven-html/` | ≥3 | **4** ✅ |
| 旧 Hero「すべての人や企業」残存 | 0 | **0** ✅ |
| 旧 biz「Restaurant AI Lab」残存 | 0 (※) | **1** (※ナビメニュー Sub-menu のみ、本文無し) |

→ **TOP は AI HTML に完全置換されている**。ナビメニュー内の「Restaurant AI Lab.」リンクは Sub-menu に残るが、これは Phase 1 のメニュー再編対象 (R-5 リスク認識済)。

---

## Step 0.6 — 田中さん視覚確認 (進行中・田中さんの作業)

田中さんに依頼中:
- シークレットウィンドウで `https://core-driven.com/` を開く
- `04_migration_plan.md §7.1` の 25 項目チェックリストを実施
- 結果を AI に共有

### 想定される表示
```
[SWELL ヘッダー: ロゴ + メニュー (TOP / Business / Company / News / Contact)]
   ↓
[AI HTML Hero: 大きなキャッチコピー + 「相談する」「サービスを見る」ボタン]
   ↓
[Role / Challenges / Services / Strengths / Members / Final CTA]
   ↓
[SWELL フッター]
```

---

## 異常検知 / ロールバック実施履歴

(該当なし — 異常があれば追記)

---

## サマリ (作業完了後に追記)

(Step 0.6 OK 後に記載)
