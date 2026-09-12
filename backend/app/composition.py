"""Application assembly for the CCSR modular monolith.

This is the only layer that wires capability definitions, workflow adapters,
handlers, exception mappings, and HTTP routers together.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.projects import router as projects_router
from app.modules.ragforge.api.chunkers import router as chunkers_router
from app.modules.ragforge.api.documents import router as documents_router
from app.modules.ragforge.api.ingest import router as ingest_router
from app.modules.ragforge.api.internal_pipeline import router as internal_pipeline_router
from app.modules.ragforge.api.overview import router as rag_overview_router
from app.modules.ragforge.api.query import router as query_router
from app.modules.ragforge.capability import register_ragforge_capability
from app.modules.ragforge.workflows import (
    CELERY_INGESTION_HANDLER,
    register_ragforge_workflows,
)
from app.platform.accounts.api import router as auth_router
from app.platform.artifacts.api import router as artifacts_router
from app.platform.audit.api import router as audit_router
from app.platform.capabilities import CapabilityRegistry, capability_registry
from app.platform.execution.adapters import (
    AirflowExecutionAdapter,
    CeleryExecutionAdapter,
)
from app.platform.execution.api import router as execution_router
from app.platform.execution.registry import ExecutionRegistry, execution_registry
from app.platform.organizations.api import router as organizations_router
from app.platform.publication.api import router as publication_router
from app.platform.quotas import QuotaExceededError
from app.platform.quotas.api import router as quotas_router
from app.platform.research.api import router as research_router


async def _dispatch_ragforge_celery_ingestion(
    payload: Mapping[str, Any],
) -> str | None:
    from app.workers.tasks import dispatch_ingestion_workflow

    return await dispatch_ingestion_workflow(str(payload["ingestion_run_id"]))


def register_capabilities(registry: CapabilityRegistry = capability_registry) -> None:
    """Register capability definitions and lifecycle hooks idempotently."""
    register_ragforge_capability(registry)


def register_execution(registry: ExecutionRegistry = execution_registry) -> None:
    """Register workflows and their concrete execution implementations."""
    register_ragforge_workflows(registry)
    registry.register_adapter(AirflowExecutionAdapter())
    registry.register_adapter(CeleryExecutionAdapter())
    registry.register_handler(
        "celery",
        CELERY_INGESTION_HANDLER,
        _dispatch_ragforge_celery_ingestion,
    )


def register_routers(app: FastAPI) -> None:
    """Mount the existing public and internal HTTP surface unchanged."""
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(projects_router, prefix="/projects", tags=["projects"])
    app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
    app.include_router(query_router, prefix="/rag", tags=["rag"])
    app.include_router(rag_overview_router, prefix="/rag", tags=["rag-overview"])
    app.include_router(documents_router, prefix="/documents", tags=["documents"])
    app.include_router(chunkers_router, prefix="/chunkers", tags=["chunkers"])
    app.include_router(
        organizations_router,
        prefix="/organizations",
        tags=["organizations"],
    )
    app.include_router(execution_router, tags=["execution"])
    app.include_router(artifacts_router, tags=["artifacts"])
    app.include_router(quotas_router, tags=["quotas"])
    app.include_router(audit_router, tags=["audit"])
    app.include_router(research_router, tags=["research"])
    app.include_router(publication_router, tags=["publication"])
    app.include_router(
        internal_pipeline_router,
        prefix="/internal/pipeline",
        tags=["internal-pipeline"],
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Map stable application errors to their existing HTTP responses."""

    @app.exception_handler(QuotaExceededError)
    async def quota_exceeded_handler(_request, exc: QuotaExceededError):
        return JSONResponse(
            status_code=429,
            content={"detail": exc.message, "error_code": exc.code},
        )


def create_app() -> FastAPI:
    """Build and explicitly compose one FastAPI application instance."""
    register_capabilities()
    register_execution()

    app = FastAPI(
        title="RAGForge API",
        swagger_ui_parameters={"persistAuthorization": True},
    )
    register_routers(app)
    register_exception_handlers(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
