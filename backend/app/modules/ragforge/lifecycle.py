"""RAGForge cleanup behavior contributed to platform lifecycle operations."""

from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy import select

from app.core.config import settings
from app.modules.ragforge.models.document import Document
from app.modules.ragforge.models.project_config import (
    DEFAULT_CHUNKER,
    DEFAULT_RETRIEVAL_CONFIGURATION,
    DEFAULT_SPARSE_MODEL,
    RAGProjectConfig,
)
from app.modules.ragforge.repositories import project_configs as project_config_repository
from app.platform.capabilities import (
    AccountDeletionContext,
    LifecycleResult,
    ProjectDeletionContext,
    ProjectProvisioningContext,
)


def _delete_collection(collection: str) -> None:
    from app.modules.ragforge.services.indexer import delete_collection

    delete_collection(collection)


def _delete_document_chunks(*, document_id: str, collection: str) -> None:
    from app.modules.ragforge.services.indexer import delete_document_chunks

    delete_document_chunks(document_id=document_id, collection=collection)


def _delete_document_images(document_id: str) -> None:
    from app.modules.ragforge.services.storage import delete_document_images

    delete_document_images(document_id)


async def after_project_create(context: ProjectProvisioningContext) -> None:
    context.db.add(
        RAGProjectConfig(
            project_id=context.project.id,
            qdrant_collection=context.project.qdrant_collection,
            embedding_model=settings.EMBEDDING_MODEL,
            sparse_model=DEFAULT_SPARSE_MODEL,
            default_chunker=DEFAULT_CHUNKER,
            retrieval_configuration=dict(DEFAULT_RETRIEVAL_CONFIGURATION),
        )
    )
    await context.db.flush()


async def before_project_delete(context: ProjectDeletionContext) -> LifecycleResult:
    project = context.project
    config = await project_config_repository.get_rag_project_config(
        context.db,
        project.id,
    )
    if config is None:
        raise RuntimeError(f"RAG configuration is missing for project {project.id}")
    documents_result = await context.db.execute(
        select(Document).where(
            Document.project_id == project.id,
            Document.deleted_at.is_(None),
        )
    )
    documents = list(documents_result.scalars().all())
    for document in documents:
        await asyncio.to_thread(
            _delete_document_chunks,
            document_id=document.id,
            collection=config.qdrant_collection,
        )
        if document.source_type == "multimodal":
            try:
                await asyncio.to_thread(_delete_document_images, document.id)
            except Exception:
                pass
        document.status = "deleted"
        document.deleted_at = datetime.utcnow()

    await asyncio.to_thread(_delete_collection, config.qdrant_collection)
    await asyncio.to_thread(
        _delete_collection,
        f"{config.qdrant_collection}_multimodal",
    )
    return LifecycleResult(deleted_resources={"documents": len(documents)})


async def before_account_delete(context: AccountDeletionContext) -> LifecycleResult:
    configs = await project_config_repository.list_rag_project_configs(
        context.db,
        [project.id for project in context.projects],
    )
    for project in context.projects:
        config = configs.get(project.id)
        if config is None:
            raise RuntimeError(f"RAG configuration is missing for project {project.id}")
        _delete_collection(config.qdrant_collection)
        _delete_collection(f"{config.qdrant_collection}_multimodal")
    return LifecycleResult()
