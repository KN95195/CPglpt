"""Live product-center acceptance against an explicitly supplied base URL."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = os.environ.get("HAIZHI_ACCEPTANCE_BASE_URL", "http://127.0.0.1:18080")


def request(path: str, *, token: str | None = None, method: str = "GET", body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
            return response.status, None if not raw else json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, None if not raw else json.loads(raw)


def login(username: str) -> str:
    password = os.environ.get("HAIZHI_ACCEPTANCE_PASSWORD_" + username.upper())
    assert password, "missing acceptance password environment variable for " + username
    status, payload = request(
        "/api/auth/login",
        method="POST",
        body={"username": username, "password": password},
    )
    assert status == 200, (username, status, payload)
    return payload["access_token"]


def main() -> int:
    admin = login("admin")
    sales = login("sales")
    suffix = str(int(time.time()))
    name = f"验收产品-{suffix}"
    model = f"HZ-ACC-{suffix}"
    created_id = None
    checks: list[str] = []
    try:
        status, products = request("/api/products", token=admin)
        assert status == 200 and products, (status, products)
        checks.append("list")

        status, created = request(
            "/api/admin/products",
            token=admin,
            method="POST",
            body={
                "name": name,
                "model_code": model,
                "category_id": 1,
                "summary": "正式验收临时数据",
                "status": "ON_SALE",
            },
        )
        assert status == 201, (status, created)
        created_id = created["id"]
        checks.append("admin_create")

        query = urllib.parse.quote(model)
        status, found = request(f"/api/products?q={query}", token=admin)
        assert status == 200 and len(found) == 1 and found[0]["id"] == created_id
        checks.append("search")

        status, detail = request(f"/api/products/{created_id}", token=admin)
        assert status == 200 and detail["modelCode"] == model
        assert isinstance(detail.get("capabilities"), list)
        checks.append("detail_relationships")

        status, updated = request(
            f"/api/admin/products/{created_id}",
            token=admin,
            method="PATCH",
            body={"summary": "正式验收临时数据-已更新"},
        )
        assert status == 200 and updated["summary"].endswith("已更新")
        checks.append("admin_update")

        status, sales_products = request("/api/products", token=sales)
        assert status == 200 and any(row["id"] == created_id for row in sales_products)
        checks.append("sales_read")

        status, _ = request("/api/prices", token=sales)
        assert status == 403
        checks.append("sales_price_denied")

        status, _ = request(
            f"/api/admin/products/{created_id}", token=admin, method="DELETE"
        )
        assert status == 204
        created_id = None
        checks.append("admin_delete")

        status, _ = request(f"/api/products?q={query}", token=admin)
        assert status == 200
        status, missing = request(f"/api/products/{updated['id']}", token=admin)
        assert status == 404, (status, missing)
        checks.append("delete_verified")
    finally:
        if created_id is not None:
            request(f"/api/admin/products/{created_id}", token=admin, method="DELETE")

    print(json.dumps({"status": "PASS", "checks": checks}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
