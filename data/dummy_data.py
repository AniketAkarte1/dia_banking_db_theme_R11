"""
DIA Dummy Data — Document history, user records, generation rules.
Includes product types (EBICS, MT101, CC) for all API calls.
"""
import random

# ── Product Types ──────────────────────────────────────────────────────────────
PRODUCT_TYPES = ["EBICS", "MT101", "CC"]

# ── Document Generation Rules (replaces Excel) ────────────────────────────────
# Each rule entry: agreement_type -> product_type -> list of required sections/fields
GENERATION_RULES = {
    "Non-Disclosure Agreement": {
        "EBICS": {
            "required_sections": ["Parties", "Definition of Confidential Information",
                                   "Obligations", "Exclusions", "Term", "Governing Law"],
            "required_fields": ["party_a", "party_b", "effective_date", "duration",
                                 "jurisdiction", "product_type"],
            "header": "NON-DISCLOSURE AGREEMENT — TYPE 1 STANDARD",
            "footer": "Page {page} | Confidential | NDA-T1 | DIA Legal Engine v3.1",
            "min_pages": 3,
        },
        "MT101": {
            "required_sections": ["Parties", "Scope", "Confidentiality Obligations",
                                   "IP Rights", "Term & Termination", "Dispute Resolution"],
            "required_fields": ["party_a", "party_b", "effective_date", "duration",
                                 "ip_ownership", "jurisdiction", "product_type"],
            "header": "NON-DISCLOSURE AGREEMENT — TYPE 2 ENHANCED",
            "footer": "Page {page} | Strictly Confidential | NDA-T2 | DIA Legal Engine v3.1",
            "min_pages": 5,
        },
        "CC": {
            "required_sections": ["Parties", "Multi-Party Confidentiality", "Scope",
                                   "Obligations", "IP", "Audit Rights", "Term"],
            "required_fields": ["party_a", "party_b", "party_c", "effective_date",
                                 "duration", "audit_clause", "product_type"],
            "header": "NON-DISCLOSURE AGREEMENT — TYPE 3 MULTI-PARTY",
            "footer": "Page {page} | Multi-Party Confidential | NDA-T3 | DIA Legal Engine v3.1",
            "min_pages": 7,
        },
    },
    "Service Agreement": {
        "EBICS": {
            "required_sections": ["Parties", "Services", "Payment Terms",
                                   "Term", "Liability"],
            "required_fields": ["party_a", "party_b", "service_description",
                                 "payment_amount", "payment_schedule", "product_type"],
            "header": "SERVICE AGREEMENT — TYPE 1",
            "footer": "Page {page} | Service Agreement | SA-T1 | DIA Legal Engine v3.1",
            "min_pages": 4,
        },
        "MT101": {
            "required_sections": ["Parties", "Scope of Services", "SLA", "Payment",
                                   "Indemnification", "Term & Renewal"],
            "required_fields": ["party_a", "party_b", "sla_terms", "payment_amount",
                                 "renewal_clause", "product_type"],
            "header": "SERVICE AGREEMENT — TYPE 2 WITH SLA",
            "footer": "Page {page} | Service Agreement SLA | SA-T2 | DIA Legal Engine v3.1",
            "min_pages": 6,
        },
        "CC": {
            "required_sections": ["Parties", "Services", "SLA", "Pricing",
                                   "IP Rights", "Data Protection", "Termination"],
            "required_fields": ["party_a", "party_b", "data_processing_terms",
                                 "ip_clause", "termination_notice", "product_type"],
            "header": "SERVICE AGREEMENT — TYPE 3 ENTERPRISE",
            "footer": "Page {page} | Enterprise Service | SA-T3 | DIA Legal Engine v3.1",
            "min_pages": 8,
        },
    },
    "Rental Agreement": {
        "EBICS": {
            "required_sections": ["Parties", "Property", "Rent", "Deposit",
                                   "Term", "Maintenance"],
            "required_fields": ["landlord", "tenant", "property_address", "rent_amount",
                                 "deposit_amount", "start_date", "product_type"],
            "header": "RENTAL AGREEMENT — TYPE 1 RESIDENTIAL",
            "footer": "Page {page} | Rental Agreement | RA-T1 | DIA Legal Engine v3.1",
            "min_pages": 3,
        },
        "MT101": {
            "required_sections": ["Parties", "Property Details", "Commercial Use",
                                   "Rent Schedule", "CAM Charges", "Term & Renewal"],
            "required_fields": ["landlord", "tenant", "property_address", "rent_amount",
                                 "cam_charges", "commercial_purpose", "product_type"],
            "header": "RENTAL AGREEMENT — TYPE 2 COMMERCIAL",
            "footer": "Page {page} | Commercial Rental | RA-T2 | DIA Legal Engine v3.1",
            "min_pages": 5,
        },
        "CC": {
            "required_sections": ["Parties", "Industrial Property", "Rent",
                                   "Utilities", "Compliance", "Term"],
            "required_fields": ["landlord", "tenant", "property_address",
                                 "utility_terms", "compliance_clause", "product_type"],
            "header": "RENTAL AGREEMENT — TYPE 3 INDUSTRIAL",
            "footer": "Page {page} | Industrial Rental | RA-T3 | DIA Legal Engine v3.1",
            "min_pages": 6,
        },
    },
}

