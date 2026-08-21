"""freeze six-center permissions

Revision ID: e4f8a2c7d910
Revises: d92a6b7c31e4
"""
from alembic import op
import sqlalchemy as sa

revision = 'e4f8a2c7d910'
down_revision = 'd92a6b7c31e4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    for code, name in [
        ('KNOWLEDGE_VIEW', '知识查看'),
        ('KNOWLEDGE_MANAGE', '知识管理'),
        ('PRICE_VIEW', '价格查看'),
    ]:
        bind.execute(sa.text("""
            INSERT INTO permissions (code, name, description, created_at, updated_at)
            SELECT :code, :name, '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE code = :code)
        """), {'code': code, 'name': name})

    mapping = {
        'sales': ['KNOWLEDGE_VIEW'],
        'presales': ['KNOWLEDGE_VIEW'],
        'sales_support': ['KNOWLEDGE_VIEW', 'PRICE_VIEW'],
        'product_admin': ['KNOWLEDGE_VIEW', 'KNOWLEDGE_MANAGE', 'PRICE_VIEW'],
        'algorithm_admin': ['KNOWLEDGE_VIEW', 'KNOWLEDGE_MANAGE', 'PRICE_VIEW'],
        'price_admin': ['KNOWLEDGE_VIEW', 'PRICE_VIEW'],
        'admin': ['KNOWLEDGE_VIEW', 'KNOWLEDGE_MANAGE', 'PRICE_VIEW'],
    }
    knowledge_codes = [
        'PRODUCT_VIEW', 'PRODUCT_EDIT', 'SOFTWARE_VIEW', 'SOFTWARE_EDIT',
        'ALGORITHM_VIEW', 'ALGORITHM_EDIT', 'CAPABILITY_VIEW', 'CAPABILITY_EDIT',
        'SCENE_VIEW', 'SCENE_EDIT', 'SOLUTION_VIEW', 'SOLUTION_EDIT',
    ]
    bind.execute(sa.text("""
        DELETE FROM role_permissions
        WHERE permission_id IN (SELECT id FROM permissions WHERE code IN :codes)
    """).bindparams(sa.bindparam('codes', expanding=True)), {'codes': knowledge_codes})
    for role_code, codes in mapping.items():
        role_id = bind.execute(sa.text('SELECT id FROM roles WHERE code = :code'), {'code': role_code}).scalar()
        if role_id is None:
            continue
        for code in codes:
            permission_id = bind.execute(sa.text('SELECT id FROM permissions WHERE code = :code'), {'code': code}).scalar_one()
            bind.execute(sa.text("""
                INSERT INTO role_permissions (role_id, permission_id)
                SELECT :role_id, :permission_id
                WHERE NOT EXISTS (
                    SELECT 1 FROM role_permissions
                    WHERE role_id = :role_id AND permission_id = :permission_id
                )
            """), {'role_id': role_id, 'permission_id': permission_id})
        bind.execute(sa.text('UPDATE roles SET permissions = :permissions WHERE id = :role_id'), {
            'permissions': ','.join(codes), 'role_id': role_id,
        })


def downgrade():
    pass
