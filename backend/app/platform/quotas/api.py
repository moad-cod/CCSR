from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import GLOBAL_ROLE_ADMIN, require_global_roles
from app.platform.accounts.model import User
from app.platform.audit import record_audit_event
from app.platform.quotas import repository
from app.platform.quotas.service import ensure_default_quota_policy


router = APIRouter()


class QuotaPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    daily_run_limit: int
    monthly_run_limit: int
    concurrent_run_limit: int
    max_runtime_seconds: int | None
    max_input_bytes: int | None
    enabled: bool
    created_at: datetime
    updated_at: datetime


class QuotaPolicyUpdate(BaseModel):
    daily_run_limit: int = Field(ge=0)
    monthly_run_limit: int = Field(ge=0)
    concurrent_run_limit: int = Field(ge=0)
    max_runtime_seconds: int | None = Field(default=None, gt=0)
    max_input_bytes: int | None = Field(default=None, gt=0)
    enabled: bool = True


class QuotaUsageResponse(BaseModel):
    policy: QuotaPolicyResponse
    daily_used: float
    monthly_used: float
    active_runs: int


@router.get("/quotas/me", response_model=QuotaUsageResponse)
async def get_my_quota(
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    policy = await ensure_default_quota_policy(db, principal["user_id"])
    today = datetime.now(UTC).date()
    month = date(today.year, today.month, 1)
    await db.commit()
    return QuotaUsageResponse(
        policy=QuotaPolicyResponse.model_validate(policy),
        daily_used=float(await repository.consumed_units(db, policy.id, period_day=today)),
        monthly_used=float(await repository.consumed_units(db, policy.id, period_month=month)),
        active_runs=await repository.active_reservation_count(db, policy.id),
    )


@router.put("/admin/quotas/users/{user_id}", response_model=QuotaPolicyResponse)
async def update_user_quota(
    user_id: str,
    body: QuotaPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_global_roles(GLOBAL_ROLE_ADMIN)),
):
    account = await db.get(User, user_id)
    if account is None or account.deleted_at is not None:
        raise HTTPException(404, "User not found")
    policy = await ensure_default_quota_policy(db, user_id)
    previous = {
        "daily_run_limit": policy.daily_run_limit,
        "monthly_run_limit": policy.monthly_run_limit,
        "concurrent_run_limit": policy.concurrent_run_limit,
        "max_runtime_seconds": policy.max_runtime_seconds,
        "max_input_bytes": policy.max_input_bytes,
        "enabled": policy.enabled,
    }
    for field, value in body.model_dump().items():
        setattr(policy, field, value)
    policy.created_by = admin["user_id"]
    await record_audit_event(
        db,
        actor_user_id=admin["user_id"],
        actor_global_role="admin",
        action="quota.update",
        target_type="user",
        target_id=user_id,
        details={"before": previous, "after": body.model_dump()},
    )
    await db.commit()
    await db.refresh(policy)
    return policy
