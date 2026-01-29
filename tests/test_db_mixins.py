"""Tests for database mixins."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from db.mixins import SurrogateIntPKMixin, TimestampMixin


def test_mixins_have_mapped_attributes() -> None:
    assert hasattr(SurrogateIntPKMixin, "id")
    assert hasattr(TimestampMixin, "created_at")
    assert hasattr(TimestampMixin, "updated_at")
