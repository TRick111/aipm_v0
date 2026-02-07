import path from "path";
import { fileURLToPath } from "url";
import { AuthClient } from "./lib/authClient.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS_PATH = path.join(__dirname, "credentials.json");

// Google Calendar: events create/modify
const SCOPES = ["https://www.googleapis.com/auth/calendar.events"];

async function main() {
  const credentials = AuthClient.loadCredentials(CREDENTIALS_PATH);
  const auth = new AuthClient(credentials);
  await auth.authorize(SCOPES);
}

main().catch((err) => {
  console.error("[Auth] Error:", err?.message || err);
  process.exit(1);
});

