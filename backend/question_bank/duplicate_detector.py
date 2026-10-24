import math
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

from backend.question_bank.normalizer import (
    normalize_for_exact_match,
    normalize_for_semantic_match,
    check_safeguards_allow_merge,
)

# Optional embedding support using project's SentenceTransformer
try:
    from backend.rag.embeddings import generate_embeddings
    _HAS_EMBEDDINGS = True
except Exception:
    _HAS_EMBEDDINGS = False


EXACT_THRESHOLD = 0.98
SEMANTIC_THRESHOLD = 0.84


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two numeric vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def string_similarity(s1: str, s2: str) -> float:
    """Fallback text similarity using SequenceMatcher."""
    return SequenceMatcher(None, s1, s2).ratio()


def calculate_question_similarity(
    q1_text: str,
    q2_text: str,
    emb1: List[float] | None = None,
    emb2: List[float] | None = None,
) -> Tuple[float, str]:
    """
    Compute similarity between two questions, checking safeguards.

    Returns:
        (score: float, match_type: str) where match_type is 'exact', 'semantic', or 'distinct'
    """
    n1_exact = normalize_for_exact_match(q1_text)
    n2_exact = normalize_for_exact_match(q2_text)

    # 1. Exact match check
    if n1_exact and n1_exact == n2_exact:
        return 1.0, "exact"

    # 2. Check safeguards
    safe, reason = check_safeguards_allow_merge(q1_text, q2_text)
    if not safe:
        return 0.0, f"safeguard_blocked: {reason}"

    # 3. Normalized semantic concept check
    n1_sem = normalize_for_semantic_match(q1_text)
    n2_sem = normalize_for_semantic_match(q2_text)
    if n1_sem and n1_sem == n2_sem:
        return 0.95, "semantic"

    # 4. Vector embedding similarity if embeddings available
    sim_score = 0.0
    if emb1 is not None and emb2 is not None:
        sim_score = float(cosine_similarity(emb1, emb2))
    else:
        # Fallback to fuzzy text similarity on normalized text
        sim_score = float(string_similarity(n1_sem, n2_sem))

    if sim_score >= EXACT_THRESHOLD:
        return sim_score, "exact"
    elif sim_score >= SEMANTIC_THRESHOLD:
        return sim_score, "semantic"
    else:
        return sim_score, "distinct"


def cluster_and_detect_duplicates(
    questions: List[Dict[str, Any]],
    use_embeddings: bool = True,
) -> Dict[str, Any]:
    """
    Group extracted questions across papers into canonical unique questions,
    exact duplicates, and review-required potential duplicates.

    Args:
        questions: List of extracted questions with 'original_text', 'paper_name', 'marks', etc.
        use_embeddings: Whether to use sentence embeddings for semantic detection.

    Returns:
        dict: {
            "unique_groups": list of merged questions with occurrences,
            "potential_duplicates": list of candidate pairs needing user review,
            "stats": {
                "total_extracted": int,
                "exact_duplicates": int,
                "semantic_duplicates": int,
                "unique_count": int,
                "pending_review_count": int
            }
        }
    """
    if not questions:
        return {
            "unique_groups": [],
            "potential_duplicates": [],
            "stats": {
                "total_extracted": 0,
                "exact_duplicates": 0,
                "semantic_duplicates": 0,
                "unique_count": 0,
                "pending_review_count": 0,
            },
        }

    # Precompute embeddings if requested
    embeddings = []
    if use_embeddings and _HAS_EMBEDDINGS:
        try:
            texts_to_embed = [q["cleaned_text"] for q in questions]
            embeddings = generate_embeddings(texts_to_embed)
        except Exception:
            embeddings = [None] * len(questions)
    else:
        embeddings = [None] * len(questions)

    # First pass: identify exact duplicates and cluster
    clusters: List[Dict[str, Any]] = []
    # cluster structure:
    # {
    #    "canonical_text": str,
    #    "normalized_text": str,
    #    "embedding": list[float],
    #    "occurrences": list[dict],
    #    "status": "unique" | "merged_duplicate" | "pending_review",
    #    "similarity_score": float,
    #    "match_type": str
    # }

    exact_dup_count = 0

    for idx, q in enumerate(questions):
        q_text = q["cleaned_text"]
        n_exact = normalize_for_exact_match(q_text)
        emb = embeddings[idx] if idx < len(embeddings) else None

        matched_cluster = None
        for cluster in clusters:
            if cluster["normalized_text"] == n_exact:
                matched_cluster = cluster
                break

        occ_info = {
            "paper_name": q.get("paper_name", "Unknown Paper"),
            "paper_id": q.get("paper_id"),
            "original_number": q.get("original_number"),
            "original_text": q.get("original_text", q_text),
            "marks": q.get("marks"),
            "section": q.get("section"),
        }

        if matched_cluster:
            matched_cluster["occurrences"].append(occ_info)
            exact_dup_count += 1
        else:
            clusters.append({
                "id": f"q_{len(clusters) + 1}",
                "canonical_text": q_text,
                "normalized_text": n_exact,
                "embedding": emb,
                "occurrences": [occ_info],
                "status": "unique",
                "similarity_score": 1.0,
                "match_type": None,
                "subject": q.get("subject"),
                "topic": q.get("topic"),
                "marks": q.get("marks"),
                "section": q.get("section"),
            })

    # Second pass: check semantic similarity between clusters
    potential_duplicates = []
    semantic_dup_count = 0

    # Compare pairs
    n_clusters = len(clusters)
    for i in range(n_clusters):
        for j in range(i + 1, n_clusters):
            c1 = clusters[i]
            c2 = clusters[j]

            score, match_type = calculate_question_similarity(
                c1["canonical_text"],
                c2["canonical_text"],
                c1["embedding"],
                c2["embedding"],
            )

            if match_type == "semantic" or score >= SEMANTIC_THRESHOLD:
                potential_duplicates.append({
                    "id": f"rev_{len(potential_duplicates) + 1}",
                    "question_1": {
                        "id": c1["id"],
                        "text": c1["canonical_text"],
                        "paper_name": c1["occurrences"][0]["paper_name"],
                        "occurrences": c1["occurrences"],
                    },
                    "question_2": {
                        "id": c2["id"],
                        "text": c2["canonical_text"],
                        "paper_name": c2["occurrences"][0]["paper_name"],
                        "occurrences": c2["occurrences"],
                    },
                    "similarity_score": round(score, 3),
                    "match_type": match_type,
                    "confidence": "high" if score >= 0.90 else "medium",
                })
                semantic_dup_count += 1

    return {
        "unique_groups": clusters,
        "potential_duplicates": potential_duplicates,
        "stats": {
            "total_extracted": len(questions),
            "exact_duplicates": exact_dup_count,
            "semantic_duplicates": semantic_dup_count,
            "unique_count": len(clusters),
            "pending_review_count": len(potential_duplicates),
        },
    }
