"""Application-level exceptions."""

from typing import Any


class AppError(Exception):
    """Application error with explicit HTTP status and code."""

    def __init__(self, code: str, message: str, *, status: int = 400, details: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details
