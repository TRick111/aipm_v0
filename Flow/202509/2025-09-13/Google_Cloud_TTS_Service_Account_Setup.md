# Google Cloud Text-to-Speech API サービスアカウント設定手順

**作成日**: 2025-09-13  
**目的**: Google Cloud Text-to-Speech API用のサービスアカウント作成と認証設定

## 📋 概要

Google Cloud Text-to-Speech APIでは以下の2つの認証方法をサポートしています：

| 認証方法 | サポート状況 | 使用場面 | セキュリティレベル |
|---------|-------------|----------|-------------------|
| **APIキー** | ✅ サポート | 簡単なテスト・プロトタイプ | 基本 |
| **サービスアカウント** | ✅ サポート | 本格運用・セキュア環境 | 高 |

**推奨**: セキュリティやアクセス制御の観点から、**サービスアカウントの使用が推奨**されています。

## 🚀 サービスアカウント作成手順

### 1. Google Cloud Consoleへのアクセス
- [Google Cloud Console](https://console.cloud.google.com/) にログイン

### 2. プロジェクトの準備
- 左上のプロジェクトセレクタで、既存のプロジェクトを選択するか、新しいプロジェクトを作成

### 3. Text-to-Speech APIの有効化
```
ナビゲーション: APIとサービス > ライブラリ
検索: "Text-to-Speech"
選択: "Cloud Text-to-Speech API"
アクション: "有効にする" をクリック
```

### 4. サービスアカウントの作成
```
ナビゲーション: IAMと管理 > サービスアカウント
アクション: "サービスアカウントを作成" をクリック

入力項目:
- サービスアカウント名: tts-service-account
- ID: tts-service-account (自動生成)
- 説明: Text-to-Speech API用サービスアカウント
```

### 5. ロールの割り当て
推奨ロールの選択：
- **推奨**: `Text-to-Speech ユーザー` (最小権限)
- **代替**: `プロジェクト > 編集者` (より広い権限)

### 6. JSONキーの作成・ダウンロード
```
手順:
1. 作成したサービスアカウントの詳細ページへ移動
2. "キー" タブを選択
3. "鍵を追加" > "新しい鍵を作成" をクリック
4. キーのタイプで "JSON" を選択
5. "作成" をクリック
6. service-account-key.json がダウンロードされる

⚠️ 重要: ダウンロードしたJSONファイルは安全な場所に保管してください
```

### 7. 環境変数の設定

#### macOS/Linux の場合:
```bash
# 一時的な設定
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# 永続的な設定（.zshrcまたは.bashrcに追加）
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows の場合:
```cmd
# コマンドプロンプト
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json

# PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

#### .envファイルでの設定:
```bash
# プロジェクトの.envファイルに追加
echo 'GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"' >> .env
```

## 🔧 スクリプトでの使用方法

### Google Cloud Text-to-Speech版スクリプト
```bash
# 環境変数設定後
python scripts/tts-from-csv-gemini.py お役立ち情報台本_rewritten2.csv --target_no 11 --start_col 3 --end_col 9
```

### 既存のGenAI API版スクリプト（継続使用可能）
```bash
# GOOGLE_API_KEYを使用
python scripts/tts-from-csv.py --input-csv お役立ち情報台本_rewritten2.csv --start-row 11 --end-row 11 --start-col 3 --end-col 9
```

## 💡 実用的な推奨事項

### 🎯 用途別の選択指針

#### 短期テスト・プロトタイプ
- **推奨**: 既存のGenAI API版（`tts-from-csv.py`）
- **理由**: 既にAPIキー設定済み、即座に使用可能

#### 本格運用・セキュア環境
- **推奨**: Google Cloud版（`tts-from-csv-gemini.py`）
- **理由**: より高いセキュリティ、詳細なアクセス制御

### 🔒 セキュリティのベストプラクティス

1. **JSONキーの管理**
   - バージョン管理システム（Git）にコミットしない
   - `.gitignore`に追加: `service-account-key.json`
   - 定期的なキーローテーション

2. **権限の最小化**
   - 必要最小限のロールのみ割り当て
   - 不要になったサービスアカウントは削除

3. **環境分離**
   - 開発・本番環境で異なるサービスアカウントを使用

## 🆘 トラブルシューティング

### よくあるエラーと対処法

#### 認証エラー
```
エラー: "Your default credentials were not found"
対処法: GOOGLE_APPLICATION_CREDENTIALS環境変数が正しく設定されているか確認
```

#### API無効化エラー
```
エラー: "Cloud Text-to-Speech API has not been used"
対処法: Google Cloud ConsoleでText-to-Speech APIが有効化されているか確認
```

#### 権限エラー
```
エラー: "Permission denied"
対処法: サービスアカウントに適切なロールが割り当てられているか確認
```

## 📚 参考資料

- [Google Cloud Text-to-Speech API公式ドキュメント](https://cloud.google.com/text-to-speech/docs)
- [Google Cloud サービスアカウント管理](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
- [Google Cloud 認証の概要](https://cloud.google.com/docs/authentication)

---

**作成者**: AI Assistant  
**最終更新**: 2025-09-13  
**ファイルパス**: `/Users/rikutanaka/aipm_v0/Flow/202509/2025-09-13/Google_Cloud_TTS_Service_Account_Setup.md`
