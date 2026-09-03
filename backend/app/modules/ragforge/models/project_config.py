from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from app.core.db import Base


DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_SPARSE_MODEL = "Qdrant/bm25"
DEFAULT_CHUNKER = "paragraph"
DEFAULT_RETRIEVAL_CONFIGURATION = {
    "strategy": "hybrid",
    "top_k": 5,
    "fetch_k": 30,
    "use_rerank": True,
}


class RAGProjectConfig(Base):
    __tablename__ = "rag_project_configs"

    project_id = Column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    qdrant_collection = Column(String, unique=True, nullable=False)
    embedding_model = Column(
        String,
        default=DEFAULT_EMBEDDING_MODEL,
        server_default=DEFAULT_EMBEDDING_MODEL,
        nullable=False,
    )
    sparse_model = Column(
        String,
        default=DEFAULT_SPARSE_MODEL,
        server_default=DEFAULT_SPARSE_MODEL,
        nullable=False,
    )
    default_chunker = Column(
        String,
        default=DEFAULT_CHUNKER,
        server_default=DEFAULT_CHUNKER,
        nullable=False,
    )
    retrieval_configuration = Column(
        MutableDict.as_mutable(JSONB),
        default=lambda: dict(DEFAULT_RETRIEVAL_CONFIGURATION),
        nullable=False,
        server_default=text(
            "'{\"strategy\": \"hybrid\", \"top_k\": 5, "
            "\"fetch_k\": 30, \"use_rerank\": true}'::jsonb"
        ),
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    project = relationship("Project", back_populates="rag_config")
