"""Tests for API schemas."""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from pydantic import ValidationError

from api.schemas.base import ApiBaseModel, ApiInputModel, _to_camel


def test_to_camel() -> None:
    assert _to_camel("foo_bar") == "fooBar"
    assert _to_camel("x") == "x"


def test_api_base_model_aliases() -> None:
    class Example(ApiBaseModel):
        foo_bar: int

    item = Example(foo_bar=1)
    assert item.model_dump(by_alias=True) == {"fooBar": 1}


def test_api_input_model_forbids_extra() -> None:
    class Example(ApiInputModel):
        foo_bar: int

    with pytest.raises(ValidationError):
        Example.model_validate({"fooBar": 1, "extra": "nope"})
