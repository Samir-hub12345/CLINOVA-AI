"""CLINOVA AI — Authentication & Identity Schemas.

Continuous Care Intelligence System.
Phase 14: Authentication + RBAC + Authorization + Identity Hardening.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials payload for authenticating a user."""
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")


class UserRead(BaseModel):
    """Canonical user identity response model."""
    id: str
    username: Optional[str] = None
    email: str
    full_name: str
    role: str
    facility_id: Optional[str] = None
    facility_name: Optional[str] = None
    patient_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Standard Bearer token envelope with profile."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class LogoutResponse(BaseModel):
    """Response returned upon successful token revocation."""
    message: str
    status: str = "revoked"


class PersonaResponse(BaseModel):
    """Evaluation persona profile representation."""
    id: str
    username: Optional[str] = None
    full_name: str
    email: str
    role: str
    facility_id: Optional[str] = None
    facility_name: Optional[str] = None


class SwitchPersonaRequest(BaseModel):
    """Request payload to switch evaluation persona."""
    persona_id: str


class SwitchPersonaResponse(BaseModel):
    """Response for rapid persona switching containing new token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
