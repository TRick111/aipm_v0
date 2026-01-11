#!/usr/bin/env node

import path from 'path';
import { fileURLToPath } from 'url';
import { AuthClient } from './lib/authClient.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * 初回OAuth認証セットアップスクリプト
 */
async function main() {
  console.log('=== Google Business Profile API 認証セットアップ ===\n');

  try {
    // credentials.jsonを読み込み
    const credentialsPath = path.join(__dirname, 'credentials.json');
    console.log(`[情報] credentials.json を読み込み中: ${credentialsPath}\n`);

    const credentials = AuthClient.loadCredentials(credentialsPath);

    // 認証クライアントを初期化
    const authClient = new AuthClient(credentials);

    // 認証フローを実行
    await authClient.authorize();

    console.log('\n[完了] 認証が完了しました!');
    console.log('       token.json が保存されました');
    console.log('\n次のステップ:');
    console.log('  1. アカウント一覧を確認: node index.js --list-accounts');
    console.log('  2. ロケーション一覧を確認: node index.js --account=<ACCOUNT> --list-locations');
    console.log('  3. レビューを取得: node index.js --account=<ACCOUNT> --location=<LOCATION>');

  } catch (error) {
    console.error('\n[エラー] 認証に失敗しました:');
    console.error(`         ${error.message}`);

    if (error.message.includes('credentials.json')) {
      console.error('\nセットアップ手順:');
      console.error('  1. Google Cloud Console (https://console.cloud.google.com/) にアクセス');
      console.error('  2. プロジェクトを作成または選択');
      console.error('  3. 以下のAPIを有効化:');
      console.error('     - My Business Business Information API');
      console.error('     - My Business Account Management API');
      console.error('  4. 認証情報 > OAuth 2.0 クライアント ID を作成');
      console.error('     アプリケーションの種類: デスクトップ アプリ');
      console.error('  5. credentials.json をダウンロード');
      console.error('  6. このディレクトリに credentials.json を配置');
      console.error('  7. 再度 npm run auth を実行');
    }

    process.exit(1);
  }
}

main();
