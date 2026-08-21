"""Add tenders and document associations.

Revision ID: d92a6b7c31e4
Revises: c81f0e2a91b7
"""

from alembic import op
import sqlalchemy as sa


revision = "d92a6b7c31e4"
down_revision = "c81f0e2a91b7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=180), nullable=False, unique=True),
        sa.Column("customer", sa.String(length=160), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PREPARING"),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column("documents", sa.Column("tender_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_documents_tender_id", "documents", "tenders", ["tender_id"], ["id"], ondelete="SET NULL"
    )


def downgrade():
    op.drop_constraint("fk_documents_tender_id", "documents", type_="foreignkey")
    op.drop_column("documents", "tender_id")
    op.drop_table("tenders")
