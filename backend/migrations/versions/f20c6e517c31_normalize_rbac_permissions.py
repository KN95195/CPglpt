"""normalize RBAC permissions

Revision ID: f20c6e517c31
Revises: 8c453412069a
"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = 'f20c6e517c31'
down_revision = '8c453412069a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=80), nullable=False, unique=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    )
    bind = op.get_bind()
    now = datetime.now(timezone.utc)
    roles = bind.execute(sa.text('SELECT id, permissions FROM roles')).mappings().all()
    codes = sorted({code for role in roles for code in (role['permissions'] or '').split(',') if code})
    for code in codes:
        bind.execute(sa.text('INSERT INTO permissions (code, name, description, created_at, updated_at) VALUES (:code, :name, :description, :created_at, :updated_at)'), {'code': code, 'name': code.replace('_', ' ').title(), 'description': '', 'created_at': now, 'updated_at': now})
    permission_ids = dict(bind.execute(sa.text('SELECT code, id FROM permissions')).all())
    for role in roles:
        for code in (role['permissions'] or '').split(','):
            if code:
                bind.execute(sa.text('INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)'), {'role_id': role['id'], 'permission_id': permission_ids[code]})


def downgrade():
    op.drop_table('role_permissions')
    op.drop_table('permissions')
