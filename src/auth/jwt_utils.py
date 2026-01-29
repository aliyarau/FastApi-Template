"""JWT helper functions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from auth.exceptions import TokenError
from config import settings


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _encode(payload: dict[str, Any], *, expires_delta: timedelta, token_type: str | None) -> str:
    now = _now()
    claims = payload.copy()
    claims["iat"] = int(now.timestamp())
    claims["exp"] = int((now + expires_delta).timestamp())
    if token_type:
        claims["typ"] = token_type
    if settings.jwt.issuer:
        claims.setdefault("iss", settings.jwt.issuer)
    if settings.jwt.audience:
        claims.setdefault("aud", settings.jwt.audience)
    secret = settings.jwt.secret.get_secret_value()
    return jwt.encode(claims, secret, algorithm=settings.jwt.algorithm)


def create_access_token(payload: dict[str, Any], *, expires_in_hours: int | None = None) -> str:
    """Create a short-lived access token."""
    ttl_hours = expires_in_hours or settings.jwt.access_token_ttl_hours
    return _encode(payload, expires_delta=timedelta(hours=ttl_hours), token_type="access")


def create_refresh_token(payload: dict[str, Any], *, expires_in_days: int | None = None) -> str:
    """Create a long-lived refresh token."""
    ttl_days = expires_in_days or settings.jwt.refresh_token_ttl_days
    extra_payload = payload.copy()
    extra_payload.setdefault("typ", "refresh")
    return _encode(extra_payload, expires_delta=timedelta(days=ttl_days), token_type="refresh")


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT."""
    secret = settings.jwt.secret.get_secret_value()
    options = {"require": ["exp", "iat"], "verify_aud": bool(settings.jwt.audience)}
    decode_kwargs: dict[str, Any] = {
        "algorithms": [settings.jwt.algorithm],
        "options": options,
    }
    if settings.jwt.audience:
        decode_kwargs["audience"] = settings.jwt.audience
    if settings.jwt.issuer:
        decode_kwargs["issuer"] = settings.jwt.issuer
    try:
        return jwt.decode(token, secret, **decode_kwargs)
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token expired", code="token_expired", status=401) from exc
    except jwt.InvalidAudienceError as exc:
        raise TokenError("Invalid audience", code="invalid_audience", status=401) from exc
    except jwt.InvalidIssuerError as exc:
        raise TokenError("Invalid issuer", code="invalid_issuer", status=401) from exc
    except jwt.PyJWTError as exc:
        raise TokenError("Token is invalid", code="invalid_token", status=401) from exc


__all__ = ["create_access_token", "create_refresh_token", "decode_token"]
