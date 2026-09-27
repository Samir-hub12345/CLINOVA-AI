from datetime import timedelta
from typing import Union, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user, get_current_admin, get_client_ip
from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.services.audit import AuditService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    if user_in.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Administrator accounts cannot be self-registered.")
    if user_in.role != UserRole.PATIENT:
        if not user_in.facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Public registration creates patient accounts only. Staff accounts are provisioned by the administrator.",
            )
        from app.models.facility import Facility
        fac_stmt = select(Facility).where(Facility.id == user_in.facility_id)
        fac_res = await db.execute(fac_stmt)
        if not fac_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid facility specified for staff registration.",
            )
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        facility_id=user_in.facility_id,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await AuditService.log_event(
        db=db,
        action="USER_REGISTER",
        resource_type="USER",
        resource_id=user.id,
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=f"New user registered with role {user.role.value}",
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    login_data: Optional[LoginRequest] = None,
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(lambda: None),
):
    """Authenticate with email and password to receive a JWT access token."""
    # Determine email and password from JSON body or OAuth2 form data
    email = None
    password = None

    if form_data and form_data.username:
        email = form_data.username
        password = form_data.password
    elif login_data:
        email = login_data.email
        password = login_data.password
    else:
        # Try to parse JSON body manually if neither was resolved
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/username and password are required.",
        )

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        await AuditService.log_event(
            db=db,
            action="LOGIN_FAILED",
            resource_type="USER",
            user_email=email,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            details="Invalid email or password",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        expires_delta=access_token_expires,
    )

    await AuditService.log_event(
        db=db,
        action="LOGIN_SUCCESS",
        resource_type="USER",
        resource_id=user.id,
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details="User authenticated successfully",
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    """Retrieve profile of the currently authenticated user."""
    return current_user
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_facility_users(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin only: Retrieve all registered facility user accounts."""
    stmt = select(User).order_by(User.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.put("/users/{user_id}/status", response_model=UserResponse)
async def toggle_user_status(
    user_id: str,
    is_active: bool,
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin only: Activate or deactivate a user account."""
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    target_user = res.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User account not found.")

    if target_user.id == current_user.id and not is_active:
        raise HTTPException(status_code=400, detail="Cannot deactivate own admin account.")

    target_user.is_active = is_active
    await db.commit()
    await db.refresh(target_user)

    await AuditService.log_event(
        db=db,
        action="USER_STATUS_UPDATED",
        resource_type="USER",
        resource_id=target_user.id,
        user=current_user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=f"User {target_user.email} active status set to {is_active} by admin {current_user.email}",
    )
    return target_user
