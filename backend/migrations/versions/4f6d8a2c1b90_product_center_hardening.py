"""implement R3 six-center production schema

Revision ID: 4f6d8a2c1b90
Revises: a2c63a4f5798
"""
import json

from alembic import op
import sqlalchemy as sa

revision = '4f6d8a2c1b90'
down_revision = 'a2c63a4f5798'
branch_labels = None
depends_on = None


def timestamps():
    return [
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def load_json(raw, fallback):
    try:
        value = json.loads(raw or '')
        return value if isinstance(value, type(fallback)) else fallback
    except (TypeError, ValueError):
        return fallback


def upgrade():
    for column in [
        sa.Column('product_code', sa.String(80), nullable=False, server_default=''),
        sa.Column('product_series', sa.String(100), nullable=False, server_default=''),
        sa.Column('current_version', sa.String(32), nullable=False, server_default='v1.0'),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('tags_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('boundaries_json', sa.Text(), nullable=False, server_default='[]'),
    ]:
        op.add_column('products', column)
    op.execute("UPDATE products SET product_code=model_code WHERE product_code='' OR product_code IS NULL")
    op.create_unique_constraint('uq_products_product_code', 'products', ['product_code'])

    op.create_table(
        'product_parameters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('value', sa.Text(), nullable=False, server_default=''),
        sa.Column('unit', sa.String(32), nullable=False, server_default=''),
        sa.Column('group_name', sa.String(80), nullable=False, server_default='基础参数'),
        sa.Column('highlight', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('data_type', sa.String(24), nullable=False, server_default='TEXT'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
        sa.UniqueConstraint('product_id', 'name', 'group_name', name='uq_product_parameter_name'),
    )
    op.create_table(
        'product_media',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image', sa.String(500), nullable=False),
        sa.Column('title', sa.String(160), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'product_features',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(160), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('icon', sa.String(80), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )

    for column in [
        sa.Column('database_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('protocols_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('boundaries_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('logo', sa.String(500), nullable=False, server_default=''),
        sa.Column('detail_description', sa.Text(), nullable=False, server_default=''),
    ]:
        op.add_column('software', column)
    op.create_table(
        'software_modules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('software_id', sa.Integer(), sa.ForeignKey('software.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('icon', sa.String(80), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'software_features',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('module_id', sa.Integer(), sa.ForeignKey('software_modules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(160), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'software_versions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('software_id', sa.Integer(), sa.ForeignKey('software.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.String(32), nullable=False),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False, server_default=''),
        *timestamps(),
    )
    op.create_table(
        'software_media',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('software_id', sa.Integer(), sa.ForeignKey('software.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image', sa.String(500), nullable=False),
        sa.Column('title', sa.String(160), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )

    op.add_column('algorithms', sa.Column('principle', sa.Text(), nullable=False, server_default=''))
    op.create_table(
        'algorithm_parameters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('algorithm_id', sa.Integer(), sa.ForeignKey('algorithms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('value', sa.Text(), nullable=False, server_default=''),
        sa.Column('unit', sa.String(32), nullable=False, server_default=''),
        sa.Column('group_name', sa.String(80), nullable=False, server_default='核心参数'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'algorithm_metrics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('algorithm_id', sa.Integer(), sa.ForeignKey('algorithms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('value', sa.Text(), nullable=False, server_default=''),
        sa.Column('unit', sa.String(32), nullable=False, server_default=''),
        sa.Column('group_name', sa.String(80), nullable=False, server_default='性能指标'),
        sa.Column('condition', sa.Text(), nullable=False, server_default=''),
        sa.Column('source', sa.String(240), nullable=False, server_default=''),
        sa.Column('highlight', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )

    for column in [
        sa.Column('model_type', sa.String(80), nullable=False, server_default='DETECTION'),
        sa.Column('task_type', sa.String(80), nullable=False, server_default=''),
        sa.Column('use_conditions_json', sa.Text(), nullable=False, server_default='[]'),
    ]:
        op.add_column('capabilities', column)
    op.create_table(
        'model_metrics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('capability_id', sa.Integer(), sa.ForeignKey('capabilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('value', sa.Text(), nullable=False, server_default=''),
        sa.Column('unit', sa.String(32), nullable=False, server_default=''),
        sa.Column('group_name', sa.String(80), nullable=False, server_default='性能指标'),
        sa.Column('condition', sa.Text(), nullable=False, server_default=''),
        sa.Column('source', sa.String(240), nullable=False, server_default=''),
        sa.Column('dataset', sa.String(200), nullable=False, server_default=''),
        sa.Column('sample_count', sa.String(80), nullable=False, server_default=''),
        sa.Column('input_resolution', sa.String(80), nullable=False, server_default=''),
        sa.Column('hardware', sa.String(160), nullable=False, server_default=''),
        sa.Column('runtime', sa.String(120), nullable=False, server_default=''),
        sa.Column('tested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('highlight', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'model_input_definitions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('capability_id', sa.Integer(), sa.ForeignKey('capabilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('data_type', sa.String(80), nullable=False),
        sa.Column('required', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('example', sa.Text(), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'model_output_definitions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('capability_id', sa.Integer(), sa.ForeignKey('capabilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('data_type', sa.String(80), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('example', sa.Text(), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )

    op.add_column('scenes', sa.Column('conditions_json', sa.Text(), nullable=False, server_default='[]'))
    op.add_column('scenes', sa.Column('tags_json', sa.Text(), nullable=False, server_default='[]'))
    for table in ['scene_pains', 'scene_goals']:
        op.create_table(
            table,
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('scene_id', sa.Integer(), sa.ForeignKey('scenes.id', ondelete='CASCADE'), nullable=False),
            sa.Column('title', sa.String(160), nullable=False),
            sa.Column('description', sa.Text(), nullable=False, server_default=''),
            sa.Column('icon', sa.String(80), nullable=False, server_default=''),
            sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
            *timestamps(),
        )
    op.create_table(
        'scene_process_steps',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('scene_id', sa.Integer(), sa.ForeignKey('scenes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('node_title', sa.String(160), nullable=False),
        sa.Column('node_description', sa.Text(), nullable=False, server_default=''),
        sa.Column('icon', sa.String(80), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )

    op.create_table(
        'solution_architecture_nodes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('solution_id', sa.Integer(), sa.ForeignKey('solutions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('layer', sa.String(100), nullable=False),
        sa.Column('name', sa.String(160), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('relation_type', sa.String(48), nullable=False, server_default=''),
        sa.Column('relation_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )
    op.create_table(
        'solution_capability_coverage',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('solution_id', sa.Integer(), sa.ForeignKey('solutions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('capability_name', sa.String(160), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='COVERED'),
        sa.Column('implementation', sa.Text(), nullable=False, server_default=''),
        sa.Column('relation_objects_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *timestamps(),
    )

    op.add_column('knowledge_relations', sa.Column('relation_type', sa.String(48), nullable=False, server_default='RELATED'))
    op.drop_constraint('uq_knowledge_relation', 'knowledge_relations', type_='unique')
    op.create_unique_constraint('uq_knowledge_relation', 'knowledge_relations', ['source_type', 'source_id', 'target_type', 'target_id', 'relation_type'])
    op.create_index('uq_product_primary_software_commercialization', 'knowledge_relations', ['source_id'], unique=True, postgresql_where=sa.text("source_type='products' AND target_type='software' AND relation_type='COMMERCIALIZATION'"))
    op.create_index('uq_software_primary_product_commercialization', 'knowledge_relations', ['target_id'], unique=True, postgresql_where=sa.text("source_type='products' AND target_type='software' AND relation_type='COMMERCIALIZATION'"))
    op.add_column('product_prices', sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True))
    # Preserve the newest row if an older installation accumulated duplicate prices.
    op.execute(sa.text("""DELETE FROM product_prices older USING product_prices newer
        WHERE older.product_id = newer.product_id
          AND (older.updated_at, older.id) < (newer.updated_at, newer.id)"""))
    op.create_unique_constraint('uq_product_prices_product_id', 'product_prices', ['product_id'])

    conn = op.get_bind()
    for product_id, raw in conn.execute(sa.text('SELECT id, dynamic_fields_json FROM products')):
        for order, (name, value) in enumerate(load_json(raw, {}).items()):
            conn.execute(sa.text("""INSERT INTO product_parameters
                (product_id,name,value,unit,group_name,highlight,data_type,sort_order,created_at,updated_at)
                VALUES (:product_id,:name,:value,'','基础参数',:highlight,'TEXT',:sort_order,now(),now())"""),
                {'product_id': product_id, 'name': str(name), 'value': str(value), 'highlight': order < 4, 'sort_order': order})
    conn.execute(sa.text("""INSERT INTO software_versions (software_id,version,summary,created_at,updated_at)
        SELECT id,version,'当前正式版本',now(),now() FROM software"""))
    for algorithm_id, raw in conn.execute(sa.text('SELECT id, metrics_json FROM algorithms')):
        for order, (name, value) in enumerate(load_json(raw, {}).items()):
            conn.execute(sa.text("""INSERT INTO algorithm_metrics
                (algorithm_id,name,value,group_name,highlight,sort_order,created_at,updated_at)
                VALUES (:parent,:name,:value,'性能指标',:highlight,:sort_order,now(),now())"""),
                {'parent': algorithm_id, 'name': str(name), 'value': str(value), 'highlight': order < 4, 'sort_order': order})
    for capability_id, raw, inputs in conn.execute(sa.text('SELECT id, metrics_json, input_requirements_json FROM capabilities')):
        for order, (name, value) in enumerate(load_json(raw, {}).items()):
            conn.execute(sa.text("""INSERT INTO model_metrics
                (capability_id,name,value,group_name,highlight,sort_order,created_at,updated_at)
                VALUES (:parent,:name,:value,'性能指标',:highlight,:sort_order,now(),now())"""),
                {'parent': capability_id, 'name': str(name), 'value': str(value), 'highlight': order < 4, 'sort_order': order})
        for order, (name, value) in enumerate(load_json(inputs, {}).items()):
            conn.execute(sa.text("""INSERT INTO model_input_definitions
                (capability_id,name,data_type,required,description,sort_order,created_at,updated_at)
                VALUES (:parent,:name,'string',true,:description,:sort_order,now(),now())"""),
                {'parent': capability_id, 'name': str(name), 'description': str(value), 'sort_order': order})
    for scene_id, pains, goals, process in conn.execute(sa.text('SELECT id,pain_points,goals_json,process_json FROM scenes')):
        if pains:
            conn.execute(sa.text("""INSERT INTO scene_pains
                (scene_id,title,description,sort_order,created_at,updated_at)
                VALUES (:parent,:title,:description,0,now(),now())"""),
                {'parent': scene_id, 'title': str(pains)[:160], 'description': str(pains)})
        for order, value in enumerate(load_json(goals, [])):
            conn.execute(sa.text("""INSERT INTO scene_goals
                (scene_id,title,sort_order,created_at,updated_at)
                VALUES (:parent,:title,:sort_order,now(),now())"""),
                {'parent': scene_id, 'title': str(value)[:160], 'sort_order': order})
        for order, value in enumerate(load_json(process, [])):
            conn.execute(sa.text("""INSERT INTO scene_process_steps
                (scene_id,node_title,sort_order,created_at,updated_at)
                VALUES (:parent,:title,:sort_order,now(),now())"""),
                {'parent': scene_id, 'title': str(value)[:160], 'sort_order': order})


def downgrade():
    op.drop_constraint('uq_product_prices_product_id', 'product_prices', type_='unique')
    op.drop_column('product_prices', 'valid_from')
    op.drop_index('uq_software_primary_product_commercialization', table_name='knowledge_relations')
    op.drop_index('uq_product_primary_software_commercialization', table_name='knowledge_relations')
    op.drop_constraint('uq_knowledge_relation', 'knowledge_relations', type_='unique')
    # The legacy schema cannot represent multiple relation types for one object pair.
    op.execute(sa.text("""
        DELETE FROM knowledge_relations AS relation
        USING (
            SELECT id
            FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY source_type, source_id, target_type, target_id
                    ORDER BY
                        CASE relation_type
                            WHEN 'COMMERCIALIZATION' THEN 0
                            WHEN 'CORE' THEN 1
                            WHEN 'REQUIRED' THEN 2
                            WHEN 'RECOMMENDED' THEN 3
                            WHEN 'SUPPORT' THEN 4
                            ELSE 5
                        END,
                        id
                ) AS row_number
                FROM knowledge_relations
            ) AS ranked
            WHERE row_number > 1
        ) AS duplicate
        WHERE relation.id = duplicate.id
    """))
    op.create_unique_constraint('uq_knowledge_relation', 'knowledge_relations', ['source_type', 'source_id', 'target_type', 'target_id'])
    op.drop_column('knowledge_relations', 'relation_type')
    for table in ['solution_capability_coverage','solution_architecture_nodes','scene_process_steps','scene_goals','scene_pains','model_output_definitions','model_input_definitions','model_metrics','algorithm_metrics','algorithm_parameters','software_media','software_versions','software_features','software_modules','product_features','product_media','product_parameters']:
        op.drop_table(table)
    for column in ['tags_json', 'conditions_json']:
        op.drop_column('scenes', column)
    for column in ['use_conditions_json', 'task_type', 'model_type']:
        op.drop_column('capabilities', column)
    op.drop_column('algorithms', 'principle')
    for column in ['detail_description', 'logo', 'boundaries_json', 'protocols_json', 'database_json']:
        op.drop_column('software', column)
    op.drop_constraint('uq_products_product_code', 'products', type_='unique')
    for column in ['boundaries_json', 'tags_json', 'description', 'current_version', 'product_series', 'product_code']:
        op.drop_column('products', column)
