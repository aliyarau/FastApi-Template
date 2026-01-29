from __future__ import annotations

from dataclasses import dataclass
from typing import cast
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.errors.exceptions import AppError
from auth.domain import RoleLiteral
from auth.exceptions import TokenError
from auth.jwt_utils import decode_token


@dataclass(slots=True)
class TokenUser:
    user_id: int
    ad_guid: UUID
    ad_login: str
    role: RoleLiteral
    full_name: str | None
    department: str | None
    email: str | None
    subordinates: list[int] | None


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),  # noqa: B008
) -> TokenUser:
    if not credentials:
        raise AppError("UNAUTHORIZED", "Missing Authorization header", status=401)
    if credentials.scheme.lower() != "bearer":
        raise AppError("UNAUTHORIZED", "Expected Bearer token", status=401)
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise AppError(exc.code, exc.message, status=exc.status) from exc

    token_type = payload.get("typ")
    if token_type != "access":
        raise AppError("INVALID_TOKEN_TYPE", "Access token required", status=401)

    try:
        ad_guid = UUID(str(payload["sub"]))
        user_id = int(payload["user_id"])
        ad_login = str(payload["ad_login"])
    except (KeyError, ValueError) as exc:
        raise AppError("INVALID_TOKEN_PAYLOAD", "Access token payload is invalid", status=401) from exc

    role = payload.get("role")
    if role not in ("admin", "editor", "viewer"):
        raise AppError("INVALID_ROLE", "Unknown role in token", status=403)

    role_literal = cast(RoleLiteral, role)
    return TokenUser(
        user_id=user_id,
        ad_guid=ad_guid,
        ad_login=ad_login,
        role=role_literal,
        full_name=payload.get("full_name"),
        department=payload.get("department"),
        email=payload.get("email"),
        subordinates=payload.get("subordinates"),
    )


__all__ = ["TokenUser", "get_current_user"]
