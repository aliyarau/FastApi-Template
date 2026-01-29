"""Auth request/response schemas."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from uuid import UUID

from pydantic import Field

from api.schemas.base import ApiBaseModel, ApiInputModel
from auth.domain import LoginResult, UserProfile


class LoginRequest(ApiInputModel):
    """Login request payload."""

    login: str = Field(min_length=1, description="Логин пользователя (sAMAccountName или DOMAIN\\login)")
    password: str = Field(min_length=1, description="Пароль пользователя")


class AuthUser(ApiBaseModel):
    """Authenticated user schema."""

    id: int
    ad_login: str
    ad_guid: UUID
    full_name: str | None = None
    email: str | None = None
    department: str | None = None
    title: str | None = None
    role: str
    last_login_at: datetime | None = None

    @classmethod
    def from_profile(cls, profile: UserProfile) -> AuthUser:
        return cls.model_validate(asdict(profile))


class LoginResponse(ApiBaseModel):
    """Login response payload."""

    access_token: str = Field(description="JWT access token")
    user: AuthUser

    @classmethod
    def from_result(cls, result: LoginResult) -> LoginResponse:
        return cls(access_token=result.access_token, user=AuthUser.from_profile(result.user))


__all__ = ["LoginRequest", "LoginResponse", "AuthUser"]
