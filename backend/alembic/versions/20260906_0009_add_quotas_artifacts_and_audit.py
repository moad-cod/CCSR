"""add quotas artifacts and audit

Revision ID: 20260906_0009
Revises: 20260905_0008
Create Date: 2026-09-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260906_0009"
down_revision: Union[str, None] = "20260905_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("runs", sa.Column("error_code", sa.String(), nullable=True))
    op.execute(
        """
        UPDATE workflow_definitions
        SET member_execution_allowed = TRUE,
            input_schema = '{"type":"object","properties":{"ingestion_run_id":{"type":"string"},"input_size_bytes":{"anyOf":[{"type":"integer","minimum":0},{"type":"null"}],"default":null}},"required":["ingestion_run_id"]}'::jsonb,
            updated_at = CURRENT_TIMESTAMP
        WHERE workflow_key = 'ragforge.ingest_document' AND version = '1.0.0'
        """
    )
    op.execute(
        """
        UPDATE runs
        SET error_code = CASE
                WHEN lower(COALESCE(error_message, '')) LIKE '%timeout%' THEN 'execution_timeout'
                WHEN lower(COALESCE(error_message, '')) LIKE '%quota%' OR lower(COALESCE(error_message, '')) LIKE '%rate limit%' THEN 'provider_unavailable'
                WHEN lower(COALESCE(error_message, '')) LIKE '%no indexable%' THEN 'input_not_processable'
                WHEN lower(COALESCE(error_message, '')) LIKE '%orchestration%' OR lower(COALESCE(error_message, '')) LIKE '%execution engine%' THEN 'dispatch_failed'
                ELSE 'workflow_failed'
            END,
            error_message = CASE
                WHEN lower(COALESCE(error_message, '')) LIKE '%timeout%' THEN 'The workflow exceeded its allowed runtime.'
                WHEN lower(COALESCE(error_message, '')) LIKE '%quota%' OR lower(COALESCE(error_message, '')) LIKE '%rate limit%' THEN 'A required provider is temporarily unavailable.'
                WHEN lower(COALESCE(error_message, '')) LIKE '%no indexable%' THEN 'The workflow could not process the supplied input.'
                WHEN lower(COALESCE(error_message, '')) LIKE '%orchestration%' OR lower(COALESCE(error_message, '')) LIKE '%execution engine%' THEN 'The execution engine could not start the workflow.'
                ELSE 'The workflow could not be completed.'
            END
        WHERE status = 'failed'
        """
    )

    op.create_table(
        "quota_policies",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("daily_run_limit", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("monthly_run_limit", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("concurrent_run_limit", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("max_runtime_seconds", sa.Integer(), nullable=True),
        sa.Column("max_input_bytes", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("daily_run_limit >= 0", name="ck_quota_policies_daily_limit"),
        sa.CheckConstraint("monthly_run_limit >= 0", name="ck_quota_policies_monthly_limit"),
        sa.CheckConstraint("concurrent_run_limit >= 0", name="ck_quota_policies_concurrent_limit"),
        sa.CheckConstraint("max_runtime_seconds IS NULL OR max_runtime_seconds > 0", name="ck_quota_policies_runtime"),
        sa.CheckConstraint("max_input_bytes IS NULL OR max_input_bytes > 0", name="ck_quota_policies_input_bytes"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_quota_policies_user_id"),
    )
    op.create_index("ix_quota_policies_user_id", "quota_policies", ["user_id"])

    op.create_table(
        "quota_reservations",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("quota_policy_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="reserved"),
        sa.Column("reserved_units", sa.Numeric(18, 6), nullable=False, server_default="1"),
        sa.Column("actual_units", sa.Numeric(18, 6), nullable=True),
        sa.Column("period_day", sa.Date(), nullable=False),
        sa.Column("period_month", sa.Date(), nullable=False),
        sa.Column("reserved_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("finalized_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("status IN ('reserved', 'finalized', 'released')", name="ck_quota_reservations_status"),
        sa.CheckConstraint("reserved_units >= 0", name="ck_quota_reservations_reserved_units"),
        sa.CheckConstraint("actual_units IS NULL OR actual_units >= 0", name="ck_quota_reservations_actual_units"),
        sa.ForeignKeyConstraint(["quota_policy_id"], ["quota_policies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", name="uq_quota_reservations_run_id"),
    )
    for column in ("quota_policy_id", "status", "period_day", "period_month"):
        op.create_index(f"ix_quota_reservations_{column}", "quota_reservations", [column])

    op.create_table(
        "artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("artifact_type", sa.String(), nullable=False),
        sa.Column("storage_provider", sa.String(), nullable=False),
        sa.Column("storage_uri", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False, server_default="1"),
        sa.Column("visibility", sa.String(), nullable=False, server_default="private"),
        sa.Column("checksum", sa.String(), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("visibility IN ('private', 'project', 'public')", name="ck_artifacts_visibility"),
        sa.CheckConstraint("storage_provider IN ('minio', 'qdrant', 'external')", name="ck_artifacts_storage_provider"),
        sa.CheckConstraint("size_bytes IS NULL OR size_bytes >= 0", name="ck_artifacts_size_bytes"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "artifact_type",
            "storage_uri",
            "version",
            name="uq_artifacts_project_type_uri_version",
        ),
    )
    for column in ("project_id", "run_id", "artifact_type", "visibility", "created_at"):
        op.create_index(f"ix_artifacts_{column}", "artifacts", [column])

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("actor_global_role", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_type", sa.String(), nullable=False),
        sa.Column("target_id", sa.String(), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("outcome", sa.String(), nullable=False, server_default="success"),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("outcome IN ('success', 'denied', 'failure')", name="ck_audit_events_outcome"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("actor_user_id", "project_id", "action", "created_at"):
        op.create_index(f"ix_audit_events_{column}", "audit_events", [column])

    op.execute(
        """
        INSERT INTO quota_policies (id, user_id, daily_run_limit, monthly_run_limit, concurrent_run_limit)
        SELECT id, id, 100, 1000, 4 FROM users
        ON CONFLICT (user_id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quota_reservations (
            id, quota_policy_id, run_id, status, reserved_units, actual_units,
            period_day, period_month, reserved_at, finalized_at
        )
        SELECT
            r.id, r.requested_by, r.id,
            CASE WHEN r.status IN ('pending', 'queued', 'running') THEN 'reserved' ELSE 'finalized' END,
            1, CASE WHEN r.status IN ('pending', 'queued', 'running') THEN NULL ELSE r.quota_cost END,
            r.created_at::date, date_trunc('month', r.created_at)::date,
            r.created_at,
            CASE WHEN r.status IN ('pending', 'queued', 'running') THEN NULL ELSE COALESCE(r.completed_at, r.updated_at) END
        FROM runs r
        ON CONFLICT (run_id) DO NOTHING
        """
    )
    op.execute(
        """
        WITH candidates AS (
            SELECT ir.generic_run_id AS run_id, ir.project_id, ir.created_by,
                   dv.id AS document_version_id, dv.document_id, dv.version_number,
                   dv.content_hash, dv.bronze_path AS path, 'rag-bronze' AS kind
            FROM ingestion_runs ir JOIN document_versions dv ON dv.id = ir.document_version_id
            WHERE dv.bronze_path IS NOT NULL
            UNION ALL
            SELECT ir.generic_run_id, ir.project_id, ir.created_by,
                   dv.id, dv.document_id, dv.version_number,
                   NULL, dv.silver_path, 'rag-silver'
            FROM ingestion_runs ir JOIN document_versions dv ON dv.id = ir.document_version_id
            WHERE dv.silver_path IS NOT NULL
            UNION ALL
            SELECT ir.generic_run_id, ir.project_id, ir.created_by,
                   dv.id, dv.document_id, dv.version_number,
                   NULL, dv.gold_path, 'rag-gold'
            FROM ingestion_runs ir JOIN document_versions dv ON dv.id = ir.document_version_id
            WHERE dv.gold_path IS NOT NULL
        ), identified AS (
            SELECT *, md5(run_id::text || ':' || kind || ':' || path) AS digest FROM candidates
        )
        INSERT INTO artifacts (
            id, project_id, run_id, artifact_type, storage_provider, storage_uri,
            version, visibility, checksum, created_by, metadata, created_at
        )
        SELECT
            (substr(digest,1,8)||'-'||substr(digest,9,4)||'-'||substr(digest,13,4)||'-'||substr(digest,17,4)||'-'||substr(digest,21,12))::uuid,
            project_id, run_id, kind, 'minio', 'minio://' || path,
            version_number::text, 'private', content_hash, created_by,
            jsonb_build_object('document_id', document_id::text, 'document_version_id', document_version_id::text),
            CURRENT_TIMESTAMP
        FROM identified
        ON CONFLICT (project_id, artifact_type, storage_uri, version) DO NOTHING
        """
    )
    op.execute(
        """
        WITH candidates AS (
            SELECT ir.generic_run_id AS run_id, ir.project_id, ir.created_by,
                   dv.id AS document_version_id, dv.document_id, dv.version_number,
                   md5(ir.generic_run_id::text || ':qdrant-index:' || dv.id::text) AS digest
            FROM ingestion_runs ir
            JOIN document_versions dv ON dv.id = ir.document_version_id
            WHERE ir.status = 'indexed' AND ir.generic_run_id IS NOT NULL
        )
        INSERT INTO artifacts (
            id, project_id, run_id, artifact_type, storage_provider, storage_uri,
            version, visibility, created_by, metadata, created_at
        )
        SELECT
            (substr(digest,1,8)||'-'||substr(digest,9,4)||'-'||substr(digest,13,4)||'-'||substr(digest,17,4)||'-'||substr(digest,21,12))::uuid,
            project_id, run_id, 'qdrant-index', 'qdrant',
            'qdrant://project/' || project_id::text || '/document-version/' || document_version_id::text,
            version_number::text, 'private', created_by,
            jsonb_build_object('document_id', document_id::text, 'document_version_id', document_version_id::text),
            CURRENT_TIMESTAMP
        FROM candidates
        ON CONFLICT (project_id, artifact_type, storage_uri, version) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE workflow_definitions
        SET member_execution_allowed = FALSE,
            input_schema = '{"type":"object","properties":{"ingestion_run_id":{"type":"string"}},"required":["ingestion_run_id"]}'::jsonb,
            updated_at = CURRENT_TIMESTAMP
        WHERE workflow_key = 'ragforge.ingest_document' AND version = '1.0.0'
        """
    )
    op.drop_table("audit_events")
    op.drop_table("artifacts")
    op.drop_table("quota_reservations")
    op.drop_table("quota_policies")
    op.drop_column("runs", "error_code")
