"""
DIA Document API Service
All API calls now include product_type parameter.
Generates realistic document sets per agreement + product type.
"""
import uuid, time, random
from datetime import datetime, timedelta
from data.dummy_data import get_generation_rules, PRODUCT_TYPES
from services.download_helper import get_sample_document_files, get_zip_download_link

# Pre-load sample document file list once at module level
_SAMPLE_FILES = get_sample_document_files()
_SAMPLE_NAMES = [f["name"] for f in _SAMPLE_FILES]

def _sample_download_url(index: int = 0) -> str:
    """
    Return a sentinel URL that components.py will replace with a real
    base64 download link at render time.  We encode the sample file index
    so each document in a set can point to a different real file.
    """
    if _SAMPLE_NAMES:
        idx = index % len(_SAMPLE_NAMES)
        return f"__sample_download__:{_SAMPLE_NAMES[idx]}"
    return "#"

def _sample_zip_url() -> str:
    """Sentinel that components.py replaces with the real ZIP download link."""
    return "__sample_zip__"

AGREEMENT_TYPES_SHORT = {
    "non-disclosure agreement": "NDA", "nda": "NDA",
    "service agreement": "SA", "rental agreement": "RA",
    "lease agreement": "LA", "loan agreement": "LOA",
    "partnership deed": "PD", "memorandum of understanding": "MOU",
    "mou": "MOU", "employment contract": "EC",
    "vendor agreement": "VA", "consultancy agreement": "CA",
}

def _doc_id(prefix="DOC"):
    return f"{prefix}-{datetime.now().year}-{random.randint(100,999)}"

def _ref():
    return f"REF-{uuid.uuid4().hex[:8].upper()}"

def _expiry(days=365):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

def _generate_doc_list(agreement_type: str, product_type: str,
                       party: str, doc_id: str) -> list:
    """Generate a list of document names based on agreement type and product type."""
    short = AGREEMENT_TYPES_SHORT.get(agreement_type.lower(), agreement_type[:3].upper())
    party_slug = party.replace(" ", "_")[:15]
    year = datetime.now().year
    rules = get_generation_rules(agreement_type, product_type)
    sections = rules.get("required_sections", [])

    docs = []
    # Main agreement document
    docs.append({
        "name": f"{short}_{party_slug}_Main_{year}.pdf",
        "desc": f"Main {agreement_type} — covers {', '.join(sections[:3])} and more.",
        "sections": sections,
        "product_type": product_type,
        "header": rules.get("header", ""),
        "footer": rules.get("footer", ""),
        "pages": random.randint(rules.get("min_pages", 3),
                                rules.get("min_pages", 3) + 3),
    })
    # Annexure if MT101 or CC
    if product_type in ("MT101", "CC"):
        docs.append({
            "name": f"{short}_{party_slug}_Annexure_A_{year}.pdf",
            "desc": f"Annexure A: Detailed schedules and addendums for {agreement_type}.",
            "sections": ["Schedule A", "Definitions", "Supplementary Terms"],
            "product_type": product_type,
            "header": rules.get("header", "").replace("MAIN", "ANNEXURE A"),
            "footer": rules.get("footer", ""),
            "pages": random.randint(2, 4),
        })
    # Compliance cert for CC
    if product_type == "CC":
        docs.append({
            "name": f"{short}_{party_slug}_Compliance_{year}.pdf",
            "desc": f"Compliance certificate and regulatory sign-off for {agreement_type}.",
            "sections": ["Regulatory Compliance", "Audit Trail", "Sign-off Sheet"],
            "product_type": product_type,
            "header": rules.get("header", "") + " | COMPLIANCE",
            "footer": rules.get("footer", ""),
            "pages": random.randint(2, 3),
        })
    # Cover letter always
    docs.append({
        "name": f"{short}_{party_slug}_Cover_Letter_{year}.pdf",
        "desc": f"Formal cover letter accompanying the {agreement_type}.",
        "sections": ["Introduction", "Summary", "Signatories"],
        "product_type": product_type,
        "header": "COVER LETTER",
        "footer": rules.get("footer", ""),
        "pages": 1,
    })
    return docs


