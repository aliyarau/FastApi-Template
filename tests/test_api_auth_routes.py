"""Integration tests for auth routes."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from api.app import create_app
from api.routers.v1.auth import routes as auth_routes
from auth.domain import LoginResult, UserProfile
from auth.exceptions import AuthError


class DummyService:
    async def login(self, *_: Any, **__: Any) -> LoginResult:
        profile = UserProfile(
            id=1,
            ad_login="user",
            ad_guid=UUID(int=1),
            full_name="User Name",
            email="user@example.com",
            department="IT",
            title="Dev",
            role="admin",
            last_login_at=None,
        )
        return LoginResult(access_token="access", refresh_token="refresh", user=profile)

    async def refresh(self, *_: Any, **__: Any) -> LoginResult:
        return await self.login()


class FailingService:
    async def login(self, *_: Any, **__: Any) -> LoginResult:
        raise AuthError("invalid_credentials", "Invalid login or password", status=401)

    async def refresh(self, *_: Any, **__: Any) -> LoginResult:
        raise AuthError("invalid_credentials", "Invalid login or password", status=401)


def _override_service(service: Any) -> TestClient:
    app = create_app()
    app.dependency_overrides[auth_routes.get_auth_service] = lambda: service
    client = TestClient(app)
    return client


def test_login_success_sets_cookie() -> None:
    client = _override_service(DummyService())
    response = client.post("/api/v1/auth/login", json={"login": "user", "password": "pass"})
    assert response.status_code == 200
    assert response.json()["user"]["adLogin"] == "user"
    assert "refresh_token" in response.cookies


def test_refresh_success() -> None:
    client = _override_service(DummyService())
    response = client.post("/api/v1/auth/refresh", cookies={"refresh_token": "token"})
    assert response.status_code == 200
    assert response.json()["accessToken"] == "access"


def test_login_failure_maps_error() -> None:
    client = _override_service(FailingService())
    response = client.post("/api/v1/auth/login", json={"login": "user", "password": "bad"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
