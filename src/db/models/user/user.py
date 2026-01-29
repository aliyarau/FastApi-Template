"""User ORM model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from db.mixins import SurrogateIntPKMixin, TimestampMixin


class User(Base, SurrogateIntPKMixin, TimestampMixin):
    """User table."""

    __tablename__ = "users"

    ad_guid: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, unique=True)
    ad_login: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    department: Mapped[str | None] = mapped_column(String(256), nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subordinates: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    supervisor: Mapped[str] = mapped_column(String(64), nullable=True)
    role: Mapped[str] = mapped_column(String(64), nullable=True)


__all__ = ["User"]
