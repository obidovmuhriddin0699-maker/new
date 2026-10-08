"""ai pipeline fields

Brand profile inputs for generation, structured content (carousel slides,
reels scenes, story frames) on contents and versions, and AI job tracking
fields. Existing rows are backfilled through server defaults, so the
migration is safe on populated databases.

Revision ID: eac1ed7cd395
Revises: 91ed60cfe649
Create Date: 2026-10-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "eac1ed7cd395"
down_revision: str | None = "91ed60cfe649"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMPTY_LIST = sa.text("'[]'")
EMPTY_OBJECT = sa.text("'{}'")
BRAND_LIST_COLUMNS = (
    "services",
    "preferred_styles",
    "content_goals",
    "preferred_ctas",
    "banned_phrases",
)


def upgrade() -> None:
    with op.batch_alter_table("brand_profiles") as batch:
        batch.add_column(sa.Column("target_audience", sa.Text(), nullable=True))
        for name in BRAND_LIST_COLUMNS:
            batch.add_column(sa.Column(name, sa.JSON(), nullable=False, server_default=EMPTY_LIST))

    for table in ("contents", "content_versions"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(
                sa.Column("structure", sa.JSON(), nullable=False, server_default=EMPTY_OBJECT)
            )

    with op.batch_alter_table("ai_jobs") as batch:
        batch.add_column(
            sa.Column("job_type", sa.String(length=50), nullable=False, server_default="generic")
        )
        batch.add_column(sa.Column("created_by_user_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("error_category", sa.String(length=50), nullable=True))
        batch.add_column(sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_index(op.f("ix_ai_jobs_created_by_user_id"), ["created_by_user_id"])
        batch.create_index(op.f("ix_ai_jobs_job_type"), ["job_type"])
        batch.create_foreign_key(
            op.f("fk_ai_jobs_created_by_user_id_users"),
            "users",
            ["created_by_user_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ai_jobs") as batch:
        batch.drop_constraint(op.f("fk_ai_jobs_created_by_user_id_users"), type_="foreignkey")
        batch.drop_index(op.f("ix_ai_jobs_job_type"))
        batch.drop_index(op.f("ix_ai_jobs_created_by_user_id"))
        for name in (
            "finished_at",
            "started_at",
            "error_category",
            "created_by_user_id",
            "job_type",
        ):
            batch.drop_column(name)

    for table in ("content_versions", "contents"):
        with op.batch_alter_table(table) as batch:
            batch.drop_column("structure")

    with op.batch_alter_table("brand_profiles") as batch:
        for name in reversed(BRAND_LIST_COLUMNS):
            batch.drop_column(name)
        batch.drop_column("target_audience")
