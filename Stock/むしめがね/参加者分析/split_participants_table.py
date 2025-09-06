import pandas as pd
import re

INPUT_CSV = "実験教室むしめがね yoyaku_rireki 20250831 all.csv"
OUTPUT_CSV = "実験教室むしめがね yoyaku_rireki 20250831 all_split.csv"

# 参加者情報を「質問」列から抽出する関数
def extract_participants(qtext):
    if not isinstance(qtext, str) or not qtext.strip():
        return []
    # 1人目、2人目、3人目...のブロックで分割
    pattern = r'＜(\d+)人目：学年＞\s*([\S\s]*?)\s*＜\1人目：フルネーム（ローマ字）＞\s*([\S\s]*?)(?=(\n+＜\d+人目：学年＞|$))'
    matches = re.findall(pattern, qtext, re.DOTALL)
    participants = []
    for m in matches:
        grade = m[1].strip().replace('\n', '').replace('\r', '')
        name = m[2].strip().replace('\n', '').replace('\r', '')
        participants.append({"grade": grade, "name": name})
    return participants

def main():
    # pandasで複数行セルを正しく読み込む
    df = pd.read_csv(INPUT_CSV, encoding='utf-8', dtype=str, engine='python')
    out_rows = []
    for _, row in df.iterrows():
        qtext = row.get("質問", "")
        participants = extract_participants(qtext)
        if not participants:
            # 参加者情報がなければそのまま出力
            row2 = row.to_dict()
            row2["参加者番号"] = 1
            row2["参加者学年"] = ""
            row2["参加者氏名（ローマ字）"] = ""
            out_rows.append(row2)
        else:
            for idx, p in enumerate(participants, 1):
                row2 = row.to_dict()
                row2["参加者番号"] = idx
                row2["参加者学年"] = p["grade"]
                row2["参加者氏名（ローマ字）"] = p["name"]
                out_rows.append(row2)
    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

if __name__ == "__main__":
    main()
