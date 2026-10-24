import os
import pymupdf

from backend.resource_processing.ocr import ocr_page


def extract_pdf(pdf_path, resource_id=None, enable_ocr=True):
    """
    Extract text from a PDF page by page, with OCR fallback for
    text-less (likely scanned) pages, and embedded-image detection.

    Args:
        pdf_path (str): Path to the PDF file.
        resource_id (str, optional): Unique identifier for this resource.
        enable_ocr (bool): Whether to attempt OCR on pages with no
            extractable text. Defaults to True.

    Returns:
        dict: Extracted PDF information. Each page includes:
            - page_number (int)
            - text (str)
            - has_text (bool)
            - is_ocr (bool): True if this page's text came from OCR
            - image_count (int): number of embedded images on this page

    Raises:
        ValueError: If pdf_path is invalid, the PDF is corrupted/empty,
            or the PDF is password-protected/encrypted.
        FileNotFoundError: If the file does not exist.
    """

    if not isinstance(pdf_path, str) or not pdf_path.strip():
        raise ValueError("pdf_path must be a non-empty string.")

    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"File does not have a .pdf extension: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        with pymupdf.open(pdf_path) as document:

            if document.is_encrypted:
                raise ValueError(f"PDF is password-protected/encrypted: {pdf_path}")

            if document.page_count == 0:
                raise ValueError(f"PDF has no pages: {pdf_path}")

            pages = []

            for page_number, page in enumerate(document, start=1):
                text = page.get_text()
                has_text = bool(text.strip())
                is_ocr = False

                if not has_text and enable_ocr:
                    ocr_text = ocr_page(page)
                    if ocr_text.strip():
                        text = ocr_text
                        has_text = True
                        is_ocr = True

                image_count = len(page.get_images(full=True))

                pages.append({
                    "page_number": page_number,
                    "text": text,
                    "has_text": has_text,
                    "is_ocr": is_ocr,
                    "image_count": image_count
                })

            raw_metadata = document.metadata or {}

            document_metadata = {
                "title": raw_metadata.get("title") or None,
                "author": raw_metadata.get("author") or None,
                "creation_date": raw_metadata.get("creationDate") or None,
            }

            result = {
                "resource_id": resource_id,
                "source_type": "pdf",
                "source_name": os.path.basename(pdf_path),
                "page_count": document.page_count,
                "document_metadata": document_metadata,
                "pages": pages
            }

        return result

    except pymupdf.FileDataError:
        raise ValueError(f"Invalid or corrupted PDF: {pdf_path}")