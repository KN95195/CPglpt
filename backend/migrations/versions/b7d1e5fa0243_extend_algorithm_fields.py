"""extend frozen algorithm fields

Revision ID: b7d1e5fa0243
Revises: a6c0d4e9f132
"""
from alembic import op
import sqlalchemy as sa

revision = 'b7d1e5fa0243'
down_revision = 'a6c0d4e9f132'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('algorithms', sa.Column('code', sa.String(length=80), nullable=False, server_default=''))
    op.add_column('algorithms', sa.Column('input_summary', sa.Text(), nullable=False, server_default=''))
    op.add_column('algorithms', sa.Column('output_summary', sa.Text(), nullable=False, server_default=''))
    op.add_column('algorithms', sa.Column('metrics_json', sa.Text(), nullable=False, server_default='{}'))
    op.add_column('algorithms', sa.Column('boundaries_json', sa.Text(), nullable=False, server_default='[]'))


def downgrade():
    for column in ['boundaries_json','metrics_json','output_summary','input_summary','code']:
        op.drop_column('algorithms', column)
