"""
FastAPI Application — Study Material Hub

Migrated from Flask to FastAPI. Preserves all existing functionality,
database schema, authentication, and frontend templates.

New features:
- Automatic Swagger UI at /docs
- OpenAPI schema at /openapi.json
- Health endpoint at /health
- Stats endpoint at /stats
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler

from config import Config
from database import init_db
from routers.common_router import router as common_router
from routers.auth_router import router as auth_router
from routers.materials_router import router as materials_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler for startup/shutdown events.

    Initializes database tables on startup.
    """
    # Startup: validate config and init database
    Config.validate()
    init_db()
    print(f"FastAPI server starting on {Config.HOST}:{Config.PORT}")
    yield
    # Shutdown: cleanup if needed
    print("FastAPI server shutting down")


app = FastAPI(
    title="Study Material Hub API",
    description="""
    API for managing study materials with user authentication,
    search, analytics, and resource redirection.

    ## Features
    * User registration and JWT-based authentication
    * Create, list, search, and delete study materials
    * View analytics and statistics
    * Resource code redirection
    * Automatic API documentation
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware — allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(common_router)
app.include_router(auth_router)
app.include_router(materials_router)


# Custom exception handler to ensure consistent error format
# (Flask-compatible: uses "error" and "details" keys instead of "detail")
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    from fastapi.responses import JSONResponse

    content = {"error": exc.detail}
    # If detail looks like a validation error, wrap it
    if isinstance(exc.detail, str) and ":" in exc.detail:
        parts = exc.detail.split(":")
        content = {"error": parts[0].strip(), "details": ":".join(parts[1:]).strip()}

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=getattr(exc, "headers", None),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app_fastapi:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="debug" if Config.DEBUG else "info",
    )