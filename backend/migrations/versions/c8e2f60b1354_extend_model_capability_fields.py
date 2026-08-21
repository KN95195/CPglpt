"""extend frozen model capability fields

Revision ID: c8e2f60b1354
Revises: b7d1e5fa0243
"""
from alembic import op
import sqlalchemy as sa

revision = 'c8e2f60b1354'
down_revision = 'b7d1e5fa0243'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('capabilities', sa.Column('code', sa.String(length=80), nullable=False, server_default=''))
    op.add_column('capabilities', sa.Column('version', sa.String(length=32), nullable=False, server_default='v1.0'))
    op.add_column('capabilities', sa.Column('function_type', sa.String(length=80), nullable=False, server_default='识别'))
    op.add_column('capabilities', sa.Column('metrics_json', sa.Text(), nullable=False, server_default='{}'))
    op.add_column('capabilities', sa.Column('input_requirements_json', sa.Text(), nullable=False, server_default='{}'))
    op.add_column('capabilities', sa.Column('deployment_requirements_json', sa.Text(), nullable=False, server_default='{}'))
    op.add_column('capabilities', sa.Column('boundaries_json', sa.Text(), nullable=False, server_default='[]'))


def downgrade():
    for column in ['boundaries_json','deployment_requirements_json','input_requirements_json','metrics_json','function_type','version','code']:
        op.drop_column('capabilities', column)
