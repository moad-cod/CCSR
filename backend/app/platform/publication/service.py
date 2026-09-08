from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.audit import record_audit_event
from app.platform.publication import repository
from app.platform.publication.model import Publication, PublicationRevision


class PublicationStateError(ValueError):
    pass


class PublicationNotFoundError(PublicationStateError):
    pass


def _public_snapshot(publication: Publication) -> dict[str, Any]:
    private_findings = [
        finding.id
        for finding in publication.findings
        if finding.visibility != "public" or finding.status != "validated"
    ]
    if private_findings:
        raise PublicationStateError(
            "Only validated public findings can be published"
        )
    private_artifacts = [
        artifact.id
        for artifact in publication.artifacts
        if artifact.visibility != "public"
    ]
    if private_artifacts:
        raise PublicationStateError("Only public artifacts can be published")

    study = publication.research_study
    return {
        "schema_version": 1,
        "project": {
            "id": publication.project.id,
            "name": publication.project.name,
        },
        "publication": {
            "id": publication.id,
            "slug": publication.slug,
            "title": publication.title,
            "summary": publication.summary,
        },
        "research_study": (
            {
                "id": study.id,
                "slug": study.slug,
                "title": study.title,
                "abstract": study.abstract,
                "objective": study.objective,
                "methodology": study.methodology,
                "status": study.status,
                "questions": [
                    {
                        "question": question.question,
                        "rationale": question.rationale,
                        "ordinal": question.ordinal,
                    }
                    for question in study.questions
                ],
                "hypotheses": [
                    {
                        "statement": hypothesis.statement,
                        "rationale": hypothesis.rationale,
                        "status": hypothesis.status,
                    }
                    for hypothesis in study.hypotheses
                ],
                "experiments": [
                    {
                        "id": experiment.id,
                        "slug": experiment.slug,
                        "name": experiment.name,
                        "objective": experiment.objective,
                        "status": experiment.status,
                    }
                    for experiment in study.experiments
                ],
            }
            if study is not None
            else None
        ),
        "findings": [
            {
                "id": finding.id,
                "experiment_id": finding.experiment_id,
                "title": finding.title,
                "statement": finding.statement,
                "evidence_summary": finding.evidence_summary,
            }
            for finding in publication.findings
        ],
        "artifacts": [
            {
                "id": artifact.id,
                "type": artifact.artifact_type,
                "version": artifact.version,
                "checksum": artifact.checksum,
                "size_bytes": artifact.size_bytes,
                "metadata": dict(artifact.artifact_metadata),
            }
            for artifact in publication.artifacts
        ],
    }


async def publish(
    db: AsyncSession,
    *,
    project_id: str,
    publication_id: str,
    actor: dict,
) -> Publication:
    publication = await repository.get_publication(
        db,
        project_id,
        publication_id,
        include_sources=True,
        lock=True,
    )
    if publication is None:
        raise PublicationNotFoundError("Publication not found")
    if publication.state != "draft":
        raise PublicationStateError("Only a draft publication can be published")

    revision_number = (publication.current_revision_number or 0) + 1
    revision = PublicationRevision(
        publication_id=publication.id,
        revision_number=revision_number,
        snapshot=_public_snapshot(publication),
        published_by=actor["user_id"],
    )
    db.add(revision)
    publication.state = "public"
    publication.current_revision_number = revision_number
    publication.published_at = datetime.now(UTC).replace(tzinfo=None)
    await record_audit_event(
        db,
        actor_user_id=actor["user_id"],
        actor_global_role=actor["global_role"],
        action="publication.publish",
        target_type="publication",
        target_id=publication.id,
        project_id=publication.project_id,
        details={"slug": publication.slug, "revision": revision_number},
    )
    await db.flush()
    return publication


async def unpublish(
    db: AsyncSession,
    *,
    publication: Publication,
    actor: dict,
) -> Publication:
    if publication.state != "public":
        raise PublicationStateError("Only a public publication can be unpublished")
    publication.state = "draft"
    await record_audit_event(
        db,
        actor_user_id=actor["user_id"],
        actor_global_role=actor["global_role"],
        action="publication.unpublish",
        target_type="publication",
        target_id=publication.id,
        project_id=publication.project_id,
        details={"slug": publication.slug},
    )
    await db.flush()
    return publication
