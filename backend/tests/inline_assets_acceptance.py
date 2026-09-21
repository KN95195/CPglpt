import json
import os
import urllib.error
import urllib.request
import uuid

BASE = os.getenv('HAIZHI_ACCEPTANCE_BASE_URL', 'http://127.0.0.1:18087').rstrip('/')


def request(method, path, token=None, body=None, content_type='application/json', expected=(200,)):
    headers = {'Content-Type': content_type}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None and content_type == 'application/json' else body
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, data=data, headers=headers, method=method), timeout=30) as response:
            status, raw, headers_out = response.status, response.read(), response.headers
    except urllib.error.HTTPError as exc:
        status, raw, headers_out = exc.code, exc.read(), exc.headers
    assert status in expected, (method, path, status, raw.decode(errors='replace'))
    return status, raw, headers_out


def login(username, password_env):
    _, raw, _ = request('POST', '/api/auth/login', body={'username': username, 'password': os.environ[password_env]})
    return json.loads(raw)


def multipart(fields, filename, content_type, content):
    boundary = '----HaiZhi' + uuid.uuid4().hex
    chunks = []
    for key, value in fields.items():
        chunks += [f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()]
    chunks += [f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\n'.encode(), content, f'\r\n--{boundary}--\r\n'.encode()]
    return b''.join(chunks), 'multipart/form-data; boundary=' + boundary


admin = login('admin', 'HAIZHI_ACCEPTANCE_PASSWORD_ADMIN')
reader = login('sales', 'HAIZHI_ACCEPTANCE_PASSWORD_SALES')
admin_token, reader_token = admin['access_token'], reader['access_token']
assert 'DOCUMENT_DOWNLOAD' in admin['user']['permissions']
assert 'DOCUMENT_DOWNLOAD' not in reader['user']['permissions']

_, products_raw, _ = request('GET', '/api/products', admin_token)
product_id = json.loads(products_raw)[0]['id']

png = b'\x89PNG\r\n\x1a\n' + b'asset-test'
body, mime = multipart({}, 'acceptance.png', 'image/png', png)
_, image_raw, _ = request('POST', '/api/media/images', admin_token, body, mime, (201,))
image = json.loads(image_raw)
try:
    _, served, image_headers = request('GET', image['url'])
    assert served == png and image_headers.get_content_type() == 'image/png'
finally:
    request('DELETE', image['url'], admin_token, expected=(204,))

body, mime = multipart({'center_type': 'products', 'center_id': str(product_id)}, 'acceptance.txt', 'text/plain', b'inline-assets-pass')
_, uploaded_raw, _ = request('POST', '/api/documents', admin_token, body, mime, (201,))
document = json.loads(uploaded_raw)
try:
    # Uploads are drafts. Publish explicitly before checking reader visibility.
    request('POST', f"/api/documents/{document['id']}/publish", admin_token)
    _, admin_list_raw, _ = request('GET', f'/api/documents?center_type=products&center_id={product_id}', admin_token)
    _, reader_list_raw, _ = request('GET', f'/api/documents?center_type=products&center_id={product_id}', reader_token)
    admin_item = next(item for item in json.loads(admin_list_raw) if item['id'] == document['id'])
    reader_item = next(item for item in json.loads(reader_list_raw) if item['id'] == document['id'])
    assert admin_item['canDownload'] is True and reader_item['canDownload'] is False
    _, preview, preview_headers = request('GET', f"/api/documents/{document['id']}/preview", reader_token)
    assert preview == b'inline-assets-pass' and preview_headers['Content-Disposition'].startswith('inline')
    request('GET', f"/api/documents/{document['id']}/download", reader_token, expected=(403,))
    _, downloaded, download_headers = request('GET', f"/api/documents/{document['id']}/download", admin_token)
    assert downloaded == b'inline-assets-pass' and download_headers['Content-Disposition'].startswith('attachment')
finally:
    request('DELETE', f"/api/documents/{document['id']}", admin_token, expected=(204,))

print({'imageUpload': True, 'genericCenterDocument': True, 'readerPreview': True, 'readerDownloadDenied': True, 'managerDownload': True, 'cleanup': True})
