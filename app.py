"""
DIA — AI Legal Agreement Assistant
Main Streamlit entry point.

Compatible with:
  Python   3.9+
  streamlit 1.28.0+

streamlit API notes used here:
  - st.set_page_config()   — unchanged
  - st.markdown()          — unchanged
  render_layout() drives all further rendering.
"""
import streamlit as st
from ui.layout import render_layout

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="D.I.A — Legal Agreement Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
from ui.styles import DIA_CSS
st.markdown(DIA_CSS, unsafe_allow_html=True)

# ── Render layout ─────────────────────────────────────────────────────────────
render_layout()
