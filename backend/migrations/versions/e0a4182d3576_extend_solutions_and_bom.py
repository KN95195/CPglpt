"""extend solutions and standard BOM

Revision ID: e0a4182d3576
Revises: d9f3071c2465
"""
from alembic import op
import sqlalchemy as sa

revision = 'e0a4182d3576'
down_revision = 'd9f3071c2465'
branch_labels = None
depends_on = None


def upgrade():
    for column in [
        sa.Column('code',sa.String(80),nullable=False,server_default=''),
        sa.Column('category',sa.String(80),nullable=False,server_default='水域安全'),
        sa.Column('status',sa.String(32),nullable=False,server_default='ACTIVE'),
        sa.Column('target_description',sa.Text(),nullable=False,server_default=''),
        sa.Column('coverage_scope',sa.Text(),nullable=False,server_default=''),
        sa.Column('architecture_summary',sa.Text(),nullable=False,server_default=''),
        sa.Column('implementation_notes',sa.Text(),nullable=False,server_default=''),
    ]: op.add_column('solutions',column)
    op.create_table('solution_bom_items',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('solution_id',sa.Integer(),sa.ForeignKey('solutions.id',ondelete='CASCADE'),nullable=False),sa.Column('product_id',sa.Integer(),sa.ForeignKey('products.id'),nullable=False),sa.Column('quantity',sa.Integer(),nullable=False,server_default='1'),sa.Column('unit',sa.String(24),nullable=False,server_default='台'),sa.Column('purpose',sa.String(240),nullable=False,server_default=''),sa.Column('requirement_level',sa.String(24),nullable=False,server_default='REQUIRED'),sa.Column('recommendation_reason',sa.Text(),nullable=False,server_default=''),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False))


def downgrade():
    op.drop_table('solution_bom_items')
    for column in ['implementation_notes','architecture_summary','coverage_scope','target_description','status','category','code']:op.drop_column('solutions',column)
