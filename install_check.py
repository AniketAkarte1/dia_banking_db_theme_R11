"""
DIA dependency checker — run this before starting the app.

Usage:
    python install_check.py

It will diagnose your OpenCV installation and fix it automatically
if you pass --fix:
    python install_check.py --fix
"""
import sys
import subprocess


def check_cv2():
    try:
        import cv2
        print("[OK] cv2 version:", cv2.__version__)
    except ImportError:
        print("[FAIL] cv2 not found. Install with:")
        print("       pip install opencv-contrib-python")
        return False

    # Check cv2.face (only in contrib build)
    try:
        r = cv2.face.LBPHFaceRecognizer_create()
        print("[OK] cv2.face.LBPHFaceRecognizer available")
        return True
    except AttributeError:
        print("[FAIL] cv2.face not available.")
        print("       You have opencv-python or opencv-python-headless installed,")
        print("       which does NOT include the face recognition module.")
        print()
        print("       Fix:")
        print("         pip uninstall opencv-python opencv-python-headless -y")
        print("         pip install opencv-contrib-python")
        return False


def check_streamlit():
    try:
        import streamlit
        print("[OK] streamlit version:", streamlit.__version__)
        return True
    except ImportError:
        print("[FAIL] streamlit not found. Run: pip install streamlit==1.56.0")
        return False


def check_gtts():
    try:
        import gtts
        print("[OK] gTTS available")
        return True
    except ImportError:
        print("[WARN] gTTS not found. Voice output will be disabled.")
        return False


def fix_opencv():
    print("\nAttempting to fix OpenCV installation...")
    subprocess.call([sys.executable, "-m", "pip", "uninstall",
                     "opencv-python", "opencv-python-headless", "-y"])
    result = subprocess.call([sys.executable, "-m", "pip", "install",
                              "opencv-contrib-python"])
    if result == 0:
        print("[OK] opencv-contrib-python installed. Please restart the app.")
    else:
        print("[FAIL] Installation failed. Try manually:")
        print("       pip install opencv-contrib-python")


if __name__ == "__main__":
    print("=" * 55)
    print(" DIA Dependency Checker")
    print("=" * 55)

    cv2_ok = check_cv2()
    st_ok  = check_streamlit()
    check_gtts()

    print()
    if cv2_ok and st_ok:
        print("All critical dependencies OK. Run with:")
        print("  streamlit run app.py")
    else:
        print("Some dependencies are missing.")
        if "--fix" in sys.argv and not cv2_ok:
            fix_opencv()
        else:
            print("Re-run with --fix to auto-install:")
            print("  python install_check.py --fix")
