# BL-0079 — 調査レポート: AI 生成済 1 ページ HTML を WordPress に丸ごと載せる仕組み

**作成日**: 2026-05-03
**作成者**: AI (mt cockpit-task-f2830076)
**ステータス**: Draft（田中さん review 待ち）
**関連 BL**: BL-0079 (CoreDriven HP WordPress更新)

---

## 0. 田中さんの問い

> CoreDriven のホームページを AI で 1 ページ丸ごと HTML 化済。今後も WordPress 上に載せていきたい。
> WordPress はパーツごとに追加していく仕様だが、**1 ページまるごと HTML で作ったページをドカンと表示**したい。
> このようなことをするための仕組みがあるかどうかを調べて教えてほしい。

結論: **3 つの実用パターンがあり、用途次第で選び分けられる**。CoreDriven 用には **「(B) Custom Page Template でテーマに HTML を吸収」** が最適、運用簡素化重視なら **「(A) ページ＝Custom HTML 1ブロックだけ」** で当面回せる。

---

## 1. パターン比較 (1 ページ HTML を WP に載せる 5 手段)

| # | 手段 | 仕組み | 良いところ | 注意点 | おすすめ用途 |
|---|---|---|---|---|---|
| **A** | **Custom HTML ブロック (Gutenberg)** | 固定ページに「カスタム HTML」ブロックを1つ追加し、そこに 1 ページ全 HTML を貼る (`<head>` を除いた `<body>` 中身相当) | 管理画面だけで完結 / プラグイン不要 / 編集者が直す時もそのブロックだけ触れば OK | テーマの header/footer/sidebar が自動で入る → 「ドカン感」が出ない場合あり。`<head>` の meta/OG はテーマ管理 | 既存テーマを残したまま、本文だけ AI 製 HTML を入れたい時 |
| **B** | **Custom Page Template (テーマ拡張)** | 子テーマに `template-fullhtml.php` を作り `Template Name: AI Full HTML` を宣言 → 固定ページ作成時に「テンプレート」で選択。テンプレ側は `<?php echo do_blocks(get_the_content()); ?>` だけで済むし、WP の header/footer すら出力しないようにも書ける | テーマの header/footer を**完全にバイパスできる** = 本当の意味で「丸ごと HTML」/ メニュー・ウィジェット・スクリプトとも切り離せる / WP 管理画面でページとして残るので URL・公開設定・SEO プラグインも効く | 子テーマが必要 (簡単な PHP 1 ファイル) / FTP かファイルマネージャ要 | **コアドリブンの推奨案**。AI 製 HTML を「ページの中身全部」として扱える |
| **C** | **Headless / 静的 HTML をテーマ外に直置き** | `wp-content/uploads/landing/index.html` 等にアップして `.htaccess` rewrite、または `/landing/` の Apache Alias で配信 | WP を完全にバイパス → 1 ms でも軽い / WP のレンダリング無効化で衝突なし | WP 管理画面から編集できなくなる (ファイル差し替え運用) / 共存させる時の URL 設計が要注意 | LP やキャンペーンページ、A/B テスト用に丸ごと差し替えたい時 |
| **D** | **iframe 埋め込み** | 別ホスト (例: `landing.coredriven.jp` を Vercel/Netlify で公開) を用意し、WP ページに `<iframe src="...">` だけ書く | デプロイ独立 / 静的ホスティングの恩恵 (CDN 即時) | iframe 高さ計算・SEO 不利・モバイル時のスクロール問題・ハッシュリンク不通 | 他社ホスティングの完成品を WP 内に表示するだけしたい時 |
| **E** | **「Custom HTML 全 1 ページ」プラグイン** | `Insert Headers and Footers` / `Custom HTML Page` 系の拡張プラグインで丸ごと HTML を 1 ページ化 | コーディングなし / 多くの場合 admin 完結 | プラグイン依存 (作者がメンテ停止すると詰む) / セキュリティリスク (HTML に script 含む際の権限) | 開発者を雇わずに継続運用したい時 |

---

## 2. 推奨案: (B) Custom Page Template

### 2.1 仕組み

1. **子テーマ作成** (1 回だけ): `wp-content/themes/coredriven-child/` を作り `style.css` + `functions.php` + `template-fullhtml.php` を置く
2. **Page Template 作成**: `template-fullhtml.php` の冒頭に下記を書く

```php
<?php
/**
 * Template Name: AI Full HTML (CoreDriven)
 * Description: AI 製の 1 ページ完結 HTML をそのまま流し込むテンプレ
 */
the_post();
echo apply_filters( 'the_content', get_the_content() );
```

`<head>` を含めて完全に AI 製 HTML を出したいときは下記:

