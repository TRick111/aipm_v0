# BL-0079 — WordPress 実装キット (子テーマ + Custom Page Template + 運用 SOP)

**作成日**: 2026-05-05
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft（田中さん review 待ち）
**関連 BL**: BL-0079 (CoreDriven HP WordPress更新)
**前提成果物**: `Flow/202605/2026-05-03/0.Other/CoreDriven/wordpress_full_html_mechanism.md`
  → 採択方針: **(B) Custom Page Template** を最終形 / **(A) Custom HTML** を暫定 とする方針で実装。

---

## 0. このキットでできること

田中さん側で実施するのは下記 3 つだけ。

1. 子テーマ用 ZIP を WP 管理画面「外観 → テーマ → 新規追加」からアップロード（or FTP で `wp-content/themes/` に展開）
2. 「外観 → テーマ」で子テーマ `CoreDriven Child` を有効化
3. 固定ページを新規作成 → テンプレート `AI Full HTML (CoreDriven)` を選択 → 「カスタム HTML」ブロックに AI 生成 HTML を貼って公開

これで採択方針 (B) が成立。ファイル一式は本ドキュメント末尾の **付録 A〜D** にコピペ可能な状態で同梱。

---

## 1. 子テーマのファイル構成

WP の `wp-content/themes/coredriven-child/` 直下に以下の 4 ファイルを配置。

```
coredriven-child/
├─ style.css            ← 子テーマ宣言 (必須)
├─ functions.php        ← 親テーマの style.css を読み込む (推奨)
├─ template-fullhtml.php       ← (B-1) header/footer を残し本文だけ HTML を流す版
└─ template-fullhtml-bare.php  ← (B-2) wp_head / wp_footer も出さない完全 bare 版
```

- 既定では (B-1) を使う想定。ヘッダー/フッターも捨てたいページ (LP 全画面型) のみ (B-2) を選べば良い。
- 親テーマ名は **TODO（田中さん確認事項 §6 Q-A）**。`style.css` の `Template:` 行と `functions.php` の親 handle 名を確定するために必要。

---

## 2. 実装手順 (担当者向け SOP)

### 2.1 Phase A — 暫定 (A) Custom HTML で「今日中に動かす」

1. WP 管理画面 → 「ページ → 新規追加」
2. タイトルに `CoreDriven Top (HTML版)` 等を入力
3. ブロック追加 → 「カスタム HTML」ブロックを 1 つ挿入
4. AI 生成 HTML の `<body>` 内側 (= `<header>` から `</footer>` まで、`<html>/<head>/<body>` タグ自体は含めない) を貼り付け
5. **公開前にプレビュー**: 親テーマの header/footer が前後に出るので、デザイン的に許容できるか確認
6. 公開 → URL を田中さんに共有

> 所要 15 分。子テーマ無しでもこの手順だけで「載せる」は実現可能。
> 親テーマの header/footer がデザイン上 NG な場合は Phase B に進む。

### 2.2 Phase B — 採択 (B) Custom Page Template で「ドカン感」を出す

1. 付録 A〜D のファイルをローカルで `coredriven-child/` フォルダにまとめる
2. `coredriven-child/` を **ZIP 圧縮** (Mac なら右クリック → 「圧縮」)
3. WP 管理画面 → 「外観 → テーマ → 新規追加 → テーマのアップロード」で ZIP をアップ → 「今すぐインストール」
4. 「外観 → テーマ」で `CoreDriven Child` を **有効化**
5. Phase A で作った固定ページを編集 → サイドバー「テンプレート」から **`AI Full HTML (CoreDriven)`** を選択 → 更新
6. プレビューで「親テーマの header/footer がそのまま出るが、本文 1 ブロックが丸ごと AI 製 HTML」になっていれば成功
7. ヘッダー/フッターも消したい場合は、テンプレートを **`AI Full HTML — Bare`** に切り替え

### 2.3 Phase C — 静的アセット (画像/CSS/JS) の運用

AI 生成 HTML が画像・CSS・JS を参照している場合の置き場所:

