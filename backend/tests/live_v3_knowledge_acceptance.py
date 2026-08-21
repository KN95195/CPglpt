import json
import os
import urllib.error
import urllib.request


BASE_URL = os.getenv("HAIZHI_ACCEPTANCE_BASE_URL", "http://haizhi-hub-api:8000").rstrip("/")


def request(method, path, token=None, payload=None, expected=(200,)):
    body = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE_URL + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    assert status in expected, (method, path, status, raw.decode(errors="replace"))
    return json.loads(raw) if raw else None


def login(username, password_env):
    response = request(
        "POST",
        "/api/auth/login",
        payload={"username": username, "password": os.environ[password_env]},
    )
    return response["access_token"], response["user"]


admin, admin_user = login("admin", "HAIZHI_ACCEPTANCE_PASSWORD_ADMIN")
reader, reader_user = login("sales", "HAIZHI_ACCEPTANCE_PASSWORD_SALES")
assert {"KNOWLEDGE_VIEW", "KNOWLEDGE_MANAGE", "PRICE_VIEW"}.issubset(admin_user["permissions"])
assert "KNOWLEDGE_VIEW" in reader_user["permissions"]
assert "KNOWLEDGE_MANAGE" not in reader_user["permissions"]
assert "PRICE_VIEW" not in reader_user["permissions"]

centers = ["products", "software", "algorithms", "model-capabilities", "scenes", "solutions"]
for center in centers:
    assert request("GET", f"/api/{center}", admin)
    assert request("GET", f"/api/{center}", reader)
    request("GET", f"/api/{center}", expected=(401,))

category_id = request("GET", "/api/product-categories", admin)[0]["id"]
created = {}
relation_id = None

try:
    created["products"] = request(
        "POST",
        "/api/products",
        admin,
        {
            "name": "海智验收临时终端",
            "product_type": "HARDWARE",
            "model_code": "HZ-V3-ACCEPT-01",
            "category_id": category_id,
            "summary": "用于验证六大知识中心闭环，验收结束后自动清理",
            "status": "ON_SALE",
            "main_image": "",
        },
        (201,),
    )["id"]
    request(
        "POST",
        "/api/products",
        reader,
        {"name": "无权限创建", "model_code": "DENIED", "category_id": category_id},
        (403,),
    )

    catalog_payloads = {
        "software": {"name": "海智验收临时软件", "code": "SW-V3-ACCEPT", "summary": "软件中心写接口验收"},
        "algorithms": {"name": "海智验收临时算法", "code": "ALG-V3-ACCEPT", "summary": "算法中心写接口验收"},
        "model-capabilities": {"name": "海智验收临时能力", "code": "CAP-V3-ACCEPT", "summary": "模型能力中心写接口验收"},
        "scenes": {"name": "海智验收临时场景", "category": "水域安全", "summary": "场景中心写接口验收"},
    }
    for center, payload in catalog_payloads.items():
        created[center] = request("POST", f"/api/{center}", admin, payload, (201,))["id"]
        request("POST", f"/api/{center}", reader, payload | {"name": "无权限创建"}, (403,))

    created["solutions"] = request(
        "POST",
        "/api/solutions",
        admin,
        {
            "name": "海智验收临时方案",
            "code": "SOL-V3-ACCEPT",
            "scene_id": created["scenes"],
            "summary": "方案中心与标准BOM写接口验收",
        },
        (201,),
    )["id"]

    for center, entity_id in created.items():
        updated_name = f"海智验收临时{center}已更新"
        request("PATCH", f"/api/{center}/{entity_id}", admin, {"name": updated_name})
        detail = request("GET", f"/api/{center}/{entity_id}", admin)
        assert detail["name"] == updated_name
        request("PATCH", f"/api/{center}/{entity_id}", reader, {"name": "无权限更新"}, (403,))

    request(
        "PATCH",
        f"/api/products/{created['products']}/prices",
        admin,
        {"reference_price": 125000, "currency": "CNY", "tax_included": True, "tax_rate": 13, "notes": "V3验收"},
    )
    priced_product = request("GET", f"/api/products/{created['products']}", admin)
    reader_product = request("GET", f"/api/products/{created['products']}", reader)
    assert priced_product["price"]["referencePrice"] == 125000
    assert "price" not in reader_product
    request("GET", f"/api/products/{created['products']}/prices", reader, expected=(403,))

    relation_id = request(
        "POST",
        "/api/relations",
        admin,
        {
            "source_type": "products",
            "source_id": created["products"],
            "target_type": "model-capabilities",
            "target_id": created["model-capabilities"],
            "metadata": {"version": "v1.0", "recommendedConcurrency": 8, "supportStatus": "SUPPORTED"},
        },
        (201,),
    )["id"]
    product_relations = request("GET", f"/api/products/{created['products']}", admin)["relations"]
    capability_relations = request("GET", f"/api/model-capabilities/{created['model-capabilities']}", admin)["relations"]
    assert any(row["type"] == "model-capabilities" and row["id"] == created["model-capabilities"] for row in product_relations)
    assert any(row["type"] == "products" and row["id"] == created["products"] for row in capability_relations)
    request(
        "POST",
        "/api/relations",
        reader,
        {"source_type": "products", "source_id": created["products"], "target_type": "software", "target_id": created["software"]},
        (403,),
    )

    bom_payload = {
        "items": [
            {
                "product_id": created["products"],
                "quantity": 2,
                "unit": "台",
                "purpose": "验收闭环",
                "requirement_level": "REQUIRED",
                "recommendation_reason": "验证真实产品与价格权限",
            }
        ]
    }
    request("PATCH", f"/api/solutions/{created['solutions']}/bom", admin, bom_payload)
    priced_bom = request("GET", f"/api/solutions/{created['solutions']}/bom", admin)
    reader_bom = request("GET", f"/api/solutions/{created['solutions']}/bom", reader)
    assert priced_bom["total"] == 250000
    assert priced_bom["items"][0]["subtotal"] == 250000
    assert "total" not in reader_bom and "currency" not in reader_bom
    assert all("unitPrice" not in row and "subtotal" not in row for row in reader_bom["items"])
    request("PATCH", f"/api/solutions/{created['solutions']}/bom", reader, bom_payload, (403,))

    request("DELETE", f"/api/relations/{relation_id}", admin, expected=(204,))
    relation_id = None
finally:
    if relation_id:
        request("DELETE", f"/api/relations/{relation_id}", admin, expected=(204, 404))
    for center in ["solutions", "scenes", "model-capabilities", "algorithms", "software", "products"]:
        if center in created:
            request("DELETE", f"/api/{center}/{created[center]}", admin, expected=(204, 404))

print(
    {
        "centers": 6,
        "ordinaryUserReadOnly": True,
        "knowledgeManagerCrud": True,
        "priceViewOmission": True,
        "bidirectionalRelation": True,
        "solutionBom": True,
        "cleanup": True,
    }
)
