# BL-0079 — Phase 1 実行ログ

**作業日**: 2026-05-06
**作業者**: AI (mt cockpit-task ab2f1e5a) / SSH 経由
**実行根拠**: `04_migration_plan.md §3 (Phase 1)` / 田中さん承認 (5/6 「A=Phase 1 で OK」)
**対象**: 残 4 ページ (biz-core / ai-core / contact-new / company-new) を AI HTML 化 + 公開
**前提**: Phase 0 で TOP 完了 (`05_phase0_execution_log.md` 参照)

---

## Step 1.0 — 事前準備 ✅

### 1.0.1 各ページの構造調査

| ファイル | 行 | サイズ | 主要セクション | 画像 | 内部リンク | members 親 class |
|---|---|---|---|---|---|---|
| biz-core.html | 391 | 20.6 KB | page-hero / value / members(3人) / process / final-cta | 3人写真 | contact.html | **`.deliver-card`** |
| ai-core.html | 733 | 40 KB | page-hero / concept / cases / pricing / final-cta | なし | contact.html | (members なし) |
| company.html | 349 | 18.2 KB | page-hero / mvv / members(3人) / company / final-cta | 3人写真 | contact.html | **`.member-block`** |
| contact.html | 227 | 9.8 KB | page-hero / examples / form | なし | (なし) | (members なし) |

→ **各ページで member 親 class が異なる** (TOP=`member-card` / biz-core=`deliver-card` / company=`member-block`) → 田中ルールのセレクタを汎用化する必要があり。

### 1.0.2 共通加工スクリプト
`/tmp/transform_ai_html.py` を作成。各 HTML に対し下記を一括適用:

1. `<head>` 内の `<style>` 抽出 + `assets/styles.css` 結合
2. `<body>` 内の `<script src="assets/site.js">` + `injectHeaderFooter()` 削除
3. 内部リンク変換: `contact.html` → `/contact-new/`, `biz-core.html` → `/biz-core/` 等
4. 画像パス変換: `assets/*` → `/wp-content/uploads/coredriven-html/*`
5. `<style>` 内連続改行圧縮 (wpautop 対策)
6. `.avatar img[alt="田中利空"]{object-position:center 22%}` 注入 (汎用セレクタ)
7. 全体を `<!-- wp:html -->` でラップ (wpautop 完全回避)

---

## Step 1.1 — Phase 1 バックアップ ✅

```bash
ssh xserver 'mkdir -p ~/backups/coredriven/20260506_phase1'
ssh xserver 'wp db export ~/backups/coredriven/20260506_phase1/db_dump_pre_phase1.sql'
# 各ページの post_content + status を保存
for id in 704 706 708 710; do
  ssh xserver "wp post get $id --field=post_content > ~/backups/.../post_content_$id.html"
  ssh xserver "wp post get $id --field=post_status > ~/backups/.../post_status_$id.txt"
done
```

**結果**:
- DB ダンプ: 3,256,183 bytes ✅
- 4 ページの旧 post_content (各 3 bytes / = 空) + status (3 件 draft, 1 件 publish=708) ✅

---

## Step 1.2 — 4 ページ生成 + 投入 (初回) ✅

### 1.2.1 4 ファイル生成

| ファイル | サイズ | 行 |
|---|---|---|
| coredriven_biz-core_paste_ready.html | 34,473 | 781 |
| coredriven_ai-core_paste_ready.html | 53,818 | 1,116 |
| coredriven_contact-new_paste_ready.html | 23,517 | 619 |
| coredriven_company-new_paste_ready.html | 32,083 | 740 |

### 1.2.2 SCP + WP-CLI 投入

```bash
scp -P 10022 *_paste_ready.html my0126@...:/tmp/
ssh xserver 'wp post update <ID> --post_content="$(cat /tmp/...)" --post_status=publish'
```

**結果**:
- ID=704 (biz-core): publish / 34,475 bytes ✅
- ID=706 (ai-core): publish / 53,820 bytes ✅
- ID=708 (contact-new): publish / 23,519 bytes ✅
- ID=710 (company-new): publish / 32,085 bytes ✅
- HTTP 200 全 4 ページ ✅

---

## Step 1.3 — Playwright 視覚確認 (PC) ✅

PC (1280×900) で 4 ページの fullPage スクリーンショット取得:

| ページ | スクショ | 観察 |
|---|---|:-:|
| `/biz-core/` | `phase1_pc_biz-core_full.png` | page-hero / value / members(3人) / process / final-cta 全て正常 ✅ |
| `/ai-core/` | `phase1_pc_ai-core_full.png` | page-hero / concept / cases / pricing / final-cta 全て正常 ✅ |
| `/contact-new/` | `phase1_pc_contact-new_full.png` | page-hero / examples (8 個) / フォーム (相談領域 / 会社情報 / 課題 / 送信ボタン) ✅ |
| `/company-new/` | `phase1_pc_company-new_full.png` | page-hero / mvv / 3 members(member-block) / 会社情報 / final-cta ✅ |

