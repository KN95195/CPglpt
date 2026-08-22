"""Initial formal schema.

Revision ID: 8c453412069a
Revises:
Create Date: 2026-08-21

This revision is an immutable historical snapshot. Importing current ORM metadata
here makes a clean install create columns and tables owned by later revisions.
"""
from alembic import op
import sqlalchemy as sa

revision = '8c453412069a'
down_revision = None
branch_labels = None
depends_on = None


def ts():
    return [
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade():
    op.create_table('roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(64), nullable=False, unique=True),
        sa.Column('name', sa.String(80), nullable=False),
        sa.Column('permissions', sa.Text(), nullable=False, server_default=''), *ts())
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(64), nullable=False, unique=True),
        sa.Column('display_name', sa.String(80), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()), *ts())
    op.create_table('product_categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(80), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=False, server_default=''), *ts())
    op.create_table('products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(160), nullable=False, unique=True),
        sa.Column('model_code', sa.String(80), nullable=False, unique=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('product_categories.id'), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(32), nullable=False, server_default='ON_SALE'),
        sa.Column('data_status', sa.String(32), nullable=False, server_default='CONFIRMED'),
        sa.Column('source', sa.String(80), nullable=False, server_default='正式演示数据'),
        sa.Column('owner', sa.String(80), nullable=False, server_default='产品中心'),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=False), *ts())
    op.create_table('capabilities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('category', sa.String(80), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='SUPPORTED'), *ts())
    op.create_table('algorithms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('version', sa.String(32), nullable=False),
        sa.Column('category', sa.String(80), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='SUPPORTED'), *ts())
    op.create_table('software',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('version', sa.String(32), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='SUPPORTED'), *ts())
    op.create_table('scenes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('pain_points', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(32), nullable=False, server_default='ON_SALE'), *ts())
    op.create_table('solutions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('scene_id', sa.Integer(), sa.ForeignKey('scenes.id'), nullable=False),
        sa.Column('tier', sa.String(32), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False), *ts())
    op.create_table('product_capabilities',
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), primary_key=True),
        sa.Column('capability_id', sa.Integer(), sa.ForeignKey('capabilities.id'), primary_key=True))
    op.create_table('bom_rules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(80), nullable=False, unique=True),
        sa.Column('name', sa.String(160), nullable=False),
        sa.Column('condition_json', sa.Text(), nullable=False),
        sa.Column('recommendation_json', sa.Text(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()), *ts())
    op.create_table('projects',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(160), nullable=False),
        sa.Column('customer', sa.String(160), nullable=False),
        sa.Column('region', sa.String(100), nullable=False),
        sa.Column('scene_id', sa.Integer(), sa.ForeignKey('scenes.id'), nullable=False),
        sa.Column('requirements_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('bom_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('bom_version', sa.Integer(), nullable=False, server_default='1'), *ts())
    op.create_table('product_prices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('reference_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('cost_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(8), nullable=False, server_default='CNY'), *ts())
    op.create_table('price_access_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('resource', sa.String(120), nullable=False), *ts())
    op.create_table('documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True),
        sa.Column('scene_id', sa.Integer(), sa.ForeignKey('scenes.id'), nullable=True), *ts())
    op.create_table('ai_interaction_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('request_id', sa.String(64), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('provider', sa.String(32), nullable=False),
        sa.Column('model_id', sa.String(160), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=False, server_default=''), *ts())


def downgrade():
    for table in [
        'ai_interaction_logs', 'documents', 'price_access_logs', 'product_prices',
        'projects', 'bom_rules', 'product_capabilities', 'solutions', 'scenes',
        'software', 'algorithms', 'capabilities', 'products', 'product_categories',
        'users', 'roles',
    ]:
        op.drop_table(table)