- **推奨**: `wp-content/uploads/coredriven-fullhtml/` に画像・CSS・JS をまとめてアップ
- HTML 内のパスを `/wp-content/uploads/coredriven-fullhtml/...` に書き換え
- 自動化したい場合は WP-CLI で `wp media import ./assets/* --regenerate-thumbnails` (要 SSH or LocalByFlywheel)
- CDN を使うなら絶対 URL のままで OK (ただし CSP / mixed content に注意)

### 2.4 Phase D — 更新フロー (週次想定)

1. AI が新しい HTML を `Flow/<today>/0.Other/CoreDriven/coredriven_top_v<n>.html` に出力
2. 田中さんが WP 管理画面でカスタム HTML ブロックの中身を**全選択 → 上書きペースト**
3. 「更新」をクリック → 即反映

→ 本フローは将来 `wp-cli` ベースのスクリプト化でゼロクリック化可能（BL-0079 残課題として後続）。

---

## 3. 動作検証チェックリスト (公開前)

- [ ] **モバイル表示**: iPhone 実機 or Chrome DevTools Responsive で iPhone 14 / Galaxy S22 サイズ確認
- [ ] **画像/CSS/JS のパス**: 全部 200 OK (DevTools Network タブで赤行ゼロ)
- [ ] **ヘッダー/フッター**: (B-1) なら親テーマのが出る / (B-2) なら一切出ない
- [ ] **OG/Twitter Card**: SEO プラグイン (Yoast/AIOSEO) が機能しているか (B-1) で確認
- [ ] **CSP/Mixed Content**: HTML 内 `<script>` の外部 src があれば CSP ヘッダで弾かれていないか確認
- [ ] **404/エラーページ**: テンプレート切替で 404 にならないか
- [ ] **編集者ロール**: 「カスタム HTML」ブロックは管理者のみ編集可。編集者ロールに権限を渡すかは方針確認 (§6 Q-D)
- [ ] **バックアップ**: 子テーマ ZIP / 既存テーマ設定 / 固定ページ DB を更新前に dump (UpdraftPlus 等)

---

## 4. ロールバック手順 (もし壊れたら)

| 症状 | 対応 |
|---|---|
| テンプレート切替後に画面が真っ白 | FTP で `wp-content/themes/coredriven-child/template-fullhtml.php` を一時退避 → 親テーマに戻す → エラーログ (`wp-content/debug.log`) 確認 |
| 子テーマ有効化後に管理画面に入れない | FTP で `wp-content/themes/coredriven-child/` をリネーム → WP が親テーマに自動 fallback |
| 固定ページが 404 | パーマリンク再保存 (「設定 → パーマリンク → 変更を保存」のみ。値変更不要) |
| カスタム HTML ブロックが消えた | リビジョン履歴から復元 (固定ページ右サイドバー「リビジョン」) |

---

## 5. セキュリティ注意点 (再掲 + 補足)

- **「カスタム HTML」ブロックは管理者のみ編集可**: WP の KSES filter は管理者を除外する (`unfiltered_html` 権限)。編集者・寄稿者には触らせない方針が原則。
- **AI 出力の `<script>` 監査**: 外部 src を含む場合は社内ホスト or 信頼ドメインのみに制限。XSS と CSP 両方で守る。
- **CSP ヘッダ**: 推奨は `Content-Security-Policy: default-src 'self'; script-src 'self' https://www.googletagmanager.com https://www.google-analytics.com; img-src 'self' data: https:;` をベースに調整。プラグインなら `Content Security Policy Pro` / Cloudflare Transform Rules / Apache `.htaccess` のいずれか。
- **管理者アカウントの 2FA**: 「カスタム HTML」を編集する管理者は必ず 2FA 必須 (`Wordfence` / `WP 2FA` 等)。

---

## 6. 田中さんへの確認事項 (実装前に解消したい)

