"""
DIA Face Authentication UI — Deutsche Bank Royal Blue Theme
Renders the face recognition / enrollment screen before the main chat.

Flow:
  FACE_SCAN       -> camera snapshot -> if recognized  -> FACE_DONE
                                     -> if unknown     -> FACE_ENROLL_NAME
  FACE_ENROLL_NAME -> user types name + picks language
  FACE_ENROLL_CAP  -> capture 12 frames -> enroll + retrain -> FACE_DONE
  FACE_DONE       -> main chat begins

Graceful degradation: if cv2.face (opencv-contrib) is not installed, the screen
shows clear install instructions and a "Skip" button so the app still runs.

Python 3.9+ + streamlit 1.28.0+ compatible.
No walrus, no match/case, no X|None unions.
"""
import time
from typing import List, Optional

import streamlit as st

from core.face_auth_engine import (
    CV2_FACE_AVAILABLE,
    decode_frame,
    detect_face_in_frame,
    recognize_face,
    enroll_face,
    draw_face_overlay,
    frame_to_jpeg_bytes,
    CONFIDENCE_THRESHOLD,
)

# ── How many frames to collect during enrolment ───────────────────────────────
ENROLL_NEEDED = 12

# ── Per-language welcome / new-user messages ──────────────────────────────────
_WELCOME_MSGS = {
    "English":          "Welcome back, {name}! Great to see you again.",
    "हिंदी (Hindi)":    "स्वागत है, {name}! आपसे मिलकर अच्छा लगा।",
    "मराठी (Marathi)":  "स्वागत आहे, {name}! तुम्हाला पुन्हा पाहून आनंद झाला.",
    "Deutsch (German)": "Willkommen zurück, {name}! Schön, Sie wieder zu sehen.",
    "普通话 (Mandarin)": "欢迎回来，{name}！很高兴再次见到您。",
}

_NEW_USER_MSGS = {
    "English":          "I don't recognise you yet. Please tell me your name.",
    "हिंदी (Hindi)":    "मैं आपको नहीं पहचानता। कृपया अपना नाम बताएं।",
    "मराठी (Marathi)":  "मी तुम्हाला ओळखत नाही. कृपया तुमचे नाव सांगा.",
    "Deutsch (German)": "Ich erkenne Sie noch nicht. Bitte nennen Sie Ihren Namen.",
    "普通话 (Mandarin)": "我还不认识您。请告诉我您的名字。",
}

_LANG_OPTS = ["English", "हिंदी (Hindi)", "मराठी (Marathi)", "Deutsch (German)", "普通话 (Mandarin)"]


# ══════════════════════════════════════════════════════════════════════════════
#  UI helpers — Deutsche Bank theme
# ══════════════════════════════════════════════════════════════════════════════

def _hud_box(content: str, color: str = "var(--accent-cyan)") -> None:
    """Render an info box styled for the DB Royal Blue theme."""
    st.markdown(
        '<div style="border:1px solid {c};border-radius:6px;padding:14px 18px;'
        'font-family:DM Mono,monospace;font-size:13px;color:{c};'
        'background:rgba(255,255,255,0.07);letter-spacing:0.5px;margin:8px 0;">'
        "{t}</div>".format(c=color, t=content),
        unsafe_allow_html=True,
    )


def _title_bar(text: str) -> None:
    st.markdown(
        '<div style="font-family:Playfair Display,serif;font-weight:700;font-size:26px;'
        'color:#FFFFFF;letter-spacing:4px;text-align:center;padding:18px 0 6px;">'
        "{}</div>".format(text),
        unsafe_allow_html=True,
    )


def _set_recognized(name: str, language: str) -> None:
    st.session_state["face_auth_done"]   = True
    st.session_state["face_auth_user"]   = name
    st.session_state["current_user"]     = name
    st.session_state["language"]         = language
    st.session_state["face_auth_status"] = "recognized"


