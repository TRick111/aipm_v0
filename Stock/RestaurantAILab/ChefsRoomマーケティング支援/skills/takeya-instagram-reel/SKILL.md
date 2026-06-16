---
name: takeya-instagram-reel
description: Generate 17-scene Instagram reel scripts for Chef's Room CEO 竹矢さん from the 竹矢Instagram Google Spreadsheet. Use when the user wants to fill a date-range sheet (e.g. "8/8-8/19", "9/1-9/12") with AI-generated Kansai-dialect reel scripts. The user records the theme by writing only シーン1 (フック), シーン13 (解決), シーン17 (エンド) for each video; this skill (1) detects which sheets/videos have themes decided, (2) extracts them into a CSV, (3) calls the Gemini-based generator to produce all 17 scenes, and (4) writes the scripts back into column E of the spreadsheet.
---

# Takeya Instagram Reel

## Prerequisites

- `gws` CLI authenticated against `auk1in1a1kart@gmail.com` (run `gws auth status` to check)
- `GOOGLE_API_KEY` in `aipm_v0/scripts/.env` (auto-loaded by the generator)
- System Python `/usr/bin/python3` with `langchain-google-genai`, `python-dotenv`, `langchain-core` installed (do NOT use pyenv shim — packages live under system Python)

## Inputs Codex needs from the user

1. Spreadsheet name or URL (default: search Drive for `竹矢Instagram`, id `1w3oZGbbYT3EvlI4sWRIQLUuQMqcDGdTmAM3ImHXfcX4`)
2. (Optional) Specific sheet names to target. If omitted, auto-select with the heuristic below.

## Phases

### Phase 1 — Locate spreadsheet and pick target sheets

1. Resolve spreadsheet ID (Drive search by name if not given).
2. List sheets via `gws sheets spreadsheets get --params '{"spreadsheetId":"<ID>","fields":"sheets(properties(title,index))"}'`.
3. **Heuristic for "target sheet"**: title contains only digits, slashes, dashes, and optional whitespace (e.g. `727-8/7`, `8/8-8/19`, `12/30-1/10`). Sheets that include a restaurant name (e.g. `212-223　RAZ カフェ&レストラン`, `麻布しき◎`) are past-completed and **must be skipped**.
4. Read each candidate sheet's range `A1:E240` (12 video blocks × 20 rows). Use `gws sheets +read --spreadsheet <ID> --range "<title>!A1:E240" --format json`. Pipe through `sed '/^Using keyring/d'` because gws prepends a keyring banner that breaks JSON.

### Phase 2 — Extract themes to input CSV

Each video block is exactly 20 rows in this layout (1-indexed):

| Row | Column A (構成) | Column D | Column E (content) |
|---|---|---|---|
| 1 | (empty) | `ネタメモ：<TITLE>` | (empty) |
| 2 | `構成` | `シーン` | (empty) |
| 3 | `フック` | `1` | **シーン1 = フック** |
| 4-14 | 問題提起/問題拡張/イントロ | `2`〜`12` | usually empty |
| 15 | `解決` | `13` | **シーン13 = 解決** |
| 16-18 | (continued) | `14`〜`16` | usually empty |
| 19 | `エンド` | `17` | **シーン17 = エンド** |
| 20 | (blank separator) | | |

Block N (1-indexed) starts at row `(N-1)*20 + 1`. So シーン1 of block N is at row `(N-1)*20 + 3`, シーン13 at `+15`, シーン17 at `+19`.

For each block:
- **Title** = D-column of title row, strip leading `ネタメモ：` (or `ネタメモ:`). Collapse newlines to single space.
- **Hook** = E-column of シーン1 row.
- **Solution** = E-column of シーン13 row.
- **Ending** = E-column of シーン17 row.
- **Skip block** if Hook is empty (theme not decided yet).

Write `scripts/extract_input.py` output to a Flow folder under today's date:
`Flow/YYYYMM/YYYY-MM-DD/RestaurantAILab_ChefsRoomマーケティング支援/input_takeya_YYYY-MM-DD.csv`

