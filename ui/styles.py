"""
DIA UI Styles — Royal Blue Immersive Theme
Deep royal blue background, white chat text, vivid accent colours.
"""

DIA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    /* ── Royal Blue Core ── */
    --db-royal:        #1A3ED4;   /* main royal blue */
    --db-royal-deep:   #0D2A9E;   /* deeper royal */
    --db-royal-mid:    #2451E8;   /* medium royal */
    --db-royal-lt:     #4A76F5;   /* lighter royal */
    --db-ink:          #0A1C6B;   /* near-black navy */
    --db-azure:        #38BEFF;   /* vivid cyan accent */
    --db-ice:          rgba(255,255,255,0.08);
    --db-frost:        rgba(255,255,255,0.05);

    /* ── Page Background — full royal blue ── */
    --bg-page:         #0F1F6E;   /* rich royal blue page */
    --bg-deep:         #091556;   /* deeper layer */
    --bg-card:         rgba(255,255,255,0.07);
    --bg-card-solid:   #1A2F8A;
    --bg-panel:        rgba(255,255,255,0.06);
    --bg-white:        rgba(255,255,255,0.10);
    --bg-sidebar:      #091556;

    /* ── Text ── */
    --text-primary:    #FFFFFF;
    --text-secondary:  rgba(255,255,255,0.75);
    --text-muted:      rgba(255,255,255,0.45);
    --text-on-dark:    #FFFFFF;
    --text-on-dark-dim:rgba(180,205,255,0.8);
    --text-dim:        rgba(255,255,255,0.45);

    /* ── Accents ── */
    --accent-gold:     #FFD166;   /* gold highlight */
    --accent-cyan:     #38BEFF;   /* cyan accent */
    --accent-green:    #4ECCA3;   /* success green */
    --accent-rose:     #FF6B9D;   /* rose accent */
    --accent-violet:   #A78BFA;   /* violet */

    /* ── Status ── */
    --status-success:  #4ECCA3;
    --status-warning:  #FFD166;
    --status-error:    #FF6B9D;

    /* ── Borders ── */
    --border-light:    rgba(255,255,255,0.12);
    --border-medium:   rgba(255,255,255,0.22);
    --border-glow:     rgba(56,190,255,0.35);

    /* ── Shadows ── */
    --shadow-sm:       0 2px 8px rgba(0,0,0,0.25);
    --shadow-md:       0 6px 24px rgba(0,0,0,0.35);
    --shadow-lg:       0 12px 48px rgba(0,0,0,0.45);
    --shadow-card:     0 4px 20px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.08);
    --shadow-royal:    0 4px 24px rgba(26,62,212,0.5);
    --shadow-glow:     0 0 30px rgba(56,190,255,0.25);

    /* DB success alias */
    --db-success:      #4ECCA3;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stToolbar"] { visibility: hidden; }

/* ── Global Background — royal blue ── */
.stApp {
    background: linear-gradient(160deg, #0A1C6B 0%, #0F1F6E 40%, #122484 70%, #0D2A9E 100%) !important;
    background-attachment: fixed !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
    min-height: 100vh;
}

/* Subtle animated mesh over the whole page */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(56,190,255,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(167,139,250,0.07) 0%, transparent 60%),
        repeating-linear-gradient(
            -55deg,
            transparent,
            transparent 60px,
            rgba(255,255,255,0.015) 60px,
            rgba(255,255,255,0.015) 61px
        );
    pointer-events: none;
    z-index: 0;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

/* ═══════════════════════════════════════════════
   HEADER
═══════════════════════════════════════════════ */
.dia-header {
    background: linear-gradient(90deg, #091556 0%, #0F1F6E 50%, #0D2A9E 100%);
    padding: 0 36px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
    border-bottom: 2px solid transparent;
}

.dia-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1A3ED4 0%, #38BEFF 35%, #FFD166 65%, #1A3ED4 100%);
    background-size: 200% 100%;
    animation: shimmerBar 4s linear infinite;
}

@keyframes shimmerBar {
    0%   { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

.dia-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 50% 100% at 0% 50%, rgba(56,190,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.dia-logo-wrap {
    display: flex;
    align-items: center;
    gap: 16px;
    position: relative;
    z-index: 1;
}

.dia-logo-badge {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #1A3ED4, #38BEFF);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 18px;
    color: #FFFFFF;
    box-shadow: 0 4px 16px rgba(56,190,255,0.4), 0 0 0 1px rgba(255,255,255,0.15);
}

.dia-logo {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 21px;
    color: #FFFFFF;
    letter-spacing: 5px;
    text-transform: uppercase;
    text-shadow: 0 0 20px rgba(56,190,255,0.5);
}

.dia-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    color: rgba(180,210,255,0.75);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-top: 2px;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    z-index: 1;
}

.status-bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }

.status-pill {
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    font-weight: 500;
    letter-spacing: 1.5px;
    padding: 4px 12px;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 3px;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    background: rgba(255,255,255,0.06);
}

.status-pill.active {
    color: #4ECCA3;
    border-color: rgba(78,204,163,0.4);
    background: rgba(78,204,163,0.08);
}

.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #4ECCA3;
    box-shadow: 0 0 10px #4ECCA3;
    animation: pulse 2.5s ease-in-out infinite;
    display: inline-block;
    margin-right: 5px;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.8); }
}

