"""Orchestrator-neutral ingestion enqueue boundary."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.modules.ragforge.repositories.ingestion_runs import (
    mark_ingestion_failed,
    update_ingestion_status,
)
from app.services.event_stream import publish_ingestion_event
from app.platform.execution.gateway import execution_gateway


logger = logging.getLogger(__name__)
DISPATCH_FAILURE_MESSAGE = (
    "Ingestion orchestration failed to start. Verify the configured "
    "Airflow or Celery service is reachable, then retry the run."
)


def selected_orchestrator() -> str:
    return settings.ORCHESTRATOR.strip().lower()


def ingestion_orchestration_enabled() -> bool:
    orchestrator = selected_orchestrator()
    if orchestrator == "airflow":
        return bool(settings.AIRFLOW_API_URL)
    if orchestrator == "celery":
        return bool(settings.CELERY_BROKER_URL or settings.CELERY_TASK_ALWAYS_EAGER)
    return False


async def mark_ingestion_dispatch_failed(
    ingestion_run_id: str,
    error_message: str = DISPATCH_FAILURE_MESSAGE,
) -> None:
    """Persist a terminal state when the selected orchestrator never accepts a run."""
    async with AsyncSessionLocal() as db:
        run = await mark_ingestion_failed(db, ingestion_run_id, error_message)
        if run is None:
            logger.warning("Could not mark missing ingestion run %s as failed", ingestion_run_id)
            return
        await db.commit()
    await publish_ingestion_event(
        ingestion_run_id,
        "failed",
        data={"error_message": error_message},
    )


async def enqueue_ingestion(ingestion_run_id: str) -> str | None:
    if not ingestion_orchestration_enabled():
        return None
    orchestrator = selected_orchestrator()
    workflow_id: str | None = None
    try:
        from app.modules.ragforge.models.ingestion_run import IngestionRun
        from app.modules.ragforge.workflows import (
            create_generic_ingestion_run,
            register_ragforge_workflows,
        )

        register_ragforge_workflows()
        async with AsyncSessionLocal() as db:
            ingestion_run = await db.get(IngestionRun, ingestion_run_id)
            if ingestion_run is None:
                raise LookupError(f"Ingestion run {ingestion_run_id} does not exist")
            if ingestion_run.generic_run_id is None:
                generic_run = await create_generic_ingestion_run(
                    db,
                    ingestion_run_id=ingestion_run.id,
                    project_id=ingestion_run.project_id,
                    requested_by=ingestion_run.created_by,
                )
                ingestion_run.generic_run_id = generic_run.id
                await db.commit()
            generic_run_id = ingestion_run.generic_run_id

        workflow_id = await execution_gateway.dispatch(generic_run_id)
        if workflow_id:
            async with AsyncSessionLocal() as db:
                await update_ingestion_status(
                    db,
                    ingestion_run_id,
                    "queued",
                    airflow_dag_run_id=workflow_id,
                )
                await db.commit()
            await publish_ingestion_event(
                ingestion_run_id,
                "queued",
                data={"airflow_dag_run_id": workflow_id},
            )
    except Exception:
        logger.exception(
            "Configured %s orchestrator failed while accepting ingestion run %s",
            orchestrator,
            ingestion_run_id,
        )
        await mark_ingestion_dispatch_failed(ingestion_run_id)
        raise

    if workflow_id:
        return workflow_id

    logger.error(
        "Configured %s orchestrator did not accept ingestion run %s",
        orchestrator,
        ingestion_run_id,
    )
    await mark_ingestion_dispatch_failed(ingestion_run_id)
    return None
