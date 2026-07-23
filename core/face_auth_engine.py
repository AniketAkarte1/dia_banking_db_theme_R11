"""
DIA Face Authentication Engine
Uses OpenCV Haar Cascade (detection) + LBPH (recognition).

DEPENDENCY: opencv-contrib-python  (NOT opencv-python or opencv-python-headless)
  Install:  pip uninstall opencv-python opencv-python-headless -y
            pip install opencv-contrib-python

Storage layout  (under data/faces/):
  faces_db.json          -- { label_int: { "name": str, "lang": str } }
  trainer/trainer.yml    -- trained LBPH model
  samples/<label>/N.png  -- grayscale sample images

Python 3.9+ compatible -- no walrus, no match/case, no X|None unions.
"""
import json
import os
from typing import Dict, List, Optional, Tuple

import numpy as np

# ── Safe OpenCV import with friendly error ─────────────────────────────────────
try:
    import cv2
except ImportError:
    raise ImportError(
        "OpenCV is not installed. Run:  pip install opencv-contrib-python"
    )

# ── Check cv2.face (only in contrib build) ────────────────────────────────────
def _check_cv2_face() -> bool:
    """Return True if cv2.face.LBPHFaceRecognizer is available."""
    try:
        _ = cv2.face.LBPHFaceRecognizer_create()
        return True
    except (AttributeError, cv2.error):
        return False

CV2_FACE_AVAILABLE = _check_cv2_face()

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE    = os.path.join(os.path.dirname(__file__), "..", "data", "faces")
_DB_PATH = os.path.join(_BASE, "faces_db.json")
_MODEL   = os.path.join(_BASE, "trainer", "trainer.yml")
_SAMPLES = os.path.join(_BASE, "samples")

# ── Cascade ────────────────────────────────────────────────────────────────────
def _load_cascade() -> cv2.CascadeClassifier:
    """Load Haar cascade, trying cv2.data and project-local fallback paths."""
    import sys

    tried = []
    # primary path from cv2
    try:
        primary = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        tried.append(primary)
        cascade = cv2.CascadeClassifier(primary)
        if not cascade.empty():
            print(f"Loaded cascade from: {primary}", file=sys.stderr)
            return cascade
    except Exception:
        pass

    # project-local cascades directory (bundled fallback)
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cascades", "haarcascade_frontalface_default.xml"))
    tried.append(project_path)
    if os.path.exists(project_path):
        cascade = cv2.CascadeClassifier(project_path)
        if not cascade.empty():
            print(f"Loaded cascade from project data: {project_path}", file=sys.stderr)
            return cascade

    # common macOS/homebrew locations
    alt_paths = [
        "/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
        "/opt/homebrew/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
        "/usr/local/Cellar/opencv/4.8.1/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
    ]
    for p in alt_paths:
        tried.append(p)
        if os.path.exists(p):
            cascade = cv2.CascadeClassifier(p)
            if not cascade.empty():
                print(f"Loaded cascade from: {p}", file=sys.stderr)
                return cascade

    # If we reach here, none loaded
    print("ERROR: Could not find haarcascade_frontalface_default.xml; face detection disabled", file=sys.stderr)
    print("Tried paths:", file=sys.stderr)
    for p in tried:
        print(f"  - {p}", file=sys.stderr)
    # return an (empty) CascadeClassifier to keep API consistent
    return cv2.CascadeClassifier()


_cascade = _load_cascade()

# Confidence threshold: lower = stricter. LBPH distance < threshold = match.
CONFIDENCE_THRESHOLD = 70.0
MIN_SAMPLES = 8


# ══════════════════════════════════════════════════════════════════════════════
#  Internal helpers
# ══════════════════════════════════════════════════════════════════════════════

def _ensure_dirs() -> None:
    os.makedirs(os.path.join(_BASE, "trainer"), exist_ok=True)
    os.makedirs(_SAMPLES, exist_ok=True)


def _load_db() -> Dict[int, Dict]:
    if not os.path.exists(_DB_PATH):
        return {}
    try:
        with open(_DB_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {int(k): v for k, v in raw.items()}
    except Exception:
        return {}


def _save_db(db: Dict[int, Dict]) -> None:
    _ensure_dirs()
    with open(_DB_PATH, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in db.items()}, f, ensure_ascii=False, indent=2)


