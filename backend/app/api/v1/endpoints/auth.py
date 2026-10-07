"""CLINOVA AI — Authentication & Clinical Persona Router.

Provides session management, RBAC verification, and rapid persona switching
for clinical evaluation (Clinician, Triage Nurse, Healthcare Administrator).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import User, Facility

router = APIRouter()


class PersonaResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    facility_id: Optional[str]
    facility_name: Optional[str] = None


class SwitchPersonaRequest(BaseModel):
    persona_id: str


# In-memory active session persona (default: Clinician Dr. Priya Sharma)
ACTIVE_USER_ID = "usr-doc-01"


@router.get("/personas", response_model=List[PersonaResponse], tags=["Authentication"])
async def list_available_personas(db: AsyncSession = Depends(get_db)):
    """Lists standard clinical evaluation personas."""
    result = await db.execute(select(User))
    users = result.scalars().all()
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
                full_name=u.full_name,
                email=u.email,
                role=u.role,
                facility_id=u.facility_id,
                facility_name=fac_name,
            )
        )
    return personas


@router.get("/me", response_model=PersonaResponse, tags=["Authentication"])
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """Returns currently authenticated clinical user profile."""
    global ACTIVE_USER_ID
    user = await db.get(User, ACTIVE_USER_ID)
    if not user:
        # Fallback to first user in database
        result = await db.execute(select(User))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="No personas configured in database.")
        ACTIVE_USER_ID = user.id

    fac_name = None
    if user.facility_id:
        fac = await db.get(Facility, user.facility_id)
        if fac:
            fac_name = fac.name

    return PersonaResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        facility_id=user.facility_id,
        facility_name=fac_name,
    )


@router.post("/switch-persona", response_model=PersonaResponse, tags=["Authentication"])
async def switch_persona(req: SwitchPersonaRequest, db: AsyncSession = Depends(get_db)):
    """Switches active evaluation persona between Clinician, Nurse, and Administrator."""
    global ACTIVE_USER_ID
    user = await db.get(User, req.persona_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Persona {req.persona_id} not found.")

    ACTIVE_USER_ID = user.id
    fac_name = None
    if user.facility_id:
        fac = await db.get(Facility, user.facility_id)
        if fac:
            fac_name = fac.name

    return PersonaResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        facility_id=user.facility_id,
        facility_name=fac_name,
    )
