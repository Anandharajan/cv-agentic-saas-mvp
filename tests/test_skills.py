import numpy as np
from PIL import Image, ImageDraw

from src.agents.skills import (
    process_single,
    quality_check,
    segment_foreground,
    tag_attributes,
)


def _make_test_image(size: int = 128) -> Image.Image:
    img = Image.new("RGB", (size, size), color=(210, 210, 210))
    draw = ImageDraw.Draw(img)
    draw.rectangle((size // 4, size // 4, 3 * size // 4, 3 * size // 4), fill=(30, 30, 30))
    return img


def test_segment_foreground_cleans_background():
    img = _make_test_image()
    segmented = segment_foreground(img)
    arr = np.array(segmented)
    assert arr[0, 0].mean() >= 200  # background pushed to white
    assert arr[arr.shape[0] // 2, arr.shape[1] // 2].mean() < 100  # object preserved


def test_quality_check_scores():
    img = _make_test_image()
    qa = quality_check(img)
    assert qa["blur_score"] > 0
    assert qa["brightness"] > 0
    assert qa["min_size_ok"] is False  # synthetic image is tiny


def test_tag_attributes_extracts_metadata():
    img = _make_test_image()
    tags = tag_attributes(img)
    assert set(tags).issuperset({"dominant_color", "orientation", "background_clean"})
    assert tags["orientation"] == "square"


def test_process_single_pipeline():
    img = _make_test_image()
    result = process_single(img)
    assert result["status"] == "ok"
    assert result["qa"]["status"] in {"pass", "review"}
    assert "segmentation" in result
    assert result["tags"]["background_clean"] is True
