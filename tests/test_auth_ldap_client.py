"""Tests for LDAP client helpers."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("pydantic")
pytest.importorskip("ldap3")

from auth import ldap_client


def test_ldap_authenticate_empty_password() -> None:
    assert ldap_client.ldap_authenticate("user", "") is None


def test_ldap_fetch_user_by_login_calls_query(monkeypatch: Any) -> None:
    called = {}

    def fake_query(bind_login: str, password: str, *, sam_login: str) -> str:
        called["bind_login"] = bind_login
        called["password"] = password
        called["sam_login"] = sam_login
        return "ok"

    monkeypatch.setattr(ldap_client, "_query_user", fake_query)
    assert ldap_client.ldap_fetch_user_by_login("TestUser") == "ok"
    assert called["sam_login"] == "testuser"


def test_extract_supplier() -> None:
    users = [
        "CN=Alice,OU=Users,DC=example,DC=loc",
        "CN=Bob,OU=Users,DC=example,DC=loc",
        "CN=DISABLED,OU=Users,DC=example,DC=loc",
        "CN=Charlie,OU=Users,DC=example,DC=loc,DISABLED",
    ]
    extracted = ldap_client._extract_suplier(users)
    assert "Alice" in extracted
    assert "Bob" in extracted
