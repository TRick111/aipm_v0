---
name: マーケダッシュボード サンプルデータ取得元台帳
description: 各媒体の管理画面から取得した CSV サンプルと取得元 URL の対応台帳。Phase 1 の取り込み実装・将来の自動エクスポート設計の一次資料。
type: project
last_updated: 2026-06-26
---

# サンプルデータ取得元台帳

マーケダッシュボード Phase 1 の取り込み実装と、いずれ実装する自動エクスポート（Playwright 等）の設計用に、各媒体管理画面から手動で取得した CSV サンプルを集約。

**重要**
- 取得元 URL はログイン必須。`{yearMonth}` 部分は対象月で置き換えて使う。
- 文字コードは全媒体で **Shift_JIS / CP932** を想定（マーケダッシュボード取り込み時は UTF-8 へ変換すること）。
- 月次レポートは毎月月初に前月分が確定する仕様（食べログノート）。当月途中ダウンロードは値が変動する点に注意。
- 列仕様・既知の制約・自動化メモは `Flow/202606/2026-06-26/マーケダッシュボード/媒体CSV調査/` 配下の調査メモを参照。

---

## 食べログノート（Tabelog Note）

サンプル配置: `sample_data/tabelog_note/`

| ファイル名 | 元ファイル名 | 取得元 URL | レポート種別 | 集計単位 | 取得日 | 備考 |
|---|---|---|---|---|---|---|
| `食べログノート_予約一覧_2026-04.csv` | `予約 (1).csv` | https://owner.tabelog.com/tn/analysis?yearMonth=2026-04 | 予約一覧（1予約1行の生データ） | 月別 | 2026-06-26 | 公式ヘルプには CSV 出力ボタンの明示記載なし → **実機にダウンロード機能あり** と確認できたサンプル |
| `食べログノート_予約一覧_2026-06.csv` | `予約.csv` | https://owner.tabelog.com/tn/analysis?yearMonth=2026-06 | 予約一覧（1予約1行の生データ） | 月別 | 2026-06-26 | 同上（2026-06 月分） |
| `食べログノート_分析_予約コース_2026-04.csv` | `20260626_分析_予約コース.csv` | https://owner.tabelog.com/tn/analysis/category/course?yearMonth=2026-04 | 予約コース分析 TOP20+ | 月別 | 2026-06-26 | 公式仕様: 画面 TOP20 まで、CSV は 21位以降も全件出力 |
| `食べログノート_分析_総客数_2026-04.csv` | `20260626_分析_総客数.csv` | https://owner.tabelog.com/tn/analysis?yearMonth=2026-04（同分析ページから「総客数」CSV出力） | 予約数・総客数 | 日別（組数/人数） | 2026-06-26 | マーケ KPI 主軸ソース（日次粒度で曜日/週次計算可） |

### 予約一覧 CSV（生データ）の列定義（実機確認結果）

ファイル先頭行を UTF-8 で復号した列名:

```
予約No, 顧客No, 来店回, キャンセル日, アンケートキャンセル日, 来店日, 来店時間, 滞在時間, 人数, お客様人数, ステータス, 受付方法, Vポイント, 卓, コース, メニュー/コース, 予約属性, 予約メモ, 作成日, 作成時間, インポート時に指定した作成日, インポート時に指定した作成時間
```

- ステータス例: `来店済み`
- 受付方法例: `HOT PEPPER外部ネット予約`, `食べログネット予約`
- 卓: テーブル番号（A1, A4, D1 等）
- → これにより `Flow/.../媒体CSV調査/食べログノート_CSV出力項目.md` の 2.10「予約一覧 CSV エクスポートは確認できず」の記述は **修正必要**。

### 未取得・追加で取得したいレポート（公式 9 種類のうち未取得）

下記レポートは公式に CSV 出力ボタン明示。サンプル未取得のため、次回ログイン時に追加取得推奨:

