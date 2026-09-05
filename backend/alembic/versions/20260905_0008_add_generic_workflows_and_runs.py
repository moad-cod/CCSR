"""add generic workflows and runs

Revision ID: 20260905_0008
Revises: 20260904_0007
Create Date: 2026-09-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260905_0008"
down_revision: Union[str, None] = "20260904_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


RAGFORGE_WORKFLOW_ID = "00000000-0000-0000-0000-000000000601"


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("workflow_key", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("capability_key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("engine", sa.String(), nullable=False),
        sa.Column("input_schema", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output_schema", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("resource_requirements", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("runtime_limit_seconds", sa.Integer(), nullable=True),
        sa.Column("member_execution_allowed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("artifact_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("handler_reference", sa.String(), nullable=False),
        sa.Column("publication_status", sa.String(), nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("engine IN ('airflow', 'celery')", name="ck_workflow_definitions_engine"),
        sa.CheckConstraint(
            "publication_status IN ('draft', 'published', 'retired')",
            name="ck_workflow_definitions_publication_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workflow_key",
            "version",
            "engine",
            name="uq_workflow_definitions_key_version_engine",
        ),
    )
    op.create_index(
        "ix_workflow_definitions_capability_key",
        "workflow_definitions",
        ["capability_key"],
    )
    op.create_index(
        "ix_workflow_definitions_publication_status",
        "workflow_definitions",
        ["publication_status"],
    )

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("engine", sa.String(), nullable=False),
        sa.Column("external_execution_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("quota_cost", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("engine IN ('airflow', 'celery')", name="ck_runs_engine"),
        sa.CheckConstraint(
            "status IN ('pending', 'queued', 'running', 'succeeded', 'failed', 'cancelled')",
            name="ck_runs_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["workflow_definition_id"],
            ["workflow_definitions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "project_id",
        "workflow_definition_id",
        "requested_by",
        "status",
        "created_at",
        "external_execution_id",
    ):
        op.create_index(f"ix_runs_{column}", "runs", [column])

    op.add_column(
        "ingestion_runs",
        sa.Column("generic_run_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.create_foreign_key(
        "fk_ingestion_runs_generic_run_id_runs",
        "ingestion_runs",
        "runs",
        ["generic_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_ingestion_runs_generic_run_id",
        "ingestion_runs",
        ["generic_run_id"],
    )
    op.create_index("ix_ingestion_runs_generic_run_id", "ingestion_runs", ["generic_run_id"])

    op.execute(
        f"""
        INSERT INTO workflow_definitions (
            id, workflow_key, version, capability_key, name, description,
            engine, input_schema, output_schema, resource_requirements,
            runtime_limit_seconds, member_execution_allowed, artifact_types,
            handler_reference, publication_status, created_at, updated_at
        ) VALUES (
            '{RAGFORGE_WORKFLOW_ID}',
            'ragforge.ingest_document',
            '1.0.0',
            'ragforge',
            'Ingest document',
            'Land, parse, chunk, embed, and index a RAGForge document.',
            'airflow',
            '{{"type":"object","properties":{{"ingestion_run_id":{{"type":"string"}}}},"required":["ingestion_run_id"]}}'::jsonb,
            '{{"type":"object","properties":{{"document_id":{{"type":"string"}}}}}}'::jsonb,
            '{{"profile":"ingestion-plan"}}'::jsonb,
            NULL,
            FALSE,
            '["rag-bronze","rag-silver","rag-gold","qdrant-index"]'::jsonb,
            'ragforge_ingestion',
            'published',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (workflow_key, version, engine) DO NOTHING
        """
    )
    op.execute(
        f"""
        INSERT INTO runs (
            id, project_id, workflow_definition_id, requested_by, engine,
            external_execution_id, status, input_snapshot, output_summary,
            quota_cost, started_at, completed_at, error_message, created_at, updated_at
        )
        SELECT
            ir.id,
            ir.project_id,
            '{RAGFORGE_WORKFLOW_ID}',
            ir.created_by,
            CASE
                WHEN ir.airflow_dag_run_id IS NOT NULL
                 AND ir.airflow_dag_run_id NOT LIKE 'ragforge__%' THEN 'celery'
                ELSE 'airflow'
            END,
            ir.airflow_dag_run_id,
            CASE
                WHEN ir.status = 'landed' THEN 'pending'
                WHEN ir.status = 'queued' THEN 'queued'
                WHEN ir.status IN ('running', 'silver_completed', 'gold_completed') THEN 'running'
                WHEN ir.status = 'indexed' THEN 'succeeded'
                WHEN ir.status = 'cancelled' THEN 'cancelled'
                ELSE 'failed'
            END,
            jsonb_build_object('ingestion_run_id', ir.id::text),
            CASE WHEN ir.status = 'indexed' THEN jsonb_build_object(
                'document_id', ir.document_id::text,
                'document_version_id', ir.document_version_id::text
            ) ELSE NULL END,
            0,
            ir.started_at,
            ir.finished_at,
            ir.error_message,
            ir.created_at,
            COALESCE(ir.finished_at, ir.started_at, ir.created_at)
        FROM ingestion_runs ir
        ON CONFLICT (id) DO NOTHING
        """
    )
    op.execute("UPDATE ingestion_runs SET generic_run_id = id WHERE generic_run_id IS NULL")


def downgrade() -> None:
    op.drop_index("ix_ingestion_runs_generic_run_id", table_name="ingestion_runs")
    op.drop_constraint("uq_ingestion_runs_generic_run_id", "ingestion_runs", type_="unique")
    op.drop_constraint(
        "fk_ingestion_runs_generic_run_id_runs",
        "ingestion_runs",
        type_="foreignkey",
    )
    op.drop_column("ingestion_runs", "generic_run_id")
    op.drop_table("runs")
    op.drop_table("workflow_definitions")
