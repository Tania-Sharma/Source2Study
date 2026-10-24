import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.question_bank.normalizer import (
    normalize_for_exact_match,
    normalize_for_semantic_match,
    check_safeguards_allow_merge,
)
from backend.question_bank.extractor import extract_questions_from_text
from backend.question_bank.duplicate_detector import (
    calculate_question_similarity,
    cluster_and_detect_duplicates,
)
from backend.question_bank.exporter import (
    export_to_csv,
    export_to_excel,
    export_to_pdf,
)
from backend.database.db import SessionLocal, init_db
from backend.database import crud

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_exact_normalization_punctuation_and_whitespace():
    q1 = "1. What is Machine Learning?  [5 Marks]"
    q2 = "what is machine learning"
    q3 = "What is machine learning???"
    q4 = "   Q.1:   What is    machine learning?   "

    n1 = normalize_for_exact_match(q1)
    n2 = normalize_for_exact_match(q2)
    n3 = normalize_for_exact_match(q3)
    n4 = normalize_for_exact_match(q4)

    assert n1 == n2 == n3 == n4 == "what is machine learning"


def test_semantic_concept_normalization():
    q1 = "Define artificial intelligence."
    q2 = "What do you mean by artificial intelligence?"
    q3 = "Explain the concept of artificial intelligence."

    s1 = normalize_for_semantic_match(q1)
    s2 = normalize_for_semantic_match(q2)
    s3 = normalize_for_semantic_match(q3)

    assert s1 == s2 == s3 == "artificial intelligence"


def test_safeguards_numeric_differences():
    # Questions with different counts should NOT merge
    q1 = "Explain 3 types of machine learning algorithms."
    q2 = "Explain 5 types of machine learning algorithms."

    safe, reason = check_safeguards_allow_merge(q1, q2)
    assert safe is False
    assert "Different numeric values" in reason

    score, match_type = calculate_question_similarity(q1, q2)
    assert score == 0.0
    assert "safeguard_blocked" in match_type


def test_safeguards_negation_and_limitations():
    # Questions with negation / limitation differences should NOT merge
    q1 = "What are the advantages of cloud computing?"
    q2 = "What are the disadvantages of cloud computing?"

    safe, reason = check_safeguards_allow_merge(q1, q2)
    assert safe is False
    assert "Difference in negative/limitation words" in reason


def test_extract_questions_from_text():
    paper_text = """
    COMPUTER SCIENCE DEPARTMENT
    Time: 3 Hours
    Max Marks: 100

    SECTION A
    1. What is supervised learning? [5 Marks]
    2. Explain overfitting in detail. (10)
    3. State Bayes theorem. [2M]

    SECTION B
    4. Describe convolutional neural networks.
    5. What is gradient descent?
    """

    questions = extract_questions_from_text(paper_text, paper_name="Paper_2024.pdf")
    assert len(questions) == 5

    assert questions[0]["original_number"] == "1."
    assert questions[0]["cleaned_text"] == "What is supervised learning?"
    assert questions[0]["marks"] == "5 Marks"
    assert questions[0]["section"] == "Section A"

    assert questions[1]["cleaned_text"] == "Explain overfitting in detail."
    assert questions[1]["marks"] == "10"

    assert questions[3]["section"] == "Section B"


def test_extract_empty_or_no_questions():
    empty = extract_questions_from_text("")
    assert empty == []

    header_only = """
    Department of Engineering
    Instructions: All questions are compulsory.
    Time Allowed: 3 hours.
    """
    assert extract_questions_from_text(header_only) == []


