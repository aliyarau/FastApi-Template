"""User repository functions for auth flow."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User


async def sync_user_from_directory(
    session: AsyncSession,
    *,
    ad_guid: UUID,
    ad_login: str,
    full_name: str | None,
    email: str | None,
    department: str | None,
    title: str | None,
    subordinates: list[int],
    supervisor: str,
    update_last_login: bool,
    role: str,
) -> User:
    """Create or update a user from directory data."""
    stmt = select(User).where(User.ad_guid == ad_guid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user = User(ad_guid=ad_guid, ad_login=ad_login)
        session.add(user)

    user.ad_login = ad_login
    user.full_name = full_name
    user.email = email
    user.department = department
    user.title = title
    user.subordinates = subordinates
    user.supervisor = supervisor
    user.role = role
    user.is_active = True
    if update_last_login:
        user.last_login_at = datetime.now(tz=UTC)

    await session.flush()
    return user


async def deactivate_user_by_guid(session: AsyncSession, ad_guid: UUID) -> None:
    """Deactivate user by AD GUID."""
    stmt = select(User).where(User.ad_guid == ad_guid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return
    user.is_active = False
    await session.flush()


__all__ = ["sync_user_from_directory", "deactivate_user_by_guid"]
