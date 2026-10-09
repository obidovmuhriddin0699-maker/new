"""session revocation and audit immutability

Revision ID: 3cd141946923
Revises: 17bac1fec7a0
Create Date: 2026-10-09 08:02:07.465303
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Copied (not imported) so this migration stays stable if the model module changes.
AUDIT_APPEND_ONLY_SQL = {
    "postgresql": [
        """
        CREATE OR REPLACE FUNCTION audit_logs_append_only() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs is append-only';
        END;
        $$ LANGUAGE plpgsql
        """,
        "CREATE TRIGGER audit_logs_no_update BEFORE UPDATE OR DELETE ON audit_logs "
        "FOR EACH ROW EXECUTE FUNCTION audit_logs_append_only()",
    ],
    "sqlite": [
        "CREATE TRIGGER audit_logs_no_update BEFORE UPDATE ON audit_logs "
        "BEGIN SELECT RAISE(ABORT, 'audit_logs is append-only'); END",
        "CREATE TRIGGER audit_logs_no_delete BEFORE DELETE ON audit_logs "
        "BEGIN SELECT RAISE(ABORT, 'audit_logs is append-only'); END",
    ],
}


revision: str = '3cd141946923'
down_revision: str | None = '17bac1fec7a0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('revoked_tokens',
    sa.Column('jti', sa.String(length=64), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_revoked_tokens_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('jti', name=op.f('pk_revoked_tokens'))
    )
    with op.batch_alter_table('revoked_tokens', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_revoked_tokens_expires_at'), ['expires_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_revoked_tokens_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sessions_valid_after', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))

    # Audit log becomes append-only at the database level.
    bind = op.get_bind()
    for statement in AUDIT_APPEND_ONLY_SQL.get(bind.dialect.name, []):
        op.execute(statement)



def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS audit_logs_no_update ON audit_logs")
        op.execute("DROP FUNCTION IF EXISTS audit_logs_append_only()")
    elif bind.dialect.name == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS audit_logs_no_update")
        op.execute("DROP TRIGGER IF EXISTS audit_logs_no_delete")
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_login_at')
        batch_op.drop_column('password_changed_at')
        batch_op.drop_column('sessions_valid_after')

    with op.batch_alter_table('revoked_tokens', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_revoked_tokens_user_id'))
        batch_op.drop_index(batch_op.f('ix_revoked_tokens_expires_at'))

    op.drop_table('revoked_tokens')
