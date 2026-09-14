"""
test_rag_full_flow.py

Run this to check EVERYTHING in one go, using fake chunks (no PDF needed).
This proves your rag/ modules (LangChain + FAISS) work correctly before
plugging in Member 1's real pdf_handler/chunker/metadata output.

HOW TO RUN:
    cd backend
    python -m tests.test_rag_full_flow
"""

from backend.rag.embeddings import generate_embedding
from backend.rag.vector_store import add_chunks, count
from backend.rag.retriever import retrieve
from backend.rag.context_builder import build_context
from backend.rag.source_tracker import get_sources, format_sources
from backend.rag.rag_pipeline import index_chunks, query_rag


# Fake chunks, shaped exactly like Member 1's build_chunks_from_pdf() output.
fake_chunks = [
    {
        "chunk_id": "demo_C0000",
        "text": "The mitochondria is the powerhouse of the cell. It produces ATP.",
        "metadata": {
            "resource_id": "demo",
            "source_type": "pdf",
            "source_name": "biology_notes.pdf",
            "page_number": 1,
            "chunk_index": 0,
            "content_type": "text",
            "word_count": 12,
            "is_ocr": False,
        },
    },
    {
        "chunk_id": "demo_C0001",
        "text": "Newton's second law states that force equals mass times acceleration.",
        "metadata": {
            "resource_id": "demo",
            "source_type": "pdf",
            "source_name": "physics_notes.pdf",
            "page_number": 5,
            "chunk_index": 1,
            "content_type": "text",
            "word_count": 11,
            "is_ocr": False,
        },
    },
]


print("=" * 60)
print("STEP 1: Testing generate_embedding()")
print("=" * 60)
vec = generate_embedding("test sentence")
print("Vector length:", len(vec))
assert len(vec) == 384, "CHECK: expected 384 dimensions for MiniLM model"
print("PASSED\n")


print("=" * 60)
print("STEP 2: Testing index_chunks() (embeds + stores fake_chunks in FAISS)")
print("=" * 60)
before = count()
index_chunks(fake_chunks)
after = count()
print(f"Vector count before: {before}, after: {after}")
assert after >= before + len(fake_chunks), "CHECK: chunks were not added"
print("PASSED\n")


print("=" * 60)
print("STEP 3: Testing query_rag() end-to-end")
print("=" * 60)
result = query_rag("What produces energy in a cell?", top_k=2)

print("\n--- Retrieved context (this goes into the LLM prompt) ---")
print(result["context"])
print("\n--- Sources (this goes in the UI) ---")
print(result["sources_text"])

# Manual check: does the top result make sense?
assert "biology_notes.pdf" in result["context"], (
    "CHECK: expected the biology chunk to be retrieved for this query. "
    "If this fails, inspect result['context'] above -- either the wrong "
    "chunk was retrieved, or top_k needs adjusting."
)
print("\nPASSED: biology chunk was correctly retrieved for a bio-related query.")

print("\nAll checks passed. Member 2's LangChain+FAISS rag/ pipeline is working correctly.")
