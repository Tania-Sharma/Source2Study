"""
vector_store.py
Stores chunk text + metadata as vectors using LangChain's FAISS
integration (per project synopsis), and supports similarity search.
The index is saved to disk (./faiss_index) so it persists between runs.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.rag.embeddings import get_embedding_model

# Absolute path so the index is found no matter which folder you run
# python from (this was the bug we hit with the old chromadb version).
_INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiss_index")

_vector_store = None


def _chunks_to_documents(chunks):
    """Convert Member 1's chunk dicts into LangChain Document objects."""
    return [
        Document(page_content=c["text"], metadata=c["metadata"])
        for c in chunks
    ]


def _load_existing():
    """Load a previously saved FAISS index from disk, if one exists."""
    embedding_model = get_embedding_model()
    if os.path.exists(_INDEX_PATH):
        return FAISS.load_local(
            _INDEX_PATH, embedding_model, allow_dangerous_deserialization=True
        )
    return None


def add_chunks(chunks):
    """
    Embed and store chunks in the FAISS vector store.

    Args:
        chunks (list[dict]): Output of Member 1's build_chunks_from_pdf().
            Each chunk must have "text" and "metadata".

    Raises:
        ValueError: If chunks is empty.
    """
    global _vector_store

    if not chunks:
        raise ValueError("chunks must be a non-empty list.")

    documents = _chunks_to_documents(chunks)
    embedding_model = get_embedding_model()

    if _vector_store is None:
        _vector_store = _load_existing()

    if _vector_store is None:
        _vector_store = FAISS.from_documents(documents, embedding_model)
    else:
        _vector_store.add_documents(documents)

    _vector_store.save_local(_INDEX_PATH)


def search(query, top_k=5):
    """
    Find the top_k chunks most similar to the query text.
    (LangChain's FAISS wrapper embeds the query internally -- you pass
    plain text here, not a vector.)

    Args:
        query (str): The user's natural-language question.
        top_k (int): How many matches to return.

    Returns:
        list[dict]: Each item has "text", "metadata", "score"
            (lower score = more similar).
    """
    global _vector_store

    if _vector_store is None:
        _vector_store = _load_existing()

    if _vector_store is None:
        return []

    results = _vector_store.similarity_search_with_score(query, k=top_k)

    matched = []
    for doc, score in results:
        matched.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),
        })
    return matched


def count():
    """Utility: how many vectors are currently stored. Useful for debugging."""
    global _vector_store
    if _vector_store is None:
        _vector_store = _load_existing()
    if _vector_store is None:
        return 0
    return _vector_store.index.ntotal


if __name__ == "__main__":
    # Quick manual check: run "python vector_store.py" from the rag/ folder,
    # or "python -m backend.rag.vector_store" from the project root.
    dummy_chunks = [
        {
            "text": "The mitochondria is the powerhouse of the cell.",
            "metadata": {"source_name": "bio.pdf", "page_number": 1, "resource_id": "test"},
        },
        {
            "text": "Newton's second law states F equals mass times acceleration.",
            "metadata": {"source_name": "physics.pdf", "page_number": 3, "resource_id": "test"},
        },
    ]

    add_chunks(dummy_chunks)
    print("Total vectors stored:", count())

    results = search("What powers a cell?", top_k=2)
    for r in results:
        print("score:", round(r["score"], 4), "|", r["text"])
