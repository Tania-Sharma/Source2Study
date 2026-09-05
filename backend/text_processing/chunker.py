def chunk_text(text, chunk_size=200, chunk_overlap=30):
    """
    Split cleaned text into overlapping, word-boundary-safe chunks.

    NOTE ON chunk_size: This is a word count, not a guaranteed-safe
    token limit for any specific embedding model. 200 words is a
    reasonable RAG starting point, but the actual safe size should be
    verified against Member 2's chosen embedding model/tokenizer
    during integration. Words and tokens are not the same thing.

    Args:
        text (str): Cleaned text (already processed by text_cleaner).
        chunk_size (int): Target number of words per chunk.
        chunk_overlap (int): Number of words repeated between
            consecutive chunks, to preserve context across boundaries.

    Returns:
        list[dict]: A list of chunks, each with:
            - "chunk_index" (int): 0-based position of this chunk.
            - "text" (str): The chunk's text content.
            - "word_count" (int): Number of words in this chunk.

    Raises:
        ValueError: If text is not a string, or if chunk_size/overlap
            are invalid (e.g. non-positive, or overlap >= chunk_size).
    """

    if not isinstance(text, str):
        raise ValueError("text must be a string.")

    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    if not isinstance(chunk_overlap, int) or chunk_overlap < 0:
        raise ValueError("chunk_overlap must be a non-negative integer.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    if not text.strip():
        return []

    words = text.split()

    if len(words) <= chunk_size:
        # Entire text fits in a single chunk; no need to loop.
        return [{
            "chunk_index": 0,
            "text": " ".join(words),
            "word_count": len(words)
        }]

    chunks = []
    start = 0
    chunk_index = 0
    step = chunk_size - chunk_overlap  # how far we advance each time

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        chunks.append({
            "chunk_index": chunk_index,
            "text": " ".join(chunk_words),
            "word_count": len(chunk_words)
        })

        chunk_index += 1
        start += step

    return chunks