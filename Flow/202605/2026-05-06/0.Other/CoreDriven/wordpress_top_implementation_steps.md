# BL-0079 — CoreDriven TOP 置換 実装手順書 (画面操作版)

**作成日**: 2026-05-06
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft（田中さん作業用）
**関連 BL**: BL-0079
**所要**: 約 45 分（初回。慣れたら 30 分）

**前提**:
- WP 管理者権限あり ✅
- WP-CLI 不使用 ✅ (画面操作 + Xserver ファイルマネージャだけで完結)
- 既存スラッグ: `company` / `contact` / `news` / `privacy-policy` / `top`
- TOP のタイトル: 「TOP」
- 既存 `/contact/` `/company/` は残す → AI 版は新スラッグで作成
- 画像配置: `/wp-content/uploads/coredriven-html/`
- 同梱貼付 HTML: `coredriven_top_paste_ready_v2.html` (リンク書換済)

---

## 0. 完成イメージ

| URL | 中身 | 備考 |
|---|---|---|
| `/` (= スラッグ `top` のページ) | **AI 製 HTML** | 既存ページの中身を置き換え |
| `/biz-core/` | AI 製 HTML | **新規作成** |
| `/ai-core/` | AI 製 HTML | **新規作成** |
| `/contact-new/` | AI 製 HTML (Phase 1) | **新規作成** |
| `/company-new/` | AI 製 HTML (Phase 1) | **新規作成** |
| `/contact/` | 既存ページ | 残す (Google Form 等の動線が壊れないように) |
| `/company/` | 既存ページ | 残す |
| `/news/` | 既存ページ | 残す |
| `/privacy-policy/` | 既存ページ | 残す |

→ TOP の AI HTML 内のボタン (「相談する」「Biz Core を見る」等) は **新スラッグ** (`/contact-new/` `/biz-core/` 等) を指す。既存 `/contact/` `/company/` は別途必要なら別の場所からリンク可能。

---

## Phase 0: TOP 置換 (本書の対象)

### Step 1. 画像 5 枚を Xserver にアップロード (10 分)

**目的**: AI HTML が参照する画像を WP 上の固定パスに配置する。

#### 1-1. Xserver サーバーパネルにログイン

- https://www.xserver.ne.jp/login_server.php
- 該当のサーバーアカウントでログイン

#### 1-2. ファイルマネージャを開く

- サーバーパネルのトップから「**ファイルマネージャ**」をクリック
- 別タブでブラウザベースのファイル管理画面が開く

#### 1-3. `/wp-content/uploads/coredriven-html/` フォルダを作成

ナビゲーションパスをたどる:

```
ホーム
└─ <ドメインフォルダ> (例: core-driven.com)
    └─ public_html
        └─ wp-content
            └─ uploads
                └─ [ここで「フォルダ作成」をクリック]
                    └─ coredriven-html  ← 新規作成
```

- 「フォルダ作成」ボタン (画面上部) → 名前 `coredriven-html` を入力 → OK

#### 1-4. 画像 5 枚をアップロード

`coredriven-html` フォルダに入って「**ファイルのアップロード**」ボタン → 以下 5 ファイルを選択:

| ファイル | サイズ | 用途 |
|---|---|---|
| `logo-core-driven.png` | 24 KB | (将来 AI ヘッダーで使用、今は予備) |
| `logo.svg` | 1 KB | (同上) |
| `tanaka.jpg` | 1.3 MB | 田中さん本人写真 (Members) |
| `machida.jpg` | 294 KB | 町田さん写真 (Members) |
| `yoshida.webp` | 46 KB | 吉田さん写真 (Members) |

ローカルファイル位置: `~/Downloads/coredriven_html_inspect/assets/`

#### 1-5. 動作確認 (任意・1 分)

ブラウザで下記 URL を開いて画像が表示されることを確認:

```
https://core-driven.com/wp-content/uploads/coredriven-html/yoshida.webp
https://core-driven.com/wp-content/uploads/coredriven-html/tanaka.jpg
https://core-driven.com/wp-content/uploads/coredriven-html/machida.jpg
```

→ 表示されれば Step 1 完了。

---

### Step 2. 新規ページ 4 つの作成 (10 分)

