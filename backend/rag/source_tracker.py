"""
source_tracker.py
Given the chunks that were used to answer a question, produce a clean
list of "sources" (file + page number) to show the user in the UI.

This directly implements the synopsis requirement:
"Implement source/reference tracking" (Week 4) and
"generate answers based on the retrieved information ... reliable and
organized" (Introduction) -- the user should always see WHERE an
answer came from, not just the answer itself.
"""


def get_sources(retrieved_chunks):
    """
    Extract unique (source_name, page_number) pairs from retrieved chunks.

    Args:
        retrieved_chunks (list[dict]): Output of retriever.retrieve().
            Each item must have "metadata" with source_name, page_number,
            resource_id.

    Returns:
        list[dict]: Each item has "source_name", "page_number", "resource_id".
            Duplicates removed, order preserved (most relevant first).
    """
    seen = set()
    sources = []

    for chunk in retrieved_chunks:
        meta = chunk.get("metadata", {})
        key = (meta.get("source_name"), meta.get("page_number"))
        if key not in seen:
            seen.add(key)
            sources.append({
                "source_name": meta.get("source_name"),
                "page_number": meta.get("page_number"),
                "resource_id": meta.get("resource_id"),
            })

    return sources


def format_sources(sources):
    """
    Turn the sources list into a human-readable string for the UI.

    Args:
        sources (list[dict]): Output of get_sources().

    Returns:
        str: e.g. "Sources:\n- bio.pdf, Page 1\n- bio.pdf, Page 2"
    """
    if not sources:
        return "No sources found."

    lines = [f"- {s['source_name']}, Page {s['page_number']}" for s in sources]
    return "Sources:\n" + "\n".join(lines)


if __name__ == "__main__":
    fake_chunks = [
        {"metadata": {"source_name": "bio.pdf", "page_number": 1, "resource_id": "r1"}},
        {"metadata": {"source_name": "bio.pdf", "page_number": 1, "resource_id": "r1"}},  # duplicate
        {"metadata": {"source_name": "bio.pdf", "page_number": 2, "resource_id": "r1"}},
    ]
    srcs = get_sources(fake_chunks)
    print(srcs)
    print(format_sources(srcs))
