import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.resource_processing.pdf_handler import extract_pdf
from backend.resource_processing.docx_handler import extract_docx
from backend.question_bank.extractor import (
    extract_questions_from_pdf_result,
    extract_questions_from_docx_result,
    extract_questions_from_text,
)
from backend.question_bank.duplicate_detector import (
    cluster_and_detect_duplicates,
    normalize_for_exact_match,
)
from backend.question_bank.exporter import export_to_csv, export_to_excel, export_to_pdf

router = APIRouter(
    prefix="/question-bank",
    tags=["Question Bank"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "papers")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class MergeRequest(BaseModel):
    canonical_id: str
    duplicate_ids: List[str]
    chosen_canonical_text: Optional[str] = None


class SeparateRequest(BaseModel):
    question_id: str


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_question_stats(db)


@router.get("/papers")
def list_papers(db: Session = Depends(get_db)):
    papers = crud.list_question_papers(db)
    return [
        {
            "id": p.id,
            "title": p.title,
            "filename": p.filename,
            "file_type": p.file_type,
            "extracted_count": p.extracted_count,
            "uploaded_at": p.uploaded_at,
        }
        for p in papers
    ]


@router.post("/upload-and-extract")
async def upload_and_extract_questions(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    all_extracted_raw = []
    processed_papers = []

    for file in files:
        filename = file.filename or "unknown_paper"
        ext = os.path.splitext(filename)[1].lower()
        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        save_path = os.path.join(UPLOAD_DIR, f"{paper_id}_{filename}")

        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        paper_questions = []

        try:
            if ext == ".pdf":
                pdf_res = extract_pdf(save_path, resource_id=paper_id)
                paper_questions = extract_questions_from_pdf_result(pdf_res)
            elif ext == ".docx":
                docx_res = extract_docx(save_path, resource_id=paper_id)
                paper_questions = extract_questions_from_docx_result(docx_res)
            elif ext in (".txt", ".md"):
                text_content = content.decode("utf-8", errors="ignore")
                paper_questions = extract_questions_from_text(
                    text_content, paper_name=filename, paper_id=paper_id
                )
            else:
                continue

            crud.create_question_paper(
                db=db,
                paper_id=paper_id,
                title=filename.rsplit(".", 1)[0],
                filename=filename,
                file_type=ext.lstrip("."),
                extracted_count=len(paper_questions),
            )

            processed_papers.append({
                "paper_id": paper_id,
                "filename": filename,
                "question_count": len(paper_questions),
            })
            all_extracted_raw.extend(paper_questions)

        except Exception as exc:
            processed_papers.append({
                "paper_id": paper_id,
                "filename": filename,
                "error": str(exc),
            })

    # Run clustering and duplicate detection
    clustering_result = cluster_and_detect_duplicates(all_extracted_raw, use_embeddings=False)

    # Persist unique questions and occurrences to DB
    for cluster in clustering_result["unique_groups"]:
        db_q = crud.create_question(
            db=db,
            canonical_text=cluster["canonical_text"],
            normalized_text=cluster["normalized_text"],
            subject=cluster.get("subject"),
            topic=cluster.get("topic"),
            marks=cluster.get("marks"),
            section=cluster.get("section"),
            status="unique",
        )
        cluster["db_id"] = db_q.id

        for occ in cluster["occurrences"]:
            crud.add_occurrence(
                db=db,
                question_id=db_q.id,
                paper_id=occ.get("paper_id"),
                paper_name=occ.get("paper_name", "Unknown Paper"),
                original_number=occ.get("original_number"),
                original_text=occ.get("original_text", cluster["canonical_text"]),
                marks=occ.get("marks"),
                section=occ.get("section"),
            )

    return {
        "status": "success",
        "processed_papers": processed_papers,
        "stats": crud.get_question_stats(db),
        "potential_duplicates": clustering_result["potential_duplicates"],
    }


@router.get("")
def get_question_bank(
    status: str = Query("unique"),
    paper_name: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    questions = crud.list_questions(
        db=db,
        status=status,
        paper_name=paper_name,
        topic=topic,
        search_query=search,
        skip=skip,
        limit=limit,
    )

    results = []
    for q in questions:
        results.append({
            "id": q.id,
            "canonical_text": q.canonical_text,
            "subject": q.subject,
            "topic": q.topic,
            "question_type": q.question_type,
            "marks": q.marks,
            "section": q.section,
            "status": q.status,
            "occurrences_count": len(q.occurrences),
            "occurrences": [
                {
                    "paper_name": o.paper_name,
                    "original_number": o.original_number,
                    "original_text": o.original_text,
                    "marks": o.marks,
                    "section": o.section,
                }
                for o in q.occurrences
            ],
            "created_at": q.created_at,
        })

    return {
        "count": len(results),
        "questions": results,
    }


@router.get("/duplicates")
def get_duplicate_review_candidates(db: Session = Depends(get_db)):
    """
    Find candidates for duplicate review among stored questions.
    """
    questions = crud.list_questions(db=db, status=None, limit=200)
    raw_list = []
    for q in questions:
        raw_list.append({
            "id": q.id,
            "cleaned_text": q.canonical_text,
            "original_text": q.canonical_text,
            "paper_name": q.occurrences[0].paper_name if q.occurrences else "Unknown",
            "marks": q.marks,
            "section": q.section,
        })

    res = cluster_and_detect_duplicates(raw_list, use_embeddings=False)
    return res["potential_duplicates"]


@router.post("/duplicates/merge")
def merge_duplicate_questions(
    request: MergeRequest,
    db: Session = Depends(get_db),
):
    merged = crud.merge_questions(
        db=db,
        canonical_id=request.canonical_id,
        duplicate_ids=request.duplicate_ids,
        chosen_canonical_text=request.chosen_canonical_text,
    )
    if not merged:
        raise HTTPException(status_code=404, detail="Canonical question not found.")

    return {
        "status": "success",
        "message": "Questions merged successfully.",
        "canonical_id": merged.id,
        "canonical_text": merged.canonical_text,
        "occurrences_count": len(merged.occurrences),
    }


@router.post("/duplicates/separate")
def separate_duplicate_question(
    request: SeparateRequest,
    db: Session = Depends(get_db),
):
    separated = crud.separate_question(db=db, question_id=request.question_id)
    if not separated:
        raise HTTPException(status_code=404, detail="Question not found.")

    return {
        "status": "success",
        "message": "Question separated and marked as distinct.",
        "question_id": separated.id,
    }


@router.get("/export")
def export_question_bank(
    format: str = Query("csv", pattern="^(csv|excel|pdf)$"),
    paper_name: Optional[str] = Query(None),
    status: str = Query("unique"),
    db: Session = Depends(get_db),
):
    questions_models = crud.list_questions(
        db=db,
        status=status,
        paper_name=paper_name,
        limit=1000,
    )

    questions_data = [
        {
            "id": q.id,
            "canonical_text": q.canonical_text,
            "topic": q.topic,
            "subject": q.subject,
            "marks": q.marks,
            "section": q.section,
            "occurrences": [
                {
                    "paper_name": o.paper_name,
                    "original_number": o.original_number,
                }
                for o in q.occurrences
            ],
        }
        for q in questions_models
    ]

    if format == "csv":
        csv_data = export_to_csv(questions_data)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="question_bank.csv"'},
        )
    elif format == "excel":
        excel_bytes = export_to_excel(questions_data)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="question_bank.xlsx"'},
        )
    elif format == "pdf":
        pdf_bytes = export_to_pdf(questions_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="question_bank.pdf"'},
        )
