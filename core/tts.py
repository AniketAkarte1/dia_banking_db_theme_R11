"""
DIA TTS Module — Python 3.9+ + gTTS 2.5.4 compatible.

Compatibility notes:
  - Optional[str] from typing (not str | None — requires Python 3.10+)
  - gTTS 2.5.4 API: gTTS(text, lang, slow) — unchanged from 2.x series
  - tempfile.NamedTemporaryFile with delete=False so Streamlit can read
    the file path after creation on all OS including Windows
  - tmp.close() called explicitly before returning path (Windows compat)
  - No walrus operator, no match/case, no structural pattern matching
  - No unused imports (threading removed)
"""
import os
import re
import tempfile
from typing import Optional

import streamlit as st

# gTTS 2.5.4 language code mapping
LANG_CODES = {
    "English":           "en",
    "हिंदी (Hindi)":    "hi",
    "मराठी (Marathi)":  "mr",
    "Deutsch (German)":  "de",
    "普通话 (Mandarin)": "zh-CN",
}

# HTML entity decode map for TTS cleanup
_HTML_ENTITIES = [
    ("&nbsp;",  " "),
    ("&amp;",   "&"),
    ("&lt;",    "<"),
    ("&gt;",    ">"),
    ("&#39;",   "'"),
    ("&quot;",  '"'),
    ("&#65039;",""),  # variation selector
    ("&#8419;", ""),  # combining enclosing keycap
]


def strip_html(text: str) -> str:
    """Remove HTML tags and decode common entities for clean TTS input."""
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode entities
    for entity, replacement in _HTML_ENTITIES:
        text = text.replace(entity, replacement)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def speak_text(text: str, language: str = "English") -> Optional[str]:
    """
    Convert text to an MP3 temp file using gTTS 2.5.4.
    Returns the absolute file path, or None if disabled / unavailable.

    Python 3.9+ compatible — no X|None unions, no walrus, no match/case.
    """
    if not st.session_state.get("audio_enabled", True):
        return None

    clean = strip_html(text)
    if not clean:
        return None

    lang_code = LANG_CODES.get(language, "en")

    try:
        from gtts import gTTS  # gTTS 2.5.4
        tts = gTTS(text=clean, lang=lang_code, slow=False)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp.name
        tmp.close()           # close before writing (Windows compatibility)
        tts.save(tmp_path)
        return tmp_path
    except ImportError:
        return None
    except Exception:
        return None


def play_audio_in_ui(audio_path: Optional[str]) -> None:
    """Embed an audio player in Streamlit using st.audio (streamlit 1.28.0+)."""
    if not audio_path:
        return
    try:
        with open(audio_path, "rb") as f:
            data = f.read()
        # st.audio signature in streamlit 1.28.0+: st.audio(data, format=...)
        st.audio(data, format="audio/mp3")
    except Exception:
        pass
