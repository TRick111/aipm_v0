# BL-0079 v3 — CoreDriven WP 移行・最終実行計画

**作成日**: 2026-05-05 22:15 JST
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft（田中さん review 待ち）
**関連 BL**: BL-0079

**先行成果物 (review 済 done)**:
- v1 調査: `Flow/.../2026-05-03/0.Other/CoreDriven/wordpress_full_html_mechanism.md`
- 実装キット: `Flow/.../2026-05-05/0.Other/CoreDriven/wordpress_implementation_kit.md`
- v2 戦略: `Flow/.../2026-05-05/0.Other/CoreDriven/wordpress_replace_strategy_v2.md`

**新規同梱**:
- 貼り付け用 HTML: `Flow/.../2026-05-05/0.Other/CoreDriven/coredriven_top_paste_ready.html` (TOP 置換専用、加工済み)

---

## 0. 田中さん回答の整理 (2026-05-05 夜)

| ID | 内容 | 確定値 |
|---|---|---|
| Q-A | 親テーマ名 | ✅ SWELL v2.12.0 |
| Q-B | 子テーマ作成要否 | ✅ swell_child 既存 |
| Q-C | AI HTML 最新版の所在 | ✅ `~/Downloads/Core Driven_20260426.zip` (本日受領) |
| Q-D | カスタム HTML 編集権限 | ✅ **管理者のみ** |
| Q-E | URL 構造 | ✅ **ルートに置き換え** (別 path 並走しない) |
| Q-F | 更新頻度・自動化 | ✅ 頻度低、**自動化スコープ外** |
| Q-G | Phase 0 の対象ページ | ✅ **トップページ** |
| Q-H | Cloudflare 既導入 | ❓ 未確定 (本計画では「不要」前提で進める) |
| 追加 | WP 管理者権限 | ✅ あり |
| 追加 | コマンドライン編集の希望 | ❓ 質問中 (§3 で回答) |

---

## 1. ZIP 内容の inventory (`Core Driven_20260426.zip`)

```
Core Driven_20260426.zip (5.8 MB)
├── index.html         (489 行 / トップページ ★)
├── ai-core.html       (733 行 / AI Core サービス詳細)
├── biz-core.html      (391 行 / Biz Core サービス詳細)
├── company.html       (349 行 / 会社概要)
├── contact.html       (227 行 / お問い合わせ)
├── index-print.html   (564 行 / 印刷版)
├── preview.html       (180 行 / プレビュー)
├── assets/
│   ├── styles.css            (13 KB / 全ページ共通 design system)
│   ├── site.js               (2.5 KB / ヘッダー/フッター動的注入)
│   ├── logo-core-driven.png  (24 KB)
│   ├── logo.svg              (945 B)
│   ├── tanaka.jpg            (1.3 MB) ← 田中さん本人
│   ├── machida.jpg           (294 KB) ← 町田さん
│   └── yoshida.webp          (46 KB)  ← 吉田さん
├── scraps/biz-mobile.png
└── uploads/(社内資料 PDF 群、公開対象外)
```

### 1.1 重要な構造的発見

AI HTML は **静的 `<header>` / `<footer>` を持っておらず、`assets/site.js` の `injectHeaderFooter()` 関数で動的注入** している:

```html
<body>
<script src="assets/site.js"></script>
<script>injectHeaderFooter('home')</script>  ← これが header/footer を JS で挿入
<section class="hero">...</section>
...
<section class="final-cta">...</section>
</body>
```

これにより **2 つの選択肢が技術的に成立** する:

| 選択 | 仕組み | SWELL ヘッダー | AI ヘッダー |
|---|---|:-:|:-:|
| **A. SWELL の枠を使う** | `<script>injectHeaderFooter</script>` 削除して section 群だけ流す | ✅ 残す | ❌ 出さない |
| **B. AI HTML の枠を使う** | `<script>` を残し、SWELL の header/footer 出力を停止 (Bare 型テンプレ) | ❌ 出さない | ✅ 出す |

→ **本計画は (A) を採用**: 既存サイトの URL/グロナビ構造を維持できる、ロールバック容易、SEO プラグイン (SEO SIMPLE PACK) も効く。AI HTML の独自ヘッダー (Biz Core / AI Core / 会社概要 / お問い合わせ) はサイト全体置換が完了してから (B) に切り替えても良い。

---

## 2. Cloudflare は何のために必要だったのか (回答)

5/5 v2 レポートで「Tier 5B: リバースプロキシ」として Cloudflare を提案したのは、**「path 別に WP と別 origin を切り替える」場合のため**:

```
[Cloudflare Worker]
  ├─ /landing/* → Vercel  (新サイトを試す)
  └─ /*         → Xserver (旧 WP のまま)
```

