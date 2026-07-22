# D.I.A — Document Intelligence Assistant (Deutsche Bank Theme)

> **AI Legal Agreement Assistant** — Multilingual voice-powered chatbot for banking document management, with face authentication.

---

## 🚀 Features

- **🤖 DIA AI Chatbot** — Deutsche Bank Royal Blue theme with professional banking UI
- **🌐 Multilingual** — English, Hindi (हिंदी), Marathi (मराठी), German (Deutsch), Mandarin (普通话)
- **🎙️ Voice I/O** — Speak to DIA, hear responses back (gTTS + SpeechRecognition)
- **🔐 Face Authentication** — OpenCV LBPH face recognition for user identity (requires opencv-contrib-python)
- **📄 Document History** — Fetch past agreements from user database
- **✨ Generate Documents** — Create new agreements with product-type-specific rules (EBICS / MT101 / CC)
- **🔄 Regenerate Agreements** — Redo old documents with one click
- **✅ Verify Documents** — Full document verification with step-by-step audit trail
- **⚙️ Modular Architecture** — Clean, layered codebase easy to extend

---

## 🐍 Python Compatibility

**Requires Python 3.9 or higher** (compatible with 3.9, 3.10, 3.11, 3.12)

All type annotations use `typing` module forms (`Optional`, `Dict`, `List`, etc.) — no Python 3.10+ union syntax (`X | Y`).

---

## 📁 Project Structure

```
dia_banking_db_theme_R7/
├── app.py                    # Streamlit entry point
├── requirements.txt          # Dependencies (Python 3.9+)
├── install_check.py          # Dependency checker / fixer
├── ui/
│   ├── styles.py             # Deutsche Bank CSS theme
│   ├── layout.py             # Main layout renderer
│   ├── components.py         # UI components
│   └── face_auth_ui.py       # Face authentication screen
├── core/
│   ├── session.py            # Session state management
│   ├── conversation.py       # Flow state machine
│   ├── intent.py             # Multilingual intent detection
│   ├── language.py           # Multi-language response strings
│   ├── tts.py                # Text-to-Speech (gTTS)
│   ├── stt.py                # Speech-to-Text (SpeechRecognition)
│   └── face_auth_engine.py   # OpenCV LBPH face recognition engine
├── data/
│   ├── dummy_data.py         # User document database + generation rules
│   └── faces/                # Face recognition data (auto-created)
├── services/
│   ├── document_api.py       # Document generation/verification API
│   └── download_helper.py    # Sample document download helpers
└── sample_document/          # Sample PDFs for download
```

---

## 🛠️ Installation

```bash
# 1. Ensure Python 3.9+ is installed
python --version

# 2. Install face recognition dependency (IMPORTANT: must be contrib build)
pip uninstall opencv-python opencv-python-headless -y
pip install opencv-contrib-python

# 3. Install all other dependencies
pip install -r requirements.txt

# 4. Verify installation
python install_check.py

# 5. Run the app
streamlit run app.py
```

---

## 🔐 Face Authentication

The app opens with a face authentication screen:

- **Known user**: Camera scans face → auto-login with welcome message
- **New user**: Enter name + language → capture 12 face frames → enrol
- **Skip option**: Available if camera/OpenCV is unavailable

> **OpenCV Note**: You must have `opencv-contrib-python` installed (not `opencv-python`).
> The contrib build includes `cv2.face` (LBPH recognizer).
> Run `python install_check.py` to verify.

---

## 💬 How to Use

### Generate Agreements
- Say/type: **"Generate Agreement"** / **"Create Agreement"**
- DIA asks for: Agreement Type → Product Type (EBICS/MT101/CC) → Party Name → Value
- Confirms details → calls API → shows generated documents

### Verify Documents
- Say/type: **"Verify Document"** / **"Verify Agreement"**
- DIA walks through a full verification audit trail

### View History
- Say/type: **"History"** / **"My Documents"**
- Shows all past agreements with regenerate buttons

### Quick Buttons
- Use the **sidebar Quick Actions** or the **panel buttons** below the chat

---

## 🌐 Language Selection

Switch language anytime from the **left sidebar** — DIA responds in chat + voice:
- English · हिंदी (Hindi) · मराठी (Marathi) · Deutsch (German) · 普通话 (Mandarin)

---

## 📦 Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | >=1.28.0 | Web UI framework |
| `opencv-contrib-python` | >=4.8.0 | Face detection + LBPH recognition |
| `gtts` | 2.5.4 | Google Text-to-Speech |
| `SpeechRecognition` | 3.16.0 | Voice-to-text |
| `numpy` | >=1.24.0,<2.0 | Array processing (Python 3.9 compatible) |
| `pandas` | >=2.0.0 | Data handling |
| `reportlab` | >=4.0.0 | PDF generation |
| `openpyxl` | 3.1.5 | Excel rules loading |

---

## 🚀 Deploy to Streamlit Cloud

1. Push project to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Set Python version to 3.9 or higher in settings
4. Connect repo, set **Main file** as `app.py`
5. Note: Face authentication requires camera access in the browser
