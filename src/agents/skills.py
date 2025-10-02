from __future__ import annotations

import os
import uuid
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from pydantic import BaseModel
import yaml


class Result(BaseModel):
    status: str = "ok"
    width: int = 0
    height: int = 0
    tags: dict = {}
    qa: dict = {}
    output_url: Optional[str] = None


# Default QA thresholds; values may be overridden via configs/thresholds.yaml or env var
DEFAULT_THRESHOLDS = {
    "qa": {
        "min_pixels": 512 * 512,
        "blur_threshold": 80.0,
        "min_brightness": 35.0,
        "max_brightness": 230.0,
    }
}


@lru_cache(maxsize=1)
def _load_thresholds() -> dict:
    """Load QA thresholds from YAML if present, falling back to sensible defaults."""
    cfg_path = os.environ.get("THRESHOLDS_CONFIG", str(Path("configs/thresholds.yaml")))
    path = Path(cfg_path)
    if path.exists():
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            loaded = {}
    else:
        loaded = {}

    merged = deepcopy(DEFAULT_THRESHOLDS)
    qa_cfg = loaded.get("qa", {}) if isinstance(loaded, dict) else {}
    merged["qa"].update({k: v for k, v in qa_cfg.items() if isinstance(v, (int, float))})
    return merged


def _ensure_numpy(img: Image.Image) -> np.ndarray:
    if img.mode != "RGB":
        img = img.convert("RGB")
    return np.array(img)


def _to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def segment_foreground(img: Image.Image) -> Image.Image:
    """Naive background cleanup via Otsu thresholding and mask compositing."""
    np_img = _ensure_numpy(img)
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Treat the smaller region as foreground; invert if Otsu picks background instead
    if np.count_nonzero(mask) > mask.size / 2:
        mask = cv2.bitwise_not(mask)

    mask = cv2.medianBlur(mask, 5)
    fg = cv2.bitwise_and(np_img, np_img, mask=mask)
    white_bg = np.full_like(np_img, 255)
    inv_mask = cv2.bitwise_not(mask)
    composed = cv2.add(fg, cv2.bitwise_and(white_bg, white_bg, mask=inv_mask))
    return _to_pil(composed)


def quality_check(img: Image.Image) -> dict:
    thresholds = _load_thresholds().get("qa", {})
    np_img = _ensure_numpy(img)
    height, width = np_img.shape[:2]
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    area_ok = width * height >= thresholds.get("min_pixels", 1)
    blur_ok = blur_score >= thresholds.get("blur_threshold", 0.0)
    brightness_ok = thresholds.get("min_brightness", 0.0) <= brightness <= thresholds.get("max_brightness", 255.0)

    return {
        "min_size_ok": area_ok,
        "blur_score": blur_score,
        "blur_ok": blur_ok,
        "brightness": brightness,
        "brightness_ok": brightness_ok,
        "width": width,
        "height": height,
        "aspect_ratio": round(width / max(height, 1), 3),
    }


_COLOR_NAMES = {
    "red": np.array([200, 40, 40]),
    "orange": np.array([230, 120, 40]),
    "yellow": np.array([240, 210, 70]),
    "green": np.array([70, 180, 90]),
    "cyan": np.array([80, 200, 200]),
    "blue": np.array([60, 90, 200]),
    "purple": np.array([160, 90, 200]),
    "pink": np.array([220, 120, 200]),
    "brown": np.array([150, 110, 70]),
    "gray": np.array([180, 180, 180]),
    "black": np.array([40, 40, 40]),
    "white": np.array([245, 245, 245]),
}


def _closest_color(rgb: np.ndarray) -> str:
    distances = {name: np.linalg.norm(rgb - ref) for name, ref in _COLOR_NAMES.items()}
    return min(distances, key=distances.get)


def tag_attributes(img: Image.Image) -> dict:
    np_img = _ensure_numpy(img)
    height, width = np_img.shape[:2]

    flat = np_img.reshape(-1, 3).astype(np.float32)
    mean_rgb = flat.mean(axis=0)
    dominant = _closest_color(mean_rgb)

    orientation = "square"
    ratio = width / max(height, 1)
    if ratio > 1.1:
        orientation = "landscape"
    elif ratio < 0.9:
        orientation = "portrait"

    white_ratio = float(np.mean(np.all(np_img >= 245, axis=2)))

    return {
        "dominant_color": dominant,
        "mean_rgb": tuple(int(x) for x in mean_rgb),
        "orientation": orientation,
        "white_background_ratio": round(white_ratio, 3),
        "background_clean": white_ratio >= 0.6,
        "size_category": "large" if width * height >= 2048 * 2048 else "medium" if width * height >= 1024 * 1024 else "small",
    }


def save_output(img: Image.Image) -> Optional[str]:
    # Write to local disk if STORAGE_DIR is set; return filesystem path
    storage_dir = os.environ.get("STORAGE_DIR")
    if not storage_dir:
        return None
    os.makedirs(storage_dir, exist_ok=True)
    fname = f"{uuid.uuid4().hex}.png"
    out_path = os.path.join(storage_dir, fname)
    img.save(out_path)
    return out_path


def process_single(img: Image.Image) -> dict:
    segmented = segment_foreground(img)
    qa = quality_check(segmented)
    tags = tag_attributes(segmented)
    out_url = save_output(segmented)

    qa_status = qa.get("min_size_ok") and qa.get("blur_ok") and qa.get("brightness_ok")

    result = Result(
        width=img.size[0],
        height=img.size[1],
        tags=tags,
        qa={**qa, "status": "pass" if qa_status else "review"},
        output_url=out_url,
    )
    payload = result.model_dump()
    payload["segmentation"] = {"background_clean": tags.get("background_clean", False)}
    return payload
