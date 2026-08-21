"""extend frozen product knowledge fields

Revision ID: f5b9c3d8e021
Revises: e4f8a2c7d910
"""
from alembic import op
import sqlalchemy as sa

revision = 'f5b9c3d8e021'
down_revision = 'e4f8a2c7d910'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('product_type', sa.String(length=48), nullable=False, server_default='HARDWARE'))
    op.add_column('products', sa.Column('main_image', sa.String(length=500), nullable=False, server_default=''))
    op.add_column('products', sa.Column('dynamic_fields_json', sa.Text(), nullable=False, server_default='{}'))


def downgrade():
    op.drop_column('products', 'dynamic_fields_json')
    op.drop_column('products', 'main_image')
    op.drop_column('products', 'product_type')
