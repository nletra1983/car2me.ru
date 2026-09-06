#!/usr/bin/env python3

"""Convert Car2Me markdown reports to PDF (Cyrillic via Chromium)."""



from __future__ import annotations



import re

import sys

from pathlib import Path



import markdown

from playwright.sync_api import sync_playwright



LANDSCAPE_MARKER = re.compile(r"<!--\s*pdf:\s*landscape\s*-->", re.IGNORECASE)

FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

DISCLAIMER_SECTION = re.compile(r"\n##\s+Дисклеймер\s*\n.*", re.DOTALL | re.IGNORECASE)

DEFAULT_DISCLAIMER = (
    "Дисклеймер: Car2Me — подбор моделей, не брокер. "
    "Поиск и покупка конкретного лота — на вашей стороне. "
    "Оценки «под ключ» — ориентир по рынку; перед покупкой пересчитайте с брокером."
)





def strip_frontmatter(text: str) -> str:

    return FRONTMATTER.sub("", text, count=1)





def parse_pdf_options(text: str) -> tuple[str, bool]:

    landscape = bool(LANDSCAPE_MARKER.search(text))

    text = LANDSCAPE_MARKER.sub("", text, count=1)

    return text, landscape





CSS = """

@page { size: A4; margin: 14mm 12mm 11mm 12mm; }

body {

    font-family: "Segoe UI", Arial, sans-serif;

    font-size: 10pt;

    line-height: 1.4;

    color: #111;

}

h1 { font-size: 18pt; margin: 0 0 10pt 0; page-break-after: avoid; }

h2 { font-size: 13pt; margin: 14pt 0 6pt 0; page-break-after: avoid; }

h2.page-break { page-break-before: always; margin-top: 0; }

h3 { font-size: 11pt; margin: 10pt 0 4pt 0; page-break-after: avoid; break-after: avoid-page; }

.model-block {

    page-break-inside: avoid;

    break-inside: avoid-page;

    margin-bottom: 6pt;

}

h4 { font-size: 10pt; margin: 8pt 0 3pt 0; font-weight: 600; }

p, li { margin: 0 0 5pt 0; }

ul, ol { margin: 6pt 0 10pt 18pt; padding: 0; }

hr { border: none; border-top: 1px solid #ccc; margin: 10pt 0; }

table {

    width: 100%;

    border-collapse: collapse;

    margin: 6pt 0 10pt 0;

    font-size: 8.5pt;

    page-break-inside: avoid;

}

th, td {

    border: 1px solid #999;

    padding: 4pt 5pt;

    vertical-align: top;

    text-align: left;

}

th { background: #eee; font-weight: 600; }

em { color: #444; }

small { font-size: 85%; color: #444; }



/* Словарь терминов */

.glossary {

    margin: 6pt 0 12pt 0;

    padding: 8pt 10pt;

    background: #f8f9fa;

    border: 1px solid #ddd;

    border-radius: 4pt;

    font-size: 8pt;

    line-height: 1.4;

    column-count: 2;

    column-gap: 16pt;

}

.glossary dl { margin: 0; }

.glossary dt { font-weight: 600; display: inline; }

.glossary dt::after { content: " — "; font-weight: 400; }

.glossary dd { display: inline; margin: 0 0 4pt 0; }

.glossary dd::after { content: ""; display: block; margin-bottom: 3pt; }

.glossary-title { font-size: 11pt; margin: 0 0 6pt 0; }

.glossary-block { margin-top: 12pt; }

.first-page { page-break-after: always; }

h2.section-title { font-size: 13pt; margin: 0 0 8pt 0; }

.col-profile {

    font-size: 9.5pt;

    line-height: 1.45;

    margin-bottom: 10pt;

}

.matrix-tail {

    page-break-before: always;

    padding-top: 4pt;

    page-break-inside: avoid;

}

.matrix-summary { font-size: 9pt; margin: 0 0 8pt 0; color: #333; }

.matrix-subhead { font-size: 10pt; margin: 8pt 0 4pt 0; }

.conflicts-table { font-size: 8.5pt; margin-top: 4pt; }

.content-wrap { }

.pdf-footer { display: none; }



/* Профиль + приоритеты — вертикальный стек */

.col-profile p { margin-bottom: 6pt; }

.priorities-three-col {

    display: grid;

    grid-template-columns: 1fr 1fr 1fr;

    gap: 10pt;

    font-size: 8.5pt;

    line-height: 1.35;

    margin-bottom: 4pt;

}

.prio-col {

    border: 1px solid #ccc;

    border-radius: 4pt;

    padding: 6pt 8pt;

    background: #fafafa;

}

.prio-col h4 { margin: 0 0 4pt 0; font-size: 9pt; }

.prio-col ul { margin: 0; padding-left: 14pt; }

.prio-col li { margin-bottom: 2pt; }

.prio-crit { border-top: 3pt solid #8b0000; }

.prio-imp { border-top: 3pt solid #e65100; }

.prio-wish { border-top: 3pt solid #666; }



/* Матрица моделей — стиль как риски */

.matrix-section { margin: 6pt 0 14pt 0; }

.matrix-section > p { font-size: 8.5pt; color: #444; margin-bottom: 6pt; }

.matrix-section table {

    font-size: 8.5pt;

    page-break-inside: auto;

}

.matrix-section th, .matrix-section td {

    padding: 4pt 5pt;

    line-height: 1.3;

    vertical-align: top;

}

.score-cell { display: block; }

.score-val {

    display: inline-block;

    font-size: 11pt;

    font-weight: 700;

    color: #111;

    margin-bottom: 2pt;

}

.score-note {

    display: block;

    font-size: 7.5pt;

    line-height: 1.25;

    margin-top: 1pt;

}

.score-note.plus { color: #2e7d32; }

.score-note.minus { color: #8b0000; }

.score-note.neutral { color: #555; font-style: italic; }

.matrix-legend {

    margin: 4pt 0 8pt 0;

    font-size: 8pt;

    color: #444;

}



/* Риски и минусы */

.risks-section { margin-top: 8pt; }

.sig-legend {

    margin: 4pt 0 8pt 0;

    font-size: 8pt;

    color: #444;

}

.sig {

    display: inline-block;

    font-size: 7pt;

    font-weight: 700;

    padding: 1pt 6pt;

    border-radius: 3pt;

    margin-bottom: 3pt;

    line-height: 1.2;

    letter-spacing: 0.02em;

}

.sig-high {

    background: #fde8e8;

    color: #8b0000;

    border: 1px solid #d4a0a0;

}

.sig-med {

    background: #fff3e0;

    color: #e65100;

    border: 1px solid #ffcc80;

}

.sig-low {

    background: #f0f0f0;

    color: #666;

    border: 1px solid #ccc;

}

.sig-ok {

    background: #e8f5e9;

    color: #2e7d32;

    border: 1px solid #a5d6a7;

    font-weight: 600;

}

.not-minus-text {

    display: block;

    font-size: 7pt;

    line-height: 1.35;

    color: #2e7d32;

}

.not-minus-detail {

    display: block;

    font-size: 6.5pt;

    color: #555;

    margin-top: 2pt;

    font-style: italic;

}

.risks-empty { color: #999; font-size: 7pt; text-align: center; }

.risks-section table { font-size: 8pt; page-break-inside: auto; }

.risks-section th, .risks-section td { padding: 5pt 6pt; }

.downside-cell .downside-text {

    display: block;

    font-size: 7.5pt;

    line-height: 1.35;

    color: #222;

}

.downside-cell .downside-impact {

    display: block;

    font-size: 7pt;

    color: #555;

    margin-top: 3pt;

    font-style: italic;

}

.sig-legend .sig { margin-right: 6pt; margin-bottom: 0; }

"""



