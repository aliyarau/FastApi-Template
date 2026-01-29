"""Tests for auth user repository."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from typing import Any
from uuid import UUID

import pytest

from db.models.user.user import User
from db.repositories.app.auth.users import deactivate_user_by_guid, sync_user_from_directory


class FakeResult:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        return self._value


class FakeSession:
    def __init__(self, user: User | None = None) -> None:
        self.user = user
        self.added: list[User] = []
        self.flushed = False

    async def execute(self, *_: Any, **__: Any) -> FakeResult:
        return FakeResult(self.user)

    def add(self, user: User) -> None:
        self.user = user
        self.added.append(user)

    async def flush(self) -> None:
        self.flushed = True


@pytest.mark.asyncio
async def test_sync_user_from_directory_creates_user() -> None:
    session = FakeSession()
    ad_guid = UUID(int=1)
    user = await sync_user_from_directory(
        session,
        ad_guid=ad_guid,
        ad_login="user",
        full_name="User Name",
        email="user@example.com",
        department="IT",
        title="Dev",
        subordinates=[1, 2],
        supervisor="Boss",
        update_last_login=True,
        role="admin",
    )
    assert user.ad_login == "user"
    assert session.added
    assert user.last_login_at is not None
    assert session.flushed


@pytest.mark.asyncio
async def test_deactivate_user_by_guid() -> None:
    user = User(ad_guid=UUID(int=1), ad_login="user")
    user.is_active = True
    session = FakeSession(user=user)
    await deactivate_user_by_guid(session, user.ad_guid)
    assert user.is_active is False
