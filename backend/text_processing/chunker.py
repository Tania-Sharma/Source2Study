def chunk_text(text, chunk_size=200, chunk_overlap=30):
    """
    Split cleaned text into overlapping, word-boundary-safe chunks.

    NOTE:
        chunk_size is a word count, not a guaranteed-safe token limit
        for a specific embedding model. The final chunk size should be
        verified against the embedding model/tokenizer during integration.

    Args:
        text (str): Cleaned text.
        chunk_size (int): Target number of words per chunk.
        chunk_overlap (int): Number of overlapping words between chunks.

    Returns:
        list[dict]: List of chunks containing:
            - chunk_index
            - text
            - word_count

    Raises:
        ValueError: If text or chunk parameters are invalid.
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
        return [{
            "chunk_index": 0,
            "text": " ".join(words),
            "word_count": len(words)
        }]

    chunks = []
    start = 0
    chunk_index = 0
    step = chunk_size - chunk_overlap

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]

        chunks.append({
            "chunk_index": chunk_index,
            "text": " ".join(chunk_words),
            "word_count": len(chunk_words)
        })

        chunk_index += 1

        # Stop once the current chunk has reached the end.
        if end == len(words):
            break

        start += step

    return chunks