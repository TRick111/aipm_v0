# BL-0079 — CoreDriven HP 移行計画書

**作成日**: 2026-05-06
**作成者**: AI (mt cockpit-task ab2f1e5a)
**ステータス**: Draft (田中さんの承認後に Phase 0 実行)
**前提ドキュメント**:
- `01_requirements.md` (要件)
- `02_current_architecture.md` (現状)
- `03_future_architecture.md` (移行後)

---

## 0. このドキュメントの目的

Phase 0 (TOP 置換) と Phase 1 (残 4 ページ AI HTML 化) を実施する際の **作業手順 / バックアップ取得 / ロールバック手順** を時系列で完全に記載する。AI が SSH 経由で実行することを前提とするが、田中さんが手作業で進める際にも参照できる粒度で書く。

---

## 1. 全体スケジュール

| Phase | 期間 | 実行者 | 田中さんの作業 |
|---|---|---|---|
| **Phase 0** | 本日 (2026-05-06) | AI (SSH 経由) | 開始承認 + 完了確認 |
| **Phase 1** | 5/7〜5/8 | AI (SSH 経由) | 各ページ完成時の確認 |
| **Phase 2** | 5/9 以降 | AI + 田中さん協議 | クリーンアップ方針の判断 |

---

## 2. Phase 0: TOP 置換 (所要 30〜45 分)

### 2.1 目的
- TOP (`https://core-driven.com/`) で AI HTML が表示されるようにする
- ヘッダー / フッター / メニューは SWELL のまま維持
- 任意のステップでロールバック可能な状態を保つ

### 2.2 前提条件 (Pre-flight Check)
| 項目 | 確認 | 確認方法 |
|---|---|---|
| SSH 接続が可能 | ✅ 確認済 | `ssh -p 10022 my0126@my0126.xsrv.jp echo OK` |
| WP-CLI が動作 (PHP 8.3) | ✅ 確認済 | `/opt/php-8.3.30/bin/php /usr/bin/wp core version --path=...` |
| TOP 固定ページが ID=10 / publish | ✅ 確認済 | `wp post get 10 --field=post_status` = publish |
| ローカルに AI HTML がある | ✅ 確認済 | `~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/coredriven_top_paste_ready_v2.html` |
| ローカルに画像 5 枚がある | ✅ 確認済 | `~/Downloads/coredriven_html_inspect/assets/` |
| 田中さんの承認 | ⚠️ Phase 0 開始前に取得 | チャットで「Phase 0 進めて OK」 |

### 2.3 作業ステップ

#### Step 0.0 — リハーサル (作業時間に含めない)
本番前に、ローカルで以下を確認:
- [ ] 全バックアップコマンドが動くこと
- [ ] tmp/front.php 最小化版に PHP 構文エラーが無いこと (`php -l` で検証)
- [ ] AI HTML が WP-CLI 経由で post_content に投入できること

#### Step 0.1 — リモートでバックアップ取得 (5 分)

下記を AI が SSH 経由で実行:

```bash
# 1. リモートのバックアップディレクトリ作成
ssh xserver 'mkdir -p ~/backups/coredriven/20260506_phase0'

# 2. tmp/front.php の物理バックアップ
ssh xserver '
TS=$(date +%Y%m%d_%H%M%S)
cd ~/core-driven.com/public_html/wp-content/themes/swell_child
cp tmp/front.php tmp/front.php.backup_$TS
cp tmp/front.php ~/backups/coredriven/20260506_phase0/tmp_front.php.original
echo "Backup: tmp/front.php.backup_$TS"
'

# 3. swell_child フォルダ全体のスナップショット (50 KB 程度)
ssh xserver '
cd ~/core-driven.com/public_html/wp-content/themes
tar czf ~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz swell_child
ls -la ~/backups/coredriven/20260506_phase0/
'

# 4. WP DB ダンプ取得
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
cd ~/core-driven.com/public_html
$PHP /usr/bin/wp db export ~/backups/coredriven/20260506_phase0/db_dump.sql --add-drop-table 2>/dev/null
ls -la ~/backups/coredriven/20260506_phase0/db_dump.sql
'

# 5. TOP (ID=10) の現状 post_content をローカルに保存
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
$PHP /usr/bin/wp post get 10 --field=post_content --path=~/core-driven.com/public_html 2>/dev/null
' > ~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/backup_top_post_content_20260506.html

# 6. リモートからローカルにバックアップを scp で取り寄せ (二重保管)
scp -P 10022 my0126@my0126.xsrv.jp:~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz \
    ~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/backup_swell_child_phase0.tar.gz
```

