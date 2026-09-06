from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.artifacts.model import Artifact
from app.platform.audit.safety import sanitize_details


async def register_artifact(
    db: AsyncSession,
    *,
    project_id: str,
    artifact_type: str,
    storage_provider: str,
    storage_uri: str,
    created_by: str | None,
    run_id: str | None = None,
    version: str = "1",
    visibility: str = "private",
    checksum: str | None = None,
    size_bytes: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> Artifact:
    result = await db.execute(
        select(Artifact).where(
            Artifact.project_id == project_id,
            Artifact.artifact_type == artifact_type,
            Artifact.storage_uri == storage_uri,
            Artifact.version == version,
        )
    )
    artifact = result.scalar_one_or_none()
    if artifact is not None:
        return artifact
    artifact = Artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type=artifact_type,
        storage_provider=storage_provider,
        storage_uri=storage_uri,
        version=version,
        visibility=visibility,
        checksum=checksum,
        size_bytes=size_bytes,
        created_by=created_by,
        artifact_metadata=sanitize_details(metadata or {}),
    )
    db.add(artifact)
    await db.flush()
    return artifact


async def get_artifact(db: AsyncSession, artifact_id: str) -> Artifact | None:
    return await db.get(Artifact, artifact_id)


async def list_project_artifacts(db: AsyncSession, project_id: str, *, limit: int = 100) -> list[Artifact]:
    result = await db.execute(
        select(Artifact)
        .where(Artifact.project_id == project_id)
        .order_by(Artifact.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
