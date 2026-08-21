"""extend product price fields

Revision ID: a2c63a4f5798
Revises: f1b5293e4687
"""
from alembic import op
import sqlalchemy as sa

revision='a2c63a4f5798'
down_revision='f1b5293e4687'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('product_prices',sa.Column('tax_included',sa.Boolean(),nullable=False,server_default=sa.true()))
    op.add_column('product_prices',sa.Column('tax_rate',sa.Numeric(5,2),nullable=False,server_default='13'))
    op.add_column('product_prices',sa.Column('valid_until',sa.DateTime(timezone=True),nullable=True))
    op.add_column('product_prices',sa.Column('notes',sa.Text(),nullable=False,server_default=''))


def downgrade():
    for column in ['notes','valid_until','tax_rate','tax_included']:op.drop_column('product_prices',column)