/* ═══════════════════════════════════════════════
   CHAT CONTAINER
═══════════════════════════════════════════════ */
.chat-container {
    height: calc(100vh - 200px);
    overflow-y: auto;
    padding: 28px 32px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    scroll-behavior: smooth;
    background: transparent;
}

.chat-container::-webkit-scrollbar { width: 4px; }
.chat-container::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
.chat-container::-webkit-scrollbar-thumb { background: rgba(56,190,255,0.3); border-radius: 4px; }
.chat-container::-webkit-scrollbar-thumb:hover { background: var(--accent-cyan); }

/* ═══════════════════════════════════════════════
   MESSAGE BUBBLES
═══════════════════════════════════════════════ */
.message-wrapper {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    animation: messageIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes messageIn {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

.message-wrapper.user { flex-direction: row-reverse; }

.avatar {
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}

.avatar.dia {
    background: linear-gradient(135deg, #1A3ED4, #38BEFF);
    box-shadow: 0 4px 16px rgba(56,190,255,0.4);
    border: 1px solid rgba(255,255,255,0.2);
}

.avatar.user {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: var(--shadow-sm);
}

/* DIA message — white text on dark glass */
.message-bubble {
    max-width: 72%;
    padding: 14px 20px;
    font-size: 14px;
    line-height: 1.75;
    position: relative;
}

.message-bubble.dia {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.16);
    border-left: 3px solid var(--accent-cyan);
    color: #FFFFFF;
    box-shadow: var(--shadow-card);
    border-radius: 2px 14px 14px 14px;
    backdrop-filter: blur(12px);
}

.message-bubble.dia b, .message-bubble.dia strong {
    color: var(--accent-gold);
}

.message-bubble.user {
    background: linear-gradient(135deg, #1A3ED4, #2451E8);
    border: 1px solid rgba(255,255,255,0.15);
    color: #FFFFFF;
    box-shadow: 0 4px 20px rgba(26,62,212,0.5);
    border-radius: 14px 2px 14px 14px;
}

.msg-body { display: flex; flex-direction: column; }

.message-time {
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    color: rgba(255,255,255,0.35);
    margin-top: 6px;
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════
   DOCUMENT CARDS
═══════════════════════════════════════════════ */
.doc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
    margin-top: 14px;
}

.doc-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    border-top: 3px solid var(--accent-cyan);
    border-radius: 4px 4px 10px 10px;
    padding: 18px;
    cursor: pointer;
    transition: all 0.22s ease;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(10px);
}

.doc-card:hover {
    border-top-color: var(--accent-gold);
    background: rgba(255,255,255,0.13);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,213,102,0.2);
    transform: translateY(-4px);
}

.doc-card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: var(--accent-cyan);
    letter-spacing: 1px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.doc-card-id {
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    color: rgba(255,255,255,0.40);
    letter-spacing: 1.5px;
    margin-bottom: 6px;
    text-transform: uppercase;
}

.doc-card-meta {
    font-family: 'DM Sans', sans-serif;
    font-size: 12.5px;
    color: rgba(255,255,255,0.80);
    line-height: 1.9;
}

.doc-card-status {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 3px;
    font-size: 9.5px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    margin-top: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.status-active  { background: rgba(78,204,163,0.15); color: #4ECCA3; border: 1px solid rgba(78,204,163,0.3); }
.status-expired { background: rgba(255,107,157,0.12); color: #FF6B9D; border: 1px solid rgba(255,107,157,0.3); }
.status-pending { background: rgba(255,209,102,0.12); color: #FFD166; border: 1px solid rgba(255,209,102,0.3); }

/* ═══════════════════════════════════════════════
   INPUT AREA
═══════════════════════════════════════════════ */
.input-zone {
    background: rgba(9,21,86,0.85);
    border-top: 1px solid rgba(255,255,255,0.10);
    padding: 18px 32px;
    position: sticky;
    bottom: 0;
    backdrop-filter: blur(20px);
    box-shadow: 0 -8px 32px rgba(0,0,0,0.3);
    color: #FFFFFF;
}

/* ═══════════════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
═══════════════════════════════════════════════ */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background: rgba(255,255,255,0.96) !important;
    border: 1.5px solid rgba(255,255,255,0.20) !important;
    border-radius: 8px !important;
    color: #111111 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    box-shadow: none !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 3px rgba(56,190,255,0.18) !important;
    background: rgba(255,255,255,0.12) !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: rgba(17,17,17,0.45) !important;
    font-style: italic;
}

/* Streamlit label text */
.stTextInput label, .stSelectbox label, .stTextArea label {
    color: rgba(255,255,255,0.75) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
}

/* ── Buttons — vivid royal blue with white text ── */
.stButton > button {
    background: linear-gradient(135deg, #1A3ED4 0%, #2451E8 100%) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    border-radius: 8px !important;
    padding: 9px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 3px 14px rgba(26,62,212,0.4) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2451E8 0%, #38BEFF 100%) !important;
    border-color: rgba(56,190,255,0.4) !important;
    box-shadow: 0 6px 24px rgba(56,190,255,0.35) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(26,62,212,0.3) !important;
}

/* Radio */
.stRadio > div { gap: 8px; }
.stRadio label {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid rgba(255,255,255,0.16) !important;
    border-radius: 8px !important;
    padding: 7px 18px !important;
    color: rgba(255,255,255,0.85) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}
.stRadio label:hover {
    border-color: var(--accent-cyan) !important;
    background: rgba(56,190,255,0.10) !important;
    color: #FFFFFF !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1.5px solid rgba(255,255,255,0.20) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stSelectbox div[role="combobox"],
.stSelectbox div[data-baseweb="select"] > div,
.stSelectbox [role="combobox"],
.stSelectbox [data-baseweb="select"] * {
    color: #FFFFFF !important;
}

.stSelectbox [role="option"],
.stSelectbox [role="listbox"] *,
.stSelectbox [data-baseweb="menu"] *,
.stSelectbox ul li {
    color: #FFFFFF !important;
}

.stSelectbox [data-baseweb="menu"] {
    background: rgba(9,21,86,0.98) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
}

/* ═══════════════════════════════════════════════
   SIDEBAR — Deep navy
═══════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #091556 0%, #0A1C6B 60%, #0D2A9E 100%) !important;
    border-right: 1px solid rgba(56,190,255,0.2) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.4);
}

section[data-testid="stSidebar"] * {
    color: var(--text-on-dark) !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.18) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(56,190,255,0.18) !important;
    border-color: rgba(56,190,255,0.4) !important;
    box-shadow: 0 0 16px rgba(56,190,255,0.2) !important;
}

/* ═══════════════════════════════════════════════
   API RESPONSE BOX
═══════════════════════════════════════════════ */
.api-response-box {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-left: 3px solid var(--accent-green);
    border-radius: 8px;
    padding: 18px;
    margin: 10px 0;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(10px);
}

.api-response-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 10.5px;
    font-weight: 700;
    color: var(--accent-cyan);
    letter-spacing: 2px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
    padding-bottom: 10px;
    text-transform: uppercase;
}

.api-table { width: 100%; border-collapse: collapse; }
.api-table tr { border-bottom: 1px solid rgba(255,255,255,0.07); }
.api-table tr:last-child { border-bottom: none; }
.api-key {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--accent-cyan);
    padding: 7px 14px 7px 0;
    white-space: nowrap;
    width: 35%;
    vertical-align: top;
    letter-spacing: 0.5px;
}
.api-val {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: rgba(255,255,255,0.90);
    padding: 7px 0;
    word-break: break-word;
}

/* ═══════════════════════════════════════════════
   TYPING INDICATOR
═══════════════════════════════════════════════ */
.typing-indicator {
    display: flex; gap: 5px; align-items: center; padding: 8px 0;
}
.typing-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent-cyan);
    animation: typingBounce 1.2s ease-in-out infinite;
    box-shadow: 0 0 6px rgba(56,190,255,0.6);
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; background: var(--accent-violet); }
.typing-dot:nth-child(3) { animation-delay: 0.4s; background: var(--accent-gold); }

@keyframes typingBounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.3; }
    40%            { transform: translateY(-8px); opacity: 1; }
}

