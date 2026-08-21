"""Backfill representative product-capability relationships.

Revision ID: c81f0e2a91b7
Revises: b460e9d728a2
"""

from alembic import op


revision = "c81f0e2a91b7"
down_revision = "b460e9d728a2"
branch_labels = None
depends_on = None


MAPPING = """
WITH ranked_products AS (
    SELECT id, row_number() OVER (ORDER BY id) AS rn FROM products
), ranked_capabilities AS (
    SELECT id, row_number() OVER (ORDER BY id) AS rn FROM capabilities
)
SELECT p.id AS product_id, c.id AS capability_id
FROM ranked_products p
JOIN ranked_capabilities c ON c.rn = p.rn
"""


def upgrade():
    op.execute(
        "INSERT INTO product_capabilities (product_id, capability_id) "
        + MAPPING
        + " ON CONFLICT (product_id, capability_id) DO NOTHING"
    )


def downgrade():
    op.execute(
        "DELETE FROM product_capabilities pc USING ("
        + MAPPING
        + ") mapped WHERE pc.product_id = mapped.product_id "
        "AND pc.capability_id = mapped.capability_id"
    )
