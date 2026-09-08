from datetime import datetime
import uuid

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from app.core.db import Base


ARTIFACT_VISIBILITIES = frozenset({"private", "project", "public"})
ARTIFACT_STORAGE_PROVIDERS = frozenset({"minio", "qdrant", "external"})


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    research_study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="SET NULL"),
        nullable=True,
    )
    experiment_id = Column(
        UUID(as_uuid=False),
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True,
    )
    artifact_type = Column(String, nullable=False)
    storage_provider = Column(String, nullable=False)
    storage_uri = Column(String, nullable=False)
    version = Column(String, nullable=False, default="1")
    visibility = Column(String, nullable=False, default="private")
    checksum = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    artifact_metadata = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="artifacts")
    run = relationship("GenericRun", back_populates="artifacts")
    research_study = relationship("ResearchStudy", back_populates="artifacts")
    experiment = relationship("Experiment", back_populates="artifacts")

    @validates("visibility")
    def validate_visibility(self, _key: str, value: str) -> str:
        if value not in ARTIFACT_VISIBILITIES:
            raise ValueError(f"Invalid artifact visibility: {value}")
        return value

    @validates("storage_provider")
    def validate_storage_provider(self, _key: str, value: str) -> str:
        if value not in ARTIFACT_STORAGE_PROVIDERS:
            raise ValueError(f"Invalid artifact storage provider: {value}")
        return value

    __table_args__ = (
        CheckConstraint("visibility IN ('private', 'project', 'public')", name="ck_artifacts_visibility"),
        CheckConstraint("storage_provider IN ('minio', 'qdrant', 'external')", name="ck_artifacts_storage_provider"),
        CheckConstraint("size_bytes IS NULL OR size_bytes >= 0", name="ck_artifacts_size_bytes"),
        UniqueConstraint(
            "project_id",
            "artifact_type",
            "storage_uri",
            "version",
            name="uq_artifacts_project_type_uri_version",
        ),
        Index("ix_artifacts_project_id", "project_id"),
        Index("ix_artifacts_run_id", "run_id"),
        Index("ix_artifacts_research_study_id", "research_study_id"),
        Index("ix_artifacts_experiment_id", "experiment_id"),
        Index("ix_artifacts_artifact_type", "artifact_type"),
        Index("ix_artifacts_visibility", "visibility"),
        Index("ix_artifacts_created_at", "created_at"),
    )
