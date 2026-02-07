import path from "path";
import { fileURLToPath } from "url";
import { google } from "googleapis";
import { AuthClient } from "./lib/authClient.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS_PATH = path.join(__dirname, "credentials.json");

async function main() {
  const credentials = AuthClient.loadCredentials(CREDENTIALS_PATH);
  const authClient = await new AuthClient(credentials).getAuthClient();
  const calendar = google.calendar({ version: "v3", auth: authClient });

  const res = await calendar.calendarList.list({ maxResults: 250 });
  const items = res.data.items || [];

  for (const c of items) {
    console.log(
      JSON.stringify(
        {
          summary: c.summary,
          id: c.id,
          primary: c.primary || false,
          accessRole: c.accessRole
        },
        null,
        2
      )
    );
  }
}

main().catch((err) => {
  console.error("[List] Error:", err?.message || err);
  process.exit(1);
});

