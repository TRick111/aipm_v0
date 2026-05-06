# BL-0079 — CoreDriven HP 移行後 構成 設計書

**作成日**: 2026-05-06
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft

---

## 1. 設計方針

### 1.1 基本原則
1. **PHP 直書きを廃止**: コンテンツは PHP に直書きせず、WP の固定ページ (post_content) に格納する
2. **編集容易性を最優先**: 田中さんが WP 管理画面 (固定ページ編集 → カスタム HTML ブロック) で更新できる状態にする
3. **WP の機能を最大活用**: SEO プラグイン / メニュー / リビジョン / メディアライブラリ等は従来どおり利用
4. **段階的移行**: TOP → 残 4 ページ → クリーンアップ の Phase 制を取り、各 Phase でロールバック可能性を担保
5. **影響範囲最小化**: 既存ページ (`/news/` `/privacy-policy/` `/company/`) は触らない

### 1.2 採用しない方針 (検討した選択肢)
| 案 | 不採用理由 |
|---|---|
| (Z) Bare 型テンプレ (page-fullhtml-bare.php 追加) | SWELL の SEO 機能が使えなくなる、ヘッダー/フッターも自作になる |
| (X) SWELL カスタマイザーのメインビジュアル復活 | 既に削除済、AI HTML の Hero と冗長になる |
| (Y') tmp/front.php に AI HTML を直書き | 編集容易性 NF-3 を満たせない (= 田中さんが PHP を触れないと更新不可) |
| (W) 完全ヘッドレス (Astro / Next.js) | スコープ外。工数 1 ヶ月以上かかる |
| (V) Cloudflare Workers でルート別配信 | 田中さんから「不要」の判断あり |

---

## 2. 移行後のアーキテクチャ全体図

```
┌──────────────────────────────────────────────┐
│ Browser (訪問者)                              │
└──────────────────────────────────────────────┘
        ↓ HTTPS
┌──────────────────────────────────────────────┐
│ Xserver / nginx / Apache / PHP 8.3            │
│ WordPress 6.9.4 + SWELL 2.12.0 + swell_child  │
└──────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────┐
│ swell_child テーマ (子テーマ)                  │
│  ├─ functions.php  (★ 変更なし)                │
│  ├─ page.php       (★ 変更なし)                │
│  ├─ tmp/front.php  (★★ 最小化版に書き換え)      │
│  │   = the_content() を呼ぶだけのプロキシ      │
│  └─ assets/style.css, bz_area.css (★ 変更なし) │
└──────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────┐
│ WordPress 固定ページ (DB に格納)               │
│  ├─ ID=10  TOP            ★ post_content に AI HTML (index.html)     │
│  ├─ ID=704 biz-core       ★ post_content に AI HTML (biz-core.html)  │
│  ├─ ID=706 ai-core        ★ post_content に AI HTML (ai-core.html)   │
│  ├─ ID=708 contact-new    ★ post_content に AI HTML (contact.html)   │
│  ├─ ID=710 company-new    ★ post_content に AI HTML (company.html)   │
│  ├─ ID=53  company        (変更なし、独自メディアセクション維持)        │
│  ├─ ID=54  news           (変更なし)                                   │
│  ├─ ID=3   privacy-policy (変更なし)                                   │
│  └─ ID=55  contact        (draft のまま、変更なし)                     │
└──────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────┐
│ アセット                                       │
│  /wp-content/uploads/                         │
│  ├─ 2024/12/CoreDriven ロゴ.png  (★ 既存・流用)│
│  └─ coredriven-html/             (★ 新規作成)  │
│       ├─ logo-core-driven.png                 │
│       ├─ logo.svg                             │
│       ├─ tanaka.jpg                           │
│       ├─ machida.jpg                          │
│       └─ yoshida.webp                         │
└──────────────────────────────────────────────┘
```

### 2.1 「★★」のコア変更点
**`swell_child/tmp/front.php`** を 112KB の独自直書き HTML から **8 行の最小プロキシ** に書き換える:

```php
<?php
if ( ! defined( 'ABSPATH' ) ) exit;
?>
<main id="main_content" class="l-mainContent l-article">
    <div class="l-mainContent__inner">
        <div class="post_content"><?php while ( have_posts() ) : the_post(); the_content(); endwhile; ?></div>
    </div>
</main>
```

→ これにより、TOP 表示時も他の固定ページと同じく **post_content (ブロックエディタの内容)** が表示されるようになる。

### 2.2 「★」の付随変更点
- `wp post update 10 --post_content=<AI HTML>` で TOP の post_content に AI HTML を投入 (Phase 0)
- 残 4 ページも同様 (Phase 1)
- 画像は `/wp-content/uploads/coredriven-html/` 配下に配置

---

## 3. 移行後のデータフロー

### 3.1 TOP アクセス時 (Phase 0 完了後)

```
[ユーザがブラウザで https://core-driven.com/ にアクセス]
        ↓
[WordPress 起動 → ID=10 取得 → page.php 選択]
        ↓
[swell_child/page.php 実行]
        ├─ get_header()  →  SWELL ヘッダー出力 (ロゴ + メニュー)
        ├─ is_front_page() = true
        └─ SWELL_Theme::get_parts('tmp/front')
              ↓
              swell_child/tmp/front.php 実行 (★ 最小化版)
              └─ while (have_posts()) : the_post(); the_content();
                  ├─ ID=10 の post_content を取得
                  └─ apply_filters('the_content', ...) で
                     カスタム HTML ブロックの中身 (= AI HTML) を出力
        └─ get_footer() → SWELL フッター出力
        ↓
[完成した HTML がブラウザに返る]
```

### 3.2 残ページアクセス時 (Phase 1 完了後)
```
[ユーザが /biz-core/ 等にアクセス]
        ↓
[page.php → is_front_page() = false → 通常処理]
        ↓
[the_content() で post_content (= AI HTML) を出力]
        ↓
[ブラウザに返る]
```

→ TOP も他ページも **同じ仕組み (post_content を表示)** で統一される。

---

## 4. ファイルレベルの変更一覧 (Diff サマリ)

### 4.1 変更するファイル
| ファイル | 変更内容 | 影響範囲 | リスク |
|---|---|---|---|
| `swell_child/tmp/front.php` | 112KB → 約 350 bytes に最小化 | TOP 表示のみ | 低 (バックアップ取得後に変更) |

### 4.2 変更しないファイル
| ファイル | 理由 |
|---|---|
| `swell_child/page.php` | `is_front_page()` 分岐は残し、tmp/front.php 経由で post_content を出す設計 |
| `swell_child/functions.php` | enqueue 設定はそのまま流用 |
| `swell_child/assets/style.css` | `.custom-message__*` は AI HTML では使わないが、移行直後は残置 (Phase 2 でクリーンアップ) |
| `swell_child/assets/bz_area.css` | 同上 (`.biz__*`) |
| `swell_child/parts/*` | ヘッダー / フッターの構成パーツはそのまま |
| 親テーマ `swell/*` | 親テーマは触らない (アップデート耐性のため) |

### 4.3 新規作成するファイル / リソース
| 種類 | パス | 内容 |
|---|---|---|
| ディレクトリ | `/wp-content/uploads/coredriven-html/` | AI HTML 用画像置き場 |
| 画像 | `/wp-content/uploads/coredriven-html/logo-core-driven.png` | AI HTML 内ロゴ (将来用) |
| 画像 | `/wp-content/uploads/coredriven-html/logo.svg` | 同上 |
| 画像 | `/wp-content/uploads/coredriven-html/tanaka.jpg` | Members 田中 |
| 画像 | `/wp-content/uploads/coredriven-html/machida.jpg` | Members 町田 |
| 画像 | `/wp-content/uploads/coredriven-html/yoshida.webp` | Members 吉田 |

### 4.4 DB レベルの変更
| WP テーブル | 変更内容 |
|---|---|
| `wp_posts` (ID=10 の post_content) | 空 → AI HTML (約 36 KB) |
| `wp_posts` (ID=704, 706, 708, 710 の post_content) | 空 → AI HTML (Phase 1) |
| `wp_posts` (ID=704, 706, 708, 710 の post_status) | draft → publish (Phase 1) |
| `wp_options` | 変更なし |
| `wp_postmeta` | 変更なし (テンプレート選択も default のまま) |

---

## 5. 各ページの仕様 (Phase 1 完了時)

### 5.1 TOP (ID=10, slug=top)
```
URL: https://core-driven.com/
画面構成 (上から):
  1. SWELL ヘッダー (ロゴ + メニュー)
  2. AI HTML 本文
     ├─ Hero「経営者の熱意を実現する 経営伴走・事業共創パートナー」
     ├─ Role (構想整理 / 事業推進 / 仕組み化)
     ├─ Challenges (10 個の課題リスト)
     ├─ Services (Biz Core / AI Core)
     ├─ Strengths (5 つの強み)
     ├─ Members (吉田 / 町田 / 田中)
     └─ Final CTA
  3. SWELL フッター
内部リンク先:
  「相談する」     → /contact-new/
  「Biz Coreを見る」→ /biz-core/
  「AI Coreを見る」→ /ai-core/
  「メンバー詳細」→ /company-new/#members
```

### 5.2 Biz Core (ID=704, slug=biz-core) — Phase 1 で公開
```
URL: https://core-driven.com/biz-core/
画面構成: SWELL ヘッダー + AI biz-core.html 本文 + SWELL フッター
状態: draft → publish に変更
```

### 5.3 AI Core (ID=706, slug=ai-core) — Phase 1 で公開
```
URL: https://core-driven.com/ai-core/
画面構成: SWELL ヘッダー + AI ai-core.html 本文 + SWELL フッター
状態: draft → publish に変更
```

### 5.4 Contact (新版) (ID=708, slug=contact-new) — Phase 1 で公開
```
URL: https://core-driven.com/contact-new/
画面構成: SWELL ヘッダー + AI contact.html 本文 + SWELL フッター
状態: draft → publish に変更
備考: 既存 /contact/ (ID=55) は draft のまま放置 (将来 Phase 2 で削除検討)
```

### 5.5 Company (新版) (ID=710, slug=company-new) — Phase 1 で公開
```
URL: https://core-driven.com/company-new/
画面構成: SWELL ヘッダー + AI company.html 本文 + SWELL フッター
状態: draft → publish に変更
備考: 既存 /company/ (ID=53) はメディアセクション付きで残置
```

### 5.6 既存ページ (変更なし)
```
/news/           ← post_content そのまま (投稿リスト)
/privacy-policy/ ← post_content そのまま
/company/        ← post_content + 独自メディアセクション (page.php 24-72 行目)
/contact/        ← draft のまま
```

---

## 6. ナビゲーションメニュー (Phase 1 完了時)

### 6.1 移行前 (現状)
```
TOP / Business.[#ai/#career/#biz] / Company / News / Contact[Google Form]
```

### 6.2 移行後 (Phase 1 完了時)
**選択肢 A (推奨)**: AI HTML 構造に合わせる
```
TOP        → /
Biz Core   → /biz-core/
AI Core    → /ai-core/
Company    → /company-new/  (or /company/ 既存に戻す選択も可)
News       → /news/
Contact    → /contact-new/  (or Google Form 直リンクのまま)
```

**選択肢 B (互換性優先)**: 既存メニュー維持 + アンカー先を AI HTML に整合させる
```
TOP / Business[/biz-core/, /ai-core/] / Company / News / Contact
```

→ 選択は田中さんと Phase 1 着手時に協議。Phase 0 中はメニューに触らない。

---

## 7. SEO への影響

### 7.1 維持される機能
- SEO SIMPLE PACK が出力する `<meta name="description">` `<meta name="keywords">` `<meta property="og:*">` `<link rel="canonical">` 等
- Twitter Card meta
- 構造化データ (SWELL が出力する Article schema 等)

### 7.2 変更されるもの
- 各ページの **コンテンツ内 H1〜H3 構造** が AI HTML のものに変わる (= キーワード密度・見出し構造が変わる)
- 内部リンク構造が新スラッグ (`/biz-core/` 等) を含む形に変わる

### 7.3 Phase 0 直後の SEO 影響予測
- TOP のコンテンツが大幅変化 → Google にクロールされ次第インデックス更新
- メタ情報は SEO SIMPLE PACK が固定値を出すので大きな変動なし
- Search Console での「インデックス → カバレッジ」確認推奨 (週次)

---

## 8. パフォーマンス影響

### 8.1 軽くなる要素
- 旧 tmp/front.php (112 KB の HTML 直書き) → 約 36 KB の AI HTML (post_content 経由)
- 不要画像 (旧 MV 03/04-scaled.jpg = 2.5MB クラス) は既に削除済

### 8.2 重くなる可能性
- AI HTML 内に Google Fonts (Inter / Noto Sans JP / JetBrains Mono) を追加読込 → +200ms 程度の初回読込増
- インライン CSS (約 13 KB) が post_content に含まれる → 初回レンダリングが遅延する可能性

### 8.3 対策 (Phase 2 検討)
- Google Fonts → 既存 TS Webfonts for XSERVER と統合可能か検討
- インライン CSS → assets/coredriven-html.css 等に外出し、enqueue で読込

---

## 9. 移行後の運用イメージ

### 9.1 田中さんが TOP のテキストを 1 文字変更したい場合
1. WP 管理画面 → 「ページ → 固定ページ一覧 → TOP」を編集
2. カスタム HTML ブロックを開く
3. 該当箇所を編集
4. 「更新」をクリック → 即反映

→ 所要 1 分。FTP / PHP 編集不要。

### 9.2 田中さんがデザイン全体を更新したい場合
1. AI に「TOP の新 HTML」を生成依頼 (zip で受領)
2. 田中さんが WP 管理画面でカスタム HTML ブロックの中身を全選択 → 新 HTML を貼付
3. 「更新」をクリック → 即反映

→ 所要 5 分。

### 9.3 ロールバックしたい場合
- WP のリビジョン機能で過去版に戻す (1 クリック)
- または `wp post update 10 --post_content=$(cat backup.html)` で SSH 経由復元

---

## 10. クリーンアップ対象 (Phase 2 候補)

移行直後は触らないが、安定運用後に削除候補:

| 対象 | 場所 | 削除タイミング | 削除前の確認 |
|---|---|---|---|
| `swell_child/tmp/front.php.backup_*` | `/wp-content/themes/swell_child/tmp/` | Phase 0 から 1 ヶ月後 | ロールバック不要が確認できたら |
| `.custom-message__*` 用 CSS | `swell_child/assets/style.css` | Phase 1 完了後 | AI HTML が依存していないこと |
| `.biz__*` 用 CSS | `swell_child/assets/bz_area.css` | 同上 | 同上 |
| 旧 MV 画像 (03-scaled.jpg, 04-scaled.jpg) | `/wp-content/uploads/2025/01/` | 既に削除済 | - |
| 旧テスト用画像 | `/wp-content/uploads/2025/02/テスト用.png` | Phase 1 完了後 | AI HTML が参照していないこと |
| `swell_child/memo.php` | `/wp-content/themes/swell_child/` | 用途確認後 | 田中さんへの確認 |

---

**END OF FUTURE ARCHITECTURE.** 作業手順の詳細は `04_migration_plan.md` を参照。
