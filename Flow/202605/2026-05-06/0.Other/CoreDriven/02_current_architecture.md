# BL-0079 — CoreDriven HP 現状構成 設計書

**作成日**: 2026-05-06
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft
**根拠**: SSH 経由で `my0126@my0126.xsrv.jp` のファイル構造を直接確認 (2026-05-06 時点)

---

## 1. インフラ構成

```
┌──────────────────────────────────────────────┐
│ Browser (訪問者)                              │
└──────────────────────────────────────────────┘
        ↓ HTTPS
┌──────────────────────────────────────────────┐
│ Xserver (sv12363)                             │
│  ホスト: my0126.xsrv.jp                       │
│  Linux Ubuntu 22.04 / kernel 6.8              │
│  ├─ nginx (前段プロキシ)                       │
│  ├─ Apache (後段、PHP 実行)                    │
│  ├─ PHP 5.4 (デフォルト) / 8.3.30 (推奨)       │
│  ├─ MySQL (DB)                                │
│  └─ ホームディレクトリ: /home/my0126/          │
└──────────────────────────────────────────────┘
```

### 1.1 SSH 接続情報
- ホスト: `my0126.xsrv.jp`
- ポート: `10022`
- ユーザー: `my0126`
- 認証: 公開鍵 (パスワード認証無効)
- WP-CLI: `/usr/bin/wp` (Xserver 標準同梱)

### 1.2 ホスティングディレクトリ
```
/home/my0126/
├── core-driven.com/             ← 本プロジェクト対象
│   └── public_html/             (ドキュメントルート)
├── fubenna.jp/                  (別サイト)
├── restaurant-career-lab.com/   (別サイト)
└── my0126.xsrv.jp/              (Xserver 自動生成)
```

---

## 2. WordPress 構成

### 2.1 バージョン
- **WordPress**: 6.9.4
- **アクティブテーマ**: `swell_child` (子テーマ)
- **親テーマ**: `swell` (v2.12.0)
- **フォールバック**: WordPress 標準 `index.php`

### 2.2 主要プラグイン (検出されたもの)
- SEO SIMPLE PACK 3.6.2 (SEO meta 出力)
- All-in-One WP Migration (バックアップ・移行)
- TS Webfonts for XSERVER (Xserver Web フォント)
- (その他 SWELL 同梱)

### 2.3 テーマ階層 (WP のテンプレート選択ロジック)
WordPress は `is_front_page()` の場合下記の順でテンプレートを探す:

```
1. front-page.php       ← swell_child / swell に存在しない (検出されず)
2. home.php             ← swell_child に存在するが、page.php が先に呼ばれる
3. page-{slug}.php      ← page-top.php は存在しない
4. page-{ID}.php        ← page-10.php は存在しない
5. page.php             ← ★ swell_child/page.php が呼ばれる
6. singular.php
7. index.php
```

→ TOP は `swell_child/page.php` 経由で表示される。

---

## 3. ファイル配置 (実機確認済)

### 3.1 swell_child の中身

```
/home/my0126/core-driven.com/public_html/wp-content/themes/swell_child/
├── functions.php              (1,438 bytes — style.css と main.js を enqueue)
├── home.php                   (1,554 bytes — 投稿一覧用、未使用)
├── index.php                  (302 bytes — フォールバック)
├── memo.php                   (6,032 bytes — 用途不明)
├── page.php                   (2,769 bytes — ★ 固定ページ全部の入口)
├── style.css                  (子テーマ宣言)
├── main.js                    (JavaScript)
│
├── tmp/
│   └── front.php              (★★★ 112,025 bytes — TOP の中身が直書き)
│
├── parts/
│   ├── archive/
│   ├── breadcrumb.php         (9,010 bytes)
│   ├── footer/
│   ├── header/
│   ├── home_content.php       (4,522 bytes)
│   ├── icon_list.php          (1,562 bytes)
│   ├── page_head.php          (681 bytes)
│   ├── post_list/
│   ├── profile_box.php        (2,726 bytes)
│   ├── sidebar_content.php    (488 bytes)
│   ├── single/
│   ├── top/
│   └── top_title_area.php     (2,605 bytes)
│
├── assets/
│   ├── style.css              (.custom-message__* CSS — Hero メッセージ用)
│   ├── bz_area.css            (.biz__* CSS — Restaurant AI Lab 等用)
│   └── styles/
│       └── breakpoints/
│           ├── _320up.scss
│           ├── _425up.scss
│           ├── _700up.scss
│           ├── _960up.scss
│           ├── _1024up.scss
│           ├── _1280up.scss
│           ├── _1400up.scss
│           ├── _1920up.scss
│           ├── _base.scss
│           ├── _bz.scss
│           └── _company.scss
│
├── classes/
├── lib/
└── swell/                     (継承用フォルダ)
```

