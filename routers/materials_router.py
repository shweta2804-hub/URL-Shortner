"""
FastAPI router for study material endpoints.

Replaces the Flask materials blueprint while preserving identical API contract.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse

from config import Config
import models.user as UserModel
import models.material as MaterialModel
from dependencies import get_current_user
from schemas.material import (
    CreateMaterialRequest,
    CreateMaterialResponse,
    MaterialResponse,
    MaterialListResponse,
    SearchResponse,
    DeleteResponse,
)
from schemas.common import ErrorResponse

router = APIRouter(tags=["Materials"])


def _material_to_response(material: dict) -> MaterialResponse:
    """Convert a material dict to a MaterialResponse Pydantic model."""
    return MaterialResponse(**material)


@router.post(
    "/api/materials",
    response_model=CreateMaterialResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Create a new study material",
)
async def create_material(
    body: CreateMaterialRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new study material for the authenticated user.

    Requires title and resource_link. Optional fields: description, subject, category.
    """
    try:
        material = MaterialModel.create_material(
            current_user["id"],
            body.title,
            body.resource_link,
            body.description,
            body.subject,
            body.category,
        )
        return CreateMaterialResponse(
            message="Study material created successfully",
            material=_material_to_response(material),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create material: {str(e)}",
        )


@router.get(
    "/api/materials",
    response_model=MaterialListResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="List all study materials for the authenticated user",
)
async def list_materials(current_user: dict = Depends(get_current_user)):
    """
    List all study materials created by the authenticated user,
    ordered newest first.
    """
    materials = MaterialModel.get_materials_by_user(current_user["id"])
    return MaterialListResponse(
        total=len(materials),
        materials=[_material_to_response(m) for m in materials],
    )


@router.get(
    "/api/materials/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Search study materials",
)
async def search_materials(
    q: str = Query(..., description="Search query string"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search study materials by title, description, subject, or category.

    Requires query parameter 'q'. Returns matching materials ordered by newest first.
    """
    query = q.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query 'q' is required",
        )

    results = MaterialModel.search_materials(current_user["id"], query)
    return SearchResponse(
        total=len(results),
        query=query,
        materials=[_material_to_response(m) for m in results],
    )


@router.get(
    "/api/analytics",
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Get detailed view analytics for user's materials",
)
async def analytics(current_user: dict = Depends(get_current_user)):
    """
    Get detailed view analytics for the authenticated user's materials.

    Returns aggregate metrics and top 5 most-viewed materials.
    """
    analytics_data = MaterialModel.get_user_analytics(current_user["id"])
    return analytics_data


@router.delete(
    "/api/materials/{material_id}",
    response_model=DeleteResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Delete a study material",
)
async def delete_material(
    material_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a study material owned by the authenticated user.

    Returns 404 if the material does not exist or is not owned by the user.
    """
    deleted = MaterialModel.delete_material(material_id, current_user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found or not owned by user",
        )

    return DeleteResponse(message="Material deleted successfully")


