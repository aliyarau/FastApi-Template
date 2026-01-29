"""LDAP client helpers."""

from __future__ import annotations

import logging
import uuid
from uuid import UUID

from ldap3 import ALL, Connection, Server
from ldap3.abstract.entry import Entry
from ldap3.core.exceptions import LDAPException, LDAPSocketOpenError
from ldap3.utils.conv import escape_filter_chars

from auth.domain import LdapUserInfo
from auth.exceptions import DirectoryUnavailableError
from config import settings

log = logging.getLogger(__name__)

_LDAP_ATTRIBUTES = [
    "sAMAccountName",
    "displayName",
    "mail",
    "department",
    "title",
    "memberOf",
    "objectGUID",
    "manager",
    "directReports",
]


def ldap_authenticate(login: str, password: str) -> LdapUserInfo | None:
    """Authenticate against LDAP and return user info."""
    if not password:
        return None
    try:
        bind_login = _normalize_bind_login(login)
    except ValueError:
        return None
    return _query_user(bind_login, password, sam_login=_extract_sam_login(login))


def ldap_fetch_user_by_login(login: str) -> LdapUserInfo | None:
    """Fetch user info by login using service credentials."""
    service_password = settings.ldap.service_pass.get_secret_value()
    return _query_user(settings.ldap.service_user, service_password, sam_login=_extract_sam_login(login))


def _query_user(bind_login: str, password: str, *, sam_login: str) -> LdapUserInfo | None:
    """Run LDAP query for a single user."""
    server = _build_server()
    try:
        with Connection(
            server,
            user=bind_login,
            password=password,
            auto_bind=True,
        ) as conn:
            entry = _search_user(conn, sam_login)
            if not entry:
                return None
            return _entry_to_user_info(entry)
    except LDAPSocketOpenError as exc:
        log.error("LDAP connection failed for %s: %s", sam_login, exc)
        raise DirectoryUnavailableError() from exc
    except LDAPException as exc:
        log.warning("LDAP query failed for %s: %s", sam_login, exc)
        return None


def _build_server() -> Server:
    """Build LDAP server configuration."""
    return Server(
        settings.ldap.server_uri,
        get_info=ALL,
        connect_timeout=settings.ldap.connect_timeout,
    )


def _normalize_bind_login(login: str) -> str:
    """Build LDAP bind login."""
    raw = login.strip()
    if not raw:
        raise ValueError("Empty login")
    domain = settings.ldap.domain.strip()
    if not domain:
        raise ValueError("LDAP domain is not configured")
    return f"{domain}\\{raw}"


def _extract_sam_login(login: str) -> str:
    """Normalize login for LDAP search."""
    return login.strip().lower()


def _search_user(conn: Connection, sam_login: str) -> Entry | None:
    """Search LDAP for user entry."""
    safe_login = escape_filter_chars(sam_login)
    flt = f"(&(objectClass=person)(sAMAccountName={safe_login}))"
    found = conn.search(
        search_base=settings.ldap.base_dn,
        search_filter=flt,
        attributes=_LDAP_ATTRIBUTES,
        size_limit=1,
        time_limit=int(settings.ldap.search_timeout),
    )
    if not found or not conn.entries:
        return None
    return conn.entries[0]


def _entry_to_user_info(entry: Entry) -> LdapUserInfo | None:
    """Map LDAP entry to domain user info."""
    guid = _extract_guid(entry)
    if not guid:
        return None
    login_value = _read_attribute(entry, "sAMAccountName")
    if not login_value:
        return None
    login = login_value.lower()
    full_name = _read_attribute(entry, "displayName")
    email = _read_attribute(entry, "mail")
    department = _read_attribute(entry, "department")
    title = _read_attribute(entry, "title")
    supervisor = _read_attribute(entry, "manager")
    groups = _read_groups(entry)
    subordinates = _read_direct_reports(entry)
    subordinates = _extract_suplier(subordinates)
    return LdapUserInfo(
        ad_login=login,
        ad_guid=guid,
        full_name=full_name,
        email=email.lower() if email else None,
        department=department,
        supervisor=supervisor.split(",")[0][3:] if supervisor else "",
        title=title,
        groups=groups,
        subordinates=subordinates,
    )


def _extract_guid(entry: Entry) -> UUID | None:
    """Extract objectGUID from LDAP entry."""
    attr = getattr(entry, "objectGUID", None)
    if not attr or not getattr(attr, "raw_values", None):
        return None
    try:
        raw = attr.raw_values[0]
        return uuid.UUID(bytes_le=raw)
    except (ValueError, TypeError) as exc:
        log.error("Failed to parse objectGUID: %s", exc)
        return None


def _read_attribute(entry: Entry, name: str) -> str | None:
    """Read a single LDAP attribute as string."""
    attr = getattr(entry, name, None)
    if not attr:
        return None
    value = getattr(attr, "value", None)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _read_groups(entry: Entry) -> list[str]:
    """Read LDAP group list."""
    attr = getattr(entry, "memberOf", None)
    if not attr:
        return []
    values = getattr(attr, "values", [])
    return [str(v) for v in values if v]


def _read_direct_reports(entry: Entry) -> list[str]:
    """Read LDAP direct reports."""
    attr = getattr(entry, "directReports", None)
    if not attr:
        return []
    values = getattr(attr, "values", [])
    return [str(v) for v in values if v]


def _extract_suplier(users: list[str]) -> list[str]:
    """Extract user names from direct report DN list."""
    if not users:
        return []
    extracted_user = []
    for user in users:
        data = user.split(",")
        if "DISABLED" in data[1]:
            continue
        name = data[0].split("=")[1].strip()
        extracted_user.append(name)
    return extracted_user


__all__ = ["ldap_authenticate", "ldap_fetch_user_by_login"]
