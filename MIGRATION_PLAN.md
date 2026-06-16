# Study Material Hub - Flask to FastAPI Migration Plan

## Overview
Migrate the backend from Flask to FastAPI while preserving all existing functionality, database schema, authentication, and frontend.

## Changes Summary

### Files to Create
| File | Purpose |
|------|---------|
| `schemas/__init__.py` | Pydantic schemas package |
| `schemas/auth.py` | Auth request/response Pydantic models |
| `schemas/material.py` | Material request/response Pydantic models |
| `schemas/user.py` | User Pydantic models |
| `schemas/common.py` | Common response models (error, health, stats) |
| `app_fastapi.py` | Main FastAPI application |
| `dependencies.py` | FastAPI dependency injection (JWT auth) |
| `routers/__init__.py` | FastAPI routers package |
| `routers/auth_router.py` | Auth endpoints (FastAPI) |
| `routers/materials_router.py` | Material endpoints (FastAPI) |
| `routers/common_router.py` | HTML routes, health, stats (FastAPI) |
| `migration_report.md` | This migration report |

### Files to Modify
| File | Change |
|------|--------|
| `requirements.txt` | Replace Flask deps with FastAPI deps |
| `config.py` | Add FastAPI/JWT config, keep existing |
| `render.yaml` | Update start command for uvicorn |

### Files to Keep Unchanged
| File | Reason |
|------|--------|
| `database.py` | PostgreSQL connection pool — framework agnostic |
| `models/user.py` | Pure DB logic — framework agnostic |
| `models/material.py` | Pure DB logic — framework agnostic |
| `templates/*` | Frontend — unchanged |
| `static/*` | Frontend — unchanged |
| `.env` | Environment config — unchanged |

## Route Mapping

### API Endpoints
| Flask Route | FastAPI Route | Method | Auth |
|-------------|---------------|--------|------|
| `/api/register` | `/api/register` | POST | No |
| `/api/login` | `/api/login` | POST | No |
| `/api/profile` | `/api/profile` | GET | JWT |
| `/api/materials` | `/api/materials` | POST | JWT |
| `/api/materials` | `/api/materials` | GET | JWT |
| `/api/materials/search?q=` | `/api/materials/search` | GET | JWT |
| `/api/analytics` | `/api/analytics` | GET | JWT |
| `/api/materials/<id>` | `/api/materials/<id>` | DELETE | JWT |
| `/<code>` | `/<code>` | GET | No |

### New Endpoints
| Endpoint | Description |
|----------|-------------|
| `/health` | Health check |
| `/stats` | System statistics |
| `/docs` | Swagger UI (automatic) |
| `/openapi.json` | OpenAPI schema (automatic) |

### HTML Form Routes (Preserved)
| Route | Method | Template |
|-------|--------|----------|
| `/` | GET | `login.html` |
| `/dashboard` | GET | `dashboard.html` |
| `/register` | GET/POST | `register.html` |
| `/login` | POST | Redirect to dashboard |

## Library Changes

### Removed
- `Flask==3.1.1`
- `Flask-JWT-Extended==4.7.1`

### Added
- `fastapi==0.115.0`
- `uvicorn[standard]==0.32.0`
- `PyJWT==2.9.0`
- `python-multipart==0.0.12` (for form data)

### Kept
- `Werkzeug==3.1.3` (password hashing only, not Flask)
- `psycopg2-binary==2.9.12`
- `python-dotenv==1.2.2`
- `gunicorn==26.0.0` (can still serve uvicorn workers)

## JWT Strategy
- Replace `flask_jwt_extended` with raw `PyJWT` library
- Custom dependency `get_current_user` decodes JWT from Authorization header
- Same token format and expiry config preserved
- Existing tokens remain valid

## Verification Plan
1. Install new dependencies
2. Start FastAPI server
3. Test registration
4. Test login (JWT generation)
5. Test create material
6. Test search
7. Test analytics
8. Test health/stats endpoints
9. Test Swagger UI at /docs
10. Verify PostgreSQL connectivity
11. Generate PASS/FAIL report