### 3.2 アップロード済みアセット (`/wp-content/uploads/`)
```
2024/12/最終確認版_CoreDrivenロゴ＿横組み_カラー.png    (現在ヘッダーに使われている)
2025/01/03-scaled.jpg                                   (旧 PC 用 MV、5/6 削除済)
2025/01/04-scaled.jpg                                   (旧 SP 用 MV、5/6 削除済)
2025/01/Restaurant-AI-Lab.png                           (tmp/front.php 内で参照)
2025/01/名称未設定-1.jpg                                  (背景パターン)
2025/02/テスト用.png                                     (custom-message セクション内)
... (その他)
```

> **AI HTML 用の画像 (logo / tanaka.jpg / machida.jpg / yoshida.webp) はまだアップロード未実施**。Phase 0 Step 2 でアップする。

---

## 4. 固定ページ一覧 (WP-CLI 取得結果)

| ID | スラッグ | タイトル | 状態 | テンプレート | 表示の中身 |
|---|---|---|:-:|---|---|
| **10** | `top` | TOP | publish | (default) | **`tmp/front.php` 直書きの 112KB HTML** |
| 53 | `company` | Company | publish | (default) | post_content + page.php 内独自「メディア」セクション |
| 54 | `news` | News | publish | (default) | post_content (投稿リスト) |
| 3 | `privacy-policy` | Privacy Policy | publish | (default) | post_content |
| 55 | `contact` | Contact | **draft** | (default) | 非公開 (現状機能していない) |
| 704 | `biz-core` | Biz Core | draft | (default) | 5/6 作成、空 |
| 706 | `ai-core` | AI Core | draft | (default) | 5/6 作成、空 |
| 708 | `contact-new` | Contact | draft | (default) | 5/6 作成、空 |
| 710 | `company-new` | Company | draft | (default) | 5/6 作成、空 |

---

## 5. ホームページ表示の仕組み (詳細)

### 5.1 WP 設定
```
設定 → 表示設定 → ホームページの表示 = 固定ページ
ホームページ = ID=10 (slug=top, title=TOP)
投稿ページ = (未設定)
```

### 5.2 page.php の挙動 (実コード)
**ファイル**: `swell_child/page.php` (2,769 bytes)

```php
<?php
if (! defined('ABSPATH')) exit;
get_header();                                  // ヘッダー出力 (l-header)
if (is_front_page()) :                         // ← TOP の時だけ
    SWELL_Theme::get_parts('tmp/front');       // ★ tmp/front.php を呼ぶ
else :                                         // ← TOP 以外
    while (have_posts()) :
        the_post();
        // 通常の固定ページ処理:
        ?>
        <main id="main_content">
            <div class="post_content">
                <?php the_content(); ?>        // ← post_content (ブロック本文)
            </div>
            <?php if (is_page('company')): ?>
                <!-- ★ /company/ 限定の独自処理 -->
                <!-- タグ=media の投稿 9 件を表示 -->
            <?php endif; ?>
        </main>
        <?php
    endwhile;
endif;
get_footer();                                  // フッター出力 (l-footer)
```

### 5.3 tmp/front.php の中身 (112KB)
**ファイル**: `swell_child/tmp/front.php`
**サイズ**: 112,025 bytes / 約 2,000 行
**実 HTML 出力**:
```html
<!-- ▼▼▼ ここからオリジナルHTMLを追加 ▼▼▼ -->
<div class="custom-message">
    <!-- Hero: 「すべての人や企業には、それぞれ独自の価値観やビジョンがあります」 -->
    <!-- 3 人写真 (テスト用.png) -->
</div>

<!-- ▼▼▼ ここからオリジナルHTMLを追加 ▼▼▼ -->
<!-- business-section.html -->
<div class="biz__container">
    <div id="ai" class="biz__card reverse">
        <!-- Restaurant AI Lab. -->
    </div>
    <div id="career" class="biz__card">
        <!-- Restaurant Career Lab. -->
    </div>
    <div id="biz" class="biz__card">
        <!-- 事業開発支援事業 -->
    </div>
</div>
```

