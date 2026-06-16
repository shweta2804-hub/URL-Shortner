from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import models.user as UserModel
import models.material as MaterialModel

materials_bp = Blueprint("materials", __name__)


@materials_bp.route("/api/materials", methods=["POST"])
@jwt_required()
def create_material():
    """
    Create a new study material.

    Headers:
        Authorization: Bearer <token>

    Request (JSON):
        {
            "title": "Python OOP Notes",
            "resource_link": "https://example.com/python-oop.pdf",
            "description": "Comprehensive notes on OOP in Python",
            "subject": "Computer Science",
            "category": "Notes"
        }

    Responses:
        201 - Material created
        400 - Invalid data
        401 - Missing/invalid token
        500 - Server error
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title", "").strip()
    resource_link = data.get("resource_link", "").strip()
    description = data.get("description", "").strip()
    subject = data.get("subject", "").strip()
    category = data.get("category", "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    if not resource_link:
        return jsonify({"error": "resource_link is required"}), 400

    if len(resource_link) > Config.MAX_URL_LENGTH:
        return jsonify({
            "error": f"Resource link exceeds maximum length of {Config.MAX_URL_LENGTH} characters"
        }), 400

    if not (resource_link.startswith("http://") or resource_link.startswith("https://")):
        return jsonify({"error": "Resource link must start with http:// or https://"}), 400

    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        material = MaterialModel.create_material(
            user["id"], title, resource_link, description, subject, category
        )
        return jsonify({
            "message": "Study material created successfully",
            "material": material
        }), 201
    except Exception as e:
        return jsonify({"error": "Failed to create material", "details": str(e)}), 500


@materials_bp.route("/api/materials", methods=["GET"])
@jwt_required()
def list_materials():
    """
    List all study materials created by the authenticated user.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - List of user's materials
        401 - Missing/invalid token
        404 - User not found
    """
    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    materials = MaterialModel.get_materials_by_user(user["id"])
    return jsonify({
        "total": len(materials),
        "materials": materials
    }), 200


@materials_bp.route("/api/materials/search", methods=["GET"])
@jwt_required()
def search_materials():
    """
    Search study materials by title, description, subject, or category.

    Headers:
        Authorization: Bearer <token>

    Query params:
        q (required) - The search query string

    Responses:
        200 - Matching materials
        400 - Missing search query
        401 - Missing/invalid token
        404 - User not found
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query 'q' is required"}), 400

    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    results = MaterialModel.search_materials(user["id"], query)
    return jsonify({
        "total": len(results),
        "query": query,
        "materials": results
    }), 200


@materials_bp.route("/api/analytics", methods=["GET"])
@jwt_required()
def analytics():
    """
    Get detailed view analytics for the authenticated user's materials.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - Analytics data with top materials
        401 - Missing/invalid token
        404 - User not found
    """
    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    analytics_data = MaterialModel.get_user_analytics(user["id"])
    return jsonify(analytics_data), 200


@materials_bp.route("/api/materials/<int:material_id>", methods=["DELETE"])
@jwt_required()
def delete_material_route(material_id):
    """
    Delete a study material owned by the authenticated user.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - Material deleted successfully
        401 - Missing/invalid token
        404 - Material not found or not owned by user
    """
    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    deleted = MaterialModel.delete_material(material_id, user["id"])
    if not deleted:
        return jsonify({"error": "Material not found or not owned by user"}), 404

    return jsonify({"message": "Material deleted successfully"}), 200


@materials_bp.route("/<code>", methods=["GET"])
def redirect_resource(code):
    """
    Redirect a resource code to the original resource link.

    This route does not require authentication — anyone can follow a resource link.
    """
    material = MaterialModel.get_material_by_code(code)
    if not material:
        return jsonify({"error": "Resource not found"}), 404

    MaterialModel.increment_views(code)
    return redirect(material["resource_link"], 302)