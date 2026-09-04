from datetime import UTC, datetime, timedelta
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.access.authentication import get_current_user
from app.platform.access.policies import (
    GLOBAL_ROLE_ADMIN,
    authorize_organization,
)
from app.core.db import get_db
from app.platform.organizations.membership import (
    ORGANIZATION_ROLE_ADMIN,
    ORGANIZATION_ROLE_MEMBER,
    ORGANIZATION_ROLE_OWNER,
)
from app.platform.accounts.model import User
from app.platform.organizations import repository as membership_repository
from app.platform.organizations.membership import OrganizationMembership
from app.platform.organizations.invitation import OrganizationInvitation
from app.platform.organizations.model import Organization

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


class InvitationCreate(BaseModel):
    email: str
    role: str = ORGANIZATION_ROLE_MEMBER

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("Invalid email address")
        return email

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in {ORGANIZATION_ROLE_ADMIN, ORGANIZATION_ROLE_MEMBER}:
            raise ValueError("Invitation role must be admin or member")
        return value


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invitation_id: str
    organization_id: str
    email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime
    invitation_token: str | None = None


def _invitation_payload(
    invitation: OrganizationInvitation,
    *,
    token: str | None = None,
) -> InvitationResponse:
    now = datetime.now(UTC).replace(tzinfo=None)
    status = (
        "accepted"
        if invitation.accepted_at is not None
        else "revoked"
        if invitation.revoked_at is not None
        else "expired"
        if invitation.expires_at <= now
        else "pending"
    )
    return InvitationResponse(
        invitation_id=invitation.id,
        organization_id=invitation.organization_id,
        email=invitation.email,
        role=invitation.role,
        status=status,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
        invitation_token=token,
    )


def _organization_payload(organization: Organization) -> OrganizationResponse:
    return OrganizationResponse(
        organization_id=organization.id,
        name=organization.name,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )


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
    if user["global_role"] == GLOBAL_ROLE_ADMIN:
        organizations = await membership_repository.list_organizations(db)
    else:
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
    organization = await authorize_organization(db, organization_id, user)
    return _organization_payload(organization)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    body: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    organization = await authorize_organization(
        db, organization_id, user, roles=MUTATION_ROLES
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
    organization = await authorize_organization(
        db, organization_id, user, roles=MUTATION_ROLES
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


@router.post(
    "/{organization_id}/invitations",
    response_model=InvitationResponse,
)
async def create_invitation(
    organization_id: str,
    body: InvitationCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await authorize_organization(db, organization_id, user, roles=MUTATION_ROLES)
    existing_membership = await db.execute(
        select(OrganizationMembership)
        .join(User, User.id == OrganizationMembership.user_id)
        .where(
            OrganizationMembership.organization_id == organization_id,
            User.email == body.email,
            OrganizationMembership.deleted_at.is_(None),
        )
    )
    if existing_membership.scalar_one_or_none() is not None:
        raise HTTPException(409, "User is already an organization member")
    pending = await db.execute(
        select(OrganizationInvitation).where(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.email == body.email,
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.revoked_at.is_(None),
            OrganizationInvitation.expires_at > datetime.now(UTC).replace(tzinfo=None),
        )
    )
    if pending.scalar_one_or_none() is not None:
        raise HTTPException(409, "A pending invitation already exists")

    token = secrets.token_urlsafe(32)
    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=body.email,
        role=body.role,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        invited_by=user["user_id"],
        expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return _invitation_payload(invitation, token=token)


@router.get(
    "/{organization_id}/invitations",
    response_model=list[InvitationResponse],
)
async def list_invitations(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await authorize_organization(db, organization_id, user, roles=MUTATION_ROLES)
    result = await db.execute(
        select(OrganizationInvitation)
        .where(OrganizationInvitation.organization_id == organization_id)
        .order_by(OrganizationInvitation.created_at.desc())
    )
    return [_invitation_payload(item) for item in result.scalars().all()]


@router.delete("/{organization_id}/invitations/{invitation_id}")
async def revoke_invitation(
    organization_id: str,
    invitation_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await authorize_organization(db, organization_id, user, roles=MUTATION_ROLES)
    invitation = await db.get(OrganizationInvitation, invitation_id)
    if invitation is None or invitation.organization_id != organization_id:
        raise HTTPException(404, "Invitation not found")
    if invitation.accepted_at is not None:
        raise HTTPException(409, "Accepted invitations cannot be revoked")
    invitation.revoked_at = datetime.now(UTC).replace(tzinfo=None)
    await db.commit()
    return {"revoked_invitation": invitation_id}


@router.post("/invitations/{token}/accept", response_model=OrganizationResponse)
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    now = datetime.now(UTC).replace(tzinfo=None)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(
        select(OrganizationInvitation).where(
            OrganizationInvitation.token_hash == token_hash,
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.revoked_at.is_(None),
            OrganizationInvitation.expires_at > now,
        )
    )
    invitation = result.scalar_one_or_none()
    account = await db.get(User, user["user_id"])
    if invitation is None or account is None or account.email != invitation.email:
        raise HTTPException(404, "Invitation not found")
    organization = await membership_repository.get_organization(
        db,
        organization_id=invitation.organization_id,
    )
    if organization is None:
        raise HTTPException(404, "Organization not found")
    await membership_repository.activate_membership(
        db,
        organization_id=invitation.organization_id,
        user_id=account.id,
        role=invitation.role,
    )
    invitation.accepted_at = now
    if account.organization_id is None:
        account.organization_id = invitation.organization_id
    await db.commit()
    return _organization_payload(organization)
