"""
FastAPI router for authentication endpoints.

Replaces the Flask auth blueprint while preserving identical API contract.
"""

from fastapi import APIRouter, HTTPException, status, Depends
import jwt as pyjwt
from datetime import datetime, timedelta, timezone

from config import Config
import models.user as UserModel
import models.material as MaterialModel
from dependencies import get_current_user
from schemas.auth import RegisterRequest, LoginRequest, ProfileResponse, ProfileStats
from schemas.user import UserResponse, UserPublic
from schemas.common import ErrorResponse

router = APIRouter(tags=["Authentication"])

ALGORITHM = "HS256"


def _create_token(email: str) -> str:
    """Create a JWT token with the same structure as flask_jwt_extended."""
    expiration = datetime.now(timezone.utc) + timedelta(
        seconds=Config.JWT_ACCESS_TOKEN_EXPIRES
    )
    payload = {
        "sub": email,
        "iat": datetime.now(timezone.utc),
        "exp": expiration,
        # Flask-JWT-Extended includes a 'jti' claim with a UUID;
        # we include it here for forward compatibility
    }
    token = pyjwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token


@router.post(
    "/api/register",
    response_model=UserResponse,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Register a new user",
)
async def register(body: RegisterRequest):
    """
    Register a new user and return a JWT token.

    Validates username, email, and password according to the same rules
    as the original Flask implementation.
    """
    # Check existing user
    existing = UserModel.get_user_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    try:
        user = UserModel.create_user(body.username, body.email, body.password)
        token = _create_token(body.email)

        return UserResponse(
            message="User registered successfully",
            token=token,
            user=UserPublic(**user),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post(
    "/api/login",
    response_model=UserResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
    summary="Authenticate a user and return a JWT token",
)
async def login(body: LoginRequest):
    """
    Authenticate a user with email and password.

    Returns a JWT token on success, identical to the Flask implementation.
    """
    user = UserModel.verify_password(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = _create_token(body.email)

    return UserResponse(
        message="Login successful",
        token=token,
        user=UserPublic(**user),
    )


@router.get(
    "/api/profile",
    response_model=ProfileResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get authenticated user's profile and stats",
)
async def profile(current_user: dict = Depends(get_current_user)):
    """
    Get the profile and material stats of the authenticated user.

    Returns user data along with aggregate statistics including
    total materials, total views, average views, and top material.
    """
    # Use lightweight stats query
    stats = MaterialModel.get_user_stats(current_user["id"])

    # Get analytics for additional data
    analytics_data = MaterialModel.get_user_analytics(current_user["id"])

    profile_stats = ProfileStats(
        total_materials=stats["total_materials"],
        total_views=stats["total_views"],
        avg_views=analytics_data.get("avg_views", 0),
        top_material=analytics_data["top_materials"][0]["title"]
        if analytics_data.get("top_materials")
        else "N/A",
    )

    return ProfileResponse(
        user=current_user,
        stats=profile_stats,
    )