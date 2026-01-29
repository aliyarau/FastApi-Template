"""SQLAlchemy mixins."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, text
from sqlalchemy.orm import Mapped, mapped_column


class SurrogateIntPKMixin:
    """Integer primary key mixin."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class TimestampMixin:
    """Created/updated timestamps mixin."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