これは「**部分的に試す**」「**A/B テスト**」「**段階的移行で旧サイトを残しながら新サイトを並走**」という用途。

### 田中さんの方針 (= ルート全体置換 + 自動化不要) では Cloudflare は不要

理由:
1. URL を `/` ルートに置き換える方針なので、path 別振り分けが不要
2. 旧サイトを並走させない (一気に置き換える) のでバックアップ用 origin も不要
3. 更新頻度が低いので CDN キャッシュ管理の自動化も不要 (あった方が速いが必須ではない)
4. Xserver 標準で既に nginx + KUSANAGI 級の高速化が効いている

→ **Cloudflare は将来 (Phase 4 以降) 検討で十分**。導入するメリットがある場面は:
- 急にトラフィックが増えて Xserver の応答が重くなった
- 海外からのアクセスを高速化したい
- DDoS / WAF 等のセキュリティ強化
- ドメインを別 host (Vercel等) と二重運用したい

---

## 3. WordPress をコマンドラインから編集できるか (回答)

**結論: 可能。ただし TOP 置換だけなら不要。** 3 つの選択肢がある。

### 選択肢 1. WP 管理画面の「外観 → テーマファイルエディタ」 (推奨・最短)

- 管理画面 → 外観 → テーマファイルエディタ
- 画面上部のセレクタで **swell_child** を選択
- 左サイドバーから既存ファイルを編集、または「新規ファイル」ボタンで `page-fullhtml.php` を作成
- **メリット**: コマンドライン不要、SSH 設定不要、即時反映
- **デメリット**: 編集ミスで真っ白になるリスク (FTP で復旧)
- **TOP 置換だけならそもそも不要** (固定ページ編集だけで完結する)

### 選択肢 2. Xserver SSH + WP-CLI

- Xserver サーバーパネル → 「SSH 設定」→ ON
- 公開鍵を登録 (パスワード認証は不可)
- ターミナルから `ssh -p 10022 <ユーザID>@<サーバ番号>.xserver.jp`
- Xserver には標準で WP-CLI が入っているが PHP バージョンが古いので、新しい WP-CLI を `~/bin/wp` に自前インストール推奨
- 例: `wp post list`、`wp post update <ID> --post_content="$(cat new.html)"`、`wp media import ./assets/*`
- **メリット**: 一括操作、自動化、CI 連携可能
- **デメリット**: 初期セットアップに 30 分〜1 時間、SSH 公開鍵の準備が必要
- **適用ケース**: 残りページを一気に置換、画像をまとめてアップ、運用自動化を目指す場合

### 選択肢 3. Xserver ファイルマネージャー (ブラウザ)

- Xserver サーバーパネル → 「ファイルマネージャー」
- ブラウザ上で `wp-content/themes/swell_child/` に PHP ファイル追加可能
- **メリット**: SSH 不要、操作が GUI
- **デメリット**: 大量ファイル操作には不向き

### 推奨: 今夜の TOP 置換は **WP 管理画面のみ完結**

固定ページの編集と画像アップロードだけなので、コマンドラインに触れる必要はゼロ。残りページの一括置換に進む段階で SSH+WP-CLI を検討。

---

## 4. 今夜の TOP 置換手順 (Tier 1A 選択肢 A、所要 30 分)

### Step 1: 画像 5 枚をアップロード (5 分)

WP 管理画面 → 「メディア → 新規追加」で以下 5 枚をアップ:

```
~/Downloads/coredriven_html_inspect/assets/
├── logo-core-driven.png
├── logo.svg
├── tanaka.jpg
├── machida.jpg
└── yoshida.webp
```

> 重要: アップロード先パスを **統一** したいので、ファイル名のまま (リネーム禁止)。
> WP 標準だと `/wp-content/uploads/2026/05/<ファイル名>` に保存される。
> 貼り付け HTML は `/wp-content/uploads/coredriven-html/<ファイル名>` を期待しているので、**Step 1.5** で対応する。

### Step 1.5: 画像パスを WP の実保存先に合わせて書き換え (任意・3 分)

選択肢が 2 つ:

**A) WP の標準パスをそのまま使う**: アップロード後に「メディアライブラリ」で各画像の URL をコピーし、`coredriven_top_paste_ready.html` 内の `/wp-content/uploads/coredriven-html/<file>` を実 URL に書換 (5 箇所)。

**B) FTP / ファイルマネージャで `/wp-content/uploads/coredriven-html/` フォルダを作って配置**: 一回だけ FTP アクセスが必要だが、貼付 HTML を書き換え不要。将来的に AI HTML を更新する時もパスが固定で楽。

→ **B 推奨**。Xserver ファイルマネージャーで 1 分。

### Step 2: TOP 用固定ページを準備 (5 分)

WP 管理画面 → 「ページ → 固定ページ一覧」を確認。

