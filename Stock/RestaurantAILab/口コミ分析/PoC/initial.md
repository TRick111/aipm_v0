# Google Maps 口コミ取得（Node.js）仕様書 草案 v1

## 1. 目的

社内分析用途として、指定した Google Maps 上の店舗（Place）について、直近1年間の口コミ（レビュー）情報を取得し、UTF-8 の CSV としてローカルに出力する。

> 重要：本仕様は Google Maps Platform（Places API 等）で取得可能な範囲に限定する。Google ビジネス プロフィール（旧 GMB）管理者であること自体は、Places API の取得可能範囲を拡張しない（別APIが必要）。

## 2. スコープ

### 2.1 対象

* 対象店舗数：1店舗（将来拡張可能な設計）
* 対象期間：実行時点から過去1年間
* 実行頻度：随時（手動実行想定。必要に応じて OS スケジューラ等で定期実行可能）
* 実行環境：ローカル

### 2.2 取得対象データ

#### A. 口コミ（レビュー）

* レビュー本文（text）
* 投稿日時（time）
* 言語コード（language）
* 評点（rating）※取得可能な場合

#### B. 投稿者（可能な範囲）

* 表示名（author_name / authorAttribution.displayName 等）
* 投稿者の総レビュー数（user_ratings_total 等、返却される場合）
* ローカルガイドレベル等（返却される場合）
* プロフィール画像URL（返却される場合。保存や二次利用は利用規約順守）

### 2.3 非スコープ（制約）

* Google Maps の口コミ全件をAPIで網羅取得すること
* 投稿者の過去投稿一覧やプロフィールページのクロール
* Google Maps Webページのスクレイピング

> 注：Places API のレビュー返却件数には上限があるため、「過去1年の口コミ全件取得」は、Places API 単体では満たせない可能性が高い。要件充足のため、必要に応じて **Google ビジネス プロフィール API（Business Profile API）** での取得可否を別途検証する（本仕様では実装対象外／拡張候補）。

## 3. 前提・依存

### 3.1 認証情報

* Google Maps Platform API Key を使用
* API Key は `.env` で管理

  * `GOOGLE_MAPS_API_KEY=...`

### 3.2 想定利用API

* Places API（Place Details）を第一候補
* 取得件数要件（過去1年の全件）を満たせない場合は、拡張として Business Profile API を検討

## 4. 入力仕様（店舗指定方法）

### 4.1 入力方式

「API連携に必要なデータを入力する」前提として、以下のいずれかで指定可能にする。

* **方式1：place_id 直接指定（推奨）**

  * 入力：`PLACE_ID`
  * 理由：店舗名検索等の前処理不要、曖昧性が少ない

* 方式2：Google Maps URL から抽出

  * 入力：`MAPS_URL`
  * 実装：URLから place_id 取得を試みる（失敗時はユーザーに place_id 指定を促す）

### 4.2 CLI インターフェース（案）

* `node index.js --place_id=<PLACE_ID> --since_days=365 --out=./reviews.csv`

デフォルト：

* `since_days=365`
* `out=./reviews.csv`

## 5. 出力仕様（CSV）

### 5.1 文字コード

* UTF-8

### 5.2 ファイル

* 1実行につき1ファイル出力
* ファイル名デフォルト：`reviews_<place_id>_<yyyymmddHHMMSS>.csv`

  * ただし `--out` 指定があればそのパスに出力

### 5.3 CSVカラム定義（案）

| カラム名                     |               型 |  必須 | 説明                   |
| ------------------------ | --------------: | :-: | -------------------- |
| place_id                 |          string |  ○  | 対象店舗 place_id        |
| fetched_at               | string(ISO8601) |  ○  | 取得実行時刻               |
| review_time              | string(ISO8601) |  △  | 投稿日時（APIが返すtimeを変換）  |
| review_time_unix         |          number |  △  | 投稿日時（Unix秒）          |
| language                 |          string |  △  | 言語コード                |
| rating                   |          number |  △  | 評点                   |
| text                     |          string |  △  | レビュー本文               |
| author_name              |          string |  △  | 投稿者表示名               |
| author_total_reviews     |          number |  △  | 投稿者の総レビュー数（返却される場合）  |
| author_local_guide_level |          number |  △  | ローカルガイドレベル等（返却される場合） |
| author_photo_url         |          string |  △  | プロフィール画像URL（返却される場合） |

> `△` は API 返却に依存するため欠損許容。

## 6. 処理フロー

1. `.env` を読み込み API Key を取得
2. 入力（place_id または maps_url）を解釈し `place_id` を確定
3. Place Details API を呼び出しレビュー情報を取得
4. 取得したレビューのうち、`review_time` が過去1年以内のものを抽出
5. CSV に整形して出力
6. 終了コードを返す

## 7. API仕様（Places: Place Details）

### 7.1 リクエスト（概念）

* Endpoint：Place Details
* パラメータ：

  * `place_id`：入力値
  * `fields`：最低限 `reviews` および分析に必要なフィールド
  * `key`：API Key

> 実装では HTTP クライアント（axios 等）を使用。

### 7.2 レスポンスの利用

* `reviews[]` 相当を抽出
* 各要素から本文、時刻、言語、投稿者情報をマッピング

## 8. エラー処理（最低限）

* API Key 未設定：メッセージ表示し終了（exit code 1）
* place_id 未指定：使い方表示し終了（exit code 1）
* API 呼び出し失敗（HTTPエラー/タイムアウト）：

  * 1回だけリトライ（任意、最小構成）
  * 失敗時はエラーメッセージとレスポンス概要を出力し終了
* CSV 書き込み失敗：エラー表示し終了

## 9. ログ

* 標準出力：開始/終了、取得件数、出力先
* 標準エラー：例外内容、APIのエラーコード/メッセージ

## 10. セキュリティ・コンプライアンス

* `.env` に API Key を保存し、Git 管理対象外にする（.gitignore）
* 取得したデータは社内分析用途に限定
* 投稿者情報は API 返却範囲に限定し、スクレイピング等は行わない

## 11. 制約・リスク（要件ギャップ）

* Places API の `reviews` は返却件数に上限があり、**過去1年分の全件取得を保証できない**。
* 要件（過去1年の全件）が必須の場合、Google ビジネス プロフィール API 等の別経路を要検討。

## 12. 受入条件（Acceptance Criteria）

* place_id を指定して実行すると、レビュー情報が CSV（UTF-8）で出力される
* 出力CSVに、本文・投稿日時・言語コードが可能な範囲で含まれる
* 過去1年フィルタが適用される
* エラー時に原因が分かるメッセージが出力される

## 13. 未確定事項（次版で確定）

1. 「過去1年の口コミ全件取得」を満たすためのデータソース（Places APIのみでよいか／Business Profile APIを使うか）
2. Google ビジネス プロフィール API を使う場合の認証方式（OAuth）と権限
3. CSVファイル命名規則の最終確定
4. 多店舗対応の入力形式（CSVで place_id 一覧など）