def call_create_agreement_api(detail1: str, detail2: str, detail3: str,
                               product_type: str = "EBICS") -> dict:
    """Create a new agreement. Returns agreement data + possible documents."""
    time.sleep(1.2)
    short = AGREEMENT_TYPES_SHORT.get(detail2.lower().strip(), detail2[:3].upper())
    doc_id = _doc_id(short)
    rules  = get_generation_rules(detail2, product_type)
    docs   = _generate_doc_list(detail2, product_type, detail1, doc_id)
    return {
        "status": "SUCCESS",
        "agreement_id": doc_id,
        "reference_number": _ref(),
        "agreement_type": detail2,
        "counterparty": detail1,
        "value_duration": detail3,
        "product_type": product_type,
        "generated_on": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
        "valid_until": _expiry(),
        "digitally_signed": "Yes — SHA-256",
        "required_sections": rules.get("required_sections", []),
        "required_fields": rules.get("required_fields", []),
        "possible_documents": docs,
        "message": f"Agreement created successfully. {len(docs)} documents can be generated.",
    }


def call_regenerate_agreement_api(doc: dict) -> dict:
    """Regenerate from existing doc record."""
    time.sleep(1.0)
    product_type = doc.get("product_type", "EBICS")
    agreement_type = doc.get("type", "Agreement")
    party = doc.get("party", "Party")
    new_id = _doc_id()
    docs = _generate_doc_list(agreement_type, product_type, party, new_id)
    return {
        "status": "SUCCESS",
        "agreement_id": new_id,
        "reference_number": _ref(),
        "agreement_type": agreement_type,
        "counterparty": party,
        "product_type": product_type,
        "original_date": doc.get("date", ""),
        "regenerated_on": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
        "valid_until": _expiry(),
        "digitally_signed": "Yes — SHA-256",
        "possible_documents": docs,
        "message": f"Agreement regenerated. {len(docs)} documents ready for generation.",
    }


def call_generate_documents_api(agreement_data: dict) -> dict:
    """Generate all documents for an agreement."""
    time.sleep(1.5)
    docs = agreement_data.get("possible_documents", [])
    generated = []
    for i, d in enumerate(docs):
        generated.append({
            "name": d["name"],
            "desc": d["desc"],
            "pages": d.get("pages", 3),
            "size_kb": random.randint(120, 800),
            "product_type": d.get("product_type", "EBICS"),
            "header": d.get("header", ""),
            "footer": d.get("footer", ""),
            "sections": d.get("sections", []),
            "download_url": _sample_download_url(i),
            "status": "GENERATED ✅",
        })
    return {
        "status": "SUCCESS",
        "agreement_id": agreement_data.get("agreement_id", ""),
        "total_documents": len(generated),
        "documents": generated,
        "zip_url": _sample_zip_url(),
        "message": f"{len(generated)} documents generated successfully.",
    }


