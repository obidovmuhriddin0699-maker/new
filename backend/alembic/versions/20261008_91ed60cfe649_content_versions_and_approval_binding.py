"""content versions and approval binding

Adds immutable content versions, binds approvals to (version, content hash),
allows approval invalidation, links schedules to the approval/version they
publish, and records the content version in audit logs.

Revision ID: 91ed60cfe649
Revises: 22d94eda60d4
Create Date: 2026-10-08 18:24:10.321915
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "91ed60cfe649"
down_revision: str | None = "22d94eda60d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACTIVE_APPROVAL_WHERE = "decision = 'APPROVED' AND invalidated_at IS NULL"


def _require_empty(table: str) -> None:
    """New NOT NULL columns cannot be invented for existing rows of these tables.

    PHASE 1 code never wrote approvals or schedules, so they are empty in every
    real database. If not, stop instead of fabricating approval data.
    """
    count = op.get_bind().execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar()  # noqa: S608
    if count:
        raise RuntimeError(
            f"Migration 91ed60cfe649 requires '{table}' to be empty (found {count} rows). "
            "These rows predate approval/version binding and cannot be migrated safely."
        )


def upgrade() -> None:
    _require_empty("approvals")
    _require_empty("content_schedules")

    op.create_table(
        "content_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "content_type",
            sa.Enum("POST", "CAROUSEL", "REELS", "STORY", name="contenttype",
                    native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            "language",
            sa.Enum("uz", "ru", "en", name="contentlanguage", native_enum=False, length=5),
            nullable=False,
        ),
        sa.Column("topic", sa.String(length=300), nullable=True),
        sa.Column("hook", sa.Text(), nullable=True),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("hashtags", sa.JSON(), nullable=False),
        sa.Column("cta", sa.Text(), nullable=True),
        sa.Column("script", sa.Text(), nullable=True),
        sa.Column("visual_prompt", sa.Text(), nullable=True),
        sa.Column("aspect_ratio", sa.String(length=10), nullable=True),
        sa.Column("media", sa.JSON(), nullable=False),
        sa.Column("ai_metadata", sa.JSON(), nullable=False),
        sa.Column(
            "source",
            sa.Enum("HUMAN", "AGENT", "SYSTEM", name="actortype", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_by_name", sa.String(length=100), nullable=True),
        sa.Column("change_note", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["content_id"], ["contents.id"],
            name=op.f("fk_content_versions_content_id_contents"), ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"],
            name=op.f("fk_content_versions_created_by_user_id_users"), ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_content_versions")),
        sa.UniqueConstraint(
            "content_id", "version", name=op.f("uq_content_versions_content_id_version")
        ),
    )
    op.create_index(
        op.f("ix_content_versions_content_id"), "content_versions", ["content_id"]
    )
    op.create_index(
        op.f("ix_content_versions_created_by_user_id"), "content_versions", ["created_by_user_id"]
    )

    with op.batch_alter_table("approvals") as batch:
        batch.add_column(sa.Column("content_hash", sa.String(length=64), nullable=False))
        batch.add_column(sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("invalidation_reason", sa.String(length=200), nullable=True))
        batch.drop_constraint("uq_approvals_content_id_content_version_decision", type_="unique")
    op.create_index("ix_approvals_content_version", "approvals", ["content_id", "content_version"])
    op.create_index(
        "uq_approvals_active_approved",
        "approvals",
        ["content_id", "content_version"],
        unique=True,
        postgresql_where=sa.text(ACTIVE_APPROVAL_WHERE),
        sqlite_where=sa.text(ACTIVE_APPROVAL_WHERE),
    )

    with op.batch_alter_table("audit_logs") as batch:
        batch.add_column(sa.Column("content_version", sa.Integer(), nullable=True))

    with op.batch_alter_table("content_assets") as batch:
        batch.add_column(sa.Column("checksum_sha256", sa.String(length=64), nullable=True))

    with op.batch_alter_table("content_schedules") as batch:
        batch.add_column(sa.Column("content_version", sa.Integer(), nullable=False))
        batch.add_column(sa.Column("approval_id", sa.Integer(), nullable=False))
        batch.add_column(sa.Column("created_by_user_id", sa.Integer(), nullable=True))
        batch.create_index(op.f("ix_content_schedules_approval_id"), ["approval_id"])
        batch.create_index(op.f("ix_content_schedules_created_by_user_id"), ["created_by_user_id"])
        batch.create_foreign_key(
            op.f("fk_content_schedules_created_by_user_id_users"), "users",
            ["created_by_user_id"], ["id"], ondelete="SET NULL",
        )
        batch.create_foreign_key(
            op.f("fk_content_schedules_approval_id_approvals"), "approvals",
            ["approval_id"], ["id"], ondelete="RESTRICT",
        )


def downgrade() -> None:
    with op.batch_alter_table("content_schedules") as batch:
        batch.drop_constraint(
            op.f("fk_content_schedules_approval_id_approvals"), type_="foreignkey"
        )
        batch.drop_constraint(
            op.f("fk_content_schedules_created_by_user_id_users"), type_="foreignkey"
        )
        batch.drop_index(op.f("ix_content_schedules_created_by_user_id"))
        batch.drop_index(op.f("ix_content_schedules_approval_id"))
        batch.drop_column("created_by_user_id")
        batch.drop_column("approval_id")
        batch.drop_column("content_version")

    with op.batch_alter_table("content_assets") as batch:
        batch.drop_column("checksum_sha256")

    with op.batch_alter_table("audit_logs") as batch:
        batch.drop_column("content_version")

    op.drop_index("uq_approvals_active_approved", table_name="approvals")
    op.drop_index("ix_approvals_content_version", table_name="approvals")
    with op.batch_alter_table("approvals") as batch:
        batch.drop_column("invalidation_reason")
        batch.drop_column("invalidated_at")
        batch.drop_column("content_hash")
        batch.create_unique_constraint(
            "uq_approvals_content_id_content_version_decision",
            ["content_id", "content_version", "decision"],
        )

    op.drop_index(op.f("ix_content_versions_created_by_user_id"), table_name="content_versions")
    op.drop_index(op.f("ix_content_versions_content_id"), table_name="content_versions")
    op.drop_table("content_versions")
