from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.execution.model import GenericRun
from app.platform.quotas.model import QuotaPolicy, QuotaReservation


async def get_user_policy(db: AsyncSession, user_id: str, *, lock: bool = False) -> QuotaPolicy | None:
    query = select(QuotaPolicy).where(QuotaPolicy.user_id == user_id)
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_default_policy(db: AsyncSession, user_id: str) -> QuotaPolicy:
    policy = QuotaPolicy(user_id=user_id)
    db.add(policy)
    await db.flush()
    return policy


async def consumed_units(db: AsyncSession, policy_id: str, *, period_day: date | None = None, period_month: date | None = None) -> Decimal:
    charged_units = func.coalesce(
        func.sum(
            func.coalesce(
                QuotaReservation.actual_units,
                QuotaReservation.reserved_units,
            )
        ),
        0,
    )
    query = select(charged_units).where(
        QuotaReservation.quota_policy_id == policy_id,
        QuotaReservation.status.in_(("reserved", "finalized")),
    )
    if period_day is not None:
        query = query.where(QuotaReservation.period_day == period_day)
    if period_month is not None:
        query = query.where(QuotaReservation.period_month == period_month)
    return Decimal(str(await db.scalar(query) or 0))


async def active_reservation_count(db: AsyncSession, policy_id: str) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(QuotaReservation)
            .join(GenericRun, GenericRun.id == QuotaReservation.run_id)
            .where(
                QuotaReservation.quota_policy_id == policy_id,
                QuotaReservation.status == "reserved",
                GenericRun.status.in_(("pending", "queued", "running")),
            )
        )
        or 0
    )


async def get_run_reservation(db: AsyncSession, run_id: str) -> QuotaReservation | None:
    result = await db.execute(select(QuotaReservation).where(QuotaReservation.run_id == run_id))
    return result.scalar_one_or_none()


async def list_user_reservations(db: AsyncSession, policy_id: str, *, limit: int = 50) -> list[QuotaReservation]:
    result = await db.execute(
        select(QuotaReservation)
        .where(QuotaReservation.quota_policy_id == policy_id)
        .order_by(QuotaReservation.reserved_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
