import os
import uuid
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.resource_processing.pdf_handler import extract_pdf
from backend.resource_processing.docx_handler import extract_docx
from backend.resource_processing.image_handler import extract_image
from backend.resource_processing.youtube_handler import extract_youtube
from backend.resource_processing.web_handler import extract_web_content
from backend.text_processing.metadata import (
    build_chunks_from_pdf,
    build_chunks_from_docx,
    build_chunks_from_image,
    build_chunks_from_youtube,
    build_chunks_from_web,
)
from backend.rag.rag_pipeline import index_chunks

router = APIRouter(
    prefix="/resources",
    tags=["Resources"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class YoutubeResourceRequest(BaseModel):
    url: str = Field(min_length=1)


class WebResourceRequest(BaseModel):
    url: str = Field(min_length=1)


@router.get("")
def list_all_resources(db: Session = Depends(get_db)):
    resources = crud.list_resources(db)
    return [
        {
            "id": r.id,
            "source_type": r.source_type,
            "source_name": r.source_name,
            "url": r.url,
            "created_at": r.created_at,
        }
        for r in resources
    ]


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    results = []

    for file in files:
        filename = file.filename or "unknown_file"
        ext = os.path.splitext(filename)[1].lower()
        resource_id = f"res_{uuid.uuid4().hex[:8]}"

        save_path = os.path.join(UPLOAD_DIR, f"{resource_id}_{filename}")
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        chunks = []
        source_type = "unknown"

        try:
            if ext == ".pdf":
                source_type = "pdf"
                pdf_res = extract_pdf(save_path, resource_id=resource_id)
                chunks = build_chunks_from_pdf(pdf_res)
            elif ext == ".docx":
                source_type = "docx"
                docx_res = extract_docx(save_path, resource_id=resource_id)
                chunks = build_chunks_from_docx(docx_res)
            elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
                source_type = "image"
                img_res = extract_image(save_path, resource_id=resource_id)
                chunks = build_chunks_from_image(img_res)
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            if chunks:
                index_chunks(chunks)

            crud.save_resource(
                db=db,
                resource_id=resource_id,
                source_type=source_type,
                source_name=filename,
                file_path=save_path,
            )

            results.append({
                "resource_id": resource_id,
                "filename": filename,
                "source_type": source_type,
                "chunk_count": len(chunks),
                "status": "success",
            })

        except Exception as exc:
            results.append({
                "filename": filename,
                "status": "error",
                "error": str(exc),
            })

    return {"processed": results}


@router.post("/youtube")
def add_youtube_resource(
    request: YoutubeResourceRequest,
    db: Session = Depends(get_db),
):
    try:
        resource_id = f"res_yt_{uuid.uuid4().hex[:8]}"
        yt_res = extract_youtube(request.url, resource_id=resource_id)
        chunks = build_chunks_from_youtube(yt_res)

        if chunks:
            index_chunks(chunks)

        crud.save_resource(
            db=db,
            resource_id=resource_id,
            source_type="youtube",
            source_name=yt_res["source_name"],
            url=request.url,
        )

        return {
            "resource_id": resource_id,
            "source_type": "youtube",
            "source_name": yt_res["source_name"],
            "chunk_count": len(chunks),
            "status": "success",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/web")
def add_web_resource(
    request: WebResourceRequest,
    db: Session = Depends(get_db),
):
    try:
        resource_id = f"res_web_{uuid.uuid4().hex[:8]}"
        web_res = extract_web_content(request.url, resource_id=resource_id)
        chunks = build_chunks_from_web(web_res)

        if chunks:
            index_chunks(chunks)

        crud.save_resource(
            db=db,
            resource_id=resource_id,
            source_type="website",
            source_name=web_res["source_name"],
            url=request.url,
        )

        return {
            "resource_id": resource_id,
            "source_type": "website",
            "source_name": web_res["source_name"],
            "chunk_count": len(chunks),
            "status": "success",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Return comprehensive system & learning overview stats."""
    return crud.get_dashboard_overview_data(db)


@router.get("/item/{resource_id}")
@router.get("/{resource_id}")
def get_resource_details(resource_id: str, db: Session = Depends(get_db)):
    """Get single resource by id."""
    r = crud.get_resource(db, resource_id)
    if not r:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {
        "id": r.id,
        "source_type": r.source_type,
        "source_name": r.source_name,
        "url": r.url,
        "created_at": r.created_at,
    }


@router.delete("/{resource_id}")
def delete_resource_by_id(resource_id: str, db: Session = Depends(get_db)):
    """Delete a resource from database and remove its uploaded file if present."""
    r = crud.get_resource(db, resource_id)
    if not r:
        raise HTTPException(status_code=404, detail="Resource not found")
    if r.file_path and os.path.exists(r.file_path):
        try:
            os.remove(r.file_path)
        except Exception:
            pass

    deleted = crud.delete_resource(db, resource_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete resource")

    return {
        "status": "success",
        "message": f"Resource {resource_id} deleted successfully."
    }
