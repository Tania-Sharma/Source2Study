import pytest
import pymupdf

from backend.resource_processing.pdf_handler import extract_pdf


def test_extract_pdf():
    pdf_path = "tests/TableOfContents.pdf"

    result = extract_pdf(pdf_path)

    assert result["source_type"] == "pdf"
    assert result["page_count"] > 0
    assert len(result["pages"]) == result["page_count"]
    assert result["pages"][0]["text"].strip() != ""

    for index, page in enumerate(result["pages"], start=1):
        assert page["page_number"] == index

    # Check that at least one page contains text
    assert any(page["text"].strip() for page in result["pages"])


def test_extract_pdf_file_not_found():
    pdf_path = "tests/does_not_exist.pdf"

    try:
        extract_pdf(pdf_path)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True


def test_extract_pdf_invalid_format():
    pdf_path = "tests/invalid.pdf"

    try:
        extract_pdf(pdf_path)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


# ---------------- New tests below ----------------

def test_extract_pdf_wrong_extension(tmp_path):
    """A file that doesn't end in .pdf should be rejected before
    PyMuPDF even tries to open it."""

    fake_file = tmp_path / "notes.txt"
    fake_file.write_text("just some text, not a real pdf")

    with pytest.raises(ValueError):
        extract_pdf(str(fake_file))


from unittest.mock import patch, MagicMock


def test_extract_pdf_empty_pdf(tmp_path):
    """A PDF that PyMuPDF reports as having zero pages should be
    rejected with a clear ValueError. We can't create a real
    zero-page PDF on disk (PyMuPDF refuses to save one), so we
    simulate this case by mocking pymupdf.open()."""

    # We still need a real file on disk, because our own code
    # checks os.path.exists() before ever calling pymupdf.open().
    # The content doesn't matter since pymupdf.open() will be faked.
    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%%EOF")

    # Build a fake document object that behaves like a context manager
    # (supports "with ... as document:") and reports page_count = 0.
    fake_document = MagicMock()
    fake_document.page_count = 0
    fake_document.__enter__.return_value = fake_document
    fake_document.__exit__.return_value = False

    # Replace pymupdf.open, but ONLY inside this "with" block, and
    # ONLY as seen from inside pdf_handler.py's namespace.
    with patch("backend.resource_processing.pdf_handler.pymupdf.open", return_value=fake_document):
        with pytest.raises(ValueError):
            extract_pdf(str(pdf_path))


def test_extract_pdf_no_text_page(tmp_path):
    """A page with no text content should be marked has_text=False,
    instead of being silently treated the same as a page with text."""

    blank_pdf_path = tmp_path / "blank_page.pdf"

    new_doc = pymupdf.open()
    new_doc.new_page()  # adds one blank page, no text inserted
    new_doc.save(str(blank_pdf_path))
    new_doc.close()

    result = extract_pdf(str(blank_pdf_path))

    assert result["page_count"] == 1
    assert result["pages"][0]["has_text"] is False