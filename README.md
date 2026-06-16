# 📚 Study Material Hub

A production-ready **study material organizer** built with **FastAPI** and **PostgreSQL (Neon)**. Features JWT-based authentication, RESTful APIs with automatic OpenAPI documentation, view analytics, search, and one-click deployment on **Render**.

---

## ✨ Features

- **Study Materials** — Create materials with title, description, subject, category, and resource link
- **Auto-generated Resource Codes** — Shareable short links for each resource
- **JWT Authentication** — Secure register/login with JSON Web Tokens (PyJWT)
- **User Dashboards** — Each user sees only their own materials
- **View Analytics** — Track total views, average views, and top-performing materials
- **Search** — Search materials by title, description, subject, or category
- **RESTful API** — Full JSON API with OpenAPI documentation (Swagger UI)
- **PostgreSQL (Neon)** — Cloud-native relational database with connection pooling
- **Password Security** — Passwords hashed with `werkzeug.security` (scrypt)
- **Input Validation** — Email format, URL format, length constraints via Pydantic
- **Automatic API Docs** — Swagger UI at `/docs`, OpenAPI schema at `/openapi.json`
- **Health & Stats** — Built-in `/health` and `/stats` endpoints
- **Deployment Ready** — Render config, uvicorn, environment variables

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Programming language |
| **FastAPI** | Async web framework with automatic OpenAPI |
| **PyJWT** | JWT authentication (HS256) |
| **PostgreSQL (Neon)** | Cloud database with SSL |
| **psycopg2-binary** | PostgreSQL database driver |
| **Werkzeug** | Password hashing (scrypt + salt) |
| **Pydantic** | Request/response validation models |
| **uvicorn** | Production ASGI server |
| **Jinja2** | HTML templating (legacy form pages) |
| **Render** | Cloud deployment platform (Free tier) |

---

## 📁 Project Structure

```
Study Material Hub/
│
├── app_fastapi.py          # FastAPI application entry point (uvicorn)
├── config.py               # Configuration from environment variables
├── database.py             # PostgreSQL connection pool & table init
├── dependencies.py         # JWT authentication dependency injection
│
├── routers/                # FastAPI route handlers
│   ├── __init__.py
│   ├── auth_router.py      # /api/register, /api/login, /api/profile
│   ├── materials_router.py # /api/materials, /api/analytics
│   └── common_router.py    # /, /dashboard, /register (HTML), /health, /stats
│
├── schemas/                # Pydantic request/response models
│   ├── __init__.py
│   ├── auth.py             # RegisterRequest, LoginRequest, ProfileStats
│   ├── material.py         # CreateMaterialRequest, MaterialResponse
│   ├── common.py           # ErrorResponse, HealthResponse, StatsResponse
│   └── user.py             # UserPublic, UserResponse
│
├── models/                 # Database access layer
│   ├── __init__.py
│   ├── user.py             # User CRUD operations
│   └── material.py         # Material CRUD, search & analytics
│
├── templates/              # HTML templates (legacy form-based UI)
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── static/
│   ├── style.css
│   └── js/
│       └── main.js
│
├── .env                    # Environment variables (NOT committed)
├── .gitignore
├── requirements.txt
├── render.yaml             # Render deployment config
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 14+** running locally or a **Neon** cloud database
- **pip** (Python package manager)

### Step 1: Clone & Enter Directory

```bash
git clone <repository-url>
cd "URL Shortner"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL

Create a database (local or Neon):

```bash
# Local PostgreSQL
psql -U postgres
CREATE DATABASE study_material_hub;
\q

# Neon: Create a database from the Neon dashboard and copy the connection string
```

### Step 5: Configure Environment

Edit `.env` with your database credentials:

```ini
DATABASE_URL=postgresql://postgres:password@localhost:5432/study_material_hub
# For Neon:
# DATABASE_URL=postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech/neondb?sslmode=require

JWT_SECRET_KEY=your-random-secret-key-here
SECRET_KEY=another-random-secret-key
```

### Step 6: Run the Application

```bash
# Development with auto-reload
uvicorn app_fastapi:app --reload

# Or via Python
python app_fastapi.py
```

The server starts at **http://127.0.0.1:5000**.

On first startup, the database tables (`users` and `materials`) are created automatically via the lifespan handler.

### Step 7: Explore API Documentation

Open your browser to:
- **Swagger UI:** http://127.0.0.1:5000/docs
- **ReDoc:** http://127.0.0.1:5000/redoc
- **OpenAPI Schema:** http://127.0.0.1:5000/openapi.json

---

## 📖 API Documentation

All API endpoints accept and return **JSON**. Authentication is via **Bearer JWT tokens**.

