# BL-0079 — Phase 2 (1/N) ヘッダー / フッター メニュー再編 ログ

**作業日**: 2026-05-06
**作業者**: AI (mt cockpit-task ab2f1e5a) / SSH + WP-CLI 経由
**実行根拠**: 田中さん指示「ヘッダーの修正」+ 案 A 承認 (5/6)
**前提**: Phase 0 / Phase 1 完了 (`05_phase0_execution_log.md` / `06_phase1_execution_log.md`)

---

## 0. 経緯

田中さんから「ヘッダーの修正もできる？」→ 案 A/B/C を提示 → 「A」採用。

案 A: AI HTML 構造に統一
- グローバルナビ: TOP / Biz Core / AI Core / Company / News / Contact
- フッター: TOP / Biz Core / AI Core / Company / News / Contact / Privacy Policy

---

## 1. バックアップ ✅

```
~/backups/coredriven/20260506_phase2_menu/
├── db_dump_pre_menu.sql   (3,720,084 bytes)
├── gnav_before.json       (984 bytes)
└── footer_before.json     (543 bytes)
```

before JSON にメニュー全構造保存 (json で wp menu item list の出力を保管 → 復元時は wp menu item add-* で再構築)。

---

## 2. グローバルナビ再編 (term_id=6) ✅

### 2.1 削除した項目 (6 件)
| db_id | type | 旧 title | 旧 URL |
|---|---|---|---|
| 103 | custom | Business. (dropdown 親) | /#ai |
| 85 | custom | Restaurant AI Lab. | /#ai |
| 86 | custom | Restaurant Career Lab. | /#career |
| 84 | custom | 事業開発支援事業 | /#biz |
| 668 | custom | Contact | https://forms.gle/... |
| 67 | post_type | Company (旧 ID=53) | /company/ |

### 2.2 追加した項目 (4 件)
| 新 db_id | post_id | title | URL | position |
|---|---|---|---|:-:|
| 725 | 704 | Biz Core | /biz-core/ | 2 |
| 726 | 706 | AI Core | /ai-core/ | 3 |
| 727 | 710 | Company | /company-new/ | 4 |
| 728 | 708 | Contact | /contact-new/ | 7 (1度 update) |

### 2.3 順序調整
- News (db_id=68) を position=6 に
- Contact (db_id=728) を position=7 に

### 2.4 最終状態
```
TOP (72)        → /
Biz Core (725)  → /biz-core/
AI Core (726)   → /ai-core/
Company (727)   → /company-new/
News (68)       → /news/
Contact (728)   → /contact-new/
```

---

## 3. フッター再編 (term_id=117) ✅

### 3.1 削除した項目 (2 件)
- 658: Company (旧 /company/)
- 670: Contact (Google Form)

### 3.2 追加した項目 (4 件)
- 729: Biz Core → /biz-core/ (position=2)
- 730: AI Core → /ai-core/ (position=3)
- 731: Company → /company-new/ (position=4)
- 732: Contact → /contact-new/ (position=6)

### 3.3 順序調整
- News (657) を position=5
- Privacy Policy (660) を position=7

### 3.4 最終状態
```
TOP (656)              → /
Biz Core (729)         → /biz-core/
AI Core (730)          → /ai-core/
Company (731)          → /company-new/
News (657)             → /news/
Contact (732)          → /contact-new/
Privacy Policy (660)   → /privacy-policy/
```

---

## 4. キャッシュ問題 → 対処 ✅

### 4.1 問題発生
WP-CLI でメニュー DB 更新後、Playwright で確認 → **ヘッダーは古いまま** (Business.メニューが残存) / **フッターは新しい状態**。

### 4.2 原因特定
SWELL の **wp_nav_menu フラグメントキャッシュ** がヘッダー出力をキャッシュしていた。footer は別キャッシュキー (or 未キャッシュ) のため即時反映。

### 4.3 対処
```bash
ssh xserver 'wp cache flush'
# → Success: The cache was flushed.
ssh xserver 'wp transient delete --all'
# → Success: 18 transients deleted from the database.
```

### 4.4 再確認 ✅
ハードリロード (?nocache パラメータ付き) でヘッダーが新メニューに切替確認:
```js
[
  {text: "TOP", href: "https://core-driven.com/"},
  {text: "Biz Core", href: "https://core-driven.com/biz-core/"},
  {text: "AI Core", href: "https://core-driven.com/ai-core/"},
  {text: "Company", href: "https://core-driven.com/company-new/"},
  {text: "News", href: "https://core-driven.com/news/"},
  {text: "Contact", href: "https://core-driven.com/contact-new/"}
]
```

---

## 5. Playwright 検証 ✅

### 5.1 PC (1280×900)
- スクショ: `screenshots/phase2_pc_top_header_after.png`
- 表示: ロゴ + 6 項目メニュー (TOP / Biz Core / AI Core / Company / News / Contact) ✅

### 5.2 SP (390×844 / iPhone 14 / ハンバーガー展開)
- スクショ: `screenshots/phase2_sp_menu_open.png`
- 表示: ハンバーガークリック → 6 項目縦並び (TOP / Biz Core / AI Core / Company / News / Contact) ✅

### 5.3 Footer も連動確認
全 5 ページ (TOP / biz-core / ai-core / contact-new / company-new) のフッターも新メニューに切替 ✅

---

## 6. ロールバック手順

万が一メニューを元に戻す場合:

```bash
# DB 全体復元 (一番確実)
ssh xserver 'wp db import ~/backups/coredriven/20260506_phase2_menu/db_dump_pre_menu.sql --path=...'

# または gnav_before.json / footer_before.json から再構築
```

---

## 7. Phase 2 残課題

| 課題 | 内容 | 優先度 |
|---|---|:-:|
| **C-2** | `/contact-new/` フォーム送信ハンドラ実装 (Google Form リンク化 / プラグイン / 自前) | 高 |
| C-3 | SWELL main.js の `#main_visual` 関連エラー整理 | 中 |
| C-4 | 旧 CSS (`.custom-message__*` `.biz__*`) の削除可否判断 | 低 |
| C-5 | 既存 `/contact/` (draft) / `/company/` (publish + 独自メディアセクション) の整理 | 低 |
| C-6 | (オプション) ヘッダー CTA「相談する」ボタン追加 (SWELL カスタマイザー) | 中 |

---

## 完了サマリ

**完了**: 2026-05-06 21:23 JST
**所要**: 約 10 分 (バックアップ → 削除 → 追加 → キャッシュクリア → 確認)
**変更**: グローバルナビ 6 削除 + 4 追加 / フッター 2 削除 + 4 追加 / 計 16 件
**バックアップ**: DB 全体 + JSON 2 種 (リモート保管)

田中さん視覚確認: シークレットウィンドウで `https://core-driven.com/` を開いて、ヘッダーが「TOP / Biz Core / AI Core / Company / News / Contact」に変わっていることを確認。OK なら Phase 2 残課題に進むか判断。
