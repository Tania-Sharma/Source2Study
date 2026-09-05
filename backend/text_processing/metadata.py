from backend.text_processing.text_cleaner import clean_text
from backend.text_processing.chunker import chunk_text


def build_chunks_from_pdf(pdf_result, chunk_size=200, chunk_overlap=30):
    """
    Take the raw output of extract_pdf() and produce standardized,
    metadata-tagged chunks ready to hand off to Member 2 (embeddings/RAG).

    resource_id is required here (even though it's optional at the
    extract_pdf() stage), because chunks without a resource_id would
    be meaningless once mixed into a shared vector store across
    multiple resources.

    Args:
        pdf_result (dict): The dict returned by extract_pdf(). Must
            include "resource_id" (non-empty), "source_type",
            "source_name", and "pages".
        chunk_size (int): Passed through to chunk_text().
        chunk_overlap (int): Passed through to chunk_text().

    Returns:
        list[dict]: Standardized chunks, each with:
            - chunk_id (str)
            - text (str)
            - metadata (dict):
                resource_id, source_type, source_name, page_number,
                chunk_index, content_type, word_count, is_ocr

    Raises:
        ValueError: If pdf_result is missing required keys, or if
            resource_id is missing/empty.
    """

    required_keys = ("resource_id", "source_type", "source_name", "pages")
    for key in required_keys:
        if key not in pdf_result:
            raise ValueError(f"pdf_result is missing required key: '{key}'")

    resource_id = pdf_result["resource_id"]

    if not resource_id or not isinstance(resource_id, str):
        raise ValueError(
            "resource_id must be a non-empty string to build chunks. "
            "extract_pdf() allows resource_id=None for standalone "
            "extraction, but build_chunks_from_pdf() requires it "
            "since chunks are meant to enter a shared vector store."
        )

    source_type = pdf_result["source_type"]
    source_name = pdf_result["source_name"]

    all_chunks = []
    global_chunk_index = 0

    for page in pdf_result["pages"]:
        if not page.get("has_text", False):
            continue

        cleaned = clean_text(page["text"])

        if not cleaned:
            continue

        page_chunks = chunk_text(cleaned, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        for chunk in page_chunks:
            chunk_id = f"{resource_id}_C{global_chunk_index:04d}"

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "metadata": {
                    "resource_id": resource_id,
                    "source_type": source_type,
                    "source_name": source_name,
                    "page_number": page["page_number"],
                    "chunk_index": global_chunk_index,
                    "content_type": "text",
                    "word_count": chunk["word_count"],
                    "is_ocr": False
                }
            })

            global_chunk_index += 1

    return all_chunks