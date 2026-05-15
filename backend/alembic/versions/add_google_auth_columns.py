"""add google auth columns

Revision ID: add_google_auth_columns
Revises:
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa


revision = "add_google_auth_columns"
down_revision = "initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auth_provider", sa.String(), nullable=True))
    op.add_column("users", sa.Column("auth_subject", sa.String(), nullable=True))
    op.create_index("ix_users_auth_subject", "users", ["auth_subject"], unique=False)
    op.create_unique_constraint(
        "uq_users_auth_provider_subject",
        "users",
        ["auth_provider", "auth_subject"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_auth_provider_subject", "users", type_="unique")
    op.drop_index("ix_users_auth_subject", table_name="users")
    op.drop_column("users", "auth_subject")
    op.drop_column("users", "auth_provider")
