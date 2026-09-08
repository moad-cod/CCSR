"""add research hierarchy and publication snapshots

Revision ID: 20260907_0010
Revises: 20260906_0009
Create Date: 2026-09-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260907_0010"
down_revision: Union[str, None] = "20260906_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UUID = postgresql.UUID(as_uuid=False)
JSONB = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "research_studies",
        sa.Column("id", UUID, nullable=False),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="planned"),
        sa.Column("created_by", UUID, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'active', 'completed', 'archived')",
            name="ck_research_studies_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id", "slug", name="uq_research_studies_project_slug"
        ),
    )
    op.create_index(
        "ix_research_studies_project_id", "research_studies", ["project_id"]
    )
    op.create_index("ix_research_studies_status", "research_studies", ["status"])
    op.create_index(
        "ix_research_studies_created_at", "research_studies", ["created_at"]
    )

    op.create_table(
        "research_questions",
        sa.Column("id", UUID, nullable=False),
        sa.Column("study_id", UUID, nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("ordinal >= 0", name="ck_research_questions_ordinal"),
        sa.ForeignKeyConstraint(
            ["study_id"], ["research_studies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_questions_study_id", "research_questions", ["study_id"]
    )

    op.create_table(
        "research_hypotheses",
        sa.Column("id", UUID, nullable=False),
        sa.Column("study_id", UUID, nullable=False),
        sa.Column("question_id", UUID, nullable=True),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="proposed"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "status IN ('proposed', 'supported', 'rejected', 'inconclusive')",
            name="ck_research_hypotheses_status",
        ),
        sa.ForeignKeyConstraint(
            ["study_id"], ["research_studies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["question_id"], ["research_questions.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_hypotheses_study_id", "research_hypotheses", ["study_id"]
    )
    op.create_index(
        "ix_research_hypotheses_question_id",
        "research_hypotheses",
        ["question_id"],
    )

    op.create_table(
        "experiments",
        sa.Column("id", UUID, nullable=False),
        sa.Column("study_id", UUID, nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="planned"),
        sa.Column(
            "configuration",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_by", UUID, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_experiments_status",
        ),
        sa.ForeignKeyConstraint(
            ["study_id"], ["research_studies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("study_id", "slug", name="uq_experiments_study_slug"),
    )
    op.create_index("ix_experiments_study_id", "experiments", ["study_id"])
    op.create_index("ix_experiments_status", "experiments", ["status"])
    op.create_index("ix_experiments_created_at", "experiments", ["created_at"])

    op.create_table(
        "research_datasets",
        sa.Column("id", UUID, nullable=False),
        sa.Column("study_id", UUID, nullable=False),
        sa.Column("artifact_id", UUID, nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="input"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "role IN ('input', 'reference', 'evaluation', 'output')",
            name="ck_research_datasets_role",
        ),
        sa.ForeignKeyConstraint(
            ["study_id"], ["research_studies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["artifact_id"], ["artifacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "study_id",
            "artifact_id",
            "role",
            name="uq_research_datasets_study_artifact_role",
        ),
    )
    op.create_index(
        "ix_research_datasets_study_id", "research_datasets", ["study_id"]
    )
    op.create_index(
        "ix_research_datasets_artifact_id", "research_datasets", ["artifact_id"]
    )

    op.create_table(
        "experiment_comparisons",
        sa.Column("id", UUID, nullable=False),
        sa.Column("study_id", UUID, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "criteria",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "result_summary",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("conclusion", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["study_id"], ["research_studies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_experiment_comparisons_study_id",
        "experiment_comparisons",
        ["study_id"],
    )

    op.create_table(
        "experiment_comparison_members",
        sa.Column("comparison_id", UUID, nullable=False),
        sa.Column("experiment_id", UUID, nullable=False),
        sa.ForeignKeyConstraint(
            ["comparison_id"], ["experiment_comparisons.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id"], ["experiments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("comparison_id", "experiment_id"),
    )

    op.create_table(
        "research_findings",
        sa.Column("id", UUID, nullable=False),
        sa.Column("study_id", UUID, nullable=False),
        sa.Column("experiment_id", UUID, nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("visibility", sa.String(), nullable=False, server_default="private"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'validated', 'superseded')",
            name="ck_research_findings_status",
        ),
        sa.CheckConstraint(
            "visibility IN ('private', 'public')",
            name="ck_research_findings_visibility",
        ),
        sa.ForeignKeyConstraint(
            ["study_id"], ["research_studies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id"], ["experiments.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_findings_study_id", "research_findings", ["study_id"]
    )
    op.create_index(
        "ix_research_findings_experiment_id",
        "research_findings",
        ["experiment_id"],
    )
    op.create_index(
        "ix_research_findings_visibility", "research_findings", ["visibility"]
    )

    op.add_column("runs", sa.Column("experiment_id", UUID, nullable=True))
    op.create_foreign_key(
        "fk_runs_experiment_id",
        "runs",
        "experiments",
        ["experiment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_runs_experiment_id", "runs", ["experiment_id"])

    op.add_column("artifacts", sa.Column("research_study_id", UUID, nullable=True))
    op.add_column("artifacts", sa.Column("experiment_id", UUID, nullable=True))
    op.create_foreign_key(
        "fk_artifacts_research_study_id",
        "artifacts",
        "research_studies",
        ["research_study_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_artifacts_experiment_id",
        "artifacts",
        "experiments",
        ["experiment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_artifacts_research_study_id", "artifacts", ["research_study_id"]
    )
    op.create_index("ix_artifacts_experiment_id", "artifacts", ["experiment_id"])

    op.create_table(
        "publications",
        sa.Column("id", UUID, nullable=False),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("research_study_id", UUID, nullable=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("state", sa.String(), nullable=False, server_default="private"),
        sa.Column("current_revision_number", sa.Integer(), nullable=True),
        sa.Column("created_by", UUID, nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "state IN ('private', 'draft', 'public')",
            name="ck_publications_state",
        ),
        sa.CheckConstraint(
            "current_revision_number IS NULL OR current_revision_number > 0",
            name="ck_publications_revision_number",
        ),
        sa.CheckConstraint(
            "state <> 'public' OR current_revision_number IS NOT NULL",
            name="ck_publications_public_revision",
        ),
        sa.CheckConstraint(
            "state <> 'public' OR published_at IS NOT NULL",
            name="ck_publications_public_timestamp",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["research_study_id"], ["research_studies.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_publications_slug"),
    )
    op.create_index("ix_publications_project_id", "publications", ["project_id"])
    op.create_index(
        "ix_publications_research_study_id",
        "publications",
        ["research_study_id"],
    )
    op.create_index("ix_publications_state", "publications", ["state"])
    op.create_index(
        "ix_publications_published_at", "publications", ["published_at"]
    )

    op.create_table(
        "publication_revisions",
        sa.Column("id", UUID, nullable=False),
        sa.Column("publication_id", UUID, nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("snapshot", JSONB, nullable=False),
        sa.Column("published_by", UUID, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "revision_number > 0", name="ck_publication_revisions_number"
        ),
        sa.ForeignKeyConstraint(
            ["publication_id"], ["publications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["published_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "publication_id",
            "revision_number",
            name="uq_publication_revisions_number",
        ),
    )
    op.create_index(
        "ix_publication_revisions_publication_id",
        "publication_revisions",
        ["publication_id"],
    )
    op.create_index(
        "ix_publication_revisions_created_at",
        "publication_revisions",
        ["created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION prevent_publication_revision_update()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'publication revisions are immutable';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER publication_revisions_immutable
        BEFORE UPDATE ON publication_revisions
        FOR EACH ROW EXECUTE FUNCTION prevent_publication_revision_update()
        """
    )

    op.create_table(
        "publication_findings",
        sa.Column("publication_id", UUID, nullable=False),
        sa.Column("finding_id", UUID, nullable=False),
        sa.ForeignKeyConstraint(
            ["publication_id"], ["publications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["finding_id"], ["research_findings.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("publication_id", "finding_id"),
    )
    op.create_table(
        "publication_artifacts",
        sa.Column("publication_id", UUID, nullable=False),
        sa.Column("artifact_id", UUID, nullable=False),
        sa.ForeignKeyConstraint(
            ["publication_id"], ["publications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["artifact_id"], ["artifacts.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("publication_id", "artifact_id"),
    )


def downgrade() -> None:
    op.drop_table("publication_artifacts")
    op.drop_table("publication_findings")
    op.execute(
        "DROP TRIGGER IF EXISTS publication_revisions_immutable ON publication_revisions"
    )
    op.execute("DROP FUNCTION IF EXISTS prevent_publication_revision_update()")
    op.drop_table("publication_revisions")
    op.drop_table("publications")

    op.drop_index("ix_artifacts_experiment_id", table_name="artifacts")
    op.drop_index("ix_artifacts_research_study_id", table_name="artifacts")
    op.drop_constraint(
        "fk_artifacts_experiment_id", "artifacts", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_artifacts_research_study_id", "artifacts", type_="foreignkey"
    )
    op.drop_column("artifacts", "experiment_id")
    op.drop_column("artifacts", "research_study_id")

    op.drop_index("ix_runs_experiment_id", table_name="runs")
    op.drop_constraint("fk_runs_experiment_id", "runs", type_="foreignkey")
    op.drop_column("runs", "experiment_id")

    op.drop_table("research_findings")
    op.drop_table("experiment_comparison_members")
    op.drop_table("experiment_comparisons")
    op.drop_table("research_datasets")
    op.drop_table("experiments")
    op.drop_table("research_hypotheses")
    op.drop_table("research_questions")
    op.drop_table("research_studies")
