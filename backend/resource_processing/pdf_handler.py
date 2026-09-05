import os
import pymupdf


def extract_pdf(pdf_path, resource_id=None):
    """
    Extract text from a PDF page by page.

    Args:
        pdf_path (str): Path to the PDF file.
        resource_id (str, optional): Unique identifier for this resource,
            assigned by the caller (e.g. the upload/database layer).
            pdf_handler does not generate this itself.

    Returns:
        dict: Extracted PDF information, with per-page text, a flag
              indicating whether meaningful text was found, and
              document-level metadata.

    Raises:
        ValueError: If pdf_path is invalid, or the PDF is corrupted/empty.
        FileNotFoundError: If the file does not exist.
    """

    # --- Step 1: Input validation (before touching PyMuPDF at all) ---
    if not isinstance(pdf_path, str) or not pdf_path.strip():
        raise ValueError("pdf_path must be a non-empty string.")

    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"File does not have a .pdf extension: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # --- Step 2: Safe opening with context manager ---
    try:
        with pymupdf.open(pdf_path) as document:

            if document.page_count == 0:
                raise ValueError(f"PDF has no pages: {pdf_path}")

            pages = []

            for page_number, page in enumerate(document, start=1):
                text = page.get_text()
                has_text = bool(text.strip())

                pages.append({
                    "page_number": page_number,
                    "text": text,
                    "has_text": has_text
                })

            # --- Document-level metadata (title/author/etc.) ---
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