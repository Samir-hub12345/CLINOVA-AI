"""CLINOVA AI — Authentication, Identity & Session Router.

Continuous Care Intelligence System.
Phase 14: Authentication + RBAC + Authorization + Identity Hardening.
Grounded in DOC-03 (Role-Based Access Control Specification).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.errors import ClinovaAPIError
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    revoke_token,
    get_current_actor,
    ActorContext,
)
from app.core.policy import record_security_audit_event
from app.db.session import get_db
from app.db.models import User, Facility, utc_now
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserRead,
    LogoutResponse,
    PersonaResponse,
    SwitchPersonaRequest,
    SwitchPersonaResponse,
)

router = APIRouter()

# Global fallback for rapid evaluation switcher
ACTIVE_USER_ID = "usr-doc-01"


async def _build_user_read(user: User, db: AsyncSession) -> UserRead:
    """Helper to convert User model to UserRead with facility name."""
    fac_name = None
    if user.facility_id:
        fac = await db.get(Facility, user.facility_id)
        if fac:
            fac_name = fac.name

    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        facility_id=user.facility_id,
        facility_name=fac_name,
        patient_id=user.patient_id,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
    )


@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticates user credentials against authoritative database records.
    Issues a cryptographically signed Bearer JWT token upon success.
    Enforces server-side rejection of inactive accounts and invalid credentials.
    """
    # 1. Look up user by username, email, or id
    clean_identifier = req.username.strip()
    stmt = select(User).where(
        (User.username == clean_identifier)
        | (User.email == clean_identifier)
        | (User.id == clean_identifier)
    )
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        await record_security_audit_event(
            db=db,
            actor_id="anonymous",
            actor_role="UNAUTHENTICATED",
            action="auth.login_failure",
            object_type="USER",
            object_id=clean_identifier,
            result="FAILURE",
            details={"reason": "User not found"},
        )
        await db.commit()
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Invalid username or password.",
            status_code=401,
        )

    # 2. Verify hashed password
    if not user.hashed_password or not verify_password(req.password, user.hashed_password):
        await record_security_audit_event(
            db=db,
            actor_id=user.id,
            actor_role=user.role,
            action="auth.login_failure",
            object_type="USER",
            object_id=user.id,
            result="FAILURE",
            details={"reason": "Password mismatch"},
        )
        await db.commit()
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Invalid username or password.",
            status_code=401,
        )

    # 3. Check account active status
    if not user.is_active:
        await record_security_audit_event(
            db=db,
            actor_id=user.id,
            actor_role=user.role,
            action="auth.login_inactive",
            object_type="USER",
            object_id=user.id,
            result="BLOCKED",
            details={"reason": "Account deactivated"},
        )
        await db.commit()
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="User account is deactivated. Contact system administration.",
            status_code=403,
        )

    # 4. Update last_login_at timestamp
    user.last_login_at = utc_now()

    # 5. Issue JWT access token
    token_claims = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "facility_id": user.facility_id,
    }
    access_token = create_access_token(token_claims)

    # 6. Audit successful login
    await record_security_audit_event(
        db=db,
        actor_id=user.id,
        actor_role=user.role,
        action="auth.login_success",
        object_type="USER",
        object_id=user.id,
        result="SUCCESS",
        details={"facility_id": user.facility_id},
    )
    await db.commit()

    user_read = await _build_user_read(user, db)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_read,
    )


@router.post("/logout", response_model=LogoutResponse, tags=["Authentication"])
async def logout(
    request: Request,
    actor: ActorContext = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    """
    Terminates the active session and adds the bearer token to the revocation blacklist.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        await revoke_token(token, db, user_id=actor.actor_id, reason="user_logout")

    await record_security_audit_event(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="auth.logout",
        object_type="USER",
        object_id=actor.actor_id,
        result="SUCCESS",
    )
    await db.commit()

    return LogoutResponse(
        message="Session successfully terminated and token invalidated.",
        status="revoked",
    )


@router.get("/me", response_model=UserRead, tags=["Authentication"])
async def get_current_user_profile(
    actor: ActorContext = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the authoritative identity profile of the currently authenticated actor.
    """
    user = await db.get(User, actor.actor_id)
    if not user:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"User record for actor '{actor.actor_id}' not found.",
            status_code=404,
        )

    return await _build_user_read(user, db)


@router.get("/personas", response_model=List[PersonaResponse], tags=["Authentication"])
async def list_available_personas(db: AsyncSession = Depends(get_db)):
    """
    Lists available synthetic evaluation personas for clinical demonstration.
    """
    stmt = select(User).where(User.is_active == True).order_by(User.role)
    res = await db.execute(stmt)
    users = res.scalars().all()

    personas = []
    for u in users:
        fac_name = None
        if u.facility_id:
            fac = await db.get(Facility, u.facility_id)
            if fac:
                fac_name = fac.name
        personas.append(
            PersonaResponse(
                id=u.id,
                username=u.username,
                full_name=u.full_name,
                email=u.email,
                role=u.role,
                facility_id=u.facility_id,
                facility_name=fac_name,
            )
        )
    return personas


@router.post("/switch-persona", response_model=SwitchPersonaResponse, tags=["Authentication"])
async def switch_persona(
    req: SwitchPersonaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Rapid evaluation persona switcher for clinical workstation testing.
    Issues a verified Bearer token for the target persona.
    """
    global ACTIVE_USER_ID
    target_id = req.persona_id.strip()
    user = await db.get(User, target_id)
    if not user:
        stmt = select(User).where((User.username == target_id) | (User.email == target_id))
        res = await db.execute(stmt)
        user = res.scalars().first()

    if not user:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Persona '{req.persona_id}' not found in synthetic directory.",
            status_code=404,
        )

    if not user.is_active:
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Persona '{req.persona_id}' is deactivated.",
            status_code=403,
        )

    ACTIVE_USER_ID = user.id
    token_claims = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "facility_id": user.facility_id,
    }
    access_token = create_access_token(token_claims)

    user_read = await _build_user_read(user, db)
    return SwitchPersonaResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_read,
    )
