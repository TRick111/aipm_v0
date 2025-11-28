import csv
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# スクリプトのディレクトリ基準のパス設定
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_IN = str((SCRIPT_DIR / "../../4.TikTok/投稿アイディア.csv").resolve())
MD_TEMPLATE = str((SCRIPT_DIR / "../../4.TikTok/絵コンテ定義.md").resolve())
CSV_OUT = str((SCRIPT_DIR / "../../4.TikTok/投稿アイディア_絵コンテ.csv").resolve())

# 列名（既存CSV準拠）
COL_NO = "No"
COL_CATEGORY = "カテゴリ"
COL_TITLE = "企画タイトル"
COL_OVERVIEW = "概要"

# 出力CSVの列名
OUTPUT_COLS = [
    "No", "カテゴリ", "企画タイトル", "概要",
    "シーン番号", "シーン概要", "映像イメージ", "必要な撮影素材", 
    "テロップ（文字）", "音声（ナレーション）", "効果音（オノマトペ）", "注意点・指示"
]

# Gemini 準備
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)

# 絵コンテ生成プロンプト
STORYBOARD_PROMPT = """
あなたはTikTok動画の絵コンテ作成の専門家です。

以下の企画内容と絵コンテ定義テンプレートを参考に、TikTok動画用の詳細な絵コンテを作成してください。

【企画内容】
カテゴリ: {category}
企画タイトル: {title}
概要: {overview}

【絵コンテ定義テンプレート】
{template}

【出力形式】
以下のCSV形式で出力してください。各シーンを1行で表現し、複数シーンがある場合は複数行で出力してください。

**重要：基本情報（No, カテゴリ, 企画タイトル, 概要）は含めず、シーン情報のみを出力してください。**

シーン番号,シーン概要,映像イメージ,必要な撮影素材,テロップ（文字）,音声（ナレーション）,効果音（オノマトペ）,注意点・指示

【注意事項】
- 人物を登場させる場合は顔から上は表示しない
- 制服・服装は清潔感を意識する
- ブランド名や個人情報が映らないように注意
- 撮影はなるべく明るい環境で、リングライトなどを活用
- 各シーンは15-30秒程度の長さを想定
- テロップは視聴者にとって分かりやすく、印象に残る内容にする
- 効果音は必ず擬音語で書く（例：「ジャーン」「ポン」「キラキラ」）
- 映像イメージ列は、CSVで表示されるような行内の改行を利用して見やすく表示してください。

CSV形式のみで出力し、前後の説明文は不要です。
"""


def load_template():
    """絵コンテ定義テンプレートを読み込み"""
    try:
        with open(MD_TEMPLATE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"テンプレートファイルが見つかりません: {MD_TEMPLATE}")
        return ""