| ID | 質問 | なぜ必要 | 暫定値 (確認後 update) |
|---|---|---|---|
| **Q-A** | 親テーマ名は何か (StudioPress / Cocoon / Astra / GeneratePress / 独自テーマ等) | 子テーマの `style.css: Template:` 行と `functions.php` の親 enqueue handle 名を確定するため | `twentytwentyfour` 仮置き |
| **Q-B** | WP 管理画面 / FTP / wp-content アクセス権限は誰が持っているか (田中さん本人 / 制作会社 / 社内エンジニア) | 子テーマ ZIP のアップロード経路と作業担当を確定するため | 田中さん本人 仮置き |
| **Q-C** | AI 生成済 HTML の最新版はどこにあるか (リポジトリ / ローカル / Notion 等) | 実装キットに同梱して引き渡せるようにするため | 別途共有 仮置き |
| **Q-D** | カスタム HTML ブロックの編集権限を編集者ロールにも与えるか | セキュリティ方針 (XSS リスク許容範囲) を確定するため | 管理者のみ 仮置き (推奨) |
| **Q-E** | 既存 CoreDriven HP の URL 構造はどうなっているか (`/` ルートを置き換え or `/landing/` 等の新規 path) | 既存ページとの URL 衝突 / canonical 設定の扱いを確定するため | 新規 path `/v2/` 仮置き |
| **Q-F** | 更新頻度は週何回想定か / 自動化(`wp-cli` 経由のスクリプト)は今期スコープに入れるか | Phase D の優先度判断 | 月次 仮置き |

---

## 7. 残課題 / 次アクション

| 期限 | アクション | 担当 |
|---|---|---|
| 5/5 中 | 本キットを田中さんが review → §6 Q-A〜Q-F に回答 | 田中さん |
| 5/5〜5/6 | Q-A 回答後、子テーマ `style.css: Template:` 行を確定 → 確定版 ZIP を生成 | AI |
| 5/6〜5/7 | Phase A (暫定 Custom HTML) で 1 ページ公開 → 動作確認 | 田中さん (or WP 管理担当) |
| 5/8〜5/12 | Phase B (Custom Page Template) に移行 → アセット整理 | AI ＋ WP 管理担当 |
| 後続 | wp-cli ベースの「AI 生成 → 自動反映」スクリプト化 (Phase D) | AI (Q-F が GO の場合) |

---

## 付録 A. `style.css` (子テーマ宣言)

```css
/*
Theme Name:   CoreDriven Child
Theme URI:    https://coredriven.jp/
Description:  CoreDriven 子テーマ — AI 生成 HTML を 1 ページ丸ごと表示するための Custom Page Template を提供
Author:       CoreDriven (RestaurantAILab)
Author URI:   https://coredriven.jp/
Template:     twentytwentyfour     /* ← TODO: §6 Q-A で確定後、親テーマの実フォルダ名に差し替え */
Version:      0.1.0
Text Domain:  coredriven-child
*/

/* 親テーマ style.css は functions.php で wp_enqueue_style 経由で読み込む (推奨方式) */

/* AI Full HTML テンプレート用の最小限の reset
   親テーマの margin / padding と AI 生成 HTML が衝突する場合に備える */
.page-template-template-fullhtml .site-main,
.page-template-template-fullhtml-bare .site-main {
    max-width: none;
    padding: 0;
    margin: 0;
}
```

## 付録 B. `functions.php` (親テーマ style 読込)

```php
<?php
/**
 * CoreDriven Child — functions.php
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * 親テーマ + 子テーマの style.css を読み込む。
 * 親テーマの handle は親テーマの functions.php を読んで合わせる。
 * 一般的な命名: 'parent-style' or '<themename>-style'。Twenty Twenty-Four なら 'twentytwentyfour-style'。
 * §6 Q-A 確定後に適切な handle 名に差し替えること。
 */
add_action( 'wp_enqueue_scripts', function () {
    // 親テーマ
    wp_enqueue_style(
        'coredriven-parent-style',
        get_template_directory_uri() . '/style.css',
        [],
        wp_get_theme( get_template() )->get( 'Version' )
    );
    // 子テーマ (親に依存)
    wp_enqueue_style(
        'coredriven-child-style',
        get_stylesheet_uri(),
        [ 'coredriven-parent-style' ],
        wp_get_theme()->get( 'Version' )
    );
}, 20 );

/**
 * Custom Page Template が固定ページサイドバーに必ず出るよう保険
 * (テーマによっては Page Template スキャンが効かないケースがあるため明示登録)
 */
add_filter( 'theme_page_templates', function ( $templates ) {
    $templates['template-fullhtml.php']      = 'AI Full HTML (CoreDriven)';
    $templates['template-fullhtml-bare.php'] = 'AI Full HTML — Bare (CoreDriven)';
    return $templates;
} );
```

