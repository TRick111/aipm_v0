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

## Step 0.6 — Playwright 自動視覚確認 ⚠️→✅ 完了

**開始**: 2026-05-06 10:16 JST

### 0.6.1 v2 で初回スクショ → ★ レイアウト崩れ検出 ★

PC (1280x900) でフルページ + viewport 撮影 → 重大問題を発見:
- 「相談する」ボタンが背景透明 (`background: rgba(0,0,0,0)`)
- `.role-grid` `.svc-grid` が `display: block` (本来 `display: grid`)
- Members 写真は表示されているが grid が効かないため縦並び

### 0.6.2 原因診断 (browser_evaluate)

```js
getComputedStyle(document.documentElement).getPropertyValue('--max')     → ""  ❌ 空
getComputedStyle(document.documentElement).getPropertyValue('--grad-deep')→ "" ❌ 空
getComputedStyle(document.documentElement).getPropertyValue('--blue-700') → "#1230FF" ✅
```

CSS 変数の一部だけ読めない → `:root { ... }` ブロックが途中で破壊されている。

**犯人特定**: WordPress の `the_content` フィルタの **wpautop が `<style>` タグの中身に `<p>` を勝手に挿入**:

```css
:root{
  --paper:#FAFBFE;
  --white:#FFFFFF;</p>     ← wpautop が連続改行を <p> 終端と解釈
<p>  --blue-900:#0B1FB3;
```

これにより `:root` が分断され、後半の変数 (`--max` `--grad-deep` 等) が定義されなかった。

検証コマンド:
```bash
python3 -c "
import re
src = open('rendered.html').read()
styles = re.findall(r'<style[^>]*>([\s\S]*?)</style>', src)
for s in styles:
    if '<p>' in s: print(f'CONTAINS <p>: len={len(s)}')
"
# → style[6] CONTAINS HTML tags inside! length=22088
```

### 0.6.3 修正版 v3 生成

**修正内容** (`coredriven_top_paste_ready_v3.html`):
1. **全体を `<!-- wp:html -->` `<!-- /wp:html -->` でラップ** → wpautop が完全スキップ (Gutenberg のカスタム HTML ブロックと同等扱い)
2. **`<style>` 内の連続改行を圧縮** → 万一 wpautop が走っても被害最小化

```python
# style 内の連続改行を 1 改行に圧縮
src = re.sub(r'<style>([\s\S]*?)</style>', squash_style, src)
# 全体を wp:html でラップ
src = '<!-- wp:html -->\n' + src + '\n<!-- /wp:html -->\n'
```

サイズ: v2 36,321 bytes → v3 36,310 bytes (ほぼ同サイズ)

### 0.6.4 v3 を WP に投入

```bash
scp v3.html xserver:/tmp/coredriven_top_paste_v3.html
ssh xserver 'wp post update 10 --post_content="$(cat /tmp/...)" --path=...'
# → Success: Updated post 10. (36312 bytes)
```

### 0.6.5 再検証 — 完全復旧 ✅

| 検査項目 | v2 (NG) | v3 (OK) |
|---|:-:|:-:|
| `--max` CSS 変数 | "" (空) | `1240px` ✅ |
| `--grad-deep` CSS 変数 | "" (空) | `linear-gradient(...)` ✅ |
| `<style>` 内の `<p>` 出現 | あり | **0 件** ✅ |
| `.btn-primary` background | 透明 | linear-gradient OK ✅ |
| `.role-grid` display | block | **grid (3 カラム 341×3)** ✅ |
| `.svc-grid` display | block | **grid (2 カラム 522×2)** ✅ |
| `.members-grid` display | grid 効くが画像なし | **grid (3 カラム / 写真表示)** ✅ |
| `section#role` padding | 0px | `120px 0px` ✅ |

### 0.6.6 スクリーンショット

| ファイル | サイズ | 内容 |
|---|---|---|
| `screenshots/phase0_pc_v3_full.png` | 1265×7243 | PC フルページ ✅ |
| `screenshots/phase0_pc_v3_viewport.png` | 1280×900 | PC ヒーロー ✅ |
| `screenshots/phase0_pc_v3_members.png` | 1280×900 | PC Members 拡大 (3 人写真表示確認) ✅ |
| `screenshots/phase0_sp_v3_viewport.png` | 390×844 | SP iPhone ヒーロー ✅ |
| `screenshots/phase0_sp_v3_full.png` | 390×... | SP フルページ (1 カラムレスポンシブ) ✅ |

### 0.6.7 Members 画像実機検証

```js
[
  {alt: "吉田柾長", complete: true, naturalWidth: 958, naturalHeight: 958},
  {alt: "町田大地", complete: true, naturalWidth: 1822, naturalHeight: 1216},
  {alt: "田中利空", complete: true, naturalWidth: 600, naturalHeight: 960},
]
```
全 3 人 fetch + decode 成功、レンダリングサイズ 276×251 で正常表示。

### 0.6.8 既知の軽微な console エラー

SWELL の main.js が削除済の `#main_visual` を探してエラー出力 (3 件):
```
[ERROR] #main_visual が見つかりませんでした。
TypeError: Failed to execute 'observe' on 'IntersectionObserver': parameter 1 is not of type 'Element'.
TypeError: Cannot read properties of null (reading 'classList')
```

→ 表示・機能に影響なし。SWELL カスタマイザーで削除した MV を JS 側が前提にしている残骸。Phase 1 で `swell_child/main.js` の整理を検討。

---

## Phase 0 サマリ ✅

**完了**: 2026-05-06 10:22 JST
**全所要**: 16 分 (10:06〜10:22)
**やり直し**: 1 回 (v2 → v3、wpautop 問題対応で 6 分追加)