→ これがブラウザに表示されている。WP の固定ページ TOP (ID=10) のブロックエディタには何も入っていない (post_content が空) ため、田中さんが固定ページ編集画面で「ブロックが無い」と認識した。

### 5.4 アクセスから表示までのデータフロー

```
[ユーザがブラウザで https://core-driven.com/ にアクセス]
        ↓
[Xserver nginx → Apache → PHP 8.3]
        ↓
[WordPress 6.9.4 が起動]
        ↓
[WP_Query: page_on_front=10 を取得]
        ↓
[テンプレ階層: front-page.php なし → page.php を選択]
        ↓
[swell_child/page.php 実行]
        ├─ get_header()  →  parts/header/ のテンプレ群を出力
        ├─ is_front_page() = true
        └─ SWELL_Theme::get_parts('tmp/front')
              ↓
              swell_child/tmp/front.php 実行
              ├─ have_posts() ループで the_post() (= ID=10)
              └─ オリジナル HTML を直接出力
                  ├─ <div class="custom-message">...</div>
                  └─ <div class="biz__container">...</div>
        └─ get_footer() → parts/footer/ のテンプレ群を出力
        ↓
[完成した HTML がブラウザに返る]
```

---

## 6. CSS とスタイルの読み込み構造

### 6.1 functions.php による enqueue
```php
add_action('wp_enqueue_scripts', function () {
    // main.js を読み込む (キャッシュバスタはファイル mtime)
    wp_enqueue_script('child_script', get_stylesheet_directory_uri() . '/main.js', ...);
}, 11);

add_action('wp_enqueue_scripts', 'enqueue_child_theme_styles');
function enqueue_child_theme_styles() {
    wp_enqueue_style('parent-style', get_template_directory_uri() . '/style.css');
    wp_enqueue_style('child-theme-style', get_stylesheet_directory_uri() . '/assets/style.css', ['parent-style'], '1.0.0');
}
```

### 6.2 実際にロードされる CSS
1. SWELL 親テーマの `main.css` (block / icons 等)
2. swell_child の `style.css` (子テーマ宣言)
3. swell_child の `assets/style.css` (.custom-message__* 用)
4. swell_child の `assets/bz_area.css` (.biz__* 用)
5. SWELL カスタマイザーで生成される `swell_custom-inline-css` (CSS 変数 :root)
6. SEO SIMPLE PACK 等のプラグイン CSS

---

## 7. ナビゲーションメニューの構造

### 7.1 メニュー構成 (実機確認)
```
TOP                            → /
Business. (ドロップダウン)      → /#ai (アンカー)
├─ Restaurant AI Lab.          → /#ai
├─ Restaurant Career Lab.      → /#career
└─ 事業開発支援事業             → /#biz
Company                        → /company/
News                           → /news/
Contact                        → https://forms.gle/GbRSdeKqWngAqx4WA  ← Google Form 直リンク
```

### 7.2 ロゴ
```
URL: /wp-content/uploads/2024/12/最終確認版_CoreDrivenロゴ＿横組み_カラー.png
```

---

## 8. 既知の問題 / 技術的負債

| ID | 問題 | 影響 | 解決済? |
|---|---|---|:-:|
| K-1 | TOP コンテンツが PHP 直書きで管理画面から編集不可 | 田中さんが更新できない | ❌ (本プロジェクトで解決) |
| K-2 | tmp/front.php がテンプレート階層外の特殊位置で発見しにくい | 引き継ぎ困難 | ❌ (本プロジェクトで整理) |
| K-3 | `/company/` のメディアセクションが page.php に直書き | 編集に PHP 知識必要 | ❌ (将来 cleanup) |
| K-4 | `/contact/` (ID=55) が draft のまま放置されている | スラッグ占有のみで機能無し | ❌ (将来 cleanup) |
| K-5 | Business メニューが `/#ai` 等のアンカーリンクで TOP に飛ぶが、Phase 0 後 AI HTML には該当 ID が無い | リンクが効かなくなる可能性 | ❌ (Phase 1 のメニュー再編で解決) |
| K-6 | PHP 5.4 がデフォルト、WP-CLI が PHP 8.3 を手動指定する必要あり | コマンド実行時に毎回 PATH 指定 | ⚠️ (運用上は許容) |
| K-7 | swell_child/memo.php (6KB) の用途が不明 | 引き継ぎ時の混乱 | ❌ (将来要確認) |

---

**END OF CURRENT ARCHITECTURE.** 移行後の構成は `03_future_architecture.md` を参照。
