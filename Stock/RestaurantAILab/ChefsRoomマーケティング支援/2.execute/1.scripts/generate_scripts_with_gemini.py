#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import os
import random
import re
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# スクリプトのディレクトリ基準のパス設定
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_IN = os.getenv("CSV_IN", str((SCRIPT_DIR / "../2.input/input07.csv").resolve()))
CSV_OUT = os.getenv("CSV_OUT", str((SCRIPT_DIR / "../3.output/generated_scripts_2025_11_20.csv").resolve()))
PROMPT_MD = str((SCRIPT_DIR / "../prompt_improved.md").resolve())
EXAMPLES_YAML = str((SCRIPT_DIR / "examples.yaml").resolve())

# 出力CSVのカラム（仕様準拠）
OUTPUT_HEADERS = ["No", "テーマ"] + [f"シーン{i}" for i in range(1, 18)] + ["参考例ID"]

# Gemini 準備（scripts/.env を明示的に読み込む）
# プロジェクトルート: .../aipm_v0
PROJECT_ROOT = Path(__file__).resolve().parents[5]
ENV_PATH = PROJECT_ROOT / "scripts/.env"
load_dotenv(dotenv_path=str(ENV_PATH))
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.4)


def load_text(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def split_example_blocks(yaml_text: str) -> List[str]:
    """
    extract_random_examples.sh と同じロジックをPythonで再現:
    - 行頭が '- title:' の箇所でブロックを分割
    - それぞれのブロック全文を返す
    """
    lines = yaml_text.splitlines()
    blocks: List[str] = []
    buf: List[str] = []
    for ln in lines:
        if re.match(r"^\s*-\s+title\s*:", ln):
            if buf:
                blocks.append("\n".join(buf))
                buf = []
        buf.append(ln)
    if buf:
        blocks.append("\n".join(buf))
    return blocks


def sample_examples(yaml_path: str, k: int = 5) -> Tuple[str, str]:
    """
    examples.yaml からランダムで k 個ブロックを抽出。
    - 戻り値1: Geminiへ渡す参考例の本文（連結）
    - 戻り値2: 参考例ID（タイトルのみ ';' 連結）
    """
    text = load_text(yaml_path)
    blocks = split_example_blocks(text)
    if not blocks:
        # フォールバック
        return "", ""
    random.shuffle(blocks)
    picked = blocks[:k]
    # タイトル抽出（- title: xxx の部分）
    titles: List[str] = []
    for b in picked:
        m = re.search(r"^\s*-\s*title\s*:\s*(.+)$", b, flags=re.MULTILINE)
        if m:
            titles.append(m.group(1).strip())
    return ("\n\n---\n\n".join(picked), ";".join(titles) if titles else "")


def build_prompt(base_md: str, theme: str, row_payload: dict, example_text: str) -> str:
    """
    台本生成に関する指示（prompt_improved.md）をベースに、
    入力行（タイトルなど）と参考例5件を付与し、17シーンのJSONでの厳格出力を指示。
    """
    # 入力情報（必要に応じて追加）
    title = row_payload.get("タイトル") or row_payload.get("テーマ") or theme or ""
    hook = row_payload.get("フック") or row_payload.get("フック（0-5秒）") or ""
    solution = row_payload.get("解決策") or ""
    ending = row_payload.get("エンド") or ""

    strict_output = (
        "出力は次のJSONのみとし、余計な前置き・後置きは一切入れないこと。"
        "キーは 'シーン1' から 'シーン17'。各値は文字列。\n"
        "例: {\"シーン1\":\"...\",\"シーン2\":\"...\",...,\"シーン17\":\"...\"}\n"
    )

    role_tone = (
        "口語的・親しみやすい関西弁で、視聴者の感情に刺さる表現を使ってください。口調は参考例として与える例の関西弁に寄せて、同じ人がしゃべっているような内容にしてください。\n"
        "17シーン構成テンプレートに厳密に従い、各シーンは1〜2文で簡潔に。\n"
    )

    user_payload = [
        f"【入力テーマ】{title}",
        f"【参考: フック】{hook}",
        f"【参考: 解決策】{solution}",
        f"【参考: エンド】{ending}",
    ]

    examples_block = f"【参考例（ランダム5件）】\n{example_text}" if example_text else "【参考例】（該当なし）"

    prompt = (
        f"{base_md}\n\n"
        "—\n"
        "上記の方針に基づき、次の入力からリール台本（17シーン）を生成してください。\n"
        f"{role_tone}\n"
        f"{strict_output}\n\n"
        + "\n".join(user_payload)
        + "\n\n"
        + examples_block
        + "\n"
    )
    return prompt


def parse_scenes_json(resp_text: str) -> List[str]:
    """
    Gemini応答(JSON)から 'シーン1'〜'シーン17' を抽出。
    失敗時は17個の空文字を返す。
    """
    try:
        txt = resp_text.strip()
        # コードブロック除去
        if txt.startswith("```"):
            txt = re.sub(r"^```[a-zA-Z]*\n", "", txt)
            txt = re.sub(r"\n```$", "", txt)
        data = json.loads(txt)
        scenes = []
        for i in range(1, 18):
            key = f"シーン{i}"
            scenes.append(str(data.get(key, "")).strip())
        # 保険
        if len(scenes) < 17:
            scenes += [""] * (17 - len(scenes))
        return scenes[:17]
    except Exception:
        return [""] * 17


def main() -> int:
    path_in = Path(CSV_IN)
    path_out = Path(CSV_OUT)
    prompt_md = load_text(PROMPT_MD)

    if not path_in.exists():
        print(f"入力CSVが見つかりません: {path_in}")
        return 1

    with open(path_in, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    if not reader:
        print("入力CSVが空です")
        return 1

    # 出力初期化（毎回新規作成）
    path_out.parent.mkdir(parents=True, exist_ok=True)
    with open(path_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADERS)

    print(f"開始: {len(reader)} 行を処理します\n入力: {path_in}\n出力: {path_out}")

    for idx, row in enumerate(reader, 1):
        # 一部CSVで列名にBOMが付与されるケースへ対応（例: '\ufeffタイトル'）
        theme = (
            row.get("テーマ")
            or row.get("タイトル")
            or row.get("\ufeffタイトル")
            or f"テーマ{idx}"
        )
        # 行ごとに参考例5件をランダム抽出
        examples_text, examples_id = sample_examples(EXAMPLES_YAML, k=5)
        prompt = build_prompt(prompt_md, theme, row, examples_text)
        print(f"[{idx}/{len(reader)}] 処理開始: No.{idx} 『{theme}』", flush=True)

        try:
            print(f"  → Gemini呼び出し中...", flush=True)
            resp = llm.invoke([HumanMessage(content=prompt)])
            content = resp.content if isinstance(resp.content, str) else str(resp.content)
            print(f"  → 応答受領（{len(content)}文字）", flush=True)
            scenes = parse_scenes_json(content)
            if any(scenes):
                print(f"  → JSON解析OK（17シーン）", flush=True)
            else:
                print(f"  → JSON解析失敗：空で埋めます", flush=True)
        except Exception as e:
            # 失敗時は空シーンで穴埋めし、次へ
            print(f"  × エラー: {e}. 空で継続します。", flush=True)
            scenes = [""] * 17

        out_row = [str(idx), theme] + scenes + [examples_id]
        with open(path_out, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(out_row)

        print(f"  完了: No.{idx} 『{theme}』", flush=True)

    print(f"完了: {len(reader)} 行を台本生成しました → {path_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


