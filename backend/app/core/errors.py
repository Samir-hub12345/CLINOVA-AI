import enum
import logging
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("clinova.errors")


class ErrorCode(str, enum.Enum):
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class APIErrorResponse(BaseModel):
    """Standardized, HIPAA-compliant API error envelope."""
    error_code: str = Field(..., description="Canonical machine-readable error category")
    message: str = Field(..., description="Human-readable safe error message")
    detail: str = Field(..., description="Backwards-compatible detail string")
    details: Optional[Any] = Field(None, description="Safe contextual metadata or validation issues")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    path: Optional[str] = None


def status_to_error_code(status_code: int) -> ErrorCode:
    """Maps HTTP status codes to standardized Clinova error categories."""
    if status_code == 401:
        return ErrorCode.AUTHENTICATION_ERROR
    elif status_code == 403:
        return ErrorCode.AUTHORIZATION_ERROR
    elif status_code in (400, 422):
        return ErrorCode.VALIDATION_ERROR
    elif status_code == 404:
        return ErrorCode.NOT_FOUND
    elif status_code == 409:
        return ErrorCode.CONFLICT
    elif status_code in (502, 503, 504):
        return ErrorCode.DEPENDENCY_ERROR
    elif status_code == 429:
        return ErrorCode.PROCESSING_ERROR
    else:
        return ErrorCode.INTERNAL_ERROR


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Formats HTTPException into the standardized, safe error envelope without exposing internal traces."""
    code = status_to_error_code(exc.status_code)
    # Detail can be a string or dict
    msg = exc.detail if isinstance(exc.detail, str) else "Request could not be processed."
    details = exc.detail if isinstance(exc.detail, (dict, list)) else None

    # Do not leak internal stack traces or database info on 500 errors
    if exc.status_code == 500:
        logger.error(f"Internal server error on {request.url.path}: {exc.detail}")
        msg = "An internal server error occurred. Please contact system administrator."
        details = None

    payload = APIErrorResponse(
        error_code=code.value,
        message=msg,
        detail=msg,
        details=details,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats Pydantic request validation errors into the safe error envelope."""
    clean_errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        clean_errors.append({
            "field": loc or "request_body",
            "issue": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })

    msg = "Request validation failed. Please check submitted fields."
    payload = APIErrorResponse(
        error_code=ErrorCode.VALIDATION_ERROR.value,
        message=msg,
        detail=clean_errors[0]["issue"] if clean_errors else msg,
        details=clean_errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches all unhandled exceptions, logs them securely, and returns a safe, unrevealing 500 response."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    msg = "An unexpected system error occurred. The technical team has been notified."
    payload = APIErrorResponse(
        error_code=ErrorCode.INTERNAL_ERROR.value,
        message=msg,
        detail=msg,
        details=None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload.model_dump(),
    )
