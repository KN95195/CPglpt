"""Live rule-based BOM and saved-project acceptance."""

from live_catalog_acceptance import call, login
import json
import time


def main():
    admin, sales = login("admin"), login("sales")
    checks = []
    base = {"scene": "桥梁防撞", "ptz_count": 4, "ais": True, "yaw": True, "ocr": True}
    status, first = call("/api/bom/recommend", admin, "POST", base)
    assert status == 200 and first["validation"]["status"] == "PASS"
    camera = next(row for row in first["items"] if row["model"] == "HZ-VC-700")
    assert camera["quantity"] == 4
    checks.append("rule_base")

    changed = dict(base, ptz_count=7, ais=False, overheight=True, vhf=True)
    status, second = call("/api/bom/recommend", admin, "POST", changed)
    assert status == 200
    assert next(row for row in second["items"] if row["model"] == "HZ-VC-700")["quantity"] == 7
    models = {row["model"] for row in second["items"]}
    assert "HZ-AS-900" not in models and {"HZ-OH-1200", "HZ-VHF-01"} <= models
    checks.append("rule_conditions")

    assert call("/api/bom/recommend", sales, "POST", base)[0] == 403
    assert call("/api/bom/recommend", admin, "POST", dict(base, ptz_count=-1))[0] == 422
    checks += ["bom_edit_denied", "invalid_requirement_denied"]

    status, scenes = call("/api/catalog/scenes", admin)
    scene_id = next(row["id"] for row in scenes if row["name"] == "桥梁防撞")
    project_id = None
    try:
        status, created = call(
            "/api/projects",
            admin,
            "POST",
            {
                "name": "项目验收-" + str(int(time.time())),
                "customer": "验收客户",
                "region": "华东",
                "scene_id": scene_id,
                "requirements_json": changed,
                "bom_json": second["items"],
            },
        )
        assert status == 201 and created["bomVersion"] == 1
        project_id = created["id"]
        status, rows = call("/api/projects", sales)
        assert status == 200 and any(row["id"] == project_id for row in rows)
        status, detail = call(f"/api/projects/{project_id}", sales)
        assert status == 200 and detail["scene"] == "桥梁防撞" and len(detail["bom"]) == len(second["items"])
        checks += ["project_create_list", "project_detail"]

        status, updated = call(
            f"/api/projects/{project_id}", admin, "PATCH", {"region": "华南", "bom_json": first["items"]}
        )
        assert status == 200 and updated["bomVersion"] == 2
        assert call(f"/api/projects/{project_id}", sales)[1]["region"] == "华南"
        assert call(f"/api/projects/{project_id}", sales, "PATCH", {"region": "越权"})[0] == 403
        checks += ["project_version_update", "project_edit_denied"]
    finally:
        if project_id:
            assert call(f"/api/projects/{project_id}", admin, "DELETE")[0] == 204
            assert call(f"/api/projects/{project_id}", admin)[0] == 404
    checks.append("project_delete_verified")
    print(json.dumps({"status": "PASS", "checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
