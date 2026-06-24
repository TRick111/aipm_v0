#!/usr/bin/env python3
"""
東京メトロ駅名 謎解き検証スクリプト
- tokyo_metro_stations.json を読み込み、3つの解析を機械的に実行する
  1. 漢字表記 5文字以上のうち、2文字目 == 5文字目 の駅
  2. ひらがな表記 5文字以上のうち、2文字目 == 5文字目 の駅（再検証）
  3. ひらがな表記がちょうど 5文字 の駅、および 1文字目と5文字目を削除した中3文字
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "tokyo_metro_stations.json"
ROMAJI_PATH = HERE / "tokyo_metro_romaji.json"
OUTPUT_PATH = HERE / "verify_puzzle_output.md"


def load_unique_stations() -> list[dict]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    romaji_map = json.loads(ROMAJI_PATH.read_text(encoding="utf-8"))["map"]
    stations = data["unique_stations"]
    missing = [s["kanji"] for s in stations if s["kanji"] not in romaji_map]
    if missing:
        raise ValueError(f"ローマ字未登録の駅: {missing}")
    for s in stations:
        s["romaji"] = romaji_map[s["kanji"]]
    return stations


def char_at(s: str, pos: int) -> str | None:
    """1-indexed 位置 pos の文字を返す。存在しなければ None。"""
    idx = pos - 1
    if 0 <= idx < len(s):
        return s[idx]
    return None


def find_pos2_eq_pos5(stations: list[dict], field: str) -> list[dict]:
    """field ('kanji' or 'hiragana') の2文字目と5文字目が同じ駅を返す。"""
    hits = []
    for st in stations:
        text = st[field]
        c2 = char_at(text, 2)
        c5 = char_at(text, 5)
        if c2 is not None and c5 is not None and c2 == c5:
            hits.append({**st, "char2": c2, "char5": c5})
    return hits


def five_char_hiragana_stations(stations: list[dict]) -> list[dict]:
    """ひらがながちょうど5文字の駅を返す。1文字目と5文字目を削除した中3文字も付与。"""
    out = []
    for st in stations:
        if len(st["hiragana"]) == 5:
            mid3 = st["hiragana"][1:4]  # index 1,2,3 → 2,3,4文字目
            out.append({**st, "middle3": mid3})
    return out


def four_char_with_3rd_in(stations: list[dict], targets: set[str]) -> list[dict]:
    """ひらがな4文字 かつ 3文字目が targets のいずれかの駅を返す。"""
    out = []
    for st in stations:
        h = st["hiragana"]
        if len(h) == 4 and h[2] in targets:
            out.append({**st, "char3": h[2]})
    return out


def romaji_pos3_n_and_pos2_eq_pos5(stations: list[dict]) -> list[dict]:
    """ローマ字3文字目が n、かつ 2文字目 == 5文字目 の駅を返す。"""
    out = []
    for st in stations:
        r = st["romaji"]
        if len(r) >= 5 and r[2] == "n" and r[1] == r[4]:
            out.append({**st, "char2": r[1], "char3": r[2], "char5": r[4]})
    return out


def render_markdown(
    kanji_hits: list[dict],
    hiragana_hits: list[dict],
    five_char_list: list[dict],
    four_char_wa_ki: list[dict],
    romaji_hits: list[dict],
) -> str:
    lines: list[str] = []
    lines.append("# 検証出力: 機械チェック結果\n")
    lines.append("> このファイルは `verify_puzzle.py` の自動出力です。手で書き換えないでください。\n")
    lines.append("## 1. 漢字表記で 2文字目 == 5文字目 の駅\n")
    if kanji_hits:
        lines.append("| 駅 (漢字) | ひらがな | 2文字目 | 5文字目 |")
        lines.append("|---|---|---|---|")
        for h in kanji_hits:
            lines.append(f"| {h['kanji']} | {h['hiragana']} | {h['char2']} | {h['char5']} |")
    else:
        lines.append("該当駅なし（東京メトロ全駅で確認）。")
    lines.append("")
    lines.append("## 2. ひらがな表記で 2文字目 == 5文字目 の駅（再検証）\n")
    if hiragana_hits:
        lines.append("| 駅 (漢字) | ひらがな | 文字数 | 2文字目 | 5文字目 |")
        lines.append("|---|---|---|---|---|")
        for h in hiragana_hits:
            lines.append(f"| {h['kanji']} | {h['hiragana']} | {h['char_count']} | {h['char2']} | {h['char5']} |")
    else:
        lines.append("該当駅なし。")
    lines.append("")
    lines.append("## 3. ひらがな5文字駅 — 1文字目と5文字目を削除した中3文字\n")
    if five_char_list:
        lines.append("| 駅 (漢字) | ひらがな (5文字) | 中3文字 (2-4文字目) |")
        lines.append("|---|---|---|")
        for h in five_char_list:
            lines.append(f"| {h['kanji']} | {h['hiragana']} | {h['middle3']} |")
        lines.append("")
        lines.append(f"合計 {len(five_char_list)} 駅")
    else:
        lines.append("該当駅なし。")
    lines.append("")
    lines.append("## 4. ひらがな4文字 かつ 3文字目が「わ」または「き」の駅\n")
    if four_char_wa_ki:
        lines.append("| 駅 (漢字) | ひらがな (4文字) | 3文字目 |")
        lines.append("|---|---|---|")
        for h in four_char_wa_ki:
            lines.append(f"| {h['kanji']} | {h['hiragana']} | {h['char3']} |")
        lines.append("")
        lines.append(f"合計 {len(four_char_wa_ki)} 駅")
    else:
        lines.append("該当駅なし。")
    lines.append("")
    lines.append("## 5. ローマ字で 3文字目=n かつ 2文字目==5文字目 の駅\n")
    if romaji_hits:
        lines.append("| 駅 (漢字) | ローマ字 | 2文字目 | 3文字目 | 5文字目 |")
        lines.append("|---|---|---|---|---|")
        for h in romaji_hits:
            lines.append(f"| {h['kanji']} | {h['romaji']} | {h['char2']} | {h['char3']} | {h['char5']} |")
        lines.append("")
        lines.append(f"合計 {len(romaji_hits)} 駅")
    else:
        lines.append("該当駅なし。")
    return "\n".join(lines) + "\n"


def main() -> None:
    stations = load_unique_stations()
    kanji_hits = find_pos2_eq_pos5(stations, "kanji")
    hiragana_hits = find_pos2_eq_pos5(stations, "hiragana")
    five_char_list = five_char_hiragana_stations(stations)
    four_char_wa_ki = four_char_with_3rd_in(stations, {"わ", "き"})
    romaji_hits = romaji_pos3_n_and_pos2_eq_pos5(stations)

    print("=== 漢字 2文字目 == 5文字目 ===")
    for h in kanji_hits:
        print(f"  {h['kanji']} ({h['hiragana']}) : {h['char2']} == {h['char5']}")
    if not kanji_hits:
        print("  該当なし")

    print("\n=== ひらがな 2文字目 == 5文字目 ===")
    for h in hiragana_hits:
        print(f"  {h['kanji']} ({h['hiragana']}) : {h['char2']} == {h['char5']}")

    print(f"\n=== ひらがな5文字駅 ({len(five_char_list)}駅) ===")
    for h in five_char_list:
        print(f"  {h['kanji']} {h['hiragana']} → 中3文字: {h['middle3']}")

    print(f"\n=== ひらがな4文字・3文字目が「わ」または「き」 ({len(four_char_wa_ki)}駅) ===")
    for h in four_char_wa_ki:
        print(f"  {h['kanji']} {h['hiragana']} : 3文字目={h['char3']}")
    if not four_char_wa_ki:
        print("  該当なし")

    print(f"\n=== ローマ字 3文字目=n かつ 2文字目==5文字目 ({len(romaji_hits)}駅) ===")
    for h in romaji_hits:
        print(f"  {h['kanji']} {h['romaji']} : pos2={h['char2']}, pos3={h['char3']}, pos5={h['char5']}")
    if not romaji_hits:
        print("  該当なし")

    OUTPUT_PATH.write_text(
        render_markdown(kanji_hits, hiragana_hits, five_char_list, four_char_wa_ki, romaji_hits),
        encoding="utf-8",
    )
    print(f"\nMarkdown 出力: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
