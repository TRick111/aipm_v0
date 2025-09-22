import csv
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# スクリプトのディレクトリ基準のパス設定
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_IN = str((SCRIPT_DIR / "../お役立ち情報台本_rewritten2.csv").resolve())
CSV_OUT = str((SCRIPT_DIR / "../お役立ち情報台本_telop.csv").resolve())

# 列名（既存CSV準拠）
COL_NO = "No."
COL_THEME = "テーマ"
COL_HOOK = "フック（0-5秒）"
COL_EMPATHY = "共感（5-12秒）"
COL_BACKGROUND = "前提知識（12-21秒）"
COL_MAIN = "メイン解説（21-30秒）"
COL_SUMMARY = "解説まとめ（30-32秒）"
COL_PRACTICE = "実践（32-44秒）"
COL_CTA = "CTA（42-45秒）"

# Gemini 準備
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)

# 箇条書き生成プロンプト（日本語）
BULLET_PROMPT = (
    "あなたはインスタグラマーです。メディカルクリニックのインスタグラムリールに乗せるテロップを作成するタスクです。\n"
    "与えられた台本から、リール状に表示するポイントを箇条書きで先頭を『・』にして出力してください。\n"
    "- 最大3行。1～3行で十分に要点化すること\n"
    "- 出力は箇条書きテキストのみ（前後説明・番号・引用符・JSON不要）\n"
    "- 原文の重要語を残しつつ冗長さを削る\n"
    "- リール視聴者にとって分かりやすく、印象に残るポイントに絞る\n\n"
    "【テキスト】\n{{TEXT}}\n"
)


def to_bullets(text: str) -> str:
    """文を箇条書き（・）に整形。
    - 既に「・」が含まれている場合はそのまま返す（既存の整形を尊重）
    - 日本語の句点（。！？）で分割し、空要素を除外
    - 各項目は行頭に「・」を付与し、改行で結合
    """
    if not text:
        return ""
    if "・" in text:
        return text

    # 句点でゆるく分割
    parts = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in "。!?？！":
            parts.append(buf)
            buf = ""
    if buf.strip():
        parts.append(buf)

    # 整形
    bullets = []
    for p in parts:
        s = p.strip()
        if not s:
            continue
        # 行末の句点や読点は削除
        while s and s[-1] in "。.!?！？、，":
            s = s[:-1]
            s = s.rstrip()
        if s:
            bullets.append(f"・{s}")

    return "\n".join(bullets) if bullets else text


def bulletize_with_gemini(text: str) -> str:
    """Geminiで3点以内の箇条書きに要約。失敗時は簡易分割にフォールバック。"""
    if not text:
        return ""
    # 既に箇条書きっぽい場合はそのまま
    if "\n・" in text or text.strip().startswith("・"):
        return text
    try:
        prompt = BULLET_PROMPT.replace("{{TEXT}}", text.strip())
        resp = llm([HumanMessage(content=prompt)])
        content = resp.content if isinstance(resp.content, str) else str(resp.content)
        # 念のため前後空白を除去し、最大3行に制限
        lines = [l.rstrip() for l in content.strip().splitlines() if l.strip()]
        # 先頭に「・」が無ければ付与
        fixed = []
        for l in lines[:3]:
            s = l.strip()
            if not s:
                continue
            if not s.startswith("・"):
                s = "・" + s.lstrip("-・* 　")
            fixed.append(s)
        if fixed:
            return "\n".join(fixed)
        # 空になった場合はフォールバック
        return to_bullets(text)
    except Exception:
        return to_bullets(text)


def main() -> int:
    path_in = Path(CSV_IN)
    path_out = Path(CSV_OUT)

    if not path_in.exists():
        print(f"入力CSVが見つかりません: {path_in}")
        return 1

    with open(path_in, encoding="utf-8") as f:
        reader = list(csv.reader(f))
    if not reader:
        print("入力CSVが空です")
        return 1

    header = reader[0]
    rows = reader[1:]

    # 出力は元と同じヘッダを採用
    with open(path_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

    # 列インデックスを解決（存在しない場合は無視）
    def col_idx(col_name: str):
        try:
            return header.index(col_name)
        except ValueError:
            return None

    idx_no = col_idx(COL_NO)
    idx_theme = col_idx(COL_THEME)
    idx_hook = col_idx(COL_HOOK)
    idx_empathy = col_idx(COL_EMPATHY)
    idx_bg = col_idx(COL_BACKGROUND)
    idx_main = col_idx(COL_MAIN)
    idx_summary = col_idx(COL_SUMMARY)
    idx_practice = col_idx(COL_PRACTICE)
    idx_cta = col_idx(COL_CTA)

    print(f"開始: {len(rows)} 行を処理します\n入力: {path_in}\n出力: {path_out}")

    for i, row in enumerate(rows, 1):
        new_row = list(row)

        # テロップ化する列のみ変換
        # ルール: フック/共感/解説まとめは原文のまま
        # それ以外（前提知識/メイン解説/実践/CTA）はGeminiで最大3点の箇条書きに凝縮
        if idx_bg is not None and idx_bg < len(new_row):
            new_row[idx_bg] = bulletize_with_gemini(new_row[idx_bg])
        if idx_main is not None and idx_main < len(new_row):
            new_row[idx_main] = bulletize_with_gemini(new_row[idx_main])
        if idx_practice is not None and idx_practice < len(new_row):
            new_row[idx_practice] = bulletize_with_gemini(new_row[idx_practice])
        if idx_cta is not None and idx_cta < len(new_row):
            new_row[idx_cta] = bulletize_with_gemini(new_row[idx_cta])

        # フック/共感/解説まとめは原文を尊重（変換なし）

        with open(path_out, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(new_row)

        no_val = (row[idx_no] if idx_no is not None and idx_no < len(row) else str(i))
        theme_val = (row[idx_theme] if idx_theme is not None and idx_theme < len(row) else "")
        print(f"  完了: No.{no_val} 『{theme_val}』")

    print(f"完了: {len(rows)} 行をテロップ化しました → {path_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


