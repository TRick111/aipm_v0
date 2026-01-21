#!/usr/bin/env python3
"""
Markdown -> HTML converter for printing.
- Small body font
- Images full width within page margins
"""

from __future__ import annotations

from pathlib import Path
import markdown


CSS = r"""
@page { size: A4; margin: 12mm; }

html, body {
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans JP", Arial, sans-serif;
  font-size: 11px;
  line-height: 1.45;
  color: #111;
}

body { max-width: 980px; margin: 0 auto; padding: 0 10px; }

h1 { font-size: 18px; margin: 12px 0 8px; }
h2 { font-size: 14px; margin: 12px 0 6px; }
h3 { font-size: 12px; margin: 10px 0 4px; }

img {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  margin: 8px 0 10px;
  page-break-inside: avoid;
}

h1, h2, h3 { page-break-after: avoid; }
table, pre { page-break-inside: avoid; }

table {
  border-collapse: collapse;
  width: 100%;
  margin: 6px 0 10px;
}
th, td {
  border: 1px solid #ddd;
  padding: 4px 6px;
  vertical-align: top;
}
th { background: #f6f6f6; }

code, pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 10px;
}
pre {
  background: #f7f7f7;
  padding: 8px;
  overflow: auto;
}

hr { border: 0; border-top: 1px solid #ddd; margin: 12px 0; }

/* Print: use full page width, remove max-width constraint */
@media print {
  body { max-width: none; padding: 0; }
  a[href]:after { content: ""; } /* don't append URLs */
}
"""


def main() -> None:
  root = Path(__file__).resolve().parent
  md_path = root / "analysis_report.md"
  html_path = root / "analysis_report.html"

  md_text = md_path.read_text(encoding="utf-8")

  # Enable a few common extensions; keep it simple
  html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc"],
    output_format="html5",
  )

  html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SegmentAnalysis Report</title>
  <style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>
"""

  html_path.write_text(html, encoding="utf-8")
  print(f"Wrote: {html_path}")


if __name__ == "__main__":
  main()

