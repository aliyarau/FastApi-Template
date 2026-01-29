"""Tests for configuration settings."""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from config import settings


def test_settings_loaded() -> None:
    assert settings.run.host
    assert settings.api.prefix.startswith("/")
    assert settings.jwt.secret.get_secret_value()
