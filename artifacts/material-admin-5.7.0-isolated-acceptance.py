import json
import os
import urllib.error
import urllib.request


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


def login(username, password):
    result = request("/api/auth/login", "POST", body={"username": username, "password": password})
    return result["access_token"], result["user"]


admin_password = os.environ.get("ACCEPTANCE_ADMIN_PASSWORD") or json.loads(os.environ.get("BOOTSTRAP_PASSWORDS_JSON", "{}"))["admin"]
suffix = os.environ.get("ACCEPTANCE_SUFFIX", "570")
admin_token, admin_user = login("admin", admin_password)
assert "USER_MANAGE" in admin_user["permissions"]
permissions = request("/api/admin/permissions", token=admin_token)
assert {"KNOWLEDGE_VIEW", "KNOWLEDGE_MANAGE", "PRICE_VIEW", "USER_MANAGE"} <= {row["code"] for row in permissions}
request("/api/admin/users", token=admin_token)
request("/api/admin/roles", token=admin_token)
directory = request("/api/admin/directory/status", token=admin_token)
assert directory["configured"] is False
request("/api/admin/directory/sync", "POST", token=admin_token, expected=503)

role_code = f"acceptance_price_viewer_{suffix}"
username = f"acceptance_price_{suffix}"
request(
    "/api/admin/roles",
    "POST",
    token=admin_token,
    body={"code": role_code, "name": "隔离价格验收角色", "permissions": ["KNOWLEDGE_VIEW", "PRICE_VIEW"]},
    expected=201,
)
created_user = request(
    "/api/admin/users",
    "POST",
    token=admin_token,
    body={
        "username": username,
        "display_name": "隔离价格验收用户",
        "password": "Acceptance570!",
        "role_code": role_code,
        "email": "",
        "department": "验收",
        "enabled": True,
    },
    expected=201,
)
user_token, _ = login(username, "Acceptance570!")
products = request("/api/products", token=user_token)
priced_detail = next(
    detail
    for detail in (request(f"/api/products/{row['id']}", token=user_token) for row in products)
    if detail.get("variants")
)
product_id = priced_detail["id"]
assert priced_detail["variants"]
assert all("agentPrice" in row and "salePrice" in row for row in priced_detail["variants"])
request(
    f"/api/admin/roles/{role_code}",
    "PATCH",
    token=admin_token,
    body={"permissions": ["KNOWLEDGE_VIEW"]},
)
hidden_detail = request(f"/api/products/{product_id}", token=user_token)
assert all("agentPrice" not in row and "salePrice" not in row for row in hidden_detail["variants"])
request(f"/api/products/{product_id}/prices", token=user_token, expected=403)
request("/api/admin/users", token=user_token, expected=403)
request(
    f"/api/admin/users/{created_user['id']}",
    "PATCH",
    token=admin_token,
    body={"display_name": "隔离价格验收用户（已更新）"},
)
listed = request(f"/api/admin/users?q={username}", token=admin_token)
assert len(listed) == 1 and listed[0]["displayName"].endswith("（已更新）")
request(f"/api/admin/users/{created_user['id']}", "DELETE", token=admin_token, expected=204)
request(f"/api/admin/roles/{role_code}", "DELETE", token=admin_token, expected=204)
print("MATERIAL_ADMIN_ISOLATED_ACCEPTANCE_PASS")
