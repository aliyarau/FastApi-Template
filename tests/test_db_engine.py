"""Tests for database engine helper."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from typing import Any

import pytest

import db.engine as engine_module


class DummyEngine:
    async def dispose(self) -> None:
        return None


class DummySession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    async def __aenter__(self) -> DummySession:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


class DummySessionMaker:
    def __call__(self) -> DummySession:
        return DummySession()


def test_database_helper_init(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_engine(url: str, *, echo: bool) -> DummyEngine:
        captured["url"] = url
        captured["echo"] = echo
        return DummyEngine()

    def fake_sessionmaker(*_: Any, **__: Any) -> DummySessionMaker:
        return DummySessionMaker()

    monkeypatch.setattr(engine_module, "create_async_engine", fake_engine)
    monkeypatch.setattr(engine_module, "async_sessionmaker", fake_sessionmaker)

    helper = engine_module.DatabaseHelper("db://url", echo=True)
    assert captured["url"] == "db://url"
    assert captured["echo"] is True
    assert helper.session_factory is not None


@pytest.mark.asyncio
async def test_transaction_commit(monkeypatch: Any) -> None:
    def fake_sessionmaker(*_: Any, **__: Any) -> DummySessionMaker:
        return DummySessionMaker()

    monkeypatch.setattr(engine_module, "create_async_engine", lambda *_args, **_kw: DummyEngine())
    monkeypatch.setattr(engine_module, "async_sessionmaker", fake_sessionmaker)

    helper = engine_module.DatabaseHelper("db://url", echo=False)
    async with helper.transaction() as session:
        assert session.committed is False
    assert session.committed is True


@pytest.mark.asyncio
async def test_transaction_rollback(monkeypatch: Any) -> None:
    def fake_sessionmaker(*_: Any, **__: Any) -> DummySessionMaker:
        return DummySessionMaker()

    monkeypatch.setattr(engine_module, "create_async_engine", lambda *_args, **_kw: DummyEngine())
    monkeypatch.setattr(engine_module, "async_sessionmaker", fake_sessionmaker)

    helper = engine_module.DatabaseHelper("db://url", echo=False)
    session = None
    with pytest.raises(RuntimeError):
        async with helper.transaction() as sess:
            session = sess
            raise RuntimeError("boom")
    assert session is not None
    assert session.rolled_back is True
