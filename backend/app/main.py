from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.platform.accounts.api import router as auth_router
from app.api.projects import router as projects_router
from app.modules.ragforge.api.ingest import router as ingest_router
from app.modules.ragforge.api.query import router as query_router
from app.modules.ragforge.api.overview import router as rag_overview_router
from app.modules.ragforge.api.documents import router as documents_router
from app.modules.ragforge.api.chunkers import router as chunkers_router
from app.platform.organizations.api import router as organizations_router
from app.modules.ragforge.api.internal_pipeline import router as internal_pipeline_router
from app.modules.ragforge.capability import register_ragforge_capability
from app.platform.capabilities import capability_registry
from app.platform.execution.api import router as execution_router
from app.modules.ragforge.workflows import register_ragforge_workflows
from app.platform.artifacts.api import router as artifacts_router
from app.platform.audit.api import router as audit_router
from app.platform.quotas.api import router as quotas_router
from app.platform.quotas import QuotaExceededError
from app.platform.research.api import router as research_router
from app.platform.publication.api import router as publication_router


register_ragforge_capability(capability_registry)
register_ragforge_workflows()

app = FastAPI(
    title="RAGForge API",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(auth_router,      prefix="/auth",      tags=["auth"])
app.include_router(projects_router,  prefix="/projects",  tags=["projects"])
app.include_router(ingest_router,    prefix="/ingest",    tags=["ingest"])
app.include_router(query_router,     prefix="/rag",       tags=["rag"])
app.include_router(rag_overview_router, prefix="/rag", tags=["rag-overview"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(chunkers_router,  prefix="/chunkers",  tags=["chunkers"])
app.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
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


@app.exception_handler(QuotaExceededError)
async def quota_exceeded_handler(_request, exc: QuotaExceededError):
    return JSONResponse(
        status_code=429,
        content={"detail": exc.message, "error_code": exc.code},
    )

@app.get("/health")
def health():
    return {"status": "ok"}
