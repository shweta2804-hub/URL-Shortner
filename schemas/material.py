from pydantic import BaseModel, field_validator
from typing import Optional
from config import Config


class CreateMaterialRequest(BaseModel):
    """Material creation request validation."""
    title: str
    resource_link: str
    description: Optional[str] = ""
    subject: Optional[str] = ""
    category: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("title is required")
        return v

    @field_validator("resource_link")
    @classmethod
    def validate_resource_link(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("resource_link is required")
        if len(v) > Config.MAX_URL_LENGTH:
            raise ValueError(
                f"Resource link exceeds maximum length of {Config.MAX_URL_LENGTH} characters"
            )
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Resource link must start with http:// or https://")
        return v

    @field_validator("description")
    @classmethod
    def strip_description(cls, v):
        if v:
            return v.strip()
        return ""

    @field_validator("subject")
    @classmethod
    def strip_subject(cls, v):
        if v:
            return v.strip()
        return ""

    @field_validator("category")
    @classmethod
    def strip_category(cls, v):
        if v:
            return v.strip()
        return ""


class MaterialResponse(BaseModel):
    """Material representation in API responses."""
    id: int
    user_id: int
    title: str
    description: str
    subject: str
    category: str
    resource_link: str
    resource_code: str
    short_url: str
    views: int
    created_at: str


class CreateMaterialResponse(BaseModel):
    """Response after creating a material."""
    message: str
    material: MaterialResponse


class MaterialListResponse(BaseModel):
    """Response for listing materials."""
    total: int
    materials: list[MaterialResponse]


class SearchResponse(BaseModel):
    """Response for search."""
    total: int
    query: str
    materials: list[MaterialResponse]


class DeleteResponse(BaseModel):
    """Response after deleting a material."""
    message: str