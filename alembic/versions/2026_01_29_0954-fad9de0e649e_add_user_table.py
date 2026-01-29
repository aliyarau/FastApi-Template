"""Add User Table

Revision ID: fad9de0e649e
Revises:
Create Date: 2026-01-29 09:54:15.774372

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "fad9de0e649e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("ad_guid", sa.UUID(), nullable=False),
        sa.Column("ad_login", sa.String(length=128), nullable=False),
        sa.Column("full_name", sa.String(length=256), nullable=True),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("department", sa.String(length=256), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("TRUE"),
            nullable=False,
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subordinates", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("supervisor", sa.String(length=64), nullable=True),
        sa.Column("role", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("ad_guid", name=op.f("uq_users_ad_guid")),
        sa.UniqueConstraint("ad_login", name=op.f("uq_users_ad_login")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
