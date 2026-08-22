import os

from fastapi.testclient import TestClient

from app.main import app


assert os.environ.get('ALLOW_R3_DESTRUCTIVE_TEST') == '1', 'isolated test opt-in required'
assert 'haizhi_test' in os.environ.get('DATABASE_URL', ''), 'refusing non-test database'

client = TestClient(app)


def login(username, password):
    response = client.post('/api/auth/login', json={'username': username, 'password': password})
    assert response.status_code == 200, response.text
    return {'Authorization': 'Bearer ' + response.json()['access_token']}


def check(response, status=200):
    assert response.status_code == status, (response.request.method, response.request.url.path, response.status_code, response.text)
    return response.json() if response.content else None


with client:
    admin = login('admin', os.environ['R3_TEST_ADMIN_PASSWORD'])
    reader = login('sales', os.environ['R3_TEST_READER_PASSWORD'])
    centers = ['products', 'software', 'algorithms', 'model-capabilities', 'scenes', 'solutions']
    for center in centers:
        assert check(client.get('/api/' + center, headers=admin))
        assert check(client.get('/api/' + center, headers=reader))

    category_id = check(client.get('/api/product-categories', headers=admin))[0]['id']
    created = {}
    relation_id = None
    product_payload = {
        'name': '海智R3验收临时终端', 'productType': 'HARDWARE',
        'primaryModel': 'HZ-R3-AUDIT-01', 'categoryId': category_id,
        'summary': '用于隔离验证六中心闭环', 'salesStatus': 'ON_SALE', 'mainImage': '',
    }
    payloads = {
        'software': {
            'name': '海智R3验收临时软件', 'code': 'HZ-R3-SW', 'version': 'V1.0',
            'summary': '软件中心验收', 'description': '隔离验收记录',
            'modules': [{'name': '事件管理', 'features': [{'name': '事件闭环'}]}],
            'versions': [{'version': 'V1.0', 'summary': '验收版'}],
        },
        'algorithms': {
            'name': '海智R3验收临时算法', 'code': 'HZ-R3-ALG', 'version': 'V1.0',
            'summary': '算法中心验收', 'principle': '规则与特征融合',
            'inputSummary': '结构化目标', 'outputSummary': '风险事件',
            'parameters': [{'name': '时间窗口', 'value': '按场景配置'}],
            'metrics': [{'name': '准确率', 'value': '待确认', 'source': '待测试报告'}],
        },
        'model-capabilities': {
            'name': '海智R3验收临时模型', 'code': 'HZ-R3-MODEL', 'version': 'V1.0',
            'summary': '模型能力中心验收', 'modelType': 'DETECTION', 'taskType': '目标检测',
            'metrics': [{'name': '准确率', 'value': '待确认', 'source': '待测试报告'}],
            'inputDefinitions': [{'name': '业务数据', 'dataType': 'JSON', 'required': True}],
            'outputDefinitions': [{'name': '检测结果', 'dataType': 'JSON'}],
        },
        'scenes': {
            'name': '海智R3验收临时场景', 'category': '水域安全', 'summary': '场景中心验收',
            'painPoints': [{'title': '数据分散'}], 'goals': [{'title': '统一态势'}],
            'process': [{'nodeTitle': '数据采集'}, {'nodeTitle': '智能研判'}],
        },
    }
    try:
        created['products'] = check(client.post('/api/products', headers=admin, json=product_payload), 201)['id']
        check(client.post('/api/products', headers=reader, json=product_payload | {'name': '无权限产品'}), 403)
        for center, payload in payloads.items():
            created[center] = check(client.post('/api/' + center, headers=admin, json=payload), 201)['id']
            check(client.post('/api/' + center, headers=reader, json=payload | {'name': '无权限创建'}), 403)

        solution_payload = {
            'name': '海智R3验收临时方案', 'code': 'HZ-R3-SOL',
            'sceneId': created['scenes'], 'summary': '方案中心验收',
            'architecture': [{'layer': '感知层', 'name': '验收终端', 'relationType': 'products', 'relationId': created['products']}],
            'capabilityCoverage': [{'capabilityName': '目标检测', 'status': 'COVERED'}],
        }
        created['solutions'] = check(client.post('/api/solutions', headers=admin, json=solution_payload), 201)['id']
        check(client.post('/api/solutions', headers=reader, json=solution_payload | {'name': '无权限方案'}), 403)

        for center, record_id in created.items():
            changed = '海智R3验收已更新-' + center
            assert check(client.patch('/api/%s/%s' % (center, record_id), headers=admin, json={'name': changed}))['name'] == changed
            check(client.patch('/api/%s/%s' % (center, record_id), headers=reader, json={'name': '无权限更新'}), 403)

        check(client.patch('/api/products/%s/prices' % created['products'], headers=admin, json={
            'referencePrice': 125000, 'currency': 'CNY', 'taxIncluded': True, 'taxRate': 13,
        }))
        assert check(client.get('/api/products/%s' % created['products'], headers=admin))['price']['referencePrice'] == 125000
        assert 'price' not in check(client.get('/api/products/%s' % created['products'], headers=reader))
        check(client.get('/api/products/%s/prices' % created['products'], headers=reader), 403)

        relation_id = check(client.post('/api/relations', headers=admin, json={
            'sourceType': 'products', 'sourceId': created['products'],
            'targetType': 'model-capabilities', 'targetId': created['model-capabilities'],
            'relationType': 'SUPPORT',
            'metadata': {'supportVersion': 'V1.0', 'recommendedConcurrency': 4, 'maxConcurrency': 8, 'supportStatus': 'SUPPORTED'},
        }), 201)['id']
        product_relations = check(client.get('/api/products/%s' % created['products'], headers=admin))['relations']
        model_relations = check(client.get('/api/model-capabilities/%s' % created['model-capabilities'], headers=admin))['relations']
        assert any(x['id'] == created['model-capabilities'] for x in product_relations)
        assert any(x['id'] == created['products'] for x in model_relations)
        check(client.post('/api/relations', headers=reader, json={
            'sourceType': 'products', 'sourceId': created['products'],
            'targetType': 'software', 'targetId': created['software'], 'relationType': 'SUPPORT', 'metadata': {},
        }), 403)

        bom = {'items': [{'productId': created['products'], 'quantity': 2, 'unit': '台', 'purpose': '验收闭环', 'requirementLevel': 'REQUIRED'}]}
        check(client.patch('/api/solutions/%s/bom' % created['solutions'], headers=admin, json=bom))
        priced_bom = check(client.get('/api/solutions/%s/bom' % created['solutions'], headers=admin))
        reader_bom = check(client.get('/api/solutions/%s/bom' % created['solutions'], headers=reader))
        assert priced_bom['productReferenceTotal'] == 250000
        assert 'productReferenceTotal' not in reader_bom and 'total' not in reader_bom
        assert all('unitPrice' not in row and 'subtotal' not in row for row in reader_bom['items'])

        check(client.delete('/api/relations/%s' % relation_id, headers=admin), 204)
        relation_id = None
    finally:
        if relation_id:
            check(client.delete('/api/relations/%s' % relation_id, headers=admin), 204)
        for center in ['solutions', 'scenes', 'model-capabilities', 'algorithms', 'software', 'products']:
            if center in created:
                check(client.delete('/api/%s/%s' % (center, created[center]), headers=admin), 204)

print('R3_ISOLATED_API_ACCEPTANCE_PASS')
