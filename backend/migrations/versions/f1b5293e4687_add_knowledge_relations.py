"""add bidirectional knowledge relations

Revision ID: f1b5293e4687
Revises: e0a4182d3576
"""
from alembic import op
import sqlalchemy as sa

revision='f1b5293e4687'
down_revision='e0a4182d3576'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('knowledge_relations',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('source_type',sa.String(48),nullable=False),sa.Column('source_id',sa.Integer(),nullable=False),sa.Column('target_type',sa.String(48),nullable=False),sa.Column('target_id',sa.Integer(),nullable=False),sa.Column('metadata_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),sa.UniqueConstraint('source_type','source_id','target_type','target_id',name='uq_knowledge_relation'))
    op.create_index('ix_knowledge_relation_source','knowledge_relations',['source_type','source_id'])
    op.create_index('ix_knowledge_relation_target','knowledge_relations',['target_type','target_id'])


def downgrade():
    op.drop_index('ix_knowledge_relation_target',table_name='knowledge_relations');op.drop_index('ix_knowledge_relation_source',table_name='knowledge_relations');op.drop_table('knowledge_relations')
