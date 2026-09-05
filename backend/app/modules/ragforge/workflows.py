"""RAGForge workflow registrations and generic ingestion-run bridge."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.platform.execution import RegisteredWorkflowDefinition
from app.platform.execution.adapters import AirflowExecutionAdapter, CeleryExecutionAdapter
from app.platform.execution.gateway import execution_gateway
from app.platform.execution.model import GenericRun
from app.platform.execution.registry import ExecutionRegistry, execution_registry


RAGFORGE_INGEST_WORKFLOW_KEY = "ragforge.ingest_document"
RAGFORGE_INGEST_WORKFLOW_VERSION = "1.0.0"
CELERY_INGESTION_HANDLER = "ragforge.ingestion.workflow"


class IngestDocumentInput(BaseModel):
    ingestion_run_id: str


async def _dispatch_celery_ingestion(payload: Mapping[str, Any]) -> str | None:
    from app.workers.tasks import dispatch_ingestion_workflow

    return await dispatch_ingestion_workflow(str(payload["ingestion_run_id"]))


def ragforge_ingestion_workflow_definition(
    engine: str | None = None,
) -> RegisteredWorkflowDefinition:
    engine = (engine or settings.ORCHESTRATOR).strip().lower()
    if engine not in {"airflow", "celery"}:
        # Keep the definition executable only through a supported configured engine.
        engine = "airflow"
    handler_reference = (
        settings.AIRFLOW_INGESTION_DAG_ID
        if engine == "airflow"
        else CELERY_INGESTION_HANDLER
    )
    return RegisteredWorkflowDefinition(
        key=RAGFORGE_INGEST_WORKFLOW_KEY,
        version=RAGFORGE_INGEST_WORKFLOW_VERSION,
        capability_key="ragforge",
        name="Ingest document",
        description="Land, parse, chunk, embed, and index a RAGForge document.",
        engine=engine,
        input_model=IngestDocumentInput,
        output_schema={"type": "object", "properties": {"document_id": {"type": "string"}}},
        handler_reference=handler_reference,
        resource_requirements={"profile": "ingestion-plan"},
        artifact_types=("rag-bronze", "rag-silver", "rag-gold", "qdrant-index"),
        publication_status="published",
        external_id_prefix="ragforge",
    )


def register_ragforge_workflows(registry: ExecutionRegistry = execution_registry) -> None:
    registry.register_workflow(
        ragforge_ingestion_workflow_definition(),
        replace=True,
    )
    registry.register_adapter(AirflowExecutionAdapter())
    registry.register_adapter(CeleryExecutionAdapter())
    registry.register_handler("celery", CELERY_INGESTION_HANDLER, _dispatch_celery_ingestion)


async def create_generic_ingestion_run(
    db: AsyncSession,
    *,
    ingestion_run_id: str,
    project_id: str,
    requested_by: str,
) -> GenericRun:
    register_ragforge_workflows()
    return await execution_gateway.create_run(
        db,
        workflow_key=RAGFORGE_INGEST_WORKFLOW_KEY,
        version=RAGFORGE_INGEST_WORKFLOW_VERSION,
        project_id=project_id,
        requested_by=requested_by,
        input_data={"ingestion_run_id": ingestion_run_id},
    )
