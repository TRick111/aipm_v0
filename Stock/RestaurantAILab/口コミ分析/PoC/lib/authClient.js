import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';
import { parse } from 'url';
import open from 'open';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * OAuth 2.0認証クライアント
 */
export class AuthClient {
  constructor(credentials) {
    this.credentials = credentials;
    this.tokenPath = path.join(__dirname, '..', 'token.json');
    this.oauth2Client = null;
  }

  /**
   * OAuth2クライアントを取得または作成
   */
  async getAuthClient() {
    if (this.oauth2Client) {
      return this.oauth2Client;
    }

    const { client_id, client_secret, redirect_uris } = this.credentials.installed || this.credentials.web;

    this.oauth2Client = new google.auth.OAuth2(
      client_id,
      client_secret,
      redirect_uris[0]
    );

    // 保存されたトークンを読み込む
    if (fs.existsSync(this.tokenPath)) {
      const token = JSON.parse(fs.readFileSync(this.tokenPath, 'utf8'));
      this.oauth2Client.setCredentials(token);

      // トークンが期限切れの場合は更新
      if (this.oauth2Client.isTokenExpiring()) {
        try {
          const { credentials } = await this.oauth2Client.refreshAccessToken();
          this.oauth2Client.setCredentials(credentials);
          this.saveToken(credentials);
        } catch (error) {
          console.error('[Auth] トークン更新エラー:', error.message);
          throw new Error('認証トークンの更新に失敗しました。再認証が必要です。');
        }
      }
    } else {
      throw new Error(
        'トークンファイルが見つかりません。先に `npm run auth` を実行して認証を完了してください。'
      );
    }

    return this.oauth2Client;
  }

  /**
   * 新規に認証フローを実行（初回セットアップ用）
   */
  async authorize() {
    const { client_id, client_secret, redirect_uris } = this.credentials.installed || this.credentials.web;

    this.oauth2Client = new google.auth.OAuth2(
      client_id,
      client_secret,
      redirect_uris[0]
    );

    // 既存のトークンがあればそれを使用
    if (fs.existsSync(this.tokenPath)) {
      const token = JSON.parse(fs.readFileSync(this.tokenPath, 'utf8'));
      this.oauth2Client.setCredentials(token);
      console.log('[Auth] 既存の認証トークンを使用します');
      return this.oauth2Client;
    }

    // 新規認証フロー
    const authUrl = this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: [
        'https://www.googleapis.com/auth/business.manage'
      ],
    });

    console.log('[Auth] ブラウザで以下のURLにアクセスして認証してください:');
    console.log(authUrl);
    console.log('\n[Auth] ブラウザを自動で開きます...\n');

    // ブラウザで認証URLを開く
    await open(authUrl);

    // ローカルサーバーでコールバックを受け取る
    const code = await this.getAuthCode(redirect_uris[0]);

    // 認証コードをトークンに交換
    const { tokens } = await this.oauth2Client.getToken(code);
    this.oauth2Client.setCredentials(tokens);

    // トークンを保存
    this.saveToken(tokens);

    console.log('[Auth] 認証が完了しました。トークンを保存しました。');
    return this.oauth2Client;
  }

  /**
   * ローカルサーバーで認証コードを受け取る
   */
  getAuthCode(redirectUri) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(redirectUri);
      const port = urlObj.port || 3000;

      const server = http.createServer(async (req, res) => {
        try {
          if (req.url.indexOf('/?code=') > -1) {
            const qs = parse(req.url, true).query;
            const code = qs.code;

            res.end('認証が完了しました。このウィンドウを閉じてください。');
            server.close();
            resolve(code);
          }
        } catch (e) {
          reject(e);
        }
      });

      server.listen(port, () => {
        console.log(`[Auth] ローカルサーバーを起動しました (port: ${port})`);
      });
    });
  }

  /**
   * トークンをファイルに保存
   */
  saveToken(token) {
    fs.writeFileSync(this.tokenPath, JSON.stringify(token, null, 2));
  }

  /**
   * credentials.jsonファイルを読み込む
   */
  static loadCredentials(credentialsPath) {
    if (!fs.existsSync(credentialsPath)) {
      throw new Error(
        `credentials.json が見つかりません: ${credentialsPath}\n` +
        'Google Cloud ConsoleでOAuth 2.0クライアントIDを作成し、credentials.jsonとして保存してください。'
      );
    }

    return JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  }
}
