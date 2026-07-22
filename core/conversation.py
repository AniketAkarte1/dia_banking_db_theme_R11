"""
DIA Conversation Engine — Python 3.9+ compatible.
Changes vs previous:
  - Optional / Dict / Any from typing (not X | None syntax)
  - No walrus operator (:=), no match/case, no structural pattern matching
  - All type annotations use typing module forms
  - FREE_FORM_STATES bypasses intent detection for raw data entry
  - cmd_lock prevents task chaining from voice commands
"""
from typing import Optional, Dict, List, Any, Callable

import streamlit as st

from core.intent import (
    detect_intent, is_confirmation, is_cancellation, extract_doc_name,
)
from core.language import get_response, get_audio_response
from core.session import (
    add_message, get_state, set_state,
    acquire_cmd_lock, release_cmd_lock,
)
from core.tts import speak_text
from data.dummy_data import get_user_documents, add_to_history, PRODUCT_TYPES
from services.document_api import (
    call_create_agreement_api,
    call_regenerate_agreement_api,
    call_generate_documents_api,
    call_verify_documents_api,
)
from services.download_helper import get_zip_download_link, get_single_file_link

def _resolve_url(url: str) -> str:
    """Resolve sentinel download URLs to real base64 anchors."""
    if url == "__sample_zip__":
        return get_zip_download_link(label="Download All as ZIP", filename="sample_documents.zip", css_class="zip-link")
    if url.startswith("__sample_download__:"):
        fname = url.split(":", 1)[1]
        return get_single_file_link(filename=fname, label="📥 View / Download", css_class="zip-link")
    return f'<a href="{url}" target="_blank">📥 View / Download</a>'

# ── States that expect RAW FREE-FORM input ─────────────────────────────────────
# In these states, ANYTHING spoken/typed is treated as the answer value.
# Intent detection is completely bypassed; only cancellation is checked.
FREE_FORM_STATES: set = {
    "ASK_NAME",           # user gives their name
    "ASK_PARTY",          # user gives counterparty name
    "ASK_VALUE",          # user gives value / duration
    "VERIFY_ASK_PARTY",   # user gives counterparty for verification
    "VERIFY_ASK_VALUE",   # user gives value for verification
    "VIEW_DOC",           # user says doc name or number
}

