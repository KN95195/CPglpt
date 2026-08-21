"""extend frozen software fields

Revision ID: a6c0d4e9f132
Revises: f5b9c3d8e021
"""
from alembic import op
import sqlalchemy as sa

revision = 'a6c0d4e9f132'
down_revision = 'f5b9c3d8e021'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('software', sa.Column('code', sa.String(length=80), nullable=False, server_default=''))
    op.add_column('software', sa.Column('software_type', sa.String(length=48), nullable=False, server_default='PLATFORM'))
    op.add_column('software', sa.Column('vendor', sa.String(length=120), nullable=False, server_default='海智科技'))
    op.add_column('software', sa.Column('deployment_mode', sa.String(length=48), nullable=False, server_default='PRIVATE'))
    op.add_column('software', sa.Column('supported_os_json', sa.Text(), nullable=False, server_default='[]'))


def downgrade():
    for column in ['supported_os_json','deployment_mode','vendor','software_type','code']:
        op.drop_column('software', column)
