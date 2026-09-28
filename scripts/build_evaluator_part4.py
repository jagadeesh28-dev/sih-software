"""
EGREEN QUANTA — SIH26138
Evaluator Evidence Package Builder — Part 4:
99_DETAILED_BACKUP/
1. END_TO_END_VERIFICATION_REPORT.pdf
2. END_TO_END_AUDIT_RAW.pdf
3. Detailed_Test_Evidence.pdf
"""

import os
import sys
import re
import html
import subprocess
import pymupdf

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(REPO_ROOT, ".."))
EVIDENCE_DIR = os.path.join(WORKSPACE_ROOT, "EGREEN_QUANTA_SIH26138_EVIDENCE")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def file_url(path):
    return "file:///" + os.path.abspath(path).replace("\\", "/")

from generate_all_evaluator_documents import render_pdf

def md_to_styled_html(md_path, title, doc_type="DETAILED TECHNICAL BACKUP"):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    html_lines = []
    in_code = False
    in_table = False
    table_header_done = False
    in_list = False
    
    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        
        # Code block toggle
        if line.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                lang = line[3:].strip()
                html_lines.append(f"<pre style='background:#0f172a; color:#f8fafc; padding:8px 12px; border-radius:4px; font-size:7.5pt; overflow-x:auto; line-height:1.35; margin:6px 0;'><code class='{lang}'>")
                in_code = True
            continue
            
        if in_code:
            html_lines.append(html.escape(line))
            continue
            
        # Table handling
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            cells = [c.strip() for c in line.strip().split("|")[1:-1]]
            # Check separator
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                table_header_done = True
                continue
            if not in_table:
                html_lines.append("<table style='width:100%; border-collapse:collapse; margin:8px 0; font-size:8pt;'>")
                in_table = True
                table_header_done = False
                
            tag = "th" if not table_header_done else "td"
            row_html = "<tr>"
            for c in cells:
                # Format cell markdown
                c_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", c)
                c_fmt = re.sub(r"`(.*?)`", r"<code>\1</code>", c_fmt)
                style = "background:#0f172a; color:#ffffff; font-weight:600; padding:4px 6px; border:1px solid #0f172a;" if tag == "th" else "padding:4px 6px; border:1px solid #cbd5e1; color:#1e293b;"
                row_html += f"<{tag} style='{style}'>{c_fmt}</{tag}>"
            row_html += "</tr>"
            html_lines.append(row_html)
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
                table_header_done = False
                
        # List items
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            if not in_list:
                html_lines.append("<ul style='margin:4px 0 6px 16px; padding:0; font-size:8pt; line-height:1.4;'>")
                in_list = True
            item_text = line.strip()[2:]
            item_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item_text)
            item_fmt = re.sub(r"`(.*?)`", r"<code style='background:#f1f5f9; padding:1px 4px; border-radius:3px;'>\1</code>", item_fmt)
            html_lines.append(f"<li style='margin-bottom:2px;'>{item_fmt}</li>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
                
        # Empty lines
        if not line.strip():
            continue
            
        # Headers
        if line.startswith("# "):
            html_lines.append(f"<h1 style='font-size:13pt; color:#0f172a; border-bottom:2px solid #0284c7; padding-bottom:4px; margin:12px 0 6px 0;'>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2 style='font-size:10.5pt; color:#0f172a; border-left:3px solid #0284c7; padding-left:6px; margin:10px 0 4px 0; text-transform:uppercase;'>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3 style='font-size:9pt; color:#0369a1; margin:8px 0 3px 0;'>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("> "):
            quote_text = line[2:].strip()
            quote_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", quote_text)
            html_lines.append(f"<div style='border-left:3px solid #0284c7; background:#f0f9ff; padding:6px 10px; font-size:8pt; margin:6px 0; border-radius:0 4px 4px 0;'>{quote_fmt}</div>")
        else:
            p_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            p_text = re.sub(r"`(.*?)`", r"<code style='background:#f1f5f9; padding:1px 4px; border-radius:3px; font-size:7.8pt;'>\1</code>", p_text)
            html_lines.append(f"<p style='margin:0 0 4px 0; font-size:8pt; color:#334155; line-height:1.4;'>{p_text}</p>")

    if in_table:
        html_lines.append("</table>")
    if in_list:
        html_lines.append("</ul>")
    if in_code:
        html_lines.append("</code></pre>")

    body_content = "\n".join(html_lines)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4 portrait;
    margin: 14mm 16mm 14mm 16mm;
}}
* {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 8pt;
    line-height: 1.4;
}}
.header-box {{
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}}
.header-box .org {{
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #0369a1;
    font-weight: 700;
}}
.header-box .doc-title {{
    font-size: 13pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
}}
.header-box .doc-meta {{
    text-align: right;
    font-size: 7.5pt;
    color: #64748b;
    font-weight: 600;
}}
.badge-evidence {{
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    border: 1px solid #7dd3fc;
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 7pt;
    margin-bottom: 4px;
}}
table tr:nth-child(even) td {{
    background: #f8fafc;
}}
</style>
</head>
<body>

<div class="header-box">
    <div>
        <div class="org">Smart India Hackathon 2024 &bull; SIH26138</div>
        <div class="doc-title">{title}</div>
    </div>
    <div class="doc-meta">
        <div class="badge-evidence">{doc_type}</div>
        <div>Ministry of Ports, Shipping & Waterways</div>
    </div>
</div>

{body_content}

</body>
</html>"""
    return full_html


def build_backup_reports():
    print("\n--- Generating Part 4 Backup Reports ---")
    dest_dir = os.path.join(EVIDENCE_DIR, "99_DETAILED_BACKUP")
    
    # 1. END_TO_END_VERIFICATION_REPORT.pdf
    src_rep1 = os.path.join(REPO_ROOT, "reports", "END_TO_END_VERIFICATION_REPORT.md")
    out_pdf1 = os.path.join(dest_dir, "END_TO_END_VERIFICATION_REPORT.pdf")
    html1 = md_to_styled_html(src_rep1, "End-to-End System Verification Report", "FORMAL VERIFICATION REPORT")
    render_pdf(html1, out_pdf1)
    
    # 2. END_TO_END_AUDIT_RAW.pdf
    src_rep2 = os.path.join(REPO_ROOT, "reports", "END_TO_END_AUDIT_RAW.md")
    out_pdf2 = os.path.join(dest_dir, "END_TO_END_AUDIT_RAW.pdf")
    html2 = md_to_styled_html(src_rep2, "End-to-End System Audit Transcript (Raw)", "RAW AUDIT LOGS")
    render_pdf(html2, out_pdf2)

    # 3. Detailed_Test_Evidence.pdf
    src_rep3 = os.path.join(REPO_ROOT, "reports", "CERTIFICATION_READINESS_REPORT.md")
    out_pdf3 = os.path.join(dest_dir, "Detailed_Test_Evidence.pdf")
    html3 = md_to_styled_html(src_rep3, "Detailed Test Evidence & Certification Report", "CERTIFICATION READINESS REPORT")
    render_pdf(html3, out_pdf3)


if __name__ == "__main__":
    build_backup_reports()
    print("Part 4 documents generation complete.")
