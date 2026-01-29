"""Tests for database base metadata."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from db.base import NAMING_CONVENTION, Base


def test_naming_convention_keys() -> None:
    assert "pk" in NAMING_CONVENTION
    assert "fk" in NAMING_CONVENTION


def test_base_metadata_attached() -> None:
    assert Base.metadata.naming_convention == NAMING_CONVENTION
