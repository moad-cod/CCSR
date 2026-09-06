from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.audit.model import AuditEvent
from app.platform.audit.safety import sanitize_details


async def record_audit_event(
    db: AsyncSession,
    *,
    actor_user_id: str | None,
    actor_global_role: str,
    action: str,
    target_type: str,
    target_id: str,
    project_id: str | None = None,
    outcome: str = "success",
    details: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor_user_id=actor_user_id,
        actor_global_role=actor_global_role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        project_id=project_id,
        outcome=outcome,
        details=sanitize_details(details or {}),
    )
    db.add(event)
    await db.flush()
    return event


async def list_audit_events(db: AsyncSession, *, limit: int = 100) -> list[AuditEvent]:
    result = await db.execute(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit))
    return list(result.scalars().all())
