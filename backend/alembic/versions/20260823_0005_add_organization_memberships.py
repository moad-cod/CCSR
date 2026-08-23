"""add organization memberships

Revision ID: 20260823_0005
Revises: 20260803_0004
Create Date: 2026-08-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260823_0005"
down_revision: Union[str, None] = "20260803_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "role IN ('owner', 'admin', 'member')",
            name="ck_organization_memberships_role",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_memberships_org_user",
        ),
    )
    op.create_index(
        "ix_organization_memberships_organization_id",
        "organization_memberships",
        ["organization_id"],
    )
    op.create_index(
        "ix_organization_memberships_user_id",
        "organization_memberships",
        ["user_id"],
    )
    op.create_index(
        "ix_organization_memberships_role",
        "organization_memberships",
        ["role"],
    )
    op.create_index(
        "ix_organization_memberships_deleted_at",
        "organization_memberships",
        ["deleted_at"],
    )

    op.execute(
        """
        INSERT INTO organization_memberships (
            id,
            organization_id,
            user_id,
            role,
            created_at,
            updated_at
        )
        SELECT
            (
                substr(md5(users.id::text || ':' || users.organization_id::text), 1, 8) || '-' ||
                substr(md5(users.id::text || ':' || users.organization_id::text), 9, 4) || '-' ||
                substr(md5(users.id::text || ':' || users.organization_id::text), 13, 4) || '-' ||
                substr(md5(users.id::text || ':' || users.organization_id::text), 17, 4) || '-' ||
                substr(md5(users.id::text || ':' || users.organization_id::text), 21, 12)
            )::uuid,
            users.organization_id,
            users.id,
            'member',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM users
        JOIN organizations ON organizations.id = users.organization_id
        WHERE users.organization_id IS NOT NULL
          AND users.deleted_at IS NULL
          AND organizations.deleted_at IS NULL
        ON CONFLICT (organization_id, user_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_organization_memberships_deleted_at", table_name="organization_memberships")
    op.drop_index("ix_organization_memberships_role", table_name="organization_memberships")
    op.drop_index("ix_organization_memberships_user_id", table_name="organization_memberships")
    op.drop_index("ix_organization_memberships_organization_id", table_name="organization_memberships")
    op.drop_table("organization_memberships")
