"""Read APIs for approved workflows and durable generic runs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import PROJECT_ACTION_READ, authorize_project
from app.platform.capabilities import repository as capability_repository
from app.platform.execution import repository


router = APIRouter()


class WorkflowDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_key: str
    version: str
    capability_key: str
    name: str
    description: str
    engine: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    resource_requirements: dict[str, Any]
    runtime_limit_seconds: int | None
    member_execution_allowed: bool
    artifact_types: list[str]
    publication_status: str


class GenericRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    workflow_definition_id: str
    requested_by: str
    experiment_id: str | None
    engine: str
    external_execution_id: str | None
    status: str
    input_snapshot: dict[str, Any]
    output_summary: dict[str, Any] | None
    quota_cost: Decimal
    started_at: datetime | None
    completed_at: datetime | None
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


@router.get("/workflows", response_model=list[WorkflowDefinitionResponse])
async def list_project_workflows(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_READ)
    capability_keys = await capability_repository.list_project_capability_keys(db, project_id)
    return await repository.list_published_workflow_definitions(db, capability_keys)


@router.get("/runs", response_model=list[GenericRunResponse])
async def list_runs(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    await authorize_project(db, project_id, principal, action=PROJECT_ACTION_READ)
    return await repository.list_project_runs(db, project_id, limit=limit)


@router.get("/runs/{run_id}", response_model=GenericRunResponse)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    principal: dict = Depends(get_current_user),
):
    run = await repository.get_run(db, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    await authorize_project(db, run.project_id, principal, action=PROJECT_ACTION_READ)
    return run
