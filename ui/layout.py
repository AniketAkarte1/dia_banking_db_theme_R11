"""DIA Layout — Deutsche Bank Royal Blue Theme. Face auth gate, then triggers greeting once."""
import streamlit as st
from core.session import init_session
from ui.components import render_header, render_chat_history, render_input_panel, render_sidebar


def render_layout():
    init_session()

    # Inject extra CSS
    from ui.styles import EXTRA_CSS, MIC_BAR_CSS
    st.markdown(EXTRA_CSS, unsafe_allow_html=True)
    st.markdown(MIC_BAR_CSS, unsafe_allow_html=True)

    # ── FACE AUTH GATE ───────────────────────────────────────────────────────
    if not st.session_state.get("face_auth_done", False):
        from ui.face_auth_ui import render_face_auth
        auth_complete = render_face_auth()
        if not auth_complete:
            return  # stay on face auth screen
        # Auth just completed — fall through to main chat

    # ── MAIN CHAT LAYOUT ─────────────────────────────────────────────────────
    render_sidebar()
    render_header()

    # Auto-greet once — the face-auth name is already in current_user
    if not st.session_state.get("greeted", False) and not st.session_state.get("messages"):
        from core.conversation import trigger_greeting
        trigger_greeting()

    render_chat_history()
    render_input_panel()
