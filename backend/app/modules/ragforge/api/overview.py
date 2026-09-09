"""Bounded aggregate reads for RAGForge workspace and project screens."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.modules.ragforge.api.documents import DocumentResponse, _document_payload
from app.modules.ragforge.api.query import QueryHistoryItem, _history_payload
from app.modules.ragforge.models.document import Document
from app.modules.ragforge.models.ingestion_run import IngestionRun
from app.modules.ragforge.models.query_log import QueryLog
from app.modules.ragforge.repositories import project_configs as project_config_repository
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import PROJECT_ACTION_READ, authorize_project
from app.repositories import projects as project_repository


router = APIRouter()
TERMINAL_INGESTION_STATUSES = frozenset({"indexed", "failed", "cancelled"})
WORKSPACE_INCLUDE_VALUES = frozenset({"documents", "runs", "history"})


class RAGRunSummary(BaseModel):
    ingestion_run_id: str
    project_id: str
    document_id: str
    document_version_id: str
    status: str
    airflow_dag_run_id: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class RAGProjectSummary(BaseModel):
    project_id: str
    document_count: int = 0
    indexed_document_count: int = 0
    active_run_count: int = 0
    failed_run_count: int = 0


class RAGWorkspaceOverviewResponse(BaseModel):
    summaries: list[RAGProjectSummary]
    documents: list[DocumentResponse] = Field(default_factory=list)
    runs: list[RAGRunSummary] = Field(default_factory=list)
    history: list[QueryHistoryItem] = Field(default_factory=list)


class RAGProjectOverviewResponse(BaseModel):
    summary: RAGProjectSummary
    query_count: int
    primary_document: DocumentResponse | None
    recent_runs: list[RAGRunSummary]
    latest_query: QueryHistoryItem | None


def _run_payload(run: IngestionRun) -> RAGRunSummary:
    return RAGRunSummary(
        ingestion_run_id=run.id,
        project_id=run.project_id,
        document_id=run.document_id,
        document_version_id=run.document_version_id,
        status=run.status,
        airflow_dag_run_id=run.airflow_dag_run_id,
        error_message=run.error_message,
        created_at=run.created_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


def _parse_include(include: str) -> frozenset[str]:
    requested = frozenset(value.strip() for value in include.split(",") if value.strip())
    unsupported = requested - WORKSPACE_INCLUDE_VALUES
    if unsupported:
        raise HTTPException(422, f"Unsupported overview include: {', '.join(sorted(unsupported))}")
    return requested


async def _rag_project_ids(db: AsyncSession, user: dict) -> list[str]:
    projects = await project_repository.list_accessible_projects(
        db,
        user_id=user["user_id"],
        global_role=user["global_role"],
    )
    return [
        str(project.id)
        for project in projects
        if any(
            association.capability_key == "ragforge"
            for association in project.__dict__.get("capabilities", ())
        )
    ]


async def _summary_rows(
    db: AsyncSession,
    project_ids: list[str],
) -> dict[str, RAGProjectSummary]:
    summaries = {
        project_id: RAGProjectSummary(project_id=project_id)
        for project_id in project_ids
    }
    document_result = await db.execute(
        select(
            Document.project_id,
            func.count(Document.id),
            func.sum(case((Document.status == "indexed", 1), else_=0)),
        )
        .where(
            Document.project_id.in_(project_ids),
            Document.deleted_at.is_(None),
        )
        .group_by(Document.project_id)
    )
    for project_id, document_count, indexed_count in document_result.all():
        summary = summaries[str(project_id)]
        summary.document_count = int(document_count or 0)
        summary.indexed_document_count = int(indexed_count or 0)

    run_result = await db.execute(
        select(
            IngestionRun.project_id,
            func.sum(
                case((IngestionRun.status.not_in(TERMINAL_INGESTION_STATUSES), 1), else_=0)
            ),
            func.sum(case((IngestionRun.status == "failed", 1), else_=0)),
        )
        .where(IngestionRun.project_id.in_(project_ids))
        .group_by(IngestionRun.project_id)
    )
    for project_id, active_count, failed_count in run_result.all():
        summary = summaries[str(project_id)]
        summary.active_run_count = int(active_count or 0)
        summary.failed_run_count = int(failed_count or 0)
    return summaries


@router.get("/workspace/overview", response_model=RAGWorkspaceOverviewResponse)
async def workspace_overview(
    include: str = Query(default="", description="Comma-separated documents,runs,history"),
    record_limit: int = Query(default=500, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    requested = _parse_include(include)
    project_ids = await _rag_project_ids(db, user)
    if not project_ids:
        return RAGWorkspaceOverviewResponse(summaries=[])

    summaries = await _summary_rows(db, project_ids)
    documents: list[DocumentResponse] = []
    runs: list[RAGRunSummary] = []
    history: list[QueryHistoryItem] = []
    if "documents" in requested:
        result = await db.execute(
            select(Document)
            .where(
                Document.project_id.in_(project_ids),
                Document.deleted_at.is_(None),
            )
            .order_by(Document.updated_at.desc())
            .limit(record_limit)
        )
        documents = [_document_payload(document) for document in result.scalars().all()]
    if "runs" in requested:
        result = await db.execute(
            select(IngestionRun)
            .where(IngestionRun.project_id.in_(project_ids))
            .order_by(IngestionRun.created_at.desc())
            .limit(record_limit)
        )
        runs = [_run_payload(run) for run in result.scalars().all()]
    if "history" in requested:
        result = await db.execute(
            select(QueryLog)
            .where(QueryLog.project_id.in_(project_ids))
            .order_by(QueryLog.created_at.desc())
            .limit(record_limit)
        )
        history = [_history_payload(query_log) for query_log in result.scalars().all()]
    return RAGWorkspaceOverviewResponse(
        summaries=list(summaries.values()),
        documents=documents,
        runs=runs,
        history=history,
    )


@router.get("/projects/{project_id}/overview", response_model=RAGProjectOverviewResponse)
async def project_overview(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, user, action=PROJECT_ACTION_READ)
    rag_project = await project_config_repository.get_rag_project(db, project_id)
    if rag_project is None:
        raise HTTPException(404, "RAGForge capability is not enabled for this project")

    summaries = await _summary_rows(db, [project_id])
    document_result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id, Document.deleted_at.is_(None))
        .order_by(Document.updated_at.desc())
        .limit(1)
    )
    run_result = await db.execute(
        select(IngestionRun)
        .where(IngestionRun.project_id == project_id)
        .order_by(IngestionRun.created_at.desc())
        .limit(5)
    )
    query_result = await db.execute(
        select(QueryLog)
        .where(QueryLog.project_id == project_id)
        .order_by(QueryLog.created_at.desc())
        .limit(1)
    )
    query_count = await db.scalar(
        select(func.count()).select_from(QueryLog).where(QueryLog.project_id == project_id)
    )
    primary_document = document_result.scalar_one_or_none()
    latest_query = query_result.scalar_one_or_none()
    return RAGProjectOverviewResponse(
        summary=summaries[project_id],
        query_count=int(query_count or 0),
        primary_document=(
            _document_payload(primary_document) if primary_document is not None else None
        ),
        recent_runs=[_run_payload(run) for run in run_result.scalars().all()],
        latest_query=_history_payload(latest_query) if latest_query is not None else None,
    )
