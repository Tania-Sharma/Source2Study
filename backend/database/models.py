from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=True)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = relationship(
        "MessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageModel.id",
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        String(64), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(16), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("ConversationModel", back_populates="messages")


class ResourceModel(Base):
    __tablename__ = "resources"

    id = Column(String(64), primary_key=True)
    source_type = Column(String(32), nullable=False)  # pdf, docx, youtube, website, image
    source_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    url = Column(String(512), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class QuestionPaperModel(Base):
    __tablename__ = "question_papers"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(32), nullable=False)
    extracted_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_text = Column(Text, nullable=False)
    normalized_text = Column(Text, index=True, nullable=False)
    subject = Column(String(128), nullable=True)
    topic = Column(String(128), nullable=True)
    question_type = Column(String(64), default="descriptive")
    marks = Column(String(32), nullable=True)
    section = Column(String(64), nullable=True)
    difficulty = Column(String(32), nullable=True)  # easy, medium, hard
    
    # review status: "unique", "pending_review", "merged_duplicate"
    status = Column(String(32), default="unique")
    canonical_parent_id = Column(String(64), ForeignKey("questions.id"), nullable=True)
    similarity_score = Column(Float, nullable=True)
    match_type = Column(String(32), nullable=True)  # exact, semantic, manual

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    occurrences = relationship(
        "OccurrenceModel",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class OccurrenceModel(Base):
    __tablename__ = "question_occurrences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(
        String(64), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    paper_id = Column(String(64), nullable=True)
    paper_name = Column(String(255), nullable=False)
    original_number = Column(String(64), nullable=True)
    original_text = Column(Text, nullable=False)
    marks = Column(String(32), nullable=True)
    section = Column(String(64), nullable=True)

    question = relationship("QuestionModel", back_populates="occurrences")
