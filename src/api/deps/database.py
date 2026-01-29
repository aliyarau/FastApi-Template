"""Database dependencies."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import db


async def get_transaction() -> AsyncGenerator[AsyncSession]:
    """Provide a transactional database session."""
    async with db.transaction() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with db.session() as session:
        yield session


__all__ = ["get_transaction"]
