# -*- coding: utf-8 -*-
"""Convert report.md to report.pdf using fpdf2 (pure Python, no GTK needed).

Parses the markdown lightly (headings, bullets, bold, links) and renders
a clean Chinese-friendly PDF using a Windows system font.
"""
import re

from fpdf import FPDF

MD_PATH = "report.md"
PDF_PATH = "report.pdf"
FONT = r"C:\Windows\Fonts\msyh.ttc"  # Microsoft YaHei

md_text = open(MD_PATH, encoding="utf-8").read()


def clean(text: str) -> str:
    """Strip markdown inline syntax for plain rendering."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)   # links -> text
    text = text.replace("**", "")                            # bold markers
    text = text.replace("`", "")                             # code markers
    return text


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("msyh", "", 8)
            self.set_text_color(130, 130, 130)
            self.cell(0, 6, "词汇搭配与人物空间：《老残游记》中“老残”的搭配词分析",
                      align="C")
            self.ln(10)
            self.set_text_color(43, 43, 43)

    def footer(self):
        self.set_y(-15)
        self.set_font("msyh", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, str(self.page_no()), align="C")
        self.set_text_color(43, 43, 43)


pdf = PDF(format="A4")
pdf.add_font("msyh", "", FONT)
pdf.add_font("msyh", "B", FONT)
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_margins(20, 18, 20)
pdf.add_page()

for raw in md_text.split("\n"):
    line = raw.rstrip()
    if not line.strip():
        pdf.ln(2)
        continue

    if line.startswith("# "):          # H1 title
        pdf.set_font("msyh", "B", 16)
        pdf.multi_cell(0, 10, clean(line[2:]), align="C")
        pdf.ln(2)
        pdf.set_draw_color(139, 47, 47)
        pdf.set_line_width(0.6)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)
    elif line.startswith("## "):       # H2 section
        pdf.ln(3)
        pdf.set_font("msyh", "B", 13)
        pdf.set_text_color(139, 47, 47)
        pdf.multi_cell(0, 8, clean(line[3:]))
        pdf.set_text_color(43, 43, 43)
        pdf.set_draw_color(229, 225, 216)
        pdf.set_line_width(0.3)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(3)
    elif line.lstrip().startswith("- "):   # bullet
        pdf.set_font("msyh", "", 10.5)
        pdf.set_x(26)                      # indent bullet content
        pdf.cell(6, 7, "•")
        pdf.multi_cell(0, 7, clean(line.lstrip()[2:]))
        pdf.set_x(20)
    else:                              # body paragraph
        pdf.set_font("msyh", "", 10.5)
        pdf.multi_cell(0, 7, clean(line))

pdf.output(PDF_PATH)
print(f"Wrote {PDF_PATH}")