# Add fallback rules for other agreement types
_DEFAULT_RULES = {
    "EBICS": {
        "required_sections": ["Parties", "Terms & Conditions", "Obligations",
                               "Payment", "Term", "Governing Law"],
        "required_fields": ["party_a", "party_b", "effective_date",
                             "value", "jurisdiction", "product_type"],
        "header": "LEGAL AGREEMENT — TYPE 1 STANDARD",
        "footer": "Page {page} | Confidential | DIA Legal Engine v3.1",
        "min_pages": 3,
    },
    "MT101": {
        "required_sections": ["Parties", "Scope", "Terms", "IP Rights",
                               "Obligations", "Term", "Dispute Resolution"],
        "required_fields": ["party_a", "party_b", "effective_date", "scope",
                             "ip_rights", "dispute_mechanism", "product_type"],
        "header": "LEGAL AGREEMENT — TYPE 2 ENHANCED",
        "footer": "Page {page} | Strictly Confidential | DIA Legal Engine v3.1",
        "min_pages": 5,
    },
    "CC": {
        "required_sections": ["Parties", "Multi-Party Terms", "Scope", "Obligations",
                               "IP", "Audit", "Data Protection", "Term"],
        "required_fields": ["party_a", "party_b", "party_c", "effective_date",
                             "data_terms", "audit_clause", "product_type"],
        "header": "LEGAL AGREEMENT — TYPE 3 ENTERPRISE",
        "footer": "Page {page} | Enterprise Confidential | DIA Legal Engine v3.1",
        "min_pages": 7,
    },
}


def get_generation_rules(agreement_type: str, product_type: str) -> dict:
    """Get generation rules for given agreement type and product type."""
    rules = GENERATION_RULES.get(agreement_type, _DEFAULT_RULES)
    return rules.get(product_type, _DEFAULT_RULES.get(product_type, _DEFAULT_RULES["EBICS"]))


