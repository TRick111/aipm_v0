---
name: マーケダッシュボード 生データ取得 SOP 索引
description: 韓国屋台ポックンパ ネネチキン 東岡崎店の過去 12 ヶ月分マーケ生データ取得手順（自動スクレイパ未整備のレポートのみ）
type: project
last_updated: 2026-06-29
---

# 取得 SOP 索引

韓国屋台ポックンパ ネネチキン 東岡崎店の **過去 12 ヶ月分マーケ生データ** を取得するための SOP 集。

**対象**: 自動化スクレイパが未整備、または既存スクレイパでは過去 12 ヶ月遡及取得ができないレポート。

**対象外**: 食べログ本体（スキル `tabelog-marketing-scrape` で対応済 → `scripts/scrapers/tabelog/`）

## SOP 一覧

| # | 媒体 | レポート | reportType | 工数（12ヶ月） | 取得方式 | SOP |
|---|---|---|---|---|---|---|
| 1 | 食べログノート | 予約一覧 | `tabelog_note_reservations` | 約 18 分 | 月別 CSV × 12 | [tabelog_note_予約一覧_SOP.md](./tabelog_note_予約一覧_SOP.md) |
| 2 | 食べログノート | 予約コース | `tabelog_note_courses` | 約 18 分 | 月別 CSV × 12 | [tabelog_note_予約コース_SOP.md](./tabelog_note_予約コース_SOP.md) |
| 3 | 食べログノート | 分析 — 総客数（日別）★ 最優先 | `tabelog_note_total_guests` | 約 18 分 | 月別 CSV × 12 | [tabelog_note_分析_総客数_SOP.md](./tabelog_note_分析_総客数_SOP.md) |
| 4 | レストランボード（HPG 系） | 予約一覧 | `hpg_restaurant_board` | 約 60 分（または一括 10 分） | 非同期 CSV 12 回 or 一括 | [hpg_restaurant_board_予約一覧_SOP.md](./hpg_restaurant_board_予約一覧_SOP.md) |
| 5 | ホットペッパーグルメ | 流入ワード | `hpg_keywords` | 約 18 分 | 月別 CSV × 12 | [hpg_流入ワード_SOP.md](./hpg_流入ワード_SOP.md) |
| 6 | ホットペッパーグルメ | クチコミ一覧 | `hpg_reviews` | 約 10〜30 分（自動） | 既存スクレイパ + ページング拡張 | [hpg_クチコミ_SOP.md](./hpg_クチコミ_SOP.md) |

## 12 ヶ月遡及取得の合計工数

### 取得方針 A: 月別取得を素直に繰り返す

| 項目 | 工数 |
|---|---|
| 食べログノート 予約一覧（12 月分） | 約 18 分 |
| 食べログノート 予約コース（12 月分） | 約 18 分 |
| 食べログノート 分析・総客数（12 月分） | 約 18 分 |
| レストランボード 予約一覧（12 月分） | 約 60 分 |
| ホットペッパー 流入ワード（12 月分） | 約 18 分 |
| ホットペッパー クチコミ（既存スクレイパ + 拡張） | 約 10〜30 分 |
| **小計（純取得時間）** | **約 142〜162 分（2.4〜2.7 時間）** |
| ログイン × 3 アカウント分の認証オーバーヘッド | 約 15 分（HPG OTP 込み） |
| **総工数** | **約 2.5〜3 時間（半日弱）** |

### 取得方針 B: レストランボードを一括取得して短縮

| 項目 | 工数 |
|---|---|
| 食べログノート × 3 種 | 約 54 分 |
| レストランボード 予約一覧（12 ヶ月一括 1 ファイル） | 約 10 分（10,000 件以内に収まれば） |
| ホットペッパー 流入ワード（12 月分） | 約 18 分 |
| ホットペッパー クチコミ（自動） | 約 10〜30 分 |
| 認証オーバーヘッド | 約 15 分 |
| **総工数** | **約 1.8〜2 時間** |

> **推奨**: 方針 B（レストランボード一括）でスタートし、10,000 件超過で失敗したら月別 12 分割に切り替え。

## アカウント／認証情報の整理

3 つのアカウント体系が必要:

| 媒体グループ | ログイン URL | 認証 | 2FA | storageState 共有 |
|---|---|---|---|---|
| 食べログ系（食べログ本体・食べログノート） | https://owner.tabelog.com/owner_account/login/ | 食べログ店舗会員 ID/PW | 必須化記載なし | 共有可能（同一ドメイン） |
| HPG 管理画面（流入ワード・クチコミ） | https://www.cms.hotpepper.jp/CLN/login/ | リクルート ID | **2FA / OTP 必須** | HPG 内で共有可能 |
| レストランボード | https://restaurant-board.com/ | リクルート ID（HPG と同系統） | **2FA / OTP 必須** | HPG と共有可能性あり（要実機確認） |

## 既存スクレイパとの関係

| スクレイパ | 場所 | 対応レポート | 過去 12 ヶ月遡及 |
|---|---|---|---|
| 食べログ本体（スキル `tabelog-marketing-scrape`） | `scripts/scrapers/tabelog/` | アクセス／CV／ランキング／本体クチコミ | ◯ `access_report_total?display_type=monthly` で 13 ヶ月分一発取得。`access_report_page` は `start_month=YYYYMM` ループ実装で対応可能。本体クチコミは `PG` ページングで遡及可 |
| HPG クチコミ | `scripts/scrapers/hotpepper/` | クチコミ 1 ページのみ | △ **要ページング拡張**（1 ページ目 = 最新 20 件のみ） |
| 食べログノート 分析 9 種 | （未実装） | — | × Phase 1.1 で新規実装が必要 |
| レストランボード予約 | （未実装） | — | × Phase 1.1 で新規実装が必要 |
| HPG 流入ワード | （未実装） | — | × Phase 1.1 で新規実装が必要 |

## ファイル配置先まとめ

```
Stock/RestaurantAILab/マーケダッシュボード/sample_data/
├── tabelog_note/
│   ├── 食べログノート_予約一覧_{YYYY-MM}.csv         × 12
│   ├── 食べログノート_分析_総客数_{YYYY-MM}.csv      × 12
│   └── 食べログノート_分析_予約コース_{YYYY-MM}.csv  × 12
├── restaurant_board/
│   └── レストランボード_予約一覧_{YYYY-MM}.csv       × 12（or 1 ファイル一括）
└── hotpepper/
    ├── ホットペッパー_流入ワード_{YYYY-MM}.csv       × 12
    └── ホットペッパー_クチコミ一覧.csv                × 1（全期間）
```

## 次のアクション（user 確認待ち）

1. **ID / PW の保管場所確定**:
   - 食べログ店舗会員アカウント（owner.tabelog.com）
   - HPG 管理画面リクルート ID（cms.hotpepper.jp）
   - レストランボード（restaurant-board.com）— HPG と同一か別か
2. **HPG の 2FA 方式確認**:
   - SMS / メール / アプリのいずれか
   - 自動化時の OTP 連携方針
3. **食べログノートの「他社台帳連携」状況確認**:
   - ポックンパが ebica / Resty / RESZAIKO / レスラク 経由でないこと
4. **過去 12 ヶ月の保持期間の実機確認**:
   - 各管理画面で 2025-07 までプルダウン／URL クエリで遡れるか
5. **レストランボード一括取得の上限テスト**:
   - 12 ヶ月一括で 10,000 件以内に収まるか
6. **食べログノート分析 — 総客数の詳細 URL 確認**:
   - 「日別／月別」切り替え UI の場所（タブ or プルダウン）
   - 詳細 URL（推定: `/tn/analysis/category/total?yearMonth=YYYY-MM`）

## 関連ドキュメント

- 取得元台帳: `Stock/RestaurantAILab/マーケダッシュボード/sample_data/README.md`
- CSV 列仕様調査: `Flow/202606/2026-06-26/マーケダッシュボード/媒体CSV調査/`
  - `食べログノート_CSV出力項目.md`
  - `ホットペッパー_CSV出力項目.md`
  - `_横断サマリ.md`
- Phase 1 要件: `Stock/RestaurantAILab/マーケダッシュボード/docs/Phase1初期実装_要件定義_v1.md`
- データ取得・UI 設計: `Stock/RestaurantAILab/マーケダッシュボード/docs/データ取得・UI設計書_v1.md`
- 既存スクレイパ README: `Stock/RestaurantAILab/マーケダッシュボード/scripts/scrapers/README.md`
- Dashboard reportType 定義: `RestaurantAILab/Dashboard/lib/marketing/reportTypes.ts`
- Dashboard パーサ実装: `RestaurantAILab/Dashboard/lib/marketing/parsers/`
