"""
embeddings.py
Wraps a free, local HuggingFace sentence-transformers model using
LangChain's embedding interface, so it plugs directly into LangChain's
FAISS vector store (per project synopsis: LangChain + FAISS).
"""

from langchain_huggingface import HuggingFaceEmbeddings

_embedding_model = None


def get_embedding_model():
    """
    Returns the LangChain embedding model object (singleton, loaded once).
    This object is what vector_store.py hands to FAISS -- FAISS will
    call it internally whenever it needs to embed text.

    Model: sentence-transformers/all-MiniLM-L6-v2
        - Free, runs locally, no API key needed
        - Produces 384-dimensional vectors
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embedding_model


def generate_embedding(text):
    """
    Generate an embedding for a single piece of text.
    Mainly useful for quick manual testing (see __main__ below).
    The actual pipeline (vector_store.py) uses get_embedding_model()
    directly and lets FAISS call it internally.

    Args:
        text (str): Text to embed.

    Returns:
        list[float]: The embedding vector.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string.")
    model = get_embedding_model()
    return model.embed_query(text)


def generate_embeddings(texts):
    """
    Generate embeddings for multiple texts at once (batch).

    Args:
        texts (list[str]): List of texts.

    Returns:
        list[list[float]]: One embedding vector per input text.
    """
    if not isinstance(texts, list) or not texts:
        raise ValueError("texts must be a non-empty list of strings.")
    model = get_embedding_model()
    return model.embed_documents(texts)


if __name__ == "__main__":
    # Quick manual check: run "python embeddings.py" directly.
    sample = "Photosynthesis is the process by which plants make food."
    vector = generate_embedding(sample)
    print("Text:", sample)
    print("Embedding length (should be 384 for this model):", len(vector))
    print("First 5 values:", vector[:5])
