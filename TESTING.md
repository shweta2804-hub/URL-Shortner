# 🧪 API Testing Guide — URL Shortner

Complete step-by-step instructions to test all REST API endpoints using **Thunder Client** (VS Code extension) or **curl**.

---

## 📋 Table of Contents

1. [Setup](#setup)
2. [API Endpoints Overview](#api-endpoints-overview)
3. [Thunder Client Testing](#thunder-client-testing)
4. [curl Commands](#curl-commands)
5. [Testing Flow](#testing-flow)
6. [Error Scenarios](#error-scenarios)
7. [Database Verification](#database-verification)

---

## Setup

### Prerequisites

- PostgreSQL running with `url_shortner` database created
- Virtual environment activated
- All dependencies installed: `pip install -r requirements.txt`
- `.env` configured with your PostgreSQL credentials

### Start the Server

```bash
python app.py
```

Server starts at **http://127.0.0.1:5000**

---

## API Endpoints Overview

| # | Method | Endpoint | Auth | Description |
|---|--------|----------|------|-------------|
| 1 | `POST` | `/api/register` | ❌ Public | Create a new user account |
| 2 | `POST` | `/api/login` | ❌ Public | Authenticate and get JWT token |
| 3 | `GET` | `/api/profile` | ✅ Bearer Token | Get user profile + URL stats |
| 4 | `POST` | `/api/shorten` | ✅ Bearer Token | Create a shortened URL |
| 5 | `GET` | `/api/urls` | ✅ Bearer Token | List all user's URLs |
| 6 | `GET` | `/api/analytics` | ✅ Bearer Token | Get detailed click analytics |
| 7 | `GET` | `/<short_code>` | ❌ Public | Follow a short URL redirect |

### Authentication Header

All protected endpoints require:
```
Authorization: Bearer <jwt_token>
```

The JWT token is returned by both `/api/register` and `/api/login`.

---

## Thunder Client Testing

### Installing Thunder Client

1. Open **VS Code**
2. Go to **Extensions** (`Ctrl+Shift+X`)
3. Search for **"Thunder Client"**
4. Click **Install**

### Creating Requests

#### 1️⃣ POST /api/register — Register User

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:5000/api/register` |
| **Headers** | `Content-Type: application/json` |

**Body → JSON:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Expected Response `201`:**
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

```
📋 Copy the `token` value — you'll need it for protected endpoints.
```

---

#### 2️⃣ POST /api/login — Login

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:5000/api/login` |
| **Headers** | `Content-Type: application/json` |

**Body → JSON:**
```json
{
  "email": "john@example.com",
  "password": "secret123"
}
```

**Expected Response `200`:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

---

#### 3️⃣ GET /api/profile — Get Profile

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://127.0.0.1:5000/api/profile` |
| **Headers** | `Authorization: Bearer <your-token>` |

**Expected Response `200`:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-06-15T14:30:00"
  },
  "stats": {
    "total_urls": 0,
    "total_clicks": 0
  }
}
```

---

#### 4️⃣ POST /api/shorten — Create Short URL

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:5000/api/shorten` |
| **Headers** | `Content-Type: application/json` + `Authorization: Bearer <token>` |

**Body → JSON:**
```json
{
  "url": "https://www.example.com/very/long/url/that/needs/shortening"
}
```

**Expected Response `201`:**
```json
{
  "message": "URL shortened successfully",
  "url": {
    "id": 1,
    "user_id": 1,
    "original_url": "https://www.example.com/very/long/url/that/needs/shortening",
    "short_code": "aB3xYz",
    "short_url": "http://127.0.0.1:5000/aB3xYz",
    "clicks": 0,
    "created_at": "2026-06-15T14:35:00"
  }
}
```

```
📋 Copy the `short_code` (e.g., "aB3xYz") — you'll need it to test the redirect.
```

---

#### 5️⃣ GET /api/urls — List User URLs

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://127.0.0.1:5000/api/urls` |
| **Headers** | `Authorization: Bearer <token>` |

**Expected Response `200`:**
```json
{
  "total": 1,
  "urls": [
    {
      "id": 1,
      "user_id": 1,
      "original_url": "https://www.example.com/very/long/url/that/needs/shortening",
      "short_code": "aB3xYz",
      "short_url": "http://127.0.0.1:5000/aB3xYz",
      "clicks": 0,
      "created_at": "2026-06-15T14:35:00"
    }
  ]
}
```

---

#### 6️⃣ GET /api/analytics — Get Analytics

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://127.0.0.1:5000/api/analytics` |
| **Headers** | `Authorization: Bearer <token>` |

**Expected Response `200`:**
```json
{
  "total_urls": 1,
  "total_clicks": 0,
  "avg_clicks": 0,
  "most_clicked_count": 0,
  "top_urls": [
    {
      "id": 1,
      "original_url": "https://www.example.com/very/long/url/that/needs/shortening",
      "short_code": "aB3xYz",
      "short_url": "http://127.0.0.1:5000/aB3xYz",
      "clicks": 0,
      "created_at": "2026-06-15T14:35:00"
    }
  ]
}
```

---

#### 7️⃣ GET /{short_code} — Test Redirect

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://127.0.0.1:5000/aB3xYz` (use actual short_code) |
| **Headers** | None required |

**Expected:** Browser/Thunder Client follows the 302 redirect to the original URL.

In Thunder Client, you'll see **Status: 302 Found** with the `Location` header pointing to your original URL. Disable "Follow Redirects" in Thunder Client to see the 302 status code.

---

## curl Commands

### 1. Register a User

```bash
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "email": "john@example.com", "password": "secret123"}'
```

### 2. Login

```bash
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret123"}'
```

### 3. Get Profile (replace TOKEN with actual JWT)

```bash
curl -X GET http://127.0.0.1:5000/api/profile \
  -H "Authorization: Bearer TOKEN"
```

### 4. Create Short URL

```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"url": "https://www.example.com/long-url"}'
```

### 5. List User URLs

```bash
curl -X GET http://127.0.0.1:5000/api/urls \
  -H "Authorization: Bearer TOKEN"
```

### 6. Get Analytics

```bash
curl -X GET http://127.0.0.1:5000/api/analytics \
  -H "Authorization: Bearer TOKEN"
```

### 7. Test Redirect

```bash
curl -v http://127.0.0.1:5000/aB3xYz
```
Use `-v` (verbose) to see the 302 redirect and `Location` header.

### Complete Automated Test Script

Save as `test_all.sh` (Linux/macOS) or use with Git Bash:

```bash
#!/bin/bash

BASE="http://127.0.0.1:5000"

echo "=== 1. Register ==="
REGISTER=$(curl -s -X POST "$BASE/api/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"test123456"}')
echo "$REGISTER" | python -m json.tool

TOKEN=$(echo "$REGISTER" | python -c "import sys,json; print(json.load(sys.stdin).get('token',''))")

echo -e "\n=== 2. Login ==="
curl -s -X POST "$BASE/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123456"}' | python -m json.tool

echo -e "\n=== 3. Profile ==="
curl -s "$BASE/api/profile" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo -e "\n=== 4. Shorten URL ==="
SHORTEN=$(curl -s -X POST "$BASE/api/shorten" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"url":"https://example.com/test"}')
echo "$SHORTEN" | python -m json.tool

CODE=$(echo "$SHORTEN" | python -c "import sys,json; print(json.load(sys.stdin).get('url',{}).get('short_code',''))")

echo -e "\n=== 5. List URLs ==="
curl -s "$BASE/api/urls" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo -e "\n=== 6. Analytics ==="
curl -s "$BASE/api/analytics" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo -e "\n=== 7. Redirect (code: $CODE) ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\nLocation: %{redirect_url}\n" "$BASE/$CODE"

echo -e "\n=== ALL TESTS COMPLETE ==="
```

---

## Testing Flow

Follow this order for a complete end-to-end test:

```mermaid
graph LR
    A[Register] --> B[Login]
    B --> C[Profile]
    C --> D[Shorten URL]
    D --> E[List URLs]
    E --> F[Analytics]
    F --> G[Test Redirect]
```

1. **Register** → Get JWT token
2. **Login** → Verify same token works
3. **Profile** → See user info and stats (should be 0/0)
4. **Shorten URL** → Get short code
5. **List URLs** → See the URL you just created
6. **Analytics** → See aggregate stats
7. **Test Redirect** → Follow the short link to original URL

---

## Error Scenarios

Test these error cases to verify error handling:

### Register — Missing Fields

```bash
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": ""}'
```

**Expected `400`:**
```json
{
  "error": "Validation failed",
  "details": [
    "username is required",
    "email is required",
    "password is required"
  ]
}
```

### Register — Duplicate Email

```bash
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe2", "email": "john@example.com", "password": "secret123"}'
```

**Expected `409`:**
```json
{
  "error": "Email already registered"
}
```

### Login — Wrong Password

```bash
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "wrongpassword"}'
```

**Expected `401`:**
```json
{
  "error": "Invalid email or password"
}
```

### Profile — No Token

```bash
curl -X GET http://127.0.0.1:5000/api/profile
```

**Expected `401`:**
```json
{
  "error": "Missing Authorization Header"
}
```

### Shorten — Invalid URL

```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"url": "not-a-valid-url"}'
```

**Expected `400`:**
```json
{
  "error": "URL must start with http:// or https://"
}
```

### Redirect — Unknown Code

```bash
curl -v http://127.0.0.1:5000/NONEXIST
```

**Expected `404`:**
```json
{
  "error": "URL not found"
}
```

---

## Database Verification

Verify that data is stored correctly in PostgreSQL:

### Connect to PostgreSQL

```bash
psql -U postgres -d url_shortner
```

### Check Users Table

```sql
SELECT id, username, email, created_at FROM users;
```

Expected output:
```
 id | username |      email       |         created_at
----+----------+------------------+----------------------------
  1 | johndoe  | john@example.com | 2026-06-15 14:30:00.123456
```

⚠️ **Note:** The `password` column is hashed — it should look like a long scrypt hash, not plain text.

### Check URLs Table

```sql
SELECT id, user_id, original_url, short_code, clicks, created_at FROM urls;
```

Expected output:
```
 id | user_id |            original_url            | short_code | clicks |         created_at
----+---------+-------------------------------------+------------+--------+----------------------------
  1 |       1 | https://www.example.com/long-url    | aB3xYz     |      0 | 2026-06-15 14:35:00.123456
```

### Verify Foreign Key Constraint

```sql
-- This should fail with foreign key violation
INSERT INTO urls (user_id, original_url, short_code)
VALUES (999, 'https://example.com', 'test123');
```

**Expected Error:**
```
ERROR:  insert or update on table "urls" violates foreign key constraint "urls_user_id_fkey"
```

### Verify Unique Constraints

```sql
-- This should fail with duplicate key violation
INSERT INTO users (username, email, password)
VALUES ('johndoe', 'john@example.com', 'hash123');
```

**Expected Error:**
```
ERROR:  duplicate key value violates unique constraint "users_email_key"
```

---

## Quick Reference Card

| Endpoint | Method | Auth | Success Code | Error Codes |
|----------|--------|------|-------------|-------------|
| `/api/register` | POST | ❌ | **201** | 400, 409, 500 |
| `/api/login` | POST | ❌ | **200** | 400, 401 |
| `/api/profile` | GET | ✅ | **200** | 401, 404 |
| `/api/shorten` | POST | ✅ | **201** | 400, 401, 500 |
| `/api/urls` | GET | ✅ | **200** | 401, 404 |
| `/api/analytics` | GET | ✅ | **200** | 401, 404 |
| `/<short_code>` | GET | ❌ | **302** | 404 |

---

## Troubleshooting

### "Connection refused" when starting the app

Ensure PostgreSQL is running:
```bash
# Windows
net start postgresql-x64-16

# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

### "FATAL: database 'url_shortner' does not exist"

```bash
createdb -U postgres url_shortner
# or via psql:
# CREATE DATABASE url_shortner;
```

### "ModuleNotFoundError: No module named 'psycopg2'"

```bash
pip install -r requirements.txt
```

### Token works on /api/profile but not on /api/shorten

The token is likely being sent as a query parameter or in the wrong header. Ensure it's in the `Authorization` header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### "Cannot connect to database" on Render

Ensure you've linked the PostgreSQL database to the web service in the Render dashboard, and the `DATABASE_URL` environment variable is set automatically.