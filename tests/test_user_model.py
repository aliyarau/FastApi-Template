"""Tests for user model."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from uuid import UUID

from db.models.user.user import User


def test_user_model_fields() -> None:
    user = User(ad_guid=UUID(int=1), ad_login="login")
    assert user.__tablename__ == "users"
    assert user.ad_login == "login"
