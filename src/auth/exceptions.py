"""Authentication exceptions."""

from __future__ import annotations


class AuthError(Exception):
    """Domain-level authentication error."""

    def __init__(self, code: str, message: str, *, status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class TokenError(AuthError):
    """Token validation error."""

    def __init__(self, message: str = "Invalid token", *, code: str = "invalid_token", status: int = 401) -> None:
        super().__init__(code, message, status=status)


class DirectoryUnavailableError(AuthError):
    """LDAP directory is unavailable."""

    def __init__(
        self,
        message: str = "Directory service is temporarily unavailable",
        *,
        code: str = "ldap_unavailable",
        status: int = 503,
    ) -> None:
        super().__init__(code, message, status=status)


__all__ = ["AuthError", "TokenError", "DirectoryUnavailableError"]
