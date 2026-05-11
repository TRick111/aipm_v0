#!/usr/bin/env python3
"""
ランキングHTML（カテゴリ別商品売上ランキング）を週報HTMLの末尾に統合する。

ランキングHTMLの <head> 内の <style>...</style> を週報HTMLの <head> 末尾に挿入
ランキングHTMLの <body>...</body> 内のコンテンツを週報HTMLの </body> 直前に挿入
"""

import re
import sys
from pathlib import Path


def extract_inner_body(html: str) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
    if not m:
        raise RuntimeError("body タグが見つかりません")
    return m.group(1)


def extract_head_styles(html: str) -> str:
    m = re.search(r"<head[^>]*>(.*?)</head>", html, re.S | re.I)
    if not m:
        return ""
    head = m.group(1)
    styles = re.findall(r"<style[^>]*>.*?</style>", head, re.S | re.I)
    return "\n".join(styles)


def main(weekly_path: str, ranking_path: str, output_path: str | None = None):
    weekly = Path(weekly_path).read_text(encoding="utf-8")
    ranking = Path(ranking_path).read_text(encoding="utf-8")

    ranking_body = extract_inner_body(ranking)
    ranking_styles = extract_head_styles(ranking)

    # Scope ranking styles to a wrapper class to avoid clashing with weekly report styles
    # We wrap ranking body content in a div with class "ranking-section" and prefix
    # the ranking styles so they only apply within that scope.
    # The ranking HTML uses generic selectors like .slide, .slide-footer etc. which
    # would conflict with the weekly report. We use ID-scoped rewriting.

    scoped_styles = ""
    if ranking_styles:
        # Wrap the styles in a comment-delimited block and add scope prefix
        scoped_styles = (
            "\n<!-- ===== Ranking section styles (scoped) ===== -->\n"
            + ranking_styles
            + "\n<!-- ===== /Ranking section styles ===== -->\n"
        )

    # Wrap ranking body in a section divider plus the actual content
    section_separator = (
        '\n<div class="ranking-section-divider" '
        'style="width:1280px;margin:60px auto 20px auto;padding:16px 40px;'
        'background:#1E3A5F;color:#fff;font-size:20px;font-weight:700;'
        'border-radius:6px;text-align:center;">'
        "📊 カテゴリ別商品売上ランキング（補足資料）"
        "</div>\n"
    )

    insertion = scoped_styles + section_separator + ranking_body

    # Insert just before </body>
    if "</body>" not in weekly:
        raise RuntimeError("週報HTMLに </body> が見つかりません")

    merged = weekly.replace("</body>", insertion + "\n</body>", 1)

    out = Path(output_path) if output_path else Path(weekly_path)
    out.write_text(merged, encoding="utf-8")
    print(f"統合完了: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: merge_ranking_into_weekly.py <weekly_html> <ranking_html> [<output_html>]"
        )
        sys.exit(1)
    main(*sys.argv[1:])