**目的**: TOP からのリンク先 (`/biz-core/`, `/ai-core/`, `/contact-new/`, `/company-new/`) を空ページとして先に作っておき、Step 4 で TOP を公開した時にリンク切れにしないため。中身は後日 (Phase 1) に AI HTML 化する。

#### 2-1. WP 管理画面 → 「ページ → 新規追加」を 4 回繰り返す

各ページで:
1. タイトル入力
2. 右サイドバー「URL」(または「パーマリンク」) 欄でスラッグを指定
3. **下書き保存** (まだ公開しない、空のままで OK)

| 回 | タイトル | スラッグ | 用途 |
|---|---|---|---|
| 1 | Biz Core | `biz-core` | TOP の「Biz Coreを見る」リンク先 |
| 2 | AI Core | `ai-core` | TOP の「AI Coreを見る」リンク先 |
| 3 | Contact (新版) | `contact-new` | TOP の「相談する」リンク先 (既存 `/contact/` と並走) |
| 4 | Company (新版) | `company-new` | TOP の「メンバー詳細を見る」リンク先 (既存 `/company/` と並走) |

> **重要**: Step 4 で TOP を公開した時にこの 4 ページが下書きでも、URL は有効になっている (admin プレビューで開ける)。**ただし非ログインユーザーには 404** になる可能性があるので、Phase 1 で AI HTML 化したら **公開** に切り替える。
>
> 暫定対応として「内容なし」のまま **公開** してしまっても良い (リンク切れよりはマシ)。本資料は **下書きのまま** を推奨 (公開ページはリンク踏まれた時点で AI HTML 完成版にしたいので Phase 1 まで温存)。

#### 2-2. スラッグが希望どおりに設定されたか確認

「ページ → 固定ページ一覧」で 4 ページ + 既存 5 ページ (company / contact / news / privacy-policy / top) の合計 9 ページが見えること。

> WP は同じスラッグの新規作成を許さない (既存 contact があると `/contact/` で新規作成すると `/contact-2/` 等に自動リネームされる) ので、必ず `contact-new` `company-new` のように指定する。

---

### Step 3. TOP ページの中身を AI HTML に置き換え (15 分)

**目的**: 既存「TOP」固定ページ (スラッグ `/top/`) の中身を AI 製の HTML に丸ごと置換する。

#### 3-1. 「TOP」固定ページの編集画面を開く

- WP 管理画面 → 「ページ → 固定ページ一覧」
- タイトル「**TOP**」を見つけてクリック
- ブロックエディタ画面が開く

#### 3-2. リビジョンの記録 (重要・ロールバック用)

- 編集画面の右サイドバー「ステータス」セクションで「**現在のリビジョンを保存**」を確認
- まだ何も変更してない状態で **「下書き保存」**ボタンを押すとリビジョンが 1 つ作られる
- これで「いつでも今の状態に戻せる」状態になる

#### 3-3. 既存ブロックをすべて削除

- 編集領域内をクリック → `Ctrl+A` (Mac は `Cmd+A`) で全選択
- もう一度 `Ctrl+A` (or `Cmd+A`) で全ブロック選択
- `Backspace` キーで全削除

> 心配なら、削除前に編集領域右上「**︙ オプション**」→「コードエディター」で全ブロックの HTML を Notepad 等にコピー保存。

#### 3-4. 「カスタム HTML」ブロックを追加

- 編集領域中央の「+」(ブロック追加) ボタン → 検索欄に「カスタム HTML」と入力 → 選択
- 空のテキストエリアが現れる

#### 3-5. 貼付 HTML を丸ごとコピペ

- ローカルで `coredriven_top_paste_ready_v2.html` (917 行 / 約 36 KB) をテキストエディタで開く
- 全選択 (`Cmd+A`) → コピー (`Cmd+C`)
- WP の「カスタム HTML」ブロック内に貼り付け (`Cmd+V`)

> **貼付ファイルの場所**: `~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/coredriven_top_paste_ready_v2.html`
> Mac の場合: VS Code / メモ帳 / nvi 何でも良い

#### 3-6. プレビュー確認

- 編集画面右上の「**プレビュー** → 新しいタブでプレビュー」をクリック
- 別タブで TOP のプレビューが開く

##### チェックリスト (順に確認)

