"""
rag_pipeline.py
The main entry point for Member 2's work -- implements exactly the
"Methodology" section of the synopsis:

  1. Take extracted/chunked text (from Member 1's resource_processing
     + text_processing modules).
  2. Convert chunks into vector representations using an embedding
     model (embeddings.py).
  3. Store them in a vector database -- FAISS via LangChain
     (vector_store.py).
  4. On a student query: search the vector database for the most
     relevant chunks (retriever.py).
  5. Build the context to hand to the LLM (context_builder.py).
  6. Track which sources/pages the answer came from
     (source_tracker.py) -- this becomes input to Member 3's LLM step.
"""

from backend.rag.vector_store import add_chunks
from backend.rag.retriever import retrieve
from backend.rag.context_builder import build_context
from backend.rag.source_tracker import get_sources, format_sources


def index_chunks(chunks):
    """
    Embed and store chunks coming from Member 1's build_chunks_from_pdf().
    Corresponds to synopsis Methodology steps 2-3 (embed + store).

    Args:
        chunks (list[dict]): Output of metadata.build_chunks_from_pdf().
    """
    if not chunks:
        return
    add_chunks(chunks)


def query_rag(query, top_k=5):
    """
    Full retrieval step for a user question (synopsis Methodology
    steps 4-5). Does NOT call the LLM itself (that's Member 3's
    ai/llm.py) -- this prepares everything the LLM needs: the context
    text and the sources to cite.

    Args:
        query (str): User's question.
        top_k (int): How many chunks to retrieve.

    Returns:
        dict: {
            "query": str,
            "context": str,       # pass this into the LLM prompt
            "sources": list[dict],
            "sources_text": str   # human-readable, show in UI
        }
    """
    retrieved = retrieve(query, top_k=top_k)
    context = build_context(retrieved)
    sources = get_sources(retrieved)

    return {
        "query": query,
        "context": context,
        "sources": sources,
        "sources_text": format_sources(sources),
    }


if __name__ == "__main__":
    # End-to-end manual check using Member 1's own PDF pipeline.
    from backend.resource_processing.pdf_handler import extract_pdf
    from backend.text_processing.metadata import build_chunks_from_pdf

    pdf_result = extract_pdf("sample.pdf", resource_id="demo_resource")
    chunks = build_chunks_from_pdf(pdf_result)

    print(f"Indexing {len(chunks)} chunks...")
    index_chunks(chunks)

    result = query_rag("What is this document about?", top_k=3)
    print("\n--- CONTEXT SENT TO LLM ---")
    print(result["context"])
    print("\n--- SOURCES ---")
    print(result["sources_text"])
