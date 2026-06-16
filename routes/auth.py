from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import Config
import models.user as UserModel
import models.material as MaterialModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    """
    Register a new user.

    Request (JSON):
        { "username": "john", "email": "john@example.com", "password": "secret123" }

    Responses:
        201 - User registered, JWT token returned
        400 - Missing or invalid fields
        409 - Email already registered
        500 - Server error
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # --- Validation ---
    errors = []
    if not username:
        errors.append("username is required")
    elif len(username) < 2 or len(username) > 80:
        errors.append("username must be between 2 and 80 characters")

    if not email:
        errors.append("email is required")
    elif not Config.EMAIL_REGEX.match(email):
        errors.append("email format is invalid")

    if not password:
        errors.append("password is required")
    elif len(password) < 6:
        errors.append("password must be at least 6 characters")

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    # Check existing user
    existing = UserModel.get_user_by_email(email)
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    # Create user
    try:
        user = UserModel.create_user(username, email, password)
        token = create_access_token(identity=email)

        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        }), 201

    except Exception as e:
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


@auth_bp.route("/api/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT token.

    Request (JSON):
        { "email": "john@example.com", "password": "secret123" }

    Responses:
        200 - Login successful, JWT token returned
        400 - Missing credentials
        401 - Invalid email or password
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = UserModel.verify_password(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=email)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }), 200


@auth_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    Get the profile and URL stats of the authenticated user.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - User profile with stats
        401 - Missing or invalid token
        404 - User not found
    """
    current_email = get_jwt_identity()

    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Use lightweight stats query instead of full analytics
    stats = MaterialModel.get_user_stats(user["id"])
    
    # Get analytics for additional data
    analytics_data = MaterialModel.get_user_analytics(user["id"])

    return jsonify({
        "user": user,
        "stats": {
            **stats,
            "avg_views": analytics_data.get("avg_views", 0),
            "top_material": analytics_data["top_materials"][0]["title"] if analytics_data.get("top_materials") else "N/A"
        }
    }), 200
