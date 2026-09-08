from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import (
    PROJECT_ACTION_MANAGE,
    PROJECT_ACTION_READ,
    PROJECT_ACTION_WRITE,
    authorize_project,
)
from app.platform.audit import record_audit_event
from app.platform.publication import repository, service
from app.platform.publication.model import Publication
from app.platform.research.validation import clean_required_text


router = APIRouter()


class PublicationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    slug: str | None = Field(default=None, max_length=120)
    summary: str | None = Field(default=None, max_length=50_000)
    state: Literal["private", "draft"] = "private"
    research_study_id: str | None = None
    finding_ids: list[str] = Field(default_factory=list, max_length=500)
    artifact_ids: list[str] = Field(default_factory=list, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_required_text(value)


class PublicationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    summary: str | None = Field(default=None, max_length=50_000)
    state: Literal["private", "draft"] | None = None
    finding_ids: list[str] | None = Field(default=None, max_length=500)
    artifact_ids: list[str] | None = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return clean_required_text(value) if value is not None else None


class PublicationResponse(BaseModel):
    id: str
    project_id: str
    research_study_id: str | None
    slug: str
    title: str
    summary: str | None
    state: str
    current_revision_number: int | None
    finding_ids: list[str]
    artifact_ids: list[str]
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PublicPublicationResponse(BaseModel):
    slug: str
    title: str
    summary: str | None
    revision_number: int
    published_at: datetime
    snapshot: dict[str, Any]


def _publication_payload(publication: Publication) -> PublicationResponse:
    return PublicationResponse(
        id=publication.id,
        project_id=publication.project_id,
        research_study_id=publication.research_study_id,
        slug=publication.slug,
        title=publication.title,
        summary=publication.summary,
        state=publication.state,
        current_revision_number=publication.current_revision_number,
        finding_ids=sorted(item.id for item in publication.findings),
        artifact_ids=sorted(item.id for item in publication.artifacts),
        published_at=publication.published_at,
        created_at=publication.created_at,
        updated_at=publication.updated_at,
    )


def _public_payload(publication, revision) -> PublicPublicationResponse:
    published = dict(revision.snapshot).get("publication", {})
    return PublicPublicationResponse(
        slug=published.get("slug", publication.slug),
        title=published.get("title", publication.title),
        summary=published.get("summary"),
        revision_number=revision.revision_number,
        published_at=revision.created_at,
        snapshot=dict(revision.snapshot),
    )


@router.post(
    "/projects/{project_id}/publications",
    response_model=PublicationResponse,
    status_code=201,
)
async def create_publication(
    project_id: str,
    body: PublicationCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_WRITE)
    try:
        publication = await repository.create_publication(
            db,
            project_id=project_id,
            created_by=principal["user_id"],
            **body.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await record_audit_event(
        db,
        actor_user_id=principal["user_id"],
        actor_global_role=principal["global_role"],
        action="publication.create",
        target_type="publication",
        target_id=publication.id,
        project_id=project_id,
        details={"slug": publication.slug, "state": publication.state},
    )
    await db.commit()
    return _publication_payload(publication)


@router.get(
    "/projects/{project_id}/publications",
    response_model=list[PublicationResponse],
)
async def list_project_publications(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_READ)
    records = await repository.list_project_publications(db, project_id)
    return [_publication_payload(item) for item in records]


@router.patch(
    "/projects/{project_id}/publications/{publication_id}",
    response_model=PublicationResponse,
)
async def update_publication(
    project_id: str,
    publication_id: str,
    body: PublicationUpdate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_WRITE)
    publication = await repository.get_publication(
        db, project_id, publication_id, include_sources=True
    )
    if publication is None:
        raise HTTPException(404, "Publication not found")
    if publication.state == "public":
        raise HTTPException(409, "Unpublish before editing a public publication")
    values = body.model_dump(exclude_unset=True)
    finding_ids = values.pop("finding_ids", None)
    artifact_ids = values.pop("artifact_ids", None)
    for field, value in values.items():
        setattr(publication, field, value)
    try:
        await repository.replace_selections(
            db,
            publication,
            finding_ids=finding_ids,
            artifact_ids=artifact_ids,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await record_audit_event(
        db,
        actor_user_id=principal["user_id"],
        actor_global_role=principal["global_role"],
        action="publication.update",
        target_type="publication",
        target_id=publication.id,
        project_id=project_id,
        details={"state": publication.state},
    )
    await db.commit()
    return _publication_payload(publication)


@router.post(
    "/projects/{project_id}/publications/{publication_id}/publish",
    response_model=PublicationResponse,
)
async def publish_publication(
    project_id: str,
    publication_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_MANAGE)
    try:
        publication = await service.publish(
            db,
            project_id=project_id,
            publication_id=publication_id,
            actor=principal,
        )
    except service.PublicationNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except service.PublicationStateError as exc:
        raise HTTPException(409, str(exc)) from exc
    await db.commit()
    return _publication_payload(publication)


@router.post(
    "/projects/{project_id}/publications/{publication_id}/unpublish",
    response_model=PublicationResponse,
)
async def unpublish_publication(
    project_id: str,
    publication_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_MANAGE)
    publication = await repository.get_publication(
        db, project_id, publication_id, include_sources=True, lock=True
    )
    if publication is None:
        raise HTTPException(404, "Publication not found")
    try:
        await service.unpublish(db, publication=publication, actor=principal)
    except service.PublicationStateError as exc:
        raise HTTPException(409, str(exc)) from exc
    await db.commit()
    return _publication_payload(publication)


@router.get("/publications", response_model=list[PublicPublicationResponse])
async def list_publications(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    records = await repository.list_public_snapshots(db, limit=limit)
    return [_public_payload(publication, revision) for publication, revision in records]


@router.get("/publications/{slug}", response_model=PublicPublicationResponse)
async def get_publication(slug: str, db: AsyncSession = Depends(get_db)):
    record = await repository.get_public_snapshot(db, slug)
    if record is None:
        raise HTTPException(404, "Publication not found")
    return _public_payload(*record)
