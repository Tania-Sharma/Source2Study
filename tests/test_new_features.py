import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import get_db, SessionLocal
from backend.database import crud
from backend.rag.vector_store import add_chunks, search
from backend.rag.retriever import retrieve

client = TestClient(app)


def test_dashboard_overview_endpoint():
    res = client.get("/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_resources" in data
    assert "total_conversations" in data
    assert "recent_resources" in data
    assert "recent_conversations" in data
    assert "question_stats" in data


def test_conversation_create_rename_delete_flow():
    # 1. Create
    create_res = client.post(
        "/chat/conversation",
        json={"user_id": "test_user_unit", "title": "Initial Title"},
    )
    assert create_res.status_code == 200
    conv_id = create_res.json()["conversation_id"]

    # 2. Rename
    rename_res = client.patch(
        f"/chat/conversation/{conv_id}",
        json={"title": "Renamed Title"},
    )
    assert rename_res.status_code == 200
    assert rename_res.json()["title"] == "Renamed Title"

    # Verify get
    get_res = client.get(f"/chat/conversation/{conv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Renamed Title"

    # 3. Delete
    del_res = client.delete(f"/chat/conversation/{conv_id}")
    assert del_res.status_code == 200

    # 4. Verify deleted
    get_after_del = client.get(f"/chat/conversation/{conv_id}")
    assert get_after_del.status_code == 404


def test_resource_crud_and_delete_flow():
    # Save a test resource to DB
    with SessionLocal() as db:
        res_model = crud.save_resource(
            db=db,
            resource_id="res_test_delete_1",
            source_type="pdf",
            source_name="delete_me.pdf",
            file_path=None,
        )
        assert res_model.id == "res_test_delete_1"

    # Verify retrieval via API
    get_res = client.get("/resources/res_test_delete_1")
    assert get_res.status_code == 200
    assert get_res.json()["source_name"] == "delete_me.pdf"

    # Delete via API
    del_res = client.delete("/resources/res_test_delete_1")
    assert del_res.status_code == 200

    # Verify 404
    get_after = client.get("/resources/res_test_delete_1")
    assert get_after.status_code == 404


def test_answer_evaluation_endpoint():
    payload = {
        "question": "What is overfitting in machine learning?",
        "student_answer": "Overfitting happens when a machine learning model learns the training data and noise too well, causing poor generalization on unseen test data.",
    }
    res = client.post("/ai/evaluate-answer", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "verdict" in data
    assert "feedback" in data
    assert "strengths" in data
    assert "improvements" in data
    assert "ideal_answer" in data
    assert data["max_score"] == 10
    assert data["score"] >= 1


def test_answer_evaluation_empty_validation():
    payload = {
        "question": "Explain recursion",
        "student_answer": "   ",
    }
    res = client.post("/ai/evaluate-answer", json=payload)
    assert res.status_code == 400


def test_retriever_resource_id_filtering():
    chunks = [
        {
            "chunk_id": "test_filter_resA_1",
            "text": "Alpha resource contains unique concept X777.",
            "metadata": {"resource_id": "res_A", "source_name": "alpha.pdf"},
        },
        {
            "chunk_id": "test_filter_resB_1",
            "text": "Beta resource contains unique concept Y888.",
            "metadata": {"resource_id": "res_B", "source_name": "beta.pdf"},
        },
    ]
    add_chunks(chunks)

    # Search with resource_id filter for res_A
    results_a = retrieve("concept", top_k=5, resource_id="res_A")
    for r in results_a:
        assert r["metadata"].get("resource_id") == "res_A"

    # Search with resource_id filter for res_B
    results_b = retrieve("concept", top_k=5, resource_id="res_B")
    for r in results_b:
        assert r["metadata"].get("resource_id") == "res_B"
