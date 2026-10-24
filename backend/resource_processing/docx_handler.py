import os
import docx
from docx.opc.exceptions import PackageNotFoundError
from docx.table import Table
from docx.text.paragraph import Paragraph


def _extract_table_text(table):
    """
    Flatten a python-docx Table into a simple, readable text block:
    cells within a row joined by " | ", rows joined by newlines.

    This is intentionally simple (not full Markdown table syntax) --
    it's good enough to preserve row/column meaning for an LLM without
    adding Markdown-parsing complexity.
    """
    rows_text = []
    for row in table.rows:
        cells_text = [cell.text.strip() for cell in row.cells]
        rows_text.append(" | ".join(cells_text))
    return "\n".join(rows_text)


def extract_docx(docx_path, resource_id=None):
    """
    Extract content from a DOCX file, preserving the true document
    order of paragraphs and tables.

    Unlike PDFs, DOCX files have no fixed "page" concept, so this
    returns a flat, ordered list of "elements" -- each either a
    paragraph or a table -- instead of pages.

    Requires python-docx >= 1.1.0 (for iter_inner_content()).

    Args:
        docx_path (str): Path to the DOCX file.
        resource_id (str, optional): Unique identifier for this
            resource, assigned by the caller.

    Returns:
        dict: {
            "resource_id": ...,
            "source_type": "docx",
            "source_name": ...,
            "element_count": int,
            "document_metadata": {"title": ..., "author": ...},
            "elements": [
                # paragraph element:
                {
                    "element_index": int,
                    "element_type": "paragraph",
                    "text": str,
                    "style": str or None,
                    "has_text": bool
                },
                # table element:
                {
                    "element_index": int,
                    "element_type": "table",
                    "text": str,          # flattened "cell | cell" rows
                    "row_count": int,
                    "column_count": int,
                    "has_text": bool
                },
                ...
            ]
        }

    Raises:
        ValueError: If docx_path is invalid, the file is corrupted,
            or the document has no content at all.
        FileNotFoundError: If the file does not exist.
        RuntimeError: If the installed python-docx is too old to
            support ordered extraction.
    """

    # --- Step 1: Input validation ---
    if not isinstance(docx_path, str) or not docx_path.strip():
        raise ValueError("docx_path must be a non-empty string.")

    if not docx_path.lower().endswith(".docx"):
        raise ValueError(f"File does not have a .docx extension: {docx_path}")

    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    # --- Step 2: Safe opening ---
    try:
        document = docx.Document(docx_path)
    except PackageNotFoundError:
        raise ValueError(f"Invalid or corrupted DOCX: {docx_path}")

    if not hasattr(document, "iter_inner_content"):
        raise RuntimeError(
            "Installed python-docx is too old for ordered paragraph+table "
            "extraction (needs iter_inner_content, added in 1.1.0). "
            "Run: pip install --upgrade python-docx"
        )

    # --- Step 3: Extract elements in true document order ---
    elements = []

    for index, item in enumerate(document.iter_inner_content(), start=1):
        if isinstance(item, Paragraph):
            text = item.text
            has_text = bool(text.strip())
            style_name = item.style.name if item.style is not None else None

            elements.append({
                "element_index": index,
                "element_type": "paragraph",
                "text": text,
                "style": style_name,
                "has_text": has_text
            })

        elif isinstance(item, Table):
            table_text = _extract_table_text(item)
            has_text = bool(table_text.strip())

            elements.append({
                "element_index": index,
                "element_type": "table",
                "text": table_text,
                "row_count": len(item.rows),
                "column_count": len(item.columns),
                "has_text": has_text
            })

    if len(elements) == 0:
        raise ValueError(f"DOCX has no content: {docx_path}")

    # --- Step 4: Document-level metadata ---
    core_props = document.core_properties

    document_metadata = {
        "title": core_props.title or None,
        "author": core_props.author or None,
    }

    result = {
        "resource_id": resource_id,
        "source_type": "docx",
        "source_name": os.path.basename(docx_path),
        "element_count": len(elements),
        "document_metadata": document_metadata,
        "elements": elements
    }

    return result