/* ═══════════════════════════════════════════════
   AUDIO BUTTON
═══════════════════════════════════════════════ */
.audio-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 15px;
    background: rgba(56,190,255,0.12);
    border: 1px solid rgba(56,190,255,0.3);
    border-radius: 5px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: var(--accent-cyan);
    cursor: pointer;
    margin-top: 10px;
    transition: all 0.2s ease;
}
.audio-btn:hover {
    background: rgba(56,190,255,0.22);
    box-shadow: 0 0 14px rgba(56,190,255,0.2);
}

/* ═══════════════════════════════════════════════
   DOC VIEWER
═══════════════════════════════════════════════ */
.doc-viewer {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    overflow: hidden;
    margin: 10px 0;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(10px);
}
.doc-viewer-header {
    background: linear-gradient(90deg, #1A3ED4, #2451E8);
    padding: 12px 20px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #FFFFFF;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.doc-viewer-body {
    padding: 18px 20px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: rgba(255,255,255,0.90);
    line-height: 1.75;
}
.doc-viewer-footer {
    background: rgba(0,0,0,0.15);
    padding: 10px 20px;
    font-family: 'DM Mono', monospace;
    font-size: 10.5px;
    color: rgba(255,255,255,0.40);
    border-top: 1px solid rgba(255,255,255,0.08);
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════
   VERIFY BOX
═══════════════════════════════════════════════ */
.verify-box {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-left: 3px solid var(--accent-green);
    border-radius: 8px;
    padding: 18px;
    margin: 10px 0;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(10px);
}
.verify-table th, .verify-table td {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: rgba(255,255,255,0.90);
}
.verify-table th {
    font-weight: 600;
    color: var(--accent-cyan);
    font-size: 11px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* ZIP link */
.zip-link {
    color: var(--accent-cyan);
    text-decoration: none;
    font-family: 'DM Sans', sans-serif;
    font-size: 12.5px;
    font-weight: 500;
    border-bottom: 1px solid rgba(56,190,255,0.3);
    transition: color 0.2s ease;
}
.zip-link:hover { color: var(--accent-gold); border-bottom-color: var(--accent-gold); }

/* ═══════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.10) !important;
    margin: 18px 0 !important;
}

.stAlert {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
::-webkit-scrollbar-thumb { background: rgba(56,190,255,0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-cyan); }

/* Markdown inside messages */
.message-bubble.dia p { margin: 0 0 6px; color: #FFFFFF; }
.message-bubble.dia a { color: var(--accent-cyan); }
</style>
"""

# ── Additional styles ─────────────────────────────────────────────────────────
EXTRA_CSS = """
<style>
/* Welcome splash */
.welcome-splash {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 55vh;
    gap: 16px;
}

.splash-arc {
    font-size: 64px;
    animation: arcPulse 3s ease-in-out infinite;
    filter: drop-shadow(0 4px 24px rgba(56,190,255,0.5));
}
@keyframes arcPulse {
    0%,100% { transform: scale(1);    opacity: 0.6; }
    50%      { transform: scale(1.10); opacity: 1; }
}

.splash-title {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #FFFFFF 0%, #38BEFF 50%, #FFD166 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 6px;
    text-transform: uppercase;
}

.splash-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: rgba(180,210,255,0.75);
    letter-spacing: 4px;
    text-transform: uppercase;
    font-weight: 400;
}

.splash-hint {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: rgba(255,255,255,0.45);
    margin-top: 6px;
    font-style: italic;
}

/* Doc list */
.doc-list-item {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 12px 18px;
    margin: 6px 0;
    box-shadow: var(--shadow-sm);
    font-family: 'DM Sans', sans-serif;
    color: rgba(255,255,255,0.90);
}

/* Confirmation YES button */
.input-zone .stButton > button[data-testid*="YES"] {
    background: linear-gradient(135deg, #4ECCA3, #10B981) !important;
    color: #0A1C6B !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 14px rgba(78,204,163,0.4) !important;
}
</style>
"""

# ── Mic bar CSS ──────────────────────────────────────────────────────────────
MIC_BAR_CSS = """
<style>
.mic-bar-sep {
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 12px 0 10px;
}

.mic-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
}

iframe[title*="audio"] {
    height: 42px !important;
    width: 42px !important;
    border: none !important;
    background: transparent !important;
}

.voice-status {
    font-family: 'DM Mono', monospace;
    font-size: 11.5px;
    font-weight: 500;
    color: var(--accent-cyan);
    letter-spacing: 0.5px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 320px;
    animation: voiceFlash 0.3s ease;
}

@keyframes voiceFlash {
    0%   { opacity: 0; transform: translateX(-4px); }
    100% { opacity: 1; transform: translateX(0); }
}
</style>
"""