def _run_checklist_for_document(doc: dict, rules: dict, product_type: str,
                                 agreement_type: str, all_docs: list) -> dict:
    """
    Run all 15 verification checks from document_generation_rules.xlsx
    (Verification Checklist sheet) for a single document.

    Returns a dict with one key per check step, plus an 'overall' verdict
    and a 'check_details' list for the detailed UI report.
    """
    checks = {}

    # ── Helper: weighted random pass/fail (realistic simulation) ─────────────
    def _pass(weight_pass=92):
        return random.choices([True, False], weights=[weight_pass, 100 - weight_pass])[0]

    # ── Step 1: Header Present — compare against generation rule ─────────────
    expected_header = rules.get("header", "")
    doc_header = doc.get("header", "")
    h_match = bool(expected_header) and (
        expected_header.lower() in doc_header.lower() or
        doc_header.lower() in expected_header.lower() or
        _pass(95)
    )
    checks["step_01_header"] = {
        "label": "Header Present",
        "expected": expected_header or "Per generation rule",
        "method": "Text comparison",
        "result": "PASS ✅" if h_match else "FAIL ❌",
        "passed": h_match,
        "detail": f"Found: {doc_header[:60] or 'N/A'}" if h_match
                  else f"Expected: {expected_header[:60]}",
    }

    # ── Step 2: Footer Present — pattern match ────────────────────────────────
    expected_footer = rules.get("footer", "Page {page} | Product | Type")
    f_pass = _pass(97)
    checks["step_02_footer"] = {
        "label": "Footer Present",
        "expected": expected_footer,
        "method": "Pattern match",
        "result": "PASS ✅" if f_pass else "FAIL ❌",
        "passed": f_pass,
        "detail": "Footer template matches rule" if f_pass
                  else "Footer template mismatch detected",
    }

    # ── Step 3: Required Sections — 100% sections found ──────────────────────
    req_sections = rules.get("required_sections", [])
    doc_sections = doc.get("sections", [])
    # Simulate: cover letter only has generic sections, main doc has full set
    is_main = "Cover_Letter" not in doc.get("name", "")
    sec_pass = _pass(94) if is_main else _pass(98)
    found_sections = req_sections if sec_pass else req_sections[:-1]
    missing = [s for s in req_sections if s not in found_sections] if not sec_pass else []
    checks["step_03_sections"] = {
        "label": "Required Sections",
        "expected": f"All {len(req_sections)} sections present",
        "method": "Section scan",
        "result": "PASS ✅" if sec_pass else "FAIL ❌",
        "passed": sec_pass,
        "detail": (
            f"All {len(req_sections)} sections verified: {', '.join(req_sections[:3])}{'...' if len(req_sections) > 3 else ''}"
            if sec_pass
            else f"Missing: {', '.join(missing)}"
        ),
    }

    # ── Step 4: Required Fields — no empty required fields ───────────────────
    req_fields = rules.get("required_fields", [])
    fld_pass = _pass(93)
    checks["step_04_fields"] = {
        "label": "Required Fields",
        "expected": f"All {len(req_fields)} fields populated",
        "method": "Field validation",
        "result": "PASS ✅" if fld_pass else "WARN ⚠️",
        "passed": fld_pass,
        "detail": (
            f"All fields populated: {', '.join(req_fields[:3])}{'...' if len(req_fields) > 3 else ''}"
            if fld_pass
            else "1 or more required fields may be empty"
        ),
    }

    # ── Step 5: Digital Signature — SHA-256 present (mandatory for all types) ─
    sig_pass = _pass(99)
    checks["step_05_signature"] = {
        "label": "Digital Signature (SHA-256)",
        "expected": "SHA-256 hash present",
        "method": "Crypto check",
        "result": "PASS ✅" if sig_pass else "FAIL ❌",
        "passed": sig_pass,
        "detail": "Valid SHA-256 digital signature verified" if sig_pass
                  else "No valid SHA-256 signature found",
    }

    # ── Step 6: Product Type Config — EBICS/MT101/CC in document ──────────
    pt_pass = _pass(98)
    checks["step_06_product_type"] = {
        "label": "Product Type Config",
        "expected": product_type,
        "method": "Config match",
        "result": "PASS ✅" if pt_pass else "FAIL ❌",
        "passed": pt_pass,
        "detail": f"Product type {product_type} confirmed in document" if pt_pass
                  else f"Product type config mismatch (expected {product_type})",
    }

    # ── Step 7: Min Page Count — per generation rule ─────────────────────────
    min_pages = rules.get("min_pages", 3)
    doc_pages = doc.get("pages", min_pages + 1)
    pg_pass = doc_pages >= min_pages
    checks["step_07_page_count"] = {
        "label": "Min Page Count",
        "expected": f">= {min_pages} pages",
        "method": "Page count",
        "result": "PASS ✅" if pg_pass else "FAIL ❌",
        "passed": pg_pass,
        "detail": f"{doc_pages} pages found (minimum: {min_pages})" if pg_pass
                  else f"Only {doc_pages} pages; minimum required: {min_pages}",
    }

    # ── Step 8: Party Details — both parties named ────────────────────────────
    party_pass = _pass(97)
    checks["step_08_party_details"] = {
        "label": "Party Details",
        "expected": "Both parties named",
        "method": "Party name check",
        "result": "PASS ✅" if party_pass else "WARN ⚠️",
        "passed": party_pass,
        "detail": "party_a and party_b fields verified in document" if party_pass
                  else "Party detail(s) may be incomplete",
    }

    # ── Step 9: Date Validity — valid date format present ────────────────────
    date_pass = _pass(99)
    checks["step_09_date_validity"] = {
        "label": "Date Validity",
        "expected": "Generated date present (valid format)",
        "method": "Date format check",
        "result": "PASS ✅" if date_pass else "FAIL ❌",
        "passed": date_pass,
        "detail": "effective_date format valid (YYYY-MM-DD)" if date_pass
                  else "Date field missing or invalid format",
    }

    # ── Step 10: Notarisation — required for MT101 and CC ─────────────────
    notari_required = product_type in ("MT101", "CC")
    if notari_required:
        not_pass = _pass(91)
        checks["step_10_notarisation"] = {
            "label": "Notarisation",
            "expected": "Notarised stamp present",
            "method": "Stamp check",
            "result": "PASS ✅" if not_pass else "FAIL ❌",
            "passed": not_pass,
            "detail": "Notarisation mark found" if not_pass
                      else "Notarisation stamp NOT found (required for " + product_type + ")",
        }
    else:
        checks["step_10_notarisation"] = {
            "label": "Notarisation",
            "expected": "N/A for EBICS",
            "method": "Stamp check",
            "result": "N/A —",
            "passed": True,
            "detail": "Not required for EBICS documents",
        }

    # ── Step 11: IP Rights Clause — required for MT101 and CC ─────────────
    ip_required = product_type in ("MT101", "CC")
    if ip_required:
        ip_pass = _pass(93)
        checks["step_11_ip_rights"] = {
            "label": "IP Rights Clause",
            "expected": "IP section present",
            "method": "Section search",
            "result": "PASS ✅" if ip_pass else "FAIL ❌",
            "passed": ip_pass,
            "detail": "IP Rights / ip_ownership section found" if ip_pass
                      else "IP Rights section missing (required for " + product_type + ")",
        }
    else:
        checks["step_11_ip_rights"] = {
            "label": "IP Rights Clause",
            "expected": "N/A for EBICS",
            "method": "Section search",
            "result": "N/A —",
            "passed": True,
            "detail": "Not required for EBICS documents",
        }

    # ── Step 12: Audit Trail — required for CC only ───────────────────────
    audit_required = product_type == "CC"
    if audit_required:
        audit_pass = _pass(90)
        checks["step_12_audit_trail"] = {
            "label": "Audit Trail",
            "expected": "Audit log appended",
            "method": "Log check",
            "result": "PASS ✅" if audit_pass else "FAIL ❌",
            "passed": audit_pass,
            "detail": "Audit Trail section found with complete log" if audit_pass
                      else "Audit Trail section missing (required for CC)",
        }
    else:
        checks["step_12_audit_trail"] = {
            "label": "Audit Trail",
            "expected": "N/A (EBICS/MT101)",
            "method": "Log check",
            "result": "N/A —",
            "passed": True,
            "detail": "Not required for " + product_type,
        }

    # ── Step 13: Confidentiality Level — NDA-specific clause ─────────────────
    is_nda = "disclosure" in agreement_type.lower() or "nda" in agreement_type.lower()
    if is_nda:
        conf_pass = _pass(96)
        checks["step_13_confidentiality"] = {
            "label": "Confidentiality Level",
            "expected": "Confidentiality clause present",
            "method": "Clause check",
            "result": "PASS ✅" if conf_pass else "FAIL ❌",
            "passed": conf_pass,
            "detail": "Confidentiality clause and level verified" if conf_pass
                      else "Confidentiality clause missing in NDA",
        }
    else:
        checks["step_13_confidentiality"] = {
            "label": "Confidentiality Level",
            "expected": "N/A (non-NDA)",
            "method": "Clause check",
            "result": "N/A —",
            "passed": True,
            "detail": "Not applicable for " + agreement_type,
        }

    # ── Step 14: Compliance Certification — required for CC ───────────────
    comp_required = product_type == "CC"
    if comp_required:
        comp_pass = _pass(90)
        checks["step_14_compliance_cert"] = {
            "label": "Compliance Certification",
            "expected": "Compliance cert attached",
            "method": "Cert check",
            "result": "PASS ✅" if comp_pass else "FAIL ❌",
            "passed": comp_pass,
            "detail": "Compliance certificate found in bundle" if comp_pass
                      else "Compliance certificate NOT found (required for CC)",
        }
    else:
        checks["step_14_compliance_cert"] = {
            "label": "Compliance Certification",
            "expected": "N/A (EBICS/MT101)",
            "method": "Cert check",
            "result": "N/A —",
            "passed": True,
            "detail": "Not required for " + product_type,
        }

    # ── Step 15: ZIP Bundle Integrity — doc count matches API response ────────
    expected_count = len(all_docs)
    zip_pass = _pass(98)
    checks["step_15_zip_integrity"] = {
        "label": "ZIP Bundle Integrity",
        "expected": f"{expected_count} documents in bundle",
        "method": "File count check",
        "result": "PASS ✅" if zip_pass else "WARN ⚠️",
        "passed": zip_pass,
        "detail": f"Bundle verified: {expected_count} documents present" if zip_pass
                  else "Document count mismatch in ZIP bundle",
    }

    # ── Overall verdict ───────────────────────────────────────────────────────
    mandatory_checks = [
        "step_01_header", "step_02_footer", "step_03_sections", "step_04_fields",
        "step_05_signature", "step_06_product_type", "step_07_page_count",
        "step_08_party_details", "step_09_date_validity",
    ]
    # Add conditional mandatory checks
    if product_type in ("MT101", "CC"):
        mandatory_checks.extend(["step_10_notarisation", "step_11_ip_rights"])
    if product_type == "CC":
        mandatory_checks.extend(["step_12_audit_trail", "step_14_compliance_cert"])
    if is_nda:
        mandatory_checks.append("step_13_confidentiality")
    mandatory_checks.append("step_15_zip_integrity")

    failed_mandatory = [k for k in mandatory_checks if not checks[k]["passed"]]
    if not failed_mandatory:
        overall = "VERIFIED ✅"
    elif len(failed_mandatory) == 1:
        overall = "ISSUES FOUND ⚠️"
    else:
        overall = "FAILED ❌"

    # Count of passed / failed checks (excluding N/A)
    all_check_keys = list(checks.keys())
    applicable = [k for k in all_check_keys if checks[k]["result"] != "N/A —"]
    passed_count = sum(1 for k in applicable if checks[k]["passed"])
    failed_count = len(applicable) - passed_count

    return {
        "document": doc.get("name", ""),
        "overall": overall,
        "checks_passed": passed_count,
        "checks_failed": failed_count,
        "checks_total": len(applicable),
        # Legacy flat fields (used by existing table renderer)
        "header_check":       checks["step_01_header"]["result"],
        "footer_check":       checks["step_02_footer"]["result"],
        "sections_check":     checks["step_03_sections"]["result"],
        "fields_check":       checks["step_04_fields"]["result"],
        "signature_check":    checks["step_05_signature"]["result"],
        "product_type_check": checks["step_06_product_type"]["result"],
        # Full 15-step detail (used by new detailed renderer)
        "all_checks": checks,
    }


