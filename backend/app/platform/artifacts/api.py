from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import GLOBAL_ROLE_ADMIN, PROJECT_ACTION_MANAGE, PROJECT_ACTION_READ, authorize_project, require_global_roles
from app.platform.artifacts import repository
from app.platform.audit import record_audit_event
from app.platform.execution.model import GenericRun


router = APIRouter()


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    run_id: str | None
    artifact_type: str
    storage_provider: str
    storage_uri: str
    version: str
    visibility: str
    checksum: str | None
    size_bytes: int | None
    created_by: str | None
    artifact_metadata: dict[str, Any]
    created_at: datetime


class ArtifactCreate(BaseModel):
    project_id: str
    run_id: str | None = None
    artifact_type: str = Field(min_length=1, max_length=100)
    storage_provider: Literal["minio", "qdrant", "external"]
    storage_uri: str = Field(min_length=1, max_length=2048)
    version: str = Field(default="1", min_length=1, max_length=100)
    visibility: Literal["private", "project", "public"] = "private"
    checksum: str | None = Field(default=None, max_length=256)
    size_bytes: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/artifacts", response_model=list[ArtifactResponse])
async def list_artifacts(
    project_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_READ)
    return await repository.list_project_artifacts(db, project_id, limit=limit)


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    artifact = await repository.get_artifact(db, artifact_id)
    if artifact is None:
        raise HTTPException(404, "Artifact not found")
    await authorize_project(db, artifact.project_id, principal, action=PROJECT_ACTION_READ)
    return artifact


@router.post("/admin/artifacts", response_model=ArtifactResponse)
async def create_artifact(
    body: ArtifactCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_global_roles(GLOBAL_ROLE_ADMIN)),
):
    await authorize_project(db, body.project_id, admin, action=PROJECT_ACTION_MANAGE)
    if body.run_id is not None:
        run = await db.get(GenericRun, body.run_id)
        if run is None or run.project_id != body.project_id:
            raise HTTPException(400, "Run does not belong to the artifact project")
    artifact = await repository.register_artifact(
        db,
        project_id=body.project_id,
        run_id=body.run_id,
        artifact_type=body.artifact_type,
        storage_provider=body.storage_provider,
        storage_uri=body.storage_uri,
        version=body.version,
        visibility=body.visibility,
        checksum=body.checksum,
        size_bytes=body.size_bytes,
        created_by=admin["user_id"],
        metadata=body.metadata,
    )
    await record_audit_event(
        db,
        actor_user_id=admin["user_id"],
        actor_global_role="admin",
        action="artifact.register",
        target_type="artifact",
        target_id=artifact.id,
        project_id=body.project_id,
        details={"artifact_type": body.artifact_type, "visibility": body.visibility},
    )
    await db.commit()
    return artifact
