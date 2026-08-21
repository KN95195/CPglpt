"""Live price confidentiality, export, and audit acceptance."""

from live_catalog_acceptance import BASE, call, login
import json
import urllib.error
import urllib.request


def raw(path, token=None):
    headers = {} if not token else {"Authorization": "Bearer " + token}
    req = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()


def main():
    admin = login("admin")
    sales = login("sales")
    support = login("sales_support")
    price_admin = login("price_admin")
    checks = []

    assert call("/api/prices")[0] == 401
    assert call("/api/prices", sales)[0] == 403
    checks += ["unauthenticated_denied", "sales_denied"]

    status, rows = call("/api/prices", support)
    assert status == 200 and rows and all(row["costPrice"] is None for row in rows)
    assert raw("/api/prices/export", support)[0] == 403
    checks += ["support_reference_only", "support_export_denied"]

    status, rows = call("/api/prices", price_admin)
    assert status == 200 and all(row["costPrice"] is not None for row in rows)
    export_status, headers, payload = raw("/api/prices/export", price_admin)
    text = payload.decode("utf-8-sig")
    assert export_status == 200 and "text/csv" in headers.get("Content-Type", "")
    assert "成本价" in text and "参考报价" in text and len(text.splitlines()) == len(rows) + 1
    checks += ["price_admin_cost_view", "protected_csv_export"]

    status, admin_rows = call("/api/prices", admin)
    assert status == 200 and all(row["costPrice"] is not None for row in admin_rows)
    status, logs = call("/api/admin/price-access-logs?limit=50", admin)
    assert status == 200
    assert any(row["username"] == "sales_support" and row["action"] == "VIEW" for row in logs)
    assert any(row["username"] == "price_admin" and row["action"] == "VIEW" for row in logs)
    assert any(row["username"] == "price_admin" and row["action"] == "EXPORT" for row in logs)
    assert any(row["username"] == "admin" and row["action"] == "VIEW" for row in logs)
    checks += ["admin_cost_view", "view_export_audited"]
    print(json.dumps({"status": "PASS", "checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
