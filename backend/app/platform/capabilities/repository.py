from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.capabilities.model import ProjectCapability


async def enable_project_capability(
    db: AsyncSession,
    *,
    project_id: str,
    capability_key: str,
) -> ProjectCapability:
    existing = await db.get(
        ProjectCapability,
        (project_id, capability_key),
    )
    if existing is not None:
        return existing
    association = ProjectCapability(
        project_id=project_id,
        capability_key=capability_key,
    )
    db.add(association)
    await db.flush()
    return association


async def list_project_capability_keys(
    db: AsyncSession,
    project_id: str,
) -> tuple[str, ...]:
    result = await db.execute(
        select(ProjectCapability.capability_key)
        .where(ProjectCapability.project_id == project_id)
        .order_by(ProjectCapability.capability_key)
    )
    return tuple(result.scalars().all())


async def list_capability_project_ids(
    db: AsyncSession,
    project_ids: Sequence[str],
) -> dict[str, set[str]]:
    if not project_ids:
        return {}
    result = await db.execute(
        select(
            ProjectCapability.capability_key,
            ProjectCapability.project_id,
        ).where(ProjectCapability.project_id.in_(project_ids))
    )
    by_capability: dict[str, set[str]] = {}
    for capability_key, project_id in result.all():
        by_capability.setdefault(capability_key, set()).add(project_id)
    return by_capability
