"""Tests for logging setup."""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

import logging
import sys

from core.logging_setup import RequestIdFilter, setup_logging


def test_request_id_filter_sets_default() -> None:
    record = logging.LogRecord("x", logging.INFO, "file", 1, "msg", (), None)
    filt = RequestIdFilter()
    assert filt.filter(record) is True
    assert record.request_id == "-"


def test_setup_logging_installs_excepthook() -> None:
    original = sys.excepthook
    try:
        setup_logging()
        assert sys.excepthook is not original
    finally:
        sys.excepthook = original