CSV columns (must match what the generator reads):
```
No,タイトル,フック,解決策,エンド,処理済み,_シート,_動画番号
```

`_シート` and `_動画番号` are extra columns for writeback bookkeeping; the generator ignores them.

### Phase 3 — Generate 17-scene scripts

Run the existing generator (do NOT rewrite it):

```bash
export CSV_IN=".../input_takeya_YYYY-MM-DD.csv"
export CSV_OUT=".../output_takeya_YYYY-MM-DD.csv"
/usr/bin/python3 "Stock/RestaurantAILab/ChefsRoomマーケティング支援/2.execute/1.scripts/generate_scripts_with_gemini.py"
```

- One call ≈ 20–30s with `gemini-2.5-pro`. 28 videos ≈ 10–15 min.
- Run with `run_in_background=true` and `ScheduleWakeup` at ~4.5min intervals (270s = stays in prompt cache TTL). Final check around the expected finish time (~120s if close).
- Log to `…/run.log`. Tail it for progress lines like `[N/M] 完了:`.
- Output CSV columns: `No, テーマ, シーン1, …, シーン17, 参考例ID`.

If a row's scenes come back empty, the generator logs `→ JSON解析失敗：空で埋めます`. Surface this to the user; do not silently write empties back.

### Phase 4 — Write scripts back to the spreadsheet

Default behavior: **overwrite all 17 scenes** (the user has confirmed they prefer the AI-refined version over their seed text). If the user asks to preserve their original シーン1/13/17, write only シーン2–12 and 14–16 instead.

Use `scripts/writeback.py` with `valueInputOption=RAW` via `gws sheets spreadsheets values batchUpdate`:
- Range for block N in `<sheet>`: `<sheet>!E<start>:E<end>` where `start = (N-1)*20 + 3`, `end = (N-1)*20 + 19`.
- Bundle all 27+ ValueRanges in a single `batchUpdate` call.

After writing, spot-check via `batchGet` for at least one early + one late cell per sheet. Report counts (`totalUpdatedCells`, ranges).

## Scripts

- `scripts/extract_input.py` — Phase 2 reference implementation. Reads JSON dumps already saved to `/tmp/takeya_sheets/<sheet>.json` (stripped of the keyring banner) and writes the input CSV. Adapt the `TARGET_SHEETS` list at the top per invocation.
- `scripts/writeback.py` — Phase 4 reference implementation. Reads the output CSV (which must include `_シート` and `_動画番号` columns) and prints a `batchUpdate` JSON body to stdout. Pipe into `gws sheets spreadsheets values batchUpdate --params '{"spreadsheetId":"<ID>"}' --json "$(...)"`.

Both scripts are intentionally small; treat them as templates Codex can adapt to the current spreadsheet (different sheet IDs, different sheet name lists). Do not over-engineer.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `JSONDecodeError` reading gws output | gws prepends `Using keyring backend: keyring` line | `sed '/^Using keyring/d'` before `json.loads` |
| `ModuleNotFoundError: langchain_google_genai` | pyenv shim Python, not system | Use `/usr/bin/python3`, not `python3` |
| Generator writes empty 17 scenes | Gemini returned non-JSON | Inspect log; re-run that single row with a tweaked prompt or fallback model |
| Writeback updates `0 cells` | Sheet title has special chars; quoting issue | Wrap sheet title in single quotes inside the range: `'8/8-8/19'!E3:E19` |
| Empty block detected but title row has Japanese category name like `5\n今伸びてるもの` and `ネタメモ：` | Title placeholder present but フック not filled = theme not decided | Skip (do not generate) |

## Naming conventions

- Today's Flow folder: `Flow/YYYYMM/YYYY-MM-DD/RestaurantAILab_ChefsRoomマーケティング支援/`
- Input CSV: `input_takeya_YYYY-MM-DD.csv`
- Output CSV: `output_takeya_YYYY-MM-DD.csv`
- Run log: `run.log`

After a successful run, leave the CSVs in Flow. Promote to Stock only on the user's explicit "Stockに保存" request.
