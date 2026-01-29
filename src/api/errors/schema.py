"""Error response schemas."""

from __future__ import annotations

from typing import Any

from api.schemas.base import ApiBaseModel


class ApiErrorPayload(ApiBaseModel):
    """Error payload schema."""

    code: str
    message: str
    request_id: str | None = None
    details: Any | None = None


class ApiErrorResponse(ApiBaseModel):
    """Error response schema."""

    error: ApiErrorPayload


_ERROR_DESCRIPTIONS: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    423: "Locked",
}


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Build OpenAPI error responses for given status codes."""
    responses: dict[int | str, dict[str, Any]] = {}
    for code in codes:
        responses[code] = {
            "model": ApiErrorResponse,
            "description": _ERROR_DESCRIPTIONS.get(code, "Error"),
        }
    return responses
