import cv2
from matplotlib.pyplot import gray
import numpy as np
from PIL import Image
import os


# Basic sharpness check using variance of Laplacian


def sharpness_score(img_cv):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


# Brightness score (mean of grayscale)


def brightness_score(img_cv):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray)) / 255.0


# Simple face detection using OpenCV's haarcascade (bundled)


cascade = None
try:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception:
    cascade = None




def detect_faces(img_cv):
    if cascade is None:
        return []
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return faces




def score_image(path):
    try:
        img_cv = cv2.imdecode(np.fromfile(os.path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img_cv is None:
            return 0.0, {}
    except Exception:
        # fallback PIL -> cv2
        from PIL import Image
        pil = Image.open(os.path).convert('RGB')
        img_cv = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


    sharp = sharpness_score(img_cv)
    bright = brightness_score(img_cv)
    faces = detect_faces(img_cv)
    face_count = len(faces)


    # Normalize scores (heuristic)
    sharp_norm = min(sharp / 1000.0, 1.0)
    bright_norm = 1.0 if 0.2 < bright < 0.9 else max(0.0, 1 - abs(0.55 - bright))
    face_bonus = min(face_count * 0.2, 0.4)


    # Penalize heavy blur
    blur_penalty = 0.0 if sharp_norm > 0.2 else 0.5


    score = max(0.0, (0.5 * sharp_norm + 0.3 * bright_norm + face_bonus) - blur_penalty)


    metadata = {
    'sharpness': float(sharp),
    'brightness': float(bright),
    'face_count': face_count,
    }
    return score, metadata