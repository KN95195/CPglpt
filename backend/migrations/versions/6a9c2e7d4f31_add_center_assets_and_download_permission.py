"""add generic center assets and document download permission

Revision ID: 6a9c2e7d4f31
Revises: 4f6d8a2c1b90
"""
from alembic import op
import sqlalchemy as sa

revision = '6a9c2e7d4f31'
down_revision = '4f6d8a2c1b90'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('tender_parameters_json', sa.Text(), nullable=False, server_default='[]'))
    op.add_column('solutions', sa.Column('cover_image', sa.String(500), nullable=False, server_default=''))
    op.add_column('documents', sa.Column('center_type', sa.String(48), nullable=True))
    op.add_column('documents', sa.Column('center_id', sa.Integer(), nullable=True))
    op.create_index('ix_documents_center', 'documents', ['center_type', 'center_id'])
    op.create_table(
        'knowledge_images',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('public_id', sa.String(64), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_knowledge_images_public_id', 'knowledge_images', ['public_id'], unique=True)

    bind = op.get_bind()
    bind.execute(sa.text("""
        INSERT INTO permissions (code, name, description, created_at, updated_at)
        SELECT 'DOCUMENT_DOWNLOAD', '资料下载', '允许下载知识中心资料附件', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE code='DOCUMENT_DOWNLOAD')
    """))
    bind.execute(sa.text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT DISTINCT rp.role_id, p.id
        FROM role_permissions rp
        JOIN permissions manage ON manage.id=rp.permission_id AND manage.code='KNOWLEDGE_MANAGE'
        JOIN permissions p ON p.code='DOCUMENT_DOWNLOAD'
        WHERE NOT EXISTS (
            SELECT 1 FROM role_permissions existing
            WHERE existing.role_id=rp.role_id AND existing.permission_id=p.id
        )
    """))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        DELETE FROM role_permissions
        WHERE permission_id IN (SELECT id FROM permissions WHERE code='DOCUMENT_DOWNLOAD')
    """))
    bind.execute(sa.text("DELETE FROM permissions WHERE code='DOCUMENT_DOWNLOAD'"))
    op.drop_index('ix_knowledge_images_public_id', table_name='knowledge_images')
    op.drop_table('knowledge_images')
    op.drop_index('ix_documents_center', table_name='documents')
    op.drop_column('documents', 'center_id')
    op.drop_column('documents', 'center_type')
    op.drop_column('solutions', 'cover_image')
    op.drop_column('products', 'tender_parameters_json')