**完了基準**: 下記 5 ファイルが揃っていること
- リモート: `~/backups/coredriven/20260506_phase0/tmp_front.php.original`
- リモート: `~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz`
- リモート: `~/backups/coredriven/20260506_phase0/db_dump.sql`
- ローカル: `backup_top_post_content_20260506.html`
- ローカル: `backup_swell_child_phase0.tar.gz`

#### Step 0.2 — 画像 5 枚のアップロード (5 分)

```bash
# リモートに /wp-content/uploads/coredriven-html/ を作成
ssh xserver 'mkdir -p ~/core-driven.com/public_html/wp-content/uploads/coredriven-html'

# ローカルから scp でアップロード
cd ~/Downloads/coredriven_html_inspect/assets
scp -P 10022 logo-core-driven.png logo.svg tanaka.jpg machida.jpg yoshida.webp \
    my0126@my0126.xsrv.jp:~/core-driven.com/public_html/wp-content/uploads/coredriven-html/

# パーミッション設定
ssh xserver '
cd ~/core-driven.com/public_html/wp-content/uploads/coredriven-html/
chmod 644 *.png *.svg *.jpg *.webp
ls -la
'
```

**動作確認**:
```
curl -sI https://core-driven.com/wp-content/uploads/coredriven-html/yoshida.webp | head -1
# → HTTP/2 200 を期待
```

#### Step 0.3 — `/contact-new/` を一時公開 (1 分)

TOP の「相談する」ボタンが 404 にならないよう、リンク先 `/contact-new/` を一時的に「公開 (中身空)」状態にする:

```bash
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
DOC=~/core-driven.com/public_html
$PHP /usr/bin/wp post update 708 --post_status=publish --path=$DOC 2>/dev/null
$PHP /usr/bin/wp post get 708 --field=post_status --path=$DOC 2>/dev/null
'
```

→ Phase 1 で正式な AI HTML を貼り、本番運用に入る。

#### Step 0.4 — `tmp/front.php` を最小化 (3 分)

新しい中身をローカルで作成 → SSH 経由でリモートに転送:

```bash
# ローカルで最小化版 PHP を作成
cat > /tmp/tmp_front_minimal.php <<'EOF'
<?php
/**
 * tmp/front.php (最小化版 — BL-0079 / Phase 0)
 * 旧: 112KB の独自直書き HTML (Hero + biz セクション) ※ swell_child/tmp/front.php.backup_* に保存
 * 新: TOP 固定ページ (ID=10) の post_content を出力するだけのプロキシ
 *      → 田中さんが WP 管理画面 (固定ページ編集) で更新できる状態を実現
 *
 * @package swell_child
 * @since   2026-05-06
 */
if ( ! defined( 'ABSPATH' ) ) exit;
?>
<main id="main_content" class="l-mainContent l-article">
    <div class="l-mainContent__inner" data-clarity-region="article">
        <div class="<?= esc_attr( apply_filters( 'swell_post_content_class', 'post_content' ) ) ?>">
            <?php
            while ( have_posts() ) :
                the_post();
                the_content();
            endwhile;
            ?>
        </div>
    </div>
</main>
EOF

# 構文チェック (ローカル PHP で)
php -l /tmp/tmp_front_minimal.php
# → "No syntax errors detected" を確認

# リモートに転送
scp -P 10022 /tmp/tmp_front_minimal.php \
    my0126@my0126.xsrv.jp:~/core-driven.com/public_html/wp-content/themes/swell_child/tmp/front.php.new

# リモートで構文チェック (PHP 8.3 で)
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
$PHP -l ~/core-driven.com/public_html/wp-content/themes/swell_child/tmp/front.php.new
'

# 構文 OK なら本番ファイルに置換 (アトミック)
ssh xserver '
cd ~/core-driven.com/public_html/wp-content/themes/swell_child/tmp
mv front.php.new front.php
ls -la front.php*
'
```