- 既に「ホームページ」用の固定ページがある場合 → その編集画面を開く (タイトル例: 「Home」「TOP」「ホーム」等)
- 無い場合 → 「新規追加」でタイトル「Core Driven Top」等で作成

WP 管理画面 → 「設定 → 表示設定 → ホームページの表示」を確認:
- 「**固定ページ**」が選択され、上記の固定ページが「ホームページ」に指定されているか
- 違ったら設定 → 保存

### Step 3: カスタム HTML ブロックに本文を貼る (10 分)

1. 上記固定ページの編集画面を開く
2. **既存ブロックを全部削除** (Ctrl/Cmd+A → Delete でも可、心配ならドラフト保存しておくと revert できる)
3. ブロック追加 → 「カスタム HTML」を選択
4. `coredriven_top_paste_ready.html` の中身を **全部 (922 行 / 36 KB)** コピーしてブロック内に貼り付け
5. 「プレビュー」で確認
   - SWELL のヘッダー (TOP / Business / Company / News / Contact) が上に出る
   - その下に AI HTML の Hero (経営者の熱意を実現する...) → Role → Challenges → Services → Strengths → Members → Final CTA が表示される
   - SWELL のフッターが下に出る
6. ヘッダー直下のスペースが詰まりすぎていたら、貼付 HTML 末尾の `.ai-fullhtml-wrap section { padding: 120px 0 }` を `padding: 80px 0` 等に調整

### Step 4: 動作確認 (5 分)

下記をプレビューで確認:

- [ ] PC 表示: Hero / Role / Challenges / Services / Strengths / Members / Final CTA が順に出る
- [ ] SP 表示 (DevTools の iPhone 14): レスポンシブが効く (1 カラムに崩れる)
- [ ] 画像 3 枚 (吉田・町田・田中) が表示される
- [ ] ボタン「相談する」を押すと SWELL の `/contact/` ページに遷移する
- [ ] 「Biz Core を見る」「AI Core を見る」が `/biz-core/` `/ai-core/` に遷移する (← Step 5 で対応)
- [ ] スクロール時の動作 (スムーズスクロール、`#services` ジャンプ等)

### Step 5: 公開 + 内部リンク先ページの一時対応 (任意)

- 「相談する」「メンバー詳細を見る」等の内部リンク先 (`/contact/`, `/company/`, `/biz-core/`, `/ai-core/`) は **まだ AI HTML 化されていない**
- リンク切れ防止: 既存の固定ページが `/contact/` 等にある場合 → そのまま遷移する (SWELL のページが出る)
- 既存ページが無い場合 → 一時的にリンクを `#contact` 等のアンカー停止に変更、または既存の SWELL ページに合わせて URL 修正

確認: WP 管理画面 → 「ページ → 固定ページ一覧」で `/contact/` `/company/` `/biz-core/` `/ai-core/` のスラッグが既に存在するか確認する。

→ 公開ボタンを押す。これで TOP 置換完了。

---

## 5. 残りページの段階移行ロードマップ

| Phase | 期日 | 内容 | 工数 |
|---|---|---|---|
| **Phase 0** | 今夜〜明日 | TOP を Tier 1A で AI HTML 化 (本ドキュメント §4) | 30 分 |
| **Phase 1** | 5/6〜5/8 | `/biz-core/` `/ai-core/` `/company/` `/contact/` を同方式で置換 | 各 30 分 × 4 = 2 時間 |
| **Phase 2** | 5/9〜5/12 | SWELL ヘッダーが浮く違和感が許容できないなら **swell_child に `page-fullhtml-bare.php` 追加** → AI HTML の独自ヘッダー/フッターに完全移行 (Tier 2B 選択肢 B) | 半日 |
| **Phase 3** | 5/13〜5/20 | News 投稿 (`/news/*`) を AI 製のリストデザインで再表示 → カスタム投稿テンプレ (single.php / archive.php を子テーマで上書き) | 半日 |
| **Phase 4** | Q3 検討 | 必要なら Tier 5/6 (Cloudflare / Astro 等) へ。現状不要 | TBD |

### Phase 1 の効率化 Tips

5 ページとも構造が同じ (head 内 `<style>` + body 内 `<section>` + `<script>injectHeaderFooter</script>`) なので、本日生成した `coredriven_top_paste_ready.html` と同じ加工スクリプトを `biz-core.html` `ai-core.html` `company.html` `contact.html` に適用するだけで、4 ファイルの貼り付け HTML が量産できる。

→ Phase 0 の TOP 公開後、田中さんから OK が出次第 AI で 4 ファイル分の貼付 HTML を一括生成する。

### Phase 2 の判断基準

Phase 1 まで完了しても **「SWELL のヘッダーと AI 製のデザインが浮いている」「AI HTML 内の `<header>` の方が良い」** と感じる場合は Phase 2 に進む。具体的には:

