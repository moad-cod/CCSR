from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.platform.artifacts.model import Artifact
from app.platform.research.model import (
    Experiment,
    ExperimentComparison,
    ResearchDataset,
    ResearchFinding,
    ResearchHypothesis,
    ResearchQuestion,
    ResearchStudy,
)
from app.platform.research.slugs import normalize_slug


STUDY_GRAPH_OPTIONS = (
    selectinload(ResearchStudy.questions),
    selectinload(ResearchStudy.hypotheses),
    selectinload(ResearchStudy.datasets).selectinload(ResearchDataset.artifact),
    selectinload(ResearchStudy.experiments),
    selectinload(ResearchStudy.comparisons).selectinload(
        ExperimentComparison.experiments
    ),
    selectinload(ResearchStudy.findings),
)


async def _available_study_slug(
    db: AsyncSession,
    project_id: str,
    preferred: str,
) -> str:
    base = normalize_slug(preferred)
    candidate = base
    suffix = 2
    while await db.scalar(
        select(ResearchStudy.id).where(
            ResearchStudy.project_id == project_id,
            ResearchStudy.slug == candidate,
        )
    ):
        candidate = f"{base[:110]}-{suffix}"
        suffix += 1
    return candidate


async def _available_experiment_slug(
    db: AsyncSession,
    study_id: str,
    preferred: str,
) -> str:
    base = normalize_slug(preferred)
    candidate = base
    suffix = 2
    while await db.scalar(
        select(Experiment.id).where(
            Experiment.study_id == study_id,
            Experiment.slug == candidate,
        )
    ):
        candidate = f"{base[:110]}-{suffix}"
        suffix += 1
    return candidate


async def create_study(
    db: AsyncSession,
    *,
    project_id: str,
    created_by: str,
    title: str,
    slug: str | None = None,
    abstract: str | None = None,
    objective: str | None = None,
    methodology: str | None = None,
    status: str = "planned",
) -> ResearchStudy:
    study = ResearchStudy(
        project_id=project_id,
        created_by=created_by,
        slug=await _available_study_slug(db, project_id, slug or title),
        title=title,
        abstract=abstract,
        objective=objective,
        methodology=methodology,
        status=status,
    )
    db.add(study)
    await db.flush()
    return study


async def list_project_studies(
    db: AsyncSession,
    project_id: str,
) -> list[ResearchStudy]:
    result = await db.execute(
        select(ResearchStudy)
        .where(ResearchStudy.project_id == project_id)
        .order_by(ResearchStudy.created_at.desc())
    )
    return list(result.scalars().all())


async def list_project_experiments(
    db: AsyncSession,
    project_id: str,
) -> list[Experiment]:
    result = await db.execute(
        select(Experiment)
        .join(ResearchStudy, ResearchStudy.id == Experiment.study_id)
        .where(ResearchStudy.project_id == project_id)
        .order_by(Experiment.created_at.desc())
    )
    return list(result.scalars().all())


async def get_study(
    db: AsyncSession,
    project_id: str,
    study_id: str,
    *,
    include_graph: bool = False,
) -> ResearchStudy | None:
    query = select(ResearchStudy).where(
        ResearchStudy.id == study_id,
        ResearchStudy.project_id == project_id,
    )
    if include_graph:
        query = query.options(*STUDY_GRAPH_OPTIONS)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def add_question(
    db: AsyncSession,
    *,
    study_id: str,
    question: str,
    rationale: str | None,
    ordinal: int,
) -> ResearchQuestion:
    record = ResearchQuestion(
        study_id=study_id,
        question=question,
        rationale=rationale,
        ordinal=ordinal,
    )
    db.add(record)
    await db.flush()
    return record


async def add_hypothesis(
    db: AsyncSession,
    *,
    study: ResearchStudy,
    statement: str,
    rationale: str | None,
    status: str,
    question_id: str | None,
) -> ResearchHypothesis:
    if question_id is not None:
        question = await db.get(ResearchQuestion, question_id)
        if question is None or question.study_id != study.id:
            raise ValueError("Research question does not belong to this study")
    record = ResearchHypothesis(
        study_id=study.id,
        question_id=question_id,
        statement=statement,
        rationale=rationale,
        status=status,
    )
    db.add(record)
    await db.flush()
    return record


async def add_dataset(
    db: AsyncSession,
    *,
    study: ResearchStudy,
    artifact_id: str,
    role: str,
    description: str | None,
) -> ResearchDataset:
    artifact = await db.get(Artifact, artifact_id)
    if artifact is None or artifact.project_id != study.project_id:
        raise ValueError("Dataset artifact does not belong to this project")
    record = ResearchDataset(
        study_id=study.id,
        artifact_id=artifact_id,
        role=role,
        description=description,
    )
    db.add(record)
    await db.flush()
    return record


async def add_experiment(
    db: AsyncSession,
    *,
    study: ResearchStudy,
    created_by: str,
    name: str,
    slug: str | None,
    objective: str | None,
    status: str,
    configuration: dict[str, Any],
) -> Experiment:
    record = Experiment(
        study_id=study.id,
        created_by=created_by,
        slug=await _available_experiment_slug(db, study.id, slug or name),
        name=name,
        objective=objective,
        status=status,
        configuration=configuration,
    )
    db.add(record)
    await db.flush()
    return record


async def add_comparison(
    db: AsyncSession,
    *,
    study: ResearchStudy,
    name: str,
    experiment_ids: Sequence[str],
    criteria: dict[str, Any],
    result_summary: dict[str, Any],
    conclusion: str | None,
) -> ExperimentComparison:
    unique_ids = tuple(dict.fromkeys(experiment_ids))
    if len(unique_ids) < 2:
        raise ValueError("A comparison requires at least two experiments")
    result = await db.execute(
        select(Experiment).where(
            Experiment.study_id == study.id,
            Experiment.id.in_(unique_ids),
        )
    )
    experiments = list(result.scalars().all())
    if len(experiments) != len(unique_ids):
        raise ValueError("Every comparison experiment must belong to this study")
    record = ExperimentComparison(
        study_id=study.id,
        name=name,
        criteria=criteria,
        result_summary=result_summary,
        conclusion=conclusion,
        experiments=experiments,
    )
    db.add(record)
    await db.flush()
    return record


async def add_finding(
    db: AsyncSession,
    *,
    study: ResearchStudy,
    title: str,
    statement: str,
    evidence_summary: str | None,
    status: str,
    visibility: str,
    experiment_id: str | None,
) -> ResearchFinding:
    if experiment_id is not None:
        experiment = await db.get(Experiment, experiment_id)
        if experiment is None or experiment.study_id != study.id:
            raise ValueError("Finding experiment does not belong to this study")
    record = ResearchFinding(
        study_id=study.id,
        experiment_id=experiment_id,
        title=title,
        statement=statement,
        evidence_summary=evidence_summary,
        status=status,
        visibility=visibility,
    )
    db.add(record)
    await db.flush()
    return record
