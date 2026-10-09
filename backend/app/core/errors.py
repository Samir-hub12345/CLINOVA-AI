"""CLINOVA AI — Core Structured Error Contract.

Continuous Care Intelligence System.
Phase 13: Core Backend Foundation, Master Case Persistence & API Layer.
Grounded in Section 22 of Master Specification.

Mandatory Error Categories:
- VALIDATION_ERROR (422)
- NOT_FOUND (404)
- AUTHORIZATION_ERROR (401 / 403)
- CONFLICT (409)
- INVALID_STATE_TRANSITION (422)
- DATABASE_ERROR (500)
- UNSUPPORTED_OPERATION (422)

Safety Invariants:
Never expose stack traces, raw SQL queries, database credentials,
filesystem paths, or internal tokens to client callers.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("clinova.errors")


class ClinovaAPIError(Exception):
    """Authoritative structured application error for Clinova AI."""

    def __init__(
        self,
        category: str = "ERROR",
        message: str = "",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        code: Optional[str] = None,
    ):
        actual_category = code or category
        self.category = actual_category
        self.code = actual_category
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.correlation_id = correlation_id or f"corr-{uuid.uuid4()}"
        super().__init__(message)


def format_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates the standardized JSON error envelope."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "correlation_id": correlation_id or f"corr-{uuid.uuid4()}",
        }
    }


async def clinova_api_error_handler(request: Request, exc: ClinovaAPIError) -> JSONResponse:
    """Handles domain-specific Clinova API exceptions."""
    logger.warning(
        "ClinovaAPIError [%s] %s (HTTP %d, Correlation: %s)",
        exc.category,
        exc.message,
        exc.status_code,
        exc.correlation_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=exc.category,
            message=exc.message,
            details=exc.details,
            correlation_id=exc.correlation_id,
        ),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Sanitizes Pydantic input validation failures without exposing internal paths."""
    correlation_id = f"corr-{uuid.uuid4()}"
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(item) for item in err.get("loc", []) if item != "body")
        msg = err.get("msg", "Invalid value")
        errors.append({"field": loc or "payload", "message": msg})

    logger.info("Validation error at %s: %s (Correlation: %s)", request.url.path, errors, correlation_id)
    return JSONResponse(
        status_code=422,
        content=format_error_response(
            code="VALIDATION_ERROR",
            message="Request payload failed structural or clinical boundary validation.",
            details={"errors": errors},
            correlation_id=correlation_id,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Maps standard HTTPExceptions into Clinova's structured error format."""
    correlation_id = f"corr-{uuid.uuid4()}"
    code_map = {
        400: "VALIDATION_ERROR",
        401: "AUTHORIZATION_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }
    category = code_map.get(exc.status_code, "DATABASE_ERROR")
    detail_str = str(exc.detail) if exc.detail else "An HTTP error occurred."

    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=category,
            message=detail_str,
            details={},
            correlation_id=correlation_id,
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled errors and strictly suppresses internal stack traces and secrets."""
    correlation_id = f"corr-{uuid.uuid4()}"
    # Log internally for diagnostics
    logger.error("Unhandled exception [%s]: %s", correlation_id, str(exc), exc_info=True)

    # Return safe de-identified error message
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            code="DATABASE_ERROR",
            message="An internal server error occurred. System administrators have been notified.",
            details={"reference": correlation_id},
            correlation_id=correlation_id,
        ),
    )