**動作確認**:
```
curl -sI https://core-driven.com/ | head -1
# → HTTP/2 200 を期待 (500 が出たら即ロールバック §6.1.A)
```

#### Step 0.5 — TOP の post_content に AI HTML を投入 (3 分)

```bash
# ローカルから WP-CLI でリモートに post_content を更新
LOCAL=~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/coredriven_top_paste_ready_v2.html

# 一旦リモートに HTML をコピー (改行・特殊文字対策)
scp -P 10022 $LOCAL my0126@my0126.xsrv.jp:/tmp/coredriven_top_paste_v2.html

# WP-CLI で post update (リモートで実行)
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
DOC=~/core-driven.com/public_html
$PHP /usr/bin/wp post update 10 --post_content="$(cat /tmp/coredriven_top_paste_v2.html)" --path=$DOC 2>/dev/null
echo "Updated TOP post_content. Length:"
$PHP /usr/bin/wp post get 10 --field=post_content --path=$DOC 2>/dev/null | wc -c
'
```

**動作確認**:
```
# サイトをハードリロード相当で取得
curl -sL "https://core-driven.com/?nocache=$(date +%s)" | grep -c "経営者の熱意を実現する"
# → 1 以上を期待 (= AI HTML の Hero テキストが出力されている)
```

#### Step 0.6 — 田中さんが視覚確認 (5 分) ★ 唯一の手作業

田中さん:
1. **シークレットウィンドウ** で `https://core-driven.com/` を開く
2. 下記チェックリスト (5.1 Phase 0 完了条件) で全項目 OK を確認
3. NG があれば AI に伝える → §6.1 のロールバック判断

---

## 3. Phase 1: 残 4 ページ AI HTML 化 (5/7〜5/8 / 各ページ 30 分)

### 3.1 対象ページ
- `/biz-core/` (ID=704) ← 元 `biz-core.html` を使用
- `/ai-core/` (ID=706) ← 元 `ai-core.html` を使用
- `/contact-new/` (ID=708) ← 元 `contact.html` を使用
- `/company-new/` (ID=710) ← 元 `company.html` を使用

### 3.2 各ページの作業フロー (繰り返し)

#### Step 1.X — ページ X の AI HTML 化

```bash
# 1. AI HTML を加工 (ローカル)
#    - 内部リンク書換 (.html → /XX/)
#    - 画像パス書換 (assets/ → /wp-content/uploads/coredriven-html/)
#    - injectHeaderFooter スクリプト削除
#    - <head> 内 <style> + assets/styles.css をインライン化

# 2. 加工済 HTML を Flow に保存
#    coredriven_<slug>_paste_ready.html

# 3. リモートに転送 + post_content 更新
scp -P 10022 coredriven_<slug>_paste_ready.html \
    my0126@my0126.xsrv.jp:/tmp/

ssh xserver '
PHP=/opt/php-8.3.30/bin/php
DOC=~/core-driven.com/public_html
$PHP /usr/bin/wp post update <ID> --post_content="$(cat /tmp/coredriven_<slug>_paste_ready.html)" --post_status=publish --path=$DOC 2>/dev/null
'

# 4. プレビュー URL を田中さんに共有
echo "https://core-driven.com/<slug>/"

# 5. 田中さんの確認 (シークレットウィンドウ)
```

