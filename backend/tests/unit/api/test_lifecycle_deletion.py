from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from app.api.projects import delete_project
from app.platform.accounts.api import delete_me
from app.platform.capabilities import LifecycleResult, capability_registry


BACKEND_ROOT = Path(__file__).parents[3]


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _ManyResult:
    def __init__(self, values):
        self.values = values

    def scalars(self):
        return self

    def all(self):
        return self.values


class LifecycleDeletionRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_project_deletion_uses_registry_and_preserves_response(self):
        project = SimpleNamespace(
            id="project-id",
            collection="project_collection",
            deleted_at=None,
        )
        db = SimpleNamespace(commit=AsyncMock())

        with (
            patch(
                "app.api.projects.authorize_project",
                AsyncMock(return_value=project),
            ),
            patch.object(
                capability_registry,
                "before_project_delete",
                AsyncMock(
                    return_value=LifecycleResult(
                        deleted_resources={"documents": 3}
                    )
                ),
            ) as lifecycle_hook,
        ):
            result = await delete_project(
                "project-id",
                db=db,
                user={"user_id": "account-id", "global_role": "member"},
            )

        context = lifecycle_hook.await_args.args[0]
        self.assertIs(context.db, db)
        self.assertIs(context.project, project)
        self.assertEqual(
            result,
            {
                "deleted_project": "project-id",
                "deleted_collection": "project_collection",
                "deleted_documents": 3,
            },
        )
        self.assertIsNotNone(project.deleted_at)
        db.commit.assert_awaited_once()

    async def test_account_deletion_uses_registry_and_preserves_response(self):
        account = SimpleNamespace(id="account-id", global_role="member", deleted_at=None)
        projects = [
            SimpleNamespace(id="one", deleted_at=None),
            SimpleNamespace(id="two", deleted_at=None),
        ]
        db = SimpleNamespace(
            execute=AsyncMock(
                side_effect=[_ScalarResult(account), _ManyResult(projects), None]
            ),
            commit=AsyncMock(),
        )

        with patch.object(
            capability_registry,
            "before_account_delete",
            AsyncMock(return_value=LifecycleResult()),
        ) as lifecycle_hook:
            result = await delete_me(
                db=db,
                user={
                    "user_id": "account-id",
                    "global_role": "member",
                    "session_id": "session-id",
                },
            )

        context = lifecycle_hook.await_args.args[0]
        self.assertIs(context.db, db)
        self.assertIs(context.account, account)
        self.assertIs(context.projects, projects)
        self.assertEqual(
            result,
            {"deleted_user": "account-id", "deleted_projects": 2},
        )
        self.assertIsNotNone(account.deleted_at)
        self.assertTrue(all(project.deleted_at is not None for project in projects))
        db.commit.assert_awaited_once()


class LifecycleDependencyBoundaryTests(unittest.TestCase):
    def test_platform_deletion_routes_do_not_import_ragforge(self):
        paths = (
            BACKEND_ROOT / "app" / "api" / "projects.py",
            BACKEND_ROOT / "app" / "platform" / "accounts" / "api.py",
        )

        for path in paths:
            with self.subTest(path=path):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                imported_modules = {
                    node.module
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module
                }
                self.assertFalse(
                    any(
                        module.startswith("app.modules.ragforge")
                        for module in imported_modules
                    )
                )


if __name__ == "__main__":
    unittest.main()
