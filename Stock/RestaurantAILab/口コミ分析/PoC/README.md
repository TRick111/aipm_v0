# Google Business Profile 口コミ取得ツール

Google Business Profile API（旧GMB API）を使用して、自社が管理する店舗の口コミ（レビュー）情報を取得し、CSV形式で出力するNode.jsツールです。

## 特徴

- **大量のレビュー取得**: Places APIの制限（最大5件程度）を超えて、過去の全レビューを取得可能
- **OAuth 2.0認証**: Google Business Profile APIを使用した安全な認証
- **ページネーション対応**: 大量のレビューも自動的に全件取得
- **期間フィルタリング**: 過去N日間のレビューをフィルタリング（デフォルト: 365日）
- **UTF-8 BOM付きCSV**: Excelでも文字化けしにくい形式で出力
- **便利なCLI**: アカウント・ロケーション一覧表示など使いやすい機能

## 前提条件

- **Google Business Profile の管理者権限**が必要です
- 取得対象の店舗を Google ビジネス プロフィールで管理している必要があります

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd "Stock/RestaurantAILab/口コミ分析/PoC"
npm install
```

### 2. Google Cloud Consoleでの設定

#### 2.1 プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択

#### 2.2 APIの有効化

以下のAPIを有効化してください:

- [My Business Business Information API](https://console.cloud.google.com/apis/library/mybusinessbusinessinformation.googleapis.com)
- [My Business Account Management API](https://console.cloud.google.com/apis/library/mybusinessaccountmanagement.googleapis.com)

#### 2.3 OAuth 2.0 クライアントIDの作成

1. [認証情報ページ](https://console.cloud.google.com/apis/credentials)にアクセス
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類: **デスクトップ アプリ** を選択
4. 名前を入力（例: "Review Fetcher"）
5. 「作成」をクリック
6. **credentials.json** をダウンロード
7. ダウンロードした `credentials.json` をこのディレクトリ（PoC/）に配置

### 3. OAuth認証の実行

```bash
npm run auth
```

このコマンドを実行すると:

1. ブラウザが自動的に開きます
2. Googleアカウントでログインします
3. アクセス権限の承認を求められるので「許可」をクリック
4. 認証が完了すると `token.json` が保存されます

## 使い方

### ステップ1: アカウント一覧を確認

```bash
node index.js --list-accounts
```

出力例:
```
利用可能なアカウント:
  - My Business Account (accounts/123456789)
```

### ステップ2: ロケーション（店舗）一覧を確認

```bash
node index.js --account=accounts/123456789 --list-locations
```

出力例:
```
利用可能なロケーション:
  - 東京本店
    accounts/123456789/locations/987654321
    東京都 渋谷区...

  - 大阪支店
    accounts/123456789/locations/111222333
    大阪府 大阪市...
```

### ステップ3: レビューを取得

#### 方法1: ロケーション名を直接指定

```bash
node index.js --account=accounts/123456789 --location=accounts/123456789/locations/987654321
```

#### 方法2: 店舗名で検索

```bash
node index.js --account=accounts/123456789 --location_title="東京本店"
```

#### オプションを指定

```bash
# 過去180日分のみ取得
node index.js --account=accounts/123456789 --location_title="東京本店" --since_days=180

# 出力先を指定
node index.js --account=accounts/123456789 --location_title="東京本店" --out=./output/reviews.csv
```

## コマンドラインオプション

| オプション | 説明 | 必須 |
|----------|------|------|
| `--account=<ACCOUNT>` | ビジネスアカウント名 (例: accounts/12345) | ○ |
| `--location=<LOCATION>` | 店舗のロケーション名 (例: accounts/12345/locations/67890) | △ |
| `--location_title=<TITLE>` | 店舗名で検索 (例: "東京本店") | △ |
| `--since_days=<DAYS>` | 過去何日分を取得するか (デフォルト: 365) | - |
| `--out=<FILE_PATH>` | 出力先CSVファイルパス (デフォルト: 自動生成) | - |
| `--list-accounts` | アカウント一覧を表示 | - |
| `--list-locations` | ロケーション一覧を表示 | - |
| `--help`, `-h` | ヘルプを表示 | - |

※ `--location` または `--location_title` のいずれかが必要

## 出力CSV形式

| カラム名 | 型 | 説明 |
|---------|-----|------|
| place_id | string | ロケーション名（location name） |
| fetched_at | string (ISO8601) | 取得実行時刻 |
| review_time | string (ISO8601) | 投稿日時 |
| review_time_unix | number | 投稿日時（Unix秒） |
| language | string | 言語コード（GMB APIでは提供されない） |
| rating | number | 評点（1-5） |
| text | string | レビュー本文 |
| author_name | string | 投稿者表示名 |
| author_total_reviews | number | （GMB APIでは提供されない） |
| author_local_guide_level | number | （GMB APIでは提供されない） |
| author_photo_url | string | プロフィール画像URL |

## Places API との違い

| 項目 | Places API | Business Profile API (GMB) |
|------|------------|----------------------------|
| 認証方式 | API Key | OAuth 2.0 |
| 取得可能件数 | 最大5件程度 | 全件（ページネーション対応） |
| 必要な権限 | なし | ビジネスオーナー/管理者 |
| 過去1年分の全件取得 | ❌ 不可能 | ✅ 可能 |

## トラブルシューティング

### credentials.json が見つからない

```
[エラー] credentials.json が見つかりません
```

→ Google Cloud Console で OAuth 2.0 クライアントIDを作成し、`credentials.json` をダウンロードしてこのディレクトリに配置してください。

### 認証トークンのエラー

```
[エラー] トークンファイルが見つかりません
```

→ `npm run auth` を実行して認証を完了してください。

### API有効化エラー

```
API Error: 403 - My Business Business Information API has not been used...
```

→ Google Cloud Console で以下のAPIを有効化してください:
- My Business Business Information API
- My Business Account Management API

### アカウントが見つからない

```
利用可能なアカウントが見つかりませんでした
```

→ 使用しているGoogleアカウントがビジネスプロフィールの管理者であることを確認してください。

## ディレクトリ構成

```
PoC/
├── index.js                # メインエントリーポイント
├── setup-auth.js           # 初回認証セットアップスクリプト
├── lib/
│   ├── authClient.js       # OAuth 2.0 認証クライアント
│   ├── gmbClient.js        # Google Business Profile API クライアント
│   └── csvWriter.js        # CSV出力ユーティリティ
├── package.json
├── credentials.json        # OAuth 2.0 クライアント認証情報（Git管理外）
├── token.json              # OAuth アクセストークン（Git管理外）
├── .env.example            # 環境変数テンプレート
├── .gitignore
└── README.md
```

## セキュリティに関する注意

- `credentials.json` と `token.json` は機密情報です
- これらのファイルは `.gitignore` に含まれており、Gitにコミットされません
- 取得したレビューデータは社内分析用途に限定してください
- OAuth トークンは定期的に更新されます（自動）

## ライセンス

ISC

## 今後の拡張候補

- [x] Google Business Profile API 対応（全レビュー取得）
- [ ] 複数店舗の一括取得機能
- [ ] レビューへの返信機能
- [ ] 進捗表示とログレベル設定
- [ ] 感情分析やキーワード抽出などの分析機能
- [ ] ダッシュボード表示機能

## 参考リンク

- [Google Business Profile API ドキュメント](https://developers.google.com/my-business)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
