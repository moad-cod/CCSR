"""Application boundary for validated, durable workflow execution."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.platform.capabilities import repository as capability_repository
from app.platform.execution import repository
from app.platform.execution.model import GenericRun, WorkflowDefinition
from app.platform.execution.registry import ExecutionRegistry, execution_registry


logger = logging.getLogger(__name__)


class ExecutionGateway:
    def __init__(self, registry: ExecutionRegistry) -> None:
        self.registry = registry

    async def create_run(
        self,
        db: AsyncSession,
        *,
        workflow_key: str,
        project_id: str,
        requested_by: str,
        input_data: dict[str, Any],
        version: str | None = None,
    ) -> GenericRun:
        definition = self.registry.get_workflow(workflow_key, version)
        if definition is None or definition.publication_status != "published":
            raise ValueError("Workflow is not registered for execution")
        enabled = await capability_repository.list_project_capability_keys(db, project_id)
        if definition.capability_key not in enabled:
            raise ValueError("Workflow capability is not enabled for this project")
        try:
            validated = definition.input_model.model_validate(input_data)
        except ValidationError as exc:
            raise ValueError("Workflow input is invalid") from exc
        durable_definition = await repository.upsert_workflow_definition(db, definition)
        return await repository.create_run(
            db,
            project_id=project_id,
            workflow_definition_id=durable_definition.id,
            requested_by=requested_by,
            engine=definition.engine,
            input_snapshot=validated.model_dump(mode="json"),
        )

    async def dispatch(self, run_id: str) -> str | None:
        async with AsyncSessionLocal() as db:
            run = await repository.get_run(db, run_id)
            if run is None:
                raise LookupError(f"Generic run {run_id} does not exist")
            definition_row = await db.get(WorkflowDefinition, run.workflow_definition_id)
            if definition_row is None:
                raise LookupError(f"Workflow definition for run {run_id} does not exist")
            definition = self.registry.get_workflow(
                definition_row.workflow_key,
                definition_row.version,
            )
            if definition is None:
                raise RuntimeError("The run's workflow version is not registered")
            if run.engine != definition.engine:
                raise RuntimeError("The durable run engine does not match its registered workflow")
            adapter = self.registry.adapter_for(definition.engine)
            if adapter is None:
                raise RuntimeError(f"No {definition.engine} execution adapter is registered")
            handler = self.registry.handler_for(
                definition.engine,
                definition.handler_reference,
            )
            try:
                receipt = await adapter.dispatch(definition, run.input_snapshot, handler)
            except Exception as exc:
                await repository.update_run_status(
                    db,
                    run.id,
                    "failed",
                    error_message="Execution engine could not accept the workflow",
                )
                await db.commit()
                logger.exception("Workflow dispatch failed for generic run %s", run.id)
                raise exc
            if receipt is None:
                await repository.update_run_status(
                    db,
                    run.id,
                    "failed",
                    error_message="Execution engine did not accept the workflow",
                )
                await db.commit()
                return None
            await repository.update_run_status(
                db,
                run.id,
                "queued",
                external_execution_id=receipt.external_execution_id,
            )
            await db.commit()
            return receipt.external_execution_id


execution_gateway = ExecutionGateway(execution_registry)
