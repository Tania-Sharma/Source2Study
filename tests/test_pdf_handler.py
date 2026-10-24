import io
import pymupdf
import pytesseract
from unittest.mock import patch
from PIL import Image
from backend.resource_processing.pdf_handler import extract_pdf
def _make_blank_pdf(path):
    doc = pymupdf.open()
    doc.new_page()
    doc.save(str(path))
    doc.close()


def _make_text_pdf(path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello world, this is normal text.")
    doc.save(str(path))
    doc.close()


def _make_pdf_with_image(path):
    img = Image.new("RGB", (50, 50), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    doc = pymupdf.open()
    page = doc.new_page()
    rect = pymupdf.Rect(50, 50, 150, 150)
    page.insert_image(rect, stream=img_bytes.read())
    doc.save(str(path))
    doc.close()


def test_extract_pdf_ocr_fills_text_for_blank_page(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    _make_blank_pdf(pdf_path)

    with patch(
        "backend.resource_processing.pdf_handler.ocr_page",
        return_value="OCR extracted this text."
    ):
        result = extract_pdf(str(pdf_path), enable_ocr=True)

    page = result["pages"][0]
    assert page["has_text"] is True
    assert page["is_ocr"] is True
    assert page["text"] == "OCR extracted this text."


def test_extract_pdf_ocr_disabled_leaves_page_textless(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    _make_blank_pdf(pdf_path)

    result = extract_pdf(str(pdf_path), enable_ocr=False)

    page = result["pages"][0]
    assert page["has_text"] is False
    assert page["is_ocr"] is False


def test_extract_pdf_ocr_not_used_when_page_already_has_text(tmp_path):
    pdf_path = tmp_path / "text.pdf"
    _make_text_pdf(pdf_path)

    with patch("backend.resource_processing.pdf_handler.ocr_page") as mock_ocr:
        result = extract_pdf(str(pdf_path), enable_ocr=True)
        mock_ocr.assert_not_called()

    page = result["pages"][0]
    assert page["is_ocr"] is False
    assert page["has_text"] is True


def test_extract_pdf_ocr_gracefully_handles_empty_ocr_result(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    _make_blank_pdf(pdf_path)

    with patch(
        "backend.resource_processing.pdf_handler.ocr_page",
        return_value=""
    ):
        result = extract_pdf(str(pdf_path), enable_ocr=True)

    page = result["pages"][0]
    assert page["has_text"] is False
    assert page["is_ocr"] is False


def test_extract_pdf_detects_embedded_images(tmp_path):
    pdf_path = tmp_path / "with_image.pdf"
    _make_pdf_with_image(pdf_path)

    result = extract_pdf(str(pdf_path), enable_ocr=False)

    assert result["pages"][0]["image_count"] >= 1


def test_extract_pdf_zero_images_on_text_only_page(tmp_path):
    pdf_path = tmp_path / "text.pdf"
    _make_text_pdf(pdf_path)

    result = extract_pdf(str(pdf_path), enable_ocr=False)

    assert result["pages"][0]["image_count"] == 0