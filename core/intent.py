"""
DIA Intent Detection — Python 3.9+ compatible.
Changes:
  - Optional from typing (not X | None)
  - All type hints use typing module forms
  - No walrus operator, no match/case, no structural pattern matching
"""
from typing import Optional, List, Dict, Set

# ── Intent keyword patterns (EN / HI / MR) ────────────────────────────────────
INTENT_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "greet": {
        "en": ["hello", "hi ", "hey", "good morning", "good evening",
               "good afternoon", "greetings", "start", "begin", "namaste"],
        "hi": ["नमस्ते", "हेलो", "हाय", "नमस्कार", "प्रणाम", "सुप्रभात", "शुरू"],
        "mr": ["नमस्कार", "हॅलो", "हाय", "नमस्ते", "सुरू"],
    },
    "generate_history": {
        "en": ["generate agreement from history", "agreement from history",
               "from my history", "from history", "regenerate from history",
               "history agreement", "past agreement"],
        "hi": ["इतिहास से समझौता", "पुराने से बनाओ"],
        "mr": ["इतिहासातून करार"],
    },
    "generate_document": {
        "en": ["generate agreement", "create agreement", "want to generate",
               "make agreement", "i want to generate agreement", "new agreement",
               "generate document", "create document", "draft agreement",
               "legal document", "bank document", "agreement"],
        "hi": ["समझौता बनाना", "करार बनाना", "दस्तावेज़ बनाना है",
               "नया समझौता", "दस्तावेज़ बनाओ"],
        "mr": ["करार तयार करा", "कागदपत्र तयार", "नवीन करार",
               "करार बनवायचे"],
    },
    "verify_document": {
        "en": ["verify", "verify document", "verify agreement", "check document",
               "validate", "authenticate", "document verification"],
        "hi": ["सत्यापन", "सत्यापित", "दस्तावेज़ जांच"],
        "mr": ["सत्यापन", "सत्यापित", "कागदपत्र तपासा"],
    },
    "view_history": {
        "en": ["history", "my documents", "past agreements", "show history",
               "view history", "document history", "my agreements"],
        "hi": ["इतिहास", "मेरे दस्तावेज़", "पिछले समझौते"],
        "mr": ["इतिहास", "माझे कागदपत्र", "मागील करार"],
    },
    "new_fresh": {
        "en": ["create fresh", "create new", "fresh agreement", "new one",
               "brand new", "start fresh", "new document", "fresh document",
               "fresh", "new fresh"],
        "hi": ["नया बनाओ", "ताज़ा बनाओ", "नया करार", "नया दस्तावेज़"],
        "mr": ["नवीन बनवा", "नवीन करार", "नवीन तयार करा"],
    },
    "regenerate_old": {
        "en": ["regenerate", "old agreement", "redo", "recreate",
               "previous agreement", "existing agreement", "use old"],
        "hi": ["पुराना समझौता", "दोबारा बनाओ", "पुनः निर्माण"],
        "mr": ["जुना करार", "पुन्हा तयार करा"],
    },
    "generate_docs": {
        "en": ["generate document", "yes generate", "create document now",
               "generate all documents", "proceed with documents",
               "create documents", "make documents", "generate pdf"],
        "hi": ["दस्तावेज़ बनाओ", "हाँ बनाओ", "सभी दस्तावेज़ बनाओ"],
        "mr": ["दस्तावेज तयार करा", "सर्व कागदपत्र बनवा"],
    },
    "view_doc": {
        "en": ["view", "open", "show me", "display", "see document",
               "view document", "open document", "i want to view"],
        "hi": ["देखो", "खोलो", "दिखाओ", "दस्तावेज़ देखो"],
        "mr": ["पहा", "उघडा", "दाखवा"],
    },
    "yes_confirm": {
        "en": ["yes", "yeah", "confirm", "proceed", "go ahead", "ok", "okay",
               "sure", "absolutely", "correct", "agreed", "approve", "yep"],
        "hi": ["हाँ", "हां", "ठीक है", "बिल्कुल", "सही", "जी हाँ"],
        "mr": ["हो", "होय", "बरोबर", "ठीक आहे", "नक्कीच"],
    },
    "no_cancel": {
        "en": ["no", "nope", "cancel", "stop", "back", "go back",
               "nevermind", "abort", "not now", "exit", "main menu"],
        "hi": ["नहीं", "नही", "रद्द करो", "वापस जाओ", "छोड़ो"],
        "mr": ["नाही", "रद्द करा", "परत जा", "सोडा"],
    },
}

