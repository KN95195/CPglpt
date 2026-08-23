import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from sqlalchemy import delete, select

from app.database import SessionLocal
from app.models import DirectorySyncCandidate, DirectorySyncRun, Role, User


BASE = "http://127.0.0.1:8000"


def request(path, method="GET", token=None, body=None, expected=200):
    payload = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
    assert status == expected, (path, status, raw.decode(errors="replace"))
    return json.loads(raw) if raw else None


password = os.environ.get("ACCEPTANCE_ADMIN_PASSWORD") or json.loads(os.environ["BOOTSTRAP_PASSWORDS_JSON"])["admin"]
login = request("/api/auth/login", "POST", body={"username": "admin", "password": password})
token = login["access_token"]
roles = request("/api/admin/roles", token=token)
assert all(not re.search(r"[A-Za-z]", row["name"]) for row in roles), roles

suffix = str(int(time.time()))[-8:]
role_code = "role_accept_" + suffix
request("/api/admin/roles", "POST", token, {"code": role_code, "name": "English Role", "permissions": ["KNOWLEDGE_VIEW"]}, 422)
request("/api/admin/roles", "POST", token, {"code": role_code, "name": "域用户验收角色", "permissions": ["KNOWLEDGE_VIEW"]}, 201)

username = "ad_accept_" + suffix
skipped_username = "ad_skip_" + suffix
external_id = "accept-external-" + suffix
with SessionLocal() as db:
    run = DirectorySyncRun(status="PENDING_CONFIRMATION")
    db.add(run)
    db.flush()
    approved = DirectorySyncCandidate(run_id=run.id, external_id=external_id, username=username, display_name="域用户验收", email="accept@example.invalid", department="研发中心", distinguished_name="CN=域用户验收,OU=研发中心,DC=hilaicloud,DC=com", role_code=role_code)
    skipped = DirectorySyncCandidate(run_id=run.id, external_id="skip-external-" + suffix, username=skipped_username, display_name="未选择用户", department="业务中心", distinguished_name="CN=未选择用户,OU=业务中心,DC=hilaicloud,DC=com", role_code="sales")
    db.add_all([approved, skipped])
    db.commit()
    run_id, approved_id = run.id, approved.id

preview = request("/api/admin/directory/candidates?run_id=" + str(run_id), token=token)
assert len(preview["items"]) == 2
result = request("/api/admin/directory/confirm", "POST", token, {"run_id": run_id, "users": [{"candidate_id": approved_id, "role_code": role_code}]})
assert result == {"status": "SUCCESS", "created": 1, "updated": 0, "selected": 1}
listed = request("/api/admin/users?q=" + urllib.parse.quote(username), token=token)
assert len(listed) == 1 and listed[0]["authSource"] == "AD" and listed[0]["roleCode"] == role_code
assert request("/api/admin/users?q=" + urllib.parse.quote(skipped_username), token=token) == []

with SessionLocal() as db:
    run = DirectorySyncRun(status="PENDING_CONFIRMATION")
    db.add(run)
    db.flush()
    update = DirectorySyncCandidate(run_id=run.id, external_id=external_id, username=username, display_name="域用户验收（已更新）", department="开发中心", distinguished_name="CN=域用户验收,OU=开发中心,DC=hilaicloud,DC=com", change_type="UPDATE", role_code=role_code)
    db.add(update)
    db.commit()
    update_run_id, update_id = run.id, update.id

result = request("/api/admin/directory/confirm", "POST", token, {"run_id": update_run_id, "users": [{"candidate_id": update_id, "role_code": role_code}]})
assert result == {"status": "SUCCESS", "created": 0, "updated": 1, "selected": 1}
listed = request("/api/admin/users?q=" + urllib.parse.quote(username), token=token)
assert listed[0]["displayName"] == "域用户验收（已更新）" and listed[0]["department"] == "开发中心"

with SessionLocal() as db:
    user = db.scalar(select(User).where(User.username == username))
    if user:
        db.delete(user)
    db.execute(delete(DirectorySyncRun).where(DirectorySyncRun.id.in_([run_id, update_run_id])))
    db.commit()
request("/api/admin/roles/" + role_code, "DELETE", token=token, expected=204)
print("AD_MANUAL_APPROVAL_ACCEPTANCE_PASS")
