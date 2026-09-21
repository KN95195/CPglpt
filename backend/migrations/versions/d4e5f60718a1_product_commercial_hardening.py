"""product commercial hardening

Revision ID: d4e5f60718a1
Revises: c3d4e5f60718
"""
from alembic import op
import sqlalchemy as sa

revision='d4e5f60718a1'
down_revision='c3d4e5f60718'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('products', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ix_products_display_order', 'products', ['display_order'])
    op.create_table(
        'product_variant_offers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('product_variants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price_type', sa.String(32), nullable=False, server_default='SALES'),
        sa.Column('channel', sa.String(32), nullable=False, server_default='DIRECT'),
        sa.Column('warranty_months', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(14, 2), nullable=False),
        sa.Column('currency', sa.String(8), nullable=False, server_default='CNY'),
        sa.Column('tax_included', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='13'),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('status', sa.String(32), nullable=False, server_default='ACTIVE'),
        sa.Column('notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_product_variant_offers_variant_id', 'product_variant_offers', ['variant_id'])
    op.execute("""
        WITH ranked AS (
          SELECT id, row_number() OVER (ORDER BY id) - 1 AS position FROM products
        )
        UPDATE products SET display_order = ranked.position FROM ranked WHERE products.id = ranked.id
    """)
    op.execute("UPDATE product_variants SET warranty_months = 24 WHERE warranty_months = 12 AND commercial_status <> 'ARCHIVED'")
    op.execute("""
        INSERT INTO product_variant_offers
          (variant_id, price_type, channel, warranty_months, amount, currency, tax_included, tax_rate, is_default, status, notes, created_at, updated_at)
        SELECT id, 'AGENT', 'AGENT', 24, agent_price, 'CNY', true, 13, false, 'ACTIVE', '由既有代理价迁移', now(), now()
        FROM product_variants WHERE agent_price IS NOT NULL AND commercial_status <> 'ARCHIVED'
    """)
    op.execute("""
        INSERT INTO product_variant_offers
          (variant_id, price_type, channel, warranty_months, amount, currency, tax_included, tax_rate, is_default, status, notes, created_at, updated_at)
        SELECT id, 'SALES', 'DIRECT', 24, sale_price, 'CNY', true, 13, is_primary, 'ACTIVE', '由既有销售价迁移；两年质保', now(), now()
        FROM product_variants WHERE sale_price IS NOT NULL AND commercial_status <> 'ARCHIVED'
    """)


def downgrade():
    op.drop_index('ix_product_variant_offers_variant_id', table_name='product_variant_offers')
    op.drop_table('product_variant_offers')
    op.drop_index('ix_products_display_order', table_name='products')
    op.drop_column('products', 'display_order')
