"""Tests for refresh token cookie helpers."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("starlette")

from starlette.requests import Request
from starlette.responses import Response

from api.errors.exceptions import AppError
from api.routers.v1.auth.cookie import clear_refresh_cookie, read_refresh_cookie, set_refresh_cookie


def _make_request(cookies: dict[str, str]) -> Request:
    headers = [(b"cookie", "; ".join(f"{k}={v}" for k, v in cookies.items()).encode())]
    scope: dict[str, Any] = {"type": "http", "headers": headers}
    return Request(scope)


def test_read_refresh_cookie_missing() -> None:
    request = _make_request({})
    with pytest.raises(AppError):
        read_refresh_cookie(request)


def test_set_and_clear_refresh_cookie() -> None:
    response = Response()
    set_refresh_cookie(response, "token")
    assert "refresh_token" in response.headers.get("set-cookie", "")
    clear_refresh_cookie(response)
