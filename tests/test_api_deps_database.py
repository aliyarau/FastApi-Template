"""Tests for database dependencies."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("sqlalchemy")

from api.deps import database as deps


class DummyCM:
    def __init__(self, value: Any) -> None:
        self.value = value

    async def __aenter__(self) -> Any:
        return self.value

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


@pytest.mark.asyncio
async def test_get_transaction(monkeypatch: Any) -> None:
    monkeypatch.setattr(deps.db, "transaction", lambda: DummyCM("session"))
    async for session in deps.get_transaction():
        assert session == "session"
