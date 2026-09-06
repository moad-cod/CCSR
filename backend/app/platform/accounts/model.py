from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    global_role = Column(String, nullable=False, default="member")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")
    organization_memberships = relationship(
        "OrganizationMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    ingestion_runs = relationship("IngestionRun", back_populates="creator")
    runs = relationship("GenericRun", back_populates="requester", foreign_keys="GenericRun.requested_by")
    query_logs = relationship("QueryLog", back_populates="user")
    quota_policy = relationship(
        "QuotaPolicy",
        foreign_keys="QuotaPolicy.user_id",
        cascade="all, delete-orphan",
        uselist=False,
    )

    @validates("global_role")
    def validate_global_role(self, _key: str, value: str) -> str:
        if value not in {"member", "admin"}:
            raise ValueError(f"Invalid global role: {value}")
        return value

    __table_args__ = (
        CheckConstraint(
            "global_role IN ('member', 'admin')",
            name="ck_users_global_role",
        ),
        Index("ix_users_organization_id", "organization_id"),
        Index("ix_users_global_role", "global_role"),
        Index("ix_users_deleted_at", "deleted_at"),
    )
