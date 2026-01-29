"""Tests for API error handling."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("starlette")
pytest.importorskip("sqlalchemy")

from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from api.errors.exceptions import AppError
from api.errors.handlers import (
    _code_by_status,
    _make_error_response,
    app_error_handler,
    integrity_error_handler,
    validation_exception_handler,
)
from api.errors.schema import error_responses


def _make_request() -> Request:
    scope: dict[str, Any] = {"type": "http", "headers": []}
    return Request(scope)


def test_code_by_status() -> None:
    assert _code_by_status(400) == "BAD_REQUEST"
    assert _code_by_status(401) == "UNAUTHORIZED"
    assert _code_by_status(499) == "HTTP_ERROR"
    assert _code_by_status(500) == "INTERNAL_ERROR"


def test_make_error_response() -> None:
    response = _make_error_response("CODE", "Message", 400, "rid", {"a": 1})
    payload = response.body.decode()
    assert "CODE" in payload
    assert "Message" in payload
    assert "rid" in payload


def test_error_responses() -> None:
    responses = error_responses(400, 401)
    assert 400 in responses
    assert responses[400]["description"] == "Bad Request"


@pytest.mark.asyncio
async def test_app_error_handler() -> None:
    request = _make_request()
    exc = AppError("bad", "Oops", status=400)
    response = await app_error_handler(request, exc)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_validation_exception_handler() -> None:
    request = _make_request()
    exc = RequestValidationError(errors=[{"loc": ("x",), "msg": "err", "type": "value_error"}])
    response = await validation_exception_handler(request, exc)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_integrity_error_handler() -> None:
    request = _make_request()
    exc = IntegrityError("stmt", {}, Exception("boom"))
    response = await integrity_error_handler(request, exc)
    assert response.status_code == 409
