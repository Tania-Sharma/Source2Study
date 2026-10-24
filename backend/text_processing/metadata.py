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


def build_chunks_from_docx(docx_result, chunk_size=200, chunk_overlap=30):
    """
    Take the raw output of extract_docx() and produce standardized,
    metadata-tagged chunks, preserving document order between
    paragraph text and tables.

    Paragraph text is accumulated and chunked normally (content_type
    "text"). Each table becomes its own dedicated chunk (content_type
    "table") without going through word-based chunking, since
    splitting a table mid-row/column would destroy its structure.

    Args:
        docx_result (dict): The dict returned by extract_docx(). Must
            include "resource_id" (non-empty), "source_type",
            "source_name", and "elements".
        chunk_size (int): Passed through to chunk_text() for
            paragraph text only.
        chunk_overlap (int): Passed through to chunk_text() for
            paragraph text only.

    Returns:
        list[dict]: Standardized chunks, same schema as
            build_chunks_from_pdf(), with page_number always None,
            and content_type either "text" or "table".

    Raises:
        ValueError: If docx_result is missing required keys, or if
            resource_id is missing/empty.
    """

    required_keys = ("resource_id", "source_type", "source_name", "elements")
    for key in required_keys:
        if key not in docx_result:
            raise ValueError(f"docx_result is missing required key: '{key}'")

    resource_id = docx_result["resource_id"]

    if not resource_id or not isinstance(resource_id, str):
        raise ValueError(
            "resource_id must be a non-empty string to build chunks."
        )

    source_type = docx_result["source_type"]
    source_name = docx_result["source_name"]

    all_chunks = []
    global_chunk_index = 0
    paragraph_buffer = []

    def _flush_paragraph_buffer():
        nonlocal global_chunk_index

        if not paragraph_buffer:
            return

        combined_text = "\n".join(paragraph_buffer)
        paragraph_buffer.clear()

        cleaned = clean_text(combined_text)
        if not cleaned:
            return

        for chunk in chunk_text(cleaned, chunk_size=chunk_size, chunk_overlap=chunk_overlap):
            chunk_id = f"{resource_id}_C{global_chunk_index:04d}"

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "metadata": {
                    "resource_id": resource_id,
                    "source_type": source_type,
                    "source_name": source_name,
                    "page_number": None,
                    "chunk_index": global_chunk_index,
                    "content_type": "text",
                    "word_count": chunk["word_count"],
                    "is_ocr": False
                }
            })

            global_chunk_index += 1

    for element in docx_result["elements"]:

        if element["element_type"] == "paragraph":
            if element.get("has_text", False):
                paragraph_buffer.append(element["text"])

        elif element["element_type"] == "table":
            # Flush any pending paragraph text BEFORE the table, so
            # ordering in the chunk sequence roughly follows document
            # order (text before the table, then the table itself).
            _flush_paragraph_buffer()

            if not element.get("has_text", False):
                continue

            chunk_id = f"{resource_id}_C{global_chunk_index:04d}"

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": element["text"],
                "metadata": {
                    "resource_id": resource_id,
                    "source_type": source_type,
                    "source_name": source_name,
                    "page_number": None,
                    "chunk_index": global_chunk_index,
                    "content_type": "table",
                    "word_count": len(element["text"].split()),
                    "is_ocr": False
                }
            })

            global_chunk_index += 1

    # Flush any trailing paragraph text after the last table (or if
    # there were no tables at all).
    _flush_paragraph_buffer()

    return all_chunks


