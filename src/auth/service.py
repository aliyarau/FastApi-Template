"""Authentication service orchestrating LDAP and database access."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain import LdapUserInfo, LoginResult, RoleLiteral, UserProfile
from auth.exceptions import AuthError, TokenError
from auth.jwt_utils import create_access_token, create_refresh_token, decode_token
from auth.ldap_client import ldap_authenticate, ldap_fetch_user_by_login
from config import settings
from db.engine import db
from db.models.user.user import User
from db.repositories.app.auth import deactivate_user_by_guid, sync_user_from_directory

log = logging.getLogger(__name__)


class AuthService:
    """Authenticate users and issue tokens."""

    def __init__(self) -> None:
        role_pairs = []
        for role, dn in (
            ("admin", settings.ldap.groups.admin),
            ("editor", settings.ldap.groups.editor),
            ("viewer", settings.ldap.groups.viewer),
        ):
            if not dn:
                continue
            role_pairs.append((cast(RoleLiteral, role), dn))
        self._role_priority: tuple[tuple[RoleLiteral, str], ...] = tuple(role_pairs)

    async def login(self, session: AsyncSession, *, login: str, password: str) -> LoginResult:
        normalized_login = login.strip()
        if not normalized_login or not password:
            raise AuthError("invalid_credentials", "Login or password is empty", status=401)

        info = await asyncio.to_thread(ldap_authenticate, normalized_login, password)
        return await self._complete_auth(session, info, update_last_login=True)

    async def refresh(self, session: AsyncSession, *, refresh_token: str) -> LoginResult:
        if not refresh_token:
            raise AuthError("missing_refresh", "Refresh token is required", status=401)

        payload = decode_token(refresh_token)
        if payload.get("typ") != "refresh":
            raise TokenError("Token is not a refresh token", code="invalid_token_type", status=401)

        ad_login = payload.get("ad_login")
        if not isinstance(ad_login, str):
            raise TokenError("Refresh token payload is missing login", code="invalid_token_payload", status=401)

        info = await asyncio.to_thread(ldap_fetch_user_by_login, ad_login)
        return await self._complete_auth(session, info, update_last_login=False)

    async def _complete_auth(
        self,
        session: AsyncSession,
        info: LdapUserInfo | None,
        *,
        update_last_login: bool,
    ) -> LoginResult:
        if not info:
            raise AuthError("invalid_credentials", "Invalid login or password", status=401)

        role = self._resolve_role(info)
        if not role:
            await self._deactivate_user(info.ad_guid)
            raise AuthError("forbidden", "User does not have required group", status=403)

        user = await self._sync_user(session, info, update_last_login=update_last_login, role=role)
        access_token, refresh_token = self._issue_tokens(user, role)
        profile = self._make_profile(user, role)
        log.info("User %s authenticated", user.ad_login)
        return LoginResult(access_token=access_token, refresh_token=refresh_token, user=profile)

    def _resolve_role(self, info: LdapUserInfo) -> RoleLiteral | None:
        groups_cf = [group.casefold() for group in info.groups]
        for role, target_dn in self._role_priority:
            target_cf = target_dn.casefold()
            if any(target_cf in group for group in groups_cf):
                return role
        return None

    async def _sync_user(
        self, session: AsyncSession, info: LdapUserInfo, *, update_last_login: bool, role: str
    ) -> User:
        user_ids = []
        for name in info.subordinates:
            result = await session.execute(select(User.id).where(User.full_name == name))
            user_id = result.scalar_one_or_none()
            if user_id is not None:
                user_ids.append(user_id)
        return await sync_user_from_directory(
            session,
            ad_guid=info.ad_guid,
            ad_login=info.ad_login,
            full_name=info.full_name,
            email=info.email,
            department=info.department,
            title=info.title,
            update_last_login=update_last_login,
            supervisor=info.supervisor if info.supervisor else "",
            subordinates=user_ids,
            role=role,
        )

    def _issue_tokens(self, user: User, role: RoleLiteral) -> tuple[str, str]:
        payload: dict[str, Any] = {
            "sub": str(user.ad_guid),
            "user_id": user.id,
            "ad_login": user.ad_login,
            "role": role,
            "full_name": user.full_name,
            "department": user.department,
            "email": user.email,
            "subordinates": user.subordinates,
        }
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token({key: payload[key] for key in ("sub", "user_id", "ad_login", "role")})
        return access_token, refresh_token

    def _make_profile(self, user: User, role: RoleLiteral) -> UserProfile:
        if user.id is None:
            raise AuthError("user_not_persisted", "User must be persisted before response", status=500)
        return UserProfile(
            id=user.id,
            ad_login=user.ad_login,
            ad_guid=user.ad_guid,
            full_name=user.full_name,
            email=user.email,
            department=user.department,
            title=user.title,
            role=role,
            last_login_at=user.last_login_at,
        )

    async def _deactivate_user(self, ad_guid: UUID) -> None:
        async with db.session() as standalone_session:
            await deactivate_user_by_guid(standalone_session, ad_guid)
            await standalone_session.commit()


auth_service = AuthService()


__all__ = ["AuthService", "auth_service"]
