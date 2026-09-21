"""Live document storage, tender workflow, and RBAC acceptance."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
import uuid

from live_catalog_acceptance import BASE, call, login


def multipart(path, token, fields, filename, payload, content_type="text/plain"):
    boundary = "----haizhi-" + uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        if value is None:
            continue
        chunks.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        )
    chunks += [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode(),
        payload,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    request = urllib.request.Request(
        BASE + path,
        data=b"".join(chunks),
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "multipart/form-data; boundary=" + boundary,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read()
            return response.status, None if not raw else json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, None if not raw else json.loads(raw)


def download(document_id, token):
    request = urllib.request.Request(
        f"{BASE}/api/documents/{document_id}/download",
        headers={"Authorization": "Bearer " + token},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()


def main():
    admin = login("admin")
    sales = login("sales")
    price_admin = login("price_admin")
    suffix = str(int(time.time()))
    tender_id = None
    document_id = None
    checks = []
    try:
        status, products = call("/api/products", admin)
        assert status == 200 and products
        status, scenes = call("/api/catalog/scenes", admin)
        assert status == 200 and scenes

        status, tender = call(
            "/api/tenders",
            admin,
            "POST",
            {
                "name": "tender-acceptance-" + suffix,
                "customer": "acceptance-customer",
                "status": "PREPARING",
                "summary": "document tender acceptance",
            },
        )
        assert status == 201, (status, tender)
        tender_id = tender["id"]
        assert call("/api/tenders", price_admin)[0] == 403
        assert call(f"/api/tenders/{tender_id}", admin)[0] == 200
        checks += ["tender_create_detail", "tender_view_denied"]

        content = ("海智产品中心 document acceptance " + suffix).encode("utf-8")
        status, document = multipart(
            "/api/documents",
            admin,
            {
                "product_id": products[0]["id"],
                "scene_id": scenes[0]["id"],
                "tender_id": tender_id,
            },
            "acceptance.txt",
            content,
        )
        assert status == 201, (status, document)
        document_id = document["id"]
        assert document["productId"] == products[0]["id"]
        assert document["sceneId"] == scenes[0]["id"]
        assert document["tenderId"] == tender_id
        status, published = call(f"/api/documents/{document_id}/publish", admin, "POST")
        assert status == 200 and published["status"] == "PUBLISHED", (status, published)
        status, rows = call("/api/documents", sales)
        assert status == 200 and any(row["id"] == document_id for row in rows)
        status, headers, downloaded = download(document_id, sales)
        assert status == 403
        status, headers, downloaded = download(document_id, admin)
        assert status == 200 and downloaded == content
        assert "attachment" in headers.get("Content-Disposition", "")
        checks += ["document_associations", "reader_download_denied", "manager_download"]

        assert multipart("/api/documents", price_admin, {}, "denied.txt", b"denied")[0] == 403
        assert call(f"/api/documents/{document_id}", price_admin, "DELETE")[0] == 403
        assert multipart("/api/documents", admin, {}, "empty.txt", b"")[0] == 413
        assert multipart("/api/documents", admin, {"product_id": 2147483647}, "invalid.txt", b"invalid")[0] == 422
        assert multipart("/api/documents", admin, {}, "oversized.bin", b"x" * (50 * 1024 * 1024 + 1))[0] == 413
        checks += ["document_edit_denied", "empty_rejected", "invalid_relation_rejected", "oversized_rejected"]

        status, detail = call(f"/api/tenders/{tender_id}", admin)
        assert status == 200 and any(row["id"] == document_id for row in detail["documents"])
        status, updated = call(
            f"/api/tenders/{tender_id}", admin, "PATCH", {"status": "SUBMITTED", "summary": "updated"}
        )
        assert status == 200 and updated["status"] == "SUBMITTED"
        checks += ["tender_document_relationship", "tender_update"]

        assert call(f"/api/documents/{document_id}", admin, "DELETE")[0] == 204
        assert download(document_id, admin)[0] == 404
        assert call(f"/api/documents/{document_id}", admin, "DELETE")[0] == 404
        document_id = None
        checks += ["document_delete", "post_delete_not_found"]

        assert call(f"/api/tenders/{tender_id}", admin, "DELETE")[0] == 204
        assert call(f"/api/tenders/{tender_id}", admin)[0] == 404
        tender_id = None
        checks += ["tender_delete", "cleanup_verified"]
    finally:
        if document_id is not None:
            call(f"/api/documents/{document_id}", admin, "DELETE")
        if tender_id is not None:
            call(f"/api/tenders/{tender_id}", admin, "DELETE")
    print(json.dumps({"status": "PASS", "checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
