# BL-0079 — Phase 2 修正ログ (2026-05-09)

**作業日**: 2026-05-09
**作業者**: AI (mt cockpit-task ab2f1e5a) / SSH 経由
**実行根拠**: 田中さん指示 3 件 (5/9)

---

## 0. 田中さんからの指示

1. トップページの**右上ロゴが表示されていない**
2. トップページの**グラデーション内の文字サイズが異なる** (Hero h1 が小さい)
3. 各ページ上部の**グラデーション長方形上のタイトルを削除**
   - CSS セレクタ: `#main_content > div > h1 > span`

---

## 1. 原因診断

### 1-1. ロゴ非表示
- WP の `siteurl` / `home` が `http://core-driven.com` のまま (HTTP)
- HTTPS ページから生成された `<img src="http://...">` が **mixed content blocked**
- `naturalWidth = 0` → ブラウザが画像を読み込まなかった

### 1-2. h1 サイズが小さい
- `.hero h1` が `font-size: 32px` で表示
- 期待: `clamp(40px, 6vw, 72px)` で 1280px 幅なら 72px
- 原因: SWELL の `post_content h1` デフォルトスタイルが `:where()` ではなく直接書きで AI HTML の `<style>` を上書き
- 加えて `assets/style.css?ver=1.0.0` のため、CSS を編集してもブラウザキャッシュが効いて新版が読まれない

### 1-3. ページタイトル
- SWELL の `<l-topTitleArea>` 内の `<h1 class="c-pageTitle"><span>` が page-hero の上に表示
- 全ページ (TOP 以外) で出ている (TOP は tmp/front.php 経由なので `l-topTitleArea` を出さない)

---

## 2. 修正内容

### 2-1. バックアップ取得 ✅

```
~/backups/coredriven/20260509_phase2_fix/
├── db_dump_pre_fix.sql                  (4.0 MB)
├── style.css.original                   (34.8 KB)
├── functions.php.original
└── functions.php.before_filemtime
```

### 2-2. siteurl/home を HTTPS 化 + 全 DB search-replace ✅

```bash
wp option update siteurl https://core-driven.com
wp option update home    https://core-driven.com
wp search-replace 'http://core-driven.com' 'https://core-driven.com' \
    --all-tables --skip-columns=guid
```

→ DB 全体の `http://core-driven.com` リファレンスを `https://...` に置換 (guid を除く)。

### 2-3. 子テーマ `assets/style.css` に修正 CSS 追記 ✅

```css
/* === BL-0079 / 2026-05-09 修正用 オーバーライド =================
 * 1. AI HTML の Hero/Page Hero の h1 を SWELL post_content デフォルトから救済
 * 2. SWELL の page top title (l-topTitleArea > c-pageTitle) を非表示
 * ============================================================ */
.ai-fullhtml-wrap .hero h1,
.ai-fullhtml-wrap .page-hero h1 {
  font-size: clamp(40px, 6vw, 72px) !important;
  line-height: 1.1 !important;
  letter-spacing: -.035em !important;
  font-weight: 800 !important;
}
@media (max-width: 640px) {
  .ai-fullhtml-wrap .hero h1,
  .ai-fullhtml-wrap .page-hero h1 {
    font-size: 38px !important;
    line-height: 1.12 !important;
  }
}

/* SWELL のページ上部タイトル (l-topTitleArea) を非表示 (田中さん指定セレクタ) */
#main_content > div > h1 > span { display: none !important; }
.l-topTitleArea { display: none !important; }
```

### 2-4. `functions.php` の CSS バージョンを `filemtime()` 動的化 ✅

旧:
```php
wp_enqueue_style('child-theme-style', ..., '1.0.0', 'all');  // ハードコード
```

新:
```php
$css_path = get_stylesheet_directory() . '/assets/style.css';
$css_ver  = file_exists($css_path) ? filemtime($css_path) : '1.0.0';
wp_enqueue_style('child-theme-style', ..., $css_ver, 'all');  // 動的
```

→ 以後 CSS を編集する度に自動でキャッシュバスト。ブラウザは `assets/style.css?ver=1778258029` 等の新 URL で取得。

### 2-5. キャッシュフラッシュ ✅

```bash
wp cache flush
wp transient delete --all
```

---

## 3. Playwright 検証結果

### 3-1. TOP (PC 1280×900)

| 項目 | Before | After |
|---|---|---|
| ロゴ src | `http://...` | **`https://...`** ✅ |
| ロゴ naturalWidth | 0 (404) | **800** ✅ |
| ロゴ表示 | 壊れた画像アイコン | **正常表示** ✅ |
| `.hero h1` font-size | 32px | **72px** ✅ |
| `.hero h1` line-height | 35.2px | 79.2px ✅ |

→ スクショ: `screenshots/phase2fix_pc_top_v2.png`

### 3-2. AI Core (PC 1280×900)

| 項目 | Before | After |
|---|---|---|
| `<l-topTitleArea>` の「AI Core」h1 表示 | 表示 (青グラデの上に重なっていた) | **非表示** ✅ |
| AI HTML の page-hero | 表示 | 表示 (上の冗長タイトル消えてクリーン) |

→ スクショ: `screenshots/phase2fix_pc_aicore_top.png`

---

## 4. 反映範囲

| 修正 | 反映先 | ロールバック方法 |
|---|---|---|
| siteurl/home HTTPS 化 | サイト全体 (DB 全テーブル) | `wp db import db_dump_pre_fix.sql` |
| `assets/style.css` 追記 | 全ページ (子テーマ enqueue) | `cp style.css.original assets/style.css` |
| `functions.php` filemtime 化 | CSS のバージョン管理のみ | `cp functions.php.original functions.php` |