### Authentication

```
Authorization: Bearer <token>
```

Obtain a token via `POST /api/register` or `POST /api/login`.

---

### `POST /api/register`

Create a new user account.

**Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response `201` — Created:**
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

**Errors:**
| Code | Description |
|------|-------------|
| 400 | Validation failed (missing fields, bad email, short password) |
| 409 | Email already registered |
| 500 | Server error |

---

### `POST /api/login`

Authenticate and receive a JWT token.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response `200` — OK:**
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

**Errors:** `400` (missing fields), `401` (invalid credentials)

---

### `GET /api/profile`

Get the authenticated user's profile and material statistics.

**Headers:** `Authorization: Bearer <token>`

**Response `200` — OK:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-06-15T14:30:00"
  },
  "stats": {
    "total_materials": 5,
    "total_views": 42,
    "avg_views": 8,
    "top_material": "Python OOP Notes"
  }
}
```

**Errors:** `401` (no token), `404` (user not found)

---

### `POST /api/materials`

Create a new study material. Requires authentication.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Python OOP Notes",
  "resource_link": "https://example.com/python-oop.pdf",
  "description": "Comprehensive notes on OOP in Python",
  "subject": "Computer Science",
  "category": "Notes"
}
```

**Response `201` — Created:**
```json
{
  "message": "Study material created successfully",
  "material": {
    "id": 1,
    "user_id": 1,
    "title": "Python OOP Notes",
    "description": "Comprehensive notes on OOP in Python",
    "subject": "Computer Science",
    "category": "Notes",
    "resource_link": "https://example.com/python-oop.pdf",
    "resource_code": "aB3xYz",
    "short_url": "http://127.0.0.1:5000/aB3xYz",
    "views": 0,
    "created_at": "2026-06-15T14:30:00"
  }
}
```

**Errors:** `400` (invalid data), `401` (no token), `500` (server error)

---

### `GET /api/materials`

List all materials created by the authenticated user, newest first.

**Headers:** `Authorization: Bearer <token>`

**Response `200` — OK:**
```json
{
  "total": 2,
  "materials": [
    {
      "id": 2,
      "user_id": 1,
      "title": "Linear Algebra Notes",
      "subject": "Mathematics",
      "category": "Notes",
      "resource_link": "https://example.com/linear-algebra.pdf",
      "resource_code": "XyZ789",
      "short_url": "http://127.0.0.1:5000/XyZ789",
      "views": 5,
      "created_at": "2026-06-15T14:35:00"
    }
  ]
}
```

**Errors:** `401` (no token), `404` (user not found)

---

### `GET /api/materials/search?q=query`

Search materials by title, description, subject, or category.

**Headers:** `Authorization: Bearer <token>`

**Response `200` — OK:**
```json
{
  "total": 1,
  "query": "python",
  "materials": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Python OOP Notes",
      "subject": "Computer Science",
      "category": "Notes",
      "resource_link": "https://example.com/python-oop.pdf",
      "resource_code": "aB3xYz",
      "short_url": "http://127.0.0.1:5000/aB3xYz",
      "views": 10,
      "created_at": "2026-06-15T14:30:00"
    }
  ]
}
```

**Errors:** `400` (no query), `401` (no token), `404` (user not found)

---

### `GET /api/analytics`

Get detailed view analytics for the authenticated user's materials.

**Headers:** `Authorization: Bearer <token>`

**Response `200` — OK:**
```json
{
  "total_materials": 5,
  "total_views": 100,
  "avg_views": 20,
  "most_viewed_count": 50,
  "top_materials": [
    {
      "id": 1,
      "title": "Python OOP Notes",
      "subject": "Computer Science",
      "category": "Notes",
      "resource_link": "https://example.com/python-oop.pdf",
      "resource_code": "abc123",
      "short_url": "http://127.0.0.1:5000/abc123",
      "views": 50,
      "created_at": "2026-06-15T14:30:00"
    }
  ]
}
```

**Errors:** `401` (no token), `404` (user not found)

---

### `GET /{resource_code}`

Follow a resource link to its original destination. No authentication required.

**Response:** `302` — Redirect to the resource link

**Errors:** `404` — Resource code not found

---

### `GET /health`

Health check endpoint for monitoring and Render load balancer.

**Response `200` — OK:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

### `GET /stats`

Get overall system statistics.

**Response `200` — OK:**
```json
{
  "total_users": 10,
  "total_materials": 25,
  "total_views": 150,
  "average_views_per_material": 6.0
}
```

---

## 🌐 Deployment

### Deploy to Render (One-Click)

