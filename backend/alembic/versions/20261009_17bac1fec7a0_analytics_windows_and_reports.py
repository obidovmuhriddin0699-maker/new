"""analytics windows and reports

Revision ID: 17bac1fec7a0
Revises: 1d19f2bddc6d
Create Date: 2026-10-09 07:18:38.092653
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '17bac1fec7a0'
down_revision: str | None = '1d19f2bddc6d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('analytics_reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instagram_account_id', sa.Integer(), nullable=True),
    sa.Column('period_start', sa.Date(), nullable=False),
    sa.Column('period_end', sa.Date(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('facts', sa.JSON(), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('highlights', sa.JSON(), nullable=False),
    sa.Column('recommendations', sa.JSON(), nullable=False),
    sa.Column('source', sa.String(length=10), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=True),
    sa.Column('model', sa.String(length=100), nullable=True),
    sa.Column('ai_rejected_reason', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Enum('HUMAN', 'AGENT', 'SYSTEM', name='actortype', native_enum=False, length=10), nullable=False),
    sa.Column('created_by_user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_analytics_reports_created_by_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['instagram_account_id'], ['instagram_accounts.id'], name=op.f('fk_analytics_reports_instagram_account_id_instagram_accounts'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_analytics_reports'))
    )
    with op.batch_alter_table('analytics_reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_analytics_reports_created_by_user_id'), ['created_by_user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_analytics_reports_instagram_account_id'), ['instagram_account_id'], unique=False)
        batch_op.create_index('ix_analytics_reports_period', ['period_start', 'period_end'], unique=False)

    with op.batch_alter_table('analytics_snapshots', schema=None) as batch_op:
        batch_op.add_column(sa.Column('window_start', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('window_end', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('ig_media_id', sa.String(length=64), nullable=True))
        batch_op.add_column(
            sa.Column('unavailable', sa.JSON(), server_default=sa.text("'[]'"), nullable=False)
        )
        batch_op.create_index('ix_analytics_snapshots_account_period_end', ['instagram_account_id', 'period', 'window_end'], unique=False)
        batch_op.create_index(batch_op.f('ix_analytics_snapshots_ig_media_id'), ['ig_media_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('analytics_snapshots', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_analytics_snapshots_ig_media_id'))
        batch_op.drop_index('ix_analytics_snapshots_account_period_end')
        batch_op.drop_column('unavailable')
        batch_op.drop_column('ig_media_id')
        batch_op.drop_column('window_end')
        batch_op.drop_column('window_start')

    with op.batch_alter_table('analytics_reports', schema=None) as batch_op:
        batch_op.drop_index('ix_analytics_reports_period')
        batch_op.drop_index(batch_op.f('ix_analytics_reports_instagram_account_id'))
        batch_op.drop_index(batch_op.f('ix_analytics_reports_created_by_user_id'))

    op.drop_table('analytics_reports')
