from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import (
    PROJECT_ACTION_MANAGE,
    PROJECT_ACTION_READ,
    PROJECT_ACTION_WRITE,
    authorize_organization,
    authorize_project,
    ProjectPermissions,
    resolve_project_permissions,
    resolve_projects_permissions,
)
from app.platform.capabilities import (
    ProjectDeletionContext,
    ProjectProvisioningContext,
    capability_registry,
)
from app.core.db import get_db
from app.models.project import Project
from app.platform.artifacts.model import Artifact
from app.platform.execution.model import GenericRun
from app.platform.publication.model import Publication
from app.platform.research.model import Experiment, ResearchStudy
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


class ProjectPermissionsResponse(BaseModel):
    read: bool
    write: bool
    manage: bool


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
    permissions: ProjectPermissionsResponse


class ProjectOverviewCounts(BaseModel):
    studies: int
    experiments: int
    runs: int
    artifacts: int
    publications: int


class ProjectOverviewResponse(BaseModel):
    project: ProjectResponse
    counts: ProjectOverviewCounts


async def _project_overview_counts(
    db: AsyncSession,
    project_ids: list[str],
) -> dict[str, ProjectOverviewCounts]:
    counts = {
        project_id: ProjectOverviewCounts(
            studies=0,
            experiments=0,
            runs=0,
            artifacts=0,
            publications=0,
        )
        for project_id in project_ids
    }
    if not project_ids:
        return counts

    async def grouped_count(model, project_column):
        result = await db.execute(
            select(project_column, func.count(model.id))
            .where(project_column.in_(project_ids))
            .group_by(project_column)
        )
        return {str(project_id): int(value) for project_id, value in result.all()}

    studies = await grouped_count(ResearchStudy, ResearchStudy.project_id)
    runs = await grouped_count(GenericRun, GenericRun.project_id)
    artifacts = await grouped_count(Artifact, Artifact.project_id)
    publications = await grouped_count(Publication, Publication.project_id)
    experiment_result = await db.execute(
        select(ResearchStudy.project_id, func.count(Experiment.id))
        .join(Experiment, Experiment.study_id == ResearchStudy.id)
        .where(ResearchStudy.project_id.in_(project_ids))
        .group_by(ResearchStudy.project_id)
    )
    experiments = {
        str(project_id): int(value) for project_id, value in experiment_result.all()
    }
    for project_id, project_counts in counts.items():
        project_counts.studies = studies.get(project_id, 0)
        project_counts.experiments = experiments.get(project_id, 0)
        project_counts.runs = runs.get(project_id, 0)
        project_counts.artifacts = artifacts.get(project_id, 0)
        project_counts.publications = publications.get(project_id, 0)
    return counts


def _project_payload(
    project: Project,
    permissions: ProjectPermissions,
) -> ProjectResponse:
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
        permissions=ProjectPermissionsResponse(
            read=permissions.read,
            write=permissions.write,
            manage=permissions.manage,
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
    permissions = await resolve_project_permissions(db, project, user)
    return _project_payload(project, permissions)


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
    permissions = await resolve_projects_permissions(db, projects, user)
    return [_project_payload(p, permissions[str(p.id)]) for p in projects]


@router.get("/overview", response_model=list[ProjectOverviewResponse])
async def list_project_overviews(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    projects = await project_repository.list_accessible_projects(
        db,
        user_id=user["user_id"],
        global_role=user["global_role"],
    )
    permissions = await resolve_projects_permissions(db, projects, user)
    project_ids = [str(project.id) for project in projects]
    counts = await _project_overview_counts(db, project_ids)
    return [
        ProjectOverviewResponse(
            project=_project_payload(project, permissions[str(project.id)]),
            counts=counts[str(project.id)],
        )
        for project in projects
    ]


@router.get("/{project_id}/overview", response_model=ProjectOverviewResponse)
async def get_project_overview(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = await authorize_project(
        db, project_id, user, action=PROJECT_ACTION_READ
    )
    permissions = await resolve_project_permissions(db, project, user)
    counts = await _project_overview_counts(db, [project_id])
    return ProjectOverviewResponse(
        project=_project_payload(project, permissions),
        counts=counts[project_id],
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = await authorize_project(
        db, project_id, user, action=PROJECT_ACTION_READ
    )
    permissions = await resolve_project_permissions(db, project, user)
    return _project_payload(project, permissions)


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

    permissions = await resolve_project_permissions(db, project, user)
    return _project_payload(project, permissions)


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
