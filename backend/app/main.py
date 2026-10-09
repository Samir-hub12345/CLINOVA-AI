"""CLINOVA AI — Application Entrypoint.

Continuous Care Intelligence System.
Non-diagnostic, advisory, human-in-the-loop clinical decision support.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import (
    ClinovaAPIError,
    clinova_api_error_handler,
    validation_error_handler,
    http_exception_handler,
    generic_exception_handler,
)
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

# Structured Error Contract Handlers
app.add_exception_handler(ClinovaAPIError, clinova_api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.middleware("http")
async def clinical_safety_disclaimer_middleware(request: Request, call_next):
    """Enforces non-diagnostic clinical safety header and standard browser security headers across all HTTP responses."""
    response = await call_next(request)
    response.headers["X-Clinical-Safety"] = "Non-Diagnostic-Advisory-Only"
    response.headers["X-Human-In-The-Loop"] = "Required-Before-Action"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
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
@app.get("/health/live", tags=["System"])
async def health_live():
    """Liveness probe: verifies that the ASGI backend process is responding."""
    return {
        "status": "healthy",
        "liveness": "alive",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/ready", tags=["System"])
async def health_ready():
    """Readiness probe: verifies that database connectivity and core configuration are ready to serve."""
    try:
        import asyncio
        from sqlalchemy import text
        from app.db.session import async_session_factory

        async def _ping_db():
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))

        await asyncio.wait_for(_ping_db(), timeout=3.0)
        return {
            "status": "ready",
            "database": "connected",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    except Exception as exc:
        logger.error("Readiness probe database check failed: %s", str(exc))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unready",
                "database": "unavailable",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            },
        )


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)