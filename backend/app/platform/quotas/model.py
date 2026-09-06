from datetime import date, datetime
from decimal import Decimal
import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.core.db import Base


RESERVATION_STATUSES = frozenset({"reserved", "finalized", "released"})


class QuotaPolicy(Base):
    __tablename__ = "quota_policies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    daily_run_limit = Column(Integer, nullable=False, default=100)
    monthly_run_limit = Column(Integer, nullable=False, default=1000)
    concurrent_run_limit = Column(Integer, nullable=False, default=4)
    max_runtime_seconds = Column(Integer, nullable=True)
    max_input_bytes = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reservations = relationship("QuotaReservation", back_populates="policy", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("daily_run_limit >= 0", name="ck_quota_policies_daily_limit"),
        CheckConstraint("monthly_run_limit >= 0", name="ck_quota_policies_monthly_limit"),
        CheckConstraint("concurrent_run_limit >= 0", name="ck_quota_policies_concurrent_limit"),
        CheckConstraint("max_runtime_seconds IS NULL OR max_runtime_seconds > 0", name="ck_quota_policies_runtime"),
        CheckConstraint("max_input_bytes IS NULL OR max_input_bytes > 0", name="ck_quota_policies_input_bytes"),
        Index("ix_quota_policies_user_id", "user_id"),
    )


class QuotaReservation(Base):
    __tablename__ = "quota_reservations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    quota_policy_id = Column(UUID(as_uuid=False), ForeignKey("quota_policies.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(String, nullable=False, default="reserved")
    reserved_units = Column(Numeric(18, 6), nullable=False, default=Decimal("1"))
    actual_units = Column(Numeric(18, 6), nullable=True)
    period_day = Column(Date, nullable=False, default=date.today)
    period_month = Column(Date, nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finalized_at = Column(DateTime, nullable=True)

    policy = relationship("QuotaPolicy", back_populates="reservations")
    run = relationship("GenericRun", back_populates="quota_reservation")

    @validates("status")
    def validate_status(self, _key: str, value: str) -> str:
        if value not in RESERVATION_STATUSES:
            raise ValueError(f"Invalid quota reservation status: {value}")
        return value

    __table_args__ = (
        CheckConstraint("status IN ('reserved', 'finalized', 'released')", name="ck_quota_reservations_status"),
        CheckConstraint("reserved_units >= 0", name="ck_quota_reservations_reserved_units"),
        CheckConstraint("actual_units IS NULL OR actual_units >= 0", name="ck_quota_reservations_actual_units"),
        Index("ix_quota_reservations_quota_policy_id", "quota_policy_id"),
        Index("ix_quota_reservations_status", "status"),
        Index("ix_quota_reservations_period_day", "period_day"),
        Index("ix_quota_reservations_period_month", "period_month"),
    )
