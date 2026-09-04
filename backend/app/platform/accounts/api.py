from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update
from jose import jwt
from app.core.config import settings
from app.core.db import get_db
from app.models.project import Project
from app.platform.access.authentication import get_current_user
from app.platform.access.authentication import token_digest
from app.platform.access.session import AuthSession
from app.platform.access.policies import GLOBAL_ROLE_ADMIN, require_global_roles
from app.platform.accounts.model import User
from app.platform.capabilities import AccountDeletionContext, capability_registry
from app.platform.organizations import repository as membership_repository
from datetime import UTC, datetime, timedelta
from pydantic import BaseModel, ConfigDict, field_validator
import uuid
import bcrypt

router = APIRouter()


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strong-password",
                "full_name": "Example User",
            }
        }
    )

    email: str
    password: str
    full_name: str | None = None
    organization_id: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @field_validator("organization_id")
    @classmethod
    def validate_organization_id(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        try:
            return str(uuid.UUID(value.strip()))
        except ValueError as exc:
            raise ValueError("organization_id must be a valid UUID") from exc

class UpdateMeRequest(BaseModel):
    email: str | None = None
    password: str | None = None
    full_name: str | None = None
    organization_id: str | None = None

    @field_validator("email")
    @classmethod
    def validate_optional_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_optional_password(cls, value: str | None) -> str | None:
        if value is not None and len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @field_validator("organization_id")
    @classmethod
    def validate_optional_organization_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return ""
        try:
            return str(uuid.UUID(normalized))
        except ValueError as exc:
            raise ValueError("organization_id must be a valid UUID") from exc

class UserResponse(BaseModel):
    user_id: str
    organization_id: str | None
    email: str
    full_name: str | None
    global_role: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GlobalRoleUpdate(BaseModel):
    global_role: str

    @field_validator("global_role")
    @classmethod
    def validate_global_role(cls, value: str) -> str:
        if value not in {"member", "admin"}:
            raise ValueError("global_role must be member or admin")
        return value


class SessionResponse(BaseModel):
    session_id: str
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    current: bool


def _user_payload(user: User) -> UserResponse:
    return UserResponse(
        user_id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        full_name=user.full_name,
        global_role=user.global_role,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == body.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    if body.organization_id:
        raise HTTPException(403, "An accepted organization invitation is required")

    user = User(
        id=str(uuid.uuid4()),
        organization_id=None,
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        global_role=(
            "admin" if body.email in settings.platform_admin_emails else "member"
        ),
    )
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)
    return _user_payload(user)


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == form.username, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    session_id = str(uuid.uuid4())
    expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
    token = jwt.encode(
        {"sub": user.id, "sid": session_id, "exp": expires_at},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    db.add(
        AuthSession(
            id=session_id,
            user_id=user.id,
            token_hash=token_digest(token),
            expires_at=expires_at,
        )
    )
    await db.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "session_id": session_id,
        "expires_at": expires_at,
    }


@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    session = await db.get(AuthSession, user["session_id"])
    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(UTC).replace(tzinfo=None)
        await db.commit()
    return {"authenticated": False}


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(AuthSession)
        .where(AuthSession.user_id == user["user_id"])
        .order_by(AuthSession.created_at.desc())
    )
    return [
        SessionResponse(
            session_id=session.id,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            created_at=session.created_at,
            current=session.id == user["session_id"],
        )
        for session in result.scalars().all()
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    session = await db.get(AuthSession, session_id)
    if session is None or session.user_id != user["user_id"]:
        raise HTTPException(404, "Session not found")
    if session.revoked_at is None:
        session.revoked_at = datetime.now(UTC).replace(tzinfo=None)
        await db.commit()
    return {"revoked_session": session_id}


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_global_role(
    user_id: str,
    body: GlobalRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_global_roles(GLOBAL_ROLE_ADMIN)),
):
    account = await db.get(User, user_id)
    if account is None or account.deleted_at is not None:
        raise HTTPException(404, "User not found")
    if account.global_role == "admin" and body.global_role == "member":
        admin_count = await db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.global_role == "admin", User.deleted_at.is_(None))
        )
        if admin_count <= 1:
            raise HTTPException(409, "The last platform admin cannot be demoted")
    account.global_role = body.global_role
    await db.commit()
    await db.refresh(account)
    return _user_payload(account)


# ── Get current user ──────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(User).where(User.id == user["user_id"], User.deleted_at.is_(None))
    )
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    return _user_payload(u)


# ── Update current user ───────────────────────────────────────────────────────

@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UpdateMeRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(User).where(User.id == user["user_id"], User.deleted_at.is_(None))
    )
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")

    if body.email:
        # check email not taken by another user
        existing = await db.execute(
            select(User).where(
                User.email == body.email,
                User.id != user["user_id"],
                User.deleted_at.is_(None),
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(400, "Email already in use")
        u.email = body.email

    if body.password:
        u.hashed_password = hash_password(body.password)
        await db.execute(
            update(AuthSession)
            .where(
                AuthSession.user_id == u.id,
                AuthSession.id != user["session_id"],
                AuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC).replace(tzinfo=None))
        )
    if body.full_name is not None:
        u.full_name = body.full_name
    if body.organization_id is not None:
        if body.organization_id:
            membership = await membership_repository.get_active_membership(
                db,
                organization_id=body.organization_id,
                user_id=user["user_id"],
            )
            if membership is None:
                raise HTTPException(403, "Organization membership required")
        u.organization_id = body.organization_id or None

    await db.commit()
    await db.refresh(u)
    return _user_payload(u)


# ── Delete current user ───────────────────────────────────────────────────────

@router.delete("/me")
async def delete_me(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(User).where(User.id == user["user_id"], User.deleted_at.is_(None))
    )
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    if u.global_role == "admin":
        admin_count = await db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.global_role == "admin", User.deleted_at.is_(None))
        )
        if admin_count <= 1:
            raise HTTPException(409, "The last platform admin cannot be deleted")

    projects_result = await db.execute(
        select(Project).where(
            Project.created_by == user["user_id"],
            Project.deleted_at.is_(None),
        )
    )
    projects = projects_result.scalars().all()
    await capability_registry.before_account_delete(
        AccountDeletionContext(db=db, account=u, projects=projects)
    )
    for project in projects:
        project.deleted_at = datetime.utcnow()

    deleted_at = datetime.now(UTC).replace(tzinfo=None)
    await db.execute(
        update(AuthSession)
        .where(
            AuthSession.user_id == u.id,
            AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=deleted_at)
    )
    u.deleted_at = deleted_at
    await db.commit()

    return {
        "deleted_user": user["user_id"],
        "deleted_projects": len(projects),
    }