def _next_label(db: Dict[int, Dict]) -> int:
    return max(db.keys(), default=-1) + 1


def _to_gray(frame: np.ndarray) -> np.ndarray:
    if len(frame.shape) == 3:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame


def _detect_face(gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Return the largest face rect (x, y, w, h) or None."""
    # If cascade failed to load, bail out
    try:
        if getattr(_cascade, 'empty', lambda: True)() :
            return None
    except Exception:
        return None

    # basic validation of image
    if gray is None:
        return None
    if not isinstance(gray, np.ndarray):
        return None
    if gray.size == 0:
        return None
    # convert color to gray if needed
    if len(gray.shape) == 3:
        try:
            gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        except Exception:
            return None

    # ensure uint8 contiguous
    if gray.dtype != np.uint8:
        try:
            gray = np.uint8(gray)
        except Exception:
            return None
    if not gray.flags['C_CONTIGUOUS']:
        gray = np.ascontiguousarray(gray)

    faces = _cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80),
    )
    if len(faces) == 0:
        return None
    best = max(faces, key=lambda r: r[2] * r[3])
    x, y, w, h = int(best[0]), int(best[1]), int(best[2]), int(best[3])
    return (x, y, w, h)


def _crop_face(gray: np.ndarray, rect: Tuple) -> np.ndarray:
    x, y, w, h = rect
    face = gray[y:y + h, x:x + w]
    return cv2.resize(face, (200, 200))


def _load_model():
    """Load saved LBPH model, or return None if not available."""
    if not CV2_FACE_AVAILABLE:
        return None
    if not os.path.exists(_MODEL):
        return None
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(_MODEL)
        return recognizer
    except Exception:
        return None


def _retrain() -> None:
    """Re-build the LBPH model from all saved sample images."""
    if not CV2_FACE_AVAILABLE:
        return
    _ensure_dirs()
    db = _load_db()
    faces_list = []   # type: List[np.ndarray]
    labels_list = []  # type: List[int]

    for label, info in db.items():
        sample_dir = os.path.join(_SAMPLES, str(label))
        if not os.path.isdir(sample_dir):
            continue
        for fname in sorted(os.listdir(sample_dir)):
            if not fname.lower().endswith(".png"):
                continue
            path = os.path.join(sample_dir, fname)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces_list.append(img)
                labels_list.append(label)

    if len(faces_list) < 2:
        return  # need at least 2 samples to train

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces_list, np.array(labels_list, dtype=np.int32))
    recognizer.save(_MODEL)


# ══════════════════════════════════════════════════════════════════════════════
#  Public API
# ══════════════════════════════════════════════════════════════════════════════

def is_face_recognition_available() -> bool:
    """Return True if full face recognition (cv2.face) is usable."""
    return CV2_FACE_AVAILABLE


def decode_frame(image_bytes: bytes) -> Optional[np.ndarray]:
    """Decode JPEG/PNG bytes (from st.camera_input) into an OpenCV BGR array."""
    try:
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def detect_face_in_frame(frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Return face rect if one face is detected, else None."""
    gray = _to_gray(frame)
    return _detect_face(gray)


def recognize_face(frame: np.ndarray) -> Tuple[Optional[str], Optional[str], float]:
    """
    Attempt to recognize a face in frame.

    Returns (name, language, confidence) where:
      - name is None if no face detected, no model trained, or confidence too low
      - confidence is the LBPH distance (lower = better match)
    """
    if not CV2_FACE_AVAILABLE:
        return None, None, 999.0

    gray = _to_gray(frame)
    rect = _detect_face(gray)
    if rect is None:
        return None, None, 999.0

    face_crop  = _crop_face(gray, rect)
    recognizer = _load_model()
    if recognizer is None:
        return None, None, 999.0

    db = _load_db()
    if not db:
        return None, None, 999.0

    try:
        label, confidence = recognizer.predict(face_crop)
    except Exception:
        return None, None, 999.0

    if confidence < CONFIDENCE_THRESHOLD and label in db:
        info = db[label]
        return info.get("name", "Unknown"), info.get("language", "English"), float(confidence)

    return None, None, float(confidence)


def enroll_face(
    frames: List[np.ndarray],
    name: str,
    language: str = "English",
) -> Tuple[bool, str]:
    """
    Enroll a new person from a list of frames.
    Returns (success, message).
    """
    if not CV2_FACE_AVAILABLE:
        return False, (
            "cv2.face module not available. "
            "Please install opencv-contrib-python:\n"
            "  pip uninstall opencv-python opencv-python-headless -y\n"
            "  pip install opencv-contrib-python"
        )

    _ensure_dirs()
    db    = _load_db()
    label = _next_label(db)
    saved = 0

    sample_dir = os.path.join(_SAMPLES, str(label))
    os.makedirs(sample_dir, exist_ok=True)

    for i, frame in enumerate(frames):
        gray = _to_gray(frame)
        rect = _detect_face(gray)
        if rect is None:
            continue
        face_crop = _crop_face(gray, rect)
        path = os.path.join(sample_dir, "{0}.png".format(i))
        cv2.imwrite(path, face_crop)
        saved += 1

    if saved < 3:
        import shutil
        shutil.rmtree(sample_dir, ignore_errors=True)
        return False, (
            "Only {0} clear face image(s) captured. "
            "Need at least 3. Try better lighting.".format(saved)
        )

    db[label] = {"name": name.strip(), "language": language}
    _save_db(db)
    _retrain()
    return True, "Enrolled successfully with {0} face samples.".format(saved)


def add_samples_to_existing(label: int, frames: List[np.ndarray]) -> int:
    """Add more sample images for an existing label and retrain. Returns count added."""
    if not CV2_FACE_AVAILABLE:
        return 0
    _ensure_dirs()
    sample_dir = os.path.join(_SAMPLES, str(label))
    os.makedirs(sample_dir, exist_ok=True)
    existing = len([f for f in os.listdir(sample_dir) if f.endswith(".png")])
    added = 0
    for i, frame in enumerate(frames):
        gray = _to_gray(frame)
        rect = _detect_face(gray)
        if rect is None:
            continue
        face_crop = _crop_face(gray, rect)
        path = os.path.join(sample_dir, "{0}.png".format(existing + i))
        cv2.imwrite(path, face_crop)
        added += 1
    if added > 0:
        _retrain()
    return added


def list_enrolled_users() -> List[Dict]:
    """Return list of enrolled user dicts with label, name, language, sample_count."""
    db = _load_db()
    result = []
    for label, info in db.items():
        sample_dir = os.path.join(_SAMPLES, str(label))
        count = 0
        if os.path.isdir(sample_dir):
            count = len([f for f in os.listdir(sample_dir) if f.endswith(".png")])
        result.append({
            "label":        label,
            "name":         info.get("name", ""),
            "language":     info.get("language", "English"),
            "sample_count": count,
        })
    return result


def get_label_for_name(name: str) -> Optional[int]:
    """Return the label integer for a given name, or None."""
    db = _load_db()
    name_lower = name.strip().lower()
    for label, info in db.items():
        if info.get("name", "").lower() == name_lower:
            return label
    return None


def draw_face_overlay(frame: np.ndarray, rect: Optional[Tuple], label: str = "") -> np.ndarray:
    """Draw a HUD-style rectangle + label on the frame."""
    out = frame.copy()
    if rect is not None:
        x, y, w, h = rect
        color = (0, 212, 255)  # DIA cyan (BGR)
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
        tick = 15
        # Corner ticks
        cv2.line(out, (x,         y),         (x + tick, y),         color, 3)
        cv2.line(out, (x,         y),         (x,         y + tick), color, 3)
        cv2.line(out, (x + w,     y),         (x + w - tick, y),     color, 3)
        cv2.line(out, (x + w,     y),         (x + w,     y + tick), color, 3)
        cv2.line(out, (x,         y + h),     (x + tick,   y + h),   color, 3)
        cv2.line(out, (x,         y + h),     (x,         y + h - tick), color, 3)
        cv2.line(out, (x + w,     y + h),     (x + w - tick, y + h), color, 3)
        cv2.line(out, (x + w,     y + h),     (x + w,     y + h - tick), color, 3)
        if label:
            cv2.putText(
                out, label, (x, max(y - 10, 15)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2,
            )
    return out


def frame_to_jpeg_bytes(frame: np.ndarray) -> bytes:
    """Encode an OpenCV frame to JPEG bytes for st.image display."""
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        return b""
    return buf.tobytes()