```php
<?php
/**
 * Template Name: AI Full HTML — Bare
 */
the_post();
remove_action( 'wp_head', 'wp_print_styles', 8 );
remove_action( 'wp_head', 'wp_print_head_scripts', 9 );
nocache_headers();
echo apply_filters( 'the_content', get_the_content() );
exit; // header/footer を出さない
```

3. **WP 管理画面**: 「ページ → 新規追加」→ サイドバー「テンプレート」で `AI Full HTML (CoreDriven)` を選択 → 本文に「カスタム HTML」ブロックを 1 つ置いて貼る → 公開
4. **更新フロー**: AI が新しい HTML を生成したら、編集画面でカスタム HTML ブロックの中身を上書き → 更新
5. **元テーマ更新時の安全性**: 子テーマなので親テーマがアップデートされても上書きされない

### 2.2 静的アセット (画像・CSS・JS) の置き方

- AI 製 HTML が外部 CDN/相対パスを参照している場合、`wp-content/uploads/coredriven-fullhtml/` に**全アセットをまとめて upload** → HTML 内のパスを `/wp-content/uploads/coredriven-fullhtml/...` に書き換え
- 自動化したいなら 1 度だけプラグイン `Real Media Library` 等で「フォルダ単位アップロード」を有効化、もしくは WP-CLI: `wp media import path/* --regenerate-thumbnails`

### 2.3 SEO / OG / favicon

- (B) で `the_content` だけ流す方式なら、`wp_head()` が走るので Yoast SEO / All in One SEO が機能する
- (B-bare) で wp_head を出さない方式は、AI 製 HTML 側に直接 meta タグを書く (それが「丸ごと」感の本懐)

### 2.4 セキュリティ注意点

- 「カスタム HTML」ブロックは **管理者ロール**のみ編集可（KSES filter で escape されない）
- AI 製 HTML 内に `<script>` がある場合は信頼できる出力であることを確認（XSS リスクは AI 出力の品質次第）
- script で外部ドメインを叩く場合は CSP ヘッダ要検討 (CoreDriven 側プラグイン `Content Security Policy Pro` 等)

---

## 3. 当面の運用 (今日できる暫定対応)

田中さんが「今すぐ管理画面から載せたい」場合:

1. WP 管理 → 「ページ → 新規追加」
2. 本文エリアにブロック追加 → 「**カスタム HTML**」を選択
3. AI 製 HTML の `<body>` の中身 (= header/footer 抜きの本体部分) を貼る
4. プレビューで確認 → 公開

これは (A) パターン。テーマの header/footer は出るが、**今日中に動かせる**。
明日以降、(B) Custom Page Template に移行して「ドカン感」を出す、という二段構えが現実的。

---

## 4. 参考: WordPress 公式・主要ドキュメント

| 機能 | 公式リンク (要約) |
|---|---|
| Page Templates (子テーマ) | `Theme Handbook → Template Files → Page Templates` (Template Name コメントヘッダで認識) |
| Custom HTML block | Gutenberg 標準ブロック (Editor Handbook) |
| 子テーマ作成 | `Theme Handbook → Child Themes` (`@import` ではなく `wp_enqueue_style` 推奨) |
| Headless WordPress | WP REST API / GraphQL / Decoupled. CoreDriven の現状規模では過剰 |

---

## 5. 田中さんへの確認事項

- [ ] **方針合意**: (B) Custom Page Template を最終形 / (A) Custom HTML を当面の暫定 で OK か?
- [ ] **管理権限**: WP 管理画面 / FTP / wp-content アクセスは誰が持ってる? (子テーマ作成のため必要)
- [ ] **テーマ**: 現在の親テーマは何 (StudioPress / Cocoon / Astra / カスタムなど)? 子テーマ作成のひな型を合わせる
- [ ] **アセット運用**: AI 製 HTML 内の画像は WP メディアライブラリ管理 (Yoast 検索対象) と外部 CDN どちらが良い?
- [ ] **更新頻度**: AI が HTML を生成 → WP に貼り替え、を週何回くらい想定? 自動化したいか (`wp-cli` 経由のスクリプト化) ?
- [ ] **既存ページ**: 既に CoreDriven HP にあるページとの URL 衝突は? (`/` ルートを丸ごと載せたいなら親テーマ側の調整必要)

---

## 6. 次アクション (推奨)

| 期限 | アクション | 担当 |
|---|---|---|
| 5/3 中 | (A) Custom HTML ブロックでまず暫定公開を試す | 田中さん |
| 5/4-5/5 | 親テーマ調査 → 子テーマひな型作成 | AI (情報受領後) |
| 5/5-5/7 | (B) Page Template 適用 → アセット整理 | AI ＋ 田中さん |
| 継続 | AI 生成 → WP 反映フローのスクリプト化 (`wp-cli` ベース) | AI |
