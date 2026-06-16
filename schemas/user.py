from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserPublic(BaseModel):
    """Public user representation (no password hash)."""
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """Response model for user registration/login."""
    message: str
    token: str
    user: UserPublic