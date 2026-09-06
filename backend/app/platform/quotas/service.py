from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.audit import record_audit_event
from app.platform.execution.contracts import RegisteredWorkflowDefinition
from app.platform.execution.model import GenericRun
from app.platform.quotas import repository
from app.platform.quotas.model import QuotaPolicy, QuotaReservation


class QuotaExceededError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


async def ensure_default_quota_policy(db: AsyncSession, user_id: str) -> QuotaPolicy:
    policy = await repository.get_user_policy(db, user_id)
    return policy or await repository.create_default_policy(db, user_id)


async def reserve_run_quota(
    db: AsyncSession,
    *,
    run: GenericRun,
    workflow: RegisteredWorkflowDefinition,
    actor_global_role: str,
) -> QuotaReservation | None:
    if actor_global_role == "admin":
        await record_audit_event(
            db,
            actor_user_id=run.requested_by,
            actor_global_role="admin",
            action="quota.bypass",
            target_type="run",
            target_id=run.id,
            project_id=run.project_id,
            details={"workflow_key": workflow.key, "workflow_version": workflow.version},
        )
        return None
    if not workflow.member_execution_allowed:
        raise QuotaExceededError("workflow_not_allowed", "This workflow is not available for member execution.")

    policy = await repository.get_user_policy(db, run.requested_by, lock=True)
    if policy is None:
        policy = await repository.create_default_policy(db, run.requested_by)
    if not policy.enabled:
        raise QuotaExceededError("quota_disabled", "Execution quota is disabled for this account.")
    declared_input_bytes = run.input_snapshot.get("input_size_bytes")
    input_bytes = (
        declared_input_bytes
        if isinstance(declared_input_bytes, int) and declared_input_bytes >= 0
        else len(json.dumps(run.input_snapshot, separators=(",", ":")).encode("utf-8"))
    )
    if policy.max_input_bytes is not None and input_bytes > policy.max_input_bytes:
        raise QuotaExceededError("input_limit_exceeded", "Workflow input exceeds the account limit.")
    if (
        policy.max_runtime_seconds is not None
        and workflow.runtime_limit_seconds is not None
        and workflow.runtime_limit_seconds > policy.max_runtime_seconds
    ):
        raise QuotaExceededError("runtime_limit_exceeded", "Workflow runtime exceeds the account limit.")

    today = datetime.now(UTC).date()
    month = date(today.year, today.month, 1)
    if await repository.active_reservation_count(db, policy.id) >= policy.concurrent_run_limit:
        raise QuotaExceededError("concurrency_limit_exceeded", "Too many workflows are already running.")
    if await repository.consumed_units(db, policy.id, period_day=today) + 1 > policy.daily_run_limit:
        raise QuotaExceededError("daily_limit_exceeded", "Daily workflow quota has been reached.")
    if await repository.consumed_units(db, policy.id, period_month=month) + 1 > policy.monthly_run_limit:
        raise QuotaExceededError("monthly_limit_exceeded", "Monthly workflow quota has been reached.")

    reservation = QuotaReservation(
        quota_policy_id=policy.id,
        run_id=run.id,
        status="reserved",
        reserved_units=Decimal("1"),
        period_day=today,
        period_month=month,
    )
    db.add(reservation)
    await db.flush()
    return reservation


async def finalize_run_quota(db: AsyncSession, run: GenericRun, *, consume: bool) -> None:
    reservation = await repository.get_run_reservation(db, run.id)
    if reservation is None or reservation.status != "reserved":
        return
    actual = reservation.reserved_units if consume else Decimal("0")
    reservation.status = "finalized" if consume else "released"
    reservation.actual_units = actual
    reservation.finalized_at = datetime.now(UTC).replace(tzinfo=None)
    run.quota_cost = actual
    await db.flush()
