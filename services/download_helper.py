"""
DIA Download Helper
Provides real file downloads from the sample_document folder.

- get_zip_download_link()      → base64 HTML <a> tag for the full ZIP bundle
- get_single_file_link(name)   → base64 HTML <a> tag for a single PDF
- get_sample_document_files()  → list of dicts describing each PDF in sample_document/
"""
import base64
import io
import os
import zipfile
from typing import Optional

# Path to the sample_document folder (relative to project root)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
SAMPLE_DOC_DIR = os.path.join(_PROJECT_ROOT, "sample_document")


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _b64_data_uri(data: bytes, mime: str = "application/octet-stream") -> str:
    """Encode bytes as a base64 data URI."""
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _html_download_anchor(
    data_uri: str,
    filename: str,
    label: str,
    css_class: str = "zip-link",
    icon: str = "📥",
) -> str:
    """Return an HTML <a download=...> tag usable inside st.markdown(unsafe_allow_html=True)."""
    return (
        f'<a href="{data_uri}" download="{filename}" class="{css_class}">'
        f"{icon} {label}"
        f"</a>"
    )


# ──────────────────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_sample_document_files() -> list:
    """
    Return a list of dicts for every PDF in sample_document/.
    Each dict has: name, path, size_kb
    """
    files = []
    if not os.path.isdir(SAMPLE_DOC_DIR):
        return files
    for fname in sorted(os.listdir(SAMPLE_DOC_DIR)):
        fpath = os.path.join(SAMPLE_DOC_DIR, fname)
        if os.path.isfile(fpath) and fname.lower().endswith(".pdf"):
            size_kb = max(1, os.path.getsize(fpath) // 1024)
            files.append({"name": fname, "path": fpath, "size_kb": size_kb})
    return files


def build_sample_zip() -> bytes:
    """
    Create an in-memory ZIP containing every file in sample_document/.
    Returns the raw ZIP bytes.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in get_sample_document_files():
            zf.write(item["path"], arcname=item["name"])
    buf.seek(0)
    return buf.read()


def get_zip_download_link(
    label: str = "Download All as ZIP",
    filename: str = "sample_documents.zip",
    css_class: str = "zip-link",
) -> str:
    """
    Return a fully self-contained HTML <a download> tag for the sample_document ZIP.
    Safe to embed in st.markdown(unsafe_allow_html=True).
    """
    try:
        zip_bytes = build_sample_zip()
        uri = _b64_data_uri(zip_bytes, "application/zip")
        return _html_download_anchor(uri, filename, label, css_class, icon="📦")
    except Exception as exc:
        return f'<span style="color:#ff4444;">ZIP error: {exc}</span>'


def get_single_file_link(
    filename: Optional[str] = None,
    label: Optional[str] = None,
    css_class: str = "zip-link",
) -> str:
    """
    Return an HTML <a download> tag for a single PDF.
    If filename is None or not found in sample_document/, falls back to the first file.
    """
    files = get_sample_document_files()
    if not files:
        return '<span style="color:#ff4444;">No sample documents found.</span>'

    target = None
    if filename:
        for f in files:
            if f["name"].lower() == filename.lower():
                target = f
                break
    if target is None:
        target = files[0]

    try:
        with open(target["path"], "rb") as fh:
            data = fh.read()
        uri = _b64_data_uri(data, "application/pdf")
        display_label = label or f"Download {target['name']}"
        return _html_download_anchor(uri, target["name"], display_label, css_class, icon="📥")
    except Exception as exc:
        return f'<span style="color:#ff4444;">File error: {exc}</span>'


# ──────────────────────────────────────────────────────────────────────────────
#  PDF Verification Report Generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_verification_report_pdf(data: dict) -> bytes:
    """
    Generate a detailed, attractive PDF verification report from verify result data.
    Returns raw PDF bytes suitable for base64 encoding and download.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.platypus import PageBreak
        from io import BytesIO
        from datetime import datetime

        buf = BytesIO()

        # ── Colour palette (Deutsche Bank Royal Blue theme) ─────────────────
        DB_BLUE     = colors.HexColor("#00214D")   # deep navy
        DB_CYAN     = colors.HexColor("#00B4D8")   # accent cyan
        DB_LIGHT    = colors.HexColor("#E8F4FD")   # light bg rows
        DB_WHITE    = colors.white
        DB_GREEN    = colors.HexColor("#00C896")   # pass
        DB_RED      = colors.HexColor("#FF4444")   # fail
        DB_AMBER    = colors.HexColor("#FFA500")   # warn
        DB_GREY     = colors.HexColor("#6B7280")
        DB_DARK     = colors.HexColor("#0A1628")

        PAGE_W, PAGE_H = A4
        MARGIN = 18 * mm

        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=22 * mm,
            bottomMargin=18 * mm,
        )

        styles = getSampleStyleSheet()

        def _style(name, **kw):
            s = ParagraphStyle(name, parent=styles["Normal"], **kw)
            return s

        # Shared styles
        s_title   = _style("Title",    fontSize=22, textColor=DB_WHITE,     alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4)
        s_sub     = _style("Sub",      fontSize=10, textColor=DB_CYAN,      alignment=TA_CENTER, fontName="Helvetica",      spaceAfter=2)
        s_meta    = _style("Meta",     fontSize=8,  textColor=DB_GREY,      alignment=TA_CENTER, fontName="Helvetica",      spaceAfter=2)
        s_section = _style("Section",  fontSize=12, textColor=DB_BLUE,      fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4, borderPad=2)
        s_body    = _style("Body",     fontSize=9,  textColor=DB_DARK,      fontName="Helvetica",   spaceAfter=3, leading=14)
        s_step    = _style("Step",     fontSize=8,  textColor=DB_DARK,      fontName="Helvetica",   spaceAfter=2, leftIndent=8, leading=12)
        s_verdict = _style("Verdict",  fontSize=13, textColor=DB_WHITE,     fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
        s_label   = _style("Label",    fontSize=8,  textColor=DB_GREY,      fontName="Helvetica-Bold", spaceAfter=1)
        s_value   = _style("Value",    fontSize=10, textColor=DB_BLUE,      fontName="Helvetica-Bold", spaceAfter=4)

        # ── Helper: coloured box around header ───────────────────────────────
        def header_block():
            now_str = datetime.now().strftime("%d %B %Y  •  %H:%M:%S")
            ref_str = data.get("agreement_type", "Document Verification")
            party   = data.get("counterparty", "—")
            prod    = data.get("product_type", "—")
            verified_on = data.get("verified_on", now_str)

            header_data = [
                [Paragraph("D.I.A — DOCUMENT VERIFICATION REPORT", s_title)],
                [Paragraph("Deutsche Bank · AI Legal Agreement Assistant", s_sub)],
                [Paragraph(f"Generated: {verified_on}", s_meta)],
            ]
            t = Table(header_data, colWidths=[PAGE_W - 2 * MARGIN])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), DB_BLUE),
                ("TOPPADDING",    (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("ROUNDEDCORNERS", [6]),
            ]))
            return t

        def summary_cards():
            passed   = data.get("passed", 0)
            total    = data.get("total_documents", 0)
            failed   = total - passed
            status   = data.get("status", "—").replace("✅", "").replace("⚠️", "").replace("❌", "").strip()
            agr_type = data.get("agreement_type", "—") or "—"
            party    = data.get("counterparty", "—") or "—"
            prod     = data.get("product_type", "—") or "—"

            pct = int(100 * passed / total) if total else 0

            # ── Metric cards (build rows directly, no .text hack) ────────────
            labels = ["TOTAL DOCS", "PASSED", "FAILED", "PASS RATE"]
            values = [str(total), str(passed), str(failed), f"{pct}%"]
            bgcolors = [DB_BLUE, DB_GREEN, DB_RED if failed else DB_GREEN, DB_CYAN]

            row_labels = [
                Paragraph(lb, _style(f"lbl{i}", fontSize=7, textColor=colors.white,
                                     fontName="Helvetica-Bold", alignment=TA_CENTER))
                for i, lb in enumerate(labels)
            ]
            row_values = [
                Paragraph(vl, _style(f"val{i}", fontSize=18, textColor=colors.white,
                                     fontName="Helvetica-Bold", alignment=TA_CENTER))
                for i, vl in enumerate(values)
            ]

            col_w = (PAGE_W - 2 * MARGIN) / 4
            metric_tbl = Table([row_labels, row_values], colWidths=[col_w] * 4)
            ts_cmds = [
                ("TOPPADDING",    (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING",   (0, 0), (-1, -1), 4),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
                ("GRID",          (0, 0), (-1, -1), 0.5, colors.white),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ]
            for i, bg in enumerate(bgcolors):
                ts_cmds.append(("BACKGROUND", (i, 0), (i, -1), bg))
            metric_tbl.setStyle(TableStyle(ts_cmds))

            # ── Info row ─────────────────────────────────────────────────────
            info_text = (
                f"Agreement: <b>{agr_type}</b> &nbsp;·&nbsp; "
                f"Counterparty: <b>{party}</b> &nbsp;·&nbsp; "
                f"Product: <b>{prod}</b> &nbsp;·&nbsp; "
                f"Status: <b>{status}</b>"
            )
            info_tbl = Table(
                [[Paragraph(info_text, s_body)]],
                colWidths=[PAGE_W - 2 * MARGIN],
            )
            info_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), DB_LIGHT),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ]))

            return metric_tbl, info_tbl

        def steps_table():
            steps = data.get("verification_steps", [])
            if not steps:
                return None
            rows = [[Paragraph(f"✔  {s}", s_step)] for s in steps]
            t = Table(rows, colWidths=[PAGE_W - 2*MARGIN])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(-1,-1), colors.HexColor("#F0F7FF")),
                ("TOPPADDING",    (0,0),(-1,-1), 3),
                ("BOTTOMPADDING", (0,0),(-1,-1), 3),
                ("LEFTPADDING",   (0,0),(-1,-1), 8),
                ("RIGHTPADDING",  (0,0),(-1,-1), 8),
                ("ROWBACKGROUNDS", (0,0),(-1,-1), [DB_LIGHT, colors.white]),
                ("LINEBELOW", (0,0),(-1,-1), 0.3, colors.HexColor("#D1E8F5")),
            ]))
            return t

        def docs_table():
            """
            Build a per-document section showing all 15 checks from
            document_generation_rules.xlsx Verification Checklist sheet.
            Each document gets its own header row + 15-row check table.
            """
            doc_results = data.get("document_results", [])
            if not doc_results:
                return None

            CHECK_META = [
                ("step_01_header",          "1",  "Header Present",          "Text comparison"),
                ("step_02_footer",          "2",  "Footer Present",          "Pattern match"),
                ("step_03_sections",        "3",  "Required Sections",       "Section scan"),
                ("step_04_fields",          "4",  "Required Fields",         "Field validation"),
                ("step_05_signature",       "5",  "Digital Signature",       "Crypto check"),
                ("step_06_product_type",    "6",  "Product Type Config",     "Config match"),
                ("step_07_page_count",      "7",  "Min Page Count",          "Page count"),
                ("step_08_party_details",   "8",  "Party Details",           "Party name check"),
                ("step_09_date_validity",   "9",  "Date Validity",           "Date format check"),
                ("step_10_notarisation",    "10", "Notarisation",            "Stamp check"),
                ("step_11_ip_rights",       "11", "IP Rights Clause",        "Section search"),
                ("step_12_audit_trail",     "12", "Audit Trail",             "Log check"),
                ("step_13_confidentiality", "13", "Confidentiality Level",   "Clause check"),
                ("step_14_compliance_cert", "14", "Compliance Certification","Cert check"),
                ("step_15_zip_integrity",   "15", "ZIP Bundle Integrity",    "File count check"),
            ]

            def _chip_para(text, style_name="td"):
                if any(p in text for p in ("PASS", "\u2705", "VERIFIED")):
                    col = "#00C896"
                elif any(p in text for p in ("FAIL", "\u274c")):
                    col = "#FF4444"
                elif "N/A" in text or text in ("\u2014", "—"):
                    col = "#888888"
                else:
                    col = "#FFA500"
                return Paragraph(
                    '<font color="' + col + '"><b>' + text + '</b></font>',
                    _style(style_name, fontSize=7, fontName="Helvetica", alignment=TA_CENTER)
                )

            cw = PAGE_W - 2 * MARGIN
            # Check table column widths: Step# | Check Name | Expected | Method | Result | Detail
            check_col_widths = [cw*0.05, cw*0.15, cw*0.22, cw*0.14, cw*0.10, cw*0.34]

            all_tables = []
            for doc_r in doc_results:
                doc_name = doc_r.get("document", "")
                overall  = doc_r.get("overall", "—")
                ck_pass  = doc_r.get("checks_passed", 0)
                ck_total = doc_r.get("checks_total", 0)
                ac       = doc_r.get("all_checks", {})

                if "VERIFIED" in overall:
                    hdr_bg  = DB_GREEN
                    hdr_txt = DB_WHITE
                elif "FAILED" in overall:
                    hdr_bg  = DB_RED
                    hdr_txt = DB_WHITE
                else:
                    hdr_bg  = DB_AMBER
                    hdr_txt = DB_WHITE

                # Document header row
                doc_hdr_data = [[
                    Paragraph(
                        "&#128196; " + doc_name,
                        _style("dh", fontSize=8, textColor=hdr_txt,
                               fontName="Helvetica-Bold")
                    ),
                    Paragraph(
                        overall + " | " + str(ck_pass) + "/" + str(ck_total) + " checks",
                        _style("ds", fontSize=7, textColor=hdr_txt,
                               fontName="Helvetica", alignment=TA_RIGHT)
                    ),
                ]]
                doc_hdr_tbl = Table(doc_hdr_data, colWidths=[cw * 0.70, cw * 0.30])
                doc_hdr_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0),(-1,-1), hdr_bg),
                    ("TOPPADDING",    (0,0),(-1,-1), 5),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 5),
                    ("LEFTPADDING",   (0,0),(-1,-1), 8),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 8),
                    ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ]))

                # 15-check table for this document
                check_hdr = [
                    Paragraph("<b>#</b>",      _style("ch", fontSize=7, textColor=DB_WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
                    Paragraph("<b>Check</b>",  _style("ch", fontSize=7, textColor=DB_WHITE, fontName="Helvetica-Bold")),
                    Paragraph("<b>Expected</b>",_style("ch", fontSize=7, textColor=DB_WHITE, fontName="Helvetica-Bold")),
                    Paragraph("<b>Method</b>", _style("ch", fontSize=7, textColor=DB_WHITE, fontName="Helvetica-Bold")),
                    Paragraph("<b>Result</b>", _style("ch", fontSize=7, textColor=DB_WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
                    Paragraph("<b>Detail</b>", _style("ch", fontSize=7, textColor=DB_WHITE, fontName="Helvetica-Bold")),
                ]
                check_rows = [check_hdr]
                for sk, num, check_lbl, _ in CHECK_META:
                    chk    = ac.get(sk, {})
                    res    = chk.get("result",   "—")
                    exp    = chk.get("expected", "—")
                    det    = chk.get("detail",   "—")
                    mth    = chk.get("method",   "—")
                    is_na  = "N/A" in res
                    row_opacity_style = {"textColor": DB_GREY} if is_na else {}
                    check_rows.append([
                        Paragraph(num, _style("cn", fontSize=7, fontName="Helvetica-Bold",
                                              alignment=TA_CENTER, **row_opacity_style)),
                        Paragraph(check_lbl, _style("cl", fontSize=7, fontName="Helvetica",
                                                     **row_opacity_style)),
                        Paragraph(exp[:45] + ("…" if len(exp) > 45 else ""),
                                  _style("ce", fontSize=6, fontName="Helvetica",
                                         textColor=DB_GREY)),
                        Paragraph(mth, _style("cm", fontSize=6, fontName="Helvetica",
                                              textColor=DB_GREY)),
                        _chip_para(res, "cr"),
                        Paragraph(det[:60] + ("…" if len(det) > 60 else ""),
                                  _style("cd", fontSize=6, fontName="Helvetica",
                                         textColor=DB_GREY)),
                    ])

                check_tbl = Table(check_rows, colWidths=check_col_widths, repeatRows=1)
                check_ts = [
                    ("BACKGROUND",    (0,0),(-1,0),  DB_BLUE),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1), [DB_LIGHT, colors.white]),
                    ("TOPPADDING",    (0,0),(-1,-1), 3),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
                    ("LEFTPADDING",   (0,0),(-1,-1), 4),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 4),
                    ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#C5DFF0")),
                    ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                    ("ALIGN",         (0,0),(0,-1),  "CENTER"),
                    ("ALIGN",         (4,0),(4,-1),  "CENTER"),
                ]
                check_tbl.setStyle(TableStyle(check_ts))

                all_tables.append(KeepTogether([doc_hdr_tbl, check_tbl, Spacer(1, 3*mm)]))

            return all_tables

        def verdict_block():
            passed = data.get("passed", 0)
            total  = data.get("total_documents", 0)
            failed = total - passed
            if failed == 0:
                txt = f"✅  ALL {total} DOCUMENTS PASSED VERIFICATION"
                bg  = DB_GREEN
            elif failed == total:
                txt = f"❌  ALL {total} DOCUMENTS FAILED VERIFICATION"
                bg  = DB_RED
            else:
                txt = f"⚠️  {passed} of {total} DOCUMENTS PASSED  ·  {failed} REQUIRE ATTENTION"
                bg  = DB_AMBER

            t = Table([[Paragraph(txt, s_verdict)]], colWidths=[PAGE_W - 2*MARGIN])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), bg),
                ("TOPPADDING",    (0,0),(-1,-1), 12),
                ("BOTTOMPADDING", (0,0),(-1,-1), 12),
                ("LEFTPADDING",   (0,0),(-1,-1), 10),
                ("RIGHTPADDING",  (0,0),(-1,-1), 10),
                ("ROUNDEDCORNERS",[6]),
            ]))
            return t

        def footer_block():
            msg = data.get("message", "Verification complete.")
            note = (
                "This report was automatically generated by D.I.A — AI Legal Agreement Assistant. "
                "For queries, contact your Deutsche Bank Relationship Manager."
            )
            rows = [
                [Paragraph(f"<b>Summary:</b> {msg}", s_body)],
                [Paragraph(note, _style("note", fontSize=7, textColor=DB_GREY, fontName="Helvetica"))],
                [Paragraph(f"<font color='#00B4D8'>© Deutsche Bank · D.I.A System · Confidential</font>",
                           _style("copy", fontSize=7, textColor=DB_GREY, alignment=TA_CENTER))],
            ]
            t = Table(rows, colWidths=[PAGE_W - 2*MARGIN])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#F8FAFC")),
                ("LINEABOVE",     (0,0),(-1,0),  1, DB_CYAN),
                ("TOPPADDING",    (0,0),(-1,-1), 6),
                ("BOTTOMPADDING", (0,0),(-1,-1), 5),
                ("LEFTPADDING",   (0,0),(-1,-1), 8),
                ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ]))
            return t

        # ── Assemble document ────────────────────────────────────────────────
        story = []
        story.append(header_block())
        story.append(Spacer(1, 6*mm))

        m_tbl, i_tbl = summary_cards()
        story.append(m_tbl)
        story.append(Spacer(1, 3*mm))
        story.append(i_tbl)
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("Verification Process", s_section))
        story.append(HRFlowable(width="100%", thickness=1, color=DB_CYAN, spaceAfter=4))
        st_tbl = steps_table()
        if st_tbl:
            story.append(st_tbl)
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("Document-Level Results — All 15 Checks", s_section))
        story.append(HRFlowable(width="100%", thickness=1, color=DB_CYAN, spaceAfter=4))
        d_tbls = docs_table()
        # docs_table now returns a list of KeepTogether blocks (one per document)
        if d_tbls:
            if isinstance(d_tbls, list):
                for blk in d_tbls:
                    story.append(blk)
            else:
                story.append(d_tbls)
        story.append(Spacer(1, 5*mm))

        story.append(verdict_block())
        story.append(Spacer(1, 5*mm))
        story.append(footer_block())

        doc.build(story)
        buf.seek(0)
        return buf.read()

    except Exception as exc:
        # Fallback: minimal plain text PDF via reportlab
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 780, "DIA Verification Report")
        c.setFont("Helvetica", 10)
        c.drawString(50, 760, f"Status: {data.get('status','')}")
        c.drawString(50, 745, f"Passed: {data.get('passed',0)} / {data.get('total_documents',0)}")
        c.drawString(50, 725, f"Error generating full report: {exc}")
        c.save()
        buf.seek(0)
        return buf.read()


def get_verification_report_link(
    data: dict,
    label: str = "📄 Download Verification Report (PDF)",
    css_class: str = "zip-link",
) -> str:
    """
    Generate a PDF verification report and return an HTML <a download> tag.
    """
    try:
        pdf_bytes = generate_verification_report_pdf(data)
        from datetime import datetime
        fname = "DIA_Verification_Report_{}.pdf".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        uri = _b64_data_uri(pdf_bytes, "application/pdf")
        return _html_download_anchor(uri, fname, label, css_class, icon="📄")
    except Exception as exc:
        return f'<span style="color:#ff4444;">PDF error: {exc}</span>'
