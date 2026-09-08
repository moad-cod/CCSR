"""Durable, capability-neutral research hierarchy."""

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


STUDY_STATUSES = frozenset({"planned", "active", "completed", "archived"})
HYPOTHESIS_STATUSES = frozenset(
    {"proposed", "supported", "rejected", "inconclusive"}
)
EXPERIMENT_STATUSES = frozenset(
    {"planned", "running", "completed", "failed", "cancelled"}
)
FINDING_STATUSES = frozenset({"draft", "validated", "superseded"})
RESEARCH_VISIBILITIES = frozenset({"private", "public"})
DATASET_ROLES = frozenset({"input", "reference", "evaluation", "output"})


experiment_comparison_members = Table(
    "experiment_comparison_members",
    Base.metadata,
    Column(
        "comparison_id",
        UUID(as_uuid=False),
        ForeignKey("experiment_comparisons.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "experiment_id",
        UUID(as_uuid=False),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ResearchStudy(Base):
    __tablename__ = "research_studies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="planned")
    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    project = relationship("Project", back_populates="research_studies")
    questions = relationship(
        "ResearchQuestion",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="ResearchQuestion.ordinal",
    )
    hypotheses = relationship(
        "ResearchHypothesis",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    datasets = relationship(
        "ResearchDataset",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    experiments = relationship(
        "Experiment",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    comparisons = relationship(
        "ExperimentComparison",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    findings = relationship(
        "ResearchFinding",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    artifacts = relationship("Artifact", back_populates="research_study")
    publications = relationship("Publication", back_populates="research_study")

    @validates("status")
    def validate_status(self, _key: str, value: str) -> str:
        if value not in STUDY_STATUSES:
            raise ValueError(f"Invalid research study status: {value}")
        return value

    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_research_studies_project_slug"),
        CheckConstraint(
            "status IN ('planned', 'active', 'completed', 'archived')",
            name="ck_research_studies_status",
        ),
        Index("ix_research_studies_project_id", "project_id"),
        Index("ix_research_studies_status", "status"),
        Index("ix_research_studies_created_at", "created_at"),
    )


class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    question = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    ordinal = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    study = relationship("ResearchStudy", back_populates="questions")
    hypotheses = relationship("ResearchHypothesis", back_populates="question")

    __table_args__ = (
        CheckConstraint("ordinal >= 0", name="ck_research_questions_ordinal"),
        Index("ix_research_questions_study_id", "study_id"),
    )


class ResearchHypothesis(Base):
    __tablename__ = "research_hypotheses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_questions.id", ondelete="SET NULL"),
        nullable=True,
    )
    statement = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="proposed")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    study = relationship("ResearchStudy", back_populates="hypotheses")
    question = relationship("ResearchQuestion", back_populates="hypotheses")

    @validates("status")
    def validate_status(self, _key: str, value: str) -> str:
        if value not in HYPOTHESIS_STATUSES:
            raise ValueError(f"Invalid hypothesis status: {value}")
        return value

    __table_args__ = (
        CheckConstraint(
            "status IN ('proposed', 'supported', 'rejected', 'inconclusive')",
            name="ck_research_hypotheses_status",
        ),
        Index("ix_research_hypotheses_study_id", "study_id"),
        Index("ix_research_hypotheses_question_id", "question_id"),
    )


class ResearchDataset(Base):
    __tablename__ = "research_datasets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    artifact_id = Column(
        UUID(as_uuid=False),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String, nullable=False, default="input")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("ResearchStudy", back_populates="datasets")
    artifact = relationship("Artifact")

    @validates("role")
    def validate_role(self, _key: str, value: str) -> str:
        if value not in DATASET_ROLES:
            raise ValueError(f"Invalid research dataset role: {value}")
        return value

    __table_args__ = (
        UniqueConstraint(
            "study_id",
            "artifact_id",
            "role",
            name="uq_research_datasets_study_artifact_role",
        ),
        CheckConstraint(
            "role IN ('input', 'reference', 'evaluation', 'output')",
            name="ck_research_datasets_role",
        ),
        Index("ix_research_datasets_study_id", "study_id"),
        Index("ix_research_datasets_artifact_id", "artifact_id"),
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    slug = Column(String, nullable=False)
    name = Column(String, nullable=False)
    objective = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="planned")
    configuration = Column(JSONB, nullable=False, default=dict)
    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    study = relationship("ResearchStudy", back_populates="experiments")
    runs = relationship("GenericRun", back_populates="experiment")
    artifacts = relationship("Artifact", back_populates="experiment")
    findings = relationship("ResearchFinding", back_populates="experiment")
    comparisons = relationship(
        "ExperimentComparison",
        secondary=experiment_comparison_members,
        back_populates="experiments",
    )

    @validates("status")
    def validate_status(self, _key: str, value: str) -> str:
        if value not in EXPERIMENT_STATUSES:
            raise ValueError(f"Invalid experiment status: {value}")
        return value

    __table_args__ = (
        UniqueConstraint("study_id", "slug", name="uq_experiments_study_slug"),
        CheckConstraint(
            "status IN ('planned', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_experiments_status",
        ),
        Index("ix_experiments_study_id", "study_id"),
        Index("ix_experiments_status", "status"),
        Index("ix_experiments_created_at", "created_at"),
    )


class ExperimentComparison(Base):
    __tablename__ = "experiment_comparisons"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    criteria = Column(JSONB, nullable=False, default=dict)
    result_summary = Column(JSONB, nullable=False, default=dict)
    conclusion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    study = relationship("ResearchStudy", back_populates="comparisons")
    experiments = relationship(
        "Experiment",
        secondary=experiment_comparison_members,
        back_populates="comparisons",
    )

    __table_args__ = (Index("ix_experiment_comparisons_study_id", "study_id"),)


class ResearchFinding(Base):
    __tablename__ = "research_findings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(
        UUID(as_uuid=False),
        ForeignKey("research_studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    experiment_id = Column(
        UUID(as_uuid=False),
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = Column(String, nullable=False)
    statement = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="draft")
    visibility = Column(String, nullable=False, default="private")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    study = relationship("ResearchStudy", back_populates="findings")
    experiment = relationship("Experiment", back_populates="findings")

    @validates("status")
    def validate_status(self, _key: str, value: str) -> str:
        if value not in FINDING_STATUSES:
            raise ValueError(f"Invalid research finding status: {value}")
        return value

    @validates("visibility")
    def validate_visibility(self, _key: str, value: str) -> str:
        if value not in RESEARCH_VISIBILITIES:
            raise ValueError(f"Invalid research finding visibility: {value}")
        return value

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'validated', 'superseded')",
            name="ck_research_findings_status",
        ),
        CheckConstraint(
            "visibility IN ('private', 'public')",
            name="ck_research_findings_visibility",
        ),
        Index("ix_research_findings_study_id", "study_id"),
        Index("ix_research_findings_experiment_id", "experiment_id"),
        Index("ix_research_findings_visibility", "visibility"),
    )
