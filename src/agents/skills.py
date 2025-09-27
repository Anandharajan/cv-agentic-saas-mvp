from PIL import Image
from pydantic import BaseModel
import os
from typing import Optional
import uuid


class Result(BaseModel):
    status: str = "ok"
    width: int = 0
    height: int = 0
    tags: dict = {}
    qa: dict = {}
    output_url: Optional[str] = None


def segment_foreground(img: Image.Image) -> Image.Image:
    # TODO: call segmenter; MVP returns original
    return img


def quality_check(img: Image.Image) -> dict:
    # TODO: simple heuristics (size, sharpness proxy)
    w, h = img.size
    return {"min_size_ok": w * h >= 512 * 512, "sharpness": "tbd"}


def tag_attributes(img: Image.Image) -> dict:
    # TODO: classifier or color histogram
    return {"category": "unknown", "dominant_color": "tbd"}


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
    seg = segment_foreground(img)
    qa = quality_check(seg)
    tags = tag_attributes(seg)
    out_url = save_output(seg)
    r = Result(width=img.size[0], height=img.size[1], tags=tags, qa=qa, output_url=out_url)
    return r.dict()
