#!/usr/bin/env node

import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { AuthClient } from './lib/authClient.js';
import { GmbClient } from './lib/gmbClient.js';
import { CsvWriter } from './lib/csvWriter.js';

// ES Moduleで__dirnameを取得
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// .envファイルを読み込み
dotenv.config();

/**
 * コマンドライン引数をパース
 */
function parseArguments() {
  const args = process.argv.slice(2);
  const options = {
    accountName: null,
    locationName: null,
    locationTitle: null,
    sinceDays: 365,
    output: null,
    listAccounts: false,
    listLocations: false
  };

  for (const arg of args) {
    if (arg.startsWith('--account=')) {
      options.accountName = arg.split('=')[1];
    } else if (arg.startsWith('--location=')) {
      options.locationName = arg.split('=')[1];
    } else if (arg.startsWith('--location_title=')) {
      options.locationTitle = arg.split('=')[1];
    } else if (arg.startsWith('--since_days=')) {
      options.sinceDays = parseInt(arg.split('=')[1], 10);
    } else if (arg.startsWith('--out=')) {
      options.output = arg.split('=')[1];
    } else if (arg === '--list-accounts') {
      options.listAccounts = true;
    } else if (arg === '--list-locations') {
      options.listLocations = true;
    } else if (arg === '--help' || arg === '-h') {
      showUsage();
      process.exit(0);
    }
  }

  return options;
}

/**
 * 使い方を表示
 */
function showUsage() {
  console.log(`
Google Business Profile 口コミ取得ツール

使い方:
  node index.js --account=<ACCOUNT> --location=<LOCATION> [オプション]

必須パラメータ:
  --account=<ACCOUNT>       ビジネスアカウント名 (例: accounts/12345)
  --location=<LOCATION>     店舗のロケーション名 (例: accounts/12345/locations/67890)
    または
  --location_title=<TITLE>  店舗名で検索 (例: "東京本店")

オプション:
  --since_days=<DAYS>       過去何日分を取得するか (デフォルト: 365)
  --out=<FILE_PATH>         出力先CSVファイルパス (デフォルト: 自動生成)
  --list-accounts           アカウント一覧を表示
  --list-locations          ロケーション一覧を表示
  --help, -h                このヘルプを表示

例:
  # 初回セットアップ（OAuth認証）
  npm run auth

  # アカウント一覧を表示
  node index.js --list-accounts

  # 特定アカウントのロケーション一覧を表示
  node index.js --account=accounts/12345 --list-locations

  # レビューを取得
  node index.js --account=accounts/12345 --location=accounts/12345/locations/67890
  node index.js --account=accounts/12345 --location_title="東京本店" --since_days=180

注意:
  - 事前に npm run auth でOAuth認証を完了してください
  - credentials.json が必要です（Google Cloud Consoleから取得）
  `);
}

/**
 * 過去N日以内のレビューをフィルタ
 */
function filterRecentReviews(reviews, sinceDays) {
  const cutoffTime = Math.floor(Date.now() / 1000) - (sinceDays * 24 * 60 * 60);

  return reviews.filter(review => {
    return review.time && review.time >= cutoffTime;
  });
}

/**
 * メイン処理
 */
