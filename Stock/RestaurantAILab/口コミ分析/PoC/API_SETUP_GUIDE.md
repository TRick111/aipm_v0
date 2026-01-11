# Google Business Profile API セットアップガイド

## プロジェクト情報

| 項目 | 値 |
|------|-----|
| プロジェクトID | `reviewapi-481603` |
| プロジェクト番号 | `689216679746` |
| 作成日 | 2024年12月18日 |

## 必要なAPI一覧

| API名 | 状態 | 有効化リンク |
|-------|------|-------------|
| My Business Account Management API | ✅ 有効化済み（クォータ申請中） | [リンク](https://console.cloud.google.com/apis/library/mybusinessaccountmanagement.googleapis.com?project=reviewapi-481603) |
| My Business Business Information API | ❓ 要確認 | [リンク](https://console.cloud.google.com/apis/library/mybusinessbusinessinformation.googleapis.com?project=reviewapi-481603) |

## クォータ申請情報

### 申請が必要なAPI

**My Business Account Management API**

- クォータ設定ページ: https://console.cloud.google.com/apis/api/mybusinessaccountmanagement.googleapis.com/quotas?project=reviewapi-481603
- 現在のクォータ: `0` (Requests per minute)
- 申請希望値: `60` (推奨)

### 申請時の説明文（テンプレート）

```
【日本語版】
自社が管理する飲食店のGoogle Business Profileから口コミ（レビュー）データを取得し、
社内での顧客満足度分析・サービス改善に使用します。
取得したデータは社内分析用途に限定し、外部への公開は行いません。

【英語版】
We need to retrieve review data from Google Business Profile for our managed restaurant locations.
The data will be used for internal customer satisfaction analysis and service improvement.
Retrieved data will be strictly limited to internal analysis purposes and will not be shared externally.
```

### 申請手順

1. **クォータページにアクセス**
   - https://console.cloud.google.com/apis/api/mybusinessaccountmanagement.googleapis.com/quotas?project=reviewapi-481603

2. **「Requests per minute」の編集アイコン（鉛筆）をクリック**

3. **希望するクォータ値を入力**
   - 推奨値: `60`（1分あたり60リクエスト）

4. **使用目的を入力して送信**
   - 上記のテンプレートを使用

5. **承認を待つ**
   - 通常、数日〜数週間かかる場合があります
   - 承認されるとメールで通知されます

## OAuth 2.0 認証情報

| ファイル | 説明 | 状態 |
|----------|------|------|
| `credentials.json` | OAuthクライアント認証情報 | ✅ 配置済み |
| `token.json` | アクセストークン | ✅ 取得済み |

## 現在の状況

- [x] Google Cloudプロジェクト作成
- [x] OAuth 2.0 クライアントID作成
- [x] credentials.json 配置
- [x] My Business Account Management API 有効化
- [ ] My Business Business Information API 有効化（要確認）
- [ ] クォータ申請 → 承認待ち
- [ ] アカウント一覧取得テスト
- [ ] ロケーション一覧取得テスト
- [ ] レビュー取得テスト

## トラブルシューティング履歴

### 2024-12-18: クォータエラー

**エラーメッセージ:**
```
Quota exceeded for quota metric 'Requests' and limit 'Requests per minute' 
of service 'mybusinessaccountmanagement.googleapis.com' 
for consumer 'project_number:689216679746'.
```

**原因:**
- Google Business Profile APIは制限付きAPIのため、デフォルトでクォータが0に設定されている
- 使用するにはGoogleへの申請と承認が必要

**対応:**
- クォータ増加をリクエスト中

## 関連リンク

- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=reviewapi-481603)
- [APIとサービス - 認証情報](https://console.cloud.google.com/apis/credentials?project=reviewapi-481603)
- [APIとサービス - ダッシュボード](https://console.cloud.google.com/apis/dashboard?project=reviewapi-481603)
- [Google Business Profile API ドキュメント](https://developers.google.com/my-business)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)

## 次のステップ

1. **クォータ承認後:**
   ```bash
   cd "Stock/RestaurantAILab/口コミ分析/PoC"
   node index.js --list-accounts
   ```

2. **アカウントID取得後:**
   ```bash
   node index.js --account=accounts/XXXXXXXX --list-locations
   ```

3. **ロケーションID取得後:**
   ```bash
   node index.js --account=accounts/XXXXXXXX --location=accounts/XXXXXXXX/locations/YYYYYYYY
   ```





