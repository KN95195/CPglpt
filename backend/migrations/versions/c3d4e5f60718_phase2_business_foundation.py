"""phase2 business foundation

Revision ID: c3d4e5f60718
Revises: 7a8c9d0e1f23
"""
from alembic import op
import sqlalchemy as sa

revision='c3d4e5f60718'
down_revision='7a8c9d0e1f23'
branch_labels=None
depends_on=None

timestamps=lambda:[sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now())]

def upgrade():
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT roles.id, permissions.id
        FROM roles
        CROSS JOIN permissions
        WHERE roles.code = 'sales'
          AND permissions.code IN ('BOM_EDIT', 'PRICE_VIEW')
        ON CONFLICT DO NOTHING
    """)
    op.add_column('bom_rules',sa.Column('rule_type',sa.String(32),nullable=False,server_default='RECOMMEND'))
    op.add_column('bom_rules',sa.Column('current_version',sa.Integer(),nullable=False,server_default='1'))
    for column in [sa.Column('sales_owner_id',sa.Integer(),nullable=True),sa.Column('status',sa.String(24),nullable=False,server_default='DRAFT'),sa.Column('current_requirement_version_id',sa.Integer(),nullable=True),sa.Column('current_bom_version_id',sa.Integer(),nullable=True),sa.Column('notes',sa.Text(),nullable=False,server_default=''),sa.Column('created_by',sa.Integer(),nullable=True)]:op.add_column('projects',column)
    op.create_foreign_key('fk_projects_sales_owner','projects','users',['sales_owner_id'],['id'],ondelete='SET NULL');op.create_foreign_key('fk_projects_created_by','projects','users',['created_by'],['id'],ondelete='SET NULL')
    op.create_table('project_requirement_versions',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('version',sa.Integer(),nullable=False),sa.Column('raw_requirement',sa.Text(),nullable=False,server_default=''),sa.Column('ai_parsed_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('user_adjusted_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('confirmed_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('confirmed_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('confirmed_at',sa.DateTime(timezone=True)),*timestamps(),sa.UniqueConstraint('project_id','version',name='uq_project_requirement_version'))
    op.create_table('bom_rule_versions',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('rule_id',sa.Integer(),sa.ForeignKey('bom_rules.id',ondelete='CASCADE'),nullable=False),sa.Column('version',sa.Integer(),nullable=False),sa.Column('rule_type',sa.String(32),nullable=False),sa.Column('condition_json',sa.Text(),nullable=False),sa.Column('action_json',sa.Text(),nullable=False),sa.Column('enabled',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('changed_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),*timestamps(),sa.UniqueConstraint('rule_id','version',name='uq_bom_rule_version'))
    op.create_table('project_bom_versions',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('version',sa.Integer(),nullable=False),sa.Column('requirement_version_id',sa.Integer(),sa.ForeignKey('project_requirement_versions.id',ondelete='SET NULL')),sa.Column('source',sa.String(32),nullable=False,server_default='AI_RECOMMEND'),sa.Column('snapshot_json',sa.Text(),nullable=False,server_default='[]'),sa.Column('manual_edited',sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column('change_summary',sa.Text(),nullable=False,server_default=''),sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),*timestamps(),sa.UniqueConstraint('project_id','version',name='uq_project_bom_version'))
    op.create_table('bom_validation_runs',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('bom_version_id',sa.Integer(),sa.ForeignKey('project_bom_versions.id',ondelete='CASCADE'),nullable=False),sa.Column('run_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column('run_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('rule_version_set_json',sa.Text(),nullable=False,server_default='[]'),sa.Column('pass_count',sa.Integer(),nullable=False,server_default='0'),sa.Column('warning_count',sa.Integer(),nullable=False,server_default='0'),sa.Column('error_count',sa.Integer(),nullable=False,server_default='0'),sa.Column('result_json',sa.Text(),nullable=False,server_default='[]'),sa.Column('override_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('override_reason',sa.Text(),nullable=False,server_default=''),sa.Column('override_at',sa.DateTime(timezone=True)),*timestamps())
    op.create_table('excel_templates',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('name',sa.String(180),nullable=False),sa.Column('description',sa.Text(),nullable=False,server_default=''),sa.Column('current_version',sa.Integer(),nullable=False,server_default='1'),sa.Column('enabled',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),*timestamps())
    op.create_table('excel_template_versions',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('template_id',sa.Integer(),sa.ForeignKey('excel_templates.id',ondelete='CASCADE'),nullable=False),sa.Column('version',sa.Integer(),nullable=False),sa.Column('original_file_name',sa.String(255),nullable=False),sa.Column('file_path',sa.String(500),nullable=False),sa.Column('file_hash',sa.String(64),nullable=False),sa.Column('sheet_name',sa.String(160),nullable=False,server_default=''),sa.Column('placeholder_mappings_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('bom_template_row',sa.Integer()),sa.Column('bom_column_mappings_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('analyzed_json',sa.Text(),nullable=False,server_default='{}'),sa.Column('uploaded_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),*timestamps(),sa.UniqueConstraint('template_id','version',name='uq_excel_template_version'))
    op.create_table('export_records',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id',ondelete='CASCADE'),nullable=False),sa.Column('bom_version_id',sa.Integer(),sa.ForeignKey('project_bom_versions.id'),nullable=False),sa.Column('template_version_id',sa.Integer(),sa.ForeignKey('excel_template_versions.id'),nullable=False),sa.Column('export_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('export_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column('file_path',sa.String(500),nullable=False),sa.Column('file_name',sa.String(255),nullable=False),sa.Column('file_hash',sa.String(64),nullable=False),*timestamps())
    document_columns=[sa.Column('original_file_name',sa.String(255),nullable=False,server_default=''),sa.Column('file_size',sa.Integer(),nullable=False,server_default='0'),sa.Column('category',sa.String(80),nullable=False,server_default='产品资料'),sa.Column('version',sa.String(32),nullable=False,server_default='V1.0'),sa.Column('description',sa.Text(),nullable=False,server_default=''),sa.Column('status',sa.String(24),nullable=False,server_default='DRAFT'),sa.Column('document_status',sa.String(24),nullable=False,server_default='CURRENT'),sa.Column('applicable_models',sa.Text(),nullable=False,server_default=''),sa.Column('applicable_versions',sa.Text(),nullable=False,server_default=''),sa.Column('knowledge_enabled',sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column('knowledge_status',sa.String(24),nullable=False,server_default='NOT_SYNCED'),sa.Column('knowledge_document_id',sa.String(160),nullable=False,server_default=''),sa.Column('knowledge_dataset_id',sa.String(160),nullable=False,server_default=''),sa.Column('last_knowledge_sync_at',sa.DateTime(timezone=True)),sa.Column('knowledge_sync_error',sa.Text(),nullable=False,server_default=''),sa.Column('uploaded_by',sa.Integer(),nullable=True)]
    for column in document_columns:op.add_column('documents',column)
    op.create_foreign_key('fk_documents_uploaded_by','documents','users',['uploaded_by'],['id'],ondelete='SET NULL')
    op.create_table('document_previews',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('document_id',sa.Integer(),sa.ForeignKey('documents.id',ondelete='CASCADE'),nullable=False),sa.Column('preview_type',sa.String(24),nullable=False),sa.Column('file_path',sa.String(500),nullable=False),sa.Column('mime_type',sa.String(100),nullable=False),sa.Column('status',sa.String(24),nullable=False,server_default='READY'),sa.Column('error_message',sa.Text(),nullable=False,server_default=''),*timestamps())
    op.create_table('document_knowledge_syncs',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('document_id',sa.Integer(),sa.ForeignKey('documents.id',ondelete='CASCADE'),nullable=False),sa.Column('status',sa.String(24),nullable=False),sa.Column('requested_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='SET NULL')),sa.Column('started_at',sa.DateTime(timezone=True)),sa.Column('finished_at',sa.DateTime(timezone=True)),sa.Column('dataset_id',sa.String(160),nullable=False,server_default=''),sa.Column('external_document_id',sa.String(160),nullable=False,server_default=''),sa.Column('error_message',sa.Text(),nullable=False,server_default=''),*timestamps())

def downgrade():
    op.drop_table('document_knowledge_syncs');op.drop_table('document_previews');op.drop_constraint('fk_documents_uploaded_by','documents',type_='foreignkey')
    for name in ['uploaded_by','knowledge_sync_error','last_knowledge_sync_at','knowledge_dataset_id','knowledge_document_id','knowledge_status','knowledge_enabled','applicable_versions','applicable_models','document_status','status','description','version','category','file_size','original_file_name']:op.drop_column('documents',name)
    for table in ['export_records','excel_template_versions','excel_templates','bom_validation_runs','project_bom_versions','bom_rule_versions','project_requirement_versions']:op.drop_table(table)
    op.drop_constraint('fk_projects_created_by','projects',type_='foreignkey');op.drop_constraint('fk_projects_sales_owner','projects',type_='foreignkey')
    for name in ['created_by','notes','current_bom_version_id','current_requirement_version_id','status','sales_owner_id']:op.drop_column('projects',name)
    op.drop_column('bom_rules','current_version');op.drop_column('bom_rules','rule_type')
    op.execute("""
        DELETE FROM role_permissions
        USING roles, permissions
        WHERE role_permissions.role_id = roles.id
          AND role_permissions.permission_id = permissions.id
          AND roles.code = 'sales'
          AND permissions.code IN ('BOM_EDIT', 'PRICE_VIEW')
    """)
