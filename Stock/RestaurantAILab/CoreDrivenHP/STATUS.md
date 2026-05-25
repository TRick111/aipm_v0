# STATUS — Core Driven HP

更新: 2026-05-26

## 進捗（全件完了）

- [x] AIPM プロジェクト作成 & 初回バックアップ (`backup/wp_20260525_233551/`)
- [x] トップページの Meta Title / Description 更新（ssp_settings）
- [x] 各ページの Meta Title / Description 適用（ID 10/710/706/704/708/54/3）
- [x] 旧 Company ページ (ID 53) を非公開化（draft）。/company → /company-new/ への 301 リダイレクトは Redirection プラグインで継続
- [x] レイアウト崩れの原因調査（`investigations/root_cause_20260526.md`）
- [x] レイアウト修正の適用（子テーマ `swell_child/assets/style.css` に追記、Version 1.0.1 へバンプ）
- [x] fit-card 円位置 & final-cta 中央揃えの v2 修正（`:where()` で specificity を SWELL と同等に揃え、`h3:before` の `position:absolute` をリセット。Version 1.0.3）

## 適用したメタ（最終）

| ID | URL | Title | Description (要約) |
|---|---|---|---|
| 10 | `/` | 株式会社Core Driven（コアドリブン） | 経営者の熱意や構想を事業として実現へ導く… |
| 710 | `/company-new` | 会社概要 \| 株式会社Core Driven（コアドリブン） | Core Drivenは経営者の熱意を実現へ導く事業共創パートナー… |
| 706 | `/ai-core` | AI Core \| AIによる経営伴走 \| 株式会社Core Driven | AI Coreは経営者の判断と実行を支えるAI業務OS… |
| 704 | `/biz-core` | Biz Core \| 人による経営伴走 \| 株式会社Core Driven | Biz Coreは経営者の熱意や構想を起点に事業設計〜現場運用まで… |
| 708 | `/contact-new` | お問い合わせ \| 株式会社Core Driven | 事業構想の整理〜AI導入まで、相談内容は未整理でも可… |
| 54 | `/news` | News \| 株式会社Core Driven | お知らせ・最新トピックス |
| 3 | `/privacy-policy` | プライバシーポリシー \| 株式会社Core Driven | 個人情報の取り扱い方針 |

## レイアウト修正 — 概要

**原因**: SWELL テーマの `.post_content h1〜h4` ルール (specificity 0,1,1) が、ローカル HTML の `<style>` 内のベース要素セレクタ (0,0,1) を上書きしていた。加えて `.l-container` の左右パディング 48px がコンテンツを内側に押し込んでいた。

**対策**: 子テーマ `style.css` の末尾に、対象ページ（ID 10/704/706/708/710）に限定したスコープ付き上書き CSS を追記。`.page-id-N .post_content h2 { ... }` の形で SWELL と同じ specificity・後勝ちで適用。

**Before / After スクショ**: `investigations/desktop_live.png` → `desktop_live_after.png`

## 残課題（任意）

- モバイル h2 が 26px（local 24px）— `clamp(26px, 3.6vw, 48px)` の下限。`@media(max-width:720px)` の上書きを追記すれば 24px に揃えられる
- Biz Core / AI Core / Contact-new / Company-new 各ページの目視確認（CSS は適用済みだが体感での確認推奨）
- 旧 Contact 下書き (ID 55) と 投稿下書き「Restaurant AI Lab.」(ID 690) の要否確認

## ロールバック手順

```bash
# 子テーマ style.css を復元
scp -P 10022 backup/wp_20260526_011424/swell_child_style.css.before \
  xserver-coredriven:/home/my0126/core-driven.com/public_html/wp-content/themes/swell_child/assets/style.css

# Version を 1.0.0 に戻す（任意）
ssh xserver-coredriven 'perl -i -pe "s/^( Version:\s+)1\.0\.1/\${1}1.0.0/" \
  ~/core-driven.com/public_html/wp-content/themes/swell_child/style.css'
```

メタを戻す場合は `backup/wp_20260525_233551/ssp_settings.json` を `wp option update ssp_settings --format=json` で書き戻し。
