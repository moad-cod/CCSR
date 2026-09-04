"""FastAPI authentication dependency owned by the platform."""

from datetime import UTC, datetime
import hashlib

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.platform.access.session import AuthSession
from app.platform.accounts.model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        session_id = payload.get("sid")
        if not user_id or not session_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(
            AuthSession.id,
            AuthSession.expires_at,
            User.id,
            User.global_role,
        )
        .join(User, User.id == AuthSession.user_id)
        .where(
            AuthSession.id == session_id,
            AuthSession.user_id == user_id,
            AuthSession.token_hash == token_digest(token),
            AuthSession.revoked_at.is_(None),
            User.deleted_at.is_(None),
        )
    )
    row = result.one_or_none()
    now = datetime.now(UTC).replace(tzinfo=None)
    if row is None:
        raise HTTPException(status_code=401, detail="Session expired or revoked")
    resolved_session_id, expires_at, resolved_user_id, global_role = row
    if expires_at <= now:
        raise HTTPException(status_code=401, detail="Session expired or revoked")
    if global_role not in {"member", "admin"}:
        raise HTTPException(status_code=403, detail="Access denied")
    return {
        "user_id": resolved_user_id,
        "global_role": global_role,
        "session_id": resolved_session_id,
    }
