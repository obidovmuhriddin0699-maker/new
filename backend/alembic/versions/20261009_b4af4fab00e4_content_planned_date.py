"""content planned date

Calendar planning date for content (not versioned, not published).

Revision ID: b4af4fab00e4
Revises: eac1ed7cd395
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b4af4fab00e4"
down_revision: str | None = "eac1ed7cd395"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("contents") as batch:
        batch.add_column(sa.Column("planned_date", sa.Date(), nullable=True))
        batch.create_index(op.f("ix_contents_planned_date"), ["planned_date"])


def downgrade() -> None:
    with op.batch_alter_table("contents") as batch:
        batch.drop_index(op.f("ix_contents_planned_date"))
        batch.drop_column("planned_date")
