"""extend frozen scene fields

Revision ID: d9f3071c2465
Revises: c8e2f60b1354
"""
from alembic import op
import sqlalchemy as sa

revision = 'd9f3071c2465'
down_revision = 'c8e2f60b1354'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scenes', sa.Column('category', sa.String(length=80), nullable=False, server_default='水域安全'))
    op.add_column('scenes', sa.Column('cover_image', sa.String(length=500), nullable=False, server_default=''))
    op.add_column('scenes', sa.Column('goals_json', sa.Text(), nullable=False, server_default='[]'))
    op.add_column('scenes', sa.Column('process_json', sa.Text(), nullable=False, server_default='[]'))
    op.add_column('scenes', sa.Column('core_capability_summary', sa.Text(), nullable=False, server_default=''))


def downgrade():
    for column in ['core_capability_summary','process_json','goals_json','cover_image','category']:
        op.drop_column('scenes', column)
