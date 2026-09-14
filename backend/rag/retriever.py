"""
retriever.py
Takes a user's natural-language query and fetches the most relevant
stored chunks from the FAISS vector store (backend.rag.vector_store).
"""

from backend.rag.vector_store import search


def retrieve(query, top_k=5):
    """
    Retrieve the top_k most relevant chunks for a user query.

    Args:
        query (str): The user's question.
        top_k (int): Number of chunks to retrieve.

    Returns:
        list[dict]: Matched chunks with "text", "metadata", "score".

    Raises:
        ValueError: If query is empty.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")

    return search(query, top_k=top_k)


if __name__ == "__main__":
    # Quick manual check (run from project root: python -m backend.rag.retriever)
    # Assumes vector_store.py's __main__ block has already been run once,
    # so there's data in the FAISS index to search.
    results = retrieve("What powers a cell?", top_k=2)
    for r in results:
        print("score:", round(r["score"], 4), "|", r["text"])
