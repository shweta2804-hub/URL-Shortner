from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    details: Optional[list[str] | str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    version: str = "1.0.0"


class StatsResponse(BaseModel):
    """System statistics response."""
    total_users: int
    total_materials: int
    total_views: int
    average_views_per_material: float