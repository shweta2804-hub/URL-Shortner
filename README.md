# 📚 Study Material Hub

A production-ready **study material organizer** built with **Flask** and **PostgreSQL**. Features JWT-based authentication, RESTful APIs, view analytics, search, and deployment support for **Render**.

---

## ✨ Features

- **Study Materials** — Create materials with title, description, subject, category, and resource link
- **Auto-generated Resource Codes** — Shareable short links for each resource
- **JWT Authentication** — Secure register/login with JSON Web Tokens
- **User Dashboards** — Each user sees only their own materials
- **View Analytics** — Track total views, average views, and top-performing materials
- **Search** — Search materials by title, description, subject, or category
- **RESTful API** — Full JSON API for integration with frontend apps or mobile
- **PostgreSQL** — Robust relational database with connection pooling
- **Password Security** — Passwords hashed with `werkzeug.security`
- **Input Validation** — Email format, URL format, length constraints
- **Deployment Ready** — Render config, Gunicorn, environment variables

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3** | Programming language |
| **Flask 3** | Web framework |
| **Flask-JWT-Extended** | JWT authentication |
| **psycopg2** | PostgreSQL database driver |
| **Werkzeug** | Password hashing |
| **Gunicorn** | Production WSGI server |
| **Render** | Cloud deployment platform |

---

## 📁 Project Structure

```
Study Material Hub/
│
├── app.py                 # Application factory, blueprint registration
├── config.py              # Configuration from environment variables
├── database.py            # PostgreSQL connection pool & table init
│
├── models/
│   ├── __init__.py
│   ├── user.py            # User CRUD operations
│   └── material.py        # Material CRUD, search & analytics operations
│
├── routes/
│   ├── __init__.py
│   ├── auth.py            # /api/register, /api/login, /api/profile
│   └── materials.py       # /api/materials, /api/analytics, /<code>
│
├── templates/             # HTML templates (legacy form-based UI)
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── static/
│   ├── style.css
│   └── js/
│       └── main.js
│
├── .env                   # Environment variables (NOT committed)
├── .gitignore
├── requirements.txt
├── render.yaml            # Render deployment config
├── postman_collection.json
├── MIGRATION_PLAN.md
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 14+** running locally or on a server
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

Create the database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE study_material_hub;

# Exit
\q
```

### Step 5: Configure Environment

Edit `.env` with your PostgreSQL credentials:

```ini
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/study_material_hub
JWT_SECRET_KEY=your-random-secret-key-here
SECRET_KEY=another-random-secret-key
```

### Step 6: Run the Application

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**.

On first startup, the database tables (`users` and `materials`) are created automatically.

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

## 🌐 Deployment

### Deploy to Render

This project includes a `render.yaml` file for one-click deployment on Render.

1. **Push code to GitHub**
2. In [Render Dashboard](https://dashboard.render.com), click **"New +" → "Blueprint"**
3. Connect your repository
4. Render automatically:
   - Creates a PostgreSQL database
   - Sets environment variables
   - Builds and deploys the application

#### Manual Render Setup

If not using Blueprint:

1. Create a **Web Service** on Render
2. Set:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:create_app --worker-class gthread --workers 2 --threads 4 --bind 0.0.0.0:$PORT --timeout 120`
3. Add a **PostgreSQL database** and connect it to the web service
4. Add environment variables:
   - `SECRET_KEY` (auto-generate)
   - `JWT_SECRET_KEY` (auto-generate)
   - `PRODUCTION=true`
   - `DEBUG=false`
   - `BASE_URL=https://your-app.onrender.com`

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | — | PostgreSQL connection string |
| `SECRET_KEY` | ✅ Yes (prod) | `change-this-in-production` | Flask secret key |
| `JWT_SECRET_KEY` | ✅ Yes (prod) | — | JWT signing key |
| `DEBUG` | ❌ No | `false` | Enable Flask debug mode |
| `PRODUCTION` | ❌ No | `false` | Enables production validation |
| `PORT` | ❌ No | `5000` | Server port |
| `HOST` | ❌ No | `127.0.0.1` | Server bind address |
| `BASE_URL` | ❌ No | `http://127.0.0.1:5000` | Base URL for short links |
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

## 🚢 Deployment Checklist

### Pre-Deployment

- [ ] Set `PRODUCTION=true` in environment
- [ ] Set `DEBUG=false` in environment
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Update `BASE_URL` to your production domain
- [ ] Ensure PostgreSQL database is created
- [ ] Test all API endpoints locally
- [ ] Verify no `print()` or debug statements in production code

### Render Deployment

- [ ] Push code to GitHub repository
- [ ] Connect repository to Render
- [ ] Verify Blueprint deployment or configure manually
- [ ] Check logs for any startup errors
- [ ] Test health endpoint: `GET /api/materials` with a valid token
- [ ] Set up custom domain (optional)

### Post-Deployment

- [ ] Register a test user
- [ ] Create a study material
- [ ] Verify the redirect works
- [ ] Check analytics data
- [ ] Test search functionality
- [ ] Monitor error logs

---

## 🔒 Security

- Passwords hashed with **scrypt** via `werkzeug.security.generate_password_hash`
- JWT tokens signed with **HS256** using `flask-jwt-extended`
- Password hashes **never exposed** in API responses
- Connection pooling with **automatic commit/rollback**
- Input validation on **all** endpoints (email format, URL format, length limits)
- Database credentials read from **environment variables only**
- `.env` file excluded from version control via `.gitignore`

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [psycopg2](https://www.psycopg.org/)
- [Render](https://render.com/)