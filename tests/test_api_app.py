"""Tests for API app factory."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from api.app import create_app
from config import settings


def test_create_app_routes() -> None:
    app = create_app()
    paths = {route.path for route in app.router.routes}
    assert f"{settings.api.prefix}/auth/login" in paths
    assert f"{settings.api.prefix}/auth/refresh" in paths


def test_docs_and_openapi_paths() -> None:
    app = create_app()
    assert app.docs_url == f"{settings.api.prefix}/docs"
    assert app.openapi_url == f"{settings.api.prefix}/openapi.json"
