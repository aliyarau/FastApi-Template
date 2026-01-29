"""Error handlers for API responses."""

import logging
from typing import Any, cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError  # type: ignore
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, Response

from .exceptions import AppError

log = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str | None:
    """Extract request id from state or header."""
    rid = getattr(request.state, "request_id", None)
    return rid or request.headers.get("X-Request-ID")


def _code_by_status(status: int) -> str:
    """Map HTTP status to error code."""
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
    }
    if status >= 500:
        return "INTERNAL_ERROR"
    return mapping.get(status, "HTTP_ERROR")


def _make_error_response(
    code: str, message: str, status: int, request_id: str | None, details: Any = None
) -> JSONResponse:
    """Build JSON error response payload."""
    payload: dict[str, Any] = {"error": {"code": code, "message": message, "requestId": request_id}}
    if details not in (None, [], {}):
        payload["error"]["details"] = details
    return JSONResponse(payload, status_code=status)


async def app_error_handler(request: Request, exc: Exception) -> Response:
    """Handle application-level errors."""
    err = cast(AppError, exc)
    rid = _get_request_id(request)
    if err.status >= 500:
        log.exception("AppError %s: %s", err.code, err.message, extra={"request_id": rid})
    else:
        log.warning("AppError %s: %s", err.code, err.message, extra={"request_id": rid})
    return _make_error_response(err.code, err.message, err.status, rid, err.details)


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle HTTP exceptions."""
    http_exc = cast(StarletteHTTPException, exc)
    rid = _get_request_id(request)
    status = http_exc.status_code
    code = _code_by_status(status)
    msg = http_exc.detail if isinstance(http_exc.detail, str) else str(http_exc.detail)
    if status >= 500:
        log.error("HTTPException %s: %s", status, msg, extra={"request_id": rid})
    else:
        log.info("HTTPException %s: %s", status, msg, extra={"request_id": rid})
    return _make_error_response(code, msg, status, rid)


async def validation_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle request validation errors."""
    val_exc = cast(RequestValidationError, exc)
    rid = _get_request_id(request)
    details = val_exc.errors()
    log.info("ValidationError: %s", details, extra={"request_id": rid})
    return _make_error_response("VALIDATION_ERROR", "Validation failed.", 422, rid, details)


async def integrity_error_handler(request: Request, exc: Exception) -> Response:
    """Handle database integrity errors."""
    integ_exc = cast(IntegrityError, exc)
    rid = _get_request_id(request)
    log.warning("IntegrityError: %s", str(integ_exc), extra={"request_id": rid})
    return _make_error_response("CONFLICT", "Integrity constraint violated.", 409, rid)


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle unhandled exceptions."""
    rid = _get_request_id(request)
    log.exception("Unhandled exception: %s", str(exc), extra={"request_id": rid})
    return _make_error_response("INTERNAL_ERROR", "Internal server error.", 500, rid)
