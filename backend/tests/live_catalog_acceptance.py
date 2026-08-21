"""Live catalog knowledge and permission acceptance."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


BASE = os.environ.get("HAIZHI_ACCEPTANCE_BASE_URL", "http://127.0.0.1:8000")


def call(path, token=None, method="GET", body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        BASE + path,
        data=None if body is None else json.dumps(body).encode(),
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
            return response.status, None if not raw else json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, None if not raw else json.loads(raw)


def login(username):
    password = os.environ.get("HAIZHI_ACCEPTANCE_PASSWORD_" + username.upper())
    assert password, "missing acceptance password environment variable for " + username
    status, data = call(
        "/api/auth/login",
        method="POST",
        body={"username": username, "password": password},
    )
    assert status == 200, (username, status, data)
    return data["access_token"]


def main():
    admin, sales, price_admin = map(login, ("admin", "sales", "price_admin"))
    kinds = ("software", "algorithms", "capabilities", "scenes", "solutions")
    checks = []
    for kind in kinds:
        status, rows = call("/api/catalog/" + kind, sales)
        assert status == 200 and rows, (kind, status, rows)
        checks.append(kind + "_sales_view")
        assert call("/api/catalog/" + kind)[0] == 401
        assert call("/api/catalog/" + kind, price_admin)[0] == 403
    checks += ["unauthenticated_denied", "entity_permission_denied"]

    suffix = str(int(time.time()))
    created = []
    scene_id = None
    try:
        for kind in ("software", "algorithms", "capabilities", "scenes"):
            payload = {
                "name": f"{kind}-acceptance-{suffix}",
                "summary": "catalog acceptance",
                "version": "v9.9",
                "category": "acceptance",
                "status": "SUPPORTED",
            }
            status, row = call("/api/admin/catalog/" + kind, admin, "POST", payload)
            assert status == 201, (kind, status, row)
            created.append((kind, row["id"]))
            if kind == "scenes":
                scene_id = row["id"]
            status, updated = call(
                f"/api/admin/catalog/{kind}/{row['id']}",
                admin,
                "PATCH",
                {"summary": "catalog acceptance updated"},
            )
            assert status == 200, (kind, status, updated)

        status, solution = call(
            "/api/admin/catalog/solutions",
            admin,
            "POST",
            {
                "name": f"solution-acceptance-{suffix}",
                "summary": "catalog acceptance",
                "scene_id": scene_id,
                "tier": "验收型",
            },
        )
        assert status == 201, (status, solution)
        created.append(("solutions", solution["id"]))
        status, solutions = call("/api/catalog/solutions", admin)
        match = next((row for row in solutions if row["id"] == solution["id"]), None)
        assert match is not None, (solution, [row["id"] for row in solutions])
        assert status == 200 and match["sceneId"] == scene_id and match["scene"]
        status, scene_detail = call(f"/api/scenes/{scene_id}", sales)
        assert status == 200 and any(row["id"] == solution["id"] for row in scene_detail["solutions"])
        checks += ["admin_crud", "solution_scene_relationship", "scene_detail_relationship"]
    finally:
        for kind, rid in reversed(created):
            status, data = call(f"/api/admin/catalog/{kind}/{rid}", admin, "DELETE")
            assert status == 204, (kind, rid, status, data)
    checks.append("delete_verified")
    print(json.dumps({"status": "PASS", "checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