_PRIORITY: List[str] = [
    "greet", "yes_confirm", "no_cancel", "generate_docs",
    "verify_document", "view_history", "generate_history",
    "regenerate_old", "new_fresh", "generate_document", "view_doc",
]

# ── Strict cancel word sets (used by is_cancellation) ─────────────────────────
_CANCEL_WORDS_EN: Set[str] = {
    "no", "nope", "cancel", "stop", "back", "go back",
    "nevermind", "abort", "not now", "exit", "main menu",
}
_CANCEL_WORDS_HI: Set[str] = {"नहीं", "नही", "रद्द करो", "वापस जाओ", "छोड़ो"}
_CANCEL_WORDS_MR: Set[str] = {"नाही", "रद्द करा", "परत जा", "सोडा"}
_ALL_CANCEL: Set[str] = _CANCEL_WORDS_EN | _CANCEL_WORDS_HI | _CANCEL_WORDS_MR

_CONFIRM_WORDS: Set[str] = {
    "yes", "yeah", "confirm", "proceed", "go ahead", "ok", "okay",
    "sure", "absolutely", "correct", "agreed", "approve", "yep",
    "हाँ", "हां", "ठीक है", "बिल्कुल", "सही", "जी हाँ",
    "हो", "होय", "बरोबर", "ठीक आहे", "नक्कीच",
}
_CONFIRM_STARTS: Set[str] = {"yes", "yeah", "yep", "हाँ", "हो", "होय"}


def detect_intent(text: str) -> str:
    """
    Detect intent from text via keyword matching.
    Returns one of the intent keys or 'unknown'.
    Compatible with Python 3.9+ — no walrus, no match/case.
    """
    if not text:
        return "unknown"
    text_lower = text.lower().strip()
    for intent in _PRIORITY:
        lang_dict = INTENT_PATTERNS.get(intent, {})
        for lang_patterns in lang_dict.values():
            for pattern in lang_patterns:
                if pattern in text_lower:
                    return intent
    return "unknown"


def is_cancellation(text: str) -> bool:
    """
    Strict whole-input cancel check.
    Only the ENTIRE trimmed input being a cancel keyword triggers True.
    Prevents company names containing 'no' (e.g. 'Non-Disclosure') from
    falsely cancelling free-form data-entry states.
    """
    trimmed = text.lower().strip()
    if trimmed in _ALL_CANCEL:
        return True
    # Allow short cancel phrases (≤4 words) that match exactly
    words = trimmed.split()
    if len(words) <= 4:
        for cancel_word in _ALL_CANCEL:
            if trimmed == cancel_word:
                return True
    return False


def is_confirmation(text: str) -> bool:
    """
    Whole-input confirmation check.
    Also allows 'yes please', 'yes generate', etc. (starts-with matching).
    """
    trimmed = text.lower().strip()
    if trimmed in _CONFIRM_WORDS:
        return True
    # Allow 'yes ...' style confirmations
    words = trimmed.split()
    if words and words[0] in _CONFIRM_STARTS:
        return True
    return False


def extract_doc_name(text: str, doc_list: List[Dict[str, str]]) -> Optional[str]:
    """
    Try to match a document name from user's free-form text.
    Returns the matched filename or None.
    Compatible with Python 3.9+.
    """
    text_lower = text.lower()
    for doc in doc_list:
        name = doc.get("name", "")
        if name.lower() in text_lower:
            return name
        # Match by ≥2 significant word fragments
        parts = name.replace("_", " ").replace(".pdf", "").lower().split()
        match_count = sum(1 for p in parts if p in text_lower)
        if match_count >= 2:
            return name
    return None