# ── States that accept a selection from a fixed list ──────────────────────────
SELECTION_STATES: set = {
    "ASK_AGREE_TYPE",     # agreement type (typed or picked from dropdown)
    "ASK_PRODUCT_TYPE",   # EBICS / MT101 / CC
    "VERIFY_ASK_TYPE",    # agreement type for verify
    "VERIFY_ASK_PRODUCT", # product type for verify
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def _lang() -> str:
    return st.session_state.get("language", "English")

def _audio() -> bool:
    return st.session_state.get("audio_enabled", True)

def _say_key(
    key: str,
    msg_type: str = "text",
    extra: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """Add a DIA message using a language-file key."""
    lang    = _lang()
    chat    = get_response(key, lang, **kwargs)
    audio_t = get_audio_response(key, lang, **kwargs)
    apath   = speak_text(audio_t, lang) if _audio() else None
    add_message("dia", chat, msg_type=msg_type, extra=extra, audio_path=apath)

def _say(
    chat: str,
    audio: str,
    msg_type: str = "text",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Add a DIA message with explicit chat and audio strings."""
    apath = speak_text(audio, _lang()) if _audio() else None
    add_message("dia", chat, msg_type=msg_type, extra=extra, audio_path=apath)

def _user(text: str) -> None:
    add_message("user", text)

# ── Batch (multi-part → single bubble) ────────────────────────────────────────
# When a handler needs to emit several logical paragraphs they MUST all land in
# ONE chat bubble and play as ONE audio clip.
#
# Usage:
#   _batch_begin()
#   _batch_add(chat_html, audio_text)          # repeat as needed
#   _batch_add_key(key, msg_type, extra, **kw) # for language-file keys
#   _batch_end(msg_type, extra)                # flushes to a single message
#
# Rules
#   • _batch_add / _batch_add_key NEVER write to session.messages directly.
#   • _batch_end writes exactly ONE message and resets the buffer.
#   • If _batch_end is never called the buffer is silently discarded.

_BATCH: Dict[str, Any] = {
    "active":   False,
    "chat":     [],    # list[str]  – HTML fragments
    "audio":    [],    # list[str]  – plain-text fragments
}

def _batch_begin() -> None:
    _BATCH["active"] = True
    _BATCH["chat"]   = []
    _BATCH["audio"]  = []

def _batch_add(chat: str, audio: str) -> None:
    """Accumulate a chat fragment + its audio narration."""
    if not _BATCH["active"]:
        # Safety: if called outside a batch, fall through to normal _say
        _say(chat, audio)
        return
    _BATCH["chat"].append(chat)
    _BATCH["audio"].append(audio)

def _batch_add_key(
    key: str,
    msg_type: str = "text",
    extra: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """Accumulate a language-file keyed response into the batch."""
    if not _BATCH["active"]:
        _say_key(key, msg_type=msg_type, extra=extra, **kwargs)
        return
    lang   = _lang()
    chat   = get_response(key, lang, **kwargs)
    audio  = get_audio_response(key, lang, **kwargs)
    _BATCH["chat"].append(chat)
    _BATCH["audio"].append(audio)

def _batch_end(
    msg_type: str = "text",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Flush all accumulated fragments as a single message + single audio clip."""
    if not _BATCH["active"]:
        return
    joined_chat  = "<br><br>".join(c for c in _BATCH["chat"] if c)
    joined_audio = " ".join(a for a in _BATCH["audio"] if a)
    _BATCH["active"] = False
    _BATCH["chat"]   = []
    _BATCH["audio"]  = []
    if not joined_chat:
        return
    apath = speak_text(joined_audio, _lang()) if _audio() else None
    add_message("dia", joined_chat, msg_type=msg_type, extra=extra, audio_path=apath)


def _options_msg() -> None:
    """Show the three main service options."""
    _say(
        "Please choose:<br>"
        "1&#65039;&#8419; &nbsp;<b>Generate Agreement from History</b><br>"
        "2&#65039;&#8419; &nbsp;<b>Generate a New Agreement</b><br>"
        "3&#65039;&#8419; &nbsp;<b>Verify Document</b>",
        "Please choose. "
        "Option 1: Generate Agreement from History. "
        "Option 2: Generate a New Agreement. "
        "Option 3: Verify Document.",
    )

# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC ENTRY POINT — ONE COMMAND = ONE TASK
# ══════════════════════════════════════════════════════════════════════════════

def handle_user_input(
    text: str,
    is_audio: bool = False,
    _internal: bool = False,
) -> None:
    """
    Single-execution gate.
    Acquires cmd_lock → routes to exactly ONE handler → releases lock.

    FREE_FORM_STATES bypass intent detection entirely so that names,
    company names, monetary values etc. spoken via voice are always
    accepted as the expected data value.
    """
    if not acquire_cmd_lock():
        return  # another command is executing — drop silently

    # Safety: reset batch buffer before every input to avoid stale state
    _BATCH["active"] = False
    _BATCH["chat"]   = []
    _BATCH["audio"]  = []

    try:
        state = get_state("flow_state", "IDLE")
        if not _internal:
            _user(text)

        # ── Free-form data-entry states (bypass intent detection) ──────────────
        if state in FREE_FORM_STATES:
            _FREEFORM: Dict[str, Callable[[str], None]] = {
                "ASK_NAME":         _handle_name,
                "ASK_PARTY":        _handle_party_name,
                "ASK_VALUE":        _handle_value,
                "VERIFY_ASK_PARTY": _handle_verify_party,
                "VERIFY_ASK_VALUE": _handle_verify_value,
                "VIEW_DOC":         _handle_view_doc,
            }
            handler = _FREEFORM.get(state)
            if handler:
                handler(text)

        # ── Selection states (bypass intent; accept raw typed/spoken value) ────
        elif state in SELECTION_STATES:
            _SELECTION: Dict[str, Callable[[str], None]] = {
                "ASK_AGREE_TYPE":    _handle_agreement_type,
                "ASK_PRODUCT_TYPE":  _handle_product_type,
                "VERIFY_ASK_TYPE":   _handle_verify_type,
                "VERIFY_ASK_PRODUCT":_handle_verify_product,
            }
            handler = _SELECTION.get(state)
            if handler:
                handler(text)

        # ── Intent-based states ────────────────────────────────────────────────
        else:
            _ROUTES: Dict[str, Callable[[str], None]] = {
                "AWAIT_MENU":              _route_menu,
                "DONE":                   _route_menu,
                "POST_AUTH_WELCOME":      _handle_post_auth_welcome,
                "SHOW_HISTORY":           _handle_show_history,
                "SHOW_HISTORY_CHOICE":    _handle_history_choice,
                "CONFIRM_NEW":            _handle_confirm_new,
                "CONFIRM_REGEN":          _handle_confirm_regen,
                "AGREEMENT_CREATED":      _handle_agreement_created,
                "CONFIRM_GENERATE_DOCS":  _handle_confirm_generate_docs,
                "DOCS_READY":             _handle_docs_ready,
                "ASK_POST_DOCS_VERIFY":   _handle_post_docs_verify,
            }
            handler = _ROUTES.get(state)
            if handler:
                handler(text)
            else:
                # IDLE or truly unknown state
                if not get_state("greeted", False):
                    _do_greeting()
                else:
                    _route_menu(text)

    finally:
        release_cmd_lock()

# ══════════════════════════════════════════════════════════════════════════════
#  GREETING — once per session
# ══════════════════════════════════════════════════════════════════════════════

def _do_greeting() -> None:
    # ── Face-auth user identified — personalised welcome flow ─────────────────
    face_user = st.session_state.get("face_auth_user")
    if face_user:
        if not get_state("current_user"):
            set_state("current_user", face_user)

        lang = _lang()
        from core.language import FACE_WELCOME, FACE_WELCOME_AUDIO
        welcome_chat  = FACE_WELCOME.get(lang,  FACE_WELCOME["English"]).format(name=face_user)
        welcome_audio = FACE_WELCOME_AUDIO.get(lang, FACE_WELCOME_AUDIO["English"]).format(name=face_user)

        intro_chat = (
            "I am <b>DIA</b> — your <b>AI Legal Agreement Assistant</b> from Deutsche Bank.<br><br>"
            "I am here to help you with:<br>"
            "⚖️ &nbsp;<b>Generate Legal / Bank Agreements</b><br>"
            "🔍 &nbsp;<b>Verify Generated Documents</b><br>"
            "📋 &nbsp;<b>Fetch &amp; Regenerate Your Agreement History</b>"
        )
        intro_audio = (
            "I am DIA, your AI Legal Agreement Assistant from Deutsche Bank. "
            "I can help you generate legal or bank agreements, verify documents, "
            "and manage your agreement history."
        )

        docs = get_user_documents(face_user)
        set_state("user_documents", docs)

        if docs:
            count = len(docs)
            choice_chat = (
                "I can see you have <b>{count}</b> past agreement(s) on file, {name}.<br><br>"
                "Would you like to:<br>"
                "1️⃣ &nbsp;<b>Generate a Fresh New Agreement</b><br>"
                "2️⃣ &nbsp;<b>Use a Past Agreement from Your History</b><br><br>"
                "Please choose an option or say <b>Fresh</b> / <b>History</b>."
            ).format(count=count, name=face_user)
            choice_audio = (
                "I can see you have {count} past agreements on file. "
                "Would you like to generate a fresh new agreement, "
                "or use one from your history? Say Fresh or History."
            ).format(count=count)
        else:
            choice_chat = (
                "It looks like this is your first visit, <b>{name}</b>. "
                "Let me help you create your first agreement!<br><br>"
                "How may I assist you today?<br>"
                "1️⃣ &nbsp;<b>Generate a New Agreement</b><br>"
                "2️⃣ &nbsp;<b>Verify a Document</b>"
            ).format(name=face_user)
            choice_audio = (
                "It looks like this is your first visit, {name}. "
                "Let me help you create your first agreement. "
                "Would you like to generate a new agreement, or verify a document? "
                "Say One for New Agreement or Two for Verify."
            ).format(name=face_user)

        # ── Single merged bubble: welcome + intro + choice ──────────────────
        _batch_begin()
        _batch_add(
            "{}<br><br>{}".format(welcome_chat, intro_chat),
            "{}. {}".format(welcome_audio, intro_audio),
        )
        _batch_add(choice_chat, choice_audio)
        _batch_end()

        set_state("greeted", True)
        set_state("flow_state", "POST_AUTH_WELCOME")
        return

    # ── Generic greeting (no face-auth user) — one merged bubble ─────────────
    _batch_begin()
    _batch_add_key("greeting")
    _batch_add(
        "Please choose:<br>"
        "1&#65039;&#8419; &nbsp;<b>Generate Agreement from History</b><br>"
        "2&#65039;&#8419; &nbsp;<b>Generate a New Agreement</b><br>"
        "3&#65039;&#8419; &nbsp;<b>Verify Document</b>",
        "Please choose. "
        "Option 1: Generate Agreement from History. "
        "Option 2: Generate a New Agreement. "
        "Option 3: Verify Document.",
    )
    _batch_end()
    set_state("greeted", True)
    set_state("flow_state", "AWAIT_MENU")

def trigger_greeting() -> None:
    """Called from layout on first page load."""
    if not get_state("greeted", False):
        if not acquire_cmd_lock():
            return
        try:
            _do_greeting()
        finally:
            release_cmd_lock()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN MENU ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def _route_menu(text: str) -> None:
    intent = detect_intent(text)

    if intent == "greet":
        if not get_state("greeted", False):
            _do_greeting()
        else:
            _options_msg()
            set_state("flow_state", "AWAIT_MENU")
        return

    if intent in ("generate_document", "generate_history",
                  "regenerate_old", "view_history", "new_fresh"):
        # If user already identified via face-auth, skip asking their name
        face_user = st.session_state.get("face_auth_user")
        current_user = get_state("current_user")
        known_user = face_user or current_user
        if known_user:
            set_state("current_user", known_user)
            docs = get_user_documents(known_user)
            set_state("user_documents", docs)
            set_state("pending_intent", intent)
            if intent in ("generate_history", "regenerate_old", "view_history"):
                if docs:
                    names_html = "".join([
                        "<br>&nbsp;&nbsp;<b>{0}.</b> {1} — {2} &nbsp;|&nbsp; {3}".format(
                            i + 1, d.get("type", ""), d.get("party", ""), d.get("date", "")
                        )
                        for i, d in enumerate(docs)
                    ])
                    names_audio = ". ".join([
                        "{0}: {1} with {2}".format(i + 1, d.get("type", ""), d.get("party", ""))
                        for i, d in enumerate(docs)
                    ])
                    _say(
                        "Here are your past agreements:<br>{0}<br><br>"
                        "Please say the <b>agreement number</b> or party name to regenerate.".format(names_html),
                        "Here are your past agreements. {0}. "
                        "Please say the agreement number you want to regenerate.".format(names_audio),
                        msg_type="doc_history",
                        extra={"documents": docs},
                    )
                    set_state("flow_state", "SHOW_HISTORY_CHOICE")
                else:
                    _batch_begin()
                    _batch_add_key("history_empty", name=known_user)
                    _batch_add_key("ask_agreement_type")
                    _batch_end()
                    set_state("flow_state", "ASK_AGREE_TYPE")
            else:
                _say_key("ask_agreement_type")
                set_state("flow_state", "ASK_AGREE_TYPE")
        else:
            set_state("pending_intent", intent)
            _say_key("ask_name")
            set_state("flow_state", "ASK_NAME")
        return

    if intent == "verify_document":
        _say(
            "🔍 <b>Document Verification</b><br>"
            "Please provide the <b>counterparty / first party name</b>:",
            "To verify documents, please provide the counterparty name.",
        )
        set_state("flow_state", "VERIFY_ASK_PARTY")
        return

    if intent in ("yes_confirm", "no_cancel"):
        _options_msg()
        set_state("flow_state", "AWAIT_MENU")
        return

    _say_key("clarify")

# ══════════════════════════════════════════════════════════════════════════════
#  FREE-FORM HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

def _handle_post_auth_welcome(text: str) -> None:
    """
    Handles the initial choice AFTER face-auth personalised greeting:
    - Fresh new agreement  (option 1 always)
    - Use history          (option 2 when history exists, else skip to create)
    - Verify document      (option 2 when no history, option 3 when history exists)
    """
    if is_cancellation(text):
        _cancelled_to_menu()
        return

    intent    = detect_intent(text)
    text_low  = text.lower().strip()
    docs      = get_state("user_documents", [])
    has_docs  = bool(docs)

    # ── Option 1 / Fresh / New Agreement ─────────────────────────────────────
    wants_fresh = (
        intent in ("new_fresh", "generate_document")
        or text_low in ("1", "one", "option 1", "option one")
        or any(kw in text_low for kw in ("fresh", "new agreement", "create new", "brand new", "start fresh"))
    )
    if wants_fresh:
        _say_key("ask_agreement_type")
        set_state("flow_state", "ASK_AGREE_TYPE")
        return

    # ── Option 2 / History (only when user has docs) ──────────────────────────
    wants_history = (
        intent in ("generate_history", "regenerate_old", "view_history")
        or (has_docs and text_low in ("2", "two", "option 2", "option two"))
        or any(kw in text_low for kw in ("history", "past", "old agreement", "previous", "existing", "regenerate"))
    )
    if wants_history:
        if not docs:
            _batch_begin()
            _batch_add(
                "You don't have any past agreements yet. Let me help you create your first one.",
                "You don't have any past agreements yet. Let me help you create your first one.",
            )
            _batch_add_key("ask_agreement_type")
            _batch_end()
            set_state("flow_state", "ASK_AGREE_TYPE")
            return

        # Render the history list inline and move to selection
        names_html = "".join([
            "<br>&nbsp;&nbsp;<b>{0}.</b> {1} — {2} &nbsp;|&nbsp; {3} &nbsp;|&nbsp; "
            '<span style="color:#4ECCA3;">{4}</span>'.format(
                i + 1,
                d.get("type", ""),
                d.get("party", ""),
                d.get("date", ""),
                d.get("status", ""),
            )
            for i, d in enumerate(docs)
        ])
        names_audio = ". ".join([
            "{0}: {1} with {2}, status {3}".format(
                i + 1, d.get("type", ""), d.get("party", ""), d.get("status", "")
            )
            for i, d in enumerate(docs)
        ])
        _say(
            "Here are your past agreements:<br>{0}<br><br>"
            "Please say the <b>agreement number</b> or the <b>party / type name</b> "
            "of the one you'd like to regenerate.".format(names_html),
            "Here are your past agreements. {0}. "
            "Please say the agreement number you want to regenerate.".format(names_audio),
            msg_type="doc_history",
            extra={"documents": docs},
        )
        set_state("flow_state", "SHOW_HISTORY_CHOICE")
        return

    # ── Option 2 (no-history) or Option 3 (with-history) / Verify ────────────
    verify_num = (
        (not has_docs and text_low in ("2", "two", "option 2", "option two"))
        or (has_docs and text_low in ("3", "three", "option 3", "option three"))
    )
    wants_verify = (
        intent == "verify_document"
        or verify_num
        or any(kw in text_low for kw in ("verify", "check document", "validate"))
    )
    if wants_verify:
        _say(
            "🔍 <b>Document Verification</b><br>"
            "Please provide the <b>counterparty / first party name</b>:",
            "To verify documents, please provide the counterparty name.",
        )
        set_state("flow_state", "VERIFY_ASK_PARTY")
        return

    # ── Fallback ──────────────────────────────────────────────────────────────
    name = get_state("current_user", "")
    docs = get_state("user_documents", [])
    if docs:
        _say(
            "Please choose, {}:<br>"
            "1️⃣ &nbsp;<b>Fresh New Agreement</b><br>"
            "2️⃣ &nbsp;<b>Use Past Agreement from History</b><br>"
            "3️⃣ &nbsp;<b>Verify a Document</b>".format(name),
            "Please say Fresh for a new agreement, History to use a past one, "
            "or Verify to check a document.",
        )
    else:
        _say_key("clarify")


def _handle_name(name: str) -> None:
    """FREE-FORM: Accept any non-empty, non-cancel string as the user name."""
    name = name.strip()
    if is_cancellation(name):
        _cancelled_to_menu()
        return
    if not name or len(name) < 2:
        _say(
            "I didn't catch that. Could you please say your full name again?",
            "I didn't catch that. Could you please say your full name again?",
        )
        return

    set_state("current_user", name)
    _say_key("fetching", name=name)
    docs = get_user_documents(name)
    set_state("user_documents", docs)

    if docs:
        count   = len(docs)
        summary = ". ".join([
            "Agreement {0}: {1} with {2}, status {3}".format(
                i + 1, d["type"], d["party"], d["status"]
            )
            for i, d in enumerate(docs)
        ])
        _batch_begin()
        _batch_add(
            "I found <b>{0}</b> agreement(s) for <b>{1}</b>. "
            "Here is your history:".format(count, name),
            "I found {0} agreements for {1}. {2}".format(count, name, summary),
        )
        _batch_add(
            "Do you want to <b>regenerate</b> a document from any of these agreements, "
            "or would you like to create a <b>fresh new agreement</b>?",
            "Do you want to regenerate a document from any of these agreements, "
            "or would you like to create a fresh new agreement?",
        )
        _batch_end(msg_type="doc_history", extra={"documents": docs})
        set_state("flow_state", "SHOW_HISTORY")
    else:
        _batch_begin()
        _batch_add_key("history_empty", name=name)
        _batch_add_key("ask_agreement_type")
        _batch_end()
        set_state("flow_state", "ASK_AGREE_TYPE")


def _handle_party_name(text: str) -> None:
    """FREE-FORM: Accept any counterparty name."""
    text = text.strip()
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    if not text:
        _say("Please provide the counterparty name.",
             "Please provide the counterparty name.")
        return
    set_state("party_name", text)
    _say_key("ask_value")
    set_state("flow_state", "ASK_VALUE")


def _handle_value(text: str) -> None:
    """FREE-FORM: Accept any value / duration string."""
    text = text.strip()
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    if not text:
        _say("Please provide the value or duration for this agreement.",
             "Please provide the value or duration for this agreement.")
        return
    d1 = get_state("party_name", "")
    d2 = get_state("agreement_type", "")
    d3 = text
    pt = get_state("product_type", "EBICS")
    set_state("new_doc_details", {"detail1": d1, "detail2": d2, "detail3": d3, "product_type": pt})
    _say_key("confirm_new_agreement", detail1=d1, detail2=d2, detail3=d3)
    set_state("flow_state", "CONFIRM_NEW")


def _handle_verify_party(text: str) -> None:
    """FREE-FORM: Accept any counterparty name for verification."""
    text = text.strip()
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    if not text:
        _say("Please provide the counterparty name.",
             "Please provide the counterparty name.")
        return
    set_state("verify_party", text)
    _say(
        "Thank you. Please provide the <b>Agreement Type</b> to verify:",
        "Thank you. Please provide the agreement type.",
    )
    set_state("flow_state", "VERIFY_ASK_TYPE")


def _handle_verify_value(text: str) -> None:
    """FREE-FORM: Accept any value / duration for verification."""
    text = text.strip()
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    if not text:
        _say("Please provide the value or duration.",
             "Please provide the value or duration.")
        return
    party = get_state("verify_party", "")
    agr   = get_state("verify_agree_type", "")
    pt    = get_state("verify_product_type", "EBICS")
    result = call_verify_documents_api(party, agr, text, pt)
    _show_verify_result(result)
    set_state("flow_state", "DONE")


def _handle_view_doc(text: str) -> None:
    """FREE-FORM: Match a document by name or number."""
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    result = get_state("generated_docs", {})
    docs   = result.get("documents", [])

    for i, doc in enumerate(docs):
        if str(i + 1) in text:
            _open_document(doc["name"], docs)
            return

    matched = extract_doc_name(text, docs)
    if matched:
        _open_document(matched, docs)
    elif docs:
        _open_document(docs[0]["name"], docs)

# ══════════════════════════════════════════════════════════════════════════════
#  SELECTION HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

def _handle_agreement_type(text: str) -> None:
    """SELECTION: Accept any agreement type string (typed or spoken)."""
    text = text.strip()
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    if not text:
        _say_key("ask_agreement_type")
        return
    set_state("agreement_type", text)
    opts  = ", ".join(PRODUCT_TYPES)
    pills = "  |  ".join(["<b>{0}</b>".format(p) for p in PRODUCT_TYPES])
    _say(
        "Please select the <b>Product Type</b>:<br>{0}".format(pills),
        "Please select the product type. Options are: {0}.".format(opts),
    )
    set_state("flow_state", "ASK_PRODUCT_TYPE")


def _handle_product_type(text: str) -> None:
    """SELECTION: Match EBICS / MT101 / CC from text."""
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    pt = "EBICS"
    for p in PRODUCT_TYPES:
        if p.lower() in text.lower():
            pt = p
            break
    set_state("product_type", pt)
    _say_key("ask_party_name", agreement_type=get_state("agreement_type", ""))
    set_state("flow_state", "ASK_PARTY")


def _handle_verify_type(text: str) -> None:
    """SELECTION: Accept any agreement type for verification."""
    text = text.strip()
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    if not text:
        _say("Please provide the agreement type to verify.",
             "Please provide the agreement type to verify.")
        return
    set_state("verify_agree_type", text)
    opts  = ", ".join(PRODUCT_TYPES)
    pills = "  |  ".join(["<b>{0}</b>".format(p) for p in PRODUCT_TYPES])
    _say(
        "Please select the <b>Product Type</b>:<br>{0}".format(pills),
        "Please select the product type. Options are: {0}.".format(opts),
    )
    set_state("flow_state", "VERIFY_ASK_PRODUCT")


def _handle_verify_product(text: str) -> None:
    """SELECTION: Match product type for verification."""
    if is_cancellation(text):
        _cancelled_to_menu()
        return
    pt = "EBICS"
    for p in PRODUCT_TYPES:
        if p.lower() in text.lower():
            pt = p
            break
    set_state("verify_product_type", pt)
    _say(
        "Please provide the <b>value or duration</b> for this agreement:",
        "Please provide the value or duration.",
    )
    set_state("flow_state", "VERIFY_ASK_VALUE")

# ══════════════════════════════════════════════════════════════════════════════
#  SHOW_HISTORY — intent-based (yes/no/new)
# ══════════════════════════════════════════════════════════════════════════════

def _handle_show_history(text: str) -> None:
    intent = detect_intent(text)

    if intent in ("yes_confirm", "regenerate_old", "generate_history"):
        docs = get_state("user_documents", [])
        if not docs:
            _batch_begin()
            _batch_add(
                "No agreements found. Let me help you create one.",
                "No agreements found. Let me help you create one.",
            )
            _batch_add_key("ask_agreement_type")
            _batch_end()
            set_state("flow_state", "ASK_AGREE_TYPE")
            return
        names_html  = "".join([
            "<br>&nbsp;&nbsp;<b>{0}.</b> {1} — {2} ({3})".format(
                i + 1, d["type"], d["party"], d["date"]
            )
            for i, d in enumerate(docs)
        ])
        names_audio = ". ".join([
            "{0}: {1} with {2}".format(i + 1, d["type"], d["party"])
            for i, d in enumerate(docs)
        ])
        _say(
            "Here are your past agreements:{0}<br><br>"
            "Please click <b>Regenerate</b> on a card, or say the "
            "<b>agreement number</b>.".format(names_html),
            "Here are your past agreements. {0}. "
            "Please say the agreement number you want to regenerate.".format(names_audio),
        )
        set_state("flow_state", "SHOW_HISTORY_CHOICE")
        return

    if intent == "no_cancel":
        _say(
            "Ok! How can I assist you?<br>"
            "1&#65039;&#8419; &nbsp;<b>Generate Agreement from History</b><br>"
            "2&#65039;&#8419; &nbsp;<b>Generate a New Agreement</b><br>"
            "3&#65039;&#8419; &nbsp;<b>Verify Document</b>",
            "Ok! Please choose. "
            "Option 1: Generate Agreement from History. "
            "Option 2: Generate a New Agreement. "
            "Option 3: Verify Document.",
        )
        set_state("flow_state", "AWAIT_MENU")
        return

    if intent in ("new_fresh", "generate_document"):
        _say_key("ask_agreement_type")
        set_state("flow_state", "ASK_AGREE_TYPE")
        return

    _say(
        "Please say <b>Yes</b> to regenerate from history, "
        "<b>Create New</b> for a fresh agreement, or <b>No</b> to go back.",
        "Please say Yes to regenerate, Create New for a fresh agreement, or No to go back.",
    )

# ══════════════════════════════════════════════════════════════════════════════
#  SHOW_HISTORY_CHOICE — user picks which past record to regenerate
# ══════════════════════════════════════════════════════════════════════════════

def _handle_history_choice(text: str) -> None:
    if is_cancellation(text):
        _cancelled_to_menu()
        return

    docs     = get_state("user_documents", [])
    selected = None

    # Match by position number (1, 2, 3…)
    for i, doc in enumerate(docs):
        if str(i + 1) in text:
            selected = doc
            break

    # Match by agreement type or party name (substring)
    if selected is None:
        text_lower = text.lower()
        for doc in docs:
            if (doc.get("type", "").lower() in text_lower or
                    doc.get("party", "").lower() in text_lower or
                    doc.get("id", "").lower() in text_lower):
                selected = doc
                break

    # Single-document shortcut
    if selected is None and len(docs) == 1:
        selected = docs[0]

    if selected is not None:
        set_state("selected_doc", selected)
        _say(
            "You selected: <b>{0}</b> — {1}<br>"
            "Date: {2} | Value: {3} | Product: {4}<br><br>"
            "⚠️ Shall I <b>regenerate this agreement</b>? Say <b>Yes</b> or <b>No</b>.".format(
                selected["type"], selected["party"],
                selected["date"], selected.get("value", "N/A"),
                selected.get("product_type", "EBICS"),
            ),
            "You selected {0} with {1}. "
            "Shall I regenerate this agreement? Say Yes or No.".format(
                selected["type"], selected["party"]
            ),
        )
        set_state("flow_state", "CONFIRM_REGEN")
    else:
        nums = ", ".join([str(i + 1) for i in range(len(docs))])
        _say(
            "I could not match that. Please say a number between 1 and {0}. "
            "(Options: {1})".format(len(docs), nums),
            "Please say a number between 1 and {0}.".format(len(docs)),
        )

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIRM NEW AGREEMENT
# ══════════════════════════════════════════════════════════════════════════════

def _handle_confirm_new(text: str) -> None:
    if is_confirmation(text):
        d  = get_state("new_doc_details", {})
        _say("⚙️ Creating your agreement… please wait.",
             "Creating your agreement. Please wait.")
        resp = call_create_agreement_api(
            d.get("detail1", ""), d.get("detail2", ""),
            d.get("detail3", ""), d.get("product_type", "EBICS"),
        )
        set_state("agreement_data", resp)
        _show_agreement_result(resp)
        user = get_state("current_user", "")
        if user:
            add_to_history(user, {
                "id":             resp.get("agreement_id", ""),
                "type":           d.get("detail2", ""),
                "party":          d.get("detail1", ""),
                "date":           resp.get("generated_on", "")[:10],
                "value":          d.get("detail3", ""),
                "status":         "Active",
                "product_type":   d.get("product_type", "EBICS"),
                "detail1":        d.get("detail1", ""),
                "detail2":        d.get("detail2", ""),
                "detail3":        d.get("detail3", ""),
                "generated_docs": resp.get("possible_documents", []),
            })
        set_state("flow_state", "AGREEMENT_CREATED")
    elif is_cancellation(text):
        _cancelled_to_menu()
    else:
        d = get_state("new_doc_details", {})
        _say_key(
            "confirm_new_agreement",
            detail1=d.get("detail1", ""),
            detail2=d.get("detail2", ""),
            detail3=d.get("detail3", ""),
        )

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIRM REGENERATE
# ══════════════════════════════════════════════════════════════════════════════

def _handle_confirm_regen(text: str) -> None:
    if is_confirmation(text):
        doc = get_state("selected_doc", {})
        _say("⚙️ Regenerating your agreement… please wait.",
             "Regenerating your agreement. Please wait.")
        resp = call_regenerate_agreement_api(doc)
        set_state("agreement_data", resp)
        _show_agreement_result(resp)
        set_state("flow_state", "AGREEMENT_CREATED")
    elif is_cancellation(text):
        _cancelled_to_menu()
    else:
        doc = get_state("selected_doc", {})
        _say(
            "Please confirm: regenerate <b>{0}</b> with <b>{1}</b>? "
            "Say <b>Yes</b> or <b>No</b>.".format(
                doc.get("type", ""), doc.get("party", "")
            ),
            "Please say Yes to regenerate or No to cancel.",
        )

def _show_agreement_result(resp: Dict[str, Any]) -> None:
    docs    = resp.get("possible_documents", [])
    n       = len(docs)
    names   = ", ".join([
        d["name"].replace("_", " ").replace(".pdf", "")
        for d in docs[:2]
    ])
    suffix  = " and {0} more".format(n - 2) if n > 2 else ""
    doc_list = "".join(["&nbsp;&nbsp;• {0}<br>".format(d["name"]) for d in docs])
    _batch_begin()
    _batch_add(
        "✅ <b>Agreement Created!</b><br>"
        "📋 ID: {0} | Product: {1}<br>"
        "📄 <b>{2} document(s)</b> ready:<br>{3}".format(
            resp.get("agreement_id", ""),
            resp.get("product_type", ""),
            n,
            doc_list,
        ),
        "Agreement created successfully. "
        "{0} documents can be generated: {1}{2}.".format(n, names, suffix),
    )
    _batch_add(
        "⚠️ <b>Do you want to generate documents for this Agreement?</b><br>"
        "Say <b>Yes</b> to generate or <b>No</b> to cancel.",
        "Do you want to generate documents for this Agreement? Say Yes or No.",
    )
    _batch_end()

# ══════════════════════════════════════════════════════════════════════════════
#  AGREEMENT_CREATED → confirm doc generation
# ══════════════════════════════════════════════════════════════════════════════

def _handle_agreement_created(text: str) -> None:
    intent = detect_intent(text)
    if intent in ("yes_confirm", "generate_docs") or is_confirmation(text):
        _say("⚙️ Generating all documents… please wait.",
             "Generating all documents now. Please wait.")
        agr    = get_state("agreement_data", {})
        result = call_generate_documents_api(agr)
        set_state("generated_docs", result)
        _show_docs_result(result)
        set_state("flow_state", "DOCS_READY")
    elif is_cancellation(text):
        _cancelled_to_menu()
    else:
        _say(
            "Please say <b>Yes</b> to generate documents or <b>No</b> to cancel.",
            "Please say Yes to generate documents or No to cancel.",
        )
        set_state("flow_state", "CONFIRM_GENERATE_DOCS")

def _handle_confirm_generate_docs(text: str) -> None:
    _handle_agreement_created(text)

def _show_docs_result(result: Dict[str, Any]) -> None:
    docs  = result.get("documents", [])
    items = "".join([
        "<br>&nbsp;&nbsp;<b>{0}.</b> {1} — {2} ({3}p)".format(
            i + 1, d["name"], d["desc"], d["pages"]
        )
        for i, d in enumerate(docs)
    ])
    audio_items = ". ".join([
        "Document {0}: {1}. {2}".format(
            i + 1,
            d["name"].replace("_", " ").replace(".pdf", ""),
            d["desc"],
        )
        for i, d in enumerate(docs)
    ])
    _batch_begin()
    _batch_add(
        "📂 <b>{0} Documents Generated!</b>{1}<br>"
        "<br>Use the buttons below to view or download documents.".format(
            len(docs), items
        ),
        "All {0} documents have been generated. {1}.".format(len(docs), audio_items),
    )
    _batch_add(
        "Do you want to view any of these documents?<br>"
        "Say <b>Yes</b> and the document number, or <b>No</b> to finish.",
        "Do you want to view any of these documents? Say Yes and the number, or No to finish.",
    )
    _batch_end(
        msg_type="doc_list",
        extra={"documents": docs, "zip_url": result.get("zip_url", "")},
    )

# ══════════════════════════════════════════════════════════════════════════════
#  DOCS_READY — user picks one to view
# ══════════════════════════════════════════════════════════════════════════════

def _handle_docs_ready(text: str) -> None:
    intent = detect_intent(text)
    result = get_state("generated_docs", {})
    docs   = result.get("documents", [])

    if intent == "no_cancel":
        _cancelled_to_menu()
        return

    matched = extract_doc_name(text, docs)
    if matched:
        _open_document(matched, docs)
        return

    for i, doc in enumerate(docs):
        if str(i + 1) in text:
            _open_document(doc["name"], docs)
            return

    if intent in ("yes_confirm", "view_doc"):
        names_html  = "".join([
            "<br>&nbsp;&nbsp;<b>{0}.</b> {1}".format(i + 1, d["name"])
            for i, d in enumerate(docs)
        ])
        names_audio = ". ".join([
            "{0}: {1}".format(
                i + 1, d["name"].replace("_", " ").replace(".pdf", "")
            )
            for i, d in enumerate(docs)
        ])
        _say(
            "Which document?{0}<br>Say the number or name.".format(names_html),
            "Which document? {0}. Say the number.".format(names_audio),
        )
        set_state("flow_state", "VIEW_DOC")
    else:
        _say(
            "Say <b>Yes</b> and a document number to view, or <b>No</b> to finish.",
            "Say Yes and a document number to view, or No to finish.",
        )

def _open_document(doc_name: str, docs: List[Dict[str, Any]]) -> None:
    doc = None
    for d in docs:
        if d["name"] == doc_name:
            doc = d
            break
    if doc is None:
        return
    sections_text = ", ".join(doc.get("sections", []))
    _batch_begin()
    _batch_add(
        "📄 <b>Opening: {0}</b><br>"
        "📝 <b>Description:</b> {1}<br>"
        "📑 <b>Sections:</b> {2}<br>"
        "📃 <b>Pages:</b> {3} | 📦 <b>Size:</b> {4} KB<br>"
        "🔖 <b>Header:</b> {5}<br>"
        "🔖 <b>Footer:</b> {6}<br>"
        "The document viewer and download link are shown below.".format(
            doc["name"], doc["desc"], sections_text,
            doc.get("pages", "-"), doc.get("size_kb", "-"),
            doc.get("header", ""),
            doc.get("footer", "").replace("{page}", "1"),
        ),
        "Opening document: {0}. {1} Sections: {2}. {3} pages.".format(
            doc["name"].replace("_", " ").replace(".pdf", ""),
            doc["desc"],
            sections_text,
            doc.get("pages", "-"),
        ),
    )
    _batch_add(
        "🔍 <b>Would you like to verify the generated documents?</b><br>"
        "Say <b>Yes</b> to run verification, or <b>No</b> to finish.",
        "Would you like to verify the generated documents? Say Yes to verify, or No to finish.",
    )
    _batch_end(msg_type="doc_viewer", extra={"doc": doc})
    set_state("flow_state", "ASK_POST_DOCS_VERIFY")

# ══════════════════════════════════════════════════════════════════════════════
#  ASK_POST_DOCS_VERIFY — ask user after view-document stage
# ══════════════════════════════════════════════════════════════════════════════

def _handle_post_docs_verify(text: str) -> None:
    """
    Called after the user has viewed a document.
    Ask if they want to verify the generated documents.
    If Yes → run verification using already-collected session data.
    If No  → return to main menu.
    """
    if is_cancellation(text):
        _cancelled_to_menu()
        return

    intent   = detect_intent(text)
    text_low = text.lower().strip()

    wants_verify = (
        intent in ("yes_confirm", "verify_document")
        or any(kw in text_low for kw in ("yes", "verify", "check", "validate", "sure", "ok", "yeah", "yep"))
    )

    if wants_verify:
        # Pull all details already stored in session — no re-asking needed
        agr_data   = get_state("agreement_data", {})
        gen_docs   = get_state("generated_docs", {})
        new_details = get_state("new_doc_details", {})

        # Resolve counterparty
        party = (
            agr_data.get("counterparty")
            or new_details.get("detail1")
            or get_state("party_name", "")
        )
        # Resolve agreement type
        agr_type = (
            agr_data.get("agreement_type")
            or new_details.get("detail2")
            or get_state("agreement_type", "")
        )
        # Resolve value/duration
        value = (
            agr_data.get("value_duration")
            or new_details.get("detail3")
            or get_state("new_doc_details", {}).get("detail3", "N/A")
        )
        # Resolve product type
        product_type = (
            agr_data.get("product_type")
            or new_details.get("product_type")
            or get_state("product_type", "EBICS")
        )

        result = call_verify_documents_api(party, agr_type, value, product_type)
        _show_verify_result(result)
        set_state("flow_state", "DONE")
        return

    # User said No or something else → finish
    wants_no = (
        intent == "no_cancel"
        or any(kw in text_low for kw in ("no", "skip", "finish", "done", "cancel", "exit"))
    )
    if wants_no:
        _say(
            "No problem! Is there anything else I can help you with?",
            "No problem. Is there anything else I can help you with?",
        )
        _options_msg()
        set_state("flow_state", "AWAIT_MENU")
        return

    # Ambiguous response — re-prompt
    _say(
        "Please say <b>Yes</b> to verify your documents, or <b>No</b> to finish.",
        "Please say Yes to verify your documents, or No to finish.",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  VERIFY RESULT DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def _show_verify_result(result: Dict[str, Any]) -> None:
    steps   = result.get("verification_steps", [])
    doc_res = result.get("document_results", [])

    # ── Rich voice narration for the full verification report ──────────────
    passed  = result.get("passed", 0)
    total   = result.get("total_documents", 0)
    failed  = total - passed
    status  = result.get("status", "").replace("✅", "").replace("⚠️", "").strip()
    message = result.get("message", "")

    # Step narration
    steps_audio = ". ".join(steps) if steps else ""

    # Per-document narration
    doc_audio_parts = []
    for r in doc_res:
        doc_name_clean = r["document"].replace("_", " ").replace(".pdf", "")
        checks = []
        for check_name, check_val in [
            ("header",    r.get("header_check",    "")),
            ("footer",    r.get("footer_check",    "")),
            ("sections",  r.get("sections_check",  "")),
            ("signature", r.get("signature_check", "")),
        ]:
            passed_check = any(p in str(check_val) for p in ("✅", "✔", "PASS", "Pass", "pass", "OK"))
            checks.append("{0} {1}".format(check_name, "passed" if passed_check else "failed"))
        overall_clean = r.get("overall", "").replace("✅", "passed").replace("❌", "failed").replace("⚠️", "has warnings")
        doc_audio_parts.append(
            "Document {0}: {1}. Overall result: {2}.".format(
                doc_name_clean, ", ".join(checks), overall_clean
            )
        )
    docs_audio = " ".join(doc_audio_parts)

    # Final summary narration
    if failed == 0:
        verdict_audio = "All {0} documents passed verification successfully.".format(total)
    elif failed == total:
        verdict_audio = "Warning: all {0} documents failed verification.".format(total)
    else:
        verdict_audio = (
            "{0} out of {1} documents passed verification. "
            "{2} document{3} require attention.".format(
                passed, total, failed, "s" if failed > 1 else ""
            )
        )

    full_audio = (
        "Verification report is ready. "
        "{steps} "
        "{docs} "
        "{verdict} "
        "Final status: {status}. {message}"
    ).format(
        steps=steps_audio,
        docs=docs_audio,
        verdict=verdict_audio,
        status=status,
        message=message,
    ).strip()

    # ── Batch: report table + closing prompt as one bubble + one voice ──────
    _batch_begin()
    # The rich table + PDF download is rendered by _render_verify_result in components.py.
    # The bubble content is a brief text summary only — no duplicate table.
    if failed == 0:
        bubble_html = (
            "&#128269; <b>Verification complete.</b> "
            "All <b>{0}</b> document{1} passed. "
            "Status: <b>{2}</b>".format(
                total, "s" if total != 1 else "", result.get("status", "")
            )
        )
    elif failed == total:
        bubble_html = (
            "&#128269; <b>Verification complete — issues found.</b> "
            "<b>{0}</b> document{1} require attention. "
            "Status: <b>{2}</b>".format(
                failed, "s" if failed != 1 else "", result.get("status", "")
            )
        )
    else:
        bubble_html = (
            "&#128269; <b>Verification complete.</b> "
            "<b>{0}</b> of <b>{1}</b> documents passed. "
            "Status: <b>{2}</b>".format(passed, total, result.get("status", ""))
        )

    _batch_add(bubble_html, full_audio)
    _batch_add(
        "The detailed report with PDF download is shown below. "
        "Is there anything else I can assist you with?",
        "The detailed report is shown below. Is there anything else I can help you with?",
    )
    _batch_end(msg_type="verify_result", extra={"verify_data": result})

# ══════════════════════════════════════════════════════════════════════════════
#  UI BUTTON TRIGGERS
# ══════════════════════════════════════════════════════════════════════════════

def trigger_regenerate(doc: Dict[str, Any]) -> None:
    """Called when user clicks the Regenerate button on a history card."""
    if not acquire_cmd_lock():
        return
    try:
        set_state("selected_doc", doc)
        _say(
            "You selected: <b>{0}</b> — {1}<br>"
            "Date: {2} | Product: {3}<br>"
            "⚠️ Shall I <b>regenerate</b> this? Say <b>Yes</b> or <b>No</b>.".format(
                doc.get("type", "Agreement"), doc.get("party", ""),
                doc.get("date", ""), doc.get("product_type", "EBICS"),
            ),
            "You selected {0} with {1}. Shall I regenerate? Say Yes or No.".format(
                doc.get("type", "Agreement"), doc.get("party", "")
            ),
        )
        set_state("flow_state", "CONFIRM_REGEN")
    finally:
        release_cmd_lock()


def trigger_new_agreement(
    detail1: str,
    detail2: str,
    detail3: str,
    product_type: str = "EBICS",
) -> None:
    if not acquire_cmd_lock():
        return
    try:
        set_state("new_doc_details", {
            "detail1": detail1, "detail2": detail2,
            "detail3": detail3, "product_type": product_type,
        })
        _say_key("confirm_new_agreement",
                 detail1=detail1, detail2=detail2, detail3=detail3)
        set_state("flow_state", "CONFIRM_NEW")
    finally:
        release_cmd_lock()


def trigger_open_document(doc_name: str) -> None:
    if not acquire_cmd_lock():
        return
    try:
        result = get_state("generated_docs", {})
        docs   = result.get("documents", [])
        _open_document(doc_name, docs)
    finally:
        release_cmd_lock()
    st.rerun()


def _cancelled_to_menu() -> None:
    _batch_begin()
    _batch_add_key("cancelled")
    _batch_add(
        "Please choose:<br>"
        "1&#65039;&#8419; &nbsp;<b>Generate Agreement from History</b><br>"
        "2&#65039;&#8419; &nbsp;<b>Generate a New Agreement</b><br>"
        "3&#65039;&#8419; &nbsp;<b>Verify Document</b>",
        "Please choose. "
        "Option 1: Generate Agreement from History. "
        "Option 2: Generate a New Agreement. "
        "Option 3: Verify Document.",
    )
    _batch_end()
    set_state("flow_state", "AWAIT_MENU")