def _speak(text: str, language: str) -> None:
    if not st.session_state.get("audio_enabled", True):
        return
    try:
        from core.tts import speak_text
        path = speak_text(text, language)
        if path:
            with open(path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  Main entry point
# ══════════════════════════════════════════════════════════════════════════════

def render_face_auth() -> bool:
    """
    Render the face authentication screen.
    Returns True when authentication is complete (user recognised or enrolled).
    Returns False to keep showing this screen.
    """
    if st.session_state.get("face_auth_done", False):
        return True

    # Initialise state keys
    for key, default in [
        ("face_auth_status",      "idle"),
        ("face_auth_user",        None),
        ("face_enroll_frames",    []),
        ("face_enroll_name",      ""),
        ("face_enroll_language",  "English"),
        ("face_enroll_cap_count", 0),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # DB-themed header bar for auth screen
    st.markdown("""
        <div class="dia-header">
            <div class="dia-logo-wrap">
                <div class="dia-logo-badge">DB</div>
                <div>
                    <div class="dia-logo">D.I.A</div>
                    <div class="dia-subtitle">Identity Verification &nbsp;&middot;&nbsp; Biometric Auth</div>
                </div>
            </div>
            <div class="status-bar">
                <div class="status-pill active"><span class="status-dot"></span>&nbsp;BIOMETRIC ACTIVE</div>
                <div class="status-pill">&#128274;&nbsp;SECURE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    from ui.styles import EXTRA_CSS
    st.markdown(EXTRA_CSS, unsafe_allow_html=True)

    _title_bar("D.I.A — IDENTITY VERIFICATION")

    # ── If cv2.face not available, show install guide + skip ─────────────────
    if not CV2_FACE_AVAILABLE:
        _render_missing_dep()
        return False

    status = st.session_state.get("face_auth_status", "idle")

    if status == "recognized":
        # Face successfully recognised — auth is complete, proceed to main chat
        return True
    elif status in ("idle", "scanning"):
        _render_scan_screen()
    elif status == "new_user":
        _render_new_user_name()
    elif status == "enrolling":
        _render_enrollment_capture()
    elif status == "enroll_done":
        _render_enroll_success()
        return True

    return False


# ──────────────────────────────────────────────────────────────────────────────
#  Screen: dependency missing
# ──────────────────────────────────────────────────────────────────────────────

def _render_missing_dep() -> None:
    st.error(
        "⚠️ **Face recognition module not available** — `cv2.face` is missing.\n\n"
        "This happens when `opencv-python` or `opencv-python-headless` is installed "
        "instead of `opencv-contrib-python`. The contrib build includes the LBPH "
        "face recognizer (`cv2.face`) required by DIA.\n\n"
        "**Fix — run in your terminal:**\n"
        "```\n"
        "pip uninstall opencv-python opencv-python-headless -y\n"
        "pip install opencv-contrib-python\n"
        "```\n"
        "Then restart the Streamlit app."
    )

    st.markdown("---")
    _hud_box(
        "💡 &nbsp;After installing, restart with:<br>"
        "<code style='color:var(--accent-cyan);'>streamlit run app.py</code>",
        color="var(--accent-cyan)",
    )

    lang = st.session_state.get("language", "English")
    lang_choice = st.selectbox("🌐 Language", _LANG_OPTS,
                               index=_LANG_OPTS.index(lang), key="missing_lang")
    st.session_state["language"] = lang_choice

    name_input = st.text_input("👤 Your name (optional — to skip face ID)",
                               key="missing_name_input",
                               placeholder="e.g. Rahul Sharma")

    if st.button("⏭️ Skip Face ID and Enter DIA", use_container_width=True, key="skip_face_missing"):
        name = name_input.strip() or "Guest"
        st.session_state["face_auth_done"]  = True
        st.session_state["face_auth_user"]  = name
        st.session_state["current_user"]    = name
        st.session_state["language"]        = lang_choice
        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
#  Screen: scan / identify
# ──────────────────────────────────────────────────────────────────────────────

def _render_scan_screen() -> None:
    lang = st.session_state.get("language", "English")

    col_info, col_cam = st.columns([1, 1])

    with col_info:
        st.markdown("<br>", unsafe_allow_html=True)
        _hud_box(
            "🔍 &nbsp;FACIAL RECOGNITION PROTOCOL<br><br>"
            "Position your face within the camera frame.<br>"
            "Ensure good lighting and look directly at the camera.<br><br>"
            "📷 &nbsp;Use the camera widget to take a snapshot.",
            color="var(--accent-cyan)",
        )
        _hud_box(
            "🔒 &nbsp;PRIVACY NOTE<br><br>"
            "Face data is stored locally on this device only.<br>"
            "No biometric data is sent externally.",
            color="var(--accent-green)",
        )

        lang_choice = st.selectbox(
            "🌐 Preferred language",
            _LANG_OPTS,
            index=_LANG_OPTS.index(lang),
            key="scan_lang_sel",
        )
        st.session_state["language"] = lang_choice

    with col_cam:
        st.markdown("**📷 Take a photo to identify yourself:**")
        img_file = st.camera_input(
            label="Face scan",
            key="face_scan_cam",
            help="Look straight at the camera in good light.",
        )

        if img_file is not None:
            image_bytes = img_file.read()
            frame = decode_frame(image_bytes)

            if frame is None:
                st.error("⚠️ Could not decode image. Please try again.")
                return

            rect = detect_face_in_frame(frame)

            if rect is None:
                st.warning("⚠️ No face detected. Ensure your face is clearly visible.")
                st.image(image_bytes, caption="No face found", use_container_width=True)
                return

            overlay = draw_face_overlay(frame, rect, "SCANNING...")
            st.image(frame_to_jpeg_bytes(overlay), caption="Face detected — analysing...",
                     use_container_width=True)

            name, detected_lang, confidence = recognize_face(frame)

            if name is not None:
                st.success("✅ Identity confirmed: **{0}**  (score: {1:.1f})".format(
                    name, confidence))

                welcome = _WELCOME_MSGS.get(detected_lang or lang_choice,
                                            _WELCOME_MSGS["English"]).format(name=name)
                st.markdown(
                    '<div style="font-family:DM Sans,sans-serif;font-size:16px;'
                    'font-weight:600;color:#4ECCA3;text-align:center;padding:16px;'
                    'border:1.5px solid rgba(0,135,90,0.4);border-radius:8px;'
                    'background:rgba(78,204,163,0.12);margin:12px 0;">👋 {}</div>'.format(welcome),
                    unsafe_allow_html=True,
                )
                _speak(welcome, detected_lang or lang_choice)
                _set_recognized(name, detected_lang or lang_choice)
                st.balloons()
                time.sleep(0.8)
                st.rerun()

            else:
                st.info("🔍 Face not recognised. You appear to be a new visitor.")
                new_msg = _NEW_USER_MSGS.get(lang_choice, _NEW_USER_MSGS["English"])
                _hud_box("🆕 &nbsp;" + new_msg, color="var(--accent-cyan)")
                st.session_state["face_auth_status"]    = "new_user"
                st.session_state["face_enroll_frames"]  = [frame]
                st.session_state["face_enroll_name"]    = ""
                st.session_state["face_enroll_language"] = lang_choice
                time.sleep(0.5)
                st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
#  Screen: ask new user for name
# ──────────────────────────────────────────────────────────────────────────────

def _render_new_user_name() -> None:
    _hud_box(
        "🆕 &nbsp;NEW VISITOR DETECTED<br><br>"
        "I don't have your face on file yet.<br>"
        "Please enter your name and choose your language.",
        color="var(--accent-cyan)",
    )

    lang = st.session_state.get("face_enroll_language",
                                st.session_state.get("language", "English"))
    lang_choice = st.selectbox(
        "🌐 Your preferred language",
        _LANG_OPTS,
        index=_LANG_OPTS.index(lang),
        key="enroll_lang_sel",
    )
    st.session_state["face_enroll_language"] = lang_choice
    st.session_state["language"] = lang_choice

    name_input = st.text_input(
        "👤 Your full name",
        value=st.session_state.get("face_enroll_name", ""),
        key="enroll_name_input",
        placeholder="e.g. Rahul Sharma",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Continue — Capture My Face", use_container_width=True,
                     key="enroll_name_ok"):
            name = name_input.strip()
            if len(name) < 2:
                st.warning("Please enter your full name (at least 2 characters).")
            else:
                st.session_state["face_enroll_name"]      = name
                st.session_state["face_enroll_language"]  = lang_choice
                st.session_state["face_auth_status"]      = "enrolling"
                st.session_state["face_enroll_cap_count"] = 0
                st.session_state["face_enroll_frames"]    = []
                st.rerun()

    with col2:
        if st.button("⏭️ Skip — Enter Without Face ID", use_container_width=True,
                     key="enroll_skip"):
            name = name_input.strip() or "Guest"
            st.session_state["face_auth_done"]  = True
            st.session_state["face_auth_user"]  = name
            st.session_state["current_user"]    = name
            st.session_state["language"]        = lang_choice
            st.session_state["face_auth_status"] = "done"
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
#  Screen: capture face frames for enrolment
# ──────────────────────────────────────────────────────────────────────────────

def _render_enrollment_capture() -> None:
    name     = st.session_state.get("face_enroll_name", "New User")
    language = st.session_state.get("face_enroll_language",
                                    st.session_state.get("language", "English"))
    frames   = st.session_state.get("face_enroll_frames", [])  # type: List
    captured = len(frames)

    _hud_box(
        "📸 &nbsp;FACE ENROLMENT — {name}<br><br>"
        "Take {need} photos from slightly different angles.<br>"
        "Progress: <b>{done} / {need}</b> captured.<br><br>"
        "Tip: tilt your head slightly between shots.".format(
            name=name, need=ENROLL_NEEDED, done=captured,
        ),
        color="var(--accent-cyan)",
    )

    st.progress(captured / ENROLL_NEEDED)

    col_cam, col_info = st.columns([1, 1])

    with col_cam:
        cam_key = "enroll_cam_{0}".format(captured)
        img_file = st.camera_input(
            label="Frame {0}/{1}".format(captured + 1, ENROLL_NEEDED),
            key=cam_key,
        )

        if img_file is not None and captured < ENROLL_NEEDED:
            image_bytes = img_file.read()
            frame = decode_frame(image_bytes)

            if frame is not None:
                rect = detect_face_in_frame(frame)
                if rect is None:
                    st.warning("⚠️ No face detected in this shot. Please try again.")
                else:
                    overlay = draw_face_overlay(
                        frame, rect,
                        "CAPTURED {0}/{1}".format(captured + 1, ENROLL_NEEDED),
                    )
                    st.image(frame_to_jpeg_bytes(overlay),
                             caption="Frame captured!", use_container_width=True)
                    frames.append(frame)
                    st.session_state["face_enroll_frames"] = frames
                    time.sleep(0.3)
                    st.rerun()
            else:
                st.error("Could not decode image. Try again.")

    with col_info:
        st.markdown("<br>", unsafe_allow_html=True)
        if 0 < captured < ENROLL_NEEDED:
            _hud_box(
                "✅ &nbsp;{0} frame(s) captured.<br>{1} more needed.".format(
                    captured, ENROLL_NEEDED - captured),
                color="var(--accent-green)",
            )

        if captured >= ENROLL_NEEDED:
            st.success("✅ All {0} frames captured!".format(ENROLL_NEEDED))

            if st.button("🔐 Enrol & Save My Face", use_container_width=True,
                         key="enroll_submit"):
                with st.spinner("🧠 Training face recognition model..."):
                    ok, msg = enroll_face(frames, name, language)

                if ok:
                    st.success("✅ " + msg)
                    _set_recognized(name, language)
                    st.session_state["face_auth_status"] = "enroll_done"

                    welcome = _WELCOME_MSGS.get(language,
                                                _WELCOME_MSGS["English"]).format(name=name)
                    _speak(welcome, language)
                    st.rerun()
                else:
                    st.error("❌ " + msg)
                    st.session_state["face_enroll_frames"] = []
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("❌ Cancel", use_container_width=True, key="enroll_cancel"):
            st.session_state["face_auth_status"]      = "idle"
            st.session_state["face_enroll_frames"]    = []
            st.session_state["face_enroll_cap_count"] = 0
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
#  Screen: enrolment success splash
# ──────────────────────────────────────────────────────────────────────────────

def _render_enroll_success() -> None:
    name     = st.session_state.get("face_auth_user", "")
    language = st.session_state.get("language", "English")
    welcome  = _WELCOME_MSGS.get(language, _WELCOME_MSGS["English"]).format(name=name)

    st.markdown(
        '<div style="font-family:Playfair Display,serif;font-size:20px;'
        'font-weight:700;color:#4ECCA3;text-align:center;padding:24px;'
        'border:2px solid rgba(0,135,90,0.4);border-radius:10px;'
        'background:rgba(78,204,163,0.12);margin:20px 0;">'
        "✅ ENROLMENT COMPLETE<br><br>"
        '<span style="font-size:16px;font-family:DM Sans,sans-serif;font-weight:400;">{}</span></div>'.format(welcome),
        unsafe_allow_html=True,
    )
    st.balloons()

    if st.button("🚀 Enter DIA", use_container_width=True, key="enter_main"):
        st.session_state["face_auth_done"] = True
        st.rerun()
