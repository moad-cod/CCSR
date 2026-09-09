from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Literal

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.project import Project
from app.platform.access.authentication import get_current_user
from app.platform.organizations import repository as organization_repository
from app.platform.organizations.membership import (
    ORGANIZATION_ROLE_ADMIN,
    ORGANIZATION_ROLE_MEMBER,
    ORGANIZATION_ROLE_OWNER,
)
from app.platform.organizations.model import Organization


GLOBAL_ROLE_MEMBER = "member"
GLOBAL_ROLE_ADMIN = "admin"
GLOBAL_ROLES = frozenset({GLOBAL_ROLE_MEMBER, GLOBAL_ROLE_ADMIN})
PROJECT_ACTION_READ = "read"
PROJECT_ACTION_WRITE = "write"
PROJECT_ACTION_MANAGE = "manage"
PROJECT_ACTIONS = frozenset(
    {PROJECT_ACTION_READ, PROJECT_ACTION_WRITE, PROJECT_ACTION_MANAGE}
)
ProjectAction = Literal["read", "write", "manage"]


@dataclass(frozen=True, slots=True)
class ProjectPermissions:
    read: bool = False
    write: bool = False
    manage: bool = False


def _permissions_for_project(
    project: Project,
    *,
    user_id: str,
    global_role: str,
    organization_role: str | None,
) -> ProjectPermissions:
    if global_role == GLOBAL_ROLE_ADMIN:
        return ProjectPermissions(read=True, write=True, manage=True)
    if project.organization_id is None:
        allowed = project.created_by == user_id
        return ProjectPermissions(read=allowed, write=allowed, manage=allowed)
    if organization_role not in {
        ORGANIZATION_ROLE_OWNER,
        ORGANIZATION_ROLE_ADMIN,
        ORGANIZATION_ROLE_MEMBER,
    }:
        return ProjectPermissions()
    may_change = project.created_by == user_id or organization_role in {
        ORGANIZATION_ROLE_OWNER,
        ORGANIZATION_ROLE_ADMIN,
    }
    return ProjectPermissions(read=True, write=may_change, manage=may_change)


async def resolve_project_permissions(
    db: AsyncSession,
    project: Project,
    principal: dict,
) -> ProjectPermissions:
    user_id, global_role = _identity(principal)
    organization_role = None
    if project.organization_id is not None and global_role != GLOBAL_ROLE_ADMIN:
        membership = await organization_repository.get_active_membership(
            db,
            organization_id=project.organization_id,
            user_id=user_id,
        )
        organization_role = membership.role if membership is not None else None
    return _permissions_for_project(
        project,
        user_id=user_id,
        global_role=global_role,
        organization_role=organization_role,
    )


async def resolve_projects_permissions(
    db: AsyncSession,
    projects: Sequence[Project],
    principal: dict,
) -> dict[str, ProjectPermissions]:
    """Resolve navigation permissions for many projects in one membership query."""
    user_id, global_role = _identity(principal)
    organization_ids = {
        project.organization_id
        for project in projects
        if project.organization_id is not None
    }
    roles: dict[str, str] = {}
    if organization_ids and global_role != GLOBAL_ROLE_ADMIN:
        from app.platform.organizations.membership import OrganizationMembership

        result = await db.execute(
            select(
                OrganizationMembership.organization_id,
                OrganizationMembership.role,
            ).where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.organization_id.in_(organization_ids),
                OrganizationMembership.deleted_at.is_(None),
            )
        )
        roles = {str(organization_id): role for organization_id, role in result.all()}
    return {
        str(project.id): _permissions_for_project(
            project,
            user_id=user_id,
            global_role=global_role,
            organization_role=roles.get(str(project.organization_id)),
        )
        for project in projects
    }


def _identity(principal: dict) -> tuple[str, str]:
    user_id = principal.get("user_id")
    global_role = principal.get("global_role")
    if not user_id or global_role not in GLOBAL_ROLES:
        raise HTTPException(403, "Access denied")
    return str(user_id), str(global_role)


def require_global_roles(*roles: str):
    allowed = frozenset(roles)
    if not allowed or not allowed.issubset(GLOBAL_ROLES):
        raise ValueError("A known global role is required")

    async def dependency(principal: dict = Depends(get_current_user)) -> dict:
        _, global_role = _identity(principal)
        if global_role not in allowed:
            raise HTTPException(403, "Platform role required")
        return principal

    return dependency


def require_organization_roles(*roles: str):
    allowed = frozenset(roles)

    async def dependency(
        organization_id: str,
        db: AsyncSession = Depends(get_db),
        principal: dict = Depends(get_current_user),
    ) -> Organization:
        return await authorize_organization(
            db,
            organization_id,
            principal,
            roles=allowed or None,
        )

    return dependency


async def authorize_organization(
    db: AsyncSession,
    organization_id: str,
    principal: dict,
    *,
    roles: Collection[str] | None = None,
) -> Organization:
    user_id, global_role = _identity(principal)
    organization = await organization_repository.get_organization(
        db,
        organization_id=organization_id,
    )
    if organization is None:
        raise HTTPException(404, "Organization not found")
    if global_role == GLOBAL_ROLE_ADMIN:
        return organization

    membership = await organization_repository.get_active_membership(
        db,
        organization_id=organization_id,
        user_id=user_id,
    )
    if membership is None:
        raise HTTPException(404, "Organization not found")
    allowed_roles = frozenset(roles) if roles is not None else {
        ORGANIZATION_ROLE_OWNER,
        ORGANIZATION_ROLE_ADMIN,
        ORGANIZATION_ROLE_MEMBER,
    }
    if membership.role not in allowed_roles:
        raise HTTPException(403, "Organization role required")
    return organization


async def authorize_project(
    db: AsyncSession,
    project_id: str,
    principal: dict,
    *,
    action: ProjectAction,
) -> Project:
    user_id, global_role = _identity(principal)
    if action not in PROJECT_ACTIONS:
        raise HTTPException(403, "Access denied")

    from app.repositories import projects as project_repository

    project = await project_repository.get_project(db, project_id)
    if project is None or project.deleted_at is not None:
        raise HTTPException(404, "Project not found")
    if global_role == GLOBAL_ROLE_ADMIN:
        return project
    if project.organization_id is None:
        if project.created_by == user_id:
            return project
        raise HTTPException(404, "Project not found")

    membership = await organization_repository.get_active_membership(
        db,
        organization_id=project.organization_id,
        user_id=user_id,
    )
    if membership is None:
        raise HTTPException(404, "Project not found")
    if action == PROJECT_ACTION_READ and membership.role in {
        ORGANIZATION_ROLE_OWNER,
        ORGANIZATION_ROLE_ADMIN,
        ORGANIZATION_ROLE_MEMBER,
    }:
        return project
    if project.created_by == user_id or membership.role in {
        ORGANIZATION_ROLE_OWNER,
        ORGANIZATION_ROLE_ADMIN,
    }:
        return project
    raise HTTPException(403, "Project write access required")


def require_project_action(action: ProjectAction):
    if action not in PROJECT_ACTIONS:
        raise ValueError("A known project action is required")

    async def dependency(
        project_id: str,
        db: AsyncSession = Depends(get_db),
        principal: dict = Depends(get_current_user),
    ) -> Project:
        return await authorize_project(db, project_id, principal, action=action)

    return dependency


require_project_read = require_project_action(PROJECT_ACTION_READ)
require_project_write = require_project_action(PROJECT_ACTION_WRITE)
require_project_manage = require_project_action(PROJECT_ACTION_MANAGE)
