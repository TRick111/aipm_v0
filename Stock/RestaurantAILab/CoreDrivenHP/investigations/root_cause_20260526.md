# レイアウト崩れ — 原因分析 (2026-05-26)

## 結論

**ローカル HTML の CSS は本番にも `<style>` ブロックで埋め込まれているが、SWELL テーマの CSS に specificity（詳細度）で負けて適用されていない。**

加えて、SWELL の `.l-container` / `.post_content` ラッパーが余計な左右パディングを足している。

## 計測結果（desktop 1440px）

| 計測対象 | ローカル HTML | 本番 (WP) | 差分 |
|---|---|---|---|
| `<body>` 幅 | 1440 | 1440 | OK |
| `#content.l-content.l-container` (SWELL) | なし | width 1440 / padding 48px 両側 | **不要な内側余白** |
| ヒーロー h2「熱意を、構想で〜」`font-size` | 48px / weight 800 | **22.4px / weight 700** | SWELL `.post_content h2 { font-size:1.2em }` に上書きされた |
| ヒーロー h2 計算上の縦サイズ | 113px | 62px | フォント差により縮小 |
| h1「経営者の熱意を実現する」`font-size` | (ローカル別ファイルだが) clamp 40–72px | 72px | 一見一致だが.l-container 影響で位置ずれ |
| `.container` の外側マージン | 100px 左右（auto） | 36px 左右 | `.l-container` 余白でセンタリング範囲が縮小 |
| `card01` (`.container`) パディング | 32px | 32px | OK |

スクショ: `desktop_local.png` vs `desktop_live.png`（同フォルダ内）

## CSS 優先度の正体

SWELL `main.css` に以下のルールがある:

```css
.post_content h2 { font-size: 1.2em; line-height: 1.4; margin: 4em 0 2em; }
.post_content h3 { font-size: 1.1em; font-weight: 700; margin: 3em 0 2em; }
.post_content h4 { font-size: 1.05em; margin: 3em 0 1.5em; }
.post_content > * { margin-bottom: var(--swl-block-margin, 2em); }
.l-container { padding-left: var(--swl-pad_container, 0); padding-right: var(--swl-pad_container, 0); }
.l-mainContent__inner > .post_content { margin: 4em 0; padding: 0 var(--swl-pad_post_content, 0); }
```

ローカル HTML の `<style>` 側は:

```css
h2 { font-size: clamp(26px, 3.6vw, 48px); ... }   ← (0,0,1) → .post_content h2 (0,1,1) に敗北
h3 { font-size: clamp(20px, 2vw, 26px); ... }      ← 同様に敗北
```

結果、SWELL の汎用 post_content 用ルールが全て勝ち、デザインシステムの type scale が無効化されている。
さらに `.post_content > *` の `margin-bottom: 2em` がカード周りに不要余白を生み出している。

## 修正方針

ローカル `<style>` ブロックの先頭に、以下の **SWELL 上書きリセット** を追加する。

```css
/* === SWELL overrides for CoreDriven page === */
.l-content.l-container { padding-left: 0; padding-right: 0; max-width: none; }
.l-mainContent__inner > .post_content { margin: 0; padding: 0; }
.post_content { line-height: 1.7; margin: 0; padding: 0; max-width: none; }
.post_content > * { margin-bottom: 0; clear: none; }

/* Type scale — re-instate local design system */
.post_content h1 { font-size: clamp(40px, 6vw, 72px); line-height: 1.1; letter-spacing: -.035em; font-weight: 800; margin: 0; }
.post_content h2 { font-size: clamp(26px, 3.6vw, 48px); line-height: 1.18; letter-spacing: -.025em; font-weight: 800; margin: 0; }
.post_content h3 { font-size: clamp(20px, 2vw, 26px); line-height: 1.3; font-weight: 800; margin: 0; }
.post_content h4 { font-size: 18px; font-weight: 800; margin: 0; }
.post_content p { margin: 0; }
.post_content ul, .post_content ol { padding-left: 0; }
.post_content li { margin: 0; line-height: inherit; }

/* Section heads — restore wrap behavior */
.post_content .section-head h2 { white-space: pre-wrap; }
```

優先度: 追加分は `.post_content` プレフィックスで SWELL と同じ specificity (0,1,1) になり、**ソース順で後に出る body 内 `<style>` のほうが勝つ**ため、`!important` 不要。

## 影響範囲

- 同様に `wp:html` ブロックで貼り付けた他ページ（Company / Biz Core / AI Core / Contact）も同じ問題が出ているはず → 各ページに同じリセットを適用
- 通常の SWELL ブロックを使った投稿・他固定ページには影響しない（`<style>` 内なので投稿に閉じる）

## ロールバック

各ページの `post_content` を `wp post update <id> --post_content=...` で復元可能。  
バックアップを `backup/wp_20260526_<HHMMSS>/page_<id>_before.html` として取得してから適用する。
