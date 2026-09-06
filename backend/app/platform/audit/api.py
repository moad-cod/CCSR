from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.platform.access.policies import GLOBAL_ROLE_ADMIN, require_global_roles
from app.platform.audit.repository import list_audit_events


router = APIRouter()


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_user_id: str | None
    actor_global_role: str
    action: str
    target_type: str
    target_id: str
    project_id: str | None
    outcome: str
    details: dict[str, Any]
    created_at: datetime


@router.get("/admin/audit-events", response_model=list[AuditEventResponse])
async def get_audit_events(
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_global_roles(GLOBAL_ROLE_ADMIN)),
):
    return await list_audit_events(db, limit=limit)