- [ ] 画面最上部に **SWELL のヘッダー** (「TOP / Business / Company / News / Contact」) が出る
- [ ] その直下に **AI 製の Hero セクション** (「経営者の熱意を実現する 経営伴走・事業共創パートナー」) が表示される
- [ ] スクロールすると以下のセクションが順に出る:
  - [ ] ROLE (構想整理 / 事業推進 / 仕組み化 の 3 カード)
  - [ ] CHALLENGES (10 個のチェックリスト)
  - [ ] SERVICES (Biz Core / AI Core 2 カード)
  - [ ] STRENGTHS (5 つの強み)
  - [ ] MEMBERS (吉田さん / 町田さん / 田中さん 3 写真)
  - [ ] FINAL CTA (「経営者の熱意を、実現へ進めるために。」)
- [ ] 画面最下部に **SWELL のフッター** が出る
- [ ] 「相談する」ボタンを押すと `/contact-new/` に遷移 (Step 2 で作った下書きページ → Phase 1 で本番化)
- [ ] 「Biz Coreを見る」「AI Coreを見る」も同様に新スラッグへ遷移
- [ ] 画像 (吉田さん / 町田さん / 田中さん) が読み込まれている (DevTools の Network タブで赤行ゼロ)
- [ ] スマホ表示 (DevTools → iPhone 14 シミュレート) でも崩れていない
- [ ] スクロールが滑らか (`scroll-behavior:smooth`)

##### よくある不具合と対策

| 症状 | 原因 | 対策 |
|---|---|---|
| 全部のテキストが中央寄せのまま動かない | SWELL の `<style>` が AI HTML より後に読まれて上書き | 貼付 HTML 末尾の `<style>` 内に `!important` を追加 (5/5 v3 計画 §6 参照) |
| 画像が出ない | `/wp-content/uploads/coredriven-html/` パスに画像なし | Step 1-5 で画像 URL 直叩きで確認、404 ならアップロード位置ミス |
| ヘッダー直下が詰まりすぎ | SWELL header の sticky と AI hero の padding が衝突 | 貼付 HTML の `.hero { padding: 140px 0 120px }` を `padding: 80px 0 60px` 等に縮小 |
| スマホで横スクロール発生 | section 内の絶対配置 (`::before` の円形) がはみ出し | `overflow-x:hidden` を `body` または `.ai-fullhtml-wrap` に追加 |
| 「カスタム HTML」がエラー表示で赤い | HTML 構文エラー (タグの閉じ忘れ等) | 「ブロックの修復を試みる」をクリック、または「コードエディター」で末尾の `</div>` 等を確認 |

#### 3-7. 公開 (= 保存) する

問題が無ければ右上「**更新**」(または「公開」) ボタンを押す。

→ TOP 置換完了！ `https://core-driven.com/` を別タブで開いて本番表示を確認。

---

### Step 4. 動作確認 (5 分)

#### 4-1. 本番 URL での確認

- ログアウト状態 (シークレットウィンドウ等) で `https://core-driven.com/` を開く
- Step 3-6 のチェックリストを再度確認

#### 4-2. SP 実機テスト

- iPhone 等で `https://core-driven.com/` を開く
- ハンバーガーメニューが SWELL のものとして動く (タップで開く)
- ヒーローのテキストが画面に収まっている
- 画像が表示される

#### 4-3. パフォーマンスチェック (任意)

- DevTools → Lighthouse → 「Analyze page load」
- Performance / SEO / Accessibility / Best Practices のスコアを記録
- AI HTML 化前のスコアと比較したい場合は事前に取っておく

---

## Phase 0 完了！ 次にやること

### 田中さんの確認事項
- [ ] TOP の見た目が想定どおり (= AI HTML が SWELL ヘッダー/フッター内で正しく表示)
- [ ] 内部リンク 4 種が新スラッグに飛ぶ
- [ ] 既存 `/contact/` `/company/` は触っていないので元のままアクセス可能
- [ ] 公開してから 24 時間放置して挙動・問い合わせ等に問題ないか様子見

### Phase 1 (5/7 以降): 残り 4 ページの AI HTML 化

田中さんが「Phase 0 OK、Phase 1 進めて」と OK 出したら、AI 側で `biz-core.html` `ai-core.html` `company.html` `contact.html` の 4 ファイルを同じ加工スクリプトで貼付 HTML 化 (各 30 分作業)。

