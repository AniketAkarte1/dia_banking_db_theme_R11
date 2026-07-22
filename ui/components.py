"""
DIA UI Components — Python 3.9+ + streamlit 1.28.0+ compatible.

streamlit 1.28.0+ API compatibility notes:
  - st.audio(data, format=...) — 'autoplay' kwarg NOT in 1.56.0.
    autoplay is injected via raw HTML <audio autoplay> instead.
  - st.toast() — NOT available in 1.56.0. Replaced with st.warning().
  - st.toggle() — NOT available in 1.56.0. Replaced with st.checkbox().
  - audio_recorder_streamlit 0.0.10 API: audio_recorder() returns bytes or None.
  - All type hints use typing module (no X|None unions).
  - No walrus operator, no match/case.
"""
import base64
import streamlit as st
from typing import Dict, List, Optional, Any

from services.download_helper import get_zip_download_link, get_single_file_link

from core.session import (
    get_state, set_state,
    audio_already_processed, acquire_cmd_lock, release_cmd_lock,
)
from core.conversation import (
    handle_user_input, trigger_regenerate,
    trigger_new_agreement, trigger_open_document,
)


# ══════════════════════════════════════════════════════════════════════════════
#  DOWNLOAD URL RESOLVER
# ══════════════════════════════════════════════════════════════════════════════

