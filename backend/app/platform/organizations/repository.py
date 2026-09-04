from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.organizations.membership import (
    ORGANIZATION_ROLE_MEMBER,
    OrganizationMembership,
)
from app.platform.organizations.model import Organization


async def create_membership(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
    role: str = ORGANIZATION_ROLE_MEMBER,
) -> OrganizationMembership:
    membership = OrganizationMembership(
        organization_id=organization_id,
        user_id=user_id,
        role=role,
    )
    db.add(membership)
    await db.flush()
    return membership


async def activate_membership(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
    role: str = ORGANIZATION_ROLE_MEMBER,
) -> OrganizationMembership:
    result = await db.execute(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        return await create_membership(
            db,
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )
    membership.role = role
    membership.deleted_at = None
    await db.flush()
    return membership


async def get_organization(
    db: AsyncSession,
    *,
    organization_id: str,
) -> Organization | None:
    result = await db.execute(
        select(Organization).where(
            Organization.id == organization_id,
            Organization.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_active_membership(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
) -> OrganizationMembership | None:
    result = await db.execute(
        select(OrganizationMembership)
        .join(Organization, Organization.id == OrganizationMembership.organization_id)
        .where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.deleted_at.is_(None),
            Organization.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_member_organization(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
) -> Organization | None:
    result = await db.execute(
        select(Organization)
        .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
        .where(
            Organization.id == organization_id,
            Organization.deleted_at.is_(None),
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def list_member_organizations(
    db: AsyncSession,
    *,
    user_id: str,
) -> list[Organization]:
    result = await db.execute(
        select(Organization)
        .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
        .where(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.deleted_at.is_(None),
            Organization.deleted_at.is_(None),
        )
        .order_by(Organization.updated_at.desc())
    )
    return list(result.scalars().all())


async def list_organizations(db: AsyncSession) -> list[Organization]:
    result = await db.execute(
        select(Organization)
        .where(Organization.deleted_at.is_(None))
        .order_by(Organization.updated_at.desc())
    )
    return list(result.scalars().all())