### 3.3 全 4 ページ完了後の作業

#### Step 1.5 — メニュー再編
WP 管理画面 → 「外観 → メニュー」または WP-CLI:

```bash
# メニュー項目の追加 (推奨案 A):
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
DOC=~/core-driven.com/public_html
# Biz Core 項目追加
$PHP /usr/bin/wp menu item add-post グローバルナビ 704 --title="Biz Core" --path=$DOC
$PHP /usr/bin/wp menu item add-post グローバルナビ 706 --title="AI Core" --path=$DOC
# 既存 Business メニュー項目を削除 or 非表示
'
```

→ 詳細は Phase 1 着手時に田中さんと協議。

---

## 4. Phase 2: クリーンアップ (5/9 以降)

### 4.1 対象 (詳細は `03_future_architecture.md §10`)
- 旧 CSS の削除 (.custom-message__*, .biz__*)
- バックアップファイル整理
- `swell_child/memo.php` の用途確認
- `/contact/` (ID=55, draft) の削除可否判断

### 4.2 着手条件
- Phase 1 完了から 7 日以上経過し、トラブル報告がないこと
- 田中さんと SEO 影響を確認 (Search Console カバレッジで急減無し)

---

## 5. バックアップ戦略

### 5.1 取得対象 (Phase 0 開始前に取得済になる)

| 種類 | 場所 | サイズ | 取得頻度 |
|---|---|---|:-:|
| `tmp/front.php` 物理バックアップ | `~/backups/coredriven/20260506_phase0/tmp_front.php.original` | 112 KB | Phase 開始時 1 回 |
| `swell_child` フォルダスナップショット | `~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz` | 約 5 MB | Phase 開始時 1 回 |
| WP DB ダンプ | `~/backups/coredriven/20260506_phase0/db_dump.sql` | 数 MB | Phase 開始時 1 回 |
| TOP post_content (Phase 0 前) | `Flow/.../backup_top_post_content_20260506.html` | 1 KB | Phase 開始時 1 回 |
| WP リビジョン | DB の wp_posts | 自動 | post update のたび自動 |

### 5.2 二重保管
- リモート: Xserver `~/backups/coredriven/`
- ローカル: `~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/backup_*`
- (Phase 1 完了後) 第三の保管先として All-in-One WP Migration プラグインで full export

### 5.3 保管期間
- Phase 0/1 中: 完了から最低 1 ヶ月
- Phase 2 完了後: 90 日 (=  SEO 影響の観察完了)

---

## 6. ロールバック手順

### 6.1 Phase 0 のロールバック (作業中・完了後)

#### ケース A — `tmp/front.php` 書き換えで画面が真っ白 (500 エラー)

```bash
ssh xserver '
cd ~/core-driven.com/public_html/wp-content/themes/swell_child/tmp
ls -la front.php.backup_*
# 最新のバックアップを front.php に戻す
LATEST=$(ls -t front.php.backup_* | head -1)
cp $LATEST front.php
echo "Restored from $LATEST"
'

# 動作確認
curl -sI https://core-driven.com/ | head -1
# → HTTP/2 200 を期待
```

**所要 30 秒**。

#### ケース B — TOP post_content 更新後にレイアウト崩れ等

```bash
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
DOC=~/core-driven.com/public_html

# 方法 1: WP のリビジョン機能 (1 つ前のリビジョン ID を取得 → restore)
PREV_REV=$($PHP /usr/bin/wp post revision list 10 --field=ID --path=$DOC 2>/dev/null | sed -n "2p")
$PHP /usr/bin/wp post revision restore $PREV_REV --path=$DOC 2>/dev/null

# 方法 2: ローカルバックアップから復元
# ssh xserver 内ではなく、ローカルから:
'

# (ローカルから実行) 方法 2 のローカル backup を投入
LOCAL_BACKUP=~/aipm_v0/Flow/202605/2026-05-06/0.Other/CoreDriven/backup_top_post_content_20260506.html
scp -P 10022 $LOCAL_BACKUP my0126@my0126.xsrv.jp:/tmp/restore_post_content.html
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
$PHP /usr/bin/wp post update 10 --post_content="$(cat /tmp/restore_post_content.html)" --path=~/core-driven.com/public_html 2>/dev/null
'
```

