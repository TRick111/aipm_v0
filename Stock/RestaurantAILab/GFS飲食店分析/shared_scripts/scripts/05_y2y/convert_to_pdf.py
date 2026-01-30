#!/usr/bin/env python3
"""
MarkdownをPDFに変換（画像込み）
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import re

# パス設定
BASE_DIR = Path(__file__).parent
MD_FILE = BASE_DIR / "analysis_report.md"
PDF_FILE = BASE_DIR / "analysis_report.pdf"

# 画像パスを絶対パスに変換
def fix_image_paths(html_content, base_dir):
    """相対パスの画像を絶対パス（file://）に変換"""
    def replace_path(match):
        img_path = match.group(1)
        if img_path.startswith(('http://', 'https://', 'file://')):
            return match.group(0)
        # 相対パスを絶対パスに変換
        abs_path = (base_dir / img_path).resolve()
        return f'src="file://{abs_path}"'
    
    return re.sub(r'src="([^"]+)"', replace_path, html_content)

# Markdownを読み込み
print(f"読み込み: {MD_FILE}")
md_content = MD_FILE.read_text(encoding='utf-8')

# MarkdownをHTMLに変換
html_content = markdown.markdown(
    md_content,
    extensions=['tables', 'fenced_code', 'toc']
)

# 画像パスを修正
html_content = fix_image_paths(html_content, BASE_DIR)

# HTMLテンプレートに埋め込み
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm;
        }}
        body {{
            font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
            font-size: 10pt;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            font-size: 20pt;
            color: #1a1a1a;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 8px;
            margin-top: 0;
        }}
        h2 {{
            font-size: 14pt;
            color: #1565C0;
            border-bottom: 1px solid #90CAF9;
            padding-bottom: 4px;
            margin-top: 25px;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 12pt;
            color: #1976D2;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        h4 {{
            font-size: 11pt;
            color: #424242;
            margin-top: 15px;
        }}
        p {{
            margin: 8px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 9pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background-color: #E3F2FD;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #FAFAFA;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 15px 0;
            display: block;
        }}
        code {{
            background-color: #F5F5F5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "SF Mono", "Monaco", monospace;
            font-size: 9pt;
        }}
        pre {{
            background-color: #F5F5F5;
            padding: 12px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 9pt;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #E0E0E0;
            margin: 20px 0;
        }}
        strong {{
            color: #D32F2F;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        li {{
            margin: 5px 0;
        }}
        .toc {{
            background-color: #FAFAFA;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

# HTMLファイルも保存（デバッグ用）
html_file = BASE_DIR / "analysis_report.html"
html_file.write_text(full_html, encoding='utf-8')
print(f"HTML保存: {html_file}")

# PDFに変換
print(f"PDF生成中...")
HTML(string=full_html, base_url=str(BASE_DIR)).write_pdf(PDF_FILE)
print(f"PDF保存: {PDF_FILE}")
print("完了!")
