import logging

import httpx

from app.core.db import AsyncSessionLocal
from app.modules.ragforge.repositories.ingestion_runs import update_ingestion_status
from app.modules.ragforge.workflows import (
    IngestDocumentInput,
    ragforge_ingestion_workflow_definition,
)
from app.platform.execution.adapters import AirflowExecutionAdapter
from app.services.event_stream import publish_ingestion_event


logger = logging.getLogger(__name__)


async def dispatch_ingestion(ingestion_run_id: str) -> str | None:
    """Compatibility entry point for the generic Airflow adapter."""
    definition = ragforge_ingestion_workflow_definition("airflow")
    receipt = await AirflowExecutionAdapter(client_factory=httpx.AsyncClient).dispatch(
        definition,
        IngestDocumentInput(ingestion_run_id=ingestion_run_id).model_dump(exclude_none=True),
        None,
    )
    return receipt.external_execution_id if receipt is not None else None


async def enqueue_ingestion(ingestion_run_id: str) -> str | None:
    """Legacy enqueue API; dispatch through the adapter and dual-write status."""
    try:
        dag_run_id = await dispatch_ingestion(ingestion_run_id)
        if dag_run_id is None:
            return None
        async with AsyncSessionLocal() as db:
            await update_ingestion_status(
                db,
                ingestion_run_id,
                "queued",
                airflow_dag_run_id=dag_run_id,
            )
            await db.commit()
        await publish_ingestion_event(
            ingestion_run_id,
            "queued",
            data={"airflow_dag_run_id": dag_run_id},
        )
        return dag_run_id
    except Exception:
        logger.exception("Could not enqueue ingestion run %s in Airflow", ingestion_run_id)
        return None