CSS 検証 (browser_evaluate):
- `--max=1240px` `--grad-deep=linear-gradient(...)` 全ページ OK
- `.page-hero` padding/background OK
- セクション数: biz-core=7, ai-core=10, contact-new=3, company-new=5

---

## Step 1.4 — 田中ルール bug 発見 → 修正 (v2) ✅

### 1.4.1 SP で company-new の田中画像確認 → ★ NG ★
SP (390×844) で `/company-new/#members` を開いて田中カード確認 → **田中ルール `objectPosition: 50% 22%` が適用されていなかった** (デフォルト `50% 50%`)

### 1.4.2 原因特定
TOP (Phase 0 v4) の田中ルールは `.member-card .avatar img[alt="田中利空"]` というセレクタ。しかし:
- TOP: `.member-card` 構造 ✅ (Phase 0 v4 で対応済)
- biz-core: **`.deliver-card`** 構造 ❌
- company-new: **`.member-block`** 構造 ❌

→ `.member-card` 限定セレクタでは他 2 ページでヒットしない。

### 1.4.3 修正: セレクタ汎用化

```css
/* 旧 */
.member-card .avatar img[alt="田中利空"]{object-position:center 22%}
/* 新 */
.avatar img[alt="田中利空"]{object-position:center 22%}
```

`/tmp/transform_ai_html.py` の `TANAKA_FIX` 定数を更新 + TOP v5 を別途生成。

### 1.4.4 5 ページ全部再投入

| ID | スラッグ | 旧 size | 新 size | status |
|---|---|---|---|:-:|
| 10 | top | 36,385 (v4) | 36,372 (v5) | publish ✅ |
| 704 | biz-core | 34,475 (v1) | 34,462 (v2) | publish ✅ |
| 706 | ai-core | 53,820 (v1) | 53,807 (v2) | publish ✅ |
| 708 | contact-new | 23,519 (v1) | 23,506 (v2) | publish ✅ |
| 710 | company-new | 32,085 (v1) | 32,072 (v2) | publish ✅ |

### 1.4.5 SP 再検証 (company-new) ✅
```js
.avatar img[alt="田中利空"]:
  objectPosition: "50% 22%"   ← 適用 OK ✅
  parent: "member-block"       ← 別構造でも OK ✅
  rendered: 302×380 (縦長フレーム)
```

スクリーンショット `phase1_sp_company-new_tanaka_v3.png`: 田中の顔全体 (頭・目・鼻・口・首・スーツ上半身) が綺麗に表示 ✅

---

## Phase 1 サマリ ✅

**完了**: 2026-05-06 15:44 JST
**全所要**: 約 1 時間 25 分 (14:21 Phase 0 完了 → 15:44 Phase 1 完了)

### 達成事項
- ✅ 4 ページ (biz-core / ai-core / contact-new / company-new) AI HTML 化 + publish
- ✅ TOP (v5) 含めて 5 ページが田中ルール汎用セレクタで統一
- ✅ 各ページのテンプレ・SEO・パフォーマンスは SWELL のまま維持
- ✅ ロールバック: Phase 1 用バックアップ取得済 (DB + 各 post_content)

### 学び (Phase 2 以降に活かす)
1. **AI HTML の構造はページごとに違う class 命名がある** — `member-card` / `deliver-card` / `member-block` 等。CSS セレクタは機能 (`.avatar img[alt="..."]`) に紐付けて広く効くようにする
2. **wpautop 対策の `<!-- wp:html -->` ラップ + style 連続改行圧縮はテンプレ化済** — 今後の AI HTML 投入時はこのパターンを踏襲
3. **画像パスを `/wp-content/uploads/coredriven-html/` に統一する規約** が新規生成 HTML との互換性を保証

### 既知の軽微な未対応
1. SWELL main.js が削除済 `#main_visual` を探すコンソールエラー 3 件 (各ページで発生、表示影響なし) → Phase 2 で main.js 整理検討
2. ナビメニューが旧構造 (TOP / Business[#ai/#career/#biz] / Company / News / Contact[Google Form]) のまま → Phase 2 でメニュー再編
3. 既存 `/contact/` (ID=55, draft) と `/company/` (ID=53, publish) が並走したまま → Phase 2 で統合検討
4. AI HTML の Contact フォーム (`<form>`) は送信ハンドラ (site.js) を削除しているため未動作 → Phase 2 で送信先実装 (Google Form / メール送信プラグイン)

### Phase 2 (クリーンアップ) 着手判断待ち
田中さんの承認が必要:
- ナビメニューの再編
- 旧 CSS (`.custom-message__*`, `.biz__*`) 削除可否判断
- フォーム送信実装 (Google Form リンク化 / プラグイン導入 / 自前実装)
- main.js の `#main_visual` 関連処理整理
- 既存 `/contact/` `/company/` ページ整理