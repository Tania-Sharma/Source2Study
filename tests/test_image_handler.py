import os
import tempfile
from unittest.mock import patch
from PIL import Image
import pytest
from backend.resource_processing.image_handler import extract_image
from backend.text_processing.metadata import build_chunks_from_image


def test_extract_image_invalid():
    with pytest.raises(ValueError):
        extract_image("sample.pdf")
    with pytest.raises(FileNotFoundError):
        extract_image("nonexistent_image.png")


def test_extract_image_success():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        img = Image.new("RGB", (200, 100), color=(255, 255, 255))
        img.save(tmp_path)

        with patch("backend.resource_processing.image_handler.ocr_image", return_value="Sample OCR Diagram Text"):
            res = extract_image(tmp_path, resource_id="img_01", enable_ocr=True)

        assert res["resource_id"] == "img_01"
        assert res["source_type"] == "image"
        assert res["dimensions"] == {"width": 200, "height": 100}
        assert res["text"] == "Sample OCR Diagram Text"
        assert res["has_text"] is True

        chunks = build_chunks_from_image(res)
        assert len(chunks) == 1
        assert chunks[0]["metadata"]["content_type"] == "ocr_image"
        assert chunks[0]["metadata"]["is_ocr"] is True
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
