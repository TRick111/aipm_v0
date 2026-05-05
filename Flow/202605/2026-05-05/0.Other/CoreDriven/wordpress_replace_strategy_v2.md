# BL-0079 v2 — WordPress→AI 製 HTML 置換戦略レポート (CoreDriven 実調査 + 一般論)

**作成日**: 2026-05-05
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft（田中さん review 待ち）
**関連 BL**: BL-0079 (CoreDriven HP WordPress 更新)
**先行成果物**:
- `Flow/202605/2026-05-03/0.Other/CoreDriven/wordpress_full_html_mechanism.md` (5/3 v1 調査)
- `Flow/202605/2026-05-05/0.Other/CoreDriven/wordpress_implementation_kit.md` (5/5 実装キット)

---

## 0. このレポートの位置づけ

田中さんからの追加スコープ:

> 一般に WordPress で作成されているホームページを今後 HTML でリプレイスしようとした時に、どういう手段があるかを知りたい。完全 HTML デプロイではなく **ヘッダーは WP のまま残すなどハイブリッドアプローチも検討したい**。

→ 本 v2 レポートは下記 2 軸で再整理:
- **(横軸) 実装手間**: コード 0 行 → 子テーマ 1 ファイル → リバースプロキシ → 完全ヘッドレス
- **(縦軸) 置換範囲**: ページ本文だけ / 個別ページ全体 / サイト全体

---

## 1. core-driven.com の WP 構成スナップショット (実調査結果)

