"""
FastAPI dependency injection for JWT authentication.

Replaces flask_jwt_extended with raw PyJWT decoding.
Maintains the same token format and header structure.
"""

import jwt as pyjwt
from fastapi import Header, HTTPException, status
from config import Config
import models.user as UserModel

ALGORITHM = "HS256"


class TokenData:
    """Decoded JWT token payload."""
    def __init__(self, sub: str):
        self.sub = sub


async def get_current_user(authorization: str = Header(None)):
    """
    FastAPI dependency that extracts and validates the JWT from
    the Authorization header.

    Expects header format: Authorization: Bearer <token>

    Returns:
        dict: The authenticated user (without password hash)
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 404: If user not found
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    try:
        payload = pyjwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except pyjwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserModel.get_public_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user