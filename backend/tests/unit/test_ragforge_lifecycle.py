from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, call, patch

from app.modules.ragforge import lifecycle
from app.platform.capabilities import (
    AccountDeletionContext,
    ProjectDeletionContext,
    ProjectProvisioningContext,
)


class _DocumentsResult:
    def __init__(self, documents):
        self.documents = documents

    def scalars(self):
        return self

    def all(self):
        return self.documents


async def _run_inline(function, *args, **kwargs):
    return function(*args, **kwargs)


class RAGForgeLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_project_hook_preserves_document_and_collection_cleanup(self):
        documents = [
            SimpleNamespace(
                id="text-document",
                source_type="file",
                status="indexed",
                deleted_at=None,
            ),
            SimpleNamespace(
                id="multimodal-document",
                source_type="multimodal",
                status="indexed",
                deleted_at=None,
            ),
        ]
        db = SimpleNamespace(execute=AsyncMock(return_value=_DocumentsResult(documents)))
        project = SimpleNamespace(id="project-id", collection="project_collection")

        with (
            patch.object(
                lifecycle.project_config_repository,
                "get_rag_project_config",
                AsyncMock(
                    return_value=SimpleNamespace(
                        qdrant_collection="project_collection"
                    )
                ),
            ),
            patch.object(
                lifecycle.asyncio,
                "to_thread",
                AsyncMock(side_effect=_run_inline),
            ),
            patch.object(lifecycle, "_delete_document_chunks", Mock()) as delete_chunks,
            patch.object(lifecycle, "_delete_document_images", Mock()) as delete_images,
            patch.object(lifecycle, "_delete_collection", Mock()) as delete_collection,
        ):
            result = await lifecycle.before_project_delete(
                ProjectDeletionContext(db=db, project=project)
            )

        self.assertEqual(result.count("documents"), 2)
        delete_chunks.assert_has_calls(
            [
                call(document_id="text-document", collection="project_collection"),
                call(
                    document_id="multimodal-document",
                    collection="project_collection",
                ),
            ]
        )
        delete_images.assert_called_once_with("multimodal-document")
        delete_collection.assert_has_calls(
            [call("project_collection"), call("project_collection_multimodal")]
        )
        self.assertTrue(all(document.status == "deleted" for document in documents))
        self.assertTrue(all(document.deleted_at is not None for document in documents))

    async def test_project_hook_keeps_multimodal_image_cleanup_best_effort(self):
        document = SimpleNamespace(
            id="document-id",
            source_type="multimodal",
            status="indexed",
            deleted_at=None,
        )
        db = SimpleNamespace(
            execute=AsyncMock(return_value=_DocumentsResult([document]))
        )
        project = SimpleNamespace(id="project-id", collection="project_collection")

        with (
            patch.object(
                lifecycle.project_config_repository,
                "get_rag_project_config",
                AsyncMock(
                    return_value=SimpleNamespace(
                        qdrant_collection="project_collection"
                    )
                ),
            ),
            patch.object(
                lifecycle.asyncio,
                "to_thread",
                AsyncMock(side_effect=_run_inline),
            ),
            patch.object(lifecycle, "_delete_document_chunks", Mock()),
            patch.object(
                lifecycle,
                "_delete_document_images",
                Mock(side_effect=RuntimeError("R2 unavailable")),
            ),
            patch.object(lifecycle, "_delete_collection", Mock()),
        ):
            result = await lifecycle.before_project_delete(
                ProjectDeletionContext(db=db, project=project)
            )

        self.assertEqual(result.count("documents"), 1)
        self.assertEqual(document.status, "deleted")

    async def test_account_hook_preserves_collection_only_cleanup(self):
        projects = [
            SimpleNamespace(id="project-one"),
            SimpleNamespace(id="project-two"),
        ]

        with (
            patch.object(
                lifecycle.project_config_repository,
                "list_rag_project_configs",
                AsyncMock(
                    return_value={
                        "project-one": SimpleNamespace(
                            qdrant_collection="project_one"
                        ),
                        "project-two": SimpleNamespace(
                            qdrant_collection="project_two"
                        ),
                    }
                ),
            ),
            patch.object(lifecycle, "_delete_collection", Mock()) as delete_collection,
        ):
            await lifecycle.before_account_delete(
                AccountDeletionContext(
                    db=SimpleNamespace(),
                    account=SimpleNamespace(id="account-id"),
                    projects=projects,
                )
            )

        delete_collection.assert_has_calls(
            [
                call("project_one"),
                call("project_one_multimodal"),
                call("project_two"),
                call("project_two_multimodal"),
            ]
        )

    async def test_project_provisioning_creates_rag_configuration(self):
        db = SimpleNamespace(add=Mock(), flush=AsyncMock())
        project = SimpleNamespace(
            id="project-id",
            qdrant_collection="project_collection",
        )

        await lifecycle.after_project_create(
            ProjectProvisioningContext(db=db, project=project)
        )

        config = db.add.call_args.args[0]
        self.assertEqual(config.project_id, "project-id")
        self.assertEqual(config.qdrant_collection, "project_collection")
        self.assertEqual(config.default_chunker, "paragraph")
        self.assertEqual(config.retrieval_configuration["strategy"], "hybrid")
        db.flush.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
