"""
FastAPI router for HTML form-based routes, health, and stats endpoints.

Preserves legacy HTML form functionality while adding new infrastructure endpoints.
"""

import re
from fastapi import APIRouter, HTTPException, status, Request, Form, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db
from config import Config
import models.material as MaterialModel
from schemas.common import HealthResponse, StatsResponse, ErrorResponse

router = APIRouter(tags=["General"])

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, summary="Login page")
async def home(request: Request):
    """Serve the login HTML page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse, summary="Dashboard page")
async def dashboard_page(request: Request):
    """Serve the dashboard HTML page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/register", response_class=HTMLResponse, summary="Register page")
async def register_page_get(request: Request):
    """Serve the registration HTML form."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse, summary="Register form submission")
async def register_page_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """Handle registration form submission (legacy HTML form support)."""
    hashed = generate_password_hash(password)

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed),
            )
            cur.close()
    except Exception:
        # If INSERT fails (e.g. duplicate email), redirect back to register
        return templates.TemplateResponse("register.html", {"request": request})

    return RedirectResponse(url="/", status_code=302)


@router.post("/login", response_class=HTMLResponse, summary="Login form submission")
async def login_page_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    """Handle login form submission (legacy HTML form support)."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, password FROM users WHERE email = %s",
            (email,),
        )
        user = cur.fetchone()
        cur.close()

    if user and check_password_hash(user[3], password):
        # Generate JWT token inline for the template
        import jwt as pyjwt
        from datetime import datetime, timedelta, timezone

        expiration = datetime.now(timezone.utc) + timedelta(
            seconds=Config.JWT_ACCESS_TOKEN_EXPIRES
        )
        payload = {
            "sub": email,
            "iat": datetime.now(timezone.utc),
            "exp": expiration,
        }
        token = pyjwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

        return templates.TemplateResponse(
            "dashboard.html", {"request": request, "token": token}
        )

    return HTMLResponse(content="Invalid Login", status_code=401)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
)
async def health():
    """
    Health check endpoint.

    Returns the status of the application and database connectivity.
    """
    db_status = "connected"
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy",
        database=db_status,
        version="1.0.0",
    )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="System statistics",
)
async def stats():
    """
    Get overall system statistics.

    Returns total users, total materials, total views, and average views.
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*)::int FROM users")
            total_users = cur.fetchone()[0]

            cur.execute(
                """
                SELECT
                    COUNT(*)::int,
                    COALESCE(SUM(views), 0)::int
                FROM materials
                """
            )
            materials_row = cur.fetchone()
            total_materials = materials_row[0]
            total_views = materials_row[1]

            cur.close()

        avg_views = (
            round(total_views / total_materials, 2) if total_materials > 0 else 0.0
        )

        return StatsResponse(
            total_users=total_users,
            total_materials=total_materials,
            total_views=total_views,
            average_views_per_material=avg_views,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}",
        )


# Resource code redirect — placed last to avoid catching other routes
# Matches short alphanumeric codes only (usually 4-8 chars)
_RESOURCE_CODE_PATTERN = re.compile(r"^[a-zA-Z0-9]{4,8}$")


@router.get(
    "/{code}",
    summary="Redirect a resource code to the original URL",
    responses={404: {"model": ErrorResponse}},
    include_in_schema=False,
)
async def redirect_resource(code: str = Path(...)):
    """
    Redirect a resource code to the original resource link.

    This route does not require authentication — anyone can follow a resource link.
    Only matches if the path is a 4-8 character alphanumeric resource code.
    Otherwise it will return 404.
    """
    if not _RESOURCE_CODE_PATTERN.match(code):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    material = MaterialModel.get_material_by_code(code)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    MaterialModel.increment_views(code)
    return RedirectResponse(url=material["resource_link"], status_code=302)
