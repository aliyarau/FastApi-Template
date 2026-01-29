"""Tests for authentication service."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("pydantic")
pytest.importorskip("jwt")
pytest.importorskip("ldap3")

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest

from auth.domain import LdapUserInfo
from auth.exceptions import AuthError
from auth.jwt_utils import create_refresh_token
from auth.service import AuthService
from config import settings
from db.models.user.user import User


class DummySession:
    async def execute(self, *_: Any, **__: Any) -> Any:
        raise AssertionError("Should not be called in this test")


def _ldap_info() -> LdapUserInfo:
    return LdapUserInfo(
        ad_login="user",
        ad_guid=uuid4(),
        supervisor=None,
        full_name="User Name",
        email="user@example.com",
        department="IT",
        title="Dev",
        groups=[settings.ldap.groups.admin or "admin"],
        subordinates=[],
    )


def _user() -> User:
    user = User(ad_guid=UUID(int=1), ad_login="user")
    user.id = 1
    user.full_name = "User Name"
    user.email = "user@example.com"
    user.department = "IT"
    user.title = "Dev"
    user.subordinates = []
    user.last_login_at = datetime.utcnow()
    return user


@pytest.mark.asyncio
async def test_login_success(monkeypatch: Any) -> None:
    service = AuthService()
    info = _ldap_info()
    user = _user()

    async def fake_sync_user(*_: Any, **__: Any) -> User:
        return user

    monkeypatch.setattr(service, "_sync_user", fake_sync_user)
    monkeypatch.setattr("auth.service.ldap_authenticate", lambda *_: info)

    result = await service.login(DummySession(), login="user", password="pass")
    assert result.user.ad_login == "user"
    assert result.access_token
    assert result.refresh_token


@pytest.mark.asyncio
async def test_login_empty_credentials() -> None:
    service = AuthService()
    with pytest.raises(AuthError):
        await service.login(DummySession(), login="", password="")


@pytest.mark.asyncio
async def test_refresh_success(monkeypatch: Any) -> None:
    service = AuthService()
    info = _ldap_info()
    user = _user()

    async def fake_sync_user(*_: Any, **__: Any) -> User:
        return user

    monkeypatch.setattr(service, "_sync_user", fake_sync_user)
    monkeypatch.setattr("auth.service.ldap_fetch_user_by_login", lambda *_: info)

    token = create_refresh_token({"sub": str(user.ad_guid), "user_id": user.id, "ad_login": "user", "role": "admin"})
    result = await service.refresh(DummySession(), refresh_token=token)
    assert result.user.ad_login == "user"
