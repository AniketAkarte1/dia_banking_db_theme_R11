"""
DIA STT Module — Python 3.9+ + SpeechRecognition 3.16.0 compatible.

Compatibility notes:
  - Optional[str] from typing (not str | None — requires Python 3.10+)
  - sr.Recognizer() API unchanged in SpeechRecognition 3.16.0
  - sr.AudioData constructor: sample_width must be int (bytes per sample)
    In SpeechRecognition 3.16.0 the signature is:
      AudioData(frame_data, sample_rate, sample_width)
    where sample_width=2 means 16-bit (2 bytes per sample)
  - recognize_google() unchanged in 3.16.0
  - No walrus, no match/case, no pipe unions
  - Supports: English, Hindi, Marathi, German (Deutsch), Mandarin (普通话)
"""
import io
from typing import Optional

# Language codes for Google Speech Recognition
LANG_CODES = {
    "English":           "en-IN",
    "हिंदी (Hindi)":    "hi-IN",
    "मराठी (Marathi)":  "mr-IN",
    "Deutsch (German)":  "de-DE",
    "普通话 (Mandarin)": "zh-CN",
}


def transcribe_audio(audio_bytes: bytes, language: str = "English") -> Optional[str]:
    """
    Transcribe raw audio bytes to text via Google Speech Recognition.

    SpeechRecognition 3.16.0 / Python 3.9+ compatible.
    Returns the recognised string, or None on any failure.

    Two-pass strategy:
      Pass 1 — treat bytes as WAV/AIFF/FLAC file (browser recorder output)
      Pass 2 — treat as raw 16-bit PCM at 16 kHz mono (fallback)
    """
    if not audio_bytes or len(audio_bytes) < 100:
        return None

    lang_code = LANG_CODES.get(language, "en-IN")

    try:
        import speech_recognition as sr
    except ImportError:
        return None

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    audio_data = None

    # Pass 1: file-based read (WAV/AIFF/FLAC)
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
    except Exception:
        audio_data = None

    # Pass 2: raw PCM fallback
    if audio_data is None:
        try:
            # SpeechRecognition 3.16.0: AudioData(frame_data, sample_rate, sample_width)
            # sample_width=2 → 16-bit signed PCM
            audio_data = sr.AudioData(audio_bytes, 16000, 2)
        except Exception:
            return None

    # Recognise
    try:
        text = recognizer.recognize_google(audio_data, language=lang_code)
        if text:
            return text.strip()
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None
    except Exception:
        return None
