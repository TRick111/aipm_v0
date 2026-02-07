import { google } from "googleapis";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import http from "http";
import { parse } from "url";
import open from "open";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * OAuth 2.0認証クライアント（Google Calendar用）
 *
 * - 初回: `node auth.js` で token.json を作成
 * - 通常: token.json を読み込んでAPIコール
 */
export class AuthClient {
  constructor(credentials) {
    this.credentials = credentials;
    this.tokenPath = path.join(__dirname, "..", "token.json");
    this.oauth2Client = null;
  }

  async getAuthClient() {
    if (this.oauth2Client) return this.oauth2Client;

    const { client_id, client_secret, redirect_uris } =
      this.credentials.installed || this.credentials.web;

    this.oauth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

    if (!fs.existsSync(this.tokenPath)) {
      throw new Error("token.json が見つかりません。先に `npm run auth` を実行してください。");
    }

    const token = JSON.parse(fs.readFileSync(this.tokenPath, "utf8"));
    this.oauth2Client.setCredentials(token);
    return this.oauth2Client;
  }

  async authorize(scopes) {
    const { client_id, client_secret, redirect_uris } =
      this.credentials.installed || this.credentials.web;

    this.oauth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

    if (fs.existsSync(this.tokenPath)) {
      const token = JSON.parse(fs.readFileSync(this.tokenPath, "utf8"));
      this.oauth2Client.setCredentials(token);
      console.log("[Auth] 既存の認証トークンを使用します");
      return this.oauth2Client;
    }

    const authUrl = this.oauth2Client.generateAuthUrl({
      access_type: "offline",
      scope: scopes,
      prompt: "consent"
    });

    console.log("[Auth] ブラウザで以下のURLにアクセスして認証してください:");
    console.log(authUrl);
    console.log("\n[Auth] ブラウザを自動で開きます...\n");
    await open(authUrl);

    const code = await this.getAuthCode(redirect_uris[0]);
    const { tokens } = await this.oauth2Client.getToken(code);
    this.oauth2Client.setCredentials(tokens);
    this.saveToken(tokens);
    console.log("[Auth] 認証が完了しました。token.json を保存しました。");
    return this.oauth2Client;
  }

  getAuthCode(redirectUri) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(redirectUri);
      const port = Number(urlObj.port || 3000);

      const server = http.createServer((req, res) => {
        try {
          if (req.url && req.url.indexOf("/?code=") > -1) {
            const qs = parse(req.url, true).query;
            const code = qs.code;
            res.end("認証が完了しました。このウィンドウを閉じてください。");
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

  saveToken(token) {
    fs.writeFileSync(this.tokenPath, JSON.stringify(token, null, 2));
  }

  static loadCredentials(credentialsPath) {
    if (!fs.existsSync(credentialsPath)) {
      throw new Error(
        `credentials.json が見つかりません: ${credentialsPath}\n` +
          "Google Cloud ConsoleでOAuth 2.0クライアントIDを作成し、credentials.jsonとして保存してください。"
      );
    }
    return JSON.parse(fs.readFileSync(credentialsPath, "utf8"));
  }
}

