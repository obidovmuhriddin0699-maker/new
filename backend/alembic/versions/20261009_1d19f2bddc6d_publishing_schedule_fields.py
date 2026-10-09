"""publishing schedule fields

Revision ID: 1d19f2bddc6d
Revises: c600c9d62a46
Create Date: 2026-10-09 04:58:54.193131
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "1d19f2bddc6d"
down_revision: str | None = "c600c9d62a46"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FK = "fk_content_schedules_instagram_account_id_instagram_accounts"


def upgrade() -> None:
    with op.batch_alter_table("content_schedules", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("ig_container_created_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(sa.Column("ig_media_id", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("instagram_account_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("outcome_unknown", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
        batch_op.create_index(
            batch_op.f("ix_content_schedules_instagram_account_id"),
            ["instagram_account_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            batch_op.f(FK),
            "instagram_accounts",
            ["instagram_account_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("content_schedules", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f(FK), type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_content_schedules_instagram_account_id"))
        batch_op.drop_column("outcome_unknown")
        batch_op.drop_column("processing_started_at")
        batch_op.drop_column("instagram_account_id")
        batch_op.drop_column("ig_media_id")
        batch_op.drop_column("ig_container_created_at")
