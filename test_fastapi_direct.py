"""
FastAPI Migration - Direct Verification using TestClient.
No running server needed - tests the app directly.
"""

import sys
import json
import os
import time
from datetime import datetime
from fastapi.testclient import TestClient

# Set test environment
os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-purposes-only"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-purposes-only"

# Import the FastAPI app
from app_fastapi import app
from database import init_db, get_db

client = TestClient(app)

# Initialize DB
init_db()

TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "testpass123"
TEST_USERNAME = f"testuser_{int(time.time())}"

results = []


def test(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append({"test": name, "status": status, "detail": detail})
    print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))


def run_verification():
    print("=" * 70)
    print("STUDY MATERIAL HUB - FLASK TO FASTAPI MIGRATION VERIFICATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # ── 1. Health Endpoint ──
    print("\n[1] HEALTH ENDPOINT")
    r = client.get("/health")
    test("Health endpoint status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Health response has status", "status" in data)
    test("Health response has database", "database" in data)
    test("Health database connected", data.get("database") == "connected",
         f"DB status: {data.get('database')}")

    # ── 2. Swagger UI / OpenAPI ──
    print("\n[2] SWAGGER UI & OPENAPI")
    r = client.get("/docs")
    test("Swagger UI /docs", r.status_code == 200, f"Got {r.status_code}")

    r = client.get("/openapi.json")
    test("OpenAPI schema /openapi.json", r.status_code == 200, f"Got {r.status_code}")
    schema = r.json()
    test("OpenAPI has info.title", "title" in schema.get("info", {}))
    test("OpenAPI has paths", "paths" in schema)

    # ── 3. Stats Endpoint ──
    print("\n[3] STATS ENDPOINT")
    r = client.get("/stats")
    test("Stats endpoint status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Stats has total_users", "total_users" in data)
    test("Stats has total_materials", "total_materials" in data)
    test("Stats has total_views", "total_views" in data)

    # ── 4. HTML Pages ──
    print("\n[4] HTML PAGES (Legacy Support)")
    r = client.get("/")
    test("Home page (/)", r.status_code == 200, f"Got {r.status_code}")
    test("Home page is HTML", "text/html" in r.headers.get("content-type", ""))

    r = client.get("/register")
    test("Register page (/register) GET", r.status_code == 200, f"Got {r.status_code}")

    r = client.get("/dashboard")
    test("Dashboard page (/dashboard)", r.status_code == 200, f"Got {r.status_code}")

    # ── 5. Registration ──
    print("\n[5] REGISTRATION")
    token = None
    r = client.post("/api/register", json={
        "username": TEST_USERNAME, "email": TEST_EMAIL, "password": TEST_PASSWORD
    })
    test("Register status code", r.status_code in [201, 200], f"Got {r.status_code}")
    data = r.json()
    test("Register returns token", "token" in data)
    test("Register returns user", "user" in data)
    if data.get("user"):
        test("Register user has id", "id" in data["user"])
        test("Register user has username", "username" in data["user"])
        test("Register user has email", "email" in data["user"])
    token = data.get("token")

    if not token:
        print("\n  ❌ Cannot continue without registration. Aborting.")
        return 0, len(results), len(results)

    # ── 6. Duplicate Registration ──
    print("\n[6] DUPLICATE REGISTRATION")
    r = client.post("/api/register", json={
        "username": TEST_USERNAME, "email": TEST_EMAIL, "password": TEST_PASSWORD
    })
    test("Duplicate register returns 409", r.status_code == 409, f"Got {r.status_code}")
    data = r.json()
    test("Duplicate error has error message", "error" in data,
         f"Error: {data.get('error', 'N/A')}")

    # ── 7. Login ──
    print("\n[7] LOGIN")
    r = client.post("/api/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    test("Login status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Login returns token", "token" in data)
    test("Login returns user", "user" in data)
    login_token = data.get("token")
    if login_token:
        test("Login token is non-empty string",
             isinstance(login_token, str) and len(login_token) > 20,
             f"Length: {len(login_token)}")

    # ── 8. Invalid Login ──
    print("\n[8] INVALID LOGIN")
    r = client.post("/api/login", json={"email": TEST_EMAIL, "password": "wrongpassword"})
    test("Invalid login returns 401", r.status_code == 401, f"Got {r.status_code}")
    data = r.json()
    test("Invalid login has error", "error" in data, f"Error: {data.get('error', 'N/A')}")

    # ── 9. JWT Protected: Profile ──
    print("\n[9] JWT - PROFILE")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/profile", headers=headers)
    test("Profile status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Profile has user", "user" in data)
    test("Profile has stats", "stats" in data)
    if data.get("stats"):
        test("Profile stats has total_materials", "total_materials" in data["stats"])
        test("Profile stats has total_views", "total_views" in data["stats"])

    # ── 10. JWT Invalid Token ──
    print("\n[10] JWT - INVALID TOKEN")
    r = client.get("/api/profile", headers={"Authorization": "Bearer invalidtoken123"})
    test("Invalid token returns 401", r.status_code == 401, f"Got {r.status_code}")
    data = r.json()
    test("Invalid token has error", "error" in data)

    # ── 11. JWT Missing Token ──
    print("\n[11] JWT - MISSING TOKEN")
    r = client.get("/api/profile")
    test("Missing token returns 401", r.status_code == 401, f"Got {r.status_code}")

    # ── 12. Create Material ──
    print("\n[12] CREATE MATERIAL")
    material_id = None
    resource_code = None
    r = client.post("/api/materials", json={
        "title": "Python OOP Notes",
        "resource_link": "https://example.com/python-oop.pdf",
        "description": "Comprehensive notes on OOP in Python",
        "subject": "Computer Science",
        "category": "Notes",
    }, headers=headers)
    test("Create material status code", r.status_code in [201, 200], f"Got {r.status_code}")
    data = r.json()
    test("Create material returns material", "material" in data)
    if data.get("material"):
        m = data["material"]
        test("Material has title", m.get("title") == "Python OOP Notes",
             f"Got: {m.get('title')}")
        test("Material has resource_code", "resource_code" in m)
        test("Material has short_url", "short_url" in m)
        test("Material has views", "views" in m)
        test("Material views starts at 0", m.get("views") == 0, f"Got: {m.get('views')}")
        material_id = m.get("id")
        resource_code = m.get("resource_code")

    # ── 13. Create Material Validation ──
    print("\n[13] CREATE MATERIAL VALIDATION")
    r = client.post("/api/materials", json={"title": "", "resource_link": ""}, headers=headers)
    test("Empty title returns 422 or 400",
         r.status_code in [422, 400], f"Got {r.status_code}")

    # ── 14. List Materials ──
    print("\n[14] LIST MATERIALS")
    r = client.get("/api/materials", headers=headers)
    test("List materials status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("List has total", "total" in data)
    test("List has materials", "materials" in data)
    test("List total > 0", data.get("total", 0) > 0, f"Total: {data.get('total', 0)}")
    test("List returns list", isinstance(data.get("materials"), list))

    # ── 15. Search ──
    print("\n[15] SEARCH")
    r = client.get("/api/materials/search?q=Python", headers=headers)
    test("Search status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Search has query", "query" in data)
    test("Search has total", "total" in data)
    test("Search has materials", "materials" in data)
    test("Search query matches", data.get("query") == "Python", f"Got: {data.get('query')}")
    test("Search found results", data.get("total", 0) > 0, f"Total: {data.get('total', 0)}")

    # ── 16. Search Empty ──
    print("\n[16] SEARCH - EMPTY QUERY")
    r = client.get("/api/materials/search?q=", headers=headers)
    test("Empty search returns 422 or 400",
         r.status_code in [422, 400], f"Got {r.status_code}")

    # ── 17. Analytics ──
    print("\n[17] ANALYTICS")
    r = client.get("/api/analytics", headers=headers)
    test("Analytics status code", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Analytics has total_materials", "total_materials" in data)
    test("Analytics has total_views", "total_views" in data)
    test("Analytics has top_materials", "top_materials" in data)
    test("Analytics total_materials > 0",
         data.get("total_materials", 0) > 0,
         f"Total: {data.get('total_materials', 0)}")
    if data.get("top_materials"):
        test("Analytics top material has title", "title" in data["top_materials"][0])
        test("Analytics top material has views", "views" in data["top_materials"][0])

    # ── 18. Redirect ──
    print("\n[18] RESOURCE REDIRECT")
    if resource_code:
        r = client.get(f"/{resource_code}", follow_redirects=False)
        test("Redirect status code", r.status_code == 302, f"Got {r.status_code}")
        test("Redirect has location header", "location" in r.headers,
             f"Location: {r.headers.get('location', 'N/A')}")
        test("Redirect to correct URL",
             r.headers.get("location") == "https://example.com/python-oop.pdf",
             f"Got: {r.headers.get('location')}")

        # ── 19. View Count Increment ──
        print("\n[19] VIEW COUNT INCREMENT")
        r = client.get("/api/materials", headers=headers)
        materials = r.json().get("materials", [])
        for m in materials:
            if m.get("resource_code") == resource_code:
                test("Views incremented after redirect",
                     m.get("views", 0) > 0, f"Views: {m.get('views', 0)}")
                break

    # ── 20. Invalid Redirect ──
    print("\n[20] INVALID REDIRECT")
    r = client.get("/INVALIDCODE")
    test("Invalid code returns 404", r.status_code == 404, f"Got {r.status_code}")
    data = r.json()
    test("Invalid code has error", "error" in data)

    # ── 21. PostgreSQL Connectivity ──
    print("\n[21] POSTGRESQL CONNECTIVITY")
    r = client.get("/stats")
    test("PostgreSQL accessible via stats", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Stats shows registered users",
         data.get("total_users", 0) > 0,
         f"Total users: {data.get('total_users', 0)}")

    # ── 22. Delete Material ──
    print("\n[22] DELETE MATERIAL")
    if material_id:
        r = client.delete(f"/api/materials/{material_id}", headers=headers)
        test("Delete status code", r.status_code == 200, f"Got {r.status_code}")
        data = r.json()
        test("Delete returns message", "message" in data,
             f"Message: {data.get('message', 'N/A')}")

    # ── 23. HTML Form Registration ──
    print("\n[23] HTML FORM REGISTRATION")
    form_email = f"formtest_{int(time.time())}@example.com"
    r = client.post("/register", data={
        "username": "formuser", "email": form_email, "password": "formpass123"
    })
    # Note: FastAPI's TestClient may follow redirects and return 200
    # The actual form registration is verified by the 200 OK (user created)
    test("Form registration succeeds", r.status_code in [200, 302], f"Got {r.status_code}")

    # ── 24. Login via HTML Form ──
    print("\n[24] HTML FORM LOGIN")
    r = client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    test("Form login status code", r.status_code == 200, f"Got {r.status_code}")
    test("Form login returns HTML", "text/html" in r.headers.get("content-type", ""))
    test("Form login contains dashboard",
         "Study Material Hub" in r.text or "dashboard" in r.text.lower(),
         "Response contains dashboard content")

    # ── Report ──
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    print(f"  Total tests: {total}")
    print(f"  Passed:      {passed}")
    print(f"  Failed:      {failed}")
    print(f"  Success rate: {passed / total * 100:.1f}%")
    print(f"  Timestamp:    {datetime.now().isoformat()}")

    if failed > 0:
        print("\n  FAILED TESTS:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    - {r['test']}: {r['detail']}")
    else:
        print("\n  ✅ ALL TESTS PASSED - Migration successful!")

    print()

    # Write report to file
    with open("VERIFICATION_REPORT.md", "w") as f:
        f.write("# Migration Verification Report\n\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Tests | {total} |\n")
        f.write(f"| Passed | {passed} |\n")
        f.write(f"| Failed | {failed} |\n")
        f.write(f"| Success Rate | {passed / total * 100:.1f}% |\n\n")
        f.write("## Detailed Results\n\n")
        f.write("| # | Test | Status | Detail |\n")
        f.write("|---|------|--------|--------|\n")
        for i, r in enumerate(results, 1):
            f.write(f"| {i} | {r['test']} | {r['status']} | {r['detail']} |\n")

    return passed, failed, total


if __name__ == "__main__":
    passed, failed, total = run_verification()
    sys.exit(0 if failed == 0 else 1)