CSS_LANDSCAPE = """

@page { size: A4 landscape; margin: 6mm 5mm 10mm 5mm; }

body.landscape { font-size: 8.5pt; }

body.landscape h2 { font-size: 12pt; margin-top: 10pt; }

body.landscape .matrix-section table { font-size: 8.5pt; }

body.landscape .matrix-section .score-val { font-size: 11.5pt; }

body.landscape .matrix-section .score-note { font-size: 7.5pt; }

body.landscape .matrix-legend { font-size: 8.5pt; }

body.landscape .glossary { font-size: 7.5pt; }

body.landscape .priorities-three-col { font-size: 8pt; }

body.landscape .matrix-section th,

body.landscape .matrix-section td {

    padding: 6pt 5pt;

    line-height: 1.35;

    min-height: 22pt;

}

body.landscape .col-priorities table { font-size: 7.5pt; }

body.landscape .risks-section table { font-size: 7.5pt; }

body.landscape table:not(.matrix-section table):not(.risks-section table):not(.col-priorities table) {

    font-size: 7.5pt;

}

"""





def wrap_model_blocks(html: str) -> str:

    """Keep h3 comment blocks from splitting across pages."""

    parts = re.split(r"(?=<h3>)", html)

    if len(parts) <= 1:

        return html

    out = [parts[0]]

    for chunk in parts[1:]:

        if chunk.startswith("<h3>"):

            out.append(f'<div class="model-block">{chunk}</div>')

        else:

            out.append(chunk)

    return "".join(out)





