from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import validates

from app.core.db import Base


AUDIT_OUTCOMES = frozenset({"success", "denied", "failure"})


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_global_role = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    outcome = Column(String, nullable=False, default="success")
    details = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @validates("outcome")
    def validate_outcome(self, _key: str, value: str) -> str:
        if value not in AUDIT_OUTCOMES:
            raise ValueError(f"Invalid audit outcome: {value}")
        return value

    __table_args__ = (
        CheckConstraint("outcome IN ('success', 'denied', 'failure')", name="ck_audit_events_outcome"),
        Index("ix_audit_events_actor_user_id", "actor_user_id"),
        Index("ix_audit_events_project_id", "project_id"),
        Index("ix_audit_events_action", "action"),
        Index("ix_audit_events_created_at", "created_at"),
    )
