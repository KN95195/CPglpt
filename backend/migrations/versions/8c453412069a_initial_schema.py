"""Initial formal schema.

Revision ID: 8c453412069a
Revises:
Create Date: 2026-08-21
"""
from alembic import op
from app.database import Base
from app import models  # noqa: F401 - registers the formal model metadata

revision = '8c453412069a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    Base.metadata.create_all(bind=op.get_bind())


def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
