from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from app.modules.ragforge.repositories.project_configs import (
    RAGProject,
    get_rag_project,
)
from app.platform.capabilities.model import ProjectCapability
from app.platform.capabilities.repository import enable_project_capability


class _RowResult:
    def __init__(self, row):
        self.row = row

    def one_or_none(self):
        return self.row


class ProjectCapabilityConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rag_reader_returns_project_and_configuration_as_one_boundary(self):
        project = SimpleNamespace(
            id="project-id",
            organization_id="organization-id",
            created_by="user-id",
        )
        config = SimpleNamespace(
            qdrant_collection="configured-collection",
            retrieval_configuration={
                "strategy": "dense",
                "top_k": 8,
                "fetch_k": 4,
                "use_rerank": False,
            },
        )
        db = SimpleNamespace(
            execute=AsyncMock(return_value=_RowResult((project, config)))
        )

        result = await get_rag_project(db, "project-id", user_id="user-id")

        self.assertIsInstance(result, RAGProject)
        self.assertIs(result.project, project)
        self.assertIs(result.config, config)
        self.assertEqual(result.collection, "configured-collection")
        self.assertEqual(result.retrieval_strategy, "dense")
        self.assertEqual(result.retrieval_top_k, 8)
        self.assertEqual(result.retrieval_fetch_k, 8)
        self.assertFalse(result.use_rerank)

    async def test_enabling_an_existing_capability_is_idempotent(self):
        association = ProjectCapability(
            project_id="project-id",
            capability_key="ragforge",
        )
        db = SimpleNamespace(
            get=AsyncMock(return_value=association),
            add=Mock(),
            flush=AsyncMock(),
        )

        result = await enable_project_capability(
            db,
            project_id="project-id",
            capability_key="ragforge",
        )

        self.assertIs(result, association)
        db.add.assert_not_called()
        db.flush.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
