from io import BytesIO
from minio import Minio
from minio.error import S3Error
from .config import settings


class ObjectStorage:
    def __init__(self):
        endpoint = (settings.storage_endpoint or 'minio:9000').replace('http://', '').replace('https://', '')
        self.client = Minio(endpoint, access_key=settings.storage_access_key,
                             secret_key=settings.storage_secret_key,
                             secure=settings.storage_secure)
        self.bucket = settings.storage_bucket

    def ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put(self, object_name: str, data: bytes, content_type: str):
        self.ensure_bucket()
        self.client.put_object(self.bucket, object_name, BytesIO(data), len(data), content_type=content_type)
        return f'{self.bucket}/{object_name}'

    def get(self, object_name: str):
        return self.client.get_object(self.bucket, object_name)

    def delete(self, object_name: str):
        self.client.remove_object(self.bucket, object_name)


storage = ObjectStorage()
