import pymupdf
import pytesseract
from unittest.mock import patch
from PIL import Image

from backend.resource_processing.ocr import ocr_page, ocr_image


def test_ocr_page_handles_tesseract_not_found(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()

    doc = pymupdf.open(str(pdf_path))
    page = doc[0]

    with patch(
        "pytesseract.image_to_string",
        side_effect=pytesseract.TesseractNotFoundError
    ):
        result = ocr_page(page)

    doc.close()
    assert result == ""


def test_ocr_image_handles_tesseract_not_found():
    fake_image = Image.new("RGB", (10, 10), color="white")

    with patch(
        "pytesseract.image_to_string",
        side_effect=pytesseract.TesseractNotFoundError
    ):
        result = ocr_image(fake_image)

    assert result == ""


def test_ocr_image_returns_text_when_mocked():
    fake_image = Image.new("RGB", (10, 10), color="white")

    with patch("pytesseract.image_to_string", return_value="mocked text"):
        result = ocr_image(fake_image)

    assert result == "mocked text"