def _format_seconds(seconds: float) -> str:
    """Format seconds into MM:SS or HH:MM:SS format."""
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def build_chunks_from_youtube(youtube_result, chunk_size=200, chunk_overlap=30):
    """
    Produce standardized chunks from extract_youtube() output.
    Preserves start and end timestamps so citations can link to specific video intervals.
    """
    required_keys = ("resource_id", "source_type", "source_name", "segments")
    for key in required_keys:
        if key not in youtube_result:
            raise ValueError(f"youtube_result is missing required key: '{key}'")

    resource_id = youtube_result["resource_id"]
    if not resource_id or not isinstance(resource_id, str):
        raise ValueError("resource_id must be a non-empty string to build chunks.")

    source_type = youtube_result["source_type"]
    source_name = youtube_result["source_name"]
    video_url = youtube_result.get("url")

    all_chunks = []
    global_chunk_index = 0

    current_words = []
    current_start = 0.0
    current_end = 0.0

    segments = youtube_result["segments"]
    if not segments:
        return []

    for seg in segments:
        seg_text = clean_text(seg["text"])
        if not seg_text:
            continue

        words = seg_text.split()
        if not current_words:
            current_start = seg["start"]
        current_words.extend(words)
        current_end = seg["start"] + seg.get("duration", 0.0)

        if len(current_words) >= chunk_size:
            chunk_words = current_words[:chunk_size]
            timestamp_str = f"{_format_seconds(current_start)} - {_format_seconds(current_end)}"
            chunk_id = f"{resource_id}_C{global_chunk_index:04d}"

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": " ".join(chunk_words),
                "metadata": {
                    "resource_id": resource_id,
                    "source_type": source_type,
                    "source_name": source_name,
                    "url": video_url,
                    "page_number": None,
                    "timestamp": timestamp_str,
                    "start_time": round(current_start, 2),
                    "end_time": round(current_end, 2),
                    "chunk_index": global_chunk_index,
                    "content_type": "transcript",
                    "word_count": len(chunk_words),
                    "is_ocr": False,
                },
            })
            global_chunk_index += 1

            # Retain overlap words
            step = chunk_size - chunk_overlap
            current_words = current_words[step:]
            current_start = seg["start"]

    if current_words:
        timestamp_str = f"{_format_seconds(current_start)} - {_format_seconds(current_end)}"
        chunk_id = f"{resource_id}_C{global_chunk_index:04d}"
        all_chunks.append({
            "chunk_id": chunk_id,
            "text": " ".join(current_words),
            "metadata": {
                "resource_id": resource_id,
                "source_type": source_type,
                "source_name": source_name,
                "url": video_url,
                "page_number": None,
                "timestamp": timestamp_str,
                "start_time": round(current_start, 2),
                "end_time": round(current_end, 2),
                "chunk_index": global_chunk_index,
                "content_type": "transcript",
                "word_count": len(current_words),
                "is_ocr": False,
            },
        })

    return all_chunks


def build_chunks_from_web(web_result, chunk_size=200, chunk_overlap=30):
    """
    Produce standardized chunks from extract_web_content() output.
    Associates chunks with original URL and section headings.
    """
    required_keys = ("resource_id", "source_type", "source_name", "sections")
    for key in required_keys:
        if key not in web_result:
            raise ValueError(f"web_result is missing required key: '{key}'")

    resource_id = web_result["resource_id"]
    if not resource_id or not isinstance(resource_id, str):
        raise ValueError("resource_id must be a non-empty string to build chunks.")

    source_type = web_result["source_type"]
    source_name = web_result["source_name"]
    web_url = web_result.get("url")

    all_chunks = []
    global_chunk_index = 0

    for sec in web_result.get("sections", []):
        heading = sec.get("heading", "")
        content = sec.get("content", "")
        cleaned = clean_text(content)
        if not cleaned:
            continue

        sec_chunks = chunk_text(cleaned, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for chunk in sec_chunks:
            chunk_id = f"{resource_id}_C{global_chunk_index:04d}"
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "metadata": {
                    "resource_id": resource_id,
                    "source_type": source_type,
                    "source_name": source_name,
                    "url": web_url,
                    "heading": heading,
                    "page_number": None,
                    "chunk_index": global_chunk_index,
                    "content_type": "text",
                    "word_count": chunk["word_count"],
                    "is_ocr": False,
                },
            })
            global_chunk_index += 1

    return all_chunks


def build_chunks_from_image(image_result):
    """
    Produce standardized chunk from extract_image() output.
    """
    required_keys = ("resource_id", "source_type", "source_name", "text")
    for key in required_keys:
        if key not in image_result:
            raise ValueError(f"image_result is missing required key: '{key}'")

    resource_id = image_result["resource_id"]
    if not resource_id or not isinstance(resource_id, str):
        raise ValueError("resource_id must be a non-empty string to build chunks.")

    cleaned = clean_text(image_result["text"])
    if not cleaned:
        return []

    chunk_id = f"{resource_id}_C0000"
    return [{
        "chunk_id": chunk_id,
        "text": cleaned,
        "metadata": {
            "resource_id": resource_id,
            "source_type": image_result["source_type"],
            "source_name": image_result["source_name"],
            "page_number": None,
            "chunk_index": 0,
            "content_type": "ocr_image",
            "word_count": len(cleaned.split()),
            "is_ocr": True,
        },
    }]
