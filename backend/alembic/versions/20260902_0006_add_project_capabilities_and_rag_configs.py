"""add project capabilities and RAG project configs

Revision ID: 20260902_0006
Revises: 20260823_0005
Create Date: 2026-09-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260902_0006"
down_revision: Union[str, None] = "20260823_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_capabilities",
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("capability_key", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "capability_key"),
    )
    op.create_index(
        "ix_project_capabilities_capability_key",
        "project_capabilities",
        ["capability_key"],
    )

    op.create_table(
        "rag_project_configs",
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("qdrant_collection", sa.String(), nullable=False),
        sa.Column(
            "embedding_model",
            sa.String(),
            nullable=False,
            server_default="BAAI/bge-small-en-v1.5",
        ),
        sa.Column(
            "sparse_model",
            sa.String(),
            nullable=False,
            server_default="Qdrant/bm25",
        ),
        sa.Column(
            "default_chunker",
            sa.String(),
            nullable=False,
            server_default="paragraph",
        ),
        sa.Column(
            "retrieval_configuration",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(
                "'{\"strategy\": \"hybrid\", \"top_k\": 5, "
                "\"fetch_k\": 30, \"use_rerank\": true}'::jsonb"
            ),
        ),
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
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id"),
        sa.UniqueConstraint(
            "qdrant_collection",
            name="uq_rag_project_configs_qdrant_collection",
        ),
    )

    op.execute(
        """
        INSERT INTO project_capabilities (project_id, capability_key, created_at)
        SELECT id, 'ragforge', COALESCE(created_at, CURRENT_TIMESTAMP)
        FROM projects
        ON CONFLICT (project_id, capability_key) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO rag_project_configs (
            project_id,
            qdrant_collection,
            embedding_model,
            sparse_model,
            default_chunker,
            retrieval_configuration,
            created_at,
            updated_at
        )
        SELECT
            id,
            qdrant_collection,
            'BAAI/bge-small-en-v1.5',
            'Qdrant/bm25',
            'paragraph',
            '{"strategy": "hybrid", "top_k": 5, "fetch_k": 30, "use_rerank": true}'::jsonb,
            COALESCE(created_at, CURRENT_TIMESTAMP),
            COALESCE(updated_at, CURRENT_TIMESTAMP)
        FROM projects
        ON CONFLICT (project_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("rag_project_configs")
    op.drop_index(
        "ix_project_capabilities_capability_key",
        table_name="project_capabilities",
    )
    op.drop_table("project_capabilities")
