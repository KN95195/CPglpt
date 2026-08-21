"""add Moodle training course associations

Revision ID: b460e9d728a2
Revises: 79b3d5c4e9f1
"""
from alembic import op
import sqlalchemy as sa

revision = 'b460e9d728a2'
down_revision = '79b3d5c4e9f1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'training_courses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('external_course_id', sa.String(length=80), nullable=False, unique=True),
        sa.Column('name', sa.String(length=180), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('launch_url', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('training_courses')