1. `swell_child/page-fullhtml-bare.php` を新規作成 (中身は v2 レポート §6.4 の Bare テンプレ)
2. 各固定ページのテンプレートを `AI Full HTML — Bare` に切替
3. 貼付 HTML から `<script>injectHeaderFooter('xxx')</script>` 削除を解除 (= 残す) → AI HTML 独自のヘッダー/フッターが出る
4. SWELL の SEO SIMPLE PACK は wp_head() を呼ばない bare では効かないので、**meta タグを各 HTML 側に直接書く**

---

## 6. リスクと対策

| リスク | 症状 | 対策 |
|---|---|---|
| 貼付後に表示が崩れる | SWELL の `.l-mainContent` が `max-width: 1920px` で AI HTML の中央寄せが効かない | 貼付 HTML 末尾の `.ai-fullhtml-wrap` 周りで `width:100%` 強制済 (今夜試して必要に応じ追加 CSS) |
| 画像が 404 | 画像パスが間違っている | DevTools Network タブで赤行を確認 → メディアライブラリの実 URL に修正 |
| 内部リンクが既存 WP ページと衝突 | `/contact/` がスラッグで既存している | スラッグ確認、既存があるならそのまま遷移、無ければ Step 5 |
| Google Form 連携が消える | AI HTML には Google Form リンクが書かれていない | 既存の WP `/contact/` ページに Google Form のリンクが残っているなら問題なし |
| カスタム HTML が `<p>` で勝手に囲まれる | wpautop が走る | 「カスタム HTML」ブロック内なら自動回避される (`<!-- wp:html -->`) |
| スマホ表示でナビが詰まる | SWELL のハンバーガー + AI ヒーローの padding 衝突 | `@media(max-width:720px)` で Hero padding を調整、本資料末尾の SP 最適化 CSS 参照 |

---

## 7. ロールバック手順 (公開後に問題が出たら)

1. 固定ページ編集画面 → 右サイドバー「リビジョン」 → 元の状態に戻して更新
2. 「カスタム HTML」ブロック削除 → 旧ブロック構成に戻す
3. 「設定 → 表示設定 → ホームページの表示」で別ページに切替
4. 最悪: SWELL の DB バックアッププラグイン (BackWPup / UpdraftPlus) で前夜のスナップショットに復元

---

## 8. 田中さんへの確認事項 (残)

| ID | 質問 | なぜ必要 |
|---|---|---|
| Q-I (新規) | 既存 TOP の固定ページの「タイトル」と「スラッグ」は何か (WP 管理画面で確認可能) | Step 2 でどのページを編集するか確定するため |
| Q-J (新規) | 内部リンク先 `/biz-core/` `/ai-core/` `/company/` `/contact/` は既に存在するスラッグか? | Step 5 のリンク切れ判定 |
| Q-K (新規) | 画像配置パスは `/wp-content/uploads/coredriven-html/` で固定する? それとも WP 標準の `/uploads/2026/05/` のまま? | 貼付 HTML の画像 URL を最終確定するため |
| Q-L (新規) | Phase 0 (TOP 置換) で本番直接置き換える? それとも下書きでプレビュー確認後に公開? | 既存 TOP ページの停止リスク管理 |

---

## 9. 結論 (TL;DR)

1. **Cloudflare は今は不要**。「path 別 origin 切替」用なので、ルート全体置換方針なら出番なし。
2. **WP コマンドラインは可能だが TOP 置換には不要**。今夜は WP 管理画面だけで完結する。
3. **30 分作業で TOP 置換完了**: 画像 5 枚アップ → 固定ページ編集 → カスタム HTML ブロックに貼付 HTML を貼る → 公開。
4. 貼付 HTML は **既に生成済み** (`coredriven_top_paste_ready.html` / 36KB / 922 行)。コピペするだけ。
5. **SWELL のヘッダー・フッターは残し**、本文だけ AI HTML 化する選択肢 (A) を採用。Phase 2 で「全部 AI HTML」に切替も容易。
6. 残り 4 ページ (`biz-core/ai-core/company/contact`) は Phase 1 で同方式の量産で 2 時間で完了予定。

---

## 10. 次の AI 側アクション (田中さんが回答後)

田中さんが Q-I〜Q-L に回答 + Phase 0 動作確認 OK を確認したら、AI 側で:

1. `biz-core.html` `ai-core.html` `company.html` `contact.html` の 4 ファイルを同じ加工スクリプトで貼付 HTML 化
2. Phase 1 ロードマップに沿って WP に貼り付ける手順を deliverable 化
3. (希望があれば) WP-CLI 経由で wp post update を一括実行する shell script を生成

---

**END OF v3 PLAN.** 今夜の Phase 0 開始可能。
