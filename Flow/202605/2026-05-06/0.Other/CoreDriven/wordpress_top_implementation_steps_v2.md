# BL-0079 — CoreDriven TOP 置換 実装手順書 v2 (現状診断反映版)

**作成日**: 2026-05-06
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft（田中さん作業用）
**前版**: `wordpress_top_implementation_steps.md` (v1) — 「TOP 固定ページに本文ブロックがある」前提で書かれていたため修正

**修正の経緯**:
田中さんから「TOP 編集画面にブロックが無い」と指摘 → 実 HTML を解析した結果、**TOP は本文空** で **SWELL の「メインビジュアル」(大画面画像のみ)** で構成されていることが判明。本書はそれを踏まえた最終手順。

---

## 0. 現状の TOP の構成 (実態)

```
[SWELL ヘッダー: ロゴ + TOP/Business/Company/News/Contact メニュー]
    ↓
[SWELL メインビジュアル: フルスクリーン画像 (PC: 03-scaled.jpg, SP: 04-scaled.jpg)]
    ↑ これが「外観 → カスタマイズ → トップページ → メインビジュアル」から設定されている
    ↑ 固定ページ TOP の本文には何も入っていない (空ブロック状態が正常)
    ↓
[w-frontTop ウィジェットエリア: カスタム HTML ウィジェット (空)]
    ↑ 「外観 → ウィジェット」で配置済だが空
    ↓
[post_content: 固定ページ TOP のブロック本文 (空)]
    ↓
[SWELL フッター]
```

### 現状の問題点 (AI HTML 化前提で見ると)

