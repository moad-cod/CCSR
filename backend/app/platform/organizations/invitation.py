from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates

from app.core.db import Base
from app.platform.organizations.membership import ORGANIZATION_ROLES


class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    email = Column(String, nullable=False)
    role = Column(String, nullable=False, default="member")
    token_hash = Column(String(64), unique=True, nullable=False)
    invited_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @validates("role")
    def validate_role(self, _key: str, value: str) -> str:
        if value not in ORGANIZATION_ROLES:
            raise ValueError(f"Invalid organization invitation role: {value}")
        return value

    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'admin', 'member')",
            name="ck_organization_invitations_role",
        ),
        Index("ix_organization_invitations_organization_id", "organization_id"),
        Index("ix_organization_invitations_email", "email"),
        Index("ix_organization_invitations_expires_at", "expires_at"),
    )
