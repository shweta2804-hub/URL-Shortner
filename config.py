import os
import re
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables.

    All secrets MUST be set via .env or environment variables.
    No hard-coded fallbacks — the app will refuse to start if
    critical values are missing.
    """

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

    # Server
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0" if os.getenv("PRODUCTION") else "127.0.0.1")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ERROR_MESSAGE_KEY = "error"

    # PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", 1))
    DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", 10))

    # Validation
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    MAX_URL_LENGTH = 2048

    @classmethod
    def validate(cls):
        """Validate critical config. Raises RuntimeError if anything is missing."""
        errors = []

        # Always required (dev + production)
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is not set — check your .env file")
        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY is not set — check your .env file")
        if not cls.JWT_SECRET_KEY:
            errors.append("JWT_SECRET_KEY is not set — check your .env file")

        # Additional production-only checks
        if cls.PRODUCTION:
            if cls.SECRET_KEY and len(cls.SECRET_KEY) < 32:
                errors.append("SECRET_KEY should be at least 32 characters in production")
            if cls.JWT_SECRET_KEY and len(cls.JWT_SECRET_KEY) < 32:
                errors.append("JWT_SECRET_KEY should be at least 32 characters in production")
            if cls.DEBUG:
                errors.append("DEBUG must be false in production")

        if errors:
            raise RuntimeError(
                "Configuration errors:\n  - " + "\n  - ".join(errors)
            )