# ── User Document History ──────────────────────────────────────────────────────
DOCUMENT_HISTORY = {
    "Rahul": [
        {
            "id": "DOC-2024-001",
            "type": "Non-Disclosure Agreement",
            "party": "TechSolutions Pvt Ltd",
            "date": "2024-03-15",
            "value": "N/A",
            "status": "Active",
            "duration": "2 years",
            "product_type": "EBICS",
            "detail1": "TechSolutions Pvt Ltd",
            "detail2": "Non-Disclosure Agreement",
            "detail3": "2 Years",
            "generated_docs": [
                {"name": "NDA_TechSolutions_2024.pdf",
                 "desc": "Main NDA document with all clauses, party details, obligations and term."},
                {"name": "NDA_Annexure_A_2024.pdf",
                 "desc": "Annexure A: Schedule of confidential information categories."},
                {"name": "NDA_Cover_Letter_2024.pdf",
                 "desc": "Formal cover letter for NDA submission."},
            ],
        },
        {
            "id": "DOC-2024-002",
            "type": "Service Agreement",
            "party": "GlobalWorks Inc",
            "date": "2024-06-01",
            "value": "₹5,00,000",
            "status": "Active",
            "duration": "1 year",
            "product_type": "MT101",
            "detail1": "GlobalWorks Inc",
            "detail2": "Service Agreement",
            "detail3": "₹5,00,000",
            "generated_docs": [
                {"name": "SA_GlobalWorks_Main_2024.pdf",
                 "desc": "Main Service Agreement with SLA terms, payment schedule and scope."},
                {"name": "SA_GlobalWorks_SLA_2024.pdf",
                 "desc": "Service Level Agreement appendix with KPIs and penalties."},
                {"name": "SA_GlobalWorks_SOW_2024.pdf",
                 "desc": "Statement of Work detailing deliverables and milestones."},
                {"name": "SA_GlobalWorks_Invoice_Template_2024.pdf",
                 "desc": "Standard invoice template for billing under this agreement."},
            ],
        },
        {
            "id": "DOC-2023-007",
            "type": "Rental Agreement",
            "party": "Shree Properties",
            "date": "2023-11-10",
            "value": "₹18,000/mo",
            "status": "Expired",
            "duration": "11 months",
            "product_type": "EBICS",
            "detail1": "Shree Properties",
            "detail2": "Rental Agreement",
            "detail3": "₹18,000/month",
            "generated_docs": [
                {"name": "RA_ShreeProperties_2023.pdf",
                 "desc": "Residential rental agreement with rent, deposit and maintenance terms."},
                {"name": "RA_ShreeProperties_Addendum_2023.pdf",
                 "desc": "Addendum for utility charges and parking allocation."},
            ],
        },
    ],
    "Priya": [
        {
            "id": "DOC-2024-015",
            "type": "Employment Contract",
            "party": "Infosys Limited",
            "date": "2024-01-10",
            "value": "₹12,00,000 PA",
            "status": "Active",
            "duration": "Permanent",
            "product_type": "MT101",
            "detail1": "Infosys Limited",
            "detail2": "Employment Contract",
            "detail3": "₹12,00,000 PA",
            "generated_docs": [
                {"name": "EC_Infosys_Offer_Letter_2024.pdf",
                 "desc": "Official offer letter with compensation, designation and joining date."},
                {"name": "EC_Infosys_Employment_Contract_2024.pdf",
                 "desc": "Full employment contract with terms, benefits and obligations."},
                {"name": "EC_Infosys_NDA_2024.pdf",
                 "desc": "Employee NDA for IP and confidentiality."},
            ],
        },
        {
            "id": "DOC-2024-020",
            "type": "Vendor Agreement",
            "party": "SupplyChain Co",
            "date": "2024-05-22",
            "value": "₹2,50,000",
            "status": "Pending",
            "duration": "6 months",
            "product_type": "CC",
            "detail1": "SupplyChain Co",
            "detail2": "Vendor Agreement",
            "detail3": "₹2,50,000",
            "generated_docs": [
                {"name": "VA_SupplyChain_Main_2024.pdf",
                 "desc": "Vendor agreement covering supply terms, pricing and delivery."},
                {"name": "VA_SupplyChain_QA_2024.pdf",
                 "desc": "Quality assurance terms and inspection procedures."},
            ],
        },
    ],
    "Amit": [
        {
            "id": "DOC-2023-030",
            "type": "Partnership Deed",
            "party": "StartupVentures LLP",
            "date": "2023-08-05",
            "value": "₹25,00,000",
            "status": "Active",
            "duration": "5 years",
            "product_type": "CC",
            "detail1": "StartupVentures LLP",
            "detail2": "Partnership Deed",
            "detail3": "₹25,00,000",
            "generated_docs": [
                {"name": "PD_StartupVentures_Deed_2023.pdf",
                 "desc": "Partnership deed with profit sharing, roles and capital contribution."},
                {"name": "PD_StartupVentures_Schedule_2023.pdf",
                 "desc": "Schedule of assets and liabilities contributed by each partner."},
                {"name": "PD_StartupVentures_Resolution_2023.pdf",
                 "desc": "Board resolution approving the partnership arrangement."},
            ],
        },
    ],
    "Sneha": [
        {
            "id": "DOC-2024-040",
            "type": "Consultancy Agreement",
            "party": "DigitalMinds Agency",
            "date": "2024-02-28",
            "value": "₹80,000/mo",
            "status": "Active",
            "duration": "12 months",
            "product_type": "EBICS",
            "detail1": "DigitalMinds Agency",
            "detail2": "Consultancy Agreement",
            "detail3": "₹80,000/month",
            "generated_docs": [
                {"name": "CA_DigitalMinds_Contract_2024.pdf",
                 "desc": "Consultancy contract with scope, fees and IP ownership."},
                {"name": "CA_DigitalMinds_SOW_2024.pdf",
                 "desc": "Statement of Work for digital transformation engagement."},
            ],
        },
        {
            "id": "DOC-2023-041",
            "type": "Memorandum of Understanding",
            "party": "NGO Foundation Trust",
            "date": "2023-12-01",
            "value": "N/A",
            "status": "Expired",
            "duration": "6 months",
            "product_type": "MT101",
            "detail1": "NGO Foundation Trust",
            "detail2": "Memorandum of Understanding",
            "detail3": "N/A",
            "generated_docs": [
                {"name": "MOU_NGOFoundation_2023.pdf",
                 "desc": "MOU outlining cooperation framework between parties."},
            ],
        },
    ],
}


def get_user_documents(name: str) -> list:
    """Fetch document history for a given user name (case-insensitive).

    Matching priority:
    1. Exact match (title-cased)
    2. Any key that starts with the query, or query that is contained in a key
    3. First token of query matches any key (handles 'Rahul Sharma' -> 'Rahul')
    4. Any key whose first token matches the query's first token
    """
    name_clean = name.strip().title()
    name_lower = name_clean.lower()

    # 1. Exact match
    if name_clean in DOCUMENT_HISTORY:
        return DOCUMENT_HISTORY[name_clean]

    # 2. Substring / prefix match on full name
    for key in DOCUMENT_HISTORY:
        key_lower = key.lower()
        if key_lower.startswith(name_lower) or name_lower.startswith(key_lower) or name_lower in key_lower:
            return DOCUMENT_HISTORY[key]

    # 3. First-token match: 'Rahul Sharma' -> first token 'Rahul' -> matches key 'Rahul'
    first_token = name_lower.split()[0] if name_lower.split() else name_lower
    for key in DOCUMENT_HISTORY:
        key_lower = key.lower()
        key_first = key_lower.split()[0] if key_lower.split() else key_lower
        if first_token == key_first or first_token == key_lower or key_first == name_lower:
            return DOCUMENT_HISTORY[key]

    return []


def add_to_history(name: str, doc_record: dict):
    """Add a new document record to user history."""
    name_clean = name.strip().title()
    if name_clean not in DOCUMENT_HISTORY:
        DOCUMENT_HISTORY[name_clean] = []
    DOCUMENT_HISTORY[name_clean].append(doc_record)