| レポート | URL（推定パス） | 集計単位 |
|---|---|---|
| ダッシュボード（KPI ハイライト） | `https://owner.tabelog.com/tn/analysis?yearMonth={yearMonth}` 内ダッシュボードタブ | 当月固定 |
| 卓稼働率 | `https://owner.tabelog.com/tn/analysis/category/seat_utilization?yearMonth={yearMonth}`（要確認） | 月別 |
| 予約経路 | `https://owner.tabelog.com/tn/analysis/category/source?yearMonth={yearMonth}`（要確認） | 月別 |
| 新規・リピート | `https://owner.tabelog.com/tn/analysis/category/repeater?yearMonth={yearMonth}`（要確認） | 月別 |
| 予約キャンセル | `https://owner.tabelog.com/tn/analysis/category/cancel?yearMonth={yearMonth}`（要確認） | 月別 |
| 人数割合 | `https://owner.tabelog.com/tn/analysis/category/persons?yearMonth={yearMonth}`（要確認） | 月別 |
| リードタイム | `https://owner.tabelog.com/tn/analysis/category/leadtime?yearMonth={yearMonth}`（要確認） | 月別 |

> 「予約コース」の URL パスから類推した推定値。実際の URL は管理画面のリンクで確認すること。

---

## 食べログ（本体・店舗管理）

サンプル配置: `sample_data/tabelog/`

| 種別 | 取得元 URL | サンプル状況 | 備考 |
|---|---|---|---|
| アクセス数レポート（PC / スマホ / アプリ / 総合の日別） | https://owner.tabelog.com/owner_rst/access_report_total | **サンプル未取得（CSV 出力ボタンなしの可能性大）** | 画面に日別のチャネル別アクセス数が表示されている → 自動化時は HTML パース or Playwright で表テキスト抽出を想定 |

### 自動化方針メモ（食べログアクセス数）

- CSV エクスポートが現時点で確認できないため、**Playwright でテーブル DOM をスクレイピングする方式** を前提に組む。
- 認証は食べログ店舗会員 ID/PW（食べログノートと同一アカウント想定）。
- 取得粒度: 日別 × チャネル（PC / スマホ / アプリ / 総合）。月次集計はマーケダッシュボード側で計算。
- 取得頻度: 月初の前月締めタイミング + 当月途中の週次トラッキング。

---

## 自動エクスポート（Playwright）統合観点メモ

将来の自動化を見据えた共通設計メモ:

1. **共通アカウント**: 食べログノートと食べログ本体は同一の店舗会員アカウントでログイン可能（ログイン URL: `https://owner.tabelog.com/owner_account/login/`）。
2. **Cookie セッション**: ログイン後の遷移は Cookie ベース。Playwright の `storageState` で使い回し可能。
3. **ダウンロード捕捉**: 食べログノート系の CSV ボタンは `download` イベントで取得可能と推定。
4. **アカウントロック注意**: 連続ログイン失敗でロック。リトライバックオフ必須。
5. **取得タイミング**: 月初 1〜3 日に前月確定値を一括取得する設計が安定（日次取り込みは「当月分が途中値」になる）。
6. **他媒体（ホットペッパー / 一休 / ぐるなび / オズモール）**: `Flow/202606/2026-06-26/マーケダッシュボード/媒体CSV調査/` に列仕様調査メモあり。サンプル CSV は未取得 → 取得次第 `sample_data/<媒体名>/` 配下に配置。

---

## 関連ドキュメント

- 列仕様調査メモ: `Flow/202606/2026-06-26/マーケダッシュボード/媒体CSV調査/`
  - `食べログノート_CSV出力項目.md`
  - `食べログ_CSV出力項目.md`
  - `ホットペッパー_CSV出力項目.md`
  - `一休_CSV出力項目.md`
  - `オズモール_CSV出力項目.md`
- プロジェクト要件: `Stock/RestaurantAILab/マーケダッシュボード/docs/要件定義書_v1.md`
- Phase 1 スコープ: `Stock/RestaurantAILab/マーケダッシュボード/docs/Phase1スコープ承認資料.html`
