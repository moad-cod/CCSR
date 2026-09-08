"""Publication state and immutable public snapshots."""

from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from app.core.db import Base


PUBLICATION_STATES = frozenset({"private", "draft", "public"})


publication_findings = Table(
    "publication_findings",
    Base.metadata,
    Column(
        "publication_id",
        UUID(as_uuid=False),
        ForeignKey("publications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "finding_id",
        UUID(as_uuid=False),
        ForeignKey("research_findings.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


publication_artifacts = Table(
    "publication_artifacts",
    Base.metadata,
    Column(
        "publication_id",
        UUID(as_uuid=False),
        ForeignKey("publications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artifact_id",
        UUID(as_uuid=False),
        ForeignKey("artifacts.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Publication(Base):
    __tablename__ = "publications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    research_study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="SET NULL"),
        nullable=True,
    )
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    state = Column(String, nullable=False, default="private")
    current_revision_number = Column(Integer, nullable=True)
    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    project = relationship("Project", back_populates="publications")
    research_study = relationship("ResearchStudy", back_populates="publications")
    findings = relationship("ResearchFinding", secondary=publication_findings)
    artifacts = relationship("Artifact", secondary=publication_artifacts)
    revisions = relationship(
        "PublicationRevision",
        back_populates="publication",
        cascade="all, delete-orphan",
        order_by="PublicationRevision.revision_number",
    )

    @validates("state")
    def validate_state(self, _key: str, value: str) -> str:
        if value not in PUBLICATION_STATES:
            raise ValueError(f"Invalid publication state: {value}")
        return value

    __table_args__ = (
        CheckConstraint(
            "state IN ('private', 'draft', 'public')",
            name="ck_publications_state",
        ),
        CheckConstraint(
            "current_revision_number IS NULL OR current_revision_number > 0",
            name="ck_publications_revision_number",
        ),
        CheckConstraint(
            "state <> 'public' OR current_revision_number IS NOT NULL",
            name="ck_publications_public_revision",
        ),
        CheckConstraint(
            "state <> 'public' OR published_at IS NOT NULL",
            name="ck_publications_public_timestamp",
        ),
        UniqueConstraint("slug", name="uq_publications_slug"),
        Index("ix_publications_project_id", "project_id"),
        Index("ix_publications_research_study_id", "research_study_id"),
        Index("ix_publications_state", "state"),
        Index("ix_publications_published_at", "published_at"),
    )


class PublicationRevision(Base):
    __tablename__ = "publication_revisions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    publication_id = Column(
        UUID(as_uuid=False),
        ForeignKey("publications.id", ondelete="CASCADE"),
        nullable=False,
    )
    revision_number = Column(Integer, nullable=False)
    snapshot = Column(JSONB, nullable=False)
    published_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    publication = relationship("Publication", back_populates="revisions")

    __table_args__ = (
        UniqueConstraint(
            "publication_id",
            "revision_number",
            name="uq_publication_revisions_number",
        ),
        CheckConstraint(
            "revision_number > 0",
            name="ck_publication_revisions_number",
        ),
        Index("ix_publication_revisions_publication_id", "publication_id"),
        Index("ix_publication_revisions_created_at", "created_at"),
    )
