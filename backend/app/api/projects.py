from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import (
    PROJECT_ACTION_MANAGE,
    PROJECT_ACTION_READ,
    PROJECT_ACTION_WRITE,
    authorize_organization,
    authorize_project,
)
from app.platform.capabilities import (
    ProjectDeletionContext,
    ProjectProvisioningContext,
    capability_registry,
)
from app.core.db import get_db
from app.models.project import Project
from app.repositories import projects as project_repository
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any
import uuid

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    organization_id: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Project name is required")
        if len(name) > 120:
            raise ValueError("Project name must be 120 characters or fewer")
        return name

    @field_validator("organization_id")
    @classmethod
    def validate_organization_id(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        try:
            return str(uuid.UUID(value.strip()))
        except ValueError as exc:
            raise ValueError("organization_id must be a valid UUID") from exc

class ProjectUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return ProjectCreate.validate_name(value)

class RAGProjectConfigResponse(BaseModel):
    qdrant_collection: str
    embedding_model: str
    sparse_model: str
    default_chunker: str
    retrieval_configuration: dict[str, Any]


class ProjectResponse(BaseModel):
    project_id: str
    organization_id: str | None
    name: str
    collection: str
    qdrant_collection: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    capabilities: list[str]
    rag_config: RAGProjectConfigResponse | None


def _project_payload(project: Project) -> ProjectResponse:
    rag_config = project.__dict__.get("rag_config")
    collection = (
        rag_config.qdrant_collection
        if rag_config is not None
        else project.qdrant_collection
    )
    capabilities = sorted(
        association.capability_key
        for association in project.__dict__.get("capabilities", ())
    )
    return ProjectResponse(
        project_id=project.id,
        organization_id=project.organization_id,
        name=project.name,
        collection=collection,
        qdrant_collection=collection,
        created_by=project.created_by,
        created_at=project.created_at,
        updated_at=project.updated_at,
        capabilities=capabilities,
        rag_config=(
            RAGProjectConfigResponse(
                qdrant_collection=rag_config.qdrant_collection,
                embedding_model=rag_config.embedding_model,
                sparse_model=rag_config.sparse_model,
                default_chunker=rag_config.default_chunker,
                retrieval_configuration=dict(rag_config.retrieval_configuration),
            )
            if rag_config is not None
            else None
        ),
    )


@router.post("/", response_model=ProjectResponse)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if body.organization_id:
        await authorize_organization(db, body.organization_id, user)

    project_id = str(uuid.uuid4())
    collection = f"project_{project_id}"
    project = await project_repository.create_project(
        db,
        id=project_id,
        organization_id=body.organization_id,
        created_by=user["user_id"],
        name=body.name,
        qdrant_collection=collection,
    )
    await capability_registry.provision_project(
        ProjectProvisioningContext(db=db, project=project)
    )
    await db.commit()
    project = await project_repository.get_project(db, project_id)
    if project is None:
        raise HTTPException(500, "Created project could not be reloaded")
    return _project_payload(project)


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    projects = await project_repository.list_accessible_projects(
        db,
        user_id=user["user_id"],
        global_role=user["global_role"],
    )
    return [_project_payload(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = await authorize_project(
        db, project_id, user, action=PROJECT_ACTION_READ
    )
    return _project_payload(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = await authorize_project(
        db, project_id, user, action=PROJECT_ACTION_WRITE
    )
    project.name = body.name
    await db.flush()

    # only update display name — collection name stays the same
    # changing collection would require re-indexing all documents
    await db.commit()
    project = await project_repository.get_project(db, project_id)
    if project is None:
        raise HTTPException(500, "Updated project could not be reloaded")

    return _project_payload(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = await authorize_project(
        db, project_id, user, action=PROJECT_ACTION_MANAGE
    )

    deleted_collection = project.collection
    lifecycle_result = await capability_registry.before_project_delete(
        ProjectDeletionContext(db=db, project=project)
    )

    project.deleted_at = datetime.utcnow()
    await db.commit()

    return {
        "deleted_project": project_id,
        "deleted_collection": deleted_collection,
        "deleted_documents": lifecycle_result.count("documents"),
    }
