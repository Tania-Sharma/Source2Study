import io
import os
import pytesseract
from PIL import Image

# Allow overriding the Tesseract binary location via an environment
# variable, since it isn't always on PATH (especially on Windows).
# Set TESSERACT_CMD in your .env if needed, e.g.:
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
_tesseract_cmd = os.environ.get("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


def ocr_page(page, dpi=300):
    """
    Render a PDF page to an image and run OCR on it.

    This is shared OCR logic, intentionally kept independent of
    pdf_handler.py so that image_handler.py (for directly-uploaded
    images) can reuse it later without depending on the PDF module.

    This is a best-effort helper: it never raises. If Tesseract isn't
    installed, or OCR fails for any reason, it returns an empty
    string rather than crashing the caller's extraction pipeline.

    Args:
        page: A PyMuPDF page object.
        dpi (int): Resolution to render the page at before OCR.
            Higher = more accurate but slower. 300 is a common
            sweet spot for OCR accuracy vs. speed.

    Returns:
        str: OCR-extracted text, or "" if unavailable/empty.
    """
    try:
        pix = page.get_pixmap(dpi=dpi)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError:
        return ""
    except Exception:
        return ""


def ocr_image(image, dpi=None):
    """
    Run OCR directly on a PIL Image object.

    This is the entry point image_handler.py will use later for
    directly-uploaded images (JPG/PNG/etc.), as opposed to ocr_page()
    which is specifically for PDF page objects. dpi is unused here
    (images don't need re-rendering) but kept in the signature for
    interface consistency with ocr_page().

    Args:
        image (PIL.Image.Image): An already-loaded image.

    Returns:
        str: OCR-extracted text, or "" if unavailable/empty.
    """
    try:
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError:
        return ""
    except Exception:
        return ""