| 項目 | 現状 | 問題 |
|---|---|---|
| メインビジュアル | フルスクリーン画像 1 枚 | AI HTML には独自の Hero セクション (キャッチコピー + CTA) があるため二重になる |
| ナビメニュー | TOP / Business (#ai/#career/#biz) / Company / News / Contact (Google Form) | AI HTML の想定リンク (Biz Core / AI Core / 会社概要 / お問い合わせ) と不一致 |
| ロゴ | 横組みカラーロゴ PNG (CoreDriven 2024/12 版) | AI HTML 内のロゴ (`logo-core-driven.png` / `logo.svg`) と異なる可能性 |
| Contact リンク | Google Form 直リンク | AI HTML の `/contact-new/` 固定ページ (= 5/6 v1 計画) と不一致 |
| 本文ブロック | 空 | ここに AI HTML を流し込めば良いが、上の MV と並んで表示される |

---

## 1. 戦略判断 (Step 0 → 田中さんに選択してもらう)

### 選択肢 X: メインビジュアルを残す + AI HTML を本文に追加 (最小変更)

```
[SWELL ヘッダー]   ← そのまま
[メインビジュアル]   ← 残す (画像 1 枚)
[AI HTML]          ← 本文ブロックに貼付 (Hero ⇒ Role ⇒ ... ⇒ Final CTA)
[SWELL フッター]   ← そのまま
```

- メリット: 既存の見た目を維持しつつコンテンツが増える、ロールバック容易
- デメリット: メインビジュアル (大画像) と AI HTML の Hero (グラデーション) が**上下で 2 連続のヒーロー**になる → 視覚的に冗長
- 工数: 30 分

### 選択肢 Y: メインビジュアルを消す + AI HTML を本文に貼付 (推奨)

```
[SWELL ヘッダー]   ← そのまま (メニューだけ後で見直し)
[AI HTML]          ← 本文ブロックに貼付 (Hero ⇒ Role ⇒ ... ⇒ Final CTA)
[SWELL フッター]   ← そのまま
```

- メリット: AI HTML が画面トップから始まる、デザイン的にスッキリ、AI HTML が想定どおりの体験
- デメリット: SWELL カスタマイザーの MV 設定を「無効化」する操作が 1 つ増える
- 工数: 35 分
- **推奨**: AI HTML 自体に強力な Hero (キャッチコピー + CTA) があるので、MV を残すと冗長

### 選択肢 Z: 全部 AI HTML 化 (Bare 型 / SWELL の枠を全部消す)

```
[AI HTML 完全版]   ← AI 製ヘッダー + 本文 + AI 製フッター
```

- メリット: 完全に AI 製のデザインになる
- デメリット: SWELL の SEO プラグイン (SEO SIMPLE PACK) が効かない、子テーマに新ファイル追加必要 (FTP/エディタ)、移行リスク高
- 工数: 半日 (子テーマ編集 + 動作検証)

→ **本書は選択肢 Y を採用** として手順を記載 (X / Z への切替も §10 で言及)。

---

## 2. 完成イメージ (選択肢 Y)

| 領域 | 中身 | 元 |
|---|---|---|
| 画面トップ | SWELL ヘッダー (ロゴ + メニュー) | 既存のまま |
| ヒーロー | AI HTML の Hero セクション「経営者の熱意を実現する 経営伴走・事業共創パートナー」 | 貼付 HTML 由来 |
| 事業紹介 | Role / Challenges / Services / Strengths / Members / Final CTA | 貼付 HTML 由来 |
| 画面下部 | SWELL フッター | 既存のまま |

メニュー再編 (§6) は今夜やらず、Phase 1 (5/7 以降) に回しても OK。

---

## 3. Step 1. メインビジュアルを非表示にする (5 分)

WP 管理画面 → **「外観 → カスタマイズ」** をクリック → 左サイドバーで以下をたどる:

```
カスタマイズ
└─ トップページ
    └─ メインビジュアル
```

**設定項目で「メインビジュアルの種類」が現在「画像 1 枚」等になっている** はず。これを **「表示しない」** に変更。

> SWELL のバージョンによって名称が違う場合あり:
> - 「メインビジュアルの種類」→「タイプを選択」→ **「使用しない」「非表示」**
> - or 「カスタマイザー → サイト全体 → トップページ表示設定」内の「メインビジュアル ON/OFF」

設定を変更したら **「公開」** ボタン (画面上部) を押す。

→ ブラウザで `https://core-driven.com/` を開いて、フルスクリーン画像が消えていれば成功。今は SWELL ヘッダー直下が空白の白画面になる。

> **ロールバック**: カスタマイザーの「すべての変更を破棄」or 元の設定値に戻して再公開。

---

## 4. Step 2. 画像 5 枚を Xserver にアップロード (10 分)

v1 計画書 §4 Step 1 と同じ。**Xserver ファイルマネージャ** で:

```
/wp-content/uploads/coredriven-html/
├─ logo-core-driven.png  (24 KB)
├─ logo.svg              (1 KB)
├─ tanaka.jpg            (1.3 MB)
├─ machida.jpg           (294 KB)
└─ yoshida.webp          (46 KB)
```

ローカル位置: `~/Downloads/coredriven_html_inspect/assets/`

確認 URL: https://core-driven.com/wp-content/uploads/coredriven-html/yoshida.webp

---

## 5. Step 3. 新規ページ 4 つの作成 (10 分)

5/6 v1 計画書 Step 2 と同じ。WP 管理画面 → 「ページ → 新規追加」を 4 回:

| タイトル | スラッグ | 状態 |
|---|---|---|
| Biz Core | `biz-core` | 下書き保存 |
| AI Core | `ai-core` | 下書き保存 |
| Contact (新版) | `contact-new` | 下書き保存 |
| Company (新版) | `company-new` | 下書き保存 |

> Phase 1 で AI HTML を流し込んでから公開する想定。今夜は下書きで OK。

---

## 6. Step 4. TOP 固定ページに AI HTML を貼付 (15 分)

### 6-1. 「TOP」固定ページ編集画面を開く

- WP 管理画面 → 「ページ → 固定ページ一覧」 → タイトル「TOP」(page-id-10) をクリック

### 6-2. リビジョン保存 (ロールバック用)

- まだ何もしてない状態で右上「**下書き保存**」を 1 度クリック → リビジョン 1 件作成

### 6-3. 「カスタム HTML」ブロックを追加

- 編集領域は現状空。中央の「+」(ブロック追加) → 検索「カスタム HTML」 → 選択
- 空のテキストエリアが現れる

### 6-4. 貼付 HTML をコピペ

ローカルファイル: `~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/coredriven_top_paste_ready_v2.html`

- テキストエディタ (VS Code 等) で開く → 全選択 (`Cmd+A`) → コピー (`Cmd+C`)
- WP 編集画面の「カスタム HTML」ブロック内に貼付 (`Cmd+V`)

### 6-5. プレビュー → 公開 (= 更新)

- 右上「**プレビュー → 新しいタブでプレビュー**」をクリック
- 別タブで TOP のプレビューが開く
- §7 のチェックリストで動作確認
- OK なら「**更新**」ボタン (= 公開) をクリック

---

## 7. プレビュー確認チェックリスト

- [ ] 画面最上部に **SWELL ヘッダー** (ロゴ + TOP / Business / Company / News / Contact)
- [ ] その直下に **AI HTML の Hero** (大きなキャッチコピー「経営者の熱意を実現する 経営伴走・事業共創パートナー」+ 「相談する」「サービスを見る」ボタン)
- [ ] **メインビジュアルの大画像が出ない** (Step 1 で非表示にしたため)
- [ ] スクロールすると Role → Challenges → Services → Strengths → Members → Final CTA
- [ ] 画像 3 枚 (吉田さん / 町田さん / 田中さん) 表示
- [ ] 「相談する」が `/contact-new/` (まだ下書きなので 404 or 「準備中」表示の可能性 → Step 5 で対応)
- [ ] 「Biz Coreを見る」「AI Coreを見る」「メンバー詳細を見る」も同様
- [ ] 画面最下部に SWELL フッター
- [ ] DevTools コンソールに JS エラーなし

### 既知の懸念

| 症状 | 原因 | 対策 |
|---|---|---|
| 「相談する」を押すと 404 | `/contact-new/` がまだ下書き | (a) 暫定で空のまま公開する、(b) Phase 1 で AI HTML 化してから公開、(c) 一時的に Google Form 直リンク `https://forms.gle/GbRSdeKqWngAqx4WA` に書き換え |
| ヒーロー直下が SWELL CSS で詰まる | SWELL の `.l-mainContent` の padding | 貼付 HTML 末尾の `<style>` で `.ai-fullhtml-wrap section{padding:120px 0}` を `padding:80px 0` に下げる |
| 画像が崩れる | 縦横比 / 親要素の幅制約 | DevTools で要素検証、必要に応じ `<style>` 追加 |

---

## 8. Step 5. (任意・推奨) Google Form リンクを暫定で残す

`/contact-new/` が下書きで空なので、TOP の「相談する」ボタンを押した時にエラーになる懸念があります。Phase 0 公開直後の一時対応として:

### 8-1. 貼付 HTML 内の `/contact-new/` を Google Form リンクに書き換え

田中さん指示があれば AI 側で:
- `coredriven_top_paste_ready_v2.html` の `href="/contact-new/"` を `href="https://forms.gle/GbRSdeKqWngAqx4WA"` に sed 置換した v3 版を生成

または田中さん自身が WP 管理画面の「カスタム HTML」ブロック内のテキストで `Cmd+F` 置換 (4 箇所)。

→ Phase 1 で `/contact-new/` を AI HTML 化したら逆置換して固定ページへ向ける。

---

## 9. Step 6. (任意) ナビメニューの再編 (Phase 1 で実施推奨)

現状メニュー (`外観 → メニュー`) は CoreDriven の旧構造:

```
TOP
Business. (ドロップダウン)
  ├─ Restaurant AI Lab. → /#ai
  ├─ Restaurant Career Lab. → /#career
  └─ 事業開発支援事業 → /#biz
Company → /company/
News → /news/
Contact → forms.gle/GbRSdeKqWngAqx4WA
```

AI HTML の世界観 (Biz Core / AI Core / 会社概要 / お問い合わせ) と一致しないため、Phase 1 完了後に:

```
TOP
Biz Core → /biz-core/
AI Core → /ai-core/
Company → /company-new/   (または /company/ のまま)
News → /news/
Contact → /contact-new/   (または Google Form のまま)
```

に再編予定。WP 管理画面 → 「外観 → メニュー」でドラッグ＆ドロップ操作。

> 今夜の Phase 0 では **触らない** (TOP の挙動と独立)。

---

## 10. 戦略選択肢別の手順差分

### 選択肢 X (MV を残す) を採る場合

- §3 (Step 1) を **スキップ**
- それ以外は同じ
- ※ 結果として MV 大画像 + AI Hero の二段構成になる

### 選択肢 Z (Bare 型 / SWELL の枠も消す) を採る場合

- §3 (Step 1) と §6 (Step 4) を別ルートに変更
- swell_child に `page-fullhtml-bare.php` 追加 (5/5 v2 戦略 §6.4 のコード)
- 「外観 → テーマファイルエディタ」で swell_child を選択 → 新規ファイル作成
- TOP 固定ページのテンプレートを「AI Full HTML — Bare」に変更
- 貼付 HTML を AI HTML 完全版 (head + body 全部、`injectHeaderFooter` も残す) に置換
- 工数: 半日

→ 5/7 以降に検討推奨。

---

## 11. 田中さんに確認したい (新規)

| ID | 質問 |
|---|---|
| **Q-M** | 戦略選択は X (MV 残す) / **Y (MV 消す・推奨)** / Z (Bare 完全置換) のどれか? |
| **Q-N** | 「相談する」リンクは Phase 0 の暫定対応として **Google Form 直リンク**で逃がすか? それとも `/contact-new/` を空のまま公開するか? それとも Phase 1 まで TOP 公開を待つか? |
| **Q-O** | 既存の **メニュー (外観→メニュー)** を再編するタイミング: (a) Phase 0 と同時 / (b) Phase 1 完了後 / (c) Phase 2 で AI ヘッダーに完全移行する時 |

---

## 12. ロールバック (TOP 公開後に問題が出たら)

| 状況 | 対処 |
|---|---|
| 表示崩れだけ | 固定ページ編集 → リビジョン → Step 6-2 の保存ポイントに戻す → 更新 |
| メインビジュアルを復活したい | カスタマイザー → メインビジュアル → 種類を元 (画像) に戻す → 公開 |
| カスタム HTML が動かない | ブロック削除 → 空ページに戻す (= 元の状態) |
| 大規模に壊れた | Xserver の自動バックアップ (14 日分) から DB リストア |

---

## 13. 関連成果物

| 種類 | パス |
|---|---|
| **本書 v2** | `Flow/202605/2026-05-06/0.Other/CoreDriven/wordpress_top_implementation_steps_v2.md` |
| 旧 v1 (参照) | `Flow/202605/2026-05-06/0.Other/CoreDriven/wordpress_top_implementation_steps.md` (needs_revision) |
| 貼付 HTML | `Flow/202605/2026-05-06/0.Other/CoreDriven/coredriven_top_paste_ready_v2.html` |
| 計画書 v3 | `Flow/202605/2026-05-05/0.Other/CoreDriven/wordpress_migration_plan_v3.md` |
| 戦略 v2 | `Flow/202605/2026-05-05/0.Other/CoreDriven/wordpress_replace_strategy_v2.md` |

---

**END OF v2 STEPS.** Q-M (戦略選択) の回答をもらえれば実行開始可能。デフォルト推奨は Y (MV 消す + 本文に AI HTML)。