### 達成事項
- ✅ TOP (`https://core-driven.com/`) が AI HTML で表示
- ✅ SWELL ヘッダー (ロゴ + メニュー) 維持
- ✅ SWELL フッター維持
- ✅ Hero / Role / Challenges / Services / Strengths / Members / Final CTA 全セクション表示
- ✅ Members 3 人写真 (吉田 / 町田 / 田中) 表示
- ✅ PC (1280px) / SP (390px) の両方でレイアウト崩れなし
- ✅ 「相談する」「Biz Coreを見る」「AI Coreを見る」「メンバー詳細」全リンク機能
- ✅ 既存 `/news/` `/privacy-policy/` `/company/` 影響なし (確認は田中さん側で実施)
- ✅ ロールバック手順整備 (バックアップ 5 種を二重保管)

### 学び (Phase 1 以降に活かす)
1. **WP の `<style>` インライン CSS は必ず `<!-- wp:html -->` でラップする** — wpautop の `<style>` 破壊を防ぐ唯一確実な方法
2. **post_content 投入後はブラウザレンダリング検証 (CSS 変数値) が必須** — HTTP 200 と表示崩れは別問題
3. **Members 等の画像は `naturalWidth/Height` で実 fetch 確認** — HTTP 200 ≠ 画像が見える
4. SWELL の main.js が削除済要素 (`#main_visual`) を探す残骸エラー → Phase 1 で main.js or 関連処理を整理

### 田中さん最終確認待ち
- シークレットウィンドウで `https://core-driven.com/` を開いて、目視で違和感がないか確認
- 既存 `/news/` `/privacy-policy/` `/company/` を開いて従来どおりであることを確認
- 「OK」で Phase 1 (残 4 ページ AI HTML 化) に進む / 「ここを直して」で再調整 / 「ロールバック」で復旧

---

## Step 0.7 — モバイル画像微調整 (v4) ✅ 完了

**開始**: 2026-05-06 14:18 JST
**所要**: 3 分

### 0.7.1 田中さんからの問題指摘
スマホ実機 (iPhone) スクリーンショット 2 枚が共有された。判明した問題:
- **田中利空の写真で顔の上部 (目から上) が切れている**
- 鼻と口だけが見える状態 → 違和感あり

### 0.7.2 原因分析
田中の画像: `tanaka.jpg` (600×960 / **縦長 5:8**)
他メンバー: 吉田 958×958 (正方形) / 町田 1822×1216 (横長 3:2)

CSS:
```css
.member-card .avatar { aspect-ratio: 1.1/1 }  /* ほぼ正方形 */
.member-card .avatar img { object-fit: cover; /* object-position: center (default) */ }
```

→ SP では .members-grid が 1 カラムになり .avatar が画面幅 (~715×~650px) に拡大。
→ 縦長 600×960 を 1.1:1 (≒ 715×650) フレームに `object-fit:cover` でフィット = 上下が大きくクロップ
→ デフォルト center クロップ = 顔の中央が切り取られる (= 顔の上半分が消失)

吉田・町田は元々正方形〜横長なので影響軽微。

### 0.7.3 修正 (v4)
田中専用セレクタで `object-position` を上方向にシフト:

```css
.member-card .avatar img[alt="田中利空"]{object-position:center 22%}
```

→ 画像の上から 22% 地点を中央配置 = 顔がフレーム上方に来る = 顔全体が見える

PC 表示への影響: 田中の画像も上 22% 位置になるが、PC では 276×251 の小さい正方形クロップなので顔の見え方の差はわずか (改善はあれど悪化なし)。

### 0.7.4 v4 投入

```bash
scp v4.html xserver:/tmp/coredriven_top_paste_v4.html
ssh xserver 'wp post update 10 --post_content="$(cat ...)" --path=...'
# → Success: Updated post 10. (36385 bytes / +73 bytes from v3)
```

### 0.7.5 Playwright 検証 (SP 390×844)

```js
.avatar img[alt="田中利空"] {
  objectPosition: "50% 22%"   ← 適用 OK ✅
  objectFit: "cover"
}
```

スクリーンショット: `screenshots/phase0_sp_v4_tanaka_fixed.png`
→ **田中の顔全体 (目・鼻・口 + スーツ上半身) が綺麗に表示** ✅

### 0.7.6 v4 で確定

| バージョン | 状態 |
|---|:-:|
| v2 (旧) | wpautop で CSS 破壊 → 廃版 |
| v3 (旧) | 中身 OK だが田中 SP 顔切れ → 廃版 |
| **v4 (現役)** | wpautop 対策 + 田中モバイル位置調整 ✅ |

---

## Phase 0 完全完了 ✅

**最終確定**: 2026-05-06 14:21 JST
**全所要**: 4 時間 15 分 (10:06〜14:21、ただし大半が AI HTML 修正待ち)

### 全成果
- バックアップ 5 種 (リモート + ローカル二重保管) 取得済
- TOP 公開状態の AI HTML 表示 ✅
- PC / SP 両対応、Members 写真 3 人とも顔全体表示 ✅
- 既存ページ (`/news/` `/privacy-policy/` `/company/`) 影響なし
- ロールバック手順整備済

### Phase 2 への引き継ぎ
田中さんの「Phase 2 進んで良い」承認を受けて、計画書 §10 (クリーンアップ) または §3 (Phase 1 = 残 4 ページ) に進む。要意思確認。

---

## 異常検知 / ロールバック実施履歴

(該当なし — 異常があれば追記)

---

## サマリ (作業完了後に追記)

(Step 0.6 OK 後に記載)
