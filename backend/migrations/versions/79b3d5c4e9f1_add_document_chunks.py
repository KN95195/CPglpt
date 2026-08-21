"""add document chunks for RAG

Revision ID: 79b3d5c4e9f1
Revises: 87c91dc462a8
"""
from alembic import op
import sqlalchemy as sa

revision = '79b3d5c4e9f1'
down_revision = '87c91dc462a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding_json', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'])


def downgrade():
    op.drop_index('ix_document_chunks_document_id', table_name='document_chunks')
    op.drop_table('document_chunks')