| 項目 | 値 | 抽出根拠 |
|---|---|---|
| **親テーマ** | **SWELL v2.12.0** | `wp-content/themes/swell/build/css/main.css?ver=2.12.0` |
| **子テーマ (既存)** | **swell_child** ✅ | `wp-content/themes/swell_child` パスを HTML 内で確認 |
| **SEO** | SEO SIMPLE PACK 3.6.2 | `<!-- SEO SIMPLE PACK 3.6.2 -->` コメント |
| **ホスティング** | **Xserver** (nginx 前段) | `webfonts.xserver.jp` 参照 + `Server: nginx` ヘッダ |
| **ページビルダー** | Gutenberg + **SWELL ブロック** (Elementor 不在) | `swell-blocks-css` あり、`elementor` クラス無し |
| **言語** | ja_JP | `<html lang="ja">` |
| **メニュー** | TOP / Business (AI Lab / Career Lab / 事業開発支援) / Company / News / Contact | サイトナビ実物 |
| **お問い合わせ** | Google Form (`forms.gle/GbRSdeKqWngAqx4WA`) | フォームリンク |
| **追加プラグイン痕跡** | `lazysizes.min.js` (画像遅延) | `wp-content/plugins/*/lazysizes.min.js` |
| **メインカラー** | white bg / black text / cyan gradient (#d8ffff→#87e7ff) | SWELL CSS 変数 `--color_main` 等 |
| **MV (ヒーロー)** | フルスクリーン (PC 50vw / SP 80vh) スライダー | `.p-mainVisual__inner` |

→ Q-A (親テーマ名) は **SWELL v2.12.0** で確定。
→ Q-B (子テーマ作成要否) は **既に swell_child が存在するので作成不要**。PHP ファイル追加だけで Custom Page Template が成立。

**重要発見**: Q.6 確認事項 6 件のうち **Q-A は調査により確定**、**Q-B の前提も大幅簡素化** (子テーマ既設なので「ZIP アップロード」不要、FTP / wp-admin で `/wp-content/themes/swell_child/` にファイル追加のみ)。

---

## 2. WP→HTML 置換アプローチの Tier 体系 (一般論)

「WordPress でできているサイトを AI 生成 HTML で置き換える」を、**置換範囲 × 実装手間** の 2 軸で 6 つの Tier に整理。

### Tier 1 — WP 管理画面のみで完結 (コードゼロ)

| 手段 | 仕組み | 置換範囲 | 適用ケース |
|---|---|---|---|
| **1A. カスタム HTML ブロック** | 固定ページに「カスタム HTML」ブロックを 1 つ置いて HTML を貼る | 本文のみ (header/footer/sidebar は親テーマのまま) | 即日公開、編集者が WP 管理画面で更新できる |
| **1B. 再利用ブロック (パターン)** | カスタム HTML ブロックを「再利用ブロック」化、複数ページで参照 | 本文の一部 (再利用パーツ) | LP のセクション単位で AI HTML を流用 |
| **1C. ヘッダー/フッターカスタム HTML プラグイン** | `Insert Headers and Footers` 等で `<head>` / `</body>` 直前に HTML 注入 | 計測タグ・カスタム JS のみ | GTM / カスタム CSS / OGP 上書き |

### Tier 2 — 子テーマで PHP 1 ファイル

| 手段 | 仕組み | 置換範囲 | 適用ケース |
|---|---|---|---|
| **2A. Custom Page Template (ハイブリッド型)** | 子テーマに `page-fullhtml.php` を置き `get_header()` + 本文 + `get_footer()` を出す | **個別ページ単位、ヘッダー/フッターは WP のまま** | **CoreDriven の主案**。「丸ごと HTML だけど WP のグロナビは残す」を実現 |
| **2B. Custom Page Template Bare 型** | 上記の `get_header()/get_footer()` を呼ばず HTML 全部出力 | 個別ページ全体 (WP の出力ゼロ) | LP・キャンペーンページで全画面型レイアウトを優先 |
| **2C. ショートコード化** | `[ai_html slug="hero"]` を AI HTML に展開する関数を `functions.php` に登録 | 本文の一部 | エディタ画面のショートコード 1 行で部品差し込み |

### Tier 3 — 動的 HTML 切替

| 手段 | 仕組み | 置換範囲 | 適用ケース |
|---|---|---|---|
| **3A. the_content フィルタ** | `add_filter('the_content', fn($c) => 特定ページなら ai_html_load($id) を返す)` | 本文だけだが、エディタ無視で強制差し替え | 本文を WP DB に書きたくない (Git 管理派) |
| **3B. 個別テンプレ `page-{slug}.php`** | 子テーマに `page-corporate.php` を置く → スラッグ `corporate` の固定ページ専用テンプレ | 個別ページ全体 | ハードコード型 LP、頻繁な更新無し |
| **3C. ACF / カスタムフィールド** | 「AI HTML」テキストフィールドを固定ページに追加 → テンプレが echo | 本文 | 編集者は「HTML 入力欄」だけ触る運用 |

### Tier 4 — 部分置換 / Islands アプローチ

| 手段 | 仕組み | 置換範囲 | 適用ケース |
|---|---|---|---|
| **4A. iframe 埋め込み** | `<iframe src="https://landing.example.jp/v2">` を WP ページに置く | iframe 領域のみ | 別ホスティングの完成品をそのまま見せる |
| **4B. Server-side include / Edge include** | `<!--#include virtual="/static/landing.html"-->` (Apache SSI) または Cloudflare Workers の `HTMLRewriter` | 任意の領域 | サーバ側で AI HTML をはめ込む、SEO は OK |
| **4C. JavaScript Islands** | WP テンプレに `<div id="ai-app"></div>` + 別 build した React/Vue/Svelte を mount | div の中だけ動的化 | 部分的に高度な UI を入れたい (検索・予約等) |

### Tier 5 — 静的化 / リバースプロキシ

| 手段 | 仕組み | 置換範囲 | 適用ケース |
|---|---|---|---|
| **5A. Static HTML Export** | WP を一度 `Simply Static` 等で全ページ静的 HTML に書き出し → 必要なページだけ AI HTML に差し替え → CDN 配信 | サイト全体 | パフォーマンス最大化 + 編集は WP のまま |
| **5B. Reverse Proxy (path 別 origin)** | nginx / Cloudflare で `/landing/*` だけ別 origin (Vercel/Netlify) に振る、それ以外は WP | path 別 (例: ランディングだけ) | WP は wp-admin / News に残し、LP だけ高速化 |
| **5C. Cloudflare Workers / Vercel Edge** | リクエスト URL ベースで origin 切替、 A/B テストも可 | path 別 + 動的判定 | 段階的移行 / カナリーリリース |

### Tier 6 — 完全ヘッドレス

| 手段 | 仕組み | 置換範囲 | 適用ケース |
|---|---|---|---|
| **6A. Astro / Next.js (SSG/SSR)** | WP を CMS に降格、フロントは Astro/Next.js で WP REST API or WPGraphQL から記事を取得 | サイト全体 (フロント別) | WP は記事入力 UI として最強、フロントは爆速 |
| **6B. Astro Islands ハイブリッド** | Astro でほぼ静的に、検索やフォームだけ React/Vue で hydrate | サイト全体 + 部分的に動的 | ヘッドレスのいいとこ取り |
| **6C. WP Admin だけ残し別 stack で書き直し** | wp-admin の URL は維持、フロントは完全に別 (別ドメインも可) | サイト全体 | 移行期に WP 入力に慣れた編集者を残す |

---

## 3. CoreDriven 向け推奨ルート (3 段階)

調査で確定した SWELL + swell_child 構成を踏まえた具体ロードマップ。

### Phase 0 — 即日 (本日 5/5)
**Tier 1A**: 暫定で固定ページに「カスタム HTML」ブロックを置いて AI HTML 本文を貼る。
- 所要 15 分 / コードゼロ / SWELL のヘッダー・フッター・グロナビは全部維持
- リスク: SWELL の本文 `padding` / `max-width: 1920px` が AI HTML と衝突する可能性 → スタイル衝突箇所をデベロッパーツールで特定 → §6.2 の `.swell-block-fullWide__inner` でフルワイド化

### Phase 1 — 今週 (5/6〜5/10)
**Tier 2A**: SWELL 子テーマ (既存 `swell_child`) に `page-fullhtml.php` を追加、固定ページから「AI Full HTML (CoreDriven)」テンプレを選択。
- ファイル追加先: `/wp-content/themes/swell_child/page-fullhtml.php` のみ (1 ファイル)
- ZIP アップロード不要 (子テーマ既存)
- ヘッダー/フッターは SWELL のまま、本文だけが AI HTML 全幅表示

### Phase 2 — 中期 (5/12〜5/30)
**Tier 4C (Islands)**: AI HTML 内で動的な部分 (お問い合わせフォーム / 求人検索等) だけを `<div id="ai-island-form"></div>` で残し、後から JavaScript で差し込み。
- AI HTML はほぼ静的 / 動的部分だけが Island

### Phase 3 — 長期 (Q3〜Q4 検討)
**Tier 5B or 6B**: トラフィック増・編集者増・パフォーマンス要求が高まったら、Cloudflare Workers でルート別 origin 振り分け、または Astro へ段階移行。

---

## 4. 各 Tier の判断マトリクス

| 観点 | Tier 1A | Tier 2A | Tier 2B | Tier 4A (iframe) | Tier 5B (Proxy) | Tier 6A (Astro) |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 実装時間 | 15 分 | 30 分 | 30 分 | 5 分 | 1 日 | 1〜4 週 |
| 必要スキル | WP 管理画面のみ | PHP 1 ファイル | PHP 1 ファイル | iframe タグ | nginx/CF 設定 | Astro/Next.js |
| WP のヘッダー残せる | ✅ | ✅ | ❌ | ❌ | △(設定次第) | ❌(自作) |
| SEO (Yoast 等の効力) | ✅ | ✅ | ❌ (HTML 側で書く) | △ (iframe SEO 不利) | △ (path 別) | ❌ (自作) |
| 編集者が WP 管理で更新 | ✅ | ✅ | ✅ | △ (別 stack 編集) | △ | △ (WP 入力可) |
| 本文 padding/max-width 衝突 | ⚠️ | ⚠️ (要対応) | なし | なし | なし | なし |
| 親テーマ更新で壊れる | なし | なし (子テーマ) | なし (子テーマ) | なし | なし | なし |
| パフォーマンス | △ (WP まま) | △ (WP まま) | ○ (header/footer 出さない) | ○ (CDN) | ◎ (path 別最適化) | ◎ (静的) |
| 段階的移行 | ✅ | ✅ | ✅ | ✅ | ✅ | △ (一気に必要) |

→ **CoreDriven の Phase 1 確定推奨は Tier 2A** (PHP 1 ファイル / SWELL header/footer 残す / SEO 維持 / 編集者 WP 更新)

---

## 5. 一般論: WP→HTML 置換の 7 原則

複数案件で共通する経験則:

1. **「全部 HTML 化」は最後の選択肢**: WP の wp-admin / 投稿 UI / SEO プラグインの蓄積を捨てるコストが大きい。最初は「本文だけ HTML」から始める。
2. **子テーマは "1 度だけ" 作って永続使う**: 親テーマ更新で吹き飛ばないので、置換テンプレは全部子テーマに置く。
3. **`page-{slug}.php` テンプレ階層を活用**: スラッグ別に専用テンプレを用意できるので、「個別の LP は専用 HTML 置換、ブログは普通の WP 表示」が無料で両立。
4. **SEO は WP のまま吸わせる**: Yoast / SEO SIMPLE PACK / AIOSEO は WP の `wp_head()` フックに乗っているので、`get_header()` を呼ぶ実装にすれば自動で効く (Tier 2A の利点)。
5. **アセット (画像/CSS/JS) は `wp-content/uploads/` 集約が無難**: WP のメディアライブラリで一元管理 → 削除・差替が容易。CDN は WP プラグイン (W3 Total Cache / WP Rocket) で自動化。
6. **CSP (Content Security Policy) を意識**: AI HTML 内に外部 `<script src>` がある場合、WP 側 CSP ヘッダで弾かれることがある。Cloudflare Transform Rules / `.htaccess` で許可リスト管理。
7. **「カスタム HTML」ブロックは管理者ロール限定**: KSES filter が無効化されるので XSS リスク。編集者ロールに開放するなら `Allow Editors to Edit Custom HTML` 系プラグイン or ロール権限カスタマイズ。

---

## 6. SWELL 固有の実装コード (CoreDriven 専用)

### 6.1 既存 swell_child に追加するファイル

```
wp-content/themes/swell_child/
├─ style.css          ← 既存 (触らない)
├─ functions.php      ← 既存 (触らない or 末尾に Page Template 登録 add_filter を追記)
└─ page-fullhtml.php  ← ★ 新規追加
```

### 6.2 `page-fullhtml.php` (CoreDriven 用 / SWELL ハイブリッド型)

```php
<?php
/**
 * Template Name: AI Full HTML (CoreDriven)
 * Description: AI 生成 1 ページ HTML を全幅で本文に流すテンプレ。SWELL のヘッダー/フッター/グロナビは維持。
 *
 * @package swell_child
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

get_header();
?>

<main id="main_content" class="l-mainContent ai-fullhtml-main">
    <?php
    if ( have_posts() ) :
        while ( have_posts() ) :
            the_post();
            // do_blocks() を通すことで「カスタム HTML」ブロックが正しく描画される
            echo apply_filters( 'the_content', get_the_content() );
        endwhile;
    endif;
    ?>
</main>

<?php
get_footer();
```

### 6.3 SWELL 由来のスタイル衝突を消す追加 CSS (子テーマ style.css 末尾)

```css
/* AI Full HTML テンプレで本文の左右余白 / max-width を解除 */
.page-template-page-fullhtml main.ai-fullhtml-main {
    max-width: none !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

/* SWELL の article 内 padding を AI HTML だけ無効化 */
.page-template-page-fullhtml .post_content,
.page-template-page-fullhtml article {
    padding: 0 !important;
    max-width: none !important;
}

/* サイドバーが出ないよう保険 (CoreDriven の固定ページは元々 sidebar-off の想定) */
.page-template-page-fullhtml #sidebar { display: none !important; }
```

### 6.4 functions.php 末尾に追記 (任意・テンプレ表示の保険)

```php
/**
 * Custom Page Template が固定ページサイドバーに必ず出るよう明示登録
 * SWELL は標準で page-*.php を拾うが、念のため。
 */
add_filter( 'theme_page_templates', function ( $templates ) {
    $templates['page-fullhtml.php'] = 'AI Full HTML (CoreDriven)';
    return $templates;
} );
```

### 6.5 オペレーション手順 (FTP 想定)

1. SSH or FTP で Xserver にログイン (ファイルマネージャ機能でも可)
2. パス: `/home/<アカウント>/core-driven.com/public_html/wp-content/themes/swell_child/`
3. 上記 `page-fullhtml.php` を新規アップロード
4. 上記 `style.css` 末尾に CSS 追記 (既存の swell_child スタイルがあればそれを活かす)
5. WP 管理画面 → 「ページ → 新規追加」 (または既存ページ編集)
6. サイドバー「テンプレート」で **`AI Full HTML (CoreDriven)`** を選択
7. 本文に「カスタム HTML」ブロックを 1 つ追加 → AI HTML を貼り付け
8. プレビュー確認 → 公開

---

## 7. 一般論ベストプラクティス: 部分置換 (Islands) と段階移行

### 7.1 Islands ハイブリッドの推奨構成

```
┌─────────────────────────────────────┐
│  WordPress Header (SWELL)           │  ← WP のまま (グロナビ・ロゴ・SP メニュー)
├─────────────────────────────────────┤
│  AI HTML 本文 (静的)                 │  ← 90% は AI 生成 HTML
│   ├─ Hero                            │
│   ├─ 事業紹介                         │
│   └─ 会社情報                         │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Island: お問い合わせフォーム      │  ← React/Vue で hydrate
│  │  (Google Form 埋込 or 自前)      │     ここだけ動的
│  └──────────────────────────────┘  │
├─────────────────────────────────────┤
│  WordPress Footer (SWELL)           │  ← WP のまま (会社情報・SNS)
└─────────────────────────────────────┘
```

→ AI HTML のうち **動的にしたい部分だけ `<div id="ai-island-X"></div>`** で空けておき、別 build したミニ JS が WP 側で hydrate。
→ 完全ヘッドレス (Tier 6) より工数 1/10、Tier 2A より柔軟性高い。

### 7.2 リバースプロキシ (Tier 5B) の典型構成

Xserver 単独では nginx 設定変更が不可なので、CoreDriven 規模なら **Cloudflare 前段** が現実解:

```
[Cloudflare DNS]
    ↓
[Cloudflare Worker]
    ├─ /landing/*  → Vercel (AI HTML 完全配信)
    ├─ /news/*     → Xserver (WP のまま)
    └─ /*          → Xserver (WP のまま)
```

→ Worker 1 ファイルで実装可、ステージング検証も Cloudflare のプレビュー URL で可能。

### 7.3 段階移行の典型タイムライン (CoreDriven 想定)

| 時期 | 状態 | 工数 |
|---|---|---|
| Phase 0 (本日) | Tier 1A: 固定ページ 1 枚を AI HTML に差替 (暫定) | 15 分 |
| Phase 1 (今週) | Tier 2A: 子テーマに `page-fullhtml.php` 追加 → 主要 LP 5 ページ AI HTML 化 | 半日 |
| Phase 2 (来月) | Tier 4C: お問い合わせ・最新ニュース等の動的部分を Island 化 | 数日 |
| Phase 3 (Q3) | Tier 5B: Cloudflare Worker で /v2/ パスを別 origin (Vercel) に振る | 1〜2 日 |
| Phase 4 (Q4 以降) | Tier 6B: Astro Islands に完全移行 (旧 WP は CMS として残す or 廃止) | 2〜4 週 |

---

## 8. 落とし穴と対策

| 落とし穴 | 症状 | 対策 |
|---|---|---|
| 「カスタム HTML」が `<p>` で勝手に囲まれる | wpautop が走る | `remove_filter('the_content', 'wpautop')` をテンプレ内で実行、または`<!-- wp:html -->` ブロックに統一 |
| SWELL の `max-width: 1920px` で AI HTML が中央寄せに | フルワイド出ない | §6.3 の CSS で本文 main 要素の max-width を解除 |
| AI HTML 内の `<script>` が動かない | KSES filter で剥がれる | 管理者ロールで編集 + Custom HTML ブロック内なら通る (KSES 例外) |
| 画像パスが相対 `./images/foo.png` で 404 | WP のページ URL から相対解決される | アップロード先を `wp-content/uploads/coredriven-fullhtml/` に統一 → 絶対パスに書き換え |
| OGP / Twitter Card が出ない | bare 型テンプレで wp_head 出してない | bare 型は AI HTML 側に `<meta>` を直接書く / もしくは Tier 2A (header あり) を使う |
| 親テーマアップデートで壊れる | swell が更新で挙動変化 | 子テーマで `page-fullhtml.php` を持てば独立、影響なし |
| メニューの current-page が当たらない | カスタムテンプレでは `body_class` の `current_page_*` が消える可能性 | `nav_menu_link_attributes` フィルタで強制付与、または SWELL の標準で十分なら無視 |

---

## 9. 田中さんへの確認事項 (更新版)

5/5 の追加調査で **Q-A は確定**、**Q-B は前提変化** で再質問は不要。残課題のみ列挙:

| ID | 質問 | 確定/未定 |
|---|---|:-:|
| Q-A | 親テーマ名 | ✅ **SWELL v2.12.0** (調査確定) |
| Q-B | 子テーマ作成要否 | ✅ **既存 swell_child を使用** (新規作成不要) |
| Q-C | AI 生成 HTML の最新版の所在 (パス / リポジトリ / 別共有) | ❓ 未定 |
| Q-D | カスタム HTML ブロック編集権限 (管理者のみ / 編集者開放) | ❓ 未定 |
| Q-E | URL 構造 (`/` ルート差替 / 別 path 並走) | ❓ 未定 |
| Q-F | 更新頻度・自動化 (wp-cli) スコープ | ❓ 未定 |
| **Q-G (新規)** | **Phase 0 (即日 Tier 1A) で試す対象ページは? (TOP / Business / Company のいずれか)** | ❓ 未定 |
| **Q-H (新規)** | **Cloudflare はもう導入済か? (Phase 3 リバースプロキシの可否判断用)** | ❓ 未定 |

---

## 10. 結論 (TL;DR)

1. **CoreDriven は SWELL + swell_child + Xserver/nginx**。子テーマは既設なので、**`page-fullhtml.php` を 1 ファイル追加するだけ**で Tier 2A (ハイブリッド) が成立する。
2. **WP→AI HTML 置換は Tier 1〜6 の段階移行が定石**。完全ヘッドレス (Tier 6) は最後。CoreDriven は **Tier 1A → Tier 2A → Tier 4C → Tier 5B** の順で段階移行を推奨。
3. **「ヘッダー/フッターは WP のまま、本文だけ AI HTML」を実現するのは Tier 2A** (最小コードで最大効果)。SEO・編集者更新・段階移行が両立。
4. **一般論として、最初の 1 ページは Tier 1A (15 分) で試し、慣れたら Tier 2A に格上げ**するのが安全。最初から Tier 6 (Astro 等) は工数過大。
5. CoreDriven 用の **`page-fullhtml.php` 完全コードは §6.2 に同梱** (そのまま swell_child に追加可)。

---

## 11. 参考リンク

### SWELL 関連
- [SWELL 公式](https://swell-theme.com/)
- [SWELL の固定ページにカスタムテンプレートを追加する方法](https://best-item.work/wordpress/swell-custom-template/)
- [SWELL テーマファイル技術構成一覧 (WAZA)](https://motoki-design.co.jp/wordpress/swell-theme-structure/)
- [SWELL で子テーマは必要？ (DesignAmus)](https://d-amus.com/web/whole/21/)

### WordPress ハイブリッドテーマ・FSE
- [WordPress Hybrid Themes (Kinsta)](https://kinsta.com/blog/hybrid-themes/)
- [Bridging the gap: Hybrid themes (developer.wordpress.org)](https://developer.wordpress.org/news/2024/12/bridging-the-gap-hybrid-themes/)
- [WordPress FSE Complete 2026 Guide (AttoWP)](https://attowp.com/wordpress-development/wordpress-full-site-editing-guide/)
- [How to use PHP templates in block themes (Full Site Editing)](https://fullsiteediting.com/lessons/how-to-use-php-templates-in-block-themes/)

### リバースプロキシ・静的化
- [Reverse Proxy 完全ガイド (Kinsta)](https://kinsta.com/blog/reverse-proxy/)
- [WordPress Reverse Proxy 設定 (Stackademic)](https://stackademic.com/blog/how-to-set-up-a-reverse-proxy-for-wordpress)
- [Static Site Export Plugin (WordPress.org)](https://wordpress.org/plugins/export-wp-page-to-static-html/)

### ヘッドレス WordPress
- [Headless WordPress with Astro & Cloudflare Workers (2026)](https://konanspade.com/headless-wordpress-with-astro-cloudflare-workers-the-ultimate-seo-stack-for-2026/)
- [Migrate WordPress to Next.js (BrowserCat)](https://www.browsercat.com/post/migrate-wordpress-to-nextjs)
- [Headless WordPress Astro Journey (Outsourcify)](https://outsourcify.net/our-headless-wordpress-journey-with-astro-js-and-vue-js/)
- [Astro 公式: WordPress 移行ガイド](https://docs.astro.build/en/guides/migrate-to-astro/from-wordpress/)

---

**END OF v2 REPORT.** 田中さん review 待ち。Q-C〜Q-H が埋まれば Phase 0 を即日実装可能。
