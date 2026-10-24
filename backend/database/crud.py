from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from backend.database.models import (
    ConversationModel,
    MessageModel,
    ResourceModel,
    QuestionPaperModel,
    QuestionModel,
    OccurrenceModel,
)


# ==========================================
# Chat & Conversation CRUD
# ==========================================

def create_conversation(
    db: Session,
    conversation_id: str,
    user_id: str,
    resource_id: Optional[str] = None,
    title: str = "New Conversation",
) -> ConversationModel:
    conv = ConversationModel(
        id=conversation_id,
        user_id=user_id,
        resource_id=resource_id,
        title=title,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get_conversation(db: Session, conversation_id: str) -> Optional[ConversationModel]:
    return db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()


def list_conversations(
    db: Session, user_id: Optional[str] = None
) -> List[ConversationModel]:
    query = db.query(ConversationModel)
    if user_id:
        query = query.filter(ConversationModel.user_id == user_id)
    return query.order_by(ConversationModel.updated_at.desc()).all()


def delete_conversation(db: Session, conversation_id: str) -> bool:
    conv = get_conversation(db, conversation_id)
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True


def update_conversation_title(
    db: Session, conversation_id: str, title: str
) -> Optional[ConversationModel]:
    conv = get_conversation(db, conversation_id)
    if not conv:
        return None
    conv.title = title.strip()
    conv.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(conv)
    return conv


def add_message(
    db: Session, conversation_id: str, role: str, content: str
) -> MessageModel:
    msg = MessageModel(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(msg)
    conv = get_conversation(db, conversation_id)
    if conv:
        conv.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)
    return msg


def get_conversation_messages(
    db: Session, conversation_id: str
) -> List[MessageModel]:
    return (
        db.query(MessageModel)
        .filter(MessageModel.conversation_id == conversation_id)
        .order_by(MessageModel.id.asc())
        .all()
    )


# ==========================================
# Resource CRUD
# ==========================================

def save_resource(
    db: Session,
    resource_id: str,
    source_type: str,
    source_name: str,
    file_path: Optional[str] = None,
    url: Optional[str] = None,
    metadata_json: Optional[str] = None,
) -> ResourceModel:
    res = ResourceModel(
        id=resource_id,
        source_type=source_type,
        source_name=source_name,
        file_path=file_path,
        url=url,
        metadata_json=metadata_json,
    )
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


def list_resources(db: Session) -> List[ResourceModel]:
    return db.query(ResourceModel).order_by(ResourceModel.created_at.desc()).all()


def get_resource(db: Session, resource_id: str) -> Optional[ResourceModel]:
    return db.query(ResourceModel).filter(ResourceModel.id == resource_id).first()


def delete_resource(db: Session, resource_id: str) -> bool:
    res = get_resource(db, resource_id)
    if not res:
        return False
    db.delete(res)
    db.commit()
    return True


# ==========================================
# Question Paper & Question Bank CRUD
# ==========================================

def create_question_paper(
    db: Session,
    paper_id: str,
    title: str,
    filename: str,
    file_type: str,
    extracted_count: int = 0,
) -> QuestionPaperModel:
    paper = QuestionPaperModel(
        id=paper_id,
        title=title,
        filename=filename,
        file_type=file_type,
        extracted_count=extracted_count,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper


def list_question_papers(db: Session) -> List[QuestionPaperModel]:
    return db.query(QuestionPaperModel).order_by(QuestionPaperModel.uploaded_at.desc()).all()


def create_question(
    db: Session,
    canonical_text: str,
    normalized_text: str,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    question_type: str = "descriptive",
    marks: Optional[str] = None,
    section: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: str = "unique",
    canonical_parent_id: Optional[str] = None,
    similarity_score: Optional[float] = None,
    match_type: Optional[str] = None,
) -> QuestionModel:
    q = QuestionModel(
        canonical_text=canonical_text,
        normalized_text=normalized_text,
        subject=subject,
        topic=topic,
        question_type=question_type,
        marks=marks,
        section=section,
        difficulty=difficulty,
        status=status,
        canonical_parent_id=canonical_parent_id,
        similarity_score=similarity_score,
        match_type=match_type,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def add_occurrence(
    db: Session,
    question_id: str,
    paper_name: str,
    original_text: str,
    paper_id: Optional[str] = None,
    original_number: Optional[str] = None,
    marks: Optional[str] = None,
    section: Optional[str] = None,
) -> OccurrenceModel:
    occ = OccurrenceModel(
        question_id=question_id,
        paper_id=paper_id,
        paper_name=paper_name,
        original_number=original_number,
        original_text=original_text,
        marks=marks,
        section=section,
    )
    db.add(occ)
    db.commit()
    db.refresh(occ)
    return occ


def list_questions(
    db: Session,
    status: Optional[str] = "unique",
    paper_name: Optional[str] = None,
    topic: Optional[str] = None,
    question_type: Optional[str] = None,
    search_query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[QuestionModel]:
    query = db.query(QuestionModel)

    if status:
        query = query.filter(QuestionModel.status == status)

    if topic:
        query = query.filter(QuestionModel.topic.ilike(f"%{topic}%"))

    if question_type:
        query = query.filter(QuestionModel.question_type == question_type)

    if search_query:
        query = query.filter(QuestionModel.canonical_text.ilike(f"%{search_query}%"))

    if paper_name:
        query = query.join(QuestionModel.occurrences).filter(
            OccurrenceModel.paper_name == paper_name
        )

    return query.order_by(QuestionModel.created_at.desc()).offset(skip).limit(limit).all()


def get_question_stats(db: Session) -> Dict[str, int]:
    total_occurrences = db.query(OccurrenceModel).count()
    total_papers = db.query(QuestionPaperModel).count()
    unique_questions = (
        db.query(QuestionModel).filter(QuestionModel.status == "unique").count()
    )
    pending_reviews = (
        db.query(QuestionModel).filter(QuestionModel.status == "pending_review").count()
    )
    exact_duplicates = (
        db.query(QuestionModel)
        .filter(
            QuestionModel.status == "merged_duplicate",
            QuestionModel.match_type == "exact",
        )
        .count()
    )
    semantic_duplicates = (
        db.query(QuestionModel)
        .filter(
            QuestionModel.status == "merged_duplicate",
            QuestionModel.match_type == "semantic",
        )
        .count()
    )
    merged_duplicates = (
        db.query(QuestionModel)
        .filter(QuestionModel.status == "merged_duplicate")
        .count()
    )

    return {
        "total_papers": total_papers,
        "total_extracted_questions": total_occurrences,
        "unique_questions": unique_questions,
        "exact_duplicates": exact_duplicates,
        "semantic_duplicates": semantic_duplicates,
        "merged_duplicates": merged_duplicates,
        "pending_reviews": pending_reviews,
    }


def merge_questions(
    db: Session,
    canonical_id: str,
    duplicate_ids: List[str],
    chosen_canonical_text: Optional[str] = None,
) -> Optional[QuestionModel]:
    canonical = db.query(QuestionModel).filter(QuestionModel.id == canonical_id).first()
    if not canonical:
        return None

    if chosen_canonical_text and chosen_canonical_text.strip():
        canonical.canonical_text = chosen_canonical_text.strip()

    canonical.status = "unique"

    for dup_id in duplicate_ids:
        if dup_id == canonical_id:
            continue
        dup = db.query(QuestionModel).filter(QuestionModel.id == dup_id).first()
        if not dup:
            continue

        dup.status = "merged_duplicate"
        dup.canonical_parent_id = canonical.id

        # Re-link occurrences to canonical
        for occ in dup.occurrences:
            occ.question_id = canonical.id

    db.commit()
    db.refresh(canonical)
    return canonical


def separate_question(db: Session, question_id: str) -> Optional[QuestionModel]:
    """Mark a question as distinct / unique (undo merge or review confirmation)."""
    q = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not q:
        return None

    q.status = "unique"
    q.canonical_parent_id = None
    q.similarity_score = None
    q.match_type = None

    db.commit()
    db.refresh(q)
    return q



def get_dashboard_overview_data(db: Session) -> Dict[str, Any]:
    q_stats = get_question_stats(db)
    total_resources = db.query(ResourceModel).count()
    total_conversations = db.query(ConversationModel).count()
    total_messages = db.query(MessageModel).count()

    recent_resources_models = (
        db.query(ResourceModel)
        .order_by(ResourceModel.created_at.desc())
        .limit(5)
        .all()
    )
    recent_resources = [
        {
            "id": r.id,
            "source_type": r.source_type,
            "source_name": r.source_name,
            "url": r.url,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent_resources_models
    ]

    recent_conversations_models = (
        db.query(ConversationModel)
        .order_by(ConversationModel.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_conversations = [
        {
            "conversation_id": c.id,
            "title": c.title,
            "resource_id": c.resource_id,
            "message_count": len(c.messages),
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in recent_conversations_models
    ]

    return {
        "total_resources": total_resources,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "question_stats": q_stats,
        "recent_resources": recent_resources,
        "recent_conversations": recent_conversations,
    }
