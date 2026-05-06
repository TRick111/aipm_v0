# BL-0079 — CoreDriven HP 移行 要件定義書

**作成日**: 2026-05-06
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft (田中さん review 待ち)
**関連 BL**: BL-0079

---

## 1. プロジェクト概要

### 1.1 背景
CoreDriven のコーポレートサイト ([core-driven.com](https://core-driven.com)) は WordPress + SWELL テーマで構築されているが、トップページのコンテンツ (Hero メッセージ「すべての人や企業…」+ Restaurant AI Lab. / Career Lab. / 事業開発支援 セクション) が **子テーマの PHP ファイル (`swell_child/tmp/front.php`) に直書き** されており、WP 管理画面のブロックエディタからは編集できない状態。

田中さん側で AI 生成済の新デザイン HTML (`Core Driven_20260426.zip` / 5 ページ + assets) があり、これを WordPress に載せ替えたい。

### 1.2 目的 (このプロジェクトのゴール)
**AI が生成した新 HTML をサイト本番に反映する。** ただし全部置換ではなく、WordPress の運用機構 (ヘッダー / フッター / メニュー / SEO プラグイン / 投稿ニュース) は維持する **ハイブリッド構成** とする。

### 1.3 ステークホルダー
| 役割 | 担当 |
|---|---|
| 意思決定者 | 田中利空 (CoreDriven CTO) |
| 実装者 | AI (Claude / ssh + WP-CLI 経由) |
| 確認者 | 田中利空 (シークレットウィンドウでのプレビュー確認) |
| 影響を受けるページ訪問者 | CoreDriven HP 訪問者全員 |

---

## 2. 機能要件

### 2.1 ユーザの言葉での要求 (原文)
> 今のワードプレスのページで添付した HTML の内容になるようにしたい。
> ただしヘッダーはワードプレスの仕組みを使ったままという形にしたい。

### 2.2 技術要件への落とし込み

| ID | 要件 | 詳細 |
|---|---|---|
| **F-1** | TOP ページで AI HTML を表示 | `https://core-driven.com/` で `Core Driven_20260426.zip` の `index.html` の本文 (Hero / Role / Challenges / Services / Strengths / Members / Final CTA) が表示される |
| **F-2** | 5 ページ全体を AI HTML 化 | TOP / Biz Core / AI Core / Contact / Company の 5 ページが AI HTML で表示される |
| **F-3** | WP ヘッダー維持 | ロゴ・グローバルナビ・SP メニューは SWELL の管理機能 (外観 → メニュー / カスタマイザー) で従来どおり管理される。AI HTML 内の独自ヘッダー (`<header class="site-header">` 等) は使わない |
| **F-4** | WP フッター維持 | フッターも同様に SWELL 管理。AI HTML 内の独自フッター (`<footer class="site-footer-mini">`) は使わない |
| **F-5** | SEO プラグイン (SEO SIMPLE PACK) の機能維持 | meta description / OG / canonical 等は SEO SIMPLE PACK が動的に出力する。AI HTML 側に重複した meta は書かない |
| **F-6** | 内部リンクの整合 | AI HTML 内の `contact.html` 等の相対リンクは WP の固定ページ URL (`/contact-new/` 等) に書換 |
| **F-7** | 画像アセットの WP 配置 | AI HTML が参照する 5 画像 (logo-core-driven.png / logo.svg / tanaka.jpg / machida.jpg / yoshida.webp) は `/wp-content/uploads/coredriven-html/` に配置 |
| **F-8** | 既存ページの保護 | `/news/` (ID=54) `/privacy-policy/` (ID=3) `/company/` (ID=53、独自メディアセクション付き) は **一切変更しない** |
| **F-9** | 既存 `/contact/` の取り扱い | スラッグ `/contact/` (ID=55) は現状 draft (非公開)。新 `/contact-new/` で代用するため触らない |
| **F-10** | TOP のホームページ表示 | `https://core-driven.com/` (= スラッグ `/top/` 相当) で AI HTML が出る (= 「設定 → 表示設定 → ホームページの表示」が固定ページ TOP に指定された状態を維持) |
| **F-11** | 編集容易性 | 将来 AI HTML を更新したい時、田中さんが WP 管理画面 (固定ページ編集 → カスタム HTML ブロック) で更新できる状態にする (= 子テーマ PHP 直書きはしない) |

### 2.3 スコープ外 (今回はやらない)
| ID | 内容 |
|---|---|
| OUT-1 | News (投稿一覧 `/news/`) の改修 |
| OUT-2 | お問い合わせフォームの実装 (現状 Google Form 直リンクのまま維持) |
| OUT-3 | SWELL 親テーマの改造 |
| OUT-4 | 完全ヘッドレス化 (Astro / Next.js への移行) |
| OUT-5 | Cloudflare 等の CDN / リバースプロキシ導入 |
| OUT-6 | カスタムフォント (TS Webfonts for Xserver) の差し替え |

---

## 3. 非機能要件

| ID | カテゴリ | 要件 | 検証方法 |
|---|---|---|---|
| **NF-1** | 可用性 | 移行作業中もサイトはダウンしない (or 数秒以内のダウンに留める) | 作業中も `curl https://core-driven.com/` が 200 を返す |
| **NF-2** | 復旧性 | 任意のステップで 5 分以内にロールバック可能 | 各ステップ別ロールバック手順を `04_migration_plan.md §6` に明記、リハーサル実施 |
| **NF-3** | 編集容易性 | AI HTML の更新は田中さん 1 人で 5 分以内に実施可能 (WP 管理画面で完結) | カスタム HTML ブロックの貼り替えだけで更新できる |
| **NF-4** | パフォーマンス | Lighthouse Performance スコアが既存比 ±10 ポイント以内 | 移行前後で測定 |
| **NF-5** | SEO 影響最小化 | meta description / canonical / 構造化データが移行前後で同等 | 移行前後の HTML を diff |
| **NF-6** | テーマ更新耐性 | SWELL 親テーマがアップデートされても表示が崩れない | 子テーマ swell_child のみで完結する設計 |
| **NF-7** | セキュリティ | カスタム HTML ブロックは管理者ロールのみ編集可 (KSES filter 適用外なので) | WP のロール権限で制御 |
| **NF-8** | アクセシビリティ | 既存テーマの a11y 機能 (スキップリンク・ARIA) を阻害しない | スクリーンリーダーで主要操作可能 |

---

## 4. 制約条件

| カテゴリ | 内容 |
|---|---|
| **インフラ** | Xserver (sv12363 / my0126.xsrv.jp) / Linux / nginx 前段 / Apache 後段 |
| **PHP** | 5.4 (デフォルト) / 8.3.30 (推奨・WP-CLI 用に手動指定) |
| **WordPress** | 6.9.4 |
| **テーマ** | SWELL v2.12.0 (親) + swell_child (子・有効化中) |
| **プラグイン** | SEO SIMPLE PACK 3.6.2、All-in-One WP Migration、TS Webfonts for XSERVER 等 |
| **既存スラッグ** | `top` `company` `contact` `news` `privacy-policy` (変更不可) |
| **新規スラッグ** | `biz-core` `ai-core` `contact-new` `company-new` (5/6 作成済、draft) |
| **権限** | 田中さん = WP 管理者 + Xserver SSH 公開鍵認証 (公開鍵登録済) |
| **言語** | 日本語 (`<html lang="ja">`) |

---

## 5. 成功基準 (Definition of Done)

### 5.1 Phase 0 完了条件 (TOP 置換)
- [ ] `https://core-driven.com/` が AI HTML の TOP で表示される
- [ ] SWELL のヘッダー (ロゴ + メニュー) が画面上部に出る
- [ ] SWELL のフッターが画面下部に出る
- [ ] AI HTML の Hero / Role / Challenges / Services / Strengths / Members / Final CTA セクションが順に表示される
- [ ] 画像 3 枚 (吉田・町田・田中) が表示される
- [ ] 「相談する」ボタンが `/contact-new/` に遷移する (= 下書き状態でも 404 にならず該当固定ページが出る)
- [ ] DevTools Console に致命的な JS エラーがない
- [ ] iPhone 実機 (or DevTools の SP モード) でレイアウトが崩れない
- [ ] 既存の `/news/` `/privacy-policy/` `/company/` がアクセス可能で表示が変わっていない
- [ ] ロールバック手順 (`04_migration_plan.md §6.1`) を実施すれば移行前の状態に戻せる

### 5.2 Phase 1 完了条件 (残 4 ページ)
- [ ] `/biz-core/` `/ai-core/` `/contact-new/` `/company-new/` が公開状態 (draft 解除)
- [ ] 各ページに対応する AI HTML (`biz-core.html` 等) の本文が表示される
- [ ] TOP からの内部リンクが全部繋がる (リンク切れゼロ)
- [ ] ナビメニューが新構造 (TOP / Biz Core / AI Core / Company / Contact) に再編される

### 5.3 全体完了条件 (Phase 2 まで)
- [ ] 旧 `tmp/front.php` のコードが整理されている (バックアップは保管)
- [ ] 不要な CSS (`.custom-message__*` `.biz__*`) が削除されている (or コメントアウト)
- [ ] CHANGELOG / 引き継ぎ資料が `Stock/` に保管されている

---

## 6. リスク

| ID | リスク | 発生確率 | 影響度 | 対策 |
|---|---|:-:|:-:|---|
| **R-1** | tmp/front.php 書き換えで PHP 構文エラー → 画面真っ白 | 低 | 高 | 書き換え前にバックアップ、構文チェック (`php -l`) を実施、問題時は cp で即復元 |
| **R-2** | wp post update で post_content が破損 | 低 | 中 | 更新前に既存 post_content をローカル保存、WP のリビジョン機能でも自動保存される |
| **R-3** | 画像アセットのアップロード忘れ → 画像 404 | 中 | 低 | 公開前に DevTools Network で全画像 200 確認、5 ファイル明示的にチェック |
| **R-4** | 内部リンク `/contact-new/` がまだ draft で 404 | 中 | 中 | Phase 0 公開前に `/contact-new/` を「公開」状態に変更 (中身空でも) |
| **R-5** | SWELL の管理メニュー (TOP / Business / Company / News / Contact) が AI HTML の意図と不一致 | 中 | 中 | Phase 1 完了後にメニュー再編、Phase 0 中は既存メニューのまま |
| **R-6** | SWELL アップデートで page.php が上書きされて TOP の AI HTML が出なくなる | 低 | 中 | swell_child のみ編集する設計 (親テーマは触らない) |
| **R-7** | キャッシュプラグインで古い表示が残り、田中さんが更新を確認できない | 中 | 低 | キャッシュクリア手順を migration_plan に明記 |

---

## 7. 用語集

| 用語 | 意味 |
|---|---|
| **AI HTML** | `Core Driven_20260426.zip` に含まれる新デザインの HTML 一式 (5 ページ + assets) |
| **SWELL** | CoreDriven が使っている WordPress 有料テーマ (v2.12.0) |
| **swell_child** | SWELL の子テーマ。CoreDriven のカスタマイズ (tmp/front.php の直書き等) はここに集約されている |
| **tmp/front.php** | swell_child 内の TOP ページ専用テンプレート。現在 112KB の独自 HTML が直書きされている |
| **post_content** | WP の固定ページの本文 (ブロックエディタで編集する内容) |
| **page.php** | WP のテンプレート階層で「固定ページ」用に呼ばれる PHP ファイル。今回 swell_child/page.php の中で `is_front_page()` 分岐で tmp/front を呼んでいる |
| **is_front_page()** | WP の関数。「設定 → 表示設定 → ホームページの表示」で固定ページ表示にして指定したページ (= ID=10 / TOP) で true を返す |
| **WP-CLI** | WordPress のコマンドラインツール。`wp post update` で post_content を直接更新できる |

---

**END OF REQUIREMENTS.** 詳細は下記ドキュメントを参照:
- 現状構成: `02_current_architecture.md`
- 移行後構成: `03_future_architecture.md`
- 作業手順: `04_migration_plan.md`
