"""Tests for JWT utilities."""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")
pytest.importorskip("jwt")

from auth.jwt_utils import create_access_token, create_refresh_token, decode_token


def test_create_and_decode_access_token() -> None:
    payload = {"sub": "user-1", "user_id": 1, "ad_login": "test"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "user-1"
    assert decoded["user_id"] == 1
    assert decoded["ad_login"] == "test"
    assert decoded["typ"] == "access"


def test_create_and_decode_refresh_token() -> None:
    payload = {"sub": "user-1", "user_id": 1, "ad_login": "test", "role": "admin"}
    token = create_refresh_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "user-1"
    assert decoded["typ"] == "refresh"
