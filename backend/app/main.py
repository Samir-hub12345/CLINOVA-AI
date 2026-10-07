"""CLINOVA AI — Application Entrypoint.

Continuous Care Intelligence System.
Non-diagnostic, advisory, human-in-the-loop clinical decision support.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.api.v1.router import api_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing %s v%s in %s mode...", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    logger.info("Clinical Governance: Non-Diagnostic | Advisory Only | Human-in-the-Loop Required")
    logger.info("Core Pillars: CareGraph | FacilityGraph | SignalGraph | Orchestration Engine")
    try:
        await init_db()
        logger.info("Database schemas and synthetic network facilities successfully initialized.")
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Clinova AI: Continuous Care Intelligence Platform. "
        "Provides CareGraph (patient state), FacilityGraph (care feasibility), "
        "SignalGraph (operational telemetry), and Orchestration (safest achievable care action). "
        "Strictly non-diagnostic and advisory with mandatory qualified human review."
    ),
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def clinical_safety_disclaimer_middleware(request: Request, call_next):
    """Enforces non-diagnostic clinical safety header across all HTTP responses."""
    response = await call_next(request)
    response.headers["X-Clinical-Safety"] = "Non-Diagnostic-Advisory-Only"
    response.headers["X-Human-In-The-Loop"] = "Required-Before-Action"
    return response


# Root & Health Endpoints
@app.get("/", tags=["Root"])
async def root():
    """System identification and safety notice."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "philosophy": "Continuous Care Intelligence",
        "notice": "Non-diagnostic clinical decision support system. For authorized clinical review only.",
    }


@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint for container orchestrators and local monitors."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)