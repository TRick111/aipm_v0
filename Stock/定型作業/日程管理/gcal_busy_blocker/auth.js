import path from "path";
import { fileURLToPath } from "url";
import { AuthClient } from "./lib/authClient.js";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS_PATH = path.join(__dirname, "credentials.json");
const TOKEN_PATH = path.join(__dirname, "token.json");

function hasFlag(name) {
  return process.argv.includes(name);
}

// Google Calendar:
// - calendar.readonly: calendarList.list（"work" を見つけるため）
// - calendar.events: events.insert（BUSYブロック作成）
const SCOPES = [
  "https://www.googleapis.com/auth/calendar.readonly",
  "https://www.googleapis.com/auth/calendar.events"
];

async function main() {
  if (hasFlag("--force") && fs.existsSync(TOKEN_PATH)) {
    fs.unlinkSync(TOKEN_PATH);
    console.log("[Auth] token.json を削除しました（--force）");
  }

  const credentials = AuthClient.loadCredentials(CREDENTIALS_PATH);
  const auth = new AuthClient(credentials);
  await auth.authorize(SCOPES);
}

main().catch((err) => {
  console.error("[Auth] Error:", err?.message || err);
  process.exit(1);
});