各ページの作業は本書 Step 3 と同じ:
1. `/biz-core/` 下書き編集 → カスタム HTML ブロックに貼付 → 公開
2. `/ai-core/` 同上
3. `/contact-new/` 同上
4. `/company-new/` 同上

→ 全部完了したら、メニュー (グロナビ) を AI HTML に揃った構成に整理。

### Phase 2 (将来): SWELL ヘッダー/フッターを捨てて完全 AI HTML 化

SWELL の枠が AI デザインと違和感あれば、`swell_child` に `page-fullhtml-bare.php` を追加 → 各固定ページのテンプレを「AI Full HTML — Bare」に切替 → AI HTML 独自のヘッダー (Biz Core / AI Core / 会社概要 / お問い合わせ) を活かす構成へ。詳細は v2 戦略レポートを参照。

---

## トラブル時のロールバック

### 軽い問題 (デザイン崩れ等)
- 編集画面右サイドバー「**リビジョン**」 → Step 3-2 で保存した編集前の状態を選択 → 「**このリビジョンを復元**」 → 「更新」

### 重い問題 (画面真っ白等)
- 別タブで `https://core-driven.com/wp-admin/` にアクセスできるか確認
- アクセス可能なら: 上記リビジョン復元
- アクセス不能なら: Xserver ファイルマネージャ → `wp-content/themes/swell_child/` を一時退避 → SWELL 親テーマのみに戻す → 管理画面復活 → リビジョン復元

### 最悪のケース (DB 破損等)
- Xserver の「**自動バックアップ**」(過去 14 日分) からリストア
- サーバーパネル → 「バックアップ」 → 該当日付の DB を復元

---

## 用語集 (WP に慣れていない場合)

| 用語 | 意味 |
|---|---|
| **固定ページ** | URL を持つ通常のページ (TOP / 会社概要 等)。投稿(ブログ記事)とは別 |
| **スラッグ** | URL の末尾部分 (例: `/contact-new/` のスラッグは `contact-new`) |
| **ブロック** | Gutenberg エディタの編集単位 (見出しブロック / 段落ブロック / カスタム HTML ブロック 等) |
| **カスタム HTML ブロック** | 任意の HTML/CSS/JS をそのまま埋め込めるブロック。管理者のみ編集可 (KSES filter 無効化) |
| **リビジョン** | 編集履歴。WP は自動で保存し、何度でも前の状態に戻せる |
| **テンプレート** | 子テーマで PHP ファイルを置けば、固定ページ毎に異なるレイアウトを使える機能 |
| **子テーマ** | 親テーマ (SWELL) のアップデートに巻き込まれずカスタマイズを保持するための仕組み。`wp-content/themes/swell_child/` |
| **wp-admin** | WP 管理画面の URL (`https://core-driven.com/wp-admin/`) |
| **KSES** | WP の HTML サニタイザ。管理者ロールのみ無効化される (= `<script>` 等が通る) |
| **wpautop** | WP が段落を `<p>` で勝手に囲むフィルタ。カスタム HTML ブロック内では無効 |

---

## 参考: 関連成果物

| 種類 | パス | 用途 |
|---|---|---|
| **本書** | `Flow/202605/2026-05-06/0.Other/CoreDriven/wordpress_top_implementation_steps.md` | 田中さん作業手順 (今これ) |
| **貼付 HTML v2** | `Flow/202605/2026-05-06/0.Other/CoreDriven/coredriven_top_paste_ready_v2.html` | Step 3-5 でコピペする中身 |
| 計画書 v3 | `Flow/202605/2026-05-05/0.Other/CoreDriven/wordpress_migration_plan_v3.md` | 全体戦略・Cloudflare/WP-CLI解説 |
| 戦略 v2 | `Flow/202605/2026-05-05/0.Other/CoreDriven/wordpress_replace_strategy_v2.md` | Tier 1〜6 の一般論 |
| 実装キット | `Flow/202605/2026-05-05/0.Other/CoreDriven/wordpress_implementation_kit.md` | 子テーマ雛形・SOP |
| 調査 v1 | `Flow/202605/2026-05-03/0.Other/CoreDriven/wordpress_full_html_mechanism.md` | 5 つの選択肢比較 |
| 元 ZIP | `~/Downloads/Core Driven_20260426.zip` | AI 生成 HTML 原本 |

---

**END OF IMPLEMENTATION STEPS.** Phase 0 開始可能。Step 1 から順に進めてください。
