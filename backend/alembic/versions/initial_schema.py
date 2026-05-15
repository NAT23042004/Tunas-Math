"""create initial schema

Revision ID: initial_schema
Revises:
Create Date: 2026-05-14
"""

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "initial_schema"
down_revision = None
branch_labels = None
depends_on = None


userrole = sa.Enum("STUDENT", "ADMIN", name="userrole")
sessionstatus = sa.Enum("ACTIVE", "COMPLETED", "ABANDONED", name="sessionstatus")
dialoguestate = sa.Enum("REVIEW", "HEURISTIC", "RECTIFY", "SUMMARIZE", name="dialoguestate")
difficultylevel = sa.Enum("EASY", "MEDIUM", "HARD", name="difficultylevel")


def upgrade() -> None:
    existing_tables = (
        set()
        if context.is_offline_mode()
        else set(sa.inspect(op.get_bind()).get_table_names())
    )

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("avatar_url", sa.String(), nullable=True),
            sa.Column("role", userrole, nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("last_active", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if "problems" not in existing_tables:
        op.create_table(
            "problems",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("topic_id", sa.String(), nullable=False),
            sa.Column("statement_latex", sa.Text(), nullable=False),
            sa.Column("difficulty", difficultylevel, nullable=False),
            sa.Column("answer", sa.Text(), nullable=False),
            sa.Column("is_geometry", sa.Boolean(), nullable=True),
            sa.Column("geometry_params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("source", sa.String(), nullable=True),
            sa.Column("misconceptions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_problems_topic_id", "problems", ["topic_id"], unique=False)

    if "sessions" not in existing_tables:
        op.create_table(
            "sessions",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("problem_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("topic_id", sa.String(), nullable=False),
            sa.Column("status", sessionstatus, nullable=True),
            sa.Column("dialogue_state", dialoguestate, nullable=True),
            sa.Column("hint_level", sa.Integer(), nullable=True),
            sa.Column("hint_count", sa.Integer(), nullable=True),
            sa.Column("fail_count", sa.Integer(), nullable=True),
            sa.Column("messages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("student_rating", sa.Integer(), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("ended_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if "progress" not in existing_tables:
        op.create_table(
            "progress",
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("topic_id", sa.String(), nullable=False),
            sa.Column("mastery_score", sa.Float(), nullable=True),
            sa.Column("sessions_count", sa.Integer(), nullable=True),
            sa.Column("last_practiced", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("user_id", "topic_id"),
        )


def downgrade() -> None:
    existing_tables = (
        {"progress", "sessions", "problems", "users"}
        if context.is_offline_mode()
        else set(sa.inspect(op.get_bind()).get_table_names())
    )

    if "progress" in existing_tables:
        op.drop_table("progress")
    if "sessions" in existing_tables:
        op.drop_table("sessions")
    if "problems" in existing_tables:
        op.drop_index("ix_problems_topic_id", table_name="problems")
        op.drop_table("problems")
    if "users" in existing_tables:
        op.drop_index("ix_users_email", table_name="users")
        op.drop_table("users")

    bind = op.get_bind()
    for enum_type in (dialoguestate, sessionstatus, difficultylevel, userrole):
        enum_type.drop(bind, checkfirst=True)