def call_verify_documents_api(detail1: str, detail2: str, detail3: str,
                               product_type: str = "EBICS") -> dict:
    """
    Instant mock verification report built directly from user-supplied inputs.
    No file I/O, no rule lookups, no loops — renders immediately on UI.
    """
    counterparty = detail1
    agreement_type = detail2
    value_duration = detail3
    year = datetime.now().year
    party_slug = counterparty.replace(" ", "_")[:12]
    short = agreement_type[:3].upper()

    # ── Mock document names derived from user inputs ──────────────────────────
    doc_names = [f"{short}_{party_slug}_Main_{year}.pdf"]
    if product_type in ("MT101", "CC"):
        doc_names.append(f"{short}_{party_slug}_Annexure_A_{year}.pdf")
    if product_type == "CC":
        doc_names.append(f"{short}_{party_slug}_Compliance_{year}.pdf")
    doc_names.append(f"{short}_{party_slug}_Cover_Letter_{year}.pdf")

    total_docs = len(doc_names)

    # ── Mock 15-check result helper ───────────────────────────────────────────
    CHECK_META = [
        ("step_01_header",          " 1", "Header Check",        "PASS ✅"),
        ("step_02_footer",          " 2", "Footer Check",        "PASS ✅"),
        ("step_03_sections",        " 3", "Required Sections",   "PASS ✅"),
        ("step_04_fields",          " 4", "Required Fields",     "PASS ✅"),
        ("step_05_signature",       " 5", "Digital Signature",   "PASS ✅"),
        ("step_06_product_type",    " 6", "Product Type",        "PASS ✅"),
        ("step_07_page_count",      " 7", "Page Count",          "PASS ✅"),
        ("step_08_party_details",   " 8", "Party Details",       "PASS ✅"),
        ("step_09_date_validity",   " 9", "Date Validity",       "PASS ✅"),
        ("step_10_notarisation",    "10", "Notarisation",
            "PASS ✅" if product_type in ("MT101", "CC") else "N/A —"),
        ("step_11_ip_rights",       "11", "IP Rights Clause",
            "PASS ✅" if product_type in ("MT101", "CC") else "N/A —"),
        ("step_12_audit_trail",     "12", "Audit Trail",
            "PASS ✅" if product_type == "CC" else "N/A —"),
        ("step_13_confidentiality", "13", "Confidentiality",
            "PASS ✅" if any(k in agreement_type.lower() for k in ("nda", "disclosure", "confidential")) else "N/A —"),
        ("step_14_compliance_cert", "14", "Compliance Cert",
            "PASS ✅" if product_type == "CC" else "N/A —"),
        ("step_15_zip_integrity",   "15", "ZIP Integrity",       "PASS ✅"),
    ]

    def _mock_check(sk, lbl, result):
        is_pass = "PASS" in result
        is_na   = "N/A"  in result
        return {
            "label":    lbl,
            "result":   result,
            "passed":   is_pass,
            "expected": "Present and valid" if not is_na else "N/A",
            "method":   "Automated scan"    if not is_na else "—",
            "detail":   (lbl + " verified successfully") if is_pass
                        else ("Not applicable for " + product_type) if is_na
                        else (lbl + " check failed"),
        }

    # ── Build per-document results ────────────────────────────────────────────
    doc_results = []
    for doc_name in doc_names:
        all_checks = {
            sk: _mock_check(sk, lbl, res)
            for sk, _, lbl, res in CHECK_META
        }
        checks_passed = sum(1 for c in all_checks.values() if c["passed"])
        checks_total  = sum(1 for c in all_checks.values() if "N/A" not in c["result"])
        doc_results.append({
            "document":      doc_name,
            "overall":       "VERIFIED ✅",
            "checks_passed": checks_passed,
            "checks_total":  checks_total,
            "all_checks":    all_checks,
        })

    # ── Verification steps log ────────────────────────────────────────────────
    verification_steps = [
        f"Step  1 · Header Check       — {agreement_type} header validated",
        f"Step  2 · Footer Check       — Page footer matches {product_type} template",
        f"Step  3 · Required Sections  — All required sections present",
        f"Step  4 · Required Fields    — All mandatory fields populated",
        "Step  5 · Digital Signature  — SHA-256 signature verified",
        f"Step  6 · Product Type       — {product_type} configuration confirmed",
        "Step  7 · Page Count         — Meets minimum page requirement",
        f"Step  8 · Party Details      — {counterparty} details verified",
        "Step  9 · Date Validity      — Effective date format valid",
        "Step 10 · Notarisation       — " + (f"Notarisation stamp present ({product_type})" if product_type in ("MT101", "CC") else "N/A for EBICS"),
        "Step 11 · IP Rights Clause   — " + (f"IP rights clause found ({product_type})" if product_type in ("MT101", "CC") else "N/A for EBICS"),
        "Step 12 · Audit Trail        — " + ("Full audit log present" if product_type == "CC" else f"N/A for {product_type}"),
        "Step 13 · Confidentiality    — " + ("NDA confidentiality clause verified" if any(k in agreement_type.lower() for k in ("nda", "disclosure", "confidential")) else f"N/A for {agreement_type}"),
        "Step 14 · Compliance Cert    — " + ("Regulatory certificate verified" if product_type == "CC" else f"N/A for {product_type}"),
        f"Step 15 · ZIP Bundle        — {total_docs} documents verified successfully",
    ]

    return {
        "status":             "VERIFIED ✅",
        "agreement_type":     agreement_type,
        "counterparty":       counterparty,
        "product_type":       product_type,
        "value_duration":     value_duration,
        "verification_steps": verification_steps,
        "document_results":   doc_results,
        "step_summary":       {},
        "total_documents":    total_docs,
        "passed":             total_docs,
        "failed":             0,
        "warnings":           0,
        "zip_url":            "#",
        "verified_on":        datetime.now().strftime("%d %b %Y, %H:%M:%S"),
        "rules_ref":          "document_generation_rules.xlsx — Verification Checklist",
        "message":            f"Verification complete. All {total_docs} documents passed all 15 checklist items for {agreement_type} ({product_type}) — {counterparty}.",
    }
