"""Convert the BFA manual markdown to HTML, then use Chrome headless to render PDF."""
import markdown
import subprocess
from pathlib import Path

BASE = Path("/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-23/RestaurantAILab/BFA")
MD_PATH = BASE / "BFA担当者向け_Airレジ売上ダッシュボードアップロードマニュアル.md"
HTML_PATH = BASE / "BFA担当者向け_Airレジ売上ダッシュボードアップロードマニュアル.html"
PDF_PATH = BASE / "BFA担当者向け_Airレジ売上ダッシュボードアップロードマニュアル.pdf"

md_text = MD_PATH.read_text(encoding="utf-8")

# Convert markdown → HTML
html_body = markdown.markdown(
    md_text,
    extensions=["extra", "tables", "fenced_code", "toc", "nl2br"],
)

# Rewrite relative image paths to absolute file:// URLs so Chrome can find them
html_body = html_body.replace(
    'src="./screenshots/',
    f'src="file://{BASE}/screenshots/'
)

# Full HTML with print-friendly CSS
CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-size: 9pt;
    color: #666;
  }
}
html, body {
  font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN",
               "Yu Gothic", "Meiryo", "Noto Sans CJK JP",
               -apple-system, BlinkMacSystemFont, "Helvetica Neue",
               Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.7;
  color: #222;
  background: #fff;
  margin: 0;
  padding: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
h1 {
  font-size: 22pt;
  border-bottom: 3px solid #2563eb;
  padding-bottom: 8px;
  margin-top: 0;
  margin-bottom: 16px;
  page-break-after: avoid;
}
h2 {
  font-size: 16pt;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 6px;
  margin-top: 28px;
  margin-bottom: 12px;
  color: #1e3a8a;
  page-break-after: avoid;
}
h3 {
  font-size: 13pt;
  margin-top: 20px;
  margin-bottom: 10px;
  color: #1f2937;
  page-break-after: avoid;
}
h4 { font-size: 11.5pt; margin-top: 14px; margin-bottom: 8px; }
p, ul, ol, table { margin: 10px 0; }
ul, ol { padding-left: 22px; }
li { margin: 4px 0; }
strong { color: #111; }
code {
  font-family: "SF Mono", "Menlo", "Consolas", monospace;
  background: #f3f4f6;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.92em;
  border: 1px solid #e5e7eb;
}
pre {
  background: #1f2937;
  color: #f9fafb;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 0.88em;
  line-height: 1.55;
  overflow-x: auto;
  page-break-inside: avoid;
}
pre code {
  background: transparent;
  color: inherit;
  border: none;
  padding: 0;
}
blockquote {
  border-left: 4px solid #fbbf24;
  background: #fffbeb;
  margin: 12px 0;
  padding: 8px 14px;
  color: #78350f;
  border-radius: 0 4px 4px 0;
  page-break-inside: avoid;
}
blockquote p { margin: 4px 0; }
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #d1d5db;
  padding: 6px 10px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #f3f4f6;
  font-weight: 600;
}
tr:nth-child(even) td { background: #fafafa; }
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 14px auto;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  page-break-inside: avoid;
}
hr {
  border: none;
  border-top: 1px solid #d1d5db;
  margin: 24px 0;
}
a { color: #2563eb; text-decoration: none; }
/* Avoid splitting major sections across pages awkwardly */
h2 { page-break-before: auto; }
"""

html_doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>FIVE Arrows 様向け｜売上データ アップロードマニュアル</title>
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>
"""

HTML_PATH.write_text(html_doc, encoding="utf-8")
print(f"HTML written: {HTML_PATH}")

# Use Chrome headless to print to PDF
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_PATH}",
    f"file://{HTML_PATH}",
]
print("Running:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("stderr:", result.stderr)
    print("stdout:", result.stdout)
else:
    print(f"PDF written: {PDF_PATH}")
    print(f"Size: {PDF_PATH.stat().st_size:,} bytes")
