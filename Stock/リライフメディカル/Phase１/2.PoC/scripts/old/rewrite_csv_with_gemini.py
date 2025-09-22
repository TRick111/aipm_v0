import csv
import json
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

# ファイルパス（scripts/ からの相対パスに修正）
csv_in = "../お役立ち情報台本.csv"
csv_out = "../お役立ち情報台本_rewritten.csv"
prompt_path = Path("../../99.jprompts/one_by_one_rewrite_prompt.md")

# Gemini 2.5 Pro (Langchain) セットアップ
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.7)

# プロンプトテンプレート読込
with open(prompt_path, encoding="utf-8") as f:
    prompt_template = f.read()

def row_to_json(row, header):
    obj = {h: v for h, v in zip(header, row)}
    return json.dumps(obj, ensure_ascii=False, indent=2)

def build_prompt(template, row_json):
    import re
    return re.sub(r'```json\n\{[\s\S]+?\n\}```', f'```json\n{row_json}\n```', template, count=1)

def extract_json_from_response(text):
    import re
    m = re.search(r'\{[\s\S]+?\}', text)
    if m:
        return json.loads(m.group(0))
    raise ValueError("JSON部分が見つかりません")

with open(csv_in, encoding="utf-8") as f:
    reader = list(csv.reader(f))
header = reader[0]
data = reader[1:]

rewritten_rows = [header]
for idx, row in enumerate(data, 1):
    row_json = row_to_json(row, header)
    prompt = build_prompt(prompt_template, row_json)
    try:
        response = llm([HumanMessage(content=prompt)])
        rewritten = extract_json_from_response(response.content)
        rewritten_row = [rewritten.get(h, "") for h in header]
        rewritten_rows.append(rewritten_row)
        print(f"{idx}/{len(data)} 完了")
    except Exception as e:
        print(f"{idx}/{len(data)} エラー: {e}")
        rewritten_rows.append(row)

with open(csv_out, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rewritten_rows)

print(f"{len(data)}件のリライト処理が完了しました。出力: {csv_out}")
