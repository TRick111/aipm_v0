import os
import sys
from pathlib import Path

# 標準出力のエンコーディングを設定
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("PDF生成スクリプトを開始します...")

# 必要なライブラリのインストール確認と実行
try:
    import markdown
    print("✓ markdown がインストールされています")
except ImportError:
    print("markdown をインストール中...")
    os.system("pip install markdown")
    import markdown

try:
    from weasyprint import HTML, CSS
    print("✓ weasyprint がインストールされています")
except ImportError:
    print("weasyprint をインストール中...")
    os.system("pip install weasyprint")
    from weasyprint import HTML, CSS

# ファイルパスの設定
base_dir = Path(r'Stock\RestaurantAILab\週報\2_output')
md_file = base_dir / '週報作成基礎資料.md'
pdf_file = base_dir / '週報作成基礎資料.pdf'

print(f"\n読み込み: {md_file}")
print(f"出力先: {pdf_file}")

# Markdownファイルを読み込み
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Markdownを拡張機能付きでHTMLに変換
md_extensions = ['tables', 'fenced_code', 'nl2br']
html_content = markdown.markdown(md_content, extensions=md_extensions)

# CSSスタイルを定義
css_content = """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Yu Gothic', 'MS Gothic', 'Meiryo', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
    margin-top: 30px;
    font-size: 24pt;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    color: #34495e;
    border-left: 5px solid #3498db;
    padding-left: 10px;
    margin-top: 25px;
    font-size: 18pt;
}

h3 {
    color: #555;
    margin-top: 20px;
    font-size: 14pt;
}

h4 {
    color: #666;
    margin-top: 15px;
    font-size: 12pt;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 10pt;
}

table th {
    background-color: #3498db;
    color: white;
    padding: 10px;
    text-align: left;
    font-weight: bold;
}

table td {
    padding: 8px;
    border-bottom: 1px solid #ddd;
}

table tr:nth-child(even) {
    background-color: #f9f9f9;
}

table tr:hover {
    background-color: #f5f5f5;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    page-break-inside: avoid;
}

p {
    margin: 10px 0;
    text-align: justify;
}

ul, ol {
    margin: 10px 0;
    padding-left: 30px;
}

li {
    margin: 5px 0;
}

hr {
    border: none;
    border-top: 2px solid #ddd;
    margin: 30px 0;
}

code {
    background-color: #f4f4f4;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}

blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    margin: 20px 0;
    color: #555;
    font-style: italic;
}

.page-break {
    page-break-after: always;
}

strong {
    color: #2c3e50;
    font-weight: bold;
}
"""

# 完全なHTMLドキュメントを作成
full_html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>週報作成基礎資料 - Five Arrows</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

# 一時的なHTMLファイルに保存
temp_html_file = base_dir / 'temp_report.html'
with open(temp_html_file, 'w', encoding='utf-8') as f:
    f.write(full_html)

print("\nHTMLファイルを生成しました")

# WeasyPrintでPDFを生成
print("PDFを生成中...")
try:
    HTML(filename=str(temp_html_file), base_url=str(base_dir)).write_pdf(
        str(pdf_file),
        stylesheets=None
    )
    print(f"\n✓ PDF生成完了: {pdf_file}")

    # ファイルサイズを表示
    file_size = os.path.getsize(pdf_file)
    file_size_mb = file_size / (1024 * 1024)
    print(f"  ファイルサイズ: {file_size_mb:.2f} MB")

except Exception as e:
    print(f"\n✗ PDF生成中にエラーが発生しました: {e}")
    print(f"  詳細: {type(e).__name__}")

    # WeasyPrintの依存関係の問題の可能性があるため、代替案を提示
    print("\n代替案として、HTMLファイルをブラウザで開いてPDF保存することもできます:")
    print(f"  {temp_html_file}")

# 一時ファイルの削除
try:
    # HTMLファイルは残しておく（デバッグ用）
    # os.remove(temp_html_file)
    print(f"\n一時HTMLファイル: {temp_html_file}")
    print("  (デバッグ用に保存しています)")
except Exception as e:
    pass

print("\n処理完了")
