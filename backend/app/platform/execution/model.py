"""Durable platform workflow definitions and generic runs."""

from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from app.core.db import Base


WORKFLOW_ENGINES = frozenset({"airflow", "celery"})
WORKFLOW_PUBLICATION_STATUSES = frozenset({"draft", "published", "retired"})
RUN_STATUSES = frozenset({"pending", "queued", "running", "succeeded", "failed", "cancelled"})


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_key = Column(String, nullable=False)
    version = Column(String, nullable=False)
    capability_key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    engine = Column(String, nullable=False)
    input_schema = Column(JSONB, nullable=False, default=dict)
    output_schema = Column(JSONB, nullable=False, default=dict)
    resource_requirements = Column(JSONB, nullable=False, default=dict)
    runtime_limit_seconds = Column(Integer, nullable=True)
    member_execution_allowed = Column(Boolean, nullable=False, default=False)
    artifact_types = Column(JSONB, nullable=False, default=list)
    handler_reference = Column(String, nullable=False)
    publication_status = Column(String, nullable=False, default="published")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    runs = relationship("GenericRun", back_populates="workflow_definition")

    @validates("engine")
    def validate_engine(self, _key: str, value: str) -> str:
        if value not in WORKFLOW_ENGINES:
            raise ValueError(f"Invalid workflow engine: {value}")
        return value

    @validates("publication_status")
    def validate_publication_status(self, _key: str, value: str) -> str:
        if value not in WORKFLOW_PUBLICATION_STATUSES:
            raise ValueError(f"Invalid workflow publication status: {value}")
        return value

    __table_args__ = (
        UniqueConstraint(
            "workflow_key",
            "version",
            "engine",
            name="uq_workflow_definitions_key_version_engine",
        ),
        CheckConstraint("engine IN ('airflow', 'celery')", name="ck_workflow_definitions_engine"),
        CheckConstraint(
            "publication_status IN ('draft', 'published', 'retired')",
            name="ck_workflow_definitions_publication_status",
        ),
        Index("ix_workflow_definitions_capability_key", "capability_key"),
        Index("ix_workflow_definitions_publication_status", "publication_status"),
    )


class GenericRun(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    workflow_definition_id = Column(
        UUID(as_uuid=False),
        ForeignKey("workflow_definitions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    requested_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    engine = Column(String, nullable=False)
    external_execution_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    input_snapshot = Column(JSONB, nullable=False, default=dict)
    output_summary = Column(JSONB, nullable=True)
    quota_cost = Column(Numeric(18, 6), nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    workflow_definition = relationship("WorkflowDefinition", back_populates="runs")
    project = relationship("Project", back_populates="runs")
    requester = relationship("User", back_populates="runs", foreign_keys=[requested_by])
    ingestion_run = relationship("IngestionRun", back_populates="generic_run", uselist=False)
    quota_reservation = relationship("QuotaReservation", back_populates="run", uselist=False)
    artifacts = relationship("Artifact", back_populates="run")

    @validates("engine")
    def validate_engine(self, _key: str, value: str) -> str:
        if value not in WORKFLOW_ENGINES:
            raise ValueError(f"Invalid run engine: {value}")
        return value

    @validates("status")
    def validate_status(self, _key: str, value: str) -> str:
        if value not in RUN_STATUSES:
            raise ValueError(f"Invalid run status: {value}")
        return value

    __table_args__ = (
        CheckConstraint("engine IN ('airflow', 'celery')", name="ck_runs_engine"),
        CheckConstraint(
            "status IN ('pending', 'queued', 'running', 'succeeded', 'failed', 'cancelled')",
            name="ck_runs_status",
        ),
        Index("ix_runs_project_id", "project_id"),
        Index("ix_runs_workflow_definition_id", "workflow_definition_id"),
        Index("ix_runs_requested_by", "requested_by"),
        Index("ix_runs_status", "status"),
        Index("ix_runs_created_at", "created_at"),
        Index("ix_runs_external_execution_id", "external_execution_id"),
    )