## 付録 C. `template-fullhtml.php` (B-1: header/footer 残す版)

```php
<?php
/**
 * Template Name: AI Full HTML (CoreDriven)
 * Description: AI 生成済の 1 ページ HTML を本文として丸ごと流し込むテンプレート。
 *              親テーマの header/footer は維持されるため、SEO プラグイン (Yoast/AIOSEO) も機能する。
 *
 * @package coredriven-child
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

get_header();
?>

<main id="primary" class="site-main page-template-template-fullhtml">
    <?php
    if ( have_posts() ) :
        while ( have_posts() ) :
            the_post();
            // do_blocks() を通すことでカスタム HTML ブロックが正しく描画される
            echo apply_filters( 'the_content', get_the_content() );
        endwhile;
    endif;
    ?>
</main>

<?php
get_footer();
```

## 付録 D. `template-fullhtml-bare.php` (B-2: wp_head/wp_footer も出さない版)

```php
<?php
/**
 * Template Name: AI Full HTML — Bare (CoreDriven)
 * Description: 親テーマの header/footer / wp_head / wp_footer を一切出さず、
 *              AI 生成 HTML を <html><head>...</head><body>...</body></html> 丸ごと出力するテンプレート。
 *              SEO プラグインも効かないので meta タグは AI 生成 HTML 側に必要。
 *
 * @package coredriven-child
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

the_post();
nocache_headers();

// the_content() を通さず raw に出すことで wpautop の <p> 自動挿入も避ける
$raw_html = get_the_content();

// ショートコードは展開したいので do_shortcode は通す (要らなければ外す)
echo do_shortcode( $raw_html );

// 以降何も出力しない (wp_footer も呼ばない) ため exit
exit;
```

> **注**: bare 版を使う場合、AI 生成 HTML 側に `<!DOCTYPE html><html><head>...meta/og/title...</head><body>...content...</body></html>` を完全に書いておくこと。テンプレート側は WP の出力を一切挟まない。

---

## 付録 E. 子テーマ ZIP の作り方 (Mac)

```bash
# 1. 作業ディレクトリで子テーマフォルダを作る
mkdir -p coredriven-child
cd coredriven-child

# 2. 付録 A〜D の中身をそれぞれ style.css / functions.php / template-fullhtml.php / template-fullhtml-bare.php に保存
#    (本ドキュメントから手でコピペ)

# 3. ZIP 化 (親フォルダで)
cd ..
zip -r coredriven-child.zip coredriven-child

# 4. coredriven-child.zip を「外観 → テーマ → 新規追加 → テーマのアップロード」でアップ
```

> WP-CLI が使える環境なら下記でも可:
> ```bash
> wp theme install ./coredriven-child.zip --activate --allow-root
> ```

---

## 付録 F. AI 側オペレーション (将来の Phase D)

`wp-cli` ベースで「AI 生成 → 自動反映」を実装する場合の擬似コード:

```bash
# 1. AI が新しい HTML を生成
node generate_html.mjs > coredriven_top_$(date +%Y%m%d).html

# 2. 既存固定ページの post_content をまるごと上書き
PAGE_ID=42  # 「CoreDriven Top (HTML版)」の固定ページ ID
wp post update $PAGE_ID --post_content="$(cat coredriven_top_$(date +%Y%m%d).html)"

# 3. キャッシュ purge (Cloudflare/W3 Total Cache 等)
wp cache flush
```

→ この自動化を進めるかは §6 Q-F の回答次第。

---

## 8. 参考リンク (再掲)

- WP Theme Handbook → Page Templates: https://developer.wordpress.org/themes/template-files-section/page-template-files/
- WP Theme Handbook → Child Themes: https://developer.wordpress.org/themes/advanced-topics/child-themes/
- WP-CLI Handbook → wp post / wp theme / wp media: https://developer.wordpress.org/cli/commands/
- Gutenberg Custom HTML block: https://wordpress.org/documentation/article/blocks/

---

**END OF KIT.** §6 (田中さんへの確認事項) の Q-A〜Q-F が埋まった時点で、親テーマ名と運用方針を反映した「最終 ZIP」を AI が生成 → そのまま WP にアップロードできる状態にする。