def build_footer_html(*, landscape: bool) -> str:

    text = DEFAULT_DISCLAIMER.replace("&", "&amp;").replace("<", "&lt;")

    font = "8.5pt" if landscape else "10pt"

    side = "5mm" if landscape else "12mm"

    return (

        f'<div style="width:100%;box-sizing:border-box;font-size:{font};'

        f"line-height:1.4;color:#111;padding:0 {side};margin:0;"

        f'font-family:Segoe UI,Arial,sans-serif;">'

        f"{text}</div>"

    )





def md_to_html(text: str) -> str:

    html = markdown.markdown(

        text,

        extensions=["tables", "fenced_code", "sane_lists", "md_in_html"],

        output_format="html5",

    )

    return wrap_model_blocks(html)





def md_to_pdf(md_path: Path, pdf_path: Path | None = None) -> Path:

    pdf_path = pdf_path or md_path.with_suffix(".pdf")

    raw = md_path.read_text(encoding="utf-8")

    raw = strip_frontmatter(raw)

    raw = DISCLAIMER_SECTION.sub("", raw).rstrip()

    raw, landscape = parse_pdf_options(raw)



    html_body = md_to_html(raw)

    css = CSS + (CSS_LANDSCAPE if landscape else "")

    body_class = ' class="landscape"' if landscape else ""

    html = f"""<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="utf-8"/>

<title>{md_path.stem}</title>

<style>{css}</style>

</head>

<body{body_class}><div class="content-wrap">{html_body}</div></body>

</html>"""



    margin = (

        {"top": "6mm", "right": "5mm", "bottom": "11mm", "left": "5mm"}

        if landscape

        else {"top": "14mm", "right": "12mm", "bottom": "13mm", "left": "12mm"}

    )



    with sync_playwright() as p:

        browser = p.chromium.launch()

        page = browser.new_page()

        page.set_content(html, wait_until="load")

        page.pdf(

            path=str(pdf_path),

            format="A4",

            landscape=landscape,

            margin=margin,

            print_background=True,

            prefer_css_page_size=True,

            display_header_footer=True,

            header_template="<span></span>",

            footer_template=build_footer_html(landscape=landscape),

        )

        browser.close()

    return pdf_path





def main(argv: list[str]) -> int:

    if len(argv) < 2:

        print("Usage: md_to_pdf.py path/to/report.md [path/to/report.pdf]", file=sys.stderr)

        return 1

    md_path = Path(argv[1]).resolve()

    pdf_path = Path(argv[2]).resolve() if len(argv) > 2 else md_path.with_suffix(".pdf")

    if not md_path.exists():

        print(f"Not found: {md_path}", file=sys.stderr)

        return 1

    out = md_to_pdf(md_path, pdf_path)

    print(f"OK: {out} ({out.stat().st_size // 1024} KB)")

    return 0





if __name__ == "__main__":

    raise SystemExit(main(sys.argv))


