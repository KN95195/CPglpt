"""add material variants and directory-backed users

Revision ID: 9d3f4a6b8c21
Revises: 6a9c2e7d4f31
"""
from alembic import op
import sqlalchemy as sa

revision = '9d3f4a6b8c21'
down_revision = '6a9c2e7d4f31'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email', sa.String(160), nullable=False, server_default=''))
    op.add_column('users', sa.Column('department', sa.String(160), nullable=False, server_default=''))
    op.add_column('users', sa.Column('auth_source', sa.String(24), nullable=False, server_default='LOCAL'))
    op.add_column('users', sa.Column('external_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('last_directory_sync_at', sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint('uq_users_external_id', 'users', ['external_id'])
    op.create_table('product_variants',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('model_code', sa.String(100), nullable=False), sa.Column('material_code', sa.String(80), nullable=False, server_default=''),
        sa.Column('unit', sa.String(24), nullable=False, server_default='台'), sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_agent_product', sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column('agent_price', sa.Numeric(14,2), nullable=True),
        sa.Column('sale_price', sa.Numeric(14,2), nullable=True), sa.Column('warranty_months', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('extended_warranty_rule', sa.Text(), nullable=False, server_default=''), sa.Column('applicable_scenes_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('sales_notes', sa.Text(), nullable=False, server_default=''), sa.Column('commercial_status', sa.String(32), nullable=False, server_default='ACTIVE'),
        sa.Column('specifications_json', sa.Text(), nullable=False, server_default='{}'), sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('product_id','model_code',name='uq_product_variant_model'))
    op.create_table('directory_sync_runs',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('provider', sa.String(32), nullable=False, server_default='AD'),
        sa.Column('status', sa.String(24), nullable=False), sa.Column('created_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_count', sa.Integer(), nullable=False, server_default='0'), sa.Column('disabled_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=False, server_default=''), sa.Column('initiated_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_table('knowledge_commercial_profiles',
        sa.Column('id',sa.Integer(),primary_key=True),sa.Column('center_type',sa.String(48),nullable=False),sa.Column('center_id',sa.Integer(),nullable=False),
        sa.Column('material_code',sa.String(80),nullable=False,server_default=''),sa.Column('unit',sa.String(32),nullable=False,server_default='套'),
        sa.Column('is_agent_product',sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column('agent_price',sa.Numeric(14,2),nullable=True),sa.Column('sale_price',sa.Numeric(14,2),nullable=True),
        sa.Column('warranty_months',sa.Integer(),nullable=False,server_default='12'),sa.Column('extended_warranty_rule',sa.Text(),nullable=False,server_default=''),
        sa.Column('applicable_scenes_json',sa.Text(),nullable=False,server_default='[]'),sa.Column('sales_notes',sa.Text(),nullable=False,server_default=''),
        sa.Column('commercial_status',sa.String(32),nullable=False,server_default='ACTIVE'),sa.Column('license_unit',sa.String(40),nullable=False,server_default=''),
        sa.Column('included_quantity',sa.Integer(),nullable=True),sa.Column('overage_unit_price',sa.Numeric(14,2),nullable=True),sa.Column('delivery_method',sa.String(160),nullable=False,server_default=''),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint('center_type','center_id',name='uq_knowledge_commercial_profile'))
    bind=op.get_bind()
    bind.execute(sa.text("""INSERT INTO permissions (code,name,description,created_at,updated_at)
        SELECT 'USER_MANAGE','用户与角色管理','管理用户、角色、权限和AD同步',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP
        WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE code='USER_MANAGE')"""))
    bind.execute(sa.text("""INSERT INTO role_permissions (role_id,permission_id)
        SELECT r.id,p.id FROM roles r CROSS JOIN permissions p WHERE r.code='admin' AND p.code='USER_MANAGE'
        AND NOT EXISTS (SELECT 1 FROM role_permissions rp WHERE rp.role_id=r.id AND rp.permission_id=p.id)"""))


def downgrade():
    op.drop_table('knowledge_commercial_profiles')
    op.drop_table('directory_sync_runs')
    op.drop_table('product_variants')
    op.drop_constraint('uq_users_external_id','users',type_='unique')
    for column in ['last_directory_sync_at','external_id','auth_source','department','email']:
        op.drop_column('users',column)
