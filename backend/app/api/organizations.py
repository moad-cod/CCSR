from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.organization_membership import (
    ORGANIZATION_ROLE_ADMIN,
    ORGANIZATION_ROLE_OWNER,
)
from app.models.tables import Organization, OrganizationMembership, User
from app.repositories import organization_memberships as membership_repository

router = APIRouter()
MUTATION_ROLES = {ORGANIZATION_ROLE_OWNER, ORGANIZATION_ROLE_ADMIN}


class OrganizationCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Organization name is required")
        if len(name) > 160:
            raise ValueError("Organization name must be 160 characters or fewer")
        return name


class OrganizationUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return OrganizationCreate.validate_name(value)


class OrganizationResponse(BaseModel):
    organization_id: str
    name: str
    created_at: datetime
    updated_at: datetime


def _organization_payload(organization: Organization) -> OrganizationResponse:
    return OrganizationResponse(
        organization_id=organization.id,
        name=organization.name,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )


async def _require_member_organization(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
) -> Organization:
    organization = await membership_repository.get_member_organization(
        db,
        organization_id=organization_id,
        user_id=user_id,
    )
    if organization is None:
        raise HTTPException(404, "Organization not found")
    return organization


async def _require_mutation_role(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
) -> Organization:
    organization = await _require_member_organization(
        db,
        organization_id=organization_id,
        user_id=user_id,
    )
    membership = await membership_repository.get_active_membership(
        db,
        organization_id=organization_id,
        user_id=user_id,
    )
    if membership is None or membership.role not in MUTATION_ROLES:
        raise HTTPException(403, "Organization admin role required")
    return organization


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    body: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    organization = Organization(name=body.name)
    db.add(organization)
    await db.flush()
    await membership_repository.create_membership(
        db,
        organization_id=organization.id,
        user_id=user["user_id"],
        role=ORGANIZATION_ROLE_OWNER,
    )
    await db.commit()
    await db.refresh(organization)
    return _organization_payload(organization)


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    organizations = await membership_repository.list_member_organizations(
        db,
        user_id=user["user_id"],
    )
    return [_organization_payload(org) for org in organizations]


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    organization = await _require_member_organization(
        db,
        organization_id=organization_id,
        user_id=user["user_id"],
    )
    return _organization_payload(organization)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    body: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    organization = await _require_mutation_role(
        db,
        organization_id=organization_id,
        user_id=user["user_id"],
    )

    organization.name = body.name
    await db.commit()
    await db.refresh(organization)
    return _organization_payload(organization)


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    organization = await _require_mutation_role(
        db,
        organization_id=organization_id,
        user_id=user["user_id"],
    )

    now = datetime.utcnow()
    organization.deleted_at = now
    await db.execute(
        update(OrganizationMembership)
        .where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.deleted_at.is_(None),
        )
        .values(deleted_at=now)
    )
    await db.execute(
        update(User)
        .where(User.organization_id == organization_id)
        .values(organization_id=None)
    )
    await db.commit()
    return {"deleted_organization": organization_id}
