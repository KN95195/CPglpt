"""add administrator-managed directory configuration

Revision ID: 7a8c9d0e1f23
Revises: 2f7b6c8d9e10
"""
from alembic import op
import sqlalchemy as sa

revision='7a8c9d0e1f23'
down_revision='2f7b6c8d9e10'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('directory_configs',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('enabled',sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column('server_type',sa.String(48),nullable=False,server_default='MS_ACTIVE_DIRECTORY'),
        sa.Column('protocol',sa.String(12),nullable=False,server_default='LDAP'),
        sa.Column('host',sa.String(255),nullable=False,server_default=''),
        sa.Column('port',sa.Integer(),nullable=False,server_default='389'),
        sa.Column('timeout_seconds',sa.Integer(),nullable=False,server_default='30'),
        sa.Column('bind_dn',sa.String(500),nullable=False,server_default=''),
        sa.Column('bind_password_encrypted',sa.Text(),nullable=False,server_default=''),
        sa.Column('base_dn',sa.String(500),nullable=False,server_default=''),
        sa.Column('login_domain',sa.String(255),nullable=False,server_default=''),
        sa.Column('user_filter',sa.String(500),nullable=False,server_default='(&(objectClass=user)(sAMAccountName=*))'),
        sa.Column('default_role',sa.String(64),nullable=False,server_default='sales'),
        sa.Column('last_test_status',sa.String(24),nullable=False,server_default='UNTESTED'),
        sa.Column('last_test_message',sa.String(500),nullable=False,server_default=''),
        sa.Column('last_test_at',sa.DateTime(timezone=True),nullable=True),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()))


def downgrade():
    op.drop_table('directory_configs')
