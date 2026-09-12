"""RAGForge workflow registrations and generic ingestion-run bridge."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.platform.execution.contracts import RegisteredWorkflowDefinition
from app.platform.execution.gateway import execution_gateway
from app.platform.execution.model import GenericRun
from app.platform.execution.registry import ExecutionRegistry, execution_registry
from app.platform.artifacts import register_artifact


RAGFORGE_INGEST_WORKFLOW_KEY = "ragforge.ingest_document"
RAGFORGE_INGEST_WORKFLOW_VERSION = "1.0.0"
CELERY_INGESTION_HANDLER = "ragforge.ingestion.workflow"


class IngestDocumentInput(BaseModel):
    ingestion_run_id: str
    input_size_bytes: int | None = Field(default=None, ge=0)


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
        member_execution_allowed=True,
        publication_status="published",
        external_id_prefix="ragforge",
    )


def register_ragforge_workflows(registry: ExecutionRegistry = execution_registry) -> None:
    """Register RAGForge workflow definitions without concrete adapters."""
    registry.register_workflow(
        ragforge_ingestion_workflow_definition(),
        replace=True,
    )


async def create_generic_ingestion_run(
    db: AsyncSession,
    *,
    ingestion_run_id: str,
    project_id: str,
    requested_by: str,
    input_size_bytes: int | None = None,
) -> GenericRun:
    register_ragforge_workflows()
    return await execution_gateway.create_run(
        db,
        workflow_key=RAGFORGE_INGEST_WORKFLOW_KEY,
        version=RAGFORGE_INGEST_WORKFLOW_VERSION,
        project_id=project_id,
        requested_by=requested_by,
        input_data={
            "ingestion_run_id": ingestion_run_id,
            "input_size_bytes": input_size_bytes,
        },
    )


async def register_ingestion_artifact(
    db: AsyncSession,
    *,
    generic_run_id: str,
    project_id: str,
    created_by: str,
    document_id: str,
    document_version_id: str,
    artifact_type: str,
    storage_provider: str,
    storage_uri: str,
    version: str,
    checksum: str | None = None,
    size_bytes: int | None = None,
):
    return await register_artifact(
        db,
        project_id=project_id,
        run_id=generic_run_id,
        artifact_type=artifact_type,
        storage_provider=storage_provider,
        storage_uri=storage_uri,
        version=version,
        visibility="private",
        checksum=checksum,
        size_bytes=size_bytes,
        created_by=created_by,
        metadata={
            "document_id": document_id,
            "document_version_id": document_version_id,
        },
    )