def test_five_papers_duplicate_detection_scenario():
    # User scenario from prompt:
    # Paper 1: What is machine learning?, Explain supervised learning., Define overfitting.
    # Paper 2: Define overfitting., What is deep learning?, What is machine learning?
    # Paper 3: Explain supervised learning., Describe neural networks.
    # Expected unique:
    # 1. What is machine learning?
    # 2. Explain supervised learning.
    # 3. Define overfitting.
    # 4. What is deep learning?
    # 5. Describe neural networks.

    all_questions = [
        # Paper 1
        {"cleaned_text": "What is machine learning?", "original_text": "1. What is machine learning?", "original_number": "1", "paper_name": "Paper 1"},
        {"cleaned_text": "Explain supervised learning.", "original_text": "2. Explain supervised learning.", "original_number": "2", "paper_name": "Paper 1"},
        {"cleaned_text": "Define overfitting.", "original_text": "3. Define overfitting.", "original_number": "3", "paper_name": "Paper 1"},
        # Paper 2
        {"cleaned_text": "Define overfitting.", "original_text": "1. Define overfitting.", "original_number": "1", "paper_name": "Paper 2"},
        {"cleaned_text": "What is deep learning?", "original_text": "2. What is deep learning?", "original_number": "2", "paper_name": "Paper 2"},
        {"cleaned_text": "What is machine learning?", "original_text": "3. What is machine learning?", "original_number": "3", "paper_name": "Paper 2"},
        # Paper 3
        {"cleaned_text": "Explain supervised learning.", "original_text": "1. Explain supervised learning.", "original_number": "1", "paper_name": "Paper 3"},
        {"cleaned_text": "Describe neural networks.", "original_text": "2. Describe neural networks.", "original_number": "2", "paper_name": "Paper 3"},
    ]

    res = cluster_and_detect_duplicates(all_questions, use_embeddings=False)

    stats = res["stats"]
    assert stats["total_extracted"] == 8
    assert stats["exact_duplicates"] == 3
    assert stats["unique_count"] == 5

    unique_texts = {group["canonical_text"] for group in res["unique_groups"]}
    expected_texts = {
        "What is machine learning?",
        "Explain supervised learning.",
        "Define overfitting.",
        "What is deep learning?",
        "Describe neural networks.",
    }
    assert unique_texts == expected_texts

    # Check occurrence tracking for "What is machine learning?"
    ml_group = next(g for g in res["unique_groups"] if g["canonical_text"] == "What is machine learning?")
    assert len(ml_group["occurrences"]) == 2
    paper_names = {occ["paper_name"] for occ in ml_group["occurrences"]}
    assert paper_names == {"Paper 1", "Paper 2"}


def test_database_crud_merge_and_separate():
    with SessionLocal() as db:
        # Create canonical question
        q1 = crud.create_question(
            db=db,
            canonical_text="Define artificial intelligence.",
            normalized_text="define artificial intelligence",
        )
        crud.add_occurrence(db=db, question_id=q1.id, paper_name="Paper 2021", original_text="Define artificial intelligence.")

        # Create duplicate candidate
        q2 = crud.create_question(
            db=db,
            canonical_text="What is artificial intelligence?",
            normalized_text="what is artificial intelligence",
            status="pending_review",
        )
        crud.add_occurrence(db=db, question_id=q2.id, paper_name="Paper 2022", original_text="What is artificial intelligence?")

        # Merge q2 into q1
        merged = crud.merge_questions(
            db=db,
            canonical_id=q1.id,
            duplicate_ids=[q2.id],
            chosen_canonical_text="Define artificial intelligence (Canonical).",
        )
        assert merged is not None
        assert merged.canonical_text == "Define artificial intelligence (Canonical)."
        assert len(merged.occurrences) == 2

        # Verify q2 is now merged_duplicate
        q2_refreshed = db.query(crud.QuestionModel).filter_by(id=q2.id).first()
        assert q2_refreshed.status == "merged_duplicate"
        assert q2_refreshed.canonical_parent_id == q1.id

        # Separate / Undo merge
        separated = crud.separate_question(db=db, question_id=q2.id)
        assert separated.status == "unique"
        assert separated.canonical_parent_id is None


def test_export_formats():
    sample_questions = [
        {
            "id": "q1",
            "canonical_text": "What is reinforcement learning?",
            "topic": "Machine Learning",
            "marks": "5",
            "section": "Section A",
            "occurrences": [
                {"paper_name": "Midterm 2023.pdf", "original_number": "Q1"},
                {"paper_name": "Final 2024.pdf", "original_number": "Q3"},
            ],
        }
    ]

    csv_out = export_to_csv(sample_questions)
    assert "What is reinforcement learning?" in csv_out
    assert "Midterm 2023.pdf" in csv_out

    excel_bytes = export_to_excel(sample_questions)
    assert len(excel_bytes) > 100
    assert excel_bytes[:2] == b"PK"  # zip header for xlsx

    pdf_bytes = export_to_pdf(sample_questions)
    assert len(pdf_bytes) > 100
    assert pdf_bytes[:4] == b"%PDF"


def test_api_upload_and_extract_flow():
    test_paper = b"""
    MIDTERM EXAM 2025
    1. Define recursion in computer science. [5 Marks]
    2. What is a binary search tree? (10 Marks)
    """

    files = [
        ("files", ("exam1.txt", io.BytesIO(test_paper), "text/plain")),
    ]

    response = client.post("/question-bank/upload-and-extract", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["stats"]["total_extracted_questions"] >= 2

    # Query question bank
    res_bank = client.get("/question-bank")
    assert res_bank.status_code == 200
    bank_data = res_bank.json()
    assert bank_data["count"] >= 2
    q_texts = [q["canonical_text"] for q in bank_data["questions"]]
    assert any("recursion" in t.lower() for t in q_texts)

    # Test export endpoint
    res_export = client.get("/question-bank/export?format=csv")
    assert res_export.status_code == 200
    assert "text/csv" in res_export.headers.get("content-type", "")
    assert "recursion" in res_export.text.lower()