This project includes a `render.yaml` Blueprint for automatic deployment.

1. **Push code to GitHub**
2. In [Render Dashboard](https://dashboard.render.com), click **"New +" → "Blueprint"**
3. Connect your repository
4. Render automatically:
   - Creates a PostgreSQL (Neon) database
   - Sets environment variables (`SECRET_KEY`, `JWT_SECRET_KEY` auto-generated)
   - Builds and deploys the application
   - Sets the health check path to `/health`

#### Manual Render Setup

If not using Blueprint:

1. Create a **Web Service** on Render
2. Set:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app_fastapi:app --host 0.0.0.0 --port $PORT --workers 2 --timeout-keep-alive 120`
   - **Health Check Path:** `/health`
3. Add a **PostgreSQL database** and connect it to the web service
4. Add environment variables:

| Variable | Required | Value |
|----------|----------|-------|
| `DATABASE_URL` | ✅ | Auto-filled from linked database |
| `SECRET_KEY` | ✅ | Click "Generate" |
| `JWT_SECRET_KEY` | ✅ | Click "Generate" |
| `PRODUCTION` | ✅ | `true` |
| `DEBUG` | ✅ | `false` |
| `HOST` | ✅ | `0.0.0.0` |
| `BASE_URL` | ✅ | `https://your-app.onrender.com` |

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | — | PostgreSQL connection string (with `?sslmode=require` for Neon) |
| `SECRET_KEY` | ✅ Yes | — | Application secret key |
| `JWT_SECRET_KEY` | ✅ Yes | — | JWT signing key |
| `DEBUG` | ❌ No | `false` | Enable debug mode (must be `false` in production) |
| `PRODUCTION` | ❌ No | `false` | Enables production validation checks |
| `PORT` | ❌ No | `5000` | Server port |
| `HOST` | ❌ No | `127.0.0.1` | Server bind address |
| `BASE_URL` | ❌ No | `http://127.0.0.1:5000` | Base URL for resource short links |
| `JWT_ACCESS_TOKEN_EXPIRES` | ❌ No | `3600` | Token expiry in seconds |

---

## 🧪 Testing with Postman

1. Open **Postman**
2. Click **"Import"** → select `postman_collection.json`
3. All endpoints are pre-configured with:
   - Request bodies
   - Authorization headers
   - Auto-token chaining (tokens are saved after register/login)
4. Set the `base_url` variable:
   - Local: `http://127.0.0.1:5000`
   - Production: Your Render URL

---

## ✅ Verification Tests

Run the built-in test suite (no external dependencies required):

```bash
python test_fastapi_direct.py
```

This tests all endpoints including health, registration, login, JWT validation, CRUD operations, search, analytics, redirect, and PostgreSQL connectivity.

---

## 🚢 Deployment Checklist

### Pre-Deployment

- [ ] Set `PRODUCTION=true` in environment
- [ ] Set `DEBUG=false` in environment
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Update `BASE_URL` to your production domain
- [ ] Ensure Neon PostgreSQL database is created
- [ ] Test all API endpoints locally
- [ ] Verify Swagger UI loads at `/docs`
- [ ] Verify health endpoint at `/health`

### Render Deployment

- [ ] Push code to GitHub repository
- [ ] Connect repository to Render
- [ ] Verify Blueprint deployment or configure manually
- [ ] Check logs for any startup errors
- [ ] Test `/health` endpoint (Render will use this for health checks)
- [ ] Verify database connection: `{"database": "connected"}`
- [ ] Test Swagger UI at `https://your-app.onrender.com/docs`
- [ ] Set up custom domain (optional)

### Post-Deployment

- [ ] Register a test user
- [ ] Create a study material
- [ ] Verify the redirect works
- [ ] Check analytics data
- [ ] Test search functionality
- [ ] Monitor error logs on Render dashboard

---

## 🔒 Security

- Passwords hashed with **scrypt** via `werkzeug.security.generate_password_hash`
- JWT tokens signed with **HS256** using `PyJWT`
- Password hashes **never exposed** in API responses
- All database queries use **parameterized statements** (SQL injection protected)
- Connection pooling with **automatic commit/rollback**
- Input validation via **Pydantic** on all endpoints (email format, URL format, length limits)
- Secrets read from **environment variables only** — no hard-coded values
- `.env` file excluded from version control via `.gitignore`
- Production config validation at startup (`Config.validate()`)

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [PyJWT](https://pyjwt.readthedocs.io/)
- [psycopg2](https://www.psycopg.org/)
- [Neon PostgreSQL](https://neon.tech/)
- [Render](https://render.com/)
- [Uvicorn](https://www.uvicorn.org/)