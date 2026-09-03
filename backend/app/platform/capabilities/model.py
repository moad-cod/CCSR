from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class ProjectCapability(Base):
    __tablename__ = "project_capabilities"

    project_id = Column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    capability_key = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="capabilities")

    __table_args__ = (
        Index("ix_project_capabilities_capability_key", "capability_key"),
    )
