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
    """Convert chunk dicts into LangChain Document objects."""
    docs = []
    for c in chunks:
        meta = dict(c.get("metadata", {}))
        if "chunk_id" in c and "chunk_id" not in meta:
            meta["chunk_id"] = c["chunk_id"]
        docs.append(Document(page_content=c["text"], metadata=meta))
    return docs


def _load_existing():
    """Load a previously saved FAISS index from disk, if one exists."""
    embedding_model = get_embedding_model()
    if os.path.exists(_INDEX_PATH):
        return FAISS.load_local(
            _INDEX_PATH, embedding_model, allow_dangerous_deserialization=True
        )
    return None


def _get_existing_chunk_identifiers(store):
    """Collect identifiers of existing chunks in the vector store."""
    if store is None or not hasattr(store, "docstore"):
        return set()
    existing = set()
    for doc in store.docstore._dict.values():
        if hasattr(doc, "metadata") and doc.metadata:
            cid = doc.metadata.get("chunk_id")
            if cid:
                existing.add(cid)
            elif doc.metadata.get("resource_id") and "chunk_index" in doc.metadata:
                existing.add(f"{doc.metadata['resource_id']}_{doc.metadata['chunk_index']}")
    return existing


def add_chunks(chunks):
    """
    Embed and store chunks in the FAISS vector store.
    Prevents duplicate indexing if the same resource/chunks are indexed multiple times.

    Args:
        chunks (list[dict]): Output of chunk builders.
            Each chunk must have "text" and "metadata".

    Raises:
        ValueError: If chunks is empty.
    """
    global _vector_store

    if not chunks:
        raise ValueError("chunks must be a non-empty list.")

    embedding_model = get_embedding_model()

    if _vector_store is None:
        _vector_store = _load_existing()

    existing_ids = _get_existing_chunk_identifiers(_vector_store)
    new_chunks = []
    for c in chunks:
        cid = c.get("chunk_id")
        if not cid and c.get("metadata"):
            cid = f"{c['metadata'].get('resource_id')}_{c['metadata'].get('chunk_index')}"
        if cid and cid in existing_ids:
            continue
        new_chunks.append(c)

    if not new_chunks:
        # All chunks already indexed
        return

    documents = _chunks_to_documents(new_chunks)

    if _vector_store is None:
        _vector_store = FAISS.from_documents(documents, embedding_model)
    else:
        _vector_store.add_documents(documents)

    _vector_store.save_local(_INDEX_PATH)


def search(query, top_k=5, resource_id=None):
    global _vector_store

    if _vector_store is None:
        _vector_store = _load_existing()

    if _vector_store is None:
        return []

    fetch_k = max(top_k * 4, 20) if resource_id else top_k
    try:
        results = _vector_store.similarity_search_with_score(query, k=fetch_k)
    except Exception:
        results = []

    matched = []
    for doc, score in results:
        if resource_id:
            meta = doc.metadata or {}
            if meta.get("resource_id") != resource_id:
                continue
        matched.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),
        })
        if len(matched) >= top_k:
            break
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
    dummy_chunks = [
        {
            "chunk_id": "demo_test_01",
            "text": "The mitochondria is the powerhouse of the cell.",
            "metadata": {"source_name": "bio.pdf", "page_number": 1, "resource_id": "test"},
        },
        {
            "chunk_id": "demo_test_02",
            "text": "Newton's second law states F equals mass times acceleration.",
            "metadata": {"source_name": "physics.pdf", "page_number": 3, "resource_id": "test"},
        },
    ]

    add_chunks(dummy_chunks)
    print("Total vectors stored:", count())

    results = search("What powers a cell?", top_k=2)
    for r in results:
        print("score:", round(r["score"], 4), "|", r["text"])