**所要 1 分**。

#### ケース C — 大規模に壊れた (ファイル + DB 両方)

```bash
# ファイル復元
ssh xserver '
cd ~/core-driven.com/public_html/wp-content/themes
rm -rf swell_child
tar xzf ~/backups/coredriven/20260506_phase0/swell_child_snapshot.tar.gz
'

# DB 復元
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
$PHP /usr/bin/wp db import ~/backups/coredriven/20260506_phase0/db_dump.sql --path=~/core-driven.com/public_html 2>/dev/null
'
```

**所要 5 分**。WP のオプション値も含めて完全復旧。

### 6.2 Phase 1 のロールバック (各ページ単位)

```bash
# 該当ページの post_content を draft + 空に戻す
ssh xserver '
PHP=/opt/php-8.3.30/bin/php
$PHP /usr/bin/wp post update <ID> --post_content="" --post_status=draft --path=~/core-driven.com/public_html 2>/dev/null
'
```

### 6.3 「巻き戻すべきか」の判断基準

| 症状 | 判断 |
|---|---|
| サイト全体が 500 エラー | 即時ロールバック (ケース A) |
| TOP の表示が崩れている | プレビューで原因特定 → 軽微なら CSS で対応、重大ならケース B |
| 内部リンク 1 件が 404 | ロールバックは不要、リンク URL を修正 |
| Lighthouse スコアが 20 以上低下 | ロールバック検討、原因が画像なら最適化で対応 |
| Google Search Console でクロールエラー急増 | 24 時間様子見 → 改善しなければロールバック検討 |

---

## 7. 検証チェックリスト

### 7.1 Phase 0 完了基準 (= 田中さんの確認項目)

#### 表示確認
- [ ] `https://core-driven.com/` でページが 200 OK で開く (シークレットウィンドウ)
- [ ] SWELL ヘッダー (ロゴ + メニュー) が表示
- [ ] AI HTML の Hero (「経営者の熱意を実現する 経営伴走・事業共創パートナー」) が表示
- [ ] 以下のセクションが順に表示:
  - [ ] Role (3 カード: 構想整理 / 事業推進 / 仕組み化)
  - [ ] Challenges (10 個のチェックリスト)
  - [ ] Services (Biz Core / AI Core)
  - [ ] Strengths (5 つの強み)
  - [ ] Members (吉田 / 町田 / 田中の写真 + 経歴)
  - [ ] Final CTA
- [ ] SWELL フッターが画面最下部に表示
- [ ] 画像 3 枚 (Members) が読み込まれている (DevTools Network で 200 OK)

#### リンク確認
- [ ] 「相談する」を押すと `/contact-new/` に遷移 (404 にならない)
- [ ] 「Biz Coreを見る」を押すと `/biz-core/` に遷移
- [ ] 「AI Coreを見る」を押すと `/ai-core/` に遷移
- [ ] 「メンバー詳細を見る」を押すと `/company-new/#members` に遷移
- [ ] グローバルナビの TOP / Business / Company / News / Contact が機能 (Contact = Google Form)

#### レイアウト確認
- [ ] PC (Chrome / 1280px 以上) で崩れなし
- [ ] スマホ (DevTools iPhone 14 / 390px) で崩れなし
- [ ] iPad (DevTools / 768px) で崩れなし

#### 既存ページ影響確認
- [ ] `https://core-driven.com/news/` が従来どおり表示
- [ ] `https://core-driven.com/privacy-policy/` が従来どおり表示
- [ ] `https://core-driven.com/company/` が従来どおり表示 (メディアセクションも維持)

