import base64
import threading
import time
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np

from app.config import AppConfig


_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Colours for bounding-box annotations (BGR)
_BBOX_COLOUR = (0, 200, 80)   # vivid green — visible on most images
_BBOX_THICKNESS = 2


def decode_image(image_bytes: bytes) -> np.ndarray:
    data = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid image data")
    return image


def encode_png(image: np.ndarray) -> str:
    success, buffer = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Failed to encode image")
    return base64.b64encode(buffer.tobytes()).decode("ascii")


def _detect_faces_worker(
    gray: np.ndarray,
    original: np.ndarray,
    result_holder: List[Tuple[List[List[int]], str]],
) -> None:
    """Run Haar-cascade face detection and produce an annotated colour image.

    Executes in a background thread so that face detection runs in parallel
    with the edge/contour/histogram work in the main thread.  Results are
    written into *result_holder* so the calling thread can retrieve them
    after joining.
    """
    faces = _FACE_CASCADE.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20)
    )

    # Build list of bounding boxes [[x, y, w, h], ...]
    bboxes: List[List[int]] = (
        [[int(x), int(y), int(w), int(h)] for (x, y, w, h) in faces]
        if len(faces) > 0
        else []
    )

    # Draw rectangles on a copy of the original (colour) resized image
    annotated = original.copy()
    for x, y, w, h in bboxes:
        cv2.rectangle(annotated, (x, y), (x + w, y + h), _BBOX_COLOUR, _BBOX_THICKNESS)
        # Small filled label background
        label = f"face"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
        cv2.rectangle(annotated, (x, y - lh - 4), (x + lw + 4, y), _BBOX_COLOUR, cv2.FILLED)
        cv2.putText(
            annotated, label, (x + 2, y - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1, cv2.LINE_AA,
        )

    result_holder.append((bboxes, encode_png(annotated)))


def process_image(image_bytes: bytes, config: AppConfig) -> Dict[str, Any]:
    start = time.perf_counter()

    image = decode_image(image_bytes)
    resized = cv2.resize(image, (config.resize_width, config.resize_height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # ── Launch face detection in a parallel thread ──────────────────────────
    face_result: List[Tuple[List[List[int]], str]] = []
    face_thread = threading.Thread(
        target=_detect_faces_worker,
        args=(gray, resized, face_result),
        daemon=True,
    )
    face_thread.start()

    # ── Main-thread CV work runs concurrently with face detection ───────────
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    histogram, _ = np.histogram(gray, bins=config.histogram_bins, range=(0, 256))

    # ── Wait for face thread to finish, then merge results ──────────────────
    face_thread.join()
    bboxes, annotated_b64 = face_result[0] if face_result else ([], encode_png(resized))

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return {
        "resize_shape": [int(resized.shape[0]), int(resized.shape[1])],
        "gray_mean": float(np.mean(gray)),
        "edges_nonzero": int(np.count_nonzero(edges)),
        "histogram": histogram.astype(int).tolist(),
        "faces": len(bboxes),
        "faces_bboxes": bboxes,
        "images": {
            "gray": encode_png(gray),
            "edges": encode_png(edges),
            "faces_annotated": annotated_b64,
        },
        "duration_ms": float(elapsed_ms),
        "contour_count": int(len(contours)),
    }
