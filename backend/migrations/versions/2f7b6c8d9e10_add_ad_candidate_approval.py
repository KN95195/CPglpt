"""add manual AD candidate approval

Revision ID: 2f7b6c8d9e10
Revises: 9d3f4a6b8c21
"""
from alembic import op
import sqlalchemy as sa

revision='2f7b6c8d9e10'
down_revision='9d3f4a6b8c21'
branch_labels=None
depends_on=None

ROLE_NAMES={'sales':'销售人员','presales':'售前人员','sales_support':'销售支持','product_admin':'产品经理','algorithm_admin':'算法管理员','price_admin':'价格管理员','admin':'系统管理员'}
PERMISSION_NAMES={
    'KNOWLEDGE_VIEW':'查看知识内容','KNOWLEDGE_MANAGE':'管理知识内容','PRICE_VIEW':'查看价格','PRICE_EXPORT':'导出价格','COST_VIEW':'查看成本价',
    'USER_MANAGE':'用户与角色管理','DOCUMENT_VIEW':'查看资料','DOCUMENT_EDIT':'管理资料','DOCUMENT_DOWNLOAD':'下载资料','TENDER_VIEW':'查看招投标','TENDER_EDIT':'管理招投标',
    'BOM_VIEW':'查看配单','BOM_EDIT':'管理配单','TRAINING_VIEW':'查看培训','TRAINING_ADMIN':'管理培训','AI_MANAGE':'使用智能能力','SYSTEM_MANAGE':'系统管理',
    'PRODUCT_VIEW':'查看产品','PRODUCT_EDIT':'管理产品','SOFTWARE_VIEW':'查看软件','SOFTWARE_EDIT':'管理软件','ALGORITHM_VIEW':'查看算法','ALGORITHM_EDIT':'管理算法',
    'CAPABILITY_VIEW':'查看模型能力','CAPABILITY_EDIT':'管理模型能力','SCENE_VIEW':'查看场景','SCENE_EDIT':'管理场景','SOLUTION_VIEW':'查看方案','SOLUTION_EDIT':'管理方案',
}

def upgrade():
    op.create_table('directory_sync_candidates',
        sa.Column('id',sa.Integer(),primary_key=True),sa.Column('run_id',sa.Integer(),sa.ForeignKey('directory_sync_runs.id',ondelete='CASCADE'),nullable=False),
        sa.Column('external_id',sa.String(255),nullable=False),sa.Column('username',sa.String(64),nullable=False),sa.Column('display_name',sa.String(80),nullable=False,server_default=''),
        sa.Column('email',sa.String(160),nullable=False,server_default=''),sa.Column('department',sa.String(160),nullable=False,server_default=''),sa.Column('distinguished_name',sa.String(500),nullable=False,server_default=''),
        sa.Column('change_type',sa.String(24),nullable=False,server_default='CREATE'),sa.Column('approval_status',sa.String(24),nullable=False,server_default='PENDING'),sa.Column('role_code',sa.String(64),nullable=False,server_default='sales'),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint('run_id','external_id',name='uq_directory_candidate_external'))
    bind=op.get_bind()
    for code,name in ROLE_NAMES.items():bind.execute(sa.text('UPDATE roles SET name=:name WHERE code=:code'),{'name':name,'code':code})
    for code,name in PERMISSION_NAMES.items():bind.execute(sa.text('UPDATE permissions SET name=:name, description=:description WHERE code=:code'),{'name':name,'description':name,'code':code})

def downgrade():
    op.drop_table('directory_sync_candidates')
