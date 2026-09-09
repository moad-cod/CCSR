from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.projects import ProjectResponse
from app.modules.ragforge.api.overview import _parse_include, workspace_overview
from app.platform.access.policies import resolve_project_permissions


class CapabilityNavigationContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_member_permissions_are_read_only_for_organization_project(self):
        project = SimpleNamespace(
            id="project-id",
            organization_id="organization-id",
            created_by="owner-id",
        )
        with patch(
            "app.platform.access.policies.organization_repository.get_active_membership",
            AsyncMock(return_value=SimpleNamespace(role="member")),
        ):
            permissions = await resolve_project_permissions(
                SimpleNamespace(),
                project,
                {"user_id": "member-id", "global_role": "member"},
            )

        self.assertTrue(permissions.read)
        self.assertFalse(permissions.write)
        self.assertFalse(permissions.manage)

    async def test_platform_admin_receives_all_project_permissions(self):
        permissions = await resolve_project_permissions(
            SimpleNamespace(),
            SimpleNamespace(
                id="project-id",
                organization_id=None,
                created_by="owner-id",
            ),
            {"user_id": "admin-id", "global_role": "admin"},
        )

        self.assertTrue(permissions.read)
        self.assertTrue(permissions.write)
        self.assertTrue(permissions.manage)

    def test_workspace_include_contract_is_explicit(self):
        self.assertEqual(_parse_include("documents,runs"), {"documents", "runs"})
        with self.assertRaises(HTTPException) as context:
            _parse_include("documents,secrets")
        self.assertEqual(context.exception.status_code, 422)

    async def test_empty_rag_workspace_returns_bounded_empty_payload(self):
        with patch(
            "app.modules.ragforge.api.overview._rag_project_ids",
            AsyncMock(return_value=[]),
        ):
            result = await workspace_overview(
                include="documents,runs,history",
                record_limit=500,
                db=SimpleNamespace(),
                user={"user_id": "user-id", "global_role": "member"},
            )

        self.assertEqual(result.summaries, [])
        self.assertEqual(result.documents, [])
        self.assertEqual(result.runs, [])
        self.assertEqual(result.history, [])

    def test_project_contract_requires_server_resolved_permissions(self):
        required = ProjectResponse.model_json_schema()["required"]
        self.assertIn("permissions", required)


if __name__ == "__main__":
    unittest.main()
