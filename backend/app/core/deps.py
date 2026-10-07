from typing import List, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.revoked_token import RevokedToken
from app.schemas.user import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Return authenticated User if valid Bearer token provided and not revoked, else None."""
    if not token:
        return None
    try:
        # Check token revocation
        token_hash = RevokedToken.hash_token(token)
        rev_stmt = select(RevokedToken).where(RevokedToken.token_hash == token_hash)
        if (await db.execute(rev_stmt)).scalar_one_or_none():
            return None

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            return None
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
    except Exception:
        pass
    return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate Bearer access token, verify non-revocation, and return authenticated User record."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    revoked_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has been revoked. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Enforce token non-revocation check
    token_hash = RevokedToken.hash_token(token)
    rev_stmt = select(RevokedToken).where(RevokedToken.token_hash == token_hash)
    if (await db.execute(rev_stmt)).scalar_one_or_none():
        raise revoked_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id, role=payload.get("role"))
    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.id == token_data.sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
        )
    return user


def require_roles(allowed_roles: List[UserRole]):
    """Enforce Role-Based Access Control (RBAC) dependency."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker


# Role-specific shortcut dependencies
get_current_clinician = require_roles([UserRole.DOCTOR, UserRole.NURSE, UserRole.STAFF])
get_current_staff = require_roles([UserRole.STAFF, UserRole.NURSE])
get_current_doctor = require_roles([UserRole.DOCTOR])
get_current_admin = require_roles([UserRole.ADMIN])
get_current_patient = require_roles([UserRole.PATIENT])
get_current_staff_or_admin = require_roles([UserRole.DOCTOR, UserRole.NURSE, UserRole.STAFF, UserRole.ADMIN])
get_intake_user = require_roles([UserRole.PATIENT, UserRole.DOCTOR, UserRole.NURSE, UserRole.STAFF])


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address for HIPAA-ready audit logging."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
