"""Refresh token cookie helpers."""

from __future__ import annotations

from fastapi import Request, Response

from api.errors.exceptions import AppError
from config import settings

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/"


def read_refresh_cookie(request: Request) -> str:
    """Read refresh token from cookies."""
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise AppError("missing_refresh_cookie", "Refresh token cookie is missing", status=401)
    return token


def set_refresh_cookie(response: Response, token: str) -> None:
    """Set refresh token cookie."""
    max_age = settings.jwt.refresh_token_ttl_days * 24 * 60 * 60
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        max_age=max_age,
        httponly=True,
        secure=False,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
    )


def clear_refresh_cookie(response: Response) -> None:
    """Clear refresh token cookie."""
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


__all__ = ["read_refresh_cookie", "set_refresh_cookie", "clear_refresh_cookie"]
