import csv
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# .env をロードして API キーなどを読み込み
load_dotenv()

# スクリプトのディレクトリ基準のパス設定
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_IN = str((SCRIPT_DIR / "../お役立ち情報台本.csv").resolve())
CSV_OUT = str((SCRIPT_DIR / "../お役立ち情報台本_rewritten2.csv").resolve())
PROMPT_PATH = (SCRIPT_DIR / "shorten_script_prompt.md").resolve()

# Gemini (LangChain) セットアップ
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)

# プロンプトテンプレート読込
with open(PROMPT_PATH, encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()
print(f"プロンプト読込: {PROMPT_PATH}", flush=True)

# 入力CSVの列名（想定）
COL_NO = "No."
COL_THEME = "テーマ"
COL_HOOK = "フック（0-5秒）"
COL_EMPATHY = "共感（5-12秒）"
COL_BACKGROUND = "前提知識（12-21秒）"
COL_MAIN = "メイン解説（21-30秒）"
COL_SUMMARY = "解説まとめ（30-32秒）"
COL_PRACTICE = "実践（32-44秒）"
COL_CTA = "CTA（42-45秒）"

# 出力JSONのキー（プロンプト仕様）
J_HOOK = "フック"
J_EMPATHY = "共感"
J_BACKGROUND = "前提知識"
J_MAIN = "メイン解説"
J_SUMMARY = "解説まとめ"
J_PRACTICE = "実践"
J_CTA = "CTA"


def build_prompt_from_row(template: str, header: list[str], row: list[str]) -> str:
    row_dict = {h: v for h, v in zip(header, row)}
    mapping = {
        "THEME": row_dict.get(COL_THEME, ""),
        "HOOK": row_dict.get(COL_HOOK, ""),
        "EMPATHY": row_dict.get(COL_EMPATHY, ""),
        "BACKGROUND": row_dict.get(COL_BACKGROUND, ""),
        "MAIN": row_dict.get(COL_MAIN, ""),
        "SUMMARY": row_dict.get(COL_SUMMARY, ""),
        "PRACTICE": row_dict.get(COL_PRACTICE, ""),
        "CTA": row_dict.get(COL_CTA, ""),
    }
    def repl(m: re.Match) -> str:
        key = m.group(1)
        return mapping.get(key, "")
    # {{KEY}} プレースホルダを置換
    return re.sub(r"\{\{(\w+)\}\}", repl, template)


def extract_json_from_response(text: str) -> dict:
    # 最初のJSONオブジェクトを抽出
    m = re.search(r"\{[\s\S]+\}", text)
    if not m:
        raise ValueError("JSON部分が見つかりません")
    return json.loads(m.group(0))


def main() -> int:
    if not os.path.exists(CSV_IN):
        print(f"入力CSVが見つかりません: {CSV_IN}", flush=True)
        return 1

    with open(CSV_IN, encoding="utf-8") as f:
        reader = list(csv.reader(f))
    header = reader[0]
    data = reader[1:]

    print(f"開始: {len(data)} 行を処理します\n入力: {CSV_IN}\n出力: {CSV_OUT}", flush=True)

    # 出力CSVにヘッダを先に書き込み
    with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    print(f"  ヘッダ書き込み完了", flush=True)

    # 事前に列インデックスを取得
    try:
        idx_no = header.index(COL_NO)
    except ValueError:
        idx_no = None
    try:
        idx_theme = header.index(COL_THEME)
    except ValueError:
        idx_theme = None

    for idx, row in enumerate(data, 1):
        no_val = row[idx_no] if idx_no is not None and idx_no < len(row) else str(idx)
        theme_val = row[idx_theme] if idx_theme is not None and idx_theme < len(row) else ""
        print(f"[{idx}/{len(data)}] No.{no_val} 『{theme_val}』 送信準備...", flush=True)

        prompt = build_prompt_from_row(PROMPT_TEMPLATE, header, row)
        print(f"  プロンプト長: {len(prompt)} 文字", flush=True)

        try:
            resp = llm([HumanMessage(content=prompt)])
            content = resp.content if isinstance(resp.content, str) else str(resp.content)
            print(f"  受信: {len(content)} 文字", flush=True)
            j = extract_json_from_response(content)

            # 同じヘッダ順で行を構築
            new_row: list[str] = []
            for h in header:
                if h == COL_NO or h == COL_THEME:
                    new_row.append(row[header.index(h)])
                elif h == COL_HOOK:
                    new_row.append(j.get(J_HOOK, ""))
                elif h == COL_EMPATHY:
                    new_row.append(j.get(J_EMPATHY, ""))
                elif h == COL_BACKGROUND:
                    new_row.append(j.get(J_BACKGROUND, ""))
                elif h == COL_MAIN:
                    new_row.append(j.get(J_MAIN, ""))
                elif h == COL_SUMMARY:
                    new_row.append(j.get(J_SUMMARY, ""))
                elif h == COL_PRACTICE:
                    new_row.append(j.get(J_PRACTICE, ""))
                elif h == COL_CTA:
                    new_row.append(j.get(J_CTA, ""))
                else:
                    # 未知の列は元の値を維持
                    new_row.append(row[header.index(h)])
            
            # 処理完了した行を即座にCSVに追記
            with open(CSV_OUT, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
            print(f"  完了: No.{no_val} → CSV書き込み", flush=True)
            
        except Exception as e:
            print(f"  エラー: No.{no_val} → {e}", flush=True)
            # 失敗時は元の行をそのまま出力
            with open(CSV_OUT, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)
            print(f"  エラー時: No.{no_val} → 元データをCSV書き込み", flush=True)

    print(f"完了: {len(data)} 行の短縮処理を出力しました → {CSV_OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
