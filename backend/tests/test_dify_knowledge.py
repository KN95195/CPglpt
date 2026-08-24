import asyncio
import json
import unittest

import httpx

from app.config import settings
from app.dify_knowledge import DifyKnowledgeClient, DifyKnowledgeError


class DifyKnowledgeClientTest(unittest.TestCase):
    def setUp(self):
        self.original = (
            settings.dify_api_base_url,
            settings.dify_dataset_api_key,
            settings.dify_knowledge_dataset_id,
            settings.dify_knowledge_timeout_seconds,
        )
        settings.dify_api_base_url = 'http://dify.test/v1'
        settings.dify_dataset_api_key = 'dataset-test-secret'
        settings.dify_knowledge_dataset_id = 'dataset-1'
        settings.dify_knowledge_timeout_seconds = 2

    def tearDown(self):
        (settings.dify_api_base_url, settings.dify_dataset_api_key,
         settings.dify_knowledge_dataset_id,
         settings.dify_knowledge_timeout_seconds) = self.original

    def test_create_file_and_wait_for_indexing(self):
        calls = []

        def handler(request: httpx.Request):
            calls.append((request.method, request.url.path, request.headers.get('authorization')))
            if request.method == 'POST':
                return httpx.Response(200, json={'document': {'id': 'document-1'}, 'batch': 'batch-1'})
            return httpx.Response(200, json={'data': [{'indexing_status': 'completed'}]})

        result = DifyKnowledgeClient(httpx.MockTransport(handler)).sync_file(
            file_name='guide.txt', mime_type='text/plain', content=b'HaiZhi knowledge')
        self.assertEqual(result.document_id, 'document-1')
        self.assertEqual(calls[0][:2], ('POST', '/v1/datasets/dataset-1/document/create-by-file'))
        self.assertEqual(calls[1][:2], ('GET', '/v1/datasets/dataset-1/documents/batch-1/indexing-status'))
        self.assertEqual(calls[0][2], 'Bearer dataset-test-secret')

    def test_update_uses_existing_document(self):
        def handler(request: httpx.Request):
            return httpx.Response(200, json={'document': {'id': 'document-1'}})

        result = DifyKnowledgeClient(httpx.MockTransport(handler)).sync_file(
            file_name='guide-v2.txt', mime_type='text/plain', content=b'new',
            existing_document_id='document-1')
        self.assertEqual(result.document_id, 'document-1')

    def test_api_failure_is_sanitized_without_key(self):
        def handler(request: httpx.Request):
            return httpx.Response(401, json={'message': 'unauthorized'})

        with self.assertRaisesRegex(DifyKnowledgeError, 'HTTP 401: unauthorized') as raised:
            DifyKnowledgeClient(httpx.MockTransport(handler)).sync_file(
                file_name='guide.txt', mime_type='text/plain', content=b'content')
        self.assertNotIn('dataset-test-secret', str(raised.exception))

    def test_retrieve_returns_normalized_document_records(self):
        def handler(request: httpx.Request):
            self.assertEqual(request.url.path, '/v1/datasets/dataset-1/retrieve')
            self.assertEqual(request.headers.get('authorization'), 'Bearer dataset-test-secret')
            payload = json.loads(request.content)
            self.assertEqual(payload['query'], '桥梁防撞怎么配置')
            return httpx.Response(200, json={'records': [{
                'score': 0.92,
                'segment': {
                    'id': 'segment-1',
                    'document_id': 'document-1',
                    'content': 'AIS融合、船名OCR和偏航预警。',
                    'document': {'id': 'document-1', 'name': '桥梁防撞说明书'},
                },
            }]})

        rows = asyncio.run(DifyKnowledgeClient(httpx.MockTransport(handler)).retrieve('桥梁防撞怎么配置'))
        self.assertEqual(rows[0]['documentId'], 'document-1')
        self.assertEqual(rows[0]['documentName'], '桥梁防撞说明书')
        self.assertIn('船名OCR', rows[0]['content'])


if __name__ == '__main__':
    unittest.main()
