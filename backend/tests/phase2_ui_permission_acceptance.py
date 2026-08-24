import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import User


BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


def token_for(username):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        assert user and user.enabled, username
        return jwt.encode(
            {"uid": user.id, "exp": datetime.now(timezone.utc) + timedelta(minutes=20)},
            settings.jwt_secret,
            algorithm="HS256",
        )


def headers(token):
    return {"Authorization": "Bearer " + token}


admin = token_for("admin")
sales = token_for("sales")
suffix = uuid.uuid4().hex[:8]
role_code = "phase2_ui_reader_" + suffix
username = "phase2_ui_reader_" + suffix
password = "Phase2-UI-Reader-2026!"
document_id = None
user_id = None

try:
    response = httpx.post(
        BASE + "/api/admin/roles",
        headers=headers(admin),
        json={
            "code": role_code,
            "name": "界面权限验收只读角色",
            "permissions": ["KNOWLEDGE_VIEW", "DOCUMENT_VIEW", "DOCUMENT_DOWNLOAD"],
        },
        timeout=30,
    )
    assert response.status_code == 201, response.text
    response = httpx.post(
        BASE + "/api/admin/users",
        headers=headers(admin),
        json={
            "username": username,
            "display_name": "界面权限验收用户",
            "password": password,
            "role_code": role_code,
        },
        timeout=30,
    )
    assert response.status_code == 201, response.text
    user_id = response.json()["id"]
    response = httpx.post(
        BASE + "/api/auth/login",
        json={"username": username, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    reader = response.json()["access_token"]

    dashboard = httpx.get(BASE + "/api/dashboard", headers=headers(reader), timeout=30)
    dashboard.raise_for_status()
    payload = dashboard.json()
    assert set(payload) >= {
        "metrics",
        "coreProducts",
        "commonScenes",
        "recentProjects",
        "recentUpdates",
        "popularCapabilities",
    }
    assert payload["coreProducts"] and payload["commonScenes"] and payload["popularCapabilities"]
    assert payload["recentProjects"] == []
    assert httpx.get(BASE + "/api/projects", headers=headers(reader), timeout=30).status_code == 403
    assert httpx.get(BASE + "/api/bom/rules", headers=headers(reader), timeout=30).status_code == 403
    assert httpx.get(BASE + "/api/admin/users", headers=headers(reader), timeout=30).status_code == 403

    sales_dashboard = httpx.get(BASE + "/api/dashboard", headers=headers(sales), timeout=30)
    sales_dashboard.raise_for_status()
    assert isinstance(sales_dashboard.json()["recentProjects"], list)

    document_bytes = "Phase 2 资料发布流程验收内容".encode("utf-8")
    response = httpx.post(
        BASE + "/api/documents",
        headers=headers(admin),
        files={"file": ("phase2-ui-acceptance.txt", document_bytes, "text/plain")},
        data={
            "category": "产品资料",
            "version": "V2.0",
            "description": "候选界面资料工作流验收",
            "applicable_models": "HZ-AI-200",
            "applicable_versions": "V2.x",
            "knowledge_enabled": "false",
        },
        timeout=30,
    )
    assert response.status_code == 201, response.text
    document_id = response.json()["id"]
    response = httpx.patch(
        BASE + f"/api/documents/{document_id}",
        headers=headers(admin),
        json={"description": "资料元数据已人工确认", "knowledge_enabled": False},
        timeout=30,
    )
    assert response.status_code == 200 and response.json()["description"] == "资料元数据已人工确认"
    response = httpx.post(
        BASE + f"/api/documents/{document_id}/publish",
        headers=headers(admin),
        timeout=30,
    )
    assert response.status_code == 200 and response.json()["status"] == "PUBLISHED"
    assert response.json()["knowledgeEnabled"] is False
    assert httpx.post(
        BASE + f"/api/documents/{document_id}/knowledge-sync",
        headers=headers(admin),
        timeout=30,
    ).status_code == 422
    preview = httpx.get(BASE + f"/api/documents/{document_id}/preview", headers=headers(reader), timeout=30)
    assert preview.status_code == 200 and preview.content == document_bytes
    download = httpx.get(BASE + f"/api/documents/{document_id}/download", headers=headers(reader), timeout=30)
    assert download.status_code == 200 and download.content == document_bytes

    frontend = httpx.get(BASE + "/", timeout=30).text
    assert "index-DYEYy9ZP.js" in frontend
    bundle = httpx.get(BASE + "/assets/index-DYEYy9ZP.js", timeout=30).text
    for marker in ["无权访问此页面", "热门模型能力", "完善资料信息", "校验通过", "必选规则"]:
        assert marker in bundle, marker

    print("PHASE2_UI_PERMISSION_DOCUMENT_ACCEPTANCE_PASS", document_id)
finally:
    if document_id:
        httpx.delete(BASE + f"/api/documents/{document_id}", headers=headers(admin), timeout=30)
    if user_id:
        httpx.delete(BASE + f"/api/admin/users/{user_id}", headers=headers(admin), timeout=30)
    httpx.delete(BASE + f"/api/admin/roles/{role_code}", headers=headers(admin), timeout=30)
