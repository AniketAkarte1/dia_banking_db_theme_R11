"""
DIA Session State Management — Python 3.9+ compatible.
Library versions: streamlit>=1.28.0

Compatibility notes:
  - All type hints use typing module (Optional, Dict, Any, List)
  - No X | None union syntax (requires Python 3.10+)
  - hashlib.md5 called WITHOUT usedforsecurity kwarg for maximum
    compatibility across all Python 3.9+ builds including FIPS-mode
  - No walrus operator, no match/case, no structural pattern matching
"""
import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


def init_session() -> None:
    """Initialise all session state keys with defaults (idempotent)."""
    defaults = {
        "session_id":       str(uuid.uuid4()),
        "messages":         [],
        "flow_state":       "IDLE",
        "language":         "English",
        "audio_enabled":    True,
        "current_user":     None,
        "user_documents":   [],
        "selected_doc":     None,
        "new_doc_details":  {},
        "last_input":       "",
        "greeted":          False,
        "pending_intent":   None,
        "agreement_data":   None,
        "generated_docs":   None,
        "product_type":     "EBICS",
        "agreement_type":   "",
        "party_name":       "",
        # Anti-chaining guards
        "last_audio_hash":  None,
        "cmd_lock":         False,
        "last_voice_text":  "",
        # ── Face authentication ──────────────────────────────────────────────
        "face_auth_done":        False,
        "face_auth_user":        None,
        "face_auth_status":      "idle",
        "face_enroll_frames":    [],
        "face_enroll_name":      "",
        "face_enroll_language":  "English",
        "face_enroll_cap_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session() -> None:
    """Clear all session state and reinitialise."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()


def add_message(
    role: str,
    content: str,
    msg_type: str = "text",
    extra: Optional[Dict[str, Any]] = None,
    audio_path: Optional[str] = None,
) -> None:
    """Append a message dict to the session messages list."""
    msg = {
        "role":      role,
        "content":   content,
        "type":      msg_type,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "extra":     extra if extra is not None else {},
    }
    if audio_path:
        msg["audio_path"] = audio_path
    st.session_state["messages"].append(msg)


def get_state(key: str, default: Any = None) -> Any:
    """Read a value from session state."""
    return st.session_state.get(key, default)


def set_state(key: str, value: Any) -> None:
    """Write a value to session state."""
    st.session_state[key] = value


def audio_already_processed(audio_bytes: bytes) -> bool:
    """
    Return True if these exact audio bytes were already handled this session.
    Uses MD5 fingerprint stored in session state to prevent re-processing
    the same recording on Streamlit rerenders.

    NOTE: hashlib.md5() is called without 'usedforsecurity' keyword argument
    for compatibility with all Python 3.9+ builds (including FIPS-mode
    variants where the keyword may behave differently).
    """
    try:
        h = hashlib.md5(audio_bytes).hexdigest()
    except TypeError:
        # Older builds that don't accept bytes directly — extremely rare
        h = hashlib.md5(bytes(audio_bytes)).hexdigest()

    if st.session_state.get("last_audio_hash") == h:
        return True
    st.session_state["last_audio_hash"] = h
    return False


def acquire_cmd_lock() -> bool:
    """
    Acquire the command execution lock.
    Returns True if the lock was free and is now held.
    Returns False if another command is already executing.
    """
    if st.session_state.get("cmd_lock", False):
        return False
    st.session_state["cmd_lock"] = True
    return True


def release_cmd_lock() -> None:
    """Release the command execution lock unconditionally."""
    st.session_state["cmd_lock"] = False
