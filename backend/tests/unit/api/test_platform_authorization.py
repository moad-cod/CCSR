from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.platform.access.authentication import get_current_user
from app.platform.access.policies import (
    PROJECT_ACTION_MANAGE,
    PROJECT_ACTION_READ,
    PROJECT_ACTION_WRITE,
    authorize_project,
    require_global_roles,
)
from app.platform.organizations.api import accept_invitation


class _RowResult:
    def __init__(self, row):
        self.row = row

    def one_or_none(self):
        return self.row


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class PlatformAuthorizationTests(unittest.IsolatedAsyncioTestCase):
    async def test_authenticated_session_resolves_global_role(self):
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=5)
        token = jwt.encode(
            {"sub": "user-id", "sid": "session-id", "exp": expires_at},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        db = SimpleNamespace(
            execute=AsyncMock(
                return_value=_RowResult(
                    ("session-id", expires_at, "user-id", "member")
                )
            )
        )

        principal = await get_current_user(token=token, db=db)

        self.assertEqual(principal["session_id"], "session-id")
        self.assertEqual(principal["global_role"], "member")

    async def test_token_without_durable_session_id_is_denied(self):
        token = jwt.encode(
            {
                "sub": "user-id",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        with self.assertRaises(HTTPException) as context:
            await get_current_user(token=token, db=SimpleNamespace())
        self.assertEqual(context.exception.status_code, 401)

    async def test_unknown_principal_role_is_denied_by_default(self):
        with self.assertRaises(HTTPException) as context:
            await authorize_project(
                SimpleNamespace(),
                "project-id",
                {"user_id": "user-id", "global_role": "unknown"},
                action=PROJECT_ACTION_READ,
            )
        self.assertEqual(context.exception.status_code, 403)

    async def test_personal_project_is_private_to_creator(self):
        project = SimpleNamespace(
            id="project-id",
            organization_id=None,
            created_by="owner-id",
            deleted_at=None,
        )
        with patch(
            "app.repositories.projects.get_project",
            AsyncMock(return_value=project),
        ):
            with self.assertRaises(HTTPException) as context:
                await authorize_project(
                    SimpleNamespace(),
                    project.id,
                    {"user_id": "other-id", "global_role": "member"},
                    action=PROJECT_ACTION_READ,
                )
        self.assertEqual(context.exception.status_code, 404)

    async def test_organization_member_can_read_but_cannot_write_project(self):
        project = SimpleNamespace(
            id="project-id",
            organization_id="organization-id",
            created_by="owner-id",
            deleted_at=None,
        )
        membership = SimpleNamespace(role="member")
        with (
            patch(
                "app.repositories.projects.get_project",
                AsyncMock(return_value=project),
            ),
            patch(
                "app.platform.access.policies.organization_repository.get_active_membership",
                AsyncMock(return_value=membership),
            ),
        ):
            allowed = await authorize_project(
                SimpleNamespace(),
                project.id,
                {"user_id": "member-id", "global_role": "member"},
                action=PROJECT_ACTION_READ,
            )
            self.assertIs(allowed, project)
            with self.assertRaises(HTTPException) as context:
                await authorize_project(
                    SimpleNamespace(),
                    project.id,
                    {"user_id": "member-id", "global_role": "member"},
                    action=PROJECT_ACTION_WRITE,
                )
        self.assertEqual(context.exception.status_code, 403)

    async def test_organization_admin_and_platform_admin_can_manage_project(self):
        project = SimpleNamespace(
            id="project-id",
            organization_id="organization-id",
            created_by="owner-id",
            deleted_at=None,
        )
        with patch(
            "app.repositories.projects.get_project",
            AsyncMock(return_value=project),
        ):
            with patch(
                "app.platform.access.policies.organization_repository.get_active_membership",
                AsyncMock(return_value=SimpleNamespace(role="admin")),
            ):
                self.assertIs(
                    await authorize_project(
                        SimpleNamespace(),
                        project.id,
                        {"user_id": "org-admin", "global_role": "member"},
                        action=PROJECT_ACTION_MANAGE,
                    ),
                    project,
                )
            self.assertIs(
                await authorize_project(
                    SimpleNamespace(),
                    project.id,
                    {"user_id": "platform-admin", "global_role": "admin"},
                    action=PROJECT_ACTION_MANAGE,
                ),
                project,
            )

    async def test_global_role_dependency_denies_member(self):
        dependency = require_global_roles("admin")
        with self.assertRaises(HTTPException) as context:
            await dependency(principal={"user_id": "user-id", "global_role": "member"})
        self.assertEqual(context.exception.status_code, 403)

    async def test_matching_account_can_accept_pending_invitation(self):
        now = datetime.now(UTC).replace(tzinfo=None)
        invitation = SimpleNamespace(
            id="invitation-id",
            organization_id="organization-id",
            email="member@example.com",
            role="member",
            accepted_at=None,
            revoked_at=None,
            expires_at=now + timedelta(days=1),
            created_at=now,
        )
        account = SimpleNamespace(
            id="user-id",
            email="member@example.com",
            organization_id=None,
        )
        organization = SimpleNamespace(
            id="organization-id",
            name="Research Lab",
            created_at=now,
            updated_at=now,
        )
        db = SimpleNamespace(
            execute=AsyncMock(return_value=_ScalarResult(invitation)),
            get=AsyncMock(return_value=account),
            commit=AsyncMock(),
        )
        with (
            patch(
                "app.platform.organizations.api.membership_repository.get_organization",
                AsyncMock(return_value=organization),
            ),
            patch(
                "app.platform.organizations.api.membership_repository.activate_membership",
                AsyncMock(),
            ) as activate_membership,
        ):
            result = await accept_invitation(
                "invitation-token",
                db=db,
                user={"user_id": "user-id", "global_role": "member"},
            )

        self.assertEqual(result.organization_id, "organization-id")
        self.assertIsNotNone(invitation.accepted_at)
        self.assertEqual(account.organization_id, "organization-id")
        activate_membership.assert_awaited_once()
        db.commit.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
