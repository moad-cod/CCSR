from datetime import datetime
from types import SimpleNamespace
import unittest
from unittest.mock import ANY, AsyncMock, patch

from fastapi import HTTPException

from app.api.auth import UpdateMeRequest, update_me
from app.api.organizations import (
    OrganizationCreate,
    OrganizationUpdate,
    create_organization,
    get_organization,
    list_organizations,
    update_organization,
)
from app.api.projects import ProjectCreate, create_project
from app.models import Organization, OrganizationMembership
from app.models.organization_membership import (
    ORGANIZATION_ROLE_MEMBER,
    ORGANIZATION_ROLE_OWNER,
)


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _FakeDb:
    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = []
        self.execute = AsyncMock()

    def add(self, record):
        self.added.append(record)

    async def flush(self):
        for record in self.added:
            if isinstance(record, Organization) and record.id is None:
                record.id = "organization-id"
                record.created_at = datetime(2026, 8, 23)
                record.updated_at = datetime(2026, 8, 23)

    async def commit(self):
        self.committed = True

    async def refresh(self, record):
        self.refreshed.append(record)


class OrganizationAuthorizationTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_organization_adds_owner_membership(self):
        db = _FakeDb()

        result = await create_organization(
            OrganizationCreate(name="Research Lab"),
            db=db,
            user={"user_id": "user-id"},
        )

        memberships = [
            record for record in db.added if isinstance(record, OrganizationMembership)
        ]
        self.assertEqual(result.organization_id, "organization-id")
        self.assertEqual(len(memberships), 1)
        self.assertEqual(memberships[0].organization_id, "organization-id")
        self.assertEqual(memberships[0].user_id, "user-id")
        self.assertEqual(memberships[0].role, ORGANIZATION_ROLE_OWNER)
        self.assertTrue(db.committed)

    async def test_list_organizations_returns_only_member_organizations(self):
        organization = SimpleNamespace(
            id="organization-id",
            name="Research Lab",
            created_at=datetime(2026, 8, 23),
            updated_at=datetime(2026, 8, 23),
        )

        with patch(
            "app.api.organizations.membership_repository.list_member_organizations",
            AsyncMock(return_value=[organization]),
        ) as list_member_organizations:
            result = await list_organizations(
                db=SimpleNamespace(),
                user={"user_id": "user-id"},
            )

        list_member_organizations.assert_awaited_once_with(ANY, user_id="user-id")
        self.assertEqual([item.organization_id for item in result], ["organization-id"])

    async def test_get_organization_hides_non_member_organizations(self):
        with patch(
            "app.api.organizations.membership_repository.get_member_organization",
            AsyncMock(return_value=None),
        ):
            with self.assertRaises(HTTPException) as context:
                await get_organization(
                    "organization-id",
                    db=SimpleNamespace(),
                    user={"user_id": "user-id"},
                )

        self.assertEqual(context.exception.status_code, 404)

    async def test_member_without_admin_role_cannot_update_organization(self):
        organization = SimpleNamespace(
            id="organization-id",
            name="Research Lab",
            created_at=datetime(2026, 8, 23),
            updated_at=datetime(2026, 8, 23),
        )
        membership = SimpleNamespace(role=ORGANIZATION_ROLE_MEMBER)

        with (
            patch(
                "app.api.organizations.membership_repository.get_member_organization",
                AsyncMock(return_value=organization),
            ),
            patch(
                "app.api.organizations.membership_repository.get_active_membership",
                AsyncMock(return_value=membership),
            ),
        ):
            with self.assertRaises(HTTPException) as context:
                await update_organization(
                    "organization-id",
                    OrganizationUpdate(name="Renamed"),
                    db=SimpleNamespace(),
                    user={"user_id": "user-id"},
                )

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(organization.name, "Research Lab")

    async def test_project_creation_requires_organization_membership(self):
        db = SimpleNamespace()

        with patch(
            "app.api.projects.membership_repository.get_active_membership",
            AsyncMock(return_value=None),
        ):
            with self.assertRaises(HTTPException) as context:
                await create_project(
                    ProjectCreate(
                        name="Private Project",
                        organization_id="10000000-0000-0000-0000-000000000002",
                    ),
                    db=db,
                    user={"user_id": "user-id"},
                )

        self.assertEqual(context.exception.status_code, 403)

    async def test_profile_update_requires_organization_membership(self):
        account = SimpleNamespace(id="user-id", deleted_at=None)
        db = SimpleNamespace(
            execute=AsyncMock(return_value=_ScalarResult(account)),
            commit=AsyncMock(),
            refresh=AsyncMock(),
        )

        with patch(
            "app.api.auth.membership_repository.get_active_membership",
            AsyncMock(return_value=None),
        ):
            with self.assertRaises(HTTPException) as context:
                await update_me(
                    UpdateMeRequest(
                        organization_id="10000000-0000-0000-0000-000000000002"
                    ),
                    db=db,
                    user={"user_id": "user-id"},
                )

        self.assertEqual(context.exception.status_code, 403)
        db.commit.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
