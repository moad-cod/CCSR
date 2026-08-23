from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.core.db import Base


ORGANIZATION_ROLE_OWNER = "owner"
ORGANIZATION_ROLE_ADMIN = "admin"
ORGANIZATION_ROLE_MEMBER = "member"
ORGANIZATION_ROLES = (
    ORGANIZATION_ROLE_OWNER,
    ORGANIZATION_ROLE_ADMIN,
    ORGANIZATION_ROLE_MEMBER,
)


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String, nullable=False, default=ORGANIZATION_ROLE_MEMBER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="organization_memberships")

    @validates("role")
    def validate_role(self, _key: str, value: str) -> str:
        if value not in ORGANIZATION_ROLES:
            raise ValueError(f"Invalid organization role: {value}")
        return value

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_memberships_org_user"),
        CheckConstraint(
            "role IN ('owner', 'admin', 'member')",
            name="ck_organization_memberships_role",
        ),
        Index("ix_organization_memberships_organization_id", "organization_id"),
        Index("ix_organization_memberships_user_id", "user_id"),
        Index("ix_organization_memberships_role", "role"),
        Index("ix_organization_memberships_deleted_at", "deleted_at"),
    )
