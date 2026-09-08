from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import (
    PROJECT_ACTION_READ,
    PROJECT_ACTION_WRITE,
    ProjectAction,
    authorize_project,
)
from app.platform.research import repository
from app.platform.research.model import ResearchStudy
from app.platform.research.validation import clean_required_text


router = APIRouter()


class StudyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    slug: str | None = Field(default=None, max_length=120)
    abstract: str | None = Field(default=None, max_length=20_000)
    objective: str | None = Field(default=None, max_length=20_000)
    methodology: str | None = Field(default=None, max_length=50_000)
    status: Literal["planned", "active", "completed", "archived"] = "planned"

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_required_text(value)


class StudyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    abstract: str | None = Field(default=None, max_length=20_000)
    objective: str | None = Field(default=None, max_length=20_000)
    methodology: str | None = Field(default=None, max_length=50_000)
    status: Literal["planned", "active", "completed", "archived"] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return clean_required_text(value) if value is not None else None


class StudyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    slug: str
    title: str
    abstract: str | None
    objective: str | None
    methodology: str | None
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class QuestionCreate(BaseModel):
    question: str = Field(min_length=1, max_length=10_000)
    rationale: str | None = Field(default=None, max_length=20_000)
    ordinal: int = Field(default=0, ge=0)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return clean_required_text(value)


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    study_id: str
    question: str
    rationale: str | None
    ordinal: int
    created_at: datetime
    updated_at: datetime


class HypothesisCreate(BaseModel):
    question_id: str | None = None
    statement: str = Field(min_length=1, max_length=20_000)
    rationale: str | None = Field(default=None, max_length=20_000)
    status: Literal["proposed", "supported", "rejected", "inconclusive"] = (
        "proposed"
    )

    @field_validator("statement")
    @classmethod
    def validate_statement(cls, value: str) -> str:
        return clean_required_text(value)


class HypothesisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    study_id: str
    question_id: str | None
    statement: str
    rationale: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class DatasetCreate(BaseModel):
    artifact_id: str
    role: Literal["input", "reference", "evaluation", "output"] = "input"
    description: str | None = Field(default=None, max_length=20_000)


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    study_id: str
    artifact_id: str
    role: str
    description: str | None
    created_at: datetime


class ExperimentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    slug: str | None = Field(default=None, max_length=120)
    objective: str | None = Field(default=None, max_length=20_000)
    status: Literal["planned", "running", "completed", "failed", "cancelled"] = (
        "planned"
    )
    configuration: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return clean_required_text(value)


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    study_id: str
    slug: str
    name: str
    objective: str | None
    status: str
    configuration: dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime


class ComparisonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    experiment_ids: list[str] = Field(min_length=2, max_length=50)
    criteria: dict[str, Any] = Field(default_factory=dict)
    result_summary: dict[str, Any] = Field(default_factory=dict)
    conclusion: str | None = Field(default=None, max_length=50_000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return clean_required_text(value)


class ComparisonResponse(BaseModel):
    id: str
    study_id: str
    name: str
    experiment_ids: list[str]
    criteria: dict[str, Any]
    result_summary: dict[str, Any]
    conclusion: str | None
    created_at: datetime
    updated_at: datetime


class FindingCreate(BaseModel):
    experiment_id: str | None = None
    title: str = Field(min_length=1, max_length=240)
    statement: str = Field(min_length=1, max_length=50_000)
    evidence_summary: str | None = Field(default=None, max_length=50_000)
    status: Literal["draft", "validated", "superseded"] = "draft"
    visibility: Literal["private", "public"] = "private"

    @field_validator("title", "statement")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return clean_required_text(value)


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    study_id: str
    experiment_id: str | None
    title: str
    statement: str
    evidence_summary: str | None
    status: str
    visibility: str
    created_at: datetime
    updated_at: datetime


class StudyDetailResponse(StudyResponse):
    questions: list[QuestionResponse]
    hypotheses: list[HypothesisResponse]
    datasets: list[DatasetResponse]
    experiments: list[ExperimentResponse]
    comparisons: list[ComparisonResponse]
    findings: list[FindingResponse]


async def _authorized_study(
    db: AsyncSession,
    principal: dict,
    project_id: str,
    study_id: str,
    action: ProjectAction,
    *,
    include_graph: bool = False,
) -> ResearchStudy:
    await authorize_project(db, project_id, principal, action=action)
    study = await repository.get_study(
        db,
        project_id,
        study_id,
        include_graph=include_graph,
    )
    if study is None:
        raise HTTPException(404, "Research study not found")
    return study


def _comparison_payload(comparison) -> ComparisonResponse:
    return ComparisonResponse(
        id=comparison.id,
        study_id=comparison.study_id,
        name=comparison.name,
        experiment_ids=sorted(experiment.id for experiment in comparison.experiments),
        criteria=dict(comparison.criteria),
        result_summary=dict(comparison.result_summary),
        conclusion=comparison.conclusion,
        created_at=comparison.created_at,
        updated_at=comparison.updated_at,
    )


def _study_detail_payload(study: ResearchStudy) -> StudyDetailResponse:
    return StudyDetailResponse(
        **StudyResponse.model_validate(study).model_dump(),
        questions=[QuestionResponse.model_validate(item) for item in study.questions],
        hypotheses=[
            HypothesisResponse.model_validate(item) for item in study.hypotheses
        ],
        datasets=[DatasetResponse.model_validate(item) for item in study.datasets],
        experiments=[
            ExperimentResponse.model_validate(item) for item in study.experiments
        ],
        comparisons=[_comparison_payload(item) for item in study.comparisons],
        findings=[FindingResponse.model_validate(item) for item in study.findings],
    )


@router.post(
    "/projects/{project_id}/research/studies",
    response_model=StudyResponse,
    status_code=201,
)
async def create_study(
    project_id: str,
    body: StudyCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_WRITE)
    try:
        study = await repository.create_study(
            db,
            project_id=project_id,
            created_by=principal["user_id"],
            **body.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await db.commit()
    return study


@router.get(
    "/projects/{project_id}/research/studies",
    response_model=list[StudyResponse],
)
async def list_studies(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_READ)
    return await repository.list_project_studies(db, project_id)


@router.get(
    "/projects/{project_id}/research/experiments",
    response_model=list[ExperimentResponse],
)
async def list_experiments(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_READ)
    return await repository.list_project_experiments(db, project_id)


@router.get(
    "/projects/{project_id}/research/studies/{study_id}",
    response_model=StudyDetailResponse,
)
async def get_study(
    project_id: str,
    study_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db,
        principal,
        project_id,
        study_id,
        PROJECT_ACTION_READ,
        include_graph=True,
    )
    return _study_detail_payload(study)


@router.patch(
    "/projects/{project_id}/research/studies/{study_id}",
    response_model=StudyResponse,
)
async def update_study(
    project_id: str,
    study_id: str,
    body: StudyUpdate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(study, field, value)
    await db.commit()
    return study


@router.post(
    "/projects/{project_id}/research/studies/{study_id}/questions",
    response_model=QuestionResponse,
    status_code=201,
)
async def create_question(
    project_id: str,
    study_id: str,
    body: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    question = await repository.add_question(db, study_id=study.id, **body.model_dump())
    await db.commit()
    return question


@router.post(
    "/projects/{project_id}/research/studies/{study_id}/hypotheses",
    response_model=HypothesisResponse,
    status_code=201,
)
async def create_hypothesis(
    project_id: str,
    study_id: str,
    body: HypothesisCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    try:
        record = await repository.add_hypothesis(
            db, study=study, **body.model_dump()
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await db.commit()
    return record


@router.post(
    "/projects/{project_id}/research/studies/{study_id}/datasets",
    response_model=DatasetResponse,
    status_code=201,
)
async def create_dataset(
    project_id: str,
    study_id: str,
    body: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    try:
        record = await repository.add_dataset(db, study=study, **body.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await db.commit()
    return record


@router.post(
    "/projects/{project_id}/research/studies/{study_id}/experiments",
    response_model=ExperimentResponse,
    status_code=201,
)
async def create_experiment(
    project_id: str,
    study_id: str,
    body: ExperimentCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    try:
        record = await repository.add_experiment(
            db,
            study=study,
            created_by=principal["user_id"],
            **body.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await db.commit()
    return record


@router.post(
    "/projects/{project_id}/research/studies/{study_id}/comparisons",
    response_model=ComparisonResponse,
    status_code=201,
)
async def create_comparison(
    project_id: str,
    study_id: str,
    body: ComparisonCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    try:
        record = await repository.add_comparison(
            db, study=study, **body.model_dump()
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await db.commit()
    return _comparison_payload(record)


@router.post(
    "/projects/{project_id}/research/studies/{study_id}/findings",
    response_model=FindingResponse,
    status_code=201,
)
async def create_finding(
    project_id: str,
    study_id: str,
    body: FindingCreate,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    study = await _authorized_study(
        db, principal, project_id, study_id, PROJECT_ACTION_WRITE
    )
    try:
        record = await repository.add_finding(db, study=study, **body.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await db.commit()
    return record
