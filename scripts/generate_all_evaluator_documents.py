"""
EGREEN QUANTA — SIH26138
Master PDF Document Generator for Smart India Hackathon Evaluator Package
Generates 16 publication-grade, verified evidence PDFs with exact page constraints.
Uses Microsoft Edge headless engine and verifies page counts with PyMuPDF.
"""

import os
import sys
import subprocess
import pymupdf

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(REPO_ROOT, ".."))
EVIDENCE_DIR = os.path.join(WORKSPACE_ROOT, "EGREEN_QUANTA_SIH26138_EVIDENCE")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print(f"=== EGREEN QUANTA DOCUMENT GENERATOR ===")
print(f"Repo Root: {REPO_ROOT}")
print(f"Evidence Root: {EVIDENCE_DIR}")

def file_url(path):
    return "file:///" + os.path.abspath(path).replace("\\", "/")

# Common CSS Stylesheet
BASE_CSS = """
@page {
    size: A4 portrait;
    margin: 10mm 12mm 10mm 12mm;
}
* {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 8.8pt;
    line-height: 1.4;
}
.page {
    width: 100%;
    height: 275mm;
    max-height: 275mm;
    overflow: hidden;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    padding-bottom: 2mm;
}
.page:last-child {
    page-break-after: avoid;
}
.header {
    border-bottom: 2px solid #0284c7;
    padding-bottom: 4px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.header-left .org {
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #0369a1;
    font-weight: 700;
}
.header-left .title {
    font-size: 11pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
}
.header-right {
    text-align: right;
    font-size: 7.5pt;
    color: #64748b;
    font-weight: 600;
}
.footer {
    border-top: 1px solid #cbd5e1;
    padding-top: 4px;
    margin-top: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7.5pt;
    color: #64748b;
}
.footer-badge {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    padding: 1px 6px;
    border-radius: 3px;
    font-weight: 700;
    color: #0f172a;
    font-size: 7pt;
    letter-spacing: 0.5px;
}
.content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
h1, h2, h3, h4 {
    margin: 0;
    color: #0f172a;
    font-weight: 700;
}
h2 {
    font-size: 10pt;
    border-left: 3px solid #0284c7;
    padding-left: 6px;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
h3 {
    font-size: 9pt;
    color: #0369a1;
    margin-bottom: 2px;
}
p {
    margin: 0 0 4px 0;
    color: #334155;
}
.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 8px;
}
.card-blue {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 4px;
    padding: 8px;
}
.card-amber {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 4px;
    padding: 8px;
}
.card-emerald {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 4px;
    padding: 8px;
}
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
}
.grid-4 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 6px;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
}
th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #0f172a;
}
td {
    padding: 4px 6px;
    border: 1px solid #cbd5e1;
    color: #1e293b;
}
tr:nth-child(even) td {
    background: #f8fafc;
}
.badge-pass {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 7pt;
}
.badge-info {
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    border: 1px solid #7dd3fc;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 7pt;
}
.badge-warn {
    display: inline-block;
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fcd34d;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 7pt;
}
.stat-box {
    text-align: center;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 6px;
}
.stat-val {
    font-size: 13pt;
    font-weight: 800;
    color: #0369a1;
    line-height: 1.1;
}
.stat-lbl {
    font-size: 7pt;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 600;
    margin-top: 2px;
}
.callout {
    border-left: 3px solid #0284c7;
    background: #f0f9ff;
    padding: 6px 10px;
    font-size: 8pt;
    border-radius: 0 4px 4px 0;
}
.callout-amber {
    border-left: 3px solid #d97706;
    background: #fffbeb;
    padding: 6px 10px;
    font-size: 8pt;
    border-radius: 0 4px 4px 0;
}
ul {
    margin: 0;
    padding-left: 14px;
}
li {
    margin-bottom: 2px;
}
"""

def render_pdf(html_content, output_pdf_path, max_pages=None):
    temp_html = output_pdf_path.replace(".pdf", "_temp.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    file_uri = file_url(temp_html)
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=" + output_pdf_path,
        file_uri
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_html):
        os.remove(temp_html)
        
    doc = pymupdf.open(output_pdf_path)
    page_count = len(doc)
    doc.close()
    
    status = "[OK]"
    if max_pages and page_count > max_pages:
        status = f"[PAGE EXCEEDED: {page_count} > {max_pages}]"
    print(f"  {status} {os.path.basename(output_pdf_path)}: {page_count} pages (Size: {os.path.getsize(output_pdf_path):,} bytes)")
    return page_count

print("Base generator harness ready.")