#### パフォーマンス確認 (任意)
- [ ] DevTools Lighthouse で Performance > 60 (目安)
- [ ] DevTools Console に致命的エラーなし

### 7.2 Phase 1 完了基準
- [ ] `/biz-core/` `/ai-core/` `/contact-new/` `/company-new/` が公開状態 (publish)
- [ ] 各ページに AI HTML が反映され、レイアウト崩れ無し
- [ ] TOP からの内部リンクが全て 200 (リンク切れゼロ)
- [ ] メニューが新構造に再編済 (or 既存メニュー維持の方針確定)

---

## 8. 監視 / 観測

### 8.1 即時 (Phase 0 公開直後 30 分)
- DevTools Console エラー監視
- DevTools Network タブで 4xx/5xx エラー監視
- ブラウザでの体感速度確認

### 8.2 短期 (1〜24 時間)
- Google Search Console で「URL 検査」を TOP に対して実行 → インデックス可能か確認
- Google アナリティクスで離脱率の急変が無いか確認

### 8.3 中期 (1〜7 日)
- Search Console カバレッジレポートで除外/エラー件数の急増がないか確認
- 主要キーワードの順位変動をモニタ (Search Console パフォーマンス)

---

## 9. コミュニケーションプラン

### 9.1 Phase 0 進行中の田中さんへの連絡
- Step 0.1〜0.5 完了時 (各 1 行報告): 「Step X 完了、次に進みます」
- Step 0.5 完了時にプレビュー URL を提示: 「`https://core-driven.com/?nocache=...` を確認してください」
- Phase 0 完了報告: 全チェックリスト OK が確認されたら BL-0079 の deliverable を `done` に

### 9.2 トラブル発生時
- 即座に田中さんに通報 (例: 「Step 0.4 で 500 エラー検出。ロールバック実行します」)
- ロールバック完了後、原因分析と次の手を提案

### 9.3 完了後
- mt CLI で BL-0079 に commitment decision を追加
- 翌日朝のタスク案で Phase 1 着手判断を仰ぐ

---

## 10. 想定 Q&A

| Q | A |
|---|---|
| Phase 0 中に他の人がサイトにアクセスしたらどうなる? | Step 0.4 (tmp/front.php 書換) の数秒間だけ瞬間的に挙動が切り替わる。500 エラーが出た訪問者には再読込で復旧する。トラフィックが少ない時間帯 (夜中など) を選ぶのが理想 |
| WP のリビジョン機能はどこから見られる? | 固定ページ編集画面 → 右サイドバー「リビジョン」セクション → 過去版リスト |
| 旧 tmp/front.php の中身を将来再表示したい場合は? | `~/backups/coredriven/20260506_phase0/tmp_front.php.original` から復元、または Phase 0 完了直後の git tag (もし git 管理に入れる場合) |
| AI HTML を編集したいが管理画面が重い | カスタム HTML ブロックは大きい HTML を含むと重い。Phase 2 でインライン CSS の外出しを検討 |
| 検索エンジンに新ページがインデックスされるまでどのくらい? | 通常 1〜7 日。Search Console で「URL 検査 → インデックス登録をリクエスト」で早められる |

---

## 11. 承認フロー

| ステップ | 承認者 | 方法 |
|---|---|---|
| 本計画 (要件・設計・移行計画) の承認 | 田中さん | チャットで「Phase 0 進めて OK」 |
| Phase 0 完了承認 | 田中さん | チェックリスト全 OK 確認後「Phase 0 OK」 |
| Phase 1 着手承認 | 田中さん | Phase 0 から 24 時間以上経過しトラブルなし、で「Phase 1 進めて OK」 |
| Phase 2 着手承認 | 田中さん | Phase 1 完了から 7 日以上経過、で「Phase 2 進めて OK」 |

---

**END OF MIGRATION PLAN.** 田中さんの承認後、Phase 0 Step 0.1 から実行開始可能。