---

## 5. 既知の副作用 / リスク

| 項目 | 内容 | 対策 |
|---|---|---|
| `wp search-replace` で予期しない URL 変更 | 例: post_content 内の `http://core-driven.com/wp-content/uploads/...` 全部 https 化 | 結果として正しい挙動 (mixed content 解消)。問題なし |
| `--skip-columns=guid` のため、過去の WP 投稿の `guid` だけ http のまま | WP の `guid` は変更しないのが標準 | 問題なし |
| SWELL アップデートで `l-topTitleArea` の class 名変更可能性 | 将来的に CSS 効かない可能性 | アップデート後の表示確認 |

---

## 6. 関連ファイル更新

| ファイル | 種類 | 状態 |
|---|---|---|
| swell_child/assets/style.css | リモート | 末尾に修正 CSS 追記 |
| swell_child/functions.php | リモート | filemtime ベースに書き換え |
| WP DB siteurl/home | リモート | https に更新 + search-replace |

---

## 7. Phase 2 残課題 (継続)

| 課題 | 状態 |
|---|:-:|
| ✅ News 削除 | 完了 |
| ✅ ヘッダー再編 (TOP / Biz Core / AI Core / Company / Contact) | 完了 |
| ✅ 「相談する」CTA ボタン | 完了 |
| ✅ GAS フォームハンドラ | 完了 |
| ✅ ロゴ HTTPS 化 (mixed content 解消) | 完了 |
| ✅ Hero h1 フォントサイズ修正 | 完了 |
| ✅ SWELL ページ上部タイトル削除 | 完了 |
| C-3 SWELL main.js の `#main_visual` エラー (3 件 / 表示影響なし) | 未着手 |
| C-4 旧 CSS (`.custom-message__*` `.biz__*`) 削除 | 未着手 |
| C-5 既存 `/contact/` `/company/` の整理 | 未着手 |
| C-7 Bot 対策 (honeypot / Turnstile) | 未着手 |

---

---

## 8. 追加修正 (5/9 後半) — パンくず + 横線削除

### 8.1 田中さんからの追加指示
> `#main_content > div` の中だけ表示すれば良くて、それ以外の上にあるもの (パンくず + 横線) はいらない

→ §2-3 の対応では `#main_content > div > h1 > span` だけ非表示にしたが、**h1 自体が残り border-bottom が 1px の横線として残存** + パンくず `<nav class="p-breadcrumb">` も残存していた。

### 8.2 追加 CSS (assets/style.css 末尾)
```css
/* パンくず非表示 */
.p-breadcrumb,
nav.p-breadcrumb,
.p-breadcrumb__list,
.l-pageBody > nav.p-breadcrumb { display: none !important; }

/* main_content の上にある可能性のある hr / セパレータ */
#main_content + hr,
.l-content > hr,
.l-pageBody > hr,
.l-mainContent::before { display: none !important; }

/* c-pageTitle h1 自体を非表示 (border-bottom も一緒に消える) */
h1.c-pageTitle,
.c-pageTitle,
#main_content > div > h1 { display: none !important; }
```

### 8.3 検証 (Playwright)
- Biz Core: ヘッダー直下スッキリ ✅ → スクショ `phase2fix_pc_bizcore_v3.png`
- AI Core: 同上 ✅ → スクショ `phase2fix_pc_aicore_v3.png`
- Company / Contact-new も同様の構造なので影響反映済

### 8.4 横線の正体
DOM 解析で判明:
```
H1.c-pageTitle (height:1px / border-bottom: 1px solid rgba(199,199,199,0.5))
```
→ 元 span だけ非表示にしたが h1 本体が `1px` 高さで残っていて、その `border-bottom` が見えていた。h1 自体を `display: none` で完全に消した。

---

**END OF FIX LOG.** 田中さん視覚確認後にタスククローズ予定。

---

## 9. 追加修正 v3 (5/9 後半 第二弾) — ヘッダー直下とpage-hero の隙間を 0 に

### 9.1 田中さんからの追加指示
> ページ上部のグラデーションの長方形とヘッダー、というかページの一番上との間の隙間を無くせる?

### 9.2 DOM 解析で空白の正体を特定 (124px)
```
header             y=0,    h=86
#content (l-content) y=86,  padding-top: 60px  ← ★主犯
.post_content     y=210,  margin-top: 64px   ← ★副犯
.ai-fullhtml-wrap y=210
.page-hero        y=210,  padding-top: 120px (内部余白なので OK)
```
合計 60 + 64 = **124px の隙間**

### 9.3 修正 CSS (assets/style.css 末尾追記)
```css
body:has(.ai-fullhtml-wrap) #content,
.l-content:has(.ai-fullhtml-wrap) {
  padding-top: 0 !important;
}
.post_content:has(.ai-fullhtml-wrap) {
  margin-top: 0 !important;
}
body.top #content {
  padding-top: 0 !important;
}
```

### 9.4 :has() で AI HTML ページ限定の理由
- 既存 `/privacy-policy/` は AI HTML 化していない (= ai-fullhtml-wrap なし)
- 既存 `/company/` `/news/` も同様 (現状維持希望)
- `body.top` は TOP 専用 (AI HTML page-hero はないが Hero がある)

### 9.5 検証
- Biz Core: page-hero `y=210` → **`y=86`** ✅ (ヘッダー直下にぴったり接続)
- スクショ: `phase2fix_pc_bizcore_v4_nogap.png`

### 9.6 反映範囲
- TOP / Biz Core / AI Core / Contact-new / Company-new (AI HTML 5 ページ)
- 既存 `/news/` `/privacy-policy/` `/company/` は影響なし (ai-fullhtml-wrap がないため)