async function main() {
  console.log('=== Google Business Profile 口コミ取得ツール ===\n');

  // 引数をパース
  const options = parseArguments();

  try {
    // credentials.jsonを読み込み
    const credentialsPath = path.join(__dirname, 'credentials.json');
    const credentials = AuthClient.loadCredentials(credentialsPath);

    // 認証クライアントを初期化
    const authClient = new AuthClient(credentials);
    const auth = await authClient.getAuthClient();

    // GMB APIクライアントを初期化
    const gmbClient = new GmbClient(auth);

    // アカウント一覧表示モード
    if (options.listAccounts) {
      console.log('[処理] アカウント一覧を取得中...\n');
      const accounts = await gmbClient.listAccounts();

      if (accounts.length === 0) {
        console.log('利用可能なアカウントが見つかりませんでした');
        process.exit(0);
      }

      console.log('利用可能なアカウント:');
      accounts.forEach(account => {
        console.log(`  - ${account.accountName} (${account.name})`);
      });
      process.exit(0);
    }

    // アカウント名の確認
    if (!options.accountName) {
      console.error('[エラー] --account パラメータが指定されていません');
      console.error('         --list-accounts でアカウント一覧を確認してください\n');
      showUsage();
      process.exit(1);
    }

    // ロケーション一覧表示モード
    if (options.listLocations) {
      console.log(`[処理] ロケーション一覧を取得中... (account: ${options.accountName})\n`);
      const locations = await gmbClient.listLocations(options.accountName);

      if (locations.length === 0) {
        console.log('ロケーションが見つかりませんでした');
        process.exit(0);
      }

      console.log('利用可能なロケーション:');
      locations.forEach(loc => {
        console.log(`  - ${loc.title || '(タイトルなし)'}`);
        console.log(`    ${loc.name}`);
        if (loc.storefrontAddress) {
          const addr = loc.storefrontAddress;
          console.log(`    ${addr.locality || ''} ${addr.addressLines?.join(' ') || ''}`);
        }
        console.log('');
      });
      process.exit(0);
    }

    // ロケーション名を決定
    let locationName = options.locationName;
    let locationTitle = '';

    if (!locationName && options.locationTitle) {
      // タイトルから検索
      const location = await gmbClient.findLocationByName(options.accountName, options.locationTitle);
      locationName = location.name;
      locationTitle = location.title;
      console.log(`[情報] ロケーションが見つかりました: ${locationTitle}`);
    } else if (!locationName) {
      console.error('[エラー] --location または --location_title パラメータが必要です\n');
      showUsage();
      process.exit(1);
    }

    console.log(`[設定] Account: ${options.accountName}`);
    console.log(`[設定] Location: ${locationName}`);
    console.log(`[設定] 取得期間: 過去${options.sinceDays}日間\n`);

    // レビューデータを取得
    console.log('[処理] レビューデータを取得中...');
    const rawReviews = await gmbClient.listReviews(locationName);

    if (rawReviews.length === 0) {
      console.log('[情報] このロケーションに対するレビューが見つかりませんでした');
      console.log('[完了] 処理を終了します');
      process.exit(0);
    }

    // レビューデータを正規化
    const allReviews = rawReviews.map(r => GmbClient.normalizeReview(r));
    console.log(`[処理] 取得したレビュー数: ${allReviews.length}件`);

    // 指定期間内のレビューをフィルタ
    const recentReviews = filterRecentReviews(allReviews, options.sinceDays);
    console.log(`[処理] 期間フィルタ後のレビュー数: ${recentReviews.length}件\n`);

    if (recentReviews.length === 0) {
      console.log(`[情報] 過去${options.sinceDays}日間のレビューが見つかりませんでした`);
      console.log('[完了] 処理を終了します');
      process.exit(0);
    }

    // 出力先パスを決定
    const locationId = locationName.split('/').pop();
    const outputPath = options.output ||
      path.join(__dirname, CsvWriter.generateDefaultFilename(locationId));

    // CSVに出力
    console.log('[処理] CSVファイルを出力中...');
    await CsvWriter.writeReviews(recentReviews, locationName, outputPath);

    console.log('\n[完了] 処理が正常に完了しました');
    console.log(`       店舗: ${locationTitle || locationName}`);
    console.log(`       出力ファイル: ${outputPath}`);
    console.log(`       出力レビュー数: ${recentReviews.length}件`);

  } catch (error) {
    console.error('\n[エラー] 処理中にエラーが発生しました:');
    console.error(`         ${error.message}`);

    if (error.stack) {
      console.error('\nスタックトレース:');
      console.error(error.stack);
    }

    process.exit(1);
  }
}

// メイン処理を実行
main();
