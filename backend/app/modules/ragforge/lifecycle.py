"""RAGForge cleanup behavior contributed to platform lifecycle operations."""

from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy import select

from app.modules.ragforge.models.document import Document
from app.platform.capabilities import (
    AccountDeletionContext,
    LifecycleResult,
    ProjectDeletionContext,
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


async def before_project_delete(context: ProjectDeletionContext) -> LifecycleResult:
    project = context.project
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
            collection=project.collection,
        )
        if document.source_type == "multimodal":
            try:
                await asyncio.to_thread(_delete_document_images, document.id)
            except Exception:
                pass
        document.status = "deleted"
        document.deleted_at = datetime.utcnow()

    await asyncio.to_thread(_delete_collection, project.collection)
    await asyncio.to_thread(_delete_collection, f"{project.collection}_multimodal")
    return LifecycleResult(deleted_resources={"documents": len(documents)})


async def before_account_delete(context: AccountDeletionContext) -> LifecycleResult:
    for project in context.projects:
        _delete_collection(project.collection)
        _delete_collection(f"{project.collection}_multimodal")
    return LifecycleResult()
