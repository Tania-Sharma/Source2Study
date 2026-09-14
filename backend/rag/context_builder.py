"""
context_builder.py
Turns retrieved chunks into a single clean string that can be inserted
into the LLM prompt (Member 3's ai/llm.py will use this).

Each chunk is tagged with its source so the LLM (and later
source_tracker.py) knows where each piece of text came from.
"""


def build_context(retrieved_chunks):
    """
    Combine retrieved chunks into one context string for the LLM prompt.

    Args:
        retrieved_chunks (list[dict]): Output of retriever.retrieve().
            Each item must have "text" and "metadata".

    Returns:
        str: Combined context, empty string if no chunks given.
    """
    if not retrieved_chunks:
        return ""

    parts = []
    for chunk in retrieved_chunks:
        meta = chunk.get("metadata", {})
        source_tag = f"[Source: {meta.get('source_name')}, Page {meta.get('page_number')}]"
        parts.append(f"{source_tag}\n{chunk['text']}")

    return "\n\n".join(parts)


if __name__ == "__main__":
    # Quick manual check with fake data (no FAISS index needed).
    fake_chunks = [
        {
            "text": "The mitochondria is the powerhouse of the cell.",
            "metadata": {"source_name": "bio.pdf", "page_number": 1},
        },
        {
            "text": "Cells use mitochondria to produce ATP energy.",
            "metadata": {"source_name": "bio.pdf", "page_number": 2},
        },
    ]
    print(build_context(fake_chunks))
