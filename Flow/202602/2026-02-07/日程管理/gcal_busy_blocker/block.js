import path from "path";
import { fileURLToPath } from "url";
import { google } from "googleapis";
import { AuthClient } from "./lib/authClient.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS_PATH = path.join(__dirname, "credentials.json");

const DOW = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"];

function getArg(name, fallback = null) {
  const key = `--${name}=`;
  const hit = process.argv.find((a) => a.startsWith(key));
  return hit ? hit.slice(key.length) : fallback;
}

function requireArg(name) {
  const v = getArg(name);
  if (!v) throw new Error(`Missing required arg: --${name}=...`);
  return v;
}

function toRfc3339(dtStr, tz) {
  // Accept: "YYYY-MM-DD HH:MM" -> "YYYY-MM-DDTHH:MM:00"
  // Timezone is provided separately to Google Calendar API.
  const s = dtStr.trim().replace(" ", "T");
  return s.length === 16 ? `${s}:00` : s;
}

function dayOfWeekCodeFromDateStr(yyyyMmDd) {
  // Use UTC noon to avoid DST edge cases (and we only care about weekday).
  const [y, m, d] = yyyyMmDd.split("-").map((x) => Number(x));
  const dt = new Date(Date.UTC(y, m - 1, d, 12, 0, 0));
  return DOW[dt.getUTCDay()];
}

async function resolveCalendarId(calendarApi, calendarName) {
  const res = await calendarApi.calendarList.list({ maxResults: 250 });
  const items = res.data.items || [];
  const found = items.find((c) => (c.summary || "").trim() === calendarName.trim());
  if (!found) {
    const names = items.map((c) => c.summary).filter(Boolean).slice(0, 30);
    throw new Error(
      `Calendar not found by summary: "${calendarName}". Try \`npm run list\`.\n` +
        `Available (first 30): ${names.join(", ")}`
    );
  }
  return found.id;
}

async function main() {
  const calendarName = getArg("calendar", "work");
  const title = getArg("title", "BUSY");
  const timezone = getArg("timezone", "Asia/Tokyo");

  const start = requireArg("start"); // "YYYY-MM-DD HH:MM"
  const end = requireArg("end"); // "YYYY-MM-DD HH:MM"
  const rrule = getArg("rrule"); // e.g. "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
  const until = getArg("until"); // e.g. "2026-03-31" (YYYY-MM-DD)
  const count = getArg("count"); // e.g. "10"
  const repeat = getArg("repeat"); // "weekly" | "biweekly"
  const byday = getArg("byday"); // "MO" or "MO,TU"

  const credentials = AuthClient.loadCredentials(CREDENTIALS_PATH);
  const authClient = await new AuthClient(credentials).getAuthClient();
  const calendar = google.calendar({ version: "v3", auth: authClient });

  const calendarId = await resolveCalendarId(calendar, calendarName);

  const event = {
    summary: title,
    visibility: "private",
    transparency: "opaque", // busy
    start: { dateTime: toRfc3339(start, timezone), timeZone: timezone },
    end: { dateTime: toRfc3339(end, timezone), timeZone: timezone }
  };

  // Recurrence (optional)
  // - rrule: raw RRULE (without "RRULE:" prefix is OK)
  // - until: convenience to append UNTIL=YYYYMMDDT235959Z if not present
  // - count: convenience to append COUNT=n if not present
  if (rrule || until || count || repeat || byday) {
    // If repeat shortcut is provided, generate base rule (unless rrule is explicitly provided).
    let rule = (rrule || "").trim();
    if (rule.toUpperCase().startsWith("RRULE:")) rule = rule.slice("RRULE:".length);

    // Add COUNT / UNTIL only if user didn't specify them in rrule.
    const upper = rule.toUpperCase();
    const parts = rule ? rule.split(";").filter(Boolean) : [];

    if (!rule && repeat) {
      const rep = String(repeat).trim().toLowerCase();
      if (rep === "weekly") {
        parts.push("FREQ=WEEKLY");
        parts.push("INTERVAL=1");
      } else if (rep === "biweekly") {
        parts.push("FREQ=WEEKLY");
        parts.push("INTERVAL=2");
      } else {
        throw new Error(`Invalid --repeat value: ${repeat} (use weekly|biweekly)`);
      }
    }

    // Default BYDAY to the weekday of the start date when using repeat shortcut.
    if (!parts.some((p) => p.toUpperCase().startsWith("BYDAY="))) {
      if (byday) {
        parts.push(`BYDAY=${String(byday).trim().toUpperCase()}`);
      } else if (repeat) {
        const datePart = start.trim().split(" ")[0]; // YYYY-MM-DD
        parts.push(`BYDAY=${dayOfWeekCodeFromDateStr(datePart)}`);
      }
    }

    if (count && !upper.includes("COUNT=") && !upper.includes("UNTIL=")) {
      parts.push(`COUNT=${String(count).trim()}`);
    }

    if (until && !upper.includes("UNTIL=") && !upper.includes("COUNT=")) {
      const u = String(until).trim().replaceAll("-", "");
      // Interpret as "end of day" UTC. (Simple + predictable for operations)
      parts.push(`UNTIL=${u}T235959Z`);
    }

    // Default to weekly if nothing specified.
    if (!parts.some((p) => p.toUpperCase().startsWith("FREQ="))) {
      parts.unshift("FREQ=WEEKLY");
    }

    event.recurrence = [`RRULE:${parts.join(";")}`];
  }

  const res = await calendar.events.insert({
    calendarId,
    requestBody: event
  });

  console.log(
    JSON.stringify(
      {
        inserted: true,
        calendar: calendarName,
        calendarId,
        id: res.data.id,
        htmlLink: res.data.htmlLink,
        summary: res.data.summary,
        start: res.data.start,
        end: res.data.end
      },
      null,
      2
    )
  );
}

main().catch((err) => {
  console.error("[Block] Error:", err?.message || err);
  process.exit(1);
});

