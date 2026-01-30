#!/usr/bin/env python3
"""
MarkdownをHTMLに変換（画像埋め込み、ブラウザで開いてPDF保存用）
"""

import markdown
from pathlib import Path
import re
import base64
import mimetypes

# パス設定
BASE_DIR = Path(__file__).parent
MD_FILE = BASE_DIR / "analysis_report.md"
HTML_FILE = BASE_DIR / "analysis_report.html"

def embed_image(match, base_dir):
    """画像をbase64で埋め込み"""
    img_path = match.group(1)
    alt_text = match.group(2) if match.lastindex >= 2 else ""
    
    if img_path.startswith(('http://', 'https://', 'data:')):
        return match.group(0)
    
    # 相対パスを絶対パスに変換
    abs_path = (base_dir / img_path).resolve()
    
    if abs_path.exists():
        mime_type, _ = mimetypes.guess_type(str(abs_path))
        if mime_type is None:
            mime_type = 'image/png'
        
        with open(abs_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        return f'<img src="data:{mime_type};base64,{img_data}" alt="{alt_text}" />'
    else:
        print(f"画像が見つかりません: {abs_path}")
        return f'<p style="color:red;">[画像が見つかりません: {img_path}]</p>'

def convert_images_in_markdown(md_content, base_dir):
    """Markdown内の画像参照をbase64埋め込みに変換"""
    # ![alt](path) 形式を検出
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        
        if img_path.startswith(('http://', 'https://')):
            return match.group(0)
        
        abs_path = (base_dir / img_path).resolve()
        
        if abs_path.exists():
            mime_type, _ = mimetypes.guess_type(str(abs_path))
            if mime_type is None:
                mime_type = 'image/png'
            
            with open(abs_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            # HTMLのimg タグに変換（markdown変換後に処理されるように）
            return f'<img src="data:{mime_type};base64,{img_data}" alt="{alt_text}" style="max-width:100%; height:auto;" />'
        else:
            print(f"画像が見つかりません: {abs_path}")
            return f'[画像が見つかりません: {img_path}]'
    
    return re.sub(pattern, replace_image, md_content)

# Markdownを読み込み
print(f"読み込み: {MD_FILE}")
md_content = MD_FILE.read_text(encoding='utf-8')

# 画像を埋め込み
print("画像を埋め込み中...")
md_content = convert_images_in_markdown(md_content, BASE_DIR)

# MarkdownをHTMLに変換
print("HTMLに変換中...")
html_content = markdown.markdown(
    md_content,
    extensions=['tables', 'fenced_code', 'toc']
)

# HTMLテンプレートに埋め込み
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>THE BIFTEKI 赤坂見附店 売上分析レポート</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 10mm;
            }}
            body {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                font-size: 8pt;
            }}
            h2 {{
                page-break-before: auto;
                page-break-after: avoid;
            }}
            img {{
                page-break-inside: avoid;
                width: 100% !important;
            }}
            table {{
                page-break-inside: avoid;
                font-size: 7pt;
            }}
        }}
        body {{
            font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", "Yu Gothic", sans-serif;
            font-size: 9pt;
            line-height: 1.5;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 15px 20px;
            background: #fff;
        }}
        h1 {{
            font-size: 18pt;
            color: #1a1a1a;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 8px;
            margin-top: 0;
        }}
        h2 {{
            font-size: 13pt;
            color: #1565C0;
            border-bottom: 2px solid #90CAF9;
            padding-bottom: 4px;
            margin-top: 25px;
        }}
        h3 {{
            font-size: 11pt;
            color: #1976D2;
            margin-top: 18px;
            border-left: 4px solid #2196F3;
            padding-left: 8px;
        }}
        h4 {{
            font-size: 10pt;
            color: #424242;
            margin-top: 15px;
        }}
        p {{
            margin: 6px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 12px 0;
            font-size: 8pt;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 6px 8px;
            text-align: left;
        }}
        th {{
            background-color: #E3F2FD;
            font-weight: bold;
            color: #1565C0;
        }}
        tr:nth-child(even) {{
            background-color: #FAFAFA;
        }}
        img {{
            width: 100%;
            height: auto;
            margin: 15px 0;
            display: block;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        code {{
            background-color: #F5F5F5;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: "SF Mono", "Monaco", "Menlo", monospace;
            font-size: 8pt;
            color: #D32F2F;
        }}
        pre {{
            background-color: #263238;
            color: #ECEFF1;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 8pt;
        }}
        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        hr {{
            border: none;
            border-top: 1px solid #E0E0E0;
            margin: 20px 0;
        }}
        strong {{
            color: #C62828;
        }}
        ul, ol {{
            margin: 8px 0;
            padding-left: 25px;
        }}
        li {{
            margin: 4px 0;
        }}
        blockquote {{
            border-left: 4px solid #2196F3;
            margin: 10px 0;
            padding: 8px 15px;
            background: #E3F2FD;
        }}
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .print-button:hover {{
            background: #1976D2;
        }}
        @media print {{
            .print-button {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">📄 PDFとして保存</button>
    {html_content}
</body>
</html>
"""

# HTMLファイルを保存
HTML_FILE.write_text(full_html, encoding='utf-8')
print(f"\nHTML保存: {HTML_FILE}")
print("\n" + "=" * 60)
print("ブラウザで開いて「PDFとして保存」ボタンをクリックするか、")
print("Cmd+P（印刷）→「PDFとして保存」を選択してください。")
print("=" * 60)