def generate_storyboard(category: str, title: str, overview: str, template: str) -> list:
    """AIで絵コンテを生成"""
    try:
        prompt = STORYBOARD_PROMPT.format(
            category=category,
            title=title,
            overview=overview,
            template=template
        )
        
        print(f"  AIに送信中...")
        resp = llm.invoke([HumanMessage(content=prompt)])
        content = resp.content if isinstance(resp.content, str) else str(resp.content)
        
        print(f"  AI応答受信: {len(content)}文字")
        print(f"  AI応答内容（最初の500文字）: {content[:500]}")
        
        # CSV形式の解析（改行を考慮したパース）
        import io
        import csv as csv_module
        
        storyboard_rows = []
        
        # CSVとして解析
        csv_reader = csv_module.reader(io.StringIO(content))
        
        for i, row in enumerate(csv_reader):
            if i == 0 and 'シーン番号' in str(row):
                continue  # ヘッダー行をスキップ
            
            # シーン情報のみを抽出（8列の形式）
            if len(row) >= 8:
                # 最初の列が数字（シーン番号）かチェック
                if row[0].strip().isdigit():
                    storyboard_rows.append(row[:8])  # 最初の8列のみ
                    print(f"  追加: シーン{row[0]}")
                elif len(row) >= 12 and row[4].strip().isdigit():
                    # 基本情報+シーン情報の形式の場合
                    scene_row = row[4:12]  # 5列目から8列分
                    storyboard_rows.append(scene_row)
                    print(f"  追加: シーン{scene_row[0]}")
        
        print(f"  解析結果: {len(storyboard_rows)}シーン")
        return storyboard_rows
        
    except Exception as e:
        print(f"AI生成エラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_existing_nos(path_out: Path) -> set:
    """既存の出力CSVから処理済みのNoを取得"""
    if not path_out.exists():
        return set()
    
    existing_nos = set()
    try:
        with open(path_out, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダーをスキップ
            for row in reader:
                if row and row[0].isdigit():
                    existing_nos.add(int(row[0]))
    except Exception as e:
        print(f"既存ファイル読み込みエラー: {e}")
    
    return existing_nos


def main() -> int:
    path_in = Path(CSV_IN)
    path_out = Path(CSV_OUT)
    
    if not path_in.exists():
        print(f"入力CSVが見つかりません: {path_in}")
        return 1
    
    # テンプレート読み込み
    template = load_template()
    if not template:
        return 1
    
    # 入力CSV読み込み
    with open(path_in, encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    if not reader:
        print("入力CSVが空です")
        return 1
    
    header = reader[0]
    rows = reader[1:]
    
    # 列インデックスを解決
    def col_idx(col_name: str):
        try:
            return header.index(col_name)
        except ValueError:
            return None
    
    idx_no = col_idx(COL_NO)
    idx_category = col_idx(COL_CATEGORY)
    idx_title = col_idx(COL_TITLE)
    idx_overview = col_idx(COL_OVERVIEW)
    
    # 既存の処理済みNoを取得
    existing_nos = get_existing_nos(path_out)
    print(f"既存の処理済みNo: {sorted(existing_nos)}")
    
    # 出力CSV作成（既存ファイルがある場合は追記モード）
    if not path_out.exists():
        with open(path_out, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(OUTPUT_COLS)
    
    print(f"開始: {len(rows)} 行を処理します\n入力: {path_in}\n出力: {path_out}")
    
    # 未処理の行のみフィルタリング
    unprocessed_rows = []
    for row in rows:
        no_val = row[idx_no] if idx_no is not None and idx_no < len(row) else ""
        if no_val.isdigit() and int(no_val) not in existing_nos:
            unprocessed_rows.append(row)
    
    print(f"未処理の行: {len(unprocessed_rows)} 行")
    
    # No.10まで処理
    target_rows = unprocessed_rows[:10]
    print(f"今回処理する行: {len(target_rows)} 行")
    
    for i, row in enumerate(target_rows, 1):
        # 基本情報取得
        no_val = row[idx_no] if idx_no is not None and idx_no < len(row) else str(i)
        category_val = row[idx_category] if idx_category is not None and idx_category < len(row) else ""
        title_val = row[idx_title] if idx_title is not None and idx_title < len(row) else ""
        overview_val = row[idx_overview] if idx_overview is not None and idx_overview < len(row) else ""
        
        print(f"\n=== 処理中: No.{no_val} 『{title_val}』 ===")
        print(f"カテゴリ: {category_val}")
        print(f"概要: {overview_val}")
        
        # AIで絵コンテ生成
        storyboard_rows = generate_storyboard(category_val, title_val, overview_val, template)
        
        if storyboard_rows:
            print(f"生成されたシーン数: {len(storyboard_rows)}")
            for j, scene in enumerate(storyboard_rows, 1):
                print(f"  シーン{j}: {scene[1] if len(scene) > 1 else 'N/A'}")
        else:
            print("  警告: シーンが生成されませんでした")
        
        # 出力CSVに追加
        with open(path_out, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            
            for scene_row in storyboard_rows:
                # 基本情報 + シーン情報で1行作成
                output_row = [no_val, category_val, title_val, overview_val] + scene_row
                writer.writerow(output_row)
                print(f"  CSVに追加: {len(output_row)}列のデータ")
        
        print(f"完了: No.{no_val} - {len(storyboard_rows)} シーン生成")
    
    print(f"完了: {len(target_rows)} 企画の絵コンテを生成しました → {path_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
