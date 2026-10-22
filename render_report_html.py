# -*- coding: utf-8 -*-
"""Render report_v2.md to a styled HTML file for PDF printing.

Uses a proper academic layout: tables, justified text, first-line indent,
section numbering, print-optimized CSS.
"""
import markdown

md_text = open("report_v2.md", encoding="utf-8").read()
body = markdown.markdown(md_text, extensions=["extra", "sane_lists"])

html_doc = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>哭泣的观察者：搭配词视角下《老残游记》的人物空间</title>
<style>
  @page {
    size: A4;
    margin: 2.2cm 2.4cm;
    @bottom-center {
      content: counter(page);
      font-family: "Times New Roman", serif;
      font-size: 10pt;
      color: #555;
    }
  }
  * { box-sizing: border-box; }
  body {
    font-family: "Microsoft YaHei", "PingFang SC", "SimSun", serif;
    font-size: 11.5pt;
    line-height: 1.9;
    color: #1a1a1a;
    text-align: justify;
    text-justify: inter-ideograph;
    max-width: 760px;
    margin: 0 auto;
    padding: 1em 0.5em;
  }
  h1 {
    font-size: 17pt;
    text-align: center;
    margin: 0.5em 0 1.2em;
    line-height: 1.5;
  }
  h2 {
    font-size: 13.5pt;
    margin: 1.8em 0 0.7em;
    padding-left: 0.5em;
    border-left: 4px solid #8b2f2f;
    page-break-after: avoid;
  }
  p { margin: 0.6em 0; text-indent: 2em; }
  h1 + p, h2 + p { text-indent: 0; }
  blockquote {
    margin: 0.8em 1.5em;
    padding: 0.4em 1em;
    border-left: 3px solid #c9b8b8;
    color: #444;
    background: #faf7f5;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 10pt;
    page-break-inside: avoid;
  }
  th, td {
    border: 1px solid #b9b0a4;
    padding: 5px 8px;
    text-align: left;
    vertical-align: top;
  }
  th { background: #f3e9e9; font-weight: 600; }
  tr:nth-child(even) td { background: #faf8f6; }
  strong { color: #5a2020; }
  a { color: #8b2f2f; text-decoration: none; }
  ol, ul { padding-left: 2em; }
  li { margin: 0.25em 0; }
  em { font-style: italic; }
  @media print {
    body { padding: 0; }
    a { color: inherit; }
  }
</style>
</head>
<body>
""" + body + """
</body>
</html>"""

with open("report_v2_print.html", "w", encoding="utf-8") as f:
    f.write(html_doc)
print("Wrote report_v2_print.html")
