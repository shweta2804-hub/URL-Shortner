from pydantic import BaseModel, field_validator
from config import Config


class RegisterRequest(BaseModel):
    """Registration request validation."""
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("username is required")
        if len(v) < 2 or len(v) > 80:
            raise ValueError("username must be between 2 and 80 characters")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        v = v.strip().lower()
        if not v:
            raise ValueError("email is required")
        if not Config.EMAIL_REGEX.match(v):
            raise ValueError("email format is invalid")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError("password is required")
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    """Login request validation."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.strip().lower()


class ProfileStats(BaseModel):
    """Profile statistics."""
    total_materials: int
    total_views: int
    avg_views: int
    top_material: str


class ProfileResponse(BaseModel):
    """Profile response model."""
    user: dict
    stats: ProfileStats