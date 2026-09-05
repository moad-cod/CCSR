"""Persistence helpers for workflow definitions and generic runs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.execution.contracts import RegisteredWorkflowDefinition
from app.platform.execution.model import GenericRun, WorkflowDefinition


ALLOWED_RUN_TRANSITIONS = {
    "pending": frozenset({"pending", "queued", "failed", "cancelled"}),
    "queued": frozenset({"queued", "running", "failed", "cancelled"}),
    "running": frozenset({"running", "succeeded", "failed", "cancelled"}),
    "succeeded": frozenset({"succeeded"}),
    "failed": frozenset({"failed"}),
    "cancelled": frozenset({"cancelled"}),
}


async def upsert_workflow_definition(
    db: AsyncSession,
    registered: RegisteredWorkflowDefinition,
) -> WorkflowDefinition:
    result = await db.execute(
        select(WorkflowDefinition).where(
            WorkflowDefinition.workflow_key == registered.key,
            WorkflowDefinition.version == registered.version,
            WorkflowDefinition.engine == registered.engine,
        )
    )
    definition = result.scalar_one_or_none()
    values = {
        "capability_key": registered.capability_key,
        "name": registered.name,
        "description": registered.description,
        "input_schema": registered.input_model.model_json_schema(),
        "output_schema": dict(registered.output_schema),
        "resource_requirements": dict(registered.resource_requirements),
        "runtime_limit_seconds": registered.runtime_limit_seconds,
        "member_execution_allowed": registered.member_execution_allowed,
        "artifact_types": list(registered.artifact_types),
        "handler_reference": registered.handler_reference,
        "publication_status": registered.publication_status,
    }
    if definition is None:
        definition = WorkflowDefinition(
            workflow_key=registered.key,
            version=registered.version,
            engine=registered.engine,
            **values,
        )
        db.add(definition)
    else:
        for field, value in values.items():
            setattr(definition, field, value)
    await db.flush()
    return definition


async def create_run(
    db: AsyncSession,
    *,
    project_id: str,
    workflow_definition_id: str,
    requested_by: str,
    engine: str,
    input_snapshot: dict[str, Any],
) -> GenericRun:
    run = GenericRun(
        project_id=project_id,
        workflow_definition_id=workflow_definition_id,
        requested_by=requested_by,
        engine=engine,
        status="pending",
        input_snapshot=input_snapshot,
        quota_cost=Decimal("0"),
    )
    db.add(run)
    await db.flush()
    return run


async def get_run(db: AsyncSession, run_id: str) -> GenericRun | None:
    return await db.get(GenericRun, run_id)


async def list_project_runs(
    db: AsyncSession,
    project_id: str,
    *,
    limit: int = 50,
) -> list[GenericRun]:
    result = await db.execute(
        select(GenericRun)
        .where(GenericRun.project_id == project_id)
        .order_by(GenericRun.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_published_workflow_definitions(
    db: AsyncSession,
    capability_keys: tuple[str, ...],
) -> list[WorkflowDefinition]:
    if not capability_keys:
        return []
    result = await db.execute(
        select(WorkflowDefinition)
        .where(
            WorkflowDefinition.capability_key.in_(capability_keys),
            WorkflowDefinition.publication_status == "published",
        )
        .order_by(WorkflowDefinition.workflow_key, WorkflowDefinition.version)
    )
    return list(result.scalars().all())


async def update_run_status(
    db: AsyncSession,
    run_id: str,
    status: str,
    *,
    external_execution_id: str | None = None,
    error_message: str | None = None,
    output_summary: dict[str, Any] | None = None,
) -> GenericRun | None:
    run = await get_run(db, run_id)
    if run is None:
        return None
    if status not in ALLOWED_RUN_TRANSITIONS.get(run.status, frozenset()):
        raise ValueError(f"Invalid generic run status transition: {run.status} -> {status}")
    now = datetime.now(UTC).replace(tzinfo=None)
    run.status = status
    if external_execution_id is not None:
        run.external_execution_id = external_execution_id
    if status == "running" and run.started_at is None:
        run.started_at = now
    if status in {"succeeded", "failed", "cancelled"}:
        run.completed_at = now
    run.error_message = error_message
    if output_summary is not None:
        run.output_summary = output_summary
    await db.flush()
    return run
