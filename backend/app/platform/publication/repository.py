from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.platform.artifacts.model import Artifact
from app.platform.publication.model import Publication, PublicationRevision
from app.platform.research.model import ResearchFinding, ResearchStudy
from app.platform.research.slugs import normalize_slug


PUBLICATION_SOURCE_OPTIONS = (
    selectinload(Publication.project),
    selectinload(Publication.research_study).selectinload(ResearchStudy.questions),
    selectinload(Publication.research_study).selectinload(ResearchStudy.hypotheses),
    selectinload(Publication.research_study).selectinload(ResearchStudy.experiments),
    selectinload(Publication.findings),
    selectinload(Publication.artifacts),
)


async def _available_slug(db: AsyncSession, preferred: str) -> str:
    base = normalize_slug(preferred)
    candidate = base
    suffix = 2
    while await db.scalar(select(Publication.id).where(Publication.slug == candidate)):
        candidate = f"{base[:110]}-{suffix}"
        suffix += 1
    return candidate


async def _selected_findings(
    db: AsyncSession,
    *,
    project_id: str,
    study_id: str | None,
    finding_ids: Sequence[str],
) -> list[ResearchFinding]:
    unique_ids = tuple(dict.fromkeys(finding_ids))
    if not unique_ids:
        return []
    if study_id is None:
        raise ValueError("A research study is required when selecting findings")
    result = await db.execute(
        select(ResearchFinding)
        .join(ResearchStudy, ResearchStudy.id == ResearchFinding.study_id)
        .where(
            ResearchFinding.id.in_(unique_ids),
            ResearchFinding.study_id == study_id,
            ResearchStudy.project_id == project_id,
        )
    )
    records = list(result.scalars().all())
    if len(records) != len(unique_ids):
        raise ValueError("Every finding must belong to the publication study")
    return records


async def _selected_artifacts(
    db: AsyncSession,
    *,
    project_id: str,
    artifact_ids: Sequence[str],
) -> list[Artifact]:
    unique_ids = tuple(dict.fromkeys(artifact_ids))
    if not unique_ids:
        return []
    result = await db.execute(
        select(Artifact).where(
            Artifact.id.in_(unique_ids),
            Artifact.project_id == project_id,
        )
    )
    records = list(result.scalars().all())
    if len(records) != len(unique_ids):
        raise ValueError("Every artifact must belong to the publication project")
    return records


async def create_publication(
    db: AsyncSession,
    *,
    project_id: str,
    created_by: str,
    title: str,
    slug: str | None,
    summary: str | None,
    state: str,
    research_study_id: str | None,
    finding_ids: Sequence[str],
    artifact_ids: Sequence[str],
) -> Publication:
    if state == "public":
        raise ValueError("Use the publish action to make a publication public")
    if research_study_id is not None:
        study = await db.get(ResearchStudy, research_study_id)
        if study is None or study.project_id != project_id:
            raise ValueError("Research study does not belong to this project")
    findings = await _selected_findings(
        db,
        project_id=project_id,
        study_id=research_study_id,
        finding_ids=finding_ids,
    )
    artifacts = await _selected_artifacts(
        db,
        project_id=project_id,
        artifact_ids=artifact_ids,
    )
    publication = Publication(
        project_id=project_id,
        research_study_id=research_study_id,
        slug=await _available_slug(db, slug or title),
        title=title,
        summary=summary,
        state=state,
        created_by=created_by,
        findings=findings,
        artifacts=artifacts,
    )
    db.add(publication)
    await db.flush()
    return publication


async def get_publication(
    db: AsyncSession,
    project_id: str,
    publication_id: str,
    *,
    include_sources: bool = False,
    lock: bool = False,
) -> Publication | None:
    query = select(Publication).where(
        Publication.id == publication_id,
        Publication.project_id == project_id,
    )
    if include_sources:
        query = query.options(*PUBLICATION_SOURCE_OPTIONS)
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_project_publications(
    db: AsyncSession,
    project_id: str,
) -> list[Publication]:
    result = await db.execute(
        select(Publication)
        .where(Publication.project_id == project_id)
        .options(selectinload(Publication.findings), selectinload(Publication.artifacts))
        .order_by(Publication.updated_at.desc())
    )
    return list(result.scalars().all())


async def replace_selections(
    db: AsyncSession,
    publication: Publication,
    *,
    finding_ids: Sequence[str] | None,
    artifact_ids: Sequence[str] | None,
) -> None:
    if finding_ids is not None:
        publication.findings = await _selected_findings(
            db,
            project_id=publication.project_id,
            study_id=publication.research_study_id,
            finding_ids=finding_ids,
        )
    if artifact_ids is not None:
        publication.artifacts = await _selected_artifacts(
            db,
            project_id=publication.project_id,
            artifact_ids=artifact_ids,
        )
    await db.flush()


async def list_public_snapshots(
    db: AsyncSession,
    *,
    limit: int,
) -> list[tuple[Publication, PublicationRevision]]:
    result = await db.execute(
        select(Publication, PublicationRevision)
        .join(
            PublicationRevision,
            and_(
                PublicationRevision.publication_id == Publication.id,
                PublicationRevision.revision_number
                == Publication.current_revision_number,
            ),
        )
        .where(Publication.state == "public")
        .order_by(Publication.published_at.desc())
        .limit(limit)
    )
    return list(result.tuples().all())


async def get_public_snapshot(
    db: AsyncSession,
    slug: str,
) -> tuple[Publication, PublicationRevision] | None:
    result = await db.execute(
        select(Publication, PublicationRevision)
        .join(
            PublicationRevision,
            and_(
                PublicationRevision.publication_id == Publication.id,
                PublicationRevision.revision_number
                == Publication.current_revision_number,
            ),
        )
        .where(Publication.slug == slug, Publication.state == "public")
    )
    return result.tuples().one_or_none()