def _resolve_download_url(url: str) -> str:
    """
    Turn a sentinel URL into a real base64 data-URI download anchor.

    Sentinels produced by document_api.py:
      "__sample_zip__"                  → full ZIP of sample_document/
      "__sample_download__:<filename>"  → single PDF from sample_document/
    Any other value is returned unchanged.
    """
    if url == "__sample_zip__":
        return get_zip_download_link(
            label="Download All as ZIP",
            filename="sample_documents.zip",
            css_class="zip-link",
        )
    if url.startswith("__sample_download__:"):
        fname = url.split(":", 1)[1]
        return get_single_file_link(
            filename=fname,
            label="View / Download Document",
            css_class="zip-link",
        )
    # Plain URL — wrap in a normal anchor
    return (
        f'<a href="{url}" target="_blank" class="zip-link">'
        f"&#128229; View / Download Document</a>"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

def render_header() -> None:
    st.markdown("""
    <div class="dia-header">
        <div class="dia-logo-wrap">
            <div class="dia-logo-badge">DB</div>
            <div>
                <div class="dia-logo">D.I.A</div>
                <div class="dia-subtitle">
                    Voice Banking &nbsp;&middot;&nbsp; Legal Document Intelligence
                </div>
            </div>
        </div>
        <div class="status-bar">
            <div class="status-pill active"><span class="status-dot"></span>&nbsp;ONLINE</div>
            <div class="status-pill">&#9878;&nbsp;LEGAL v3.1</div>
            <div class="status-pill">&#128274;&nbsp;SECURE</div>
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div style="font-family:DM Sans,sans-serif;font-size:13px;'
            'color:var(--accent-cyan);letter-spacing:2px;padding:14px 0 10px;">'
            '&#9881; CONTROL PANEL</div>',
            unsafe_allow_html=True,
        )

        lang_opts = ["English", "हिंदी (Hindi)", "मराठी (Marathi)", "Deutsch (German)", "普通话 (Mandarin)"]
        lang = st.selectbox(
            "🌐 Language",
            lang_opts,
            index=lang_opts.index(st.session_state.get("language", "English")),
            key="sb_lang",
        )
        st.session_state["language"] = lang

        st.markdown("---")

        # streamlit 1.28.0+: use st.checkbox instead of st.toggle
        audio_on = st.checkbox(
            "🔊 DIA Voice Output",
            value=st.session_state.get("audio_enabled", True),
            key="sb_audio_chk",
        )
        st.session_state["audio_enabled"] = audio_on

        st.markdown("---")

        pt_opts = ["EBICS", "MT101", "CC"]
        pt = st.selectbox(
            "📦 Default Product Type",
            pt_opts,
            index=pt_opts.index(st.session_state.get("product_type", "EBICS")),
            key="sb_pt",
        )
        st.session_state["product_type"] = pt

        st.markdown("---")

        flow = st.session_state.get("flow_state", "IDLE")
        user = st.session_state.get("current_user") or "—"
        msgs = len(st.session_state.get("messages", []))
        sid  = st.session_state.get("session_id", "")[:8].upper()
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:10px;'
            'color:rgba(255,255,255,0.40);line-height:2.2;">'
            "SESSION: {0}<br>STATE: {1}<br>CLIENT: {2}<br>MSGS: {3}"
            "</div>".format(sid, flow, user, msgs),
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("**&#9889; Quick Actions**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 History", use_container_width=True, key="sb_hist"):
                handle_user_input("show my agreement history", _internal=True)
                st.rerun()
        with c2:
            if st.button("✨ New Doc", use_container_width=True, key="sb_new"):
                handle_user_input("generate new agreement", _internal=True)
                st.rerun()
        if st.button("🔍 Verify Doc", use_container_width=True, key="sb_ver"):
            handle_user_input("verify document", _internal=True)
            st.rerun()

        st.markdown("---")
        if st.button("🔄 Reset Session", use_container_width=True, key="sb_reset"):
            from core.session import reset_session
            reset_session()
            st.rerun()

        st.markdown("---")
        st.markdown("**&#128100; Face ID**")
        face_user = st.session_state.get("face_auth_user")
        if face_user:
            st.markdown(
                '<div style="font-family:DM Mono,monospace;font-size:10px;'
                'color:var(--accent-green);">&#10003; Identified: <b>{0}</b></div>'.format(face_user),
                unsafe_allow_html=True,
            )
        if st.button("📷 Re-scan Face", use_container_width=True, key="sb_rescan"):
            for k in ["face_auth_done", "face_auth_user", "face_auth_status",
                      "face_enroll_frames", "face_enroll_name", "face_enroll_cap_count"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
        # Face DB management expander
        with st.expander("&#128273; Manage Enrolled Faces"):
            try:
                from core.face_auth_engine import list_enrolled_users
                users = list_enrolled_users()
                if not users:
                    st.caption("No faces enrolled yet.")
                else:
                    for u in users:
                        st.markdown(
                            "**{name}** — {lang} — {n} samples".format(
                                name=u["name"], lang=u["language"], n=u["sample_count"]
                            )
                        )
            except Exception as e:
                st.caption("Face DB: " + str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════

def render_chat_history() -> None:
    messages = st.session_state.get("messages", [])
    if not messages:
        _splash()
        return
    for msg in messages:
        _render_message(msg)
    st.markdown('<div id="chat-end"></div>', unsafe_allow_html=True)


def _splash() -> None:
    st.markdown("""
    <div class="welcome-splash">
        <div class="splash-arc">&#9878;</div>
        <div class="splash-title">D.I.A</div>
        <div class="splash-sub">AI LEGAL AGREEMENT ASSISTANT</div>
        <div class="splash-hint">Click the &#127897; mic below or type to begin</div>
    </div>""", unsafe_allow_html=True)


def _render_message(msg: Dict[str, Any]) -> None:
    role    = msg.get("role", "dia")
    content = msg.get("content", "")
    ts      = msg.get("timestamp", "")
    mtype   = msg.get("type", "text")
    extra   = msg.get("extra", {})
    is_user = (role == "user")

    wc = "user" if is_user else ""
    bc = "user" if is_user else "dia"
    av = "&#128100;" if is_user else "&#9878;"
    ac = "user" if is_user else "dia"

    st.markdown(
        '<div class="message-wrapper {0}">'
        '<div class="avatar {1}">{2}</div>'
        '<div class="msg-body">'
        '<div class="message-bubble {3}">{4}</div>'
        '<div class="message-time">{5}</div>'
        "</div></div>".format(wc, ac, av, bc, content, ts),
        unsafe_allow_html=True,
    )

    # Extra content by message type
    if mtype == "doc_history" and "documents" in extra:
        _render_doc_cards(extra["documents"])
    elif mtype == "api_response" and "api_data" in extra:
        _render_api_response(extra["api_data"])
    elif mtype == "doc_list" and "documents" in extra:
        _render_doc_list(extra["documents"], extra.get("zip_url", ""))
    elif mtype == "doc_viewer" and "doc" in extra:
        _render_doc_viewer(extra["doc"])
    elif mtype == "verify_result" and "verify_data" in extra:
        _render_verify_result(extra["verify_data"])

    # Audio player — autoplay only on the latest message to prevent overlap
    all_msgs  = st.session_state.get("messages", [])
    is_latest = bool(all_msgs) and (all_msgs[-1] is msg)
    if msg.get("audio_path") and st.session_state.get("audio_enabled", True):
        _play_audio(msg["audio_path"], autoplay=is_latest)


def _play_audio(audio_path: str, autoplay: bool = False) -> None:
    """
    Embed audio player via raw HTML.
    streamlit 1.28.0+ st.audio() does not support autoplay kwarg,
    so we inject a raw <audio> tag for the latest message.
    Non-latest messages get a plain controls-only player.
    """
    try:
        with open(audio_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        auto_attr = "autoplay" if autoplay else ""
        st.markdown(
            '<audio {0} controls '
            'style="height:26px;width:180px;margin:3px 0 0 54px;'
            'filter:invert(0.8) hue-rotate(160deg);">'
            '<source src="data:audio/mp3;base64,{1}" type="audio/mp3">'
            "</audio>".format(auto_attr, b64),
            unsafe_allow_html=True,
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT CARDS (history)
# ══════════════════════════════════════════════════════════════════════════════

def _render_doc_cards(documents: List[Dict[str, Any]]) -> None:
    st.markdown('<div style="margin:10px 0 4px 54px;">', unsafe_allow_html=True)
    cols = st.columns(min(len(documents), 3))
    for i, doc in enumerate(documents):
        col = cols[i % len(cols)]
        status_map = {
            "Active":  "status-active",
            "Expired": "status-expired",
            "Pending": "status-pending",
        }
        sc = status_map.get(doc.get("status", "Active"), "status-active")
        with col:
            st.markdown(
                '<div class="doc-card">'
                '<div class="doc-card-id">{0}</div>'
                '<div class="doc-card-title">&#128196; {1}</div>'
                '<div class="doc-card-meta">'
                "<b>Party:</b> {2}<br><b>Date:</b> {3}<br>"
                "<b>Value:</b> {4}<br><b>Product:</b> {5}"
                "</div>"
                '<span class="doc-card-status {6}">{7}</span>'
                "</div>".format(
                    doc.get("id", ""),
                    doc.get("type", ""),
                    doc.get("party", ""),
                    doc.get("date", ""),
                    doc.get("value", "N/A"),
                    doc.get("product_type", "—"),
                    sc,
                    doc.get("status", "Active"),
                ),
                unsafe_allow_html=True,
            )
            btn_key = "regen_{0}_{1}".format(doc.get("id", "x"), i)
            if st.button("🔄 Regenerate", key=btn_key, use_container_width=True):
                set_state("selected_doc", doc)
                trigger_regenerate(doc)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  API RESPONSE TABLE
# ══════════════════════════════════════════════════════════════════════════════

def _render_api_response(api_data: Dict[str, Any]) -> None:
    rows = ""
    for k, v in api_data.items():
        if k == "possible_documents":
            continue
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        rows += (
            '<tr><td class="api-key">{0}</td>'
            '<td class="api-val">{1}</td></tr>'.format(k, v)
        )
    st.markdown(
        '<div class="api-response-box" style="margin-left:54px;">'
        '<div class="api-response-header">&#128193; AGREEMENT REPORT</div>'
        '<table class="api-table">{0}</table>'
        "</div>".format(rows),
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT LIST (after generation)
# ══════════════════════════════════════════════════════════════════════════════

def _render_doc_list(documents: List[Dict[str, Any]], zip_url: str = "") -> None:
    st.markdown('<div style="margin:8px 0 4px 54px;">', unsafe_allow_html=True)
    st.markdown(
        '<div class="api-response-box">'
        '<div class="api-response-header">&#128193; GENERATED DOCUMENTS</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    for i, doc in enumerate(documents):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(
                '<div class="doc-list-item">'
                "<b>{0}. {1}</b><br>"
                '<span style="color:rgba(255,255,255,0.45);font-size:12px;">{2}</span><br>'
                '<span style="font-size:11px;">'
                "&#128211; {3}p &nbsp;|&nbsp; &#128230; {4}KB &nbsp;|&nbsp; &#127991; {5}"
                "</span></div>".format(
                    i + 1,
                    doc.get("name", ""),
                    doc.get("desc", ""),
                    doc.get("pages", "-"),
                    doc.get("size_kb", "-"),
                    doc.get("product_type", "-"),
                ),
                unsafe_allow_html=True,
            )
        with c2:
            btn_key = "vd_{0}_{1}".format(i, doc.get("name", "")[:8])
            if st.button("👁 View", key=btn_key, use_container_width=True):
                trigger_open_document(doc.get("name", ""))
                st.rerun()
    if zip_url:
        st.markdown(
            '<div style="margin-top:8px;">'
            + _resolve_download_url(zip_url)
            + "</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT VIEWER
# ══════════════════════════════════════════════════════════════════════════════

def _render_doc_viewer(doc: Dict[str, Any]) -> None:
    sections_str = ", ".join(doc.get("sections", [])) or "—"
    footer_text  = doc.get("footer", "").replace("{page}", "1") or "—"

    # ── Part 1: doc body — no base64 blobs so Streamlit never silently drops it
    st.markdown(
        '<div class="doc-viewer" style="margin-left:54px;">'
        '<div class="doc-viewer-header">{0}</div>'
        '<div class="doc-viewer-body">'
        "<b>Document:</b> {1}<br><br>"
        "<b>Description:</b> {2}<br><br>"
        "<b>Sections:</b> {3}<br><br>"
        "<b>Product Type:</b> {4} &nbsp;|&nbsp; "
        "<b>Pages:</b> {5} &nbsp;|&nbsp; "
        "<b>Size:</b> {6} KB<br>"
        "</div>"
        '<div class="doc-viewer-footer">{7}</div>'
        "</div>".format(
            doc.get("header", "DOCUMENT HEADER"),
            doc.get("name", "—"),
            doc.get("desc", "—"),
            sections_str,
            doc.get("product_type", "—"),
            doc.get("pages", "—"),
            doc.get("size_kb", "—"),
            footer_text,
        ),
        unsafe_allow_html=True,
    )

    # ── Part 2: download anchor in its own call (base64 PDF can be large)
    download_anchor = _resolve_download_url(doc.get("download_url", "#"))
    st.markdown(
        '<div style="margin-left:54px;padding:4px 0 10px;">'
        + download_anchor
        + "</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  VERIFICATION RESULT
# ══════════════════════════════════════════════════════════════════════════════

def _render_verify_result(data: Dict[str, Any]) -> None:
    """
    Render the instant mock 15-check verification report from user-supplied data.

    Layout:
      1. Report header + meta (agreement / counterparty / product / timestamp)
      2. Metric cards (total docs, verified, issues, pass rate, checks/doc)
      3. Verdict banner
      4. 15-check matrix — all documents vs all checks at a glance
      5. Per-document drill-down with all 15 check details, expected, method, detail
      6. Verification execution log (15 steps)
      7. Rules reference + summary message
    """
    doc_results  = data.get("document_results", [])
    passed       = data.get("passed", 0)
    total        = data.get("total_documents", 0)
    failed       = data.get("failed", 0)
    warnings     = data.get("warnings", 0)
    verified_on  = data.get("verified_on", "")
    agr_type     = data.get("agreement_type", "\u2014")
    counterparty = data.get("counterparty", "\u2014")
    product      = data.get("product_type", "\u2014")
    message      = data.get("message", "")
    rules_ref    = data.get("rules_ref", "document_generation_rules.xlsx")

    pct = int(100 * passed / total) if total else 0

    # ── Chip helper ───────────────────────────────────────────────────────────
    def _chip(val, small=False):
        # type: (str, bool) -> str
        size = "9px" if small else "10px"
        if any(p in val for p in ("PASS", "\u2705", "VERIFIED")):
            col = "#00C896"
        elif any(p in val for p in ("FAIL", "\u274c")):
            col = "#FF4444"
        elif "N/A" in val or val in ("\u2014", "—"):
            col = "rgba(255,255,255,0.30)"
        else:
            col = "#FFA500"
        return (
            '<span style="color:' + col + ';font-weight:700;font-size:' + size + ';">'
            + val + '</span>'
        )

    # ── Verdict colour ────────────────────────────────────────────────────────
    if failed == 0 and warnings == 0:
        verdict_color = "#00C896"
        verdict_bg    = "rgba(0,200,150,0.12)"
        verdict_icon  = "\u2705"
        verdict_text  = "ALL " + str(total) + " DOCUMENTS FULLY VERIFIED"
    elif failed == total:
        verdict_color = "#FF4444"
        verdict_bg    = "rgba(255,68,68,0.12)"
        verdict_icon  = "\u274c"
        verdict_text  = "ALL " + str(total) + " DOCUMENTS FAILED VERIFICATION"
    else:
        verdict_color = "#FFA500"
        verdict_bg    = "rgba(255,165,0,0.12)"
        verdict_icon  = "\u26a0\ufe0f"
        verdict_text  = (str(passed) + "/" + str(total) + " DOCUMENTS VERIFIED  \u00b7  "
                         + str(failed + warnings) + " WITH ISSUES")

    ts_span = ""
    if verified_on:
        ts_span = ('<span style="font-size:9px;color:rgba(255,255,255,0.4);float:right;">'
                   + verified_on + '</span>')

    # ── Metric cards ─────────────────────────────────────────────────────────
    fc  = "#FF4444" if (failed + warnings) else "#00C896"
    fbd = "0.4"     if (failed + warnings) else "0.1"
    metrics_html = (
        '<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">'

        '<div style="flex:1;min-width:60px;background:rgba(0,33,77,0.6);'
        'border:1px solid rgba(0,180,216,0.3);border-radius:6px;padding:8px;text-align:center;">'
        '<div style="font-size:9px;color:#00B4D8;letter-spacing:1px;">TOTAL DOCS</div>'
        '<div style="font-size:20px;font-weight:700;color:#fff;">' + str(total) + '</div></div>'

        '<div style="flex:1;min-width:60px;background:rgba(0,200,150,0.15);'
        'border:1px solid rgba(0,200,150,0.4);border-radius:6px;padding:8px;text-align:center;">'
        '<div style="font-size:9px;color:#00C896;letter-spacing:1px;">VERIFIED</div>'
        '<div style="font-size:20px;font-weight:700;color:#00C896;">' + str(passed) + '</div></div>'

        '<div style="flex:1;min-width:60px;background:rgba(255,68,68,0.15);'
        'border:1px solid rgba(255,68,68,' + fbd + ');border-radius:6px;padding:8px;text-align:center;">'
        '<div style="font-size:9px;color:#FF6B6B;letter-spacing:1px;">ISSUES</div>'
        '<div style="font-size:20px;font-weight:700;color:' + fc + ';">' + str(failed + warnings) + '</div></div>'

        '<div style="flex:1;min-width:60px;background:rgba(0,180,216,0.15);'
        'border:1px solid rgba(0,180,216,0.4);border-radius:6px;padding:8px;text-align:center;">'
        '<div style="font-size:9px;color:#00B4D8;letter-spacing:1px;">PASS RATE</div>'
        '<div style="font-size:20px;font-weight:700;color:#00B4D8;">' + str(pct) + '%</div></div>'

        '<div style="flex:1;min-width:60px;background:rgba(0,33,77,0.4);'
        'border:1px solid rgba(255,255,255,0.1);border-radius:6px;padding:8px;text-align:center;">'
        '<div style="font-size:9px;color:rgba(255,255,255,0.5);letter-spacing:1px;">CHECKS</div>'
        '<div style="font-size:14px;font-weight:700;color:rgba(255,255,255,0.8);">15/DOC</div></div>'

        '</div>'
    )

    # ── 15-check matrix ───────────────────────────────────────────────────────
    CHECK_META = [
        ("step_01_header",          " 1", "Header"),
        ("step_02_footer",          " 2", "Footer"),
        ("step_03_sections",        " 3", "Sections"),
        ("step_04_fields",          " 4", "Fields"),
        ("step_05_signature",       " 5", "Signature"),
        ("step_06_product_type",    " 6", "Prod Type"),
        ("step_07_page_count",      " 7", "Pages"),
        ("step_08_party_details",   " 8", "Parties"),
        ("step_09_date_validity",   " 9", "Date"),
        ("step_10_notarisation",    "10", "Notarise"),
        ("step_11_ip_rights",       "11", "IP Rights"),
        ("step_12_audit_trail",     "12", "Audit"),
        ("step_13_confidentiality", "13", "Confid."),
        ("step_14_compliance_cert", "14", "Compliance"),
        ("step_15_zip_integrity",   "15", "ZIP"),
    ]

    mx_header = (
        '<tr style="background:rgba(0,33,77,0.85);color:#00B4D8;'
        'font-family:DM Mono,monospace;font-size:9px;">'
        '<th style="padding:5px 8px;text-align:left;min-width:120px;">Document</th>'
        '<th style="padding:5px 4px;text-align:center;">#</th>'
    )
    for _, num, lbl in CHECK_META:
        mx_header += ('<th style="padding:5px 2px;text-align:center;font-size:8px;">'
                      + num + '<br/>' + lbl + '</th>')
    mx_header += '<th style="padding:5px 6px;text-align:center;">Result</th></tr>'

    mx_rows = ""
    for idx, r in enumerate(doc_results):
        row_bg   = "rgba(0,33,77,0.25)" if idx % 2 == 0 else "rgba(0,33,77,0.12)"
        doc_name = r.get("document", "")
        short    = (doc_name[:28] + "\u2026") if len(doc_name) > 30 else doc_name
        ac       = r.get("all_checks", {})
        row = (
            '<tr style="background:' + row_bg + ';">'
            '<td style="font-size:9px;padding:5px 8px;max-width:140px;overflow:hidden;'
            'text-overflow:ellipsis;white-space:nowrap;" title="' + doc_name + '">' + short + '</td>'
            '<td style="text-align:center;font-size:9px;color:rgba(255,255,255,0.45);">' + str(idx + 1) + '</td>'
        )
        for sk, _, _ in CHECK_META:
            res = ac.get(sk, {}).get("result", "\u2014")
            row += '<td style="text-align:center;padding:3px 2px;">' + _chip(res, small=True) + '</td>'
        row += ('<td style="text-align:center;padding:4px;">'
                + _chip(r.get("overall", "\u2014")) + '</td></tr>')
        mx_rows += row

    summary_table_html = (
        '<div style="margin-bottom:14px;overflow-x:auto;">'
        '<div style="font-size:10px;color:#00B4D8;letter-spacing:1px;'
        'margin-bottom:6px;font-weight:700;">&#10003;&nbsp;ALL 15 CHECKS \u2014 DOCUMENT MATRIX'
        '<span style="font-size:8px;color:rgba(255,255,255,0.4);margin-left:8px;">'
        '(ref: ' + rules_ref + ')</span></div>'
        '<table style="width:100%;border-collapse:collapse;font-size:9px;">'
        + mx_header + mx_rows +
        '</table></div>'
    )

    # ── Per-document drill-down ───────────────────────────────────────────────
    doc_detail_blocks = []
    for r in doc_results:
        ac       = r.get("all_checks", {})
        doc_name = r.get("document", "")
        overall  = r.get("overall", "\u2014")
        ck_pass  = r.get("checks_passed", 0)
        ck_total = r.get("checks_total", 0)

        if "VERIFIED" in overall:
            hc = "#00C896"; hbg = "rgba(0,200,150,0.10)"
        elif "FAILED" in overall:
            hc = "#FF4444"; hbg = "rgba(255,68,68,0.10)"
        else:
            hc = "#FFA500"; hbg = "rgba(255,165,0,0.10)"

        det_rows = ""
        for sk, num, lbl in CHECK_META:
            chk   = ac.get(sk, {})
            res   = chk.get("result",   "\u2014")
            exp   = chk.get("expected", "\u2014")
            mth   = chk.get("method",   "\u2014")
            det   = chk.get("detail",   "\u2014")
            is_na = "N/A" in res
            rb2   = "rgba(0,0,0,0.0)"  if is_na else "rgba(0,33,77,0.15)"
            op2   = "0.50"             if is_na else "1.0"
            det_rows += (
                '<tr style="background:' + rb2 + ';opacity:' + op2 + ';">'
                '<td style="font-size:9px;padding:4px 6px;color:#00B4D8;'
                'font-weight:700;white-space:nowrap;">Step ' + num + '</td>'
                '<td style="font-size:9px;padding:4px 6px;font-weight:600;">' + lbl + '</td>'
                '<td style="font-size:8px;padding:4px 6px;color:rgba(255,255,255,0.55);">' + exp + '</td>'
                '<td style="font-size:8px;padding:4px 6px;color:rgba(255,255,255,0.45);">' + mth + '</td>'
                '<td style="text-align:center;padding:4px 4px;">' + _chip(res, small=True) + '</td>'
                '<td style="font-size:8px;padding:4px 6px;color:rgba(255,255,255,0.65);">' + det + '</td>'
                '</tr>'
            )

        block = (
            '<div style="background:' + hbg + ';border:1px solid ' + hc + ';'
            'border-radius:6px;margin-bottom:8px;overflow:hidden;">'

            '<div style="border-bottom:1px solid rgba(255,255,255,0.06);'
            'padding:7px 10px;display:flex;justify-content:space-between;align-items:center;">'
            '<span style="font-size:10px;font-weight:700;color:' + hc + ';">&#128196;&nbsp;' + doc_name + '</span>'
            '<span style="font-size:9px;">'
            + _chip(overall) +
            '&nbsp;&nbsp;<span style="color:rgba(255,255,255,0.45);">'
            + str(ck_pass) + '/' + str(ck_total) + ' checks passed'
            '</span></span></div>'

            '<div style="overflow-x:auto;">'
            '<table style="width:100%;border-collapse:collapse;">'
            '<tr style="background:rgba(0,33,77,0.7);color:rgba(0,180,216,0.8);'
            'font-family:DM Mono,monospace;font-size:8px;">'
            '<th style="padding:4px 6px;text-align:left;">Step</th>'
            '<th style="padding:4px 6px;text-align:left;">Check</th>'
            '<th style="padding:4px 6px;text-align:left;">Expected</th>'
            '<th style="padding:4px 6px;text-align:left;">Method</th>'
            '<th style="padding:4px 4px;text-align:center;">Result</th>'
            '<th style="padding:4px 6px;text-align:left;">Detail</th>'
            '</tr>'
            + det_rows +
            '</table></div></div>'
        )
        doc_detail_blocks.append(block)

    doc_details_html = (
        '<div style="margin-bottom:12px;">'
        '<div style="font-size:10px;color:#00B4D8;letter-spacing:1px;'
        'margin-bottom:8px;font-weight:700;">&#128269;&nbsp;PER-DOCUMENT DRILL-DOWN (15 CHECKS EACH)</div>'
        + "".join(doc_detail_blocks) +
        '</div>'
    )

    # ── Verification steps log ────────────────────────────────────────────────
    steps      = data.get("verification_steps", [])
    steps_block = ""
    if steps:
        step_items = "".join(
            '<div style="padding:2px 0;font-size:9px;color:rgba(255,255,255,0.65);">'
            '<span style="color:#00B4D8;font-family:DM Mono,monospace;">\u25b6</span>&nbsp;'
            + s + '</div>'
            for s in steps
        )
        steps_block = (
            '<div style="background:rgba(0,0,0,0.20);border-left:2px solid #00B4D8;'
            'border-radius:0 4px 4px 0;padding:8px 12px;margin-bottom:10px;">'
            '<div style="font-size:9px;color:#00B4D8;letter-spacing:1px;'
            'margin-bottom:4px;font-weight:700;">\u2699\ufe0f&nbsp;VERIFICATION EXECUTION LOG (15 STEPS)</div>'
            + step_items +
            '</div>'
        )

    # ── Rules reference + message ─────────────────────────────────────────────
    rules_msg_html = ""
    if message:
        rules_msg_html = (
            '<div style="background:rgba(0,33,77,0.35);border-radius:4px;'
            'padding:8px 10px;margin-bottom:8px;">'
            '<div style="font-size:9px;color:rgba(0,180,216,0.7);margin-bottom:2px;">'
            '&#128214;&nbsp;RULES REFERENCE:&nbsp;'
            '<span style="color:rgba(255,255,255,0.45);">' + rules_ref + '</span></div>'
            '<div style="font-size:11px;color:rgba(255,255,255,0.75);">&#128221;&nbsp;' + message + '</div>'
            '</div>'
        )

    # ── PART 1: Report body HTML — NO download anchors (kept small) ──────────
    # Embedding the ZIP base64 (~14 MB) in this string causes Streamlit's markdown
    # renderer to silently drop the entire block.  Downloads go in a separate call.
    report_html = (
        '<div class="verify-box" style="margin-left:54px;padding:16px;">'

        '<div class="api-response-header" style="margin-bottom:12px;">'
        '&#128269;&nbsp;VERIFICATION REPORT &nbsp;\u00b7&nbsp;'
        '<span style="font-size:10px;color:rgba(255,255,255,0.6);">'
        + agr_type + ' &nbsp;\u00b7&nbsp; ' + counterparty + ' &nbsp;\u00b7&nbsp; ' + product +
        '</span>' + ts_span + '</div>'

        + metrics_html

        + '<div style="background:' + verdict_bg + ';border:1px solid ' + verdict_color + ';'
        'border-radius:6px;padding:10px 14px;margin-bottom:14px;text-align:center;'
        'font-size:13px;font-weight:700;color:' + verdict_color + ';">'
        + verdict_icon + '&nbsp;&nbsp;' + verdict_text + '</div>'

        + summary_table_html
        + doc_details_html
        + steps_block
        + rules_msg_html

        + '</div>'
    )
    st.markdown(report_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT PANEL
# ══════════════════════════════════════════════════════════════════════════════

def render_input_panel() -> None:
    state = get_state("flow_state", "IDLE")
    st.markdown('<div class="input-zone">', unsafe_allow_html=True)
    _text_input_for_state(state)
    _render_mic_bar()
    st.markdown("</div>", unsafe_allow_html=True)


# ── Persistent mic bar ─────────────────────────────────────────────────────────

def _render_mic_bar() -> None:
    """
    Always-visible voice input bar at the bottom of the input zone.
    Layout: [Language selector] | [Mic button] | [Last voice status]

    audio-recorder-streamlit 0.0.10 API:
      audio_recorder(text, recording_color, neutral_color,
                     icon_name, icon_size, pause_threshold, key)
      Returns bytes or None.
    """
    st.markdown(
        '<div style="margin-top:12px;border-top:1px solid rgba(255,255,255,0.10);'
        'padding-top:10px;"></div>',
        unsafe_allow_html=True,
    )

    lang_opts = ["English", "हिंदी (Hindi)", "मराठी (Marathi)", "Deutsch (German)", "普通话 (Mandarin)"]
    col_lang, col_mic, col_status = st.columns([3, 1, 5])

    with col_lang:
        lang = st.selectbox(
            "🌐 Language",
            lang_opts,
            index=lang_opts.index(st.session_state.get("language", "English")),
            key="mic_lang",
        )
        st.session_state["language"] = lang

    with col_mic:
        st.markdown("**&#127897; Talk**")
        _mic_button()

    with col_status:
        last = st.session_state.get("last_voice_text", "")
        lock = st.session_state.get("cmd_lock", False)
        if lock:
            st.markdown(
                '<div style="font-family:DM Mono,monospace;font-size:11px;'
                'color:var(--accent-cyan);padding:20px 0 0;">&#9881;&#65039; Processing&hellip;</div>',
                unsafe_allow_html=True,
            )
        elif last:
            display = last[:55]
            st.markdown(
                '<div style="font-family:DM Mono,monospace;font-size:11px;'
                'color:var(--accent-cyan);padding:20px 0 0;overflow:hidden;'
                'white-space:nowrap;text-overflow:ellipsis;">'
                "&#127897; &ldquo;{0}&rdquo;</div>".format(display),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-family:DM Mono,monospace;font-size:10px;'
                'color:rgba(255,255,255,0.35);padding:20px 0 0;letter-spacing:2px;">'
                "CLICK MIC &middot; SPEAK &middot; RELEASE</div>",
                unsafe_allow_html=True,
            )


def _mic_button() -> None:
    """
    audio-recorder-streamlit 0.0.10 compatible mic widget.

    Guards applied in order:
      1. audio_already_processed() — same bytes seen before → skip
      2. cmd_lock check            — another command running → skip
      3. transcribe_audio()        — convert to text
      4. handle_user_input()       — process as one command

    st.toast() is NOT available in streamlit 1.28.0+;
    st.warning() is used as replacement.
    """
    try:
        from audio_recorder_streamlit import audio_recorder
        # audio-recorder-streamlit 0.0.10 API
        audio_bytes = audio_recorder(
            text="",
            recording_color="#38BEFF",
            neutral_color="#1A3ED4",
            icon_name="microphone",
            icon_size="lg",
            pause_threshold=2.0,
            key="dia_mic",
        )

        if not audio_bytes or len(audio_bytes) < 800:
            return

        # Guard 1: skip already-processed audio
        if audio_already_processed(audio_bytes):
            return

        # Guard 2: skip if locked
        if st.session_state.get("cmd_lock", False):
            return

        # Transcribe
        lang = st.session_state.get("language", "English")
        from core.stt import transcribe_audio
        with st.spinner("🎤 Recognising..."):
            transcript = transcribe_audio(audio_bytes, language=lang)

        if transcript and transcript.strip():
            st.session_state["last_voice_text"] = transcript
            handle_user_input(transcript, is_audio=True)
            st.rerun()
        else:
            st.session_state["last_voice_text"] = ""
            # st.toast not available in 1.56.0 → use st.warning
            st.warning("&#127897; Could not recognise speech. Please try again.")

    except ImportError:
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:9px;'
            'color:#ff4444;">Install: pip install audio-recorder-streamlit==0.0.10</div>',
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.warning("Voice error: {0}".format(str(exc)))


# ══════════════════════════════════════════════════════════════════════════════
#  STATE → INPUT PANEL DISPATCH
# ══════════════════════════════════════════════════════════════════════════════

def _text_input_for_state(state: str) -> None:
    dispatch = {
        "IDLE":                  _panel_main,
        "AWAIT_MENU":            _panel_main,
        "DONE":                  _panel_main,
        "POST_AUTH_WELCOME":     _panel_post_auth_welcome,
        "ASK_NAME":              lambda: _panel_single(
            "&#128100; Please enter your full name:", "n", "ni", "e.g. Rahul Sharma"),
        "SHOW_HISTORY":          _panel_show_history,
        "SHOW_HISTORY_CHOICE":   _panel_history_choice,
        "ASK_AGREE_TYPE":        _panel_agreement_type,
        "ASK_PRODUCT_TYPE":      _panel_product_type,
        "ASK_PARTY":             lambda: _panel_single(
            "&#127970; Counterparty name:", "p", "pi", "e.g. ABC Pvt Ltd"),
        "ASK_VALUE":             lambda: _panel_single(
            "&#128176; Value / Duration:", "v", "vi", "e.g. Rs.5,00,000 or 2 years"),
        "CONFIRM_NEW":           _panel_confirm,
        "CONFIRM_REGEN":         _panel_confirm,
        "AGREEMENT_CREATED":     _panel_confirm_docs,
        "CONFIRM_GENERATE_DOCS": _panel_confirm_docs,
        "DOCS_READY":            _panel_docs_ready,
        "VIEW_DOC":              lambda: _panel_single(
            "&#128196; Document number or name:", "vd", "vdi",
            "e.g. 1  or  NDA_ABC_Main.pdf"),
        "ASK_POST_DOCS_VERIFY":  _panel_post_docs_verify,
        "VERIFY_ASK_PARTY":      lambda: _panel_single(
            "&#127970; Counterparty name:", "vp", "vpi", "e.g. TechCorp Ltd"),
        "VERIFY_ASK_TYPE":       _panel_agreement_type,
        "VERIFY_ASK_PRODUCT":    _panel_product_type,
        "VERIFY_ASK_VALUE":      lambda: _panel_single(
            "&#128176; Agreement Value / Duration:", "vv", "vvi", "e.g. Rs.10,00,000"),
    }
    fn = dispatch.get(state, _panel_main)
    fn()


def _panel_post_auth_welcome() -> None:
    """Quick-action buttons shown right after face-auth personalised welcome."""
    docs = get_state("user_documents", [])
    name = get_state("current_user", "")
    label = "Welcome back{0} — what would you like to do?".format(
        ", {}".format(name) if name else ""
    )
    st.markdown(_lbl(label), unsafe_allow_html=True)

    if docs:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✨ Fresh New Agreement", use_container_width=True, key="paw_fresh"):
                handle_user_input("fresh agreement", _internal=True)
                st.rerun()
        with c2:
            if st.button("📋 Use Past Agreement", use_container_width=True, key="paw_hist"):
                handle_user_input("show my agreement history", _internal=True)
                st.rerun()
        with c3:
            if st.button("🔍 Verify Document", use_container_width=True, key="paw_ver"):
                handle_user_input("verify document", _internal=True)
                st.rerun()
    else:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✨ Generate New Agreement", use_container_width=True, key="paw_new"):
                handle_user_input("create new agreement", _internal=True)
                st.rerun()
        with c2:
            if st.button("🔍 Verify Document", use_container_width=True, key="paw_ver2"):
                handle_user_input("verify document", _internal=True)
                st.rerun()
    _free("paw_free", "Or type your choice here…")


def _panel_main() -> None:
    st.markdown(
        '<div style="font-family:DM Mono,monospace;font-size:10px;'
        'color:rgba(255,255,255,0.40);margin-bottom:8px;letter-spacing:2px;">'
        "SELECT A SERVICE OR TYPE / SPEAK BELOW</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚖️ Generate Agreement", use_container_width=True, key="pm_gen"):
            handle_user_input("i want to generate agreement", _internal=True)
            st.rerun()
    with c2:
        if st.button("🔍 Verify Document", use_container_width=True, key="pm_ver"):
            handle_user_input("verify document", _internal=True)
            st.rerun()
    with c3:
        if st.button("📋 Agreement History", use_container_width=True, key="pm_his"):
            handle_user_input("show my agreement history", _internal=True)
            st.rerun()
    _free("mc", "Type your message here&hellip;")


def _panel_show_history() -> None:
    st.markdown(_lbl("Regenerate from history or create a new agreement?"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Yes — Regenerate from History", use_container_width=True, key="sh_yes"):
            handle_user_input("yes i want to regenerate", _internal=True)
            st.rerun()
    with c2:
        if st.button("✨ Create New Agreement", use_container_width=True, key="sh_new"):
            handle_user_input("create new agreement", _internal=True)
            st.rerun()
    with c3:
        if st.button("🔙 No — Main Menu", use_container_width=True, key="sh_no"):
            handle_user_input("no", _internal=True)
            st.rerun()


def _panel_history_choice() -> None:
    docs = get_state("user_documents", [])
    st.markdown(_lbl("Select an agreement to regenerate:"), unsafe_allow_html=True)
    if docs:
        cols = st.columns(min(len(docs), 3))
        for i, doc in enumerate(docs):
            with cols[i % len(cols)]:
                label = "{0}. {1}".format(i + 1, doc.get("type", "")[:22])
                btn_k = "hc_{0}_{1}".format(i, doc.get("id", "")[:6])
                if st.button(label, key=btn_k, use_container_width=True):
                    handle_user_input(str(i + 1), _internal=True)
                    st.rerun()
    _free("hcf", "Or type agreement number / type&hellip;")


def _panel_agreement_type() -> None:
    types = [
        "Non-Disclosure Agreement",
        "Service Agreement",
        "Rental Agreement",
        "Loan Agreement",
        "Employment Contract",
        "Partnership Deed",
        "Memorandum of Understanding",
        "Vendor Agreement",
        "Consultancy Agreement",
        "Account Opening Agreement",
        "Foreign Exchange Agreement",
        "Electronic Banking Agreement",
    ]
    st.markdown(_lbl("&#128196; Select Agreement Type:"), unsafe_allow_html=True)
    c1, c2 = st.columns([7, 3])
    with c1:
        sel = st.selectbox("at", types, label_visibility="collapsed", key="at_sel")
    with c2:
        if st.button("SELECT ▶", use_container_width=True, key="at_btn"):
            handle_user_input(sel)
            st.rerun()
    _free("at_f", "Or type agreement type&hellip;")


def _panel_product_type() -> None:
    st.markdown(_lbl("&#128230; Select Product Type:"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, pt in zip([c1, c2, c3], ["EBICS", "MT101", "CC"]):
        with col:
            if st.button(pt, key="ptype_{0}".format(pt), use_container_width=True):
                handle_user_input(pt)
                st.rerun()


def _panel_confirm() -> None:
    st.markdown(
        '<div style="font-family:DM Sans,sans-serif;font-size:11px;'
        'color:var(--accent-cyan);letter-spacing:2px;margin-bottom:10px;">'
        "&#9888; AWAITING CONFIRMATION</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([3, 3, 4])
    with c1:
        if st.button("✅ YES — PROCEED", use_container_width=True, key="cf_y"):
            handle_user_input("yes")
            st.rerun()
    with c2:
        if st.button("❌ NO — CANCEL", use_container_width=True, key="cf_n"):
            handle_user_input("no")
            st.rerun()
    with c3:
        _free("cf_t", "Or type Yes / No&hellip;")


def _panel_confirm_docs() -> None:
    st.markdown(_lbl("&#128196; Generate documents for this Agreement?"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 3, 4])
    with c1:
        if st.button("🚀 YES — GENERATE", use_container_width=True, key="gd_y"):
            handle_user_input("yes generate documents")
            st.rerun()
    with c2:
        if st.button("❌ NOT NOW", use_container_width=True, key="gd_n"):
            handle_user_input("no")
            st.rerun()
    with c3:
        _free("gd_t", "Or type Yes / No&hellip;")


def _panel_docs_ready() -> None:
    result = get_state("generated_docs", {})
    docs   = result.get("documents", [])
    st.markdown(_lbl("&#128196; Which document would you like to view?"), unsafe_allow_html=True)
    if docs:
        cpr = 3
        for rs in range(0, len(docs), cpr):
            row  = docs[rs:rs + cpr]
            cols = st.columns(len(row))
            for col, doc in zip(cols, row):
                with col:
                    name = doc.get("name", "")
                    short = name[:22] + ("…" if len(name) > 22 else "")
                    btn_k = "dr_{0}".format(name[:14])
                    if st.button("👁 {0}".format(short), key=btn_k, use_container_width=True):
                        trigger_open_document(name)
                        st.rerun()
    _free("dr_t", "Or say / type document number or name&hellip;")


def _panel_post_docs_verify() -> None:
    """Yes/No panel shown after user views a document — offer to verify."""
    st.markdown(
        _lbl("&#128269; Would you like to verify the generated documents?"),
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([3, 3, 4])
    with c1:
        if st.button("🔍 YES — VERIFY", use_container_width=True, key="pdv_yes"):
            handle_user_input("yes", _internal=True)
            st.rerun()
    with c2:
        if st.button("❌ NO — FINISH", use_container_width=True, key="pdv_no"):
            handle_user_input("no", _internal=True)
            st.rerun()
    with c3:
        _free("pdv_t", "Type Yes or No&hellip;")


def _panel_single(label: str, k: str, ik: str, ph: str) -> None:
    st.markdown(_lbl(label), unsafe_allow_html=True)
    c1, c2 = st.columns([8, 2])
    with c1:
        val = st.text_input(k, placeholder=ph, key=ik + "_w", label_visibility="collapsed")
    with c2:
        if st.button("▶", key=ik + "_b", use_container_width=True):
            if val.strip():
                handle_user_input(val.strip())
                st.rerun()


def _free(key: str, ph: str) -> None:
    c1, c2 = st.columns([9, 1])
    with c1:
        val = st.text_input(key, placeholder=ph, key=key + "_t", label_visibility="collapsed")
    with c2:
        if st.button("▶", key=key + "_s", use_container_width=True):
            if val.strip():
                handle_user_input(val.strip())
                st.rerun()


def _lbl(text: str) -> str:
    return (
        '<div style="font-family:DM Mono,monospace;font-size:11px;'
        'color:var(--accent-cyan);letter-spacing:1px;margin-bottom:8px;">'
        "&#9889; {0}</div>".format(text)
    )
