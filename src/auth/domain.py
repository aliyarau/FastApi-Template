"""Domain models for authentication."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

RoleLiteral = Literal["admin", "editor", "viewer"]


@dataclass(slots=True)
class LdapUserInfo:
    """LDAP user information."""

    ad_login: str
    ad_guid: UUID
    supervisor: str | None
    full_name: str | None
    email: str | None
    department: str | None
    title: str | None
    groups: list[str]
    subordinates: list[str]


@dataclass(slots=True)
class UserProfile:
    """User profile returned by authentication."""

    id: int
    ad_login: str
    ad_guid: UUID
    full_name: str | None
    email: str | None
    department: str | None
    title: str | None
    role: RoleLiteral
    last_login_at: datetime | None


@dataclass(slots=True)
class LoginResult:
    """Result of successful authentication."""

    access_token: str
    refresh_token: str
    user: UserProfile


__all__ = ["RoleLiteral", "LdapUserInfo", "UserProfile", "LoginResult"]
