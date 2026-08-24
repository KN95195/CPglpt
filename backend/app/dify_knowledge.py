import json
import time
from dataclasses import dataclass

import httpx

from .config import settings


class DifyKnowledgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class DifySyncResult:
    dataset_id: str
    document_id: str
    batch: str


class DifyKnowledgeClient:
    def __init__(self, transport=None):
        self.base_url = settings.dify_api_base_url.rstrip('/')
        self.api_key = settings.dify_dataset_api_key
        self.dataset_id = settings.dify_knowledge_dataset_id
        self.indexing_technique = settings.dify_knowledge_indexing_technique
        self.timeout_seconds = settings.dify_knowledge_timeout_seconds
        self.transport = transport

    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.dataset_id)

    def sync_file(self, *, file_name: str, mime_type: str, content: bytes,
                  existing_document_id: str = '') -> DifySyncResult:
        if not self.configured():
            raise DifyKnowledgeError('Dify Knowledge integration is not configured')
        headers = {'Authorization': f'Bearer {self.api_key}'}
        process = {
            'indexing_technique': self.indexing_technique,
            'process_rule': {'mode': 'automatic'},
        }
        if existing_document_id:
            path = f'/datasets/{self.dataset_id}/documents/{existing_document_id}/update-by-file'
        else:
            path = f'/datasets/{self.dataset_id}/document/create-by-file'
        with httpx.Client(base_url=self.base_url, headers=headers,
                          timeout=self.timeout_seconds, transport=self.transport) as client:
            response = client.post(
                path,
                data={'data': json.dumps(process, ensure_ascii=False)},
                files={'file': (file_name, content, mime_type or 'application/octet-stream')},
            )
            self._raise_for_status(response)
            payload = response.json()
            document = payload.get('document') or payload.get('data') or payload
            document_id = str(document.get('id') or existing_document_id)
            batch = str(payload.get('batch') or '')
            if not document_id:
                raise DifyKnowledgeError('Dify did not return a document id')
            if batch:
                self._wait_until_indexed(client, batch)
        return DifySyncResult(self.dataset_id, document_id, batch)

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.configured():
            raise DifyKnowledgeError('Dify Knowledge integration is not configured')
        headers = {'Authorization': f'Bearer {self.api_key}'}
        payload = {
            'query': query,
            'retrieval_model': {
                'search_method': 'keyword_search',
                'reranking_enable': False,
                'top_k': max(1, min(top_k, 10)),
                'score_threshold_enabled': False,
            },
        }
        async with httpx.AsyncClient(base_url=self.base_url, headers=headers,
                                     timeout=self.timeout_seconds,
                                     transport=self.transport) as client:
            response = await client.post(f'/datasets/{self.dataset_id}/retrieve', json=payload)
            self._raise_for_status(response)
        records = []
        for row in response.json().get('records') or []:
            segment = row.get('segment') or {}
            document = segment.get('document') or row.get('document') or {}
            records.append({
                'content': str(segment.get('content') or ''),
                'score': row.get('score'),
                'segmentId': str(segment.get('id') or ''),
                'documentId': str(
                    segment.get('document_id') or document.get('id') or row.get('document_id') or ''
                ),
                'documentName': str(document.get('name') or segment.get('document_name') or ''),
            })
        return records

    def _wait_until_indexed(self, client: httpx.Client, batch: str) -> None:
        deadline = time.monotonic() + self.timeout_seconds
        path = f'/datasets/{self.dataset_id}/documents/{batch}/indexing-status'
        while time.monotonic() < deadline:
            response = client.get(path)
            self._raise_for_status(response)
            rows = response.json().get('data') or []
            statuses = {str(row.get('indexing_status') or '').lower() for row in rows}
            if rows and statuses <= {'completed'}:
                return
            failed = statuses & {'error', 'failed', 'stopped'}
            if failed:
                message = next((row.get('error') for row in rows if row.get('error')), '')
                raise DifyKnowledgeError(f'Dify indexing failed: {message or sorted(failed)[0]}')
            time.sleep(1)
        raise DifyKnowledgeError('Dify indexing timed out')

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            payload = response.json()
            detail = payload.get('message') or payload.get('error') or payload.get('code')
        except Exception:
            detail = response.text[:300]
        raise DifyKnowledgeError(f'Dify API returned HTTP {response.status_code}: {detail or "unknown error"}')
